"""Outliner kiểu Maya cho Rig Lab: cây xương theo cấp + lớp mesh. Idempotent (/*OUTLINER*/). Chạy: python patch_outliner.py"""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")
s = open(P, encoding="utf8").read()
if "/*OUTLINER*/" in s:
    print("already patched"); raise SystemExit

CSS = r"""
/*OUTLINER*/
#olBtn{padding:0;width:34px;height:30px;display:inline-flex;align-items:center;justify-content:center}
#olBtn svg,.ol svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
#olBtn.on{background:var(--accent);border-color:var(--accent);color:#fff}
.ol{position:absolute;left:8px;top:52px;width:264px;max-height:calc(100% - 128px);display:none;flex-direction:column;background:var(--panel);border:1px solid var(--line);border-radius:10px;z-index:5;box-shadow:0 4px 18px #0003;overflow:hidden}
.ol.show{display:flex}
.olh{display:flex;align-items:center;gap:2px;padding:4px;border-bottom:1px solid var(--line)}
.olh input{flex:1;min-width:0;height:26px;padding:0 8px;border-radius:6px;border:1px solid var(--line);background:var(--bg);color:var(--fg);font-size:12px}
.olh button,.olr button{padding:0;width:26px;height:26px;display:inline-flex;align-items:center;justify-content:center;border:0;background:transparent;color:var(--mute);border-radius:6px;flex:none}
.olh button:hover,.olr button:hover{background:var(--line);color:var(--fg)}
.olb{overflow:auto;padding:3px 0;flex:1;-webkit-overflow-scrolling:touch}
.ols{font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--mute);padding:6px 10px 2px}
.olr{display:flex;align-items:center;gap:2px;height:26px;padding-right:2px;cursor:pointer;font-size:12px;white-space:nowrap;user-select:none}
.olr:hover{background:color-mix(in srgb,var(--line) 55%,transparent)}
.olr.sel{background:color-mix(in srgb,var(--accent) 22%,transparent);color:var(--fg);font-weight:600}
.olr.hid .olt{opacity:.38}
.olr .olt{flex:1;overflow:hidden;text-overflow:ellipsis}
.olr .olx{width:16px;text-align:center;color:var(--mute);font-size:10px;flex:none}
.olr .old{width:8px;height:8px;border-radius:50%;flex:none;margin-right:4px}
.olr button.act{color:var(--accent)}
.olr button.off{color:var(--mute);opacity:.55}
.olr.dim{opacity:.4}
body.tm .olr{height:38px}body.tm .olr button,body.tm .olh button{width:36px;height:36px}body.tm .olh input{height:36px}
body.tm .ol{width:min(300px,calc(100% - 16px))}
"""

IC = {
 "tree": '<path d="M4 5h6M4 12h6M4 19h6M14 5h6M14 12h6"/><path d="M7 5v14"/>',
 "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 "lock": '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/>',
 "iso": '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/>',
 "all": '<path d="M5 12.5l4.5 4.5L19 7"/>',
 "plus": '<path d="M12 5v14M5 12h14"/>',
 "minus": '<path d="M5 12h14"/>',
 "branch": '<circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="12" r="2"/><path d="M6 8v8M8 6c6 0 6 6 8 6"/>',
 "focus": '<path d="M4 8V5h3M17 5h3v3M20 16v3h-3M7 19H4v-3"/><circle cx="12" cy="12" r="2"/>',
}
def svg(n): return '<svg viewBox="0 0 24 24">%s</svg>' % IC[n]

BTN = '<button class="tool" id="olBtn" title="Outliner: cây xương và các lớp mesh" aria-label="Outliner">%s</button>' % svg("tree")
PANEL = ('<div class="ol" id="ol" role="tree" aria-label="Outliner">'
         '<div class="olh"><input id="olQ" type="search" placeholder="Tìm…" aria-label="Tìm trong Outliner">'
         '<button id="olSel" title="Chọn cả nhánh con của mục đang chọn" aria-label="Chọn nhánh">%s</button>'
         '<button id="olFoc" title="Nhìn vào mục đang chọn" aria-label="Nhìn vào">%s</button>'
         '<button id="olIso" title="Cô lập: ẩn mọi khớp khác" aria-label="Cô lập">%s</button>'
         '<button id="olAll" title="Hiện tất cả, mở khoá tất cả" aria-label="Hiện tất cả">%s</button>'
         '<button id="olExp" title="Mở / thu gọn cả cây" aria-label="Mở hoặc thu gọn">%s</button></div>'
         '<div class="olb" id="olB"></div></div>') % (svg("branch"), svg("focus"), svg("iso"), svg("all"), svg("plus"))

