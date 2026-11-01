// Node test for the Apps Script server code with a fake spreadsheet (no Google services needed).
// Usage: node tests/apps_script_test.js   (prints ALL PASSED, exits 1 on failure)
const fs = require('fs'), vm = require('vm'), path = require('path');
const ROOT = path.dirname(__dirname);
let fails = 0; const check = (c, m) => { console.log((c ? 'ok   ' : 'FAIL ') + m); if (!c) fails++; };

function fakeSheet(rows) {
  const g = { rows };
  const range = (r, c, nr = 1, nc = 1) => ({
    getValue: () => (g.rows[r - 1] || [])[c - 1] ?? '',
    getValues: () => Array.from({ length: nr }, (_, i) => Array.from({ length: nc }, (_, j) => (g.rows[r - 1 + i] || [])[c - 1 + j] ?? '')),
    setValue: v => { while (g.rows.length < r) g.rows.push([]); g.rows[r - 1][c - 1] = v; return range(r, c); },
  });
  return { g, getRange: range, getLastColumn: () => g.rows[0].length, getLastRow: () => g.rows.length,
    getDataRange: () => ({ getDisplayValues: () => g.rows.map(r => g.rows[0].map((_, j) => String(r[j] ?? ''))) }) };
}
const HDR = ['時間戳記', '樓層', '名稱', '回報種類', '怪物・等級', '怪物・座標 x, z', '截圖', '回報編號', '截圖預覽', '內容摘要', '狀態', '審核備註', '處理結果'];
const rows = () => [HDR,
  ['2026/11/01 0:20', '1', 'Young Spider', '怪物', '3', '', 'https://drive.google.com/open?id=AAA', 'R0001', '', '', '核准', '', '已上線 x'],
  ['2026/11/01 1:00', '1', 'Albal', '怪物', '8', '2513, 3722', 'https://drive.google.com/open?id=BBB, https://drive.google.com/open?id=CCC', 'R0002', '', '', '待審核', '', ''],
  ['2026/11/01 1:05', '2', 'Hidden Well', '地點', '', '', 'https://drive.google.com/open?id=DDD', 'R0003', '', '', '待審核', '', '']];

// ---- review web app server ----
{
  const sh = fakeSheet(rows());
  const ctx = { console, Session: { getActiveUser: () => ({ getEmail: () => 'rev@gmail.com' }) },
    SpreadsheetApp: { openById: () => ({ getSheetByName: () => sh }), flush() {} },
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) } };
  vm.createContext(ctx);
  const src = fs.readFileSync(path.join(ROOT, 'google', 'review.gs'), 'utf8')
    .replace("const SHEET_URL = '';", "const SHEET_URL = 'https://docs.google.com/spreadsheets/d/TEST123/edit';");
  vm.runInContext(src + '\nthis.apiList=apiList;this.apiDecide=apiDecide;', ctx);
  const L = ctx.apiList();
  check(L.me === 'rev@gmail.com' && L.items.length === 3, 'apiList returns every report and the reviewer');
  const a = L.items.find(x => x.id === 'R0002');
  check(a.row === 3 && a.type === '怪物' && a.floor === '1' && a.shots.join() === 'BBB,CCC', 'apiList reads row, type, floor and screenshot ids');
  check(JSON.stringify(a.fields) === JSON.stringify([['怪物・等級', '8'], ['怪物・座標 x, z', '2513, 3722']]), 'apiList keeps only the answer fields');
  const r = ctx.apiDecide(3, 'R0002', '核准', '清楚');
  check(r.ok && sh.g.rows[2][10] === '核准' && sh.g.rows[2][11] === '審核：rev｜清楚' && sh.g.rows[2][12] === '', 'apiDecide sets status and note only');
  const r2 = ctx.apiDecide(3, 'R0002', '退回', '');
  check(!r2.ok && sh.g.rows[2][10] === '核准', 'apiDecide does not overwrite a report someone already handled');
  let threw = false; try { ctx.apiDecide(4, 'R0099', '核准', ''); } catch (e) { threw = /位置變了/.test(e.message); }
  check(threw, 'apiDecide refuses when the row no longer holds that report');
  threw = false; try { ctx.apiDecide(4, 'R0003', '刪除', ''); } catch (e) { threw = true; }
  check(threw, 'apiDecide only accepts approve or reject');
}

