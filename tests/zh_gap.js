// Untranslated-name report (2026-11-08, user: 網站一直有沒翻的，難道我要一個一個檢查).
// Part 1: every floor-1 name the site shows that players meet in game but that still has no official Chinese name
//   (items with game evidence, site materials with a drop/gather/recipe, NPCs, towns, places, monsters, sets) — needs screenshots.
// Part 2: English names written inside Chinese sentences on any panel although an official Chinese name exists
//   (e.g. 「前往 Virelune」「Vallhat 附近」) — fixable on the site right away. Subtitle lines (no Chinese) and 原文 lines are skipped.
// Official Chinese names come only from game screenshots (the official site's Chinese pages keep item names in French).
// Usage: start a server on :8765 (python3 -m http.server 8765), then  node tests/zh_gap.js [out.md]
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(String(e)));
  await p.addInitScript(()=>{try{localStorage.setItem('sao-tour-v1','1')}catch(e){}});
  await p.goto('http://localhost:8765/index.html#f1-equip');await p.waitForFunction(()=>typeof window.__zhGap==='function',null,{timeout:20000});
  const r=await p.evaluate(()=>window.__zhGap());
  const scan=await p.evaluate(()=>{const ids=window.__auditIds(),W=document.createElement('div'),hits={};
    W.style.cssText='position:fixed;left:-10000px;top:0;width:640px';document.body.appendChild(W);
    for(const [t,L] of Object.entries(ids))for(const i of L){let h;try{h=window.__detail(t,i)}catch(e){continue}W.innerHTML=h;
      W.querySelectorAll('.effen,.hfr,.sten,.lore').forEach(x=>x.remove());
      for(const ln of W.innerText.split(/\n/)){const s=ln.trim();if(!/[\u4e00-\u9fff]/.test(s)||s.includes('原文：'))continue;
        const z=window.__zhText(s);if(z===s)continue;const a=s.split(/\s+/),k=s.slice(0,90);
        const key=[...s.matchAll(/[A-Z][A-Za-z'’]+(?: [A-Z][A-Za-z'’]+)*/g)].map(x=>x[0]).filter(x=>window.__zhText('中'+x)!=='中'+x).join('、')||'?';
        (hits[key]=hits[key]||{zh:window.__zhText('中'+key).slice(1),n:0,ex:[]}).n++;if(hits[key].ex.length<3)hits[key].ex.push(t+'|'+i+'：'+k)}}
    return hits});
  await b.close();
  if(errs.length){console.log('PAGE ERRORS',errs);process.exit(1)}
  const by={};r.forEach(x=>(by[x.k]=by[x.k]||[]).push(x));
  const order=['裝備','道具','素材','NPC','城鎮','地點','怪物','任務','套裝'];
  let md=`# 還沒有官方中文名稱的項目（${new Date().toISOString().slice(0,10)}，共 ${r.length} 個）\n\n`;
  md+='只列第 1 層玩家在遊戲裡會遇到的（有遊戲資料、掉落、採集、配方或位置的）。截到中文提示框、屬性視窗、名牌或拍賣場格子就能補上。\n';
  for(const k of order){const L=by[k]||[];if(!L.length)continue;md+=`\n## ${k}（${L.length}）\n\n`;
    L.forEach(x=>{md+=`- ${x.en||x.fr}${x.fr&&x.en&&x.fr!==x.en?`（${x.fr}）`:''}${x.where?` — ${x.where}`:''}\n`})}
  const sh=Object.entries(scan).sort((a,b)=>b[1].n-a[1].n);
  md+=`\n# 句子裡還寫英文、但已經有官方中文的名稱（${sh.length} 個）\n\n`;
  sh.forEach(([e,v])=>{md+=`- ${e} → ${v.zh}（${v.n} 處）例：${v.ex.join(' ／ ')}\n`});
  if(process.argv[2])fs.writeFileSync(process.argv[2],md);
  console.log(order.map(k=>`${k} ${(by[k]||[]).length}`).join('・'),'| total',r.length,'| English-in-sentence names',sh.length,'places',sh.reduce((a,x)=>a+x[1].n,0));
})();
