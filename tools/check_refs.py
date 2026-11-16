#!/usr/bin/env python3
"""R0.5 stage 1: build-time reference checker (plan: R05_stage1_plan_v5.md, design: R05_design_final.md).

What it does
  * loads every data file the page loads (tools/check_refs_load.js, Node vm; Node is required),
  * walks every field of every data file and checks that it is registered in COVERAGE
    (scanned, or excluded with a reason and the stage that will handle it)  -> E9 when not,
  * resolves the scanned references (items, monsters, NPCs, places, quests, sets)  -> E1 / E2,
  * finds external ids claimed by two site records  -> E3,
  * checks the pins in registry/pins.json  -> E6 (identity) / E7 (icon),
  * compares the errors with registry/exceptions.json (locked, item by item),
  * writes build/registry_report.md (committed, deterministic) and build/registry_report.json (not committed).

It never writes data files or index.html.  Exit code 1 when an error is not covered by an approved exception,
when an exception is no longer needed, or when the exception file itself is invalid.

Usage (repo root):
  python3 tools/check_refs.py                     # check (what src/build.py runs)
  python3 tools/check_refs.py --draft             # treat not-yet-approved exceptions as locked (feature branch only)
  python3 tools/check_refs.py --write-exceptions  # first run only: write registry/exceptions.json (refused if it exists)
"""
import argparse, collections, difflib, hashlib, json, os, re, shutil, subprocess, sys, unicodedata

ERROR_CODES = ('E1', 'E2', 'E3', 'E6', 'E7', 'E9')
EXCEPTABLE = ('E1', 'E2', 'E3')          # E9 (G1 needs E9 = 0), E6, E7 can never be excepted
STATUS_OF = {'E1': 'unresolved', 'E2': 'ambiguous', 'E3': 'ambiguous'}
# data written by Apps Script / Actions, not by builds: loaded (W11 reads reports), never walked (design Q13, G5)
EXTERNAL_FILES = {'reports.js': '玩家回報（Apps Script 寫入）', 'jmmeta.js': '探索地圖紀錄（Actions 寫入）',
                  'formcfg.js': '回報表單設定（Apps Script 寫入）'}
DATA_FILES = ['data.js', 'data23.js', 'bosses.js', 'hints.js', 'codex.js', 'mobphotos.js', 'mainq.js', 'equip.js',
              'props.js', 'gameinfo.js', 'buyback.js', 'npcs.js', 'changelog.js', 'recipes.js', 'classes.js',
              'gameskills.js', 'events.js', 'gacha.js', 'gamestats.js', 'sets.js', 'zhnames.js', 'staticons.js',
              'gameicons.js', 'recicons.js']

# ------------------------------------------------------------------ normalisation (design lines 187-191)
_FW = {c: c - 0xFEE0 for c in range(0xFF01, 0xFF5F)}
_FW[0x3000] = 0x20
_QT = str.maketrans({'’': "'", '‘': "'", '“': '"', '”': '"'})


def safe(s):
    """always applied: case, surrounding / repeated spaces, curly quotes, full-width -> half-width"""
    if s is None:
        return None
    s = unicodedata.normalize('NFC', str(s)).translate(_FW).translate(_QT).casefold()
    return re.sub(r'\s+', ' ', s).strip()


def risky(k):
    """applied only when the result has no collision inside the same kind: accents, roman numeral I / letter l"""
    k = ''.join(c for c in unicodedata.normalize('NFD', k) if unicodedata.category(c) != 'Mn')
    return ' '.join(t.replace('l', 'i') if re.fullmatch(r'[ilvx]+', t) else t for t in k.split(' '))


def plural_variants(k):
    """candidates only (line 190): singular / plural; never counted as resolved"""
    out = set()
    for i, t in enumerate(k.split(' ')):
        ts = k.split(' ')
        if len(t) > 3 and t.endswith('s'):
            ts[i] = t[:-1]
        else:
            ts[i] = t + 's'
        out.add(' '.join(ts))
    return out


QTY = re.compile(r'^\s*(\d+)\s+(.+?)\s*$')             # "24 Minerai de Fer"
TIMES = re.compile(r'^(.+?)\s*[×x]\s*\d+\s*$')          # "Colossus Fragments ×3"

# ------------------------------------------------------------------ container shapes (declared, never inferred)
# map: the dict keys are data (each key is a record / a name); tuple: list positions have fixed meanings.
MAPS = {
    'SAO.ZONES', 'SAO.PHOTO', 'SAO.ITEMS', 'SAO.ITEMS{}.st', 'SAO23_ITEMS', 'SAO23_ITEMS{}[6]', 'SAO23.floors',
    'SAO23.floors{}.zones', 'SAO23.extra', 'SAO23.unknown', 'SAO_HINTS', 'SAO_HINTS{}', 'SAO_CODEX', 'SAO_CODEX{}',
    'SAO_MOBPHOTO.srcs', 'SAO_MOBPHOTO.by', 'SAO_MOBPHOTO.by{}', 'SAO_MAINQ', 'SAO_MAINQ{}[].en', 'SAO_MAINQ{}[].img',
    'SAO_EQUIP[][7]', 'SAO_PROPS[][6]', 'SAO_BUYBACK.shops', 'SAO_BUYBACK.items', 'SAO_NPCS', 'SAO_NPC_CALC',
    'SAO_CHANGELOG_SUM', 'SAO_RECIPES', 'SAO_RECIPE_QTY', 'SAO_GAMESKILLS', 'SAO_GAMESKILLS{}.icons',
    'SAO_EVENTS.eqPatch.items', 'SAO_EVENTS.eqPatch.items{}.set', 'SAO_GAMESTATS.items', 'SAO_ZHNAMES.search',
    'SAO_ZHNAMES.sets', 'SAO_ZHNAMES.mobs', 'SAO_ZHNAMES.mobsByName', 'SAO_ZHNAMES.places', 'SAO_ZHNAMES.terms',
    'SAO_ZHNAMES.npcEn', 'SAO_ZHNAMES.npcs', 'SAO_ZHNAMES.quests', 'SAO_ZHNAMES.quests{}.obj', 'SAO_STATICONS',
    'SAO_GAMEICONS', 'SAO_RECICONS', 'SAO_BOSSES.world[]', 'SAO_CLASSES[]', 'SAO_EVENTS.dungeons[]',
}
TUPLES = {
    'SAO.BOSS_SPAWNS[]', 'SAO.M[].drops[]', 'SAO.SPOTS[].dg.loot[]', 'SAO.QUESTS[].need[]', 'SAO.QUESTS[].kill',
    'SAO.ITEMS{}.set.tiers[]', 'SAO23_ITEMS{}', 'SAO23.floors{}.M[].drops[]', 'SAO23.floors{}.spots[].dg.loot[]',
    'SAO23.floors{}.BOSS_SPAWNS[]', 'SAO_HINTS{}{}', 'SAO_EQUIP[]', 'SAO_PROPS[]', 'SAO_NPCS{}[]',
    'SAO_CHANGELOG[]', 'SAO_RECIPES{}.items[]', 'SAO_RECIPES{}.items[][3][]', 'SAO_BOSSES.uniqueWiki[]',
    'SAO_EVENTS.dungeons[]{}[]', 'SAO_SETS.sets[].tiers[]', 'SAO_MAINQ{}[].s[]', 'SAO_BOSSES.world[]{}[]',
    'SAO_CLASSES[]{}[]', 'SAO_EVENTS.dungeons[]{}.rows[]', 'SAO_EVENTS.dungeons[]{}.mats[]',
    'SAO_EVENTS.dungeons[]{}.loot[]', 'SAO_GAMESTATS.items{}.st[]', 'SAO_MAINQ{}[].img{}[]',
}

# ------------------------------------------------------------------ COVERAGE: every field signature is scanned or excluded
# Signature format: '.field' dict field, '{}' map entry, '{key}' the key of a map entry, '[]' list element,
# '[N]' tuple position.  Exact signatures only (no wildcards): a field listed in neither COVERAGE nor SKIP is E9.
COVERAGE = {
    'SAO.BOSS_SPAWNS[][0]': 'mob_bs',
    'SAO.M[].drops[][0]': 'item_drop',
    'SAO.M[].zone': 'zone_ref',
    'SAO.M[].zone[]': 'zone_ref',
    'SAO.ITEMS{}.fr': 'item_fr',
    'SAO.SPOTS[].mons[]': 'mob_spot',
    'SAO.SPOTS[].items[]': 'item_gather',
    'SAO.SPOTS[].zone': 'zone_ref',
    'SAO.SPOTS[].zone[]': 'zone_ref',
    'SAO.SPOTS[].dg.loot[][0]': 'item_loot',
    'SAO.SPOTS[].dg.loot[][1]': 'mob_loot',
    'SAO.QUESTS[].need[][0]': 'item_quest',
    'SAO.QUESTS[].bonus': 'item_bonus',
    'SAO.QUESTS[].kill[0][]': 'mob_kill',
    'SAO.QUESTS[].npc': 'npc_quest',
    'SAO.QUESTS[].town': 'town_ref',
    'SAO23_ITEMS{}[0]': 'item_fr',
    'SAO23.floors{}.M[].drops[][0]': 'item_drop',
    'SAO23.floors{}.M[].zone': 'zone_ref',
    'SAO23.floors{}.M[].zone[]': 'zone_ref',
    'SAO23.floors{}.spots[].mons[]': 'mob_spot',
    'SAO23.floors{}.spots[].zone': 'zone_ref',
    'SAO23.floors{}.spots[].zone[]': 'zone_ref',
    'SAO23.floors{}.spots[].dg.loot[][0]': 'item_loot',
    'SAO23.floors{}.spots[].dg.loot[][1]': 'mob_loot',
    'SAO23.floors{}.BOSS_SPAWNS[][0]': 'mob_bs',
    'SAO23.extra{key}': 'item_extra',
    'SAO_BOSSES.world[]{}[][0]': 'item_roulette',
    'SAO_BOSSES.world[]{}[][1]': 'item_roulette_fr',
    'SAO_HINTS{}{key}': 'mob_hint',
    'SAO_CODEX{}{key}': 'codex_num',
    'SAO_MOBPHOTO.by{}{key}': 'mob_photo',
    'SAO_MAINQ{}[].npc': 'npc_mainq',
    'SAO_GAMEINFO.items[].oid[]': 'gi_oid',
    'SAO_GAMEINFO.items[].site': 'gi_site',
    'SAO_GAMEINFO.items[].obt[]': 'gi_obt',
    'SAO_BUYBACK.items{key}': 'npc_buyback',
    'SAO_BUYBACK.items{}[][0]': 'item_buyback',
    'SAO_BUYBACK.shops{key}': 'npc_shopmap',
    'SAO_NPC_CALC{key}': 'npc_calc',
    'SAO_RECIPES{key}': 'npc_recipe',
    'SAO_RECIPES{}.items[][0]': 'rec_out_id',
    'SAO_RECIPES{}.items[][1]': 'rec_out_name',
    'SAO_RECIPES{}.items[][3][][0]': 'item_mat',
    'SAO_EVENTS.dungeons[]{}.loot[][0]': 'item_loot',
    'SAO_EVENTS.dungeons[]{}.loot[][1]': 'mob_loot_any',
    'SAO_EVENTS.eqPatch.items{}.en': 'item_patch',
    'SAO_EVENTS.eqPatch.items{key}': 'cat_id_key',
    'SAO_GACHA.banners[].items[].en': 'item_gacha',
    'SAO_GACHA.banners[].items[].id': 'gacha_id',
    'SAO_GAMESTATS.items{key}': 'cat_id_key',
    'SAO_SETS.sets[].members[]': 'item_setmember',
    'SAO_SETS.potions[].name': 'item_potion',
    'SAO_ZHNAMES.items[].ids[]': 'zh_ids',
    'SAO_ZHNAMES.mobs{key}': 'codex_num',
    'SAO_ZHNAMES.mobsByName{key}': 'mob_zh',
    'SAO_ZHNAMES.places{key}': 'place_zh',
    'SAO_ZHNAMES.npcs{key}': 'npc_zh',
    'SAO_ZHNAMES.npcEn{key}': 'npc_zh',
    'SAO_ZHNAMES.quests{key}': 'quest_zh',
    'SAO_ZHNAMES.sets{key}': 'set_zh',
    'SAO_GAMEICONS{key}': 'item_icon',
    'SAO_RECICONS{key}': 'item_recicon',
}