// ---- review web app with the new per-type floor / name questions ----
{
  const H3 = ['時間戳記', '樓層', '名稱', '回報種類', '物品・樓層', '物品・名稱', '物品・來源', '技能・名稱', '截圖', '回報編號', '狀態', '審核備註', '處理結果'];
  const sh = fakeSheet([H3,
    ['2026/11/02 9:10', '', '', '物品', '', 'Health Potion I', 'Shop', 'https://drive.google.com/open?id=Q1', 'R0010', '待審核', '', ''],
    ['2026/11/02 9:20', '', '', '技能', '', '', '', 'https://drive.google.com/open?id=Q2', 'R0011', '待審核', '', '']]);
  sh.g.rows[2][7] = 'Combinaison Brutale';
  const ctx = { console, Session: { getActiveUser: () => ({ getEmail: () => 'rev@gmail.com' }) },
    SpreadsheetApp: { openById: () => ({ getSheetByName: () => sh }), flush() {} } };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'google', 'review.gs'), 'utf8')
    .replace("const SHEET_URL = '';", "const SHEET_URL = 'https://docs.google.com/spreadsheets/d/T/edit';") + '\nthis.apiList=apiList;', ctx);
  const L = ctx.apiList().items;
  check(L[0].name === 'Health Potion I' && L[0].floor === '' && L[1].name === 'Combinaison Brutale' && JSON.stringify(L[0].fields) === JSON.stringify([['物品・來源', 'Shop']]),
    'review web app reads the per-type name / floor questions (and does not repeat them as fields)');
}
// ---- main script: processQueue ----
{
  const sh = fakeSheet(rows());
  sh.g.rows[2][10] = '核准';   // approved from the web app, result still empty
  sh.g.rows[3][10] = '退回';
  const published = [];
  const ctx = { console, PropertiesService: { getScriptProperties: () => ({ getProperty: () => 'X' }) },
    SpreadsheetApp: { openById: () => ({ getSheetByName: () => sh }) },
    Utilities: { formatDate: () => '2026-11-01' } };
  vm.createContext(ctx);
  const src = fs.readFileSync(path.join(ROOT, 'google', 'apps-script.gs'), 'utf8');
  vm.runInContext(src + '\nthis.processQueue=processQueue;publishRow_=function(s,r){__pub.push(r)};syncPending_=function(){__sync.n++};', Object.assign(ctx, { __pub: published, __sync: { n: 0 } }));
  ctx.processQueue();
  check(JSON.stringify(published) === '[3]', 'processQueue publishes approved rows whose result is empty (not R0001, already online)');
  check(sh.g.rows[3][12] === '已退回，不會上線 2026-11-01', 'processQueue marks rejected rows with the date');
  check(ctx.__sync.n === 1, 'processQueue refreshes the public pending list');
}

