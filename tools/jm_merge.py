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
Prints one JSON line; exit code 0 = merged, 2 = rejected (reason in the JSON), 3 = held (a possible new floor that cannot be told
yet; kept to try again), 4 = merged but some worlds held, 1 = error.
"""
import datetime, io, json, os, re, shutil, statistics, sys, zipfile
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

# Floors 2 and 3 (2026-11-11): the owner's JourneyMap showed each floor in its own server folder (floor 2
# Triggers_ba411067…/overworld, floor 3 Triggers_95a78a58…/overworld), in real Minecraft X / Z. Frames: floor 2 = the wiki map
# (SIFT on 2,030 points: 1 px = 1.0114 block, X/Z -1062…1062; the site's floor-2 map frame), floor 3 = the reference map's
# "map-local" frame (centre 597,771, radius 850; SIFT against the owner's map: within 2 blocks). A floor's mask is in chunks
# from its own origin (MX0, MZ0); floor 1 keeps world chunks (origin 0, 320 x 320) so its existing explored.png stays valid.
# Floors 2 / 3 take the surface ("day") only: no height layers, dungeons or preview jpg (yet).
FLOOR_CFG = {1: dict(x0=70, z0=70, size=4980, full=5120, base="floor1.jpg", prev="floor1_jm.jpg", mx0=0, mz0=0, mw=320),
             2: dict(x0=-1062, z0=-1062, size=2124, full=2304, base="floor2.jpg", prev=None),
             3: dict(x0=-253, z0=-79, size=1700, full=1792, base="floor3.jpg", prev=None)}
# Opening a new floor (2026-11-12, user「樓層確認…要自動」): add it here with x0 = None (frame not known yet) and, if known, words =
# dungeon / boss folder names of that floor (JourneyMap names a dungeon run "<uuid>_<name>", e.g. floor 2's "_djtaurus").
# A never-seen server folder whose "overworld" matches no floor then becomes the one open floor that has no map yet, by
# itself (see new_floor()). The frame of a floor added with x0 None is centred on its first upload, 5120 blocks wide.
FLOOR_WORDS = {2: ["taurus", "djtaurus", "rugiboeuf", "velindra", "breches"]}
# Fractured Underworld server folders also hold an "overworld" (beside island_player_… / rulid / ice_cave …): never a floor
UNDERWORLD = re.compile(r"^(island_|rulid$|ice_cave$|gigas_cedar$|tuto_arrivee$|scene_akihiko$|backrooms$)|_memoryice$", re.I)
FLOOR = 1
Z0, CX0, CX1, CZ0, CZ1, MX0, MZ0 = X0, C0, C1, C0, C1, 0, 0


def use_floor(f):
    """point the module's frame constants at floor f (floor 1 = the values above)"""
    global FLOOR, X0, Z0, SIZE, FULL, TILES, MASK, MW, CX0, CX1, CZ0, CZ1, MX0, MZ0, C0, C1
    c = FLOOR_CFG[f]
    FLOOR, X0, Z0, SIZE, FULL = f, c["x0"], c["z0"], c["size"], c["full"]
    TILES = os.path.join(ROOT, "tiles", f"f{f}jm")
    MASK = os.path.join(TILES, "explored.png")
    CX0, CX1, CZ0, CZ1 = X0 // CH, (X0 + SIZE - 1) // CH, Z0 // CH, (Z0 + SIZE - 1) // CH
    MX0, MZ0 = c.get("mx0", CX0), c.get("mz0", CZ0)
    MW = c.get("mw", max(CX1 - MX0, CZ1 - MZ0) + 1)
    C0, C1 = CX0, CX1   # floor-1-only code (height layers, 「地下」) still reads these


def mget(mask, cx, cz):
    return mask.getpixel((cx - MX0, cz - MZ0))


def mset(mask, cx, cz):
    mask.putpixel((cx - MX0, cz - MZ0), 255)


def in_frame(rx, rz):
    return rx * 512 < X0 + SIZE and rz * 512 < Z0 + SIZE and rx * 512 + 512 > X0 and rz * 512 + 512 > Z0


