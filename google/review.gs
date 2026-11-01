/**
 * Aincrad 回報審核網頁（Apps Script Web App）
 *
 * 這是「另一個」獨立的 Apps Script 專案，和放 GitHub 金鑰的「Aincrad 回報自動化」分開，
 * 以「存取網頁的使用者」身分執行：審核員用自己的 Google 帳號登入，只有試算表的編輯者能用，
 * 而且只會改「狀態」和「審核備註」兩欄（就是審核員在試算表本來就能改的欄位）。
 * 真正上線（寫到 GitHub）由主程式的 processQueue 每分鐘處理，這個專案碰不到 GitHub 金鑰。
 *
 * 設定步驟寫在 google/SETUP.md「審核網頁」。
 * 這個檔案由 tools/build_review.py 和 google/review.html 合成 google/review.gs，請貼 review.gs。
 */

const SHEET_URL = '';   // ← 貼上「Aincrad 查詢工具・回報審核」試算表的網址（設定資訊分頁第 4 列）

const H = {
  TIME: '時間戳記', TYPE: '回報種類', FLOOR: '樓層', NAME: '名稱', SHOT: '截圖',
  ID: '回報編號', STATUS: '狀態', NOTE: '審核備註', RESULT: '處理結果', PREVIEW: '截圖預覽', SUMMARY: '內容摘要'
};
const SHEET_NAME = '回報';

function sheet_() {
  const m = String(SHEET_URL).match(/\/d\/([\w-]+)/);
  if (!m) throw new Error('還沒設定：請在程式第一行的 SHEET_URL 貼上審核試算表的網址');
  const sh = SpreadsheetApp.openById(m[1]).getSheetByName(SHEET_NAME);
  if (!sh) throw new Error('試算表裡找不到「' + SHEET_NAME + '」分頁');
  return sh;
}

function doGet() {
  return HtmlService.createHtmlOutput(REVIEW_HTML)
    .setTitle('艾恩葛朗特 回報審核')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

/** 所有回報（前端自己分「待審核／已處理」和分類）。 */
function apiList() {
  const me = Session.getActiveUser().getEmail();
  let sh;
  try { sh = sheet_(); } catch (e) {
    return { me: me, error: '打不開審核試算表：' + e.message + '\n\n請確認你是「Aincrad 查詢工具・回報審核」試算表的編輯者。' };
  }
  const vals = sh.getDataRange().getDisplayValues();
  const hdr = vals[0];
  const ix = n => hdr.indexOf(n);
  const skip = Object.keys(H).map(k => H[k]);
  const items = [];
  for (let r = 1; r < vals.length; r++) {
    const v = vals[r];
    const id = v[ix(H.ID)];
    if (!id) continue;
    const fields = [];
    hdr.forEach((h, i) => {
      if (!h || i === 0 || skip.indexOf(h) >= 0) return;
      const x = String(v[i]).trim();
      if (x && x !== '不確定') fields.push([String(h), x]);
    });
    items.push({
      row: r + 1, id: id, time: v[0], type: v[ix(H.TYPE)], floor: v[ix(H.FLOOR)], name: v[ix(H.NAME)],
      fields: fields, shots: (String(v[ix(H.SHOT)]).match(/id=([\w-]+)/g) || []).map(s => s.slice(3)),
      status: v[ix(H.STATUS)], note: v[ix(H.NOTE)], result: v[ix(H.RESULT)]
    });
  }
  return { me: me, items: items };
}

/** 截圖縮圖（以審核員自己的權限讀雲端硬碟，所以截圖資料夾要分享給審核員：主程式的 enableReviewQueue 會做）。 */
function apiShot(fileId, size) {
  const auth = { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() };
  const res = UrlFetchApp.fetch('https://www.googleapis.com/drive/v3/files/' + encodeURIComponent(fileId) + '?fields=thumbnailLink',
    { headers: auth, muteHttpExceptions: true });
  const meta = JSON.parse(res.getContentText() || '{}');
  if (!meta.thumbnailLink) {
    if (res.getResponseCode() === 404 || res.getResponseCode() === 403)
      throw new Error('你還沒有這張截圖的檢視權限。請試算表擁有者在「Aincrad 回報自動化」執行 enableReviewQueue');
    throw new Error('雲端硬碟還在產生縮圖，等幾分鐘再按「重新整理」');
  }
  const r = UrlFetchApp.fetch(meta.thumbnailLink.replace(/=s\d+$/, '=s' + Math.min(Number(size) || 1200, 1600)),
    { headers: auth, muteHttpExceptions: true });
  if (r.getResponseCode() !== 200) throw new Error('縮圖下載失敗（' + r.getResponseCode() + '）');
  return 'data:image/jpeg;base64,' + Utilities.base64Encode(r.getBlob().getAs(MimeType.JPEG).getBytes());
}

/** 核准或退回一筆。只改「狀態」「審核備註」；別人已經處理過就不覆蓋。 */
function apiDecide(row, id, decision, note) {
  if (decision !== '核准' && decision !== '退回') throw new Error('不明的動作');
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const sh = sheet_();
    const hdr = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
    const c = n => hdr.indexOf(n) + 1;
    if (String(sh.getRange(row, c(H.ID)).getValue()) !== String(id)) throw new Error('資料位置變了，請按「重新整理」');
    const cur = String(sh.getRange(row, c(H.STATUS)).getValue());
    if (cur && cur !== '待審核') return { ok: false, msg: id + ' 已經被處理過了（目前狀態：' + cur + '），已重新整理' };
    const who = (Session.getActiveUser().getEmail() || '').split('@')[0];
    const text = '審核：' + (who || '?') + (note ? '｜' + String(note).slice(0, 300) : '');
    sh.getRange(row, c(H.NOTE)).setValue(text);
    sh.getRange(row, c(H.STATUS)).setValue(decision);
    SpreadsheetApp.flush();
    return { ok: true, note: text, msg: decision === '核准' ? id + ' 已核准，約 1 分鐘內自動上線' : id + ' 已退回' };
  } finally {
    lock.releaseLock();
  }
}

