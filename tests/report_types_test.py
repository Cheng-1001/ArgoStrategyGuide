"""New report types from the Google form (配方 / 任務追蹤 / 技能 / extended 地點) and how the site uses them.

Usage (repo root, after src/build.py): python3 tests/report_types_test.py
Serves the site with reports.js = the real reports + fake approved ones and checks the integration. Exits 1 on failure.
"""
import http.server, json, os, re, sys, threading
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8792
src = open(os.path.join(ROOT, "reports.js"), encoding="utf-8").read()
m = re.match(r"^([\s\S]*?window\.SAO_REPORTS\s*=\s*)(\[[\s\S]*\])\s*;?\s*$", src)
reports = json.loads(m.group(2))
rep = lambda id_, typ, name, raw: {"id": id_, "type": typ, "floor": 1, "name": name, "date": "2026-11-02", "raw": raw, "source": "form"}
reports += [
    rep("T101", "recipe", "Shark Amulet", {"配方・NPC": "Shark Accessories", "配方・分類": "飾品", "配方・材料": "Shark Carapace 9\nBirch String 1",
                                          "配方・費用 Col": "31", "配方・製作時間（秒）": "20", "回報者・遊戲內暱稱": "Kirito_TW"}),
    rep("T102", "recipe", "Iron Sword", {"配方・NPC": "Weaponsmith", "配方・分類": "武器", "配方・材料": "Iron Ingot 3", "配方・費用 Col": "0", "配方・稀有度": "稀有"}),
    rep("T103", "quest", "A New World", {"任務・種類": "主線", "任務・編號": "1", "任務・目前步驟": "Talk to Yui", "任務・座標 x, z": "1700, 4300"}),
    rep("T104", "skill", "Boule de Feu", {"技能・職業": "Mage", "技能・主動或被動": "主動", "技能・解鎖等級": "1", "技能・說明原文": "Lance une boule de feu"}),
    rep("T105", "place", "Test Smith", {"地點・種類": "NPC", "地點・座標 x, z": "1800, 4100", "地點・NPC 類別": "武器鐵匠"}),
    rep("T106", "place", "Test Gate", {"地點・種類": "傳送點", "地點・座標 x, z": "2000, 3000", "地點・傳送選單名稱": "Porte de Test"}),
    rep("T107", "place", "Pumba", {"地點・種類": "首領位置", "地點・座標 x, z": "1900, 3550", "地點・在地下嗎": "地下（要從入口走下去）"}),
    rep("T108", "place", "Putrid Swamp", {"地點・種類": "怪物區", "地點・座標 x, z": "1400, 3100"}),
    rep("T109", "jmap", "My map", {"探索地圖・說明": "north road"}),
    {**rep("T110", "idea", "Mark my position", {"建議・內容": "Show where I am on the map", "建議・相關頁面": "地圖", "回報者・遊戲內暱稱": "Asuna"}), "review": "審核：someone@example.com｜已排入待辦"},
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
    pg.add_init_script("localStorage.setItem('sao-map-filter-v4','{}')")
    base = f"http://127.0.0.1:{PORT}/index.html"
    # recipes
    pg.goto(base + "#recipes"); pg.wait_for_timeout(500)
    pg.fill("#q", "Shark Amulet"); pg.wait_for_timeout(250)
    card = pg.locator("#lRc .rcard", has_text="Shark Amulet").first
    t = card.inner_text()
    check("玩家回報" in t and "Shark Shell ×9" in t and "31 Col" in t, "recipe report replaces the same NPC + item (material name mapped, cost)")
    card.click(); pg.wait_for_timeout(300)
    check("T101" in pg.inner_text("#pBody") and "20 秒" in pg.inner_text("#pBody"), "recipe panel names the report")
    pg.click("#pClose"); pg.fill("#q", "Iron Sword"); pg.wait_for_timeout(250)
    t = pg.inner_text("#lRc")
    check("Iron Sword" in t and "Weaponsmith" in t and "免費" in t and "稀有" in t, "recipe report for a new NPC adds a row")
    pg.fill("#q", "")
    # quest
    pg.goto(base + "#quests"); pg.wait_for_timeout(400)
    num = pg.locator("#view-quests .card", has_text="A New World").first.locator(".mqn")
    check(num.inner_text().strip() == "1" and "nonum" not in (num.get_attribute("class") or ""), "main quest number from the tracker report")
    pg.locator("#view-quests .card", has_text="A New World").first.click(); pg.wait_for_timeout(300)
    t = pg.inner_text("#pBody")
    check("玩家回報" in t and "Talk to Yui" in t and "T103" in t, "quest panel lists the report")
    pg.click("#pClose")
    # skill
    pg.goto(base + "#classes"); pg.wait_for_timeout(400)
    card = pg.locator("#lCls .card", has_text="Mage").first
    check("技能回報 1" in card.inner_text(), "class card counts skill reports")
    card.click(); pg.wait_for_timeout(300)
    t = pg.inner_text("#pBody")
    check("技能（玩家回報）" in t and "Boule de Feu" in t and "Lance une boule de feu" in t, "class panel lists reported skills before the wiki list")
    pg.click("#pClose")
    # places
    pg.goto(base + "#f1-map"); pg.wait_for_timeout(800)
    zl = pg.inner_text("#zlist")
    check("Test Smith" in zl and "Test Gate" in zl, "place reports: new NPC and teleport point are on the map list")
    check(pg.locator('.bsp[title*="Pumba"]').count() == 6 and pg.locator('.bsp.ug[title*="Pumba"]').count() == 1, "boss place report adds an underground spawn")
    pg.locator("#zlist .zn", has_text="Putrid Swamp").first.click(); pg.wait_for_timeout(300)
    check("玩家回報的座標" in pg.inner_text("#pBody") and "T108" in pg.inner_text("#pBody"), "a report for a known place is attached, the point is not moved")
    pg.goto(base + "#report"); pg.wait_for_timeout(400)
    t = pg.inner_text("#doneL")
    check("配方・Iron Sword" in t and "技能・Boule de Feu" in t and "任務・A New World" in t and "看配方" in t and "看職業" in t and "看任務" in t,
          "received list labels the new types and links to them")
    check("探索地圖・My map" in t and "合併中" in t, "an approved JourneyMap upload shows as merging until jmmeta.js has its result")
    check("Mark my position" not in t, "suggestions are not listed with the data reports")
    check("Kirito_TW 提供" in t, "the reporter's in-game nickname is shown with the report")
    pg.goto(base + "#feedback"); pg.wait_for_timeout(400)
    t = pg.inner_text("#ideaL")
    check("Mark my position" in t and "Show where I am on the map" in t and "回覆：已排入待辦" in t and "someone@example.com" not in t,
          "approved suggestions are listed under 玩家建議 with the reviewer's reply (reviewer account hidden)")
    check("Asuna 提出" in t, "the suggestion shows who proposed it (nickname)")
    check("viewform" in (pg.get_attribute("#ideaGo", "href") or ""), "提出建議 opens the Google form")
    check(not errs, "no page errors" + ("" if not errs else ": " + errs[0]))
    b.close()
srv.shutdown()
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
