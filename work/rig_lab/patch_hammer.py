# Hammer skin (như Maya "Hammer Skin Weights"): thay trọng số của đỉnh bằng trung bình (cotan) của đỉnh lân cận để phá các mảng nhọn/cánh gãy.
# - Cọ kiểu "Hammer"; nút "Hammer pose hiện tại" (đỉnh căng > 25% + 1 vòng lân cận); nút "Hammer tự động" (lặp bộ pose tới khi hết đỉnh căng, tối đa 4 vòng).
import os
R = os.path.dirname(os.path.abspath(__file__)); p = f"{R}/template.html"; s = open(p, encoding="utf8").read()
assert "hammerVerts" not in s
def sub(old, new):
    global s
    assert s.count(old) == 1, old[:70]; s = s.replace(old, new)

sub("function dab(i, j, a, mode) {", '''// ---- Hammer: trọng số đỉnh := (1-m)·cũ + m·trung bình cotan của lân cận (đỉnh ngoài tập đóng vai neo)
function hammerVerts(ids, iters, mixOf) {
  for (let it = 0; it < iters; it++) {
    const out = new Map();
    for (const i of ids) {
      const v = new Float64Array(SK.nb); let sw = 0;
      for (let e = LAP.start[i]; e < LAP.start[i + 1]; e++) { const w = LAP.nw[e], nb = LAP.nb[e]; sw += w; for (let j = 0; j < SK.nb; j++) v[j] += w * SK.full[j * NV + nb]; }
      if (!sw) continue;
      const cur = getVec(i), m = Math.max(0, Math.min(1, mixOf(i)));
      for (let j = 0; j < SK.nb; j++) v[j] = (1 - m) * cur[j] + m * v[j] / sw;
      out.set(i, v);
    }
    out.forEach((v, i) => setVec(i, v));
  }
}
const snap4 = i => [Array.from(SK.I.slice(i * 4, i * 4 + 4)), Array.from(SK.W.slice(i * 4, i * 4 + 4))];
function strainedSet(thr) {   // đỉnh căng > thr ở pose hiện tại + 1 vòng lân cận
  poseSkin(); const set = new Set();
  for (let i = 0; i < NV; i++) if (STR[i] > thr) { set.add(i); for (let e = LAP.start[i]; e < LAP.start[i + 1]; e++) set.add(LAP.nb[e]); }
  return set;
}
function hammerFinish(snap, msg) {
  skinUndo.push(snap); if (skinUndo.length > 60) skinUndo.shift(); skinRedo = [];
  saveMsg = msg; scheduleSkinSave(); scheduleSelfTest(); applyPose(); paintSkin(); renderPanel();
}
function hammerCurrent() {
  if (!SK) return; const set = strainedSet(0.25), n0 = strainSummary().pct;
  if (!set.size) { saveMsg = "Pose hiện tại không có đỉnh căng quá 25%: chọn pose có lỗi rồi Hammer."; return renderPanelLight(); }
  const snap = new Map(); set.forEach(i => snap.set(i, snap4(i)));
  hammerVerts([...set], 3, () => 0.8); poseSkin();
  hammerFinish(snap, `Hammer pose hiện tại: ${set.size} đỉnh, căng quá 25% ${fix(n0)}% → ${fix(strainSummary().pct)}%.`);
}
function hammerAuto() {
  if (!SK) return; const keep = JSON.stringify(POSE), kt = poseOpt.twist; poseOpt.twist = true;
  const snap = new Map(), pct = () => { let w = 0; for (const p of Object.values(PRESETS)) { for (const k in POSE) delete POSE[k]; for (const k in p) POSE[k] = p[k].slice(); poseSkin(); w = Math.max(w, strainSummary().pct); } return w; };
  const before = pct(); let rounds = 0, touched = new Set();
  for (; rounds < 4; rounds++) {
    const union = new Set();
    for (const p of Object.values(PRESETS)) { for (const k in POSE) delete POSE[k]; for (const k in p) POSE[k] = p[k].slice(); strainedSet(0.25).forEach(i => union.add(i)); }
    if (!union.size) break;
    union.forEach(i => { if (!snap.has(i)) snap.set(i, snap4(i)); touched.add(i); });
    hammerVerts([...union], 2, () => 0.7);
  }
  const after = pct();
  for (const k in POSE) delete POSE[k]; Object.assign(POSE, JSON.parse(keep)); poseOpt.twist = kt; poseSkin();
  if (!snap.size) { saveMsg = "Hammer tự động: không có đỉnh căng quá 25% ở bộ pose."; return renderPanelLight(); }
  hammerFinish(snap, `Hammer tự động: ${rounds} vòng, ${touched.size} đỉnh; căng quá 25% (pose xấu nhất) ${fix(before)}% → ${fix(after)}%.`);
}
const hammerHtml = () => `<div class="row"><button id="hammerNow" title="Làm phẳng trọng số quanh đỉnh đang căng quá 25% ở pose hiện tại">Hammer pose hiện tại</button><button id="hammerAuto" title="Lặp bộ pose, hammer các đỉnh căng tới khi hết (tối đa 4 vòng)">Hammer tự động</button></div>`;
const wireHammer = () => { const a = $("hammerNow"), b = $("hammerAuto"); if (a) a.onclick = hammerCurrent; if (b) b.onclick = hammerAuto; };
function dab(i, j, a, mode) {''')

