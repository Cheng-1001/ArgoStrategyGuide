// Untranslated-name report (2026-11-08): lists every floor-1 name the site shows that players meet in game but that still has
// no official Chinese name (items with game evidence, site materials with a drop/gather/recipe, NPCs, towns, places, monsters, sets).
// Official Chinese names come only from game screenshots (the official site's Chinese pages keep item names in French).
// Usage: start a server on :8765 (python3 -m http.server 8765), then  node tests/zh_gap.js [out.md]
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
  await p.goto('http://localhost:8765/index.html#f1-equip');await p.waitForFunction(()=>typeof window.__zhGap==='function',null,{timeout:20000});
  const r=await p.evaluate(()=>window.__zhGap());await b.close();
  if(errs.length){console.log('PAGE ERRORS',errs);process.exit(1)}
  const by={};r.forEach(x=>(by[x.k]=by[x.k]||[]).push(x));
  const order=['裝備','道具','素材','NPC','城鎮','地點','怪物','套裝'];
  let md=`# 還沒有官方中文名稱的項目（${new Date().toISOString().slice(0,10)}，共 ${r.length} 個）\n\n`;
  md+='只列第 1 層玩家在遊戲裡會遇到的（有遊戲資料、掉落、採集、配方或位置的）。截到中文提示框、屬性視窗、名牌或拍賣場格子就能補上。\n';
  for(const k of order){const L=by[k]||[];if(!L.length)continue;md+=`\n## ${k}（${L.length}）\n\n`;
    L.forEach(x=>{md+=`- ${x.en||x.fr}${x.fr&&x.en&&x.fr!==x.en?`（${x.fr}）`:''}${x.where?` — ${x.where}`:''}\n`})}
  if(process.argv[2])fs.writeFileSync(process.argv[2],md);
  console.log(order.map(k=>`${k} ${(by[k]||[]).length}`).join('・'),'| total',r.length);
})();
