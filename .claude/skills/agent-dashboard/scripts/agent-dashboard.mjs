#!/usr/bin/env node
// Sinh trang HTML trực quan hoá hệ thống agent từ các file thật trong repo.
// Cách dùng: node agent-dashboard.mjs [--root <repo>] [--open]
// Mặc định xem repo git của thư mục hiện tại. Trang lưu trong ~/.claude/agent-dashboard/.
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { outputFile, resolveRoot } from './dashboard-paths.mjs';

const ROOT = resolveRoot();
const OUT = outputFile(ROOT);
const MAX_SCRIPTS = 12;
// Script nằm trong một skill không phải script của repo.
const REPO_SCRIPT = /(?<!skills\/[\w.-]+\/)scripts\/([\w.-]+\.(?:sh|mjs))/;
const MAX_BODY = 20000;

const rel = (p) => path.relative(ROOT, p).split(path.sep).join('/');
const exists = (p) => fs.existsSync(p);
const read = (p) => fs.readFileSync(p, 'utf8').replace(/^﻿/, '').replace(/\r\n/g, '\n');
const clip = (s) => (s.length > MAX_BODY ? `${s.slice(0, MAX_BODY)}\n\n… (đã cắt bớt)` : s);
const entries = (dir) => (exists(dir) ? fs.readdirSync(dir, { withFileTypes: true }) : []);
const dirs = (dir) => entries(dir).filter((e) => e.isDirectory() && !e.name.startsWith('.')).map((e) => e.name).sort();
const files = (dir, ext) => entries(dir).filter((e) => e.isFile() && e.name.endsWith(ext)).map((e) => e.name).sort();