# cọ Hammer
sub("  const PP = skinGeo.attributes.position.array, j = SK.idx[skinBone], jm = SK.idx[mirName(skinBone)], mi = brush.mirror && jm !== undefined && mirName(skinBone) !== skinBone ? getMirror() : null;\n  for (let i = 0; i < NV; i++) {",
    '''  const PP = skinGeo.attributes.position.array, j = SK.idx[skinBone], jm = SK.idx[mirName(skinBone)], mi = brush.mirror && jm !== undefined && mirName(skinBone) !== skinBone ? getMirror() : null;
  if (brush.mode === "hammer") {   // không phụ thuộc xương đang chọn
    const mx = new Map(), M2 = brush.mirror ? getMirror() : null;
    for (let i = 0; i < NV; i++) { const d = Math.hypot(PP[3 * i] - pt.x, PP[3 * i + 1] - pt.y, PP[3 * i + 2] - pt.z); if (d > brush.r) continue; const m = Math.min(1, brush.str * (1 - (d / brush.r) ** 2) ** 2 * 1.6);
      mx.set(i, Math.max(mx.get(i) || 0, m)); if (M2) mx.set(M2[i], Math.max(mx.get(M2[i]) || 0, m)); }
    mx.forEach((_, i) => { if (!stroke.has(i)) stroke.set(i, snap4(i)); });
    hammerVerts([...mx.keys()], 1, i => mx.get(i)); paintSkin(); dirtySkin = true; return;
  }
  if (!SK || j === undefined) return;
  for (let i = 0; i < NV; i++) {''')
sub("  if (!SK || !skinBone || SK.idx[skinBone] === undefined) return;\n  const pt = brushHit(e); if (!pt) return;", "  if (!SK || (brush.mode !== \"hammer\" && (!skinBone || SK.idx[skinBone] === undefined))) return;\n  const pt = brushHit(e); if (!pt) return;")
sub('<option value="smooth" ${brush.mode === "smooth" ? "selected" : ""}>Làm mượt</option></select>', '<option value="smooth" ${brush.mode === "smooth" ? "selected" : ""}>Làm mượt</option><option value="hammer" ${brush.mode === "hammer" ? "selected" : ""}>Hammer (phá mảng nhọn)</option></select>')

# nút trong panel
sub("    ${testHtml()}\n    <div class=\"row\">${tools}</div>", "    ${testHtml()}\n    <div class=\"row\">${tools}</div>\n    ${hammerHtml()}")
sub("  wirePoseSection();\n}\nasync function exportWeights()", "  wirePoseSection(); wireHammer();\n}\nasync function exportWeights()")
sub('    ${sm && sm.worst.length && pct > 1 ? `<div class="sub">Vùng xấu: ${sm.worst.map(w => w[0]).join(", ")}</div>` : ""}', '    ${sm && sm.worst.length && pct > 1 ? `<div class="sub">Vùng xấu: ${sm.worst.map(w => w[0]).join(", ")}</div>` : ""}\n    ${hammerHtml()}')
sub("  on(\"pBat\", () => { battery = batteryRun(); OPEN.m5bat = true; renderPanel(); });\n}", "  on(\"pBat\", () => { battery = batteryRun(); OPEN.m5bat = true; renderPanel(); });\n  wireHammer();\n}")
open(p, "w", encoding="utf8").write(s); print("ok")
