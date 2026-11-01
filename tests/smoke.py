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
            for v in ("map", "monsters", "items", "props", "quests", "equip", "bosses", "report"):
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
    steps_y = pg.locator("#pBody .mqs").bounding_box()["y"]; map_y = pg.locator("#pBody .qmap").bounding_box()["y"]
    check(steps_y < map_y, "quest panel lists the steps above the route map")
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

    pg.goto(base + "#f1-map"); pg.wait_for_timeout(500)
    zl = pg.inner_text("#zlist")
    check("傳送點 13" in zl and pg.locator(".town.tp").count() == 7 and pg.locator(".town:not(.tp)").count() == 1,
          "13 teleport points: 7 towns marked as teleports, Vallhat is not")
    n = pg.locator(".zone.shop").count()
    pg.click(".legend .lgt[data-k=shop]"); pg.wait_for_timeout(300)
    check(n == 16 and pg.locator(".zone.shop").count() == 0, "16 loot buyers on the map and the legend hides them")
    pg.click(".legend .lgt[data-k=shop]"); pg.wait_for_timeout(200)

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
