"""修復分流地圖 v15 (src/index.html, jmFixE / jmFixPick / jmFixRecord): the gates of plan r3 that run on made-up folders.

Usage (repo root, after src/build.py): python3 tests/jm_fix_v15_test.py   (prints ALL PASSED, exits 1 on failure)
Folders cut from the site's floor-3 map, as in tests/jm_fix_test.py (0,0 1,-1 0,2 1,2 shown by the site's map; 0,3 and
1,3 not shown; 5,5 reached by no map). Everything is picked through the page's own folder input and its buttons.
- A (r3 §2): A-1 two folders with the same unconfirmed image and no confirmed copy anywhere: neither is in E, both listed,
  nothing written there. M2 / A-3: TG drew at 1,3 (topo) and 0,3 (night) exactly what the donors confirm there, each
  missing the other square (the stuck state of the real S6 run): it takes the missing images and the next run is done;
  T5 (nothing there) gets each pixel from the newest confirmed copy (DN2 over DN), never TG's (E is no source). A-2 TX drew
  the confirmed piece at 1,3 joined to a bit of its own colour: the 0,3 it would take is cut and listed, its own colour is
  in no image after every run
- B (r3 §3): records (ids, at most 5, never overwritten), the fingerprint, every view and button: not placed yet, one
  pack missing (①, ②), part of a pack, content changed (newer and older than the record), all placed (then the next run),
  another copy with the same names and contents (backup) and with other contents, too few files for a fingerprint, no
  record, storage full; the three results (complete, done with squares left out, packs missing)
"""
import functools, http.server, io, os, re, shutil, sys, tempfile, threading, time, zipfile
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(c, msg):
    print(("ok   " if c else "FAIL ") + msg, flush=True)
    if not c:
        fails.append(msg)


def fl_canvas(f, full, x0, z0):
    c = Image.new("RGB", (full, full))
    d = os.path.join(ROOT, "tiles", f"f{f}jm", "3")
    for n in os.listdir(d):
        a, b = map(int, n[:-4].split("_"))
        c.paste(Image.open(os.path.join(d, n)), (a * 256, b * 256))

    def cut(rx, rz, box=None):
        im = c.crop((rx * 512 - x0, rz * 512 - z0, rx * 512 - x0 + 512, rz * 512 - z0 + 512)).convert("RGBA")
        if box:
            keep = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            keep.paste(im.crop(box), box[:2])
            im = keep
        return im
    return cut


cut = fl_canvas(3, 1792, -253, -79)
tex = cut(0, 0)


def piece(*boxes, fill=None):
    im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    for bx in boxes:
        im.paste(tex.crop(bx) if fill is None else Image.new("RGBA", (bx[2] - bx[0], bx[3] - bx[1]), fill), bx[:2])
    return im


T = 1_790_000_000
D = "overworld/%s/%s.png"
SITE = ((0, 0), (1, -1), (0, 2), (1, 2))
DN, DN2, TG, TX, T5, NA, NB = ("Triggers_v15a0001~dn", "Triggers_v15a0002~dn2", "Triggers_v15a0003~tg", "Triggers_v15a0004~tx",
                               "Triggers_v15a0005~t5", "Triggers_v15a0006~na", "Triggers_v15a0007~nb")
FS = [DN, DN2, TG, TX, T5, NA, NB]
MT = {DN: T + 50, DN2: T + 60, TG: T + 90, TX: T, T5: T, NA: T, NB: T}
P03, P13 = (100, 0, 512, 151), (0, 50, 301, 151)   # touches 0,2; on through 0,3 into 1,3 (one piece over two squares)
DN2C = (210, 40, 160, 255)
RED = (230, 20, 20, 255)


def dn2(box):   # DN2's copy of the same piece: another colour, so the newest copy is seen in every pixel
    return piece(box, fill=DN2C)


