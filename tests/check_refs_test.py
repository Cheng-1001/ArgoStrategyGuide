#!/usr/bin/env python3
"""R0.5 stage 1 regression tests for tools/check_refs.py (plan v5: cases 1-26; 25-26 use tests/baseline_compare.js; 27-31 added after the P1 reviews).

Every case works on a temporary copy of the repo: the data files are changed there by appending a small JS
statement at the end of the file (it runs after the file's own code, like the page would), so the real data is
never touched.  Fake pins / fake approved exceptions live only in the temporary copy.

Usage (repo root):  python3 tests/check_refs_test.py      -> prints one line per case, "ALL PASSED" or exit 1
Needs: Python 3, Node (same as the checker); cases 25-26 also need Playwright Chromium.
"""
import json, os, shutil, subprocess, sys, tempfile, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for s in (sys.stdout, sys.stderr):
    try:
        s.reconfigure(encoding='utf-8')
    except Exception:
        pass


def copy_repo():
    d = tempfile.mkdtemp(prefix='checkrefs_')
    for f in os.listdir(ROOT):
        if f.endswith('.js') or f == 'index.html':
            shutil.copy2(os.path.join(ROOT, f), d)
    for sub in ('src', 'tools', 'registry', 'icons'):
        if os.path.isdir(os.path.join(ROOT, sub)):
            shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub), ignore=shutil.ignore_patterns('__pycache__'))
    os.makedirs(os.path.join(d, 'registry'), exist_ok=True)
    return d


def append(d, file, js):
    with open(os.path.join(d, file), 'a', encoding='utf-8', newline='\n') as f:
        f.write('\n;' + js + '\n')


def run(d, exceptions=None, pins=None, extra=()):
    args = [sys.executable, os.path.join(d, 'tools', 'check_refs.py'), '--root', d, '--out', os.path.join(d, 'build'), '--quiet']
    args += ['--exceptions', exceptions or os.path.join(d, 'registry', 'no_exceptions.json')]
    args += ['--pins', pins or os.path.join(d, 'registry', 'pins.json')]
    args += list(extra)
    p = subprocess.run(args, capture_output=True)
    rep = json.load(open(os.path.join(d, 'build', 'registry_report.json'), encoding='utf-8'))
    rep['_exit'] = p.returncode
    rep['_out'] = p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')
    return rep


def errs(rep, code=None):
    return [e for e in rep['errors'] if code is None or e['code'] == code]


def has(rep, code, key_part, file=None):
    return any(e['code'] == code and key_part in e['key'] and (file is None or e['file'] == file) for e in rep['errors'])


