#!/usr/bin/env python3
"""Official BlueMap (saominecraft.com/bluemap) -> the site's tile pyramid, as a separate base map.

The user (2026-11-13) chose to build an "official map" base layer from the official BlueMap; the
official 2026-11-11 permission covers the site's current ways of getting data.

BlueMap low-res tiles (LOD 1): one PNG per 500 x 500 blocks, 501 x 1002 px. The top 501 rows are
the shaded top-down colour (1 px = 1 block; the last row/column overlaps the next tile), the
bottom half is height/light data (not used). Tile (x, z) pixel (i, j) = block (x*500+i, z*500+j)
(checked 2026-11-13 against tiles/f1jm L3: correlation peak at offset 0,0).
Tile URL: <base>/maps/<map>/tiles/1/<path>.png, path = "x" + digits split by "/" + "z" + ...
(BlueMap webapp pathFromCoords: x3,z8 -> x3/z8 ; x10,z8 -> x1/0/z8 ; x-3 -> x-3).

Settings seen from the cloud on 2026-11-12 17:32 UTC (saominecraft.com/bluemap/maps/palier_01/settings.json):
  name "PALIER_01 (overworld)", lowres tileSize 500, lodFactor 5, lodCount 3, hires translate [2,2].
From 20:07 UTC the same URL answered 404 and tile URLs answered 200 with an empty body
(a map name that doesn't exist answers 404), so the tiles were not obtainable from the cloud then.

Usage:
  python3 -I tools/bluemap_tiles.py fetch <work dir> [--base URL] [--map palier_01] [--range 0 10]
      downloads LOD-1 tiles one by one (1 s apart); keeps only real PNGs; prints how many were empty.
  python3 -I tools/bluemap_tiles.py build <work dir> [--floor 1] [--out tiles/f1bm]
      <work dir> holds x<X>_z<Z>.png (from fetch, or tiles someone exported); writes the 256 px
      pyramid L0..L3 like tiles/f1jm (same frame: X/Z 70, 5120 px) + meta.json.
Nothing here ever writes into tiles/f1jm (the exploration map stays JourneyMap only).
"""
import io, json, os, sys, time, urllib.request, datetime

FRAMES = {1: dict(x0=70, z0=70, full=5120)}   # same frame as tools/jm_merge.py FLOOR_CFG[1]
TS = 256
LEVELS = 4   # L3 = full px (1 block / px), L0 = full/8


def tile_path(x, z):
    def split(n):
        s = "-" if n < 0 else ""
        return s + "".join(c + "/" for c in str(abs(n)))
    return ("x" + split(x) + "z" + split(z))[:-1]


def fetch(work, base, mp, lo, hi):
    os.makedirs(work, exist_ok=True)
    got = empty = miss = 0
    for x in range(lo, hi + 1):
        for z in range(lo, hi + 1):
            url = f"{base}/maps/{mp}/tiles/1/{tile_path(x, z)}.png"
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    data = r.read()
            except Exception as e:  # 404 etc.
                miss += 1
                data = b""
            if data[:8] == b"\x89PNG\r\n\x1a\n":
                open(os.path.join(work, f"x{x}_z{z}.png"), "wb").write(data)
                got += 1
            elif data == b"":
                empty += 1
            time.sleep(1)
    print(json.dumps({"png": got, "empty": empty, "error": miss}))
    return got


def build(work, floor, out):
    from PIL import Image
    fr = FRAMES[floor]
    full = fr["full"]
    canvas = Image.new("RGB", (full, full), (0, 0, 0))
    have = Image.new("L", (full, full), 0)
    n = 0
    for fn in sorted(os.listdir(work)):
        if not (fn.startswith("x") and fn.endswith(".png") and "_z" in fn):
            continue
        x, z = (int(v) for v in fn[1:-4].split("_z"))
        im = Image.open(os.path.join(work, fn)).convert("RGBA")
        if im.size != (501, 1002):
            print("skip (size)", fn, im.size)
            continue
        col = im.crop((0, 0, 500, 500))          # drop the 1 px overlap row/column
        px, pz = x * 500 - fr["x0"], z * 500 - fr["z0"]
        a = col.getchannel("A")
        canvas.paste(col.convert("RGB"), (px, pz), a)
        have.paste(a, (px, pz), a)
        n += 1
    if not n:
        print("no tiles in", work)
        return 0
    for L in range(LEVELS):
        size = full >> (LEVELS - 1 - L)
        img = canvas if size == full else canvas.resize((size, size), Image.LANCZOS)
        hv = have if size == full else have.resize((size, size), Image.BILINEAR)
        d = os.path.join(out, str(L))
        os.makedirs(d, exist_ok=True)
        for c in range(size // TS):
            for r in range(size // TS):
                box = (c * TS, r * TS, (c + 1) * TS, (r + 1) * TS)
                if hv.crop(box).getbbox() is None:
                    continue                     # nothing there: leave the tile out
                img.crop(box).save(os.path.join(d, f"{c}_{r}.jpg"), quality=85)
    meta = dict(floor=floor, tiles=n, frame=fr, src="saominecraft.com/bluemap (BlueMap low-res LOD 1)",
                date=datetime.date.today().isoformat())
    json.dump(meta, open(os.path.join(out, "meta.json"), "w"), ensure_ascii=False)
    print(json.dumps(meta, ensure_ascii=False))
    return n


def main(a):
    def opt(k, d):
        return a[a.index(k) + 1] if k in a else d
    if len(a) < 2 or a[0] not in ("fetch", "build"):
        print(__doc__)
        return 2
    if a[0] == "fetch":
        lo, hi = (int(v) for v in (a[a.index("--range") + 1:a.index("--range") + 3] if "--range" in a else (0, 10)))
        return 0 if fetch(a[1], opt("--base", "https://saominecraft.com/bluemap"), opt("--map", "palier_01"), lo, hi) else 1
    fl = int(opt("--floor", "1"))
    return 0 if build(a[1], fl, opt("--out", f"tiles/f{fl}bm")) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
