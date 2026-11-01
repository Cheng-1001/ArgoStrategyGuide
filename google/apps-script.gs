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
  TYPES: { '怪物': 'monster', '物品': 'item', '地點': 'place', '配方': 'recipe', '任務追蹤': 'quest', '技能': 'skill', '探索地圖': 'jmap', '建議': 'idea' },
  Q_NICK: '回報者・遊戲內暱稱',   // 選填，會公開顯示在網站上
  Q_JMAP: '探索地圖・壓縮檔',   // 上傳題目，要手動加在「探索地圖」頁（Google 不允許程式建立上傳題目）
  JMAP_MAX_MB: 45,
  // 試算表欄位名稱（前四個是表單題目，後四個是審核用欄位）
  Q_TYPE: '回報種類', Q_FLOOR: '樓層', Q_NAME: '名稱', Q_SHOT: '截圖',
  C_ID: '回報編號', C_STATUS: '狀態', C_NOTE: '審核備註', C_RESULT: '處理結果',
  C_PREVIEW: '截圖預覽', C_SUMMARY: '內容摘要',   // upgradeSheet() 加的兩欄，只給審核員看，不送到網站
  STATUS: ['待審核', '核准', '退回'],
  SHEET_NAME: '回報'
};

const P = () => PropertiesService.getScriptProperties();
/** 「處理結果」表示已經完成（上線，或探索地圖已交給 GitHub 合併），不再重做。 */
const done_ = v => /^(已上線|已送去合併)/.test(String(v || ''));

/** 表單「截圖」頁的說明：教玩家用遊戲內建的 F2 截圖。upgradeSheet() 會把現有表單的說明換成這段。 */
const SHOT_HELP = '用遊戲內建截圖就好：在遊戲裡按 F2（有些筆電要按 Fn+F2）。聊天框會出現「Saved screenshot as ….png」，點檔名可以直接打開。\n檔案在：%APPDATA%\\.Triggers Client\\instances\\Sword Art Online\\screenshots（按 Win+R，貼上這一行按 Enter 就會打開資料夾）。\n按「新增檔案」→「瀏覽」選檔，按住 Ctrl 可以一次選多張（最多 5 張）。不用裁切。\n拍怪物時不要按 F1，F1 會把等級和座標一起藏起來。';

const FORM_DESC = '回報 SAO Minecraft 的怪物、物品、地點、配方、任務追蹤、技能資料，或上傳 JourneyMap 探索地圖。每筆都要附遊戲截圖，審核員核對後會更新到查詢工具網站。工具裡還沒有的也可以回報。';
const NAME_HELP = '照遊戲裡的名稱寫，例如怪物 Young Spider、物品 Leg of a Spider、配方填做出來的物品名稱、任務填任務標題、技能填技能名稱。地點可以寫中文。';
const PLACE_KINDS = ['村鎮', '傳送點', 'NPC', '採集點', '地下城或礦坑', '首領位置', '怪物區', '怪物重生點', '其他'];
const NPC_KINDS = ['鍊金術士', '收購商', '鑰匙鐵匠', '飾品鐵匠', '伐木工', '武器收購商', '旅行商人', '裝備商人', '工具商人', '飾品商人', '神秘商人', '消耗品商人', '武器鐵匠', '防具鐵匠', '金屬錠鐵匠', '材料工匠', '裝備鐵匠', '隱藏飾品鐵匠', '其他'];
const NEW_TYPES = ['配方', '任務追蹤', '技能', '探索地圖', '建議'];   // 建議一定要放最後：它填完直接送出，不經過截圖頁
const NICK_HELP = '選填。填了會顯示在網站上，表示這筆資料是你提供的；不想公開就留空。請不要填 Google 帳號或真實姓名。';
const NUM = () => FormApp.createTextValidation().requireWholeNumber().setHelpText('只填數字').build();

/** 地點頁在座標後面多的三題。 */
function addPlaceExtras_(form) {
  return [
    form.addListItem().setTitle('地點・在地下嗎').setChoiceValues(['不確定', '地面', '地下（要從入口走下去）']),
    form.addTextItem().setTitle('地點・傳送選單名稱').setHelpText('種類是「傳送點」才填：遊戲傳送選單上顯示的名稱，照抄原文，例如 Vallée des Loups'),
    form.addListItem().setTitle('地點・NPC 類別').setHelpText('種類是「NPC」才填').setChoiceValues(NPC_KINDS)
  ];
}

