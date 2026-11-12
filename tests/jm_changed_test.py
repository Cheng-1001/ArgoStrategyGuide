"""更新打包 also offers squares that are already on the site but whose file is newer and clearly different
(2026-11-12, user: a corrected area must not need 全地圖打包), and the merge lets them replace explored chunks; an older
copy is neither offered nor merged over the site.

Usage: python3 tests/jm_changed_test.py   (prints ALL PASSED, exits 1 on failure)
"""
import functools, http.server, json, os, shutil, subprocess, sys, tempfile, threading, time, zipfile
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c:
        fails.append(msg)


tmp = tempfile.mkdtemp()
BASE = os.path.join(tmp, "base")
shutil.copytree(ROOT, BASE, ignore=lambda d, names: [n for n in names if n in (".git", "inbox") or n.startswith("f1jm_c") or (os.path.abspath(d) == os.path.join(ROOT, "tiles") and n == "dg")])
jm_path = os.path.join(BASE, "jmmeta.js")
jm_txt = open(jm_path, encoding="utf-8").read()
jm_i = jm_txt.index("window.SAO_JM = ") + len("window.SAO_JM = ")
META = json.loads(jm_txt[jm_i:jm_txt.rindex(";")])
META["1"].pop("layers", None); META.pop("dg", None)


def write_meta(rt):
    m = json.loads(json.dumps(META))
    m["1"]["rt"] = rt
    open(jm_path, "w", encoding="utf-8").write(jm_txt[:jm_i] + json.dumps(m, ensure_ascii=False, indent=1) + ";\n")


def canvas(root):
    cv = Image.new("RGB", (5120, 5120))
    d = os.path.join(root, "tiles", "f1jm", "3")
    for n in os.listdir(d):
        c, r = map(int, n[:-4].split("_"))
        cv.paste(Image.open(os.path.join(d, n)), (c * 256, r * 256))
    return cv