SKIP_REASONS = {
    'R1': ('不是引用（數值、座標、說明文字、日期、旗標）', '—'),
    'R2': ('區域 id 本身（被引用的一方）', '—'),
    'R3': ('區域排序，值是 ZONES 的鍵（網站內部 id）', '階段 3'),
    'R4': ('遊戲圖鑑編號（E3 另外檢查）', '—'),
    'R5': ('怪物紀錄本身（被引用的一方）', '—'),
    'R6': ('怪物舊名（名字索引的一部分）', '—'),
    'R7': ('怪物圖片的鍵（只有 3 張舊圖，網站內部用）', '階段 4'),
    'R8': ('本站物品紀錄本身（被引用的一方）', '—'),
    'R9': ('套裝顯示名稱（說明文字）', '階段 2'),
    'R10': ('城鎮紀錄本身（被引用的一方）', '—'),
    'R11': ('地點紀錄本身（被引用的一方）或說明文字', '—'),
    'R12': ('地下城鑰匙名（顯示文字，網站另外用配方對鑰匙）', '階段 2'),
    'R13': ('任務原文', '階段 4'),
    'R14': ('支線標題（被引用的一方）', '—'),
    'R15': ('說明文字', '階段 4'),
    'R16': ('樓層號碼', '—'),
    'R17': ('區域排序，值是 zones 的鍵（網站內部 id）', '階段 3'),
    'R18': ('任務原文裡對不到物品的名稱（已知未知，說明在 note）', '階段 4'),
    'R19': ('世界首領資料（說明、時間、攻擊招式；物品只有輪盤欄位掃描）', '階段 2'),
    'R20': ('遊戲圖鑑原文', '—'),
    'R21': ('官網新聞的原文、圖片路徑和數值', '—'),
    'R22': ('主線步驟文字、座標、圖片', '階段 4'),
    'R23': ('主線標題（被引用的一方）', '—'),
    'R24': ('主線獎勵（自由文字）', '階段 4'),
    'R25': ('主線舊標題（名字索引的一部分）', '—'),
    'R26': ('官網圖鑑匯入的紀錄本身', '—'),
    'R27': ('遊戲英文名（名字索引的一部分）', '—'),
    'R28': ('NPC 紀錄本身（被引用的一方）', '—'),
    'R29': ('更新紀錄文字', '—'),
    'R30': ('配方產量的鍵（NPC|產出，網站內部組合鍵）', '階段 2'),
    'R31': ('職業資料（wiki 文字、屬性、技能）', '—'),
    'R32': ('遊戲技能文字和圖示路徑', '—'),
    'R33': ('活動公告文字、兌換表、碎片表', '階段 2'),
    'R34': ('遊戲英文名（小寫，W7 跨檔線索用）', '—'),
    'R35': ('套裝名稱本身（被引用的一方）', '—'),
    'R36': ('官方中文名本身（顯示文字）', '—'),
    'R37': ('只用在搜尋的別名（鍵是 e|id／p|id）', '階段 2'),
    'R38': ('遊戲取得途徑的商店名（顯示用對照）', '階段 3'),
    'R39': ('官方中文名本身（名字索引的一部分）', '—'),
    'R40': ('數值圖示（鍵是數值名，不是物品）', '—'),
    'R41': ('圖示檔路徑（E7 釘選另外檢查）', '—'),
    'R42': ('圖示檔路徑', '—'),
    'RN': ('名稱文字（首領、活動怪物、官網新聞的法文名、區域標籤），不在 v5 階段 1 涵蓋表；之後依種類搬家時處理', '階段 3／4'),
}
SKIP = {
    'SAO.BOSS_SPAWNS[][1]': 'R1',
    'SAO.BOSS_SPAWNS[][2]': 'R1',
    'SAO.BOSS_SPAWNS[][3]': 'R1',
    'SAO.MAP': 'R1',
    'SAO.STATUS.label.t': 'R1',
    'SAO.STATUS.label.c': 'R1',
    'SAO.STATUS.label.d': 'R1',
    'SAO.STATUS.npc.t': 'R1',
    'SAO.STATUS.npc.c': 'R1',
    'SAO.STATUS.npc.d': 'R1',
    'SAO.STATUS.est.t': 'R1',
    'SAO.STATUS.est.c': 'R1',
    'SAO.STATUS.est.d': 'R1',
    'SAO.STATUS.player.t': 'R1',
    'SAO.STATUS.player.c': 'R1',
    'SAO.STATUS.player.d': 'R1',
    'SAO.STATUS.unk.t': 'R1',
    'SAO.STATUS.unk.c': 'R1',
    'SAO.STATUS.unk.d': 'R1',
    'SAO.STATUS.user.t': 'R1',
    'SAO.STATUS.user.c': 'R1',
    'SAO.STATUS.user.d': 'R1',
    'SAO.STATUS.ref.t': 'R1',
    'SAO.STATUS.ref.c': 'R1',
    'SAO.STATUS.ref.d': 'R1',
    'SAO.ZONES{key}': 'R2',
    'SAO.ZONES{}.n': 'R1',
    'SAO.ZONES{}.zh': 'R1',
    'SAO.ZONES{}.zl': 'R1',
    'SAO.ZONES{}.fr': 'R1',
    'SAO.ZONES{}.note': 'R1',
    'SAO.ZONES{}.old': 'R1',
    'SAO.ZONE_ORDER[]': 'R3',
    'SAO.M[].id': 'R1',
    'SAO.M[].num': 'R4',
    'SAO.M[].name': 'R5',
    'SAO.M[].type': 'R1',
    'SAO.M[].beh': 'R1',
    'SAO.M[].diff': 'R1',
    'SAO.M[].drops[][1]': 'R1',
    'SAO.M[].note': 'R1',
    'SAO.M[].icon': 'R1',
    'SAO.M[].aka[]': 'R6',
    'SAO.M[].lvShot': 'R1',
    'SAO.PHOTO{key}': 'R7',
    'SAO.PHOTO{}': 'R1',
    'SAO.ITEMS{key}': 'R8',
    'SAO.ITEMS{}.id': 'R1',
    'SAO.ITEMS{}.r': 'R1',
    'SAO.ITEMS{}.lv': 'R1',
    'SAO.ITEMS{}.cat': 'R1',
    'SAO.ITEMS{}.lore': 'R1',
    'SAO.ITEMS{}.dmg': 'R1',
    'SAO.ITEMS{}.st{key}': 'R1',
    'SAO.ITEMS{}.st{}': 'R1',
    'SAO.ITEMS{}.ic': 'R1',
    'SAO.ITEMS{}.st': 'R1',
    'SAO.ITEMS{}.use[]': 'R1',
    'SAO.ITEMS{}.locked': 'R1',
    'SAO.ITEMS{}.note': 'R1',
    'SAO.ITEMS{}.src': 'R1',
    'SAO.ITEMS{}.vanilla': 'R1',
    'SAO.ITEMS{}.icsrc': 'R1',
    'SAO.ITEMS{}.set.name': 'R9',
    'SAO.ITEMS{}.set.tiers[][0]': 'R1',
    'SAO.ITEMS{}.set.tiers[][1]': 'R1',
    'SAO.TOWNS[].id': 'R10',
    'SAO.TOWNS[].tp': 'R10',
    'SAO.TOWNS[].n': 'R10',
    'SAO.TOWNS[].csrc': 'R10',
    'SAO.TOWNS[].old': 'R10',
    'SAO.TOWNS[].zh': 'R10',
    'SAO.TOWNS[].x': 'R10',
    'SAO.TOWNS[].z': 'R10',
    'SAO.TOWNS[].note': 'R10',
    'SAO.SPOTS[].src': 'R11',
    'SAO.SPOTS[].id': 'R11',
    'SAO.SPOTS[].area[][]': 'R11',
    'SAO.SPOTS[].kind': 'R11',
    'SAO.SPOTS[].n': 'R11',
    'SAO.SPOTS[].csrc': 'R11',
    'SAO.SPOTS[].old': 'R11',
    'SAO.SPOTS[].nsrc': 'R11',
    'SAO.SPOTS[].zh': 'R11',
    'SAO.SPOTS[].x': 'R11',
    'SAO.SPOTS[].z': 'R11',
    'SAO.SPOTS[].note': 'R11',
    'SAO.SPOTS[].tp': 'R11',
    'SAO.SPOTS[].game': 'R11',
    'SAO.SPOTS[].dg.date': 'R11',
    'SAO.SPOTS[].dg.title': 'RN',
    'SAO.SPOTS[].dg.boss': 'RN',
    'SAO.SPOTS[].dg.bossZh': 'RN',
    'SAO.SPOTS[].dg.key': 'R12',
    'SAO.SPOTS[].dg.modes[]': 'R11',
    'SAO.SPOTS[].dg.easy[][]': 'R11',
    'SAO.SPOTS[].dg.loot[][2]': 'R11',
    'SAO.SPOTS[].gt': 'R11',
    'SAO.QUESTS[].x': 'R1',
    'SAO.QUESTS[].z': 'R1',
    'SAO.QUESTS[].need[][1]': 'R1',
    'SAO.QUESTS[].need[][2]': 'R1',
    'SAO.QUESTS[].xp': 'R1',
    'SAO.QUESTS[].money': 'R1',
    'SAO.QUESTS[].raw': 'R13',
    'SAO.QUESTS[].id': 'R1',
    'SAO.QUESTS[].kill[1]': 'R1',
    'SAO.QUESTS[].title': 'R14',
    'SAO.QUESTS[].src': 'R1',
    'SAO.QUESTS[].tnote': 'R15',
    'SAO23_ITEMS{key}': 'R8',
    'SAO23_ITEMS{}[1]': 'R1',
    'SAO23_ITEMS{}[2]': 'R1',
    'SAO23_ITEMS{}[3]': 'R1',
    'SAO23_ITEMS{}[4]': 'R1',
    'SAO23_ITEMS{}[5]': 'R1',
    'SAO23_ITEMS{}[6]{key}': 'R1',
    'SAO23_ITEMS{}[6]{}': 'R1',
    'SAO23_ITEMS{}[7]': 'R1',
    'SAO23_ITEMS{}[6]': 'R1',
    'SAO23.floors{key}': 'R16',
    'SAO23.floors{}.name': 'R1',
    'SAO23.floors{}.lv': 'R1',
    'SAO23.floors{}.boss': 'R1',
    'SAO23.floors{}.status': 'R1',
    'SAO23.floors{}.opened': 'R1',
    'SAO23.floors{}.map.img': 'R1',
    'SAO23.floors{}.map.lo': 'R1',
    'SAO23.floors{}.map.size': 'R1',
    'SAO23.floors{}.map.x0': 'R1',
    'SAO23.floors{}.map.z0': 'R1',
    'SAO23.floors{}.map.clip.c': 'R1',
    'SAO23.floors{}.map.clip.r': 'R1',
    'SAO23.floors{}.map.note': 'R1',
    'SAO23.floors{}.zones{key}': 'R2',
    'SAO23.floors{}.zones{}.n': 'R1',
    'SAO23.floors{}.zones{}.zh': 'R1',
    'SAO23.floors{}.zones{}.note': 'R1',
    'SAO23.floors{}.order[]': 'R17',
    'SAO23.floors{}.M[].id': 'R1',
    'SAO23.floors{}.M[].num': 'R1',
    'SAO23.floors{}.M[].name': 'R5',
    'SAO23.floors{}.M[].type': 'R1',
    'SAO23.floors{}.M[].beh': 'R1',
    'SAO23.floors{}.M[].diff': 'R1',
    'SAO23.floors{}.M[].drops[][1]': 'R1',
    'SAO23.floors{}.M[].note': 'R1',
    'SAO23.floors{}.M[].icon': 'R1',
    'SAO23.floors{}.M[].gameDrop': 'R1',
    'SAO23.floors{}.M[].news': 'R1',
    'SAO23.floors{}.towns[].id': 'R10',
    'SAO23.floors{}.towns[].n': 'R10',
    'SAO23.floors{}.towns[].zh': 'R10',
    'SAO23.floors{}.towns[].x': 'R10',
    'SAO23.floors{}.towns[].z': 'R10',
    'SAO23.floors{}.towns[].src': 'R10',
    'SAO23.floors{}.towns[].note': 'R10',
    'SAO23.floors{}.towns[].old': 'R10',
    'SAO23.floors{}.spots[].id': 'R11',
    'SAO23.floors{}.spots[].kind': 'R11',
    'SAO23.floors{}.spots[].n': 'R11',
    'SAO23.floors{}.spots[].zh': 'R11',
    'SAO23.floors{}.spots[].old': 'R11',
    'SAO23.floors{}.spots[].x': 'R11',
    'SAO23.floors{}.spots[].z': 'R11',
    'SAO23.floors{}.spots[].src': 'R11',
    'SAO23.floors{}.spots[].note': 'R11',
    'SAO23.floors{}.spots[].dg.date': 'R11',
    'SAO23.floors{}.spots[].dg.title': 'RN',
    'SAO23.floors{}.spots[].dg.boss': 'RN',
    'SAO23.floors{}.spots[].dg.bossZh': 'RN',
    'SAO23.floors{}.spots[].dg.key': 'R12',
    'SAO23.floors{}.spots[].dg.modes[]': 'R11',
    'SAO23.floors{}.spots[].dg.easy[][]': 'R11',
    'SAO23.floors{}.spots[].dg.loot[][2]': 'R11',
    'SAO23.floors{}.spots[].dg.lootNote': 'R11',
    'SAO23.floors{}.spots[].u': 'R11',
    'SAO23.floors{}.spots[].area[][]': 'R11',
    'SAO23.floors{}.BOSS_SPAWNS[][1]': 'R1',
    'SAO23.floors{}.BOSS_SPAWNS[][2]': 'R1',
    'SAO23.floors{}.BOSS_SPAWNS[][3]': 'R1',
    'SAO23.floors{}.map.blank': 'R1',
    'SAO23.floors{}.zones{}.zhKeep': 'R1',
    'SAO23.floors{}.zones{}.news': 'R1',
    'SAO23.floors{}.M[].lvShot': 'R1',
    'SAO23.floors{}.M[].drops[][2]': 'R1',
    'SAO23.floors{}.spots[].tp': 'R11',
    'SAO23.extra{}.use[]': 'R1',
    'SAO23.extra{}.note': 'R1',
    'SAO23.extra{}.slot': 'R1',
    'SAO23.extra{}.src': 'R1',
    'SAO23.unknown{key}': 'R18',
    'SAO23.unknown{}.note': 'R1',
    'SAO_BOSSES.world[]{key}': 'R19',
    'SAO_BOSSES.world[]{}': 'R19',
    'SAO_BOSSES.world[]{}[].day': 'R19',
    'SAO_BOSSES.world[]{}[].time': 'R19',
    'SAO_BOSSES.world[]{}[].zone': 'R19',
    'SAO_BOSSES.world[]{}[].minutes': 'R19',
    'SAO_BOSSES.world[]{}[][2]': 'R19',
    'SAO_BOSSES.unique[].id': 'R19',
    'SAO_BOSSES.unique[].img': 'R19',
    'SAO_BOSSES.unique[].imgFront': 'R19',
    'SAO_BOSSES.unique[].name': 'R19',
    'SAO_BOSSES.unique[].fr': 'R19',
    'SAO_BOSSES.unique[].zh': 'R19',
    'SAO_BOSSES.unique[].unit': 'R19',
    'SAO_BOSSES.unique[].floor': 'R19',
    'SAO_BOSSES.unique[].level': 'R19',
    'SAO_BOSSES.unique[].levelSrc': 'R19',
    'SAO_BOSSES.unique[].available': 'R19',
    'SAO_BOSSES.unique[].attacks[][]': 'R19',
    'SAO_BOSSES.unique[].phases': 'R19',
    'SAO_BOSSES.unique[].note': 'R19',
    'SAO_BOSSES.uniqueRules[]': 'R19',
    'SAO_BOSSES.uniqueWiki[][0]': 'R19',
    'SAO_BOSSES.uniqueWiki[][1]': 'R19',
    'SAO_BOSSES.uniqueWiki[][2]': 'R19',
    'SAO_BOSSES.uniqueWiki[][3]': 'R19',
    'SAO_BOSSES.uniqueWiki[][4]': 'R19',
    'SAO_BOSSES.wikiWorld[][]': 'R19',
    'SAO_HINTS{key}': 'R16',
    'SAO_HINTS{}{}[0]': 'R1',
    'SAO_HINTS{}{}[1]': 'R1',
    'SAO_HINTS{}{}[2]': 'R1',
    'SAO_CODEX{key}': 'R16',
    'SAO_CODEX{}{}.n': 'R20',
    'SAO_CODEX{}{}.reg': 'RN',
    'SAO_CODEX{}{}.desc': 'R20',
    'SAO_MOBPHOTO.srcs{key}': 'R21',
    'SAO_MOBPHOTO.srcs{}.title': 'R21',
    'SAO_MOBPHOTO.srcs{}.title_fr': 'R21',
    'SAO_MOBPHOTO.srcs{}.url': 'R21',
    'SAO_MOBPHOTO.srcs{}.date': 'R21',
    'SAO_MOBPHOTO.srcs{}.title_tw': 'R21',
    'SAO_MOBPHOTO.by{key}': 'R16',
    'SAO_MOBPHOTO.by{}{}.old[].fr': 'RN',
    'SAO_MOBPHOTO.by{}{}.old[].ch[]': 'R21',
    'SAO_MOBPHOTO.by{}{}.old[].v': 'R21',
    'SAO_MOBPHOTO.by{}{}.old[].f': 'R21',
    'SAO_MOBPHOTO.by{}{}.f': 'R21',
    'SAO_MOBPHOTO.by{}{}.rows[].fr': 'RN',
    'SAO_MOBPHOTO.by{}{}.rows[].ch[]': 'R21',
    'SAO_MOBPHOTO.by{}{}.rows[].v': 'R21',
    'SAO_MOBPHOTO.by{}{}.rows[].tw': 'RN',
    'SAO_MOBPHOTO.by{}{}.rows[].f': 'R21',
    'SAO_MOBPHOTO.by{}{}.z[]': 'RN',
    'SAO_MOBPHOTO.by{}{}.lv': 'R21',
    'SAO_MAINQ{key}': 'R22',
    'SAO_MAINQ{}[].t': 'R23',
    'SAO_MAINQ{}[].lv': 'R22',
    'SAO_MAINQ{}[].s[][0]': 'R22',
    'SAO_MAINQ{}[].s[][1]': 'R22',
    'SAO_MAINQ{}[].s[][2]': 'R22',
    'SAO_MAINQ{}[].tip': 'R22',
    'SAO_MAINQ{}[].n': 'R22',
    'SAO_MAINQ{}[].rw': 'R24',
    'SAO_MAINQ{}[].s[][3]': 'R22',
    'SAO_MAINQ{}[].d': 'R22',
    'SAO_MAINQ{}[].en{key}': 'R22',
    'SAO_MAINQ{}[].en{}': 'R22',
    'SAO_MAINQ{}[].img{key}': 'R22',
    'SAO_MAINQ{}[].img{}[][0]': 'R22',
    'SAO_MAINQ{}[].img{}[][1]': 'R22',
    'SAO_MAINQ{}[].aka': 'R25',
    'SAO_EQUIP[][0]': 'R26',
    'SAO_EQUIP[][1]': 'R26',
    'SAO_EQUIP[][2]': 'R26',
    'SAO_EQUIP[][3]': 'R26',
    'SAO_EQUIP[][4]': 'R26',
    'SAO_EQUIP[][5]': 'R26',
    'SAO_EQUIP[][6]': 'R26',
    'SAO_EQUIP[][7]{key}': 'R26',
    'SAO_EQUIP[][7]{}': 'R26',
    'SAO_EQUIP[][8]': 'R26',
    'SAO_EQUIP[][9]': 'R26',
    'SAO_PROPS[][0]': 'R26',
    'SAO_PROPS[][1]': 'R26',
    'SAO_PROPS[][2]': 'R26',
    'SAO_PROPS[][3]': 'R26',
    'SAO_PROPS[][4]': 'R26',
    'SAO_PROPS[][5]': 'R26',
    'SAO_PROPS[][6]{key}': 'R26',
    'SAO_PROPS[][6]{}': 'R26',
    'SAO_PROPS[][7]': 'R26',
    'SAO_GAMEINFO.date': 'R1',
    'SAO_GAMEINFO.items[].en': 'R27',
    'SAO_GAMEINFO.items[].lvl': 'R1',
    'SAO_GAMEINFO.items[].date': 'R1',
    'SAO_GAMEINFO.items[].desc': 'R1',
    'SAO_GAMEINFO.items[].note': 'R1',
    'SAO_BUYBACK.shops{}': 'R1',
    'SAO_BUYBACK.items{}[][]': 'R1',
    'SAO_NPCS{key}': 'R16',
    'SAO_NPCS{}[][0]': 'R1',
    'SAO_NPCS{}[][1]': 'R28',
    'SAO_NPCS{}[][2]': 'R1',
    'SAO_NPCS{}[][3]': 'R1',
    'SAO_NPCS{}[][4]': 'R1',
    'SAO_NPCS{}[][5]': 'R1',
    'SAO_NPC_CALC{}.m': 'R1',
    'SAO_NPC_CALC{}.k': 'R1',
    'SAO_NPC_CALC{}.d': 'R1',
    'SAO_NPC_CALC{}.t': 'R1',
    'SAO_CHANGELOG[][0]': 'R29',
    'SAO_CHANGELOG[][1][]': 'R29',
    'SAO_CHANGELOG_SUM{key}': 'R29',
    'SAO_CHANGELOG_SUM{}[]': 'R29',
    'SAO_RECIPES{}.floor': 'R1',
    'SAO_RECIPES{}.items[][2]': 'R1',
    'SAO_RECIPES{}.items[][3][][1]': 'R1',
    'SAO_RECIPES{}.items[][4]': 'R1',
    'SAO_RECIPES{}.items[][5]': 'R1',
    'SAO_RECIPES{}.items[][6]': 'R1',
    'SAO_RECIPES{}.items[][7]': 'R1',
    'SAO_RECIPES{}.items[][8]': 'R1',
    'SAO_RECIPE_QTY{key}': 'R30',
    'SAO_RECIPE_QTY{}': 'R1',
    'SAO_CLASSES[]{key}': 'R31',
    'SAO_CLASSES[]{}': 'R31',
    'SAO_CLASSES[]{}[][0]': 'R31',
    'SAO_CLASSES[]{}[][1]': 'R31',
    'SAO_CLASSES[]{}[][2]': 'R31',
    'SAO_CLASSES[]{}[][3]': 'R31',
    'SAO_CLASSES[]{}.shield': 'R31',
    'SAO_CLASSES[]{}.sword': 'R31',
    'SAO_CLASSES[]{}[][4]': 'R31',
    'SAO_CLASSES[]{}.dagger': 'R31',
    'SAO_CLASSES[]{}.staff_mage': 'R31',
    'SAO_CLASSES[]{}.staff_shaman': 'R31',
    'SAO_CLASSES[]{}.crossbow': 'R31',
    'SAO_CLASSES[]{}.bow': 'R31',
    'SAO_GAMESKILLS{key}': 'R32',
    'SAO_GAMESKILLS{}.date': 'R32',
    'SAO_GAMESKILLS{}.lv': 'R32',
    'SAO_GAMESKILLS{}.icons{key}': 'R32',
    'SAO_GAMESKILLS{}.icons{}': 'R32',
    'SAO_GAMESKILLS{}.list[].g': 'R32',
    'SAO_GAMESKILLS{}.list[].fr': 'R32',
    'SAO_GAMESKILLS{}.list[].en': 'R32',
    'SAO_GAMESKILLS{}.list[].zh': 'R32',
    'SAO_GAMESKILLS{}.list[].t': 'R32',
    'SAO_GAMESKILLS{}.list[].slot': 'R32',
    'SAO_GAMESKILLS{}.list[].max': 'R32',
    'SAO_GAMESKILLS{}.list[].d': 'R32',
    'SAO_GAMESKILLS{}.list[].dOff': 'R32',
    'SAO_GAMESKILLS{}.list[].lore': 'R32',
    'SAO_GAMESKILLS{}.list[].data[]': 'R32',
    'SAO_GAMESKILLS{}.list[].dz[]': 'R32',
    'SAO_GAMESKILLS{}.list[].base': 'R32',
    'SAO_EVENTS.dungeons[]{key}': 'R33',
    'SAO_EVENTS.dungeons[]{}': 'R33',
    'SAO_EVENTS.dungeons[]{}.title': 'R33',
    'SAO_EVENTS.dungeons[]{}.url': 'R33',
    'SAO_EVENTS.dungeons[]{}.date': 'R33',
    'SAO_EVENTS.dungeons[]{}[][0]': 'R33',
    'SAO_EVENTS.dungeons[]{}[][1]': 'R33',
    'SAO_EVENTS.dungeons[]{}[]': 'R33',
    'SAO_EVENTS.dungeons[]{}[].n': 'R33',
    'SAO_EVENTS.dungeons[]{}[].mobs[]': 'RN',
    'SAO_EVENTS.dungeons[]{}[].leader': 'RN',
    'SAO_EVENTS.dungeons[]{}[].frag': 'RN',
    'SAO_EVENTS.dungeons[]{}.n': 'R33',
    'SAO_EVENTS.dungeons[]{}.npc': 'RN',
    'SAO_EVENTS.dungeons[]{}.where': 'R33',
    'SAO_EVENTS.dungeons[]{}.mats[][0]': 'R33',
    'SAO_EVENTS.dungeons[]{}.mats[][1]': 'R33',
    'SAO_EVENTS.dungeons[]{}.note': 'R33',
    'SAO_EVENTS.dungeons[]{}.rows[][0]': 'R33',
    'SAO_EVENTS.dungeons[]{}.rows[][1]': 'R33',
    'SAO_EVENTS.dungeons[]{}.rows[][2]': 'R33',
    'SAO_EVENTS.dungeons[]{}.rows[][3]': 'R33',
    'SAO_EVENTS.dungeons[]{}.extra': 'R33',
    'SAO_EVENTS.dungeons[]{}.lvNote': 'R33',
    'SAO_EVENTS.dungeons[]{}.boss': 'R33',
    'SAO_EVENTS.dungeons[]{}.bossZh': 'R33',
    'SAO_EVENTS.dungeons[]{}.key': 'R33',
    'SAO_EVENTS.dungeons[]{}.modes[]': 'R33',
    'SAO_EVENTS.dungeons[]{}.easy[][]': 'R33',
    'SAO_EVENTS.dungeons[]{}.loot[][2]': 'R33',
    'SAO_EVENTS.eqPatch.src.title': 'R33',
    'SAO_EVENTS.eqPatch.src.url': 'R33',
    'SAO_EVENTS.eqPatch.src.date': 'R33',
    'SAO_EVENTS.eqPatch.items{}.set{key}': 'R33',
    'SAO_EVENTS.eqPatch.items{}.set{}': 'R33',
    'SAO_EVENTS.eqPatch.items{}.note': 'R33',
    'SAO_EVENTS.eqPatch.unmatched': 'R33',
    'SAO_GACHA.src.title': 'R1',
    'SAO_GACHA.src.url': 'R1',
    'SAO_GACHA.src.date': 'R1',
    'SAO_GACHA.banners[].n': 'R1',
    'SAO_GACHA.banners[].note': 'R1',
    'SAO_GAMESTATS.date': 'R1',
    'SAO_GAMESTATS.items{}.date': 'R1',
    'SAO_GAMESTATS.items{}.en': 'R34',
    'SAO_GAMESTATS.items{}.lvl': 'R1',
    'SAO_GAMESTATS.items{}.dmg': 'R1',
    'SAO_GAMESTATS.items{}.st[][0]': 'R1',
    'SAO_GAMESTATS.items{}.st[][1]': 'R1',
    'SAO_GAMESTATS.items{}.auc': 'R1',
    'SAO_GAMESTATS.items{}.r': 'R1',
    'SAO_GAMESTATS.items{}.st': 'R1',
    'SAO_SETS.date': 'R1',
    'SAO_SETS.sets[].name': 'R35',
    'SAO_SETS.sets[].zh': 'R1',
    'SAO_SETS.sets[].tiers[][0]': 'R1',
    'SAO_SETS.sets[].tiers[][1]': 'R1',
    'SAO_SETS.potions[].effects[]': 'R1',
    'SAO_ZHNAMES.date': 'R36',
    'SAO_ZHNAMES.search{key}': 'R37',
    'SAO_ZHNAMES.search{}[]': 'R36',
    'SAO_ZHNAMES.sets{}': 'R36',
    'SAO_ZHNAMES.mobs{}': 'R36',
    'SAO_ZHNAMES.mobsByName{}': 'R36',
    'SAO_ZHNAMES.places{}': 'R36',
    'SAO_ZHNAMES.terms{key}': 'R38',
    'SAO_ZHNAMES.terms{}': 'R36',
    'SAO_ZHNAMES.npcEn{}': 'R36',
    'SAO_ZHNAMES.npcs{}': 'R36',
    'SAO_ZHNAMES.items[].zh': 'R39',
    'SAO_ZHNAMES.items[].en': 'R39',
    'SAO_ZHNAMES.items[].fr': 'R39',
    'SAO_ZHNAMES.items[].src': 'R39',
    'SAO_ZHNAMES.items[].inf': 'R39',
    'SAO_ZHNAMES.quests{}.zh': 'R36',
    'SAO_ZHNAMES.quests{}.d': 'R36',
    'SAO_ZHNAMES.quests{}.reg': 'RN',
    'SAO_ZHNAMES.quests{}.obj{key}': 'R36',
    'SAO_ZHNAMES.quests{}.obj{}': 'R36',
    'SAO_STATICONS{key}': 'R40',
    'SAO_STATICONS{}': 'R40',
    'SAO_GAMEICONS{}': 'R41',
    'SAO_RECICONS{}': 'R42',
}


