"""Sinh tools/studio/modules/rig_engine.js từ phần lõi Rig Lab (work/rig_lab/template.html).

Giữ nguyên thuật toán (khớp, xương, twist, skin cotan, cọ / island / hammer, pose thử, self-test, xuất glTF, dùng rig khách),
chỉ thay chỗ chạm vào renderer / camera / canvas / gizmo / undo / kho lưu / bảng điều khiển bằng bản của Studio (đối tượng `host`).
Chạy lại khi template đổi:  python tools/studio/port_rig.py
Mỗi phép thay phải khớp đúng (assert), để biết ngay khi template đổi khác đi.
"""
import os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SRC = os.path.join(ROOT, "work", "rig_lab", "template.html")
OUT = os.path.join(ROOT, "tools", "studio", "modules", "rig_engine.js")
t = open(SRC, encoding="utf8").read().replace(chr(13) + chr(10), chr(10))   # template có dòng CRLF lẫn LF

a = t.index("const DATA = (window.__meshApply")
a = t.index("\n", a) + 1
b = t.index("renderVbar(); resize(); setView(")
main = t[a:b]
p = t.index("/*POSEEXPORT*/")
tail = t[p:t.index("</script>", p)]


def cut(s, start, end, repl="", close=False):
    """Thay đoạn từ dòng chứa `start` tới hết dòng chứa `end` (close: bỏ luôn dòng "}" đóng hàm ngay sau)."""
    i = s.index(start)
    i = s.rfind("\n", 0, i) + 1
    j = s.index(end, i) + len(end)   # tới hết dòng chứa ký tự cuối của `end` (end có thể nhiều dòng)
    if not end.endswith("\n"):
        j = s.index("\n", j) + 1
    if close:
        assert s[j:j + 2] == "}\n", "không có } sau " + end[:40]
        j += 2
    return s[:i] + repl + s[j:]


def rep(s, old, new, count=1):
    n = s.count(old)
    assert n >= 1, "không thấy: " + old[:80]
    if count == 1:
        assert n == 1, "thấy %d lần: %s" % (n, old[:80])
    return s.replace(old, new)


m = main
# báo lỗi ra màn hình + listener lỗi toàn cục: Studio dùng toast
m = cut(m, "// báo lỗi JS lên màn hình", 'window.addEventListener("unhandledrejection"', "")
m = m.replace("window.__showErr", "__err")
# renderer / scene / camera / orbit / đèn: Studio có sẵn; scene = nhóm cm của host
m = cut(m, 'const cv = $("cv"), vp = $("vp");', "dl.position.set(200, 400, 500); scene.add(dl);",
        "const TARGET = new THREE.Vector3(0, DATA.auto.H * 0.5, 0);\n")
