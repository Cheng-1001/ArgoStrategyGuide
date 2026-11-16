// R0.5 stage 1 (plan v5, B8): capture the behaviour baseline of the site and the fixed-links list.
// Usage (repo root):
//   node tests/baseline_capture.js                 -> writes tests/baseline/{panels,resources,operations,transfer}.json,
//                                                      tests/baseline/fixtures/* and tests/fixed_links.json
//   (run it on the implementation start commit only; tests/baseline_compare.js checks a tree against it)
// What is captured (design line 380; no private data):
//   structure  - every detail panel (window.__auditIds / __detail): a hash of its text and of its link targets
//   resources  - every icon file referenced by gameicons / recicons / staticons + the sprite sheets: sha256
//   operations - every route, a set of search terms, every data-go / data-goview link (what it opens)
//   transfer   - mobile (390 px) cold-cache first-load transfer size (G7 method; stage 1 only records it)
// Data written outside builds (reports.js, pending.js, jmmeta.js, formcfg.js) is served from tests/baseline/fixtures/
// in both capture and compare, so an Apps Script / Actions push never changes the result (G5, design Q13).
'use strict';
const fs = require('fs'), path = require('path'), http = require('http'), crypto = require('crypto');
const EXTERNAL = ['reports.js', 'pending.js', 'jmmeta.js', 'formcfg.js'];
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.css': 'text/css', '.woff2': 'font/woff2' };
const sha = b => crypto.createHash('sha256').update(b).digest('hex');
const ROUTE_VIEWS = ['map', 'monsters', 'equip', 'items', 'props', 'npcs', 'quests', 'recipes', 'dungeons', 'classes', 'bosses',
  'report', 'feedback', 'about', 'changelog'];
const SEARCHES = [ // [view, term] - includes the renamed names (design "現況" row 5: Shark Shell, Leaf Fragment, Pumba's Ring)
  ['items', 'Shark Shell'], ['items', 'Leaf Fragment'], ['equip', "Pumba's Ring"], ['items', '腐化碎片'], ['items', 'Fragment Corrompu'],
  ['equip', '墮落者之戒'], ['equip', 'Training Dagger'], ['equip', 'Training Lantern'], ['props', 'Training Lantern'], ['monsters', 'Forest Treant'],
  ['npcs', 'Alchemist'], ['recipes', 'Slime'], ['monsters', 'Nymbrea']];

function serve(root, fixtures) {
  return new Promise(res => {
    const srv = http.createServer((q, r) => {
      let u = decodeURIComponent(q.url.split('?')[0]);
      if (u === '/') u = '/index.html';
      const name = u.slice(1);
      let f = path.join(root, name);
      if (fixtures && EXTERNAL.includes(name) && fs.existsSync(path.join(fixtures, name))) f = path.join(fixtures, name);
      if (!f.startsWith(root) && !(fixtures && f.startsWith(fixtures))) { r.writeHead(403); return r.end(); }
      fs.readFile(f, (e, b) => {
        if (e) { r.writeHead(404); return r.end(); }
        r.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
        r.end(b);
      });
    });
    srv.listen(0, '127.0.0.1', () => res(srv));
  });
}

async function openPage(browser, base, vp) {
  const ctx = await browser.newContext({ viewport: vp || { width: 1280, height: 900 } });
  await ctx.addInitScript(() => { try { localStorage.setItem('sao-tour-v1', '1'); } catch (e) {} });
  const p = await ctx.newPage();
  p._errs = [];
  p.on('pageerror', e => p._errs.push(e.message));
  await p.goto(base + 'index.html#f1-monsters');
  await p.waitForFunction(() => typeof window.__detail === 'function' && typeof window.__auditIds === 'function', null, { timeout: 60000 });
  await p.waitForTimeout(800);
  return p;
}

const norm = s => String(s || '').replace(/\s+/g, ' ').trim();

