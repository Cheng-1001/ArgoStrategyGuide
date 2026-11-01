"""Smoke test for the built site (repo root index.html).

Usage (from the repo root):  python3 src/build.py && python3 tests/smoke.py
Needs Python Playwright with Chromium (`pip install playwright && playwright install chromium`
if the environment does not already have it).

Checks: every tab on floors 1-3 loads without page errors, no horizontal scroll at phone width,
a monster detail opens, the codex hint and player-report data show, the base-map toggle works,
and the report tab links to the Google Form with the floor filled in.
Exits with status 1 on any failure.
"""
import http.server, os, sys, threading
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8790


class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8"}

    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, *a):
        pass


fails = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{PORT}/index.html"
with sync_playwright() as p:
    b = p.chromium.launch()
    errs = []
    for w, h in [(1280, 900), (390, 844)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        pg.route("https://fonts.googleapis.com/**", lambda r: r.abort())
        pg.route("https://fonts.gstatic.com/**", lambda r: r.abort())
        pg.on("pageerror", lambda e: errs.append(str(e)))
        for f in (1, 2, 3):
            for v in ("map", "monsters", "items", "props", "recipes", "quests", "equip", "bosses", "report"):
                pg.goto(f"{base}#f{f}-{v}")
                pg.wait_for_timeout(250)
                if w < 500:
                    over = pg.evaluate("document.documentElement.scrollWidth>innerWidth")
                    if over:
                        check(False, f"no horizontal scroll at {w}px: f{f}-{v}")
        pg.close()
    check(not errs, "no page errors on any tab" + ("" if not errs else ": " + errs[0]))

    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(base + "#monsters"); pg.wait_for_timeout(400)
    pg.fill("#q", "Albal"); pg.wait_for_timeout(300)
    pg.click("#lMon .card >> nth=0"); pg.wait_for_timeout(300)
    t = pg.inner_text("#pBody")
    check("A lone wolf" in t, "Albal shows codex description (reports.js)")
    check("Wolf Valley" in t, "Albal shows codex location hint (hints.js)")
    check("35%" in t, "Albal drop rates come from the report")

    pg.goto(base + "#monsters"); pg.wait_for_timeout(300)
    pg.fill("#q", "Forest Spider"); pg.wait_for_timeout(300)
    pg.click("#lMon .card >> nth=0"); pg.wait_for_timeout(300)
    check("X 1239 · Z 1374" in pg.inner_text("#pBody"), "Forest Spider sits in Arakh'Nol (reference map)")

    pg.goto(base + "#monsters"); pg.wait_for_timeout(300)
    pg.fill("#q", "Nasgul"); pg.wait_for_timeout(300)
    check(pg.locator("#lMon .card").count() >= 1 and "Cursed Nazgul Protector" in pg.inner_text("#lMon"),
          "old monster name (Nasgul) still finds the renamed monster")
    pg.fill("#q", ""); pg.wait_for_timeout(200)

    pg.goto(base + "#quests"); pg.wait_for_timeout(400)
    check(pg.locator(".qcard").count() >= 30, "quests tab lists the floor 1 main questline")
    seal = pg.locator(".qcard", has_text="The Truth About the Seal").first
    check(seal.locator(".mqn").inner_text() == "24" and pg.locator(".qcard", has_text="The Southern Marshes").locator(".mqn").inner_text() == "14",
          "main quests show the in-game numbers (Truth About the Seal = 24, as in report R0001; Southern Marshes = 14)")
    pg.click("[data-go='q|mq1_15']"); pg.wait_for_timeout(400)
    check(pg.locator("#pBody .qmap svg polyline").count() == 1 and pg.locator("#pBody .mqs li").count() >= 5,
          "clicking a main quest opens the panel with its steps and a route mini map")
    check(pg.evaluate("(()=>{const b=document.getElementById('pBody');const m=b.querySelector('.qmap');return [...b.children].slice([...b.children].indexOf(m)+1).every(e=>e.matches('[data-route]'))})()"),
          "quest panel: the route map is the last block (only the enlarge button after it)")
    pg.click("#pBody [data-route]"); pg.wait_for_timeout(600)
    vb0 = pg.get_attribute("#rwSvg", "viewBox")
    check(pg.is_visible("#rwin") and pg.locator("#rwSvg polyline").count() == 1, "enlarge opens the floating route window")
    pg.click("#rwIn"); pg.wait_for_timeout(200)
    check(pg.get_attribute("#rwSvg", "viewBox") != vb0, "the route window zooms")
    pg.click("#rwX"); pg.wait_for_timeout(200)
    check(not pg.is_visible("#rwin"), "the route window closes")
    pg.goto(base + "#quests"); pg.wait_for_timeout(300)
    pg.click('#fQKind .chip[data-v="side"]'); pg.wait_for_timeout(300)
    pg.locator(".qside", has_text="Daiki").first.click(); pg.wait_for_timeout(400)
    t = pg.inner_text("#pBody")
    check("收集 Boar Hide ×5" in t and "掉落" in t and pg.locator("#pBody .qmap svg").count() == 1,
          "side quest panel spells out what to collect, where it drops, and shows the route")

    pg.goto(base + "#equip"); pg.wait_for_timeout(500)
    total = pg.locator("#lEq .card").count()
    pg.click("#fEqPart .chip[data-v=weapon]"); pg.wait_for_timeout(200)
    pg.locator("#lEq .card").first.click(); pg.wait_for_timeout(300)
    check(total > 100 and "官方圖鑑 #" in pg.inner_text("#pBody"), "equipment tab lists official items and opens a detail")

    pg.goto(base + "#recipes"); pg.wait_for_timeout(400)
    tot = pg.locator("#lRc .rcard").count()
    pg.click('#fRcCat .chip[data-v="key"]'); pg.wait_for_timeout(200)
    check(tot >= 100 and pg.locator("#lRc .rcard").count() == 4 and "Forest Key" in pg.inner_text("#lRc"), "recipes tab: 100+ recipes, key filter shows the 4 dungeon keys")
    check(pg.locator('nav.tabs a[data-v="recipes"][aria-current="page"]').count() == 1 and pg.is_hidden("#codexTabs")
          and pg.eval_on_selector_all("nav.tabs a", "e=>e.map(a=>a.dataset.v).join(',')") == "map,codex,quests,recipes,bosses,report",
          "recipes is its own top tab between quests and world bosses")
    pg.click('#fRcCat .chip[data-v="potion"]'); pg.wait_for_timeout(200)
    pg.locator("#lRc .rcard", has_text="Quality Health Potion I").first.click(); pg.wait_for_timeout(300)
    t = pg.inner_text("#pBody")
    check(pg.locator("#lRc .rcard.sel").count() == 1 and "Alchemist" in t and "Sylvan Sprout" in t and "× 8" in t,
          "clicking one potion recipe selects only that card and opens its recipe panel")
    check(pg.locator('#lRc .rcard', has_text="Quality Health Potion I").first.locator(".eslot.empty").count() == 0,
          "Quality Health Potion I uses the official catalogue icon (Qualité Potion de Vie I)")
    pg.locator("#pBody .lrow", has_text="Allium").first.click(); pg.wait_for_timeout(300)
    check(pg.locator("#pBody .qmap svg").count() == 1 and pg.locator("#pBody .rnum").count() >= 1 and pg.locator("#pBody [data-imap]").count() == 1,
          "material panel (Allium) shows a numbered map of where to get it")
    icons = pg.eval_on_selector_all("#pBody .recipes .lrow .eslot.empty", "e=>e.map(x=>x.textContent.trim())")
    check(icons and "💍" not in icons, f"potion recipes under 可以拿去製作 use the potion icon ({set(icons)})")
    pg.click("#pBody [data-imap]"); pg.wait_for_timeout(400)
    check(pg.is_visible("#rwin") and pg.locator("#rwSvg polyline").count() == 0, "enlarged item map opens without a route line")
    pg.click("#rwX") if pg.locator("#rwX").count() else None; pg.wait_for_timeout(150)
    pg.click("#pClose"); pg.wait_for_timeout(150)
    pg.goto(base + "#monsters"); pg.wait_for_timeout(400)
    c0 = pg.evaluate("getComputedStyle(document.getElementById('lMon')).gridTemplateColumns.split(' ').length")
    pg.locator("#lMon .card").first.click(); pg.wait_for_timeout(300)
    c1 = pg.evaluate("getComputedStyle(document.getElementById('lMon')).gridTemplateColumns.split(' ').length")
    pg.click("#pClose"); pg.wait_for_timeout(300)
    c2 = pg.evaluate("getComputedStyle(document.getElementById('lMon')).gridTemplateColumns.split(' ').length")
    check(c0 == c1 == c2, f"monster grid keeps its column count when the side panel opens and closes ({c0}/{c1}/{c2})")

    pg.goto(base + "#f1-map"); pg.wait_for_timeout(500)
    zl = pg.inner_text("#zlist")
    check("傳送點－城鎮 7" in zl and "傳送點－地標 6" in zl and pg.locator(".town.tp").count() == 13 and pg.locator(".town.land").count() == 2,
          "13 teleports (7 towns, 6 landmarks) share one marker style; landmarks (Vallhat, hidden well) another")
    check(pg.locator(".areas path").count() >= 13 and pg.get_attribute(".areas path", "vector-effect") == "non-scaling-stroke",
          "monster areas are outlined with a zoom-independent line width")
    n = pg.locator(".zone.npc").count()
    pg.click('#fpCats .fchip[data-k="npc"]'); pg.wait_for_timeout(300)
    check(n >= 70 and pg.locator(".zone.npc").count() == 0 and "🧑 NPC" not in pg.inner_text("#zlist"),
          "NPCs on the map; the filter hides them on the map and in the list")
    pg.click('#fpCats .fchip[data-k="npc"]'); pg.wait_for_timeout(200)
    pg.click("#fpNpcWrap summary"); pg.wait_for_timeout(150)
    pg.click('#fpNpc .fchip[data-k="npc:lootBuyers"]'); pg.wait_for_timeout(300)
    check(pg.locator(".zone.npc").count() == n - 16, "NPC sub-filter hides the 16 loot buyers only")
    pg.click("#fpAll"); pg.wait_for_timeout(200)
    pg.click('#fpCats .fchip[data-k="area"]'); pg.click('#fpCats .fchip[data-k="mobs"]'); pg.wait_for_timeout(300)
    check(pg.locator('.zone[data-s="slimes"]').count() == 0 and pg.locator('.town.tp[data-s="wolf"]').count() == 1,
          "hiding monster areas keeps an area that is also a teleport (Wolf Valley)")
    check(pg.locator(".areas path").count() == 0, "hiding monster areas hides their outlines")
    pg.click("#fpAll"); pg.wait_for_timeout(200)
    for k in ("land", "area", "mobs", "gather", "dungeon", "wboss", "boss", "npc"):
        pg.click(f'#fpCats .fchip[data-k="{k}"]'); pg.wait_for_timeout(80)
    pg.wait_for_timeout(300)
    check(pg.locator('.zone[data-s="wolf"] .thumbs').count() == 0 and pg.locator('.town.tp[data-s="wolf"]').count() == 1
          and pg.locator('#zlist .zrow[data-s="wolf"] .thumbs').count() == 0,
          "teleports only: Wolf Valley shows without monsters on the map and in the list")
    pg.click("#fpAll"); pg.wait_for_timeout(200)
    if pg.is_visible("#pClose"):
        pg.click("#pClose"); pg.wait_for_timeout(200)
    pg.locator("#zlist .npcrow", has_text="Bandit Accessories").locator(".zn").click(); pg.wait_for_timeout(400)
    t = pg.inner_text("#pBody")
    check("可以製作\n5" in t and "Bandit Coin" in t and "Stolen Cloak" in t and "Small Pouch ×24" in t, "Bandit Accessories lists its 5 recipes (4 from screenshots, 1 from the reference map)")
    pg.click("#pClose"); pg.wait_for_timeout(200)
    pg.locator("#zlist .npcrow", has_text="Shark Accessories").locator(".zn").click(); pg.wait_for_timeout(400)
    t = pg.inner_text("#pBody")
    check("Shark Fang" in t and "Wolf Fangs ×8" in t and "33 Col" in t, "Shark Accessories lists its recipes with cost")
    off = pg.evaluate("""(()=>{const b=document.querySelector('.town.gather[data-s="farm"] .pin').getBoundingClientRect();
      const w=document.getElementById('world').getBoundingClientRect();const k=w.width/1000;
      const x=w.left+(2351-70)/4980*1000*k, y=w.top+(3662-70)/4980*1000*k;return Math.hypot(b.left+b.width/2-x,b.top+b.height/2-y)})()""")
    check(off < 2, f"gathering-spot pin is centred on its coordinate (off by {off:.1f}px)")
    tp = pg.evaluate("""(()=>{const e=[...document.querySelectorAll('.town.tp')].find(x=>x.textContent.trim()==='Hanaka');const b=e.querySelector('.pin').getBoundingClientRect(),n=e.querySelector('.tname').getBoundingClientRect();
      const w=document.getElementById('world').getBoundingClientRect();const k=w.width/1000;
      const x=w.left+(1492-70)/4980*1000*k, y=w.top+(3453-70)/4980*1000*k;return [Math.hypot(b.left+b.width/2-x,b.top+b.height/2-y),n.bottom<=b.top+1,getComputedStyle(e.querySelector('.tname')).backgroundColor]})()""")
    check(tp[0] < 2 and tp[1] and tp[2] == "rgb(255, 255, 255)", f"teleport point: dot on the coordinate (off {tp[0]:.1f}px), white name box above it")
    sz0 = pg.evaluate("document.querySelector('.town.tp .pin').getBoundingClientRect().width")
    w0 = pg.evaluate("getComputedStyle(document.querySelector('.areas path')).strokeWidth")
    for _ in range(4):
        pg.click("#zin"); pg.wait_for_timeout(120)
    sz1 = pg.evaluate("document.querySelector('.town.tp .pin').getBoundingClientRect().width")
    w1 = pg.evaluate("getComputedStyle(document.querySelector('.areas path')).strokeWidth")
    check(sz1 < sz0 and float(w1.rstrip("px")) < float(w0.rstrip("px")), f"zooming in shrinks markers ({sz0:.1f}->{sz1:.1f}px) and area lines ({w0}->{w1})")
    pg.click("#zfit"); pg.wait_for_timeout(200)
    check(pg.locator(".bsp").count() == 23 and pg.locator('.bsp[title*="Pumba"]').count() == 5, "23 boss spawn points drawn (Pumba has 5)")
    check(pg.is_visible("#fpanel") and pg.locator("#fpanel").bounding_box()["width"] <= 200, "filter panel stays open on the left and is narrow")
    pg.eval_on_selector('.bsp[title*="Nazgul"]', 'e=>e.click()'); pg.wait_for_timeout(300)
    t = pg.inner_text("#pBody")
    check("8 遊戲截圖" in t and "Behind the Great Door" in t and "兩個階段" in t, "Cursed Nazgul Protector: LV 8 from a screenshot and its two phases")
    pg.click("#pClose"); pg.wait_for_timeout(150)
    check(pg.evaluate("document.querySelector('#fpCats .fchip[data-k=npc]').nextElementSibling.id") == "fpNpcWrap",
          "NPC sub-categories sit right under the NPC chip")
    pg.evaluate("document.getElementById('fpNpcWrap').open=true"); pg.wait_for_timeout(200)
    fb, pb = pg.locator("#fpFly").bounding_box(), pg.locator("#fpanel").bounding_box()
    check(pg.is_visible("#fpFly") and fb["x"] >= pb["x"] + pb["width"] and pg.locator("#fpFly .fchip").count() >= 10,
          "desktop: NPC sub-categories open in a flyout to the right of the filter panel")
    pg.click("#fpFlyX"); pg.wait_for_timeout(150)
    check(pg.is_hidden("#fpFly"), "flyout closes")
    names = pg.eval_on_selector_all(".zone.mobarea .zlabel", "e=>e.map(x=>x.textContent.trim())")
    check("Putrid Swamp" in names and "Boar Zone" in names and "Treants / Swamp" not in names, "monster areas use the wiki region names where one exists")
    st = pg.evaluate("""(()=>{const d=document.querySelector('.town.dungeon[data-s="fallen"]');const z=document.querySelector('.zone.mobarea .zlabel');
      return [!!d&&!!d.querySelector('.pin'),z?getComputedStyle(z).backgroundColor:'none',[...document.querySelectorAll('.bsp')].every(b=>getComputedStyle(b).borderTopStyle==='solid')]})()""")
    check(st[0] and st[1] == "rgba(0, 0, 0, 0)" and st[2], "dungeons have a pin on the entrance, monster-area names have no box, boss rings are all solid")
    sz = pg.evaluate("""(()=>{const w=s=>{const e=document.querySelector(s);return e?e.getBoundingClientRect().width:0};return [w('.bsp.boss'),w('.bsp.mini'),w('.zone .mapth:not(.boss):not(.mini):not(.minion)')]})()""")
    check(sz[0] > sz[1] > sz[2] > 0, f"bosses drawn bigger than mini-bosses and monsters ({sz[0]:.0f} > {sz[1]:.0f} > {sz[2]:.0f}px)")
    pg.click('#fpCats .fchip[data-k="boss"]'); pg.wait_for_timeout(200)
    check(pg.locator(".bsp").count() == 0, "区域首領 filter hides spawn points")
    pg.click('#fpCats .fchip[data-k="boss"]'); pg.wait_for_timeout(200)
    check("⛏️ 採集點 4" in pg.inner_text("#zlist") and "🌾 Farm" in pg.inner_text("#zlist"), "gathering spots listed with their type")

    pg.goto(base + "#map"); pg.wait_for_timeout(500)
    check(pg.is_visible("#baseBtn"), "floor 1 shows the base-map button")
    pg.click("#baseBtn"); pg.wait_for_timeout(600)
    n0 = pg.evaluate("[...document.querySelectorAll('#tiles img')].filter(i=>i.complete&&i.naturalWidth===256).length")
    check(n0 >= 9 and pg.is_visible("#tiles"), "base-map button switches to the tiled explored map")
    for _ in range(4):
        pg.click("#zin"); pg.wait_for_timeout(150)
    pg.wait_for_timeout(900)
    hi = pg.evaluate("[...document.querySelectorAll('#tiles img.hi')].map(i=>i.src.split('/tiles/f1jm/')[1])")
    check(len(hi) > 0 and len(hi) < 60 and all(h and not h.startswith("0/") for h in hi),
          "zooming in loads only the visible higher-resolution tiles")
    pg.click("#baseBtn"); pg.wait_for_timeout(200)
    pg.goto(base + "#f2-map"); pg.wait_for_timeout(400)
    check(pg.is_hidden("#tiles") and pg.evaluate("document.getElementById('mapImg').style.visibility") != "hidden",
          "floor 2 still uses its single map image")

    pg.goto(base + "#report"); pg.wait_for_timeout(400)
    check(pg.text_content(".rform code") == r"%APPDATA%\.Triggers Client\instances\Sword Art Online\screenshots",
          "report tab shows the F2 screenshot folder path with its backslashes")

    pg.goto(base + "#f2-report"); pg.wait_for_timeout(400)
    href = pg.get_attribute("#formGo", "href") or ""
    check("docs.google.com/forms" in href and href.endswith("=2"), "report tab links to the Google Form with floor 2")
    b.close()
srv.shutdown()
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
