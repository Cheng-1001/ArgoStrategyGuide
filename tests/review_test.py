"""Local test for the review web app UI (google/review.html) with a fake google.script.run.

Usage: python3 tests/review_test.py [screenshot-dir]
Checks: priority order (monsters and items before places, oldest first), type/floor filters and counts,
approve moves to the next card and the item into "done", reject asks for a reason, screenshot loads,
coordinates mark the floor map, no horizontal scroll at 390px. Exits 1 on failure.
"""
import base64, json, os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else None
html = open(os.path.join(ROOT, "google", "review.html"), encoding="utf-8").read()
img = "data:image/jpeg;base64," + base64.b64encode(open(os.path.join(ROOT, "reports", "R0001.jpg"), "rb").read()).decode()

def it(row, id_, t, fl, name, fields, status="待審核", result="", time="2026/11/01 10:%02d" ):
    return {"row": row, "id": id_, "time": time % row, "type": t, "floor": str(fl), "name": name, "fields": fields,
            "shots": ["f" + id_, "g" + id_] if row % 2 else ["f" + id_], "status": status, "note": "", "result": result}
ITEMS = [
    it(2, "R0001", "怪物", 1, "Young Spider", [["怪物・等級", "3"]], "核准", "已上線 2026-11-01 00:25"),
    it(3, "R0002", "地點", 1, "Hidden Well", [["地點・種類", "其他"], ["地點・座標 x, z", "4309, 3697"]]),
    it(4, "R0003", "怪物", 1, "Albal", [["怪物・等級", "8"], ["怪物・座標 x, z", "2513, 3722"]]),
    it(5, "R0004", "物品", 2, "Wolf Fangs", [["物品・怎麼拿到的", "怪物掉落"], ["物品・來源", "White Dire Wolf"]]),
    it(6, "R0005", "地點", 2, "Urbus Shop", [["地點・種類", "NPC"], ["地點・座標 x, z", "10, -20"]]),
    it(7, "R0006", "怪物", 2, "Bull", [["怪物・等級", "12"]]),
]
MOCK = """<script>
window.__calls=[];window.__items=%s;
window.google={script:{get run(){var ok=function(){},no=function(){};var o={
 withSuccessHandler:function(f){ok=f;return o},withFailureHandler:function(f){no=f;return o},
 apiList:function(){__calls.push(["apiList"]);setTimeout(function(){ok({me:"reviewer@gmail.com",items:JSON.parse(JSON.stringify(__items))})},30)},
 apiShot:function(id){__calls.push(["apiShot",id]);setTimeout(function(){ok(%s)},30)},
 apiDecide:function(row,id,d,note){__calls.push(["apiDecide",row,id,d,note]);var x=__items.find(function(i){return i.id===id});x.status=d;
   setTimeout(function(){ok({ok:true,note:"審核：reviewer"+(note?"｜"+note:""),msg:id+(d==="核准"?" 已核准，約 1 分鐘內自動上線":" 已退回")})},30)}};return o}}};
</script>""" % (json.dumps(ITEMS, ensure_ascii=False), json.dumps(img))
page_html = "<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'></head><body>" + MOCK + html + "</body></html>"

fails = []
def check(c, m):
    print(("ok   " if c else "FAIL ") + m)
    if not c: fails.append(m)

with sync_playwright() as p:
    b = p.chromium.launch()
    for w, h, tag in [(1280, 900, "desk"), (390, 844, "phone")]:
        pg = b.new_page(viewport={"width": w, "height": h})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.route("https://cheng-1001.github.io/**", lambda r: r.fulfill(path=os.path.join(ROOT, r.request.url.rsplit("/", 1)[1])))
        pg.set_content(page_html); pg.wait_for_timeout(400)
        order = pg.eval_on_selector_all(".qi .nm", "e=>e.map(x=>x.textContent)")
        if tag == "desk":
            check(order == ["Albal", "Wolf Fangs", "Bull", "Hidden Well", "Urbus Shop"], f"pending queue: monsters/items first, oldest first ({order})")
            check("待審核 5" in pg.inner_text("#fView") and "已處理 1" in pg.inner_text("#fView"), "view chips show pending/done counts")
            check("怪物 2" in pg.inner_text("#fType") and "地點 2" in pg.inner_text("#fType"), "type chips show counts")
            pg.wait_for_timeout(200)
            check(pg.locator("#shot img").count() == 1, "screenshot loads into the card")
            check(pg.locator(".map i").count() == 1, "coordinates are marked on the floor map")
            if OUT: pg.screenshot(path=os.path.join(OUT, "review_desk.png"))
            pg.click('#fType .chip[data-v="地點"]'); pg.wait_for_timeout(100)
            check(pg.eval_on_selector_all(".qi .nm", "e=>e.map(x=>x.textContent)") == ["Hidden Well", "Urbus Shop"], "type filter: places only")
            pg.click('#fType .chip[data-v="all"]'); pg.select_option("#fFloor", "2"); pg.wait_for_timeout(100)
            check(pg.eval_on_selector_all(".qi .nm", "e=>e.map(x=>x.textContent)") == ["Wolf Fangs", "Bull", "Urbus Shop"], "floor filter: floor 2 only")
            pg.select_option("#fFloor", "all"); pg.wait_for_timeout(100)
            pg.fill("#note", "截圖清楚"); pg.click("#bOk"); pg.wait_for_timeout(300)
            calls = pg.evaluate("__calls.filter(c=>c[0]==='apiDecide')")
            check(calls == [["apiDecide", 4, "R0003", "核准", "截圖清楚"]], f"approve sends row, id, decision, note ({calls})")
            check(pg.inner_text(".card h2") == "Wolf Fangs", "after approving, the next card opens")
            check("待審核 4" in pg.inner_text("#fView") and "已處理 2" in pg.inner_text("#fView"), "counts update after approving")
            pg.on("dialog", lambda d: d.dismiss())
            pg.click("#bNo"); pg.wait_for_timeout(200)
            check(len(pg.evaluate("__calls.filter(c=>c[0]==='apiDecide')")) == 1, "reject without a reason asks first (cancel keeps it pending)")
            pg.keyboard.press("j"); pg.wait_for_timeout(100)
            check(pg.inner_text(".card h2") == "Bull", "J goes to the next report")
            pg.click('#fView .chip[data-v="done"]'); pg.wait_for_timeout(200)
            check(pg.locator(".result").count() == 1 and pg.locator("#bOk").count() == 0, "done view shows the result and no buttons")
            if OUT: pg.screenshot(path=os.path.join(OUT, "review_done.png"))
        else:
            check(not pg.evaluate("document.documentElement.scrollWidth>innerWidth"), "no horizontal scroll at 390px")
            if OUT: pg.screenshot(path=os.path.join(OUT, "review_phone.png"), full_page=True)
        check(not errs, f"no page errors ({tag})" + ("" if not errs else ": " + errs[0]))
        pg.close()
    b.close()
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