/* ===== 以下是網頁畫面（由 google/review.html 產生，不要直接改這裡） ===== */
const REVIEW_HTML = "<!-- Aincrad 回報審核網頁（前端）。tools/build_review.py 會把它塞進 google/review.gs，使用者只要貼 review.gs。\n     本機測試：tests/review_test.py 會用假的 google.script.run 開這個檔案。 -->\n<style>\n:root{--bg:#f4f6f8;--panel:#fff;--panel2:#f0f3f6;--fg:#1d2733;--muted:#5f6c7a;--line:#dde3ea;--accent:#d9701a;--ok:#2f8a5b;--okbg:#e3f4ea;--bad:#c0392b;--badbg:#fbe6e4;--warnbg:#fff4cc;--hi:#7b55c8}\n*{box-sizing:border-box}\nbody{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 \"Noto Sans TC\",\"Microsoft JhengHei\",system-ui,sans-serif}\nbutton,select,textarea{font:inherit;color:inherit}\nheader{position:sticky;top:0;z-index:5;background:var(--panel);border-bottom:1px solid var(--line);padding:10px 16px;display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center}\nheader h1{margin:0;font-size:17px;white-space:nowrap}\nheader .me{color:var(--muted);font-size:12.5px;margin-left:auto;overflow-wrap:anywhere}\n.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;width:100%}\n.chips{display:flex;flex-wrap:wrap;gap:6px}\n.chip{border:1px solid var(--line);background:var(--panel);border-radius:999px;padding:3px 12px;cursor:pointer;white-space:nowrap}\n.chip[aria-pressed=\"true\"]{background:var(--accent);border-color:var(--accent);color:#fff}\n.chip b{font-weight:600;margin-left:4px}\nselect{border:1px solid var(--line);border-radius:6px;padding:4px 8px;background:var(--panel)}\nmain{display:grid;grid-template-columns:minmax(240px,320px) minmax(0,1fr);gap:16px;padding:16px;max-width:1400px;margin:0 auto}\n.queue{display:flex;flex-direction:column;gap:6px;align-self:start;position:sticky;top:120px;max-height:calc(100vh - 136px);overflow:auto}\n.qi{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:2px 8px;align-items:center;text-align:left;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:7px 10px;cursor:pointer}\n.qi[aria-current=\"true\"]{border-color:var(--accent);box-shadow:0 0 0 2px rgba(217,112,26,.25)}\n.qi .ic{font-size:18px;grid-row:span 2}\n.qi .nm{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n.qi .sub{grid-column:2;font-size:12px;color:var(--muted)}\n.qi .tag{grid-row:span 2;font-size:11px}\n.pri{background:var(--hi);color:#fff;border-radius:4px;padding:0 6px;font-size:11px}\n.st{border-radius:4px;padding:0 6px;font-size:11px;white-space:nowrap}\n.st.ok{background:var(--okbg);color:var(--ok)}.st.bad{background:var(--badbg);color:var(--bad)}.st.wait{background:var(--warnbg);color:#7a5a00}\n.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:14px;min-width:0}\n.ctop{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:center}\n.ctop h2{margin:0;font-size:20px;overflow-wrap:anywhere}\n.badge{border:1px solid var(--line);border-radius:999px;padding:1px 10px;font-size:12.5px;background:var(--panel2)}\n.cbody{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:16px}\n.shot{background:#0d1218;border-radius:8px;min-height:240px;display:grid;place-items:center;overflow:hidden;color:#cfd8e3;font-size:13px;text-align:center;padding:4px}\n.shot img{max-width:100%;max-height:62vh;display:block;cursor:zoom-in}\n.thumbs{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}\n.thumbs button{border:2px solid var(--line);border-radius:6px;background:var(--panel2);padding:2px 10px;cursor:pointer}\n.thumbs button[aria-pressed=\"true\"]{border-color:var(--accent)}\ndl{display:grid;grid-template-columns:auto minmax(0,1fr);gap:4px 12px;margin:0;font-size:13.5px}\ndt{color:var(--muted);white-space:nowrap}dd{margin:0;overflow-wrap:anywhere;white-space:pre-line}\n.map{position:relative;border-radius:8px;overflow:hidden;background:#0d1218;aspect-ratio:1;max-width:260px}\n.map img{width:100%;height:100%;display:block}\n.map i{position:absolute;width:14px;height:14px;border-radius:50%;background:#e8a23a;border:3px solid #fff;box-shadow:0 0 0 2px rgba(0,0,0,.5);transform:translate(-50%,-50%)}\n.map span{position:absolute;left:6px;bottom:6px;background:rgba(10,16,22,.8);color:#fff;font-size:11.5px;padding:1px 6px;border-radius:4px}\n.muted{color:var(--muted);font-size:12.5px}\n.act{display:flex;flex-wrap:wrap;gap:10px;align-items:stretch;border-top:1px solid var(--line);padding-top:14px}\n.act textarea{flex:1 1 260px;min-height:44px;border:1px solid var(--line);border-radius:8px;padding:8px;resize:vertical}\n.btn{border:0;border-radius:10px;padding:10px 22px;font-size:16px;font-weight:700;cursor:pointer;color:#fff;min-width:120px}\n.btn.ok{background:var(--ok)}.btn.bad{background:var(--bad)}.btn.ghost{background:var(--panel2);color:var(--fg);border:1px solid var(--line);font-weight:600;min-width:0}\n.btn:disabled{opacity:.5;cursor:default}\n.nav{display:flex;gap:8px;align-items:center;flex-wrap:wrap}\n.result{background:var(--panel2);border-radius:8px;padding:8px 12px;font-size:13px;white-space:pre-line}\n.empty{background:var(--panel);border:1px dashed var(--line);border-radius:12px;padding:32px;text-align:center;color:var(--muted)}\n.toast{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);background:#1d2733;color:#fff;padding:10px 18px;border-radius:999px;font-size:14px;z-index:20;max-width:calc(100% - 32px);text-align:center}\n.err{background:var(--badbg);color:var(--bad);border-radius:8px;padding:12px;white-space:pre-line}\nkbd{font:11.5px ui-monospace,monospace;border:1px solid var(--line);border-bottom-width:2px;border-radius:4px;padding:0 4px;background:var(--panel2)}\n.zoom{position:fixed;inset:0;background:rgba(0,0,0,.88);z-index:30;display:grid;place-items:center;cursor:zoom-out}\n.zoom img{max-width:96vw;max-height:94vh}\n@media (max-width:860px){\n  main{grid-template-columns:minmax(0,1fr);padding:10px}\n  .queue{position:static;max-height:none;flex-direction:row;overflow-x:auto;padding-bottom:4px}\n  .qi{min-width:200px}\n  .cbody{grid-template-columns:minmax(0,1fr)}\n  .btn{flex:1}\n  .keys{display:none}\n}\n</style>\n<header>\n  <h1>艾恩葛朗特 回報審核</h1><span class=\"me\" id=\"me\"></span>\n  <div class=\"bar\">\n    <div class=\"chips\" id=\"fView\"></div>\n    <div class=\"chips\" id=\"fType\"></div>\n    <select id=\"fFloor\" aria-label=\"樓層\"></select>\n    <select id=\"fSort\" aria-label=\"排序\">\n      <option value=\"pri\">優先：怪物、物品、配方、任務追蹤先，再依時間</option>\n      <option value=\"old\">最舊優先</option>\n      <option value=\"new\">最新優先</option>\n    </select>\n    <button class=\"btn ghost\" id=\"reload\" type=\"button\">重新整理</button>\n  </div>\n</header>\n<main id=\"main\"><div class=\"empty\">載入中…</div></main>\n<script>\nvar MAPS={1:{img:\"https://cheng-1001.github.io/ArgoStrategyGuide/floor1.jpg\",x0:70,size:4980},2:{img:\"https://cheng-1001.github.io/ArgoStrategyGuide/floor2.jpg\",x0:-1062,size:2124}};\nvar ICON={\"怪物\":\"🐾\",\"物品\":\"🎒\",\"地點\":\"📍\",\"配方\":\"⚒️\",\"任務追蹤\":\"📜\",\"技能\":\"✨\",\"探索地圖\":\"🗺️\"};\nvar PRI={\"怪物\":0,\"物品\":0,\"配方\":0,\"任務追蹤\":0};\nvar TYPES=[\"怪物\",\"物品\",\"地點\",\"配方\",\"任務追蹤\",\"技能\",\"探索地圖\"];\nvar SITE_TAB={\"物品\":\"items\",\"地點\":\"map\",\"配方\":\"recipes\",\"任務追蹤\":\"quests\",\"技能\":\"classes\",\"探索地圖\":\"map\"};\nvar S={items:[],view:\"wait\",type:\"all\",floor:\"all\",sort:\"pri\",cur:null,shotIdx:0,busy:false};\nvar shotCache={};\nfunction $(id){return document.getElementById(id)}\nfunction esc(s){return String(s==null?\"\":s).replace(/[&<>\"']/g,function(c){return{\"&\":\"&amp;\",\"<\":\"&lt;\",\">\":\"&gt;\",'\"':\"&quot;\",\"'\":\"&#39;\"}[c]})}\nfunction run(fn){var args=[].slice.call(arguments,1);return new Promise(function(ok,no){var r=google.script.run.withSuccessHandler(ok).withFailureHandler(function(e){no(e&&e.message?e:new Error(String(e)))});r[fn].apply(r,args)})}\nfunction toast(t){var d=document.createElement(\"div\");d.className=\"toast\";d.textContent=t;document.body.appendChild(d);setTimeout(function(){d.remove()},3200)}\nfunction stCls(s){return s===\"核准\"?\"ok\":s===\"退回\"?\"bad\":\"wait\"}\nfunction pending(x){return x.status===\"待審核\"||!x.status}\nfunction chips(el,opts,get,set){el.innerHTML=opts.map(function(o){return'<button class=\"chip\" type=\"button\" data-v=\"'+esc(o[0])+'\" aria-pressed=\"'+(get()===o[0])+'\">'+o[1]+'</button>'}).join(\"\");\n  [].forEach.call(el.querySelectorAll(\".chip\"),function(b){b.onclick=function(){set(b.dataset.v);S.cur=null;render()}})}\nfunction filtered(){var a=S.items.filter(function(x){return(S.view===\"wait\"?pending(x):!pending(x))&&(S.type===\"all\"||x.type===S.type)&&(S.floor===\"all\"||String(x.floor)===S.floor)});\n  var t=function(x){return x.row};\n  a.sort(function(x,y){if(S.view===\"done\")return t(y)-t(x);if(S.sort===\"new\")return t(y)-t(x);if(S.sort===\"old\")return t(x)-t(y);\n    var px=PRI[x.type]===0?0:1,py=PRI[y.type]===0?0:1;return px-py||t(x)-t(y)});return a}\nfunction coords(x){for(var i=0;i<x.fields.length;i++){if(/座標/.test(x.fields[i][0])){var m=x.fields[i][1].match(/(-?\\d+)[^\\d-]+(-?\\d+)/);if(m)return{x:+m[1],z:+m[2]}}}return null}\nfunction label(h){return String(h).replace(/^(怪物|物品|地點|配方|任務|技能|探索地圖)・/,\"\")}\nfunction render(){\n  var base=S.items.filter(function(x){return S.view===\"wait\"?pending(x):!pending(x)});\n  var nWait=S.items.filter(pending).length;\n  chips($(\"fView\"),[[\"wait\",\"待審核 <b>\"+nWait+\"</b>\"],[\"done\",\"已處理 <b>\"+(S.items.length-nWait)+\"</b>\"]],function(){return S.view},function(v){S.view=v});\n  var cnt=function(t){return base.filter(function(x){return x.type===t}).length};\n  chips($(\"fType\"),[[\"all\",\"全部 <b>\"+base.length+\"</b>\"]].concat(TYPES.map(function(t){return[t,ICON[t]+\" \"+t+\" <b>\"+cnt(t)+\"</b>\"]})),function(){return S.type},function(v){S.type=v});\n  var fl=[];S.items.forEach(function(x){if(fl.indexOf(String(x.floor))<0)fl.push(String(x.floor))});fl.sort(function(a,b){return a-b});\n  $(\"fFloor\").innerHTML='<option value=\"all\">全部樓層</option>'+fl.map(function(f){return'<option value=\"'+esc(f)+'\"'+(S.floor===f?\" selected\":\"\")+'>第 '+esc(f)+' 層</option>'}).join(\"\");\n  $(\"fSort\").disabled=S.view===\"done\";\n  var a=filtered();\n  if(!a.length){$(\"main\").innerHTML='<div class=\"empty\" style=\"grid-column:1/-1\">'+(S.view===\"wait\"?\"🎉 這個分類沒有待審核的回報。\":\"還沒有處理過的回報。\")+'</div>';return}\n  if(!S.cur||!a.some(function(x){return x.id===S.cur}))S.cur=a[0].id;\n  var q=a.map(function(x){return'<button class=\"qi\" type=\"button\" data-id=\"'+esc(x.id)+'\" aria-current=\"'+(x.id===S.cur)+'\"><span class=\"ic\">'+(ICON[x.type]||\"❔\")+'</span><span class=\"nm\">'+esc(x.name)+'</span>'\n    +(S.view===\"wait\"?(PRI[x.type]===0?'<span class=\"tag pri\">優先</span>':'<span class=\"tag\"></span>'):'<span class=\"tag st '+stCls(x.status)+'\">'+esc(x.status)+'</span>')\n    +'<span class=\"sub\">'+esc(x.id)+'・第 '+esc(x.floor)+' 層・'+esc(String(x.time).slice(0,16))+'</span></button>'}).join(\"\");\n  $(\"main\").innerHTML='<nav class=\"queue\" aria-label=\"回報清單\">'+q+'</nav><section class=\"card\" id=\"card\"></section>';\n  [].forEach.call(document.querySelectorAll(\".qi\"),function(b){b.onclick=function(){S.cur=b.dataset.id;S.shotIdx=0;render()}});\n  renderCard(a);\n}\nfunction renderCard(a){\n  var i=a.findIndex(function(x){return x.id===S.cur}),x=a[i];var c=coords(x),mp=MAPS[x.floor];\n  var dl=x.fields.map(function(f){return\"<dt>\"+esc(label(f[0]))+\"</dt><dd>\"+esc(f[1])+\"</dd>\"}).join(\"\")||'<dt>內容</dt><dd class=\"muted\">玩家只填了名稱</dd>';\n  var map=\"\";\n  if(c&&mp){var px=(c.x-mp.x0)/mp.size*100,pz=(c.z-mp.x0)/mp.size*100;map='<div><div class=\"muted\" style=\"margin-bottom:4px\">位置</div><div class=\"map\"><img src=\"'+mp.img+'\" alt=\"第 '+esc(x.floor)+' 層地圖\"><i style=\"left:'+px+'%;top:'+pz+'%\"></i><span>X '+c.x+' · Z '+c.z+'</span></div></div>'}\n  var wait=pending(x);\n  $(\"card\").innerHTML='<div class=\"ctop\"><span style=\"font-size:24px\">'+(ICON[x.type]||\"❔\")+'</span><h2>'+esc(x.name)+'</h2><span class=\"badge\">'+esc(x.type)+'</span><span class=\"badge\">第 '+esc(x.floor)+' 層</span><span class=\"badge\">'+esc(x.id)+'</span>'\n    +(wait?(PRI[x.type]===0?'<span class=\"pri\">優先</span>':\"\"):'<span class=\"st '+stCls(x.status)+'\">'+esc(x.status)+'</span>')+'<span class=\"muted\">'+esc(x.time)+'</span></div>'\n    +'<div class=\"cbody\"><div><div class=\"shot\" id=\"shot\">'+(x.shots.length?\"截圖載入中…\":\"這筆回報沒有截圖\")+'</div>'\n    +(x.shots.length>1?'<div class=\"thumbs\">'+x.shots.map(function(s,k){return'<button type=\"button\" data-k=\"'+k+'\" aria-pressed=\"'+(k===S.shotIdx)+'\">第 '+(k+1)+' 張</button>'}).join(\"\")+'</div>':\"\")+'</div>'\n    +'<div style=\"display:flex;flex-direction:column;gap:12px;min-width:0\"><dl>'+dl+'</dl>'+map\n    +'<a class=\"muted\" href=\"https://cheng-1001.github.io/ArgoStrategyGuide/#f'+encodeURIComponent(x.floor)+'-'+(SITE_TAB[x.type]||\"monsters\")+'\" target=\"_blank\" rel=\"noopener\">在網站上看目前的資料 ↗</a></div></div>'\n    +(wait?'<div class=\"act\"><textarea id=\"note\" placeholder=\"審核備註（可不填）。退回時寫原因；如果這隻其實是舊怪物改名，寫「舊名：原本的名字」，例如 舊名：Young Spider\"></textarea><button class=\"btn ok\" id=\"bOk\" type=\"button\">✅ 核准</button><button class=\"btn bad\" id=\"bNo\" type=\"button\">❌ 退回</button></div>'\n      :'<div class=\"result\"><b>處理結果</b>\\n'+esc(x.result||(x.status===\"核准\"?\"等待上線（約 1 分鐘內）\":\"—\"))+(x.note?'\\n\\n<b>審核備註</b>\\n'+esc(x.note):\"\")+'</div>')\n    +'<div class=\"nav\"><button class=\"btn ghost\" id=\"bPrev\" type=\"button\"'+(i<=0?\" disabled\":\"\")+'>← 上一筆</button><button class=\"btn ghost\" id=\"bNext\" type=\"button\"'+(i>=a.length-1?\" disabled\":\"\")+'>下一筆 →</button><span class=\"muted\">'+(i+1)+' / '+a.length+'</span>'\n    +(wait?'<span class=\"muted keys\">快捷鍵：<kbd>A</kbd> 核准、<kbd>R</kbd> 退回、<kbd>J</kbd>/<kbd>K</kbd> 下一筆／上一筆</span>':\"\")+'</div>';\n  [].forEach.call(document.querySelectorAll(\".thumbs button\"),function(b){b.onclick=function(){S.shotIdx=+b.dataset.k;renderCard(a)}});\n  $(\"bPrev\").onclick=function(){if(i>0){S.cur=a[i-1].id;S.shotIdx=0;render()}};\n  $(\"bNext\").onclick=function(){if(i<a.length-1){S.cur=a[i+1].id;S.shotIdx=0;render()}};\n  if(wait){$(\"bOk\").onclick=function(){decide(x,\"核准\",a,i)};$(\"bNo\").onclick=function(){decide(x,\"退回\",a,i)}}\n  loadShot(x);\n}\nfunction loadShot(x){var id=x.shots[S.shotIdx];if(!id)return;var el=$(\"shot\");\n  var show=function(src){if($(\"shot\")!==el||x.id!==S.cur)return;el.innerHTML='<img alt=\"'+esc(x.id)+' 第 '+(S.shotIdx+1)+' 張截圖\" src=\"'+src+'\">';el.querySelector(\"img\").onclick=function(){var z=document.createElement(\"div\");z.className=\"zoom\";z.innerHTML='<img alt=\"\" src=\"'+src+'\">';z.onclick=function(){z.remove()};document.body.appendChild(z)}};\n  if(shotCache[id]){show(shotCache[id]);return}\n  run(\"apiShot\",id,1600).then(function(src){shotCache[id]=src;show(src)}).catch(function(e){if($(\"shot\")===el)el.innerHTML='<div>截圖載入失敗：'+esc(e.message)+'<br><a style=\"color:#9cc6ff\" href=\"https://drive.google.com/file/d/'+encodeURIComponent(id)+'/view\" target=\"_blank\" rel=\"noopener\">在雲端硬碟開啟</a></div>'})}\nfunction decide(x,d,a,i){if(S.busy)return;var note=($(\"note\")||{}).value||\"\";\n  if(d===\"退回\"&&!note.trim()&&!confirm(\"沒有填退回原因，確定要退回 \"+x.id+\"？\"))return;\n  S.busy=true;[].forEach.call(document.querySelectorAll(\".act .btn\"),function(b){b.disabled=true});\n  run(\"apiDecide\",x.row,x.id,d,note.trim()).then(function(r){S.busy=false;toast(r.msg);\n    if(r.ok){x.status=d;x.note=r.note||note;var nx=a[i+1]||a[i-1];S.cur=nx&&nx.id!==x.id?nx.id:null;S.shotIdx=0;render()}else load()})\n  .catch(function(e){S.busy=false;toast(\"沒有成功：\"+e.message);render()})}\nfunction load(){$(\"main\").innerHTML='<div class=\"empty\" style=\"grid-column:1/-1\">載入中…</div>';\n  run(\"apiList\").then(function(r){$(\"me\").textContent=r.me?\"審核員：\"+r.me:\"\";\n    if(r.error){$(\"main\").innerHTML='<div class=\"err\" style=\"grid-column:1/-1\">'+esc(r.error)+'</div>';return}\n    S.items=r.items;render()}).catch(function(e){$(\"main\").innerHTML='<div class=\"err\" style=\"grid-column:1/-1\">載入失敗：'+esc(e.message)+'</div>'})}\n$(\"fFloor\").onchange=function(){S.floor=this.value;S.cur=null;render()};\n$(\"fSort\").onchange=function(){S.sort=this.value;S.cur=null;render()};\n$(\"reload\").onclick=load;\ndocument.addEventListener(\"keydown\",function(e){if(/TEXTAREA|SELECT|INPUT/.test(e.target.tagName)||e.ctrlKey||e.metaKey||e.altKey)return;var k=e.key.toLowerCase();\n  if(k===\"a\"&&$(\"bOk\"))$(\"bOk\").click();else if(k===\"r\"&&$(\"bNo\"))$(\"bNo\").click();else if(k===\"j\"&&$(\"bNext\"))$(\"bNext\").click();else if(k===\"k\"&&$(\"bPrev\"))$(\"bPrev\").click()});\nload();\n</script>\n";
