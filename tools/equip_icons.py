"""Icons for equipment the official item catalogue does not have (Elite Treant / Shark / Ice Golem / Ice Spirit / Nepenthes /
Spider accessories, quivers, Galiath's weapons, Rhitta, Lostvayne...), taken from the server resource pack.

Same rule as tools/recipe_icons.py (owner's decision 2026-11-01): the pack is analysed on the owner's PC only;
GitHub gets nothing but the chosen icons, each scaled to 64 px. Never commit the pack, other textures, models or the
candidate sheet. The cloud session cannot reach the pack.

Why (2026-11-06): icons cut from screenshots were blurry (the 16 px texture is scaled by a non-integer factor on screen).
The cloud session rebuilt the ones with a big enough screenshot onto the 16 px pixel grid; the pack has the exact textures,
so an icon chosen here replaces the rebuilt one.

Run on the owner's PC (local Claude Code):
  1. Find candidates (textures and item models whose path or text matches the keywords):
       python tools/equip_icons.py find "<game folder>/resourcepacks/sao.zip" [keyword ...]
     Default keywords: the "_kw" list in tools/equip_icons.json (shark requin nepenthes spider araignee glacial frozen glace
     elite treant albal quiver carquois galiath colosse rhitta lostvayne nodachi...).
     Writes equip_icon_candidates.png (numbered contact sheet) in the current folder: look at it, do not commit it.
  2. Put the chosen texture path for each item in tools/equip_icons.json ("" = keep what the site has now).
     Compare with the in-game auction house / crafting window; a wrong icon is worse than a placeholder.
  3. Build:  python tools/equip_icons.py build "<game folder>/resourcepacks/sao.zip"
     -> icons/game/<slug>.png and the "equip_icons.py" block of gameicons.js (these names are removed from the rest of
     the file, so the pack icon wins). Then python src/build.py, python tests/smoke.py, commit, push.
"""
import json, os, re, sys, zipfile
from io import BytesIO
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "tools", "equip_icons.json")
JS = os.path.join(ROOT, "gameicons.js")
BEGIN, END = " // equip_icons.py BEGIN (resource pack, owner's PC)", " // equip_icons.py END"


def first_frame(im):
    im = im.convert("RGBA")
    w, h = im.size
    if h > w and h % w == 0:            # animated texture strip: keep the first frame
        im = im.crop((0, 0, w, w))
    return im


def find(pack, keys):
    keys = [k.lower() for k in keys] or json.load(open(MAP, encoding="utf-8"))["_kw"]
    z = zipfile.ZipFile(pack)
    names = z.namelist()
    hit = [n for n in names if n.endswith(".png") and "/textures/" in n and any(k in n.lower() for k in keys)]
    for n in names:                     # item models that mention a keyword point at their textures
        if n.endswith(".json") and "/models/" in n:
            try:
                txt = z.read(n).decode("utf-8", "ignore")
            except Exception:
                continue
            if any(k in n.lower() or k in txt.lower() for k in keys):
                for tex in re.findall(r'"(?:layer\d|texture|all|particle)"\s*:\s*"([^"]+)"', txt):
                    ns, _, p = tex.partition(":") if ":" in tex else ("minecraft", "", tex)
                    cand = f"assets/{ns}/textures/{p}.png"
                    if cand in names and cand not in hit:
                        hit.append(cand)
                        print(f"  model {n} -> {cand}")
    hit.sort()
    cell, cols = 72, 10
    sheet = Image.new("RGBA", (cols * cell, ((len(hit) + cols - 1) // cols or 1) * (cell + 14)), (40, 40, 40, 255))
    d = ImageDraw.Draw(sheet)
    for i, n in enumerate(hit):
        print(f"{i:3d}  {n}")
        try:
            im = first_frame(Image.open(BytesIO(z.read(n)))).resize((cell - 8, cell - 8), Image.NEAREST)
        except Exception:
            continue
        x, y = (i % cols) * cell, (i // cols) * (cell + 14)
        sheet.paste(im, (x + 4, y + 4), im)
        d.text((x + 4, y + cell), str(i), fill=(255, 220, 120, 255))
    sheet.save("equip_icon_candidates.png")
    print(len(hit), "candidates; sheet: equip_icon_candidates.png (do not commit)")


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower().replace("é", "e").replace("'", "")).strip("_")


def build(pack):
    want = {k: v for k, v in json.load(open(MAP, encoding="utf-8")).items() if not k.startswith("_") and v}
    z = zipfile.ZipFile(pack)
    os.makedirs(os.path.join(ROOT, "icons", "game"), exist_ok=True)
    table = {}
    for name, path in sorted(want.items()):
        im = first_frame(Image.open(BytesIO(z.read(path))))
        im = im.resize((64, 64), Image.NEAREST)
        out = f"icons/game/{slug(name)}.png"
        im.save(os.path.join(ROOT, out), optimize=True)
        table[name] = out
        print(name, "<-", path)
    js = open(JS, encoding="utf-8").read()
    js = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n", "", js, flags=re.S)
    keep = [l for l in js.split("\n") if not any(l.strip().startswith(json.dumps(n, ensure_ascii=False) + ":") for n in table)]
    js = "\n".join(keep)
    block = BEGIN + "\n" + "".join(f" {json.dumps(n, ensure_ascii=False)}: {json.dumps(p)},\n" for n, p in sorted(table.items())) + END + "\n"
    js = js.replace("\n};", ",\n" + block + "};", 1) if table else js
    js = re.sub(r",\s*,", ",", js)
    open(JS, "w", encoding="utf-8").write(js)
    print(len(table), "icons written")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("find", "build"):
        sys.exit(__doc__)
    find(sys.argv[2], sys.argv[3:]) if sys.argv[1] == "find" else build(sys.argv[2])