def cover(sig):
    if sig in COVERAGE:
        return sig, ('scan', COVERAGE[sig])
    if sig in SKIP:
        r, st = SKIP_REASONS[SKIP[sig]]
        return sig, ('skip', r, st)
    return None, None


# ------------------------------------------------------------------ loading
def load(root):
    node = shutil.which('node')
    if not node:
        sys.exit('check_refs: 找不到 Node（node）。階段 1 起 build 需要 Node 才能載入資料檔；請先安裝 Node。')
    p = subprocess.run([node, os.path.join(root, 'tools', 'check_refs_load.js'), root], capture_output=True)
    if p.returncode != 0:
        sys.exit('check_refs: 載入資料檔失敗：\n' + p.stderr.decode('utf-8', 'replace'))
    d = json.loads(p.stdout.decode('utf-8'))
    if d['errors']:
        sys.exit('check_refs: 資料檔執行錯誤：' + json.dumps(d['errors'], ensure_ascii=False))
    return d


def npc_note_keys(root):
    """NPC_NOTE lives in src/index.html (code); its keys are NPC names (v5 coverage table, NPC row)"""
    html = open(os.path.join(root, 'src', 'index.html'), encoding='utf-8').read()
    i = html.find('const NPC_NOTE={')
    if i < 0:
        return []
    seg = html[i:i + 60000]
    seg = seg[:seg.find('\n};')]
    start = html[:i].count('\n') + 1
    out = []
    for m in re.finditer(r'^\s*(?:get\s+)?"([^"]+)"\s*(?::|\()', seg, re.M):
        out.append((m.group(1), start + seg[:m.start()].count('\n')))
    return out


