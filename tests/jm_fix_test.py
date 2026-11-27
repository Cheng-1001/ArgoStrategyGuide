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
- (v13) an image of a square that is not shown gives only its pieces connected to confirmed map (square 0,-1 included); waypoints
  are not in the main fixture's zip; an image with an unreadable or wrong-size shown copy is never in the zip
- the result never says "complete" while something was left out; it does when nothing was
- the zip splits by size counting zip headers; above the total limit nothing is produced; running again finds nothing to do
- v11 (owner 2026-11-27, waypoints of one floor merged; separate fixture mp3, the main fixture keeps "no waypoints"): a folder
  takes the other folders' points it lacks, byte for byte, and keeps every byte it had; death and temp points are not shared;
  a point it has (same guid, or same name, position and dimension) is not changed; of a point several folders have the
  newest file's copy is given; a custom group comes along; a file without points gets its "waypoints" tag; gzip, cut-off,
  trailing-byte and garbage files are listed and neither give nor take; running again writes nothing
- v12 (GPT V11-M1, V11-M2; separate fixture mp4): a file whose "groups" holds a non-compound, whose root holds another tag or
  "groups"/"waypoints" twice, or with a key twice in any compound (a point's guid, the points, a nested compound) is listed and
  neither gives nor takes; a folder whose merged file would be over 4 MiB is listed and left alone while the other folders and
  the images are still repaired; exactly 4 MiB is written and read back; running again stays the same
- v13 (owner 2026-11-27: straight cuts at 0,-1 and at squares the site's map hardly reaches; separate fixture mp6): a piece of
  an unshown image is given only when it touches drawn pixels of a site-shown square of the same folder and layer and every
  side it reaches leads to one or on into the same piece (across two unshown squares); the login world, pieces reaching
  unexplored sides and pieces joined to such are not given; a folder with its own unconfirmed copy takes pieces at 0,-1, not
  where its own pieces would join theirs, and elsewhere only when all of its own is confirmed; running again writes nothing
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


# JourneyMap 6 WaypointData.dat (uncompressed NBT), written and read here independently of the page (v11)
import struct, gzip


def mutf8(t):   # Java modified UTF-8: a character above U+FFFF as two 3-byte surrogates
    out = b""
    for ch in t:
        o = ord(ch)
        if o > 0xFFFF:
            o -= 0x10000
            out += (chr(0xD800 + (o >> 10)) + chr(0xDC00 + (o & 0x3FF))).encode("utf-8", "surrogatepass")
        else:
            out += ch.encode("utf-8")
    return out


def nstr(t):
    b = mutf8(t) if isinstance(t, str) else t
    return struct.pack(">H", len(b)) + b


def ntag(t, name, payload):
    return bytes([t]) + nstr(name) + payload


def ncomp(*kids):
    return b"".join(kids) + b"\0"


def wp_point(guid, name, xyz, group, color=-12884949):
    pos = ncomp(ntag(3, "x", struct.pack(">i", xyz[0])), ntag(3, "y", struct.pack(">i", xyz[1])), ntag(3, "z", struct.pack(">i", xyz[2])),
                ntag(8, "dimension", nstr("minecraft:overworld")))
    return ntag(10, guid, ncomp(ntag(10, "settings", ncomp(ntag(1, "enable", b"\1"))), ntag(3, "color", struct.pack(">i", color)),
                                ntag(10, "pos", pos), ntag(8, "groupId", nstr(group)), ntag(8, "name", nstr(name)), ntag(8, "guid", nstr(guid)),
                                ntag(9, "dimensions", b"\x08" + struct.pack(">i", 1) + nstr("minecraft:overworld"))))


def wp_group(guid, name):
    return ntag(10, guid, ncomp(ntag(8, "name", nstr(name)), ntag(8, "guid", nstr(guid)), ntag(8, "modId", nstr("journeymap"))))


BUILTIN = [wp_group(g, n) for g, n in (("journeymap_all", "全部"), ("journeymap_death", "死亡"), ("journeymap_temp", "暫存"), ("journeymap_default", "預設"))]


def wp_file(points, groups=()):
    kids = [ntag(10, "groups", ncomp(*BUILTIN, *groups))]
    if points:
        kids.append(ntag(10, "waypoints", ncomp(*points)))
    return b"\x0a" + nstr("") + ncomp(*kids)


def nkids(b, p):
    """the children of the compound whose payload starts at p: [(name, type, start, end)], and the position after its TAG_End"""
    out = []
    while True:
        t = b[p]
        if t == 0:
            return out, p + 1
        a = p
        n = struct.unpack(">H", b[p + 1:p + 3])[0]
        name = b[p + 3:p + 3 + n]
        p = nskip(b, t, p + 3 + n)
        out.append((name, t, a, p))


def nskip(b, t, p):
    if t in (1, 2, 3, 4, 5, 6):
        return p + {1: 1, 2: 2, 3: 4, 4: 8, 5: 4, 6: 8}[t]
    if t == 8:
        return p + 2 + struct.unpack(">H", b[p:p + 2])[0]
    if t == 9:
        et, n = b[p], struct.unpack(">i", b[p + 1:p + 5])[0]
        p += 5
        for _ in range(n):
            p = nskip(b, et, p)
        return p
    if t == 10:
        return nkids(b, p)[1]
    raise ValueError(t)


def wp_read(b):
    """{"groups": {guid bytes: the whole tag}, "waypoints": {...}}; raises unless the file is exactly one root compound"""
    assert b[:3] == b"\x0a\0\0"
    top, end = nkids(b, 3)
    assert end == len(b)
    return {name.decode(): {k: b[x:y] for k, _, x, y in nkids(b, a + 3 + len(name))[0]} for name, t, a, e in top}


def pieces(alpha, site, judged, roots=False):
    """v13 reference. alpha: {(folder, layer, sq): bytes of 512*512 alpha}; site: {folder: set of sq}; judged: keys to judge.
    Returns {key: bytearray, 1 = pixel of a given piece}; with roots also {key: [piece of each pixel, -1 = clear]} (v14)"""
    from collections import deque
    lab, ncomp_, base, tot = {}, {}, {}, 0
    for key in judged:
        a = alpha[key]
        lb = [-1] * 262144
        n = 0
        for s0 in range(262144):
            if not a[s0] or lb[s0] >= 0:
                continue
            q = deque([s0])
            lb[s0] = n
            while q:
                i = q.popleft()
                x, y = i % 512, i // 512
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < 512 and 0 <= ny < 512:
                        j = ny * 512 + nx
                        if a[j] and lb[j] < 0:
                            lb[j] = n
                            q.append(j)
            n += 1
        lab[key], ncomp_[key], base[key] = lb, n, tot
        tot += n
    par = list(range(tot))

    def root(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    good, bad = set(), set()
    for key in judged:
        f, L, sq = key
        rx, rz = map(int, sq.split(","))
        for (dx, dz) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nb = "%d,%d" % (rx + dx, rz + dz)
            nk = (f, L, nb)
            here = [(0, y) for y in range(512)] if dx < 0 else [(511, y) for y in range(512)] if dx > 0 else [(x, 0) for x in range(512)] if dz < 0 else [(x, 511) for x in range(512)]
            reach, touch = set(), set()
            for x, y in here:
                c = lab[key][y * 512 + x]
                if c < 0:
                    continue
                reach.add(c)
                ax, ay = (x + dx) % 512, (y + dz) % 512   # the pixel across the side, in the neighbour
                j = ay * 512 + ax
                if nb in site.get(f, ()):
                    if nk in alpha and alpha[nk][j]:
                        good.add(base[key] + c)
                elif nk in lab and alpha[nk][j]:
                    touch.add(c)
                    par[root(base[key] + c)] = root(base[nk] + lab[nk][j])
            if nb not in site.get(f, ()):
                bad |= {base[key] + c for c in reach - touch}
    rg, rb = {root(g) for g in good}, {root(g) for g in bad}
    out, rt = {}, {}
    for key in judged:
        m, q = bytearray(262144), [-1] * 262144
        for i, c in enumerate(lab[key]):
            if c >= 0:
                r = root(base[key] + c)
                q[i] = r
                m[i] = 1 if r in rg and r not in rb else 0
        out[key] = m
        rt[key] = q
    return (out, rt) if roots else out


def keep_ref(f, live, alpha, acc, shown, site, hold, pre):
    """v14 reference (GPT V13-M1): live = {(layer, sq): alpha bytes after taking} a folder would take; alpha = the folder's
    own images now; acc = their given pixels now; pre = (layer, sq) of its images judged now. Judged again as the next run
    would: with its site-shown squares, and with every square whose surface image it takes (not 0,-1) shown too. Where an
    own pixel not given now would be given, left out: images with new pixels in that piece, images with new pixels right
    across from it in a site-shown square, every image of a square becoming shown next to it; again until nothing changes.
    Returns the (layer, sq) left out, in order"""
    live, cut_ = dict(live), []
    side = lambda dx, dz: [(0, y) for y in range(512)] if dx < 0 else [(511, y) for y in range(512)] if dx > 0 else [(x, 0) for x in range(512)] if dz < 0 else [(x, 511) for x in range(512)]
    while True:
        nd = {sq for (L, sq) in live if L == "day" and sq not in site and sq != "0,-1"}
        kill, flip = [], False
        for st in (set(site), set(site) | nd):
            A = {(f, L, sq): a for (L, sq), a in alpha.items()}
            A.update({(f, L, sq): a for (L, sq), a in live.items()})
            jd = {(f, L, sq) for (L, sq) in set(pre) | {k for k in live if k[1] not in shown and k[1] not in hold} if sq not in st and (f, L, sq) in A}
            m2, rt = pieces(A, {f: st}, jd, roots=True)
            for L in sorted({k[1] for k in jd}):
                V = set()
                for key in jd:
                    if key[1] != L or (L, key[2]) not in acc or (L, key[2]) not in alpha:
                        continue
                    own, m = alpha[(L, key[2])], acc[(L, key[2])]
                    V |= {rt[key][i] for i in range(262144) if own[i] and not m[i] and m2[key][i]}
                if not V:
                    continue
                flip = True
                for key in sorted(jd):
                    if key[1] != L:
                        continue
                    sq = key[2]
                    if (L, sq) in live:
                        own = alpha.get((L, sq))
                        if any(live[(L, sq)][i] and not (own and own[i]) and rt[key][i] in V for i in range(262144)):
                            kill.append((L, sq))
                    rx, rz = map(int, sq.split(","))
                    for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        nb = "%d,%d" % (rx + dx, rz + dz)
                        if nb not in st:
                            continue
                        hit = [(x, y) for x, y in side(dx, dz) if rt[key][y * 512 + x] in V]
                        if not hit:
                            continue
                        c, own = live.get((L, nb)), alpha.get((L, nb))
                        if c and any(c[((y + dz) % 512) * 512 + (x + dx) % 512] and not (own and own[((y + dz) % 512) * 512 + (x + dx) % 512]) for x, y in hit):
                            kill.append((L, nb))
                        if nb in nd:
                            kill += [k for k in live if k[1] == nb]
        if not flip:
            return cut_
        for k in (dict.fromkeys(kill) or list(live)):
            if k in live:
                del live[k]
                cut_.append(k)


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

    def load(folder, rel, root=None):
        p = os.path.join(root or mp, folder, *rel.split("/"))
        if not os.path.exists(p):
            return None
        try:
            im = Image.open(p)
            im.load()
            return im.convert("RGBA") if im.size == (512, 512) else "bad"
        except Exception:
            return "bad"

    def files_of(f, root=None):
        out = set()
        for dp, _, fn in os.walk(os.path.join(root or mp, f, "overworld")):
            for x in fn:
                out.add(os.path.relpath(os.path.join(dp, x), os.path.join(root or mp, f)).replace("\\", "/"))
        return out

    def expect(shown, site, hold, root=None, folders=None, mt=None):
        """PIL reference: per image, the folders whose surface image of that square is shown take part; for the other
        layers only folders whose surface image the site's map shows give pixels (v5); (v13) an image of a square that is
        not shown gives its pieces connected to confirmed map (pieces() above). Returns (images, bad keys, cut, part)"""
        root, folders, mt = root or mp, folders or SAFE, mt or MT
        ex = lambda f, k: os.path.exists(os.path.join(root, f, *k.split("/")))
        keys, has, fk = set(), {}, {}
        for f in folders:
            fk[f] = files_of(f, root)
            keys |= fk[f]
            has[f] = {k.split("/")[-1][:-4] for k in fk[f]}
        alpha, judged, part = {}, set(), {}
        for f in folders:
            for k in fk[f]:
                L, sq = k.split("/")[1], k.split("/")[-1][:-4]
                im = load(f, k, root)
                if im not in (None, "bad"):
                    alpha[(f, L, sq)] = im.getchannel("A").tobytes()
                if sq in shown.get(f, ()) or sq in hold.get(f, ()):
                    continue
                if im in (None, "bad"):
                    part.setdefault(f, set()).add(L + "/" + sq)
                else:
                    judged.add((f, L, sq))
        acc = pieces(alpha, {f: set(site.get(f, ())) for f in folders}, judged)
        for (f, L, sq), m in acc.items():
            if any(a and not g for a, g in zip(alpha[(f, L, sq)], m)):
                part.setdefault(f, set()).add(L + "/" + sq)
        sure = lambda f, sq: all((f, k.split("/")[1], sq) in acc and k.split("/")[1] + "/" + sq not in part.get(f, ()) for k in fk[f] if k.split("/")[-1][:-4] == sq)
        out, bad, cut_ = {}, set(), []
        for k in sorted(keys):
            L, sq = k.split("/")[1], k.split("/")[-1][:-4]
            src = shown if k.startswith("overworld/day/") else site
            have = [f for f in folders if sq not in hold.get(f, ()) and ex(f, k) and (sq in src.get(f, ()) or (sq not in shown.get(f, ()) and any(acc.get((f, L, sq), b""))))]
            if not have:
                continue
            tg = [f for f in folders if sq not in hold.get(f, ()) and (sq in shown.get(f, ()) or sq not in has[f] or sq == "0,-1" or sure(f, sq))]
            ims = {f: load(f, k, root) for f in set(have) | {f for f in tg if ex(f, k)}}
            if "bad" in ims.values():
                bad.add(k)
                continue
            give = {}
            for g in have:   # an unshown copy gives only its pieces
                im = ims[g]
                if sq not in shown.get(g, ()):
                    keep = Image.frombytes("L", (512, 512), bytes(255 if v else 0 for v in acc[(g, L, sq)]))
                    im = Image.composite(im, Image.new("RGBA", (512, 512), (0, 0, 0, 0)), keep)   # the rest clear
                give[g] = im
            for f in tg:
                own = ims.get(f)
                base = None
                for g in sorted(have, key=mt.get):   # the other copies, oldest first: the newest wins where they disagree
                    if g != f:
                        base = give[g] if base is None else Image.alpha_composite(base, give[g])
                if base is None:
                    continue
                res = base if own is None else Image.alpha_composite(base, own)   # own pixels on top: never changed
                if not ((own is None or res.tobytes() != own.tobytes()) and res.getchannel("A").getbbox()):
                    continue
                out[f + "/" + k] = res
        for f in folders:   # v14: judged again as the next run would see the folder
            mine = {k: v for k, v in out.items() if k.startswith(f + "/")}
            if not mine:
                continue
            lk = lambda k: tuple(k[len(f + "/overworld/"):-4].split("/"))
            live = {lk(k): v.getchannel("A").tobytes() for k, v in mine.items()}
            own = {(L, sq): a for (g, L, sq), a in alpha.items() if g == f}
            pre = [(L, sq) for (g, L, sq) in judged if g == f]
            accf = {(L, sq): m for (g, L, sq), m in acc.items() if g == f}
            for L, sq in keep_ref(f, live, own, accf, set(shown.get(f, ())), set(site.get(f, ())), set(hold.get(f, ())), pre):
                del out[f + "/overworld/" + L + "/" + sq + ".png"]
                cut_.append(f + " " + L + "/" + sq)
        return out, bad, cut_, part

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
        want, bad, _, part1 = expect(EXP, SITE, HOLD)
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
        check(not any("0,-1" in x or "waypoints" in x for x in r["names"]) and {A + " 0,-1", B + " 0,-1"} <= set(f3.get("unshown") or []) and "day/0,-1" in r["part"].get(A, []) and "day/0,-1" in r["part"].get(B, []),
              f"v13: A's 0,-1 (reaching sides with nothing confirmed across) and B's whole-square login image give nothing and are listed; no waypoints: {r['part'].get(A)}")
        check({f: sorted(v) for f, v in r["part"].items() if v and f in SAFE} == {f: sorted(v) for f, v in part1.items() if v},
              f"v13: the images with pieces left out are exactly the reference's: {[f[-6:] for f, v in r['part'].items() if v]}")
        badk = {k[len("overworld/"):-4] for k in bad}
        check(badk == {"night/" + c(R1), "topo/" + c(R1)} and set(f3.get("bad", [])) == badk and not any(x.split("/", 2)[2][:-4] in badk for x in r["names"]),
              f"images with an unreadable or wrong-size shown copy are left alone in every folder: {f3.get('bad')} vs {sorted(badk)}")
        check(f3.get("conflict", 0) > 0, f"pixels the folders drew differently are counted: {f3.get('conflict')}")
        check(not any(x == B + "/" + D % R3 for x in r["names"]), "a folder's own drawn image is not changed by a newer, different copy")
        txt = pg.inner_text("#jmFixOut")
        check(all(t in txt for t in ("第 3 層", "補 ", "不用修復", "不處理", "沒有和已確認的地圖相連", "讀不到", "無法確認是這一層", "畫得不一樣")),
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
        # v11: waypoints (separate fixture)
        check(f3.get("wpBad") == [B] and not any("waypoints" in x for x in r["names"]), f"the main fixture: B's unreadable waypoint file is listed, no waypoint file is written: {f3.get('wpBad')}")
        mp3 = os.path.join(tmp, "mp3")
        P, Q, RR, GZ, TR, CUT, JUNK, NOF = ("Triggers_wp00001~p", "Triggers_wp00002~q", "Triggers_wp00003~r", "Triggers_wp00004~gz",
                                            "Triggers_wp00005~trail", "Triggers_wp00006~cut", "Triggers_wp00007~junk", "Triggers_wp00008~nofile")
        g1, gq, gq2 = "11111111-0000-0000-0000-000000000001", "22222222-0000-0000-0000-000000000001", "22222222-0000-0000-0000-000000000002"
        gd, gt, gc, gu = ("11111111-0000-0000-0000-00000000000d", "11111111-0000-0000-0000-00000000000e",
                          "11111111-0000-0000-0000-00000000000c", "11111111-0000-0000-0000-00000000000f")
        MINE = wp_group("g-custom-1", "我的")
        pts = {"p1": wp_point(g1, "遠古樹人", (100, 70, 200), "journeymap_default"),
               "pd": wp_point(gd, "死亡 00:05:24 11-24-2026", (5, 6, 7), "journeymap_death"),
               "pt": wp_point(gt, "暫存", (8, 9, 10), "journeymap_temp"),
               "pc": wp_point(gc, "自己的群組", (11, 12, 13), "g-custom-1"),
               "pu": wp_point(gu, "樹\U0001F332", (14, 15, 16), "journeymap_default"),   # a character above U+FFFF
               "q1": wp_point(gq, "Q 的點", (300, 71, 400), "journeymap_default"),
               "p1q": wp_point(g1, "改名", (100, 70, 200), "journeymap_default", 255),   # P's point, changed in Q (newer)
               "q2": wp_point(gq2, "遠古樹人", (100, 70, 200), "journeymap_default")}   # P's point again under another guid
        WF = {P: wp_file([pts[k] for k in ("p1", "pd", "pt", "pc", "pu")], [MINE]), Q: wp_file([pts[k] for k in ("q1", "p1q", "q2")]),
              RR: wp_file([]), GZ: gzip.compress(wp_file([pts["q1"]])), TR: wp_file([pts["q1"]]) + b"\0", CUT: wp_file([pts["q1"]])[:-5], JUNK: b"x" * 40}
        MTW = {P: T + 10, Q: T + 20, RR: T + 5, GZ: T + 30, TR: T + 30, CUT: T + 30, JUNK: T + 30}
        for f in (P, Q, RR, GZ, TR, CUT, JUNK, NOF):
            put(f, D % R1, cut(*R1), T, mp3)
        for f, data in WF.items():
            put(f, "waypoints/WaypointData.dat", data, MTW[f], mp3)
        r7 = run(mp3)
        f37 = {s["floor"]: s for s in r7["floors"]}.get(3, {})
        zd7 = {}
        for i in range(pg.locator("#jmFixDl [data-jmfix]").count()):
            with pg.expect_download(timeout=120000) as dl:
                pg.click(f"#jmFixDl [data-jmfix='{i}']")
            zi = zipfile.ZipFile(io.BytesIO(open(dl.value.path(), "rb").read()))
            zd7.update({k: zi.read(k) for k in zi.namelist()})
        WK = lambda f: f + "/waypoints/WaypointData.dat"
        check(sorted(f37.get("folders", [])) == sorted([P, Q, RR, GZ, TR, CUT, JUNK, NOF]) and sorted(zd7) == sorted(map(WK, (P, Q, RR))) and sorted(r7["names"]) == sorted(zd7),
              f"waypoints: only P, Q and R get a file (the images are already the same): {sorted(zd7)}")
        check(sorted(f37.get("wpBad") or []) == sorted([GZ, TR, CUT, JUNK]), f"gzip, trailing-byte, cut-off and garbage files are listed: {f37.get('wpBad')}")
        GU = {"q1": gq, "q2": gq2, "pc": gc, "pu": gu, "p1q": g1}
        want = {P: ["q1"], Q: ["pc", "pu"], RR: ["q1", "p1q", "q2", "pc", "pu"]}   # sources newest first: Q, then P
        okp = True
        for f, add in want.items():
            try:
                o, n = wp_read(WF[f]), wp_read(zd7.get(WK(f), b""))
            except Exception as e:
                check(False, f"waypoints: {f}'s new file reads ({e!r})")
                okp = False
                continue
            nw, ow = n.get("waypoints", {}), o.get("waypoints", {})
            got = [k for k in nw if k not in ow]
            exp = [GU[a].encode() for a in add]
            check(got == exp and all(nw[k] == pts[a] for k, a in zip(exp, add)),
                  f"waypoints: {f[-1]} takes {add} byte for byte, nothing else: {[k.decode()[-2:] for k in got]}")
            check(all(nw.get(k) == v for k, v in ow.items()) and all(n["groups"].get(k) == v for k, v in o["groups"].items()),
                  f"waypoints: every point and group {f[-1]} had is unchanged")
            nb = zd7[WK(f)]   # the old file is the new one with the added tags taken out (for R also the "waypoints" tag it had to get)
            for v in [nw.get(k, b"\xff") for k in exp] + ([MINE] if "pc" in add else []):   # a point that is missing: no match, FAIL below
                i = nb.rfind(v)
                if i >= 0:
                    nb = nb[:i] + nb[i + len(v):]
            if not ow:
                nb = nb.replace(b"\x0a\x00\x09waypoints\x00", b"", 1)
            check(nb == WF[f], f"waypoints: {f[-1]}'s file is its old bytes with only the added tags inserted")
        check(okp and b"g-custom-1" in wp_read(zd7[WK(RR)])["groups"] and b"g-custom-1" in wp_read(zd7[WK(Q)])["groups"],
              "waypoints: a custom group comes with its point")
        check(f37.get("wp") == 8 and f37.get("wpf") == 3 and "路標 8 個" in pg.inner_text("#jmFixOut") and "3 個分流的路標" in pg.inner_text("#jmFixNote"),
              f"waypoints: the result counts 8 points in 3 folders: {f37.get('wp')}, {f37.get('wpf')}")
        for k, v in zd7.items():
            open(os.path.join(mp3, *k.split("/")), "wb").write(v)
        r8 = run(mp3)
        check(r8["names"] == [], f"waypoints: running again writes nothing: {r8['names']}")
        # v12: files that are not exactly the shape, and the 4 MiB limit after merging (separate fixture)
        mp4 = os.path.join(tmp, "mp4")
        GOOD, SMALL, BIG, BIGOK = "Triggers_wq00001~good", "Triggers_wq00002~small", "Triggers_wq00003~big", "Triggers_wq00004~bigok"
        BADS = ["Triggers_wq%05d~bad%d" % (10 + i, i) for i in range(1, 8)]
        gk = "33333333-0000-0000-0000-000000000001"
        k1 = wp_point(gk, "好的點", (1, 2, 3), "journeymap_default")
        bp = [wp_point("44444444-0000-0000-0000-00000000000%d" % i, "壞的點 %d" % i, (i, i, i), "journeymap_default") for i in range(1, 9)]
        root = lambda *kids: b"\x0a" + nstr("") + ncomp(*kids)
        grp = lambda *extra: ntag(10, "groups", ncomp(*BUILTIN, *extra))
        wps = lambda *pp: ntag(10, "waypoints", ncomp(*pp))

        def pt_raw(guid, fields):   # a point from its fields, so a field can be there twice
            return ntag(10, guid, ncomp(*fields))
        pos = ntag(10, "pos", ncomp(ntag(3, "x", struct.pack(">i", 7)), ntag(3, "y", struct.pack(">i", 7)), ntag(3, "z", struct.pack(">i", 7)),
                                    ntag(8, "dimension", nstr("minecraft:overworld"))))
        g5 = "44444444-0000-0000-0000-000000000005"
        g7 = "44444444-0000-0000-0000-000000000007"
        BADF = [root(grp(ntag(8, "oops", nstr("x"))), wps(bp[0])),                                  # 1 "groups" holds a string
                root(grp(), wps(bp[1]), ntag(8, "extra", nstr("x"))),                               # 2 another tag in the root
                root(grp(), grp(), wps(bp[2])),                                                     # 3 "groups" twice
                root(grp(), wps(bp[3]), wps(bp[7])),                                                # 4 "waypoints" twice
                root(grp(), wps(pt_raw(g5, [pos, ntag(8, "groupId", nstr("journeymap_default")), ntag(8, "name", nstr("壞的點 5")),
                                            ntag(8, "guid", nstr(g5)), ntag(8, "guid", nstr(g5))]))),   # 5 a point's guid twice
                root(grp(), wps(bp[5], bp[5])),                                                     # 6 one point key twice in "waypoints"
                root(grp(), wps(pt_raw(g7, [ntag(10, "settings", ncomp(ntag(1, "enable", b"\1"), ntag(1, "enable", b"\0"))), pos,
                                            ntag(8, "groupId", nstr("journeymap_default")), ntag(8, "name", nstr("壞的點 7")), ntag(8, "guid", nstr(g7))])))]   # 7 a key twice in a nested compound
        WMAX = 4 * 1048576

        def padded(size):   # a file without points of exactly this size: a custom group carries a byte array
            def mk(n):
                return wp_file([], [ntag(10, "g-pad", ncomp(ntag(8, "name", nstr("pad")), ntag(8, "guid", nstr("g-pad")), ntag(7, "pad", struct.pack(">i", n) + b"\0" * n)))])
            return mk(size - len(mk(0)))
        WF4 = {GOOD: wp_file([k1]), SMALL: wp_file([]), BIG: padded(WMAX - 64), BIGOK: padded(WMAX - len(k1) - 13)}   # 13: the "waypoints" tag it has to get
        WF4.update(zip(BADS, BADF))
        check(len(WF4[BIG]) == WMAX - 64 and len(WF4[BIG]) + len(k1) > WMAX and len(WF4[BIGOK]) + 13 + len(k1) == WMAX and len(k1) > 64,
              f"v12 fixture: BIG is under 4 MiB and over it with the point added, BIGOK exactly 4 MiB: {len(WF4[BIG])}, {len(k1)}")
        for f in WF4:
            put(f, D % R1, cut(*R1, (256, 0, 512, 512)) if f == SMALL else cut(*R1), T, mp4)
            put(f, "waypoints/WaypointData.dat", WF4[f], T + 10, mp4)
        r9 = run(mp4)
        f49 = {s["floor"]: s for s in r9["floors"]}.get(3, {})
        zd9 = {}
        for i in range(pg.locator("#jmFixDl [data-jmfix]").count()):
            with pg.expect_download(timeout=120000) as dl:
                pg.click(f"#jmFixDl [data-jmfix='{i}']")
            zi = zipfile.ZipFile(io.BytesIO(open(dl.value.path(), "rb").read()))
            zd9.update({k: zi.read(k) for k in zi.namelist()})
        out9 = pg.inner_text("#jmFixOut")
        check(sorted(f49.get("wpBad") or []) == sorted(BADS), f"v12: every file that is not exactly the shape is listed: {[x[-4:] for x in f49.get('wpBad') or []]}")
        check(sorted(zd9) == sorted([WK(SMALL), WK(BIGOK), SMALL + "/" + D % R1]) and sorted(r9["names"]) == sorted(zd9),
              f"v12: only SMALL (image and points) and BIGOK are written; BIG, GOOD and the bad files are not: {sorted(zd9)}")
        try:
            n9 = wp_read(zd9.get(WK(SMALL), b""))
            check(list(n9.get("waypoints", {})) == [gk.encode()] and n9["waypoints"][gk.encode()] == k1,
                  f"v12: SMALL takes the good point only, none from a bad file: {[k.decode()[-2:] for k in n9.get('waypoints', {})]}")
        except Exception as e:
            check(False, f"v12: SMALL's new file reads ({e!r})")
        bo = zd9.get(WK(BIGOK), b"")
        check(len(bo) == WMAX and bo.replace(k1, b"", 1).replace(b"\x0a\x00\x09waypoints\x00", b"", 1) == WF4[BIGOK],
              f"v12: BIGOK is written at exactly 4 MiB, its old bytes and the point: {len(bo)}")
        check(f49.get("wpBig") == [BIG] and "超過 4.0 MB" in out9 and "已經完整" not in out9 and f49.get("wp") == 2 and f49.get("wpf") == 2 and f49.get("n") == 1,
              f"v12: BIG (over 4 MiB merged) is listed and left alone, the rest still repaired: {f49.get('wpBig')}, {f49.get('wp')}, {f49.get('n')}")
        for k, v in zd9.items():
            open(os.path.join(mp4, *k.split("/")), "wb").write(v)
        r10 = run(mp4)
        f410 = {s["floor"]: s for s in r10["floors"]}.get(3, {})
        check(r10["names"] == [] and f410.get("wpBig") == [BIG] and sorted(f410.get("wpBad") or []) == sorted(BADS),
              f"v12: running again writes nothing, the 4 MiB file reads back, BIG and the bad files stay listed: {r10['names']}, {f410.get('wpBig')}")
        mp5 = os.path.join(tmp, "mp5")   # only the 4 MiB case left out: not "complete"
        for f in (GOOD, BIG):
            put(f, D % R1, cut(*R1), T, mp5)
            put(f, "waypoints/WaypointData.dat", WF4[f], T + 10, mp5)
        r11 = run(mp5)
        check(r11["names"] == [] and "已經完整" not in pg.inner_text("#jmFixNote") + pg.inner_text("#jmFixOut") and "無法確認完整" in pg.inner_text("#jmFixOut"),
              f"v12: a floor whose only left-out folder is over 4 MiB is not called complete: {pg.inner_text('#jmFixNote')}")
        # v13: pieces of unshown images (separate fixture). 0,0 1,-1 0,2 1,2 are shown by the site's map; 0,-1 is never
        # judged; 0,3 and 1,3 have 17 and 22 chunks on the site's map (< NMIN): not shown
        mp6 = os.path.join(tmp, "mp6")
        DN, T1, T2, T3, T4 = "Triggers_cn00001~donor", "Triggers_cn00002~none", "Triggers_cn00003~login", "Triggers_cn00004~joins", "Triggers_cn00005~own03"
        F6 = [DN, T1, T2, T3, T4]
        MT6 = {DN: T + 50, T1: T, T2: T, T3: T, T4: T}
        tex = cut(0, 0)

        def piece(*boxes, fill=None):
            im = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            for bx in boxes:
                im.paste(tex.crop(bx) if fill is None else Image.new("RGBA", (bx[2] - bx[0], bx[3] - bx[1]), fill), bx[:2])
            return im
        P1, P2, P3, P4 = (300, 430, 512, 512), (64, 150, 272, 361), (0, 496, 16, 512), (100, 0, 141, 41)
        for f in F6:
            for sq in ((0, 0), (1, -1), (0, 2), (1, 2)):
                put(f, D % sq, cut(*sq), MT6[f], mp6)
        for sq in ((0, 0), (1, -1), (0, 2), (1, 2)):
            put(DN, "overworld/night/%d,%d.png" % sq, cut(*sq), MT6[DN], mp6)
        put(DN, D % (0, -1), piece(P1, P2, P3, P4), MT6[DN], mp6)             # P1 touches 0,0 and 1,-1; P2 the login world; P3, P4 reach unexplored sides
        put(DN, "overworld/night/0,-1.png", piece(P1, P2), MT6[DN], mp6)
        put(DN, D % (0, 3), piece((100, 0, 512, 151)), MT6[DN], mp6)          # touches 0,2 ...
        put(DN, D % (1, 3), piece((0, 50, 301, 151)), MT6[DN], mp6)           # ... and this only through it (one piece over two squares)
        put(DN, "overworld/night/0,3.png", piece((100, 0, 512, 151)), MT6[DN], mp6)
        put(DN, "overworld/night/1,3.png", piece((0, 50, 301, 512)), MT6[DN], mp6)   # the same, but it reaches the unexplored side: none of it
        for sq in ((0, 2), (1, 2)):
            put(DN, "overworld/topo/%d,%d.png" % sq, cut(*sq), MT6[DN], mp6)
        put(DN, "overworld/topo/0,3.png", piece((0, 0, 512, 151)), MT6[DN], mp6)     # the part touching 0,2 reaches the unexplored west side ...
        put(DN, "overworld/topo/1,3.png", piece((0, 50, 301, 151)), MT6[DN], mp6)    # ... so this part of the same piece goes nowhere either
        put(DN, "overworld/biome/0,2.png", cut(0, 2), MT6[DN], mp6)
        put(DN, "overworld/biome/0,3.png", piece((0, 0, 200, 151)), MT6[DN], mp6)    # touches 0,2, reaches -1,3 whose image cannot be read
        put(DN, "overworld/biome/-1,3.png", b"not a png", MT6[DN], mp6)
        put(T2, D % (0, -1), piece(P2, fill=(20, 160, 40, 255)), MT6[T2], mp6)          # its own login world, apart from P1
        put(T3, D % (0, -1), piece((250, 440, 300, 501), fill=(200, 30, 30, 255)), MT6[T3], mp6)   # its own unconfirmed bit right next to P1
        put(T4, D % (0, 3), piece((20, 300, 61, 341), fill=(200, 30, 30, 255)), MT6[T4], mp6)     # its own unconfirmed bit at 0,3
        S6 = {f: ["0,0", "0,2", "1,-1", "1,2"] for f in F6}
        r12 = run(mp6)
        f612 = {s["floor"]: s for s in r12["floors"]}.get(3, {})
        check(sorted(f612.get("folders", [])) == sorted(F6) and {f: sorted(r12["site"].get(f, [])) for f in F6} == S6 and {f: sorted(r12["shown"].get(f, [])) for f in F6} == S6,
              f"v13 fixture: five floor-3 folders, 0,0 0,2 1,-1 1,2 shown by the site's map, nothing else: {r12['shown'].get(DN)}")
        want6, bad6, cut6, part6 = expect(S6, S6, {}, mp6, F6, MT6)
        zd12 = {}
        for i in range(pg.locator("#jmFixDl [data-jmfix]").count()):
            with pg.expect_download(timeout=120000) as dl:
                pg.click(f"#jmFixDl [data-jmfix='{i}']")
            zi = zipfile.ZipFile(io.BytesIO(open(dl.value.path(), "rb").read()))
            zd12.update({k: zi.read(k) for k in zi.namelist()})
        check(sorted(zd12) == sorted(want6) and sorted(r12["names"]) == sorted(want6),
              f"v13: the zip holds exactly the reference's images: extra {sorted(set(zd12) - set(want6))[:3]} missing {sorted(set(want6) - set(zd12))[:3]}")
        diff6 = [k for k in want6 if k in zd12 and Image.open(io.BytesIO(zd12[k])).convert("RGBA").tobytes() != want6[k].tobytes()]
        check(not diff6, f"v13: every image is the reference's, pixel for pixel: {[k[13:] for k in diff6][:4]}")
        g = lambda f, k: Image.open(io.BytesIO(zd12[f + "/overworld/" + k + ".png"])).convert("RGBA") if f + "/overworld/" + k + ".png" in zd12 else None
        dn01 = Image.open(os.path.join(mp6, DN, *(D % (0, -1)).split("/"))).convert("RGBA")
        t1 = g(T1, "day/0,-1")
        p1only = piece(P1)
        check(t1 is not None and t1.tobytes() == p1only.tobytes(),
              "v13: at 0,-1 a folder with nothing there takes the piece touching 0,0 and 1,-1 only: not the login world, not the pieces reaching unexplored sides")
        t2 = g(T2, "day/0,-1")
        check(t2 is not None and t2.tobytes() == Image.alpha_composite(p1only, piece(P2, fill=(20, 160, 40, 255))).tobytes(),
              "v13: a folder with its own login world at 0,-1 keeps it and takes the piece")
        check(g(T3, "day/0,-1") is None and f612.get("cut") == [T3 + " day/0,-1"] and g(T3, "night/0,-1") is not None and cut6 == f612.get("cut"),
              f"v13: a piece that would join a folder's own unconfirmed pixels is not given there, and that image is listed: {f612.get('cut')}")
        check(g(T1, "day/1,3") is not None and g(T1, "day/1,3").tobytes() == piece((0, 50, 301, 151)).tobytes() and g(T1, "day/0,3") is not None,
              "v13: a piece over two unshown squares is given in both, also where it does not touch confirmed map itself")
        check(not any("night/0,3" in k or "night/1,3" in k for k in zd12) and "night/1,3" in r12["part"].get(DN, []),
              "v13: the same piece reaching an unexplored side is given nowhere")
        check(not any("topo/0,3" in k or "topo/1,3" in k for k in zd12) and {"topo/0,3", "topo/1,3"} <= set(r12["part"].get(DN, [])),
              "v13: a piece over two squares is given nowhere when either part reaches an unexplored side")
        check(not any("biome/0,3" in k or "biome/-1,3" in k for k in zd12) and {"biome/0,3", "biome/-1,3"} <= set(r12["part"].get(DN, [])),
              "v13: a side leading to an image that cannot be read is not confirmed")
        check(g(T4, "day/0,3") is None and g(T4, "day/1,3") is not None and "day/0,3" in r12["part"].get(T4, []),
              "v13: a folder with its own unconfirmed copy of a square (not 0,-1) is not changed there")
        check({f: sorted(v) for f, v in r12["part"].items() if v} == {f: sorted(v) for f, v in part6.items() if v} and not bad6,
              f"v13: the images with pieces left out are exactly the reference's: {[(f[-5:], v) for f, v in r12['part'].items() if v]}")
        check(not any("0,-1" in x and x.startswith(DN) for x in zd12) and dn01.tobytes() == Image.open(os.path.join(mp6, DN, *(D % (0, -1)).split("/"))).convert("RGBA").tobytes(),
              "v13: the donor's own 0,-1 is not changed")
        for k, v in zd12.items():
            os.makedirs(os.path.dirname(os.path.join(mp6, *k.split("/"))), exist_ok=True)
            open(os.path.join(mp6, *k.split("/")), "wb").write(v)
        r13 = run(mp6)
        check(r13["names"] == [], f"v13: running again writes nothing: {r13['names'][:3]}")
        # v14 (GPT V13-M1): a folder's own unconfirmed pixels must never become a source on the next run, across squares too.
        # Separate fixture mp7: SR gives; each target has one unconfirmed bit (its own colour) that a repair would confirm:
        # TA (GPT's case) a bit at -1,-1 next to the piece it would take at 0,-1; TB a bit at 0,-1 next to a clear part of its
        # site-shown 0,0 that it would take; TC a bit at 0,-1 reaching 1,-1, a square it lacks and would take (site-shown next
        # run); TM a bit at 2,3 that only the pieces at 1,3 and 0,3 together would join to confirmed map;
        # TK (judged again after one image is left out) a bit B1 that the second piece at 0,-1 would confirm, and a bit B2 that
        # the first piece at 0,-1 holds back (it reaches TK's own -1,-1, which has nothing across) and that the clear part of
        # its 0,0 it would take confirms once 0,-1 is left out; TS a piece at 1,3 touching only a square shown by a small
        # surface piece (not by the site's map): not confirmed, and the full 1,2 it would take makes 1,2 site-shown next run,
        # so that is not given either. Round 2 adds E
        mp7 = os.path.join(tmp, "mp7")
        SR, TA, TB, TC, TM, TK, E7 = ("Triggers_cx00001~src", "Triggers_cx00002~ta", "Triggers_cx00003~tb", "Triggers_cx00004~tc",
                                      "Triggers_cx00005~tm", "Triggers_cx00007~tk", "Triggers_cx00006~new")
        TS = "Triggers_cx00008~ts"
        F7 = [SR, TA, TB, TC, TM, TK, TS]
        MT7 = {SR: T + 50, TA: T, TB: T, TC: T, TM: T, TK: T, TS: T, E7: T}
        BIT = {TA: (11, 22, 33, 255), TB: (44, 55, 66, 255), TC: (77, 88, 99, 255), TM: (111, 122, 133, 255), TK: (150, 10, 200, 255),
               TS: (5, 200, 120, 255)}
        for f in F7:
            for sq in ((0, 0), (1, -1), (0, 2), (1, 2)):
                if f == TC and sq == (1, -1):
                    continue
                im = cut(*sq)
                if f == TB and sq == (0, 0):
                    im.paste((0, 0, 0, 0), (380, 0, 430, 20))   # clear where its bit at 0,-1 touches
                if f == TK and sq == (0, 0):
                    im.paste((0, 0, 0, 0), (200, 0, 230, 20))
                if f == TS and sq == (1, 2):
                    im = cut(1, 2, (0, 448, 64, 512))   # 16 chunks, the same picture as SR's: shown as a small piece
                put(f, D % sq, im, MT7[f], mp7)
        PQ, QQ = (0, 380, 212, 512), (300, 380, 512, 500)
        put(SR, D % (0, -1), piece(PQ, (300, 480, 360, 512)), MT7[SR], mp7)   # both touch 0,0; PQ also -1,-1 (site-shown), as in GPT's case
        put(SR, D % (-1, -1), cut(-1, -1, QQ), MT7[SR], mp7)   # the real map there (48 chunks on the site's map)
        put(SR, D % (0, 3), piece((100, 0, 512, 151)), MT7[SR], mp7)   # touches 0,2 ...
        put(SR, D % (1, 3), piece((0, 50, 512, 151)), MT7[SR], mp7)    # ... on through 1,3 ...
        put(SR, D % (2, 3), piece((0, 80, 60, 140)), MT7[SR], mp7)     # ... to 2,3
        put(TA, D % (-1, -1), piece((510, 505, 512, 507), fill=BIT[TA]), MT7[TA], mp7)
        put(TB, D % (0, -1), piece((400, 510, 403, 512), fill=BIT[TB]), MT7[TB], mp7)
        put(TC, D % (0, -1), piece((480, 500, 512, 512), fill=BIT[TC]), MT7[TC], mp7)
        put(TM, D % (2, 3), piece((0, 60, 2, 62), fill=BIT[TM]), MT7[TM], mp7)
        put(TK, D % (0, -1), piece((298, 490, 300, 492), (212, 505, 215, 512), fill=BIT[TK]), MT7[TK], mp7)   # B1 next to the second piece, B2 next to PQ
        put(TK, D % (-1, -1), piece((5, 5, 7, 7), fill=BIT[TK]), MT7[TK], mp7)   # its own -1,-1: nothing at its east side
        put(TS, D % (1, 3), piece((10, 0, 40, 30), fill=BIT[TS]), MT7[TS], mp7)
        S7 = {f: ["0,0", "0,2", "1,-1", "1,2"] for f in F7}
        S7[SR] = ["-1,-1", "0,0", "0,2", "1,-1", "1,2"]
        S7[TC] = ["0,0", "0,2", "1,2"]
        SITE7 = dict(S7, **{TS: ["0,0", "0,2", "1,-1"]})
        CUT7 = sorted([TA + " day/0,-1", TB + " day/0,0", TC + " day/1,-1", TM + " day/0,3", TM + " day/1,3", TK + " day/0,-1", TK + " day/0,0", TS + " day/1,2"])

        def zipped():
            out = {}
            for i in range(pg.locator("#jmFixDl [data-jmfix]").count()):
                with pg.expect_download(timeout=120000) as dl:
                    pg.click(f"#jmFixDl [data-jmfix='{i}']")
                zi = zipfile.ZipFile(io.BytesIO(open(dl.value.path(), "rb").read()))
                out.update({k: zi.read(k) for k in zi.namelist()})
            return out

        def bits_in(zd, owners=BIT):   # (folder, image) of zip images holding another folder's bit colour
            hit = []
            for k, v in zd.items():
                cols = {c for _, c in Image.open(io.BytesIO(v)).convert("RGBA").getcolors(262144)}
                hit += [(k, o) for o, c in owners.items() if c in cols and not k.startswith(o + "/")]
            return hit

        def place(zd):
            for k, v in zd.items():
                os.makedirs(os.path.dirname(os.path.join(mp7, *k.split("/"))), exist_ok=True)
                open(os.path.join(mp7, *k.split("/")), "wb").write(v)
        r14 = run(mp7)
        f714 = {s["floor"]: s for s in r14["floors"]}.get(3, {})
        check(sorted(f714.get("folders", [])) == sorted(F7) and {f: sorted(r14["shown"].get(f, [])) for f in F7} == S7
              and {f: sorted(r14["site"].get(f, [])) for f in F7} == SITE7,
              f"v14 fixture: five floor-3 folders, shown squares as written: {r14['why']} {[(f[-3:], r14['shown'].get(f)) for f in F7 if sorted(r14['shown'].get(f, [])) != S7[f]]}")
        zd14 = zipped()
        want7, bad7, cut7, part7 = expect(S7, SITE7, {}, mp7, F7, MT7)
        same = lambda zd, want: sorted(zd) == sorted(want) and all(Image.open(io.BytesIO(zd[k])).convert("RGBA").tobytes() == want[k].tobytes() for k in want)
        check(same(zd14, want7) and sorted(cut7) == CUT7 and not bad7 and {f: sorted(v) for f, v in r14["part"].items() if v} == {f: sorted(v) for f, v in part7.items() if v},
              f"v14: the zip, pixel for pixel, the images left out and the unconfirmed images are the reference's: {sorted(cut7)} {sorted(set(zd14) ^ set(want7))[:3]}")
        check(sorted(f714.get("cut") or []) == CUT7,
              f"v14: each image that would confirm a folder's own unconfirmed bit (across a side, through a site-shown square, by a square becoming site-shown, by two images together) is not given and listed: {sorted(f714.get('cut') or [])}")
        check(not bits_in(zd14), f"v14: no folder's unconfirmed bit is given to anyone: {bits_in(zd14)[:3]}")
        check(not any(x.split("/overworld/")[0] + " " + x.split("/overworld/")[1][:-4] in CUT7 for x in zd14),
              "v14: none of those images is in the zip")
        check(TB + "/overworld/day/0,-1.png" in zd14 and TC + "/overworld/day/0,-1.png" in zd14 and TA + "/overworld/day/0,3.png" in zd14
              and TM + "/overworld/day/0,-1.png" in zd14 and TB + "/overworld/day/-1,-1.png" in zd14 and TK + "/overworld/day/0,3.png" in zd14,
              "v14: the same folders still take everything else")
        place(zd14)
        for sq in ((0, 0), (1, -1), (0, 2), (1, 2)):
            put(E7, D % sq, cut(*sq), MT7[E7], mp7)
        r15 = run(mp7)
        f715 = {s["floor"]: s for s in r15["floors"]}.get(3, {})
        zd15 = zipped()
        S7e, SITE7e = dict(S7, **{E7: ["0,0", "0,2", "1,-1", "1,2"]}), dict(SITE7, **{E7: ["0,0", "0,2", "1,-1", "1,2"]})
        want7b, _, cut7b, _ = expect(S7e, SITE7e, {}, mp7, F7 + [E7], MT7)
        check(same(zd15, want7b) and sorted(cut7b) == CUT7, f"v14: round 2 is the reference's too: {sorted(set(zd15) ^ set(want7b))[:3]} {sorted(cut7b)}")
        check(not bits_in(zd15), f"v14: round 2 with a new folder: no folder's unconfirmed bit is given to anyone: {bits_in(zd15)[:3]}")
        check(sorted(f715.get("cut") or []) == CUT7 and "day/-1,-1" in r15["part"].get(TA, [])
              and "day/0,-1" in r15["part"].get(TB, []) and "day/0,-1" in r15["part"].get(TC, []) and "day/2,3" in r15["part"].get(TM, [])
              and "day/0,-1" in r15["part"].get(TK, []) and "day/1,3" in r15["part"].get(TS, []),
              f"v14: round 2: the bits are still unconfirmed and the same images still left out: {sorted(f715.get('cut') or [])}")
        e11 = Image.open(io.BytesIO(zd15[E7 + "/overworld/day/-1,-1.png"])).convert("RGBA") if E7 + "/overworld/day/-1,-1.png" in zd15 else None
        check(e11 is not None and e11.tobytes() == cut(-1, -1, QQ).tobytes() and all(k.startswith(E7 + "/") for k in zd15),
              f"v14: round 2 writes only the new folder's images, and its -1,-1 is the source's piece alone: {[k for k in zd15 if not k.startswith(E7)][:3]}")
        place(zd15)
        r16 = run(mp7)
        check(r16["names"] == [], f"v14: running again writes nothing: {r16['names'][:3]}")
        check(not errs, f"no page errors: {errs[:2]}")
        b.close()
    srv.shutdown()
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("ALL PASSED" if not fails else f"{len(fails)} FAILED")
sys.exit(1 if fails else 0)
