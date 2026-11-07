"""Merge a player's JourneyMap upload into the floor 1 explored map (tiles/f1jm) without a full rebuild.

Usage:
  python3 -I tools/jm_merge.py <upload.zip | folder> [--report R0005] [--date YYYY-MM-DD] [--min-overlap 20]
  python3 -I tools/jm_merge.py --init-mask        (one-off: derive the explored mask from the current tiles)
  python3 -I tools/jm_merge.py --overviews        (redraw every dungeon's overview.jpg from its stored tiles)

The upload holds JourneyMap region images "x,z.png" (512 x 512, 1 block = 1 px, region x,z starts at block x*512,
z*512) in "day" folders (the surface) and, since 2026-11-06, in the height-layer folders next to them: JourneyMap names
those by the 16-block slice number (folder "1" = Y 16-31, the in-game minimap shows "y: 24 (1)"; negative numbers too).
The site's 「打包探索地圖」 tool builds it from the player's journeymap/data/mp folder (one sub-folder per world the
player visited; only the floor 1 ones are packed; the player picks the layers and, optionally, an X/Z area), but a
hand-made zip works too. Images are grouped by WORLD (the folder that holds "day" and the layer folders); night / topo /
biome folders are ignored. A world is accepted only through its "day" images (the colour check below), so a pack with
only height layers still carries a few surface regions as anchors; layer data of a world that fails the check is dropped.
Height layers go to their own tiles (tiles/f1jm_c<n>/, dark background, own explored mask) and never change the
surface map, its explored share, the contributor list or floor1_jm.jpg. Only slices -4..19 are used (Minecraft's world
height -64..319); JourneyMap also keeps folders like "-398" that cannot be real heights, they are ignored.
Dungeons (2026-11-06): JourneyMap keeps each dungeon instance as a dimension folder next to "overworld" in the same
server folder, named "<uuid>_<dungeon>" (a57676b0-…-000000000001_geldorack, …_xalzirith, …_labyrinthe). A dungeon is
merged only when the same server folder in the upload also holds a floor 1 overworld that passes the colour check (the
packer adds a few surface regions for that), and only for the names in DUNGEONS; all its instances go into one map per
dungeon and height (tiles/dg/<id>/<key>/, level-3 tiles named by absolute world tile index, levels 0-2 over a frame
that grows with the data, chunks.json = explored chunks), plus overview.jpg for the dungeon panel. An instance whose
colours do not match what the site already has for that dungeon is skipped. Run by .github/workflows/jm_merge.yml for every 「探索地圖」 report (approved
automatically: the checks below are the review), or by the owner locally (use this instead of jm_tiles.py so other
players' data is kept).

What it does
  1. Rebuilds the 5120 px full-resolution canvas from the level 3 tiles (tiles/f1jm/3, 1 px = 1 block, frame starts
     at block 70) and reads tiles/f1jm/explored.png (1 px per 16 x 16 chunk, world chunk coordinates).
  2. Checks the upload: only "x,z.png" entries (other files are ignored), at most 600 regions, 4 MB each, 512 x 512.
     Each folder is checked on its own: it must overlap at least --min-overlap (20) chunks that are already explored
     and the colours there must match the current map (median difference <= 32). A folder that overlaps too little
     cannot be confirmed as floor 1 and a folder that does not match is another world / floor; both are skipped.
     If no folder passes, nothing is changed.
  3. Pastes the passing folders oldest first (newest data wins where they overlap; transparent parts keep the
     current map), marks the chunks as explored, rewrites the
     level 3 tiles it touched, regenerates levels 0-2 and floor1_jm.jpg and updates jmmeta.js. The result (merged or
     rejected, with the reason) is stored in jmmeta.js under results[report]; reports.js is never touched, so this
     cannot conflict with the Google script that appends reports.
Prints one JSON line; exit code 0 = merged, 2 = rejected (reason in the JSON), 1 = error.
"""
import datetime, io, json, os, re, statistics, sys, zipfile
from PIL import Image, ImageChops, ImageEnhance, ImageStat

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TILES = os.path.join(ROOT, "tiles", "f1jm")
MASK = os.path.join(TILES, "explored.png")
META = os.path.join(ROOT, "jmmeta.js")
X0, SIZE, FULL, T, CH, MW = 70, 4980, 5120, 256, 16, 320
BG = (7, 12, 17)
OV_THR, OV_PAD, OV_MAX = 40, 12, 1024   # dungeon overview: content threshold, margin, longest side
NAME = re.compile(r"(?:^|/)(-?\d+),(-?\d+)\.png$")
LAYER = re.compile(r"-?\d+")    # JourneyMap height-layer folder (16-block slice number)
LAYER_MIN, LAYER_MAX = -4, 19   # world height -64..319; keep in sync with JMP.LMIN/LMAX in src/index.html
DG_RE = re.compile(r"(?:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_)?([a-z0-9]+)")
# JourneyMap dimension name suffix -> site name; keep in sync with DG_DIM in src/index.html
DUNGEONS = {"xalzirith": "Sanctuary of Xal'Zirith", "geldorack": "Geldorack Dungeon", "labyrinthe": "Labyrinth of the Fallen"}
DG_ROOT = os.path.join(ROOT, "tiles", "dg")
DG_MIN_OVERLAP = 8   # dungeons are small: 8 matching chunks are enough to tell a wrong map
MAX_REGIONS, MAX_BYTES = 1500, 4 * 1024 * 1024   # keep MAX_REGIONS in sync with JMP.MAXN in src/index.html
MIN_OVERLAP = 20   # explored chunks a folder must cover (with matching colours) before it is accepted as floor 1
C0, C1 = X0 // CH, (X0 + SIZE - 1) // CH          # chunk range inside the frame (inclusive)