/** 新種類的分頁，每頁一個函式。回傳那一頁的分頁。 */
const PAGE_BUILDERS = {
  '配方': form => {
  const pg = form.addPageBreakItem().setTitle('配方')
    .setHelpText('打開 NPC 的製作或購買選單，點到那個物品按 F2 截圖（要看得到材料、數量、費用、時間）。「名稱」填做出來的物品名稱。');
  form.addTextItem().setTitle('配方・NPC').setRequired(true).setHelpText('製作選單上方的 NPC 名稱，照抄原文，例如 Bandit Accessories');
  form.addListItem().setTitle('配方・分類').setChoiceValues(['武器', '防具', '飾品', '藥水', '鑰匙', '其他']);
  form.addParagraphTextItem().setTitle('配方・材料').setRequired(true).setHelpText('一行一個「名稱 數量」，例如：\nShark Shell 8\nBirch String 1');
  form.addTextItem().setTitle('配方・費用 Col').setHelpText('免費寫 0').setValidation(NUM());
  form.addTextItem().setTitle('配方・製作時間（秒）').setValidation(NUM());
  form.addTextItem().setTitle('配方・需求等級').setValidation(NUM());
  form.addListItem().setTitle('配方・稀有度').setChoiceValues(['不確定', '普通', '稀有', '史詩', '傳說']);
  form.addParagraphTextItem().setTitle('配方・備註');
  return pg;
  },
  '任務追蹤': form => {
  const pg = form.addPageBreakItem().setTitle('任務追蹤')
    .setHelpText('任務追蹤畫面（右側 Tracked quest）或任務選單按 F2 截圖。「名稱」填任務標題，不含前面的數字，例如 The Truth About the Seal。');
  form.addListItem().setTitle('任務・種類').setRequired(true).setChoiceValues(['主線', '支線']);
  form.addTextItem().setTitle('任務・編號').setHelpText('追蹤畫面上任務標題前面的數字，例如「24. The Truth About the Seal」就填 24').setValidation(NUM());
  form.addParagraphTextItem().setTitle('任務・目前步驟').setHelpText('照抄追蹤畫面上的步驟原文，例如 Speak with Catherine to continue the main story');
  form.addTextItem().setTitle('任務・NPC');
  form.addTextItem().setTitle('任務・座標 x, z').setHelpText('步驟目標的位置（小地圖座標），例如 2382, 2415');
  form.addTextItem().setTitle('任務・獎勵');
  form.addParagraphTextItem().setTitle('任務・備註');
  return pg;
  },
  '技能': form => {
  const pg = form.addPageBreakItem().setTitle('技能')
    .setHelpText('打開技能選單，點到那個技能按 F2 截圖。「名稱」填技能名稱原文，例如 Combinaison Brutale。');
  form.addListItem().setTitle('技能・職業').setRequired(true).setChoiceValues(['Guerrier', 'Assassin', 'Mage', 'Shaman', 'Archer', 'Martial Artist']);
  form.addListItem().setTitle('技能・主動或被動').setChoiceValues(['不確定', '主動', '被動']);
  form.addTextItem().setTitle('技能・解鎖等級').setValidation(NUM());
  form.addParagraphTextItem().setTitle('技能・說明原文').setHelpText('照抄遊戲裡的技能說明');
  form.addTextItem().setTitle('技能・冷卻或消耗').setHelpText('例如 冷卻 12 秒、魔力 30');
  form.addParagraphTextItem().setTitle('技能・備註');
  return pg;
  },
  '探索地圖': form => {
  const pg = form.addPageBreakItem().setTitle('探索地圖')
    .setHelpText('上傳 JourneyMap 記錄的地圖，網站會自動合併到「探索地圖」。\n' +
      '1. 打開資料夾：按 Win+R，貼上 %APPDATA%\\.Triggers Client\\instances\\Sword Art Online\\journeymap\\data\\mp 按 Enter。\n' +
      '2. 進入伺服器的資料夾（名稱以 Triggers_ 開頭）→ overworld，找到 day 資料夾。\n' +
      '3. 在 day 資料夾上按右鍵 →「壓縮成 ZIP 檔案」（Windows 10 是「傳送到 → 壓縮的資料夾」）。\n' +
      '4. 把 zip 上傳到下面的「探索地圖・壓縮檔」（' + CFG.JMAP_MAX_MB + ' MB 以內）。最後一頁的截圖請拍 JourneyMap 的全螢幕地圖（按 J 打開，再按 F2）。\n' +
      '目前只合併第 1 層；「名稱」填你的遊戲名稱或「探索地圖」都可以。');
  form.addParagraphTextItem().setTitle('探索地圖・說明').setHelpText('例如這次新探索的地方（可不填）');
  return pg;
  },
  '建議': form => {
  const pg = form.addPageBreakItem().setTitle('建議')
    .setHelpText('對查詢工具網站的建議：想要的新功能、版面或操作上的改善、任何讓攻略更好用的想法。不用截圖，填完直接送出。\n' +
      '「名稱」填一句話的標題，例如「地圖可以標記自己的位置」。審核員看過後會公開在網站「協作區 → 問題回報及建議」，你的 Google 帳號不會公開。');
  form.addParagraphTextItem().setTitle('建議・內容').setRequired(true).setHelpText('想要什麼、在哪裡、為什麼有幫助');
  form.addTextItem().setTitle('建議・相關頁面').setHelpText('例如 地圖、圖鑑、任務、配方（可不填）');
  return pg;
  }
};

