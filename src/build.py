"""Build index.html (repo root, served by GitHub Pages) from src/index.html.

src/index.html is the editable page. It has no <!doctype>/<head> because it started as a
Claude artifact (the artifact host adds the skeleton). This script adds the skeleton and moves
everything up to the first </style> into <head>.

Usage (from the repo root):  python3 src/build.py
Data files (data.js, data23.js, bosses.js, reports.js, hints.js) and images live in the repo
root and are edited there directly; this script does not touch them.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
body = open(os.path.join(ROOT, "src", "index.html"), encoding="utf-8").read()
head = '''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="阿爾戈的攻略本：SAO Minecraft 艾恩葛朗特（Aincrad）攻略，地圖、怪物、裝備、配方、任務、地下城、職業技能、世界王。">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,"Segoe UI",sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
'''
i = body.index("</style>") + len("</style>")
page = head + body[:i] + "\n</head>\n<body>\n" + body[i:] + "\n</body>\n</html>\n"
# cache busting: each local script gets ?v=<content hash>, so a phone that still has an old copy of a data file
# (GitHub Pages lets browsers keep files 10 minutes) loads the new one as soon as it gets the new page
import re, hashlib
def _ver(m):
    f = os.path.join(ROOT, m.group(1))
    if not os.path.isfile(f): return m.group(0)
    return '<script src="%s?v=%s"' % (m.group(1), hashlib.md5(open(f, "rb").read()).hexdigest()[:8])
page = re.sub(r'<script src="([\w.-]+\.js)"', _ver, page)
# build id: the page checks it against the live copy (fetched without cache) and offers a reload when they differ
build = hashlib.md5(page.encode("utf-8")).hexdigest()[:10]
page = page.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="sao-build" content="%s">' % build, 1)
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)
open(os.path.join(ROOT, ".nojekyll"), "w").close()
print("built index.html")
