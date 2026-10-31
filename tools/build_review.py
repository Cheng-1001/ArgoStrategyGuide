"""Bundle the review web app into one paste-able Apps Script file.

google/review_server.js + google/review.html  ->  google/review.gs
(the HTML becomes the REVIEW_HTML string constant). Run after editing either file.
"""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
srv = open(os.path.join(ROOT, "google", "review_server.js"), encoding="utf-8").read()
html = open(os.path.join(ROOT, "google", "review.html"), encoding="utf-8").read()
out = (srv.rstrip() + "\n\n/* ===== 以下是網頁畫面（由 google/review.html 產生，不要直接改這裡） ===== */\n"
       + "const REVIEW_HTML = " + json.dumps(html, ensure_ascii=False) + ";\n")
open(os.path.join(ROOT, "google", "review.gs"), "w", encoding="utf-8").write(out)
print("built google/review.gs", len(out), "chars")
