"""Merge a player's JourneyMap upload into the floor 1 explored map (tiles/f1jm) without a full rebuild.

Usage:
  python3 -I tools/jm_merge.py <upload.zip | folder> [--report R0005] [--date YYYY-MM-DD] [--min-overlap 20]
  python3 -I tools/jm_merge.py --init-mask        (one-off: derive the explored mask from the current tiles)

The upload holds JourneyMap "day" folders: region images "x,z.png" (512 x 512, 1 block = 1 px, region x,z starts at
block x*512, z*512). The site's 「打包探索地圖」 tool builds it from the player's whole journeymap/data/mp folder
(one sub-folder per world the player visited; only the floor 1 ones are packed), but a hand-made zip works too:
images are grouped by the folder they are in and only folders named "day" (or the zip root) are used, so night /
topo / cave layers are ignored. Run by .github/workflows/jm_merge.yml for every 「探索地圖」 report (approved
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
NAME = re.compile(r"(?:^|/)(-?\d+),(-?\d+)\.png$")
MAX_REGIONS, MAX_BYTES = 600, 4 * 1024 * 1024
MIN_OVERLAP = 20   # explored chunks a folder must cover (with matching colours) before it is accepted as floor 1
C0, C1 = X0 // CH, (X0 + SIZE - 1) // CH          # chunk range inside the frame (inclusive)


def out(code, **kw):
    print(json.dumps(kw, ensure_ascii=False))
    sys.exit(code)


def load_canvas():
    cv = Image.new("RGB", (FULL, FULL), BG)
    for name in os.listdir(os.path.join(TILES, "3")):
        m = re.fullmatch(r"(\d+)_(\d+)\.jpg", name)
        if m:
            cv.paste(Image.open(os.path.join(TILES, "3", name)).convert("RGB"), (int(m[1]) * T, int(m[2]) * T))
    return cv


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


def read_upload(src):
    """[{"name", "date", "regions": [(rx, rz, RGBA image)]}], one entry per folder; raises ValueError with a reason
    players can understand. Only images directly in a folder named "day" (or at the top level) are used."""
    found = {}   # folder -> [(rx, rz, bytes, mtime)]

    def take(folder, name, size, read, mtime):
        parent = os.path.basename(folder.rstrip("/"))
        if folder and parent.lower() != "day":
            return
        m = NAME.search("/" + name)
        if not m:
            return
        if size > MAX_BYTES:
            raise ValueError(f"{name} 超過 4 MB，不像 JourneyMap 的地圖圖片")
        found.setdefault(folder, []).append((int(m[1]), int(m[2]), read, mtime))

    if os.path.isdir(src):
        for dirpath, _, files in os.walk(src):
            rel = os.path.relpath(dirpath, src).replace(os.sep, "/")
            rel = "" if rel == "." else rel
            for f in sorted(files):
                fp = os.path.join(dirpath, f)
                take(rel, f, os.path.getsize(fp), (lambda fp=fp: open(fp, "rb").read()), os.path.getmtime(fp))
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
    if os.path.isdir(src):
        found = {k: [(rx, rz, rd(), t) for rx, rz, rd, t in v] for k, v in found.items()}
        if sum(len(v) for v in found.values()) > MAX_REGIONS:
            raise ValueError(f"資料夾裡有超過 {MAX_REGIONS} 張地圖圖片")
    if not found:
        raise ValueError("壓縮檔裡沒有 JourneyMap 的白天地圖（day 資料夾裡 3,7.png 這種檔案）。請用網站協作區的「打包探索地圖」產生壓縮檔")
    groups = []
    for folder, items in found.items():
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
        groups.append({"name": folder_label(folder), "date": max(t for *_, t in items), "regions": regions})
    return groups


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


def main(argv):
    if "--init-mask" in argv:
        return init_mask()
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
    accepted, skipped = [], []
    for g in groups:
        inside = [(rx, rz, im) for rx, rz, im in g["regions"]
                  if rx * 512 < X0 + SIZE and rz * 512 < X0 + SIZE and rx * 512 + 512 > X0 and rz * 512 + 512 > X0]
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
    mask.save(MASK, optimize=True)
    for tx, ty in touched:
        save_tile(cv.crop((tx * T, ty * T, tx * T + T, ty * T + T)), os.path.join(TILES, "3", f"{tx}_{ty}.jpg"))
    for L, size in enumerate((640, 1280, 2560)):
        im = cv.resize((size, size), Image.LANCZOS)
        for r in range(size // T + (size % T > 0)):
            for c in range(size // T + (size % T > 0)):
                if c * T * FULL // size >= SIZE or r * T * FULL // size >= SIZE:
                    continue
                save_tile(im.crop((c * T, r * T, c * T + T, r * T + T)), os.path.join(TILES, str(L), f"{c}_{r}.jpg"))
    cv.crop((0, 0, SIZE, SIZE)).resize((3000, 3000), Image.LANCZOS).save(os.path.join(ROOT, "floor1_jm.jpg"), quality=85, optimize=True)
    explored = sum(1 for cz in range(C0, C1 + 1) for cx in range(C0, C1 + 1) if mask.getpixel((cx, cz)))
    pct = round(100 * explored / (C1 - C0 + 1) ** 2, 1)
    res = {"ok": True, "regions": sum(len(g["inside"]) for g in accepted), "newChunks": len(new_chunks),
           "overlap": sum(g["overlap"] for g in accepted), "pct": pct, "date": date,
           "folders": len(accepted), "skipped": len(skipped)}
    write_meta(report, dict(res, chunks=explored))
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


def write_meta(report, res):
    """per merge: date, explored share, total explored chunks ("chunks") and a log entry with the chunks it added.
    The site lists contributors by these numbers (the first log entry is the owner's map, its newChunks = the rest)."""
    meta = load_meta()
    f1 = meta.setdefault("1", {"date": res["date"], "pct": res["pct"], "log": []})
    f1["date"], f1["pct"] = res["date"], res["pct"]
    f1["chunks"] = res.get("chunks", f1.get("chunks"))
    if f1["log"] and f1["log"][0].get("report") is None and "newChunks" not in f1["log"][0] and f1.get("chunks"):
        f1["log"][0]["newChunks"] = f1["chunks"] - res["newChunks"] - sum(e.get("newChunks", 0) for e in f1["log"][1:])
    f1["log"].append({"report": report, "date": res["date"], "regions": res["regions"], "newChunks": res["newChunks"]})
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
