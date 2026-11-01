"""tools/jm_merge.py on a temporary copy of the map (the real tiles are not touched).

Usage: python3 tests/jm_merge_test.py   (prints ALL PASSED, exits 1 on failure)
Uploads tried: a real-looking one (explored area + a new area), one from another world, broken zips.
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
    for f in ("floor1.jpg", "floor1_jm.jpg", "reports.js"):
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
    check(max(IC.difference(before37, after37).getextrema()[i][1] for i in range(3)) < 40, "night / cave layers and the skipped folder change nothing")
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
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("\n" + ("ALL PASSED" if not fails else f"{len(fails)} FAILED"))
sys.exit(1 if fails else 0)
