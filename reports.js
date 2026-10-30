/* Accepted player reports (one entry per accepted GitHub issue in Cheng-1001/ArgoStrategyGuide).
   type: "monster" | "item" | "place" | "other"
   floor: floor number; name: English name as in the game
   level: monster level (monsters have exactly one level), x / z: coordinates from a field screenshot
   codexNo / region / desc / drops: read from an in-game Codex screenshot; drops replace the wiki drop list,
     and drops whose item is not unlocked in the Codex use the name "???"
   img: local copy of the screenshot (reports/<issue>.jpg); issue: issue number; date: accepted date
   summary: one-line Chinese summary of what was added to the tool */
window.SAO_REPORTS = [
  { type: "monster", floor: 1, name: "Albal", codexNo: "#006", region: "Forêts du 1er Palier",
    desc: "A lone wolf with icy silver eyes. Its passing leaves mist and silence.",
    drops: [["Wolf Fangs", 100], ["Wolf Fur", 100], ["Albal's Fangs", 35], ["???", 3]],
    img: "reports/1.jpg", issue: 1, date: "2026-10-30",
    summary: "圖鑑：掉落機率更新（Wolf Fangs 70%→100%、Albal's Fangs 20%→35%），另有一種未解鎖掉落物 3%，補上描述" }
];
