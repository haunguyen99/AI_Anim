# Một lần: chọn joint trực tiếp trong viewport (bước 4, 5), cọ tô trọng số, lưu skin vào db
p = "template.html"
s = open(p, encoding="utf8").read()


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


NEW = r'''
// ================================================================ M3 sớm: chọn joint trong viewport + cọ tô skin
let skTool = "pick", brush = { mode: "add", r: 10, str: 0.35, mirror: true };
let skinUndo = [], skinRedo = [], stroke = null, painting = false, pickDown = null, lastDab = 0, mirrorIdx = null;
const selPt = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 13, sizeAttenuation: false, depthTest: false, color: 0xffffff }));
selPt.renderOrder = 12; selPt.visible = false; scene.add(selPt);
const ring = new THREE.Mesh(new THREE.SphereGeometry(1, 20, 14), new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: true, transparent: true, opacity: .45, depthTest: false }));
ring.visible = false; ring.renderOrder = 11; scene.add(ring);

function denseFrom(I, W, nb) { const f = new Float32Array(nb * NV); for (let i = 0; i < NV; i++) for (let k = 0; k < 4; k++) if (W[i * 4 + k] > 0) f[I[i * 4 + k] * NV + i] = W[i * 4 + k]; return f; }
function updateSelPt() {
  const name = step === 4 ? skinBone : step === 5 ? poseBone : null;
  if (!name || step < 4) { selPt.visible = false; return; }
  const B = buildSkeleton(LM), b = B.find(x => x.name === name); if (!b) { selPt.visible = false; return; }
  const pos = step === 5 && SK ? posedBones(B)[name] : b.pos;
  selPt.geometry.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); selPt.material.color.set(css("--accent")); selPt.visible = true;
}
// ---- phép tô trên ma trận dày SK.full
function getVec(i) { const v = new Float64Array(SK.nb); for (let j = 0; j < SK.nb; j++) v[j] = SK.full[j * NV + i]; return v; }
function setVec(i, v) {
  const idx = [...v.keys()].sort((a, b) => v[b] - v[a]).slice(0, 4).filter(j => v[j] > 0.005), s = idx.reduce((q, j) => q + v[j], 0) || 1;
  for (let j = 0; j < SK.nb; j++) SK.full[j * NV + i] = 0;
  for (let k = 0; k < 4; k++) { if (k < idx.length) { const j = idx[k]; SK.I[i * 4 + k] = j; SK.W[i * 4 + k] = v[j] / s; SK.full[j * NV + i] = v[j] / s; } else { SK.I[i * 4 + k] = 0; SK.W[i * 4 + k] = 0; } }
}
function dab(i, j, a, mode) {
  const v = getVec(i), wj = v[j]; let nw;
  if (mode === "add") nw = Math.min(1, wj + a);
  else if (mode === "sub") nw = Math.max(0, wj - a);
  else { let sw = 0, sx = 0; for (let e = LAP.start[i]; e < LAP.start[i + 1]; e++) { sw += LAP.nw[e]; sx += LAP.nw[e] * SK.full[j * NV + LAP.nb[e]]; } nw = wj + (sx / (sw || 1) - wj) * Math.min(1, a * 2); }
  let so = 0; for (let k = 0; k < v.length; k++) if (k !== j) so += v[k];
  if (so > 1e-9) { const f = (1 - nw) / so; for (let k = 0; k < v.length; k++) if (k !== j) v[k] *= f; v[j] = nw; } else v[j] = mode === "sub" ? wj : 1;
  setVec(i, v);
}
const mirName = n => n.endsWith("_R") ? n.slice(0, -1) + "L" : n.endsWith("_L") ? n.slice(0, -1) + "R" : n;
function getMirror() {
  if (mirrorIdx) return mirrorIdx; mirrorIdx = new Int32Array(NV);
  for (let i = 0; i < NV; i++) { let best = 1e9, bj = i; const a = bodyV[i]; for (let j = 0; j < NV; j++) { const b = bodyV[j], d = (a[0] + b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2; if (d < best) { best = d; bj = j; } } mirrorIdx[i] = bj; }
  return mirrorIdx;
}
function brushHit(e) {
  const r = cv.getBoundingClientRect();
  ray.setFromCamera({ x: ((e.clientX - r.left) / r.width) * 2 - 1, y: -((e.clientY - r.top) / r.height) * 2 + 1 }, cam);
  const h = ray.intersectObject(skinMesh, false)[0]; return h ? h.point : null;
}
function paintAt(e) {
  if (!SK || !skinBone || SK.idx[skinBone] === undefined) return;
  const pt = brushHit(e); if (!pt) return;
  const j = SK.idx[skinBone], jm = SK.idx[mirName(skinBone)], mi = brush.mirror && jm !== undefined && mirName(skinBone) !== skinBone ? getMirror() : null;
  for (let i = 0; i < NV; i++) {
    const d = Math.hypot(bodyV[i][0] - pt.x, bodyV[i][1] - pt.y, bodyV[i][2] - pt.z); if (d > brush.r) continue;
    const f = (1 - (d / brush.r) ** 2) ** 2, a = brush.str * f * 0.5;
    const touch = (vi, bj) => { if (!stroke.has(vi)) stroke.set(vi, [Array.from(SK.I.slice(vi * 4, vi * 4 + 4)), Array.from(SK.W.slice(vi * 4, vi * 4 + 4))]); dab(vi, bj, a, brush.mode); };
    touch(i, j); if (mi) touch(mi[i], jm);
  }
  paintSkin(); dirtySkin = true;
}
let dirtySkin = false;
function skinSnapshotOf(map) { const o = new Map(); map.forEach((_, i) => o.set(i, [Array.from(SK.I.slice(i * 4, i * 4 + 4)), Array.from(SK.W.slice(i * 4, i * 4 + 4))])); return o; }
function restoreSkin(map) { map.forEach(([I4, W4], i) => { for (let k = 0; k < 4; k++) { SK.I[i * 4 + k] = I4[k]; SK.W[i * 4 + k] = W4[k]; } for (let j = 0; j < SK.nb; j++) SK.full[j * NV + i] = 0; for (let k = 0; k < 4; k++) if (W4[k] > 0) SK.full[I4[k] * NV + i] = W4[k]; }); paintSkin(); }
function skinUndoStep() { const m = skinUndo.pop(); if (!m) return; skinRedo.push(skinSnapshotOf(m)); restoreSkin(m); renderPanelLight(); }
function skinRedoStep() { const m = skinRedo.pop(); if (!m) return; skinUndo.push(skinSnapshotOf(m)); restoreSkin(m); }

// ---- chọn joint trực tiếp
function pickJoint(e) {
  const r = cv.getBoundingClientRect(), B = buildSkeleton(LM), PB = step === 5 && SK ? posedBones(B) : null;
  let best = 16, name = null;
  for (const b of B) {
    if (b.name === "root" || b.name === "Weapon" || (step === 4 && (!SK || SK.idx[b.name] === undefined))) continue;
    if (step === 5 && b.twist) continue;
    const pp = PB ? PB[b.name] : b.pos, v = new THREE.Vector3(...pp).project(cam), px = r.left + (v.x + 1) / 2 * r.width, py = r.top + (1 - v.y) / 2 * r.height, d = Math.hypot(px - e.clientX, py - e.clientY);
    if (d < best) { best = d; name = b.name; }
  }
  if (!name) return;
  if (step === 4) { skinBone = name; if (skinView === "dom") skinView = "one"; paintSkin(); } else poseBone = name;
  syncScene(); renderPanel();
}
cv.addEventListener("pointerdown", e => {
  if (step < 4 || e.pointerType !== "mouse" || e.button !== 0 || e.altKey) return;
  if (step === 4 && skTool === "brush" && SK) { painting = true; stroke = new Map(); paintAt(e); lastDab = performance.now(); }
  else pickDown = [e.clientX, e.clientY];
});
cv.addEventListener("pointermove", e => {
  if (step === 4 && skTool === "brush" && SK && !e.altKey) { const pt = brushHit(e); ring.visible = !!pt; if (pt) { ring.position.copy(pt); ring.scale.setScalar(brush.r); } } else ring.visible = false;
  if (painting && performance.now() - lastDab > 30) { paintAt(e); lastDab = performance.now(); }
});
window.addEventListener("pointerup", e => {
  if (painting) { painting = false; const m = new Map(); stroke.forEach((v, i) => m.set(i, v)); if (m.size) { skinUndo.push(m); if (skinUndo.length > 60) skinUndo.shift(); skinRedo = []; saveMsg = "Skin có thay đổi chưa lưu."; renderPanelLight(); } stroke = null; return; }
  if (pickDown) { const d = pickDown; pickDown = null; if (Math.hypot(e.clientX - d[0], e.clientY - d[1]) < 4 && e.target === cv) pickJoint(e); }
});
async function saveSkin() {
  if (!SK) return;
  const doc = { names: SK.names, I: Array.from(SK.I), W: Array.from(SK.W, v => +v.toFixed(3)), sig: SK.LMsnap, nv: NV, at: Date.now() };
  try {
    if (db) await db.doc("rig/skin").set(doc); else localStorage.setItem("rig_skin", JSON.stringify(doc));
    dirtySkin = false; saveMsg = "Đã lưu skin" + (db ? "." : " (chỉ trong trình duyệt này).");
  } catch (e) { saveMsg = "Không lưu được skin: " + (e.message || e.code || e); }
  renderPanelLight();
}
function loadSkinDoc(d) {
  if (!d || !d.names || d.nv !== NV) return;
  const nb = d.names.length, I = Uint16Array.from(d.I), W = Float32Array.from(d.W);
  SK = { names: d.names, idx: Object.fromEntries(d.names.map((n, i) => [n, i])), I, W, nb, full: denseFrom(I, W, nb), LMsnap: d.sig };
  skinBone = skinBone || d.names[0]; skinMs = 0;
}
'''
rep('renderVbar(); resize(); setView("front")', NEW + '\nrenderVbar(); resize(); setView("front")')
# panel
rep("      <h2>Lệch nhiều nhất (theo xương khách)</h2>", '''      <h2>Công cụ</h2>
      <div class="row"><button data-skt="pick" ${skTool === "pick" ? 'class="pri"' : ""}>Chọn joint (Q)</button><button data-skt="brush" ${skTool === "brush" ? 'class="pri"' : ""}>Cọ tô (B)</button></div>
      <div class="sub">Click một joint trên viewport để xem và chỉnh skin của nó. Joint đang chọn: <b>${skinBone || "chưa có"}</b>.</div>
      ${skTool === "brush" ? `<div class="row"><select id="brMode"><option value="add" ${brush.mode === "add" ? "selected" : ""}>Cộng trọng số</option><option value="sub" ${brush.mode === "sub" ? "selected" : ""}>Trừ trọng số</option><option value="smooth" ${brush.mode === "smooth" ? "selected" : ""}>Làm mượt</option></select>
        <label class="t"><input type="checkbox" id="brMir" ${brush.mirror ? "checked" : ""}> Đối xứng</label></div>
        <div class="row" style="flex-wrap:nowrap"><label for="brR" style="width:90px;font-size:12px">Bán kính</label><input id="brR" type="range" min="2" max="40" step="1" value="${brush.r}" style="flex:1"><span id="brRv" class="sub" style="width:44px;text-align:right">${brush.r} cm</span></div>
        <div class="row" style="flex-wrap:nowrap"><label for="brS" style="width:90px;font-size:12px">Cường độ</label><input id="brS" type="range" min="0.05" max="1" step="0.05" value="${brush.str}" style="flex:1"><span id="brSv" class="sub" style="width:44px;text-align:right">${brush.str}</span></div>
        <div class="sub">Giữ chuột trái và kéo trên mesh. Ctrl+Z hoàn tác từng nét. Alt+chuột vẫn xoay, kéo, zoom.</div>` : ""}
      <h2>Lệch nhiều nhất (theo xương khách)</h2>''')