# ------------------------------------------------------------------ walking
class Leaf:
    __slots__ = ('sig', 'path', 'value', 'file', 'root')

    def __init__(self, sig, path, value, file, root):
        self.sig, self.path, self.value, self.file, self.root = sig, path, value, file, root


def walk(value, sig, path, file, rootname, out):
    if isinstance(value, dict):
        if sig in MAPS:
            for k, v in value.items():
                out.append(Leaf(sig + '{key}', path + [('key', k)], k, file, rootname))
                walk(v, sig + '{}', path + [('k', k)], file, rootname, out)
        else:
            for k, v in value.items():
                walk(v, sig + '.' + k, path + [('f', k)], file, rootname, out)
    elif isinstance(value, list):
        tup = sig in TUPLES
        for i, v in enumerate(value):
            walk(v, sig + ('[%d]' % i if tup else '[]'), path + [('i', i)], file, rootname, out)
    else:
        out.append(Leaf(sig, path, value, file, rootname))


def get(data, rootname, path):
    v = data[rootname]
    for kind, k in path:
        if kind == 'key':
            return k
        v = v[k]
    return v


# ------------------------------------------------------------------ the model (entities and name indexes)
class Index:
    def __init__(self, kind):
        self.kind = kind
        self.exact = collections.defaultdict(set)
        self.names = {}                     # entity -> display

    def add(self, name, ent, disp=None):
        k = safe(name)
        if not k:
            return
        self.exact[k].add(ent)
        self.names.setdefault(ent, disp or str(name))

    def finish(self):
        self.risky = collections.defaultdict(set)
        for k, ents in self.exact.items():
            self.risky[risky(k)] |= ents
        self.plural = collections.defaultdict(set)
        for k in self.exact:
            for p in plural_variants(k):
                self.plural[p].add(k)

    def resolve(self, name):
        """-> (status, entities, how)  status in resolved / ambiguous / unresolved"""
        k = safe(name)
        if not k:
            return 'unresolved', [], 'empty'
        if k in self.exact:
            e = sorted(self.exact[k])
            return ('resolved' if len(e) == 1 else 'ambiguous'), e, 'exact'
        r = risky(k)
        if r in self.risky:
            e = sorted(self.risky[r])
            return ('resolved' if len(e) == 1 else 'ambiguous'), e, 'normalized'
        return 'unresolved', [], 'none'

    def candidates(self, name):
        k = safe(name) or ''
        return sorted(self.plural.get(k, ()))


class Model:
    def __init__(self, d, root):
        D = self.D = d['data']
        self.root = root
        self.cat = {}
        for r in D['SAO_EQUIP']:
            self.cat[int(r[0])] = ('e', r[1], r)
        for r in D['SAO_PROPS']:
            self.cat[int(r[0])] = ('p', r[1], r)
        catfr = collections.defaultdict(list)
        for i, (kind, fr, _) in self.cat.items():
            catfr[safe(fr)].append(i)
        self.catfr = catfr
        ITEMS, S23 = D['SAO']['ITEMS'], D['SAO23_ITEMS']

        def via_fr(fr):
            ids = catfr.get(safe(fr), []) if fr else []
            return ids[0] if len(ids) == 1 else None
        self.item_ent = {}
        for k, v in ITEMS.items():
            i = via_fr(v.get('fr'))
            self.item_ent['I:' + k] = 'C:%d' % i if i is not None else 'I:' + k
        for k, v in S23.items():
            i = via_fr(v[0])
            self.item_ent['J:' + k] = 'C:%d' % i if i is not None else 'J:' + k
        self.record_names = {}
        for k in ITEMS:
            self.record_names[k] = self.item_ent['I:' + k]
        for k in S23:
            self.record_names.setdefault(k, self.item_ent['J:' + k])

        def name_ent(name):
            """game-only names (gameinfo without oid/site, zhnames g|) join the site record of the same name"""
            if name in self.record_names:
                return self.record_names[name]
            return 'G:' + safe(name)
        self.name_ent = name_ent
        ix = self.items = Index('item')
        for i, (kind, fr, _) in self.cat.items():
            ix.add(fr, 'C:%d' % i)
        for k, v in ITEMS.items():
            e = self.item_ent['I:' + k]
            ix.add(k, e)
            if v.get('fr'):
                ix.add(v['fr'], e)
        for k, v in S23.items():
            e = self.item_ent['J:' + k]
            ix.add(k, e)
            if v[0]:
                ix.add(v[0], e)
        # recipe outputs with a catalogue id are site records; id = null outputs are references only (B1)
        for npc, o in D['SAO_RECIPES'].items():
            for row in o['items']:
                if row[0] is not None and int(row[0]) in self.cat:
                    ix.add(row[1], 'C:%d' % int(row[0]))
        # phase 1: names that come with an id (gameinfo oid / site, zhnames e| p| i|)
        name_only_gi, name_only_zh = [], []
        for g in D['SAO_GAMEINFO']['items']:
            if g.get('oid') or g.get('site'):
                for e in self.gi_ents(g):
                    ix.add(g['en'], e)
            else:
                name_only_gi.append(g)
        for z in D['SAO_ZHNAMES']['items']:
            ids = z.get('ids') or []
            if ids and not any(i.startswith('g|') for i in ids):
                for e in self.zh_ents(z):
                    for n in (z.get('en'), z.get('fr'), z.get('zh')):
                        if n:
                            ix.add(n, e)
            else:
                name_only_zh.append(z)

        # phase 2: names without an id (game-only things) join the one entity their name already has, else their own
        def join(name):
            ents = ix.exact.get(safe(name), set())
            return next(iter(ents)) if len(ents) == 1 else 'G:' + safe(name)
        self.name_ent = join
        for g in name_only_gi:
            ix.add(g['en'], join(g['en']))
        for z in name_only_zh:
            ents = [e for e in self.zh_ents(z) if not e.startswith('G:')]
            gnames = [i.split('|', 1)[1] for i in z.get('ids') or [] if i.startswith('g|')]
            ents += [join(n) for n in gnames]
            if not z.get('ids') and z.get('en'):
                ents.append(join(z['en']))
            for e in sorted(set(ents)):
                for n in [z.get('en'), z.get('fr'), z.get('zh')] + gnames:
                    if n:
                        ix.add(n, e)
        ix.finish()
        self._mobs()
        self._npcs()
        self._places()
        self._quests()
        self._sets()

    def gi_ents(self, g):
        oid = [int(i) for i in (g.get('oid') or []) if int(i) in self.cat]
        if oid:
            return ['C:%d' % i for i in oid]
        if g.get('site'):
            s = g['site']
            if 'I:' + s in self.item_ent:
                return [self.item_ent['I:' + s]]
            if 'J:' + s in self.item_ent:
                return [self.item_ent['J:' + s]]
            return []
        return [self.name_ent(g['en'])]

    def zh_ents(self, z):
        out = []
        for idd in z.get('ids') or []:
            t, v = idd.split('|', 1)
            if t in ('e', 'p') and v.isdigit() and int(v) in self.cat:
                out.append('C:%d' % int(v))
            elif t == 'i':
                if 'I:' + v in self.item_ent:
                    out.append(self.item_ent['I:' + v])
                elif 'J:' + v in self.item_ent:
                    out.append(self.item_ent['J:' + v])
            elif t == 'g':
                out.append(self.name_ent(v))
        return sorted(set(out))

    # ---- monsters (per floor; references without a floor use all floors)
    def floors(self):
        D = self.D
        F = {1: dict(M=D['SAO']['M'], towns=D['SAO']['TOWNS'], spots=D['SAO']['SPOTS'], zones=D['SAO']['ZONES'])}
        for f in ('2', '3'):
            x = D['SAO23']['floors'][f]
            F[int(f)] = dict(M=x['M'], towns=x.get('towns', []), spots=x.get('spots', []), zones=x.get('zones', {}))
        return F

    def _mobs(self):
        self.F = self.floors()
        self.mob = {}
        self.mob_all = Index('mob')
        for f, x in self.F.items():
            ix = self.mob[f] = Index('mob')
            for i, m in enumerate(x['M']):
                e = 'M%d:%s' % (f, m.get('id') or i)
                for n in [m['name']] + list(m.get('aka') or []):
                    ix.add(n, e, m['name'])
                    self.mob_all.add(n, e, m['name'])
            ix.finish()
        self.mob_all.finish()
        self.mob_num = collections.defaultdict(list)
        for m in self.F[1]['M']:
            if m.get('num'):
                self.mob_num[m['num']].append(m['name'])

    def _npcs(self):
        D = self.D
        self.npc = {}
        self.npc_all = Index('npc')
        npcEn = D['SAO_ZHNAMES'].get('npcEn') or {}
        shops = D['SAO_BUYBACK'].get('shops') or {}
        for f in (1, 2, 3):
            ix = self.npc[f] = Index('npc')
            for i, n in enumerate(D['SAO_NPCS'].get(str(f)) or []):
                e = 'N%d:%d:%s' % (f, i, n[1])     # one entity per npcs.js row (same-name NPCs stay apart)
                for name in [n[1]]:
                    ix.add(name, e)
                    self.npc_all.add(name, e)
                if n[1] in npcEn:
                    ix.add(npcEn[n[1]], e)
                    self.npc_all.add(npcEn[n[1]], e)
                if n[1] in shops:                      # buyback.shops: site NPC -> shop name in the game text
                    ix.add(shops[n[1]], e)
                    self.npc_all.add(shops[n[1]], e)
            ix.finish()
        self.npc_all.finish()
        qn = set()
        for f in ('1', '2', '3'):
            for q in D['SAO_MAINQ'].get(f) or []:
                if q.get('npc'):
                    qn.add(safe(q['npc']))
        for q in D['SAO']['QUESTS']:
            if q.get('npc'):
                qn.add(safe(q['npc']))
        self.quest_npcs = qn

    def _places(self):
        self.place = {}
        self.zone_ids = {}
        self.place_ids = {}
        for f, x in self.F.items():
            ix = self.place[f] = Index('place')
            ids = set()
            for kind, arr in (('town', x['towns']), ('spot', x['spots'])):
                for p in arr:
                    e = 'P%d:%s:%s' % (f, kind, p['id'])   # a town and a spot can share an id
                    ids.add(p['id'])
                    for n in [p.get('n'), p.get('id'), p.get('tp'), p.get('csrc') if isinstance(p.get('csrc'), str) else None]:
                        if n:
                            ix.add(n, e, p.get('n'))
                    for o in re.split(r'\s*/\s*', str(p.get('old') or '')):
                        if o:
                            ix.add(o, e, p.get('n'))
            ix.finish()
            self.place_ids[f] = ids
            self.zone_ids[f] = set(x['zones'].keys())

    def _quests(self):
        D = self.D
        ix = self.quest = Index('quest')
        for f in ('1', '2', '3'):
            for i, q in enumerate(D['SAO_MAINQ'].get(f) or []):
                e = 'Q%s:%s' % (f, q['t'])
                ix.add(q['t'], e)
                for a in ([q['aka']] if isinstance(q.get('aka'), str) else (q.get('aka') or [])):
                    ix.add(a, e)
        for q in D['SAO']['QUESTS']:
            if q.get('title'):
                ix.add(q['title'], 'S:' + q['id'])
        ix.finish()

    def _sets(self):
        ix = self.set = Index('set')
        for s in self.D['SAO_SETS']['sets']:
            ix.add(s['name'], 'T:' + s['name'])
        ix.finish()


