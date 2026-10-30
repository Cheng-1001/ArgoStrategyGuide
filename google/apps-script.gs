/**
 * Aincrad 查詢工具：回報表單 → 審核試算表 → 自動上線到 GitHub
 *
 * 這是「獨立」的 Apps Script 專案（在 script.google.com 建立），不要放在試算表裡面，
 * 這樣有試算表編輯權限的審核員看不到 GitHub 金鑰，也改不了這份程式。
 *
 * 需要的指令碼屬性（專案設定 → 指令碼屬性）：
 *   GITHUB_TOKEN  只限 Cheng-1001/ArgoStrategyGuide、Contents 可讀寫的 GitHub 金鑰
 * setup() 會自動寫入：SHEET_ID、FORM_ID
 *
 * 這份程式不解讀回報內容：除了種類、樓層、名稱、截圖之外，其他題目都以「題目名稱：答案」
 * 原封不動送到網站，由網站（index.html 的 normRep）解讀。所以之後新增或調整題目，通常只要改網站。
 */

const CFG = {
  OWNER: 'Cheng-1001',
  REPO: 'ArgoStrategyGuide',
  BRANCH: 'main',
  REPORTS_FILE: 'reports.js',
  IMG_DIR: 'reports',
  TZ: 'Asia/Taipei',
  TYPES: { '怪物': 'monster', '物品': 'item', '地點': 'place' },
  // 試算表欄位名稱（前四個是表單題目，後四個是審核用欄位）
  Q_TYPE: '回報種類', Q_FLOOR: '樓層', Q_NAME: '名稱', Q_SHOT: '截圖',
  C_ID: '回報編號', C_STATUS: '狀態', C_NOTE: '審核備註', C_RESULT: '處理結果',
  STATUS: ['待審核', '核准', '退回'],
  SHEET_NAME: '回報'
};

const P = () => PropertiesService.getScriptProperties();

/* ===================== 一次性設定 ===================== */

