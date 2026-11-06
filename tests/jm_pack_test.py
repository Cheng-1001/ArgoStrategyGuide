"""The site's 「打包探索地圖」 tool (src/index.html, jmRun) end to end, on a fake JourneyMap "mp" folder.

Usage (repo root, after src/build.py): python3 tests/jm_pack_test.py   (prints ALL PASSED, exits 1 on failure)
Builds world folders from the real explored map: a floor 1 world with a new area, two other worlds with real-looking
terrain (shifted map), noise, a world that only covers unexplored land, one outside the floor and a night layer. Picks
the folder in the browser, checks which folders are recognised, downloads the zip and runs tools/jm_merge.py on a
temporary copy of the map with it (the real tiles are not touched). Height layers (2026-11-06): cave folders "0", "1",
"2" of the floor 1 world are found and packed; unticking a layer, packing only layers (surface anchors are added) and
an X/Z box change the zip; the file cap splits a pack.
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
    cave = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    cave.paste(Image.new("RGBA", (90, 40), (120, 200, 60, 255)), (230, 70))   # a lit room (the ink room is in layer 1 at 5,9)
    put("Triggers_f1~a/overworld/1", "5,9.png", cave)
    for i in range(6):                                                           # layer 2: six small regions (file cap test)
        put("Triggers_f1~a/overworld/2", f"{i + 1},2.png", cave)
    put("Triggers_f1~a/overworld/2", "40,40.png", cave)                          # outside the floor: never packed
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
        check(J["found"].get("c1") == 1 and J["found"].get("c2") == 6 and J["found"].get("c0") == 1 and J["found"].get("day", 0) >= 1,
              f"the height layers of the floor 1 world are found ({J['found']})")
        check(st["Triggers_f1~a"]["layers"]["c2"]["files"] == 7 and sorted(J["sel"]["layers"]) == ["c0", "c1", "c2", "day"],
              "every layer is ticked to start with; a region outside the floor is not counted")
        if os.environ.get("SHOT_DIR"):
            pg.locator("#jmOut").scroll_into_view_if_needed()
            pg.screenshot(path=os.path.join(os.environ["SHOT_DIR"], "pack_card.png"))
        lt = pg.inner_text("#jmOut")
        check("地面 3 張" in lt and "地底洞穴 8 張" in lt and not pg.locator("#jmOut input").count(),
              "no height or coordinate fields: the summary counts surface and underground maps")
        regs = pg.eval_on_selector_all("[data-jmreg]", "e=>e.map(x=>x.dataset.jmreg)")
        check("5,9" in regs and "2,2" in regs and "40,40" not in regs and pg.locator(".jmmap .jmtown").count() >= 5
              and "已選 %d／%d 格" % (len(regs), len(regs)) in lt, f"the squares with new data are on a small map with town names ({regs})")
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
        check(names and all(nm.startswith("mp/Triggers_f1~a/overworld/") for nm in names) and "mp/Triggers_f1~a/overworld/day/%d,%d.png" % new in names
              and "mp/Triggers_f1~a/overworld/1/5,9.png" in names and sum(nm.startswith("mp/Triggers_f1~a/overworld/2/") for nm in names) == 6
              and "mp/Triggers_f1~a/overworld/2/40,40.png" not in names and not any("/night/" in nm for nm in names),
              f"the zip has floor 1 surface and height-layer maps, including the new area ({names})")
        check(open(os.path.join(mp, "Triggers_f1~a", "overworld", "day", "%d,%d.png" % new), "rb").read() == z.read("mp/Triggers_f1~a/overworld/day/%d,%d.png" % new),
              "files are stored byte for byte")
        def names_now():
            return pg.evaluate("window.__jm.parts.flatMap(p=>p.names)")
        # only the ink room square (layer 1, region 5,9): that square plus surface anchors from elsewhere
        pg.click("#jmRegNone"); pg.wait_for_timeout(100)
        check(not pg.locator("[data-jmpart]").count() and "請在下面的地圖上點選方格" in pg.inner_text("#jmOut"), "nothing picked -> no download, the note says what to do")
        pg.click("[data-jmreg='5,9']", force=True); pg.wait_for_timeout(100)
        J2 = pg.evaluate("window.__jm")
        nn = names_now()
        inside = [x for x in nn if x.endswith("/5,9.png")]
        anchors = [x for x in nn if not x.endswith("/5,9.png")]
        check("mp/Triggers_f1~a/overworld/1/5,9.png" in inside and all("/day/" in x for x in anchors) and J2["parts"][0]["ov"] >= 60
              and (J2["parts"][0]["anchors"] >= 1 and "另含" in pg.inner_text("#jmOut") if not any("/day/" in x for x in inside) else True)
              and "已選 1／" in pg.inner_text("#jmRegSum"),
              f"one square with only underground data carries surface anchors ({J2['parts']}, {pg.inner_text('#jmRegSum')})")
        with pg.expect_download() as dl2:
            pg.click("[data-jmpart]")
        zl = os.path.join(tmp, "layer.zip")
        dl2.value.save_as(zl)
        pg.click("[data-jmreg='5,9']", force=True); pg.click("[data-jmreg='2,2']", force=True); pg.wait_for_timeout(100)
        nn = names_now()
        packed = [x for x in nn if "/overworld/2/" in x]
        check(packed == ["mp/Triggers_f1~a/overworld/2/2,2.png"] and "/overworld/1/5,9.png" not in " ".join(nn)
              and pg.get_attribute("[data-jmreg='5,9']", "aria-checked") == "false", f"clicking squares changes what is packed ({packed})")
        pg.click("#jmRegAll"); pg.wait_for_timeout(100)
        check(pg.evaluate("window.__jm.sel.off") == [] and len(names_now()) == len(names), "全部選 packs everything again")
        if os.environ.get("SHOT_DIR"):
            pg.click("[data-jmreg='2,2']", force=True); pg.wait_for_timeout(100)
            pg.locator(".jmmap").scroll_into_view_if_needed()
            pg.screenshot(path=os.path.join(os.environ["SHOT_DIR"], "pack_map.png"))
            pg.click("#jmRegAll"); pg.wait_for_timeout(100)
        pg.evaluate("__JMP.MAXN=8"); pg.click("#jmRegAll"); pg.wait_for_timeout(100)
        cp = pg.evaluate("window.__jm.parts")
        check(len(cp) >= 2 and all(q["n"] <= 8 and q["ov"] >= 60 for q in cp), f"the file cap splits a pack, every part verifiable ({[(q['n'], q['ov']) for q in cp]})")
        pg.evaluate("__JMP.MAXN=1500")
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
    check(set(res.get("layers", {})) == {"c0", "c1", "c2"} and res["layers"]["c1"] > 0, f"... and its height layers ({res.get('layers')})")
    r = subprocess.run([sys.executable, "-I", os.path.join(w, "tools", "jm_merge.py"), zl, "--report", "T991"], capture_output=True, text=True)
    res = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"stderr": r.stderr[-300:]}
    check(r.returncode == 0 and res.get("ok") and list(res.get("layers", {})) == ["c1"], f"the underground-only pack is accepted through its anchors ({res})")
    # the map viewer: a merged height layer gets its own entry in the 高度 menu and only existing tiles are requested
    site = os.path.join(tmp, "site")
    shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns(".git", "inbox"))
    r = subprocess.run([sys.executable, "-I", os.path.join(site, "tools", "jm_merge.py"), zp, "--report", "T992"], capture_output=True, text=True)
    check(r.returncode == 0, "merge into the site copy")
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=site))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900})
        bad, errs = [], []
        pg.on("response", lambda q: bad.append(q.url) if q.status >= 400 and "/tiles/" in q.url else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script("localStorage.setItem('sao-map-base','jm');localStorage.setItem('sao-tour-v1','1')")
        pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html#f1-map"); pg.wait_for_timeout(800)
        opts = pg.eval_on_selector_all("#layerSel option", "o=>o.map(x=>x.textContent)")
        check(pg.is_visible("#layerSel") and opts[0] == "高度：地面" and "地底 Y 16～31" in opts and len(opts) == 4, f"the explored map has a height menu ({opts})")
        pg.select_option("#layerSel", "c1"); pg.wait_for_timeout(300)
        pg.evaluate("__centerOn(5*512+275,9*512+90,10)"); pg.wait_for_timeout(1200)
        srcs = pg.eval_on_selector_all("#tiles img", "i=>i.map(x=>x.getAttribute('src'))")
        check(srcs and all("tiles/f1jm_c1/" in x for x in srcs) and any("/3/" in x for x in srcs) and not bad,
              f"layer tiles come from tiles/f1jm_c1, level 3 only where it exists ({len(srcs)} tiles, failed: {bad[:3]})")
        check("Y 16～31" in pg.inner_text("#mapNote") and pg.is_hidden("#jmCredit"), "the note names the layer; the surface contributor box is hidden")
        pg.screenshot(path=os.path.join(os.environ.get("SHOT_DIR", tmp), "layer_view.png"))
        pg.select_option("#layerSel", "day"); pg.wait_for_timeout(500)
        check(all("tiles/f1jm/" in x for x in pg.eval_on_selector_all("#tiles img", "i=>i.map(x=>x.getAttribute('src'))")), "back to the surface tiles")
        pg.select_option("#layerSel", "c1"); pg.set_viewport_size({"width": 390, "height": 844}); pg.wait_for_timeout(500)
        check(pg.is_visible("#layerSel") and pg.evaluate("document.documentElement.scrollWidth") <= 390, "the height menu fits on a phone")
        pg.screenshot(path=os.path.join(os.environ.get("SHOT_DIR", tmp), "layer_phone.png"))
        check(not errs, "no page errors in the viewer" + ("" if not errs else ": " + errs[0]))
        b.close()
    srv.shutdown()
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
