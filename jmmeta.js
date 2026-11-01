/* Explored-map (JourneyMap) status: per floor the last merge date, share of the map frame explored (16x16 chunks)
   and every merged upload; results[report id] = outcome of each player upload. Written by tools/jm_merge.py. */
window.SAO_JM = {
 "1": {
  "date": "2026-11-01",
  "pct": 28.5,
  "log": [
   {
    "report": null,
    "date": "2026-11-01",
    "note": "站長的 JourneyMap（jm-upload-2），探索範圍由 tools/jm_merge.py --init-mask 從切片推算",
    "newChunks": 27712
   },
   {
    "report": "R0002",
    "date": "2026-11-01",
    "regions": 52,
    "newChunks": 27,
    "by": "站長"
   }
  ],
  "chunks": 27739
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
  }
 }
};
