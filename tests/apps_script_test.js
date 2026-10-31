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
console.log('\n' + (fails ? fails + ' FAILED' : 'ALL PASSED'));
process.exit(fails ? 1 : 0);
