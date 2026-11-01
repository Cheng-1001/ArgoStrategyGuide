"""The site's 「打包探索地圖」 tool (src/index.html, jmRun) end to end, on a fake JourneyMap "mp" folder.

Usage (repo root, after src/build.py): python3 tests/jm_pack_test.py   (prints ALL PASSED, exits 1 on failure)
Builds world folders from the real explored map: a floor 1 world with a new area, two other worlds with real-looking
terrain (shifted map), noise, a world that only covers unexplored land, one outside the floor and a night layer. Picks
the folder in the browser, checks which folders are recognised, downloads the zip and runs tools/jm_merge.py on a
temporary copy of the map with it (the real tiles are not touched).
"""
import functools, http.server, json, os, shutil, subprocess, sys, tempfile, threading, zipfile
from PIL import Image, ImageEnhance
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c:
        fails.append(msg)


tmp = tempfile.mkdtemp()
try:
    cv = Image.new("RGB", (5120, 5120))
    d = os.path.join(ROOT, "tiles", "f1jm", "3")
    for n in os.listdir(d):
        c, r = map(int, n[:-4].split("_"))
        cv.paste(Image.open(os.path.join(d, n)), (c * 256, r * 256))
    wiki = ImageEnhance.Brightness(Image.open(os.path.join(ROOT, "floor1.jpg")).convert("RGB").resize((4980, 4980))).enhance(1.1)
    mask = Image.open(os.path.join(ROOT, "tiles", "f1jm", "explored.png")).convert("L")

    def region(rx, rz, src, dx=0, dz=0):
        return src.crop((rx * 512 - 70 + dx, rz * 512 - 70 + dz, rx * 512 + 442 + dx, rz * 512 + 442 + dz)).convert("RGBA")

    def explored(rx, rz):
        return sum(1 for cz in range(rz * 32, rz * 32 + 32) for cx in range(rx * 32, rx * 32 + 32)
                   if 0 <= cx < 320 and 0 <= cz < 320 and mask.getpixel((cx, cz)))

    cand = sorted(((explored(rx, rz), rx, rz) for rz in range(10) for rx in range(10)), reverse=True)
    top = [(rx, rz) for _, rx, rz in cand[:3]]
    lone = next((rx, rz) for e, rx, rz in sorted(cand) if e == 0 and 1 <= rx <= 8 and 1 <= rz <= 8)
    new = next((rx, rz) for e, rx, rz in sorted(cand) if e == 0 and 1 <= rx <= 8 and 1 <= rz <= 8 and (rx, rz) != lone)
    mp = os.path.join(tmp, "mp")

    def put(folder, name, im):
        p = os.path.join(mp, folder)
        os.makedirs(p, exist_ok=True)
        im.save(os.path.join(p, name))

    n = Image.effect_noise((512, 512), 90)
    noise = Image.merge("RGB", (n, n.point(lambda v: 255 - v), n)).convert("RGBA")
    for rx, rz in top:
        put("Triggers_f1~a/overworld/day", f"{rx},{rz}.png", region(rx, rz, cv))
    put("Triggers_f1~a/overworld/day", "%d,%d.png" % new, region(*new, wiki))
    put("Triggers_f1~a/overworld/night", "%d,%d.png" % top[0], noise)
    put("Triggers_f1~a/overworld/0", "%d,%d.png" % top[0], noise)
    for i, (rx, rz) in enumerate(top):
        put("Triggers_other~b/overworld/day", f"{rx},{rz}.png", region(rx, rz, cv, 700, -400) if i != 1 else region(rx, rz, cv, -900, 300))
    for rx, rz in top:
        put("Triggers_other2~c/overworld/day", f"{rx},{rz}.png", region(rx, rz, wiki, 350, 350))
    put("Triggers_noise~d/overworld/day", "%d,%d.png" % top[0], noise)
    put("Triggers_lone~e/overworld/day", "%d,%d.png" % lone, region(*lone, wiki))
    put("Triggers_out~f/overworld/day", "40,40.png", region(*top[0], cv))
    open(os.path.join(mp, "Triggers_f1~a", "overworld", "day", "notes.txt"), "w").write("x")

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900}, accept_downloads=True)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(base + "#report"); pg.wait_for_timeout(600)
        check(pg.is_visible("#jmPick") and "journeymap\\data" in pg.inner_text("#jmPack"), "the packer is on the data page, with the folder path")
        pg.set_input_files("#jmDir", mp)
        pg.wait_for_function("window.__jm", timeout=60000)
        J = pg.evaluate("window.__jm")
        st = {g["label"]: g for g in J["groups"]}
        check(set(st) == {"Triggers_f1~a", "Triggers_other~b", "Triggers_other2~c", "Triggers_noise~d", "Triggers_lone~e", "Triggers_out~f"},
              "one entry per world folder (night / cave layers are not separate worlds)")
        check(st["Triggers_f1~a"]["state"] == "f1" and st["Triggers_f1~a"]["files"] == 4, f"the floor 1 world is recognised ({st['Triggers_f1~a']})")
        check(all(st[k]["state"] == "other" for k in ("Triggers_other~b", "Triggers_other2~c", "Triggers_noise~d")),
              "other worlds with real-looking terrain and noise are not floor 1 (" + ", ".join("%.0f" % st[k]["med"] for k in ("Triggers_other~b", "Triggers_other2~c", "Triggers_noise~d")) + ")")
        check(st["Triggers_lone~e"]["state"] == "few" and st["Triggers_out~f"]["state"] == "out", "no overlap -> cannot confirm; outside the floor -> skipped")
        t = pg.inner_text("#jmOut")
        check("找到 1 個第 1 層的資料夾" in t and "下載壓縮檔" in t, "the summary names the floor 1 folder and offers the zip")
        with pg.expect_download() as dl:
            pg.click("[data-jmpart]")
        zp = os.path.join(tmp, "up.zip")
        dl.value.save_as(zp)
        z = zipfile.ZipFile(zp)
        names = [i.filename for i in z.infolist()]
        check(z.testzip() is None and dl.value.suggested_filename.endswith(".zip"), "the download is a valid zip")
        check(names and all(nm.startswith("mp/Triggers_f1~a/overworld/day/") for nm in names) and "mp/Triggers_f1~a/overworld/day/%d,%d.png" % new in names,
              f"the zip has only floor 1 day maps, including the new area ({names})")
        check(open(os.path.join(mp, "Triggers_f1~a", "overworld", "day", "%d,%d.png" % new), "rb").read() == z.read("mp/Triggers_f1~a/overworld/day/%d,%d.png" % new),
              "files are stored byte for byte")
        # a big upload is split; every part repeats overlapping regions so the server can still verify it
        pg.evaluate("__JMP.BUDGET=1.2*1048576; __JMP.ANCHOR=40"); pg.evaluate("window.__jm=null")
        pg.set_input_files("#jmDir", mp)
        pg.wait_for_function("window.__jm", timeout=60000)
        parts = pg.evaluate("window.__jm.parts")
        check(len(parts) >= 2 and all(q["ov"] >= 40 for q in parts) and pg.locator("[data-jmpart]").count() == len(parts) and "每一份都要各送出一次表單" in pg.inner_text("#jmOut"),
              f"an upload over the size limit is split into parts ({parts})")
        pg.set_viewport_size({"width": 390, "height": 844}); pg.wait_for_timeout(200)
        check(pg.evaluate("document.documentElement.scrollWidth") <= 390, "no sideways scrolling on a phone")
        check(not errs, "no page errors" + ("" if not errs else ": " + errs[0]))
        b.close()
    srv.shutdown()
    # the server accepts what the browser packed
    w = os.path.join(tmp, "work")
    os.makedirs(os.path.join(w, "tools"))
    shutil.copy(os.path.join(ROOT, "tools", "jm_merge.py"), os.path.join(w, "tools"))
    shutil.copytree(os.path.join(ROOT, "tiles", "f1jm"), os.path.join(w, "tiles", "f1jm"))
    for f in ("floor1.jpg", "floor1_jm.jpg", "jmmeta.js"):
        shutil.copy(os.path.join(ROOT, f), w)
    r = subprocess.run([sys.executable, "-I", os.path.join(w, "tools", "jm_merge.py"), zp, "--report", "T990"], capture_output=True, text=True)
    res = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"stderr": r.stderr[-300:]}
    check(r.returncode == 0 and res.get("ok") and res.get("folders") == 1 and res.get("newChunks", 0) > 300, f"tools/jm_merge.py merges the packed zip ({res})")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
