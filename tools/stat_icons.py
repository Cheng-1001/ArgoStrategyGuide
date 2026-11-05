"""Stat / effect icons as the game's tooltips show them (heart for Health, sword for Attack Damage...), taken from the
server resource pack. Same rule as tools/recipe_icons.py (owner 2026-11-01): the pack is analysed on the owner's PC
only; GitHub gets nothing but the chosen small icons (32 px).

Run on the owner's PC (local Claude Code). The cloud session cannot reach the pack.
Tooltip icons are usually font glyphs: a font JSON (assets/<ns>/font/*.json) lists "bitmap" providers, each a PNG
atlas split into a grid of glyphs (one row per string in "chars"). Some packs use plain textures instead.

  1. Find candidates:
       python tools/stat_icons.py find "<game folder>/resourcepacks/sao.zip"
     Writes stat_icon_candidates.png (every glyph cell of every bitmap font provider + textures whose path has a stat
     keyword, each numbered) and prints what each number is. Look at it next to an in-game tooltip (F2 screenshot);
     do not commit it.
  2. Fill tools/stat_icons.json: for each key, either a texture path ("assets/x/textures/gui/heart.png")
     or a glyph {"file": "assets/x/textures/font/icons.png", "row": 0, "col": 3, "rows": 4, "cols": 16}
     (the find output prints these values). "" = keep the site's emoji.
  3. Build:  python tools/stat_icons.py build "<game folder>/resourcepacks/sao.zip"
     -> icons/stats/<key>.png and staticons.js. Then python src/build.py, python tests/smoke.py, commit, push.
"""
import json, os, re, sys, zipfile
from io import BytesIO
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "tools", "stat_icons.json")
KEYS = ("heart health mana stamina endurance sword attack damage shield defense defence crit critical speed boot "
        "dodge cooldown haste clock lifesteal life_steal vampir heal regen magic arrow projectile skill block level food").split()


def load_png(z, path):
    im = Image.open(BytesIO(z.read(path))).convert("RGBA")
    w, h = im.size
    if h > w and h % w == 0 and "/font/" not in path:   # animated texture strip: first frame
        im = im.crop((0, 0, w, w))
    return im


def glyph(im, row, col, rows, cols):
    w, h = im.size
    cw, ch = w // cols, h // rows
    g = im.crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))
    bb = g.getbbox()
    return g.crop(bb) if bb else g


def find(pack):
    z = zipfile.ZipFile(pack)
    names = set(z.namelist())
    cells = []          # (label, image, spec)
    for n in sorted(names):
        if not (n.endswith(".json") and "/font/" in n):
            continue
        try:
            js = json.loads(z.read(n).decode("utf-8", "ignore"))
        except Exception:
            continue
        for pv in js.get("providers", []):
            if pv.get("type") != "bitmap" or not pv.get("chars"):
                continue
            f = pv["file"]
            ns, _, p = f.partition(":") if ":" in f else ("minecraft", "", f)
            path = f"assets/{ns}/textures/{p}"
            if path not in names:
                continue
            rows, cols = len(pv["chars"]), max(len(r) for r in pv["chars"])
            try:
                im = load_png(z, path)
            except Exception:
                continue
            for r, line in enumerate(pv["chars"]):
                for c, ch in enumerate(line):
                    if ch in ("\u0000", " "):
                        continue
                    g = glyph(im, r, c, rows, cols)
                    if g.getbbox() is None:
                        continue
                    cells.append((f"{n} U+{ord(ch):04X}", g, {"file": path, "row": r, "col": c, "rows": rows, "cols": cols}))
    for n in sorted(names):
        if n.endswith(".png") and "/textures/" in n and "/font/" not in n and any(k in n.lower() for k in KEYS):
            try:
                cells.append((n, load_png(z, n), n))
            except Exception:
                pass
    cell, cols = 56, 16
    sheet = Image.new("RGBA", (cols * cell, ((len(cells) + cols - 1) // cols or 1) * (cell + 12)), (40, 40, 40, 255))
    d = ImageDraw.Draw(sheet)
    for i, (label, im, spec) in enumerate(cells):
        print(f"{i:4d}  {label}  {json.dumps(spec)}")
        t = im.copy()
        t.thumbnail((cell - 8, cell - 8), Image.NEAREST)
        if t.width < 16:
            t = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        x, y = (i % cols) * cell, (i // cols) * (cell + 12)
        sheet.paste(t, (x + 4, y + 4), t)
        d.text((x + 3, y + cell - 2), str(i), fill=(255, 220, 120, 255))
    sheet.save("stat_icon_candidates.png")
    print(len(cells), "candidates; sheet: stat_icon_candidates.png (do not commit)")


def build(pack):
    want = {k: v for k, v in json.load(open(MAP, encoding="utf-8")).items() if not k.startswith("_") and v}
    z = zipfile.ZipFile(pack)
    out = os.path.join(ROOT, "icons", "stats")
    os.makedirs(out, exist_ok=True)
    table = {}
    for key, spec in sorted(want.items()):
        if isinstance(spec, dict):
            im = glyph(load_png(z, spec["file"]), spec["row"], spec["col"], spec["rows"], spec["cols"])
        else:
            im = load_png(z, spec)
            bb = im.getbbox()
            im = im.crop(bb) if bb else im
        s = 32 / max(im.size)
        im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.NEAREST)
        canvas = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        canvas.paste(im, ((32 - im.width) // 2, (32 - im.height) // 2), im)
        canvas.save(os.path.join(out, key + ".png"), optimize=True)
        table[key] = f"icons/stats/{key}.png"
        print(key, "<-", spec)
    # hand-made icons (cut from screenshots, see _notes): key left empty above but the file exists -> keep them
    for key, spec in json.load(open(MAP, encoding="utf-8")).items():
        if not key.startswith("_") and not spec and os.path.exists(os.path.join(out, key + ".png")):
            table[key] = f"icons/stats/{key}.png"; print(key, "<- kept (hand-made)")
    hdr = open(os.path.join(ROOT, "staticons.js"), encoding="utf-8").read().split("window.SAO_STATICONS")[0]
    open(os.path.join(ROOT, "staticons.js"), "w", encoding="utf-8").write(
        hdr + "window.SAO_STATICONS = " + json.dumps(table, ensure_ascii=False, indent=1) + ";\n")
    print(len(table), "icons written")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("find", "build"):
        sys.exit(__doc__)
    find(sys.argv[2]) if sys.argv[1] == "find" else build(sys.argv[2])