/** 建立所有新種類的分頁（setup 用）。回傳 {種類: 分頁}。 */
function addNewPages_(form) {
  const pages = {};
  NEW_TYPES.forEach(n => { pages[n] = PAGE_BUILDERS[n](form); });
  return pages;
}

/**
 * 更新「已經建立好」的表單：加入配方、任務追蹤、技能三頁，地點頁多三題、種類多「傳送點」「怪物區」。
 * 只要執行一次；重複執行也不會重複新增。舊題目和已收到的回報都不會動。
 */
function upgradeForm() {
  const form = FormApp.openById(P().getProperty('FORM_ID'));
  const items = () => form.getItems();
  const byTitle = (t, type) => items().find(i => i.getTitle() === t && (!type || i.getType() === type));
  const shot = byTitle(CFG.Q_SHOT, FormApp.ItemType.PAGE_BREAK);
  if (!shot) throw new Error('找不到「截圖」分頁');
  const typeQ = byTitle(CFG.Q_TYPE, FormApp.ItemType.MULTIPLE_CHOICE);
  if (!typeQ) throw new Error('找不到「回報種類」題目');
  form.setDescription(FORM_DESC);
  const nameQ = byTitle(CFG.Q_NAME, FormApp.ItemType.TEXT);
  if (nameQ) nameQ.setHelpText(NAME_HELP);
  // 第 1 頁：選填的遊戲內暱稱，放在「名稱」後面
  if (!byTitle(CFG.Q_NICK)) {
    const nick = form.addTextItem().setTitle(CFG.Q_NICK).setHelpText(NICK_HELP);
    if (nameQ) form.moveItem(nick.getIndex(), nameQ.getIndex() + 1);
  }

  // 地點頁：種類選項、三個新題目放在座標後面
  const kind = byTitle('地點・種類', FormApp.ItemType.LIST);
  if (kind) kind.asListItem().setChoiceValues(PLACE_KINDS);
  if (!byTitle('地點・在地下嗎')) {
    const coords = byTitle('地點・座標 x, z');
    const added = addPlaceExtras_(form);
    let at = coords ? coords.getIndex() + 1 : shot.getIndex();
    added.forEach(it => { form.moveItem(it.getIndex(), at); at++; });
  }

  // 新種類的頁面依序放在截圖頁前面；已經有的頁面不重複新增
  const pages = {};
  NEW_TYPES.forEach(n => {
    const have = byTitle(n, FormApp.ItemType.PAGE_BREAK);
    if (have) { pages[n] = have.asPageBreakItem(); return; }
    const before = items().length;
    pages[n] = PAGE_BUILDERS[n](form);
    const created = items().slice(before);   // 新增的題目都在最後面，依序搬到截圖頁前面
    created.forEach(it => form.moveItem(it.getIndex(), byTitle(CFG.Q_SHOT, FormApp.ItemType.PAGE_BREAK).getIndex()));
  });
  const pShot = byTitle(CFG.Q_SHOT, FormApp.ItemType.PAGE_BREAK).asPageBreakItem();
  NEW_TYPES.forEach(n => pages[n].setGoToPage(pShot));   // 前一頁（地點、配方、任務追蹤…）填完 → 截圖頁
  pShot.setGoToPage(FormApp.PageNavigationType.SUBMIT);   // 截圖頁前面一頁是「建議」：建議填完直接送出，不用截圖

  // 回報種類：保留原本三個選項的跳頁，再加三個新的
  const mc = typeQ.asMultipleChoiceItem();
  const old = {};
  mc.getChoices().forEach(c => { old[c.getValue()] = c.getGotoPage(); });
  const pageOf = n => old[n] || byTitle(n, FormApp.ItemType.PAGE_BREAK).asPageBreakItem();
  mc.setChoices(['怪物', '物品', '地點'].concat(NEW_TYPES).map(n => mc.createChoice(n, pageOf(n))));
  Logger.log('表單已更新：回報種類 ' + mc.getChoices().map(c => c.getValue()).join('、') + '；共 ' + items().length + ' 題');
  if (!byTitle(CFG.Q_JMAP)) Logger.log('還要手動在「探索地圖」頁加上傳題目「' + CFG.Q_JMAP + '」，步驟在 SETUP.md。');
}

