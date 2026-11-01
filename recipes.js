/* Crafting recipes by NPC (key = NPC name in npcs.js).
   items: [officialCatalogueId or null, in-game English name, seconds, [[material, qty], ...], cost in Col ("Free" = 0), rarity]
   Materials use the site's ITEMS id when there is one; other names are shown as written in game.
   rarity (c/b/a/s) is only needed when the item is not in the official catalogue (officialCatalogueId null).
   Bandit / Shark Accessories: owner's in-game screenshots, 2026-11-01.
   "Small Purse" in game = Small Pouch (Petite Bourse); "Shark Carapace" = Shark Shell (Carapace de Requin). */
window.SAO_RECIPES = {
 "Bandit Accessories": {floor: 1, src: "使用者的遊戲截圖（2026-11-01）", items: [
  [1455, "Bandit Coin", 30, [["Small Pouch", 24]], "Free"],
  [2040, "Gloves of the Bandit", 15, [["Small Pouch", 16]], "Free"],
  [1456, "Bandit Hood", 15, [["Small Pouch", 16]], "Free"],
  [1292, "Stolen Amulet", 30, [["Small Pouch", 24]], "Free"]
 ]},
 "Shark Accessories": {floor: 1, src: "使用者的遊戲截圖（2026-11-01）。這四件官網物品圖鑑還沒有收錄", items: [
  [null, "Shark Amulet", 15, [["Shark Shell", 8], ["Birch String", 1]], "30", "c"],
  [null, "Shark Fang", 30, [["Shark Shell", 12], ["Wolf Fangs", 8]], "33", "b"],
  [null, "Bracelet of the Shark", 30, [["Shark Shell", 12], ["Iron Ingot", 1]], "33", "b"],
  [null, "Ring of the Shark", 15, [["Shark Shell", 8]], "30", "c"]
 ]}
};
