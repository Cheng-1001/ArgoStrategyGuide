"""Redraw the darkened wiki background of the floor 1 explored map after floor1.jpg was replaced.

The explored-map tiles (tiles/f1jm) are JourneyMap terrain on top of a darkened copy of the wiki map. When the wiki map
changes, run this once: every 16 x 16 chunk that is NOT marked explored in tiles/f1jm/explored.png gets the darkened
new floor1.jpg; explored chunks (the players' JourneyMap data) are kept as they are. Then levels 0-2 and floor1_jm.jpg
are rebuilt from level 3, exactly like tools/jm_merge.py does after a merge. jmmeta.js is not touched.

Usage (from the repo root):  python3 -I tools/jm_rebase.py
"""
import importlib.util, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("jm_merge", os.path.join(HERE, "jm_merge.py"))
jm = importlib.util.module_from_spec(spec); spec.loader.exec_module(jm)


def main():
    cv = jm.load_canvas()                                   # FULL x FULL, pixel = block - X0
    dark = jm.dark_base()                                   # SIZE x SIZE, same origin
    # explored chunks as a canvas-sized mask (explored.png: 1 px = 16 blocks, from block 0)
    m = Image.open(jm.MASK).convert("L").resize((jm.MW * jm.CH, jm.MW * jm.CH), Image.NEAREST)
    m = m.crop((jm.X0, jm.X0, jm.X0 + jm.SIZE, jm.X0 + jm.SIZE))
    keep_wiki = m.point(lambda v: 0 if v else 255)          # 255 where the chunk is unexplored
    cv.paste(dark, (0, 0), keep_wiki)
    n = 0
    for ty in range((jm.SIZE + jm.T - 1) // jm.T):
        for tx in range((jm.SIZE + jm.T - 1) // jm.T):
            jm.save_tile(cv.crop((tx * jm.T, ty * jm.T, tx * jm.T + jm.T, ty * jm.T + jm.T)),
                         os.path.join(jm.TILES, "3", f"{tx}_{ty}.jpg")); n += 1
    for L, size in enumerate((640, 1280, 2560)):
        im = cv.resize((size, size), Image.LANCZOS)
        for r in range(size // jm.T + (size % jm.T > 0)):
            for c in range(size // jm.T + (size % jm.T > 0)):
                if c * jm.T * jm.FULL // size >= jm.SIZE or r * jm.T * jm.FULL // size >= jm.SIZE:
                    continue
                jm.save_tile(im.crop((c * jm.T, r * jm.T, c * jm.T + jm.T, r * jm.T + jm.T)),
                             os.path.join(jm.TILES, str(L), f"{c}_{r}.jpg"))
    cv.crop((0, 0, jm.SIZE, jm.SIZE)).resize((3000, 3000), Image.LANCZOS).save(
        os.path.join(jm.ROOT, "floor1_jm.jpg"), quality=85, optimize=True)
    print(f"rebased {n} level-3 tiles; levels 0-2 and floor1_jm.jpg rebuilt")


if __name__ == "__main__":
    main()
