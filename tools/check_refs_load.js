// R0.5 stage 1: load the site's data files the same way the page does, and print them as JSON.
// Usage: node tools/check_refs_load.js <repo root>
// - The file list is taken from the <script src="x.js"> tags in src/index.html (same list build.py hashes),
//   so a new data file added to the page is seen by the checker (and must be registered in COVERAGE).
// - Each file runs in a Node vm with a bare `window` object, like the page; nothing is written to disk.
// - Output (stdout, UTF-8 JSON): {order:[file...], owner:{global: file}, data:{global: value}, errors:[...]}
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');
const root = process.argv[2] || process.cwd();
const html = fs.readFileSync(path.join(root, 'src', 'index.html'), 'utf8');
const order = [...html.matchAll(/<script src="([\w.-]+\.js)"/g)].map(m => m[1]);
const ctx = { window: {} }; ctx.window.window = ctx.window; vm.createContext(ctx);
const owner = {}, errors = [];
for (const f of order) {
  const p = path.join(root, f);
  if (!fs.existsSync(p)) { errors.push({ file: f, error: 'missing' }); continue; }
  const before = new Set(Object.keys(ctx.window));
  try { vm.runInContext(fs.readFileSync(p, 'utf8'), ctx, { filename: f }); }
  catch (e) { errors.push({ file: f, error: String(e && e.message || e) }); continue; }
  for (const k of Object.keys(ctx.window)) if (!before.has(k) && k !== 'window') owner[k] = f;
}
const data = {};
for (const k of Object.keys(owner)) data[k] = ctx.window[k];
// getters / functions are dropped by JSON; that is fine: they are code, not data
process.stdout.write(JSON.stringify({ order, owner, data, errors }));