def write_pins(d, pins):
    p = os.path.join(d, 'registry', 'test_pins.json')
    json.dump({'version': 1, 'pins': pins}, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    return p


def approved_exceptions(d, drop=()):
    """the real flow writes the list with --write-exceptions; here it is approved with a test marker (temp copy only)"""
    p = os.path.join(d, 'registry', 'test_exceptions.json')
    if os.path.exists(p):
        os.remove(p)
    subprocess.run([sys.executable, os.path.join(d, 'tools', 'check_refs.py'), '--root', d, '--out', os.path.join(d, 'build'),
                    '--quiet', '--write-exceptions', '--exceptions', p, '--pins', os.path.join(d, 'registry', 'pins.json')],
                   capture_output=True)
    ex = json.load(open(p, encoding='utf-8'))
    ex['exceptions'] = [dict(e, approved_by='test', approved_at='2026-01-01') for e in ex['exceptions']
                        if not any(x in e['key'] for x in drop)]
    json.dump(ex, open(p, 'w', encoding='utf-8'), ensure_ascii=False)
    return p


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


RESULTS = []


def case(n, title):
    def deco(fn):
        def wrap():
            d = copy_repo()
            try:
                ok, why = fn(d)
            except Exception as e:      # a crash is a failure, with the reason
                ok, why = False, 'exception: %r' % e
            finally:
                shutil.rmtree(d, ignore_errors=True)
            RESULTS.append((n, title, ok, why))
            print('%s case %2d %s%s' % ('PASS' if ok else 'FAIL', n, title, '' if ok else '  -> ' + why), flush=True)
        wrap.n = n
        return wrap
    return deco


# ------------------------------------------------------------------ cases 1-24
@case(1, '墮落者之戒：把 2484 掛回死神之戒 → E6')
def c1(d):
    pins = write_pins(d, [dict(id='t2484', type='identity', names=['Ring of the Fallen'], oid=2484)])
    base = run(d, pins=pins)
    if errs(base, 'E6'):
        return False, '未改資料時就有 E6：%s' % errs(base, 'E6')
    append(d, 'gameinfo.js', 'window.SAO_GAMEINFO.items.find(g=>g.en==="Ring of the Reaper").oid=[2484];')
    r = run(d, pins=pins)
    return has(r, 'E6', 'link:Ring of the Reaper'), json.dumps(errs(r, 'E6'), ensure_ascii=False)[:300]


@case(2, '銅／鐵手套圖示：對調兩件的圖示檔 → E7')
def c2(d):
    a, b = os.path.join(d, 'icons/game/copper_gloves.png'), os.path.join(d, 'icons/game/iron_gloves.png')
    pins = write_pins(d, [dict(id='tcopper', type='icon', name='Copper Gloves', file='icons/game/copper_gloves.png', sha256=sha(a)),
                          dict(id='tiron', type='icon', name='Iron Gloves', file='icons/game/iron_gloves.png', sha256=sha(b))])
    if errs(run(d, pins=pins), 'E7'):
        return False, '未改資料時就有 E7'
    ta, tb = open(a, 'rb').read(), open(b, 'rb').read()
    open(a, 'wb').write(tb)
    open(b, 'wb').write(ta)
    r = run(d, pins=pins)
    return has(r, 'E7', 'tcopper') and has(r, 'E7', 'tiron'), json.dumps(errs(r, 'E7'), ensure_ascii=False)[:300]


@case(3, 'Slime Tear 對不到：E1；在例外清單上就通過，從清單拿掉就擋下')
def c3(d):
    r = run(d)
    if not has(r, 'E1', 'Slime Tear'):
        return False, '沒有 Slime Tear 的 E1'
    ex = approved_exceptions(d)
    ok = run(d, exceptions=ex)
    ex2 = approved_exceptions(d, drop=('Slime Tear',))
    bad = run(d, exceptions=ex2)
    news = [p for p in bad['problems'] if p['kind'] == 'new']
    return ok['_exit'] == 0 and bad['_exit'] == 1 and news and all('Slime Tear' in p['key'] for p in news), \
        'exit %s／%s、new %s' % (ok['_exit'], bad['_exit'], [p['key'] for p in news])


@case(4, 'Slime Tear 解析得到但沒接 2370 → W7 候選裡有 2370（不要求 E1）')
def c4(d):
    append(d, 'data.js', 'window.SAO.ITEMS["Slime Tear"]={id:"Slime Tear",fr:null,r:"c",lv:1,cat:"loot",lore:"",dmg:null,st:null,ic:-1};')
    r = run(d)
    w = [x for x in r['warnings']['W7'] if x['name'] == 'Slime Tear' and x['src'].startswith('data.js')]
    return bool(w) and any(c['id'] == 2370 for c in w[0]['cands']), json.dumps(w, ensure_ascii=False)[:300]


@case(5, 'Slime Tear 釘選後關聯不見 → E6')
def c5(d):
    pins = write_pins(d, [dict(id='tslime', type='identity', names=['Slime Tear'], oid=2370)])
    r = run(d, pins=pins)
    return has(r, 'E6', 'pin:tslime'), json.dumps(errs(r, 'E6'), ensure_ascii=False)[:300]


@case(6, '森林連結：兩種情境 W7 候選裡都有 1448（跨資料檔線索）')
def c6(d):
    append(d, 'data.js', 'window.SAO.ITEMS["Bond of the Sylve"]={id:"Bond of the Sylve",fr:null,r:"s",lv:1,cat:"artifact",lore:"",dmg:null,st:null,ic:-1};')
    r1 = run(d)
    w1 = [x for x in r1['warnings']['W7'] if x['name'] == 'Bond of the Sylve' and x['src'].startswith('data.js')]
    append(d, 'gameinfo.js', 'window.SAO_GAMEINFO.items.push({en:"Bond of the Sylve",oid:[1448],site:null,lvl:null,desc:"",obt:[]});')
    r2 = run(d)
    w2 = [x for x in r2['warnings']['W7'] if x['name'] == 'Bond of the Sylve' and x['src'].startswith('data.js')]
    c1 = [c for c in (w1[0]['cands'] if w1 else []) if c['id'] == 1448]
    c2 = [c for c in (w2[0]['cands'] if w2 else []) if c['id'] == 1448]
    return bool(c1) and bool(c2) and '跨檔線索' in c1[0]['how'], '①%s ②%s' % (c1, c2)


@case(7, '腐化碎片 2380：掛回綠框 → 至少有 E6（正式釘選）')
def c7(d):
    append(d, 'gameinfo.js', 'window.SAO_GAMEINFO.items.find(g=>g.en==="Corrupted Fragment").oid=[2380];')
    r = run(d)
    return has(r, 'E6', 'corrupted-fragment-3'), json.dumps(errs(r, 'E6'), ensure_ascii=False)[:300]


@case(8, 'Training Dagger 現況：名字解析成 1760（唯一）；「(2)」是 E1')
def c8(d):
    sys.path.insert(0, os.path.join(d, 'tools'))
    import importlib
    import check_refs as C
    importlib.reload(C)
    ld = C.load(d)
    m = C.Model(ld, d)
    st, ents, how = m.items.resolve('Training Dagger')
    sys.path.pop(0)
    r = run(d)
    e1 = [e['key'] for e in errs(r, 'E1') if 'Training Dagger (2)' in e['key']]
    return st == 'resolved' and ents == ['C:1760'] and any('out:Training Dagger (2)' in k for k in e1) and \
        not any(e['code'] == 'E2' and 'Training Dagger' in e['key'] for e in r['errors']), '%s %s %s' % (st, ents, e1)


@case(9, 'Training Dagger 同名：另加同名紀錄、gameicons 的鍵改成「Training Dagger」→ 這個鍵是 E2')
def c9(d):
    append(d, 'data.js', 'window.SAO.ITEMS["Training Dagger"]={id:"Training Dagger",fr:null,r:"c",lv:1,cat:"weapon",lore:"",dmg:null,st:null,ic:-1};')
    append(d, 'gameicons.js', 'var _g=window.SAO_GAMEICONS;_g["Training Dagger"]=_g["Training Dagger (2)"];delete _g["Training Dagger (2)"];')
    r = run(d)
    return has(r, 'E2', 'gameicons:Training Dagger'), [e['key'] for e in errs(r, 'E2') if 'Training Dagger' in e['key']]


@case(10, 'Forest Treant 同名：hints 加只寫「Forest Treant」的引用，#043 改回遊戲名 → E2')
def c10(d):
    append(d, 'data.js', 'window.SAO.M.find(m=>m.name==="Evil Forest Treant").name="Forest Treant";')
    append(d, 'hints.js', 'window.SAO_HINTS["1"]["Forest Treant"]=["x","y",0];')
    r = run(d)
    return has(r, 'E2', 'F1/hint:Forest Treant'), [e['key'] for e in errs(r, 'E2') if 'Forest Treant' in e['key']]


@case(11, 'Training Lantern 同 id：E3；在清單上就通過，拿掉就擋下')
def c11(d):
    r = run(d)
    if not has(r, 'E3', 'id:1627'):
        return False, '沒有 1627 的 E3'
    ok = run(d, exceptions=approved_exceptions(d))
    bad = run(d, exceptions=approved_exceptions(d, drop=('id:1627',)))
    return ok['_exit'] == 0 and bad['_exit'] == 1 and any(p['kind'] == 'new' and p['key'] == 'id:1627' for p in bad['problems']), \
        'exit %s／%s' % (ok['_exit'], bad['_exit'])


@case(12, '新的 E3：Training Dagger (2) 配方列的 id 改成 1760 → E3 出現')
def c12(d):
    ex = approved_exceptions(d)
    append(d, 'recipes.js', 'window.SAO_RECIPES["Starting Merchant"].items.find(r=>r[1]==="Training Dagger (2)")[0]=1760;')
    r = run(d, exceptions=ex)
    stale = [p['key'] for p in r['problems'] if p['kind'] == 'stale']
    return has(r, 'E3', 'id:1760') and r['_exit'] == 1, 'E3 1760=%s、stale=%s' % (has(r, 'E3', 'id:1760'), stale)


@case(13, '新的對不到：配方材料加一個不存在的名稱 → E1，建置失敗')
def c13(d):
    ex = approved_exceptions(d)
    append(d, 'recipes.js', 'window.SAO_RECIPES["Iron Accessories"].items[0][3].push(["Nonexistent Test Material",1]);')
    r = run(d, exceptions=ex)
    return r['_exit'] == 1 and any(p['kind'] == 'new' and 'Nonexistent Test Material' in p['key'] for p in r['problems']), r['_out'][:300]


@case(14, 'E2 從清單拿掉（Leggings of Ika）→ 建置失敗')
def c14(d):
    r = run(d, exceptions=approved_exceptions(d, drop=('Leggings of Ika',)))
    return r['_exit'] == 1 and any(p['kind'] == 'new' and p['code'] == 'E2' and 'Leggings of Ika' in p['key'] for p in r['problems']), r['_out'][:300]


@case(15, '例外修好了：清單不動 → 建置失敗，要求刪掉那一筆')
def c15(d):
    ex = approved_exceptions(d)
    append(d, 'recipes.js', 'var _r=window.SAO_RECIPES["Iron Accessories"].items.find(r=>r[3].some(m=>m[0]==="Iron String"));_r[3]=_r[3].filter(m=>m[0]!=="Iron String");')
    r = run(d, exceptions=ex)
    return r['_exit'] == 1 and any(p['kind'] == 'stale' and 'Iron String' in p['key'] for p in r['problems']), r['_out'][:300]


@case(16, '總數相同的掉包：修一個、另加一個新的 → 建置失敗（不用總數門檻）')
def c16(d):
    ex = approved_exceptions(d)
    append(d, 'recipes.js', 'var _r=window.SAO_RECIPES["Iron Accessories"].items.find(r=>r[3].some(m=>m[0]==="Iron String"));_r[3]=_r[3].map(m=>m[0]==="Iron String"?["Swapped Test Material",m[1]]:m);')
    r = run(d, exceptions=ex)
    kinds = {p['kind'] for p in r['problems']}
    return r['_exit'] == 1 and {'stale', 'new'} <= kinds, str(kinds)


@case(17, '建置外資料：改 reports.js、pending.js、jmmeta.js、formcfg.js → E 類結果和結束代碼不變')
def c17(d):
    ex = approved_exceptions(d)
    a = run(d, exceptions=ex)
    append(d, 'reports.js', 'window.SAO_REPORTS.push({id:"R9999",type:"monster",name:"No Such Test Monster",floor:1,newField:1});')
    append(d, 'jmmeta.js', 'window.SAO_JM.testField={x:1};')
    append(d, 'formcfg.js', 'window.SAO_FORM.testField=1;')
    open(os.path.join(d, 'pending.js'), 'a', encoding='utf-8').write('\n// test\n')
    b = run(d, exceptions=ex)
    ka = sorted((e['code'], e['file'], e['key']) for e in a['errors'])
    kb = sorted((e['code'], e['file'], e['key']) for e in b['errors'])
    return ka == kb and a['_exit'] == b['_exit'] == 0, 'exit %s／%s、E 類相同=%s、W11=%s' % (a['_exit'], b['_exit'], ka == kb, b['warnings']['W11'])


@case(18, '正規化：去重音後唯一（Anneau Dechu）→ 解析成功，標「靠正規化」')
def c18(d):
    append(d, 'recipes.js', 'window.SAO_RECIPES["Iron Accessories"].items[0][3].push(["Anneau Dechu",1]);')
    r = run(d)
    rows = [x for x in r['rows'] if x['name'] == 'Anneau Dechu']
    return bool(rows) and rows[0]['status'] == 'resolved' and rows[0]['how'] == 'normalized' and rows[0]['ents'] == ['C:2484'], str(rows)[:300]


@case(19, '正規化：去重音後碰撞 → E2')
def c19(d):
    append(d, 'data.js', 'window.SAO.ITEMS["Anneau Dèchu"]={id:"Anneau Dèchu",fr:null,r:"c",lv:1,cat:"loot",lore:"",dmg:null,st:null,ic:-1};')
    append(d, 'recipes.js', 'window.SAO_RECIPES["Iron Accessories"].items[0][3].push(["Anneau Dechu",1]);')
    r = run(d)
    return has(r, 'E2', 'mat:Anneau Dechu'), [e['key'] for e in errs(r, 'E2') if 'Anneau' in e['key']]


@case(20, '單複數只當候選：Leaf Fragment → E1，報告列 Leaf Fragments 為候選')
def c20(d):
    append(d, 'recipes.js', 'window.SAO_RECIPES["Iron Accessories"].items[0][3].push(["Leaf Fragment",1]);')
    r = run(d)
    e = [x for x in errs(r, 'E1') if 'mat:Leaf Fragment' in x['key']]
    return bool(e) and 'leaf fragments' in (e[0].get('cands') or []), str(e)[:300]


@case(21, 'E9 欄位層：資料檔加一個沒登記的欄位 → E9（新紀錄用既有欄位則沒有 E9）')
def c21(d):
    append(d, 'data.js', 'window.SAO.ITEMS["Normal New Test Item"]={id:"Normal New Test Item",fr:null,r:"c",lv:1,cat:"loot",lore:"",dmg:null,st:null,ic:-1};')
    append(d, 'recipes.js', 'window.SAO_RECIPES["Iron Accessories"].items.push([null,"Normal New Test Item",10,[["Iron Ingot",1]],"1","c","acc",1,"shot"]);')
    a = run(d)
    if errs(a, 'E9'):
        return False, '正常的新紀錄產生了 E9：%s' % errs(a, 'E9')
    append(d, 'data.js', 'window.SAO.ITEMS["Normal New Test Item"].newRef="Iron Ingot";')
    r = run(d)
    return has(r, 'E9', 'field:SAO.ITEMS{}.newRef'), [e['key'] for e in errs(r, 'E9')]


@case(22, 'E9 列層：掃描程式漏掉一列（測試掛鉤）→ E9')
def c22(d):
    r = run(d, extra=['--test-skip-row', 'SAO_RECIPES{}.items[][3][][0]'])
    return has(r, 'E9', 'row:SAO_RECIPES{}.items[][3][][0]'), [e['key'] for e in errs(r, 'E9')][:3]


@case(23, '重複 NPC（W5）：把 Boar and Wolf loot buyer 加回新手商人旁邊 → W5 列出這一對')
def c23(d):
    append(d, 'npcs.js', 'window.SAO_NPCS["1"].push(["lootBuyers","Boar and Wolf loot buyer",1787,4179,"ref"]);')
    r = run(d)
    w = [x for x in r['warnings']['W5'] if 'Boar and Wolf loot buyer' in x and 'Starting Merchant' in x]
    return bool(w), str(w)[:300]


@case(24, '遊戲和圖鑑數值不同（W2）：gamestats 的 Iron Gloves 等級改成 7 → 只有 gamestats 等級那一項少 1')
def c24(d):
    a = run(d)['warnings']['W2']
    append(d, 'gamestats.js', 'window.SAO_GAMESTATS.items["2042"].lvl=7;')
    b = run(d)['warnings']['W2']
    gone = [x for x in a['gamestats 等級'] if x.startswith('2042 ')]
    still = [x for x in b['配方等級'] if x.startswith('2042 ')]
    return (len(b['gamestats 等級']) == len(a['gamestats 等級']) - 1 and gone and not [x for x in b['gamestats 等級'] if x.startswith('2042 ')]
            and len(b['配方等級']) == len(a['配方等級']) and still and len(b['gameinfo 等級']) == len(a['gameinfo 等級'])), \
        'gamestats %d→%d、配方 %d→%d、gameinfo %d→%d' % (len(a['gamestats 等級']), len(b['gamestats 等級']), len(a['配方等級']),
                                                    len(b['配方等級']), len(a['gameinfo 等級']), len(b['gameinfo 等級']))


def compare(d, only):
    p = subprocess.run(['node', os.path.join(ROOT, 'tests', 'baseline_compare.js'), d, '--links-only', '--only', only],
                       capture_output=True)
    return p.returncode, p.stdout.decode('utf-8', 'replace') + p.stderr.decode('utf-8', 'replace')


@case(25, '固定連結打不開：從官網裝備表刪掉 2484（墮落者之戒）→ 行為比對的 e|2484 是 E5，同批的腐化碎片 (3) 不變')
def c25(d):
    only = r'^(entity:i\|Corrupted Fragment \(3\)|entity:e\|2484)$'
    c0, o0 = compare(d, only)             # unchanged copy: identical
    append(d, 'equip.js', 'window.SAO_EQUIP=window.SAO_EQUIP.filter(r=>r[0]!==2484);')
    c1, o1 = compare(d, only)
    e5 = [l for l in o1.splitlines() if l.startswith('E5 ')]
    return (c0 == 0 and c1 == 1 and len(e5) == 1 and 'entity:e|2484' in e5[0]), (o0[-200:] + ' / ' + o1[-400:])


@case(26, '舊名搜尋：從 index.html 的 ITEM_OLD 拿掉 Shark Shell → 「Shark Shell」搜尋是 E5，其他舊名不變')
def c26(d):
    only = r'^search:items\|(Shark Shell|Leaf Fragment)$'
    c0, o0 = compare(d, only)
    f = os.path.join(d, 'index.html')
    h = open(f, encoding='utf-8').read()
    n = h.count('"Shark Shell": "Shark Carapace", ')
    open(f, 'w', encoding='utf-8', newline='\n').write(h.replace('"Shark Shell": "Shark Carapace", ', ''))
    c1, o1 = compare(d, only)
    e5 = [l for l in o1.splitlines() if l.startswith('E5 ')]
    return (n == 1 and c0 == 0 and c1 == 1 and len(e5) == 1 and 'search:items|Shark Shell' in e5[0]), (o0[-200:] + ' / ' + o1[-400:])


@case(27, 'E9 欄位層（紀錄型容器）：世界王、活動地下城、職業的紀錄加新欄位 → 各自報 E9')
def c27(d):
    append(d, 'bosses.js', 'window.SAO_BOSSES.world[0].drops="Galiath\'s Axe";')
    append(d, 'events.js', 'window.SAO_EVENTS.dungeons[0].reward="Nonexistent Test Item";')
    append(d, 'classes.js', 'window.SAO_CLASSES[0].newRef="Iron Ingot";')
    r = run(d)
    want = ['field:SAO_BOSSES.world[].drops', 'field:SAO_EVENTS.dungeons[].reward', 'field:SAO_CLASSES[].newRef']
    got = [e['key'] for e in errs(r, 'E9')]
    return r['_exit'] == 1 and all(w in got for w in want), str(got)[:300]


@case(28, '例外清單同一筆出現兩次 → 建置失敗（duplicate）')
def c28(d):
    ex = approved_exceptions(d)
    j = json.load(open(ex, encoding='utf-8'))
    j['exceptions'].append(dict(j['exceptions'][0]))
    json.dump(j, open(ex, 'w', encoding='utf-8'), ensure_ascii=False)
    r = run(d, exceptions=ex)
    return r['_exit'] == 1 and [p['kind'] for p in r['problems']] == ['duplicate'], str(r['problems'])[:300]


@case(29, '例外清單登記 E9 → 建置失敗（not-exceptable）；只收 E1、E2、E3')
def c29(d):
    append(d, 'bosses.js', 'window.SAO_BOSSES.world[0].drops="x";')
    ex = approved_exceptions(d)
    j = json.load(open(ex, encoding='utf-8'))
    j['exceptions'].append(dict(code='E9', file='bosses.js', key='field:SAO_BOSSES.world[].drops', reason='test',
                                status='', approved_by='test', approved_at='2026-01-01', clear_by=''))
    json.dump(j, open(ex, 'w', encoding='utf-8'), ensure_ascii=False)
    r = run(d, exceptions=ex)
    return r['_exit'] == 1 and any(p['kind'] == 'not-exceptable' for p in r['problems']), str(r['problems'])[:300]


@case(30, 'Local Farmer：收購商店名只接第 1 層 NPC → 第 2、3 層同名的不會被當成遊戲文字指的 NPC')
def c30(d):
    r = run(d)
    k = 'gameinfo:Wheat/bought-back-by:F1 Local Farmer - Near the Starting City'
    a = [e for e in r['errors'] if e['key'] == k]
    append(d, 'npcs.js', 'window.SAO_NPCS["3"]=window.SAO_NPCS["3"].filter(n=>n[1]!=="Local Farmer");')
    r2 = run(d)
    b = [e for e in r2['errors'] if e['key'] == k]
    return (len(a) == 1 and a[0]['code'] == 'E1' and len(b) == 1 and b[0]['code'] == 'E1'), str(a + b)[:300]


@case(31, '雙欄陣列（座標點、Easy 條件、首領招式）宣告成 tuple：六組各加第三欄 → 各自報 E9')
def c31(d):
    append(d, 'data.js', 'window.SAO.SPOTS[0].area[0].push(9);window.SAO.SPOTS[14].dg.easy[0].push("x");')
    append(d, 'data23.js', 'window.SAO23.floors[2].spots[3].area[0].push(9);window.SAO23.floors[2].spots[0].dg.easy[0].push("x");')
    append(d, 'bosses.js', 'window.SAO_BOSSES.unique[0].attacks[0].push("x");')
    append(d, 'events.js', 'window.SAO_EVENTS.dungeons[0].dg.easy[0].push("x");')
    r = run(d)
    want = ['field:SAO.SPOTS[].area[][2]', 'field:SAO.SPOTS[].dg.easy[][2]', 'field:SAO23.floors{}.spots[].area[][2]',
            'field:SAO23.floors{}.spots[].dg.easy[][2]', 'field:SAO_BOSSES.unique[].attacks[][2]',
            'field:SAO_EVENTS.dungeons[].dg.easy[][2]']
    got = [e['key'] for e in errs(r, 'E9')]
    return r['_exit'] == 1 and sorted(got) == sorted(want), str(got)[:400]


def main():
    cases = sorted([v for v in globals().values() if callable(v) and hasattr(v, 'n')], key=lambda f: f.n)
    only = {int(x) for x in sys.argv[1:]}
    for c in cases:
        if not only or c.n in only:
            c()
    bad = [r for r in RESULTS if not r[2]]
    print('ALL PASSED (%d)' % len(RESULTS) if not bad else 'FAILED %d／%d' % (len(bad), len(RESULTS)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
