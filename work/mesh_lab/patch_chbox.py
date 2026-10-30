"""Mesh Lab: Channel Box (Translate / Rotate / Scale của vùng chọn, sửa được) + công cụ Free Transform (hộp bao + tay nắm).
Idempotent (/*CHBOX*/). Chạy: python work/mesh_lab/patch_chbox.py rồi build_mesh.py."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")
s = open(P, encoding="utf8").read()
if "/*CHBOX*/" in s:
    print("already patched"); raise SystemExit

def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:80], s.count(a))
    s = s.replace(a, b)

CSS = r"""
/*CHBOX*/
#chbox{position:absolute;right:8px;top:8px;width:196px;z-index:4;background:color-mix(in srgb,var(--panel) 92%,transparent);border:1px solid var(--line);border-radius:10px;font-size:12px;overflow:hidden;backdrop-filter:blur(4px)}
#chbox .chh{display:flex;align-items:center;gap:6px;padding:6px 8px;cursor:pointer;user-select:none;border-bottom:1px solid var(--line)}
#chbox .chh b{font-size:11px;letter-spacing:.05em;text-transform:uppercase;color:var(--mute)}
#chbox .chh span{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--fg)}
#chbox .chh svg{width:14px;height:14px;transition:transform .15s}
#chbox.fold .chh{border-bottom:0} #chbox.fold .chh svg{transform:rotate(-90deg)} #chbox.fold .chr,#chbox.fold .chf{display:none}
#chbox .chr{display:grid;grid-template-columns:1fr 74px;align-items:center;gap:6px;padding:1px 8px}
#chbox .chr label{color:var(--mute);cursor:ew-resize;user-select:none;touch-action:none;padding:3px 0}
#chbox .chr label:hover{color:var(--fg)}
#chbox .chr input{width:100%;font:12px var(--mono);text-align:right;background:var(--raise);color:var(--fg);border:1px solid var(--line);border-radius:5px;padding:2px 5px}
#chbox .chs{padding:5px 8px 2px;font-size:10px;letter-spacing:.06em;text-transform:uppercase;color:var(--mute)}
#chbox .chf{display:flex;gap:6px;padding:6px 8px 8px}
#chbox .chf button{flex:1;font-size:11.5px;padding:3px 4px}
#chbox .chn{padding:8px;color:var(--mute)}
body.tm #chbox .chr{padding:3px 8px} body.tm #chbox .chr input{padding:6px 5px;font-size:14px}
@media (max-width:900px){#chbox{width:176px}}
"""

HTML = '    <div id="chbox"></div>\n'

JS = r"""
/*CHBOX*/
// ---------------------------------------------------------------- Channel Box + Free Transform
// TS = phép biến đổi cộng dồn của vùng chọn hiện tại (A, quanh tâm c0); đổi vùng chọn thì về 0 / 1. Mọi thao tác (gizmo, ô số, Free Transform)
// đều là "áp ma trận M lên vị trí hiện tại" nên dùng chung falloff mềm và đối xứng X của gizmo.
let TS = null;
const V3x = THREE.Vector3, M4x = THREE.Matrix4;
const selSig = () => mode === "o" ? "o:" + [...selO].sort().join(",") : mode + ":" + (active ? active.id : 0) + ":" + selV.size + ":" + (() => { let h = 0; selV.forEach(i => h = (h * 31 + i) % 1000003); return h; })();
function ensureTS() { if (!TS) { const c = selCenter(); if (!c) return null; TS = { c0: c.clone(), A: new M4x(), sig: selSig() }; } return TS; }
function xformApply(M, aff) {
  const R = new M4x().makeScale(-1, 1, 1), Mm = R.clone().multiply(M).multiply(R), tmp = new V3x(), os = new Set();
  for (const a of aff) {
    tmp.copy(a.p0).applyMatrix4(a.m ? Mm : M); const P = a.o.pos, i = a.i;
    P[3 * i] = a.p0.x + (tmp.x - a.p0.x) * a.w; P[3 * i + 1] = a.p0.y + (tmp.y - a.p0.y) * a.w; P[3 * i + 2] = a.p0.z + (tmp.z - a.p0.z) * a.w; os.add(a.o);
  }
  os.forEach(o => touchGeo(o, false));
}
function affSnapshot() { const aff = buildAffected(); aff.forEach(a => { a.p0 = new V3x(a.o.pos[3 * a.i], a.o.pos[3 * a.i + 1], a.o.pos[3 * a.i + 2]); }); return aff; }
function xformEnd(aff) { const os = new Set(aff.map(a => a.o)); os.forEach(o => { touchGeo(o, true); o.mirror = null; }); changed(); refreshSel(); }

// ---- Channel Box
const rad = d => d * Math.PI / 180, deg = r => r * 180 / Math.PI;
function chVals() {
  const c = selCenter(); if (!c) return null;
  if (!TS) return { t: [c.x, c.y, c.z], r: [0, 0, 0], s: [1, 1, 1] };
  const t = TS.c0.clone().applyMatrix4(TS.A), L = TS.A.clone().setPosition(0, 0, 0), q = new THREE.Quaternion(), p = new V3x(), sc = new V3x();
  L.decompose(p, q, sc); const e = new THREE.Euler().setFromQuaternion(q, "XYZ");
  return { t: [t.x, t.y, t.z], r: [deg(e.x), deg(e.y), deg(e.z)], s: [sc.x, sc.y, sc.z] };
}
const CHROWS = [["Translate X", "t", 0, 0.1], ["Translate Y", "t", 1, 0.1], ["Translate Z", "t", 2, 0.1], ["Rotate X", "r", 0, 0.5], ["Rotate Y", "r", 1, 0.5], ["Rotate Z", "r", 2, 0.5], ["Scale X", "s", 0, 0.01], ["Scale Y", "s", 1, 0.01], ["Scale Z", "s", 2, 0.01]];
const chBox = $("chbox"); let chFold = false; try { chFold = localStorage.getItem("meshlab:chfold") === "1"; } catch {}
function chTitle() { return mode === "o" ? (selO.size > 1 ? selO.size + " mesh" : (active && selO.size ? active.name : "")) : (active ? (mode === "v" ? selV.size + " điểm" : selF.size + " mặt") : ""); }
function chRender() {
  chBox.classList.toggle("fold", chFold);
  const v = chVals(), head = `<div class="chh" id="chh"><svg class="i" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg><b>Channel Box</b><span title="${esc(chTitle())}">${esc(chTitle())}</span></div>`;
  if (!v) { chBox.innerHTML = head + '<div class="chn">Chưa chọn gì.</div>'; return; }
  let h = head, last = "";
  for (const [lab, g, i, st] of CHROWS) {
    if (g !== last) { h += `<div class="chs">${g === "t" ? "Translate" : g === "r" ? "Rotate" : "Scale"}</div>`; last = g; }
    h += `<div class="chr"><label data-g="${g}" data-i="${i}" data-st="${st}" title="Kéo trái / phải để đổi giá trị">${lab.split(" ")[1]}</label><input type="number" data-g="${g}" data-i="${i}" step="${st}" value="${+v[g][i].toFixed(g === "s" ? 3 : 2)}"></div>`;
  }
  h += `<div class="chf"><button data-a="rst" title="Coi trạng thái hiện tại là gốc: Rotate về 0, Scale về 1">Đặt lại 0/1</button></div>`;
  chBox.innerHTML = h;
}
function chRefresh() {   // làm tươi số khi vùng chọn / gizmo đổi (không đụng ô đang gõ)
  const v = chVals(), ins = chBox.querySelectorAll("input[data-g]");
  if (!v || !ins.length || chBox.querySelector(".chn")) { chRender(); return; }
  ins.forEach(el => { if (document.activeElement !== el) el.value = +v[el.dataset.g][+el.dataset.i].toFixed(el.dataset.g === "s" ? 3 : 2); });
  const sp = chBox.querySelector(".chh span"); if (sp) { sp.textContent = chTitle(); sp.title = chTitle(); }
}
function chApply(vals, push) {   // vals = {t,r,s}: dựng ma trận tuyệt đối mới Anew rồi áp phần chênh lệch D = Anew · A⁻¹
  const T = ensureTS(); if (!T) return;
  const R = new M4x().makeRotationFromEuler(new THREE.Euler(rad(vals.r[0]), rad(vals.r[1]), rad(vals.r[2]), "XYZ")), S = new M4x().makeScale(...vals.s.map(x => Math.abs(x) < 1e-3 ? (x < 0 ? -1e-3 : 1e-3) : x));
  const tv = new V3x(...vals.t), Anew = new M4x().makeTranslation(tv.x, tv.y, tv.z).multiply(R).multiply(S).multiply(new M4x().makeTranslation(-T.c0.x, -T.c0.y, -T.c0.z));
  const D = Anew.clone().multiply(T.A.clone().invert());
  if (push) pushUndo();
  const aff = affSnapshot(); xformApply(D, aff); T.A = Anew;
  const os = new Set(aff.map(a => a.o)); os.forEach(o => { touchGeo(o, true); o.mirror = null; });
  refreshSelPositions(); placePivot(); chRefresh(); dirty = true; saveMsg = "Đang lưu…"; clearTimeout(saveT); saveT = setTimeout(save, 1500);
}
function chRead() { const v = { t: [0, 0, 0], r: [0, 0, 0], s: [1, 1, 1] }; chBox.querySelectorAll("input[data-g]").forEach(el => { const x = parseFloat(String(el.value).replace(",", ".")); v[el.dataset.g][+el.dataset.i] = isFinite(x) ? x : (el.dataset.g === "s" ? 1 : 0); }); return v; }
chBox.addEventListener("change", e => { if (e.target.matches("input[data-g]")) chApply(chRead(), true); });
chBox.addEventListener("keydown", e => { if (e.target.matches("input")) { e.stopPropagation(); if (e.key === "Enter") e.target.blur(); } });
chBox.addEventListener("click", e => {
  if (e.target.closest("#chh")) { chFold = !chFold; try { localStorage.setItem("meshlab:chfold", chFold ? "1" : "0"); } catch {} chRender(); return; }
  if (e.target.closest('[data-a="rst"]')) { const T = TS; TS = null; chRender(); }
});
let chDrag = null;   // kéo nhãn để đổi giá trị liên tục (như Maya)
chBox.addEventListener("pointerdown", e => {
  const l = e.target.closest("label[data-g]"); if (!l) return;
  const v = chVals(); if (!v) return; e.preventDefault(); l.setPointerCapture(e.pointerId); pushUndo();
  chDrag = { g: l.dataset.g, i: +l.dataset.i, st: +l.dataset.st, x0: e.clientX, v0: v[l.dataset.g][+l.dataset.i], base: v };
});
chBox.addEventListener("pointermove", e => {
  if (!chDrag) return; const d = chDrag, k = e.shiftKey ? 0.1 : e.ctrlKey ? 10 : 1, nv = JSON.parse(JSON.stringify(chVals()));
  nv[d.g][d.i] = d.v0 + (e.clientX - d.x0) * d.st * k; chApply(nv, false);
});
chBox.addEventListener("pointerup", () => { chDrag = null; });
chBox.addEventListener("pointercancel", () => { chDrag = null; });
// làm tươi theo vùng chọn: bọc refreshSel / restore
const _refreshSel = refreshSel; refreshSel = function () { if (TS && TS.sig !== selSig()) TS = null; const r = _refreshSel.apply(this, arguments); chRefresh(); return r; };
const _restore = restore; restore = function () { TS = null; return _restore.apply(this, arguments); };
const _setTopology = setTopology; setTopology = function () { TS = null; return _setTopology.apply(this, arguments); };
// gizmo: ghi lại phép cộng dồn
tc.addEventListener("mouseDown", () => { if (drag) { ensureTS(); drag.A0 = TS ? TS.A.clone() : new M4x(); } });
tc.addEventListener("objectChange", () => { if (drag && TS && drag.A0) { pivot.updateMatrixWorld(true); TS.A = pivot.matrixWorld.clone().multiply(drag.inv).multiply(drag.A0); chRefresh(); } });

// ---- Free Transform: hộp bao (AABB) của vùng chọn + tay nắm. Mặt = kéo giãn một trục (neo mặt đối diện), góc = scale đều (neo góc đối diện),
//      tâm = dời trong mặt phẳng camera. Shift = giãn đều cả 3 trục, Alt = neo ở tâm hộp.
const FREE = { group: new THREE.Group(), box: null, hs: [] }; FREE.group.visible = false; scene.add(FREE.group);
const FCOL = 0xff7a1a;
function selBox() {
  const b = new THREE.Box3(), v = new V3x();
  if (mode === "o") { selO.forEach(id => { const o = get(id); if (!o || !o.vis || o.lock) return; for (let i = 0; i < nV(o); i++) b.expandByPoint(v.set(o.pos[3 * i], o.pos[3 * i + 1], o.pos[3 * i + 2])); }); }
  else if (active) selV.forEach(i => b.expandByPoint(v.set(active.pos[3 * i], active.pos[3 * i + 1], active.pos[3 * i + 2])));
  if (b.isEmpty()) return null;
  ["x", "y", "z"].forEach(a => { if (b.max[a] - b.min[a] < 0.5) { const m = (b.max[a] + b.min[a]) / 2; b.min[a] = m - 0.25; b.max[a] = m + 0.25; } });
  return b;
}
function buildFree() {
  FREE.group.children.slice().forEach(c => { FREE.group.remove(c); if (c.geometry) c.geometry.dispose(); if (c.material) c.material.dispose(); }); FREE.hs = [];
  const b = tool === "free" ? selBox() : null; FREE.box = b; FREE.group.visible = !!b; if (!b) return;
  const c = b.getCenter(new V3x()), sz = b.getSize(new V3x());
  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(sz.x, sz.y, sz.z)), new THREE.LineBasicMaterial({ color: FCOL, depthTest: false, transparent: true, opacity: 0.9 })); edges.position.copy(c); edges.renderOrder = 28; edges.raycast = () => {}; FREE.group.add(edges);
  const mk = (geo, pos, data) => { const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: data.t === "center" ? 0x2f9bff : FCOL, depthTest: false, transparent: true })); m.position.copy(pos); m.renderOrder = 30; m.userData = data; FREE.group.add(m); FREE.hs.push(m); };
  const sph = new THREE.SphereGeometry(1, 10, 8), cube = new THREE.BoxGeometry(1.5, 1.5, 1.5);
  for (const x of [0, 1]) for (const y of [0, 1]) for (const z of [0, 1]) mk(sph, new V3x(x ? b.max.x : b.min.x, y ? b.max.y : b.min.y, z ? b.max.z : b.min.z), { t: "corner", sg: [x, y, z] });
  for (let ax = 0; ax < 3; ax++) for (const sg of [0, 1]) { const p = c.clone(); p.setComponent(ax, sg ? b.max.getComponent(ax) : b.min.getComponent(ax)); mk(cube, p, { t: "face", ax, sg }); }
  mk(sph, c, { t: "center" });
}
function freeScaleHandles() { const d = new V3x(); FREE.hs.forEach(h => { const k = cam.position.distanceTo(h.position) * 0.0032; h.scale.setScalar(Math.max(0.2, k)); }); }
const _frame = renderer.render.bind(renderer); renderer.render = function (sc, ca) { if (FREE.group.visible) freeScaleHandles(); return _frame(sc, ca); };
const _placePivot = placePivot; placePivot = function () { const r = _placePivot.apply(this, arguments); if (tool === "free") tc.detach(); buildFree(); return r; };
let fdrag = null;
function rayAt(e) { ray.setFromCamera(ndc(e.clientX, e.clientY), cam); return ray.ray; }
function closestOnAxis(r, O, D) {   // điểm trên đường thẳng (O, D) gần tia chuột nhất, trả tham số t
  const w0 = O.clone().sub(r.origin), a = D.dot(D), b = D.dot(r.direction), c = r.direction.dot(r.direction), d = D.dot(w0), e2 = r.direction.dot(w0), den = a * c - b * b;
  return Math.abs(den) < 1e-9 ? 0 : (b * e2 - c * d) / den;
}
function planeHit(r, P) { const n = cam.getWorldDirection(new V3x()); const pl = new THREE.Plane().setFromNormalAndCoplanarPoint(n, P); return r.intersectPlane(pl, new V3x()); }
cv.addEventListener("pointerdown", e => {
  if (tool !== "free" || !FREE.group.visible || e.button !== 0 || e.altKey && false) return;
  ray.setFromCamera(ndc(e.clientX, e.clientY), cam);
  const hit = ray.intersectObjects(FREE.hs, false)[0]; if (!hit) return;
  e.stopImmediatePropagation(); e.preventDefault(); down = null; boxing = false;
  const h = hit.object.userData, b = FREE.box.clone(), c = b.getCenter(new V3x());
  pushUndo(); ensureTS(); fdrag = { h, b, c, aff: affSnapshot(), A0: TS.A.clone(), start: e.clientX + "," + e.clientY }; orbit.enabled = false; cv.setPointerCapture(e.pointerId);
}, true);
function freeMove(e) {
  const d = fdrag; if (!d) return; const r = rayAt(e), h = d.h, b = d.b, c = d.c; let M = new M4x();
  const anchorAt = (ax, sg) => (e.altKey ? c.getComponent(ax) : (sg ? b.min.getComponent(ax) : b.max.getComponent(ax)));
  if (h.t === "face") {
    const ax = h.ax, hp = h.sg ? b.max.getComponent(ax) : b.min.getComponent(ax), an = anchorAt(ax, h.sg), O = c.clone(); O.setComponent(ax, hp);
    const D = new V3x(); D.setComponent(ax, 1); const t = closestOnAxis(r, O, D), np = hp + t, den = hp - an;
    if (Math.abs(den) < 1e-6) return; let sc = (np - an) / den; sc = Math.max(0.01, sc);
    const S = new V3x(1, 1, 1); if (e.shiftKey) S.set(sc, sc, sc); else S.setComponent(ax, sc);
    const pivotP = c.clone(); pivotP.setComponent(ax, an); if (e.shiftKey) pivotP.copy(e.altKey ? c : new V3x(...[0, 1, 2].map(k => k === ax ? an : (e.altKey ? c.getComponent(k) : c.getComponent(k)))));
    M = new M4x().makeTranslation(pivotP.x, pivotP.y, pivotP.z).multiply(new M4x().makeScale(S.x, S.y, S.z)).multiply(new M4x().makeTranslation(-pivotP.x, -pivotP.y, -pivotP.z));
  } else if (h.t === "corner") {
    const cp = new V3x(h.sg[0] ? b.max.x : b.min.x, h.sg[1] ? b.max.y : b.min.y, h.sg[2] ? b.max.z : b.min.z), an = e.altKey ? c.clone() : new V3x(h.sg[0] ? b.min.x : b.max.x, h.sg[1] ? b.min.y : b.max.y, h.sg[2] ? b.min.z : b.max.z);
    const P = planeHit(r, cp); if (!P) return; const dv = cp.clone().sub(an), den = dv.dot(dv); if (den < 1e-9) return;
    const sc = Math.max(0.01, P.clone().sub(an).dot(dv) / den);
    M = new M4x().makeTranslation(an.x, an.y, an.z).multiply(new M4x().makeScale(sc, sc, sc)).multiply(new M4x().makeTranslation(-an.x, -an.y, -an.z));
  } else {
    const P = planeHit(r, c); if (!P) return; const dl = P.sub(c); M = new M4x().makeTranslation(dl.x, dl.y, dl.z);
  }
  xformApply(M, d.aff); TS.A = M.clone().multiply(d.A0); refreshSelPositions(); buildFree(); chRefresh();
}
addEventListener("pointermove", e => { if (fdrag) freeMove(e); });
addEventListener("pointerup", () => { if (!fdrag) return; const aff = fdrag.aff; fdrag = null; orbit.enabled = true; xformEnd(aff); });
"""

rep("</style>", CSS + "</style>")
rep('    <div class="vinfo" id="vinfo"></div>\n', '    <div class="vinfo" id="vinfo"></div>\n' + HTML)
# icon + toolbar + shortcut
rep("  all: '<path d=\"M5 12.500l4.500 4.500L19 7\"/>',", "  free: '<rect x=\"6\" y=\"6\" width=\"12\" height=\"12\" stroke-dasharray=\"2 2\"/><rect x=\"3\" y=\"3\" width=\"4\" height=\"4\"/><rect x=\"17\" y=\"3\" width=\"4\" height=\"4\"/><rect x=\"3\" y=\"17\" width=\"4\" height=\"4\"/><rect x=\"17\" y=\"17\" width=\"4\" height=\"4\"/>',\n  all: '<path d=\"M5 12.500l4.500 4.500L19 7\"/>',")
rep('${B("t:scl", "scl", "Scale (R)", tool === "scl")}', '${B("t:scl", "scl", "Scale (R)", tool === "scl")}${B("t:free", "free", "Free Transform: hộp bao, kéo mặt / góc để giãn (T)", tool === "free")}')
rep('else if (k === "r") { tool = "scl"; placePivot(); renderToolbar(); }', 'else if (k === "r") { tool = "scl"; placePivot(); renderToolbar(); } else if (k === "t") { tool = "free"; placePivot(); renderToolbar(); }')
# chbox first render at init
rep("loadMeshes(src); resize(); renderToolbar(); renderPanel(); refreshSel(); frameAll();", "loadMeshes(src); resize(); renderToolbar(); renderPanel(); refreshSel(); chRender(); frameAll();")
k = s.rfind("</script>")
s = s[:k] + JS + s[k:]
open(P, "w", encoding="utf8", newline="").write(s)
print("ok")