function setup() {
  if (P().getProperty('SHEET_ID')) throw new Error('已經設定過了。要重新設定，請先到「專案設定 → 指令碼屬性」刪掉 SHEET_ID 和 FORM_ID。');

  const form = FormApp.create('Aincrad 查詢工具・資料回報');
  form.setDescription('回報 SAO Minecraft 的怪物、物品、地點資料。每筆都要附遊戲截圖，審核員核對後會更新到查詢工具網站。工具裡還沒有的也可以回報。')
    .setCollectEmail(false).setAllowResponseEdits(false).setProgressBar(true)
    .setConfirmationMessage('收到了，謝謝！審核員核對截圖後，資料會自動更新到查詢工具網站。');

  // 第 1 頁：共同題目
  const floor = form.addTextItem().setTitle(CFG.Q_FLOOR).setHelpText('只填數字，例如 1').setRequired(true)
    .setValidation(FormApp.createTextValidation().requireNumberBetween(1, 100).setHelpText('請填 1 到 100 的數字').build());
  form.addTextItem().setTitle(CFG.Q_NAME).setRequired(true)
    .setHelpText('照遊戲裡的英文名稱寫，例如 Young Spider、Leg of a Spider。地點可以寫中文。');
  const type = form.addMultipleChoiceItem().setTitle(CFG.Q_TYPE).setRequired(true);

  // 怪物
  const pMon = form.addPageBreakItem().setTitle('怪物')
    .setHelpText('野外截圖才看得到等級（名字上方的 LV）；圖鑑（Codex）截圖看得到編號、區域、掉落機率，但沒有等級。');
  form.addMultipleChoiceItem().setTitle('怪物・截圖種類').setRequired(true)
    .setChoiceValues(['野外截圖（看得到等級和座標）', '圖鑑截圖（Codex）', '兩種都有']);
  form.addTextItem().setTitle('怪物・等級').setHelpText('只填數字；每隻怪物只有一個等級。圖鑑截圖不用填。')
    .setValidation(FormApp.createTextValidation().requireWholeNumber().setHelpText('只填數字').build());
  form.addTextItem().setTitle('怪物・座標 x, z').setHelpText('截圖時小地圖上的座標，例如 1340, 3569');
  form.addTextItem().setTitle('怪物・圖鑑編號').setHelpText('圖鑑截圖才填，例如 #012');
  form.addTextItem().setTitle('怪物・圖鑑區域').setHelpText('圖鑑截圖才填，例如 Forêts du 1er Palier');
  form.addListItem().setTitle('怪物・類型').setChoiceValues(['不確定', '一般怪物', '小首領', '首領']);
  form.addListItem().setTitle('怪物・行為').setChoiceValues(['不確定', '主動攻擊（看到就打）', '中立（被打才還手）', '被動（不會攻擊）']);
  form.addParagraphTextItem().setTitle('怪物・掉落物和機率').setHelpText('一行一個，例如：\nWolf Fangs 100%\nWolf Fur 100%\n還沒解鎖的寫 ??? 3%');
  form.addParagraphTextItem().setTitle('怪物・圖鑑描述或 LOCATION HINT').setHelpText('照抄原文即可');
  form.addParagraphTextItem().setTitle('怪物・備註');

  // 物品
  const pItem = form.addPageBreakItem().setTitle('物品');
  form.addListItem().setTitle('物品・怎麼拿到的').setRequired(true).setChoiceValues(['怪物掉落', '採集', '任務獎勵', '商店購買', '合成或鍛造', '其他']);
  form.addTextItem().setTitle('物品・來源').setHelpText('怪物名稱、NPC 或地點');
  form.addTextItem().setTitle('物品・座標 x, z');
  form.addParagraphTextItem().setTitle('物品・備註').setHelpText('例如數值、用途、合成配方、價格');

  // 地點
  const pPlace = form.addPageBreakItem().setTitle('地點');
  form.addListItem().setTitle('地點・種類').setRequired(true).setChoiceValues(['村鎮', 'NPC', '採集點', '地下城或礦坑', '首領位置', '怪物重生點', '其他']);
  form.addTextItem().setTitle('地點・座標 x, z').setRequired(true).setHelpText('小地圖上的座標，例如 4309, 3697');
  form.addParagraphTextItem().setTitle('地點・說明');

  // 截圖（上傳題目要手動加在這一頁，Google 不允許程式建立上傳題目）
  const pShot = form.addPageBreakItem().setTitle('截圖').setHelpText('上傳遊戲截圖，可以放多張。');

  type.setChoices([type.createChoice('怪物', pMon), type.createChoice('物品', pItem), type.createChoice('地點', pPlace)]);
  pItem.setGoToPage(pShot);   // 怪物頁填完 → 截圖頁
  pPlace.setGoToPage(pShot);  // 物品頁填完 → 截圖頁

  // 試算表
  const ss = SpreadsheetApp.create('Aincrad 查詢工具・回報審核');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  SpreadsheetApp.flush();
  Utilities.sleep(3000);
  const sh = ss.getSheets().find(s => s.getFormUrl()) || ss.getSheets()[0];
  if (sh.getLastColumn() < 3) throw new Error('試算表還沒出現表單欄位，請等一分鐘後到「專案設定 → 指令碼屬性」刪掉 SHEET_ID、FORM_ID（若有），刪除剛建立的表單和試算表，再執行一次 setup');
  sh.setName(CFG.SHEET_NAME);
  ss.getSheets().forEach(s => { if (s.getSheetId() !== sh.getSheetId() && s.getLastRow() === 0 && ss.getSheets().length > 1) ss.deleteSheet(s); });
  const last = sh.getLastColumn();
  sh.getRange(1, last + 1, 1, 4).setValues([[CFG.C_ID, CFG.C_STATUS, CFG.C_NOTE, CFG.C_RESULT]]).setFontWeight('bold').setBackground('#fff2cc');
  sh.setFrozenRows(1);
  applySheetRules_(sh);

  const prefill = form.createResponse().withItemResponse(floor.createResponse('1')).toPrefilledUrl().replace(/=1(&|$)/, '={floor}$1');

  P().setProperties({ SHEET_ID: ss.getId(), FORM_ID: form.getId() });
  ScriptApp.newTrigger('onReportSubmit').forSpreadsheet(ss).onFormSubmit().create();
  ScriptApp.newTrigger('onReviewEdit').forSpreadsheet(ss).onEdit().create();

  const info = ss.insertSheet('設定資訊');
  info.getRange(1, 1, 5, 2).setValues([
    ['表單（給玩家填）', form.getPublishedUrl()],
    ['表單（編輯）', form.getEditUrl()],
    ['預先填好樓層的網址（交給 Claude）', prefill],
    ['試算表', ss.getUrl()],
    ['說明', '審核員只能改「狀態」和「審核備註」兩欄。把狀態改成「核准」就會自動上線。']
  ]);
  info.autoResizeColumns(1, 1);
  Logger.log('表單（編輯）：' + form.getEditUrl());
  Logger.log('試算表：' + ss.getUrl());
  Logger.log('預先填好樓層的網址（交給 Claude）：' + prefill);
}

