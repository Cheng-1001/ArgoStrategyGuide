/* Accepted player reports. The Google Apps Script appends to this file automatically; keep it as
   "window.SAO_REPORTS = <JSON array>;" so the script can read and rewrite it.
   Form reports carry "raw" (question title -> answer); index.html turns raw answers into fields.
   Older entries (#issue) were added by hand with the fields already filled in. */
window.SAO_REPORTS = [
 {
  "type": "monster",
  "floor": 1,
  "name": "Albal",
  "codexNo": "#006",
  "region": "Forêts du 1er Palier",
  "desc": "A lone wolf with icy silver eyes. Its passing leaves mist and silence.",
  "drops": [
   [
    "Wolf Fangs",
    100
   ],
   [
    "Wolf Fur",
    100
   ],
   [
    "Albal's Fangs",
    35
   ],
   [
    "???",
    3
   ]
  ],
  "img": "reports/1.jpg",
  "issue": 1,
  "date": "2026-10-30",
  "summary": "圖鑑：掉落機率更新（Wolf Fangs 70%→100%、Albal's Fangs 20%→35%），另有一種未解鎖掉落物 3%，補上描述"
 }
];
