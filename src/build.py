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
<meta name="description" content="SAO Minecraft Aincrad 樓層查詢工具：地圖、怪物、物品、支線任務。">
<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,-apple-system,"Segoe UI",sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
'''
i = body.index("</style>") + len("</style>")
page = head + body[:i] + "\n</head>\n<body>\n" + body[i:] + "\n</body>\n</html>\n"
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page)
open(os.path.join(ROOT, ".nojekyll"), "w").close()
print("built index.html")
