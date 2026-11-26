"""Peak memory of the 「修復分流地圖」 tool near its size limit (GPT review of v2 806b5b5: the 150 MiB / 1 GiB limits were
not measured). Not part of CI (needs psutil, takes a few minutes); run by hand and keep the output with the review.

Usage (repo root, after src/build.py): python3 tests/jm_fix_mem.py [K]
A floor-3 folder whose four squares hold the site's floor-3 map on the surface and noise (about 1 MB per PNG, the worst
case for PNG size) on 12 more layers, plus K folders holding only the surface: every one of the K gets the 48 noise images,
about K x 50 MB to write (default K = 4, close to JMFIX.TOTAL = 256 MiB). Samples the private bytes of all browser
processes every 50 ms: after the page loads, while the folder is read and merged, and while every zip part is made.
"""
import functools, http.server, os, shutil, sys, tempfile, threading, time
import psutil
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = int(sys.argv[1]) if len(sys.argv) > 1 else 4
MB = 1048576

c = Image.new("RGB", (1792, 1792))
for n in os.listdir(os.path.join(ROOT, "tiles", "f3jm", "3")):
    a, b = map(int, n[:-4].split("_"))
    c.paste(Image.open(os.path.join(ROOT, "tiles", "f3jm", "3", n)), (a * 256, b * 256))
cut = lambda rx, rz: c.crop((rx * 512 + 253, rz * 512 + 79, rx * 512 + 765, rz * 512 + 591)).convert("RGBA")
REGS = [(1, 1), (0, 1), (1, 0), (1, 2)]
LAYERS = ["night", "topo", "biome"] + [str(i) for i in range(9)]
tmp = tempfile.mkdtemp()
try:
    mp = os.path.join(tmp, "mp")
    for f in ["Triggers_95a78a58~76fa~4903~92aa~8a87c523440c"] + [f"Triggers_mem{i:05d}~x" for i in range(K)]:
        for R in REGS:
            p = os.path.join(mp, f, "overworld", "day")
            os.makedirs(p, exist_ok=True)
            cut(*R).save(os.path.join(p, "%d,%d.png" % R))
    for L in LAYERS:
        for R in REGS:
            p = os.path.join(mp, "Triggers_95a78a58~76fa~4903~92aa~8a87c523440c", "overworld", L)
            os.makedirs(p, exist_ok=True)
            Image.merge("RGBA", [Image.effect_noise((512, 512), 90) for _ in range(3)] + [Image.new("L", (512, 512), 255)]).save(os.path.join(p, "%d,%d.png" % R))
    src = sum(os.path.getsize(os.path.join(dp, x)) for dp, _, fn in os.walk(mp) for x in fn)

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    me = psutil.Process()
    samples, phase = [], ["load"]
    run = [True]

    def mem():
        t = 0
        for ch in me.children(recursive=True):
            try:
                mi = ch.memory_info()
                t += getattr(mi, "private", mi.rss)
            except psutil.Error:
                pass
        return t

    def sampler():
        while run[0]:
            samples.append((phase[0], mem()))
            time.sleep(0.05)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1280, "height": 900}, accept_downloads=True)
        threading.Thread(target=sampler, daemon=True).start()
        pg.goto(f"http://127.0.0.1:{srv.server_address[1]}/index.html#report"); pg.wait_for_timeout(1500)
        phase[0] = "merge"
        t0 = time.time()
        pg.set_input_files("#jmFixDir", mp)
        pg.wait_for_function("window.__jmFix", timeout=900000)
        t1 = time.time()
        r = pg.evaluate("window.__jmFix")
        phase[0] = "zip"
        nb = pg.locator("#jmFixDl [data-jmfix]").count()
        zsz = []
        for i in range(nb):
            with pg.expect_download(timeout=600000) as dl:
                pg.click(f"#jmFixDl [data-jmfix='{i}']")
            zsz.append(os.path.getsize(dl.value.path()))
        t2 = time.time()
        phase[0] = "done"
        time.sleep(0.3)
        run[0] = False
        b.close()
    srv.shutdown()
    pk = lambda ph: max((m for q, m in samples if q == ph), default=0)
    base = max((m for q, m in samples if q == "load"), default=0)
    print(f"K={K} folders to fill; source images {src / MB:.1f} MiB")
    print(f"images to write {len(r['names'])}, stop={r['stop']}, zip parts {nb}, zip total {sum(zsz) / MB:.1f} MiB, largest part {max(zsz or [0]) / MB:.1f} MiB")
    print(f"merge {t1 - t0:.1f} s, zip {t2 - t1:.1f} s, {len(samples)} samples")
    print(f"browser private bytes: after load {base / MB:.0f} MiB, peak while merging {pk('merge') / MB:.0f} MiB, peak while zipping {pk('zip') / MB:.0f} MiB")
    print(f"peak above the loaded page: {(max(pk('merge'), pk('zip')) - base) / MB:.0f} MiB")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