async function panels(p) {
  return p.evaluate(() => {
    const W = document.createElement('div'), out = {}, links = new Set(), ids = window.__auditIds();
    const h = s => { let x = 2166136261; for (let i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619) >>> 0; } return ('0000000' + x.toString(16)).slice(-8); };
    for (const [t, L] of Object.entries(ids)) for (const i of L) {
      let html;
      try { html = window.__detail(t, i); } catch (e) { out[t + '|' + i] = 'ERR:' + e.message; continue; }
      W.innerHTML = html;
      const go = [...W.querySelectorAll('[data-go],[data-goview]')].map(a => a.dataset.go ? 'go:' + a.dataset.go : 'gv:' + a.dataset.goview);
      go.forEach(g => links.add(g));
      const imgs = [...W.querySelectorAll('img')].map(im => im.getAttribute('src'));
      out[t + '|' + i] = h((W.textContent || '').replace(/\s+/g, ' ').trim()) + ':' + h(go.join('\n')) + ':' + h(imgs.join('\n'));
    }
    return { out, links: [...links].sort() };
  });
}

// what does a link open?  Reuse a real link in a real panel (the page's own handler), change its target, click it.
async function probeGo(p, g) {
  p._errs.length = 0;
  const t = await p.evaluate(g => {
    const card = document.querySelector('.card[data-key="m|m0"]');
    if (!card) return 'NO-BASE';
    card.click();
    const pb = document.getElementById('pBody');
    const a = pb.querySelector('[data-go]');
    if (!a) return 'NO-LINK';
    a.dataset.go = g;
    a.click();
    return pb.textContent;
  }, g);
  return { text: norm(t).slice(0, 60), errs: [...p._errs] };
}

async function goviewProbe(p, base, g) {
  // open the source panel through its own list (equip view), then retarget its data-goview button
  p._errs.length = 0;
  const r = await p.evaluate(async g => {
    const box = () => { const bs = document.querySelectorAll('.gvbox'); return bs.length ? bs[bs.length - 1].textContent : ''; };
    document.querySelectorAll('.gvbox').forEach(() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })));
    const pb = document.getElementById('pBody');
    const a = pb.querySelector('[data-goview]');
    if (!a) return 'NO-LINK';
    a.dataset.goview = g;
    a.click();
    await new Promise(r => setTimeout(r, 30));
    const t = box();
    document.querySelectorAll('.gvbox').forEach(() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })));
    return t;
  }, g);
  // the pop-up keeps a history ("← 上一個"); that depends on what was probed before, so it is not part of the result
  return { text: norm(r).replace(/^← 上一個\s*/, '').slice(0, 60), errs: [...p._errs] };
}

async function openGoviewBase(p) {
  await p.evaluate(() => { location.hash = '#f1-equip'; });
  await p.waitForTimeout(700);
  return p.evaluate(() => {
    const c = document.querySelector('.card[data-key="e|1760"]') || document.querySelector('#view-equip .card[data-key]');
    c.click();
    return !!document.getElementById('pBody').querySelector('[data-goview]');
  });
}

async function routes(p) {
  const out = {};
  for (const f of [1, 2, 3]) for (const v of ROUTE_VIEWS) {
    if (f > 1 && ['report', 'feedback', 'about', 'changelog'].includes(v)) continue;
    p._errs.length = 0;
    const hsh = '#f' + f + '-' + v;
    await p.evaluate(h => { location.hash = h; }, hsh);
    await p.waitForTimeout(250);
    const r = await p.evaluate(() => {
      const vis = [...document.querySelectorAll('[id^="view-"]')].filter(x => getComputedStyle(x).display !== 'none').map(x => x.id);
      return { views: vis, hash: location.hash };
    });
    out[hsh] = { views: r.views, hash: r.hash, errs: [...p._errs] };
  }
  return out;
}

async function searches(p) {
  const out = {};
  for (const [v, q] of SEARCHES) {
    await p.evaluate(h => { location.hash = h; }, '#f1-' + v);
    await p.waitForTimeout(300);
    await p.fill('#q', q);
    await p.waitForTimeout(500);
    out[v + '|' + q] = await p.evaluate(v => [...document.querySelectorAll('#view-' + v + ' .card[data-key]')].filter(c => c.offsetParent).map(c => c.dataset.key).sort(), v);
    await p.fill('#q', '');
  }
  return out;
}