/** 狀態下拉選單 + 保護：審核員只能改「狀態」「審核備註」。上傳題目加好之後要再執行一次。 */
function applySheetRules_(sh) {
  const col = headers_(sh);
  const maxRows = sh.getMaxRows();
  const st = sh.getRange(2, col[CFG.C_STATUS], maxRows - 1, 1);
  st.setDataValidation(SpreadsheetApp.newDataValidation().requireValueInList(CFG.STATUS, true).setAllowInvalid(false).build());
  sh.getProtections(SpreadsheetApp.ProtectionType.SHEET).forEach(p => p.remove());
  const prot = sh.protect().setDescription('審核員只能改狀態和審核備註');
  prot.setUnprotectedRanges([st, sh.getRange(2, col[CFG.C_NOTE], maxRows - 1, 1)]);
  prot.removeEditors(prot.getEditors());
  prot.addEditor(Session.getEffectiveUser());
  if (prot.canDomainEdit()) prot.setDomainEdit(false);
}

/** 加好「截圖」上傳題目後執行：檢查欄位並重新套用保護。 */
function checkSetup() {
  const sh = sheet_();
  const col = headers_(sh);
  const miss = [CFG.Q_TYPE, CFG.Q_FLOOR, CFG.Q_NAME, CFG.Q_SHOT, CFG.C_ID, CFG.C_STATUS, CFG.C_NOTE, CFG.C_RESULT].filter(h => !col[h]);
  applySheetRules_(sh);
  if (!P().getProperty('GITHUB_TOKEN')) miss.push('指令碼屬性 GITHUB_TOKEN');
  else gh_('GET', ''); // 金鑰無效會在這裡報錯
  if (miss.length) throw new Error('還缺：' + miss.join('、'));
  Logger.log('設定都正確。');
}

/* ===================== 觸發器 ===================== */

function onReportSubmit(e) {
  const sh = e.range.getSheet();
  const row = e.range.getRow();
  const col = headers_(sh);
  sh.getRange(row, col[CFG.C_ID]).setValue('R' + String(row - 1).padStart(4, '0'));
  sh.getRange(row, col[CFG.C_STATUS]).setValue('待審核');
}

function onReviewEdit(e) {
  const sh = e.range.getSheet();
  if (sh.getName() !== CFG.SHEET_NAME || e.range.getNumRows() !== 1) return;
  const col = headers_(sh);
  if (e.range.getColumn() !== col[CFG.C_STATUS] || e.range.getRow() < 2) return;
  const v = String(e.range.getValue());
  const row = e.range.getRow();
  if (v === '核准') publishRow_(sh, row);
  else if (v === '退回') sh.getRange(row, col[CFG.C_RESULT]).setValue('已退回，不會上線');
}

