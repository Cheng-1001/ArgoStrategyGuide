"""tools/jm_merge.py on a temporary copy of the map (the real tiles are not touched).

Usage: python3 tests/jm_merge_test.py   (prints ALL PASSED, exits 1 on failure)
Uploads tried: a real-looking one (explored area + a new area), one from another world, broken zips, height layers
(2026-11-06: surface + layer merge, layer-only rejected, region cap).
"""
import io, json, os, shutil, subprocess, sys, tempfile, zipfile
from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = []


def check(c, msg):
    print(("ok   " if c else "FAIL ") + msg)
    if not c:
        fails.append(msg)


tmp = tempfile.mkdtemp()
try:
    os.makedirs(os.path.join(tmp, "tools"))
    shutil.copy(os.path.join(ROOT, "tools", "jm_merge.py"), os.path.join(tmp, "tools"))
    shutil.copytree(os.path.join(ROOT, "tiles", "f1jm"), os.path.join(tmp, "tiles", "f1jm"))
    for f in ("floor1.jpg", "floor1_jm.jpg", "reports.js", "jmmeta.js"):
        shutil.copy(os.path.join(ROOT, f), tmp)
    with open(os.path.join(tmp, "reports.js"), "a", encoding="utf-8"):
        pass
    t = open(os.path.join(tmp, "reports.js"), encoding="utf-8").read()
    t = t.rstrip().rstrip(";").rstrip().rstrip("]") + (',' if t.count("{") else '') + '{"id":"T900","type":"jmap","floor":1,"name":"x","raw":{}}];\n'
    open(os.path.join(tmp, "reports.js"), "w", encoding="utf-8").write(t)

    def canvas():
        cv = Image.new("RGB", (5120, 5120))
        d = os.path.join(tmp, "tiles", "f1jm", "3")
        for n in os.listdir(d):
            c, r = map(int, n[:-4].split("_"))
            cv.paste(Image.open(os.path.join(d, n)), (c * 256, r * 256))
        return cv

    def region(rx, rz, src):
        """a 512x512 JourneyMap-like region cut from src (canvas coords = world - 70)"""
        return src.crop((rx * 512 - 70, rz * 512 - 70, rx * 512 - 70 + 512, rz * 512 - 70 + 512)).convert("RGBA")

    def zipped(files):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            for name, im in files.items():
                if isinstance(im, bytes):
                    z.writestr(name, im)
                else:
                    s = io.BytesIO(); im.save(s, "PNG"); z.writestr(name, s.getvalue())
        p = os.path.join(tmp, f"up{len(os.listdir(tmp))}.zip")
        open(p, "wb").write(b.getvalue())
        return p

    def run(path, *extra):
        r = subprocess.run([sys.executable, "-I", os.path.join(tmp, "tools", "jm_merge.py"), path, *extra], capture_output=True, text=True)
        try:
            return r.returncode, json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            return r.returncode, {"stderr": r.stderr[-500:]}

    mask0 = Image.open(os.path.join(tmp, "tiles", "f1jm", "explored.png")).convert("L")
    cv0 = canvas()
    # 1. town of beginnings region (explored) + a new area in the east (unexplored), coloured like real terrain
    wiki = Image.open(os.path.join(ROOT, "floor1.jpg")).convert("RGB").resize((4980, 4980))
    wiki = ImageEnhance.Brightness(wiki).enhance(1.1)
    new_area = region(8, 4, wiki)
    good = zipped({"day/3,7.png": region(3, 7, cv0), "day/8,4.png": new_area, "day/readme.txt": b"x", "__MACOSX/day/._3,7.png": b"x"})
    code, res = run(good, "--report", "T900", "--date", "2026-11-02")
    check(code == 0 and res.get("ok") and res["regions"] == 2 and res["newChunks"] > 300 and res["overlap"] >= 20,
          f"a real-looking upload merges: explored part matches, new area added ({res})")
    mask1 = Image.open(os.path.join(tmp, "tiles", "f1jm", "explored.png")).convert("L")
    cx, cz = (8 * 512 + 256) // 16, (4 * 512 + 256) // 16
    check(not mask0.getpixel((cx, cz)) and mask1.getpixel((cx, cz)), "the new area is marked explored")
    cv1 = canvas()
    px = (8 * 512 + 256 - 70, 4 * 512 + 256 - 70)
    a, b = cv1.getpixel(px), new_area.getpixel((256, 256))[:3]
    check(sum(abs(x - y) for x, y in zip(a, b)) < 40, "the new area's pixels are on the level 3 tiles")
    meta = open(os.path.join(tmp, "jmmeta.js"), encoding="utf-8").read()
    check('"date": "2026-11-02"' in meta and '"report": "T900"' in meta, "jmmeta.js records the merge")
    mt = json.loads(meta[meta.index("window.SAO_JM =") + 15:].strip().rstrip(";"))
    check(mt["results"]["T900"]["ok"] is True and mt["1"]["log"][-1]["report"] == "T900", "the merge result is stored under results (reports.js untouched)")
    mk = Image.open(os.path.join(tmp, "tiles", "f1jm", "explored.png")).convert("L")
    n_expl = sum(1 for cz in range(4, 316) for cx in range(4, 316) if mk.getpixel((cx, cz)))
    check(mt["1"]["chunks"] == n_expl and sum(e.get("newChunks", 0) for e in mt["1"]["log"]) == n_expl,
          f"jmmeta.js keeps the explored chunk total and every contributor's share adds up to it ({mt['1']['chunks']})")
    # 2. another world: random-ish colours over explored chunks -> rejected, nothing changes
    before = open(os.path.join(tmp, "tiles", "f1jm", "3", "6_15.jpg"), "rb").read()
    n = Image.effect_noise((512, 512), 90)
    other = Image.merge("RGB", (n, n.point(lambda v: 255 - v), n)).convert("RGBA")
    code, res = run(zipped({"3,7.png": other}), "--report", "T901")
    check(code == 2 and not res["ok"] and "對不上" in res["reason"], f"an upload from another world is rejected ({res.get('reason')})")
    check(open(os.path.join(tmp, "tiles", "f1jm", "3", "6_15.jpg"), "rb").read() == before, "a rejected upload changes no tile")
    meta = open(os.path.join(tmp, "jmmeta.js"), encoding="utf-8").read()
    mt = json.loads(meta[meta.index("window.SAO_JM =") + 15:].strip().rstrip(";"))
    check(mt["results"]["T901"]["ok"] is False and "對不上" in mt["results"]["T901"]["reason"] and mt["1"]["log"][-1]["report"] == "T900",
          "a rejection is recorded with its reason and is not in the merge log")
    # 3. a folder that only covers unexplored land cannot be confirmed as floor 1 -> rejected (it used to slip through)
    mask_now = Image.open(os.path.join(tmp, "tiles", "f1jm", "explored.png")).convert("L")
    def explored_in(rx, rz):
        return sum(1 for cz in range(rz * 32, rz * 32 + 32) for cx in range(rx * 32, rx * 32 + 32)
                   if 0 <= cx < 320 and 0 <= cz < 320 and mask_now.getpixel((cx, cz)))
    lone = next((rx, rz) for rz in range(1, 9) for rx in range(1, 9) if explored_in(rx, rz) == 0)
    code, res = run(zipped({"Triggers_x/overworld/day/%d,%d.png" % lone: region(*lone, wiki)}), "--report", "T902")
    check(code == 2 and "重疊" in res["reason"] and "無法確認" in res["reason"], f"a folder with no overlap is not trusted ({res.get('reason')})")
    # 4. the whole journeymap mp folder: floor 1 folder merged, another world skipped, night / cave layers ignored
    cv2 = canvas()
    noise = Image.merge("RGB", (n, n.point(lambda v: 255 - v), n)).convert("RGBA")
    older = region(3, 6, cv2)
    newer = region(3, 6, cv2)
    patch = Image.new("RGBA", (40, 40), (255, 0, 255, 255))
    older.paste(Image.new("RGBA", (40, 40), (0, 255, 255, 255)), (300, 300)); newer.paste(patch, (300, 300))
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        def put(name, im, when):
            s2 = io.BytesIO(); im.save(s2, "PNG")
            z.writestr(zipfile.ZipInfo(name, date_time=when), s2.getvalue())
        put("mp/Triggers_old/overworld/day/3,6.png", older, (2026, 10, 28, 12, 0, 0))
        put("mp/Triggers_new/overworld/day/3,6.png", newer, (2026, 10, 31, 12, 0, 0))
        put("mp/Triggers_new/overworld/night/3,7.png", noise, (2026, 10, 31, 12, 0, 0))
        put("mp/Triggers_new/overworld/0/3,7.png", noise, (2026, 10, 31, 12, 0, 0))
        put("mp/Triggers_floor2/overworld/day/3,7.png", noise, (2026, 10, 30, 12, 0, 0))
    multi = os.path.join(tmp, "multi.zip"); open(multi, "wb").write(b.getvalue())
    before37 = canvas().crop((3 * 512 - 70, 7 * 512 - 70, 3 * 512 + 442, 7 * 512 + 442))
    code, res = run(multi, "--report", "T903")
    check(code == 0 and res.get("folders") == 2 and res.get("skipped") == 1, f"mp folder: both floor 1 folders merged, the other world skipped ({res})")
    cv3 = canvas()
    px = cv3.getpixel((3 * 512 + 320 - 70, 6 * 512 + 320 - 70))
    check(px[0] > 180 and px[1] < 90 and px[2] > 180, f"where two floor 1 folders overlap, the newer one wins ({px})")
    after37 = cv3.crop((3 * 512 - 70, 7 * 512 - 70, 3 * 512 + 442, 7 * 512 + 442))
    from PIL import ImageChops as IC
    check(max(IC.difference(before37, after37).getextrema()[i][1] for i in range(3)) < 40, "night, height layers and the skipped folder leave the surface map alone")
    check(os.path.isdir(os.path.join(tmp, "tiles", "f1jm_c0", "3")), "the height-layer folder 0 of an accepted world goes to its own tiles (tiles/f1jm_c0)")
    # 4b. surface + height layer 1 of the same world (the ink room under the old mill is in layer 1: "y: 24 (1)")
    meta_before = json.loads(open(os.path.join(tmp, "jmmeta.js"), encoding="utf-8").read().split("window.SAO_JM =")[1].strip().rstrip(";"))
    cave = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    cave.paste(Image.new("RGBA", (90, 40), (120, 200, 60, 255)), (230, 70))     # a lit room, the rest unexplored (transparent)
    up = zipped({"mp/Triggers_new/overworld/day/3,6.png": region(3, 6, canvas()),
                 "mp/Triggers_new/overworld/1/5,9.png": cave, "mp/Triggers_new/overworld/topo/5,9.png": noise})
    code, res = run(up, "--report", "T904", "--date", "2026-11-06")
    mt = json.loads(open(os.path.join(tmp, "jmmeta.js"), encoding="utf-8").read().split("window.SAO_JM =")[1].strip().rstrip(";"))
    L1 = mt["1"].get("layers", {}).get("c1", {})
    check(code == 0 and res.get("layers", {}).get("c1", 0) > 0 and L1.get("chunks", 0) > 0 and L1.get("label") == "Y 16～31",
          f"a surface + layer-1 pack merges the layer into its own map ({res.get('layers')}, {L1.get('label')})")
    t3 = (5 * 512 + 250 - 70) // 256, (9 * 512 + 80 - 70) // 256
    check(f"{t3[0]}_{t3[1]}" in L1.get("l3", []) and os.path.exists(os.path.join(tmp, "tiles", "f1jm_c1", "3", f"{t3[0]}_{t3[1]}.jpg")),
          f"jmmeta.js lists the level-3 tiles the layer has ({len(L1.get('l3', []))})")
    lpx = Image.open(os.path.join(tmp, "tiles", "f1jm_c1", "3", f"{t3[0]}_{t3[1]}.jpg")).getpixel(((5 * 512 + 270 - 70) % 256, (9 * 512 + 90 - 70) % 256))
    check(lpx[1] > 150 and lpx[0] < 160, f"the layer's pixels are on its level-3 tile ({lpx})")
    check(mt["1"]["pct"] == meta_before["1"]["pct"] and mt["1"]["chunks"] == meta_before["1"]["chunks"],
          "height-layer data does not change the surface explored share or chunk count")
    check(all(os.path.exists(os.path.join(tmp, "tiles", "f1jm_c1", str(L), "0_0.jpg")) for L in range(3)), "levels 0-2 of the layer are complete")
    # 4c. a world with only height layers cannot be confirmed as floor 1
    code, res = run(zipped({"mp/Triggers_x/overworld/1/5,9.png": cave}), "--report", "T905")
    check(code == 2 and "沒有地面" in res["reason"], f"layer data without surface images is rejected ({res.get('reason')})")
    # 4d. the region cap (cave images are tiny, so a 40 MB part could hold thousands)
    tiny = io.BytesIO(); Image.new("RGBA", (512, 512)).save(tiny, "PNG"); tiny = tiny.getvalue()
    many = {f"mp/W/overworld/1/{i % 60},{i // 60}.png": tiny for i in range(1501)}
    code, res = run(zipped(many))
    check(code == 2 and "1500" in res["reason"], f"more than 1500 images are rejected ({res.get('reason')})")
    # 4e. dungeons (2026-11-06): dimension folders "<uuid>_<name>" next to the floor 1 overworld; instances of one
    # dungeon share one map; accepted only with an accepted floor 1 overworld in the same server folder
    room = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    room.paste(Image.new("RGBA", (120, 60), (200, 120, 40, 255)), (100, 300))
    room2 = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    room2.paste(Image.new("RGBA", (120, 60), (200, 120, 40, 255)), (100, 300))
    room2.paste(Image.new("RGBA", (60, 60), (40, 120, 200, 255)), (300, 100))
    up = zipped({"mp/Triggers_new/overworld/day/3,6.png": region(3, 6, canvas()),
                 "mp/Triggers_new/a57676b0-5d0c-4000-8000-000000000001_geldorack/-1/-1,-1.png": room,
                 "mp/Triggers_new/a57676b0-5d0c-4000-8000-000000000002_geldorack/-1/-1,-1.png": room2,
                 "mp/Triggers_new/a57676b0-5d0c-4000-8000-000000000002_geldorack/day/-1,-1.png": Image.new("RGBA", (512, 512)),
                 "mp/Triggers_new/ca72d386-5d0c-4000-8000-000000000001_labyrinthe/-3/0,0.png": room,
                 "mp/Triggers_new/a57676b0-5d0c-4000-8000-000000000009_backrooms/5/0,0.png": room,
                 "mp/Triggers_new/overworld/-398/3,6.png": room,
                 "mp/Triggers_other/66ea2dea-5d0c-4000-8000-000000000003_xalzirith/0/0,0.png": room})
    code, res = run(up, "--report", "T906", "--date", "2026-11-06")
    mt = json.loads(open(os.path.join(tmp, "jmmeta.js"), encoding="utf-8").read().split("window.SAO_JM =")[1].strip().rstrip(";"))
    G = mt.get("dg", {}).get("geldorack", {})
    check(code == 0 and set(res.get("dungeons", {})) == {"geldorack", "labyrinthe"} and res["dungeons"]["geldorack"] > 0,
          f"dungeon instances next to an accepted floor 1 overworld are merged ({res.get('dungeons')})")
    check(any("backrooms" in w for w in res.get("skippedWhy", [])) and any("xalzirith" in w.lower() or "Triggers_other" in w for w in res.get("skippedWhy", [])),
          f"an unknown dungeon name and a dungeon without a floor 1 overworld beside it are skipped ({res.get('skippedWhy')})")
    check("c-398" not in mt["1"].get("layers", {}) and not os.path.isdir(os.path.join(tmp, "tiles", "f1jm_c-398")), "impossible height folders (-398) are ignored")
    check(G.get("frame", {}).get("x0") == -512 and G.get("frame", {}).get("full") == 2048 and G.get("best") == "c-1"
          and G["layers"]["c-1"]["l3"] and G["layers"]["c-1"]["l3"][0].startswith("-") and G.get("bounds", [0])[0] < 0,
          f"the dungeon frame follows its data, negative coordinates included ({G.get('frame')}, {G.get('bounds')}, best {G.get('best')})")
    gd = os.path.join(tmp, "tiles", "dg", "geldorack")
    tp = os.path.join(gd, "c-1", "3", "-1_-2.jpg")      # room2's blue square: block (-212, -412) -> tile (-1, -2), pixel (44, 100)
    t2 = Image.open(tp).getpixel((54, 110)) if os.path.exists(tp) else None
    check(t2 is not None and t2[2] > 150 and os.path.exists(os.path.join(gd, "overview.jpg")) and all(os.path.isdir(os.path.join(gd, "c-1", str(L))) for L in range(3)),
          f"both instances end up on one map, with levels 0-2 and an overview ({t2})")
    # a later instance whose colours disagree with what the site has is skipped
    wrong = Image.new("RGBA", (512, 512), (0, 0, 0, 0)); wrong.paste(Image.new("RGBA", (120, 60), (20, 240, 240, 255)), (100, 300))
    code, res = run(zipped({"mp/Triggers_new/overworld/day/3,6.png": region(3, 6, canvas()),
                            "mp/Triggers_new/a57676b0-5d0c-4000-8000-000000000003_geldorack/-1/-1,-1.png": wrong}), "--report", "T907")
    check(code == 0 and "geldorack" not in res.get("dungeons", {}) and any("顏色對不上" in w for w in res.get("skippedWhy", [])),
          f"a dungeon instance that does not match the site's map of it is skipped ({res.get('skippedWhy')})")
    # 5. broken uploads
    code, res = run(zipped({"notes.txt": b"hello"}))
    check(code == 2 and "沒有 JourneyMap" in res["reason"], "a zip without map images is rejected")
    code, res = run(zipped({"3,7.png": Image.new("RGBA", (100, 100))}))
    check(code == 2 and "512x512" in res["reason"], "a wrong-size image is rejected")
    code, res = run(zipped({"40,40.png": region(3, 7, cv0)}))
    check(code == 2 and "範圍外" in res["reason"], "regions outside floor 1 are rejected")
    bad = os.path.join(tmp, "bad.zip"); open(bad, "wb").write(b"not a zip")
    code, res = run(bad)
    check(code == 2 and "zip" in res["reason"], "a file that is not a zip is rejected")
    # 6. floors 2 and 3 (2026-11-12): a copy with all three explored maps; each world goes to the floor its colours match,
    # a floor-3 folder's stray floor-2 region is dropped, non-overworld folders (boss-room instances) and the hub are not
    # taken for floors 2 / 3, and floor 1 is not touched
    import hashlib
    t2 = tempfile.mkdtemp()
    os.makedirs(os.path.join(t2, "tools"))
    shutil.copy(os.path.join(ROOT, "tools", "jm_merge.py"), os.path.join(t2, "tools"))
    for f in ("f1jm", "f2jm", "f3jm"):
        shutil.copytree(os.path.join(ROOT, "tiles", f), os.path.join(t2, "tiles", f))
    for f in ("floor1.jpg", "floor1_jm.jpg", "floor2.jpg", "floor3.jpg", "jmmeta.js"):
        shutil.copy(os.path.join(ROOT, f), t2)

    def fcanvas(f, full, x0, z0):
        c = Image.new("RGB", (full, full))
        for n in os.listdir(os.path.join(t2, "tiles", f"f{f}jm", "3")):
            a, b = map(int, n[:-4].split("_"))
            c.paste(Image.open(os.path.join(t2, "tiles", f"f{f}jm", "3", n)), (a * 256, b * 256))
        m = Image.open(os.path.join(t2, "tiles", f"f{f}jm", "explored.png")).convert("L")
        def ex(rx, rz):
            return sum(1 for cz in range(rz * 32, rz * 32 + 32) for cx in range(rx * 32, rx * 32 + 32)
                       if 0 <= cx - x0 // 16 < m.width and 0 <= cz - z0 // 16 < m.height and m.getpixel((cx - x0 // 16, cz - z0 // 16)))
        return (lambda rx, rz: c.crop((rx * 512 - x0, rz * 512 - z0, rx * 512 - x0 + 512, rz * 512 - z0 + 512)).convert("RGBA")), ex

    def fhash(d):
        h = hashlib.sha256()
        for dp, _, fs in sorted(os.walk(d)):
            for n in sorted(fs):
                h.update(open(os.path.join(dp, n), "rb").read())
        return h.hexdigest()
    c2, e2 = fcanvas(2, 2304, -1062, -1062)
    c3, e3 = fcanvas(3, 1792, -253, -79)
    r2 = max((e2(rx, rz), rx, rz) for rx in range(-3, 2) for rz in range(-3, 2))[1:]
    r3 = max((e3(rx, rz), rx, rz) for rx in range(-1, 3) for rz in range(-1, 4))[1:]
    stray = next(((rx, rz) for rx in range(-1, 3) for rz in range(-1, 3) if e3(rx, rz) == 0 and e2(rx, rz) > 100 and (rx, rz) != r3), None)
    files = {f"S/Triggers_f2/overworld/day/{r2[0]},{r2[1]}.png": c2(*r2), f"S/Triggers_f3/overworld/day/{r3[0]},{r3[1]}.png": c3(*r3),
             f"S/Triggers_inst/gorge_x/day/{r2[0]},{r2[1]}.png": c2(*r2), "S/Triggers/overworld/day/0,0.png": noise}
    if stray:
        files[f"S/Triggers_f3/overworld/day/{stray[0]},{stray[1]}.png"] = c2(*stray)
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for n, im in files.items():
            q = io.BytesIO(); im.save(q, "PNG"); z.writestr(n, q.getvalue())
    zp = os.path.join(t2, "f23.zip"); open(zp, "wb").write(b.getvalue())
    h1 = fhash(os.path.join(t2, "tiles", "f1jm"))
    r = subprocess.run([sys.executable, "-I", os.path.join(t2, "tools", "jm_merge.py"), zp, "--report", "T950"], capture_output=True, text=True)
    res = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"stderr": r.stderr[-300:]}
    why = " ".join(res.get("skippedWhy", []))
    check(r.returncode == 0 and set(res.get("floors", {})) == {"2", "3"} and res.get("folders") == 2,
          f"floor-2 and floor-3 worlds each go to their own floor ({res.get('floors')}, folders {res.get('folders')})")
    check("不是 overworld" in why and "Triggers：" in why, f"a boss-room instance and the hub are not taken ({why[:200]})")
    if stray:   # the stray region went to floor 2 (where it matches), not onto the floor-3 map
        m3 = Image.open(os.path.join(t2, "tiles", "f3jm", "explored.png")).convert("L")
        lit = [(cx, cz) for cz in range(stray[1] * 32, stray[1] * 32 + 32) for cx in range(stray[0] * 32, stray[0] * 32 + 32)
               if 0 <= cx + 16 < m3.width and 0 <= cz + 5 < m3.height and m3.getpixel((cx + 16, cz + 5))]
    check(stray is None or not lit, f"a floor-2 region inside the floor-3 folder is not put on the floor-3 map ({stray})")
    check(fhash(os.path.join(t2, "tiles", "f1jm")) == h1, "floor 1's explored map is not touched")
    shutil.rmtree(t2, ignore_errors=True)
    # 7. automatic floors (2026-11-12): a known server folder (world id) is its floor even with little overlap; a never-seen
    # "overworld" folder becomes the one open floor without a map (frame from its first upload, id remembered); it waits
    # (exit 3) when two floors could be it; a zip without the packer's folder list is not a new floor; a Fractured Underworld folder is never a floor
    import random

    def setup(extra_cfg):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "tools"))
        src = open(os.path.join(ROOT, "tools", "jm_merge.py"), encoding="utf-8").read()
        src = src.replace('3: dict(x0=-253, z0=-79, size=1700, full=1792, base="floor3.jpg", prev=None)}',
                          '3: dict(x0=-253, z0=-79, size=1700, full=1792, base="floor3.jpg", prev=None), ' + extra_cfg + '}')
        open(os.path.join(d, "tools", "jm_merge.py"), "w", encoding="utf-8").write(src)
        for f in ("f1jm", "f2jm", "f3jm"):
            shutil.copytree(os.path.join(ROOT, "tiles", f), os.path.join(d, "tiles", f))
        for f in ("floor1.jpg", "floor1_jm.jpg", "floor2.jpg", "floor3.jpg", "jmmeta.js"):
            shutil.copy(os.path.join(ROOT, f), d)
        return d

    def terrain(seed):
        rnd = random.Random(seed); im = Image.new("RGBA", (512, 512))
        for y in range(0, 512, 16):
            for x in range(0, 512, 16):
                im.paste((rnd.randrange(40, 200), rnd.randrange(40, 200), rnd.randrange(40, 200), 255), (x, y, x + 16, y + 16))
        return im

    def zp(d, files, man):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as z:
            for n, im in files.items():
                q = io.BytesIO(); im.save(q, "PNG"); z.writestr(n, q.getvalue())
            if man is not None:
                z.writestr("sao_pack.json", json.dumps({"v": 1, "worlds": man}))
        p = os.path.join(d, f"u{len(os.listdir(d))}.zip"); open(p, "wb").write(b.getvalue())
        return p

    def go(d, path, rep):
        r = subprocess.run([sys.executable, "-I", os.path.join(d, "tools", "jm_merge.py"), path, "--report", rep], capture_output=True, text=True)
        return r.returncode, (json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"stderr": r.stderr[-400:]})

    def meta(d):
        t = open(os.path.join(d, "jmmeta.js"), encoding="utf-8").read()
        return json.loads(t[t.index("window.SAO_JM =") + 15:].strip().rstrip(";"))

    NF = '4: dict(x0=None, z0=None, size=None, full=None, base=None, prev=None)'
    d = setup(NF)
    W = "mp/Triggers_aaaa1111~new/overworld"
    files = {f"{W}/day/{rx},{rz}.png": terrain(rx * 7 + rz) for rx in (8, 9) for rz in (8, 9)}
    code, res = go(d, zp(d, files, {W: {"siblings": ["overworld", "1234abcd-5d0c-4000-8000-000000000001_djnew"]}}), "T960")
    m = meta(d)
    check(code == 0 and res.get("newFloors") == [4] and m.get("ids", {}).get("Triggers_aaaa1111~new") == 4 and "4" in m.get("frames", {})
          and os.path.exists(os.path.join(d, "tiles", "f4jm", "explored.png")),
          f"a never-seen overworld becomes the one open floor without a map, by itself ({code} {res.get('newFloors')} {res.get('reason', '')[:80]})")
    fr = m.get("frames", {}).get("4", {})
    check(fr and fr["x0"] <= 8 * 512 and fr["x0"] + fr["size"] >= 10 * 512, f"its frame covers the first upload ({fr})")
    # the next upload from the same server folder, somewhere new, needs no overlap: the folder is known now
    code, res = go(d, zp(d, {f"{W}/day/12,8.png": terrain(99)}, {W: {"siblings": ["overworld"]}}), "T961")
    check(code == 0 and set(res.get("floors", {"4": 0}) or {"4": 0}) <= {"4"} and res.get("newChunks", 0) > 0,
          f"a later upload of that folder with no overlap still goes to floor 4 ({code} {res.get('reason', '')[:80]})")
    # no folder list in the zip: wait
    W2 = "mp/Triggers_bbbb2222~x/overworld"
    code, res = go(d, zp(d, {f"{W2}/day/1,1.png": terrain(5)}, None), "T962")
    check(code == 2 and not res.get("held"), f"a zip without the packer's folder list is not taken as a new floor ({code})")
    # Fractured Underworld server folder: never a floor
    W3 = "mp/Triggers_cccc3333~uw/overworld"
    code, res = go(d, zp(d, {f"{W3}/day/1,1.png": terrain(6)}, {W3: {"siblings": ["island_player_728a3c30", "overworld"]}}), "T963")
    check(code == 2 and not meta(d).get("ids", {}).get("Triggers_cccc3333~uw"), f"an overworld beside island_player_… is not a floor ({code})")
    # every open floor has a map now: a further unknown folder waits for the site to open a floor
    code, res = go(d, zp(d, {f"{W2}/day/1,1.png": terrain(5)}, {W2: {"siblings": ["overworld"]}}), "T964")
    check(code == 3 and "還沒有的樓層" in res.get("reason", ""), f"no open floor left: it waits ({code} {res.get('reason', '')[:60]})")
    shutil.rmtree(d, ignore_errors=True)
    # two open floors without a map: waits, unless a dungeon word tells them apart
    d = setup(NF + ', 5: dict(x0=None, z0=None, size=None, full=None, base=None, prev=None)')
    code, res = go(d, zp(d, files, {W: {"siblings": ["overworld"]}}), "T965")
    check(code == 3 and "分不出" in res.get("reason", ""), f"two candidate floors: it waits ({code} {res.get('reason', '')[:60]})")
    shutil.rmtree(d, ignore_errors=True)
    # floor 2's own server folder (remembered id) with a region the site has not explored: taken with no overlap
    d = setup(NF)
    m2 = Image.open(os.path.join(d, "tiles", "f2jm", "explored.png")).convert("L")
    def lit2(rx, rz):
        return sum(1 for cz in range(rz * 32, rz * 32 + 32) for cx in range(rx * 32, rx * 32 + 32)
                   if 0 <= cx + 67 < m2.width and 0 <= cz + 67 < m2.height and m2.getpixel((cx + 67, cz + 67)))
    blank = next(((rx, rz) for rx in range(-2, 2) for rz in range(-2, 2) if lit2(rx, rz) == 0), None)
    if blank:
        W4 = "mp/Triggers_ba411067~7be9~4787~a9dc~da5c74995cb4/overworld"
        code, res = go(d, zp(d, {f"{W4}/day/{blank[0]},{blank[1]}.png": terrain(11)}, {W4: {"siblings": ["overworld"]}}), "T966")
        check(code == 0 and "2" in (res.get("floors") or {}), f"floor 2's known server folder is taken without overlap ({code} {res.get('reason', '')[:80]})")
    else:
        check(True, "floor 2 has no unexplored region near the centre (known-id check skipped)")
    check(fhash(os.path.join(d, "tiles", "f1jm")) == fhash(os.path.join(ROOT, "tiles", "f1jm")), "floor 1 is not touched by any of this")
    shutil.rmtree(d, ignore_errors=True)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
