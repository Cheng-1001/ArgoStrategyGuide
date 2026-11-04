/* Explored-map (JourneyMap) status: per floor the last merge date, share of the map frame explored (16x16 chunks)
   and every merged upload; results[report id] = outcome of each player upload. Written by tools/jm_merge.py. */
window.SAO_JM = {
 "1": {
  "date": "2026-11-04",
  "pct": 35.1,
  "log": [
   {
    "report": null,
    "date": "2026-11-01",
    "note": "站長的 JourneyMap（jm-upload-2），探索範圍由 tools/jm_merge.py --init-mask 從切片推算",
    "newChunks": 27712,
    "by": "IICHENGII"
   },
   {
    "report": "R0002",
    "date": "2026-11-01",
    "regions": 52,
    "newChunks": 27,
    "by": "IICHENGII"
   },
   {
    "report": "R0003",
    "date": "2026-11-03",
    "regions": 61,
    "newChunks": 3515
   },
   {
    "report": "R0004",
    "date": "2026-11-03",
    "regions": 61,
    "newChunks": 691
   },
   {
    "report": "R0005",
    "date": "2026-11-04",
    "regions": 62,
    "newChunks": 2198
   }
  ],
  "chunks": 34143
 },
 "results": {
  "R0002": {
   "ok": true,
   "regions": 52,
   "newChunks": 27,
   "overlap": 25894,
   "pct": 28.5,
   "date": "2026-11-01",
   "folders": 2,
   "skipped": 0
  },
  "R0003": {
   "ok": true,
   "regions": 61,
   "newChunks": 3515,
   "overlap": 26441,
   "pct": 32.1,
   "date": "2026-11-03",
   "folders": 2,
   "skipped": 0
  },
  "R0004": {
   "ok": true,
   "regions": 61,
   "newChunks": 691,
   "overlap": 30072,
   "pct": 32.8,
   "date": "2026-11-03",
   "folders": 2,
   "skipped": 0
  },
  "R0005": {
   "ok": true,
   "regions": 62,
   "newChunks": 2198,
   "overlap": 30060,
   "pct": 35.1,
   "date": "2026-11-04",
   "folders": 1,
   "skipped": 0
  }
 }
};