JS = r"""
/*OUTLINER*/
// Outliner kiểu Maya: lớp mesh + cây xương (cha → con). Mắt = ẩn/hiện (ẩn cha thì con ẩn theo), khoá = không chọn được,
// Ctrl/Shift/"+" nhiều mục, double-click = nhìn vào. Quan hệ cha-con do mẫu rig quyết định nên không kéo-thả đổi cha.
(function () {
  const ol = $("ol"), body = $("olB"), btn = $("olBtn"), q = $("olQ");
  const hide = new Set(), lock = new Set(), openN = {}, ico = {
    eye: '%EYE%', eyeOff: '<svg viewBox="0 0 24 24"><path d="M3 3l18 18M10.6 6.1A9.8 9.8 0 0112 6c6 0 10 6 10 6a17 17 0 01-3.2 3.7M6.4 7.5C3.6 9.3 2 12 2 12s4 7 10 7a9.700 9.700 0 004.100-.9"/></svg>', lock: '%LOCK%', unlock: '<svg viewBox="0 0 24 24"><rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 017.600-1.700"/></svg>' };
  let tree = [], kids = {}, sig = "", anchor = null, queued = 0, expAll = false;
  const store = { get: k => { try { return localStorage.getItem(k); } catch { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch {} } };
  const KEY = "ol:" + location.pathname;
  const label = n => n === "root" ? "root" : n;
  function build() {
    const B = buildSkeleton(LM); kids = {}; B.forEach(b => (kids[b.parent || ""] = kids[b.parent || ""] || []).push(b.name));
    const depth = {}, order = [];
    (function walk(n, d) { depth[n] = d; order.push(n); (kids[n] || []).forEach(c => walk(c, d + 1)); })("root", 0);
    // "Weapon" nằm cạnh root, các nút mồ côi khác (nếu có) đứng cuối
    B.forEach(b => { if (!(b.name in depth)) { (function walk(n, d) { depth[n] = d; order.push(n); (kids[n] || []).forEach(c => walk(c, d + 1)); })(b.name, 1); } });
    tree = order.map(n => ({ n, d: depth[n], twist: !!(B.find(b => b.name === n) || {}).twist }));
    sig = order.join("|");
  }
  const parentOf = n => { for (const p in kids) if (kids[p].includes(n)) return p || null; return null; };
  const effHidden = n => { for (let c = n; c; c = parentOf(c)) if (hide.has(c)) return true; return false; };
  const lockedEff = n => { for (let c = n; c; c = parentOf(c)) if (lock.has(c)) return true; return false; };
  const isOpen = n => (n in openN) ? openN[n] : (expAll || !/(Finger|Twist)/.test(n) && !/^Wrist_/.test(n));
  function sub(n) { const out = []; (function w(x) { (kids[x] || []).forEach(c => { out.push(c); w(c); }); })(n); return out; }
  function visibleRows() {
    const f = q.value.trim().toLowerCase(), rows = [], hiddenBy = [];
    let skipDepth = null;
    for (const t of tree) {
      if (skipDepth !== null && t.d > skipDepth) continue; skipDepth = null;
      if (f) { if (!t.n.toLowerCase().includes(f)) continue; rows.push(t); continue; }
      rows.push(t);
      if ((kids[t.n] || []).length && !isOpen(t.n)) skipDepth = t.d;
    }
    return rows;
  }
  const selNames = () => step === 2 ? [...S] : (jointSel ? [jointSel] : []);
  function meshRows() {
    const r = [{ id: "body", t: "Thân (mesh)", on: vis.body }];
    if (typeof clothMeshes !== "undefined" && clothMeshes.length) r.push({ id: "cloth", t: "Quần áo", on: vis.cloth });
    DATA.props.forEach((p, i) => r.push({ id: "p" + i, t: String(p.name || "Prop").replace("EN_M11_Boss_Gaygor_", "Prop "), on: vis.props[i] }));
    r.push({ id: "skel", t: "Xương (đường nối)", on: showSkel });
    if (FINGERS && FINGERS.length) r.push({ id: "fing", t: "Ngón tay", on: showFing });
    return r;
  }
  function render() {
    queued = 0;
    if (!ol.classList.contains("show")) return;
    const B = buildSkeleton(LM).map(b => b.name).join("|"); if (B !== sig) build();
    const sn = new Set(selNames()), rows = visibleRows();
    let h = '<div class="ols">Lớp mesh</div>' + meshRows().map(m => `<div class="olr ${m.on ? "" : "hid"}" data-m="${m.id}"><span class="olx"></span><span class="olt">${esc(m.t)}</span><button data-a="mv" class="${m.on ? "" : "off"}" title="Ẩn / hiện" aria-label="Ẩn hoặc hiện">${m.on ? ico.eye : ico.eyeOff}</button></div>`).join("");
    h += '<div class="ols">Xương</div>';
    h += rows.map(t => {
      const hn = effHidden(t.n), ln = lockedEff(t.n), has = (kids[t.n] || []).length, col = t.n === "root" ? "var(--mute)" : lmColor(t.n);
      const dis = !(t.n in lmMesh) && step === 2;
      return `<div class="olr ${sn.has(t.n) ? "sel" : ""} ${hn ? "hid" : ""} ${dis ? "dim" : ""}" role="treeitem" data-n="${t.n}" style="padding-left:${4 + (q.value ? 0 : t.d) * 11}px" title="${t.n}${t.twist ? " (twist)" : ""}">
        <span class="olx" data-a="x">${has && !q.value ? (isOpen(t.n) ? "▾" : "▸") : ""}</span><i class="old" style="background:${col}"></i><span class="olt">${esc(label(t.n))}</span>
        <button data-a="v" class="${hide.has(t.n) ? "off" : hn ? "off" : ""}" title="Ẩn / hiện (ẩn cha thì con ẩn theo)" aria-label="Ẩn hoặc hiện">${hn ? ico.eyeOff : ico.eye}</button>
        <button data-a="l" class="${lock.has(t.n) ? "act" : ln ? "act" : "off"}" title="Khoá: không chọn được" aria-label="Khoá">${ln ? ico.lock : ico.unlock}</button></div>`;
    }).join("");
    const sy = body.scrollTop; body.innerHTML = h; body.scrollTop = sy;
  }
  const later = () => { if (!queued) queued = setTimeout(render, 30); };

  // ---- chọn
  function setJointByName(n) { try { selectBoneByName(n); } catch (e) { console.error(e); } }
  function select(n, mode) {   // mode: "set" | "toggle" | "range"
    if (lockedEff(n)) return;
    if (step === 2) {
      if (!(n in lmMesh)) return;
      if (mode === "range" && anchor && anchor !== n) {
        const rows = visibleRows().map(t => t.n).filter(x => x in lmMesh && !lockedEff(x)), a = rows.indexOf(anchor), b = rows.indexOf(n);
        if (a >= 0 && b >= 0) { setSel(rows.slice(Math.min(a, b), Math.max(a, b) + 1), false); return; }
      }
      if (mode === "toggle") pick(n, true); else pick(n, false);
      anchor = n;
    } else if (step >= 4) { setJointByName(n); anchor = n; }
    later();
  }
  function applyHide() { syncScene(); later(); }
  body.addEventListener("click", e => {
    const mr = e.target.closest("[data-m]");
    if (mr) {
      const id = mr.dataset.m;
      if (id === "body") vis.body = !vis.body; else if (id === "cloth") vis.cloth = !vis.cloth; else if (id === "skel") showSkel = !showSkel; else if (id === "fing") showFing = !showFing;
      else if (id[0] === "p") vis.props[+id.slice(1)] = !vis.props[+id.slice(1)];
      try { renderVopts(); } catch {} syncScene(); later(); return;
    }
    const r = e.target.closest("[data-n]"); if (!r) return; const n = r.dataset.n, a = (e.target.closest("[data-a]") || {}).dataset;
    if (a && a.a === "x") { openN[n] = !isOpen(n); later(); return; }
    if (a && a.a === "v") { hide.has(n) ? hide.delete(n) : hide.add(n); applyHide(); return; }
    if (a && a.a === "l") { lock.has(n) ? lock.delete(n) : lock.add(n); if (lockedEff(n)) { S.delete(n); if (sel === n) sel = [...S].pop() || null; syncScene(); } later(); return; }
    select(n, e.shiftKey ? "range" : (e.ctrlKey || e.metaKey || TM.add) ? "toggle" : "set");
  });
  body.addEventListener("dblclick", e => { const r = e.target.closest("[data-n]"); if (r && !e.target.closest("[data-a]")) { try { frameView([r.dataset.n].filter(k => LM[k])); } catch {} } });
  q.addEventListener("input", later);
  $("olSel").onclick = () => { const n = selNames(); if (!n.length) return; const all = new Set(); n.forEach(x => { all.add(x); sub(x).forEach(c => all.add(c)); });
    if (step === 2) setSel([...all].filter(k => k in lmMesh && !lockedEff(k)), false); later(); };
  $("olFoc").onclick = () => { const n = selNames().filter(k => LM[k]); try { frameView(n.length ? n : null); } catch {} };
  $("olIso").onclick = () => { const n = new Set(selNames()); if (!n.size) return;
    const keep = new Set(); n.forEach(x => { keep.add(x); for (let c = parentOf(x); c; c = parentOf(c)) keep.add(c); sub(x).forEach(c => keep.add(c)); });
    hide.clear(); tree.forEach(t => { if (!keep.has(t.n)) hide.add(t.n); }); applyHide(); };
  $("olAll").onclick = () => { hide.clear(); lock.clear(); applyHide(); };
  $("olExp").onclick = () => { expAll = !expAll; for (const k in openN) delete openN[k]; if (!expAll) tree.forEach(t => { openN[t.n] = !/(Finger|Twist)/.test(t.n) && !/^Wrist_/.test(t.n) && t.d < 99; });
    if (expAll) tree.forEach(t => openN[t.n] = true); else tree.forEach(t => { if (t.d > 2) openN[t.n] = false; }); later(); };

  // ---- nối vào Rig Lab: ẩn marker, khoá chọn, làm tươi khi đổi chọn / bước / dữ liệu
  const _sync = syncScene;
  syncScene = function (d) { _sync.apply(this, arguments); if (step === 2) for (const k in lmMesh) if (effHidden(k)) lmMesh[k].visible = false; later(); };
  const _pick = pick; pick = function (k, add) { if (k && lockedEff(k)) return; return _pick.apply(this, arguments); };
  const _apply = applySel; applySel = function (keys, e) { return _apply.call(this, keys.filter(k => !lockedEff(k)), e); };
  const _setSel = setSel; setSel = function (keys, add) { return _setSel.call(this, keys.filter(k => !lockedEff(k)), add); };
  const _rp = renderPanel; renderPanel = function () { const r = _rp.apply(this, arguments); later(); return r; };

  function show(on) { ol.classList.toggle("show", on); btn.classList.toggle("on", on); store.set(KEY, on ? "1" : "0"); if (on) { build(); render(); } }
  btn.onclick = () => show(!ol.classList.contains("show"));
  const saved = store.get(KEY);
  show(saved === null ? innerWidth > 900 : saved === "1");
})();
""".replace("%EYE%", svg("eye")).replace("%LOCK%", svg("lock"))