function parseDoc(text) {
  const match = text.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!match) return { meta: {}, body: text };
  const meta = {};
  const lines = match[1].split('\n');
  for (let i = 0; i < lines.length; i++) {
    const kv = lines[i].match(/^([\w-]+):\s*(.*)$/);
    if (!kv) continue;
    let value = kv[2].trim();
    if (/^[>|][+-]?$/.test(value)) {
      const parts = [];
      while (i + 1 < lines.length && (/^\s+/.test(lines[i + 1]) || lines[i + 1] === '')) parts.push(lines[++i].trim());
      value = parts.join(' ').trim();
    }
    meta[kv[1]] = value.replace(/^(['"])(.*)\1$/, '$2');
  }
  return { meta, body: text.slice(match[0].length) };
}

const nodes = new Map();
const edges = new Map();
const warnings = [];

const addNode = (node) => nodes.set(node.id, { items: [], ...node });
const addEdge = (from, to, kind) => {
  if (from !== to && nodes.has(from) && nodes.has(to)) edges.set(`${from}>${to}`, { from, to, kind });
};
const warn = (where, message) => {
  if (!warnings.some((w) => w.where === where && w.message === message)) warnings.push({ where, message });
};

function addDocNode(id, type, lane, file, source, fallbackName) {
  if (!exists(file)) {
    addNode({ id, type, lane, source, title: fallbackName, desc: '', path: rel(file), body: '', missing: true });
    return null;
  }
  const text = read(file);
  const { meta, body } = parseDoc(text);
  addNode({
    id, type, lane, source,
    title: meta.name || fallbackName,
    desc: meta.description || '',
    path: rel(file),
    body: clip(body.trim()),
  });
  return { id, file, text };
}

// Điều phối
const claudeFile = path.join(ROOT, 'CLAUDE.md');
addNode({
  id: 'main', type: 'main', lane: 0, source: 'repo', title: 'Agent chính',
  desc: 'Nhận yêu cầu, điều phối subagent và skill, hỏi bạn trước khi ghi bài học.',
  path: 'CLAUDE.md', body: exists(claudeFile) ? clip(read(claudeFile).trim()) : '',
});

// Script, kiến thức, game
for (const name of [...files(path.join(ROOT, 'scripts'), '.sh'), ...files(path.join(ROOT, 'scripts'), '.mjs')]) {
  const file = path.join(ROOT, 'scripts', name);
  addNode({ id: `script:${name}`, type: 'script', lane: 4, source: 'repo', title: name, desc: 'Script tự động', path: rel(file), body: clip(read(file).trim()) });
}

const lessonDir = path.join(ROOT, 'lessons-learned');
const lessonFiles = files(lessonDir, '.md').filter((n) => n.toLowerCase() !== 'readme.md');
if (lessonFiles.length) addNode({
  id: 'lessons', type: 'knowledge', lane: 3, source: 'repo', title: 'lessons-learned',
  desc: `${lessonFiles.length} chủ đề bài học dùng chung`, path: 'lessons-learned/', body: '',
  items: lessonFiles.map((n) => ({ name: n, body: clip(read(path.join(lessonDir, n)).trim()) })),
});

const gameDir = path.join(ROOT, 'games');
const games = dirs(gameDir);
if (exists(gameDir)) addNode({
  id: 'games', type: 'knowledge', lane: 3, source: 'repo', title: 'games/',
  desc: games.length ? `${games.length} game` : 'Chưa có game', path: 'games/', body: '',
  items: games.map((n) => {
    const file = path.join(gameDir, n, 'CLAUDE.md');
    return { name: n, body: exists(file) ? clip(read(file).trim()) : 'Thiếu CLAUDE.md' };
  }),
});
for (const name of games) {
  if (!exists(path.join(gameDir, name, 'CLAUDE.md'))) warn(`games/${name}`, 'Game thiếu CLAUDE.md, agent không có hướng dẫn riêng.');
}

const domainNames = dirs(path.join(ROOT, 'domains'));
for (const name of domainNames) {
  const dir = path.join(ROOT, 'domains', name);
  const doc = ['CLAUDE.md', 'README.md'].map((f) => path.join(dir, f)).find(exists);
  addNode({ id: `domain:${name}`, type: 'knowledge', lane: 3, source: name, title: name, desc: 'Repo kiến thức chuyên môn', path: `domains/${name}/`, body: doc ? clip(read(doc).trim()) : '' });
}
// Domain đã khai báo nhưng chưa clone: gom mọi hệ quả thành một cảnh báo ở cuối.
const missingDomains = new Map();
const domainList = path.join(ROOT, 'scripts', 'domains.txt');
if (exists(domainList)) {
  for (const line of read(domainList).split('\n')) {
    const name = line.trim().split(/\s+/)[0];
    if (name && !name.startsWith('#') && !domainNames.includes(name)) {
      missingDomains.set(name, { docs: new Set(), unchecked: new Set() });
    }
  }
}

// Agent và skill
const rootDocs = [];
const domainMembers = new Map();

function scanCapabilities(base, source) {
  const members = [];
  const isRepo = source === 'repo';
  for (const name of files(path.join(base, '.claude', 'agents'), '.md')) {
    const short = name.replace(/\.md$/, '');
    const id = `agent:${source}:${short}`;
    const doc = addDocNode(id, 'agent', 1, path.join(base, '.claude', 'agents', name), source, short);
    if (doc) members.push({ key: nodes.get(id).title, id });
    if (doc && isRepo) rootDocs.push(doc);
    if (isRepo && doc && !nodes.get(id).desc) warn(rel(doc.file), 'Agent thiếu description, sẽ khó được chọn đúng lúc.');
  }
  for (const name of dirs(path.join(base, '.claude', 'skills'))) {
    const id = `skill:${source}:${name}`;
    const doc = addDocNode(id, 'skill', 2, path.join(base, '.claude', 'skills', name, 'SKILL.md'), source, name);
    members.push({ key: name, id });
    if (doc && isRepo) rootDocs.push(doc);
    if (isRepo && !doc) warn(`.claude/skills/${name}`, 'Skill thiếu SKILL.md.');
    if (isRepo && doc && !nodes.get(id).desc) warn(rel(doc.file), 'Skill thiếu description, sẽ khó được kích hoạt.');
  }
  return members;
}

const repoMembers = scanCapabilities(ROOT, 'repo');
for (const name of domainNames) domainMembers.set(name, scanCapabilities(path.join(ROOT, 'domains', name), name));
for (const member of repoMembers) addEdge('main', member.id, 'delegates');
for (const name of domainNames) {
  for (const member of domainMembers.get(name)) addEdge(`domain:${name}`, member.id, 'contains');
}

// Kiến thức nằm trong repo: rules, bộ nhớ, tài liệu, thư mục kiến thức của từng skill
const MAX_ITEM_BODY = 6000;
const knowledgeRoots = [];
const walkMd = (dir, base = dir) => entries(dir).flatMap((e) => {
  const full = path.join(dir, e.name);
  if (e.isDirectory()) return e.name.startsWith('.') || e.name === 'node_modules' ? [] : walkMd(full, base);
  return e.isFile() && e.name.endsWith('.md') ? [path.relative(base, full).split(path.sep).join('/')] : [];
}).sort();

function addKnowledgeDir(id, title, unit, dir, parent) {
  const names = walkMd(dir);
  if (!names.length) return;
  const prefix = `${rel(dir)}/`;
  addNode({
    id, type: 'knowledge', lane: 3, source: 'repo', title, desc: `${names.length} ${unit}`, path: prefix, body: '',
    items: names.map((n) => {
      const text = read(path.join(dir, n)).trim();
      return { name: n, body: text.length > MAX_ITEM_BODY ? `${text.slice(0, MAX_ITEM_BODY)}\n\n… (đã cắt bớt)` : text };
    }),
  });
  knowledgeRoots.push({ id, prefix: prefix.toLowerCase() });
  addEdge(parent, id, 'reads');
}

addKnowledgeDir('kb:rules', 'Luật (rules)', 'file luật', path.join(ROOT, '.claude', 'rules'), 'main');
addKnowledgeDir('kb:memory', 'Bộ nhớ Claude', 'ghi nhớ', path.join(ROOT, '.claude', 'memory_store'), 'main');
for (const name of dirs(ROOT).filter((n) => n.toLowerCase() === 'docs')) {
  addKnowledgeDir('kb:docs', `Tài liệu (${name})`, 'tài liệu', path.join(ROOT, name), 'main');
}
for (const name of dirs(path.join(ROOT, '.claude', 'skills'))) {
  for (const sub of ['knowledge', 'references']) {
    addKnowledgeDir(`kb:skill:${name}:${sub}`, `${name} · ${sub}`, 'file', path.join(ROOT, '.claude', 'skills', name, sub), `skill:repo:${name}`);
  }
}

// Hook
const settingsFile = path.join(ROOT, '.claude', 'settings.json');
if (exists(settingsFile)) {
  let hooks = {};
  try {
    hooks = JSON.parse(read(settingsFile)).hooks || {};
  } catch {
    warn('.claude/settings.json', 'Không đọc được file settings.');
  }
  for (const [event, groups] of Object.entries(hooks)) {
    groups.forEach((group, g) => (group.hooks || []).forEach((hook, h) => {
      const script = hook.command?.match(REPO_SCRIPT)?.[1];
      const shown = hook.command?.match(/([\w.-]+\.(?:sh|mjs|js|py))(?=["'\s]|$)/)?.[1];
      const id = `hook:${event}:${g}:${h}`;
      addNode({ id, type: 'hook', lane: 0, source: 'repo', title: event, desc: shown || hook.command || hook.type, path: '.claude/settings.json', body: hook.command || '' });
      addEdge(id, 'main', 'prepares');
      if (script) {
        addEdge(id, `script:${script}`, 'runs');
        if (!nodes.has(`script:${script}`)) warn('.claude/settings.json', `Hook gọi script không tồn tại: scripts/${script}`);
      }
    }));
  }
}

// Quan hệ đọc từ nội dung file
const codeRefs = (text) => [...text.matchAll(/`([^`\n]+)`/g)].map((m) => m[1].trim());

function linkDoc(id, text, where) {
  const tokens = codeRefs(text);
  const linkedDomains = new Set();
  for (const token of tokens) {
    if (token.startsWith('lessons-learned') || lessonFiles.includes(token)) addEdge(id, 'lessons', 'reads');
    if (/(^|\s)games\//.test(token)) addEdge(id, 'games', 'works-in');
    const lowered = token.toLowerCase();
    for (const kb of knowledgeRoots) if (lowered.startsWith(kb.prefix)) addEdge(id, kb.id, 'reads');
    for (const m of token.matchAll(new RegExp(REPO_SCRIPT.source, 'g'))) {
      if (nodes.has(`script:${m[1]}`)) addEdge(id, `script:${m[1]}`, 'runs');
      else warn(where, `Nhắc tới script không tồn tại: scripts/${m[1]}`);
    }
    const domain = token.match(/^domains\/([\w.-]+)/)?.[1];
    if (domain) {
      if (nodes.has(`domain:${domain}`)) {
        addEdge(id, `domain:${domain}`, 'reads');
        linkedDomains.add(domain);
      } else if (missingDomains.has(domain)) {
        missingDomains.get(domain).docs.add(where);
      } else warn(where, `Nhắc tới domain không tồn tại: ${domain}`);
    }
    const local = repoMembers.find((m) => m.key === token);
    if (local) addEdge(id, local.id, 'uses');
  }
  for (const domain of linkedDomains) {
    for (const member of domainMembers.get(domain)) {
      if (tokens.includes(member.key)) addEdge(id, member.id, 'uses');
    }
  }
}

function checkPaths(doc) {
  const where = rel(doc.file);
  const refs = [...new Set(codeRefs(doc.text))];
  // File đã khai báo dạng games/<tên-game>/x có thể được nhắc lại ngắn là x, tính từ thư mục game.
  const gameRelative = new Set(refs.map((t) => t.match(/^games\/<[^>]+>\/(.+)$/)?.[1]).filter(Boolean));
  const candidates = refs.filter((t) => (
    !/[\s<>*{}$:]/.test(t) && !t.startsWith('/') && !t.startsWith('~') && (t.includes('/') || t.endsWith('.md'))
    // Tên thư mục đơn như build/ thường là thư mục đầu ra trong game, không phải tham chiếu tới repo.
    && !/^[^/]+\/$/.test(t)
    && !gameRelative.has(t)
  ));
  const bases = new Set([ROOT, lessonDir, path.dirname(doc.file), ...domainNames.map((n) => path.join(ROOT, 'domains', n))]);
  const resolveWith = (token) => [...bases].map((b) => path.join(b, token)).find(exists);
  const pending = [];
  for (const token of candidates) {
    const hit = resolveWith(token);
    if (!hit) { pending.push(token); continue; }
    // Đường dẫn rút gọn như knowledge/INDEX.md được tính từ thư mục của đường dẫn đầy đủ trước đó.
    for (let dir = path.dirname(hit); dir.startsWith(ROOT) && dir !== ROOT; dir = path.dirname(dir)) bases.add(dir);
  }
  // File phụ thuộc domain chưa clone có thể dùng đường dẫn rút gọn, nên chưa kết luận là hỏng.
  const blockedBy = [...new Set(refs.map((t) => t.match(/^domains\/([\w.-]+)/)?.[1]))].filter((d) => missingDomains.has(d));
  for (const token of pending) {
    if (resolveWith(token)) continue;
    if (blockedBy.length) blockedBy.forEach((d) => missingDomains.get(d).unchecked.add(token));
    else warn(where, `Đường dẫn không tồn tại: ${token}`);
  }
}

linkDoc('main', exists(claudeFile) ? read(claudeFile) : '', 'CLAUDE.md');
if (exists(claudeFile)) checkPaths({ file: claudeFile, text: read(claudeFile) });
for (const doc of rootDocs) {
  linkDoc(doc.id, doc.text, rel(doc.file));
  checkPaths(doc);
}

for (const [name, { docs, unchecked }] of missingDomains) {
  const impact = docs.size ? ` Ảnh hưởng: ${[...docs].join(', ')}.` : '';
  const pendingCheck = unchecked.size ? ` ${unchecked.size} đường dẫn chưa kiểm tra được.` : '';
  warn('scripts/domains.txt', `Domain "${name}" chưa được clone, có thể do thiếu quyền truy cập.${impact}${pendingCheck}`);
}

const scriptNodes = [...nodes.values()].filter((n) => n.type === 'script');
if (scriptNodes.length > MAX_SCRIPTS) {
  // Repo nhiều script chỉ hiện những script agent, skill hoặc hook thật sự dùng.
  const linked = new Set([...edges.values()].flatMap((e) => [e.from, e.to]));
  for (const node of scriptNodes) if (!linked.has(node.id)) nodes.delete(node.id);
}

const data = {
  repo: path.basename(ROOT),
  generatedAt: new Date().toLocaleString('vi-VN'),
  nodes: [...nodes.values()],
  edges: [...edges.values()],
  warnings,
};

const TEMPLATE = String.raw`<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Hệ thống agent</title>
<style>
:root{color-scheme:dark;--bg:#1c1c1a;--card:#282825;--text:#ecebe4;--muted:#a3a198;--line:#3d3d38;--edge:#68665e;--accent:#afa9ec;--agent:#312b70;--agent-t:#dedcfb;--skill:#0c3560;--skill-t:#cfe4f8;--know:#0a4236;--know-t:#c9f0e2;--tool:#393935;--tool-t:#dedcd2;--warn:#4a3005;--warn-t:#fae2b8}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.5 system-ui,"Segoe UI",sans-serif}
header{padding:20px 24px 8px}h1{font-size:22px;font-weight:600;margin:0}.sub{color:var(--muted);font-size:13px}
.stats{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.stat{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px 12px}.stat b{font-size:17px;margin-right:5px}
.tools{display:flex;flex-wrap:wrap;gap:12px;align-items:center;padding:10px 24px}input[type=search]{font:inherit;color:inherit;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:7px 11px;width:260px;max-width:100%}label{display:flex;gap:6px;align-items:center;cursor:pointer}
#warnings{margin:2px 24px 10px;background:var(--warn);color:var(--warn-t);border-radius:8px;padding:9px 13px}#warnings summary{cursor:pointer;font-weight:600}#warnings ul{margin:7px 0 2px;padding-left:18px}#warnings code{font-size:12px}
.layout{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:16px;padding:6px 24px 24px;align-items:start}
#board{position:relative;display:grid;grid-template-columns:repeat(var(--cols,5),minmax(112px,1fr));gap:30px;min-width:0}#wires{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible}
#wires path{fill:none;stroke:var(--edge);stroke-width:1;opacity:.55}#wires path.on{stroke:var(--accent);stroke-width:2;opacity:1}#wires path.off{opacity:.07}
.lane{position:relative;display:flex;flex-direction:column;gap:8px;min-width:0}.lane h2{font-size:13px;font-weight:600;color:var(--muted);margin:0 0 2px}.group{font-size:12px;color:var(--muted);margin-top:8px}
.card{display:block;width:100%;text-align:left;font:inherit;border:1px solid transparent;border-radius:8px;padding:7px 10px;cursor:pointer;background:var(--tool);color:var(--tool-t);transition:opacity .12s}.card strong{display:block;font-size:13px;font-weight:600;overflow-wrap:anywhere}.card span{display:block;font-size:12px;opacity:.8;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.card.agent,.card.main{background:var(--agent);color:var(--agent-t)}.card.skill{background:var(--skill);color:var(--skill-t)}.card.knowledge{background:var(--know);color:var(--know-t)}.card.sel{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}.card.dim{opacity:.25}.card:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
#panel{position:sticky;top:12px;max-height:calc(100vh - 24px);overflow:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}#panel h2{font-size:18px;margin:0;overflow-wrap:anywhere}#panel h3{font-size:13px;margin:15px 0 5px;color:var(--muted)}#panel p{margin:6px 0}.path{font:12px ui-monospace,Consolas,monospace;color:var(--muted);overflow-wrap:anywhere}
.chips{display:flex;flex-wrap:wrap;gap:5px}.chip{font:inherit;font-size:12px;color:inherit;background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:2px 7px;cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.55 ui-monospace,Consolas,monospace;background:var(--bg);border-radius:8px;padding:10px;margin:0}details{margin:4px 0}details>summary{cursor:pointer}
@media(max-width:1320px){.layout{grid-template-columns:1fr}#panel{position:static;max-height:none}}
@media(max-width:720px){#board{grid-template-columns:1fr;gap:18px}#wires{display:none}header,.tools{padding-left:14px;padding-right:14px}.layout{padding-left:14px;padding-right:14px}#warnings{margin-left:14px;margin-right:14px}}
</style></head><body>
<header><h1>Hệ thống agent</h1><div class="sub" id="generated"></div><div class="stats" id="stats"></div></header>
<details id="warnings" hidden><summary></summary><ul></ul></details>
<div class="tools"><input id="search" type="search" placeholder="Tìm agent, skill, file…" aria-label="Tìm trong hệ thống"><label><input id="all" type="checkbox"> Hiện mọi skill chuyên môn</label></div>
<div class="layout"><main id="board"><svg id="wires" aria-hidden="true"></svg></main><aside id="panel" aria-live="polite"></aside></div>
<script id="data" type="application/json">__DATA__</script>
<script>
var D=JSON.parse(document.getElementById('data').textContent),byId={},cards={},sel='main',hover=null,showAll=false,query='';
var LANES=['Điều phối','Agent','Skill','Kiến thức','Công cụ'],TYPES={main:'Agent chính',agent:'Agent',skill:'Skill',knowledge:'Kiến thức',script:'Script',hook:'Hook'};
var KINDS={delegates:'giao việc',reads:'đọc',uses:'dùng',runs:'chạy','works-in':'làm việc trong',contains:'chứa',prepares:'chuẩn bị'};
D.nodes.forEach(function(n){byId[n.id]=n});
var board=document.getElementById('board'),wires=document.getElementById('wires'),panel=document.getElementById('panel');
function el(tag,cls,text){var e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e}
function near(id){var s={};s[id]=1;D.edges.forEach(function(e){if(e.from===id)s[e.to]=1;if(e.to===id)s[e.from]=1});return s}
function directlyUsed(n){return D.edges.some(function(e){return e.to===n.id&&e.kind!=='contains'})}
function visible(n){return n.type!=='skill'&&n.type!=='agent'||n.source==='repo'||showAll||n.id===sel||directlyUsed(n)||(query&&matches(n))}
function matches(n){return (n.title+' '+n.desc+' '+n.path).toLowerCase().indexOf(query)>=0}
function stat(v,l){var s=el('div','stat');s.appendChild(el('b',null,v));s.appendChild(document.createTextNode(l));return s}
function count(t,repo){return D.nodes.filter(function(n){return n.type===t&&(!repo||n.source==='repo')}).length}
document.title='Hệ thống agent · '+D.repo;document.querySelector('h1').textContent=document.title;document.getElementById('generated').textContent='Sinh lúc '+D.generatedAt+'. Chạy lại script để cập nhật.';
var st=document.getElementById('stats');[[count('agent'),'agent'],[count('skill'),'skill'],[D.nodes.filter(function(n){return n.id.indexOf('domain:')===0}).length||null,'domain'],[byId.lessons?byId.lessons.items.length:null,'bài học'],[byId.games?byId.games.items.length:null,'game'],[D.warnings.length,'cảnh báo']].forEach(function(x){if(x[0]!=null)st.appendChild(stat(x[0],x[1]))});
if(D.warnings.length){var w=document.getElementById('warnings');w.hidden=false;w.open=true;w.querySelector('summary').textContent=D.warnings.length+' vấn đề cần xem';D.warnings.forEach(function(x){var li=el('li');li.appendChild(el('code',null,x.where));li.appendChild(document.createTextNode(': '+x.message));w.querySelector('ul').appendChild(li)})}
function build(){
  board.querySelectorAll('.lane').forEach(function(l){l.remove()});cards={};
  var cols=0;LANES.forEach(function(name,i){
    if(!D.nodes.some(function(n){return n.lane===i}))return;cols++;
    var lane=el('section','lane');lane.appendChild(el('h2',null,name));var last=null;
    D.nodes.filter(function(n){return n.lane===i&&visible(n)}).sort(function(a,b){return (a.source==='repo'?0:1)-(b.source==='repo'?0:1)||(a.type==='main'?-1:0)||0}).forEach(function(n){
      var g=i===4?(n.type==='script'?'Script':'Tool của Claude'):(i===1||i===2)?(n.source==='repo'?'Repo này':n.source):null;if(g&&g!==last){lane.appendChild(el('div','group',g));last=g}
      var c=el('button','card '+n.type);c.type='button';c.appendChild(el('strong',null,n.title));c.appendChild(el('span',null,n.desc||n.path));c.title=n.desc||n.path;
      c.onclick=function(){select(n.id)};c.onmouseenter=function(){hover=n.id;paint()};c.onmouseleave=function(){hover=null;paint()};c.onfocus=function(){hover=n.id;paint()};c.onblur=function(){hover=null;paint()};
      cards[n.id]=c;lane.appendChild(c)});
    var hidden=D.nodes.filter(function(n){return n.lane===i&&!visible(n)}).length;if(hidden)lane.appendChild(el('div','group','+'+hidden+' mục đang ẩn'));
    board.appendChild(lane)});
  board.style.setProperty('--cols',cols);
  draw();paint();
}
function box(c,b){var r=c.getBoundingClientRect();return{l:r.left-b.left,r:r.right-b.left,y:r.top-b.top+r.height/2}}
function draw(){
  while(wires.firstChild)wires.removeChild(wires.firstChild);var b=board.getBoundingClientRect();
  D.edges.forEach(function(e){var f=cards[e.from],t=cards[e.to];if(!f||!t)return;var A=box(f,b),B=box(t,b),d;
    if(Math.abs(A.l-B.l)<4){var o=16+Math.min(26,Math.abs(A.y-B.y)/5);d='M'+A.r+' '+A.y+'C'+(A.r+o)+' '+A.y+' '+(B.r+o)+' '+B.y+' '+B.r+' '+B.y}
    else if(A.l<B.l){var m=(A.r+B.l)/2;d='M'+A.r+' '+A.y+'C'+m+' '+A.y+' '+m+' '+B.y+' '+B.l+' '+B.y}
    else{var m2=(A.l+B.r)/2;d='M'+A.l+' '+A.y+'C'+m2+' '+A.y+' '+m2+' '+B.y+' '+B.r+' '+B.y}
    var p=document.createElementNS('http://www.w3.org/2000/svg','path');p.setAttribute('d',d);p.dataset.from=e.from;p.dataset.to=e.to;wires.appendChild(p)});
  paint();
}
function paint(){
  var f=hover||sel,s=near(f);
  Object.keys(cards).forEach(function(id){var n=byId[id],hit=query?matches(n):!!s[id];cards[id].classList.toggle('dim',!hit);cards[id].classList.toggle('sel',id===sel)});
  wires.querySelectorAll('path').forEach(function(p){var on=p.dataset.from===f||p.dataset.to===f;p.setAttribute('class',on?'on':'off')});
}
function chips(title,list){if(!list.length)return;panel.appendChild(el('h3',null,title));var w=el('div','chips');list.forEach(function(x){var b=el('button','chip',x.label);b.type='button';b.onclick=function(){select(x.id)};w.appendChild(b)});panel.appendChild(w)}
function select(id){var rebuild=!cards[id];sel=id;if(rebuild)build();else paint();detail(byId[id])}
function detail(n){
  panel.textContent='';panel.scrollTop=0;panel.appendChild(el('div','sub',TYPES[n.type]+(n.source!=='repo'?' · '+n.source:'')));panel.appendChild(el('h2',null,n.title));if(n.desc)panel.appendChild(el('p',null,n.desc));panel.appendChild(el('div','path',n.path));
  chips('Đi tới',D.edges.filter(function(e){return e.from===n.id}).map(function(e){return{id:e.to,label:(KINDS[e.kind]||e.kind)+': '+byId[e.to].title}}));
  chips('Được gọi từ',D.edges.filter(function(e){return e.to===n.id}).map(function(e){return{id:e.from,label:byId[e.from].title+' ('+(KINDS[e.kind]||e.kind)+')'}}));
  if(n.items.length){panel.appendChild(el('h3',null,'Nội dung'));n.items.forEach(function(it){var d=el('details');d.appendChild(el('summary',null,it.name));d.appendChild(el('pre',null,it.body));panel.appendChild(d)})}
  if(n.body){panel.appendChild(el('h3',null,n.type==='agent'||n.type==='skill'?'Prompt':'Chi tiết'));panel.appendChild(el('pre',null,n.body))}
}
document.getElementById('search').oninput=function(){query=this.value.trim().toLowerCase();build()};
document.getElementById('all').onchange=function(){showAll=this.checked;build()};
new ResizeObserver(draw).observe(board);if(document.fonts&&document.fonts.ready)document.fonts.ready.then(draw);
build();detail(byId[sel]);
</script></body></html>
`;

const json = JSON.stringify(data).replace(/</g, '\\u003c');
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, TEMPLATE.replace('__DATA__', () => json));

const count = (type) => data.nodes.filter((n) => n.type === type).length;
console.log(`Đã tạo ${OUT}: ${count('agent')} agent, ${count('skill')} skill, ${data.edges.length} liên kết, ${warnings.length} cảnh báo.`);
for (const w of warnings) console.log(`  ! ${w.where}: ${w.message}`);

if (process.argv.includes('--open')) {
  const [cmd, args] = process.platform === 'win32' ? ['cmd', ['/c', 'start', '', OUT]]
    : process.platform === 'darwin' ? ['open', [OUT]] : ['xdg-open', [OUT]];
  spawn(cmd, args, { detached: true, stdio: 'ignore' }).unref();
}
