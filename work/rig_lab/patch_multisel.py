# Một lần: thêm chọn nhiều khớp (Shift/Ctrl+click, Shift+kéo khung, nhóm nhanh, dời/xoay/co giãn nhóm) vào template.html
p = "template.html"
s = open(p, encoding="utf8").read()


def rep(a, b):
    global s
    assert a in s, a[:60]
    s = s.replace(a, b, 1)


rep("let step = 1, sel = null,", "const S = new Set();\nlet step = 1, sel = null,")
a = s.index("const tc = new THREE.TransformControls")
b = s.index("function setView")
s = s[:a] + r'''const tc = new THREE.TransformControls(cam, cv); tc.setSize(0.8); scene.add(tc);
const pivot = new THREE.Object3D(); scene.add(pivot);
let start = null, startM = new THREE.Matrix4();
function centroid() { const c = new THREE.Vector3(); S.forEach(k => c.add(new THREE.Vector3(...LM[k]))); return c.multiplyScalar(1 / Math.max(S.size, 1)); }
function resetPivot() { pivot.position.copy(centroid()); pivot.quaternion.identity(); pivot.scale.set(1, 1, 1); pivot.updateMatrix(); }
tc.addEventListener("dragging-changed", e => {
  orbit.enabled = !e.value;
  if (e.value) { pivot.updateMatrix(); startM.copy(pivot.matrix).invert(); start = {}; S.forEach(k => start[k] = new THREE.Vector3(...LM[k])); }
  else { start = null; resetPivot(); }
});
tc.addEventListener("objectChange", () => {
  if (!start) return;
  pivot.updateMatrix(); const M = pivot.matrix.clone().multiply(startM);
  for (const k in start) { const v = start[k].clone().applyMatrix4(M); LM[k] = [v.x, v.y, v.z]; }
  if (mirror) {
    for (const k of S) {
      const m = mirrorKey(k);
      if (!m) { LM[k][0] = 0; continue; }
      if (sideOf(k) === "R" || !S.has(m)) LM[m] = [-LM[k][0], LM[k][1], LM[k][2]];
    }
  }
  syncScene(true); dirty();
});

''' + s[b:]
rep("    m.scale.setScalar(k === sel ? 1.5 : 1);", "    m.scale.setScalar(S.has(k) ? 1.5 : 1);")
rep("    if (isFinger(k)) m.scale.setScalar(k === sel ? 1.2 : 0.6);",
    '    if (isFinger(k)) m.scale.setScalar(S.has(k) ? 1.2 : 0.6);\n    m.material.color.set(S.has(k) ? css("--accent") : lmColor(k));')
rep("function syncScene() {", "function syncScene(dragging) {")
rep("  if (sel && step === 2) tc.attach(lmMesh[sel]); else tc.detach();",
    "  if (S.size && step === 2) { if (!dragging) resetPivot(); tc.attach(pivot); } else tc.detach();")
rep("function pick(k) { sel = k; syncScene(); renderPanelLight(); }", r'''function pick(k, add) {
  if (add) { if (S.has(k)) { S.delete(k); if (sel === k) sel = [...S].pop() || null; } else { S.add(k); sel = k; } }
  else { S.clear(); if (k) S.add(k); sel = k; }
  syncScene(); renderPanelLight();
}
function setSel(keys, add) { if (!add) S.clear(); keys.forEach(k => S.add(k)); sel = keys.length ? keys[keys.length - 1] : (S.size ? [...S].pop() : null); syncScene(); renderPanelLight(); }
const GROUPS = {
  fingR: () => LM_ORDER.filter(k => isFinger(k) && k.endsWith("_R")), fingL: () => LM_ORDER.filter(k => isFinger(k) && k.endsWith("_L")),
  armR: () => LM_ORDER.filter(k => /^(Scapula|Shoulder|Elbow|Wrist)_R$/.test(k) || (isFinger(k) && k.endsWith("_R"))),
  armL: () => LM_ORDER.filter(k => /^(Scapula|Shoulder|Elbow|Wrist)_L$/.test(k) || (isFinger(k) && k.endsWith("_L"))),
  legR: () => LM_ORDER.filter(k => /^(Hip|Knee|Ankle|Toes|ToesEnd)_R$/.test(k)), legL: () => LM_ORDER.filter(k => /^(Hip|Knee|Ankle|Toes|ToesEnd)_L$/.test(k)),
  spine: () => CENTER.slice(0, 6), all: () => LM_ORDER.filter(k => showFing || !isFinger(k)) };''')