/* ===================== 一次性設定 ===================== */

function setup() {
  if (P().getProperty('SHEET_ID')) throw new Error('已經設定過了。要重新設定，請先到「專案設定 → 指令碼屬性」刪掉 SHEET_ID 和 FORM_ID。');

  const form = FormApp.create('Aincrad 查詢工具・資料回報');
  form.setDescription(FORM_DESC)
    .setCollectEmail(false).setAllowResponseEdits(false).setProgressBar(true)
    .setConfirmationMessage('收到了，謝謝！審核員核對截圖後，資料會自動更新到查詢工具網站。');

  // 第 1 頁：共同題目
  const floor = form.addTextItem().setTitle(CFG.Q_FLOOR).setHelpText('只填數字，例如 1').setRequired(true)
    .setValidation(FormApp.createTextValidation().requireNumberBetween(1, 100).setHelpText('請填 1 到 100 的數字').build());
  form.addTextItem().setTitle(CFG.Q_NAME).setRequired(true).setHelpText(NAME_HELP);
  form.addTextItem().setTitle(CFG.Q_NICK).setHelpText(NICK_HELP);
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
  form.addListItem().setTitle('地點・種類').setRequired(true).setChoiceValues(PLACE_KINDS);
  form.addTextItem().setTitle('地點・座標 x, z').setRequired(true).setHelpText('小地圖上的座標，例如 4309, 3697');
  addPlaceExtras_(form);
  form.addParagraphTextItem().setTitle('地點・說明');

  // 配方、任務追蹤、技能
  const extra = addNewPages_(form);

  // 截圖（上傳題目要手動加在這一頁，Google 不允許程式建立上傳題目）
  const pShot = form.addPageBreakItem().setTitle('截圖').setHelpText(SHOT_HELP);

  type.setChoices([type.createChoice('怪物', pMon), type.createChoice('物品', pItem), type.createChoice('地點', pPlace)]
    .concat(NEW_TYPES.map(n => type.createChoice(n, extra[n]))));
  // 每個種類的頁面填完都跳到截圖頁：「下一個分頁」的 setGoToPage 決定前一頁填完要去哪裡
  [pItem, pPlace].concat(NEW_TYPES.map(n => extra[n])).forEach(pb => pb.setGoToPage(pShot));
  pShot.setGoToPage(FormApp.PageNavigationType.SUBMIT);   // 截圖頁前面是「建議」頁：建議填完直接送出

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

/** 補做 setup 沒完成的部分：自動處理（觸發器）、「設定資訊」分頁、三個網址。可以重複執行，不會重複建立。 */
function repair() {
  const props = P().getProperties();
  if (!props.SHEET_ID || !props.FORM_ID) throw new Error('找不到表單或試算表的記錄，請把執行記錄截圖給 Claude');
  const ss = SpreadsheetApp.openById(props.SHEET_ID);
  const form = FormApp.openById(props.FORM_ID);
  const have = ScriptApp.getProjectTriggers().map(t => t.getHandlerFunction());
  if (have.indexOf('onReportSubmit') < 0) ScriptApp.newTrigger('onReportSubmit').forSpreadsheet(ss).onFormSubmit().create();
  if (have.indexOf('onReviewEdit') < 0) ScriptApp.newTrigger('onReviewEdit').forSpreadsheet(ss).onEdit().create();
  const floor = form.getItems(FormApp.ItemType.TEXT).find(i => i.getTitle() === CFG.Q_FLOOR);
  const prefill = floor ? form.createResponse().withItemResponse(floor.asTextItem().createResponse('1')).toPrefilledUrl().replace(/=1(&|$)/, '={floor}$1') : '（找不到「樓層」題目）';
  const info = ss.getSheetByName('設定資訊') || ss.insertSheet('設定資訊');
  info.getRange(1, 1, 5, 2).setValues([
    ['表單（給玩家填）', form.getPublishedUrl()],
    ['表單（編輯）', form.getEditUrl()],
    ['預先填好樓層的網址（交給 Claude）', prefill],
    ['試算表', ss.getUrl()],
    ['說明', '審核員只能改「狀態」和「審核備註」兩欄。把狀態改成「核准」就會自動上線。']
  ]);
  info.autoResizeColumns(1, 1);
  Logger.log('自動處理（觸發器）：' + ScriptApp.getProjectTriggers().map(t => t.getHandlerFunction()).join('、'));
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
  if (col[CFG.C_PREVIEW]) { try { decorateRow_(sh, row); } catch (err) { console.warn('decorateRow_: ' + err.message); } }
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
    if (st === '核准' && !done_(res)) publishRow_(sh, r);
  }
}

