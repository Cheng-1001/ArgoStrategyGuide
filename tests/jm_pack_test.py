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
# The fake upload adds height layers and a dungeon. The real site has had those since R0007 (2026-11-07), so the test
# runs on a copy of the site without them: otherwise its "new" squares and dungeon are already on the map.
BASE = os.path.join(tmp, "base")
def _ign(d, names):
    return [n for n in names if n in (".git", "inbox") or n.startswith("f1jm_c") or (os.path.abspath(d) == os.path.join(ROOT, "tiles") and n == "dg")]
shutil.copytree(ROOT, BASE, ignore=_ign)
_jm = open(os.path.join(ROOT, "jmmeta.js"), encoding="utf-8").read()
_i = _jm.index("window.SAO_JM = ") + len("window.SAO_JM = ")
_J = json.loads(_jm[_i:_jm.rindex(";")])
_J["1"].pop("layers", None); _J.pop("dg", None)
open(os.path.join(BASE, "jmmeta.js"), "w", encoding="utf-8").write(_jm[:_i] + json.dumps(_J, ensure_ascii=False, indent=1) + ";\n")
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
    # dungeons: "<uuid>_<name>" folders next to the floor 1 overworld (two Geldorack runs), an unknown one, and one
    # whose server folder has no floor 1 map
    put("Triggers_f1~a/a57676b0-5d0c-4000-8000-000000000001_geldorack/-1", "-1,-1.png", cave)
    put("Triggers_f1~a/a57676b0-5d0c-4000-8000-000000000002_geldorack/-1", "-1,-1.png", cave)
    put("Triggers_f1~a/a57676b0-5d0c-4000-8000-000000000002_geldorack/-2", "-1,-1.png", cave)
    put("Triggers_f1~a/a57676b0-5d0c-4000-8000-000000000002_geldorack/day", "-1,-1.png", Image.new("RGBA", (512, 512)))
    put("Triggers_f1~a/bb0000b0-5d0c-4000-8000-000000000001_backrooms/5", "0,0.png", cave)
    put("Triggers_other~b/03b352fd-5d0c-4000-8000-000000000002_xalzirith/0", "0,0.png", cave)
    put("Triggers_f1~a/overworld/-398", "%d,%d.png" % top[0], cave)
    open(os.path.join(mp, "Triggers_f1~a", "overworld", "day", "notes.txt"), "w").write("x")
    os.makedirs(os.path.join(mp, "Triggers_f1~a", "waypoints"), exist_ok=True)                      # waypoints never go in a zip
    open(os.path.join(mp, "Triggers_f1~a", "waypoints", "Home_1.json"), "w").write('{"name":"Home","x":1,"z":2}')
    put("Triggers_f1~a/waypoints", "%d,%d.png" % top[0], noise)

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=BASE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900}, accept_downloads=True)
        pg.add_init_script("window.__COLLAB_OPEN=1")   # the packer is greyed out on the site while waiting for the game team (2026-11-09)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(base + "#report"); pg.wait_for_timeout(600)
        check(pg.is_visible("#jmPick") and "journeymap\\data" in pg.inner_text("#jmPack"), "the packer is on the data page, with the folder path")
        pg.set_input_files("#jmDir", mp)
        # choose first (user 2026-11-09「先選全圖還是更新打包地圖，不要每次都全讀」)
        pg.wait_for_selector("#jmOut [data-jmmode]")
        check(pg.locator("#jmOut [data-jmmode]").count() == 2 and pg.evaluate("window.__jm") is None and pg.is_disabled("#jmDl .repbtn"),
              "after picking the folder it asks 更新打包 or 全地圖打包 before reading the maps")
        if os.environ.get("SHOT_DIR"): pg.locator("#jmPack").screenshot(path=os.path.join(os.environ["SHOT_DIR"], "jm_choose.png"))
        pg.click("#jmOut [data-jmmode='full']")
        pg.wait_for_function("window.__jmFull", timeout=60000)
        if os.environ.get("SHOT_DIR"): pg.locator("#jmPack").screenshot(path=os.path.join(os.environ["SHOT_DIR"], "jm_full.png"))
        # 全地圖打包 (user 2026-11-09): everything of floor 1 without picking, waypoints left out
        F = pg.evaluate("window.__jmFull") or []
        check(pg.locator("#jmOut .jmmode").count() == 1 and "全地圖打包" in pg.inner_text("#jmOut .jmmode") and pg.locator("#jmHead").count() == 0,
              "全地圖打包 shows no square picking, only the folders and the download")
        fn = [x for p_ in F for x in p_["names"]]
        exp_day = {f"mp/Triggers_f1~a/overworld/day/{rx},{rz}.png" for rx, rz in top} | {"mp/Triggers_f1~a/overworld/day/%d,%d.png" % new}
        check(pg.locator("#jmDl [data-jmfull]").count() == len(F) >= 1 and exp_day <= set(fn)
              and "mp/Triggers_f1~a/overworld/1/5,9.png" in fn and any("_geldorack/" in x for x in fn)
              and not any("waypoint" in x.lower() or "Triggers_other" in x or "/night/" in x or "/-398/" in x or "40,40" in x for x in fn),
              f"全地圖打包 offers every floor 1 image (surface, heights, dungeons) and no waypoints ({len(fn)} files, {len(F)} parts; missing {sorted(exp_day - set(fn))[:3]}, {[x for x in fn if 'day' not in x]})")
        pg.locator("#jmDl [data-jmfull]").first.evaluate("e=>e.scrollIntoView({block:'center'})")
        with pg.expect_download() as dl:
            pg.click("#jmDl [data-jmfull]")
        zf = os.path.join(tmp, "full.zip"); dl.value.save_as(zf)
        zn = zipfile.ZipFile(zf).namelist()
        check("全地圖" in dl.value.suggested_filename and set(zn) == set(F[0]["names"]) and not any(".json" in x for x in zn),
              f"the 全地圖 zip holds exactly those images ({len(zn)}, {dl.value.suggested_filename})")
        pg.click("#jmOut [data-jmsw='new']")
        pg.wait_for_function("window.__jm", timeout=60000)
        J0 = pg.evaluate("window.__jm")
        check(not J0["parts"] and not pg.locator("[data-jmpart]").count() and pg.is_disabled("#jmDl .repbtn") and "還沒選" in pg.inner_text("#jmDlNote")
              and "第 1 層 0／" in pg.inner_text("#jmRegSum") and "地下城 0／1" in pg.inner_text("#jmRegSum"),
              "nothing is picked to start with; the download button is beside the folder button, greyed")
        pk = pg.evaluate("(()=>{const a=document.querySelector('#jmPick').getBoundingClientRect(),b=document.querySelector('#jmDl .repbtn').getBoundingClientRect();return [Math.abs(a.top-b.top)<4,b.left>a.right]})()")
        check(pg.locator(".jmtools #jmPick").count() == 1 and pg.locator(".jmtools #jmDl").count() == 1 and not pg.locator("#jmOut .repbtn").count() and pk == [True, True],
              f"the download button is to the right of the folder button, apart from the selection ({pk})")
        HJS = "[document.querySelector('#jmPack').getBoundingClientRect().height, document.querySelector('#jmNamesBtn').getBoundingClientRect().height, document.querySelector('.jmdlnote').getBoundingClientRect().height]"
        h0 = pg.evaluate(HJS)
        # flat layout (使用者 2026-11-06): no nested boxes or floor tabs, a section per floor and one for the dungeons,
        # 全選／清除 beside each heading (not next to the count), dungeons are picture tiles like the squares
        check(pg.locator(".jmsec").count() == 2 and pg.locator(".jmsec .jmmap").count() == 1 and pg.locator(".jmdgt[data-jmdg]").count() == 1
              and not pg.locator(".jmopt, .jmflb[role=tab], .jmregbar, [data-jmdgpv], input[data-jmdg], select#jmFloor").count()
              and pg.locator(".jmsech #jmRegAll").count() == 1 and pg.locator(".jmsech #jmDgAll").count() == 1 and not pg.locator("#jmRegSum #jmRegAll").count()
              and pg.locator("#jmFloorIn").count() == 1, "flat layout: floor and dungeon sections with their own 全選／清除, no tabs, no boxes")
        # the floor: a narrow box you can type a number into, with ▾ for the list (使用者 2026-11-06)
        fw = pg.evaluate("document.querySelector('.jmfl').getBoundingClientRect().width")
        pg.click("#jmFloorBtn"); pg.wait_for_timeout(100)
        fo = pg.eval_on_selector_all("#jmFloorList [data-jmfl]", "o=>o.map(x=>x.textContent)")
        check(pg.input_value("#jmFloorIn") == "1" and fw < 130 and fo[0] == "第 1 層" and len(fo) == 3 and all("尚未開放" in t for t in fo[1:]),
              f"the floor box is narrow ({fw:.0f}px), shows 1, and its list has floors 1-3 ({fo})")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(100)
        check(not pg.is_visible("#jmFloorList"), "Esc closes the floor list")
        # 「ⓘ 說明」 in the top-left corner of the map; the picked count is itself the button that lists the picked squares;
        # both look like the rarity pills and open as pop-overs that do not change the height (使用者 2026-11-06)
        hp = pg.evaluate("""(()=>{const b=document.querySelector('#jmHelpBtn').getBoundingClientRect(),m=document.querySelector('.jmmapw').getBoundingClientRect(),
            hit=[...document.querySelectorAll('[data-jmreg]')].some(e=>{const r=e.getBoundingClientRect();return !(r.right<=b.left||r.left>=b.right||r.bottom<=b.top||r.top>=b.bottom)});
            return [Math.round(b.left-m.left),Math.round(b.top-m.top),hit]})()""")
        check(pg.locator(".jmmapw .jmhelpa #jmHelpBtn").count() == 1 and hp[0] == 0 and hp[1] == 0 and not hp[2]
              and pg.locator(".jmselbar #jmNamesBtn #jmRegSum").count() == 1 and "已選：第 1 層" in pg.inner_text("#jmNamesBtn") and "已選的地方" not in pg.inner_text("#jmOut")
              and all("pill" in pg.get_attribute(q, "class") and "r-b" in pg.get_attribute(q, "class") for q in ("#jmHelpBtn", "#jmNamesBtn"))
              and not pg.locator(".jmselbar #jmHelpBtn, .jmtools #jmHelpBtn, #jmPrevOpen, .jmhint").count() and not pg.is_visible("#jmHelp"),
              f"「ⓘ 說明」 is in the map's top-left corner without covering a square ({hp}); the count is a rarity-style button")
        pg.click("#jmHelpBtn"); pg.wait_for_timeout(100)
        hh = pg.evaluate(HJS)
        hin = pg.evaluate("(()=>{const C=document.querySelector('#jmPack').getBoundingClientRect(),r=document.querySelector('#jmHelp').getBoundingClientRect();return r.left>=C.left&&r.right<=C.right})()")
        check(pg.is_visible("#jmHelp") and "停留" in pg.inner_text("#jmHelp") and "右上 ✕" in pg.inner_text("#jmHelp") and "選取示意" in pg.inner_text("#jmHelp") and hh == h0 and hin, f"「ⓘ 說明」 opens the selection help without changing the height ({h0} -> {hh})")
        if os.environ.get("SHOT_DIR"):
            pg.locator("#jmPack").screenshot(path=os.path.join(os.environ["SHOT_DIR"], "pack_help.png"))
        pg.keyboard.press("Escape"); pg.wait_for_timeout(100)
        check(not pg.is_visible("#jmHelp"), "Esc closes it")
        pg.click("#jmRegAll"); pg.click("#jmDgAll"); pg.wait_for_timeout(150)
        h1 = pg.evaluate(HJS)
        check(h0 == h1 and pg.is_enabled("#jmDl .repbtn"), f"picking everything changes nothing but the button and the text: the card keeps its height ({h0} -> {h1})")
        # the same at other widths (使用者 2026-11-06 的畫面：沒選時說明一行、全選後兩行，高度跳了；1280 剛好都是兩行沒抓到)
        hw = []
        for w in (1101, 1200, 1100, 1440, 1600, 1920):
            pg.set_viewport_size({"width": w, "height": 900}); pg.wait_for_timeout(150)
            pg.click("#jmRegNone"); pg.click("#jmDgNone"); pg.wait_for_timeout(120); a0 = pg.evaluate(HJS)
            pg.click("#jmRegAll"); pg.click("#jmDgAll"); pg.wait_for_timeout(120); a1 = pg.evaluate(HJS)
            hw.append((w, a0 == a1 and a0[2] < 25, a0[2], a1[2]))
        pg.set_viewport_size({"width": 1280, "height": 900}); pg.wait_for_timeout(150)
        check(all(x[1] for x in hw), f"none ↔ everything keeps the card height, and the note stays one line (no blank line), at 1101/1200/1100/1440/1600/1920 ({hw})")
        pg.click("#jmNamesBtn"); pg.wait_for_timeout(100)
        nt = pg.inner_text("#jmNames"); hn = pg.evaluate(HJS)
        inside = pg.evaluate("(()=>{const C=document.querySelector('#jmPack').getBoundingClientRect();return ['#jmNames'].concat(document.querySelector('#jmHelp')&&!document.querySelector('#jmHelp').hidden?['#jmHelp']:[]).every(q=>{const r=document.querySelector(q).getBoundingClientRect();return r.left>=C.left&&r.right<=C.right})})()")
        check(inside, "the pop-over stays inside the card")
        check("已選區塊" in nt and "Geldorack Dungeon" in nt and "第 1 層" in nt and hn == h0, f"「已選的地方」 lists every picked place in full, without changing the height ({nt[:60]}, {hn})")
        if os.environ.get("SHOT_DIR"):
            pg.locator("#jmPack").screenshot(path=os.path.join(os.environ["SHOT_DIR"], "pack_names.png"))
        pg.mouse.click(5, 5); pg.wait_for_timeout(100)
        check(not pg.locator("#jmNames").count(), "a click elsewhere closes it")
        # switching floors: 2 shows its greyed map and what will appear, 3 has no map yet, back to 1 keeps the picks
        pg.click("#jmFloorBtn"); pg.click("#jmFloorList [data-jmfl='2']"); pg.wait_for_timeout(200)
        f2 = [pg.locator("[data-jmreg]").count(), pg.locator(".jmsoon img").count(), pg.inner_text("#jmOpts")]
        if os.environ.get("SHOT_DIR"):
            pg.locator("#jmPack").screenshot(path=os.path.join(os.environ["SHOT_DIR"], "pack_floor2.png"))
        pg.fill("#jmFloorIn", "3"); pg.press("#jmFloorIn", "Enter"); pg.wait_for_timeout(200)
        f3 = [pg.locator("[data-jmreg]").count(), pg.locator(".jmsoonx").count(), pg.inner_text("#jmRegSum")]
        if os.environ.get("SHOT_DIR"):
            pg.locator("#jmPack").screenshot(path=os.path.join(os.environ["SHOT_DIR"], "pack_floor3.png"))
        pg.fill("#jmFloorIn", "12"); pg.press("#jmFloorIn", "Enter"); pg.wait_for_timeout(200)
        f12 = [pg.input_value("#jmFloorIn"), "第 12 層" in pg.inner_text("#jmOpts")]
        pg.fill("#jmFloorIn", "abc"); pg.press("#jmFloorIn", "Enter"); pg.wait_for_timeout(100)
        bad = pg.input_value("#jmFloorIn")
        pg.fill("#jmFloorIn", "1"); pg.press("#jmFloorIn", "Enter"); pg.wait_for_timeout(300)
        check(f2[0] == 0 and f2[1] == 1 and "第 2 層開放後" in f2[2] and f3[0] == 0 and f3[1] == 1 and "地下城 1／1" in f3[2] and f12 == ["12", True] and bad == "12"
              and pg.locator("[data-jmreg]").count() > 0 and pg.evaluate("window.__jm.sel.off") == [] and pg.input_value("#jmFloorIn") == "1",
              f"floors switch by the list (2) and by typing (3, 12, back to 1); a non-number goes back; the picks stay ({f2[:2]}, {f3}, {f12}, {bad})")
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
        # counts come from the tool's own numbers: the fixture picks regions from the site's current map, so they change
        # whenever a real upload makes the map bigger (R0006, 2026-11-06)
        nday = J["found"].get("day", 0); ncave = sum(v for k, v in J["found"].items() if k != "day")
        check(f"地面 {nday} 張" in lt and f"室內・洞穴 {ncave} 張" in lt and nday >= 1 and ncave == 8 and not pg.locator("#jmOut [data-jmbox], #jmOut [data-jmlay]").count(),
              "no height or coordinate fields: the summary counts surface and underground maps")
        pg.hover("[data-jmreg='5,9']", force=True); pg.wait_for_timeout(200)
        pg.wait_for_selector("#jmPop canvas", timeout=5000)
        check(pg.locator("#jmPop canvas").count() == 1 and "室內・洞穴 1 張" in pg.inner_text("#jmPop"), "pointing at a square previews the player's own map of it in the floating window")
        sqw = pg.evaluate("document.querySelector('#jmPop canvas').getBoundingClientRect().width")
        pg.click("#jmPopX"); pg.wait_for_timeout(100); closed = not pg.locator("#jmPop").count()
        pg.hover("[data-jmreg='5,9']", force=True); pg.wait_for_selector("#jmPop canvas", timeout=5000)
        pg.keyboard.press("Escape"); pg.wait_for_timeout(100); esc_closed = not pg.locator("#jmPop").count()
        pg.hover("[data-jmreg='2,2']", force=True); pg.hover("[data-jmreg='5,9']", force=True); pg.wait_for_selector("#jmPop canvas", timeout=5000)
        check(closed and esc_closed, "✕ or Esc closes the preview; resting on a square opens it again")
        if os.environ.get("SHOT_DIR"):
            pg.locator("#jmOut").scroll_into_view_if_needed()
            pg.locator("#jmOut").screenshot(path=os.path.join(os.environ["SHOT_DIR"], "pack_opts.png"))
        D = J["dgs"]; st2 = {(g["leaf"] or ""): g for g in J["groups"]}
        check(D.get("geldorack", {}).get("inst") == 2 and D["geldorack"]["news"] == 3 and D["geldorack"]["bounds"] == [-1, -1, -1, -1]
              and st2["bb0000b0-5d0c-4000-8000-000000000001_backrooms"]["state"] == "dgunk" and st2["03b352fd-5d0c-4000-8000-000000000002_xalzirith"]["state"] == "dgno",
              f"dungeons are recognised by folder name; unknown and unconfirmed ones are listed but not packed ({D}, {[(k, v['state']) for k, v in st2.items() if v.get('dg')]})")
        pg.hover("[data-jmdg=geldorack] .n"); pg.wait_for_function("document.querySelector('#jmPop')&&document.querySelector('#jmPop').innerText.includes('合在一起')", timeout=10000)
        cw = pg.evaluate("[document.querySelector('#jmPop canvas').width,document.querySelector('#jmPop canvas').height]")
        check(cw[0] > 100 and cw[1] > 30 and "Geldorack Dungeon" in pg.inner_text("#jmPopT"), f"pointing at a dungeon tile previews it in the same floating window ({cw})")
        pg.wait_for_selector("[data-jmdgth=geldorack] canvas", timeout=10000)
        tw = pg.evaluate("document.querySelector('[data-jmdgth=geldorack] canvas').getBoundingClientRect().width")
        check(tw > 40, f"the dungeon tile carries a thumbnail of the player's map ({tw})")
        if os.environ.get("SHOT_DIR"):
            pg.locator(".jmmap").scroll_into_view_if_needed(); pg.wait_for_timeout(200)
            pg.screenshot(path=os.path.join(os.environ["SHOT_DIR"], "pack_dgprev.png"))
        check(not pg.evaluate("document.getElementById('jmHow').open"), "the how-to folds away once a folder is picked")
        pw = [sqw, pg.evaluate("document.querySelector('#jmPop canvas').getBoundingClientRect().width")]
        pg.click("#jmPop canvas"); pg.wait_for_selector(".jmzoom img", timeout=5000)
        zw = pg.evaluate("document.querySelector('.jmzoom img').getBoundingClientRect().width")
        check(pw[0] >= 300 and pw[1] >= 300 and zw >= 500 and "Geldorack" in pg.inner_text(".jmzoom span"), f"previews are large; clicking a dungeon preview zooms it ({pw}, zoom {zw})")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(100)
        # a real mouse: rest on the square whose way to the preview window crosses the most other squares, then move there
        # like a person (about 0.4 s) and click the picture — the preview must still be that square (使用者 2026-11-06)
        pg.locator(".jmmap").evaluate("e=>e.scrollIntoView({block:'center'})"); pg.wait_for_timeout(200)
        cr = pg.evaluate("(()=>{const r=document.querySelector('#jmPop canvas').getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2]})()")
        best = pg.evaluate("""([cx,cy])=>{let best=null;for(const e of document.querySelectorAll('[data-jmreg]')){const r=e.getBoundingClientRect(),x0=r.x+r.width/2,y0=r.y+r.height/2,seen=new Set();
            for(let i=1;i<60;i++){const x=x0+(cx-x0)*i/60,y=y0+(cy-y0)*i/60,h=document.elementFromPoint(x,y);if(h&&h.dataset&&h.dataset.jmreg&&h!==e)seen.add(h.dataset.jmreg)}
            if(!best||seen.size>best[3])best=[e.dataset.jmreg,x0,y0,seen.size]}return best}""", cr)
        pg.mouse.move(best[1], best[2]); pg.wait_for_timeout(700)
        for i in range(1, 26):
            pg.mouse.move(best[1] + (cr[0] - best[1]) * i / 25, best[2] + (cr[1] - best[2]) * i / 25); pg.wait_for_timeout(16)
        pv = pg.evaluate("window.__jmPv"); title = pg.inner_text("#jmPopT")
        pg.mouse.click(cr[0], cr[1]); pg.wait_for_selector(".jmzoom img", timeout=5000)
        if os.environ.get("SHOT_DIR"):
            pg.screenshot(path=os.path.join(os.environ["SHOT_DIR"], "pack_zoom.png"))
        cap = pg.inner_text(".jmzoom span")
        check(best[3] >= 2 and pv == best[0] and title in cap, f"moving from square {best[0]} to the preview across {best[3]} other squares keeps its preview, and its picture zooms ({pv}, {cap})")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(100)
        zc = [not pg.locator(".jmzoom").count(), pg.locator("#jmPop").count() == 1]
        pg.click("#jmPop canvas"); pg.wait_for_selector(".jmzoom .jmzx", timeout=5000); pg.click(".jmzoom .jmzx"); pg.wait_for_timeout(100)
        check(zc == [True, True] and not pg.locator(".jmzoom").count(), f"Esc closes only the zoom (the preview stays); the ✕ at the top right closes it too ({zc})")
        check("Geldorack Dungeon" in lt and "2 次進場" in lt and "backrooms" in lt and pg.get_attribute("[data-jmdg=geldorack]", "aria-pressed") == "true", "the dungeon tiles name the dungeon and its runs")
        regs = pg.eval_on_selector_all("[data-jmreg]", "e=>e.map(x=>x.dataset.jmreg)")
        check("5,9" in regs and "2,2" in regs and "40,40" not in regs and pg.locator(".jmmap .jmtown").count() >= 5
              and "第 1 層 %d／%d 格" % (len(regs), len(regs)) in pg.inner_text("#jmRegSum"), f"the squares with new data are on a small map with town names ({regs})")
        check(set(st) == {"Triggers_f1~a", "Triggers_other~b", "Triggers_other2~c", "Triggers_noise~d", "Triggers_lone~e", "Triggers_out~f"},
              "one entry per world folder (night / cave layers are not separate worlds)")
        check(st["Triggers_f1~a"]["state"] == "f1" and st["Triggers_f1~a"]["files"] == 4, f"the floor 1 world is recognised ({st['Triggers_f1~a']})")
        check(all(st[k]["state"] == "other" for k in ("Triggers_other~b", "Triggers_other2~c", "Triggers_noise~d")),
              "other worlds with real-looking terrain and noise are not floor 1 (" + ", ".join("%.0f" % st[k]["med"] for k in ("Triggers_other~b", "Triggers_other2~c", "Triggers_noise~d")) + ")")
        check(st["Triggers_lone~e"]["state"] == "few" and st["Triggers_out~f"]["state"] == "out", "no overlap -> cannot confirm; outside the floor -> skipped")
        t = pg.inner_text("#jmOut")
        nall = pg.evaluate("window.__jm.nNew")
        check(f"共 {nall} 張" in pg.inner_text("#jmDlNote") and "下載壓縮檔" in pg.inner_text("#jmDl"), f"the note counts the maps ({nall}) and the zip is offered")
        pg.locator("[data-jmpart]").first.evaluate("e=>e.scrollIntoView({block:'center'})")
        with pg.expect_download() as dl:
            pg.click("[data-jmpart]")
        zp = os.path.join(tmp, "up.zip")
        dl.value.save_as(zp)
        z = zipfile.ZipFile(zp)
        names = [i.filename for i in z.infolist()]
        check(z.testzip() is None and dl.value.suggested_filename.endswith(".zip"), "the download is a valid zip")
        dgn = [nm for nm in names if "_geldorack/" in nm]
        check(sorted(dgn) == ["mp/Triggers_f1~a/a57676b0-5d0c-4000-8000-000000000001_geldorack/-1/-1,-1.png",
                              "mp/Triggers_f1~a/a57676b0-5d0c-4000-8000-000000000002_geldorack/-1/-1,-1.png",
                              "mp/Triggers_f1~a/a57676b0-5d0c-4000-8000-000000000002_geldorack/-2/-1,-1.png"]
              and not any("backrooms" in nm or "xalzirith" in nm or "/-398/" in nm for nm in names), f"the zip has both Geldorack runs, not the unknown / unconfirmed ones ({dgn})")
        names_fl = [nm for nm in names if "_geldorack/" not in nm]
        check(names and all(nm.startswith("mp/Triggers_f1~a/overworld/") for nm in names_fl) and "mp/Triggers_f1~a/overworld/day/%d,%d.png" % new in names
              and "mp/Triggers_f1~a/overworld/1/5,9.png" in names and sum(nm.startswith("mp/Triggers_f1~a/overworld/2/") for nm in names) == 6
              and "mp/Triggers_f1~a/overworld/2/40,40.png" not in names and not any("/night/" in nm for nm in names),
              f"the zip has floor 1 surface and height-layer maps, including the new area ({names})")
        check(open(os.path.join(mp, "Triggers_f1~a", "overworld", "day", "%d,%d.png" % new), "rb").read() == z.read("mp/Triggers_f1~a/overworld/day/%d,%d.png" % new),
              "files are stored byte for byte")
        def names_now():
            return pg.evaluate("window.__jm.parts.flatMap(p=>p.names)")
        # only the ink room square (layer 1, region 5,9): that square plus surface anchors from elsewhere
        pg.click("[data-jmdg=geldorack]"); pg.wait_for_timeout(100)
        check(not any("_geldorack/" in x for x in names_now()) and pg.get_attribute("[data-jmdg=geldorack]", "aria-pressed") == "false", "clicking a picked dungeon tile leaves it out")
        pg.click("#jmRegNone"); pg.wait_for_timeout(100)
        check(not pg.locator("[data-jmpart]").count() and pg.is_disabled("#jmDl .repbtn") and "還沒選" in pg.inner_text("#jmDlNote"), "nothing picked -> the download button greys out, the note says what to do")
        pg.click("[data-jmreg='5,9']", force=True); pg.wait_for_timeout(100)
        J2 = pg.evaluate("window.__jm")
        nn = names_now()
        inside = [x for x in nn if x.endswith("/5,9.png")]
        anchors = [x for x in nn if not x.endswith("/5,9.png")]
        check("mp/Triggers_f1~a/overworld/1/5,9.png" in inside and all("/day/" in x for x in anchors) and J2["parts"][0]["ov"] >= 60
              and (J2["parts"][0]["anchors"] >= 1 and "另含" in (pg.get_attribute("[data-jmpart]", "title") or "") if not any("/day/" in x for x in inside) else True)
              and "第 1 層 1／" in pg.inner_text("#jmRegSum"),
              f"one square with only underground data carries surface anchors ({J2['parts']}, {pg.inner_text('#jmRegSum')})")
        pg.locator("[data-jmpart]").first.evaluate("e=>e.scrollIntoView({block:'center'})")
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
        check(pg.evaluate("window.__jm.sel.off") == [] and pg.evaluate("window.__jm.sel.dgOff") == ["geldorack"], "the floor's 全選 picks the squares only, not the dungeons")
        pg.click("#jmDgAll"); pg.wait_for_timeout(100)
        check(pg.evaluate("window.__jm.sel.dgOff") == [] and len(names_now()) == len(names), "the dungeons' 全選 picks them again; everything is packed")
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
        pg.wait_for_selector("#jmOut [data-jmmode]"); pg.click("#jmOut [data-jmmode='new']")
        pg.wait_for_function("window.__jm", timeout=60000)
        pg.click("#jmRegAll"); pg.click("#jmDgAll"); pg.wait_for_timeout(150)
        parts = pg.evaluate("window.__jm.parts")
        check(len(parts) >= 2 and all(q["ov"] >= 40 for q in parts) and pg.locator("[data-jmpart]").count() == len(parts) and "每份都要各送一次表單" in pg.inner_text("#jmDlNote") and pg.evaluate("document.querySelector('#jmDlNote').getBoundingClientRect().height") < 25,
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
    shutil.copytree(os.path.join(BASE, "tiles", "f1jm"), os.path.join(w, "tiles", "f1jm"))
    for f in ("floor1.jpg", "floor1_jm.jpg", "jmmeta.js"):
        shutil.copy(os.path.join(BASE, f), w)
    r = subprocess.run([sys.executable, "-I", os.path.join(w, "tools", "jm_merge.py"), zp, "--report", "T990"], capture_output=True, text=True)
    res = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"stderr": r.stderr[-300:]}
    check(r.returncode == 0 and res.get("ok") and res.get("folders") == 1 and res.get("newChunks", 0) > 300, f"tools/jm_merge.py merges the packed zip ({res})")
    check(set(res.get("layers", {})) == {"c0", "c1", "c2"} and res["layers"]["c1"] > 0, f"... and its height layers ({res.get('layers')})")
    check(set(res.get("dungeons", {})) == {"geldorack"} and res["dungeons"]["geldorack"] > 0, f"... and the dungeon ({res.get('dungeons')}, {res.get('skippedWhy')})")
    r = subprocess.run([sys.executable, "-I", os.path.join(w, "tools", "jm_merge.py"), zl, "--report", "T991"], capture_output=True, text=True)
    res = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"stderr": r.stderr[-300:]}
    check(r.returncode == 0 and res.get("ok") and list(res.get("layers", {})) == ["c1"], f"the underground-only pack is accepted through its anchors ({res})")
    # the map viewer: a merged height layer gets its own entry in the 高度 menu and only existing tiles are requested
    site = os.path.join(tmp, "site")
    shutil.copytree(BASE, site)
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
        # no 地下 menu on the map (user 2026-11-08「移除地下顯示」): a place panel's 「查看地下」 opens it around that place
        check(pg.is_hidden("#layerSel") and pg.is_hidden("#dgBack"), "the map has no height menu")
        x, z = 5 * 512 + 275, 9 * 512 + 90
        check(pg.evaluate(f"window.__underNear({x},{z})") and not pg.evaluate("window.__underNear(300,300)"),
              "「查看地下」 is offered only near underground data (content.png)")
        # 「查看地下／室內」 shows only the surroundings, under the button, from level-3 tiles (user 2026-11-08「只顯示周邊就好」)
        pg.evaluate(f"""(()=>{{const w=document.createElement('div');w.className='maplinks';w.innerHTML='<button id="tUnder" data-under="測試地點" data-ux="{x}" data-uz="{z}">u</button>';document.body.appendChild(w)}})()""")
        bad.clear(); pg.click("#tUnder"); pg.wait_for_timeout(1500)
        nat = pg.evaluate("(()=>{const i=document.querySelector('.maplinks + .underfig img');return i?i.naturalWidth:0})()")
        check(nat == 1280 and not bad and pg.is_hidden("#dgBack"), f"「查看地下」 draws a 320×320-block picture of the surroundings, the map stays as it was ({nat}, {bad[:2]})")
        check(pg.evaluate("[...performance.getEntriesByType('resource')].filter(e=>e.name.includes('f1jm_under/')).every(e=>e.name.includes('f1jm_under/3/')||e.name.includes('content.png'))"),
              "it reads only level-3 underground tiles (no blurry low levels)")
        pg.click("#tUnder"); pg.wait_for_timeout(200)
        check(pg.locator(".underfig").count() == 0, "clicking again hides it")
        pg.screenshot(path=os.path.join(os.environ.get("SHOT_DIR", tmp), "layer_view.png"))
        # dungeon map: no dungeon list on the map tab (user 2026-11-08「不用放地下城」); opened from the dungeon page, left with 「回到第 1 層」
        check(pg.is_hidden("#dgSel") and pg.is_hidden("#dgBack"), "the map tab has no dungeon switch")
        pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html#f1-dungeons"); pg.wait_for_timeout(800)
        pg.click("#lDg [data-go='s|geldorakd']"); pg.wait_for_timeout(600)
        ov = pg.locator("#pBody .dgmap img")
        check(ov.count() == 1 and pg.evaluate("document.querySelector('#pBody .dgmap img').naturalWidth") > 0, "the dungeon panel shows the dungeon's map")
        bad.clear(); pg.click("#pBody .dgmap figcaption [data-dgmap]"); pg.wait_for_timeout(1500)
        check(pg.evaluate("window.__dgMode()") == "geldorack" and pg.is_visible("#view-map") and pg.is_visible("#dgBack"), f"its button opens the dungeon map on the map tab, with a back button ({pg.evaluate('window.__dgMode()')}, {pg.url})")
        srcs = pg.eval_on_selector_all("#tiles img", "i=>i.map(x=>x.getAttribute('src'))")
        check(srcs and all("tiles/dg/geldorack/" in x for x in srcs) and not bad and pg.is_hidden("#fpanel")
              and not pg.locator("#world .town").count() and "Geldorack Dungeon" in pg.inner_text("#mapNote"),
              f"dungeon mode shows only the dungeon's tiles (absolute level-3 names), no floor markers ({len(srcs)}, failed {bad[:2]})")
        pg.screenshot(path=os.path.join(os.environ.get("SHOT_DIR", tmp), "dg_view.png"))
        pg.select_option("#layerSel", "c-2"); pg.wait_for_timeout(800)
        check(all("tiles/dg/geldorack/c-2/" in x for x in pg.eval_on_selector_all("#tiles img", "i=>i.map(x=>x.getAttribute('src'))")), "the height menu switches the dungeon's heights")
        pg.set_viewport_size({"width": 390, "height": 844}); pg.wait_for_timeout(400)
        check(pg.evaluate("document.documentElement.scrollWidth") <= 390, "dungeon mode fits on a phone")
        pg.screenshot(path=os.path.join(os.environ.get("SHOT_DIR", tmp), "dg_phone.png"))
        pg.set_viewport_size({"width": 1280, "height": 900}); pg.wait_for_timeout(300)
        pg.click("#dgBack"); pg.wait_for_timeout(500)
        check(pg.evaluate("window.__dgMode()") is None and pg.locator("#world .town").count() > 5 and pg.is_hidden("#dgBack"), "「回到第 1 層」goes back to floor 1 with its markers")
        check(all("tiles/f1jm/" in x for x in pg.eval_on_selector_all("#tiles img", "i=>i.map(x=>x.getAttribute('src'))")), "the floor map shows the surface tiles")
        # blurry map while zooming (user 2026-11-08「模糊是全地圖」): all of level 1 stays loaded, level 2 sits under level 3
        pg.evaluate(f"__centerOn({x},{z},10)"); pg.wait_for_timeout(1200)
        cls = pg.eval_on_selector_all("#tiles img", "i=>i.map(x=>x.className+' '+x.getAttribute('src').split('/').slice(-2)[0])")
        n1 = sum(1 for c in cls if c.startswith("l1 1")); n2 = sum(1 for c in cls if c.startswith("mid 2")); n3 = sum(1 for c in cls if c.startswith("hi 3"))
        check(n1 == 25 and n2 > 0 and n3 > 0, f"zoomed in: whole level 1 ({n1}), level 2 under level 3 ({n2}, {n3})")
        pg.screenshot(path=os.path.join(os.environ.get("SHOT_DIR", tmp), "layer_phone.png"))
        check(not errs, "no page errors in the viewer" + ("" if not errs else ": " + errs[0]))
        b.close()
    srv.shutdown()
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
