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
            for v in ("map", "monsters", "items", "props", "recipes", "quests", "equip", "classes", "bosses", "report"):
                pg.goto(f"{base}#f{f}-{v}")
                pg.wait_for_timeout(250)
                if w < 500:
                    over = pg.evaluate("document.documentElement.scrollWidth>innerWidth")
                    if over:
                        check(False, f"no horizontal scroll at {w}px: f{f}-{v}")
        pg.close()
    check(not errs, "no page errors on any tab" + ("" if not errs else ": " + errs[0]))

    pg = b.new_page(viewport={"width": 390, "height": 844})
    pg.goto(base + "#f1-quests"); pg.wait_for_timeout(500)
    pg.evaluate("__updCheck()"); pg.wait_for_timeout(400)
    no_bar = pg.locator("#updBar").count() == 0
    pg.route("**/index.html?_=*", lambda r: r.fulfill(status=200, content_type="text/html",
             body=open(os.path.join(ROOT, "index.html"), encoding="utf-8").read().replace('name="sao-build" content="', 'name="sao-build" content="ff', 1)))
    pg.evaluate("__updCheck()"); pg.wait_for_timeout(400)
    bar = pg.locator("#updBar").count() == 1 and "網站有更新" in pg.inner_text("#updBar")
    over = pg.evaluate("document.documentElement.scrollWidth>innerWidth")
    pg.click("#updBar .ub-go"); pg.wait_for_timeout(1200)
    check(no_bar and bar and not over and pg.url.endswith("/index.html#f1-quests") and pg.evaluate("!!document.querySelector('meta[name=sao-build]')"),
          "update check: no bar when the live page is the same build; a newer build shows the bar, which reloads (and drops ?u=)")
    pg.close()

    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(base + "#f1-map"); pg.wait_for_timeout(500)
    check(pg.eval_on_selector_all("#fpCats .fchip", "e=>e.filter(b=>!b.dataset.k.includes(':')&&b.getAttribute('aria-pressed')==='true').map(b=>b.dataset.k).join(',')") == "tp,land,area,mobs"
          and pg.locator(".bsp").count() == 0 and pg.locator(".town.dungeon").count() == 0, "default map filter: teleports, landmarks, monster areas, regular monsters")
    pg.click('#fpCats .fchip[data-k="npc"]'); pg.wait_for_timeout(200)
    on = pg.eval_on_selector_all("#fpFly .fchip", "e=>e.filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.dataset.k).join(',')")
    check(on == "npc:potion,npc:loot,npc:key,npc:acc", f"default NPC sub-categories: the 4 chosen ones ({on})")
    pg.evaluate("localStorage.setItem('sao-map-filter-v5','{}')")   # the rest of the tests start with everything on
    pg.reload(); pg.wait_for_timeout(300)
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
    c24 = seal.locator(".mqt b").inner_text()
    pg.click("[data-go='q|mq1_33']"); pg.wait_for_timeout(400)
    t34 = pg.inner_text("#pBody")
    check(c24 == "封印的真相" and pg.inner_text("#pBody h2") == "水晶之下" and "Beneath the Crystal" in pg.inner_text("#pBody .sub")
          and "門開了。梅菲斯特在托爾巴納的水晶下等候" in t34 and "遊戲：前往水晶下方（Go down beneath the crystal）" in t34 and "💡 水晶下面是浮空島" in t34,
          "main quests use the official Chinese title and quest-log text (English as subtitle; objectives with the English line; our tip below)")
    pg.locator("#pBody .stimg a").first.click(); pg.wait_for_timeout(300)
    iz = pg.evaluate("(()=>{const z=document.querySelector('.imgzoom');return {open:!!z,img:z&&z.querySelector('img').complete,pages:pg_count=0}})()".replace("pg_count=0","1"))
    check(iz["open"] and len(pg.context.pages) == 1, "quest step picture opens in a viewer on the page, not a new tab")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    check(pg.locator(".imgzoom").count() == 0 and pg.is_visible("#panel"), "Esc closes the picture viewer and keeps the quest panel")
    pg.fill("#q", "梅菲斯特"); pg.wait_for_timeout(300)
    check(pg.locator("#lQ .qcard", has_text="梅菲斯特").count() >= 3, "searching a Chinese quest NPC name finds the main quests")
    pg.fill("#q", ""); pg.wait_for_timeout(200)
    pg.click("[data-go='q|mq1_15']"); pg.wait_for_timeout(400)
    check(pg.locator("#pBody .qmap svg polyline").count() == 1 and pg.locator("#pBody .mqs li").count() >= 5,
          "clicking a main quest opens the panel with its steps and a route mini map")
    check(pg.evaluate("(()=>{const b=document.getElementById('pBody');const m=b.querySelector('.qmap');return [...b.children].slice([...b.children].indexOf(m)+1).every(e=>e.matches('[data-route],.srcend'))&&b.lastElementChild.matches('.srcend')})()"),
          "quest panel: the route map is the last block before the source note (only the enlarge button between; source note at the very bottom)")
    pg.click("#pBody [data-route]"); pg.wait_for_timeout(600)
    vb0 = pg.get_attribute("#rwSvg", "viewBox")
    check(pg.is_visible("#rwin") and pg.locator("#rwSvg polyline").count() == 1, "enlarge opens the floating route window")
    pg.click("#rwIn"); pg.wait_for_timeout(200)
    check(pg.get_attribute("#rwSvg", "viewBox") != vb0, "the route window zooms")
    pg.click("#rwX"); pg.wait_for_timeout(200)
    check(not pg.is_visible("#rwin"), "the route window closes")
    pg.goto(base + "#quests"); pg.wait_for_timeout(300)
    pg.click('#fQKind .chip[data-v="side"]'); pg.wait_for_timeout(300)
    bone = pg.locator(".qside", has_text="白骨與塵土").first
    check(bone.count() == 1 and "Bone and Dust" in bone.inner_text() and "檔案管理員歐林" in bone.inner_text(),
          "side quests from the quest log show the official Chinese title and NPC (English title kept)")
    pg.locator(".qside", has_text="Daiki").first.click(); pg.wait_for_timeout(400)
    t = pg.inner_text("#pBody")
    check("收集 Boar Hide ×5" in t and "掉落" in t and pg.locator("#pBody .qmap svg").count() == 1,
          "side quest panel spells out what to collect, where it drops, and shows the route")

    pg.goto(base + "#equip"); pg.wait_for_timeout(500)
    total = pg.locator("#lEq .card").count()
    pg.click("#fEqPart .chip[data-v=weapon]"); pg.wait_for_timeout(200)
    pg.locator("#lEq .card").first.click(); pg.wait_for_timeout(300)
    check(total > 100 and "官方圖鑑 #" in pg.inner_text("#pBody"), "equipment tab lists official items and opens a detail")

    pg.goto(base + "#map"); pg.wait_for_timeout(400)
    pg.click("#aboutBtn"); pg.wait_for_timeout(150)
    check(pg.is_visible("#aboutMenu") and pg.inner_text("#aboutMenu").split() == ["介紹及資訊", "更新紀錄", "網頁導覽"], "關於本站 opens a menu: 介紹及資訊, 更新紀錄, 網頁導覽")
    pg.click("#logBtn"); pg.wait_for_timeout(300)
    check(pg.is_hidden("#aboutMenu") and pg.url.endswith("#changelog") and pg.is_visible("#changelog") and pg.locator('#aboutBtn[aria-current="page"]').count() == 1, "更新紀錄 in the menu opens the changelog page")
    pg.click("#aboutBtn"); pg.wait_for_timeout(150); pg.mouse.click(400, 600); pg.wait_for_timeout(150)
    check(pg.is_hidden("#aboutMenu"), "the menu closes when clicking elsewhere")
    check(pg.locator("#tour").count() == 0, "the tour does not start by itself in automated browsers")
    pg.click("#aboutBtn"); pg.wait_for_timeout(150); pg.click("#tourBtn"); pg.wait_for_timeout(400)
    steps = pg.evaluate("saoTour.steps"); seen = []
    for k in range(steps):
        seen.append(pg.inner_text("#tour .tour-card h3"))
        if k == 4: mapok = pg.url.endswith("#map")
        pg.click("#tour .tour-card button.pri"); pg.wait_for_timeout(350)
    check(steps == 9 and seen[4] == "篩選器" and seen[5] == "地圖" and "兩種底圖" not in seen and mapok and pg.locator("#tour").count() == 0
          and pg.evaluate("localStorage.getItem('sao-tour-v1')") == "done", "網頁導覽: 9 steps, the filter step switches to the map, finishing closes it and remembers")
    pg.evaluate("localStorage.removeItem('sao-tour-v1')")
    pg.click("#aboutBtn"); pg.wait_for_timeout(150); pg.click("#tourBtn"); pg.wait_for_timeout(400)
    pg.click("#tour .tour-card button.skip"); pg.wait_for_timeout(400)
    last = pg.inner_text("#tour .tour-card h3") if pg.locator("#tour").count() else ""
    pg.click("#tour .tour-card button.pri"); pg.wait_for_timeout(300)
    check(last == "導覽結束" and pg.locator("#tour").count() == 0 and pg.evaluate("localStorage.getItem('sao-tour-v1')") == "done", "網頁導覽: 略過 jumps to the last step, which then closes the tour")
    pg.goto(base + "#quests"); pg.wait_for_timeout(400); pg.click('#fQKind .chip[data-v="main"]'); pg.fill("#q", "hanaka merchant"); pg.wait_for_timeout(300)
    hit_q = pg.inner_text("#cQ").startswith("1 /")
    pg.locator("#lQ [data-go]", has_text="The Geldorak Mine").first.click(); pg.wait_for_timeout(400)
    marks = pg.eval_on_selector_all(".qmap g[data-xz] text", "e=>e.map(x=>x.textContent)")
    check(hit_q and "遊戲原文：(Bonus) Hand the rare material" in pg.inner_text("#pBody") and marks == ["1–4", "5", "6"],
          "main quest steps keep the in-game English text (searchable); close route points merge into one marker 1–4")
    pg.click("#pClose"); pg.fill("#q", ""); pg.evaluate("localStorage.removeItem('sao-map-filter-v5')"); pg.goto(base + "#map"); pg.reload(); pg.wait_for_timeout(800)
    n0 = pg.locator("#view-map .npc").count(); pg.fill("#q", "hanaka"); pg.wait_for_timeout(500)
    check(n0 == 0 and pg.locator("#view-map .npc.hit").count() == 1 and pg.locator("#zlist", has_text="商店-哈娜卡").count() == 1,
          "map search shows matching NPCs even when the NPC filter is off")
    pg.fill("#q", ""); pg.wait_for_timeout(300); pg.click("#fpAll"); pg.wait_for_timeout(300)
    pg.goto(base + "#recipes"); pg.wait_for_timeout(400)
    tot = pg.locator("#lRc .rcard").count()
    pg.click('#fRcCat .chip[data-v="key"]'); pg.wait_for_timeout(200)
    check(tot >= 100 and pg.locator("#lRc .rcard").count() == 4 and "Forest Key" in pg.inner_text("#lRc"), "recipes tab: 100+ recipes, key filter shows the 4 dungeon keys")
    check(pg.locator('nav.tabs a[data-v="recipes"][aria-current="page"]').count() == 1 and pg.is_hidden("#codexTabs")
          and pg.eval_on_selector_all("nav.tabs a", "e=>e.map(a=>a.dataset.v).join(',')") == "map,codex,quests,recipes,dungeons,classes,bosses" and pg.locator("#collabBtn").count() == 1,
          "top tabs: recipes after quests, then dungeons, classes, world bosses; collaboration is a button by the changelog")
    pg.click('nav.tabs a[data-v="dungeons"]'); pg.wait_for_timeout(300)
    dn = pg.eval_on_selector_all("#lDg .card b", "e=>e.map(x=>x.textContent)")
    check(len(dn) == 5 and dn[0] == "Sanctuary of Souls" and "狗頭人之塔" not in dn and "墮落者迷宮區" in dn, f"dungeons tab lists the event dungeon first, then the 4 floor-1 dungeons, not the boss tower ({dn})")
    pg.click('#lDg [data-go="d|souls"]'); pg.wait_for_timeout(300)
    check("Sanctuary of Souls Key" in pg.inner_text("#pBody") and pg.locator("#pBody .btbl").count() == 2 and "一般抽取" not in pg.inner_text("#pBody"),
          "event dungeon panel: key recipe, fragment zones and forge tables; no gacha rate table (gacha is only a source)")
    dg = pg.evaluate("(()=>({cols:getComputedStyle(document.getElementById('lDg')).gridTemplateColumns.split(' ').length,keys:document.querySelectorAll('#lDg .th.dgk').length,inline:document.body.classList.contains('cls-inline'),close:!!document.getElementById('pClose').offsetParent,kn:[...document.querySelectorAll('#lDg .dgkn')].map(e=>e.textContent)}))()")
    pg.click('#lDg [data-go="s|xal"]'); pg.wait_for_timeout(250)
    check(pg.locator("#pBody .phead .th.dgk").count() == 1, "the dungeon shown on the page uses its key as the header icon")
    check(dg["cols"] == 1 and dg["keys"] == 3 and dg["inline"] and not dg["close"] and "鑰匙：森林鑰匙" in dg["kn"],
          f"dungeons: one column, each floor dungeon shows its own key icon, the dungeon is shown on the page next to the list (no window frame) ({dg})")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
    check(not pg.is_hidden("#panel"), "Esc does not close the dungeon shown on the page")
    pg.goto(base + "#equip"); pg.wait_for_timeout(400)
    pg.fill("#fEqEff", "爆擊率"); pg.wait_for_timeout(300)
    ef = pg.evaluate("(()=>({n:document.querySelectorAll('#lEq .card').length,st:[...document.querySelectorAll('#lEq .card .estat')].slice(0,30).every(e=>e.textContent.includes('爆擊率')),inHead:!!document.querySelector('#view-equip .rhead #fEqEff'),chip:[...document.querySelectorAll('#view-equip .actf .af')].some(b=>b.textContent.includes('爆擊率')),opts:document.querySelectorAll('#dlEqEff option').length}))()")
    check(ef["n"] > 10 and ef["st"] and ef["inHead"] and ef["chip"] and ef["opts"] > 15, f"equipment effect filter next to the list title: only items with the effect, card shows the value, active-filter chip ({ef})")
    pg.fill("#fEqEff", ""); pg.fill("#q", "孱弱之狼"); pg.wait_for_timeout(300)
    wn = pg.inner_text("#lEq")
    check("阿爾巴爾項鍊" in wn and "狼戒指" in wn and "群狼手套" in wn, "searching a set name lists its members (Albal's Necklace via the Weakling Wolf Set)")
    pg.fill("#q", ""); pg.wait_for_timeout(200)
    pg.goto(base + "#props"); pg.wait_for_timeout(400); pg.fill("#q", "Bourse de 500Cols"); pg.wait_for_timeout(300)
    pg.locator("#view-props .card").first.click(); pg.wait_for_timeout(300)
    gt = pg.inner_text("#pBody")
    check("可以從商城的「Aincrad 轉蛋」抽到" in gt and "%" not in gt.split("轉蛋")[-1].split("轉蛋內容")[0], "gacha shows as an obtain source on the item, without rates (Pouch of 500 Cols)")
    pg.fill("#q", ""); pg.wait_for_timeout(200)
    pg.click("#legalBtn"); pg.wait_for_timeout(350)
    t = pg.inner_text("#legal")
    check("about" in pg.url and pg.is_visible("#view-about") and "非官方" in t and "Triggers SAO" in t and "GitHub Issues" in t and "中文玩家社群協力製作" in t,
          "floor-bar copyright link opens the notice on the about page")
    box_a = pg.locator("#aboutBtn").bounding_box(); box_q = pg.locator(".gsearch").bounding_box()
    t = pg.inner_text("#aWrap")
    check(pg.locator('#aboutBtn[aria-current="page"]').count() == 1 and box_a["x"] + box_a["width"] <= box_q["x"] and abs(box_a["y"] - box_q["y"]) < 20
          and "資料來源" in t and "SAO MC Interactive Map" in t and "Minecraft Wiki" in t
          and pg.locator('#aWrap a[href="https://discord.gg/HdHba5awgn"]').count() == 1 and pg.locator('#aWrap a[href="https://saominecraft.com/"]').count() == 1,
          "about button sits left of the search box; about page lists official links, data sources and the notice")
    pg.goto(base + "#recipes"); pg.wait_for_timeout(400)
    pg.click('#fRcCat .chip[data-v="potion"]'); pg.wait_for_timeout(200)
    pg.locator("#lRc .rcard", has_text="Quality Health Potion I").first.click(); pg.wait_for_timeout(300)
    t = pg.inner_text("#pBody")
    check(pg.locator("#lRc .rcard.sel").count() == 1 and "煉金術士" in t and "Sylve Sprout" in t and "× 8" in t,
          "clicking one potion recipe selects only that card and opens its recipe panel")
    check(pg.locator('#lRc .rcard', has_text="Quality Health Potion I").first.locator('img[src="icons/recipes/quality_health_potion_i.png"]').count() == 1,
          "Quality Health Potion I uses the game icon from recicons.js (game icons win over the official catalogue)")
    pg.locator("#pBody .lrow", has_text="Allium").first.click(); pg.wait_for_timeout(300)
    check(pg.locator("#pBody .qmap svg").count() == 1 and pg.locator("#pBody .rnum").count() >= 1 and pg.locator("#pBody [data-imap]").count() == 1,
          "material panel (Allium) shows a numbered map of where to get it")
    icons = pg.eval_on_selector_all("#pBody .recipes .lrow .eslot.empty", "e=>e.map(x=>x.textContent.trim())")
    check(icons and "💍" not in icons, f"potion recipes under 可以拿去製作 use the potion icon ({set(icons)})")
    pg.click("#pBody [data-imap]"); pg.wait_for_timeout(400)
    check(pg.is_visible("#rwin") and pg.locator("#rwSvg polyline").count() == 0, "enlarged item map opens without a route line")
    pg.click("#rwX") if pg.locator("#rwX").count() else None; pg.wait_for_timeout(150)
    pg.click("#pClose"); pg.wait_for_timeout(150)
    pg.goto(base + "#items"); pg.wait_for_timeout(300); pg.fill("#q", "Magic Mycelium"); pg.wait_for_timeout(300)
    pg.locator("#lItem .card").first.click(); pg.wait_for_timeout(300)
    labels = pg.eval_on_selector_all("#pBody .qmap svg g:not(.refm) text", "e=>e.map(x=>x.textContent)")
    check(labels and set(labels) == {"1"}, f"one source with several spawn points (Guardian Colossal) is numbered 1 at every point ({labels})")
    pg.fill("#q", ""); pg.click("#pClose"); pg.wait_for_timeout(150)
    pg.goto(base + "#monsters"); pg.wait_for_timeout(400)
    pg.fill("#q", "Albal"); pg.wait_for_timeout(250)
    pg.locator("#lMon .card", has_text="Albal").first.click(); pg.wait_for_timeout(300)
    pg.locator("#pBody [data-rep]").first.click(); pg.wait_for_timeout(500)
    check(pg.is_visible("#rwin") and "#monsters" in pg.url and pg.locator("#rwSvg g:not(.refm)").count() == 3 and pg.locator("#rwSvg polyline").count() == 0,
          "codex: a spawn coordinate opens the floating map window (all 3 Albal spawns), the codex stays")
    pg.click("#rwX"); pg.wait_for_timeout(150)
    pg.locator("#pBody [data-rep]").nth(1).click(); pg.wait_for_timeout(500)
    sel = pg.eval_on_selector_all("#rwSvg g.rwsel text", "e=>e.map(x=>x.textContent)")
    check(sel == ["2"] and "第 2 點（共 3 點）" in pg.inner_text("#rwTitle")
          and pg.locator("#pBody .rnum").count() == 3, "the clicked spawn is highlighted and named in the title; the panel numbers match the map")
    pg.click("#rwX"); pg.click("#pClose"); pg.fill("#q", ""); pg.wait_for_timeout(150)
    pg.goto(base + "#quests"); pg.wait_for_timeout(400)
    pg.click('#fQKind .chip[data-v="main"]'); pg.wait_for_timeout(200)
    pg.locator("#view-quests .card", has_text="Show Me").first.click(); pg.wait_for_timeout(300)
    pg.locator("#pBody .mqs [data-rep]").nth(2).click(); pg.wait_for_timeout(600)
    vb = pg.evaluate("document.getElementById('rwSvg').getAttribute('viewBox').split(' ').map(Number)")
    check(pg.is_visible("#rwin") and "#quests" in pg.url and pg.locator("#rwSvg polyline").count() == 1 and vb[2] < 200,
          f"quest step coordinate opens the route window zoomed to that step ({[round(v) for v in vb]})")
    pg.click("#rwX"); pg.click("#pClose"); pg.wait_for_timeout(150)
    check("100 xp" in pg.locator("#view-quests .card", has_text="Show Me").first.inner_text(), "main quest reward in the same format as side quests")
    pg.click('#fQKind .chip[data-v="side"]'); pg.fill("#q", "Pinceau Magique"); pg.wait_for_timeout(300)
    check(pg.locator("#view-quests .card").count() == 1 and "Nacht" in pg.inner_text("#view-quests"), "quest search finds an item reward")
    pg.locator("#view-quests .card", has_text="Nacht").first.click(); pg.wait_for_timeout(300)
    check(pg.locator('#pBody .rwi [data-go="p|2165"]').count() == 1, "a reward item that is in the codex links to it (Pinceau Magique)")
    pg.click("#pClose"); pg.wait_for_timeout(150)
    pg.fill("#q", "Skeleton Warrior"); pg.wait_for_timeout(300)
    check("Bone and Dust" in pg.inner_text("#view-quests"), "quest search finds kill targets in the steps")
    pg.fill("#q", ""); pg.click('#fQKind .chip[data-v="main"]'); pg.wait_for_timeout(200)
    pg.goto(base + "#recipes"); pg.wait_for_timeout(400)
    pg.locator("#lRc .rcard", has_text="Quality Health Potion II").first.click(); pg.wait_for_timeout(300)
    pg.locator("#pBody [data-go^='n|']").first.click(); pg.wait_for_timeout(300)
    pg.locator("#pBody [data-rep]").first.click(); pg.wait_for_timeout(500)
    check(pg.is_visible("#rwin") and "#recipes" in pg.url and pg.locator("#rwSvg g:not(.refm)").count() == 1 and "Alchemist" in pg.inner_text("#rwTitle"),
          "recipe -> Alchemist -> 在地圖上查看 opens the floating map window with one point, the recipes tab stays")
    pg.click("#rwX"); pg.click("#pClose"); pg.wait_for_timeout(150)
    pg.goto(base + "#classes"); pg.wait_for_timeout(400)
    check(pg.locator("#lCls .card").count() == 6 and pg.is_hidden("#codexTabs"), "classes tab lists the 6 classes")
    pg.locator("#lCls .card", has_text="Guerrier").click(); pg.wait_for_timeout(300)
    t = pg.evaluate("document.getElementById('pBody').textContent")
    check("Combinaison Brutale" in t and "Paladin" in t and "起始屬性" in t and "Physical Might" in t and "佔位圖" not in t,
          "Guerrier panel: skills, specialisations, base stats and talents")
    fold = pg.evaluate("(()=>{const L=document.querySelector('#pBody .cls2>div:first-child');return {n:L.querySelectorAll('details.clsfold').length,open:L.querySelectorAll('details.clsfold[open]').length,t:[...L.querySelectorAll('details.clsfold>summary')].map(s=>s.textContent)}})()")
    check(fold["n"] == 3 and fold["open"] == 0 and "天賦樹" in fold["t"][2], f"ability stars, base stats and talent tree sit together in the left column, folded ({fold})")
    check(pg.locator("#pBody img").count() == 0, "no class or skill pictures")
    pg.evaluate("document.querySelector('#lCls [data-go=\"c|archer\"]').click()"); pg.wait_for_timeout(300)
    t = pg.inner_text("#pBody")
    check("技能（遊戲畫面）" in t and "迴避射擊" in t and "終極技能" in t and "等級上限 18" in t and "Embuscade" in t and "技能畫面裡都沒有出現" in t
          and "遊戲技能 20" in pg.inner_text("#lCls"), "Archer panel: in-game skills with slots and level caps; wiki list marked as not in the game")
    rows = pg.evaluate("[...document.querySelectorAll('#pBody .gsklist>li>.lrow b')].map(x=>x.textContent)"); pb = pg.inner_text("#pBody")
    check(pg.locator("#pBody img.gskic").count() == 20 and pg.locator("#pBody details.gskup").count() == 6 and pg.locator("#pBody details.gskup[open]").count() == 0
          and rows[:2] == ["迴避射擊", "疾風戰刃"] and rows[-2:] == ["箭矢齊射", "爆裂連擊"] and "目前沒有裝備" in pb and "升級 2 個：集中箭雨、天空彈幕" in pb and "Tir Évasif" in pb,
          f"Archer skills: one row per base skill (equipped ones in slot order, then 箭矢齊射, then the weapon skill), upgrades folded, every skill has an icon ({rows})")
    pg.evaluate("document.querySelector('#lCls [data-go=\"c|guerrier\"]').click()"); pg.wait_for_timeout(300)
    top = pg.evaluate("(()=>{const b=document.getElementById('pBody'),c=b.querySelector('.cls2');return {first:[...b.children].indexOf(c),lore:!!c.querySelector('.lore'),facts:!!c.querySelector('.facts'),btn:!!c.querySelector('.clsbtns'),title:b.querySelector('h2').textContent,clx:[...document.querySelectorAll('#lCls .clx')].filter(e=>e.offsetParent).length}})()")
    check(top["first"] == 1 and top["lore"] and top["facts"] and top["btn"] and top["title"] == "戰士" and top["clx"] == 12,
          f"class panel: intro, difficulty/weapons/specs and buttons sit in the left column (no empty top-right); official Chinese title; list cards keep weapons and specs ({top})")
    cols = pg.evaluate("getComputedStyle(document.getElementById('lCls')).gridTemplateColumns.split(' ').length")
    pw = pg.locator("#panel").bounding_box()["width"]
    two = pg.evaluate("getComputedStyle(document.querySelector('#pBody .cls2')).gridTemplateColumns.split(' ').length")
    lr = pg.evaluate("document.getElementById('lCls').getBoundingClientRect().right"); px = pg.locator("#panel").bounding_box()["x"]
    check(cols == 1 and px >= lr and pw > 900 and two == 2, f"classes: one compact column, the panel fills the space right of it ({px:.0f}>={lr:.0f}, {pw:.0f}px), two inner columns at 1280 ({two})")
    pg.set_viewport_size({"width": 2000, "height": 1000}); pg.wait_for_timeout(300)
    two2 = pg.evaluate("getComputedStyle(document.querySelector('#pBody .cls2')).gridTemplateColumns.split(' ').length"); pw2 = pg.locator("#panel").bounding_box()["width"]
    check(two2 == 2 and pw2 > 1200, f"classes at 2000px: wide panel ({pw2:.0f}px) split in two ({two2})")
    pg.set_viewport_size({"width": 1280, "height": 900}); pg.wait_for_timeout(300)
    pg.click("#pBody [data-eqcls]"); pg.wait_for_timeout(300)
    n = pg.locator("#cwBody .card").count()
    check(pg.is_visible("#cwin") and n > 50 and "#equip" not in pg.url, f"equipment window opens over the classes tab ({n} items)")
    pg.locator("#cwBody .card").first.click(); pg.wait_for_timeout(300)
    check("官方圖鑑 #" in pg.inner_text("#cwBody") and "戰士" in pg.inner_text("#pCrumb"), "item detail opens inside the window; the class panel stays")
    pg.click("#cwBack"); pg.wait_for_timeout(200)
    check(pg.locator("#cwBody .card").count() == n, "back to the equipment list")
    pg.click("#cwX"); pg.wait_for_timeout(150)
    check(not pg.locator("#pClose").is_visible() and pg.evaluate("document.body.classList.contains('cls-inline')"), "the class is shown on the page (no ✕ / window frame)")
    pg.locator("#lCls .card", has_text="Martial Artist").click(); pg.wait_for_timeout(300)
    check("可能還沒開放" in pg.inner_text("#pBody") and "佔位圖" in pg.inner_text("#pBody"), "Martial Artist flagged as possibly unreleased, skills unconfirmed")
    pg.goto(base + "#monsters"); pg.wait_for_timeout(400)
    vt = pg.evaluate("""(()=>{const F=document.querySelector('#view-monsters .filters');const n=F.firstElementChild;
      return {cls:n.className,cur:n.querySelector('a[aria-current=page]')?.dataset.v,links:n.querySelectorAll('a').length,}})()""")
    check(vt["cls"] == "vtabs" and vt["cur"] == "monsters" and vt["links"] == 5 and pg.is_hidden("#codexTabs"),
          f"desktop: codex sub-tabs sit at the top of the left filter column ({vt})")
    pg.click('#view-monsters .vtabs a[data-v="equip"]'); pg.wait_for_timeout(300)
    check(pg.evaluate("location.hash").endswith("equip") and pg.locator('#view-equip .vtabs a[aria-current="page"][data-v="equip"]').count() == 1,
          "left-column codex tab switches to the equipment list")
    pg.click('#fEqPart .chip[data-v="acc"]'); pg.wait_for_timeout(200)
    af = pg.locator("#view-equip .actf .af")
    check(af.count() == 1 and "飾品" in af.first.inner_text(), "active filter row lists the chosen part")
    af.first.click(); pg.wait_for_timeout(200)
    check(pg.locator("#view-equip .actf .af").count() == 0 and pg.locator('#fEqPart .chip[data-v="all"][aria-pressed="true"]').count() == 1,
          "removing an active filter resets it in the left column")
    check(pg.locator("#view-equip .topf #fEqPart").count() == 1 and pg.locator("#view-equip .filters #fEqPart").count() == 0,
          "desktop: equipment part / rarity chips sit above the list, not in the left column")
    pg.click('#fEqPart .chip[data-v="off"]'); pg.wait_for_timeout(200)
    subs = pg.evaluate("[...document.querySelectorAll('#fEqSub .chip')].map(c=>c.dataset.v)")
    check(subs == ["all", "shield", "catalyst", "quiver"] and "副手" in pg.inner_text("#view-equip .actf"), f"副手 = shields + catalysts + quivers (game-only), with a sub-part row ({subs})")
    pg.click('#fEqPart .chip[data-v="armor"]'); pg.wait_for_timeout(200)
    tot = pg.locator("#lEq .card").count()
    parts = pg.evaluate("[...document.querySelectorAll('#fEqSub .chip .cn')].map(c=>+c.textContent)")
    check(len(parts) == 4 and sum(parts) == tot, f"every armour piece has a slot: head/chest/legs/feet {parts} add up to {tot}")
    pg.goto(base + "#props"); pg.wait_for_timeout(400)
    pg.click('#fPrGroup .chip[data-v="活動"]'); pg.wait_for_timeout(200)
    ev = pg.evaluate("[...document.querySelectorAll('#fPrSub .chip')].map(c=>c.textContent.replace(/\\s*\\d+$/,''))")
    check(set(ev) >= {"全部", "萬聖節", "聖誕節（2025）", "情人節", "農曆新年"}, f"event items split by event ({ev})")
    # four-tab codex: 怪物／裝備／道具／素材 (an item lives in exactly one tab; links open the right panel)
    pg.goto(base + "#items"); pg.wait_for_timeout(400)
    tabs = pg.evaluate("[...document.querySelectorAll('#view-items .vtabs a')].map(a=>a.textContent.replace(/\\s*\\d+$/,'').trim())")
    names = pg.evaluate("[...document.querySelectorAll('#lItem .card')].map((c=>{const b=c.querySelector('.cname b').textContent,sp=(c.querySelector('.cname span')||{}).textContent||'';return /[\\u4e00-\\u9fff]/.test(b)?sp.split('・')[0]:b}))")
    check(tabs == ["怪物", "裝備", "道具", "素材", "NPC"] and "Allium Flower" in names and "Sylvan Bow" not in names and "Boar Meat" not in names,
          f"codex tabs 怪物／裝備／道具／素材; 素材 holds materials, not equipment or food ({tabs})")
    # 素材 has a 怪物掉落物 group (user 2026-11-07)
    pg.click("#fItemGroup .chip[data-v='怪物掉落物']"); pg.wait_for_timeout(200)
    check(pg.locator("#lItem .card").count() > 20 and "Wolf Fangs" in pg.inner_text("#lItem") or "狼牙" in pg.inner_text("#lItem"), "素材: the 怪物掉落物 group lists monster drops")
    pg.click("#fItemGroup .chip[data-v='all']"); pg.wait_for_timeout(100)
    # 圖鑑・NPC: grouped by area, area filter, loot buyers list what they buy back (user 2026-11-07)
    pg.goto(base + "#npcs"); pg.wait_for_timeout(500)
    hs = pg.eval_on_selector_all("#lNpc .npcgh", "h=>h.map(x=>x.textContent)")
    opts = pg.eval_on_selector_all("#fNpcArea option", "o=>o.map(x=>x.value)")
    check(len(hs) >= 5 and pg.locator("#lNpc .card").count() > 50 and len(opts) >= 6, f"NPC tab: cards grouped by area with an area filter ({hs[:3]}, {len(opts)} options)")
    pg.select_option("#fNpcArea", opts[1]); pg.wait_for_timeout(200)
    check(pg.locator("#lNpc .npcgh").count() == 1, "picking an area leaves only that area")
    pg.select_option("#fNpcArea", "all"); pg.wait_for_timeout(100)
    pg.locator("#lNpc .card", has_text="Hanaka - Loot Buyer").first.click(); pg.wait_for_timeout(300)
    bt = pg.inner_text("#pBody")
    check("回收物品" in bt and "收購價 15 珂爾" in bt and "先祖之根" in bt, "a loot buyer's panel lists what it buys back with the price")
    pg.click("#pClose"); pg.wait_for_timeout(100)
    # game-only equipment (not in the official catalogue): the Elite Treant set comes from the owner's tooltips + recipe windows (user 2026-11-06)
    pg.goto(base + "#equip"); pg.wait_for_timeout(400); pg.click('#fEqPart .chip[data-v="all"]'); pg.wait_for_timeout(200)
    pg.fill("#q", "Elite"); pg.wait_for_timeout(400)
    el = pg.evaluate("[...document.querySelectorAll('#lEq .card')].map((c=>{const b=c.querySelector('.cname b').textContent,sp=(c.querySelector('.cname span')||{}).textContent||'';return /[\\u4e00-\\u9fff]/.test(b)?sp.split('・')[0]:b})).filter(t=>/^Elite /.test(t)).sort()")
    check(el == ["Elite Amulet", "Elite Bracelet", "Elite Carapace", "Elite Gloves"], f"equipment tab lists the 4 Elite Treant accessories ({el})")
    pg.evaluate("[...document.querySelectorAll('#lEq .card')].find(c=>(c=>{const b=c.querySelector('.cname b').textContent,sp=(c.querySelector('.cname span')||{}).textContent||'';return /[\\u4e00-\\u9fff]/.test(b)?sp.split('・')[0]:b})(c)==='Elite Gloves').click()"); pg.wait_for_timeout(300)
    pb = pg.inner_text("#pBody")
    check("+1%" in pb and "0.25" in pb and "Elite Treant Accessories" in pb and "查看配方" in pb and pg.locator("#pBody .phead .eslot img[src*='elite_gloves']").count() == 1,
          f"Elite Gloves panel: game stats, recipe with 查看配方, icon cut from the auction screenshot ({['+1%' in pb, '0.25' in pb, 'Elite Treant Accessories' in pb, '查看配方' in pb, pg.locator('#pBody .phead img').count()]})")
    pg.fill("#q", "Rhitta"); pg.wait_for_timeout(400)
    pg.evaluate("[...document.querySelectorAll('#lEq .card')].find(c=>(c=>{const b=c.querySelector('.cname b').textContent,sp=(c.querySelector('.cname span')||{}).textContent||'';return /[\\u4e00-\\u9fff]/.test(b)?sp.split('・')[0]:b})(c)==='Rhitta').click()"); pg.wait_for_timeout(300)
    pb = pg.inner_text("#pBody")
    check("戰士" in pb and "冷卻" in pb and "22" in pb, "game-only weapons keep their class restriction (Rhitta = 戰士) and translated stats")
    pg.fill("#q", ""); pg.wait_for_timeout(200); pg.click("#pClose"); pg.wait_for_timeout(150)
    pg.goto(base + "#props"); pg.wait_for_timeout(300)
    check(pg.locator('#fPrGroup .chip[data-v="材料"]').count() == 0 and pg.locator('#fPrGroup .chip[data-v="採集"]').count() == 0, "道具 no longer lists materials / gathered things")
    pg.goto(base + "#monsters"); pg.wait_for_timeout(400)
    pg.evaluate("[...document.querySelectorAll('#lMon .card')].find(c=>c.querySelector('b').textContent==='菁英樹人').click()"); pg.wait_for_timeout(300)
    pg.evaluate("[...document.querySelectorAll('#pBody [data-go=\"i|Sylvan Bow\"]')][0].click()"); pg.wait_for_timeout(300)
    pb = pg.inner_text("#pBody")
    check(pg.inner_text("#pBody h2") == "森林之弓" and "Sylvan Bow・Arc Sylvestre" in pg.inner_text("#pBody .phead .sub") and "取得方式" in pb and "Elite Treant" in pb, "a dropped weapon opens its equipment panel (official Chinese name, English and French below) with drop rate and map")
    check("遊戲寫的取得方式" in pb and "怪物掉落：Elite Treant（0.5%）" in pb, "equipment panel shows the in-game Obtainable lines with a Chinese gloss")
    pg.fill("#q", "Narax's Ring"); pg.wait_for_timeout(400)
    check(pg.locator("#lMon .card, #lEq .card, #lIt .card").count() >= 1 or "Ring of Narax" in pg.inner_text("body"), "old wiki item names still find the renamed item")
    pg.fill("#q", ""); pg.wait_for_timeout(200)
    pg.click("#pClose"); pg.wait_for_timeout(150)
    pg.goto(base + "#monsters"); pg.wait_for_timeout(400)
    pg.select_option("#fMonZone", "@dg"); pg.wait_for_timeout(200)
    dz = pg.evaluate("[...document.querySelectorAll('#lMon .card')].length")
    check(0 < dz < 67 and pg.locator('#fMonZone optgroup[label="地下城"] option').count() >= 4, f"monster area filter groups dungeons ({dz} monsters in dungeons)")
    pg.select_option("#fMonZone", "all"); pg.wait_for_timeout(200)
    c0 = pg.evaluate("getComputedStyle(document.getElementById('lMon')).gridTemplateColumns.split(' ').length")
    pg.locator("#lMon .card").first.click(); pg.wait_for_timeout(300)
    c1 = pg.evaluate("getComputedStyle(document.getElementById('lMon')).gridTemplateColumns.split(' ').length")
    pg.click("#pClose"); pg.wait_for_timeout(300)
    c2 = pg.evaluate("getComputedStyle(document.getElementById('lMon')).gridTemplateColumns.split(' ').length")
    check(c0 == c1 == c2, f"monster grid keeps its column count when the side panel opens and closes ({c0}/{c1}/{c2})")

    pg.goto(base + "#f1-map"); pg.wait_for_timeout(500)
    zl = pg.inner_text("#zlist")
    check("傳送點－城鎮 7" in zl and "傳送點－地標 6" in zl and pg.locator(".town.tp").count() == 13 and pg.locator(".town.land").count() == 4,
          "13 teleports (7 towns, 6 landmarks) share one marker style; landmarks (Vallhat, hidden well, Lac des Nénuphars, Valley of Petals) another")
    check(pg.locator(".areas path").count() >= 13 and pg.get_attribute(".areas path", "vector-effect") == "non-scaling-stroke",
          "monster areas are outlined with a zoom-independent line width")
    n = pg.locator(".zone.npc").count()
    pg.click('#fpCats .fchip[data-k="npc"]'); pg.wait_for_timeout(300)
    check(n >= 70 and pg.locator(".zone.npc").count() == 0 and "🧑 NPC" not in pg.inner_text("#zlist"),
          "NPCs on the map; the filter hides them on the map and in the list")
    pg.click('#fpCats .fchip[data-k="npc"]'); pg.wait_for_timeout(200)
    pg.click('#fpNpc .fchip[data-k="npc:loot"]'); pg.wait_for_timeout(300)
    check(pg.locator(".zone.npc").count() == n - 18, "NPC function filter: 收購商 hides the 18 buyers (16 loot + 2 weapon buyers) only")
    pg.click("#fpAll"); pg.wait_for_timeout(200)
    pg.click('#fpCats .fchip[data-k="area"]'); pg.click('#fpCats .fchip[data-k="mobs"]'); pg.wait_for_timeout(300)
    check(pg.locator('.zone[data-s="slimes"]').count() == 0 and pg.locator('.town.tp[data-s="wolf"]').count() == 1,
          "hiding monster areas keeps an area that is also a teleport (Wolf Valley)")
    check(pg.locator(".areas path").count() == 0, "hiding monster areas hides their outlines")
    pg.click("#fpAll"); pg.wait_for_timeout(200)
    for k in ("land", "area", "mobs", "gather", "dungeon", "wboss", "boss", "mini", "npc"):
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
    check("可以製作\n5" in t and "Bandit Coin" in t and "Stolen Cloak" in t and "小錢袋 ×24" in t, "Bandit Accessories lists its 5 recipes (4 from screenshots, 1 from the reference map)")
    pg.click("#pClose"); pg.wait_for_timeout(200)
    pg.locator("#zlist .npcrow", has_text="Shark Accessories").locator(".zn").click(); pg.wait_for_timeout(400)
    t = pg.inner_text("#pBody")
    check("Shark Fang" in t and "狼牙 ×8" in t and "33 珂爾" in t, "Shark Accessories lists its recipes with cost")
    off = pg.evaluate("""(()=>{const b=document.querySelector('.town.gather[data-s="farm"] .pin').getBoundingClientRect();
      const w=document.getElementById('world').getBoundingClientRect();const k=w.width/1000;
      const x=w.left+(2351-70)/4980*1000*k, y=w.top+(3662-70)/4980*1000*k;return Math.hypot(b.left+b.width/2-x,b.top+b.height/2-y)})()""")
    check(off < 2, f"gathering-spot pin is centred on its coordinate (off by {off:.1f}px)")
    tp = pg.evaluate("""(()=>{const e=[...document.querySelectorAll('.town.tp')].find(x=>x.textContent.trim()==='哈娜卡');const b=e.querySelector('.pin').getBoundingClientRect(),n=e.querySelector('.tname').getBoundingClientRect();
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
    check(pg.locator(".bsp").count() == 23 and pg.locator('.bsp[title*="Pumba"]').count() == 5 and pg.locator('.bsp[title^="澎巴"]').count() == 5, "23 boss spawn points drawn (Pumba has 5)")
    check(pg.is_visible("#fpanel") and pg.locator("#fpanel").bounding_box()["width"] <= 200, "filter panel stays open on the left and is narrow")
    pg.fill("#q", "Magic Mycelium"); pg.wait_for_timeout(300)
    check(pg.is_visible("#srchHint") and "Magic Mycelium" in pg.inner_text("#srchHint") and pg.locator(".zone.shide").count() > 0 and pg.locator(".town.shide").count() > 0
          and "只顯示符合" in pg.inner_text("#srchHint"), "searching on the map shows a hint and hides everything that does not match")
    pg.click("#srchClr"); pg.wait_for_timeout(300)
    check(pg.is_hidden("#srchHint") and pg.locator(".zone.dim").count() == 0 and pg.input_value("#q") == "", "清除搜尋 clears the search and the dimming")
    pg.eval_on_selector('.bsp[title*="Nazgul"]', 'e=>e.click()'); pg.wait_for_timeout(300)
    t = pg.inner_text("#pBody")
    check("8 遊戲截圖" in t and "Behind the Great Door" in t and "兩個階段" in t, "Cursed Nazgul Protector: LV 8 from a screenshot and its two phases")
    pg.click("#pClose"); pg.wait_for_timeout(150)
    check(pg.evaluate("document.querySelector('#fpCats .fchip[data-k=npc]').nextElementSibling.id") == "fpNpcWrap",
          "NPC sub-categories sit right under the NPC chip")
    fb, pb = pg.locator("#fpFly").bounding_box(), pg.locator("#fpanel").bounding_box()
    top4 = pg.eval_on_selector_all("#fpFly .fchip", "e=>e.slice(0,4).map(b=>b.dataset.k).join(',')")
    check(pg.is_visible("#fpFly") and fb["x"] >= pb["x"] + pb["width"] and pg.locator("#fpFly .fchip").count() == 10
          and top4 == "npc:potion,npc:loot,npc:key,npc:acc",
          f"desktop: NPC sub-categories shown on the right as soon as NPC is on, the 4 main ones first ({top4})")
    pg.click('#fpCats .fchip[data-k="npc"]'); pg.wait_for_timeout(200)
    check(pg.is_hidden("#fpFly"), "turning NPC off hides the sub-categories")
    pg.click('#fpCats .fchip[data-k="npc"]'); pg.wait_for_timeout(200)
    pg.wait_for_timeout(300)
    ov = pg.evaluate("""(()=>{const L=[...document.querySelectorAll('.town .tname,.zone.mobarea .zlabel')].filter(e=>e.offsetParent&&getComputedStyle(e).visibility!=='hidden').map(e=>[e.textContent.trim(),e.getBoundingClientRect(),!!e.closest('.town.tp')]);
      const P=[...document.querySelectorAll('.town .pin')].map(e=>e.getBoundingClientRect());const bad=[];
      for(const [n,r,tp] of L){if(tp)continue;for(const q of P){if(r.left<q.right-1&&r.right>q.left+1&&r.top<q.bottom-1&&r.bottom>q.top+1)bad.push(n)}}
      for(let i=0;i<L.length;i++)for(let j=i+1;j<L.length;j++){const a=L[i][1],b=L[j][1];if(a.left<b.right-1&&a.right>b.left+1&&a.top<b.bottom-1&&a.bottom>b.top+1)bad.push(L[i][0]+'/'+L[j][0])}return bad})()""")
    check(not ov, f"map names do not cover each other; only teleport names may sit over a pin ({ov[:4]})")
    names = pg.eval_on_selector_all(".zone.mobarea .zlabel", "e=>e.map(x=>x.textContent.trim())")
    check("腐臭沼澤" in names and "野豬區" in names and "Treants / Swamp" not in names, "monster areas use the official Chinese names (腐臭沼澤 Putrid Swamp, 野豬區 Boar Zone)")
    pg.locator("#zlist .zn", has_text="狼之谷").first.click(); pg.wait_for_timeout(400)
    check("Vallée des Loups" in pg.inner_text("#pBody .phead .sub"), "confirmed French in-game name shows in the place subtitle (Vallée des Loups)")
    pg.click("#pClose"); pg.wait_for_timeout(200)
    st = pg.evaluate("""(()=>{const d=document.querySelector('.town.dungeon[data-s="fallen"]');const z=document.querySelector('.zone.mobarea .zlabel');
      return [!!d&&!!d.querySelector('.pin'),z?getComputedStyle(z).backgroundColor:'none',[...document.querySelectorAll('.bsp')].every(b=>getComputedStyle(b).borderTopStyle==='solid')]})()""")
    check(st[0] and st[1] == "rgba(0, 0, 0, 0)" and st[2], "dungeons have a pin on the entrance, monster-area names have no box, boss rings are all solid")
    sz = pg.evaluate("""(()=>{const w=s=>{const e=document.querySelector(s);return e?e.getBoundingClientRect().width:0};return [w('.bsp.boss'),w('.bsp.mini'),w('.zone .mapth:not(.boss):not(.mini):not(.minion)')]})()""")
    check(sz[0] > sz[1] > sz[2] > 0, f"bosses drawn bigger than mini-bosses and monsters ({sz[0]:.0f} > {sz[1]:.0f} > {sz[2]:.0f}px)")
    labels = pg.eval_on_selector_all('#fpCats .fchip[data-k="boss"], #fpCats .fchip[data-k="mini"]', "e=>e.map(x=>x.textContent.replace(/\\d+/g,'').trim())")
    check(labels == ["👑 首領", "🎖️ 小首領"] and "區域首領" not in pg.inner_text("#fpanel"), f"map filters use the codex words 首領 / 小首領 ({labels})")
    nb, nm = pg.locator(".bsp.boss").count(), pg.locator(".bsp.mini").count()
    pg.click('#fpCats .fchip[data-k="boss"]'); pg.wait_for_timeout(200)
    check(pg.locator(".bsp.boss").count() == 0 and pg.locator(".bsp.mini").count() == nm > 0, f"首領 filter hides only boss spawns ({nb} bosses, {nm} mini-bosses)")
    pg.click('#fpCats .fchip[data-k="mini"]'); pg.wait_for_timeout(200)
    check(pg.locator(".bsp").count() == 0, "小首領 filter hides the mini-boss spawns")
    pg.click('#fpCats .fchip[data-k="boss"]'); pg.click('#fpCats .fchip[data-k="mini"]'); pg.wait_for_timeout(200)
    zl = pg.inner_text("#zlist")
    check("👑 首領" in zl and "🎖️ 小首領" in zl and "區域首領" not in zl, "side list splits 首領 and 小首領")
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

    pg.goto(base + "#feedback"); pg.wait_for_timeout(500)
    check(pg.locator('#collabBtn').inner_text().strip() == "協作區" and pg.locator('#collabBtn[aria-current="page"]').count() == 1
          and pg.is_visible("#rFeedW") and pg.is_hidden("#rData") and pg.locator('#rFeedW a[href*="template=5-bug.yml"]').count() == 1
          and pg.locator('#rFeedW a[href*="template=6-idea.yml"]').count() == 1, "協作區: #feedback opens 問題回報及建議 with the bug and idea buttons")
    pg.click('.csub a[data-sub="data"]'); pg.wait_for_timeout(300)
    check(pg.is_visible("#rData") and pg.is_hidden("#rFeedW") and "#report" in pg.url, "協作區: 攻略資料維護 shows the data form")
    # recipe panel <-> codex: 查看圖鑑 / 查看配方 open a pop-up in the middle (user 2026-11-05: 不要跳轉)
    pg.goto(base + "#recipes"); pg.wait_for_timeout(500)
    pg.fill("#q", ""); pg.click('#fRcCat .chip[data-v="all"]'); pg.wait_for_timeout(300)   # earlier steps left a category filter on
    pg.locator("#lRc .rcard", has_text="Belt of the Stags").first.click(); pg.wait_for_timeout(300)
    check("裝備資料" in pg.inner_text("#pBody") and "HP" in pg.inner_text("#pBody"), "the recipe panel shows the crafted item's data")
    pg.click('#pBody [data-goview^="equip"]'); pg.wait_for_timeout(500)
    hh, gt = pg.evaluate("location.hash"), pg.inner_text(".gvback:last-child .gvbody") if pg.locator(".gvback").count() else ""
    check(hh.endswith("recipes") and "Ceinture des Cerfs" in gt and "Belt of the Stags" in pg.inner_text("#pBody"),
          f"查看圖鑑 opens the item in a pop-up, tab and panel unchanged ({hh})")
    # the top menu decides: another menu (配方, 地圖＝NPC) opens another pop-up, one already open lower down closes the ones above
    pg.click('.gvback:last-child .gvbody [data-goview^="recipes"]'); pg.wait_for_timeout(400)
    gv = pg.evaluate("window.__gv()")
    check(gv["count"] == 2 and gv["depth"] == 1 and "Belt of the Stags" in pg.inner_text(".gvback:last-child .gvbody"), f"查看配方 in a codex pop-up opens a recipe pop-up on top ({gv})")
    pg.click('.gvback:last-child .gvbody [data-goview^="equip"]'); pg.wait_for_timeout(300)
    check(pg.evaluate("window.__gv()")["count"] == 1, "查看圖鑑 back to the item already open below does not stack")
    pg.click('.gvback:last-child .gvbody [data-go^="n|"]'); pg.wait_for_timeout(300)
    gv2 = pg.evaluate("window.__gv()")
    check(gv2["count"] == 2 and "Belt of the Stags" in pg.inner_text("#pBody"), f"an NPC link opens a second pop-up on top ({gv2})")
    first = pg.locator('.gvback:last-child .gvbody [data-go^="r|"]')
    if first.count():
        first.first.click(); pg.wait_for_timeout(300)
        check(pg.evaluate("window.__gv()")["count"] == 3, "a recipe link from an NPC pop-up opens a third pop-up (another menu)")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    check(pg.evaluate("window.__gv()")["count"] == 1, "Esc closes only the top pop-up")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    check(pg.locator(".gvback").count() == 0 and pg.is_visible("#panel"), "Esc closes the pop-ups, not the side panel")
    ic = pg.evaluate("['Critical Strike Chance','Skill Critical Strike Chance','Critical Strike Power','Fall Damage Reduction'].map(k=>window.__effIc(k))")
    check(ic[:3] == ["crit_chance", "skill_crit_chance", "crit_damage"] and ic[3] != "damage_reduction", f"stat icons: crit chance is not the crit damage icon ({ic})")
    # official news pictures of the monsters (mobphotos.js): every floor, bosses facing right, the note names the source
    ph = pg.evaluate("(()=>{const M=window.SAO_MOBPHOTO.by;return [M['1']['Bandit Archer'].f, Object.values(M).reduce((s,o)=>s+Object.values(o).reduce((t,e)=>t+e.rows.length,0),0), M['3']['Cave Goblin'].rows.length, JSON.stringify(M).includes('flip')]})()")
    check(ph[0] == "img/mobs/bandit-archer-palier-1.png" and ph[1] == 44 and ph[2] == 3 and not ph[3] and not pg.evaluate("'Orc Samurai Boss' in window.SAO_MOBPHOTO.by['3']"),
          f"mobphotos.js: 44 rows of the official table matched by name (Chef de la Tribu left out), nothing flipped ({ph})")
    pg.goto(base + "#f3-monsters"); pg.wait_for_timeout(600)
    fc = pg.evaluate("[...document.querySelectorAll('#lMon img.face')].map(i=>i.getAttribute('src')).filter(s=>s.startsWith('img/mobs/')&&s.includes('palier-3')).length")
    check(fc >= 30, f"floor 3 monster cards show the official pictures ({fc})")
    pg.goto(base + "#f1-monsters"); pg.wait_for_timeout(600)
    pg.click("#lMon [data-go='m|" + pg.evaluate("window.SAO.M.find(m=>m.name==='Kobold Warrior').id") + "']"); pg.wait_for_timeout(400)
    pt = pg.inner_text("#panel")
    check("官網公布的模樣和數值調整" in pt and "生命 220 → 250" in pt and "圖片和數值取自官網新聞" in pt and "Guerrier Kobold" in pt, "the monster panel shows the news' balance change and the picture source")
    pg.goto(base + "#f3-monsters"); pg.wait_for_timeout(600)
    pg.click("#lMon [data-go='m|" + pg.evaluate("window.SAO23.floors[3].M.find(m=>m.name==='Cave Goblin').id") + "']"); pg.wait_for_timeout(400)
    cg = [pg.locator("#panel .mphr img").count(), pg.inner_text("#panel").count("Gobelin de la Caverne")]
    pg.click("#lMon [data-go='m|" + pg.evaluate("window.SAO23.floors[3].M.find(m=>m.name==='Jeune pousse').id") + "']"); pg.wait_for_timeout(400)
    jp = pg.inner_text("#panel")
    check(cg[0] == 3 and cg[1] >= 3 and "生命 1000 → 800" in jp and "官網沒有附圖" in jp and pg.locator("#lMon [data-go]").filter(has_text="Nerius the Evil Treant").count() == 1,
          f"the three Gobelin de la Caverne rows are Cave Goblin's variants; Jeune pousse and Nerius are on floor 3 ({cg})")
    ic2 = pg.evaluate("['Heal Bonus','HEAL BONUS','HEAL_BONUS','Magic Damage','Skill Damage'].map(k=>window.__effIc(k))")
    check(ic2 == ["healing", "healing", "healing", "magic_damage", "skill_damage"], f"stat icons: every spelling of Heal Bonus gets the healing icon ({ic2})")
    # calibration mode is for the owner only (?edit)
    pg.goto(base + "#map"); pg.wait_for_timeout(500)
    check(pg.is_hidden("#editToggle") and pg.is_hidden(".mapfoot"), "players do not see the calibration button")
    pg.goto(base + "?edit#map"); pg.wait_for_timeout(800)
    check(pg.is_visible("#editToggle"), "?edit shows the calibration button")
    pg.goto(base + "#report"); pg.wait_for_timeout(400)
    codes = pg.eval_on_selector_all(".rform code, #jmPack code", "e=>e.map(x=>x.textContent)")
    check(r"%APPDATA%\.Triggers Client\instances\Sword Art Online\screenshots" in codes
          and r"%APPDATA%\.Triggers Client\instances\Sword Art Online\journeymap\data" in codes,
          "report tab shows the F2 screenshot and JourneyMap folder paths with their backslashes")

    pg.goto(base + "#f2-report"); pg.wait_for_timeout(400)
    href = pg.get_attribute("#formGo", "href") or ""
    check("docs.google.com/forms" in href and href.endswith("=2"), "report tab links to the Google Form with floor 2")
    b.close()
srv.shutdown()
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
