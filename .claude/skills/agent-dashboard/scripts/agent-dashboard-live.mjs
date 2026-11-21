#!/usr/bin/env node
// Dashboard trực tiếp: theo dõi log phiên Claude Code và cho thấy các luồng đang tương tác.
// Cách dùng: node agent-dashboard-live.mjs [--root <repo>] [--detach] [--open]
// Chỉ nghe trên 127.0.0.1, chỉ gửi metadata (tên agent, tool, file), không gửi nội dung hội thoại.
import { execFile, spawn } from 'node:child_process';
import fs from 'node:fs';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { outputFile, resolveRoot } from './dashboard-paths.mjs';

const SCRIPT = fileURLToPath(import.meta.url);
const ROOT = resolveRoot();
const GENERATOR = path.join(path.dirname(SCRIPT), 'agent-dashboard.mjs');
const HTML = outputFile(ROOT);
const PROJECTS = path.join(os.homedir(), '.claude', 'projects');
const HOST = '127.0.0.1';
const PORT_FIRST = 8790;
const PORT_LAST = 8799;
const APP = 'agent-dashboard-live';
const POLL_MS = 600;
const IDLE_EXIT_MS = 30 * 60 * 1000;
const RING_SIZE = 400;
const TAIL_BYTES = 1.5 * 1024 * 1024;
const MAX_READ = 8 * 1024 * 1024;
const RECENT_MS = 12 * 60 * 60 * 1000;
const RUNNING_MS = 5 * 60 * 1000;

const files = new Map();
const titles = new Map();
const delegations = new Map();
const openTools = new Set();
const clients = new Set();
const ring = [];
let seq = 0;
let booting = true;
let idleSince = Date.now();

const short = (s, n = 70) => {
  const text = String(s ?? '').replace(/\s+/g, ' ').trim();
  return text.length > n ? `${text.slice(0, n - 1)}…` : text;
};

function projectDirs() {
  const prefix = ROOT.replace(/[^a-zA-Z0-9]/g, '-');
  if (!fs.existsSync(PROJECTS)) return [];
  return fs.readdirSync(PROJECTS, { withFileTypes: true })
    .filter((e) => e.isDirectory() && (e.name === prefix || e.name.startsWith(`${prefix}-`)))
    .map((e) => path.join(PROJECTS, e.name));
}

function emit(event, hist) {
  const out = { seq: ++seq, title: titles.get(event.session) || '', ...event };
  ring.push(out);
  if (ring.length > RING_SIZE) ring.shift();
  if (hist) return;
  const frame = `event: ev\ndata: ${JSON.stringify(out)}\n\n`;
  for (const res of clients) res.write(frame);
}

// Thống kê trong ngày theo giờ máy. Mỗi lượt chỉ đếm một lần, kể cả khi phiên resume chép lại log cũ.
const localDay = (date) => {
  const pad = (n) => String(n).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
};
const freshDay = (day) => ({
  day, prompts: 0, sessions: new Set(), agents: {}, skills: {}, tools: {}, scripts: {}, files: {}, seen: new Set(), discovered: new Set(),
});
const bump = (map, key) => { map[key] = (map[key] || 0) + 1; };
const fileCalls = new Map();
let today = freshDay(localDay(new Date()));
let todayDirty = false;

function rollDay() {
  const now = localDay(new Date());
  if (today.day !== now) {
    today = freshDay(now);
    todayDirty = true;
  }
  return now;
}

function countOnce(ts, key) {
  const date = new Date(ts);
  if (Number.isNaN(date.getTime())) return null;
  const now = rollDay();
  if (localDay(date) !== now || today.seen.has(key)) return null;
  today.seen.add(key);
  todayDirty = true;
  return today;
}

function statsView() {
  rollDay();
  const { seen, sessions, discovered, files: logged, ...rest } = today;
  const merged = Object.fromEntries(Object.entries(logged).map(([ref, f]) => [ref, { ...f }]));
  for (const ref of discovered) {
    merged[ref] ??= { read: 0, created: 0, updated: 0 };
    merged[ref].created = Math.max(merged[ref].created, 1);
  }
  return { ...rest, files: merged, sessions: sessions.size };
}

const runGit = (repo, args) => new Promise((resolve) => {
  execFile('git', ['-c', 'core.quotePath=false', '-C', repo, ...args], { windowsHide: true, maxBuffer: 16 * 1024 * 1024 },
    (error, out) => resolve(error ? '' : out));
});

// File kiến thức mới dù do Claude, người dùng hay app khác tạo: commit thêm hôm nay, hoặc chưa commit và sinh ra hôm nay.
// Không dựa riêng vào ngày tạo file, vì repo vừa clone có mọi file mang ngày hôm nay.
let scanningKnowledge = false;
async function scanNewKnowledge() {
  if (scanningKnowledge) return;
  scanningKnowledge = true;
  try {
    const day = rollDay();
    const start = new Date();
    start.setHours(0, 0, 0, 0);
    const found = new Set();
    const addIfBornToday = (file) => {
      const stat = fs.statSync(file, { throwIfNoEntry: false });
      const ref = stat?.isFile() ? knowledgeRef(file) : '';
      // File được chép hoặc đồng bộ có ngày tạo mới nhưng giữ ngày sửa cũ, nên phải xét cả hai.
      if (ref && Math.min(stat.birthtimeMs, stat.mtimeMs) >= start.getTime()) found.add(ref);
    };
    const children = (name) => {
      const dir = path.join(ROOT, name);
      return fs.existsSync(dir) ? fs.readdirSync(dir).map((n) => path.join(dir, n)) : [];
    };
    for (const repo of [ROOT, ...children('domains'), ...children('games')]) {
      if (!fs.existsSync(path.join(repo, '.git'))) continue;
      const added = await runGit(repo, ['log', `--since=${start.toISOString()}`, '--diff-filter=A', '--name-only', '--format=']);
      for (const name of added.split('\n').filter(Boolean)) {
        const file = path.join(repo, name);
        const ref = fs.existsSync(file) ? knowledgeRef(file) : '';
        if (ref) found.add(ref);
      }
      const untracked = await runGit(repo, ['ls-files', '--others', '--exclude-standard']);
      for (const name of untracked.split('\n').filter(Boolean)) addIfBornToday(path.join(repo, name));
    }
    for (const dir of projectDirs()) {
      const memory = path.join(dir, 'memory');
      if (fs.existsSync(memory)) for (const name of fs.readdirSync(memory)) addIfBornToday(path.join(memory, name));
    }
    if (today.day === day && [...found].sort().join('\n') !== [...today.discovered].sort().join('\n')) {
      today.discovered = found;
      todayDirty = true;
    }
  } catch (error) {
    console.error(error.message);
  } finally {
    scanningKnowledge = false;
  }
}

