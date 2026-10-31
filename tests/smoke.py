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
            for v in ("map", "monsters", "items", "quests", "bosses", "report"):
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

    pg.goto(base + "#f1-map"); pg.wait_for_timeout(500)
    n = pg.locator(".zone.shop").count()
    pg.click(".legend .lgt[data-k=shop]"); pg.wait_for_timeout(300)
    check(n == 16 and pg.locator(".zone.shop").count() == 0, "16 loot buyers on the map and the legend hides them")
    pg.click(".legend .lgt[data-k=shop]"); pg.wait_for_timeout(200)

    pg.goto(base + "#map"); pg.wait_for_timeout(500)
    check(pg.is_visible("#baseBtn"), "floor 1 shows the base-map button")
    pg.click("#baseBtn"); pg.wait_for_timeout(400)
    src = pg.evaluate("document.getElementById('mapImg').src")
    check(src.endswith("floor1_jm.jpg"), "base-map button switches to the explored map")
    pg.click("#baseBtn"); pg.wait_for_timeout(200)

    pg.goto(base + "#f2-report"); pg.wait_for_timeout(400)
    href = pg.get_attribute("#formGo", "href") or ""
    check("docs.google.com/forms" in href and href.endswith("=2"), "report tab links to the Google Form with floor 2")
    b.close()
srv.shutdown()
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