def in_chunks(cx, cz):
    return CX0 <= cx <= CX1 and CZ0 <= cz <= CZ1


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
    for L, size in enumerate((FULL // 8, FULL // 4, FULL // 2)):
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


UNDER = "under"
GROUND_R = 3      # blocks (16 m each) a detected ground level spreads to
SURF_CORR = 0.45
CONTENT_MIN = 0.1
DARK = 24        # JourneyMap paints explored solid rock pure black and the site's empty background is (7,12,17): neither is data,
                 # otherwise a black lower layer covers the room above it (the mill ink room at Y 24 vanished under Y 0-15)   # a 16x16 cave block whose grey pattern correlates this much with the surface map is at ground level there


def build_under(date=None):
    """「地下」(user 2026-11-08「直接整合成地下」): all height layers combined into tiles/f1jm_under, so the site offers only
    地面 / 地下. Ground height differs across the island (Starting Town is at Y 17, mountains much higher), and JourneyMap's
    cave layer at ground level shows the houses there, which look like the surface (user 2026-11-08「該區域地面跟地下長一樣
    為什麼還要算地下」). So per 16x16 block the layer whose picture correlates best with the surface map (>= SURF_CORR) is taken
    as ground level there and only the layers below it count; blocks where no layer looks like the surface (caves inside a
    mountain) keep all layers. Layers are pasted from high to low, so where several remain the deepest wins. The per-height
    tile sets stay (the packing tool compares against them, quest maps are cut from them)."""
    import numpy as np
    keys = sorted((n[5:] for n in os.listdir(os.path.join(ROOT, "tiles")) if re.fullmatch(r"f1jm_c-?\d+", n)),
                  key=lambda k: int(k[1:]), reverse=True)
    if not keys:
        return None
    n = FULL // CH
    def blocks(a):
        return a.reshape(n, CH, n, CH).transpose(0, 2, 1, 3).reshape(n, n, CH * CH)
    sb = blocks(np.asarray(load_canvas(TILES).convert("L"), np.float32))
    sb = sb - sb.mean(axis=2, keepdims=True)
    # pass 1: per block, the LOWEST layer that looks like the surface = ground level. Mountain tops, towers and roofs above
    # it look like the surface too (Tolbana: Y 192-207 houses, Y 240-303 peaks), so taking the highest match kept the houses
    ground = np.full((n, n), -999, np.int32)
    for key in keys:                                     # high to low
        gb = blocks(np.asarray(load_canvas(layer_dir(key)).convert("L"), np.float32))
        data = (gb > DARK).mean(axis=2) > 0.3
        cb = gb - gb.mean(axis=2, keepdims=True)
        corr = (cb * sb).sum(axis=2) / (np.sqrt((cb * cb).sum(axis=2) * (sb * sb).sum(axis=2)) + 1e-6)
        ground[data & (corr >= SURF_CORR)] = int(key[1:])   # later (lower) layers overwrite: the lowest match wins
    # blocks where the match failed (house interiors that do not look like their roof) take the lowest ground level found
    # within GROUND_R blocks, so a whole town gets one ground level instead of a checkerboard (the highest would let a
    # nearby peak lift the level above the houses again)
    NONE = 9999
    pad = np.pad(np.where(ground == -999, NONE, ground), GROUND_R, constant_values=NONE)
    near = np.full_like(ground, NONE)
    for dz in range(2 * GROUND_R + 1):
        for dx in range(2 * GROUND_R + 1):
            near = np.minimum(near, pad[dz:dz + n, dx:dx + n])
    ground = np.where(ground == -999, np.where(near == NONE, -999, near), ground)
    # pass 2: composite the layers below ground level (all layers where no ground level was found)
    cv = Image.new("RGB", (FULL, FULL), BG)
    mask = Image.new("L", (MW, MW), 0)
    names = set()
    for key in keys:
        tiles = layer_dir(key)
        names |= {nm for nm in os.listdir(os.path.join(tiles, "3")) if nm.endswith(".jpg")}
        lc = load_canvas(tiles)
        has = lc.convert("L").point(lambda v: 255 if v > DARK else 0)
        below = (ground == -999) | (int(key[1:]) < ground)
        keep = Image.fromarray(np.kron(below, np.ones((CH, CH), bool)).astype(np.uint8) * 255)
        cv.paste(lc, (0, 0), ImageChops.multiply(has, keep))
        mp = os.path.join(tiles, "explored.png")
        if os.path.exists(mp):
            mask = ImageChops.lighter(mask, Image.open(mp).convert("L"))
    tiles = layer_dir(UNDER)
    if os.path.isdir(tiles):
        shutil.rmtree(tiles)
    os.makedirs(os.path.join(tiles, "3"))
    mask.save(os.path.join(tiles, "explored.png"), optimize=True)
    for nm in names:
        tx, ty = map(int, nm[:-4].split("_"))
        save_tile(cv.crop((tx * T, ty * T, tx * T + T, ty * T + T)), os.path.join(tiles, "3", nm))
    pyramid(cv, tiles)
    # content.png: 1 px per 16x16 block of the canvas (block = (world - X0) // 16, not world chunks), 255 where at least
    # CONTENT_MIN of the block is real underground picture. The site shows 「查看地下」 on a teleport point / landmark panel
    # only when such blocks are near it (user 2026-11-08: no 地下 menu on the map, an option on the panel instead)
    lum = blocks(np.asarray(cv.convert("L"), np.uint8))
    Image.fromarray(((lum > DARK).mean(axis=2) >= CONTENT_MIN).astype(np.uint8) * 255).save(os.path.join(tiles, "content.png"), optimize=True)
    chunks = sum(1 for cz in range(C0, C1 + 1) for cx in range(C0, C1 + 1) if mask.getpixel((cx, cz)))
    meta = load_meta()
    f1 = meta.setdefault("1", {})
    date = date or f1.get("date")
    f1.setdefault("layers", {})[UNDER] = {"label": "地下", "date": date, "chunks": chunks, "l3": sorted(nm[:-4] for nm in names),
                                          "v": f"{date}-{chunks}-g", "of": keys}
    save_meta(meta)
    return chunks


def dark_base():
    if not FLOOR_CFG[FLOOR].get("base"):
        return Image.new("RGB", (SIZE, SIZE), BG)
    base = Image.open(os.path.join(ROOT, FLOOR_CFG[FLOOR]["base"])).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
    return ImageEnhance.Brightness(ImageEnhance.Color(base).enhance(0.35)).enhance(0.45)


def chunk_box(cx, cz):
    """canvas pixel box of world chunk (cx, cz), clipped to the frame"""
    x0, z0 = cx * CH - X0, cz * CH - Z0
    return (max(0, x0), max(0, z0), min(SIZE, x0 + CH), min(SIZE, z0 + CH))


def mean_diff(a, b):
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


def init_mask():
    cv, base = load_canvas(), dark_base()
    diffs = {}
    for cz in range(CZ0, CZ1 + 1):
        for cx in range(CX0, CX1 + 1):
            bx = chunk_box(cx, cz)
            if bx[2] - bx[0] < 4 or bx[3] - bx[1] < 4:
                continue
            diffs[(cx, cz)] = mean_diff(cv.crop(bx), base.crop(bx))
    mask = Image.new("L", (MW, MW), 0)
    for (cx, cz), d in diffs.items():
        if d > 9:                                    # JPEG noise on the darkened wiki map stays below 4 (bimodal histogram)
            mset(mask, cx, cz)
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


def server_of(world):
    """the JourneyMap server folder of a world path ("…/Triggers_<world id>/overworld" -> "Triggers_<world id>"); the id is the
    world ID the server sends to every player (JourneyMap server docs), so the same floor has the same folder name for all"""
    p = parent_of(world).split("/")[-1]
    return p if re.match(r"(?i)triggers_.", p) else None


def read_manifest(src):
    """sao_pack.json written by the site's packer: {"worlds": {world path: {"siblings": [folder names beside it]}}}"""
    try:
        if os.path.isdir(src):
            fp = os.path.join(src, "sao_pack.json")
            return json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else {}
        with zipfile.ZipFile(src) as z:
            n = next((i for i in z.namelist() if i.split("/")[-1] == "sao_pack.json"), None)
            return json.loads(z.read(n)) if n else {}
    except Exception:
        return {}


def frame_for(f, regions):
    """a floor added with x0 None: a 5120-block square centred on its first upload (multiple of 16)"""
    xs = [rx * 512 for rx, _, _ in regions] + [rx * 512 + 512 for rx, _, _ in regions]
    zs = [rz * 512 for _, rz, _ in regions] + [rz * 512 + 512 for _, rz, _ in regions]
    cx, cz = (min(xs) + max(xs)) // 2, (min(zs) + max(zs)) // 2
    return dict(x0=(cx - 2560) // 16 * 16, z0=(cz - 2560) // 16 * 16, size=5120, full=5120)


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
                if not in_chunks(cx, cz):
                    continue
                a = alpha.crop((lx, lz, lx + CH, lz + CH))
                if a.getextrema()[1] == 0:
                    continue
                if mget(mask, cx, cz) and ImageStat.Stat(a).mean[0] > 200:
                    bx = chunk_box(cx, cz)
                    cut = im.crop((lx + bx[0] - (cx * CH - X0), lz + bx[1] - (cz * CH - Z0),
                                   lx + bx[2] - (cx * CH - X0), lz + bx[3] - (cz * CH - Z0))).convert("RGB")
                    diffs.append(mean_diff(cut, cv.crop(bx)))
                elif not mget(mask, cx, cz):
                    new.add((cx, cz))
    return diffs, new


def new_in(rx, rz, im, mask):
    """chunks of one region that have map data and are not explored yet"""
    alpha, new = im.getchannel("A"), set()
    for lz in range(0, 512, CH):
        for lx in range(0, 512, CH):
            cx, cz = (rx * 512 + lx) // CH, (rz * 512 + lz) // CH
            if in_chunks(cx, cz) and not mget(mask, cx, cz) \
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
    if "--under" in argv:
        return print("地下", build_under(), "chunks")
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
    # --seed N (owner only, never in the Actions workflow): start floor N's explored map from this upload; every world in
    # the frame is taken without the colour check (there is nothing to compare with yet)
    seed = int(opt["--seed"]) if "--seed" in opt else None
    meta0 = load_meta()
    for f, fr in (meta0.get("frames") or {}).items():          # frames worked out for floors added with x0 None
        if int(f) in FLOOR_CFG and FLOOR_CFG[int(f)].get("x0") is None:
            FLOOR_CFG[int(f)].update(fr)
    ids = dict(meta0.get("ids") or {})                          # server folder -> floor, learnt from accepted uploads
    manifest = (read_manifest(args[0]).get("worlds") or {})
    floors = [f for f in FLOOR_CFG if os.path.exists(os.path.join(ROOT, "tiles", f"f{f}jm", "explored.png"))]
    seeding = {seed} if seed else set()
    state, held, newids, conflicts = {}, [], {}, []

    def st(f):
        use_floor(f)
        if f not in state:
            if f in seeding and not os.path.exists(MASK):
                cv = Image.new("RGB", (FULL, FULL), BG)
                cv.paste(dark_base(), (0, 0))
                state[f] = (cv, Image.new("L", (MW, MW), 0))
            else:
                state[f] = (load_canvas(), Image.open(MASK).convert("L"))
        return state[f]

    accepted, skipped, dgs = [], [], []
    for g in groups:
        d = dungeon_of(g.get("path", ""))
        if d and d.startswith("?"):
            skipped.append((g["name"], f"網站還不認得的副本「{d[1:]}」，先不收"))
            continue
        if d:
            dgs.append(dict(g, dg=d))
            continue
        if not g["layers"].get("day"):
            skipped.append((g["name"], "沒有地面（day）地圖，無法確認是第 1 層（只打包高度層時也要附上幾張地面圖）"))
            continue
        if seed:
            st(seed)
            inside = [(rx, rz, im) for rx, rz, im in g["layers"]["day"] if in_frame(rx, rz)]
            if inside:
                accepted.append(dict(g, inside=inside, overlap=0, floor=seed))
            else:
                skipped.append((g["name"], f"地圖圖片都在第 {seed} 層的範圍外"))
            continue
        # the floor whose explored map the colours match (frames of floors 1-3 overlap). Every floor is tried and the one
        # with the most matching chunks wins: the owner's floor-3 folder also held a few floor-2 regions (written around the
        # teleport, 2026-11-12), which match floor 2 exactly but are far fewer than its floor-3 ones
        tried, ok, perf = [], None, {}
        # floors 2 / 3 take only "overworld" folders: the owner's boss-room instances (gorge_rugiboeuf, pre_breches) sit on
        # floor-2 coordinates but are changed copies (the gorge's arena has no sand disc), and would overwrite the real map
        leaf = g.get("path", "").replace("\\", "/").rstrip("/").split("/")[-1].lower()
        fl_ok = [f for f in floors if f == 1 or leaf == "overworld"]
        if len(fl_ok) < len(floors):
            tried.append((1, -1, f"「{leaf}」不是 overworld 資料夾：第 2、3 層只收 overworld（副本、首領房間先不收）"))
        for f in fl_ok:
            cv, mask = st(f)
            inside = [(rx, rz, im) for rx, rz, im in g["layers"]["day"] if in_frame(rx, rz)]
            if not inside:
                tried.append((0, -1, f"地圖圖片都在第 {f} 層的範圍外"))
                continue
            diffs, new = check_group(inside, cv, mask)
            med = statistics.median(diffs) if diffs else None
            perf[f] = (inside, diffs, med)
            if len(diffs) >= 20 and med > 32:
                tried.append((2, len(diffs), f"和目前地圖重疊的 {len(diffs)} 個區塊顏色對不上（差異 {med:.0f}），可能是別的樓層或別的世界"))
            elif len(diffs) < min_overlap:
                tried.append((1, len(diffs), f"和網站現有的地圖只重疊 {len(diffs)} 個區塊（至少要 {min_overlap} 個），無法確認是第 {f} 層"))
            elif not ok or len(diffs) > ok["overlap"]:
                ok = dict(g, inside=inside, overlap=len(diffs), floor=f)
        srv = server_of(g.get("path", ""))
        known = (ids.get(srv) or newids.get(srv)) if srv and leaf == "overworld" else None
        if not ok and known and known in perf:
            # a server folder already tied to a floor: too little overlap is fine (the player explored new ground), a colour
            # mismatch is not
            inside, diffs, med = perf[known]
            if not (len(diffs) >= 20 and med > 32):
                ok = dict(g, inside=inside, overlap=len(diffs), floor=known)
        if ok:
            if srv and leaf == "overworld":
                if ids.get(srv) not in (None, ok["floor"]):
                    conflicts.append(f"{srv} 原本記為第 {ids[srv]} 層，這次比色是第 {ok['floor']} 層")
                newids[srv] = ok["floor"]
            # single regions that clearly belong to another floor (no match on this one, a near-exact match there: a real
            # duplicate is ~10 per pixel, JPEG noise; other terrain 40+) go to that floor; the rest stays with the world's floor
            moved = {}
            if len(fl_ok) > 1:
                keep = []
                for r in ok["inside"]:
                    st(ok["floor"]); d0, _ = check_group([r], *state[ok["floor"]])
                    dest = None
                    if not (len(d0) >= 8 and statistics.median(d0) <= 32):
                        best = None
                        for f in fl_ok:
                            if f == ok["floor"]:
                                continue
                            st(f)
                            if in_frame(r[0], r[1]):
                                d1, _ = check_group([r], *state[f])
                                if len(d1) >= 8 and statistics.median(d1) <= 16 and (not best or len(d1) > best[1]):
                                    best = (f, len(d1))
                        dest = best and best[0]
                    if dest:
                        moved.setdefault(dest, []).append(r)
                    else:
                        keep.append(r)
                ok["inside"] = keep
            if ok["inside"]:
                accepted.append(ok)
            for f, rs in moved.items():
                accepted.append(dict(g, inside=rs, overlap=0, floor=f))
        else:
            nf = new_floor(g, srv, leaf, known, perf, ids, floors, manifest, groups) if not seed else None
            if nf and nf[0] == "floor":
                f = nf[1]
                if FLOOR_CFG[f].get("x0") is None:
                    FLOOR_CFG[f].update(frame_for(f, g["layers"]["day"]))
                    meta1 = load_meta(); meta1.setdefault("frames", {})[str(f)] = {k: FLOOR_CFG[f][k] for k in ("x0", "z0", "size", "full")}; save_meta(meta1)
                seeding.add(f)
                st(f)
                inside = [(rx, rz, im) for rx, rz, im in g["layers"]["day"] if in_frame(rx, rz)]
                accepted.append(dict(g, inside=inside, overlap=0, floor=f, newFloor=True))
                newids[srv] = f
                floors.append(f)
            elif nf and nf[0] == "hold":
                held.append((g["name"], nf[1]))
            else:
                # the reason from the first floor whose frame the world is in (floor 1 first), as the site's packer shows it
                skipped.append((g["name"], next((t[2] for t in tried if t[0]), tried[0][2]) if tried else "網站還沒有可以比對的樓層地圖"))
    if not accepted and held:
        # kept for later (the Actions job keeps the release and tries again every day): new clues such as the floor being
        # marked open on the site, or its words, decide it then
        reason = "；".join(f"{n}：{w}" for n, w in held[:3])
        record(report, {"ok": False, "held": True, "reason": reason, "date": date})
        out(3, ok=False, held=True, reason=reason)
    if not accepted:
        if len(skipped) == 1:
            reason = skipped[0][1]
        else:
            reason = f"{len(skipped)} 個資料夾都不是" + ("第 1 層" if floors == [1] else "網站認得的樓層") + "的地圖：" + "；".join(f"{n}：{r}" for n, r in skipped[:3]) + ("…" if len(skipped) > 3 else "")
        if all("範圍外" in r for _, r in skipped):
            reason += "（可能選錯世界資料夾）"
        record(report, {"ok": False, "reason": reason})
        out(2, ok=False, reason=reason, skipped=[n for n, _ in skipped])
    per, layers = {}, {}
    for f in sorted({g["floor"] for g in accepted}):
        cv, mask = st(f)
        acc = [g for g in accepted if g["floor"] == f]
        os.makedirs(os.path.join(TILES, "3"), exist_ok=True)
        new_chunks, touched = set(), set()
        if f in seeding and not os.path.exists(MASK):    # a new floor: write every tile of the frame
            touched = {(tx, ty) for ty in range((SIZE - 1) // T + 1) for tx in range((SIZE - 1) // T + 1)}
        for g in sorted(acc, key=lambda g: g["date"]):          # oldest first: the newest data ends up on top
            for rx, rz, im in g["inside"]:
                new_chunks |= new_in(rx, rz, im, mask)
                ox, oz = rx * 512 - X0, rz * 512 - Z0
                cv.paste(im.convert("RGB"), (ox, oz), im.getchannel("A"))
                for ty in range(max(0, oz) // T, min(SIZE - 1, oz + 511) // T + 1):
                    for tx in range(max(0, ox) // T, min(SIZE - 1, ox + 511) // T + 1):
                        touched.add((tx, ty))
        # anything outside the frame that the paste wrote must stay background
        cv.paste(Image.new("RGB", (FULL - SIZE, FULL), BG), (SIZE, 0))
        cv.paste(Image.new("RGB", (FULL, FULL - SIZE), BG), (0, SIZE))
        for cx, cz in new_chunks:
            mset(mask, cx, cz)
        # surface regions are always written (newer terrain wins), as before; anchors of a layer-only pack paste the same picture
        mask.save(MASK, optimize=True)
        for tx, ty in touched:
            save_tile(cv.crop((tx * T, ty * T, tx * T + T, ty * T + T)), os.path.join(TILES, "3", f"{tx}_{ty}.jpg"))
        pyramid(cv, TILES)
        if FLOOR_CFG[f].get("prev"):
            cv.crop((0, 0, SIZE, SIZE)).resize((3000, 3000), Image.LANCZOS).save(os.path.join(ROOT, FLOOR_CFG[f]["prev"]), quality=85, optimize=True)
        explored = sum(1 for cz in range(CZ0, CZ1 + 1) for cx in range(CX0, CX1 + 1) if mget(mask, cx, cz))
        pct = round(100 * explored / ((CX1 - CX0 + 1) * (CZ1 - CZ0 + 1)), 1)
        per[f] = {"regions": sum(len(g["inside"]) for g in acc), "newChunks": len(new_chunks),
                  "overlap": sum(g["overlap"] for g in acc), "pct": pct, "chunks": explored, "folders": len(acc)}
        if f == 1:     # height layers: floor 1 only
            for key in sorted({k for g in acc for k in g["layers"] if k != "day"}, key=lambda k: int(k[1:])):
                nc, nr = merge_layer(key, acc)
                if nr:
                    layers[key] = {"newChunks": nc, "regions": nr}
    use_floor(1)
    fl = sorted(per)
    res = {"ok": True, "regions": sum(v["regions"] for v in per.values()), "newChunks": sum(v["newChunks"] for v in per.values()),
           "overlap": sum(v["overlap"] for v in per.values()), "pct": per[fl[0]]["pct"], "date": date,
           "folders": len({g["name"] + "|" + g.get("path", "") for g in accepted}), "skipped": len(skipped)}
    if fl != [1]:
        res["floors"] = {str(f): {"newChunks": v["newChunks"], "pct": v["pct"]} for f, v in per.items()}
    if layers:
        res["layers"] = {k: v["newChunks"] for k, v in layers.items()}
    # dungeons: only those whose server folder also holds an accepted floor 1 overworld
    ok_parents = {parent_of(g.get("path", "")) for g in accepted if g["floor"] == 1}
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
    if held:
        res["held"] = [f"{n}：{w}" for n, w in held[:3]]
    if newids or conflicts:
        meta1 = load_meta()
        meta1.setdefault("ids", {}).update({k: v for k, v in newids.items() if k not in meta1["ids"]})
        if conflicts:
            meta1.setdefault("idConflicts", []).extend({"report": report, "date": date, "what": c} for c in conflicts)
            res["idConflicts"] = conflicts
        save_meta(meta1)
    newfl = sorted({g["floor"] for g in accepted if g.get("newFloor")})
    if newfl:
        res["newFloors"] = newfl
    for f, v in per.items():
        write_meta(report, dict(res, regions=v["regions"], newChunks=v["newChunks"], pct=v["pct"], chunks=v["chunks"]), layers if f == 1 else None, f)
    if layers:
        build_under(date)
    record(report, res)
    out(4 if held else 0, **res)     # 4 = merged, but some worlds wait (the Actions job keeps the release for a later try)


def new_floor(g, srv, leaf, known, perf, ids, floors, manifest, groups):
    """("floor", f) when this world is the first map of an open floor, ("hold", why) to try again later, None = not a floor.
    Only an "overworld" folder in a Triggers_<id> server folder that no floor's colours match (a mismatch against an existing
    map is fine: that proves it is not that floor) and whose server folder holds no Fractured Underworld world."""
    if not srv or leaf != "overworld" or known or not g["layers"].get("day"):
        return None
    if any(len(d) >= 20 and m <= 32 for _, d, m in perf.values()):
        return None
    sib = (manifest.get(g.get("path", "")) or {}).get("siblings")
    if sib is None:      # not packed by the site (no folder list): cannot rule out the Fractured Underworld, treated as before
        return None
    if any(UNDERWORLD.search(n) for n in sib):
        return None
    taken = set(ids.values())
    cands = [f for f in sorted(FLOOR_CFG) if f not in floors and f not in taken]
    if len(cands) > 1:
        words = " ".join(n.lower() for n in sib)
        hit = [f for f in cands if any(w in words for w in FLOOR_WORDS.get(f, []))]
        if len(hit) == 1:
            cands = hit
    if len(cands) == 1:
        return ("floor", cands[0])
    if not cands:
        return ("hold", "這是網站還沒有的樓層（新的伺服器資料夾），網站標記新樓層開放後會自動合併")
    return ("hold", f"有 {len(cands)} 個樓層（第 {'、'.join(map(str, cands))} 層）都還沒有地圖，還分不出是哪一層，有新線索時會自動再判斷")


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


def write_meta(report, res, layers=None, floor=1):
    """per merge: date, explored share, total explored chunks ("chunks") and a log entry with the chunks it added.
    The site lists contributors by these numbers (the first log entry is the owner's map, its newChunks = the rest)."""
    meta = load_meta()
    f1 = meta.setdefault(str(floor), {"date": res["date"], "pct": res["pct"], "log": []})
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