a = s.index("// chọn khớp bằng click")
b = s.index("// ---------------------------------------------------------------- lưu")
s = s[:a] + r'''// chọn khớp: click, Shift/Ctrl+click thêm hoặc bỏ, Shift+kéo khung để chọn nhiều
const ray = new THREE.Raycaster(); let down = null, boxing = false;
const boxEl = document.createElement("div");
boxEl.style.cssText = "position:absolute;border:1px dashed var(--accent);background:color-mix(in srgb,var(--accent) 14%,transparent);display:none;pointer-events:none";
vp.appendChild(boxEl);
cv.addEventListener("pointerdown", e => {
  down = [e.clientX, e.clientY]; boxing = false;
  if (step === 2 && e.shiftKey && !tc.dragging) { boxing = true; orbit.enabled = false; }
}, true);
cv.addEventListener("pointermove", e => {
  if (!boxing || !down) return;
  const r = vp.getBoundingClientRect(), x0 = down[0] - r.left, y0 = down[1] - r.top, x1 = e.clientX - r.left, y1 = e.clientY - r.top;
  Object.assign(boxEl.style, { display: "block", left: Math.min(x0, x1) + "px", top: Math.min(y0, y1) + "px", width: Math.abs(x1 - x0) + "px", height: Math.abs(y1 - y0) + "px" });
});
window.addEventListener("pointerup", e => {
  if (!down) return;
  const moved = Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 4, was = boxing, d0 = down;
  down = null; boxing = false; boxEl.style.display = "none"; if (was) orbit.enabled = true;
  if (step !== 2 || (e.target !== cv && !was)) return;
  const r = cv.getBoundingClientRect();
  if (was && moved) {
    const xa = Math.min(d0[0], e.clientX), xb = Math.max(d0[0], e.clientX), ya = Math.min(d0[1], e.clientY), yb = Math.max(d0[1], e.clientY), hit = [];
    for (const k of LM_ORDER) {
      const m = lmMesh[k]; if (!m.visible) continue;
      const v = m.position.clone().project(cam), px = r.left + (v.x + 1) / 2 * r.width, py = r.top + (1 - v.y) / 2 * r.height;
      if (px >= xa && px <= xb && py >= ya && py <= yb) hit.push(k);
    }
    setSel(hit, true); return;
  }
  if (moved) return;
  ray.setFromCamera({ x: ((e.clientX - r.left) / r.width) * 2 - 1, y: -((e.clientY - r.top) / r.height) * 2 + 1 }, cam);
  const h = ray.intersectObjects(Object.values(lmMesh).filter(m => m.visible), false)[0];
  if (h) pick(h.object.userData.key, e.shiftKey || e.ctrlKey || e.metaKey);
  else if (!(e.shiftKey || e.ctrlKey || e.metaKey) && !tc.dragging) pick(null);
});

''' + s[b:]
rep('<tr class="pick ${k === sel ? "sel" : ""}"', '<tr class="pick ${S.has(k) ? "sel" : ""}"')
rep('tr.classList.toggle("sel", tr.dataset.k === sel);', 'tr.classList.toggle("sel", S.has(tr.dataset.k));')
rep('document.querySelectorAll("#lmrows tr").forEach(tr => tr.addEventListener("click", () => pick(tr.dataset.k)));',
    'document.querySelectorAll("#lmrows tr").forEach(tr => tr.addEventListener("click", e => pick(tr.dataset.k, e.shiftKey || e.ctrlKey || e.metaKey)));')
a = s.index("function renderSel()")
b = s.index("function renderPanelLight")
s = s[:a] + r'''let mode = "translate";
function setMode(m) { mode = m; tc.setMode(m); renderSel(); }
function renderSel() {
  const b = $("selbox"); if (!b) return;
  const modes = `<div class="row">${[["translate", "Dời (W)"], ["rotate", "Xoay (E)"], ["scale", "Co giãn (R)"]].map(([m, t]) => `<button data-mode="${m}" ${mode === m ? 'class="pri"' : ""}>${t}</button>`).join("")}</div>`;
  const grp = `<div class="row">${[["armR", "Tay R"], ["armL", "Tay L"], ["fingR", "Ngón R"], ["fingL", "Ngón L"], ["legR", "Chân R"], ["legL", "Chân L"], ["spine", "Thân"], ["all", "Tất cả"]].map(([g, t]) => `<button data-g="${g}">${t}</button>`).join("")}<button id="clr">Bỏ chọn</button></div>`;
  let body;
  if (!S.size) body = '<div class="msg">Chưa chọn khớp nào. Click một chấm; Shift/Ctrl+click để thêm; Shift+kéo khung để chọn nhiều.</div>';
  else if (S.size > 1) body = `<div class="msg">Đã chọn ${S.size} khớp. Kéo mũi tên, vòng xoay hoặc ô vuông để dời, xoay, co giãn cả nhóm quanh tâm nhóm.</div>`;
  else body = `<h2>${sel}${LM_LABEL[sel.replace(/_[RL]$/, "")] ? " · " + LM_LABEL[sel.replace(/_[RL]$/, "")] : ""}</h2><div class="num">${["x", "y", "z"].map((a, i) => `<div><label for="n${a}">${a} (cm)</label><input id="n${a}" type="number" step="0.5" value="${fix(LM[sel][i], 2)}"></div>`).join("")}</div>`;
  b.innerHTML = grp + modes + body;
  $("clr").addEventListener("click", () => pick(null));
  b.querySelectorAll("[data-g]").forEach(x => x.addEventListener("click", e => setSel(GROUPS[x.dataset.g](), e.shiftKey)));
  b.querySelectorAll("[data-mode]").forEach(x => x.addEventListener("click", () => setMode(x.dataset.mode)));
  if (S.size === 1) ["x", "y", "z"].forEach((a, i) => $("n" + a).addEventListener("change", e => {
    LM[sel][i] = +e.target.value; if (mirror && mirrorKey(sel)) { const k = mirrorKey(sel); LM[k] = [-LM[sel][0], LM[sel][1], LM[sel][2]]; }
    syncScene(); dirty(); renderPanel();
  }));
}
''' + s[b:]
rep("if (n !== 2) sel = null;", "if (n !== 2) { sel = null; S.clear(); }")
rep("if (!showFing && sel && isFinger(sel)) sel = null;", "if (!showFing) { [...S].filter(isFinger).forEach(k => S.delete(k)); sel = [...S].pop() || null; }")
rep('  if (e.key === "w") tc.setMode("translate");',
    '  if (e.key === "w") setMode("translate"); if (e.key === "e") setMode("rotate"); if (e.key === "r") setMode("scale"); if (e.key === "Escape") pick(null);')
rep("if (step !== 2 || !sel ||", "if (step !== 2 ||")
open(p, "w", encoding="utf8").write(s)