async function transfer(browser, base) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await ctx.addInitScript(() => { try { localStorage.setItem('sao-tour-v1', '1'); } catch (e) {} });
  const p = await ctx.newPage();
  const cdp = await ctx.newCDPSession(p);
  await cdp.send('Network.enable');
  await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
  let bytes = 0, n = 0;
  cdp.on('Network.loadingFinished', e => { bytes += e.encodedDataLength; n++; });
  await p.goto(base + 'index.html', { waitUntil: 'networkidle' });
  await p.waitForTimeout(1500);
  const sw = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  await ctx.close();
  return { bytes, requests: n, horizontalOverflow: sw };
}

function resources(root, data) {
  const files = new Set(['equip.png', 'props.png', 'items.png']);
  for (const src of ['SAO_GAMEICONS', 'SAO_RECICONS', 'SAO_STATICONS']) for (const v of Object.values(data[src] || {})) files.add(v);
  const out = {};
  for (const f of [...files].sort()) {
    const p = path.join(root, f);
    out[f] = fs.existsSync(p) ? sha(fs.readFileSync(p)) : 'MISSING';
  }
  return out;
}

async function capture(root, fixtures, opts) {
  opts = opts || {};
  const { chromium } = require('playwright');
  const srv = await serve(root, fixtures);
  const base = 'http://127.0.0.1:' + srv.address().port + '/';
  const browser = await chromium.launch();
  try {
    const p = await openPage(browser, base);
    const data = await p.evaluate(() => ({ SAO_GAMEICONS: window.SAO_GAMEICONS, SAO_RECICONS: window.SAO_RECICONS, SAO_STATICONS: window.SAO_STATICONS }));
    const pn = await panels(p);
    const res = { panels: pn.out, links: pn.links, resources: resources(root, data) };
    if (opts.panelsOnly) return res;
    res.routes = await routes(p);
    res.searches = await searches(p);
    if (opts.transfer) res.transfer = await transfer(browser, base);
    res.pageErrors = [...p._errs];
    return res;
  } finally { await browser.close(); srv.close(); }
}

// resolve a list of fixed links on a tree: route -> which view; entity go -> panel text head; goview -> pop-up text head
async function resolveLinks(root, fixtures, links) {
  const { chromium } = require('playwright');
  const srv = await serve(root, fixtures);
  const base = 'http://127.0.0.1:' + srv.address().port + '/';
  const browser = await chromium.launch();
  const out = {};
  try {
    const p = await openPage(browser, base);
    for (const l of links.filter(x => x.type === 'route')) {
      p._errs.length = 0;
      await p.evaluate(h => { location.hash = h; }, l.target);
      await p.waitForTimeout(250);
      const vis = await p.evaluate(() => [...document.querySelectorAll('[id^="view-"]')].filter(x => getComputedStyle(x).display !== 'none').map(x => x.id).join(',') + '@' + location.hash);
      out[l.id] = { got: vis, errs: [...p._errs] };
    }
    await p.evaluate(() => { location.hash = '#f1-monsters'; });
    await p.waitForTimeout(500);
    for (const l of links.filter(x => x.type === 'entity')) {
      const r = await probeGo(p, l.target);
      out[l.id] = { got: r.text, errs: r.errs };
    }
    for (const l of links.filter(x => x.type === 'search')) {
      const [v, q] = l.target.split(/\|(.+)/);
      await p.evaluate(h => { location.hash = h; }, '#f1-' + v);
      await p.waitForTimeout(300);
      await p.fill('#q', q);
      await p.waitForTimeout(500);
      const k = await p.evaluate(v => [...document.querySelectorAll('#view-' + v + ' .card[data-key]')].filter(c => c.offsetParent).map(c => c.dataset.key).sort().join(','), v);
      await p.fill('#q', '');
      out[l.id] = { got: k, errs: [] };
    }
    const gvl = links.filter(x => x.type === 'goview');
    if (gvl.length) {
      await openGoviewBase(p);
      for (const l of gvl) {
        await openGoviewBase(p);
        const r = await goviewProbe(p, base, l.target);
        out[l.id] = { got: r.text, errs: r.errs };
      }
    }
  } finally { await browser.close(); srv.close(); }
  return out;
}