/** 手動重試：處理所有「核准」但還沒成功上線的列（在編輯器選這個函式按「執行」）。 */
function retryApproved() {
  const sh = sheet_();
  const col = headers_(sh);
  const n = sh.getLastRow();
  for (let r = 2; r <= n; r++) {
    const st = sh.getRange(r, col[CFG.C_STATUS]).getValue();
    const res = String(sh.getRange(r, col[CFG.C_RESULT]).getValue());
    if (st === '核准' && !res.startsWith('已上線')) publishRow_(sh, r);
  }
}

/* ===================== 上線 ===================== */

function publishRow_(sh, row) {
  const col = headers_(sh);
  const out = sh.getRange(row, col[CFG.C_RESULT]);
  if (String(out.getValue()).startsWith('已上線')) return;
  const lock = LockService.getScriptLock();
  lock.waitLock(60000);
  try {
    out.setValue('處理中…');
    const hdr = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
    const val = sh.getRange(row, 1, 1, sh.getLastColumn()).getValues()[0];
    const get = h => { const i = hdr.indexOf(h); return i < 0 ? '' : String(val[i]).trim(); };
    const id = get(CFG.C_ID) || ('R' + String(row - 1).padStart(4, '0'));
    const type = CFG.TYPES[get(CFG.Q_TYPE)];
    const floor = parseInt(get(CFG.Q_FLOOR), 10);
    const name = get(CFG.Q_NAME);
    if (!type || !floor || !name) throw new Error('回報種類、樓層或名稱沒填好');

    const skip = [CFG.Q_TYPE, CFG.Q_FLOOR, CFG.Q_NAME, CFG.Q_SHOT, CFG.C_ID, CFG.C_STATUS, CFG.C_NOTE, CFG.C_RESULT];
    const raw = {};
    hdr.forEach((h, i) => { if (i === 0 || skip.includes(h) || !h) return; const v = String(val[i]).trim(); if (v && v !== '不確定') raw[h] = v; });

    // 截圖：Google Drive 上的檔案 → 縮成約 1600px 的 JPEG → 存進網站的 reports 資料夾
    const ids = (get(CFG.Q_SHOT).match(/id=([\w-]+)/g) || []).map(s => s.slice(3));
    if (!ids.length) throw new Error('沒有截圖');
    const imgs = [];
    ids.forEach((fid, k) => {
      const img = imageBlob_(fid);
      const path = CFG.IMG_DIR + '/' + id + (k ? '-' + (k + 1) : '') + '.' + img.ext;
      putFile_(path, Utilities.base64Encode(img.blob.getBytes()), '回報 ' + id + '：截圖');
      imgs.push(path);
    });

    const entry = {
      id: id, type: type, floor: floor, name: name,
      date: Utilities.formatDate(new Date(), CFG.TZ, 'yyyy-MM-dd'),
      img: imgs[0], imgs: imgs, raw: raw, source: 'form'
    };
    if (get(CFG.C_NOTE)) entry.review = get(CFG.C_NOTE);
    const sha = upsertReport_(entry);
    out.setValue('已上線 ' + Utilities.formatDate(new Date(), CFG.TZ, 'yyyy-MM-dd HH:mm') + '（網站約 1～3 分鐘後更新，' + sha.slice(0, 7) + '）');
  } catch (err) {
    out.setValue('錯誤：' + err.message + '（修正後在程式編輯器執行 retryApproved 重試）');
  } finally {
    lock.releaseLock();
  }
}

function imageBlob_(fileId) {
  const file = DriveApp.getFileById(fileId);
  const auth = { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() };
  try {
    const meta = JSON.parse(UrlFetchApp.fetch('https://www.googleapis.com/drive/v3/files/' + fileId + '?fields=thumbnailLink', { headers: auth, muteHttpExceptions: true }).getContentText());
    if (meta.thumbnailLink) {
      const r = UrlFetchApp.fetch(meta.thumbnailLink.replace(/=s\d+$/, '=s1600'), { headers: auth, muteHttpExceptions: true });
      if (r.getResponseCode() === 200 && r.getBlob().getBytes().length > 5000) {
        const t = r.getBlob().getContentType() || '';
        return { blob: r.getBlob(), ext: t.indexOf('png') >= 0 ? 'png' : 'jpg' };
      }
    }
  } catch (e) { /* 改用原始檔 */ }
  const b = file.getBlob();
  if (b.getBytes().length > 8 * 1024 * 1024) throw new Error('截圖超過 8 MB，而且無法縮圖');
  const t = b.getContentType() || '';
  return { blob: b, ext: t.indexOf('png') >= 0 ? 'png' : t.indexOf('webp') >= 0 ? 'webp' : 'jpg' };
}

