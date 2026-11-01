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

    pg = b.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(base + "#f1-map"); pg.wait_for_timeout(500)
    check(pg.eval_on_selector_all("#fpCats .fchip", "e=>e.filter(b=>!b.dataset.k.includes(':')&&b.getAttribute('aria-pressed')==='true').map(b=>b.dataset.k).join(',')") == "tp,land,area,mobs"
          and pg.locator(".bsp").count() == 0 and pg.locator(".town.dungeon").count() == 0, "default map filter: teleports, landmarks, monster areas, regular monsters")
    pg.click('#fpCats .fchip[data-k="npc"]'); pg.wait_for_timeout(200)
    on = pg.eval_on_selector_all("#fpFly .fchip", "e=>e.filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.dataset.k).join(',')")
    check(on == "npc:alchemist,npc:lootBuyers,npc:keyBlacksmith,npc:accessoriesBlacksmith", f"default NPC sub-categories: the 4 chosen ones ({on})")
    pg.evaluate("localStorage.setItem('sao-map-filter-v3','{}')")   # the rest of the tests start with everything on
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
          and pg.eval_on_selector_all("nav.tabs a", "e=>e.map(a=>a.dataset.v).join(',')") == "map,codex,quests,recipes,classes,bosses,report",
          "recipes is its own top tab between quests and world bosses")
    pg.click("#legalBtn"); pg.wait_for_timeout(250)
    t = pg.inner_text("#pBody")
    check("非官方" in t and "Triggers SAO" in t and "GitHub Issues" in t and "中文玩家社群協力製作" in t, "copyright / non-affiliation notice opens from the floor bar")
    pg.click("#pClose"); pg.wait_for_timeout(150)
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
    pg.goto(base + "#items"); pg.wait_for_timeout(300); pg.fill("#q", "Magic Mycelium"); pg.wait_for_timeout(300)
    pg.locator("#lItem .card").first.click(); pg.wait_for_timeout(300)
    labels = pg.eval_on_selector_all("#pBody .qmap svg text", "e=>e.map(x=>x.textContent)")
    check(labels and set(labels) == {"1"}, f"one source with several spawn points (Guardian Colossal) is numbered 1 at every point ({labels})")
    pg.fill("#q", ""); pg.click("#pClose"); pg.wait_for_timeout(150)
    pg.goto(base + "#monsters"); pg.wait_for_timeout(400)
    pg.fill("#q", "Albal"); pg.wait_for_timeout(250)
    pg.locator("#lMon .card", has_text="Albal").first.click(); pg.wait_for_timeout(300)
    pg.locator("#pBody [data-rep]").first.click(); pg.wait_for_timeout(500)
    check(pg.is_visible("#rwin") and "#monsters" in pg.url and pg.locator("#rwSvg g").count() == 3 and pg.locator("#rwSvg polyline").count() == 0,
          "codex: a spawn coordinate opens the floating map window (all 3 Albal spawns), the codex stays")
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
    pg.fill("#q", "Skeleton Warrior"); pg.wait_for_timeout(300)
    check("Bone and Dust" in pg.inner_text("#view-quests"), "quest search finds kill targets in the steps")
    pg.fill("#q", ""); pg.click('#fQKind .chip[data-v="main"]'); pg.wait_for_timeout(200)
    pg.goto(base + "#recipes"); pg.wait_for_timeout(400)
    pg.locator("#lRc .rcard", has_text="Quality Health Potion II").first.click(); pg.wait_for_timeout(300)
    pg.locator("#pBody [data-go^='n|']").first.click(); pg.wait_for_timeout(300)
    pg.locator("#pBody [data-rep]").first.click(); pg.wait_for_timeout(500)
    check(pg.is_visible("#rwin") and "#recipes" in pg.url and pg.locator("#rwSvg g").count() == 1 and "Alchemist" in pg.inner_text("#rwTitle"),
          "recipe -> Alchemist -> 在地圖上查看 opens the floating map window with one point, the recipes tab stays")
    pg.click("#rwX"); pg.click("#pClose"); pg.wait_for_timeout(150)
    pg.goto(base + "#classes"); pg.wait_for_timeout(400)
    check(pg.locator("#lCls .card").count() == 6 and pg.is_hidden("#codexTabs"), "classes tab lists the 6 classes")
    pg.locator("#lCls .card", has_text="Guerrier").click(); pg.wait_for_timeout(300)
    t = pg.inner_text("#pBody")
    check("Combinaison Brutale" in t and "Paladin" in t and "起始屬性" in t and "Physical Might" in t and "佔位圖" not in t,
          "Guerrier panel: skills, specialisations, base stats and talents")
    check(pg.locator("#pBody img").count() == 0, "no class or skill pictures")
    cols = pg.evaluate("getComputedStyle(document.getElementById('lCls')).gridTemplateColumns.split(' ').length")
    pw = pg.locator("#panel").bounding_box()["width"]
    two = pg.evaluate("getComputedStyle(document.querySelector('#pBody .cls2')).gridTemplateColumns.split(' ').length")
    check(cols == 3 and pw > 700 and two == 2, f"classes: 3 columns ({cols}), wide panel ({pw:.0f}px) split in two ({two})")
    pg.click("#pBody [data-eqcls]"); pg.wait_for_timeout(300)
    n = pg.locator("#cwBody .card").count()
    check(pg.is_visible("#cwin") and n > 50 and "#equip" not in pg.url, f"equipment window opens over the classes tab ({n} items)")
    pg.locator("#cwBody .card").first.click(); pg.wait_for_timeout(300)
    check("官方圖鑑 #" in pg.inner_text("#cwBody") and "Guerrier" in pg.inner_text("#pCrumb"), "item detail opens inside the window; the class panel stays")
    pg.click("#cwBack"); pg.wait_for_timeout(200)
    check(pg.locator("#cwBody .card").count() == n, "back to the equipment list")
    pg.click("#cwX"); pg.wait_for_timeout(150)
    pg.click("#pClose"); pg.wait_for_timeout(150)
    pg.locator("#lCls .card", has_text="Martial Artist").click(); pg.wait_for_timeout(300)
    check("可能還沒開放" in pg.inner_text("#pBody") and "佔位圖" in pg.inner_text("#pBody"), "Martial Artist flagged as possibly unreleased, skills unconfirmed")
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
    pg.fill("#q", "Magic Mycelium"); pg.wait_for_timeout(300)
    check(pg.is_visible("#srchHint") and "Magic Mycelium" in pg.inner_text("#srchHint") and pg.locator(".zone.dim").count() > 0, "searching on the map shows a hint (things not matching are dimmed)")
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
    check(pg.is_visible("#fpFly") and fb["x"] >= pb["x"] + pb["width"] and pg.locator("#fpFly .fchip").count() >= 10
          and top4 == "npc:alchemist,npc:lootBuyers,npc:keyBlacksmith,npc:accessoriesBlacksmith",
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

    pg.goto(base + "#feedback"); pg.wait_for_timeout(500)
    check(pg.locator('nav.tabs a[data-v="report"]').inner_text().strip() == "協作區" and pg.locator('nav.tabs a[data-v="report"][aria-current="page"]').count() == 1
          and pg.is_visible("#rFeedW") and pg.is_hidden("#rData") and pg.locator('#rFeedW a[href*="template=5-bug.yml"]').count() == 1
          and pg.locator('#rFeedW a[href*="template=6-idea.yml"]').count() == 1, "協作區: #feedback opens 問題回報及建議 with the bug and idea buttons")
    pg.click('.csub a[data-sub="data"]'); pg.wait_for_timeout(300)
    check(pg.is_visible("#rData") and pg.is_hidden("#rFeedW") and "#report" in pg.url, "協作區: 攻略資料維護 shows the data form")
    pg.goto(base + "#report"); pg.wait_for_timeout(400)
    codes = pg.eval_on_selector_all(".rform code", "e=>e.map(x=>x.textContent)")
    check(r"%APPDATA%\.Triggers Client\instances\Sword Art Online\screenshots" in codes
          and r"%APPDATA%\.Triggers Client\instances\Sword Art Online\journeymap\data\mp" in codes,
          "report tab shows the F2 screenshot and JourneyMap folder paths with their backslashes")

    pg.goto(base + "#f2-report"); pg.wait_for_timeout(400)
    href = pg.get_attribute("#formGo", "href") or ""
    check("docs.google.com/forms" in href and href.endswith("=2"), "report tab links to the Google Form with floor 2")
    b.close()
srv.shutdown()
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
