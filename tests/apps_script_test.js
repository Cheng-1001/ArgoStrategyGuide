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

// ---- main script: processQueue ----
{
  const sh = fakeSheet(rows());
  sh.g.rows[2][10] = '核准';   // approved from the web app, result still empty
  sh.g.rows[3][10] = '退回';
  const published = [];
  const ctx = { console, PropertiesService: { getScriptProperties: () => ({ getProperty: () => 'X' }) },
    SpreadsheetApp: { openById: () => ({ getSheetByName: () => sh }) } };
  vm.createContext(ctx);
  const src = fs.readFileSync(path.join(ROOT, 'google', 'apps-script.gs'), 'utf8');
  vm.runInContext(src + '\nthis.processQueue=processQueue;publishRow_=function(s,r){__pub.push(r)};', Object.assign(ctx, { __pub: published }));
  ctx.processQueue();
  check(JSON.stringify(published) === '[3]', 'processQueue publishes approved rows whose result is empty (not R0001, already online)');
  check(sh.g.rows[3][12] === '已退回，不會上線', 'processQueue marks rejected rows');
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
    };
    list.push(self); return self;
  };
  const form = {
    getItems: ty => ty ? list.filter(i => i.getType() === ty) : list.slice(), setDescription: () => form,
    addTextItem: () => mk(T.TEXT, ''), addParagraphTextItem: () => mk(T.PARAGRAPH_TEXT, ''), addListItem: () => mk(T.LIST, ''),
    addMultipleChoiceItem: () => mk(T.MULTIPLE_CHOICE, ''), addPageBreakItem: () => mk(T.PAGE_BREAK, ''),
    moveItem: (from, to) => { const [x] = list.splice(from, 1); list.splice(to, 0, x); },
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
  const ctx = { console, Logger: { log: () => {} }, PropertiesService: { getScriptProperties: () => ({ getProperty: () => 'F' }) },
    FormApp: { ItemType: T, openById: () => form, createTextValidation: () => val } };
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
  // walk the form: choose a type, fill its page, the next page must be 截圖
  const pages = list.filter(i => i.getType() === T.PAGE_BREAK);
  const nextAfter = pg => { const k = pages.indexOf(pg); const nx = pages[k + 1]; return nx ? (nx._it.goto || nx) : null; };
  const route = type._it.choices.map(c => [c.getValue(), c.getGotoPage().getTitle(), nextAfter(c.getGotoPage()).getTitle()]);
  check(route.length === 6 && route.every(([v, pg, nx]) => v === pg && nx === '截圖'), 'every report type opens its own page and then goes to 截圖: ' + route.map(r => r.join('→')).join('，'));
}
console.log('\n' + (fails ? fails + ' FAILED' : 'ALL PASSED'));
process.exit(fails ? 1 : 0);