// ---- upgradeForm on a fake Google Form shaped like the live one (built by the old setup) ----
{
  const T = { TEXT: 'TEXT', PARAGRAPH_TEXT: 'PARAGRAPH_TEXT', LIST: 'LIST', MULTIPLE_CHOICE: 'MULTIPLE_CHOICE', PAGE_BREAK: 'PAGE_BREAK', FILE_UPLOAD: 'FILE_UPLOAD' };
  const list = [];
  const mk = (type, title) => {
    const it = { type, title, help: '', choices: [], goto: null };
    const self = {
      _it: it, getTitle: () => it.title, getType: () => it.type, getIndex: () => list.indexOf(self),
      setTitle: v => { it.title = v; return self; }, setHelpText: v => { it.help = v; return self; }, setRequired: () => self,
      setValidation: () => self, setChoiceValues: v => { it.choices = v.map(x => ({ getValue: () => x, getGotoPage: () => null })); return self; },
      setGoToPage: pg => { it.goto = pg; return self; }, getChoices: () => it.choices, setChoices: c => { it.choices = c; return self; },
      createChoice: (v, pg) => ({ getValue: () => v, getGotoPage: () => pg }),
      asListItem: () => self, asPageBreakItem: () => self, asMultipleChoiceItem: () => self, asTextItem: () => self,
      createResponse: v => ({ item: self, v }), getId: () => list.indexOf(self) + 1000, req: false,
    };
    self.setRequired = r => { it.req = r; return self; };
    list.push(self); return self;
  };
  const form = {
    getItems: ty => ty ? list.filter(i => i.getType() === ty) : list.slice(), setDescription: () => form,
    addTextItem: () => mk(T.TEXT, ''), addParagraphTextItem: () => mk(T.PARAGRAPH_TEXT, ''), addListItem: () => mk(T.LIST, ''),
    addMultipleChoiceItem: () => mk(T.MULTIPLE_CHOICE, ''), addPageBreakItem: () => mk(T.PAGE_BREAK, ''),
    moveItem: (from, to) => { const [x] = list.splice(from, 1); list.splice(to, 0, x); },
    deleteItem: x => { list.splice(list.indexOf(x), 1); },
    createResponse: () => { const rs = []; const o = { withItemResponse: r => { rs.push(r); return o; },
      toPrefilledUrl: () => 'https://docs.google.com/forms/d/e/X/viewform?usp=pp_url&' + rs.map(r => 'entry.' + r.item.getId() + '=' + r.v).join('&') }; return o; },
  };
  // the live form
  mk(T.TEXT, '樓層'); mk(T.TEXT, '名稱'); const type = mk(T.MULTIPLE_CHOICE, '回報種類');
  const pMon = mk(T.PAGE_BREAK, '怪物'); mk(T.TEXT, '怪物・等級');
  const pItem = mk(T.PAGE_BREAK, '物品'); mk(T.LIST, '物品・怎麼拿到的');
  const pPlace = mk(T.PAGE_BREAK, '地點'); mk(T.LIST, '地點・種類'); mk(T.TEXT, '地點・座標 x, z'); mk(T.PARAGRAPH_TEXT, '地點・說明');
  const pShot = mk(T.PAGE_BREAK, '截圖'); mk(T.FILE_UPLOAD, '截圖');
  type.setChoices([type.createChoice('怪物', pMon), type.createChoice('物品', pItem), type.createChoice('地點', pPlace)]);
  pItem.setGoToPage(pShot); pPlace.setGoToPage(pShot);
  const val = { requireWholeNumber: () => val, requireNumberBetween: () => val, setHelpText: () => val, build: () => ({}) };
  const puts = [];
  const ctx = { console, Logger: { log: () => {} }, PropertiesService: { getScriptProperties: () => ({ getProperty: () => 'F' }) },
    FormApp: { ItemType: T, PageNavigationType: { SUBMIT: 'SUBMIT' }, openById: () => form, createTextValidation: () => val },
    Utilities: { formatDate: () => '2026-11-02 10:00', base64Encode: x => Buffer.from(String(x)).toString('base64'), Charset: { UTF_8: 'UTF-8' } },
    UrlFetchApp: { fetch: (url, opt) => { if ((opt.method || '').toLowerCase() === 'put') { puts.push(JSON.parse(opt.payload)); return { getResponseCode: () => 200, getContentText: () => '{}' }; }
      return { getResponseCode: () => 404, getContentText: () => '' }; } } };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'google', 'apps-script.gs'), 'utf8') + '\nthis.upgradeForm=upgradeForm;', ctx);
  ctx.upgradeForm();
  const n1 = list.length;
  ctx.upgradeForm();
  check(list.length === n1, 'upgradeForm can run twice without adding anything twice (' + n1 + ' items)');
  const titles = list.map(i => i.getTitle());
  const ix = s => titles.indexOf(s);
  check(ix('地點・座標 x, z') < ix('地點・在地下嗎') && ix('地點・NPC 類別') < ix('地點・說明') && ix('地點・說明') < ix('配方'),
    'place page: the three new questions sit after the coordinates');
  check(ix('配方') < ix('任務追蹤') && ix('任務追蹤') < ix('技能') && ix('技能') < ix('截圖') && titles[titles.length - 1] === '截圖' && list[list.length - 1].getType() === T.FILE_UPLOAD,
    'new pages are placed before the screenshot page; the upload question stays last');
  check(list.find(i => i.getTitle() === '地點・種類')._it.choices.map(c => c.getValue()).includes('傳送點'), 'place kinds include 傳送點');
  check(JSON.stringify(titles.slice(0, 2)) === JSON.stringify(['回報者・遊戲內暱稱', '回報種類']) && !titles.includes('樓層') && !titles.includes('名稱'),
    'page 1 asks only the nickname and the report type (old 樓層 / 名稱 removed)');
  const after = (pg, n) => titles.slice(ix(pg) + 1, ix(pg) + 1 + n).join('|');
  check(after('怪物', 2) === '怪物・樓層|怪物・名稱' && after('物品', 2) === '物品・樓層|物品・名稱' && after('地點', 2) === '地點・樓層|地點・名稱'
    && after('配方', 2) === '配方・樓層|配方・物品名稱' && after('任務追蹤', 2) === '任務・樓層|任務・標題' && after('技能', 1) === '技能・名稱'
    && after('建議', 1) === '建議・標題' && after('探索地圖', 1) === '探索地圖・說明',
    'each type page starts with its own floor / name questions (skills, suggestions: no floor; explored map: neither)');
  const q = t => list.find(i => i.getTitle() === t)._it;
  check(q('怪物・樓層').req && !q('物品・樓層').req && q('任務・樓層').req, 'floor is required except for items (shared items leave it empty)');
  const cfg = puts.length ? Buffer.from(puts[puts.length - 1].content, 'base64').toString() : '';
  const pre = (cfg.match(/"prefill": "([^"]+)"/) || [])[1] || '';
  check(/window\.SAO_FORM = /.test(cfg) && (pre.match(/=\{floor\}/g) || []).length === 4 && !pre.includes('entry.' + list.find(i => i.getTitle() === '物品・樓層').getId() + '='),
    'upgradeForm writes formcfg.js with a prefill URL for the 4 required floor questions (not the optional item floor): ' + pre);
  // walk the form: choose a type, fill its page, the next page must be 截圖
  const pages = list.filter(i => i.getType() === T.PAGE_BREAK);
  const nextAfter = pg => { const k = pages.indexOf(pg); const nx = pages[k + 1]; const g = nx ? (nx._it.goto || nx) : null; return g === 'SUBMIT' ? '送出' : g.getTitle(); };
  const route = type._it.choices.map(c => [c.getValue(), c.getGotoPage().getTitle(), nextAfter(c.getGotoPage())]);
  check(route.length === 8 && route.every(([v, pg, nx]) => v === pg && nx === (v === '建議' || v === '探索地圖' ? '送出' : '截圖')),
    'every report type opens its own page, then 截圖 (建議 and 探索地圖 go straight to 送出): ' + route.map(r => r.join('→')).join('，'));
  // a form that already got the first three new pages (upgradeForm of 2026-11-02) only gets 探索地圖 added
  const k = list.findIndex(i => i.getTitle() === '探索地圖');
  list.splice(k, 6);   // 探索地圖 and 建議: page breaks and their questions (2 + 4 items)
  type.setChoices(type._it.choices.filter(c => !['探索地圖', '建議'].includes(c.getValue())));
  list.find(i => i.getTitle() === '截圖')._it.goto = null;
  ctx.upgradeForm();
  const t2 = list.map(i => i.getTitle());
  check(t2.indexOf('技能・備註') < t2.indexOf('探索地圖') && t2.indexOf('探索地圖') < t2.indexOf('建議') && t2.indexOf('建議') < t2.indexOf('截圖')
    && list.length === n1 && type._it.choices.length === 8 && list.find(i => i.getTitle() === '截圖')._it.goto === 'SUBMIT'
    && list.find(i => i.getTitle() === '建議' && i.getType() === T.PAGE_BREAK)._it.goto === 'SUBMIT',
    'running the new upgradeForm on an already upgraded form adds only the missing pages (探索地圖, 建議) before 截圖; 建議 submits directly');
}
// ---- pending.js: only id, type, floor, date and status are published; written only when something changed ----
{
  const sh = fakeSheet([HDR.concat(['回報者・遊戲內暱稱']),
    ['2026/11/01 0:20', '1', 'Young Spider', '怪物', '3', '', 'x', 'R0001', '', '', '核准', '', '已上線 x', ''],
    ['2026/11/01 1:00', '1', 'Albal', '怪物', '8', '', 'x', 'R0002', '', '', '待審核', '', '', 'Kirito_TW'],
    ['2026/11/2 9:05', '2', 'Hidden Well', '地點', '', '', 'x', 'R0003', '', '', '核准', '審核：someone@gmail.com｜ok', '處理中…', ''],
    ['2026/10/01 1:00', '1', 'Old', '物品', '', '', 'x', 'R0004', '', '', '退回', '', '已退回，不會上線 2026-10-01', ''],
    ['2026/10/30 1:00', '1', 'Bad shot', '物品', '', '', 'x', 'R0005', '', '', '退回', '審核：a@b.c｜看不清楚', '已退回，不會上線 2026-10-31', ''],
    ['2026/11/01 2:00', '1', 'My map', '探索地圖', '', '', '', 'R0006', '', '', '核准', '', '已送去合併 2026-11-01', ''],
    ['2026/11/01 3:00', '1', 'Iron Sword', '配方', '', '', 'x', 'R0007', '', '', '核准', '', '錯誤：GitHub 金鑰無效', ''],
    ['2026/11/01 4:00', '1', 'Mark my position', '建議', '', '', '', 'R0008', '', '', '', '', '', '']]);
  const props = {}, puts = [];
  const resp = (code, obj) => ({ getResponseCode: () => code, getContentText: () => JSON.stringify(obj || {}) });
  const ctx = { console, Logger: { log: () => {} },
    PropertiesService: { getScriptProperties: () => ({ getProperty: k => k === 'GITHUB_TOKEN' ? 'tok' : k === 'SHEET_ID' ? 'S' : props[k] ?? null,
      setProperty: (k, v) => { props[k] = v; }, deleteProperty: k => { delete props[k]; } }) },
    SpreadsheetApp: { openById: () => ({ getSheetByName: () => sh }) },
    Utilities: { formatDate: () => '2026-11-02 10:00', base64Encode: x => Buffer.from(String(x)).toString('base64'), sleep() {},
      computeDigest: (a, x) => [...require('crypto').createHash('md5').update(String(x)).digest()], DigestAlgorithm: { MD5: 'MD5' }, Charset: { UTF_8: 'UTF-8' } },
    UrlFetchApp: { fetch: (url, opt) => { if ((opt.method || 'get').toLowerCase() === 'put') { puts.push(JSON.parse(opt.payload)); return resp(200, { commit: { sha: 'abc' } }); } return resp(404); } } };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'google', 'apps-script.gs'), 'utf8') + '\nthis.pendingList_=pendingList_;this.syncPending_=syncPending_;this.syncPending=syncPending;', ctx);
  const L = ctx.pendingList_(sh, new Date('2026-11-02T12:00:00+08:00'));
  check(L.map(x => x.id + ':' + x.status).join(',') === 'R0002:pending,R0003:approved,R0005:rejected,R0007:error,R0008:pending',
    'pending list: waiting, approved-not-online, recently rejected and failed reports; online, merged and old rejections are left out');
  check(JSON.stringify(L[0]) === JSON.stringify({ id: 'R0002', type: 'monster', floor: 1, date: '2026-11-01 01:00', status: 'pending' }) && L[1].date === '2026-11-02 09:05' && L[2].rdate === '2026-10-31',
    'each entry has only id, type, floor, submit time and status (plus the rejection date)');
  const txt = JSON.stringify(L);
  check(!/Albal|Kirito|someone|gmail|看不清楚|Bad shot/.test(txt), 'no names, nicknames, review notes or reviewer accounts are published');
  ctx.syncPending_();
  const body = puts.length === 1 ? Buffer.from(puts[0].content, 'base64').toString() : '';
  const m = body.match(/window\.SAO_PENDING = ([\s\S]*);\n$/);
  check(puts.length === 1 && puts[0].message === '處理中的回報：' + JSON.parse(m[1]).list.length + ' 則' && JSON.parse(m[1]).updated === '2026-11-02 10:00',
    'syncPending_ writes pending.js as window.SAO_PENDING = {updated, list}');
  ctx.syncPending_();
  check(puts.length === 1, 'syncPending_ does not commit again when nothing changed');
  sh.g.rows[2][10] = '退回'; sh.g.rows[2][12] = '已退回，不會上線 2026-11-02';
  ctx.syncPending_();
  check(puts.length === 2 && /"R0002"[\s\S]*?"rejected"/.test(Buffer.from(puts[1].content, 'base64').toString()), 'a status change is written again');
  ctx.syncPending();
  check(puts.length === 3, 'syncPending (manual) always rewrites the file');
}
// ---- publishRow_ with the new per-type floor / name questions (and the old page-1 ones); explored maps are auto-approved ----
{
  const H2 = ['時間戳記', '樓層', '名稱', '回報者・遊戲內暱稱', '回報種類', '怪物・樓層', '怪物・名稱', '怪物・等級', '物品・樓層', '物品・名稱', '物品・怎麼拿到的',
    '技能・名稱', '技能・職業', '探索地圖・說明', ' 探索地圖・壓縮檔 ', '截圖', '回報編號', '截圖預覽', '內容摘要', '狀態', '審核備註', '處理結果'];   // the upload question was added by hand with stray spaces (R0002)
  const row = o => H2.map(h => o[h] ?? '');
  const sh = fakeSheet([H2,
    row({ '時間戳記': '2026/11/01 0:20', '樓層': '1', '名稱': 'Young Spider', '回報種類': '怪物', '怪物・等級': '3', '截圖': 'https://drive.google.com/open?id=A1', '回報編號': 'R0001', '狀態': '核准' }),
    row({ '時間戳記': '2026/11/02 9:00', '回報種類': '怪物', '怪物・樓層': '2', '怪物・名稱': 'Kobold', '怪物・等級': '7', '截圖': 'https://drive.google.com/open?id=A2', '回報編號': 'R0002', '狀態': '核准' }),
    row({ '時間戳記': '2026/11/02 9:10', '回報種類': '物品', '物品・名稱': 'Health Potion I', '物品・怎麼拿到的': '商店購買', '截圖': 'https://drive.google.com/open?id=A3', '回報編號': 'R0003', '狀態': '核准' }),
    row({ '時間戳記': '2026/11/02 9:20', '回報種類': '技能', '技能・名稱': 'Combinaison Brutale', '技能・職業': 'Guerrier', '截圖': 'https://drive.google.com/open?id=A4', '回報編號': 'R0004', '狀態': '核准' }),
    row({ '時間戳記': '2026/11/02 9:30', '回報種類': '怪物', '怪物・名稱': 'No Floor', '截圖': 'https://drive.google.com/open?id=A5', '回報編號': 'R0005', '狀態': '核准' }),
    row({ '時間戳記': '2026/11/02 9:40', '回報者・遊戲內暱稱': 'Kirito_TW', '回報種類': '探索地圖', ' 探索地圖・壓縮檔 ': 'https://drive.google.com/open?id=Z1', '回報編號': '' })]);
  const entries = [], jm = [];
  const ctx = { console, Logger: { log: () => {} }, PropertiesService: { getScriptProperties: () => ({ getProperty: () => 'X' }) },
    SpreadsheetApp: { openById: () => ({ getSheetByName: () => sh }) },
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
    Utilities: { formatDate: () => '2026-11-02', base64Encode: () => '' } };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'google', 'apps-script.gs'), 'utf8') + `
    this.publishRow_=publishRow_;this.onReportSubmit=onReportSubmit;
    imageBlob_=function(){return{ext:'jpg',blob:{getBytes:function(){return[]}}}};putFile_=function(){};syncPending_=function(){};decorateRow_=function(){};
    upsertReport_=function(e){__e.push(e);return'abcdef0123'};publishJmap_=function(id,f){__jm.push([id,f])};`, Object.assign(ctx, { __e: entries, __jm: jm }));
  const col = n => H2.indexOf(n);
  [2, 3, 4, 5, 6].forEach(r => ctx.publishRow_(sh, r));
  const E = id => entries.find(e => e.id === id);
  check(E('R0001') && E('R0001').floor === 1 && E('R0001').name === 'Young Spider', 'old reports still read the page-1 樓層 / 名稱');
  check(E('R0002') && E('R0002').floor === 2 && E('R0002').name === 'Kobold' && E('R0002').raw['怪物・等級'] === '7' && !('怪物・名稱' in E('R0002').raw) && !('怪物・樓層' in E('R0002').raw),
    'new reports read the type page floor / name (and do not repeat them in raw)');
  check(E('R0003') && E('R0003').floor === null && E('R0003').name === 'Health Potion I', 'an item without a floor goes online as shared by all floors (floor null)');
  check(E('R0004') && E('R0004').floor === null && E('R0004').name === 'Combinaison Brutale', 'skills have no floor');
  check(!E('R0005') && /樓層或名稱沒填好/.test(sh.g.rows[5][col('處理結果')]), 'a monster without a floor is refused with a clear message');
  ctx.onReportSubmit({ range: { getSheet: () => sh, getRow: () => 7 } });
  const r7 = sh.g.rows[6];
  check(r7[col('回報編號')] === 'R0006' && r7[col('狀態')] === '核准' && /自動核准/.test(r7[col('審核備註')]) && jm.length === 1 && jm[0][1] === 'Z1'
    && E('R0006') && E('R0006').floor === 1 && E('R0006').name === '探索地圖' && E('R0006').img === null && /^已送去合併/.test(r7[col('處理結果')]),
    'an explored-map report is approved on submit and sent to merge without a screenshot (floor 1), even with spaces around the upload question title');
  check(!Object.keys(E('R0006').raw).some(k => /壓縮檔/.test(k)), 'the zip link is not published in raw');
}
// ---- publishJmap_: zip to a GitHub release (created once), size limit; processQueue does not redo it ----
{
  const calls = [];
  let release = null;
  const resp = (code, obj) => ({ getResponseCode: () => code, getContentText: () => JSON.stringify(obj || {}) });
  const ctx = { console, Logger: { log: () => {} }, PropertiesService: { getScriptProperties: () => ({ getProperty: k => k === 'GITHUB_TOKEN' ? 'tok' : 'X' }) },
    DriveApp: { getFileById: id => ({ getBlob: () => ({ getBytes: () => ({ length: id === 'BIG' ? 46 * 1048576 : 1000 }) }) }) },
    UrlFetchApp: { fetch: (url, opt) => {
      calls.push([opt.method || 'get', url.replace('https://api.github.com/repos/Cheng-1001/ArgoStrategyGuide', '')]);
      if (url.includes('/releases/tags/')) return release ? resp(200, release) : resp(404);
      if (url.endsWith('/releases')) { release = { upload_url: 'https://uploads.github.com/repos/x/y/releases/9/assets{?name,label}', assets: [] }; return resp(201, release); }
      if (url.includes('uploads.github.com')) { release.assets.push({}); return resp(201, {}); }
      return resp(500);
    } } };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'google', 'apps-script.gs'), 'utf8') + '\nthis.publishJmap_=publishJmap_;this.done_=done_;', ctx);
  ctx.publishJmap_('R0009', 'ZIP');
  check(calls.map(c => c[0].toLowerCase() + ' ' + c[1]).join(' | ') === 'get /releases/tags/jmap-R0009 | post /releases | post https://uploads.github.com/repos/x/y/releases/9/assets?name=R0009.zip',
    'publishJmap_ creates release jmap-R0009 and uploads R0009.zip');
  calls.length = 0; ctx.publishJmap_('R0009', 'ZIP');
  check(calls.length === 1, 'a retry does not upload the zip twice');
  let err = ''; try { ctx.publishJmap_('R0010', 'BIG'); } catch (e) { err = e.message; }
  check(/超過 45 MB/.test(err), 'zips over 45 MB are refused with a clear message');
  check(ctx.done_('已送去合併 2026-11-02 10:00') && ctx.done_('已上線 x') && !ctx.done_('錯誤：x') && !ctx.done_(''), 'done_: sent-to-merge counts as done, errors do not');
}
console.log('\n' + (fails ? fails + ' FAILED' : 'ALL PASSED'));
process.exit(fails ? 1 : 0);