/* ===================== GitHub ===================== */

function gh_(method, path, body, allow404) {
  const token = P().getProperty('GITHUB_TOKEN');
  if (!token) throw new Error('還沒設定 GITHUB_TOKEN（專案設定 → 指令碼屬性）');
  const opt = {
    method: method, muteHttpExceptions: true,
    headers: { Authorization: 'Bearer ' + token, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28' }
  };
  if (body) { opt.contentType = 'application/json'; opt.payload = JSON.stringify(body); }
  const r = UrlFetchApp.fetch('https://api.github.com/repos/' + CFG.OWNER + '/' + CFG.REPO + path, opt);
  const c = r.getResponseCode();
  if (c === 404 && allow404) return null;
  if (c === 401) throw new Error('GitHub 金鑰無效或已過期，請重新產生並更新 GITHUB_TOKEN');
  if (c === 403) throw new Error('GitHub 金鑰沒有寫入權限（Contents 要設成 Read and write）');
  if (c >= 300) { const e = new Error('GitHub 回應 ' + c + '：' + r.getContentText().slice(0, 200)); e.code = c; throw e; }
  return JSON.parse(r.getContentText() || '{}');
}

function putFile_(path, base64, message) {
  const cur = gh_('GET', '/contents/' + encodeURI(path) + '?ref=' + CFG.BRANCH, null, true);
  const body = { message: message, content: base64, branch: CFG.BRANCH };
  if (cur && cur.sha) body.sha = cur.sha;
  return gh_('PUT', '/contents/' + encodeURI(path), body);
}

/** 讀 reports.js、加入或取代同編號的回報、寫回。遇到同時寫入的衝突會重試。 */
function upsertReport_(entry) {
  for (let attempt = 0; attempt < 3; attempt++) {
    const cur = gh_('GET', '/contents/' + CFG.REPORTS_FILE + '?ref=' + CFG.BRANCH);
    const text = Utilities.newBlob(Utilities.base64Decode(cur.content.replace(/\n/g, ''))).getDataAsString('UTF-8');
    const m = text.match(/^([\s\S]*?window\.SAO_REPORTS\s*=\s*)(\[[\s\S]*\])\s*;?\s*$/);
    if (!m) throw new Error(CFG.REPORTS_FILE + ' 的格式不對，無法自動加入');
    const list = JSON.parse(m[2]);
    const i = list.findIndex(x => x.id === entry.id);
    if (i >= 0) list[i] = entry; else list.push(entry);
    const next = m[1] + JSON.stringify(list, null, 1) + ';\n';
    try {
      const res = gh_('PUT', '/contents/' + CFG.REPORTS_FILE, {
        message: '收錄回報 ' + entry.id + '：' + entry.name, branch: CFG.BRANCH, sha: cur.sha,
        content: Utilities.base64Encode(next, Utilities.Charset.UTF_8)
      });
      return res.commit.sha;
    } catch (e) {
      if (e.code === 409 || e.code === 422) { Utilities.sleep(1500); continue; }
      throw e;
    }
  }
  throw new Error('寫入 ' + CFG.REPORTS_FILE + ' 時一直發生衝突，請稍後執行 retryApproved');
}

/* ===================== 小工具 ===================== */

function sheet_() {
  const id = P().getProperty('SHEET_ID');
  if (!id) throw new Error('還沒執行 setup');
  return SpreadsheetApp.openById(id).getSheetByName(CFG.SHEET_NAME);
}

function headers_(sh) {
  const h = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
  const o = {};
  h.forEach((v, i) => { if (v && !o[v]) o[v] = i + 1; });
  return o;
}
