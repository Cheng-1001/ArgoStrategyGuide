"""Rebuild the floor 1 explored map from JourneyMap day tiles, then cut it into map tiles.

Usage:  python3 tools/jm_tiles.py <journeymap .../overworld/day folder> [--date YYYY-MM-DD]

Input: JourneyMap region images "x,z.png" (512x512, 1 block = 1 px, region x,z starts at block x*512, z*512).
Steps: paste every region at its world position, crop to the map frame [70, 5050] (4980 px, same frame as
floor1.jpg), lay it over floor1.jpg darkened (colour 0.35, brightness 0.45), then write
  floor1_jm.jpg            3000 px preview (kept for reference)
  tiles/f1jm/{L}/{c}_{r}.jpg  256 px JPEG tiles, levels 0..3 = 640, 1280, 2560, 5120 px (image padded to 5120)
After running, set jmDate in src/index.html (floor 1 map config) and run src/build.py.
The floor 1 world folder is Triggers_815bd3d6-f22f-4114-a601-dfcf0a106221 (overworld).
"""
import glob, os, re, shutil, sys
from PIL import Image, ImageEnhance

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
X0, SIZE, FULL, T = 70, 4980, 5120, 256

src = sys.argv[1]
jm = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
n = 0
for f in glob.glob(os.path.join(src, "*.png")):
    m = re.fullmatch(r"(-?\d+),(-?\d+)\.png", os.path.basename(f))
    if not m:
        continue
    ox, oz = int(m[1]) * 512 - X0, int(m[2]) * 512 - X0
    if ox >= SIZE or oz >= SIZE or ox + 512 <= 0 or oz + 512 <= 0:
        continue
    im = Image.open(f).convert("RGBA")
    jm.paste(im, (ox, oz), im)
    n += 1
base = Image.open(os.path.join(ROOT, "floor1.jpg")).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
base = ImageEnhance.Brightness(ImageEnhance.Color(base).enhance(0.35)).enhance(0.45).convert("RGBA")
base.alpha_composite(jm)
full = base.convert("RGB")
full.resize((3000, 3000), Image.LANCZOS).save(os.path.join(ROOT, "floor1_jm.jpg"), quality=85, optimize=True)

out = os.path.join(ROOT, "tiles", "f1jm")
if os.path.exists(out):
    shutil.rmtree(out)
pad = Image.new("RGB", (FULL, FULL), (7, 12, 17))
pad.paste(full, (0, 0))
cnt = tot = 0
for L, size in enumerate((640, 1280, 2560, 5120)):
    im = pad if size == FULL else pad.resize((size, size), Image.LANCZOS)
    os.makedirs(os.path.join(out, str(L)), exist_ok=True)
    k = -(-size // T)
    for r in range(k):
        for c in range(k):
            if c * T * FULL // size >= SIZE or r * T * FULL // size >= SIZE:
                continue
            p = os.path.join(out, str(L), f"{c}_{r}.jpg")
            im.crop((c * T, r * T, c * T + T, r * T + T)).save(p, quality=80, optimize=True, progressive=True)
            cnt += 1
            tot += os.path.getsize(p)
print(f"{n} JourneyMap regions -> {cnt} tiles, {tot / 1e6:.1f} MB")
