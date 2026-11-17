// R0.5 stage 1 (plan v5, B8 / gate G5): check a tree against the behaviour baseline.
// Usage: node tests/baseline_compare.js [repo root] [--links-only] [--only <regex on link id>] [--transfer]
//   - panels / resources / routes / searches must equal tests/baseline/*.json
//   - every entry of tests/fixed_links.json must open what it opened at the start commit; a link that
//     no longer works (or opens something else) is E5
//   - external files (reports.js, pending.js, jmmeta.js, formcfg.js) come from tests/baseline/fixtures/
// Exit 0 = identical; exit 1 = differences (printed one per line; first word is the code).
'use strict';
const fs = require('fs'), path = require('path');
const { capture, resolveLinks } = require('./baseline_capture.js');
const argv = process.argv.slice(2);
const flag = n => argv.includes(n);
const opt = n => { const i = argv.indexOf(n); return i >= 0 ? argv[i + 1] : null; };
const ROOT = path.resolve(argv.find((a, i) => !a.startsWith('--') && argv[i - 1] !== '--only') || path.join(__dirname, '..'));
const HERE = __dirname; // baseline + fixed links always come from the checked-in copy next to this script
const B = n => JSON.parse(fs.readFileSync(path.join(HERE, 'baseline', n), 'utf8'));
const FIX = path.join(HERE, 'baseline', 'fixtures');

(async () => {
  const diffs = [];
  const fixed = JSON.parse(fs.readFileSync(path.join(HERE, 'fixed_links.json'), 'utf8')).links;
  const only = opt('--only') ? new RegExp(opt('--only')) : null;
  if (!flag('--links-only')) {
    const r = await capture(ROOT, FIX, { transfer: flag('--transfer') });
    const P = B('panels.json'), R = B('resources.json'), O = B('operations.json');
    for (const k of new Set([...Object.keys(P), ...Object.keys(r.panels)]))
      if (P[k] !== r.panels[k]) diffs.push('PANEL ' + k + ' ' + (P[k] || '(none)') + ' -> ' + (r.panels[k] || '(none)'));
    for (const k of new Set([...Object.keys(R), ...Object.keys(r.resources)]))
      if (R[k] !== r.resources[k]) diffs.push('RESOURCE ' + k + ' ' + (R[k] || '(none)') + ' -> ' + (r.resources[k] || '(none)'));
    for (const [k, v] of Object.entries(O.routes)) {
      const g = r.routes[k];
      if (!g || g.views.join(',') + '@' + g.hash !== v.views.join(',') + '@' + v.hash || g.errs.length) diffs.push('ROUTE ' + k + ' ' + JSON.stringify(g));
    }
    for (const [k, v] of Object.entries(O.searches)) {
      const g = r.searches[k] || [];
      if (g.join(',') !== v.join(',')) diffs.push('SEARCH ' + k + ' [' + v.join(',') + '] -> [' + g.join(',') + ']');
    }
    if (r.pageErrors.length) diffs.push('PAGEERROR ' + r.pageErrors.join(' | '));
    if (r.transfer) console.log('transfer (mobile 390, cold cache):', JSON.stringify(r.transfer), 'baseline', JSON.stringify(B('transfer.json')));
    console.log('panels', Object.keys(r.panels).length, 'resources', Object.keys(r.resources).length,
      'routes', Object.keys(r.routes).length, 'searches', Object.keys(r.searches).length);
  }
  const L = fixed.filter(l => !only || only.test(l.id));
  let got;
  try { got = await resolveLinks(ROOT, FIX, L); }
  catch (e) { // the page itself does not load: every link is broken
    console.log('LOADFAIL the page did not finish loading: ' + String(e.message || e).split('\n')[0]);
    got = Object.fromEntries(L.map(l => [l.id, { got: '', errs: ['page did not load'] }]));
  }
  for (const l of L) {
    const g = got[l.id];
    const now = g.errs.length ? 'ERROR:' + g.errs[0] : (l.type === 'route' ? g.got : g.got);
    if (now !== l.expect) diffs.push('E5 ' + l.id + ' expect [' + l.expect + '] got [' + now + ']');
  }
  console.log('fixed links checked', L.length);
  for (const d of diffs) console.log(d);
  console.log(diffs.length ? 'DIFFERENCES ' + diffs.length : 'IDENTICAL');
  process.exit(diffs.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