m = cut(m, "const grid = new THREE.GridHelper(500", "scene.add(grid);", "")
# gizmo: TransformControls riêng → gizmo chung (host.placeGizmo, ENGINE.gz*)
m = cut(m, "const tc = new THREE.TransformControls(cam, cv);", "syncScene(true); dirty();\n});",
        """// Gizmo mọi bước: bước 2–3 dời / xoay / scale khớp (xoay thì khớp con quay theo, như Maya);
// bước 4–5 xoay = pose thử của xương đang chọn (POSE, không sửa rig), dời = dời khớp (rig đổi, cần tính lại skin).
let start = null, gzBone = null;
function centroid() { const c = new THREE.Vector3(); S.forEach(k => c.add(new THREE.Vector3(...LM[k]))); return c.multiplyScalar(1 / Math.max(S.size, 1)); }
const gzJoint = () => step >= 4 ? (step === 5 ? (poseBone || jointSel) : jointSel) : null;
function lmKids(keys) {   // các khớp con cháu (có landmark) của nhóm khớp
  const kids = {}; buildSkeleton(LM).forEach(b => { if (b.parent && !b.twist) (kids[b.parent] = kids[b.parent] || []).push(b.name); });
  const out = new Set(), st = [...keys];
  while (st.length) { const n = st.pop(); for (const c of kids[n] || []) if (Array.isArray(LM[c]) && !keys.has(c) && !out.has(c)) { out.add(c); st.push(c); } }
  return out;
}
function gzPlace() {
  if (mode === "select") return null;
  if (step === 2 || step === 3) return S.size ? centroid() : null;
  const j = gzJoint(); if (!j || !Array.isArray(LM[j]) && mode !== "rotate") return null;
  if (mode === "rotate") { if (!SK) return null; const p = posedBones(buildSkeleton(LM))[j]; return p ? new THREE.Vector3(...p) : null; }
  return new THREE.Vector3(...LM[j]);
}
function gzStart(md) {   // md: ép kiểu thao tác (Channel Box nhập số = dời)
  md = md || mode; start = null; gzBone = null;
  if (step >= 4) {
    const j = gzJoint(); if (!j) return;
    if (md === "rotate" && SK) {
      const B = buildSkeleton(LM), W = poseMats(B), b = B.find(x => x.name === j); if (!b) return;
      gzBone = { j, b, W0: W[j].clone(), Wpi: (b.parent && W[b.parent] ? W[b.parent].clone() : new THREE.Matrix4()).invert(), F: boneFrames(B)[j] };
      return;
    }
    if (Array.isArray(LM[j])) { start = { [j]: new THREE.Vector3(...LM[j]) }; start.__one = j; }
    return;
  }
  start = {}; S.forEach(k => start[k] = new THREE.Vector3(...LM[k]));
  if (md === "rotate") lmKids(S).forEach(k => start[k] = new THREE.Vector3(...LM[k]));
}
function gzChange(M) {
  if (gzBone) {
    const g = gzBone, p = new THREE.Vector3(...g.b.pos), T = (x, y, z) => new THREE.Matrix4().makeTranslation(x, y, z);
    const loc = g.Wpi.clone().multiply(M).multiply(g.W0);
    const R = g.F.clone().invert().multiply(T(-p.x, -p.y, -p.z)).multiply(loc).multiply(T(p.x, p.y, p.z)).multiply(g.F);
    const e = new THREE.Euler().setFromRotationMatrix(R, "XYZ");
    POSE[g.j] = [e.x, e.y, e.z].map(v => Math.round(THREE.MathUtils.radToDeg(v) * 10) / 10);
    poseSkin(); if (strainOn) paintSkin(); syncScene(true); return;
  }
  if (!start) return;
  const one = start.__one, keys = Object.keys(start).filter(k => k !== "__one");
  for (const k of keys) { const v = start[k].clone().applyMatrix4(M); LM[k] = [v.x, v.y, v.z]; }
  if (mirror) {
    for (const k of keys) {
      const m = mirrorKey(k);
      if (!m) { LM[k][0] = 0; continue; }
      if (sideOf(k) === "R" || !start[m]) LM[m] = [-LM[k][0], LM[k][1], LM[k][2]];
    }
  }
  if (one && SK) { poseSkin(); }
  syncScene(true); dirty();
}
function gzEnd() {
  if (gzBone) { gzBone = null; syncScene(); renderJointBox(); if (step === 5) renderPanel(); return; }
  const one = start && start.__one; start = null; syncScene(); commit();
  if (one && SK) ST.toast("Đã dời khớp " + one + ": bấm Tính skin để skin theo khớp mới.");
}
""")
m = rep(m, "function setMode(m) { mode = m; if (m !== 'select') tc.setMode(m); syncScene(); renderSel(); }",
        "function setMode(m) { mode = m; host.onMode(m); syncScene(); renderSel(); }")
m = cut(m, "function setView(v) {", "new ResizeObserver(resize).observe(vp);", "")
m = rep(m, "  if (S.size && step === 2 && mode !== 'select') { if (!dragging) resetPivot(); tc.attach(pivot); } else tc.detach();",
        "  if (!dragging) host.placeGizmo(gzPlace(), mode);")
m = rep(m, "    m.visible = step === 2 && (showFing || !isFinger(k));", "    m.visible = (step === 2 || step === 3) && (showFing || !isFinger(k));")   # bước 3 cũng chọn / dời khớp được
m = cut(m, "function frame() { requestAnimationFrame(frame);", "function frame() {", "")
# chuột: chọn khớp bằng click / khung → host gọi pickLM / boxLM theo khung đang dùng
m = cut(m, "const MAYA = { LEFT: THREE.MOUSE.ROTATE", "vp.appendChild(boxEl);",
        "const TM = host.TM;\nconst tmE = e => ({ ctrlKey: e.ctrlKey, metaKey: e.metaKey, shiftKey: e.shiftKey || TM.add });\nconst ray = new THREE.Raycaster();\n")
