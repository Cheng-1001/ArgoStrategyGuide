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
// 2026-11-02 起樓層、名稱在各種類頁（主程式 CFG.HEAD）；舊回報在第 1 頁的「樓層」「名稱」
const HEAD_FLOOR = ['怪物・樓層', '物品・樓層', '地點・樓層', '配方・樓層', '任務・樓層'];
const HEAD_NAME = ['怪物・名稱', '物品・名稱', '地點・名稱', '配方・物品名稱', '任務・標題', '技能・名稱', '建議・標題'];

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
  const skip = Object.keys(H).map(k => H[k]).concat(HEAD_FLOOR, HEAD_NAME);
  const first = (v, list, old) => { for (const h of list) { const x = ix(h) < 0 ? '' : String(v[ix(h)]).trim(); if (x) return x; } return ix(old) < 0 ? '' : String(v[ix(old)]).trim(); };
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
      row: r + 1, id: id, time: v[0], type: v[ix(H.TYPE)], floor: first(v, HEAD_FLOOR, H.FLOOR) || (v[ix(H.TYPE)] === '探索地圖' ? '1' : ''),
      name: first(v, HEAD_NAME, H.NAME) || (v[ix(H.TYPE)] === '探索地圖' ? '探索地圖' : ''),
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