# 1) pickJoint tail → selectBoneByName (shared by the viewport and the outliner)
old = """  if (!name) { if (jointSel) { jointSel = null; renderJointBox(); } return; }
  jointSel = /Twist/.test(name) ? null : name; if (jointSel) poseBone = name;
  if (step === 4) { skinBone = name; if (!/Twist/.test(name)) poseBone = name; if (skinView === "dom") skinView = "one"; paintSkin(); } else poseBone = name;
  syncScene(); renderPanel();
}"""
new = """  if (!name) { if (jointSel) { jointSel = null; renderJointBox(); } return; }
  selectBoneByName(name);
}
function selectBoneByName(name) {
  if (name === "root" || name === "Weapon" || step < 4) return;
  if (step === 4 && (!SK || SK.idx[name] === undefined)) return;
  jointSel = /Twist/.test(name) ? null : name; if (jointSel) poseBone = name;
  if (step === 4) { skinBone = name; if (!/Twist/.test(name)) poseBone = name; if (skinView === "dom") skinView = "one"; paintSkin(); } else poseBone = name;
  syncScene(); renderPanel();
}"""
assert s.count(old) == 1; s = s.replace(old, new)

# 2) header button, panel, css, js
a = 'id="tmLbl"'
assert a in s
i = s.index("</label>", s.index(a)) + len("</label>")
s = s[:i] + "\n  " + BTN + s[i:]
a = '    <canvas id="cv"></canvas>'
assert s.count(a) == 1; s = s.replace(a, a + "\n    " + PANEL)
j = s.index("</style>"); s = s[:j] + CSS + s[j:]
k = s.rfind("</script>"); s = s[:k] + JS + s[k:]
open(P, "w", encoding="utf8", newline="").write(s)
print("ok")