m = cut(m, 'cv.addEventListener("pointerdown", e => {\n  if (e.pointerType === "mouse") orbit.mouseButtons', "else if (!(e.shiftKey || e.ctrlKey || e.metaKey || TM.add)) pick(null);\n});",
        """function pickLM(x, y, e, pane) {
  const h = host.raycaster(x, y, pane).intersectObjects(Object.values(lmMesh).filter(m => m.visible), false)[0];
  if (h) applySel([h.object.userData.key], tmE(e));
  else if (!(e.shiftKey || e.ctrlKey || e.metaKey || TM.add)) pick(null);
}
function boxLM(x0, y0, x1, y1, e, pane) {
  const xa = Math.min(x0, x1), xb = Math.max(x0, x1), ya = Math.min(y0, y1), yb = Math.max(y0, y1), hit = [], w = new THREE.Vector3();
  for (const k of LM_ORDER) { const m = lmMesh[k]; if (!m.visible) continue; const s = host.toScreen(m.getWorldPosition(w), pane); if (s.x >= xa && s.x <= xb && s.y >= ya && s.y <= yb) hit.push(k); }
  applySel(hit, tmE(e));
}
""")
m = cut(m, "function frameView(keys) {", "orbit.target.copy(c); cam.position.copy(c).addScaledVector(u, d); orbit.update();\n}", "")
# kho lưu: host.db (Home /api/store, cùng kho <nhân vật>_rig_lab với Rig Lab cũ)
m = cut(m, "  try { if (window.claude && window.claude.use) db = await window.claude.use(\"db\");", "if (!db) saveMsg = saveMsg ||", "  db = host.db;\n")
# undo: lịch sử chung của Studio
m = rep(m, "function resetHist() { undoS = []; redoS = []; cur = snap(); renderVbar(); }", "function resetHist() { cur = snap(); }")
m = cut(m, "function commit() {", "undoS.push(cur); if (undoS.length > 100) undoS.shift(); cur = n; redoS = []; syncHistBtns();\n}",
        "function commit() { const n = snap(); if (n === cur) return; host.pushLM(cur); cur = n; }\n")
m = rep(m, "function undo() { if (step === 4 && skinUndo.length) return skinUndoStep(); if (!undoS.length) return; redoS.push(cur); applySnap(undoS.pop()); }", "function undo() { ST.hist.undo(); }")
m = rep(m, "function redo() { if (step === 4 && skinRedo.length) return skinRedoStep(); if (!redoS.length) return; undoS.push(cur); applySnap(redoS.pop()); }", "function redo() { ST.hist.redo(); }")
m = re.sub(r"skinUndo\.push\((\w+)\);", r"host.pushSkin(\1);", m)
# bảng điều khiển: nằm trong tab dock của Studio (#panel); thanh bước / thanh view / Hiển thị → tab + menu Studio
m = rep(m, '  const p = $("panel");\n  if (step === 1) {', '  const p = $("panel"); if (!p) { host.refresh(); return; }\n  if (step === 1) {')
m = cut(m, "function renderSteps() {", '$("steps").querySelectorAll("button")', "function renderSteps() { host.refresh(); }\n", close=True)
m = cut(m, "function renderVbar() {", '$("vbar").querySelectorAll("button")', "function renderVbar() {}\n", close=True)
m = cut(m, "function renderVopts() {", 'const r = $("oref"); if (r) r.onchange', "function renderVopts() { host.refresh(); }\n", close=True)
m = cut(m, 'window.addEventListener("keydown", e => {', 'if (k === "f") frameView([...S]); if (k === "escape") pick(null);\n});', "")
# viewport: toạ độ cm trong nhóm host → đổi sang thế giới khi chiếu / về cm khi trúng tia
m = re.sub(r"\bcam\b", "CAM()", m)
m = rep(m, "v = new THREE.Vector3(...pp).project(CAM())", "v = new THREE.Vector3(...pp).applyMatrix4(scene.matrixWorld).project(CAM())")
m = rep(m, "  const h = ray.intersectObject(skinMesh, false)[0]; return h ? h.point : null;", "  const h = ray.intersectObject(skinMesh, false)[0]; return h ? scene.worldToLocal(h.point.clone()) : null;")
m = rep(m, "  return ray.intersectObject(skinMesh, false)[0] || null;", "  const h = ray.intersectObject(skinMesh, false)[0] || null; if (h) h.point = scene.worldToLocal(h.point.clone()); return h;")
m = rep(m, 'cv.addEventListener("pointerdown", e => {\n  if (step < 4', 'host.listen("pointerdown", e => {\n  if (step < 4')
m = rep(m, 'cv.addEventListener("pointermove", e => {\n  if (step === 4 && skTool === "brush"', 'host.listen("pointermove", e => {\n  if (step === 4 && skTool === "brush"')
m = rep(m, 'window.addEventListener("pointerup", e => {\n  if (painting)', 'window.addEventListener("pointerup", e => {\n  if (!host.alive()) return;\n  if (painting)')
m = rep(m, 'window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => syncScene());', "")

