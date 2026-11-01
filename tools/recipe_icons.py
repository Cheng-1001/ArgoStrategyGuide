"""Small icons for recipes the official item catalogue does not have, taken from the server resource pack.

ON HOLD (2026-11-01): the server's Terms of Use (art. 5) forbid copying, extracting or reproducing any part of
the Services without written authorisation. Do not run this until the owner has decided (see CLAUDE.md).

Run on the owner's PC (local Claude Code). The cloud session cannot reach the pack.
The pack (resourcepacks/sao.zip) holds paid assets: copy ONLY the icons listed in tools/recipe_icons.json,
each scaled to 48 px. Never commit the pack, other textures, models or the candidate sheet.

  1. Find candidates (textures and item models whose path or text matches the keywords):
       python tools/recipe_icons.py find "<game folder>/resourcepacks/sao.zip" [keyword ...]
     Default keywords: potion mana stamina quality qualite teleport kobold purification elixir crystal cristal.
     Writes recipe_icon_candidates.png (numbered contact sheet) in the current folder: look at it, do not commit it.
  2. Put the chosen texture path for each recipe in tools/recipe_icons.json ("" = leave the placeholder).
     Check against the in-game crafting menu (F2 screenshot) when unsure; a wrong icon is worse than a placeholder.
  3. Build:  python tools/recipe_icons.py build "<game folder>/resourcepacks/sao.zip"
     -> icons/recipes/<slug>.png and recicons.js. Then python src/build.py, python tests/smoke.py, commit, push.
"""
import json, os, re, sys, zipfile
from io import BytesIO
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "tools", "recipe_icons.json")
KEYS = "potion mana stamina quality qualite teleport kobold purification elixir crystal cristal".split()


def first_frame(im):
    im = im.convert("RGBA")
    w, h = im.size
    if h > w and h % w == 0:            # animated texture strip: keep the first frame
        im = im.crop((0, 0, w, w))
    return im


def find(pack, keys):
    keys = [k.lower() for k in keys] or KEYS
    z = zipfile.ZipFile(pack)
    names = z.namelist()
    hit = [n for n in names if n.endswith(".png") and "/textures/" in n and any(k in n.lower() for k in keys)]
    # item models that mention a keyword point at their textures
    for n in names:
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
    sheet.save("recipe_icon_candidates.png")
    print(len(hit), "candidates; sheet: recipe_icon_candidates.png (do not commit)")


def build(pack):
    want = {k: v for k, v in json.load(open(MAP, encoding="utf-8")).items() if not k.startswith("_") and v}
    z = zipfile.ZipFile(pack)
    out_dir = os.path.join(ROOT, "icons", "recipes")
    os.makedirs(out_dir, exist_ok=True)
    table = {}
    for name, path in sorted(want.items()):
        im = first_frame(Image.open(BytesIO(z.read(path)))).resize((48, 48), Image.NEAREST)
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        im.save(os.path.join(out_dir, slug + ".png"), optimize=True)
        table[name] = f"icons/recipes/{slug}.png"
        print(name, "<-", path)
    hdr = open(os.path.join(ROOT, "recicons.js"), encoding="utf-8").read().split("window.SAO_RECICONS")[0]
    open(os.path.join(ROOT, "recicons.js"), "w", encoding="utf-8").write(
        hdr + "window.SAO_RECICONS = " + json.dumps(table, ensure_ascii=False, indent=1) + ";\n")
    print(len(table), "icons written")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("find", "build"):
        sys.exit(__doc__)
    find(sys.argv[2], sys.argv[3:]) if sys.argv[1] == "find" else build(sys.argv[2])