def put(root, folder, rel, im, t):
    p = os.path.join(root, folder, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if isinstance(im, bytes):
        open(p, "wb").write(im)
    else:
        im.save(p)
    os.utime(p, (t, t))


def build(root):
    for f in FS:
        for sq in SITE:
            put(root, f, D % ("day", "%d,%d" % sq), cut(*sq), MT[f])
    for f, mk in ((DN, lambda b: piece(b)), (DN2, dn2)):
        for L in ("day", "night", "topo"):
            if L != "day":
                put(root, f, D % (L, "0,2"), cut(0, 2), MT[f])
            put(root, f, D % (L, "0,3"), mk(P03), MT[f])
            put(root, f, D % (L, "1,3"), mk(P13), MT[f])
    for L in ("night", "topo"):
        put(root, TG, D % (L, "0,2"), cut(0, 2), MT[TG])
    put(root, TG, D % ("topo", "1,3"), piece(P13), MT[TG])    # = DN's topo 1,3; its topo 0,3 is missing
    put(root, TG, D % ("night", "0,3"), piece(P03), MT[TG])   # = DN's night 0,3; its night 1,3 is missing
    put(root, TX, D % ("day", "1,3"), Image.alpha_composite(piece(P13), piece((301, 50, 340, 151), fill=RED)), MT[TX])   # DN's piece + its own bit
    for f in (NA, NB):
        put(root, f, D % ("day", "5,5"), piece((0, 0, 120, 120)), MT[f])   # the same unconfirmed image, confirmed nowhere


def img(b):
    return Image.open(io.BytesIO(b)).convert("RGBA")


class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


tmp = tempfile.mkdtemp()
try:
    mp = os.path.join(tmp, "mp")
    build(mp)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900}, accept_downloads=True)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html#report")
        pg.wait_for_timeout(600)
        pg.evaluate("localStorage.removeItem('jmFixJobs')")
        WAIT = "window.__jmFix||(window.__jmFixCheck&&window.__jmFixCheck.view&&window.__jmFixCheck.view!=='done')"

        def pick(path):   # the player picks the folder: a result, or a question from the check (B)
            pg.evaluate("window.__jmFix=null;window.__jmFixCheck=null")
            pg.set_input_files("#jmFixDir", path)
            pg.wait_for_function(WAIT, timeout=180000)
            return pg.evaluate("window.__jmFix?['run',window.__jmFix]:['check',window.__jmFixCheck]")

        def press(k):   # one of the check's buttons
            pg.evaluate("window.__jmFix=null")
            v0 = pg.evaluate("window.__jmFixCheck&&window.__jmFixCheck.view")
            pg.click(f"#jmFixOut [data-jmc='{k}']")
            pg.wait_for_function(f"window.__jmFix||(window.__jmFixCheck&&window.__jmFixCheck.view&&window.__jmFixCheck.view!=='done'&&window.__jmFixCheck.view!=={v0!r})", timeout=180000)
            return pg.evaluate("window.__jmFix?['run',window.__jmFix]:['check',window.__jmFixCheck]")

        def jobs():
            return pg.evaluate("JSON.parse(localStorage.getItem('jmFixJobs')||'[]')")

        def download():   # every zip of the result: {zip name: {file: bytes}}
            got = {}
            for i in range(pg.locator("#jmFixDl [data-jmfix]").count()):
                with pg.expect_download(timeout=120000) as dl:
                    pg.click(f"#jmFixDl [data-jmfix='{i}']")
                zi = zipfile.ZipFile(dl.value.path())
                got[dl.value.suggested_filename] = {k: zi.read(k) for k in zi.namelist()}
            return got

        def apply(root, files, t=None):   # put in as the player does (the file gets the time it is written)
            for k, v in files.items():
                q = os.path.join(root, *k.split("/"))
                os.makedirs(os.path.dirname(q), exist_ok=True)
                open(q, "wb").write(v)
                if t:
                    os.utime(q, (t, t))

        def note():
            return pg.inner_text("#jmFixNote")

        def out():
            return pg.inner_text("#jmFixOut")

        # ---------- A ----------
        k, r = pick(mp)
        check(k == "run" and sorted({s["floor"]: s for s in r["floors"]}.get(3, {}).get("folders", [])) == sorted(FS) and all(sorted(r["shown"][f]) == ["0,0", "0,2", "1,-1", "1,2"] for f in FS),
              f"fixture: seven floor-3 folders, the four site squares shown, nothing else ({k})")
        f3 = {s["floor"]: s for s in r["floors"]}[3]
        z1 = download()
        files1 = {n: v for zz in z1.values() for n, v in zz.items()}
        E = r.get("E", {})
        # A-1
        check("day/5,5" not in E.get(NA, []) and "day/5,5" not in E.get(NB, []) and {NA + " 5,5", NB + " 5,5"} <= set(f3["unshown"]) and not any("5,5" in n for n in r["names"]),
              f"A-1: two folders with the same unconfirmed image and no confirmed copy are not in E, both listed, nothing written there ({E.get(NA)}, {E.get(NB)})")
        # M2 / A-3: the stuck state
        check(sorted(E.get(TG, [])) == ["night/0,3", "topo/1,3"] and not any(x.startswith(TG) for x in f3["unshown"]),
              f"M2: TG's own topo 1,3 and night 0,3 are all the same as the donors' confirmed copies (E) and not listed: {E.get(TG)} {[x for x in f3['unshown'] if x.startswith(TG)]}")
        newest = {b: Image.alpha_composite(piece(b), dn2(b)) for b in (P03, P13)}   # DN2 is newer than DN: it wins where both drew
        tg03, tg13 = files1.get(TG + "/" + D % ("topo", "0,3")), files1.get(TG + "/" + D % ("night", "1,3"))
        check(tg03 is not None and tg13 is not None and img(tg03).tobytes() == newest[P03].tobytes() and img(tg13).tobytes() == newest[P13].tobytes(),
              "M2: TG takes the topo 0,3 and night 1,3 it was missing, each pixel from the newest confirmed copy")
        check(not any(x.startswith(TG) for x in f3["cut"]), f"M2: nothing of TG is cut by the next-run check (its pixels in E do not count): {f3['cut']}")
        t5 = {n: img(v) for n, v in files1.items() if n.startswith(T5)}
        want5 = {T5 + "/" + D % (L, sq): newest[bx] for L in ("day", "night", "topo") for sq, bx in (("0,3", P03), ("1,3", P13))}
        want5.update({T5 + "/" + D % (L, "0,2"): cut(0, 2) for L in ("night", "topo")})
        check(sorted(t5) == sorted(want5) and all(t5[n].tobytes() == want5[n].tobytes() for n in want5),
              f"A-3: a folder with nothing there gets every pixel from the newest confirmed copy, none from TG's E (TG is the newest file): {sorted(set(t5) ^ set(want5))[:3]}")
        # A-2
        check(TX + "/" + D % ("day", "0,3") not in files1 and TX + " day/0,3" in f3["cut"] and TX + " 1,3" in f3["unshown"] and "day/1,3" in E.get(TX, []),
              f"A-2: TX's confirmed-looking piece joined to its own bit: the 0,3 that would confirm it next run is cut and listed, the square stays listed: {f3['cut']}")
        red = lambda ims: [n for n, im in ims.items() if RED in {c for _, c in im.getcolors(1 << 24)}]
        check(not red({n: img(v) for n, v in files1.items()}), "A-2: TX's own colour is in no image")
        check(re.fullmatch(r"jm_fix_\d{8}_\d{4}_[a-z2-9]{4}_1of1\.zip", list(z1)[0]) is not None and r["zips"] == list(z1) and len(jobs()) == 1 and jobs()[0]["id"] == r["job"],
              f"B: the zip is named by the run's id and one record is kept: {list(z1)} {[j['id'] for j in jobs()]}")
        # ---------- B on this record: nothing placed yet ----------
        backup = os.path.join(tmp, "backup", "mp")
        shutil.copytree(mp, backup)   # the player's backup: same names, same contents
        k, c = pick(mp)
        check(k == "check" and c["fp"] == "same" and c["view"] == "notyet" and [x["state"] for x in c["packs"]] == ["not"] and "網站分不出來" in out(),
              f"B: before anything is put in, the site does not decide which copy this is and asks: {c}")
        k, c = press("notyet")
        check(k == "check" and c["view"] == "notyet_how" and list(z1)[0] in out() and pg.locator("#jmFixDl [data-jmfix]").count() == 0, "B: 「我還沒放」 says which zip to put in and writes nothing")
        # ---------- part of the pack ----------
        names1 = sorted(files1)
        half = {n: files1[n] for n in names1[: len(names1) // 2]}
        apply(mp, half)
        k, c = pick(mp)
        check(k == "check" and c["view"] == "missing" and c["packs"][0]["state"] == "part" and c["packs"][0]["placed"] == len(half) and "只放了一部分" in out(),
              f"M2-3: half the pack put in is seen as part of it: {c['packs']}")
        k, c = press("have")
        check(k == "check" and c["view"] == "have" and list(z1)[0] in out() and "不會產生新的檔案" in out() and pg.locator("#jmFixDl [data-jmfix]").count() == 0 and len(jobs()) == 1,
              "B ①: 「我還有那一包」 says which zip to put in again and writes nothing, no new record")
        apply(mp, files1)
        # ---------- all placed: the next run follows, done ----------
        k, r2 = pick(mp)
        check(k == "run" and r2["how"].get("done") == 1 and r2["names"] == [] and "上次的 1 包都已放好" in note(),
              f"B: everything placed: says so and works the folder out again, nothing more to write (M2 converges in 2 runs): {r2['names'][:3]} {note()}")
        f32 = {s["floor"]: s for s in r2["floors"]}[3]
        check(r2.get("result") == "done_left" and re.search(r"修復完成，有 \d+ 格地圖本來就不補", note()) is not None and not any(x.startswith(TG) for x in f32["unshown"]) and TX + " 1,3" in f32["unshown"],
              f"S4: the result is 「修復完成，有 N 格本來就不補」; TG is no longer listed, TX still is: {note()}")
        check(TX + " day/0,3" in f32["cut"] and not any(n.startswith(TX) for n in r2["names"]), "A-2: on the next run TX's 0,3 is still cut")
        # ---------- B-1 (a): the backup (same names, same contents as before the repair) ----------
        k, c = pick(backup)
        check(k == "check" and c["fp"] == "same" and c["view"] == "notyet" and c["job"] == r["job"],
              f"B-1 (a): a backup with the same names and contents is not taken for the repaired copy; the player is asked: {c['view']}")
        k, rb = press("new")
        jb = jobs()
        check(k == "run" and rb.get("job") and rb["job"] != r["job"] and [j["id"] for j in jb] == [r["job"], rb["job"]] and sorted(rb["names"]) == names1,
              f"B-1 (a): 「另一份 mp」 repairs it under a new id; the first record is kept: {[j['id'] for j in jb]}")
        zb = download()
        # the repaired copy again: the newest record (the backup's) has the same fingerprint, and its files are what mp has: placed
        k, r3 = pick(mp)
        check(k == "run" and r3["how"].get("done") == 1 and r3["names"] == [], f"B-1 (a): the repaired copy is seen as having all of the newest record placed ({k})")
        # ---------- B-1 (b): same names, other contents ----------
        other = os.path.join(tmp, "other", "mp")
        shutil.copytree(backup, other)
        for f in FS:   # the game drew on: every file changes a little
            for L, sq in (("day", "0,0"), ("day", "1,-1"), ("day", "0,2"), ("day", "1,2")):
                im = cut(*[int(v) for v in sq.split(",")])
                im.putpixel((5, 5), (1, 2, 3, 255))
                put(other, f, D % (L, sq), im, T + 1000)
        k, c = pick(other)
        check(k == "check" and c["fp"] == "diff" and c["view"] == "diff" and "內容和上次修復" in out(), f"B-1 (b): same names, other contents: the player is asked ({c['fp']})")
        k, c = press("inspect")
        check(k == "check" and c["view"] == "notyet", f"B-1 (b): 「這是上次那份，檢查各包」 shows the packs: {c['view']}")
        k, ro = press("new")
        check(k == "run" and ro.get("job") not in (r["job"], rb["job"]) and len(jobs()) == 3, "B-1 (b): 「另一份 mp」 repairs it under a new id; the two records before are kept")
        download()
        # ---------- several packs, one missing (M2-1), ② to regenerate (B-3) ----------
        mp2 = os.path.join(tmp, "mp2")   # the same names again: a fresh browser, so no record picks it
        build(mp2)
        pg.evaluate("localStorage.removeItem('jmFixJobs')")
        pg.evaluate("window.__JMFIX.PART=300000")
        k, r4 = pick(mp2)
        z4 = download()
        zn = r4["zips"]
        check(k == "run" and len(zn) >= 3 and list(z4) == zn and all(re.fullmatch(r"jm_fix_\d{8}_\d{4}_[a-z2-9]{4}_%dof%d\.zip" % (i + 1, len(zn)), n) for i, n in enumerate(zn)),
              f"M2-1: several packs, named i of n: {zn}")
        miss = zn[1]
        for n in zn:
            if n != miss:
                apply(mp2, z4[n])
        k, c = pick(mp2)
        st = [x["state"] for x in c["packs"]]
        check(k == "check" and c["view"] == "missing" and st == ["placed", "not"] + ["placed"] * (len(zn) - 2) and f"第 2／{len(zn)} 包" in out() and "沒有放進去" in out(),
              f"M2-1: the missing pack is named: {st}")
        miss_txt = out() + note()
        check(all(pg.locator(f"#jmFixOut [data-jmc='{x}']").count() == 1 for x in ("have", "regen", "restore", "new")), "B: the four choices are on the page")
        k, c = press("restore")
        check(k == "check" and c["view"] == "restore" and "mp_修復後" in out(), "B ③: how to put the backup back")
        k, c = pick(mp2)
        k, r5 = press("regen")   # B-3: that zip is gone
        z5 = download()
        f5 = {n: v for zz in z5.values() for n, v in zz.items()}
        check(k == "run" and r5["job"] not in [r4["job"]] and sorted(f5) == sorted(z4[miss]) and all(f5[n] == z4[miss][n] for n in f5),
              f"B-3: 「重新產生缺少的部分」 writes exactly what the lost zip held, under a new id: {len(f5)} vs {len(z4[miss])}")
        apply(mp2, f5)
        k, r6 = pick(mp2)
        check(k == "run" and r6["how"].get("done") == 1 and r6["names"] == [], "B-3: after that the folder is done; the player was never stuck")
        pg.evaluate("window.__JMFIX.PART=40*1048576")
        # ---------- M2-7: content changed after the record, newer and older ----------
        for t_, tag in ((time.time() + 5, "newer"), (T - 100000, "older")):
            mp3 = os.path.join(tmp, "mp3_" + tag)
            build(mp3)
            pg.evaluate("localStorage.removeItem('jmFixJobs')")
            k, r7 = pick(mp3)
            z7 = download()
            f7 = {n: v for zz in z7.values() for n, v in zz.items()}
            apply(mp3, f7)
            n0 = sorted(f7)[0]
            im = img(f7[n0])
            im.putpixel((0, 511), (9, 9, 9, 255))
            q = os.path.join(mp3, *n0.split("/"))
            im.save(q)
            os.utime(q, (t_, t_))
            k, c = pick(mp3)
            check(k == "check" and c["view"] == "changed" and c["packs"][0]["changed"] == 1 and c["packs"][0]["state"] == "part" and "原因未確認" in out()
                  and (("在修復後被改過" in out()) == (tag == "newer")) and pg.locator("#jmFixOut [data-jmc='have']").count() == 0,
                  f"M2-7 ({tag}): a file changed after it was put in is 「內容已變更，原因未確認」, never placed; the time only adds the hint: {c['packs']}")
            check(pg.locator("#jmFixOut [data-jmc='regen']").count() == 1 and pg.locator("#jmFixOut [data-jmc='restore']").count() == 1, f"M2-7 ({tag}): ② and ③ are offered")
        # ---------- M2-8: the three results ----------
        mp4 = os.path.join(tmp, "mp4")
        for f in (DN, DN2):
            for sq in SITE:
                put(mp4, f, D % ("day", "%d,%d" % sq), cut(*sq), MT[f])
        k, r8 = pick(mp4)
        check(k == "run" and r8["result"] == "complete" and "已經完整" in note() and "修復完成" not in note(), f"M2-8: nothing to do: 「已經完整」: {note()}")
        check(r2.get("result") == "done_left" and r8.get("result") == "complete" and "沒有完整放好" in miss_txt and "修復完成" not in miss_txt and "已經完整" not in miss_txt,
              "M2-8: three different results: complete, done with squares left out, packs missing (never 「修復完成」 then)")
        # ---------- M2-9: no record ----------
        pg.evaluate("localStorage.removeItem('jmFixJobs')")
        k, r9 = pick(mp2)
        check(k == "run" and r9["how"].get("nojob") == "none" and "沒有這份 mp 的修復紀錄" in note() and r9["names"] == [], f"M2-9: without a record it says so and still finds the folder done: {note()}")
        # ---------- B-2: storage full ----------
        mp5 = os.path.join(tmp, "mp5")
        build(mp5)
        pg.evaluate("()=>{window.__si=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw new DOMException('full','QuotaExceededError')};return 1}")
        k, r10 = pick(mp5)
        check(k == "run" and r10["names"] and r10["saved"] is False and "這次沒有留下紀錄，無法事後檢查" in note() and pg.locator("#jmFixDl [data-jmfix]").count() >= 1,
              f"B-2: when the record cannot be written the zips are still made and it says so: {note()[-40:]}")
        pg.evaluate("()=>{Storage.prototype.setItem=window.__si;return 1}")
        # ---------- records: at most 5, the oldest goes, a clash draws again ----------
        pg.evaluate("localStorage.removeItem('jmFixJobs')")
        ids = pg.evaluate("""()=>{const B=window.__JMFIXB,o=[];for(let i=0;i<6;i++){const id=B.newId(B.read());o.push(id);B.save({id,at:i,names:['x'],fp:[],parts:[]})}return o}""")
        jj = jobs()
        check([j["id"] for j in jj] == ids[1:] and len(set(ids)) == 6 and len(jj) == 5, f"B: the sixth record drops only the oldest one: {len(jj)}")
        clash = pg.evaluate("""()=>{const B=window.__JMFIXB,g=crypto.getRandomValues.bind(crypto);let n=0;
          crypto.getRandomValues=a=>{a.fill(n++<2?0:1);return a};const a=B.newId([]);n=0;const b=B.newId([{id:a}]);crypto.getRandomValues=g;return[a,b]}""")
        check(clash[0].endswith("_aaaa") and clash[1].endswith("_bbbb"), f"B: an id that is already kept is drawn again: {clash}")
        # ---------- too few files for a fingerprint ----------
        mp6 = os.path.join(tmp, "mp6")
        for f, sqs in ((DN, SITE[:2]), (T5, SITE[:1])):   # T5 lacks 1,-1
            for sq in sqs:
                put(mp6, f, D % ("day", "%d,%d" % sq), cut(*sq), MT[f])
        pg.evaluate("localStorage.removeItem('jmFixJobs')")
        k, r11 = pick(mp6)
        download()
        k, c = pick(mp6)
        check(r11["names"] and len(jobs()[0]["fp"]) < 32 and k == "check" and c["fp"] == "few" and c["view"] == "diff" and "檔案太少" in out(),
              f"B: with fewer than 32 files to fingerprint the copy is never taken as the same: {len(jobs()[0]['fp'])} {c.get('fp')}")
        check(not errs, f"no page errors: {errs[:3]}")
        b.close()
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("ALL PASSED" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