def out(code, **kw):
    print(json.dumps(kw, ensure_ascii=False))
    sys.exit(code)


def load_canvas(tiles=None):
    tiles = tiles or TILES
    cv = Image.new("RGB", (FULL, FULL), BG)
    d = os.path.join(tiles, "3")
    for name in (os.listdir(d) if os.path.isdir(d) else []):
        m = re.fullmatch(r"(\d+)_(\d+)\.jpg", name)
        if m:
            cv.paste(Image.open(os.path.join(d, name)).convert("RGB"), (int(m[1]) * T, int(m[2]) * T))
    return cv


def layer_dir(key):
    return os.path.join(ROOT, "tiles", "f1jm_" + key)


def pyramid(cv, tiles):
    """levels 0-2 of a tile set from its full-resolution canvas"""
    for L, size in enumerate((640, 1280, 2560)):
        os.makedirs(os.path.join(tiles, str(L)), exist_ok=True)
        im = cv.resize((size, size), Image.LANCZOS)
        for r in range(size // T + (size % T > 0)):
            for c in range(size // T + (size % T > 0)):
                if c * T * FULL // size >= SIZE or r * T * FULL // size >= SIZE:
                    continue
                save_tile(im.crop((c * T, r * T, c * T + T, r * T + T)), os.path.join(tiles, str(L), f"{c}_{r}.jpg"))


def merge_layer(key, worlds):
    """paste the height-layer regions of the accepted worlds (oldest first) into tiles/f1jm_<key>; returns
    (new chunks, regions). Only level-3 tiles that hold data exist; levels 0-2 are always complete."""
    tiles = layer_dir(key)
    os.makedirs(os.path.join(tiles, "3"), exist_ok=True)
    cv = load_canvas(tiles)
    mpath = os.path.join(tiles, "explored.png")
    mask = Image.open(mpath).convert("L") if os.path.exists(mpath) else Image.new("L", (MW, MW), 0)
    new, touched, n = set(), set(), 0
    for g in sorted(worlds, key=lambda g: g["date"]):
        for rx, rz, im in g["layers"].get(key, []):
            if not (rx * 512 < X0 + SIZE and rz * 512 < X0 + SIZE and rx * 512 + 512 > X0 and rz * 512 + 512 > X0):
                continue
            n += 1
            new |= new_in(rx, rz, im, mask)
            alpha = im.getchannel("A")
            for lz in range(0, 512, CH):            # every chunk with data counts as explored in this layer
                for lx in range(0, 512, CH):
                    cx, cz = (rx * 512 + lx) // CH, (rz * 512 + lz) // CH
                    if C0 <= cx <= C1 and C0 <= cz <= C1 and alpha.crop((lx, lz, lx + CH, lz + CH)).getextrema()[1] > 0:
                        mask.putpixel((cx, cz), 255)
            ox, oz = rx * 512 - X0, rz * 512 - X0
            cv.paste(im.convert("RGB"), (ox, oz), alpha)
            for ty in range(max(0, oz) // T, min(SIZE - 1, oz + 511) // T + 1):
                for tx in range(max(0, ox) // T, min(SIZE - 1, ox + 511) // T + 1):
                    touched.add((tx, ty))
    if not n:
        return 0, 0
    cv.paste(Image.new("RGB", (FULL - SIZE, FULL), BG), (SIZE, 0))
    cv.paste(Image.new("RGB", (FULL, FULL - SIZE), BG), (0, SIZE))
    mask.save(mpath, optimize=True)
    for tx, ty in touched:
        save_tile(cv.crop((tx * T, ty * T, tx * T + T, ty * T + T)), os.path.join(tiles, "3", f"{tx}_{ty}.jpg"))
    pyramid(cv, tiles)
    return len(new), n


def tile_xy(name):
    m = re.fullmatch(r"(-?\d+)_(-?\d+)\.jpg", name)
    return (int(m[1]), int(m[2])) if m else None


def merge_dungeon(d, instances, date, report):
    """merge the instances of one dungeon (oldest first) into tiles/dg/<d>/<key>/; returns {newChunks, regions,
    check (median colour difference against what the site had), skipped}"""
    base = os.path.join(DG_ROOT, d)
    meta = load_meta().get("dg", {}).get(d, {})
    state = {}   # key -> {"tiles": {(tx,tz): RGB}, "touched": set, "chunks": set}

    def st(key):
        if key not in state:
            kd = os.path.join(base, key)
            cpath = os.path.join(kd, "chunks.json")
            chunks = {tuple(c) for c in json.load(open(cpath))} if os.path.exists(cpath) else set()
            state[key] = {"dir": kd, "tiles": {}, "touched": set(), "chunks": chunks, "old": set(chunks)}
        return state[key]

    def tile(s, tx, tz):
        if (tx, tz) not in s["tiles"]:
            p = os.path.join(s["dir"], "3", f"{tx}_{tz}.jpg")
            s["tiles"][(tx, tz)] = Image.open(p).convert("RGB") if os.path.exists(p) else Image.new("RGB", (T, T), BG)
        return s["tiles"][(tx, tz)]

    new, regions, diffs_all, skipped = set(), 0, [], []
    for g in sorted(instances, key=lambda g: g["date"]):
        diffs = []                      # colour check against the map as it stands before this instance
        for key, regs in g["layers"].items():
            s = st(key)
            for rx, rz, im in regs:
                alpha = im.getchannel("A")
                for lz in range(0, 512, CH):
                    for lx in range(0, 512, CH):
                        cx, cz = (rx * 512 + lx) // CH, (rz * 512 + lz) // CH
                        if (cx, cz) not in s["chunks"]:
                            continue
                        a = alpha.crop((lx, lz, lx + CH, lz + CH))
                        if ImageStat.Stat(a).mean[0] <= 200:
                            continue
                        wx, wz = rx * 512 + lx, rz * 512 + lz
                        t = tile(s, wx // T, wz // T)
                        diffs.append(mean_diff(im.crop((lx, lz, lx + CH, lz + CH)).convert("RGB"), t.crop((wx % T, wz % T, wx % T + CH, wz % T + CH))))
        med = statistics.median(diffs) if diffs else None
        if len(diffs) >= DG_MIN_OVERLAP and med > 32:
            skipped.append((g["name"], f"和網站上 {DUNGEONS[d]} 的地圖重疊 {len(diffs)} 個區塊但顏色對不上（差異 {med:.0f}）"))
            continue
        diffs_all += diffs
        for key, regs in g["layers"].items():
            s = st(key)
            for rx, rz, im in regs:
                regions += 1
                alpha = im.getchannel("A")
                if alpha.getextrema()[1] == 0:
                    continue
                for lz in range(0, 512, CH):
                    for lx in range(0, 512, CH):
                        if alpha.crop((lx, lz, lx + CH, lz + CH)).getextrema()[1] > 0:
                            c = ((rx * 512 + lx) // CH, (rz * 512 + lz) // CH)
                            if c not in s["chunks"]:
                                s["chunks"].add(c)
                                new.add((key,) + c)
                for oz in (0, T):
                    for ox in (0, T):
                        a = alpha.crop((ox, oz, ox + T, oz + T))
                        if a.getextrema()[1] == 0:
                            continue
                        tx, tz = (rx * 512 + ox) // T, (rz * 512 + oz) // T
                        tile(s, tx, tz).paste(im.crop((ox, oz, ox + T, oz + T)).convert("RGB"), (0, 0), a)
                        s["touched"].add((tx, tz))
    if not regions:
        return {"newChunks": 0, "regions": 0, "skipped": skipped}
    for key, s in state.items():
        if not s["touched"]:
            continue
        os.makedirs(os.path.join(s["dir"], "3"), exist_ok=True)
        for tx, tz in s["touched"]:
            save_tile(s["tiles"][(tx, tz)], os.path.join(s["dir"], "3", f"{tx}_{tz}.jpg"))
        json.dump(sorted(s["chunks"]), open(os.path.join(s["dir"], "chunks.json"), "w"), separators=(",", ":"))
    # frame over every height of this dungeon (it grows with the data), then levels 0-2 and the overview
    keys = sorted(k for k in os.listdir(base) if os.path.isdir(os.path.join(base, k, "3")))
    l3 = {k: [xy for xy in map(tile_xy, os.listdir(os.path.join(base, k, "3"))) if xy] for k in keys}
    allt = [xy for v in l3.values() for xy in v]
    tx0, tz0 = min(x for x, _ in allt), min(z for _, z in allt)
    span = max(max(x for x, _ in allt) - tx0 + 1, max(z for _, z in allt) - tz0 + 1) * T
    full = -(-span // 2048) * 2048
    chunks = {k: {tuple(c) for c in json.load(open(os.path.join(base, k, "chunks.json")))} for k in keys}
    allc = [c for v in chunks.values() for c in v]
    bounds = [min(c[0] for c in allc) * CH, min(c[1] for c in allc) * CH, (max(c[0] for c in allc) + 1) * CH, (max(c[1] for c in allc) + 1) * CH]
    best = max(keys, key=lambda k: len(chunks[k]))
    layers = {}
    for k in keys:
        cv = Image.new("RGB", (full, full), BG)
        for tx, tz in l3[k]:
            cv.paste(Image.open(os.path.join(base, k, "3", f"{tx}_{tz}.jpg")).convert("RGB"), ((tx - tx0) * T, (tz - tz0) * T))
        for L, size in enumerate((full // 8, full // 4, full // 2)):
            ld = os.path.join(base, k, str(L))
            os.makedirs(ld, exist_ok=True)
            for f in os.listdir(ld):
                os.remove(os.path.join(ld, f))
            im = cv.resize((size, size), Image.LANCZOS)
            for r in range(-(-size // T)):
                for c in range(-(-size // T)):
                    save_tile(im.crop((c * T, r * T, c * T + T, r * T + T)), os.path.join(ld, f"{c}_{r}.jpg"))
        if k == best:
            bx = (max(0, bounds[0] - tx0 * T - 16), max(0, bounds[1] - tz0 * T - 16), min(full, bounds[2] - tx0 * T + 16), min(full, bounds[3] - tz0 * T + 16))
            save_overview(cv.crop(bx), os.path.join(base, "overview.jpg"))
        n = len(chunks[k])
        layers[k] = {"label": layer_label(k), "chunks": n, "l3": sorted(f"{x}_{z}" for x, z in l3[k]), "v": f"{date}-{n}"}
    newc = len(new)
    allmeta = load_meta()
    e = allmeta.setdefault("dg", {}).setdefault(d, {"log": []})
    e.update({"name": DUNGEONS[d], "date": date, "frame": {"x0": tx0 * T, "z0": tz0 * T, "full": full}, "bounds": bounds,
              "best": best, "layers": layers, "v": f"{date}-{len(allc)}"})
    e["log"].append({"report": report, "date": date, "regions": regions, "newChunks": newc})
    save_meta(allmeta)
    return {"newChunks": newc, "regions": regions, "check": round(statistics.median(diffs_all), 1) if diffs_all else None, "skipped": skipped}


def dark_base():
    base = Image.open(os.path.join(ROOT, "floor1.jpg")).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
    return ImageEnhance.Brightness(ImageEnhance.Color(base).enhance(0.35)).enhance(0.45)


def chunk_box(cx, cz):
    """canvas pixel box of world chunk (cx, cz), clipped to the frame"""
    x0, z0 = cx * CH - X0, cz * CH - X0
    return (max(0, x0), max(0, z0), min(SIZE, x0 + CH), min(SIZE, z0 + CH))


def mean_diff(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


def init_mask():
    cv, base = load_canvas(), dark_base()
    diffs = {}
    for cz in range(C0, C1 + 1):
        for cx in range(C0, C1 + 1):
            bx = chunk_box(cx, cz)
            if bx[2] - bx[0] < 4 or bx[3] - bx[1] < 4:
                continue
            diffs[(cx, cz)] = mean_diff(cv.crop(bx), base.crop(bx))
    mask = Image.new("L", (MW, MW), 0)
    for (cx, cz), d in diffs.items():
        if d > 9:                                    # JPEG noise on the darkened wiki map stays below 4 (bimodal histogram)
            mask.putpixel((cx, cz), 255)
    mask.save(MASK, optimize=True)
    n = sum(1 for v in mask.get_flattened_data() if v) if hasattr(mask, "get_flattened_data") else sum(1 for v in mask.getdata() if v)
    hist = [sum(1 for d in diffs.values() if lo <= d < lo + 4) for lo in range(0, 40, 4)]
    print(json.dumps({"ok": True, "explored_chunks": n, "frame_chunks": len(diffs), "diff_histogram_0_40_by_4": hist}))


def folder_label(d):
    """a short name for a folder of the upload (the JourneyMap world folder if there is one)"""
    parts = [p for p in d.replace("\\", "/").split("/") if p]
    for p in parts:
        if p.lower().startswith("triggers"):
            return p
    return "/".join(parts) or "（壓縮檔根目錄）"


def layer_of(folder):
    """("world folder", layer key) for a folder of the upload: "day" = surface, "c<n>" = height layer n; None = ignore"""
    parts = [p for p in folder.replace("\\", "/").split("/") if p]
    if not parts:
        return "", "day"                      # loose files at the zip root: surface (hand-made zips)
    leaf = parts[-1]
    if leaf.lower() == "day":
        return "/".join(parts[:-1]), "day"
    if LAYER.fullmatch(leaf):
        n = int(leaf)
        return ("/".join(parts[:-1]), "c" + str(n)) if LAYER_MIN <= n <= LAYER_MAX else None
    return None


def dungeon_of(world):
    """dungeon id of a world folder ("…/<uuid>_geldorack" -> "geldorack"), "?name" for an unknown "<uuid>_name",
    None for anything else"""
    leaf = world.replace("\\", "/").rstrip("/").split("/")[-1].lower()
    m = DG_RE.fullmatch(leaf)
    if not m:
        return None
    if m[1] in DUNGEONS:
        return m[1]
    return "?" + m[1] if "_" in leaf else None


def parent_of(world):
    return "/".join(world.replace("\\", "/").rstrip("/").split("/")[:-1])


def layer_label(key):
    if key == "day":
        return "地面"
    n = int(key[1:])
    return f"Y {n * 16}～{n * 16 + 15}"


def read_upload(src):
    """[{"name", "date", "layers": {key: [(rx, rz, RGBA image)]}}], one entry per world folder; raises ValueError with a
    reason players can understand."""
    found = {}   # (world, layer) -> [(rx, rz, bytes, mtime)]

    def take(folder, name, size, read, mtime):
        wl = layer_of(folder)
        if wl is None:
            return
        m = NAME.search("/" + name)
        if not m:
            return
        if size > MAX_BYTES:
            raise ValueError(f"{name} 超過 4 MB，不像 JourneyMap 的地圖圖片")
        found.setdefault(wl, []).append((int(m[1]), int(m[2]), read, mtime))

    if os.path.isdir(src):
        for dirpath, _, files in os.walk(src):
            rel = os.path.relpath(dirpath, src).replace(os.sep, "/")
            rel = "" if rel == "." else rel
            for f in sorted(files):
                fp = os.path.join(dirpath, f)
                take(rel, f, os.path.getsize(fp), (lambda fp=fp: open(fp, "rb").read()), os.path.getmtime(fp))
        if sum(len(v) for v in found.values()) > MAX_REGIONS:
            raise ValueError(f"資料夾裡有超過 {MAX_REGIONS} 張地圖圖片")
        found = {k: [(rx, rz, rd(), t) for rx, rz, rd, t in v] for k, v in found.items()}
    else:
        with zipfile.ZipFile(src) as z:
            for i in z.infolist():
                if i.is_dir() or "__MACOSX" in i.filename:
                    continue
                folder, name = os.path.split(i.filename.replace("\\", "/"))
                take(folder, name, i.file_size, (lambda i=i: z.read(i)), datetime.datetime(*i.date_time).timestamp())
            total = sum(len(v) for v in found.values())
            if total > MAX_REGIONS:
                raise ValueError(f"壓縮檔裡有 {total} 張地圖圖片，超過上限 {MAX_REGIONS}")
            found = {k: [(rx, rz, rd(), t) for rx, rz, rd, t in v] for k, v in found.items()}
    if not found:
        raise ValueError("壓縮檔裡沒有 JourneyMap 的地圖圖片（day 或高度層資料夾裡 3,7.png 這種檔案）。請用網站協作區的「打包探索地圖」產生壓縮檔")
    worlds = {}
    for (world, key), items in found.items():
        regions = []
        for rx, rz, data, _ in items:
            try:
                im = Image.open(io.BytesIO(data))
                im.load()
            except Exception:
                raise ValueError(f"{rx},{rz}.png 不是正常的 PNG 圖片")
            if im.size != (512, 512):
                raise ValueError(f"{rx},{rz}.png 的大小是 {im.size[0]}x{im.size[1]}，JourneyMap 的地圖圖片應該是 512x512")
            regions.append((rx, rz, im.convert("RGBA")))
        w = worlds.setdefault(world, {"name": folder_label(world), "path": world, "date": 0, "layers": {}})
        w["layers"][key] = regions
        w["date"] = max(w["date"], max(t for *_, t in items))
    return list(worlds.values())


def save_tile(im, path):
    im.save(path, quality=80, optimize=True, progressive=True)


def check_group(inside, cv, mask):
    """colour difference of every chunk that is already explored and fully covered by the upload, and the set of
    chunks the upload adds"""
    diffs, new = [], set()
    for rx, rz, im in inside:
        alpha = im.getchannel("A")
        for lz in range(0, 512, CH):
            for lx in range(0, 512, CH):
                cx, cz = (rx * 512 + lx) // CH, (rz * 512 + lz) // CH
                if not (C0 <= cx <= C1 and C0 <= cz <= C1):
                    continue
                a = alpha.crop((lx, lz, lx + CH, lz + CH))
                if a.getextrema()[1] == 0:
                    continue
                if mask.getpixel((cx, cz)) and ImageStat.Stat(a).mean[0] > 200:
                    bx = chunk_box(cx, cz)
                    cut = im.crop((lx + bx[0] - (cx * CH - X0), lz + bx[1] - (cz * CH - X0),
                                   lx + bx[2] - (cx * CH - X0), lz + bx[3] - (cz * CH - X0))).convert("RGB")
                    diffs.append(mean_diff(cut, cv.crop(bx)))
                elif not mask.getpixel((cx, cz)):
                    new.add((cx, cz))
    return diffs, new


def new_in(rx, rz, im, mask):
    """chunks of one region that have map data and are not explored yet"""
    alpha, new = im.getchannel("A"), set()
    for lz in range(0, 512, CH):
        for lx in range(0, 512, CH):
            cx, cz = (rx * 512 + lx) // CH, (rz * 512 + lz) // CH
            if C0 <= cx <= C1 and C0 <= cz <= C1 and not mask.getpixel((cx, cz)) \
                    and alpha.crop((lx, lz, lx + CH, lz + CH)).getextrema()[1] > 0:
                new.add((cx, cz))
    return new


def content_box(im, thr=OV_THR, pad=OV_PAD):
    """Box around what the map really shows. Explored-but-empty chunks are drawn black (or the dark blue of the void),
    so the chunk bounds leave big dark margins (user 2026-11-07: 地圖縮太小了，可以裁掉不必要的部分).
    A row/column counts when at least 2 pixels are brighter than thr in any channel."""
    g = im.convert("RGB").point(lambda v: 255 if v > thr else 0).convert("L").point(lambda v: 255 if v else 0)
    w, h = g.size
    px = g.load()
    cols = [x for x in range(w) if sum(1 for y in range(0, h) if px[x, y]) >= 2]
    rows = [y for y in range(h) if sum(1 for x in range(0, w) if px[x, y]) >= 2]
    if not cols or not rows:
        return (0, 0, w, h)
    return (max(0, cols[0] - pad), max(0, rows[0] - pad), min(w, cols[-1] + 1 + pad), min(h, rows[-1] + 1 + pad))


def save_overview(im, path):
    im = im.crop(content_box(im))
    im.thumbnail((OV_MAX, OV_MAX), Image.LANCZOS)
    im.save(path, quality=88, optimize=True)


def redraw_overviews():
    meta = load_meta().get("dg", {})
    for d, e in meta.items():
        base = os.path.join(ROOT, "tiles", "dg", d)
        k, fr = e.get("best"), e.get("frame") or {}
        if not k or not os.path.isdir(os.path.join(base, k, "3")):
            continue
        tx0, tz0, full = fr["x0"] // T, fr["z0"] // T, fr["full"]
        cv = Image.new("RGB", (full, full), BG)
        for xy in map(tile_xy, os.listdir(os.path.join(base, k, "3"))):
            if xy:
                cv.paste(Image.open(os.path.join(base, k, "3", f"{xy[0]}_{xy[1]}.jpg")).convert("RGB"), ((xy[0] - tx0) * T, (xy[1] - tz0) * T))
        b = e["bounds"]
        save_overview(cv.crop((max(0, b[0] - fr["x0"] - 16), max(0, b[1] - fr["z0"] - 16), min(full, b[2] - fr["x0"] + 16), min(full, b[3] - fr["z0"] + 16))), os.path.join(base, "overview.jpg"))
        print(d, Image.open(os.path.join(base, "overview.jpg")).size)


def main(argv):
    if "--init-mask" in argv:
        return init_mask()
    if "--overviews" in argv:
        return redraw_overviews()
    opt = {argv[i]: argv[i + 1] for i in range(len(argv) - 1) if argv[i].startswith("--")}
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and not (i and argv[i - 1] in opt)]
    report, date = opt.get("--report"), opt.get("--date") or datetime.date.today().isoformat()
    if not args:
        sys.exit(__doc__)
    min_overlap = int(opt.get("--min-overlap", MIN_OVERLAP))
    try:
        groups = read_upload(args[0])
    except (ValueError, zipfile.BadZipFile) as e:
        record(report, {"ok": False, "reason": str(e) if not isinstance(e, zipfile.BadZipFile) else "檔案不是正常的 zip 壓縮檔"})
        out(2, ok=False, reason=str(e))
    cv = load_canvas()
    mask = Image.open(MASK).convert("L")
    accepted, skipped, dgs = [], [], []
    for g in groups:
        d = dungeon_of(g.get("path", ""))
        if d and d.startswith("?"):
            skipped.append((g["name"], f"網站還不認得的副本「{d[1:]}」，先不收"))
            continue
        if d:
            dgs.append(dict(g, dg=d))
            continue
        inside = [(rx, rz, im) for rx, rz, im in g["layers"].get("day", [])
                  if rx * 512 < X0 + SIZE and rz * 512 < X0 + SIZE and rx * 512 + 512 > X0 and rz * 512 + 512 > X0]
        if not g["layers"].get("day"):
            skipped.append((g["name"], "沒有地面（day）地圖，無法確認是第 1 層（只打包高度層時也要附上幾張地面圖）"))
            continue
        if not inside:
            skipped.append((g["name"], "地圖圖片都在第 1 層的範圍外"))
            continue
        diffs, new = check_group(inside, cv, mask)
        med = statistics.median(diffs) if diffs else None
        if len(diffs) >= 20 and med > 32:
            skipped.append((g["name"], f"和目前地圖重疊的 {len(diffs)} 個區塊顏色對不上（差異 {med:.0f}），可能是別的樓層或別的世界"))
        elif len(diffs) < min_overlap:
            skipped.append((g["name"], f"和網站現有的地圖只重疊 {len(diffs)} 個區塊（至少要 {min_overlap} 個），無法確認是第 1 層"))
        else:
            accepted.append(dict(g, inside=inside, overlap=len(diffs)))
    if not accepted:
        if len(skipped) == 1:
            reason = skipped[0][1]
        else:
            reason = f"{len(skipped)} 個資料夾都不是第 1 層的地圖：" + "；".join(f"{n}：{r}" for n, r in skipped[:3]) + ("…" if len(skipped) > 3 else "")
        if all("範圍外" in r for _, r in skipped):
            reason += "（可能選錯世界資料夾）"
        record(report, {"ok": False, "reason": reason})
        out(2, ok=False, reason=reason, skipped=[n for n, _ in skipped])
    new_chunks, touched = set(), set()
    for g in sorted(accepted, key=lambda g: g["date"]):          # oldest first: the newest data ends up on top
        for rx, rz, im in g["inside"]:
            new_chunks |= new_in(rx, rz, im, mask)
            ox, oz = rx * 512 - X0, rz * 512 - X0
            cv.paste(im.convert("RGB"), (ox, oz), im.getchannel("A"))
            for ty in range(max(0, oz) // T, min(SIZE - 1, oz + 511) // T + 1):
                for tx in range(max(0, ox) // T, min(SIZE - 1, ox + 511) // T + 1):
                    touched.add((tx, ty))
    # anything outside the frame that the paste wrote must stay background
    cv.paste(Image.new("RGB", (FULL - SIZE, FULL), BG), (SIZE, 0))
    cv.paste(Image.new("RGB", (FULL, FULL - SIZE), BG), (0, SIZE))
    for cx, cz in new_chunks:
        mask.putpixel((cx, cz), 255)
    # surface regions are always written (newer terrain wins), as before; anchors of a layer-only pack paste the same picture
    mask.save(MASK, optimize=True)
    for tx, ty in touched:
        save_tile(cv.crop((tx * T, ty * T, tx * T + T, ty * T + T)), os.path.join(TILES, "3", f"{tx}_{ty}.jpg"))
    pyramid(cv, TILES)
    cv.crop((0, 0, SIZE, SIZE)).resize((3000, 3000), Image.LANCZOS).save(os.path.join(ROOT, "floor1_jm.jpg"), quality=85, optimize=True)
    explored = sum(1 for cz in range(C0, C1 + 1) for cx in range(C0, C1 + 1) if mask.getpixel((cx, cz)))
    pct = round(100 * explored / (C1 - C0 + 1) ** 2, 1)
    layers = {}
    for key in sorted({k for g in accepted for k in g["layers"] if k != "day"}, key=lambda k: int(k[1:])):
        nc, nr = merge_layer(key, accepted)
        if nr:
            layers[key] = {"newChunks": nc, "regions": nr}
    res = {"ok": True, "regions": sum(len(g["inside"]) for g in accepted), "newChunks": len(new_chunks),
           "overlap": sum(g["overlap"] for g in accepted), "pct": pct, "date": date,
           "folders": len(accepted), "skipped": len(skipped)}
    if layers:
        res["layers"] = {k: v["newChunks"] for k, v in layers.items()}
    # dungeons: only those whose server folder also holds an accepted floor 1 overworld
    ok_parents = {parent_of(g.get("path", "")) for g in accepted}
    dres = {}
    for d in sorted({g["dg"] for g in dgs}):
        inst = [g for g in dgs if g["dg"] == d and parent_of(g.get("path", "")) in ok_parents]
        for g in dgs:
            if g["dg"] == d and g not in inst:
                skipped.append((g["name"], "同一個世界資料夾裡沒有確認過的第 1 層地圖，無法確認是這個伺服器的地下城"))
        if inst:
            r = merge_dungeon(d, inst, date, report)
            skipped += r.pop("skipped")
            if r["regions"]:
                dres[d] = r
    if dres:
        res["dungeons"] = {d: r["newChunks"] for d, r in dres.items()}
    if skipped:
        res["skipped"] = len(skipped)
        res["skippedWhy"] = [f"{n}：{w}" for n, w in skipped[:5]]
    write_meta(report, dict(res, chunks=explored), layers)
    record(report, res)
    out(0, **res)


def load_meta():
    if not os.path.exists(META):
        return {}
    t = open(META, encoding="utf-8").read()
    return json.loads(t[t.index("window.SAO_JM =") + 15:].strip().rstrip(";"))


def save_meta(meta):
    open(META, "w", encoding="utf-8").write(
        "/* Explored-map (JourneyMap) status: per floor the last merge date, share of the map frame explored (16x16 chunks)\n"
        "   and every merged upload; results[report id] = outcome of each player upload. Written by tools/jm_merge.py. */\n"
        "window.SAO_JM = " + json.dumps(meta, ensure_ascii=False, indent=1) + ";\n")


def write_meta(report, res, layers=None):
    """per merge: date, explored share, total explored chunks ("chunks") and a log entry with the chunks it added.
    The site lists contributors by these numbers (the first log entry is the owner's map, its newChunks = the rest)."""
    meta = load_meta()
    f1 = meta.setdefault("1", {"date": res["date"], "pct": res["pct"], "log": []})
    f1["date"], f1["pct"] = res["date"], res["pct"]
    f1["chunks"] = res.get("chunks", f1.get("chunks"))
    if f1["log"] and f1["log"][0].get("report") is None and "newChunks" not in f1["log"][0] and f1.get("chunks"):
        f1["log"][0]["newChunks"] = f1["chunks"] - res["newChunks"] - sum(e.get("newChunks", 0) for e in f1["log"][1:])
    f1["log"].append({"report": report, "date": res["date"], "regions": res["regions"], "newChunks": res["newChunks"]})
    # height layers: own explored count, the level-3 tiles that exist (the viewer asks only for those) and a version
    # string for cache-busting; kept apart from the surface numbers above
    for key, v in (layers or {}).items():
        tiles = layer_dir(key)
        lm = Image.open(os.path.join(tiles, "explored.png")).convert("L")
        chunks = sum(1 for cz in range(C0, C1 + 1) for cx in range(C0, C1 + 1) if lm.getpixel((cx, cz)))
        l3 = sorted(n[:-4] for n in os.listdir(os.path.join(tiles, "3")) if n.endswith(".jpg"))
        e = f1.setdefault("layers", {}).setdefault(key, {"log": []})
        e.update({"label": layer_label(key), "date": res["date"], "chunks": chunks, "l3": l3, "v": f"{res['date']}-{chunks}"})
        e["log"].append({"report": report, "date": res["date"], "regions": v["regions"], "newChunks": v["newChunks"]})
    save_meta(meta)


def record(report, res):
    """the outcome of a player upload, shown on the report in the site's report list"""
    if not report:
        return
    meta = load_meta()
    meta.setdefault("results", {})[report] = res
    save_meta(meta)


if __name__ == "__main__":
    main(sys.argv[1:])