function knownSkill(name) {
  const bases = [ROOT, os.homedir()];
  const domains = path.join(ROOT, 'domains');
  if (fs.existsSync(domains)) for (const d of fs.readdirSync(domains)) bases.push(path.join(domains, d));
  return bases.some((base) => fs.existsSync(path.join(base, '.claude', 'skills', name, 'SKILL.md')));
}

// Đường dẫn của một file kiến thức, rỗng nếu file đó là code hoặc cấu hình.
function knowledgeRef(file) {
  if (typeof file !== 'string' || !path.isAbsolute(file) || !file.toLowerCase().endsWith('.md')) return '';
  const inProjects = path.relative(PROJECTS, file).split(path.sep);
  if (inProjects.length === 3 && inProjects[1] === 'memory') {
    const mine = projectDirs().some((dir) => path.basename(dir) === inProjects[0]);
    return mine && inProjects[2] !== 'MEMORY.md' ? `claude-memory/${inProjects[2]}` : '';
  }
  const rel = path.relative(ROOT, file);
  if (!rel || rel.startsWith('..') || path.isAbsolute(rel)) return '';
  const ref = rel.split(path.sep).join('/');
  if (/^domains\/[^/]+\/\.claude\/(agents\/|skills\/[^/]+\/SKILL\.md$)/i.test(ref)) return '';
  const isKnowledge = /^(lessons-learned|docs)\//i.test(ref)
    || /^\.claude\/(rules|memory_store)\//i.test(ref)
    || /^\.claude\/skills\/[^/]+\/(knowledge|references)\//i.test(ref)
    || /^domains\/[^/]+\//i.test(ref)
    || /^games\/[^/]+\/CLAUDE\.md$/i.test(ref);
  return isKnowledge ? ref : '';
}

function toolFamily(name) {
  const m = name.match(/^mcp__(.+?)__(.+)$/);
  if (!m) return { family: name, action: '' };
  const server = /^[0-9a-f-]{36}$/.test(m[1]) ? 'Connector' : m[1].replace(/^Claude_/, '');
  return { family: server, action: m[2] };
}

