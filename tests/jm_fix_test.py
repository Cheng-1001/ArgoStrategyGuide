"""The site's 「修復分流地圖」 tool (src/index.html, jmFixRun) end to end, on a fake JourneyMap "mp" folder.

Usage (repo root, after src/build.py): python3 tests/jm_fix_test.py   (prints ALL PASSED, exits 1 on failure)
Three floor-3 server instances cut from the site's floor-3 explored map, each holding a different part of it (one folder
has an id the site has never seen), plus a lone floor-1 world and a noise world. Picks the folder in the browser,
downloads the zip and checks: only the floor-3 folders get images, each image is the union of every copy (PIL
alpha_composite), images a folder already has unchanged are left out, square 0,-1 and waypoints are never touched.
"""
import functools, http.server, io, os, shutil, sys, tempfile, threading, zipfile
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c:
        fails.append(msg)


tmp = tempfile.mkdtemp()
try:
    # floor 3 canvas (frame -253 / -79, as FLOOR_CFG in tools/jm_merge.py)
    X0, Z0, FULL = -253, -79, 1792
    cv = Image.new("RGB", (FULL, FULL))
    d = os.path.join(ROOT, "tiles", "f3jm", "3")
    for n in os.listdir(d):
        a, b = map(int, n[:-4].split("_"))
        cv.paste(Image.open(os.path.join(d, n)), (a * 256, b * 256))
    m3 = Image.open(os.path.join(ROOT, "tiles", "f3jm", "explored.png")).convert("L")
    mx0, mz0 = X0 // 16, Z0 // 16

    def expl(rx, rz):
        return sum(1 for cz in range(rz * 32, rz * 32 + 32) for cx in range(rx * 32, rx * 32 + 32)
                   if 0 <= cx - mx0 < m3.width and 0 <= cz - mz0 < m3.height and m3.getpixel((cx - mx0, cz - mz0)))

    def cut(rx, rz, box=None):
        im = cv.crop((rx * 512 - X0, rz * 512 - Z0, rx * 512 - X0 + 512, rz * 512 - Z0 + 512)).convert("RGBA")
        if box:   # keep only this part, the rest clear (not drawn yet)
            keep = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            keep.paste(im.crop(box), box[:2])
            im = keep
        return im

    regs = [r for _, *r in sorted(((expl(rx, rz), rx, rz) for rx in range(-1, 3) for rz in range(-1, 4) if (rx, rz) != (0, -1)), reverse=True)[:3]]
    R1, R2, R3 = map(tuple, regs)
    mp = os.path.join(tmp, "mp")
    A, B, C = ("Triggers_95a78a58~76fa~4903~92aa~8a87c523440c", "Triggers_fix00001~b", "Triggers_fix00002~c")

    def put(folder, rel, im, t):
        p = os.path.join(mp, folder, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        im.save(p)
        os.utime(p, (t, t))
        return p

    T = 1_790_000_000
    put(A, "overworld/day/%d,%d.png" % R1, cut(*R1), T)
    put(A, "overworld/day/%d,%d.png" % R2, cut(*R2, (0, 0, 512, 256)), T)
    put(A, "overworld/night/%d,%d.png" % R1, cut(*R1, (0, 0, 256, 512)), T)
    put(A, "overworld/day/0,-1.png", cut(0, -1, (0, 0, 512, 200)), T)
    put(B, "overworld/day/%d,%d.png" % R1, cut(*R1, (256, 0, 512, 512)), T + 100)
    put(B, "overworld/day/%d,%d.png" % R2, cut(*R2, (0, 200, 512, 512)), T + 100)
    put(B, "overworld/day/%d,%d.png" % R3, cut(*R3), T + 100)
    put(B, "overworld/night/%d,%d.png" % R1, cut(*R1, (200, 0, 512, 512)), T + 100)
    put(B, "overworld/day/0,-1.png", Image.new("RGBA", (512, 512), (20, 160, 40, 255)), T + 100)   # the login world
    put(C, "overworld/day/%d,%d.png" % R3, cut(*R3, (0, 0, 300, 300)), T + 200)
    put(C, "overworld/day/%d,%d.png" % R1, cut(*R1), T + 200)                                     # already whole
    put(C, "overworld/4/%d,%d.png" % R3, cut(*R3, (100, 100, 200, 200)), T + 200)                  # a cave layer only C has
    os.makedirs(os.path.join(mp, B, "waypoints"), exist_ok=True)
    open(os.path.join(mp, B, "waypoints", "WaypointData.dat"), "wb").write(b"x")
    # a lone floor-1 world (one folder: nothing to do) and a noise world (no floor)
    c1 = Image.new("RGB", (5120, 5120))
    for n in os.listdir(os.path.join(ROOT, "tiles", "f1jm", "3")):
        a, b = map(int, n[:-4].split("_"))
        c1.paste(Image.open(os.path.join(ROOT, "tiles", "f1jm", "3", n)), (a * 256, b * 256))
    put("Triggers_815bd3d6~f22f~4114~a601~dfcf0a106221", "overworld/day/4,4.png", c1.crop((4 * 512 - 70, 4 * 512 - 70, 4 * 512 + 442, 4 * 512 + 442)).convert("RGBA"), T)
    n = Image.effect_noise((512, 512), 90)
    put("Triggers_noise~d", "overworld/day/%d,%d.png" % R1, Image.merge("RGB", (n, n, n)).convert("RGBA"), T)

    def load(folder, rel):
        p = os.path.join(mp, folder, *rel.split("/"))
        return Image.open(p).convert("RGBA") if os.path.exists(p) else None

    def expect():
        keys = set()
        for f in (A, B, C):
            for dp, _, fn in os.walk(os.path.join(mp, f, "overworld")):
                for x in fn:
                    keys.add(os.path.relpath(os.path.join(dp, x), os.path.join(mp, f)).replace("\\", "/"))
        out = {}
        for k in sorted(keys):
            if k.endswith("/0,-1.png"):
                continue
            base = None
            for f in (A, B, C):   # oldest first
                im = load(f, k)
                if im is not None:
                    base = im if base is None else Image.alpha_composite(base, im)
            for f in (A, B, C):
                own = load(f, k)
                if own is None or own.tobytes() != base.tobytes():
                    out[f + "/" + k] = base
        return out

    want = expect()

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900}, accept_downloads=True)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html#report"); pg.wait_for_timeout(600)
        check(pg.locator("#jmFix").count() == 1 and pg.locator("#jmFixDir").count() == 1, "the 修復分流地圖 card is on the report page")
        pg.set_input_files("#jmFixDir", mp)
        pg.wait_for_function("window.__jmFix", timeout=60000)
        r = pg.evaluate("window.__jmFix")
        fl = {s["floor"]: s for s in r["floors"]}
        check(sorted(fl.get(3, {}).get("folders", [])) == sorted([A, B, C]), f"the three floor-3 folders are found (new ids by colour): {fl.get(3)}")
        check(fl.get(1, {}).get("folders") == ["Triggers_815bd3d6~f22f~4114~a601~dfcf0a106221"] and fl[1]["n"] == 0, "a lone floor-1 world is left alone")
        check(r["unknown"] == ["Triggers_noise~d"], f"the noise world is listed as unknown: {r['unknown']}")
        check(sorted(r["names"]) == sorted(want), f"the zip holds exactly the images that change ({len(r['names'])} vs {len(want)})")
        check(not any("0,-1" in x or "waypoints" in x for x in r["names"]), "square 0,-1 and waypoints are never in the zip")
        check(not any(x.startswith("Triggers_noise") or x.startswith("Triggers_815") for x in r["names"]), "other floors are not touched")
        txt = pg.inner_text("#jmFixOut")
        check("第 3 層" in txt and "補 " in txt and "不用修復" in txt and "認不出" in txt, "the result lists each floor")
        with pg.expect_download() as dl:
            pg.click("#jmFixGo")
        z = zipfile.ZipFile(io.BytesIO(open(dl.value.path(), "rb").read()))
        names = z.namelist()
        check(sorted(names) == sorted(want) and dl.value.suggested_filename.startswith("jm_fix_"), "the download matches")
        bad = [k for k in names if k in want and Image.open(io.BytesIO(z.read(k))).convert("RGBA").tobytes() != want[k].tobytes()]
        check(not bad, f"every image is pixel-for-pixel the union of all copies (differs: {bad[:3]})")
        # nothing more to do once the zip is copied in
        for k in names:
            q = os.path.join(mp, *k.split("/"))
            os.makedirs(os.path.dirname(q), exist_ok=True)
            open(q, "wb").write(z.read(k))
        pg.evaluate("window.__jmFix=null"); pg.set_input_files("#jmFixDir", mp)
        pg.wait_for_function("window.__jmFix", timeout=60000)
        r2 = pg.evaluate("window.__jmFix")
        check(r2["names"] == [] and "不用修復" in pg.inner_text("#jmFixNote"), "running it again on the fixed folder finds nothing to do")
        check(not errs, f"no page errors: {errs[:2]}")
        b.close()
    srv.shutdown()
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("ALL PASSED" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