tl = tail.replace("/*POSEEXPORT*/", "// ---- xuất glTF cho Pose (POSEEXPORT)")
tl = tl.replace("/*ADOPTRIG*/", "// ---- dùng rig khách (ADOPTRIG)")

for bad in [r"\brenderer\b", r"\borbit\.", r"\btc\.", r"setView\(", r"frameView\(", "requestAnimationFrame", r'\$\("cv"\)', r'\$\("vp"\)']:
    hit = re.search(bad, m)
    assert not hit, "còn sót: " + m[max(0, hit.start() - 80):hit.start() + 60]

head = '''// SINH TỰ ĐỘNG bởi tools/studio/port_rig.py từ work/rig_lab/template.html — đừng sửa tay, sửa port_rig.py rồi chạy lại.
// Lõi Rig Lab chạy trong viewport Studio: ST.rigEngine(DATA, host) → API cho modules/rig.js.
ST.rigEngine = function (DATA, host) {
const __err = m => { console.error(m); ST.toast("Rig: " + m); };
const scene = host.root, cv = host.cv, CAM = host.cam;
'''
foot = '''
syncScene(); renderAll(); resetHist();
const ready = initDb();
return {
  ready, renderPanel, renderAll, go, setMode, pick, setSel, applySel, pickLM, boxLM, pickJoint, selectBoneByName, gzStart, gzChange, gzEnd, syncScene,
  snapStr: snap, applySnap, skinSnapshotOf, restoreSkin, scheduleSkinSave, saveLM, saveSkin, exportRig, exportGltf, buildGltf, adoptGuestJoints, adoptGuestSkin, assignIslandOf, stripBoneFromBody, moveWeight, cleanWeights, guestJ, guestS,
  setSkTool, assignIsland, computeSkin, hammerCurrent, hammerAuto, runSelfTest, exportWeights, renderPanelLight, buildSkeleton: () => buildSkeleton(LM), LM_ORDER, GROUPS, isFinger, mirrorKey, sideOf, centroid, dirty, commit, initFingers,
  get: () => ({ step, sel, S, mode, mirror, showRef, showWire, showSkel, showFing, vis, SK, skTool, saveMsg, gates, jointSel, poseBone, skinBone, LM, TW, CFG, DATA, clothN: clothMeshes.length, propN: propMeshes.length }),
  set(k, v) {
    if (k === "mirror") mirror = v; else if (k === "showRef") showRef = v; else if (k === "showWire") showWire = v; else if (k === "showSkel") showSkel = v;
    else if (k === "showFing") { showFing = v; if (!v) { [...S].filter(isFinger).forEach(x => S.delete(x)); sel = [...S].pop() || null; } }
    else if (k === "visBody") vis.body = v; else if (k === "visCloth") vis.cloth = v; else if (k === "visProps") vis.props = vis.props.map(() => v);
    else if (k === "saveMsg") saveMsg = v;
    syncScene(); renderPanel();
  },
  setLM(k, xyz) { LM[k] = xyz.slice(); if (mirror && mirrorKey(k)) LM[mirrorKey(k)] = [-xyz[0], xyz[1], xyz[2]]; syncScene(); dirty(); commit(); renderPanel(); },
  wantsSkinPointer: e => step === 4 && !!SK && (skTool === "brush" || skTool === "island") && e.button === 0 && !e.altKey,
};
};
'''
out = head + m + "\n" + tl + foot
open(OUT, "w", encoding="utf8", newline=chr(10)).write(out)
print(len(out) // 1024, "KB ->", OUT)
