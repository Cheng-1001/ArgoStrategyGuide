"""The site's 「修復分流地圖」 tool (src/index.html, jmFixRun) end to end, on a fake JourneyMap "mp" folder.

Usage (repo root, after src/build.py): python3 tests/jm_fix_test.py   (prints ALL PASSED, exits 1 on failure)
Three floor-3 server instances cut from the site's floor-3 explored map, each holding a different part of it (two have ids
the site has never seen), plus folders the tool must refuse: a lone floor-1 world (nothing to do), noise, a folder whose id
the site ties to floor 2 but whose map is floor 3, a floor-3 folder with one floor-2 image in it, and one that matches both.
Checks (GPT reviews of v1 a7e9942, v2 806b5b5, v3 7a5718e, v4 09e2526 and v5 8f91a7c; local reviews of v6 057ca56 and v7 db18f97 and GPT's review of v8 e368162):
- a folder's copy of a square is used or changed only when its surface image of that square is shown to be that floor:
  by the site's map, or (a small piece) by lying inside a copy the site's map shows, the same picture in many colours; a
  surface image too small to check, a night image without a surface image and small pieces that differ from the shown copy,
  drew outside it, match only another unshown piece (A -> B -> C), are another floor's map, are 1/4 another floor or are one
  flat colour are neither used nor changed. Which copies are shown is written out here from the fixture, not read back
- a folder's own drawn pixels never change; only its clear pixels are filled (where shown copies disagree the newest wins
  and the count is shown); every image equals a PIL reference built from the shown squares the page reports
- square 0,-1, waypoints and an image with an unreadable or wrong-size shown copy are never in the zip
- the result never says "complete" while something was left out; it does when nothing was
- the zip splits by size counting zip headers; above the total limit nothing is produced; running again finds nothing to do
"""
import functools, http.server, io, os, shutil, sys, tempfile, threading, zipfile
from PIL import Image, ImageOps
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c:
        fails.append(msg)


def fl_canvas(f, full, x0, z0):
    """the site's explored map of floor f (frames as FLOOR_CFG in tools/jm_merge.py): cut(rx, rz) and explored-chunk count"""
    c = Image.new("RGB", (full, full))
    d = os.path.join(ROOT, "tiles", f"f{f}jm", "3")
    for n in os.listdir(d):
        a, b = map(int, n[:-4].split("_"))
        c.paste(Image.open(os.path.join(d, n)), (a * 256, b * 256))
    m = Image.open(os.path.join(ROOT, "tiles", f"f{f}jm", "explored.png")).convert("L")
    mx0, mz0 = x0 // 16, z0 // 16

    def expl(rx, rz):
        return sum(1 for cz in range(rz * 32, rz * 32 + 32) for cx in range(rx * 32, rx * 32 + 32)
                   if 0 <= cx - mx0 < m.width and 0 <= cz - mz0 < m.height and m.getpixel((cx - mx0, cz - mz0)))

    def cut(rx, rz, box=None):
        im = c.crop((rx * 512 - x0, rz * 512 - z0, rx * 512 - x0 + 512, rz * 512 - z0 + 512)).convert("RGBA")
        if box:   # keep only this part, the rest clear (not drawn yet)
            keep = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            keep.paste(im.crop(box), box[:2])
            im = keep
        return im
    return cut, expl