# ------------------------------------------------------------------ results
class Result:
    def __init__(self):
        self.rows = []          # every scanned leaf: dict(code?, file, key, sig, name, status, ents, how, line)

    def add(self, **kw):
        self.rows.append(kw)


def ent_label(m, e):
    if e.startswith('C:'):
        i = int(e[2:])
        kind, fr, _ = m.cat[i]
        return '%d %s（%s）' % (i, fr, '裝備' if kind == 'e' else '道具')
    return e


class Checker:
    def __init__(self, root, d, skip_row=None):
        self.root, self.d, self.D = root, d, d['data']
        self.m = Model(d, root)
        self.res = Result()
        self.skip_row = skip_row          # test hook (case 22): a handler that "forgets" one row
        self.line_cache = {}

    # -- helpers
    def line_of(self, file, text):
        """first line in the file that contains the text (for humans; keys never use line numbers)"""
        if file not in self.line_cache:
            p = os.path.join(self.root, file)
            self.line_cache[file] = open(p, encoding='utf-8').read().split('\n') if os.path.isfile(p) else []
        t = json.dumps(text, ensure_ascii=False)[1:-1] if isinstance(text, str) else str(text)
        for i, l in enumerate(self.line_cache[file]):
            if t and t in l:
                return i + 1
        return None

    def item(self, leaf, name, key, ctx=None):
        if isinstance(name, str) and '看不出' in name:
            # the data itself says which one is unknown (v5 B2): a known ambiguous reference, not a missing one
            return self.conclude(leaf, key, name, 'ambiguous', [], 'text-says-ambiguous', 'item', ctx)
        st, ents, how = self.m.items.resolve(name)
        self.conclude(leaf, key, name, st, ents, how, 'item', ctx)

    def conclude(self, leaf, key, name, st, ents, how, kind, ctx=None, note=None):
        code = {'unresolved': 'E1', 'ambiguous': 'E2'}.get(st)
        row = dict(code=code, file=leaf.file, key=key, sig=leaf.sig, name=name, status=st, kind=kind,
                   ents=ents, how=how, ctx=ctx, note=note)
        if code == 'E1' and kind == 'item':
            row['cands'] = self.m.items.candidates(name)
        self.res.add(**row)
        return True

    def ok(self, leaf, key, name, note):
        self.res.add(code=None, file=leaf.file, key=key, sig=leaf.sig, name=name, status='excluded-row', kind='-',
                     ents=[], how='-', ctx=None, note=note)
        return True

    def parent(self, leaf, up=1):
        return get(self.D, leaf.root, leaf.path[:-up])

    def pk(self, leaf, kind):
        """value of the nearest path element of a kind ('k' map key / 'f' field / 'i' index)"""
        for k, v in reversed(leaf.path):
            if k == kind:
                return v
        return None

    def floor_of(self, leaf):
        if leaf.root == 'SAO':
            return 1
        if leaf.root == 'SAO23':
            return int(leaf.path[1][1])
        return None

    # -- handlers: each returns True when the leaf got a conclusion
    def h_item_drop(self, leaf):
        f = self.floor_of(leaf)
        mob = self.parent(leaf, 3)['name']
        return self.item(leaf, leaf.value, 'F%d/%s/drop:%s' % (f, mob, leaf.value)) or True

    def h_item_loot(self, leaf):
        if leaf.root == 'SAO_EVENTS':
            dg = self.pk(leaf, 'k')
            where = 'event:%s' % dg
        else:
            spot = self.parent(leaf, 4)
            where = 'F%d/spot:%s' % (self.floor_of(leaf), spot['id'])
        return self.item(leaf, leaf.value, '%s/loot:%s' % (where, leaf.value)) or True

    def h_mob_loot(self, leaf):
        if leaf.value is None:
            return self.ok(leaf, None, None, '寶箱這一格沒有寫怪物')
        f = self.floor_of(leaf)
        spot = self.parent(leaf, 4)
        st, ents, how = self.m.mob[f].resolve(leaf.value)
        return self.conclude(leaf, 'F%d/spot:%s/loot-mob:%s' % (f, spot['id'], leaf.value), leaf.value, st, ents, how, 'mob')

    def h_mob_loot_any(self, leaf):
        if leaf.value is None:
            return self.ok(leaf, None, None, '寶箱這一格沒有寫怪物')
        st, ents, how = self.m.mob_all.resolve(leaf.value)
        return self.conclude(leaf, 'event:%s/loot-mob:%s' % (self.pk(leaf, 'k'), leaf.value), leaf.value, st, ents, how, 'mob')

    def h_item_gather(self, leaf):
        spot = self.parent(leaf, 2)
        return self.item(leaf, leaf.value, 'F1/spot:%s/item:%s' % (spot['id'], leaf.value)) or True

    def h_item_quest(self, leaf):
        q = self.parent(leaf, 3)
        return self.item(leaf, leaf.value, 'F1/quest:%s/need:%s' % (q['id'], leaf.value)) or True

    def h_item_bonus(self, leaf):
        q = self.parent(leaf, 1)
        if leaf.value is None:
            return self.ok(leaf, None, None, '沒有額外獎勵')
        m = QTY.match(leaf.value)
        name = m.group(2) if m else leaf.value
        return self.item(leaf, name, 'F1/quest:%s/bonus:%s' % (q['id'], name)) or True

    def h_mob_kill(self, leaf):
        q = self.parent(leaf, 3)
        st, ents, how = self.m.mob[1].resolve(leaf.value)
        return self.conclude(leaf, 'F1/quest:%s/kill:%s' % (q['id'], leaf.value), leaf.value, st, ents, how, 'mob')

    def h_npc_quest(self, leaf):
        q = self.parent(leaf, 1)
        return self.npc_q(leaf, 1, leaf.value, 'F1/quest:%s/npc' % q['id'])

    def h_npc_mainq(self, leaf):
        f = int(leaf.path[0][1])
        q = self.parent(leaf, 1)
        if leaf.value in (None, '', '—', '-'):
            return self.ok(leaf, None, leaf.value, '排除：沒有 NPC（還沒有截圖）')
        return self.npc_q(leaf, f, leaf.value, 'F%d/mainq:%s/npc' % (f, q['t']))

    def npc_q(self, leaf, f, name, key):
        st, ents, how = self.m.npc[f].resolve(name)
        if st == 'unresolved':
            # only a quest NPC (not in npcs.js): not an error (v5 B3)
            return self.conclude(leaf, key, name, 'quest-npc', [], 'quest-only', 'npc')
        return self.conclude(leaf, key, name, st, ents, how, 'npc')

    def h_town_ref(self, leaf):
        q = self.parent(leaf, 1)
        ok = leaf.value in self.m.place_ids[1]
        return self.conclude(leaf, 'F1/quest:%s/town' % q['id'], leaf.value, 'resolved' if ok else 'unresolved',
                             ['P1:' + leaf.value] if ok else [], 'id', 'place')

    def h_zone_ref(self, leaf):
        f = self.floor_of(leaf)
        owner = self.parent(leaf, 2 if leaf.sig.endswith('[]') else 1)
        who = owner.get('name') or owner.get('id')
        ok = leaf.value in self.m.zone_ids[f]
        return self.conclude(leaf, 'F%d/%s/zone:%s' % (f, who, leaf.value), leaf.value, 'resolved' if ok else 'unresolved',
                             ['Z%d:%s' % (f, leaf.value)] if ok else [], 'id', 'zone')

    def h_mob_bs(self, leaf):
        f = self.floor_of(leaf)
        st, ents, how = self.m.mob[f].resolve(leaf.value)
        return self.conclude(leaf, 'F%d/boss-spawn:%s' % (f, leaf.value), leaf.value, st, ents, how, 'mob')

    def h_mob_spot(self, leaf):
        f = self.floor_of(leaf)
        spot = self.parent(leaf, 2)
        st, ents, how = self.m.mob[f].resolve(leaf.value)
        return self.conclude(leaf, 'F%d/spot:%s/mon:%s' % (f, spot['id'], leaf.value), leaf.value, st, ents, how, 'mob')

    def h_mob_hint(self, leaf):
        f = int(leaf.path[0][1])
        st, ents, how = self.m.mob[f].resolve(leaf.value)
        return self.conclude(leaf, 'F%d/hint:%s' % (f, leaf.value), leaf.value, st, ents, how, 'mob')

    def h_mob_photo(self, leaf):
        f = int(leaf.path[1][1])
        st, ents, how = self.m.mob[f].resolve(leaf.value)
        return self.conclude(leaf, 'F%d/photo:%s' % (f, leaf.value), leaf.value, st, ents, how, 'mob')

    def h_mob_zh(self, leaf):
        st, ents, how = self.m.mob_all.resolve(leaf.value)
        return self.conclude(leaf, 'mobsByName:%s' % leaf.value, leaf.value, st, ents, how, 'mob')

    def h_codex_num(self, leaf):
        names = self.m.mob_num.get(leaf.value, [])
        st = 'resolved' if len(names) == 1 else ('ambiguous' if names else 'unresolved')
        where = 'codex' if leaf.root == 'SAO_CODEX' else 'zhnames.mobs'
        return self.conclude(leaf, '%s:#%s' % (where, leaf.value), leaf.value, st, ['M1:' + n for n in names], 'num', 'mob')

    def h_npc_recipe(self, leaf):
        m = re.match(r'^(\d+)\|(.*)$', leaf.value)
        f, name = (int(m.group(1)), m.group(2)) if m else (1, leaf.value)
        st, ents, how = self.m.npc[f].resolve(name)
        return self.conclude(leaf, 'recipe-npc:%s' % leaf.value, leaf.value, st, ents, how, 'npc')

    def h_npc_buyback(self, leaf):
        st, ents, how = self.m.npc[1].resolve(leaf.value)
        return self.conclude(leaf, 'buyback-npc:%s' % leaf.value, leaf.value, st, ents, how, 'npc')

    h_npc_shopmap = h_npc_buyback

    def h_npc_calc(self, leaf):
        m = re.match(r'^(\d+)\|(.*)$', leaf.value)
        f, name = (int(m.group(1)), m.group(2)) if m else (1, leaf.value)
        st, ents, how = self.m.npc[f].resolve(name)
        return self.conclude(leaf, 'npc-calc:%s' % leaf.value, leaf.value, st, ents, how, 'npc')

    def h_npc_zh(self, leaf):
        st, ents, how = self.m.npc_all.resolve(leaf.value)
        what = 'npcEn' if leaf.path[0][1] == 'npcEn' else 'npcs'
        if st == 'unresolved' and safe(leaf.value) in self.m.quest_npcs:
            return self.conclude(leaf, 'zhnames.%s:%s' % (what, leaf.value), leaf.value, 'quest-npc', [], 'quest-only', 'npc')
        return self.conclude(leaf, 'zhnames.%s:%s' % (what, leaf.value), leaf.value, st, ents, how, 'npc')

    def h_place_zh(self, leaf):
        best = None
        for f in (1, 2, 3):
            st, ents, how = self.m.place[f].resolve(leaf.value)
            if st != 'unresolved':
                best = (st, ents, how)
                break
        st, ents, how = best or ('unresolved', [], 'none')
        return self.conclude(leaf, 'zhnames.places:%s' % leaf.value, leaf.value, st, ents, how, 'place')

    def h_quest_zh(self, leaf):
        st, ents, how = self.m.quest.resolve(leaf.value)
        return self.conclude(leaf, 'zhnames.quests:%s' % leaf.value, leaf.value, st, ents, how, 'quest')

    def h_set_zh(self, leaf):
        st, ents, how = self.m.set.resolve(leaf.value)
        return self.conclude(leaf, 'zhnames.sets:%s' % leaf.value, leaf.value, st, ents, how, 'set')

    def h_rec_out_id(self, leaf):
        npc = leaf.path[0][1]
        row = self.parent(leaf, 1)
        if leaf.value is None:
            return self.ok(leaf, None, None, '沒有官網 id（產出名稱另外解析）')
        ok = int(leaf.value) in self.m.cat
        return self.conclude(leaf, 'recipe:%s/out-id:%s' % (npc, row[1]), leaf.value, 'resolved' if ok else 'unresolved',
                             ['C:%d' % int(leaf.value)] if ok else [], 'id', 'item')

    def h_rec_out_name(self, leaf):
        npc = leaf.path[0][1]
        row = self.parent(leaf, 1)
        if row[0] is not None and int(row[0]) in self.m.cat:
            return self.ok(leaf, None, leaf.value, '有官網 id 的產出是本站紀錄（用 id 對）')
        return self.item(leaf, leaf.value, 'recipe:%s/out:%s' % (npc, leaf.value)) or True

    def h_item_mat(self, leaf):
        npc = leaf.path[0][1]
        row = self.parent(leaf, 3)
        return self.item(leaf, leaf.value, 'recipe:%s/%s/mat:%s' % (npc, row[1], leaf.value)) or True

    def h_item_buyback(self, leaf):
        npc = leaf.path[1][1]
        return self.item(leaf, leaf.value, 'buyback:%s/%s' % (npc, leaf.value)) or True

    def h_item_setmember(self, leaf):
        s = self.parent(leaf, 2)
        return self.item(leaf, leaf.value, 'set:%s/member:%s' % (s['name'], leaf.value)) or True

    def h_item_potion(self, leaf):
        return self.item(leaf, leaf.value, 'potion:%s' % leaf.value) or True

    def h_item_icon(self, leaf):
        return self.item(leaf, leaf.value, 'gameicons:%s' % leaf.value) or True

    def h_item_recicon(self, leaf):
        return self.item(leaf, leaf.value, 'recicons:%s' % leaf.value) or True

    def h_item_extra(self, leaf):
        return self.item(leaf, leaf.value, 'SAO23.extra:%s' % leaf.value) or True

    def h_item_gacha(self, leaf):
        b = self.parent(leaf, 3)
        row = self.parent(leaf, 1)
        t, v = (str(row['id']).split('|', 1) + [''])[:2] if row.get('id') else ('', '')
        if v.isdigit() and int(v) in self.m.cat:
            return self.conclude(leaf, 'gacha:%s/%s' % (b['n'], leaf.value), leaf.value, 'resolved', ['C:' + v], 'row-id', 'item')
        return self.item(leaf, leaf.value, 'gacha:%s/%s' % (b['n'], leaf.value)) or True

    def h_gacha_id(self, leaf):
        t, v = str(leaf.value).split('|', 1)
        ok = v.isdigit() and int(v) in self.m.cat
        b = self.parent(leaf, 3)
        return self.conclude(leaf, 'gacha:%s/id:%s' % (b['n'], leaf.value), leaf.value, 'resolved' if ok else 'unresolved',
                             ['C:' + v] if ok else [], 'id', 'item')

    def h_item_patch(self, leaf):
        """label of a row keyed by a catalogue id: the id is the link (checked on the key), the label is not re-resolved"""
        i = leaf.path[2][1]
        if str(i).isdigit() and int(i) in self.m.cat:
            return self.conclude(leaf, 'eqPatch:%s/en' % i, leaf.value, 'resolved', ['C:%d' % int(i)], 'row-id', 'item')
        return self.item(leaf, leaf.value, 'eqPatch:%s/en' % i) or True

    def h_cat_id_key(self, leaf):
        ok = str(leaf.value).isdigit() and int(leaf.value) in self.m.cat
        what = 'gamestats' if leaf.root == 'SAO_GAMESTATS' else 'eqPatch'
        return self.conclude(leaf, '%s:id:%s' % (what, leaf.value), leaf.value, 'resolved' if ok else 'unresolved',
                             ['C:' + str(leaf.value)] if ok else [], 'id', 'item')

    def h_item_roulette(self, leaf):
        """world boss roulette row [en, fr, %]: one item; the English name first, then the French one"""
        key = self.pk(leaf, 'k')
        if key not in ('roulette', 'roulette0'):
            return self.ok(leaf, None, leaf.value, '不是物品（攻擊招式等文字）')
        row = self.parent(leaf, 1)
        clean = lambda s: re.sub(r'（[^）]*）\s*$', '', (TIMES.match(s).group(1) if TIMES.match(s or '') else (s or ''))).strip()
        en, fr = clean(row[0]), clean(row[1]) if len(row) > 1 and isinstance(row[1], str) else None
        st, ents, how = self.m.items.resolve(en)
        if st == 'unresolved' and fr:
            st, ents, how = self.m.items.resolve(fr)
            how = 'fr:' + how
        boss = self.parent(leaf, 3).get('id')
        return self.conclude(leaf, 'boss:%s/%s:%s' % (boss, key, en), en, st, ents, how, 'item')

    def h_item_roulette_fr(self, leaf):
        if self.pk(leaf, 'k') not in ('roulette', 'roulette0'):
            return self.ok(leaf, None, leaf.value, '不是物品（攻擊招式等文字）')
        return self.ok(leaf, None, leaf.value, '和同一列的英文名一起解析')

    def h_item_fr(self, leaf):
        if leaf.value in (None, ''):
            return self.ok(leaf, None, None, '沒有法文名（不連官網）')
        ids = self.m.catfr.get(safe(leaf.value), [])
        key = leaf.path[0][1] if leaf.root == 'SAO23_ITEMS' else leaf.path[1][1]
        st = 'resolved' if len(ids) == 1 else ('ambiguous' if ids else 'unresolved')
        if st == 'unresolved':
            # not in the catalogue: a game-only French name; the record still exists (W7 territory, not E1)
            return self.conclude(leaf, '%s/fr' % key, leaf.value, 'no-catalogue', [], 'fr', 'item')
        return self.conclude(leaf, '%s/fr' % key, leaf.value, st, ['C:%d' % i for i in ids], 'fr', 'item')

    def h_gi_oid(self, leaf):
        g = self.parent(leaf, 2)
        ok = int(leaf.value) in self.m.cat
        return self.conclude(leaf, 'gameinfo:%s/oid:%s' % (g['en'], leaf.value), leaf.value, 'resolved' if ok else 'unresolved',
                             ['C:%d' % int(leaf.value)] if ok else [], 'id', 'item')

    def h_gi_site(self, leaf):
        g = self.parent(leaf, 1)
        if leaf.value is None:
            return self.ok(leaf, None, None, '沒有 site')
        ok = leaf.value in self.D['SAO']['ITEMS'] or leaf.value in self.D['SAO23_ITEMS']
        return self.conclude(leaf, 'gameinfo:%s/site' % g['en'], leaf.value, 'resolved' if ok else 'unresolved', [], 'key', 'item')

    def h_zh_ids(self, leaf):
        z = self.parent(leaf, 2)
        t, v = leaf.value.split('|', 1)
        if t in ('e', 'p'):
            ok = v.isdigit() and int(v) in self.m.cat
        elif t == 'i':
            ok = v in self.D['SAO']['ITEMS'] or v in self.D['SAO23_ITEMS']
        elif t == 'g':
            return self.ok(leaf, 'zhnames:%s/%s' % (z['zh'], leaf.value), leaf.value, '遊戲才有的物品名（g|），沒有外部 id')
        else:
            ok = False
        return self.conclude(leaf, 'zhnames:%s/%s' % (z['zh'], leaf.value), leaf.value, 'resolved' if ok else 'unresolved',
                             [], 'id', 'item')

    OBT = re.compile(r'^(Loot|Crafted at|Sold by|Bought back by)\s*:?\s*(.+?)\s*(?:\(([^)]*)\))?\s*$', re.I)

    def h_gi_obt(self, leaf):
        g = self.parent(leaf, 2)
        m = self.OBT.match(leaf.value or '')
        if not m:
            return self.ok(leaf, 'gameinfo:%s/obt' % g['en'], leaf.value, '不是名稱引用（寶箱、採集、任務獎勵、轉蛋…文字）')
        kind, name = m.group(1).lower(), m.group(2).strip()
        key = 'gameinfo:%s/%s:%s' % (g['en'], kind.replace(' ', '-'), name)
        if kind == 'loot':
            st, ents, how = self.m.mob_all.resolve(name)
            if st == 'unresolved':
                st2, ents2, how2 = self.zh_mob(name)
                if st2 != 'unresolved':
                    st, ents, how = st2, ents2, how2
            return self.conclude(leaf, key, name, st, ents, how, 'mob')
        st, ents, how = self.m.npc_all.resolve(name)
        if st == 'unresolved' and safe(name) in {safe(t) for t in (self.D['SAO_ZHNAMES'].get('terms') or {})}:
            # a game shop name recorded in zhnames.terms, not yet tied to an npcs.js record (stage 0 counted it the same way)
            return self.conclude(leaf, key, name, 'term', [], 'zhnames.terms', 'npc')
        return self.conclude(leaf, key, name, st, ents, how, 'npc')

    def zh_mob(self, name):
        """game text in Chinese: zhnames.mobsByName value -> key"""
        inv = {safe(v): k for k, v in (self.D['SAO_ZHNAMES'].get('mobsByName') or {}).items()}
        k = inv.get(safe(name))
        if k:
            return self.m.mob_all.resolve(k)
        return 'unresolved', [], 'none'

    # ---- run
    def run(self, files_owner):
        leaves = []
        self.unregistered_files = []
        for g, f in sorted(files_owner.items(), key=lambda x: (DATA_FILES.index(x[1]) if x[1] in DATA_FILES else 999, x[0])):
            if f in EXTERNAL_FILES:
                continue
            if f not in DATA_FILES:
                self.unregistered_files.append((f, g))
                continue
            walk(self.D[g], g, [], f, g, leaves)
        self.e9 = []
        self.sigs = collections.OrderedDict()
        for lf in leaves:
            p, a = cover(lf.sig)
            s = self.sigs.setdefault(lf.sig, dict(rule=p, action=a, n=0, file=lf.file))
            s['n'] += 1
            if a is None:
                continue
            if a[0] == 'scan':
                h = getattr(self, 'h_' + a[1])
                done = False
                if not (self.skip_row and self.skip_row == lf.sig and not getattr(self, '_skipped', False)):
                    done = h(lf)
                else:
                    self._skipped = True
                if not done:
                    self.e9.append(dict(code='E9', file=lf.file, key='row:%s:%s' % (lf.sig, json.dumps(lf.value, ensure_ascii=False)),
                                        sig=lf.sig, name=lf.value, note='掃描欄位的這一列沒有得到結論'))
        for sig, s in self.sigs.items():
            if s['action'] is None:
                self.e9.append(dict(code='E9', file=s['file'], key='field:%s' % sig, sig=sig, name=None,
                                    note='欄位沒有登記在 COVERAGE（%d 個值）' % s['n']))
        for f, g in self.unregistered_files:
            self.e9.append(dict(code='E9', file=f, key='file:%s' % f, sig=g, name=None, note='資料檔沒有登記（DATA_FILES／EXTERNAL_FILES）'))
        # NPC_NOTE keys (src/index.html, read as text)
        for k, line in npc_note_keys(self.root):
            st, ents, how = self.m.npc[1].resolve(k)
            self.res.add(code={'unresolved': 'E1', 'ambiguous': 'E2'}.get(st), file='src/index.html', key='NPC_NOTE:%s' % k,
                         sig='NPC_NOTE{key}', name=k, status=st, kind='npc', ents=ents, how=how, ctx=None, note=None, line=line)
        self.e3 = self.find_e3()

    def find_e3(self):
        """one external id claimed by two different site records (within one source; zhnames duplicates are W5)"""
        out = []
        by = collections.defaultdict(lambda: collections.defaultdict(set))
        for npc, o in self.D['SAO_RECIPES'].items():
            for row in o['items']:
                if row[0] is not None:
                    by['recipes.js'][int(row[0])].add(row[1])
        for g in self.D['SAO_GAMEINFO']['items']:
            for i in g.get('oid') or []:
                by['gameinfo.js'][int(i)].add(g['en'])
        for k, v in self.D['SAO']['ITEMS'].items():
            ids = self.m.catfr.get(safe(v.get('fr')), []) if v.get('fr') else []
            if len(ids) == 1:
                by['data.js'][ids[0]].add(k)
        for k, v in self.D['SAO23_ITEMS'].items():
            ids = self.m.catfr.get(safe(v[0]), []) if v[0] else []
            if len(ids) == 1:
                by['data23.js'][ids[0]].add(k)
        for src, d in by.items():
            for i, names in d.items():
                if len(names) > 1:
                    out.append(dict(code='E3', file=src, key='id:%d' % i, name=sorted(names),
                                    note='官網 %s 掛在 %d 筆本站紀錄：%s' % (ent_label(self.m, 'C:%d' % i), len(names), '、'.join(sorted(names)))))
        # monster codex numbers on floor 1
        for num, names in self.m.mob_num.items():
            if len(names) > 1:
                out.append(dict(code='E3', file='data.js', key='mob-num:%s' % num, name=sorted(names),
                                note='遊戲圖鑑 #%s 掛在 %d 隻怪物：%s' % (num, len(names), '、'.join(sorted(names)))))
        return out