/* ===================== 審核網頁用的佇列 ===================== */

/**
 * 審核網頁（另一個專案，見 SETUP.md「審核網頁」）只會把「狀態」改成核准／退回；
 * 用程式改儲存格不會觸發 onReviewEdit，所以由這個函式每分鐘把「核准但還沒處理」的列送上線。
 * 「處理結果」已經有字（已上線、錯誤…）的列不會重做；錯誤修好後照舊執行 retryApproved。
 */
function processQueue() {
  const sh = sheet_();
  const col = headers_(sh);
  const n = sh.getLastRow();
  if (n < 2) return;
  const vals = sh.getRange(2, 1, n - 1, sh.getLastColumn()).getValues();
  vals.forEach((v, i) => {
    const st = String(v[col[CFG.C_STATUS] - 1]);
    const res = String(v[col[CFG.C_RESULT] - 1]).trim();
    if (res) return;
    if (st === '核准') publishRow_(sh, i + 2);
    else if (st === '退回') sh.getRange(i + 2, col[CFG.C_RESULT]).setValue('已退回，不會上線');
  });
}

/**
 * 啟用審核網頁：① 建立每分鐘執行 processQueue 的觸發器（只建一次）；
 * ② 把表單的截圖資料夾以「檢視者」分享給試算表的所有編輯者，審核網頁才看得到截圖。
 * 之後新增審核員：先在試算表「共用」加他為編輯者，再執行一次這個函式。
 */
function enableReviewQueue() {
  if (!ScriptApp.getProjectTriggers().some(t => t.getHandlerFunction() === 'processQueue')) {
    ScriptApp.newTrigger('processQueue').timeBased().everyMinutes(1).create();
  }
  const sh = sheet_();
  const me = Session.getEffectiveUser().getEmail();
  const editors = SpreadsheetApp.openById(P().getProperty('SHEET_ID')).getEditors().map(u => u.getEmail()).filter(e => e && e !== me);
  const col = headers_(sh);
  const shots = sh.getRange(2, col[CFG.Q_SHOT], Math.max(1, sh.getLastRow() - 1), 1).getValues().map(r => String(r[0])).join(' ');
  const roots = {};
  (shots.match(/id=([\w-]+)/g) || []).slice(0, 20).forEach(s => {
    try {
      const q = DriveApp.getFileById(s.slice(3)).getParents();          // 「截圖」題目的資料夾
      if (!q.hasNext()) return;
      const qf = q.next(); const up = qf.getParents();                    // 上一層：整份表單的上傳資料夾
      const root = up.hasNext() ? up.next() : qf;
      roots[root.getId()] = root;
    } catch (e) { /* 找不到就略過 */ }
  });
  const folders = Object.keys(roots).map(k => roots[k]);
  if (editors.length) folders.forEach(f => f.addViewers(editors));
  Logger.log('每分鐘處理佇列：已啟用。');
  Logger.log(folders.length ? '截圖資料夾「' + folders.map(f => f.getName()).join('、') + '」已分享給：' + (editors.join('、') || '（目前沒有其他編輯者）')
                            : '還沒找到截圖資料夾（試算表裡還沒有附截圖的回報）。有回報之後再執行一次。');
}

/* ===================== 上線 ===================== */