function repoRef(input) {
  const candidate = input?.file_path || input?.path || input?.notebook_path;
  if (typeof candidate === 'string' && path.isAbsolute(candidate)) {
    const rel = path.relative(ROOT, candidate);
    if (rel && !rel.startsWith('..') && !path.isAbsolute(rel)) return rel.split(path.sep).join('/');
  }
  const command = typeof input?.command === 'string' ? input.command : '';
  return command.match(/(?:^|[\s"'/])((?:scripts|games|domains|lessons-learned)\/[^\s"';|&]+)/)?.[1] || '';
}

function toolLabel(input, action) {
  if (input?.file_path) return path.basename(String(input.file_path));
  if (input?.description) return short(input.description);
  return action;
}

function handleAssistant(row, st, base, hist) {
  const content = row.message?.content;
  if (!Array.isArray(content)) return;
  for (const block of content) {
    if (block.type !== 'tool_use') continue;
    const { name, id, input } = block;
    if (name === 'Agent' || name === 'Task') {
      const target = input?.subagent_type || 'general-purpose';
      delegations.set(id, { agent: st.agent, agentType: st.agentType });
      const day = countOnce(row.timestamp, `call:${id}`);
      if (day) bump(day.agents, target);
      emit({ ...base, kind: 'delegate', id, name: target, label: short(input?.description) }, hist);
    } else if (name === 'Skill') {
      const day = countOnce(row.timestamp, `call:${id}`);
      if (day && input?.skill) bump(day.skills, String(input.skill));
      emit({ ...base, kind: 'skill', id, name: String(input?.skill || '') }, hist);
    } else if (!name.startsWith('mcp__ccd_') && name !== 'ToolSearch') {
      const { family, action } = toolFamily(name);
      const day = countOnce(row.timestamp, `call:${id}`);
      if (day) {
        bump(day.tools, family);
        const script = /^(Bash|PowerShell)$/.test(name) && String(input?.command || '')
          .match(/(?<!skills\/[\w.-]+\/)scripts\/([\w.-]+\.(?:sh|mjs))/)?.[1];
        if (script) bump(day.scripts, script);
      }
      const knowledge = /^(Read|Write|Edit|MultiEdit)$/.test(name) ? knowledgeRef(input?.file_path) : '';
      if (knowledge) fileCalls.set(id, { ref: knowledge, write: name !== 'Read' });
      openTools.add(id);
      emit({ ...base, kind: 'tool', id, name: family, label: toolLabel(input, action), ref: repoRef(input) }, hist);
    }
  }
  if (!st.isSub && row.message?.stop_reason === 'end_turn') emit({ ...base, kind: 'reply' }, hist);
}

function handleUser(row, st, base, hist) {
  if (row.isMeta) return;
  const content = row.message?.content;
  if (Array.isArray(content)) {
    for (const block of content) {
      const call = block.type === 'tool_result' ? fileCalls.get(block.tool_use_id) : null;
      if (call) {
        fileCalls.delete(block.tool_use_id);
        const day = block.is_error ? null : countOnce(row.timestamp, `done:${block.tool_use_id}`);
        if (day) {
          day.files[call.ref] ??= { read: 0, created: 0, updated: 0 };
          const key = !call.write ? 'read' : row.toolUseResult?.type === 'create' ? 'created' : 'updated';
          day.files[call.ref][key]++;
        }
      }
      if (block.type === 'tool_result' && openTools.delete(block.tool_use_id)) {
        emit({ ...base, kind: 'tool-done', id: block.tool_use_id, ok: !block.is_error }, hist);
      }
    }
  }
  if (st.isSub || row.toolUseResult) return;
  const text = typeof content === 'string' ? content
    : Array.isArray(content) ? content.filter((b) => b.type === 'text').map((b) => b.text).join('\n') : '';
  const trimmed = text.trim();
  if (!trimmed) return;
  const command = trimmed.match(/<command-name>\/?([^<]+)<\/command-name>/)?.[1]?.trim();
  if (command || !trimmed.startsWith('<')) {
    const day = countOnce(row.timestamp, `prompt:${row.uuid}`);
    if (day) {
      day.prompts++;
      if (command && knownSkill(command)) bump(day.skills, command);
    }
  }
  if (command) {
    emit({ ...base, kind: 'prompt', label: `/${command}` }, hist);
    emit({ ...base, kind: 'skill', id: row.uuid, name: command, cmd: true }, hist);
  } else if (!trimmed.startsWith('<')) {
    emit({ ...base, kind: 'prompt', label: 'Bạn gửi yêu cầu' }, hist);
  }
}

function parseLine(line, st, hist) {
  if (st.inRoot && line.includes('"hookEvent":"SessionStart"')) {
    try {
      const hook = JSON.parse(line);
      if (hook.type === 'attachment' && hook.attachment?.hookEvent === 'SessionStart') {
        const day = countOnce(hook.timestamp, `session:${st.session}`);
        if (day) day.sessions.add(st.session);
      }
    } catch { /* Dòng log chưa ghi xong. */ }
    return;
  }
  if (!/"type":"(assistant|user|custom-title)"/.test(line)) return;
  let row;
  try { row = JSON.parse(line); } catch { return; }
  if (row.type === 'custom-title') {
    if (row.customTitle) titles.set(st.session, short(row.customTitle, 60));
    return;
  }
  const parent = st.toolUseId ? delegations.get(st.toolUseId) : null;
  const base = {
    ts: row.timestamp, session: st.session, agent: st.agent, agentType: st.agentType,
    parent: parent?.agent || 'main', parentType: parent?.agentType || '',
  };
  if (row.type === 'assistant') handleAssistant(row, st, base, hist);
  else handleUser(row, st, base, hist);
}

function readMeta(file, st, stat, hist) {
  const metaFile = file.replace(/\.jsonl$/, '.meta.json');
  let metaStat;
  try { metaStat = fs.statSync(metaFile); } catch { return; }
  if (metaStat.mtimeMs === st.metaTime) return;
  st.metaTime = metaStat.mtimeMs;
  let meta;
  try { meta = JSON.parse(fs.readFileSync(metaFile, 'utf8')); } catch { st.metaTime = 0; return; }
  st.agentType = meta.agentType || st.agentType;
  st.toolUseId = meta.toolUseId || st.toolUseId;
  st.description = short(meta.description);
  if (meta.finished && !st.finished) {
    st.finished = true;
    const parent = delegations.get(st.toolUseId);
    emit({
      ts: new Date(Math.max(metaStat.mtimeMs, stat.mtimeMs)).toISOString(), session: st.session,
      agent: st.agent, agentType: st.agentType, parent: parent?.agent || 'main', parentType: parent?.agentType || '',
      kind: 'agent-done', id: st.toolUseId, label: st.description,
    }, hist);
  }
}

function readNew(file, st, size, hist) {
  const length = Math.min(size - st.offset, MAX_READ);
  const buffer = Buffer.alloc(length);
  const fd = fs.openSync(file, 'r');
  let got = 0;
  try { got = fs.readSync(fd, buffer, 0, length, st.offset); } finally { fs.closeSync(fd); }
  const end = buffer.subarray(0, got).lastIndexOf(0x0a);
  if (end < 0) {
    if (length === MAX_READ) st.offset += got;
    return;
  }
  st.offset += end + 1;
  const lines = buffer.subarray(0, end).toString('utf8').split('\n');
  if (st.dropFirst) { lines.shift(); st.dropFirst = false; }
  for (const line of lines) parseLine(line, st, hist);
}

function track(file, ctx) {
  let stat;
  try { stat = fs.statSync(file); } catch { return; }
  let st = files.get(file);
  if (!st) {
    // File có hoạt động hôm nay phải đọc từ đầu để số liệu trong ngày đủ.
    const touchedToday = localDay(stat.mtime) === localDay(new Date());
    const old = booting && !touchedToday && Date.now() - stat.mtimeMs > RECENT_MS;
    const offset = old ? stat.size : booting && !touchedToday ? Math.max(0, stat.size - TAIL_BYTES) : 0;
    st = { ...ctx, offset, dropFirst: !old && offset > 0, mtime: 0, metaTime: 0, finished: false };
    files.set(file, st);
  }
  if (stat.size < st.offset) st.offset = 0;
  st.mtime = stat.mtimeMs;
  // Agent gốc phải được đọc trước để biết quan hệ giao việc của subagent.
  if (st.isSub) readMeta(file, st, stat, booting);
  while (stat.size > st.offset) {
    const before = st.offset;
    readNew(file, st, stat.size, booting);
    if (st.offset === before) break;
  }
  if (st.isSub) readMeta(file, st, stat, booting);
}

function scan() {
  const subs = [];
  for (const dir of projectDirs()) {
    let items;
    try { items = fs.readdirSync(dir, { withFileTypes: true }); } catch { continue; }
    for (const item of items) {
      if (item.isFile() && item.name.endsWith('.jsonl')) {
        track(path.join(dir, item.name), {
          session: item.name.slice(0, -6), agent: 'main', agentType: '', isSub: false,
          inRoot: path.basename(dir) === ROOT.replace(/[^a-zA-Z0-9]/g, '-'),
        });
      } else if (item.isDirectory()) {
        const subDir = path.join(dir, item.name, 'subagents');
        if (!fs.existsSync(subDir)) continue;
        for (const name of fs.readdirSync(subDir)) {
          if (!name.endsWith('.jsonl')) continue;
          subs.push([path.join(subDir, name), { session: item.name, agent: name.slice(0, -6), agentType: 'agent', isSub: true }]);
        }
      }
    }
  }
  for (const [file, ctx] of subs) track(file, ctx);
  booting = false;
}

function runningAgents() {
  const now = Date.now();
  const list = [];
  for (const st of files.values()) {
    if (st.isSub && !st.finished && now - st.mtime < RUNNING_MS) {
      const parent = delegations.get(st.toolUseId);
      list.push({
        session: st.session, agent: st.agent, agentType: st.agentType, id: st.toolUseId, label: st.description || '',
        parent: parent?.agent || 'main', parentType: parent?.agentType || '', title: titles.get(st.session) || '',
      });
    }
  }
  return list;
}

const LIVE_CSS = String.raw`
#livebar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:0 24px 10px;padding:8px 12px;background:var(--card);border:1px solid var(--line);border-radius:8px}
#livebar select,#livebar button{font:inherit;font-size:13px;color:inherit;background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:4px 9px;max-width:240px}#livebar button{cursor:pointer}#livebar button:disabled{opacity:.5;cursor:default}
#livestate{display:flex;align-items:center;gap:7px;font-weight:600}#livedot{width:9px;height:9px;border-radius:50%;background:var(--muted)}#livedot.on{background:#1d9e75}#livedot.err{background:#e24b4a}#livemetrics{color:var(--muted);font-size:13px;flex:1;min-width:180px}
body.live .card.dim{opacity:.62}body.live #wires path.off{opacity:.2}
#pulses{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible;z-index:3}
.card.running{border-color:#1d9e75;box-shadow:0 0 0 1px #1d9e75;opacity:1!important}.card.hit{outline:2px solid var(--accent);outline-offset:1px;opacity:1!important}.card.user{background:var(--warn);color:var(--warn-t)}
#side{position:sticky;top:12px;display:flex;flex-direction:column;gap:10px;max-height:calc(100vh - 24px);min-width:0}#side #panel{position:static;flex:1;min-height:160px;max-height:none}
#feedbox{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;max-height:44vh;min-height:150px}#feedbox h2{font-size:14px;margin:0 0 6px}#feed{overflow:auto;flex:1;display:flex;flex-direction:column;gap:2px}
.ev{display:grid;grid-template-columns:62px 1fr;gap:6px;width:100%;text-align:left;font:inherit;font-size:12px;color:inherit;background:none;border:0;border-radius:5px;padding:3px 4px;cursor:pointer}.ev:hover{background:var(--bg)}.ev time{color:var(--muted)}.ev b{font-weight:600}.ev.err{color:#e24b4a}.ev.fresh{background:var(--bg)}.ev span{overflow-wrap:anywhere}
#feedempty{color:var(--muted);font-size:13px}
#todaybar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:0 24px 12px}#todaybar .label{font-weight:600;margin-right:4px}#todaybar .stat{padding:4px 10px;font-size:13px}#todaybar .stat b{font-size:15px}#todaybar .new{border-color:#1d9e75}
.card em.count{display:block;margin-top:3px;font-style:normal;font-size:11.5px;font-weight:600;opacity:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.card em.count.zero{font-weight:400;opacity:.55}
#daybox .dayline{font-size:13px;margin:0}#daybox .dayfile{display:grid;grid-template-columns:1fr auto;gap:8px;font-size:12px;padding:2px 0}#daybox .dayfile span{overflow-wrap:anywhere}#daybox .dayfile b{font-weight:600;white-space:nowrap}
@media(max-width:720px){#todaybar{margin-left:14px;margin-right:14px}}
@media(max-width:1320px){body.live .layout{grid-template-columns:1fr}#side{position:static;max-height:none}#feedbox{max-height:300px}}
@media(max-width:720px){body.live #board{grid-template-columns:1fr;gap:16px}#pulses{display:none}#livebar{margin-left:14px;margin-right:14px}}
`;

const LIVE_CLIENT = String.raw`
(function(){
var log=[],seen=0,open={},runs={},filter='all',sessions={},dirty=false,active=0,replaying=false,MAX=140;
var COLORS={prompt:'#ef9f27',reply:'#ef9f27',delegate:'#7f77dd',skill:'#378add',tool:'#1d9e75','tool-done':'#97c459','agent-done':'#7f77dd',err:'#e24b4a'};
var calm=matchMedia('(prefers-reduced-motion: reduce)').matches;
document.body.classList.add('live');TYPES.tool='Công cụ';TYPES.user='Người dùng';KINDS.live='tương tác';
var bar=el('div');bar.id='livebar';
var state=el('div');state.id='livestate';var dot=el('span');dot.id='livedot';var stateText=el('span',null,'Đang kết nối');state.appendChild(dot);state.appendChild(stateText);
var metrics=el('div',null,'');metrics.id='livemetrics';
var pick=el('select');pick.setAttribute('aria-label','Chọn phiên');pick.appendChild(new Option('Tất cả phiên','all'));
var replay=el('button',null,'Phát lại 40 bước');replay.type='button';
[state,metrics,pick,replay].forEach(function(x){bar.appendChild(x)});
var layout=document.querySelector('.layout');layout.parentNode.insertBefore(bar,layout);
var side=el('div');side.id='side';var box=el('section');box.id='feedbox';box.appendChild(el('h2',null,'Luồng trực tiếp'));var feed=el('div');feed.id='feed';feed.setAttribute('aria-live','off');box.appendChild(feed);
layout.insertBefore(side,panel);side.appendChild(box);side.appendChild(panel);
var pulses=document.createElementNS('http://www.w3.org/2000/svg','svg');pulses.id='pulses';pulses.setAttribute('aria-hidden','true');board.appendChild(pulses);
function ensure(id,props){if(byId[id])return id;var n={id:id,items:[],path:'',body:'',desc:'',source:'Trực tiếp'};Object.keys(props).forEach(function(k){n[k]=props[k]});D.nodes.push(n);byId[id]=n;dirty=true;return id}
ensure('live:user',{type:'user',lane:0,title:'Bạn',desc:'Người gửi yêu cầu',source:'repo'});
function link(a,b){if(a===b)return;if(D.edges.some(function(e){return e.from===a&&e.to===b||e.from===b&&e.to===a}))return;D.edges.push({from:a,to:b,kind:'live'});dirty=true}
function agentNode(type){var hit=D.nodes.filter(function(n){return n.type==='agent'&&n.title===type});if(hit.length)return hit[0].id;return ensure('agent:live:'+type,{type:'agent',lane:1,title:type,desc:'Agent có sẵn'})}
function actor(key,type){return key==='main'?'main':agentNode(type||'agent')}
function skillNode(name,cmd){var bare=name.split(':').pop();var hit=D.nodes.filter(function(n){return n.type==='skill'&&n.title===bare});if(hit.length)return hit[0].id;if(cmd)return null;return ensure('skill:live:'+name,{type:'skill',lane:2,title:bare,desc:'Skill ngoài repo'})}
function refNode(ref){if(!ref)return null;var m;
if(ref.indexOf('lessons-learned')===0&&byId.lessons)return 'lessons';if(ref.indexOf('games/')===0&&byId.games)return 'games';
if((m=ref.match(/^domains\/([^/]+)\/\.claude\/skills\/([^/]+)/))&&byId['skill:'+m[1]+':'+m[2]])return 'skill:'+m[1]+':'+m[2];
if((m=ref.match(/^domains\/([^/]+)/))&&byId['domain:'+m[1]])return 'domain:'+m[1];
if((m=ref.match(/^scripts\/([^/]+)/))&&byId['script:'+m[1]])return 'script:'+m[1];
if((m=ref.match(/^\.claude\/agents\/([^/]+)\.md/))&&byId['agent:repo:'+m[1]])return 'agent:repo:'+m[1];
if((m=ref.match(/^\.claude\/skills\/([^/]+)/))&&byId['skill:repo:'+m[1]])return 'skill:repo:'+m[1];return null}
function toolNode(ev){return refNode(ev.ref)||ensure('tool:'+ev.name,{type:'tool',lane:4,title:ev.name,desc:'Công cụ'})}
function route(ev){var me=actor(ev.agent,ev.agentType);switch(ev.kind){
case 'prompt':return['live:user','main'];case 'reply':return['main','live:user'];
case 'delegate':return[me,agentNode(ev.name)];
case 'skill':var s=skillNode(ev.name,ev.cmd);return s?[me,s]:null;
case 'tool':return[me,toolNode(ev)];
case 'tool-done':var o=open[ev.id];return o?[o.to,o.from]:null;
case 'agent-done':return[me,actor(ev.parent,ev.parentType)];}return null}
function apply(ev,r){if(ev.kind==='tool')open[ev.id]={from:r[0],to:r[1],label:ev.label||ev.name,t:Date.now()};
if(ev.kind==='tool-done')delete open[ev.id];
if(ev.kind==='delegate')runs[ev.id]={node:r[1],t:Date.now(),label:ev.label};
if(ev.kind==='agent-done'){delete runs[ev.id];Object.keys(open).forEach(function(k){if(open[k].from===r[0]&&!Object.keys(runs).some(function(x){return runs[x].node===r[0]}))delete open[k]})}}
function words(ev){var f=byId[ev._f],t=byId[ev._t],a=f?f.title:'',b=t?t.title:'';switch(ev.kind){
case 'prompt':return[a+' → '+b,ev.label];case 'reply':return[a+' → '+b,'trả lời'];case 'delegate':return[a+' → '+b,'giao việc: '+(ev.label||'')];
case 'skill':return[a+' → '+b,'dùng skill'];case 'tool':return[a+' → '+b,ev.label||''];case 'tool-done':return[a+' → '+b,ev.ok?'xong':'lỗi'];case 'agent-done':return[a+' → '+b,'báo kết quả'];}return[a,'']}
function row(ev,fresh){var b=el('button','ev'+(ev.ok===false?' err':'')+(fresh?' fresh':''));b.type='button';var d=new Date(ev.ts);var time=el('time',null,isNaN(d)?'':d.toLocaleTimeString('vi-VN',{hour12:false}));var w=words(ev);var s=el('span');s.appendChild(el('b',null,w[0]));if(w[1])s.appendChild(document.createTextNode('  '+w[1]));b.appendChild(time);b.appendChild(s);b.onclick=function(){if(byId[ev._t])select(ev._t)};if(fresh)setTimeout(function(){b.classList.remove('fresh')},1400);return b}
function pushRow(ev,fresh){var e=document.getElementById('feedempty');if(e)e.remove();var stick=feed.scrollTop<8;feed.insertBefore(row(ev,fresh),feed.firstChild);while(feed.children.length>MAX)feed.removeChild(feed.lastChild);if(stick)feed.scrollTop=0}
function wire(a,b){var ps=wires.querySelectorAll('path');for(var i=0;i<ps.length;i++){var p=ps[i];if(p.dataset.from===a&&p.dataset.to===b)return{p:p,rev:false};if(p.dataset.from===b&&p.dataset.to===a)return{p:p,rev:true}}return null}
function flash(id){var c=cards[id];if(!c)return;c.classList.add('hit');setTimeout(function(){if(cards[id])cards[id].classList.remove('hit')},520)}
function pulse(a,b,color){flash(b);var w=wire(a,b);if(calm||!w||active>32||document.hidden)return;active++;var len=w.p.getTotalLength(),c=document.createElementNS('http://www.w3.org/2000/svg','circle');c.setAttribute('r','4.5');c.setAttribute('fill',color);pulses.appendChild(c);var t0=performance.now(),D0=Math.min(900,420+len);
function step(now){var k=Math.min(1,(now-t0)/D0);if(!w.p.isConnected||k>=1){c.remove();active--;return}var e=k<.5?2*k*k:1-Math.pow(-2*k+2,2)/2,pt=w.p.getPointAtLength((w.rev?1-e:e)*len);c.setAttribute('cx',pt.x);c.setAttribute('cy',pt.y);requestAnimationFrame(step)}requestAnimationFrame(step)}
function busy(){var m={};Object.keys(runs).forEach(function(k){m[runs[k].node]=m[runs[k].node]||(runs[k].label?runs[k].label:'đang chạy')});Object.keys(open).forEach(function(k){m[open[k].from]=open[k].label});return m}
function decorate(){var m=busy();Object.keys(cards).forEach(function(id){var c=cards[id],n=byId[id],s=c.querySelector('span'),on=m[id]!=null;c.classList.toggle('running',on);if(s)s.textContent=on?m[id]:(n.desc||n.path)});var a=Object.keys(runs).length,t=Object.keys(open).length,now=Date.now(),rate=log.filter(function(e){var x=new Date(e.ts).getTime();return now-x<60000&&(filter==='all'||e.session===filter)}).length;metrics.textContent=a+' agent đang chạy · '+t+' tool đang mở · '+rate+' sự kiện/phút'}
var baseBuild=build,basePaint=paint;
window.build=function(){baseBuild();board.appendChild(pulses);decorate();badges()};
var day=null,baseVisible=visible,baseDetail=detail,todayBar=el('div');todayBar.id='todaybar';layout.parentNode.insertBefore(todayBar,layout);
function sumSkill(n){return Object.keys(day.skills).reduce(function(t,k){return k.split(':').pop()===n.title?t+day.skills[k]:t},0)}
function kbFor(ref){if(ref.indexOf('claude-memory/')===0)return ensure('kb:automemory',{type:'knowledge',lane:3,title:'Bộ nhớ tự động',desc:'Ghi nhớ của Claude cho repo này',source:'repo'});var low=ref.toLowerCase(),best=null;D.nodes.forEach(function(n){if(n.type!=='knowledge'||!n.path)return;var p=n.path.toLowerCase();if(low.indexOf(p)===0&&(!best||p.length>best.path.length))best=n});return best?best.id:null}
function byKnowledge(){var out={};if(!day)return out;Object.keys(day.files).forEach(function(ref){var id=kbFor(ref);if(!id)return;var x=out[id]=out[id]||{read:0,created:0,updated:0,files:[]},f=day.files[ref];x.read+=f.read;x.created+=f.created?1:0;x.updated+=f.updated;x.files.push({ref:ref,read:f.read,created:f.created,updated:f.updated})});return out}
function countFor(n){if(!day)return null;switch(n.type){case 'main':case 'user':return day.prompts;case 'agent':return day.agents[n.title]||0;case 'skill':return sumSkill(n);case 'tool':return day.tools[n.title]||0;case 'hook':return n.title==='SessionStart'?day.sessions:null;
case 'script':var runs=D.nodes.filter(function(h){return h.type==='hook'&&h.title==='SessionStart'&&h.desc===n.title}).length*day.sessions;return(day.scripts[n.title]||0)+runs;}return null}
function unit(n){return n.type==='user'||n.type==='main'?' yêu cầu':n.type==='hook'?' phiên':' lượt'}
function kbText(x){return x.read+' đọc · '+x.created+' mới · '+x.updated+' sửa'}
function badges(){if(!day)return;var k=byKnowledge();Object.keys(cards).forEach(function(id){var c=cards[id],n=byId[id],b=c.querySelector('em.count'),text,zero;if(n.type==='knowledge'){var x=k[id]||{read:0,created:0,updated:0};text=kbText(x);zero=!(x.read+x.created+x.updated)}else{var v=countFor(n);if(v==null){if(b)b.remove();return}text=v+unit(n);zero=!v}if(!b){b=el('em','count');c.appendChild(b)}b.textContent=text;b.classList.toggle('zero',zero);b.title='Thống kê hôm nay'})}
function chip(value,label,cls){var s=el('div','stat'+(cls?' '+cls:''));s.appendChild(el('b',null,value));s.appendChild(document.createTextNode(label));return s}
function total(map){return Object.keys(map).reduce(function(t,k){return t+map[k]},0)}
function renderBar(){if(!day)return;var r=0,c=0,u=0;Object.keys(day.files).forEach(function(k){var f=day.files[k];r+=f.read;if(f.created)c++;u+=f.updated});todayBar.textContent='';var p=day.day.split('-');todayBar.appendChild(el('span','label','Hôm nay '+p[2]+'/'+p[1]));[[day.prompts,'yêu cầu'],[day.sessions,'phiên'],[total(day.agents),'lượt agent'],[total(day.skills),'lượt skill'],[total(day.tools),'lượt tool'],[r,'lượt đọc kiến thức']].forEach(function(x){todayBar.appendChild(chip(x[0],x[1]))});todayBar.appendChild(chip(c,'kiến thức mới','new'));todayBar.appendChild(chip(u,'lượt cập nhật kiến thức','new'))}
function dayDetail(n){var old=document.getElementById('daybox');if(old)old.remove();if(!day||!n)return;var box=el('div');box.id='daybox';box.appendChild(el('h3',null,'Hôm nay'));if(n.type==='knowledge'){var x=byKnowledge()[n.id];if(!x)box.appendChild(el('p','dayline','Chưa được đọc hoặc ghi hôm nay.'));else{box.appendChild(el('p','dayline',kbText(x)));x.files.sort(function(a,b){return(b.read+b.created+b.updated)-(a.read+a.created+a.updated)}).slice(0,12).forEach(function(f){var row=el('div','dayfile');row.appendChild(el('span',null,f.ref.replace(/^claude-memory\//,'')));var bits=[];if(f.read)bits.push(f.read+' đọc');if(f.created)bits.push('mới');if(f.updated)bits.push(f.updated+' sửa');row.appendChild(el('b',null,bits.join(' · ')));box.appendChild(row)})}}else{var v=countFor(n);if(v==null)return;box.appendChild(el('p','dayline',v+unit(n)))}var at=panel.querySelector('.path');if(at)at.parentNode.insertBefore(box,at.nextSibling);else panel.appendChild(box)}
window.visible=function(n){if(baseVisible(n))return true;return !!day&&(n.type==='agent'||n.type==='skill')&&countFor(n)>0};
window.detail=function(n){baseDetail(n);dayDetail(n)};
function setDay(v){day=v;Object.keys(day.agents).forEach(agentNode);Object.keys(day.skills).forEach(function(k){skillNode(k)});Object.keys(day.tools).forEach(function(k){ensure('tool:'+k,{type:'tool',lane:4,title:k,desc:'Công cụ'})});Object.keys(day.files).forEach(kbFor);var had=dirty;flush();if(!had)badges();renderBar();dayDetail(byId[sel])}
window.paint=function(){basePaint();Object.keys(busy()).forEach(function(id){if(cards[id])cards[id].classList.remove('dim')})};
function flush(){if(dirty){dirty=false;window.build()}else decorate()}
function noteSession(ev){if(!ev.session)return;var known=sessions[ev.session];var label=ev.title||ev.session.slice(0,8);if(!known){var o=new Option(label,ev.session);sessions[ev.session]=o;pick.appendChild(o)}else if(ev.title)known.text=ev.title}
function take(ev,liveNow){if(ev.seq<=seen)return;seen=ev.seq;noteSession(ev);log.push(ev);if(log.length>600)log.shift();if(filter!=='all'&&ev.session!==filter)return;play(ev,liveNow)}
function play(ev,liveNow){var r=route(ev);if(!r)return;ev._f=r[0];ev._t=r[1];link(r[0],r[1]);if(liveNow){apply(ev,r);flush();pushRow(ev,true);pulse(r[0],r[1],ev.ok===false?COLORS.err:COLORS[ev.kind]);decorate()}else pushRow(ev,false)}
function setRunning(list){list.forEach(function(x){if(filter!=='all'&&x.session!==filter)return;var n=agentNode(x.agentType);var p=actor(x.parent,x.parentType);link(p,n);runs[x.id||x.agent]={node:n,t:Date.now(),label:x.label}})}
function rerender(){open={};runs={};feed.textContent='';log.forEach(function(ev){if(filter==='all'||ev.session===filter)play(ev,false)});if(!feed.children.length){var e=el('div',null,'Chưa có hoạt động trong phiên này.');e.id='feedempty';feed.appendChild(e)}setRunning(lastRunning);flush()}
var lastRunning=[];
pick.onchange=function(){filter=pick.value;rerender()};
replay.onclick=function(){if(replaying)return;var list=log.filter(function(e){return(filter==='all'||e.session===filter)&&e._f&&e._t}).slice(-40);if(!list.length)return;replaying=true;replay.disabled=true;var i=0;(function next(){if(i>=list.length){replaying=false;replay.disabled=false;replay.textContent='Phát lại 40 bước';return}var ev=list[i++];replay.textContent='Đang phát '+i+'/'+list.length;pulse(ev._f,ev._t,ev.ok===false?COLORS.err:COLORS[ev.kind]);setTimeout(next,380)})()};
setInterval(function(){var now=Date.now(),changed=false;Object.keys(open).forEach(function(k){if(now-open[k].t>600000){delete open[k];changed=true}});if(changed)decorate();else decorate()},5000);
var es=new EventSource('/events');
es.addEventListener('hello',function(m){var d=JSON.parse(m.data);d.history.forEach(function(ev){take(ev,false)});lastRunning=d.running;setRunning(d.running);if(!log.length){var e=el('div',null,'Đang chờ hoạt động…');e.id='feedempty';feed.appendChild(e)}flush();setDay(d.today);dot.className='on';stateText.textContent='Trực tiếp'});
es.addEventListener('ev',function(m){take(JSON.parse(m.data),true)});
es.addEventListener('stats',function(m){setDay(JSON.parse(m.data))});
es.onerror=function(){dot.className='err';stateText.textContent='Mất kết nối, đang thử lại'};
flush();
})();
`;

function regenerate() {
  return new Promise((resolve, reject) => {
    execFile(process.execPath, [GENERATOR, '--root', ROOT], { cwd: ROOT, windowsHide: true }, (error, _out, stderr) => {
      if (error) reject(new Error(stderr || error.message));
      else resolve(fs.readFileSync(HTML, 'utf8'));
    });
  });
}

function inject(html) {
  return html
    .replace('</style>', () => `${LIVE_CSS}</style>`)
    .replace('</body>', () => `<script>${LIVE_CLIENT}</script></body>`);
}

function createServer(port) {
  const allowed = new Set([`${HOST}:${port}`, `localhost:${port}`]);
  return http.createServer(async (req, res) => {
    // Chặn DNS rebinding: trang web lạ không thể đọc dữ liệu qua tên miền trỏ về máy này.
    if (!allowed.has(req.headers.host) || req.method !== 'GET') {
      res.writeHead(403).end();
      return;
    }
    const url = req.url.split('?')[0];
    if (url === '/health') {
      res.writeHead(200, { 'Content-Type': 'application/json' }).end(JSON.stringify({ app: APP, root: ROOT }));
    } else if (url === '/events') {
      res.writeHead(200, { 'Content-Type': 'text/event-stream; charset=utf-8', 'Cache-Control': 'no-store', Connection: 'keep-alive' });
      res.write(`event: hello\ndata: ${JSON.stringify({ history: ring, running: runningAgents(), today: statsView() })}\n\n`);
      clients.add(res);
      req.on('close', () => {
        clients.delete(res);
        if (!clients.size) idleSince = Date.now();
      });
    } else if (url === '/') {
      try {
        const page = inject(await regenerate());
        res.writeHead(200, {
          'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store',
          'Content-Security-Policy': "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self'",
        }).end(page);
      } catch (error) {
        res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' }).end(error.message);
      }
    } else {
      res.writeHead(404).end();
    }
  });
}

async function probe(port) {
  try {
    const res = await fetch(`http://${HOST}:${port}/health`, { signal: AbortSignal.timeout(500) });
    const body = await res.json();
    return body.app === APP && body.root === ROOT;
  } catch {
    return false;
  }
}

async function findRunning() {
  for (let port = PORT_FIRST; port <= PORT_LAST; port++) {
    if (await probe(port)) return `http://${HOST}:${port}/`;
  }
  return null;
}

function openBrowser(url) {
  const [cmd, args] = process.platform === 'win32' ? ['cmd', ['/c', 'start', '', url]]
    : process.platform === 'darwin' ? ['open', [url]] : ['xdg-open', [url]];
  spawn(cmd, args, { detached: true, stdio: 'ignore', windowsHide: true }).unref();
}

function listen(port) {
  if (port > PORT_LAST) {
    console.error(`Không còn cổng trống trong khoảng ${PORT_FIRST}-${PORT_LAST}.`);
    process.exit(1);
  }
  const server = createServer(port);
  server.once('error', (error) => {
    if (error.code === 'EADDRINUSE') listen(port + 1);
    else throw error;
  });
  server.listen(port, HOST, () => {
    const url = `http://${HOST}:${port}/`;
    console.log(`Agent Dashboard Live: ${url}`);
    if (process.argv.includes('--open')) openBrowser(url);
    setInterval(() => { for (const res of clients) res.write(': ping\n\n'); }, 15000);
    scanNewKnowledge();
    setInterval(scanNewKnowledge, 15000);
    setInterval(() => {
      rollDay();
      if (!todayDirty) return;
      todayDirty = false;
      const frame = `event: stats\ndata: ${JSON.stringify(statsView())}\n\n`;
      for (const res of clients) res.write(frame);
    }, 1000);
    const codeTime = () => fs.statSync(SCRIPT).mtimeMs;
    const startedWith = codeTime();
    setInterval(() => {
      // Code đã cập nhật thì tắt để lần mở sau chạy bản mới.
      if (codeTime() !== startedWith) process.exit(0);
      if (!clients.size && Date.now() - idleSince > IDLE_EXIT_MS) process.exit(0);
    }, 5000);
  });
}

async function main() {
  const existing = await findRunning();
  if (existing) {
    console.log(`Agent Dashboard Live: ${existing}`);
    if (process.argv.includes('--open')) openBrowser(existing);
    return;
  }
  if (process.argv.includes('--detach')) {
    spawn(process.execPath, [SCRIPT, '--root', ROOT], { cwd: ROOT, detached: true, stdio: 'ignore', windowsHide: true }).unref();
    for (let i = 0; i < 40; i++) {
      await new Promise((resolve) => setTimeout(resolve, 250));
      const url = await findRunning();
      if (url) {
        console.log(`Agent Dashboard Live: ${url}`);
        if (process.argv.includes('--open')) openBrowser(url);
        return;
      }
    }
    console.error('Không khởi động được server live sau 10 giây.');
    process.exit(1);
  }
  scan();
  setInterval(() => {
    try { scan(); } catch (error) { console.error(error.message); }
  }, POLL_MS);
  listen(PORT_FIRST);
}

main();
