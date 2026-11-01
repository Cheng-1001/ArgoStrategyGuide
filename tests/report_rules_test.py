"""How approved reports are matched to monsters (codex screenshots win over the wiki).

Usage (repo root, after src/build.py): python3 tests/report_rules_test.py
Serves the site with reports.js = the real reports + a few fake ones and checks:
  - official 3-digit codex number -> same monster, renamed, old names kept as aliases
  - no number -> matched by name / alias only (R0001 Young Spider)
  - no number and unknown name -> a new "player reported" monster, nothing renamed
  - reviewer note "舊名：X" -> monster X renamed to the reported name
  - unofficial numbers such as 014-2 are never used for matching
Exits 1 on failure.
"""
import http.server, json, os, re, sys, threading
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8791
src = open(os.path.join(ROOT, "reports.js"), encoding="utf-8").read()
m = re.match(r"^([\s\S]*?window\.SAO_REPORTS\s*=\s*)(\[[\s\S]*\])\s*;?\s*$", src)
reports = json.loads(m.group(2))
fake = lambda id_, name, raw, review=None: {"id": id_, "type": "monster", "floor": 1, "name": name, "date": "2026-11-01",
                                           "raw": raw, "source": "form", **({"review": review} if review else {})}
reports += [
    fake("T001", "Mountain Elk", {"怪物・截圖種類": "圖鑑截圖（Codex）", "怪物・圖鑑編號": "#018", "怪物・圖鑑區域": "Montagnes de Tolbana"}),
    fake("T002", "Yung Spider", {"怪物・等級": "4"}),
    fake("T003", "Cave Spider", {"怪物・等級": "5"}, "審核：rev｜舊名：Young Spider"),
    fake("T004", "Forest Spider Mk2", {"怪物・圖鑑編號": "014-2"}),
]
body = m.group(1) + json.dumps(reports, ensure_ascii=False) + ";\n"


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, *a):
        pass


fails = []


def check(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c:
        fails.append(msg)


srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.route("**/reports.js*", lambda r: r.fulfill(status=200, content_type="application/javascript; charset=utf-8", body=body))
    pg.route("https://fonts.*/**", lambda r: r.abort())

    def find(q):
        pg.goto(f"http://127.0.0.1:{PORT}/index.html#monsters"); pg.wait_for_timeout(300)
        pg.fill("#q", q); pg.wait_for_timeout(250)
        return pg.eval_on_selector_all("#lMon .card .cname b", "e=>e.map(x=>x.textContent)")

    def detail(q):
        find(q); pg.locator("#lMon .card").first.click(); pg.wait_for_timeout(300)
        return pg.inner_text("#pBody")

    # official codex number renames, old names become aliases, position and hint still work
    check(find("Mountain Deer") == ["Mountain Elk"] and find("Mountain Stag") == ["Mountain Elk"],
          "codex #018 renames Mountain Deer -> Mountain Elk; both old names still find it")
    t = detail("Mountain Elk")
    check("舊名：Mountain Stag、Mountain Deer" in t and "遊戲圖鑑 #018" in t, "renamed monster shows its old names and why")
    check("Montagnes de Tolbana" in t and "X 4102" in t, "codex region shown, map position kept after the rename")
    check(find("Albal") == ["Albal"], "Albal report with matching codex #006 keeps the name")
    # no number: name / reviewer note
    check(find("Yung Spider") == ["Yung Spider"] and "玩家回報新增" in detail("Yung Spider"),
          "unknown name without a number becomes a new player-reported monster")
    t = detail("Cave Spider")
    check(find("Young Spider") == ["Cave Spider"] and "舊名：Young Spider" in t and "審核員確認" in t,
          "reviewer note 舊名：Young Spider renames Young Spider -> Cave Spider")
    check("等級 3" in t and "R0001" in t, "R0001 (matched by name before the rename) stays on the renamed monster")
    # unofficial number never matches
    check(find("Forest Spider") == ["Forest Spider", "Forest Spider Mk2"],
          "014-2 is not an official number: Forest Spider (#014) untouched, Mk2 added separately")
    check(not errs, "no page errors" + ("" if not errs else ": " + errs[0]))
    b.close()
srv.shutdown()
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
