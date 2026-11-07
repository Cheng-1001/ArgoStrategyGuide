// Site-wide check (2026-11-07, user: 全站檢查): opens every detail panel (monsters, equipment, props, items, recipes, NPCs, quests,
// places, towns, classes) through the window.__detail / __auditIds hooks and reports script errors, 「找不到」/「本站還沒有這個物品的資料」/
// undefined / NaN in the text, links to things that do not exist, images that do not load, and placeholder (emoji) icons.
// Usage: serve the repo (python3 -m http.server 8765) and run  node tests/site_audit.js [http://localhost:8765/]
const BASE=process.argv[2]||'http://localhost:8765/';
const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1280,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.addInitScript(()=>{try{localStorage.setItem('sao-tour-v1','1')}catch(e){}});await p.goto(BASE+'index.html#equip');await p.waitForTimeout(2000);
const R=await p.evaluate(()=>{const ids=window.__auditIds();const all={};for(const [t,L] of Object.entries(ids))for(const i of L)(all[t]=all[t]||new Set()).add(i);
 const out={err:[],flags:{},badgo:{},imgs:new Set(),emoji:{},counts:{}};const W=document.createElement('div');
 const PH=[/本站還沒有這個物品的資料/,/找不到/,/undefined/,/NaN/,/\bnull\b/,/\[object/];
 for(const [t,L] of Object.entries(ids)){out.counts[t]=L.length;for(const i of L){let h;try{h=window.__detail(t,i)}catch(e){out.err.push(t+'|'+i+': '+e.message);continue}
  W.innerHTML=h;const tx=W.innerText||W.textContent;for(const r of PH){if(r.test(tx)){const k=String(r);(out.flags[k]=out.flags[k]||[]).push(t+'|'+i)}}
  W.querySelectorAll('[data-go]').forEach(a=>{const g=a.getAttribute('data-go');const [gt,gi]=g.split(/\|(.+)/);if(!gt||gt==='t'||gt==='d'||gt==='wb')return;if(all[gt]&&!all[gt].has(gi))(out.badgo[g]=out.badgo[g]||[]).push(t+'|'+i)});
  W.querySelectorAll('img').forEach(im=>out.imgs.add(im.getAttribute('src')));
  W.querySelectorAll('.eslot.empty').forEach(e=>{const x=e.textContent.trim();if(x){const lab=(e.closest('li,.phead,.lrow')||e.parentNode).textContent.replace(/\s+/g,' ').slice(0,60);(out.emoji[t+'|'+i]=out.emoji[t+'|'+i]||[]).push(x+' '+lab)}});
 }}out.imgs=[...out.imgs];return out});
const bad=[];for(const s of R.imgs){if(!s||/^data:/.test(s))continue;const r=await p.request.get(BASE+''+s.replace(/^\.\//,'').split('?')[0]).catch(()=>null);if(!r||r.status()!==200)bad.push(s)}
R.badimgs=bad;R.pageerrs=errs;
console.log('counts',JSON.stringify(R.counts));console.log('errors',R.err.length,R.err.slice(0,10));for(const [k,v] of Object.entries(R.flags))console.log('flag',k,v.length,v.slice(0,12).join(' '));console.log('badgo',Object.keys(R.badgo).length,Object.entries(R.badgo).slice(0,15).map(([g,v])=>g+'<-'+v[0]).join(' ; '));console.log('imgs',R.imgs.length,'bad',bad.slice(0,10));console.log('emoji panels',Object.keys(R.emoji).length);console.log('pageerrs',errs);await b.close()})()