rep('on("skPrev", () => step1(-1)); on("skNext", () => step1(1));', '''on("skPrev", () => step1(-1)); on("skNext", () => step1(1));
  document.querySelectorAll("[data-skt]").forEach(b => b.addEventListener("click", () => setSkTool(b.dataset.skt)));
  const bm = $("brMode"); if (bm) bm.onchange = () => brush.mode = bm.value;
  const bx = $("brMir"); if (bx) bx.onchange = () => brush.mirror = bx.checked;
  const br = $("brR"); if (br) br.oninput = () => { brush.r = +br.value; $("brRv").textContent = brush.r + " cm"; };
  const bs = $("brS"); if (bs) bs.oninput = () => { brush.str = +bs.value; $("brSv").textContent = brush.str; };
  on("saveSkin", saveSkin);''')
rep('<button id="expW">Xuất weights.json</button>', '<button class="pri" id="saveSkin">Lưu skin</button><button id="expW">Xuất weights.json</button>')
rep("function boneList() {", '''function setSkTool(t) { skTool = t; if (t === "brush" && skinView === "dom") skinView = "one"; if (t !== "brush") ring.visible = false; paintSkin(); renderPanel(); }
function boneList() {''')
# tính skin: ma trận dày đã chuẩn hóa
rep("I, W, full: Wt, nb,", "I, W, full: null, nb,")
rep("skinStale = false; skinBusy = false; skinMs", "SK.full = denseFrom(I, W, nb); skinUndo = []; skinRedo = []; skinStale = false; skinBusy = false; skinMs")
# undo / redo ở bước 4
rep("function undo() { if (!undoS.length) return;", "function undo() { if (step === 4 && skinUndo.length) return skinUndoStep(); if (!undoS.length) return;")
rep("function redo() { if (!redoS.length) return;", "function redo() { if (step === 4 && skinRedo.length) return skinRedoStep(); if (!redoS.length) return;")
# phím Q / B ở bước 4
rep('  if (k === "a") frameView(null);\n  if (step !== 2) return;', '  if (k === "a") frameView(null);\n  if (step === 4) { if (k === "q") setSkTool("pick"); if (k === "b") setSkTool("brush"); }\n  if (step !== 2) return;')
# tải skin khi mở trang
rep("      saveMsg = \"Đã nối db: lưu cho AI đọc được.\";", "      saveMsg = \"Đã nối db: lưu cho AI đọc được.\";\n      const sk = await db.doc(\"rig/skin\").get(); if (sk.exists) loadSkinDoc(sk.data());")
rep('const t = localStorage.getItem("rig_tw");', 'try { const k = localStorage.getItem("rig_skin"); if (k) loadSkinDoc(JSON.parse(k)); } catch (e) {} const t = localStorage.getItem("rig_tw");')
# đồng bộ điểm chọn
rep("  refLines.material.color.set(css(\"--ref\")); refLines.visible = showRef;", "  refLines.material.color.set(css(\"--ref\")); refLines.visible = showRef; if (typeof updateSelPt === \"function\") updateSelPt();")
open(p, "w", encoding="utf8").write(s)