function publishRow_(sh, row) {
  const col = headers_(sh);
  const out = sh.getRange(row, col[CFG.C_RESULT]);
  if (done_(out.getValue())) return;
  const lock = LockService.getScriptLock();
  lock.waitLock(60000);
  try {
    // 拿到鎖之後再看一次：試算表觸發器和 processQueue 可能同時想處理同一列，先拿到鎖的那次已經上線就不重做。
    // （這時看到「處理中…」代表之前某次執行中途中斷，持鎖的只有自己，所以照常重試。）
    if (done_(out.getValue())) return;
    out.setValue('處理中…');
    const hdr = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
    const val = sh.getRange(row, 1, 1, sh.getLastColumn()).getValues()[0];
    const get = h => { const i = hdr.indexOf(h); return i < 0 ? '' : String(val[i]).trim(); };
    const id = get(CFG.C_ID) || ('R' + String(row - 1).padStart(4, '0'));
    const type = CFG.TYPES[get(CFG.Q_TYPE)];
    const floor = parseInt(get(CFG.Q_FLOOR), 10);
    const name = get(CFG.Q_NAME);
    if (!type || !floor || !name) throw new Error('回報種類、樓層或名稱沒填好');

    const skip = [CFG.Q_TYPE, CFG.Q_FLOOR, CFG.Q_NAME, CFG.Q_SHOT, CFG.Q_JMAP, CFG.C_ID, CFG.C_STATUS, CFG.C_NOTE, CFG.C_RESULT, CFG.C_PREVIEW, CFG.C_SUMMARY];
    const zipIds = type === 'jmap' ? (get(CFG.Q_JMAP).match(/id=([\w-]+)/g) || []).map(s => s.slice(3)) : [];
    if (type === 'jmap' && !zipIds.length) throw new Error('探索地圖回報沒有附壓縮檔（' + CFG.Q_JMAP + '）');
    if (type === 'jmap' && floor !== 1) throw new Error('探索地圖目前只合併第 1 層；第 ' + floor + ' 層的地圖還沒有探索地圖可以合併');
    const raw = {};
    hdr.forEach((h, i) => { if (i === 0 || skip.includes(h) || !h) return; const v = String(val[i]).trim(); if (v && v !== '不確定') raw[h] = v; });

    // 截圖：Google Drive 上的檔案 → 縮成約 1600px 的 JPEG → 存進網站的 reports 資料夾
    const ids = (get(CFG.Q_SHOT).match(/id=([\w-]+)/g) || []).map(s => s.slice(3));
    if (!ids.length && type !== 'idea') throw new Error('沒有截圖');
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
      img: imgs[0] || null, imgs: imgs, raw: raw, source: 'form'
    };
    if (get(CFG.C_NOTE)) entry.review = get(CFG.C_NOTE);
    const sha = upsertReport_(entry);
    if (type === 'jmap') {
      publishJmap_(id, zipIds[0]);
      out.setValue('已送去合併 ' + Utilities.formatDate(new Date(), CFG.TZ, 'yyyy-MM-dd HH:mm') + '（GitHub 約 3～5 分鐘自動合併；結果會顯示在網站協作區的這筆回報上）');
      return;
    }
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
        return { blob: r.getBlob().getAs(MimeType.JPEG), ext: 'jpg' };
      }
    }
  } catch (e) { /* 改用原始檔 */ }
  const b = file.getBlob();
  if (b.getBytes().length > 8 * 1024 * 1024) throw new Error('截圖超過 8 MB，而且無法縮圖');
  try { return { blob: b.getAs(MimeType.JPEG), ext: 'jpg' }; } catch (e) { /* 無法轉檔就照原格式 */ }
  const t = b.getContentType() || '';
  return { blob: b, ext: t.indexOf('png') >= 0 ? 'png' : t.indexOf('webp') >= 0 ? 'webp' : 'jpg' };
}

/* ===================== 審核畫面（試算表） ===================== */

/**
 * 讓「回報」分頁更好審：在「回報編號」右邊加「截圖預覽」「內容摘要」兩欄，把原始題目欄位收起來，
 * 狀態用顏色標示（待審核黃、核准綠、退回紅），每一列放大到看得清楚截圖。
 * 重新貼上程式後在編輯器執行一次；可以重複執行，會重畫所有列。新回報會自動套用。
 */