# ------------------------------------------------------------------ pins (E6 identity, E7 icon)
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        h.update(f.read())
    return h.hexdigest()


def check_pins(ck, pins):
    m, D, out = ck.m, ck.D, []
    for p in pins.get('pins', []):
        pid = p.get('id') or p.get('name')
        if p.get('type') == 'identity':
            oid, names = int(p['oid']), list(p.get('names') or [])
            allowed = {safe(n) for n in names} | ({safe(m.cat[oid][1])} if oid in m.cat else set())
            st, ents, how = m.items.resolve(names[0]) if names else ('unresolved', [], 'none')
            if oid not in m.cat:
                out.append(dict(code='E6', file='registry/pins.json', key='pin:%s' % pid, name=names[:1],
                                note='釘選的官網 id %d 不在官網圖鑑裡' % oid))
            elif not (st == 'resolved' and ents == ['C:%d' % oid]):
                out.append(dict(code='E6', file='registry/pins.json', key='pin:%s' % pid, name=names[:1],
                                note='釘選「%s＝%s」的關聯不見了或對到別的（現在解析結果：%s %s）' %
                                     (names[0] if names else '?', ent_label(m, 'C:%d' % oid), st, '、'.join(ent_label(m, e) for e in ents) or '無')))
            links = []
            for k, v in D['SAO']['ITEMS'].items():
                if v.get('fr') and m.catfr.get(safe(v['fr'])) == [oid]:
                    links.append(('data.js', k))
            for k, v in D['SAO23_ITEMS'].items():
                if v[0] and m.catfr.get(safe(v[0])) == [oid]:
                    links.append(('data23.js', k))
            for g in D['SAO_GAMEINFO']['items']:
                if oid in [int(i) for i in g.get('oid') or []]:
                    links.append(('gameinfo.js', g['en']))
            for npc, o in D['SAO_RECIPES'].items():
                for row in o['items']:
                    if row[0] is not None and int(row[0]) == oid:
                        links.append(('recipes.js', row[1]))
            for z in D['SAO_ZHNAMES']['items']:
                if any(i in ('e|%d' % oid, 'p|%d' % oid) for i in z.get('ids') or []) and z.get('en'):
                    links.append(('zhnames.js', z['en']))
            for f, n in sorted(set(links)):
                if safe(n) not in allowed:
                    out.append(dict(code='E6', file=f, key='pin:%s/link:%s' % (pid, n), name=n,
                                    note='官網 %s 已釘選給「%s」，但 %s 的「%s」也接到它' % (ent_label(m, 'C:%d' % oid), names[0], f, n)))
        elif p.get('type') == 'icon':
            name, file, h = p['name'], p['file'], p['sha256']
            cur = (D.get('SAO_GAMEICONS') or {}).get(name)
            path = os.path.join(ck.root, file)
            if cur != file:
                out.append(dict(code='E7', file='gameicons.js', key='pin:%s' % pid, name=name,
                                note='釘選「%s」的圖示是 %s，現在是 %s' % (name, file, cur)))
            elif not os.path.isfile(path) or sha256_file(path) != h:
                out.append(dict(code='E7', file=file, key='pin:%s/hash' % pid, name=name,
                                note='釘選「%s」的圖示檔內容變了（雜湊不同）' % name))
    return out