tmp = tempfile.mkdtemp()
try:
    cut, expl = fl_canvas(3, 1792, -253, -79)
    cut2, expl2 = fl_canvas(2, 2304, -1062, -1062)
    regs = [tuple(r) for _, *r in sorted(((expl(rx, rz), rx, rz) for rx in range(-1, 3) for rz in range(-1, 4) if (rx, rz) != (0, -1)), reverse=True)[:4]]
    R1, R2, R3, R4 = regs
    # a floor-2 square the site's floor-3 map does not reach (and not 0,-1, which the tool never reads)
    reg2 = max(((expl2(rx, rz), rx, rz) for rx in range(-3, 2) for rz in range(-3, 2) if (rx, rz) != (0, -1) and not expl(rx, rz)))[1:]
    FAR = (5, 5)   # a square no site map reaches
    mp = os.path.join(tmp, "mp")
    A, B, C = ("Triggers_95a78a58~76fa~4903~92aa~8a87c523440c", "Triggers_fix00001~b", "Triggers_fix00002~c")
    WRONG, MIXED, MIXED2 = "Triggers_ba411067~7be9~4787~a9dc~da5c74995cb4", "Triggers_fix00003~mixed", "Triggers_fix00004~both"   # ba411067 = floor 2 in SAO_JM.ids

    def put(folder, rel, im, t, root=None):
        p = os.path.join(root or mp, folder, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if isinstance(im, bytes):
            open(p, "wb").write(im)
        else:
            im.save(p)
        os.utime(p, (t, t))

    T = 1_790_000_000
    D = "overworld/day/%d,%d.png"
    put(A, D % R1, cut(*R1), T)
    put(A, D % R2, cut(*R2, (0, 0, 512, 256)), T)
    put(A, D % R4, cut(*R4), T)
    put(A, "overworld/night/%d,%d.png" % R1, cut(*R1, (0, 0, 256, 512)), T)
    put(A, "overworld/topo/%d,%d.png" % R2, cut(*R2), T)
    put(A, "overworld/day/0,-1.png", cut(0, -1, (0, 0, 512, 200)), T)
    put(B, D % R1, cut(*R1, (256, 0, 512, 512)), T + 100)
    put(B, D % R2, cut(*R2, (0, 200, 512, 512)), T + 100)
    put(B, D % R3, cut(*R3), T + 100)
    put(B, D % R4, cut(*R4, (100, 100, 164, 164)), T + 100)                            # 64 x 64: too small for the site check, same as A's
    # v5 (GPT review of v4 09e2526, V4-M1): NIGHT's R4 is shown only by a small piece (the same as B's) and it also has a
    # big night image there (floor 2's map, never checked): that whole square of NIGHT gives nothing and takes nothing.
    # B (the same small piece, no other layer) still takes A's surface and night images
    NIGHT = "Triggers_fix00010~night"
    put(NIGHT, D % R4, cut(*R4, (100, 100, 164, 164)), T)
    put(NIGHT, "overworld/night/%d,%d.png" % R4, cut2(*reg2, (0, 0, 512, 256)), T + 800)
    put(A, "overworld/night/%d,%d.png" % R4, cut(*R4, (0, 256, 512, 512)), T)
    put(B, "overworld/night/%d,%d.png" % R1, b"not a png", T + 100)                   # unreadable copy of a shown square
    put(B, "overworld/night/%d,%d.png" % FAR, cut2(*reg2), T + 100)                    # a floor-2 night image without any surface image
    put(B, "overworld/day/0,-1.png", Image.new("RGBA", (512, 512), (20, 160, 40, 255)), T + 100)   # the login world
    r3c = cut(*R3, (0, 0, 300, 300))
    r3c.paste(ImageOps.invert(r3c.crop((40, 40, 100, 100)).convert("RGB")).convert("RGBA"), (40, 40))   # C drew this bit differently
    put(C, D % R3, r3c, T + 200)
    put(C, D % R1, cut(*R1), T + 200)                                                    # already whole
    put(C, "overworld/4/%d,%d.png" % R3, cut(*R3, (100, 100, 200, 200)), T + 200)        # a cave layer only C has
    put(C, "overworld/topo/%d,%d.png" % R1, Image.new("RGBA", (256, 256), (9, 9, 9, 255)), T + 200)   # wrong size, shown square
    r4c = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    r4c.paste(ImageOps.invert(cut(*R4).convert("RGB").crop((300, 300, 364, 364))).convert("RGBA"), (300, 300))
    put(C, D % R4, r4c, T + 200)                                                         # 64 x 64 piece unlike A's: not shown
    n = Image.effect_noise((512, 512), 90)
    put(C, D % FAR, Image.merge("RGB", (n, n, n)).convert("RGBA"), T + 200)            # a surface image no map can check
    # v4 (GPT review of v3 7a5718e, V3-M1): small pieces at square R5, where A's only copy is its top half (shown by the
    # site's map). Each piece is too small for the site check, so only the "inside a site-shown copy" rule can show it
    R5 = sorted(((expl(rx, rz), rx, rz) for rx in range(-1, 3) for rz in range(-1, 4) if (rx, rz) != (0, -1)), reverse=True)[4][1:]
    CHB, CHC, XF, MX = "Triggers_fix00005~chainb", "Triggers_fix00006~chainc", "Triggers_fix00007~xfloor", "Triggers_fix00008~mixpiece"
    full5, f2 = cut(*R5), cut2(*reg2)
    def drawn(im, box):   # no unexplored (black) pixel in the box
        b = im.crop(box).convert("RGB").tobytes()
        return all(b[i:i + 3] != bytes(3) for i in range(0, len(b), 3))
    cx = next(x for x in range(0, 448, 8) if drawn(full5, (x, 192, x + 64, 340)))
    put(A, D % R5, cut(*R5, (0, 0, 512, 256)), T)
    put(CHB, D % R5, cut(*R5, (cx, 192, cx + 64, 280)), T + 300)   # 64 rows inside A's half, 24 rows below it (not in A)
    put(CHC, D % R5, cut(*R5, (cx, 256, cx + 64, 340)), T + 400)   # same as CHB where both drew (1,536 px), nothing in common with A
    xb = next((x, y) for y in range(0, 192, 8) for x in range(0, 448, 8) if drawn(full5, (x, y, x + 64, y + 64)))
    fb = next((x, y) for y in range(0, 448, 8) for x in range(0, 448, 8) if drawn(f2, (x, y, x + 64, y + 64)))
    other = f2.crop((fb[0], fb[1], fb[0] + 64, fb[1] + 64))                     # 64 x 64 of floor 2's map
    xf = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    xf.paste(other, xb)
    put(XF, D % R5, xf, T + 500)                                    # floor-2 content inside A's half: not the same picture
    mx = cut(*R5, (xb[0], xb[1], xb[0] + 64, xb[1] + 64))
    mx.paste(other.crop((48, 0, 64, 64)), (xb[0] + 48, xb[1]))
    put(MX, D % R5, mx, T + 600)                                    # 3/4 the same as A, 1/4 floor 2: not enough
    # a flat colour proves nothing: A's copy of R6 has one 64 x 64 block of a single colour, FLAT has only that block
    R6 = sorted(((expl(rx, rz), rx, rz) for rx in range(-1, 3) for rz in range(-1, 4) if (rx, rz) != (0, -1)), reverse=True)[5][1:]
    FLAT = "Triggers_fix00009~flat"
    a6 = cut(*R6)
    a6.paste((40, 90, 160, 255), (200, 200, 264, 264))
    put(A, D % R6, a6, T)
    blk = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    blk.paste((40, 90, 160, 255), (200, 200, 264, 264))
    put(FLAT, D % R6, blk, T + 700)                                 # 4,096 pixels, all the same as A's, one colour
    # v6: a small piece whose other layers there are each inside the same layer of the site-shown copy (A) and the same
    # picture is not left alone (OKN); one whose night image drew outside A's night (OUTN), differs from it (DIFN) or whose
    # layer A does not have there (TOPO) still is. A's night at R4 is its bottom half, so these pieces sit in that half
    full4 = cut(*R4)
    nx = next(x for x in range(0, 448, 8) if drawn(full4, (x, 280, x + 64, 364)))
    OKN, OUTN, DIFN, TOPO = "Triggers_fix00011~nightok", "Triggers_fix00012~nightout", "Triggers_fix00013~nightdiff", "Triggers_fix00014~topo"
    pc = (nx, 300, nx + 64, 364)
    an4 = cut(*R4, (0, 256, 512, 512))
    def piece(im, box):
        o = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        o.paste(im.crop(box), box[:2])
        return o
    # v7 (local review of v6 057ca56): EDGE's night drew 4 rows above A's night (6%, so below the 10% the same-picture rule
    # allows: only "every pixel inside A's" refuses it, M1); OKN's night has 4 rows in another colour inside A's night (still
    # 94% the same), so its own pixels must be kept (M3) and must not be given out while it is only a small piece (S2)
    EDGE = "Triggers_fix00015~nightedge"
    MAG = (255, 0, 255, 255)
    eb = (nx, 252, nx + 64, 256)                     # the rows outside A's night
    ob = (nx, 300, nx + 64, 304)                     # OKN's rows of another colour
    for i, f in enumerate((OKN, OUTN, DIFN, TOPO, EDGE)):
        put(f, D % R4, cut(*R4, pc), T + 900 + i)
    okn = piece(an4, pc)
    okn.paste(MAG, ob)
    put(OKN, "overworld/night/%d,%d.png" % R4, okn, T + 900)
    edn = piece(full4, (nx, 252, nx + 64, 316))
    edn.paste(MAG, eb)
    put(EDGE, "overworld/night/%d,%d.png" % R4, edn, T + 904)
    # v8 (local review of v7 db18f97, N1): NEAR's night is inside A's but 8 of its 64 rows are another colour (87.5% the
    # same): below the 90% the rule asks for, so it is left alone; a lower bar (0.85, 0.5) would let it in
    NEAR = "Triggers_fix00017~nightnear"
    CYAN = (0, 255, 255, 255)
    put(NEAR, D % R4, cut(*R4, pc), T + 905)
    nrn = piece(an4, pc)
    nrn.paste(CYAN, (nx, 310, nx + 64, 318))
    put(NEAR, "overworld/night/%d,%d.png" % R4, nrn, T + 905)
    # v9 (GPT review of v8 e368162, V8-M1): the 90% bar to the pixel. LO's and HI's night are inside A's; of the n pixels they
    # drew (4,096) LO has one same pixel fewer than 90% (3,686, 89.99%), HI exactly enough (3,687, 90.01%). LO is left alone
    # and its pixels go nowhere in either round; HI is not left alone and keeps its own pixels. Any other bar (0.88, 0.93)
    # flips one of them
    LO, HI = "Triggers_fix00018~bound899", "Triggers_fix00019~bound900"
    YEL, ORA = (255, 255, 0, 255), (255, 128, 0, 255)
    apc = an4.crop(pc)
    bn = sum(1 for p in apc.getdata() if p[3])
    need = -(-bn * 9 // 10)                                      # the fewest same pixels that pass: ceil(0.9 n)
    bpos = [(nx + i % 64, 300 + i // 64) for i, p in enumerate(apc.getdata()) if p[3]]
    def bound(col, same):
        im = piece(an4, pc)
        for xy in bpos[:bn - same]:
            im.putpixel(xy, col)
        return im
    lon, hin = bound(YEL, need - 1), bound(ORA, need)
    for f, im, t in ((LO, lon, T + 906), (HI, hin, T + 907)):
        put(f, D % R4, cut(*R4, pc), t)
        put(f, "overworld/night/%d,%d.png" % R4, im, t)
    put(OUTN, "overworld/night/%d,%d.png" % R4, piece(full4, (nx, 232, nx + 64, 364)), T + 901)   # 24 rows above A's night
    dn = piece(an4, pc)
    dn.paste(ImageOps.invert(dn.crop(pc).convert("RGB")).convert("RGBA"), pc[:2])
    put(DIFN, "overworld/night/%d,%d.png" % R4, dn, T + 902)                                   # same place, other picture
    put(TOPO, "overworld/topo/%d,%d.png" % R4, piece(full4, pc), T + 903)                      # A has no topo image at R4
    for f in (CHB, CHC, XF, MX, FLAT, NIGHT, OKN, OUTN, DIFN, TOPO, EDGE, NEAR, LO, HI):
        put(f, D % R1, cut(*R1), T)                                 # a big floor-3 image, so the folder is floor 3
    os.makedirs(os.path.join(mp, B, "waypoints"), exist_ok=True)
    open(os.path.join(mp, B, "waypoints", "WaypointData.dat"), "wb").write(b"x")
    # refused folders
    cut1, _ = fl_canvas(1, 5120, 70, 70)
    put("Triggers_815bd3d6~f22f~4114~a601~dfcf0a106221", "overworld/day/4,4.png", cut1(4, 4), T)
    put("Triggers_noise~d", D % R1, Image.merge("RGB", (n, n, n)).convert("RGBA"), T)
    put(WRONG, D % R1, cut(*R1), T)
    put(WRONG, D % R3, cut(*R3), T)
    for R in regs:                       # mostly floor 3 (the folder as a whole matches only floor 3) ...
        put(MIXED, D % R, cut(*R), T)
    put(MIXED, D % reg2, cut2(*reg2, (0, 0, 192, 192)), T)   # ... but one image is floor 2 (a small part, about 140 chunks)
    put(MIXED2, D % R1, cut(*R1), T)     # half and half: matches both floors
    put(MIXED2, D % reg2, cut2(*reg2), T)

    SAFE = (A, B, C, CHB, CHC, XF, MX, FLAT, NIGHT, OKN, OUTN, DIFN, TOPO, EDGE, NEAR, LO, HI)
    MT = {A: T, B: T + 100, C: T + 200, CHB: T, CHC: T, XF: T, MX: T, FLAT: T, NIGHT: T, OKN: T + 900, OUTN: T + 901, DIFN: T + 902, TOPO: T + 903, EDGE: T + 904, NEAR: T + 905, LO: T + 906, HI: T + 907}
    c = lambda R: "%d,%d" % R
    # which copies must be shown, written out from the fixture (not taken from the page): by the site's map, or as a piece
    # inside a site-shown copy. The reference images below are built from this, not from what the page reports
    SITE = {A: [R1, R2, R4, R5, R6], B: [R1, R2, R3], C: [R1, R3], CHB: [R1], CHC: [R1], XF: [R1], MX: [R1], FLAT: [R1], NIGHT: [R1], OKN: [R1], OUTN: [R1], DIFN: [R1], TOPO: [R1], EDGE: [R1], NEAR: [R1], LO: [R1], HI: [R1]}
    SITE = {f: sorted(map(c, v)) for f, v in SITE.items()}
    SIM = {f: [c(R4)] if f in (B, NIGHT, OKN, OUTN, DIFN, TOPO, EDGE, NEAR, LO, HI) else [] for f in SAFE}
    HOLD = {f: [c(R4)] for f in (NIGHT, OUTN, DIFN, TOPO, EDGE, NEAR, LO)}   # shown by a small piece, another layer there not checked: left alone
    EXP = {f: sorted(SITE[f] + SIM[f]) for f in SAFE}

    def load(folder, rel):
        p = os.path.join(mp, folder, *rel.split("/"))
        if not os.path.exists(p):
            return None
        try:
            im = Image.open(p)
            im.load()
            return im.convert("RGBA") if im.size == (512, 512) else "bad"
        except Exception:
            return "bad"

    def files_of(f):
        out = set()
        for dp, _, fn in os.walk(os.path.join(mp, f, "overworld")):
            for x in fn:
                out.add(os.path.relpath(os.path.join(dp, x), os.path.join(mp, f)).replace("\\", "/"))
        return out

    def expect(shown, site, hold):
        """PIL reference: per image, the folders whose surface image of that square is shown take part; for the other
        layers only folders whose surface image the site's map shows give pixels (v5)"""
        keys, has = set(), {}
        for f in SAFE:
            fk = files_of(f)
            keys |= fk
            has[f] = {k.split("/")[-1][:-4] for k in fk}
        out, bad = {}, set()
        for k in sorted(keys):
            sq = k.split("/")[-1][:-4]
            if sq == "0,-1":
                continue
            src = shown if k.startswith("overworld/day/") else site
            have = [f for f in SAFE if sq in src.get(f, ()) and sq not in hold.get(f, ()) and os.path.exists(os.path.join(mp, f, *k.split("/")))]
            if not have:
                continue
            tg = [f for f in SAFE if sq not in hold.get(f, ()) and (sq in shown.get(f, ()) or sq not in has[f])]
            ims = {f: load(f, k) for f in set(have) | {f for f in tg if os.path.exists(os.path.join(mp, f, *k.split("/")))}}
            if "bad" in ims.values():
                bad.add(k)
                continue
            for f in tg:
                own = ims.get(f)
                base = None
                for g in sorted(have, key=MT.get):   # the other shown copies, oldest first: the newest wins where they disagree
                    if g != f:
                        base = ims[g] if base is None else Image.alpha_composite(base, ims[g])
                if base is None:
                    continue
                res = base if own is None else Image.alpha_composite(base, own)   # own pixels on top: never changed
                if (own is None or res.tobytes() != own.tobytes()) and res.getchannel("A").getbbox():
                    out[f + "/" + k] = res
        return out, bad

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900}, accept_downloads=True)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html#report"); pg.wait_for_timeout(600)
        check(pg.locator("#jmFix").count() == 1 and pg.locator("#jmFixDir").count() == 1, "the 修復分流地圖 card is on the report page")

        def run(path=mp):
            pg.evaluate("window.__jmFix=null")
            pg.set_input_files("#jmFixDir", path)
            pg.wait_for_function("window.__jmFix", timeout=120000)
            return pg.evaluate("window.__jmFix")

        r = run()
        fl = {s["floor"]: s for s in r["floors"]}
        f3 = fl.get(3, {})
        sh = r.get("shown", {})
        check(sorted(f3.get("folders", [])) == sorted(SAFE), f"the three floor-3 folders are found (new ids by colour): {f3.get('folders')}")
        check(fl.get(1, {}).get("folders") == ["Triggers_815bd3d6~f22f~4114~a601~dfcf0a106221"] and fl[1]["n"] == 0, "a lone floor-1 world is left alone")
        check(sorted(r["unknown"]) == sorted(["Triggers_noise~d", WRONG, MIXED, MIXED2]), f"noise, wrong-id and mixed folders are refused: {r['why']}")
        check("第 2 層" in r["why"].get(WRONG, "") and "第 3 層" in r["why"].get(WRONG, ""), f"a known id that disagrees with the map says so: {r['why'].get(WRONG)}")
        check(r["why"].get(MIXED, "") == "%d,%d 這一格像第 2 層" % reg2, f"a floor-3 folder with one floor-2 image in it is refused by that image: {r['why'].get(MIXED)}")
        check(r["why"].get(MIXED2, "").startswith("同時像"), f"a folder that matches two floors is refused: {r['why'].get(MIXED2)}")
        # which squares are shown
        check(all(c(R) in sh.get(f, []) for f, R in ((A, R1), (A, R2), (A, R4), (B, R1), (B, R2), (B, R3), (C, R1), (C, R3))), f"big surface images are shown by the site's map: {sh}")
        check(c(R4) in sh.get(B, []), "a small piece that is the same picture as a shown copy is shown")
        check(c(R4) not in sh.get(C, []), "a small piece unlike the shown copy is not shown")
        check(c(FAR) not in sh.get(C, []) and c(FAR) not in sh.get(B, []), "a surface image no map can check, and a night image without one, are not shown")
        # v4 (V3-M1)
        check(c(R5) not in sh.get(CHB, []), "a piece that is the same as a site-shown copy where both drew, but also drew outside it, is not shown")
        check(c(R5) not in sh.get(CHC, []), "a piece that matches only that unshown piece (A -> B -> C) is not shown: no chain")
        check(c(R5) not in sh.get(XF, []), "a small piece of another floor's map inside a site-shown copy is not shown")
        check(c(R5) not in sh.get(MX, []), "a small piece 3/4 the same as the site-shown copy and 1/4 another floor is not shown")
        check(c(R6) not in sh.get(FLAT, []), "a piece of one flat colour, the same as the site-shown copy, is not shown")
        check(not any(x.startswith(FLAT) and x.endswith("/%d,%d.png" % R6) for x in r["names"]), "and it is not changed")
        only = lambda m: {f: (m or {}).get(f) for f in SAFE}
        check(only(r.get("site")) == SITE and only(r.get("sim")) == SIM and only(sh) == EXP,
              f"the shown copies are exactly the ones written out from the fixture (site {only(r.get('site')) == SITE}, piece {only(r.get('sim'))} vs {SIM})")
        want, bad = expect(EXP, SITE, HOLD)
        check(not any(x.startswith((WRONG, MIXED, MIXED2, "Triggers_noise", "Triggers_815")) for x in r["names"]), "refused folders and other floors are not touched")
        check(sorted(r["names"]) == sorted(want), f"the zip holds exactly the images that change ({len(r['names'])} vs {len(want)}): extra {sorted(set(r['names']) - set(want))[:3]} missing {sorted(set(want) - set(r['names']))[:3]}")
        check(not any(x.endswith("/%d,%d.png" % FAR) for x in r["names"]), "nothing at the unchecked square goes anywhere")
        nk = "overworld/night/%d,%d.png" % R4
        check(sorted(f3.get("held") or []) == sorted(f + " " + c(R4) for f in HOLD), f"a square shown by a small piece whose other layers are not each inside A's and the same is listed as left alone: {f3.get('held')}")
        check(sorted(f3.get("simok") or []) == sorted([B + " " + c(R4), OKN + " " + c(R4), HI + " " + c(R4)]), f"a small piece whose night image is inside A's and >= 90% the same is not left alone (v6): {f3.get('simok')}")
        check(OKN + "/" + D % R4 in r["names"] and OKN + "/" + nk in r["names"] and not any(x.startswith((OUTN, DIFN, TOPO, EDGE, NEAR, LO)) and x.endswith("/%d,%d.png" % R4) for x in r["names"]),
              "that folder takes A's surface and night images there; OUTN, DIFN, TOPO, EDGE, NEAR and LO are not changed there")
        check(not any(x.startswith(NIGHT) and x.endswith("/%d,%d.png" % R4) for x in r["names"]) and B + "/" + nk in r["names"] and B + "/" + D % R4 in r["names"],
              "that folder is not changed there; the folder with the same small piece and no other layer takes A's surface and night images")
        r5 = sorted(x.split("/")[0] for x in r["names"] if x.endswith("/%d,%d.png" % R5))
        check(r5 == sorted([B, C, FLAT, NIGHT, OKN, OUTN, DIFN, TOPO, EDGE, NEAR, LO, HI]), f"at the square of the unshown pieces only the folders with nothing there take A's shown half: {r5}")
        check(not any(x.startswith(C) and x.endswith("/%d,%d.png" % R4) for x in r["names"]) and any(x == B + "/" + D % R4 for x in r["names"]),
              "the folder with an unshown copy is not changed there; the shown small piece is filled")
        check(not any("0,-1" in x or "waypoints" in x for x in r["names"]) and f3.get("skip") == 2, f"square 0,-1 (2 copies) and waypoints are never in the zip: skip {f3.get('skip')}")
        badk = {k[len("overworld/"):-4] for k in bad}
        check(badk == {"night/" + c(R1), "topo/" + c(R1)} and set(f3.get("bad", [])) == badk and not any(x.split("/", 2)[2][:-4] in badk for x in r["names"]),
              f"images with an unreadable or wrong-size shown copy are left alone in every folder: {f3.get('bad')} vs {sorted(badk)}")
        check(f3.get("conflict", 0) > 0, f"pixels the folders drew differently are counted: {f3.get('conflict')}")
        check(not any(x == B + "/" + D % R3 for x in r["names"]), "a folder's own drawn image is not changed by a newer, different copy")
        txt = pg.inner_text("#jmFixOut")
        check(all(t in txt for t in ("第 3 層", "補 ", "不用修復", "不處理", "0,-1", "讀不到", "無法確認是這一層", "畫得不一樣")),
              "the result lists each floor, the skipped, unreadable and unchecked squares and the conflicts")
        zd, fnames = {}, []   # every part (v6: the fixture is now above one 40 MiB part)
        for i in range(pg.locator("#jmFixDl [data-jmfix]").count()):
            with pg.expect_download(timeout=120000) as dl:
                pg.click(f"#jmFixDl [data-jmfix='{i}']")
            zi = zipfile.ZipFile(io.BytesIO(open(dl.value.path(), "rb").read()))
            zd.update({k: zi.read(k) for k in zi.namelist()})
            fnames.append(dl.value.suggested_filename)
        names = sorted(zd)

        class z:
            read = staticmethod(lambda k: zd[k])
        check(names == sorted(want) and all(f.startswith("jm_fix_") for f in fnames), f"the download matches ({len(fnames)} parts)")
        diff = [k for k in names if k in want and Image.open(io.BytesIO(z.read(k))).convert("RGBA").tobytes() != want[k].tobytes()]
        check(not diff, f"every image keeps the folder's own pixels and fills the rest pixel for pixel (differs: {diff[:3]})")
        half = cut(*R5, (0, 0, 512, 256)).tobytes()
        check(all(Image.open(io.BytesIO(z.read(k))).convert("RGBA").tobytes() == half for k in names if k.endswith("/%d,%d.png" % R5)),
              "those images are A's shown half pixel for pixel: nothing the unshown pieces drew (below A's half, other floor) is in them")
        an = cut(*R4, (0, 256, 512, 512)).tobytes()
        nn = [k for k in names if k.endswith("/" + nk) and not k.startswith((OKN, HI))]
        check(nn and all(Image.open(io.BytesIO(z.read(k))).convert("RGBA").tobytes() == an for k in nn),
              f"every other night image written at that square is A's pixel for pixel: none of NIGHT's, OUTN's, DIFN's, EDGE's, NEAR's, LO's, HI's or OKN's own night pixels are in them ({len(nn)} images)")
        okb = zd.get(OKN + "/" + nk)
        okw = okb and Image.open(io.BytesIO(okb)).convert("RGBA")
        check(okw and okw.tobytes() == Image.alpha_composite(an4, okn).tobytes() and okw.crop(ob).tobytes() == okn.crop(ob).tobytes(),
              "OKN's own night pixels (the rows in another colour) are kept; the rest of its night image is A's")
        def no_edge(ks, get):   # nothing EDGE drew outside A's night shows up anywhere
            return all(not Image.open(io.BytesIO(get(k))).convert("RGBA").crop(eb).getchannel("A").getbbox() for k in ks if k.endswith("/" + nk))
        check(no_edge(names, z.read), "the rows EDGE drew outside A's night are in no image")
        def no_cyan(ks, get):   # nothing of NEAR's rows of another colour shows up anywhere (v8)
            return all(CYAN not in set(Image.open(io.BytesIO(get(k))).convert("RGBA").getdata()) for k in ks if k.endswith("/" + nk))
        check(no_cyan(names, z.read), "NEAR's night image (87.5% the same as A's) is in no image")
        def col_in(ks, get, col):   # the night images at that square holding a colour (v9)
            return sorted(k for k in ks if k.endswith("/" + nk) and col in set(Image.open(io.BytesIO(get(k))).convert("RGBA").getdata()))
        check(bn == 4096 and need == 3687 and YEL not in set(apc.getdata()) and ORA not in set(apc.getdata()),
              f"the bound pieces: {bn} drawn pixels, LO {need - 1} the same ({(need - 1) / bn:.4%}), HI {need} ({need / bn:.4%})")
        check(not col_in(names, z.read, YEL), "LO's night image (one same pixel short of 90%) is in no image")
        hib = zd.get(HI + "/" + nk)
        hiw = hib and Image.open(io.BytesIO(hib)).convert("RGBA")
        check(HI + "/" + D % R4 in r["names"] and hiw and hiw.tobytes() == Image.alpha_composite(an4, hin).tobytes(),
              "HI (exactly 90% the same) takes A's surface and night images there and keeps every pixel of its own")
        check(col_in(names, z.read, ORA) == [HI + "/" + nk], f"HI's own pixels are in no other image: {col_in(names, z.read, ORA)}")
        # split by size (zip headers counted), and the total limit
        # about 8 parts: headless Chromium on CI dropped the 20th download in a row from one page (22 parts at 1.6 MB)
        pg.evaluate("window.__JMFIX.PART=4000000")
        r2 = run()
        parts = r2.get("parts") or []
        nb = pg.locator("#jmFixDl [data-jmfix]").count()
        check(len(parts) > 1 and nb == len(parts) and sorted(sum(parts, [])) == sorted(want), f"a pack above the part size is split ({len(parts)} parts, {nb} buttons)")
        got, sizes = [], []
        for i in range(nb):
            with pg.expect_download(timeout=120000) as dl:
                pg.click(f"#jmFixDl [data-jmfix='{i}']")
            got += zipfile.ZipFile(dl.value.path()).namelist()
            sizes.append(os.path.getsize(dl.value.path()))
        check(sorted(got) == sorted(want), "the parts together hold every image once")
        check(any(len(q) > 1 for q in parts) and all(s <= 4000000 for s, q in zip(sizes, parts) if len(q) > 1) and sizes == r2["partBytes"],
              f"every zip is at most the part size and its size is counted exactly: {sizes} vs {r2['partBytes']}")
        pg.evaluate("window.__JMFIX.PART=40*1048576;window.__JMFIX.TOTAL=300000")
        r3 = run()
        check(r3["stop"] and r3["names"] == [] and pg.locator("#jmFixDl [data-jmfix]").count() == 0 and "停止" in pg.inner_text("#jmFixNote"), "above the total limit nothing is produced")
        pg.evaluate("window.__JMFIX.TOTAL=256*1048576")
        # copied in: nothing more to do, but this floor had squares left out, so it is not called complete
        for k in names:
            q = os.path.join(mp, *k.split("/"))
            os.makedirs(os.path.dirname(q), exist_ok=True)
            open(q, "wb").write(z.read(k))
        r4 = run()
        f34 = {s["floor"]: s for s in r4["floors"]}.get(3, {})
        note = pg.inner_text("#jmFixNote")
        check(r4["names"] == [] and "無法確認是否完整" in note and "已經完整" not in note and "無法確認完整" in pg.inner_text("#jmFixOut"),
              f"running again finds nothing to do and does not call a floor with left-out squares complete: {note}")
        # v7 (local review of v6, M1/M2): a second round with a folder that joins after the repair (nothing at R4).
        # OKN is now whole there, so the site's map shows it and its night image is a source. What it gives is fixed here
        # (v7 keeps v6's rule, choice (a)): A's night with OKN's 4 rows of another colour on top, because the copied-in
        # image is the newest. The copied-in images get set times so the newest is not a tie
        for k in names:
            t = T + 2001 if k == OKN + "/" + nk else T + 2000
            os.utime(os.path.join(mp, *k.split("/")), (t, t))
        NEW = "Triggers_fix00016~new"
        put(NEW, D % R1, cut(*R1), T + 2000)
        r6 = run()
        f36 = {s["floor"]: s for s in r6["floors"]}.get(3, {})
        zd6 = {}
        for i in range(pg.locator("#jmFixDl [data-jmfix]").count()):
            with pg.expect_download(timeout=120000) as dl:
                pg.click(f"#jmFixDl [data-jmfix='{i}']")
            zi = zipfile.ZipFile(io.BytesIO(open(dl.value.path(), "rb").read()))
            zd6.update({k: zi.read(k) for k in zi.namelist()})
        check(sorted(r6["names"]) == sorted(zd6) and r6["names"] and all(k.startswith(NEW + "/") for k in r6["names"]),
              f"second round: only the new folder takes anything ({len(r6['names'])} images, others {[k for k in r6['names'] if not k.startswith(NEW + '/')][:3]})")
        check(sorted(f36.get("held") or []) == sorted(f + " " + c(R4) for f in HOLD), f"second round: the same squares are left alone: {f36.get('held')}")
        nw = zd6.get(NEW + "/" + nk)
        check(nw is not None and Image.open(io.BytesIO(nw)).convert("RGBA").tobytes() == Image.alpha_composite(an4, okn).tobytes(),
              "second round: the new folder's night image there is A's with OKN's rows of another colour (inside A's night, at most 10% of OKN's piece)")
        check(no_edge(zd6, zd6.get), "second round: the rows EDGE drew outside A's night are in no image")
        check(no_cyan(zd6, zd6.get), "second round: NEAR's night image is in no image")
        check(not col_in(zd6, zd6.get, YEL), "second round: LO's night image is in no image")
        # a clean pair: complete
        mp2 = os.path.join(tmp, "mp2")
        for f in (A, B):
            put(f, D % R1, cut(*R1), T, mp2)
        r5 = run(mp2)
        check(r5["names"] == [] and "已經完整" in pg.inner_text("#jmFixNote") and "已經完整" in pg.inner_text("#jmFixOut"), "two folders that hold the same is called complete")
        check(not errs, f"no page errors: {errs[:2]}")
        b.close()
    srv.shutdown()
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("ALL PASSED" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