function upgradeSheet() {
  const sh = sheet_();
  let col = headers_(sh);
  if (!col[CFG.C_PREVIEW]) {
    sh.insertColumnsAfter(col[CFG.C_ID], 2);
    sh.getRange(1, col[CFG.C_ID] + 1, 1, 2).setValues([[CFG.C_PREVIEW, CFG.C_SUMMARY]]);
    col = headers_(sh);
  }
  const last = sh.getLastColumn();
  // 表單回應常被 Google 自動轉成「表格」，表格標題預設白字，在淺黃底上看不清楚，所以明確設成深色字
  sh.getRange(1, col[CFG.C_ID], 1, last - col[CFG.C_ID] + 1).setFontWeight('bold').setBackground('#fff2cc').setFontColor('#3b2f00');
  // 收起表單原始欄位（時間戳記留著）；內容都整理在「內容摘要」，要看原始答案可以按欄位上方的 + 展開
  const firstReview = Math.min(col[CFG.C_ID], col[CFG.C_STATUS], col[CFG.C_NOTE], col[CFG.C_RESULT]);
  if (firstReview > 2) {
    sh.getColumnGroupDepth(2) > 0 || sh.getRange(1, 2, 1, firstReview - 2).shiftColumnGroupDepth(1);
    sh.hideColumns(2, firstReview - 2);
  }
  sh.setColumnWidth(col[CFG.C_ID], 80);
  sh.setColumnWidth(col[CFG.C_PREVIEW], 300);
  sh.setColumnWidth(col[CFG.C_SUMMARY], 320);
  sh.setColumnWidth(col[CFG.C_STATUS], 90);
  sh.setColumnWidth(col[CFG.C_NOTE], 200);
  sh.setColumnWidth(col[CFG.C_RESULT], 260);
  sh.setFrozenColumns(0);
  // 狀態顏色：整列（回報編號到最後一欄）
  const L = (n) => sh.getRange(1, n).getA1Notation().replace(/\d+/, '');
  const rng = sh.getRange(2, col[CFG.C_ID], sh.getMaxRows() - 1, last - col[CFG.C_ID] + 1);
  const st = '$' + L(col[CFG.C_STATUS]) + '2';
  const keep = sh.getConditionalFormatRules().filter(r => !r.getRanges().some(x => x.getA1Notation() === rng.getA1Notation()));
  sh.setConditionalFormatRules(keep.concat([
    SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied('=' + st + '="待審核"').setBackground('#fff4cc').setRanges([rng]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied('=' + st + '="核准"').setBackground('#dcf3e3').setRanges([rng]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenFormulaSatisfied('=' + st + '="退回"').setBackground('#fbe0e0').setRanges([rng]).build()
  ]));
  sh.getRange(2, col[CFG.C_STATUS], sh.getMaxRows() - 1, 1).setFontWeight('bold').setFontSize(12).setHorizontalAlignment('center');
  sh.getRange(2, col[CFG.C_SUMMARY], sh.getMaxRows() - 1, 1).setWrap(true).setVerticalAlignment('top');
  sh.getRange(2, col[CFG.C_RESULT], sh.getMaxRows() - 1, 1).setWrap(true).setVerticalAlignment('top');
  for (let r = 2; r <= sh.getLastRow(); r++) decorateRow_(sh, r);
  applySheetRules_(sh);
  // 表單「截圖」頁的說明改成 F2 截圖教學
  try {
    const form = FormApp.openById(P().getProperty('FORM_ID'));
    const pb = form.getItems(FormApp.ItemType.PAGE_BREAK).find(i => i.getTitle() === CFG.Q_SHOT);
    if (pb) pb.asPageBreakItem().setHelpText(SHOT_HELP);
  } catch (err) { Logger.log('表單說明沒有更新：' + err.message); }
  Logger.log('審核畫面已更新：' + Math.max(0, sh.getLastRow() - 1) + ' 筆回報。');
}

/** 一列的「截圖預覽」（第一張截圖的縮圖，直接嵌在儲存格裡，Drive 檔案不必公開）和「內容摘要」。 */
function decorateRow_(sh, row) {
  const col = headers_(sh);
  const hdr = sh.getRange(1, 1, 1, sh.getLastColumn()).getValues()[0];
  const val = sh.getRange(row, 1, 1, sh.getLastColumn()).getValues()[0];
  const get = h => { const i = hdr.indexOf(h); return i < 0 ? '' : String(val[i]).trim(); };
  if (!get(CFG.Q_NAME)) return;
  const skip = [CFG.Q_TYPE, CFG.Q_FLOOR, CFG.Q_NAME, CFG.Q_SHOT, CFG.C_ID, CFG.C_STATUS, CFG.C_NOTE, CFG.C_RESULT, CFG.C_PREVIEW, CFG.C_SUMMARY];
  const lines = [get(CFG.Q_TYPE) + '｜第 ' + get(CFG.Q_FLOOR) + ' 層｜' + get(CFG.Q_NAME), ''];
  hdr.forEach((h, i) => {
    if (i === 0 || !h || skip.includes(h)) return;
    const v = String(val[i]).trim();
    if (v && v !== '不確定') lines.push(String(h).replace(/^(怪物|物品|地點|配方|任務|技能|探索地圖|建議)・/, '') + '：' + v);
  });
  const ids = (get(CFG.Q_SHOT).match(/id=([\w-]+)/g) || []).map(s => s.slice(3));
  lines.push('', '截圖 ' + ids.length + ' 張' + (ids.length > 1 ? '（預覽只顯示第一張，其他請點「截圖」欄的連結）' : ''));
  sh.getRange(row, col[CFG.C_SUMMARY]).setValue(lines.join('\n'));
  const cell = sh.getRange(row, col[CFG.C_PREVIEW]);
  if (!ids.length) { cell.setValue('（沒有截圖）'); return; }
  try {
    const auth = { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() };
    const meta = JSON.parse(UrlFetchApp.fetch('https://www.googleapis.com/drive/v3/files/' + ids[0] + '?fields=thumbnailLink', { headers: auth, muteHttpExceptions: true }).getContentText());
    if (!meta.thumbnailLink) throw new Error('Drive 還沒產生縮圖');
    const r = UrlFetchApp.fetch(meta.thumbnailLink.replace(/=s\d+$/, '=s480'), { headers: auth, muteHttpExceptions: true });
    if (r.getResponseCode() !== 200) throw new Error('縮圖下載失敗 ' + r.getResponseCode());
    const jpg = r.getBlob().getAs(MimeType.JPEG);
    const img = SpreadsheetApp.newCellImage().setSourceUrl('data:image/jpeg;base64,' + Utilities.base64Encode(jpg.getBytes()))
      .setAltTextTitle(get(CFG.C_ID) + ' 截圖').build();
    cell.setValue(img);
    sh.setRowHeight(row, 175);
  } catch (err) {
    cell.setFormula('=HYPERLINK("https://drive.google.com/file/d/' + ids[0] + '/view","開啟截圖（預覽失敗：' + String(err.message).replace(/"/g, "'").slice(0, 60) + '）")');
  }
}

/* ===================== GitHub ===================== */

/**
 * 探索地圖：把玩家上傳的 zip 放到 GitHub Release「jmap-回報編號」，GitHub Actions（.github/workflows/jm_merge.yml）
 * 會下載、檢查、合併到網站的探索地圖，然後刪掉這個 Release。重試時同一個 Release 不會重複上傳。
 */
function publishJmap_(id, fileId) {
  const blob = DriveApp.getFileById(fileId).getBlob();
  const mb = blob.getBytes().length / 1048576;
  if (mb > CFG.JMAP_MAX_MB) throw new Error('壓縮檔 ' + mb.toFixed(1) + ' MB，超過 ' + CFG.JMAP_MAX_MB + ' MB。請玩家只壓縮第 1 層的 day 資料夾，或分成兩次回報');
  const tag = 'jmap-' + id;
  let rel = gh_('GET', '/releases/tags/' + tag, null, true);
  if (!rel) rel = gh_('POST', '/releases', { tag_name: tag, target_commitish: CFG.BRANCH, name: '探索地圖 ' + id, prerelease: true,
    body: '玩家回報 ' + id + ' 的 JourneyMap 地圖。GitHub Actions 合併完會自動刪除這個 Release。' });
  if ((rel.assets || []).length) return rel;
  const r = UrlFetchApp.fetch(String(rel.upload_url).replace(/\{.*\}$/, '') + '?name=' + encodeURIComponent(id + '.zip'), {
    method: 'post', contentType: 'application/zip', payload: blob.getBytes(), muteHttpExceptions: true,
    headers: { Authorization: 'Bearer ' + P().getProperty('GITHUB_TOKEN'), Accept: 'application/vnd.github+json' } });
  if (r.getResponseCode() >= 300) throw new Error('上傳探索地圖到 GitHub 失敗 ' + r.getResponseCode() + '：' + r.getContentText().slice(0, 150));
  return rel;
}

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