# ------------------------------------------------------------------ warnings (report only)
def sim(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def w7_vocab(root):
    p = os.path.join(root, 'tools', 'check_refs_vocab.json')
    return json.load(open(p, encoding='utf-8'))['gloss'] if os.path.isfile(p) else {}


STOP = set('de du des la le les l d en a au aux et of the a an'.split())


def _strip_acc(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def toks_fr(s):
    s = _strip_acc(safe(s)).replace("'", ' ')
    return set(t.rstrip('sx') if len(t) > 3 else t for t in re.findall(r'[a-z0-9]+', s) if t not in STOP)


def toks_en(s, gloss):
    s = _strip_acc(safe(s))
    out = set()
    for t in re.findall(r"[a-z0-9']+", s):
        t2 = t.replace("'s", '').replace("'", '')
        if t2 in STOP or t in STOP:
            continue
        g = gloss.get(t) or gloss.get(t2)
        if g:
            out |= set(x.rstrip('sx') if len(x) > 3 else x for x in g.split())
        else:
            out.add(t2.rstrip('sx') if len(t2) > 3 else t2)
    return out


def w7_candidates(ck, name, fr=None):
    """B7: the stage 0 rule (inv_analyze.py candidates(): French difflib >= 0.6; English -> French vocabulary,
    Dice >= 0.6 with at least 2 shared words) + the cross-file clue (v3: zhnames / gameinfo / gamestats English
    name equal to this name and carrying a catalogue id)"""
    m, res = ck.m, {}
    if not hasattr(ck, '_cat_tok'):
        ck._cat_tok = {i: toks_fr(fr_) for i, (k_, fr_, _) in m.cat.items()}
        ck._cat_acc = {i: _strip_acc(safe(fr_)) for i, (k_, fr_, _) in m.cat.items()}
    if fr:
        f = _strip_acc(safe(fr))
        for i, n in ck._cat_acc.items():
            s = difflib.SequenceMatcher(None, f, n).ratio()
            if s >= 0.6:
                res[i] = max(res.get(i, (0, ''))[0], round(s, 3)), '法文相似度'
    te = toks_en(name, ck.vocab) if name else set()
    if te:
        for i, tc in ck._cat_tok.items():
            inter = te & tc
            if not inter or (len(inter) < 2 and not (len(te) == 1 and len(tc) == 1)):
                continue
            d = 2 * len(inter) / (len(te) + len(tc))
            if d >= 0.6 and d > res.get(i, (0, ''))[0]:
                res[i] = (round(d, 3), '英→法字彙')
    k = safe(name)
    for z in ck.D['SAO_ZHNAMES']['items']:
        if z.get('en') and safe(z['en']) == k:
            for idd in z.get('ids') or []:
                t, v = idd.split('|', 1)
                if t in ('e', 'p') and v.isdigit() and int(v) in m.cat and int(v) not in res:
                    res[int(v)] = (1.0, '跨檔線索：zhnames')
    for g in ck.D['SAO_GAMEINFO']['items']:
        if safe(g['en']) == k:
            for i in g.get('oid') or []:
                if int(i) in m.cat and int(i) not in res:
                    res[int(i)] = (1.0, '跨檔線索：gameinfo')
    for i, s in ck.D['SAO_GAMESTATS']['items'].items():
        if s.get('en') and safe(s['en']) == k and str(i).isdigit() and int(i) in m.cat and int(i) not in res:
            res[int(i)] = (1.0, '跨檔線索：gamestats')
    return sorted(((sc, i, how) for i, (sc, how) in res.items()), key=lambda x: (-x[0], x[1]))


RAR = {'c': 1, 'b': 2, 'a': 3, 's': 4, 'splus': 5, 'splusplus': 5, 'ss': 5}


def warnings(ck):
    m, D, W = ck.m, ck.D, collections.OrderedDict()
    # W2: game value != catalogue value, per source and field
    w2 = collections.defaultdict(list)
    for i, s in D['SAO_GAMESTATS']['items'].items():
        if not str(i).isdigit() or int(i) not in m.cat:
            continue
        kind, fr, r = m.cat[int(i)]
        if s.get('lvl') is not None and str(s['lvl']) != str(r[4]):
            w2['gamestats 等級'].append('%s %s：遊戲 %s／圖鑑 %s' % (i, fr, s['lvl'], r[4]))
        if s.get('r') and s['r'] != r[3]:
            w2['gamestats 稀有度'].append('%s %s：遊戲 %s／圖鑑 %s' % (i, fr, s['r'], r[3]))
    for npc, o in D['SAO_RECIPES'].items():
        for row in o['items']:
            if row[0] is not None and int(row[0]) in m.cat and row[7] is not None:
                kind, fr, r = m.cat[int(row[0])]
                if str(row[7]) != str(r[4]):
                    w2['配方等級'].append('%s %s（%s）：配方 %s／圖鑑 %s' % (row[0], fr, npc, row[7], r[4]))
    for g in D['SAO_GAMEINFO']['items']:
        oid = [int(i) for i in g.get('oid') or [] if int(i) in m.cat]
        if len(oid) == 1 and g.get('lvl') is not None:
            kind, fr, r = m.cat[oid[0]]
            if str(g['lvl']) != str(r[4]):
                w2['gameinfo 等級'].append('%s %s：遊戲 %s／圖鑑 %s' % (oid[0], fr, g['lvl'], r[4]))
    W['W2'] = {k: sorted(set(v)) for k, v in sorted(w2.items())}
    # W5: suspected duplicates
    w5 = []
    for f in ('1', '2', '3'):
        L = [n for n in D['SAO_NPCS'].get(f) or [] if n[2] is not None]
        for a in range(len(L)):
            for b in range(a + 1, len(L)):
                x, y = L[a], L[b]
                dist = ((x[2] - y[2]) ** 2 + (x[3] - y[3]) ** 2) ** .5
                if dist <= 5 or sim(safe(x[1]), safe(y[1])) >= 0.85:
                    w5.append('第 %s 層 NPC：%s ↔ %s（%.1f 格）' % (f, x[1], y[1], dist))
    recs = sorted(set(list(D['SAO']['ITEMS']) + list(D['SAO23_ITEMS'])))
    for a in range(len(recs)):
        for b in range(a + 1, len(recs)):
            x, y = recs[a], recs[b]
            if re.sub(r' \(\d+\)$', '', x) == re.sub(r' \(\d+\)$', '', y):
                continue
            if sim(safe(x), safe(y)) >= 0.85:
                w5.append('物品：%s ↔ %s' % (x, y))
    seen = collections.defaultdict(list)
    for z in D['SAO_ZHNAMES']['items']:
        if z.get('ids'):
            seen[tuple(sorted(z['ids']))].append(z['zh'])
    for ids, zs in sorted(seen.items()):
        if len(zs) > 1:
            w5.append('zhnames 重複條目：%s → %s' % ('、'.join(ids), '、'.join(zs)))
    W['W5'] = w5
    # W6: two objects share one icon file (same content)
    hashes = collections.defaultdict(set)
    for src in ('SAO_GAMEICONS', 'SAO_RECICONS'):
        for k, v in (D.get(src) or {}).items():
            p = os.path.join(ck.root, v)
            if os.path.isfile(p):
                hashes[sha256_file(p)].add(k)
    W['W6'] = sorted('、'.join(sorted(v)) for v in hashes.values() if len(v) > 1)
    # W7: records without a catalogue link that have candidates
    w7 = []
    for k, v in D['SAO']['ITEMS'].items():
        if m.item_ent['I:' + k].startswith('I:') and not v.get('vanilla'):
            c = w7_candidates(ck, k, v.get('fr'))
            if c:
                w7.append(('data.js ITEMS', k, c[:3]))
    for k, v in D['SAO23_ITEMS'].items():
        if m.item_ent['J:' + k].startswith('J:'):
            c = w7_candidates(ck, k, v[0])
            if c:
                w7.append(('data23.js SAO23_ITEMS', k, c[:3]))
    for g in D['SAO_GAMEINFO']['items']:
        if not g.get('oid') and not g.get('site'):
            c = w7_candidates(ck, g['en'])
            if c:
                w7.append(('gameinfo.js', g['en'], c[:3]))
    seen_out = set()
    for npc, o in D['SAO_RECIPES'].items():
        for row in o['items']:
            if row[0] is None and row[1] not in seen_out:
                seen_out.add(row[1])
                c = w7_candidates(ck, row[1])
                if c:
                    w7.append(('recipes.js 產出（id 是 null）', row[1], c[:3]))
    W['W7'] = [dict(src=s, name=n, cands=[dict(id=i, fr=m.cat[i][1], score=sc, how=h) for sc, i, h in c]) for s, n, c in sorted(w7)]
    # W10: only ref / site sources
    w10 = []
    for f in ('1', '2', '3'):
        for n in D['SAO_NPCS'].get(f) or []:
            if n[4] in ('ref', 'ref23', 'site', 'site2'):
                w10.append('第 %s 層 NPC %s（%s）' % (f, n[1], n[4]))
    for f, x in m.F.items():
        for p in list(x['towns']) + list(x['spots']):
            if p.get('src') == 'ref':
                w10.append('第 %d 層地點 %s（ref）' % (f, p.get('n')))
    W['W10'] = {'count': len(w10), 'list': sorted(w10)}
    # W11: names in player reports (external data; counted, not checked)
    w11 = collections.Counter()
    bad = []
    for r in ck.d['data'].get('SAO_REPORTS') or []:
        if r.get('type') == 'monster':
            st = m.mob.get(r.get('floor') or 1, m.mob_all).resolve(r.get('name'))[0]
        elif r.get('type') == 'item':
            st = m.items.resolve(r.get('name'))[0]
        else:
            continue
        w11[st] += 1
        if st != 'resolved':
            bad.append('%s %s「%s」：%s' % (r.get('id') or '(舊)', r.get('type'), r.get('name'), st))
    W['W11'] = {'count': dict(sorted(w11.items())), 'list': sorted(bad)}
    # W12: catalogue links supported by only one kind of source
    srcs = collections.defaultdict(set)
    for k, v in D['SAO']['ITEMS'].items():
        if v.get('fr') and len(m.catfr.get(safe(v['fr']), [])) == 1:
            srcs[m.catfr[safe(v['fr'])][0]].add('ITEMS fr')
    for k, v in D['SAO23_ITEMS'].items():
        if v[0] and len(m.catfr.get(safe(v[0]), [])) == 1:
            srcs[m.catfr[safe(v[0])][0]].add('SAO23 fr')
    for npc, o in D['SAO_RECIPES'].items():
        for row in o['items']:
            if row[0] is not None and int(row[0]) in m.cat:
                srcs[int(row[0])].add('配方 id')
    for g in D['SAO_GAMEINFO']['items']:
        for i in g.get('oid') or []:
            if int(i) in m.cat:
                srcs[int(i)].add('gameinfo oid')
    for z in D['SAO_ZHNAMES']['items']:
        for idd in z.get('ids') or []:
            t, v = idd.split('|', 1)
            if t in ('e', 'p') and v.isdigit() and int(v) in m.cat:
                srcs[int(v)].add('zhnames ids')
    for i in D['SAO_GAMESTATS']['items']:
        if str(i).isdigit() and int(i) in m.cat:
            srcs[int(i)].add('gamestats')
    one = collections.Counter()
    w12 = []
    for i, s in sorted(srcs.items()):
        if len(s) == 1:
            one[next(iter(s))] += 1
            w12.append('%d %s：只有 %s' % (i, m.cat[i][1], next(iter(s))))
    W['W12'] = {'count': dict(sorted(one.items())), 'list': w12}
    W['未量測'] = ['W1（同順位來源矛盾：資料檔沒有同時保存 catalog 和 wiki 的值）',
                  'W3（同一來源的不同觀察：資料檔每件物品只存一個值）',
                  'W4（同一外部編號在新舊匯入之間改名：階段 1 沒有上一次匯入的快照）',
                  'W8、W9 由瀏覽器測試 tests/zh_gap.js、tests/site_audit.js 產生（CI 執行）']
    return W


# ------------------------------------------------------------------ exceptions
CLEAR_BY = {'item': '階段 2', 'npc': '階段 3', 'place': '階段 3', 'zone': '階段 3', 'mob': '階段 4', 'quest': '階段 4',
            'set': '階段 2'}


def reason_of(r, m):
    if r['code'] == 'E1':
        c = r.get('cands') or []
        return '解析不到：沒有任何物品紀錄、官網名或遊戲名對得上' + ('（單複數候選：%s）' % '、'.join(c) if c else '') \
            if r.get('kind') == 'item' else '解析不到：沒有對得上的%s' % {'npc': ' NPC', 'mob': '怪物', 'place': '地點',
                                                                    'zone': '區域', 'quest': '任務', 'set': '套裝'}.get(r.get('kind'), '紀錄')
    if r['code'] == 'E2':
        return '對到 %d 個不同的實體：%s' % (len(r['ents']), '、'.join(ent_label(m, e) for e in r['ents']))
    return r.get('note') or ''


def collect_errors(ck, pin_errors):
    errs = collections.OrderedDict()
    for r in ck.res.rows:
        if r['code']:
            k = (r['code'], r['file'], r['key'])
            if k not in errs:
                errs[k] = dict(r, count=0, reason=reason_of(r, ck.m), line=r.get('line') or ck.line_of(r['file'], r['name']))
            errs[k]['count'] += 1
    for r in ck.e3 + ck.e9 + pin_errors:
        k = (r['code'], r['file'], r['key'])
        if k not in errs:
            errs[k] = dict(r, count=0, reason=r.get('note'), line=None)
        errs[k]['count'] += 1
    return errs


def judge(errs, exc, draft):
    """-> list of problems (each blocks the build)"""
    probs = []
    seen = set()
    for e in exc.get('exceptions', []):
        k = (e.get('code'), e.get('file'), e.get('key'))
        if k in seen:
            probs.append(('duplicate', k, '例外清單裡同一筆出現兩次'))
        seen.add(k)
        if e.get('code') not in EXCEPTABLE:
            probs.append(('not-exceptable', k, '%s 不能登記例外（只收 E1、E2、E3）' % e.get('code')))
        if k not in errs:
            probs.append(('stale', k, '這個錯誤已經不見了，請刪掉這一筆例外'))
        elif not (e.get('approved_by') and e.get('approved_at')) and not draft:
            probs.append(('unapproved', k, '例外還沒有核准（approved_by／approved_at 空白），不算鎖定'))
    for k, e in errs.items():
        if k not in seen:
            probs.append(('new', k, e.get('reason') or ''))
    return probs


# ------------------------------------------------------------------ report
def md_report(ck, errs, probs, W, exc, draft):
    L = ['# 引用檢查報告（R0.5 階段 1）', '',
         '由 `python3 tools/check_refs.py` 產生，內容是建置當下的結果；Apps Script 之後收錄的回報（W11）要等下一次建置才反映。', '']
    cnt = collections.Counter(k[0] for k in errs)
    exk = {(e['code'], e['file'], e['key']) for e in exc.get('exceptions', [])}
    L += ['## 結果', '', '| 代號 | 數量 | 在例外清單上 | 不在例外清單上 |', '| --- | --- | --- | --- |']
    for c in ERROR_CODES:
        n = cnt.get(c, 0)
        a = sum(1 for k in errs if k[0] == c and k in exk)
        L.append('| %s | %d | %d | %d |' % (c, n, a, n - a))
    pc = collections.Counter(p[0] for p in probs)
    L += ['', '建置判定：' + ('**通過**' if not probs else '**失敗**（%s）' % '、'.join('%s %d' % (k, v) for k, v in sorted(pc.items()))) +
          ('（--draft：未核准的例外暫時視為鎖定，只能在實作分支開發時用）' if draft else ''), '']
    # coverage
    sc = collections.Counter()
    for s in ck.sigs.values():
        sc['掃描' if s['action'] and s['action'][0] == 'scan' else ('排除' if s['action'] else '沒有登記')] += 1
    L += ['## 來源覆蓋（G1，和例外分開統計）', '', '欄位簽名 %d 個：掃描 %d、排除 %d、沒有登記 %d（E9）。' %
          (len(ck.sigs), sc['掃描'], sc['排除'], sc['沒有登記']), '']
    rows = collections.Counter()
    for r in ck.res.rows:
        rows[(r['sig'], r['status'])] += 1
    L += ['| 欄位 | 結論 | 列數 |', '| --- | --- | --- |']
    for (sig, st), n in sorted(rows.items()):
        L.append('| `%s` | %s | %d |' % (sig, st, n))
    L += ['', '排除的欄位（理由、處理階段、欄位數）：', '']
    ex = collections.defaultdict(list)
    for sig, s in ck.sigs.items():
        if s['action'] and s['action'][0] == 'skip':
            ex[(s['action'][1], s['action'][2])].append(sig)
    for (why, stage), sigs in sorted(ex.items()):
        L.append('- %s；%s；%d 個：%s' % (why, stage, len(sigs), '、'.join('`%s`' % x for x in sorted(sigs))))
    L += ['', '## 錯誤清單', '']
    for c in ERROR_CODES:
        items = [(k, e) for k, e in errs.items() if k[0] == c]
        if not items:
            continue
        L += ['### %s（%d）' % (c, len(items)), '', '| 檔案 | 鍵 | 行 | 原因 | 例外 |', '| --- | --- | --- | --- | --- |']
        for k, e in sorted(items, key=lambda x: (x[0][1], x[0][2])):
            L.append('| %s | `%s` | %s | %s | %s |' % (k[1], k[2].replace('|', '\\|'), e.get('line') or '', (e.get('reason') or '').replace('|', '\\|'),
                                                      '有' if k in exk else '**沒有**'))
        L.append('')
    if probs:
        L += ['## 建置失敗的原因', '']
        for kind, k, why in sorted(probs):
            L.append('- %s：%s `%s`（%s）：%s' % (kind, k[0], k[2], k[1], why))
        L.append('')
    L += ['## 提醒（只寫報告）', '']
    for w, v in W.items():
        if w == 'W7':
            L += ['### W7（%d 筆有候選）' % len(v), '']
            for x in v:
                L.append('- %s「%s」→ %s' % (x['src'], x['name'], '；'.join('%d %s（%s，%s）' % (c['id'], c['fr'], c['score'], c['how']) for c in x['cands'])))
        elif w == 'W2':
            L += ['### W2', ''] + ['- %s：%d 件' % (k, len(x)) for k, x in v.items()]
        elif isinstance(v, dict):
            L += ['### %s' % w, '', '- 數量：%s' % json.dumps(v.get('count'), ensure_ascii=False)]
        elif isinstance(v, list):
            L += ['### %s（%d）' % (w, len(v)), ''] + ['- %s' % x for x in v]
        L.append('')
    return '\n'.join(L).rstrip() + '\n'


def write_text(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding='utf-8')
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--draft', action='store_true', help='未核准的例外暫時視為鎖定（只能在實作分支開發時用）')
    ap.add_argument('--write-exceptions', action='store_true', help='第一次產生 registry/exceptions.json（已存在就拒絕）')
    ap.add_argument('--exceptions', default=None, help='例外清單路徑（測試用）')
    ap.add_argument('--pins', default=None, help='釘選檔路徑（測試用）')
    ap.add_argument('--out', default=None, help='報告目錄（預設 <root>/build）')
    ap.add_argument('--test-skip-row', default=None, help=argparse.SUPPRESS)
    ap.add_argument('--quiet', action='store_true')
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    exc_p = a.exceptions or os.path.join(root, 'registry', 'exceptions.json')
    pin_p = a.pins or os.path.join(root, 'registry', 'pins.json')
    out = a.out or os.path.join(root, 'build')
    d = load(root)
    ck = Checker(root, d, skip_row=a.test_skip_row)
    ck.vocab = w7_vocab(root)
    ck.run(d['owner'])
    pins = json.load(open(pin_p, encoding='utf-8')) if os.path.isfile(pin_p) else {'pins': []}
    pin_errors = check_pins(ck, pins)
    errs = collect_errors(ck, pin_errors)
    if a.write_exceptions:
        if os.path.exists(exc_p):
            print('check_refs: %s 已經存在，拒絕重新產生或覆寫（例外清單只能在第一次產生；之後只能刪）。' % exc_p)
            return 2
        lst = []
        for k, e in sorted(errs.items(), key=lambda x: x[0]):
            if k[0] in EXCEPTABLE:
                lst.append(collections.OrderedDict(code=k[0], file=k[1], key=k[2], reason=e.get('reason') or '',
                                                   status=STATUS_OF[k[0]], approved_by='', approved_at='',
                                                   clear_by='階段 1.5' if k[0] == 'E3' else CLEAR_BY.get(e.get('kind'), '階段 2')))
        write_text(exc_p, json.dumps(collections.OrderedDict(
            version=1, note='R0.5 階段 1 例外清單。由 check_refs.py --write-exceptions 第一次產生；站長整批核准後才填 approved_by／approved_at。之後只能刪，不能自動加。',
            exceptions=lst), ensure_ascii=False, indent=1) + '\n')
        print('check_refs: 已產生 %s（%d 筆，全部未核准）' % (exc_p, len(lst)))
    exc = json.load(open(exc_p, encoding='utf-8')) if os.path.isfile(exc_p) else {'exceptions': []}
    probs = judge(errs, exc, a.draft)
    W = warnings(ck)
    rep = dict(errors=[dict(code=k[0], file=k[1], key=k[2], count=e['count'], reason=e.get('reason'), line=e.get('line'),
                            status=e.get('status'), kind=e.get('kind'), name=e.get('name'), ents=e.get('ents'), cands=e.get('cands'))
                       for k, e in sorted(errs.items())],
               problems=[dict(kind=p[0], code=p[1][0], file=p[1][1], key=p[1][2], why=p[2]) for p in sorted(probs)],
               coverage={s: dict(rule=v['rule'], action=v['action'], n=v['n'], file=v['file']) for s, v in ck.sigs.items()},
               rows=[{k: v for k, v in r.items() if k != 'ctx'} for r in ck.res.rows],
               warnings=W, draft=a.draft)
    write_text(os.path.join(out, 'registry_report.json'), json.dumps(rep, ensure_ascii=False, indent=1, default=str) + '\n')
    write_text(os.path.join(out, 'registry_report.md'), md_report(ck, errs, probs, W, exc, a.draft))
    cnt = collections.Counter(k[0] for k in errs)
    if not a.quiet:
        print('check_refs: ' + '、'.join('%s %d' % (c, cnt.get(c, 0)) for c in ERROR_CODES) +
              '；建置%s' % ('通過' if not probs else '失敗（%d 個問題，見 build/registry_report.md）' % len(probs)))
        for kind, k, why in sorted(probs)[:30]:
            print('  [%s] %s %s %s：%s' % (kind, k[0], k[1], k[2], why))
        if len(probs) > 30:
            print('  …（共 %d 個，完整清單在報告）' % len(probs))
    return 1 if probs else 0


if __name__ == '__main__':
    sys.exit(main())