try:
    cv = canvas(ROOT)
    mask = Image.open(os.path.join(ROOT, "tiles", "f1jm", "explored.png")).convert("L")
    def explored(rx, rz):
        return sum(1 for cz in range(rz * 32, rz * 32 + 32) for cx in range(rx * 32, rx * 32 + 32) if 0 <= cx < 320 and 0 <= cz < 320 and mask.getpixel((cx, cz)))
    full = sorted(((explored(rx, rz), rx, rz) for rz in range(10) for rx in range(10)), reverse=True)
    regs = [(rx, rz) for e, rx, rz in full[:4]]        # well explored squares: the world is recognised as floor 1
    chg = regs[1]

    def region(rx, rz):
        return cv.crop((rx * 512 - 70, rz * 512 - 70, rx * 512 + 442, rz * 512 + 442)).convert("RGBA")

    def changed():
        im = region(*chg)
        im.paste((20, 20, 60, 255), (100, 100, 300, 300))         # a redrawn area: dark, unlike the terrain under it
        return im

    def make_mp(t_chg):
        mp = os.path.join(tmp, f"mp{int(t_chg)}")
        d = os.path.join(mp, "Triggers_f1~a", "overworld", "day")
        os.makedirs(d, exist_ok=True)
        for rx, rz in regs:
            p = os.path.join(d, f"{rx},{rz}.png")
            (changed() if (rx, rz) == chg else region(rx, rz)).save(p)
            os.utime(p, (t_chg - 86400, t_chg - 86400) if (rx, rz) != chg else (t_chg, t_chg))
        return mp

    now = time.time()
    rec = int((now - 3600) * 1000)                       # the site's copy of the square: one hour ago

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=BASE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/index.html"

    def pack(mp, pick):
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 1280, "height": 900}, accept_downloads=True)
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.add_init_script("window.__COLLAB_OPEN=1")
            pg.goto(base + "#report"); pg.wait_for_timeout(600)
            pg.set_input_files("#jmDir", mp)
            pg.click("#jmOut [data-jmmode='new']")
            pg.wait_for_function("window.__jm", timeout=60000)
            squares = pg.eval_on_selector_all("[data-jmreg]", "e=>e.map(x=>[x.dataset.jmreg,x.getAttribute('class')])")
            zp = None
            if pick and os.environ.get("SHOT_DIR"):
                pg.locator("#jmPack").screenshot(path=os.path.join(os.environ["SHOT_DIR"], "jm_chg.png"))
            if pick:
                k = "%d,%d" % chg
                pg.locator(f"[data-jmreg='{k}']").first.evaluate("e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
                pg.wait_for_timeout(200)
                btn = pg.locator("[data-jmpart]").first
                btn.evaluate("e=>e.scrollIntoView({block:'center'})")
                with pg.expect_download() as dl:
                    btn.click()
                zp = os.path.join(tmp, f"up{len(os.listdir(tmp))}.zip"); dl.value.save_as(zp)
            b.close()
            return squares, zp, errs

    # 1. unchanged files: no square offered
    write_meta({})
    mp0 = os.path.join(tmp, "mp_same"); d0 = os.path.join(mp0, "Triggers_f1~a", "overworld", "day"); os.makedirs(d0)
    for rx, rz in regs:
        region(rx, rz).save(os.path.join(d0, f"{rx},{rz}.png"))
    sq, _, errs = pack(mp0, False)
    check(sq == [] and not errs, f"files the same as the site: no square is offered ({sq}, {errs[:1]})")

    # 2. newer and different: offered as a changed (blue) square; merged, it replaces the explored chunks
    write_meta({"%d,%d" % chg: rec})
    sq, zp, errs = pack(make_mp(now), True)
    k = "%d,%d" % chg
    check([x for x in sq if x[0] == k] and "chg" in dict(sq)[k] and len(sq) == 1 and not errs, f"the newer, different square is offered, marked as changed ({sq})")
    man = json.loads(zipfile.ZipFile(zp).read("sao_pack.json"))
    tkey = f"mp{int(now)}/Triggers_f1~a/overworld/day/{k}.png"
    check(abs(man.get("times", {}).get(tkey, 0) / 1000 - now) < 5, f"the zip carries the file's UTC time ({list(man.get('times', {}).items())[:2]})")
    r = subprocess.run([sys.executable, "-I", os.path.join(BASE, "tools", "jm_merge.py"), zp, "--report", "T990"], capture_output=True, text=True)
    res = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"stderr": r.stderr[-300:]}
    px = canvas(BASE).getpixel((chg[0] * 512 - 70 + 200, chg[1] * 512 - 70 + 200))
    rt_after = json.loads(open(jm_path, encoding="utf-8").read()[jm_i:].rstrip().rstrip(";"))["1"].get("rt", {}).get(k)
    check(r.returncode == 0 and max(abs(px[0] - 20), abs(px[1] - 20), abs(px[2] - 60)) < 25 and rt_after and rt_after > rec,
          f"merged: the explored chunks now show the newer file, and the square's time is recorded ({r.returncode} {px} {rt_after} {res.get('reason', '')[:60]})")

    # 3. older than the site's copy: not offered; a zip claiming the older time does not overwrite
    write_meta({k: int((now + 3600) * 1000)})
    sq, _, errs = pack(make_mp(now), False)
    check(sq == [] and not errs, f"an older file is not offered even if it differs ({sq})")
    z_old = os.path.join(tmp, "old.zip")
    src = os.path.join(make_mp(now - 10), "Triggers_f1~a", "overworld", "day")
    with zipfile.ZipFile(z_old, "w") as z:
        for f in os.listdir(src):
            if f == f"{k}.png":       # the older copy has the old terrain (what the site showed before the newer upload)
                q = os.path.join(tmp, "oldregion.png"); region(*chg).save(q); z.write(q, f"mp/Triggers_f1~a/overworld/day/{f}")
            else:
                z.write(os.path.join(src, f), f"mp/Triggers_f1~a/overworld/day/{f}")
        z.writestr("sao_pack.json", json.dumps({"v": 1, "worlds": {"mp/Triggers_f1~a/overworld": {"siblings": ["overworld"]}},
                                               "times": {f"mp/Triggers_f1~a/overworld/day/{f}": int((now - 10) * 1000) for f in os.listdir(src)}}))
    before = canvas(BASE).getpixel((chg[0] * 512 - 70 + 200, chg[1] * 512 - 70 + 200))
    r = subprocess.run([sys.executable, "-I", os.path.join(BASE, "tools", "jm_merge.py"), z_old, "--report", "T991"], capture_output=True, text=True)
    res = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"stderr": r.stderr[-300:]}
    after = canvas(BASE).getpixel((chg[0] * 512 - 70 + 200, chg[1] * 512 - 70 + 200))
    check(r.returncode == 0 and after == before and any("比網站上這一格舊" in w for w in res.get("skippedWhy", [])),
          f"a zip with an older copy does not overwrite the square ({r.returncode} {before}->{after} {res.get('skippedWhy')})")
    srv.shutdown()
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