module.exports = { capture, resolveLinks, serve, EXTERNAL, ROUTE_VIEWS, SEARCHES };

if (require.main === module) {
  (async () => {
    const ROOT = path.resolve(process.argv[2] || path.join(__dirname, '..'));
    const outDir = path.join(ROOT, 'tests', 'baseline');
    const fix = path.join(outDir, 'fixtures');
    fs.mkdirSync(fix, { recursive: true });
    for (const f of EXTERNAL) if (fs.existsSync(path.join(ROOT, f))) fs.copyFileSync(path.join(ROOT, f), path.join(fix, f));
    const r = await capture(ROOT, fix, { transfer: true });
    const w = (n, o) => fs.writeFileSync(path.join(outDir, n), JSON.stringify(o, null, 0).replace(/,"/g, ',\n"') + '\n');
    w('panels.json', r.panels);
    w('resources.json', r.resources);
    w('operations.json', { routes: r.routes, searches: r.searches });
    w('transfer.json', r.transfer);
    // fixed links (design line 382): official-letter links, every route, every data-go / data-goview in the baseline,
    // links in changelog.js / reports.js (report-number links), the renamed names (search), and the plan's extra entries
    const links = [];
    const add = (type, target, expect, why) => links.push({ id: type + ':' + target, type, target, expect, why });
    for (const [h, v] of Object.entries(r.routes)) add('route', h, v.views.join(',') + '@' + v.hash, h === '#f1-recipes' || h === '#f1-equip' ? '官方信件裡的連結；分頁網址' : '分頁網址');
    const res = await resolveLinks(ROOT, fix, r.links.filter(x => x.startsWith('go:')).map(x => ({ id: 'entity:' + x.slice(3), type: 'entity', target: x.slice(3) }))
      .concat(r.links.filter(x => x.startsWith('gv:')).map(x => ({ id: 'goview:' + x.slice(3), type: 'goview', target: x.slice(3) })))
      .concat(Object.keys(r.searches).map(k => ({ id: 'search:' + k, type: 'search', target: k }))));
    for (const x of r.links) {
      const type = x.startsWith('go:') ? 'entity' : 'goview', t = x.slice(3), g = res[type + ':' + t];
      add(type, t, g.errs.length ? 'ERROR:' + g.errs[0] : g.got, '基準快照裡的連結');
    }
    for (const [k, v] of Object.entries(r.searches)) add('search', k, v.join(','), /Shark Shell|Leaf Fragment|Pumba/.test(k) ? '改名的舊名（「現況」第 5 列）' : '搜尋詞');
    const extra = links.filter(l => /Corrupted Fragment \(3\)|e\|2484|Training Lantern/.test(l.target)).length;
    fs.writeFileSync(path.join(ROOT, 'tests', 'fixed_links.json'), JSON.stringify({
      version: 1, note: 'R0.5 階段 1 固定連結清單（定稿第 382 行）。由 tests/baseline_capture.js 在實作起點產生；expect 是起點打開的結果。改鍵要同時改這裡並說明原因。',
      links }, null, 0).replace(/},\{/g, '},\n{') + '\n');
    const broken = links.filter(l => String(l.expect).startsWith('ERROR:'));
    console.log('panels', Object.keys(r.panels).length, 'links', links.length, '(plan extras present:', extra, ') broken at baseline', broken.length,
      'transfer', JSON.stringify(r.transfer), 'pageErrors', r.pageErrors.length);
    if (broken.length) console.log(broken.slice(0, 10).map(b => b.id + ' ' + b.expect).join('\n'));
  })().catch(e => { console.error(e); process.exit(1); });
}
