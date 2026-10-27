// SINH TỰ ĐỘNG bởi tools/studio/port_rig.py từ work/rig_lab/template.html — đừng sửa tay, sửa port_rig.py rồi chạy lại.
// Lõi Rig Lab chạy trong viewport Studio: ST.rigEngine(DATA, host) → API cho modules/rig.js.
ST.rigEngine = function (DATA, host) {
const __err = m => { console.error(m); ST.toast("Rig: " + m); };
const scene = host.root, cv = host.cv, CAM = host.cam;
const $ = id => document.getElementById(id);
const fix = (v, n = 1) => (+v).toFixed(n);

// ---------------------------------------------------------------- mẫu skeleton (tên theo rig khách)
const CFG = Object.assign({ name: "Gaygor", fingers: ["Middle", "Thumb", "Index", "Ring", "Pinky"], fseg: 3, toes: true, toesEnd: false, fingerEnd: false, dress: true, prop: true, weapon: true, headEnd: true }, DATA.cfg || {});
const SIDE_J = ["Scapula", "Shoulder", "Elbow", "Wrist", "Hip", "Knee", "Ankle", ...(CFG.toes ? ["Toes", "ToesEnd"] : CFG.toesEnd ? ["ToesEnd"] : [])];
const LEG_J = ["Hip", "Knee", "Ankle", ...(CFG.toes ? ["Toes", "ToesEnd"] : CFG.toesEnd ? ["ToesEnd"] : [])];
const LM_LABEL = { Root_M: "Hông (Root)", Spine1_M: "Eo", Chest_M: "Ngực", Neck_M: "Cổ", Head_M: "Đầu", HeadEnd_M: "Đỉnh đầu",
  DressFront_M: "Váy trước", DressBack_M: "Váy sau", Prop_M: "Điểm cầm prop", Weapon: "Chùy (pivot)", HandTip: "Đầu ngón giữa" };
const CENTER = ["Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M", ...(CFG.headEnd ? ["HeadEnd_M"] : []), ...(CFG.dress ? ["DressFront_M", "DressBack_M"] : []), ...(CFG.prop ? ["Prop_M"] : []), ...(CFG.weapon ? ["Weapon"] : [])];
const NC = CFG.headEnd ? 6 : 5;   // số khớp thân giữa (cột sống + đầu)
const FINGERS = CFG.fingers, FSEG = [1, 2, 3].filter(i => i <= CFG.fseg);
const FKEYS = FINGERS.flatMap(f => [...FSEG.map(i => f + "Finger" + i), ...(CFG.fingerEnd ? [f + "FingerEnd"] : [])]);
const isFinger = k => /Finger(\d|End)_/.test(k);
const LM_ORDER = [...CENTER.slice(0, NC), ...["Scapula", "Shoulder", "Elbow", "Wrist"].map(n => n + "_R"), ...LEG_J.map(n => n + "_R"),
  ...["Scapula", "Shoulder", "Elbow", "Wrist"].map(n => n + "_L"), ...LEG_J.map(n => n + "_L"), ...CENTER.slice(NC),
  ...FKEYS.map(n => n + "_R"), ...FKEYS.map(n => n + "_L")];
const sideOf = k => k.endsWith("_R") ? "R" : k.endsWith("_L") ? "L" : "M";
const mirrorKey = k => k.endsWith("_R") ? k.slice(0, -1) + "L" : k.endsWith("_L") ? k.slice(0, -1) + "R" : null;

function buildSkeleton(L) {
  const B = [], add = (name, parent, pos) => B.push({ name, parent, pos: pos.slice() });
  add("root", null, [0, 0, 0]);
  const P = n => L[n];
  [["Root_M", "root"], ["Spine1_M", "Root_M"], ["Chest_M", "Spine1_M"], ["Neck_M", "Chest_M"], ["Head_M", "Neck_M"], ...(CFG.headEnd ? [["HeadEnd_M", "Head_M"]] : [])].forEach(([n, p]) => add(n, p, P(n)));
  for (const s of ["R", "L"]) {
    add("Scapula_" + s, "Chest_M", P("Scapula_" + s)); add("Shoulder_" + s, "Scapula_" + s, P("Shoulder_" + s));
    add("Elbow_" + s, "Shoulder_" + s, P("Elbow_" + s)); add("Wrist_" + s, "Elbow_" + s, P("Wrist_" + s));
    for (const f of FINGERS) { for (const i of FSEG) add(f + "Finger" + i + "_" + s, i > 1 ? f + "Finger" + (i - 1) + "_" + s : "Wrist_" + s, P(f + "Finger" + i + "_" + s));
      if (CFG.fingerEnd) add(f + "FingerEnd_" + s, f + "Finger" + FSEG[FSEG.length - 1] + "_" + s, P(f + "FingerEnd_" + s)); }
  }
  if (CFG.prop) add("Prop_M", "Chest_M", P("Prop_M")); if (CFG.dress) { add("DressFront_M", "Root_M", P("DressFront_M")); add("DressBack_M", "Root_M", P("DressBack_M")); }
  for (const s of ["R", "L"]) for (const [i, n] of LEG_J.entries())
    add(n + "_" + s, i ? LEG_J[i - 1] + "_" + s : "Root_M", P(n + "_" + s));
  if (CFG.weapon) add("Weapon", "root", P("Weapon"));
  // twist: đoạn đầu (Shoulder/Hip) nhận roll NGƯỢC t lần roll của khớp đầu; đoạn cuối (Elbow/Knee) nhận roll +t lần roll của Wrist/Ankle
  const byName = {}; B.forEach(b => byName[b.name] = b);
  for (const s of ["R", "L"]) for (const st in TW_SEG) {
    const n = TW[st], a = byName[st + "_" + s], z = byName[TW_SEG[st][0] + "_" + s];
    for (let i = 1; i <= n; i++) {
      const t = i / (n + 1), proximal = st === "Shoulder" || st === "Hip";
      B.push({ name: st + "Twist" + i + "_" + s, parent: st + "_" + s, pos: a.pos.map((v, k) => v + (z.pos[k] - v) * t),
        twist: { source: proximal ? st + "_" + s : z.name, factor: +(proximal ? -t : t).toFixed(4), axis: "segment", segment: [st + "_" + s, z.name] } });
    }
  }
  return B;
}

// ngón sinh từ mẫu theo cổ tay + đầu ngón giữa; sau đó là khớp tự do
function initFingers(L, force) {
  for (const s of ["R", "L"]) {
    const w = L["Wrist_" + s], t = L["HandTip_" + s] || w, len = Math.abs(t[0] - w[0]) || 1, sg = s === "R" ? -1 : 1;
    for (const f of FINGERS) DATA.fingers[f].forEach((o, i) => { const k = f + "Finger" + (i + 1) + "_" + s;
      if (force || !L[k]) L[k] = [w[0] + sg * o[0] * len, w[1] + o[1] * len, w[2] + o[2] * len]; });
    if (CFG.fingerEnd) for (const f of FINGERS) { const k = f + "FingerEnd_" + s; if (force || !L[k]) L[k] = f === "Middle" ? t.slice() : [t[0], t[1] - 0.2 * len, t[2]]; }
  }
}
// ---------------------------------------------------------------- trạng thái
function completeLM(L0) {   // trả về BẢN SAO đầy đủ: dữ liệu từ db có thể bị đóng băng (gán thêm khớp mới bị bỏ qua âm thầm) hoặc thiếu khớp mới (End…)
  const L = JSON.parse(JSON.stringify(L0 || {}));
  for (const k in L) if (L[k] && !Array.isArray(L[k]) && typeof L[k] === "object") L[k] = Object.keys(L[k]).sort((x, y) => x - y).map(i => L[k][i]);   // mảng bị lưu thành object {0:..,1:..}
  L.HandTip_R = L.HandTip_R || DATA.auto.landmarks.HandTip_R; L.HandTip_L = L.HandTip_L || DATA.auto.landmarks.HandTip_L; initFingers(L);
  for (const k of LM_ORDER) if (!Array.isArray(L[k]) || L[k].length !== 3 || L[k].some(v => !isFinite(v))) L[k] = (DATA.auto.landmarks[k] || [0, 0, 0]).slice();
  return L;
}
let LM = JSON.parse(JSON.stringify(DATA.auto.landmarks));        // tên → [x,y,z]
initFingers(LM, true);
const S = new Set();
let undoS = [], redoS = [], cur = null;
let mode = "translate";
// twist joint: số lượng theo đoạn (khớp đầu đoạn), áp cho cả R và L. Tên: <Khớp đầu>Twist<i>_<R|L>
const TW_SEG = { Shoulder: ["Elbow", "Cánh tay trên"], Elbow: ["Wrist", "Cẳng tay"], Hip: ["Knee", "Đùi"], Knee: ["Ankle", "Cẳng chân"] };
let TW = { Shoulder: 0, Elbow: 0, Hip: 0, Knee: 0 };
const vis = { body: true, cloth: true, props: DATA.props.map(() => true) };
let step = 1, sel = null, mirror = true, showRef = false, showWire = false, showSkel = true, showFing = true;
let gates = { 1: null, 2: null, 3: null, 4: null, 5: null };
let db = null, saveMsg = "";

// ---------------------------------------------------------------- three.js
const TARGET = new THREE.Vector3(0, DATA.auto.H * 0.5, 0);

function meshFrom(m, color, opacity) {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(m.verts, 3));
  g.setIndex(m.tris); g.computeVertexNormals();
  const mat = new THREE.MeshLambertMaterial({ color, transparent: true, opacity, side: THREE.DoubleSide, depthWrite: false });
  const mesh = new THREE.Mesh(g, mat);
  const wire = new THREE.LineSegments(new THREE.WireframeGeometry(g), new THREE.LineBasicMaterial({ color: 0x8aa0c0, transparent: true, opacity: .35 }));
  wire.visible = false; mesh.add(wire); mesh.userData.wire = wire;
  return mesh;
}
const bodyMesh = meshFrom(DATA.body, 0x8a96aa, 0.55); scene.add(bodyMesh);
const clothMeshes = (DATA.clothes || []).map(c => { const m = meshFrom(c, 0xc9a77a, 0.4); scene.add(m); return m; });
const propMeshes = DATA.props.map(p => { const m = meshFrom(p, 0xb59a6a, 0.55); scene.add(m); return m; });

const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const lmGroup = new THREE.Group(); scene.add(lmGroup);
const lmMesh = {};
const sphereGeo = new THREE.SphereGeometry(2.6, 14, 10);
for (const k of LM_ORDER) {
  const m = new THREE.Mesh(sphereGeo, new THREE.MeshBasicMaterial({ color: 0xffffff, depthTest: false, transparent: true }));
  m.renderOrder = 10; m.userData.key = k; lmGroup.add(m); lmMesh[k] = m;
}
const skelLines = new THREE.LineSegments(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0xffffff, depthTest: false, transparent: true }));
skelLines.renderOrder = 8; scene.add(skelLines);
const twPts = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 7, sizeAttenuation: false, depthTest: false, color: 0xffaa00 }));
twPts.renderOrder = 9; scene.add(twPts);
const skelPts = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 4, sizeAttenuation: false, depthTest: false, color: 0xffffff }));
skelPts.renderOrder = 9; scene.add(skelPts);
const refLines = new THREE.LineSegments(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ depthTest: false, transparent: true, opacity: .85 }));
refLines.renderOrder = 7; scene.add(refLines);
{
  const pos = [], idx = {}; DATA.ref.forEach((b, i) => idx[b.name] = b);
  DATA.ref.forEach(b => { if (b.pos && b.parent && b.parent !== "root" && idx[b.parent] && idx[b.parent].pos) pos.push(...idx[b.parent].pos, ...b.pos); });
  refLines.geometry.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
}

let start = null;
function centroid() { const c = new THREE.Vector3(); S.forEach(k => c.add(new THREE.Vector3(...LM[k]))); return c.multiplyScalar(1 / Math.max(S.size, 1)); }
function gzStart() { start = {}; S.forEach(k => start[k] = new THREE.Vector3(...LM[k])); }
function gzChange(M) {
  if (!start) return;
  for (const k in start) { const v = start[k].clone().applyMatrix4(M); LM[k] = [v.x, v.y, v.z]; }
  if (mirror) {
    for (const k of S) {
      const m = mirrorKey(k);
      if (!m) { LM[k][0] = 0; continue; }
      if (sideOf(k) === "R" || !S.has(m)) LM[m] = [-LM[k][0], LM[k][1], LM[k][2]];
    }
  }
  syncScene(true); dirty();
}
function gzEnd() { start = null; syncScene(); commit(); }


function lmColor(k) { return css(sideOf(k) === "R" ? "--right" : sideOf(k) === "L" ? "--left" : "--mid"); }
function syncScene(dragging) {
  for (const k of LM_ORDER) {
    const m = lmMesh[k]; if (!Array.isArray(LM[k])) { LM = completeLM(LM); } m.position.set(...LM[k]);
    m.material.color.set(lmColor(k));
    m.scale.setScalar(S.has(k) ? 1.5 : 1);
    m.visible = step === 2 && (showFing || !isFinger(k));
    if (isFinger(k)) m.scale.setScalar(S.has(k) ? 1.2 : 0.6);
    m.material.color.set(S.has(k) ? css("--accent") : lmColor(k));
  }
  // skeleton
  const B = buildSkeleton(LM), idx = {}; B.forEach(b => idx[b.name] = b);
  const seg = [], pts = [], tpts = [], PB = step >= 4 && SK ? posedBones(B) : null, ps = b => PB ? PB[b.name] : b.pos;
  B.forEach(b => { if (b.twist) { tpts.push(...ps(b)); return; } pts.push(...ps(b)); if (b.parent && b.parent !== "root") seg.push(...ps(idx[b.parent]), ...ps(b)); });
  twPts.geometry.setAttribute("position", new THREE.Float32BufferAttribute(tpts, 3)); twPts.material.color.set(css("--warn"));
  skelLines.geometry.setAttribute("position", new THREE.Float32BufferAttribute(seg, 3));
  skelPts.geometry.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
  skelLines.material.color.set(css("--fg")); skelPts.material.color.set(css("--accent"));
  skelLines.visible = skelPts.visible = step >= 3 || (step === 2 && showSkel); twPts.visible = step >= 3;
  refLines.material.color.set(css("--ref")); refLines.visible = showRef; if (typeof updateSelPt === "function") updateSelPt();
  bodyMesh.material.opacity = step === 3 ? 0.28 : 0.5;
  bodyMesh.visible = vis.body && step < 4; skinMesh.visible = vis.body && step >= 4 && !!SK; skinWire.visible = step >= 4 && showWire;
  if (SK && step >= 4) skinMesh.material.opacity = 1;
  propMeshes.forEach((m, i) => m.visible = vis.props[i]);
  clothMeshes.forEach(m => { m.visible = vis.cloth; m.material.opacity = step >= 4 ? 0.35 : 0.4; m.userData.wire.visible = showWire; });
  bodyMesh.userData.wire.visible = showWire; propMeshes.forEach(m => m.userData.wire.visible = showWire);
  if (!dragging) host.placeGizmo(S.size && step === 2 && mode !== 'select' ? centroid() : null, mode);
}

// ---- thao tác kiểu Maya
// Alt+LMB xoay · Alt+MMB kéo · Alt+RMB / lăn chuột zoom · LMB click hoặc kéo khung để chọn
// Shift đảo chọn · Ctrl bỏ chọn · Ctrl+Shift thêm · Q chọn, W dời, E xoay, R co giãn · F nhìn vào vùng chọn · A nhìn toàn bộ
const TM = host.TM;
const tmE = e => ({ ctrlKey: e.ctrlKey, metaKey: e.metaKey, shiftKey: e.shiftKey || TM.add });
const ray = new THREE.Raycaster();
function applySel(keys, e) {   // quy tắc chọn của Maya
  const ctrl = e.ctrlKey || e.metaKey, sh = e.shiftKey;
  if (!ctrl && !sh) { setSel(keys, false); return; }
  const cur = new Set(S);
  keys.forEach(k => { if (ctrl && sh) cur.add(k); else if (ctrl) cur.delete(k); else (cur.has(k) ? cur.delete(k) : cur.add(k)); });
  S.clear(); cur.forEach(k => S.add(k)); sel = keys.length && cur.has(keys[keys.length - 1]) ? keys[keys.length - 1] : ([...S].pop() || null);
  syncScene(); renderPanelLight();
}
function pickLM(x, y, e, pane) {
  const h = host.raycaster(x, y, pane).intersectObjects(Object.values(lmMesh).filter(m => m.visible), false)[0];
  if (h) applySel([h.object.userData.key], tmE(e));
  else if (!(e.shiftKey || e.ctrlKey || e.metaKey || TM.add)) pick(null);
}
function boxLM(x0, y0, x1, y1, e, pane) {
  const xa = Math.min(x0, x1), xb = Math.max(x0, x1), ya = Math.min(y0, y1), yb = Math.max(y0, y1), hit = [], w = new THREE.Vector3();
  for (const k of LM_ORDER) { const m = lmMesh[k]; if (!m.visible) continue; const s = host.toScreen(m.getWorldPosition(w), pane); if (s.x >= xa && s.x <= xb && s.y >= ya && s.y <= yb) hit.push(k); }
  applySel(hit, tmE(e));
}

// ---------------------------------------------------------------- lưu / cổng duyệt
const dirtyFlag = { v: false };
let lmTimer = null;
function dirty() { dirtyFlag.v = true; saveMsg = "Đang lưu…"; renderPanelLight(); clearTimeout(lmTimer); lmTimer = setTimeout(saveLM, 1200); }
async function initDb() {
  db = host.db;
  try {
    if (db) {
      const a = await db.doc("rig/landmarks").get(); if (a.exists && a.data().lm) { LM = completeLM(a.data().lm); if (window.__meshAt && a.data().meshAt !== window.__meshAt) { LM = completeLM(window.__meshLM(LM)); setTimeout(dirty, 800); } } if (a.exists && a.data().tw) TW = Object.assign(TW, a.data().tw);
      const g = await db.doc("rig/gates").get(); if (g.exists) gates = Object.assign(gates, g.data().g || {});
      saveMsg = db.isLocal ? "Đã lưu vào dự án trên máy (work/store)." : "Đã nối db: lưu cho AI đọc được.";
      const sk = await db.doc("rig/skin").get(); if (sk.exists) loadSkinDoc(sk.data());
    } else {
      const a = localStorage.getItem("rig_lm"); if (a) LM = completeLM(JSON.parse(a)); try { const k = localStorage.getItem("rig_skin"); if (k) loadSkinDoc(JSON.parse(k)); } catch (e) {} const t = localStorage.getItem("rig_tw"); if (t) TW = Object.assign(TW, JSON.parse(t));
      const g = localStorage.getItem("rig_gates"); if (g) gates = JSON.parse(g);
    }
  } catch (e) {}
  LM = completeLM(LM);
  syncScene(); renderAll(); resetHist();
}
async function saveLM() {
  try {
    if (db) await db.doc("rig/landmarks").set({ lm: LM, tw: TW, at: Date.now(), meshAt: window.__meshAt || null }); else { localStorage.setItem("rig_lm", JSON.stringify(LM)); localStorage.setItem("rig_tw", JSON.stringify(TW)); }
    dirtyFlag.v = false; saveMsg = db ? "Đã lưu" : "Đã lưu (chỉ trình duyệt này)";
  } catch (e) { saveMsg = "Không lưu được: " + (e.message || e.code || e); }
  renderPanelLight();
}
async function setGate(n, status) {
  gates[n] = { status, note: ($("note") || {}).value || "", at: Date.now() };
  try { if (db) await db.doc("rig/gates").set({ g: gates }); else localStorage.setItem("rig_gates", JSON.stringify(gates)); saveMsg = "Đã ghi kết quả bước " + n + "."; }
  catch (e) { saveMsg = "Không ghi được: " + (e.message || e.code || e); }
  renderAll();
}
async function exportRig() {
  const B = buildSkeleton(LM);
  const out = { character: CFG.name, template: "biped", unit: "cm", up: "+Y", front: "+Z", landmarks: LM, twist_counts: TW, bones: B.map(b => Object.assign({ name: b.name, parent: b.parent, head: b.pos.map(v => +v.toFixed(3)) }, b.twist ? { twist: b.twist } : {})) };
  const text = JSON.stringify(out, null, 1);
  try { const d = await window.claude.use("downloads"); if (d) { await d.save({ filename: CFG.name + "_rig_m1.json", data: text }); saveMsg = "Đã xuất rig.json."; return renderPanelLight(); } } catch (e) {}
  try { await navigator.clipboard.writeText(text); saveMsg = "Đã chép rig.json vào clipboard."; } catch (e) { saveMsg = "Không xuất được rig.json."; }
  renderPanelLight();
}

// ---------------------------------------------------------------- phân tích bước 1/3
const bodyV = (() => { const a = DATA.body.verts, o = []; for (let i = 0; i < a.length; i += 3) o.push([a[i], a[i + 1], a[i + 2]]); return o; })();
const bb = (() => { const mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9]; bodyV.forEach(v => v.forEach((c, i) => { mn[i] = Math.min(mn[i], c); mx[i] = Math.max(mx[i], c); })); return { mn, mx }; })();
function symmetryDev() {   // trung vị khoảng cách từ mỗi đỉnh tới đỉnh gương gần nhất (lưới 6cm)
  const cell = 6, g = new Map(), key = (x, y, z) => Math.floor(x / cell) + "," + Math.floor(y / cell) + "," + Math.floor(z / cell);
  bodyV.forEach(v => { const k = key(...v); (g.get(k) || g.set(k, []).get(k)).push(v); });
  const ds = [];
  for (let i = 0; i < bodyV.length; i += 3) {
    const v = bodyV[i], m = [-v[0], v[1], v[2]]; let best = 99;
    const cx = Math.floor(m[0] / cell), cy = Math.floor(m[1] / cell), cz = Math.floor(m[2] / cell);
    for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
      const l = g.get((cx + a) + "," + (cy + b) + "," + (cz + c)); if (l) l.forEach(u => best = Math.min(best, Math.hypot(u[0] - m[0], u[1] - m[1], u[2] - m[2])));
    }
    ds.push(best);
  }
  ds.sort((a, b) => a - b); return { med: ds[ds.length >> 1], p90: ds[Math.floor(ds.length * .9)] };
}
const SYM = symmetryDev();

function footFront() { const f = bodyV.filter(v => v[1] < 8 && v[0] < 0); return f.length ? f.reduce((s, v) => s + v[2], 0) / f.length > LM.Ankle_R[2] - 0.5 : true; }
function dist(a, b) { return Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]); }
function skelChecks() {
  const B = buildSkeleton(LM), idx = {}; B.forEach(b => idx[b.name] = b);
  const out = [];
  const refNames = new Set(DATA.ref.map(b => b.name)), mine = new Set(B.map(b => b.name));
  const miss = [...refNames].filter(n => !mine.has(n)), extra = [...mine].filter(n => !refNames.has(n) && !/Twist\d/.test(n) && !/End_/.test(n));
  out.push([!miss.length && !extra.length ? "ok" : "bad", "Tên xương khớp rig khách", `${B.length} xương` + (miss.length ? ", thiếu " + miss.join(",") : "") + (extra.length ? ", thừa " + extra.join(",") : "")]);
  let short = 1e9, shortN = ""; B.forEach(b => { if (b.parent && b.parent !== "root") { const l = dist(b.pos, idx[b.parent].pos); if (l < short) { short = l; shortN = b.name; } } });
  out.push([short > 1 ? "ok" : "bad", "Không có xương quá ngắn", `ngắn nhất ${shortN} ${fix(short)} cm`]);
  let asym = 0; for (const n of SIDE_J) {
    const r = idx[n + "_R"].pos, l = idx[n + "_L"].pos; asym = Math.max(asym, dist([-r[0], r[1], r[2]], l)); }
  out.push([asym < 1 ? "ok" : asym < 4 ? "warn" : "bad", "Đối xứng trái/phải", `lệch lớn nhất ${fix(asym)} cm`]);
  for (const [nm, a, b, c] of [["gối", "Hip", "Knee", "Ankle"], ["khuỷu", "Shoulder", "Elbow", "Wrist"]]) {
    let w = 1e9; for (const s of ["R", "L"]) {
      const A = idx[a + "_" + s].pos, Bk = idx[b + "_" + s].pos, C = idx[c + "_" + s].pos;
      const ac = C.map((v, i) => v - A[i]), ab = Bk.map((v, i) => v - A[i]), al = Math.hypot(...ac), t = (ab[0] * ac[0] + ab[1] * ac[1] + ab[2] * ac[2]) / (al * al);
      w = Math.min(w, Math.hypot(...ab.map((v, i) => v - t * ac[i])));
    }
    out.push([w > 3 ? "ok" : w > 1.5 ? "warn" : "bad", "Độ cong " + nm + " (xác định hướng pole)", `lệch khỏi đường thẳng ${fix(w)} cm`]);
  }
  const ul = dist(idx.Hip_R.pos, idx.Knee_R.pos), ll = dist(idx.Knee_R.pos, idx.Ankle_R.pos), r = ul / ll;
  out.push([r > .6 && r < 1.6 ? "ok" : "warn", "Tỉ lệ đùi / cẳng chân", `${fix(ul)} / ${fix(ll)} cm (tỉ lệ ${fix(r, 2)})`]);
  if (CFG.toes || CFG.toesEnd) { const ground = Math.min(idx.ToesEnd_R.pos[1], idx.ToesEnd_L.pos[1]);
    out.push([Math.abs(ground) < 1.5 ? "ok" : "warn", "Mũi chân chạm sàn (y = 0)", `y = ${fix(ground)} cm`]); }
  else { const a = Math.min(idx.Ankle_R.pos[1], idx.Ankle_L.pos[1]); out.push([a > 2 && a < 20 ? "ok" : "warn", "Cổ chân cao trên sàn", `y = ${fix(a)} cm`]); }
  return out;
}
function refErrors() {
  const B = buildSkeleton(LM), idx = {}; B.forEach(b => idx[b.name] = b);
  return DATA.ref.filter(r => r.pos && r.name !== "root" && idx[r.name]).map(r => [r.name, dist(idx[r.name].pos, r.pos)]);
}

// ---------------------------------------------------------------- bảng điều khiển
// ---- undo / redo: ảnh chụp {LM, TW} sau mỗi thao tác hoàn tất (thả chuột, nhập số, đặt lại, đổi twist)
const snap = () => JSON.stringify({ LM, TW });
function resetHist() { cur = snap(); }
function commit() { const n = snap(); if (n === cur) return; host.pushLM(cur); cur = n; }
function applySnap(str) { const o = JSON.parse(str); LM = completeLM(o.LM); TW = o.TW; cur = str; syncScene(); dirty(); commit(); renderPanel(); syncHistBtns(); }
function undo() { ST.hist.undo(); }
function redo() { ST.hist.redo(); }
function syncHistBtns() { const u = $("bUndo"), r = $("bRedo"); if (u) u.disabled = !undoS.length; if (r) r.disabled = !redoS.length; }
function pick(k, add) {
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
  spine: () => CENTER.slice(0, NC), all: () => LM_ORDER.filter(k => showFing || !isFinger(k)) };
function dims() { const d = i => bb.mx[i] - bb.mn[i]; return [d(0), d(1), d(2)]; }
const esc = t => String(t).replace(/</g, "&lt;");
const OPEN = {};
const more = (id, title, html) => `<details class="more" data-more="${id}" ${OPEN[id] ? "open" : ""}><summary>${title}</summary>${html}</details>`;
function gateHtml(n) {
  const g = gates[n];
  const st = g ? (g.status === "ok" ? '<span class="chip ok">Đã duyệt</span>' : '<span class="chip fix">Cần sửa</span>') : '<span class="chip">Chưa duyệt</span>';
  return `<div class="gate"><div class="ghead"><b>Bước ${n}</b>${st}<span class="msg" id="smsg">${saveMsg}</span></div>
    <textarea id="note" rows="2" placeholder="Ghi chú cho AI nếu cần sửa">${g ? esc(g.note) : ""}</textarea>
    <div class="row"><button class="pri" id="gOk">Duyệt</button><button class="bad" id="gFix">Cần sửa</button></div></div>`;
}
function renderPanel() {
  const p = $("panel"); if (!p) { host.refresh(); return; }
  if (step === 1) {
    const [dx, dy, dz] = dims(), front = CFG.toes || CFG.toesEnd ? LM.ToesEnd_R[2] > LM.Ankle_R[2] : footFront(), tris = DATA.body.tris.length / 3 | 0;
    const items = [
      [Math.abs(bb.mn[1]) < 1.5 ? "ok" : "warn", "Chân đứng trên sàn", "y nhỏ nhất " + fix(bb.mn[1]) + " cm"],
      [Math.abs((bb.mn[0] + bb.mx[0]) / 2) < 2 ? "ok" : "warn", "Thân đối xứng quanh x = 0", "tâm bbox x = " + fix((bb.mn[0] + bb.mx[0]) / 2) + " cm"],
      ["ok", "Hướng: đầu +Y", "đỉnh đầu y = " + fix(bb.mx[1]) + " cm"],
      [front ? "ok" : "warn", "Mặt nhìn +Z", "mũi chân ở trước cổ chân theo trục z"],
      [SYM.med < 1.5 ? "ok" : "warn", "Mesh đối xứng gương", "lệch trung vị " + fix(SYM.med) + " cm"],
      [DATA.props.length ? "warn" : "ok", "Phần rời (island)", DATA.props.length ? "1 prop rời: gắn vào xương Weapon" : "không có"],
      ...(DATA.clothes || []).map(c => ["ok", "Lớp mặc thêm", c.name + " · " + (c.verts.length / 3 | 0) + " đỉnh · skin theo thân"]),
      [dx > dy * 1.5 ? "warn" : "ok", "Tư thế bind", dx > dy ? "tay dang ngang (T-pose)" : ""]];
    const warns = items.filter(x => x[0] !== "ok").length;
    p.innerHTML = `<h2>Kiểm tra mesh</h2>
      <div class="big ${warns ? "warn" : "ok"}">${warns ? "! " + warns + " mục cần chú ý" : "✓ Mesh ổn"}</div>
      <div class="sub">${fix(dy, 0)} cm cao · ${bodyV.length} đỉnh${DATA.props.length ? " · " + DATA.props.length + " prop rời" : ""}</div>
      ${more("m1", "Chi tiết kiểm tra", items.map(x => chk(x[0], x[1], x[2])).join("") + `<div class="kv"><span>Rộng (sải tay)</span><span>${fix(dx)} cm</span><span>Sâu</span><span>${fix(dz)} cm</span><span>Tam giác</span><span>${tris}</span></div>`)}
      <div class="row"><button class="pri" id="toStep2">Tiếp: đặt khớp</button></div>${gateHtml(1)}`;
  } else if (step === 2) {
    const rows = LM_ORDER.filter(k => showFing || !isFinger(k)).map(k => `<tr class="pick ${S.has(k) ? "sel" : ""}" data-k="${k}"><td><span class="ltxt" style="background:${lmColor(k)}"></span>${k}</td><td>${fix(LM[k][0])}</td><td>${fix(LM[k][1])}</td><td>${fix(LM[k][2])}</td></tr>`).join("");
    p.innerHTML = `<h2>Đặt khớp</h2>
      <div class="row"><label class="t"><input type="checkbox" id="mir" ${mirror ? "checked" : ""}> Đối xứng R→L</label><button id="resetAuto">Về gợi ý</button>${guestJ() ? '<button id="useRefJ" title="Đặt mọi khớp theo xương có sẵn của mesh (vàng), khỏi đặt tay">Dùng xương khách</button>' : ""}</div>
      <div id="selbox"></div>
      ${more("m2", "Bảng toạ độ (" + LM_ORDER.filter(k => showFing || !isFinger(k)).length + " khớp)", `<table><thead><tr><th>Khớp</th><th>x</th><th>y</th><th>z</th></tr></thead><tbody id="lmrows">${rows}</tbody></table>`)}
      ${gateHtml(2)}`;
    renderSel();
  } else if (step === 3) {
    const checks = skelChecks(), errs = refErrors().sort((a, b) => b[1] - a[1]), mean = errs.length ? errs.reduce((s, e) => s + e[1], 0) / errs.length : 0;
    const bad = checks.filter(c => c[0] !== "ok");
    p.innerHTML = `<h2>Bộ xương</h2>
      <div class="big ${bad.length ? "warn" : "ok"}">${bad.length ? "! " + bad.length + " mục cần chú ý" : "✓ " + checks.length + " kiểm tra đạt"} · ${buildSkeleton(LM).length} xương</div>
      ${bad.map(c => chk(c[0], c[1], c[2])).join("")}
      <h2>Twist joint</h2>
      <div class="kv" style="align-items:center">${Object.keys(TW_SEG).map(st => `<span><label for="tw_${st}">${TW_SEG[st][1]}</label></span><span><select id="tw_${st}">${[0, 1, 2, 3].map(n => `<option value="${n}" ${TW[st] === n ? "selected" : ""}>${n}</option>`).join("")}</select></span>`).join("")}</div>
      <div class="row"><button data-tw="0">Không twist</button><button data-tw="1">1 mỗi đoạn</button><button data-tw="2">2 mỗi đoạn</button></div>
      ${more("m3a", "Tất cả kiểm tra", checks.map(c => chk(c[0], c[1], c[2])).join(""))}
      ${!errs.length ? more("m3b", "Rig khách", `<div class="sub">Chỉ đối chiếu tên xương, không có vị trí đáp án (mesh khác tỉ lệ rig cũ).</div>`) : more("m3b", "Đối chiếu rig khách", `<div class="kv"><span>Sai lệch trung bình</span><span>${fix(mean)} cm</span><span>Lớn nhất</span><span>${errs[0][0]} ${fix(errs[0][1])} cm</span></div>
        <div class="row"><label class="t"><input type="checkbox" id="ref" ${showRef ? "checked" : ""}> Vẽ xương khách (vàng)</label></div>
        <table><thead><tr><th>Xương</th><th>lệch cm</th></tr></thead><tbody>${errs.slice(0, 10).map(e => `<tr><td>${e[0]}</td><td class="${e[1] > 8 ? "err-hi" : e[1] > 4 ? "err-mid" : ""}">${fix(e[1])}</td></tr>`).join("")}</tbody></table>`)}
      ${more("m3c", "Xuất", `<div class="row"><button id="exportRig">Xuất rig.json</button></div>`)}
      ${gateHtml(3)}`;
  } else if (step === 4) { renderSkinPanel(p); } else { renderPosePanel(p); }
  dockGate(p); wirePanel(); renderJointBox();
}
function dockGate(p) {   // cổng duyệt cố định ở đáy panel, phần còn lại cuộn
  const g = p.querySelector(".gate"), body = document.createElement("div"); body.className = "pbody";
  while (p.firstChild && p.firstChild !== g) body.appendChild(p.firstChild);
  p.insertBefore(body, g || null);
}
function chk(s, t, d) { return `<div class="chk"><i class="s-${s}">${s === "ok" ? "✓" : s === "warn" ? "!" : "✕"}</i><span>${t}</span>${d ? `<small>${d}</small>` : ""}</div>`; }
function setMode(m) { mode = m; host.onMode(m); syncScene(); renderSel(); }
function renderSel() {
  const b = $("selbox"); if (!b) return;
  const modes = [["select", "Chọn (Q)"], ["translate", "Dời (W)"], ["rotate", "Xoay (E)"], ["scale", "Co giãn (R)"]].map(([m, t]) => `<button data-mode="${m}" ${mode === m ? 'class="pri"' : ""}>${t}</button>`).join("");
  const grp = `<select id="grpSel" aria-label="Chọn nhanh"><option value="">Chọn nhanh…</option>${[["armR", "Tay R"], ["armL", "Tay L"], ["fingR", "Ngón R"], ["fingL", "Ngón L"], ["legR", "Chân R"], ["legL", "Chân L"], ["spine", "Thân"], ["all", "Tất cả"]].map(([g, t]) => `<option value="${g}">${t}</option>`).join("")}</select>`;
  let body;
  if (!S.size) body = '<div class="sub">Click một chấm hoặc kéo khung để chọn.</div>';
  else if (S.size > 1) body = `<div class="msg">Đã chọn ${S.size} khớp.</div>`;
  else body = `<div class="sub"><b>${sel}</b>${LM_LABEL[sel.replace(/_[RL]$/, "")] ? " · " + LM_LABEL[sel.replace(/_[RL]$/, "")] : ""}</div><div class="num">${["x", "y", "z"].map((a, i) => `<div><label for="n${a}">${a} (cm)</label><input id="n${a}" type="number" step="0.5" value="${fix(LM[sel][i], 2)}"></div>`).join("")}</div>`;
  b.innerHTML = `<div class="row">${modes}</div><div class="row">${grp}<button id="clr">Bỏ chọn</button></div>` + body;
  $("clr").addEventListener("click", () => pick(null));
  $("grpSel").onchange = e => { if (e.target.value) setSel(GROUPS[e.target.value](), false); e.target.value = ""; };
  b.querySelectorAll("[data-mode]").forEach(x => x.addEventListener("click", () => setMode(x.dataset.mode)));
  if (S.size === 1) ["x", "y", "z"].forEach((a, i) => $("n" + a).addEventListener("change", e => {
    LM[sel][i] = +e.target.value; if (mirror && mirrorKey(sel)) { const k = mirrorKey(sel); LM[k] = [-LM[sel][0], LM[sel][1], LM[sel][2]]; }
    syncScene(); dirty(); commit(); renderPanel();
  }));
}
function renderPanelLight() { const m = $("smsg"); if (m) m.textContent = saveMsg; if (step === 2) { renderSel(); document.querySelectorAll("#lmrows tr").forEach(tr => { tr.classList.toggle("sel", S.has(tr.dataset.k)); const k = tr.dataset.k, c = tr.children; c[1].textContent = fix(LM[k][0]); c[2].textContent = fix(LM[k][1]); c[3].textContent = fix(LM[k][2]); }); } }
function wirePanel() {
  document.querySelectorAll("[data-more]").forEach(d => d.addEventListener("toggle", () => OPEN[d.dataset.more] = d.open));
  const on = (id, f) => { const e = $(id); if (e) e.addEventListener("click", f); };
  on("gOk", () => setGate(step, "ok")); on("gFix", () => setGate(step, "fix"));
  on("toStep2", () => go(2)); on("saveLM", saveLM); on("exportRig", exportRig);
  on("useRefJ", () => adoptGuestJoints());
  on("resetAuto", () => { LM = JSON.parse(JSON.stringify(DATA.auto.landmarks)); initFingers(LM, true); syncScene(); dirty(); commit(); renderPanel(); });
  Object.keys(TW_SEG).forEach(st => { const e = $("tw_" + st); if (e) e.addEventListener("change", () => { TW[st] = +e.value; syncScene(); dirty(); commit(); renderPanel(); }); });
  document.querySelectorAll("[data-tw]").forEach(b => b.addEventListener("click", () => { Object.keys(TW).forEach(st => TW[st] = +b.dataset.tw); syncScene(); dirty(); commit(); renderPanel(); }));
  const m = $("mir"); if (m) m.addEventListener("change", e => { mirror = e.target.checked; if (mirror) { for (const k of LM_ORDER) if (sideOf(k) === "R") LM[mirrorKey(k)] = [-LM[k][0], LM[k][1], LM[k][2]]; syncScene(); dirty(); commit(); } });
  const r = $("ref"); if (r) r.addEventListener("change", e => { showRef = e.target.checked; syncScene(); renderVopts(); });
  document.querySelectorAll("#lmrows tr").forEach(tr => tr.addEventListener("click", e => pick(tr.dataset.k, e.shiftKey || e.ctrlKey || e.metaKey)));
}
function renderSteps() { host.refresh(); }
function renderVbar() {}
function renderVopts() { host.refresh(); }
function showSkinFor() {
  if (!SK) return;
  if (step === 4) { strainOn = false; poseSkin(); paintSkin(); }
  if (step === 5) { poseSkin(); paintSkin(); }
}
function go(n) { step = n; if (n < 4) jointSel = null; try { showSkinFor(); } catch (e) { if (__err) __err('skin: ' + (e.message || e)); } if (n !== 2) { sel = null; S.clear(); } syncScene(); renderAll(); }
function renderAll() { renderSteps(); renderVopts(); renderPanel(); }


// ================================================================ M2: skin tự động + thử khớp
const NV = bodyV.length, TRI = DATA.body.tris, NT = TRI.length / 3;
const REFW = (() => { const r = Array.from({ length: NV }, () => ({})); for (const b in DATA.refW) { const [ix, wt] = DATA.refW[b]; ix.forEach((v, i) => r[v][b] = wt[i]); } return r; })();
let SK = null, skinBusy = false, skinStale = false, skinMs = 0;
let skinMode = "pro";   // "smart" = nhìn thấy xương + tách trái/phải; "classic" = gần nhất theo khoảng cách
const SIDE_X = 4;         // cm: đỉnh cách trục giữa hơn mức này chỉ nhận xương cùng bên
const segSide = n => /_R$/.test(n) ? -1 : /_L$/.test(n) ? 1 : 0;
const otherSide = (n, x) => { const sd = segSide(n); return sd !== 0 && Math.abs(x) > SIDE_X && sd * x < 0; };
const NORM = (() => { const g = bodyMesh.geometry; g.computeVertexNormals(); return g.attributes.normal.array; })();
function segHitsMesh(o, q, skip) {   // đoạn o→q có cắt tam giác nào của thân (bỏ tam giác chứa đỉnh skip) không
  const dx = q[0] - o[0], dy = q[1] - o[1], dz = q[2] - o[2];
  for (let t = 0; t < NT; t++) {
    const a = TRI[3 * t], b = TRI[3 * t + 1], c = TRI[3 * t + 2]; if (a === skip || b === skip || c === skip) continue;
    const A = bodyV[a], B = bodyV[b], C = bodyV[c];
    const e1x = B[0] - A[0], e1y = B[1] - A[1], e1z = B[2] - A[2], e2x = C[0] - A[0], e2y = C[1] - A[1], e2z = C[2] - A[2];
    const px = dy * e2z - dz * e2y, py = dz * e2x - dx * e2z, pz = dx * e2y - dy * e2x, det = e1x * px + e1y * py + e1z * pz;
    if (Math.abs(det) < 1e-9) continue; const inv = 1 / det, tx = o[0] - A[0], ty = o[1] - A[1], tz = o[2] - A[2];
    const u = (tx * px + ty * py + tz * pz) * inv; if (u < 0 || u > 1) continue;
    const qx = ty * e1z - tz * e1y, qy = tz * e1x - tx * e1z, qz = tx * e1y - ty * e1x, v = (dx * qx + dy * qy + dz * qz) * inv; if (v < 0 || u + v > 1) continue;
    const tt = (e2x * qx + e2y * qy + e2z * qz) * inv; if (tt > 0.02 && tt < 0.98) return true;
  }
  return false;
}
function closestOnSeg(p, a, b) {
  const ab0 = b[0] - a[0], ab1 = b[1] - a[1], ab2 = b[2] - a[2], l2 = ab0 * ab0 + ab1 * ab1 + ab2 * ab2;
  let t = l2 ? ((p[0] - a[0]) * ab0 + (p[1] - a[1]) * ab1 + (p[2] - a[2]) * ab2) / l2 : 0; t = Math.max(0, Math.min(1, t));
  return [a[0] + t * ab0, a[1] + t * ab1, a[2] + t * ab2];
}
let skinView = "dom", skinBone = null, refShown = "tool";
const noSkin = n => n === "root" || n === "Weapon" || /End_/.test(n) || /Finger3_/.test(n);
const mergeName = n => n.replace(/Twist\d+/, "");          // trọng số twist gộp về khớp đầu đoạn khi so với rig khách

// ---- skin mesh (màu theo đỉnh)
const skinGeo = new THREE.BufferGeometry();
skinGeo.setAttribute("position", new THREE.Float32BufferAttribute(DATA.body.verts.slice(), 3));
skinGeo.setAttribute("color", new THREE.Float32BufferAttribute(new Float32Array(NV * 3).fill(0.6), 3));
skinGeo.setIndex(DATA.body.tris); skinGeo.computeVertexNormals();
const skinMesh = new THREE.Mesh(skinGeo, new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide }));
skinMesh.visible = false; scene.add(skinMesh);
const skinWire = new THREE.LineSegments(new THREE.WireframeGeometry(skinGeo), new THREE.LineBasicMaterial({ color: 0x000000, transparent: true, opacity: .25 }));
skinWire.visible = false; scene.add(skinWire);

// ---- đoạn xương dùng cho skin (xương twist chia nhỏ đoạn chi)
function boneSegments(B) {
  const byN = {}, kids = {}; B.forEach(b => byN[b.name] = b);
  B.forEach(b => { if (b.parent) (kids[b.parent] = kids[b.parent] || []).push(b); });
  const segs = [], lerp = (a, b, t) => a.map((v, i) => v + (b[i] - v) * t);
  for (const b of B) {
    if (noSkin(b.name) || b.twist) continue;
    const ks = (kids[b.name] || []).filter(k => !k.twist && k.name !== "Weapon");
    let end = ks.length ? ks[0].pos : b.pos.slice();   // xương lá (Prop_M, váy): điểm seed, không kéo dài
    let leafExt = false;
    if (!ks.length && /^Ankle_/.test(b.name) && !CFG.toes) {   // bàn chân không có xương ngón: đoạn cổ chân → mũi chân (landmark ToesEnd nếu có)
      const t = LM["ToesEnd_" + b.name.slice(-1)]; end = t ? t.slice() : [b.pos[0], b.pos[1] * 0.3, b.pos[2] + 15]; leafExt = true;
    } else if (!ks.length && byN[b.parent] && (b.name === "Head_M" || /Finger1_/.test(b.name))) {   // lá thật của thân (rig không có HeadEnd / ngón 2-3): kéo dài theo hướng cha → xương, nếu không đoạn dài 0 bị phạt ×2,5 và không đỉnh nào chọn
      const pp = byN[b.parent].pos, f = b.name === "Head_M" ? 1.6 : 0.4; end = b.pos.map((v, i) => v + (v - pp[i]) * f); leafExt = true; }
    const a0 = /^Hip_/.test(b.name) ? lerp(b.pos, end, 0.35) : /^Scapula_/.test(b.name) ? lerp(b.pos, end, 0.4) : b.pos;   // phần trên đùi thuộc vùng xương hông
    const st = b.name.replace(/_[RL]$/, ""), sd = b.name.slice(-1), n = TW_SEG[st] ? TW[st] : 0;
    if (!n) { segs.push({ name: b.name, a: a0, b: end, bias: ks.length || leafExt ? 1 : (/Finger|End_/.test(b.name) ? 1 : 2.5) }); continue; }
    segs.push({ name: b.name, a: a0, b: lerp(a0, end, 1 / (n + 1)) });
    for (let i = 1; i <= n; i++) segs.push({ name: st + "Twist" + i + "_" + sd, a: lerp(a0, end, i / (n + 1)), b: lerp(a0, end, (i + 1) / (n + 1)) });
  }
  return segs;
}
function distSeg(p, a, b) {
  const ab0 = b[0] - a[0], ab1 = b[1] - a[1], ab2 = b[2] - a[2], l2 = ab0 * ab0 + ab1 * ab1 + ab2 * ab2;
  let t = l2 ? ((p[0] - a[0]) * ab0 + (p[1] - a[1]) * ab1 + (p[2] - a[2]) * ab2) / l2 : 0; t = Math.max(0, Math.min(1, t));
  return Math.hypot(p[0] - a[0] - t * ab0, p[1] - a[1] - t * ab1, p[2] - a[2] - t * ab2);
}

// ---- cotan Laplacian + diện tích (một lần)
const LAP = (() => {
  const wm = new Map(), area = new Float64Array(NV);
  const add = (i, j, w) => { const a = Math.min(i, j), b = Math.max(i, j), k = a * NV + b; wm.set(k, (wm.get(k) || 0) + w); };
  for (let t = 0; t < NT; t++) {
    const id = [TRI[3 * t], TRI[3 * t + 1], TRI[3 * t + 2]], P = id.map(i => bodyV[i]);
    for (let c = 0; c < 3; c++) {
      const v = P[c], p = P[(c + 1) % 3], q = P[(c + 2) % 3], u = [p[0] - v[0], p[1] - v[1], p[2] - v[2]], w = [q[0] - v[0], q[1] - v[1], q[2] - v[2]];
      const cr = [u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0]], cl = Math.hypot(...cr) || 1e-9;
      add(id[(c + 1) % 3], id[(c + 2) % 3], 0.5 * (u[0] * w[0] + u[1] * w[1] + u[2] * w[2]) / cl);
      if (c === 0) { const A = cl / 2; id.forEach(i => area[i] += A / 3); }
    }
  }
  const deg = new Int32Array(NV + 1); for (const k of wm.keys()) { const i = Math.floor(k / NV), j = k % NV; deg[i + 1]++; deg[j + 1]++; }
  for (let i = 0; i < NV; i++) deg[i + 1] += deg[i];
  const fill = deg.slice(0, NV), nb = new Int32Array(deg[NV]), nw = new Float64Array(deg[NV]);
  for (const [k, w0] of wm) { const i = Math.floor(k / NV), j = k % NV, w = Math.max(w0, 1e-3); nb[fill[i]] = j; nw[fill[i]++] = w; nb[fill[j]] = i; nw[fill[j]++] = w; }
  const edges = []; for (const k of wm.keys()) edges.push([Math.floor(k / NV), k % NV]);
  return { start: deg, nb, nw, area, edges };
})();
const EDGE_L0 = LAP.edges.map(([i, j]) => dist(bodyV[i], bodyV[j]) || 1e-6);

let SK_INFO = null;
function treeHops(B) {   // số bước giữa hai xương trên cây xương (xương twist tính như khớp đầu đoạn)
  const par = {}; B.forEach(b => par[b.name] = b.parent); const base = n => n.replace(/Twist\d+/, ""), memo = new Map();
  const anc = n => { const o = []; while (n) { o.push(n); n = par[n]; } return o; };
  return (a, b) => { a = base(a); b = base(b); const key = a + "|" + b; if (memo.has(key)) return memo.get(key);
    const A = anc(a), C = anc(b); let h = 99; for (let i = 0; i < A.length; i++) { const j = C.indexOf(A[i]); if (j >= 0) { h = i + j; break; } } memo.set(key, h); return h; };
}
async function computeSkin() {
  if (skinBusy) return; skinBusy = true; window.__adoptNote = ""; const t0 = performance.now(); renderPanel();
  await new Promise(r => setTimeout(r, 20));
  const B = buildSkeleton(LM), segs = boneSegments(B), nb = segs.length, C = 1.0;
  const dmin = new Float64Array(NV), near = new Int16Array(NV);
  const smart = skinMode !== "classic"; let nVis = 0, nFall = 0;
  for (let i = 0; i < NV; i++) {
    const v = bodyV[i], cand = [];
    for (let j = 0; j < nb; j++) { if (smart && otherSide(segs[j].name, v[0])) continue; const d = distSeg(v, segs[j].a, segs[j].b); cand.push([d * (segs[j].bias || 1), j, d]); }
    cand.sort((x, y) => x[0] - y[0]);
    let pick = cand[0];
    if (smart) {
      pick = null;
      for (const c of cand.slice(0, 6)) {
        const q = closestOnSeg(v, segs[c[1]].a, segs[c[1]].b), dl = Math.hypot(q[0] - v[0], q[1] - v[1], q[2] - v[2]) || 1e-9;
        const inward = ((q[0] - v[0]) * NORM[3 * i] + (q[1] - v[1]) * NORM[3 * i + 1] + (q[2] - v[2]) * NORM[3 * i + 2]) / dl < 0.5;
        if (inward && !segHitsMesh(v, q, i)) { pick = c; break; }
      }
      if (pick) nVis++; else { pick = cand[0]; nFall++; }
    }
    near[i] = pick[1]; dmin[i] = Math.max(pick[2], 0.5);
  }
  SK_INFO = { mode: skinMode, visible: nVis, fallback: nFall };
  const AH = new Float64Array(NV); for (let i = 0; i < NV; i++) AH[i] = LAP.area[i] / (dmin[i] * dmin[i]) * C;
  const Wt = new Float32Array(nb * NV), w = new Float64Array(NV), p = new Float64Array(NV);
  const { start, nb: nbr, nw } = LAP;
  for (let j = 0; j < nb; j++) {
    for (let i = 0; i < NV; i++) { p[i] = near[i] === j ? 1 : 0; w[i] = p[i]; }
    for (let it = 0; it < 200; it++) {
      let mx = 0;
      for (let i = 0; i < NV; i++) {
        let sw = 0, sx = 0; for (let e = start[i]; e < start[i + 1]; e++) { sw += nw[e]; sx += nw[e] * w[nbr[e]]; }
        const nv = (AH[i] * p[i] + sx) / (AH[i] + sw), d = Math.abs(nv - w[i]); if (d > mx) mx = d; w[i] = nv;
      }
      if (mx < 1e-4) break;
    }
    for (let i = 0; i < NV; i++) Wt[j * NV + i] = w[i];
    if (j % 8 === 7) await new Promise(r => setTimeout(r, 0));
  }
  const names = segs.map(s => s.name), I = new Uint16Array(NV * 4), W = new Float32Array(NV * 4), hops = treeHops(B), pro = skinMode === "pro";
  for (let i = 0; i < NV; i++) {
    const a = []; for (let j = 0; j < nb; j++) { if (skinMode !== "classic" && (otherSide(segs[j].name, bodyV[i][0]) || (j !== near[i] && distSeg(bodyV[i], segs[j].a, segs[j].b) > 2.5 * dmin[i] + 12))) continue; a.push([j, Wt[j * NV + i]]); }
    a.sort((x, y) => y[1] - x[1]);
    if (pro && a.length) { const dom = segs[a[0][0]].name; for (let k = a.length - 1; k > 0; k--) if (hops(segs[a[k][0]].name, dom) > 2 || a[k][1] < 0.03) a.splice(k, 1); }   // cấp cao: chỉ xương gần xương trội ≤ 2 bước
    const top = a.slice(0, 4).filter(x => x[1] > 0.01), s = top.reduce((q, x) => q + x[1], 0) || 1;
    top.forEach((x, k) => { I[i * 4 + k] = x[0]; W[i * 4 + k] = x[1] / s; });
  }
  SK = { names, idx: Object.fromEntries(names.map((n, i) => [n, i])), I, W, full: null, nb, LMsnap: JSON.stringify({ LM, TW }) };
  SK.full = denseFrom(I, W, nb); skinUndo = []; skinRedo = []; skinStale = false; skinBusy = false; skinMs = performance.now() - t0; if (!skinBone) skinBone = names[0]; setTimeout(scheduleSkinSave, 0);
  try { SK_TEST = skinSelfTest(); } catch (e) { SK_TEST = { rows: [["warn", "Tự kiểm lỗi", String(e.message || e)]], leaks: [], t: Date.now() }; }
  paintSkin(); syncScene(); renderPanel();
}
function vw(i) { const o = {}; for (let k = 0; k < 4; k++) { const w = SK.W[i * 4 + k]; if (w > 0) o[SK.names[SK.I[i * 4 + k]]] = w; } return o; }
function vwMerged(i) { const o = {}; const r = vw(i); for (const n in r) o[mergeName(n)] = (o[mergeName(n)] || 0) + r[n]; return o; }
function skinStats() {
  let same = 0, l1 = 0, over = 0, infl = 0, bone = {}, n = 0;
  for (let i = 0; i < NV; i++) {
    const a = vwMerged(i), r = REFW[i]; let da = "", dw = -1, dr = "", drw = -1;
    for (const k in a) if (a[k] > dw) { dw = a[k]; da = k; } for (const k in r) if (r[k] > drw) { drw = r[k]; dr = k; }
    if (da === dr) same++;
    let s = 0; const ks = new Set([...Object.keys(a), ...Object.keys(r)]); ks.forEach(k => s += Math.abs((a[k] || 0) - (r[k] || 0)));
    l1 += s / 2; (bone[dr] = bone[dr] || []).push(s / 2); infl += Object.keys(vw(i)).length; n++;
  }
  const worst = Object.entries(bone).map(([k, v]) => [k, v.reduce((a, b) => a + b, 0) / v.length, v.length]).filter(x => x[2] >= 8).sort((a, b) => b[1] - a[1]).slice(0, 8);
  return { same: same / n, l1: l1 / n, infl: infl / n, worst };
}

// ---- màu
const RAMP = [[0, [0.10, 0.17, 0.42]], [0.25, [0.16, 0.5, 0.72]], [0.5, [0.24, 0.7, 0.44]], [0.75, [0.91, 0.79, 0.23]], [1, [0.84, 0.2, 0.17]]];
function ramp(t) { t = Math.max(0, Math.min(1, t)); for (let k = 1; k < RAMP.length; k++) if (t <= RAMP[k][0]) { const [t0, c0] = RAMP[k - 1], [t1, c1] = RAMP[k], f = (t - t0) / (t1 - t0); return c0.map((v, i) => v + (c1[i] - v) * f); } return RAMP[4][1]; }
const hueCol = (n, nb) => { const c = new THREE.Color(); c.setHSL(((n * 137.5) % 360) / 360, 0.62, 0.55); return [c.r, c.g, c.b]; };
let strainOn = false, STR = null;
function paintSkin() {
  if (!SK) return; const col = skinGeo.attributes.color.array;
  const bone = skinBone, bm = n => n === bone;
  for (let i = 0; i < NV; i++) {
    let c;
    if (strainOn && STR) c = ramp(STR[i] / 0.4);
    else if (step === 5) c = [0.62, 0.66, 0.74];
    else if (skinView === "dom") { const r = vw(i); let bn = "", bw = -1; for (const k in r) if (r[k] > bw) { bw = r[k]; bn = k; } c = hueCol(SK.idx[bn] || 0); }
    else {
      const a = vwMerged(i), r = REFW[i], key = mergeName(bone), tw = bone !== key ? 0 : 1;
      const wt = skinView === "ref" ? (r[key] || 0) : skinView === "diff" ? Math.abs((a[key] || 0) - (r[key] || 0)) : (vw(i)[bone] || 0);
      c = ramp(skinView === "diff" ? wt * 2 : wt);
    }
    col[i * 3] = c[0]; col[i * 3 + 1] = c[1]; col[i * 3 + 2] = c[2];
  }
  skinGeo.attributes.color.needsUpdate = true;
}

// ---- FK + LBS để thử khớp
const POSE = {}, poseOpt = { twist: true };
const ROT = (r, a, b) => new THREE.Matrix4().makeRotationX(r * Math.PI / 180).multiply(new THREE.Matrix4().makeRotationY(a * Math.PI / 180)).multiply(new THREE.Matrix4().makeRotationZ(b * Math.PI / 180));
function boneFrames(B) {
  const byN = {}, kids = {}; B.forEach(b => byN[b.name] = b); B.forEach(b => { if (b.parent) (kids[b.parent] = kids[b.parent] || []).push(b); });
  const F = {};
  for (const b of B) {
    let d;
    if (b.twist) { const [s0, s1] = b.twist.segment; d = byN[s1].pos.map((v, i) => v - byN[s0].pos[i]); }
    else { const ks = (kids[b.name] || []).filter(k => !k.twist && k.name !== "Weapon"); d = ks.length ? ks[0].pos.map((v, i) => v - b.pos[i]) : (b.parent && byN[b.parent] ? b.pos.map((v, i) => v - byN[b.parent].pos[i]) : [0, 1, 0]); }
    const x = new THREE.Vector3(...d).normalize(); if (x.lengthSq() < 1e-6) x.set(0, 1, 0);
    const ref = Math.abs(x.y) > 0.9 ? new THREE.Vector3(0, 0, 1) : new THREE.Vector3(0, 1, 0);
    const z = new THREE.Vector3().crossVectors(x, ref).normalize(), y = new THREE.Vector3().crossVectors(z, x);
    F[b.name] = new THREE.Matrix4().makeBasis(x, y, z);
  }
  return F;
}
function poseMats(B) {
  const F = boneFrames(B), W = {};
  for (const b of B) {
    const P = POSE[b.name] || [0, 0, 0]; let r = P[0];
    if (b.twist && poseOpt.twist) r += b.twist.factor * ((POSE[b.twist.source] || [0, 0, 0])[0]);
    const p = new THREE.Vector3(...b.pos), Fm = F[b.name], R = ROT(r, P[1], P[2]);
    const loc = new THREE.Matrix4().makeTranslation(p.x, p.y, p.z).multiply(Fm).multiply(R).multiply(Fm.clone().invert()).multiply(new THREE.Matrix4().makeTranslation(-p.x, -p.y, -p.z));
    W[b.name] = b.parent && W[b.parent] ? W[b.parent].clone().multiply(loc) : loc;
  }
  return W;
}
function posedBones(B) { const W = poseMats(B), o = {}; B.forEach(b => o[b.name] = new THREE.Vector3(...b.pos).applyMatrix4(W[b.name]).toArray()); return o; }
const CLOTH_K = 6;
const CLOTH_MAP = clothMeshes.map(m => {   // đỉnh quần áo → 6 đỉnh thân gần nhất (cùng bên trái/phải), trọng số 1/(d+0.5)²
  const a = m.geometry.attributes.position.array, n = a.length / 3, nn = new Int32Array(n * CLOTH_K), nw = new Float32Array(n * CLOTH_K);
  for (let i = 0; i < n; i++) { const x = a[3 * i], y = a[3 * i + 1], z = a[3 * i + 2], c = [];
    for (let j = 0; j < bodyV.length; j++) { const b = bodyV[j]; if (x * b[0] < 0 && Math.abs(x) > SIDE_X && Math.abs(b[0]) > SIDE_X) continue; c.push([(x - b[0]) ** 2 + (y - b[1]) ** 2 + (z - b[2]) ** 2, j]); }
    c.sort((p, q) => p[0] - q[0]);
    for (let k = 0; k < CLOTH_K; k++) { const e = c[Math.min(k, c.length - 1)]; nn[i * CLOTH_K + k] = e[1]; nw[i * CLOTH_K + k] = 1 / (Math.sqrt(e[0]) + 0.5) ** 2; } }
  return { rest: Float32Array.from(a), nn, nw };
});
const CLOTH_SMOOTH = 0;   // 0 = không làm mượt: thử 3 lượt (2026-10-26) làm đỉnh trùng nhau ở đường may tách rời (max ×156000) và Ngồi xổm/Xoay đùi xấu hơn
const CLOTH_ADJ = clothMeshes.map(m => { const idx = m.geometry.index.array, n = m.geometry.attributes.position.count, adj = Array.from({ length: n }, () => new Set());
  for (let t = 0; t < idx.length; t += 3) for (let e = 0; e < 3; e++) { const x = idx[t + e], y = idx[t + (e + 1) % 3]; adj[x].add(y); adj[y].add(x); }
  return adj.map(s => [...s]); });
const CLOTH_ISL = CLOTH_ADJ.map(adj => { const seen = new Uint8Array(adj.length), out = [];
  for (let i = 0; i < adj.length; i++) { if (seen[i]) continue; const q = [i], isl = []; seen[i] = 1;
    while (q.length) { const v = q.pop(); isl.push(v); adj[v].forEach(u => { if (!seen[u]) { seen[u] = 1; q.push(u); } }); } out.push(isl); }
  return out; });
const smooth01 = (a, b, x) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
function applySkirt(c, cur) {
  const rest = CLOTH_MAP[c].rest, ry = LM.Root_M[1], ky = LM.Knee_R[1], sy = LM.Spine1_M[1];
  const iR = SK.idx.Root_M, iHR = SK.idx.Hip_R, iHL = SK.idx.Hip_L; if (iR === undefined || iHR === undefined || iHL === undefined) return;
  let n = 0;
  for (const isl of CLOTH_ISL[c]) {
    let y0 = 1e9, y1 = -1e9, x1 = 0; isl.forEach(i => { y0 = Math.min(y0, rest[3 * i + 1]); y1 = Math.max(y1, rest[3 * i + 1]); x1 = Math.max(x1, Math.abs(rest[3 * i])); });
    const cy = (y0 + y1) / 2; if (!(cy > ky - 3 && cy < sy + 10 && x1 < 0.3 * (LM.Shoulder_L[0] - LM.Shoulder_R[0]))) continue;
    for (const i of isl) {
      const y = rest[3 * i + 1], x = rest[3 * i], u = smooth01(ry + 8, ry - 8, y);   // 0 = theo thân, 1 = theo vùng
      if (u <= 0) continue;
      const h = 0.55 * Math.max(0, Math.min(1, (ry - y) / (ry - ky))), s = 0.5 + 0.5 * Math.max(-1, Math.min(1, x / 8));
      const reg = new Map([[iR, 1 - h], [iHR, h * (1 - s)], [iHL, h * s]]), o = new Map();
      cur[i].forEach((w, b) => o.set(b, w * (1 - u))); reg.forEach((w, b) => o.set(b, (o.get(b) || 0) + w * u));
      cur[i] = o; n++;
    }
  }
  return n;
}
function clothWeights(c) {   // mỗi đỉnh quần áo: 4 xương mạnh nhất; 6 đỉnh thân gần nhất → (tuỳ chọn CLOTH_SMOOTH) làm mượt trên lưới quần áo
  const { nn, nw } = CLOTH_MAP[c], n = nn.length / CLOTH_K, adj = CLOTH_ADJ[c];
  let cur = Array.from({ length: n }, (_, i) => { const acc = new Map(); let tot = 0;
    for (let k = 0; k < CLOTH_K; k++) { const j = nn[i * CLOTH_K + k], wk = nw[i * CLOTH_K + k]; tot += wk;
      for (let m = 0; m < 4; m++) { const w = SK.W[j * 4 + m]; if (w > 0) acc.set(SK.I[j * 4 + m], (acc.get(SK.I[j * 4 + m]) || 0) + w * wk); } }
    acc.forEach((w, b) => acc.set(b, w / tot)); return acc; });
  { const rs = CLOTH_MAP[c].rest;   // đảo nằm trọn một bên trục giữa (bao tay, vòng ống chân…): bỏ xương bên kia dù đỉnh sát trục (kNN thân ở đáy chậu trộn cả hai chân)
    for (const isl of CLOTH_ISL[c]) { let mn = 1e9, mx = -1e9; isl.forEach(i => { mn = Math.min(mn, rs[3 * i]); mx = Math.max(mx, rs[3 * i]); });
      const side = mn >= -0.5 ? 1 : mx <= 0.5 ? -1 : 0; if (!side) continue;
      isl.forEach(i => { const m = cur[i]; let keep = 0; m.forEach((w, b) => { if (segSide(SK.names[b]) * side >= 0) keep += w; });
        if (keep <= 0.05) return; const o = new Map(); m.forEach((w, b) => { if (segSide(SK.names[b]) * side >= 0) o.set(b, w / keep); }); cur[i] = o; }); } }
  if (CFG.clothSkirt) applySkirt(c, cur);
  for (let it = 0; it < CLOTH_SMOOTH; it++) cur = cur.map((m, i) => { const o = new Map(); m.forEach((w, b) => o.set(b, w * 0.5));
    const nb = adj[i]; if (nb.length) { const f = 0.5 / nb.length; nb.forEach(j => cur[j].forEach((w, b) => o.set(b, (o.get(b) || 0) + w * f))); } else m.forEach((w, b) => o.set(b, w * 2));
    return o; });
  return cur.map(m => { const top = [...m.entries()].sort((p, q) => q[1] - p[1]).slice(0, 4), sum = top.reduce((s, e) => s + e[1], 0) || 1; return top.map(([b, w]) => [b, w / sum]); });
}
function poseCloth(M) {
  clothMeshes.forEach((m, c) => {
    const g = m.geometry, pos = g.attributes.position.array, { rest } = CLOTH_MAP[c], v = new THREE.Vector3(), o = new THREE.Vector3();
    const CW = clothWeights(c);
    for (let i = 0; i < rest.length / 3; i++) { o.set(0, 0, 0);
      for (const [b, w] of CW[i]) { v.set(rest[3 * i], rest[3 * i + 1], rest[3 * i + 2]).applyMatrix4(M[b]); o.addScaledVector(v, w); }
      pos[3 * i] = o.x; pos[3 * i + 1] = o.y; pos[3 * i + 2] = o.z; }
    g.attributes.position.needsUpdate = true; g.computeVertexNormals(); g.computeBoundingSphere();
    m.userData.wire.geometry.dispose(); m.userData.wire.geometry = new THREE.WireframeGeometry(g);
  });
}
function poseSkin() {
  if (!SK) return null;
  const B = buildSkeleton(LM), W = poseMats(B), pos = skinGeo.attributes.position.array, v = new THREE.Vector3(), o = new THREE.Vector3();
  const IDENT = new THREE.Matrix4(), M = SK.names.map(n => W[n] || IDENT);   // skin đã lưu có xương không còn trong bộ xương hiện tại: coi như đứng yên, không làm văng lỗi
  for (let i = 0; i < NV; i++) {
    o.set(0, 0, 0);
    for (let k = 0; k < 4; k++) { const w = SK.W[i * 4 + k]; if (w <= 0) continue; v.set(...bodyV[i]).applyMatrix4(M[SK.I[i * 4 + k]]); o.addScaledVector(v, w); }
    pos[i * 3] = o.x; pos[i * 3 + 1] = o.y; pos[i * 3 + 2] = o.z;
  }
  try { poseCloth(M); } catch (e) { if (__err) __err('quần áo: ' + (e.message || e)); }
  skinGeo.attributes.position.needsUpdate = true; skinGeo.computeVertexNormals(); skinGeo.computeBoundingSphere(); skinGeo.computeBoundingBox(); skinWire.geometry.dispose(); skinWire.geometry = new THREE.WireframeGeometry(skinGeo);
  const sum = new Float64Array(NV), cnt = new Int32Array(NV);
  LAP.edges.forEach(([i, j], e) => { const l = Math.hypot(pos[3 * i] - pos[3 * j], pos[3 * i + 1] - pos[3 * j + 1], pos[3 * i + 2] - pos[3 * j + 2]), s = Math.abs(l / EDGE_L0[e] - 1); sum[i] += s; sum[j] += s; cnt[i]++; cnt[j]++; });
  STR = new Float32Array(NV); for (let i = 0; i < NV; i++) STR[i] = cnt[i] ? sum[i] / cnt[i] : 0;
  return STR;
}
let SK_TEST = null, testTimer = null;
function runSelfTest() {
  try { SK_TEST = skinSelfTest(); } catch (e) { SK_TEST = { rows: [["bad", "Tự kiểm lỗi", String(e.message || e)]], leaks: [], t: Date.now(), ms: 0 }; }
  paintSkin(); syncScene(); if (step === 4) renderPanel();
}
const scheduleSelfTest = () => { clearTimeout(testTimer); testTimer = setTimeout(() => { if (SK && step === 4 && !painting) runSelfTest(); }, 1500); };
function skinSelfTest() {
  if (!SK) return null;
  const T0 = performance.now();
  const rows = [], B = buildSkeleton(LM), segs = boneSegments(B), keep = JSON.stringify(POSE), kt = poseOpt.twist; poseOpt.twist = true;
  const kids = {}; B.forEach(b => { if (b.parent) (kids[b.parent] = kids[b.parent] || []).push(b.name); });
  const sub = n => { const o = new Set([n]), q = [n]; while (q.length) for (const k of kids[q.pop()] || []) { o.add(k); q.push(k); } return o; };
  // 1. đếm đỉnh / xương
  const cnt = new Int32Array(SK.names.length); for (let i = 0; i < NV; i++) for (let k = 0; k < 4; k++) if (SK.W[i * 4 + k] > 0.05) cnt[SK.I[i * 4 + k]]++;
  const dead = SK.names.filter((n, j) => cnt[j] < 4 && !/Finger\d_|End_/.test(n));
  rows.push([dead.length ? "bad" : "ok", "Mọi xương đều có skin", dead.length ? "ít hơn 4 đỉnh: " + dead.join(", ") : `xương ít nhất ${Math.min(...[...cnt].filter((c, j) => !/Finger\d_|End_/.test(SK.names[j])))} đỉnh`]);
  // 2. chéo trái/phải
  let cross = 0; for (let i = 0; i < NV; i++) for (let k = 0; k < 4; k++) if (SK.W[i * 4 + k] > 0.02 && otherSide(SK.names[SK.I[i * 4 + k]], bodyV[i][0])) cross++;
  rows.push([cross ? "bad" : "ok", "Không lẫn xương trái/phải", cross ? cross + " ảnh hưởng chéo bên" : "0"]);
  // 2b. xương xa trên cây: ảnh hưởng > 0,02 của xương cách xương trội > 2 bước (vai → đầu)
  { const hp = treeHops(B); let far = 0; const by = {};
    for (let i = 0; i < NV; i++) { let dom = -1, dw = -1; for (let k = 0; k < 4; k++) if (SK.W[i * 4 + k] > dw) { dw = SK.W[i * 4 + k]; dom = SK.I[i * 4 + k]; }
      for (let k = 0; k < 4; k++) { const w = SK.W[i * 4 + k]; if (w <= 0.02 || SK.I[i * 4 + k] === dom) continue; if (hp(SK.names[SK.I[i * 4 + k]], SK.names[dom]) > 2) { far++; const key = SK.names[SK.I[i * 4 + k]] + " ← " + SK.names[dom]; by[key] = (by[key] || 0) + 1; } } }
    rows.push([far ? "warn" : "ok", "Không ảnh hưởng xa trên cây xương", far ? far + " ảnh hưởng cách > 2 bước: " + Object.entries(by).sort((a, b) => b[1] - a[1]).slice(0, 3).map(e => e[0] + " ×" + e[1]).join(", ") : "mọi ảnh hưởng ≤ 2 bước (vai không kéo đầu)"]); }
  // 3. rò rỉ: xoay từng khớp 50°
  const leaks = [], zero = [], rest = DATA.body.verts, pos = skinGeo.attributes.position.array, joints = B.filter(b => !b.twist && b.name !== "root" && (kids[b.name] || []).length);
  for (const b of joints) {
    const S = sub(b.name), mine = segs.filter(g => S.has(g.name) || S.has(g.name.replace(/Twist\d+/, "")));
    let worst = 0, wI = -1, moved = 0;
    for (const ax of [[0, 0, 50], [0, 50, 0]]) {
      for (const k in POSE) delete POSE[k]; POSE[b.name] = ax.slice(); poseSkin();
      for (let i = 0; i < NV; i++) { const d = Math.hypot(pos[3 * i] - rest[3 * i], pos[3 * i + 1] - rest[3 * i + 1], pos[3 * i + 2] - rest[3 * i + 2]); if (d < 1) continue; moved++;
        let near = 1e9, all = 1e9; for (const g of segs) { const dg = distSeg(bodyV[i], g.a, g.b); all = Math.min(all, dg); if (mine.includes(g)) near = Math.min(near, dg); }
        if (near > 15 && near > 1.8 * all + 2 && d > worst) { worst = d; wI = i; } }   // rò rỉ = đỉnh dịch dù gần xương KHÁC nhánh hơn hẳn (mesh vươn ra ngoài đoạn xương như gót chân, đỉnh đầu không tính)
    }
    if (moved < 3 && !/Neck|Scapula/.test(b.name)) zero.push(b.name);
    if (worst > 1) leaks.push([b.name, worst, wI]);
  }
  leaks.sort((a, c) => c[1] - a[1]);
  rows.push([!leaks.length ? "ok" : leaks[0][1] > 4 ? "bad" : "warn", "Không rò rỉ sang phần khác", leaks.length ? leaks.slice(0, 3).map(l => `${l[0]} kéo đỉnh #${l[2]} xa nhánh con ${fix(l[1])} cm`).join("; ") : "xoay từng khớp 50°: không đỉnh nào xa nhánh con bị kéo"]);
  rows.push([zero.length ? "bad" : "ok", "Xoay khớp nào cũng làm mesh dịch", zero.length ? "không đỉnh nào dịch: " + zero.join(", ") : "mọi khớp có đỉnh theo"]);
  // 4. cạnh giãn ở bộ pose thử
  let worstP = "", worstPct = 0; const names = ["Giơ tay lên", "Gập khuỷu", "Gập hông", "Ngồi xổm", "Xoay đùi", "Vặn thân", "Cúi cổ"];
  for (const n of names) { for (const k in POSE) delete POSE[k]; for (const k in PRESETS[n]) POSE[k] = PRESETS[n][k].slice(); poseSkin(); const sm = strainSummary(); if (sm.pct > worstPct) { worstPct = sm.pct; worstP = n; } }
  rows.push([worstPct < 1 ? "ok" : worstPct < 3 ? "warn" : "bad", "Cạnh giãn/co quá 25% ở pose thử", worstPct ? `${fix(worstPct)}% đỉnh (${worstP})` : "0% ở 7 pose"]);
  // 5. quần áo
  if (clothMeshes.length) { let wc = 0, wn = "";
    clothMeshes.forEach((m, c) => { const idx = m.geometry.index.array, rs = CLOTH_MAP[c].rest;
      for (const n of ["Gập hông", "Ngồi xổm", "Xoay đùi", "Giơ tay lên"]) { for (const k in POSE) delete POSE[k]; for (const k in PRESETS[n]) POSE[k] = PRESETS[n][k].slice(); poseSkin(); const q = m.geometry.attributes.position.array; let bad = 0;
        for (let t = 0; t < idx.length; t += 3) for (let e = 0; e < 3; e++) { const a = idx[t + e], b = idx[t + (e + 1) % 3], l0 = Math.hypot(rs[3 * a] - rs[3 * b], rs[3 * a + 1] - rs[3 * b + 1], rs[3 * a + 2] - rs[3 * b + 2]); if (l0 < 1e-3) continue; const r = Math.hypot(q[3 * a] - q[3 * b], q[3 * a + 1] - q[3 * b + 1], q[3 * a + 2] - q[3 * b + 2]) / l0; if (r > 2.5 || r < 0.4) bad++; }
        const pct = bad / idx.length * 300; if (pct > wc) { wc = pct; wn = n; } } });
    rows.push([wc < 0.3 ? "ok" : wc < 1 ? "warn" : "bad", "Quần áo không bị kéo giãn", wc ? `${fix(wc, 2)}% cạnh >2,5× (${wn})` : "0%"]); }
  for (const k in POSE) delete POSE[k]; Object.assign(POSE, JSON.parse(keep)); poseOpt.twist = kt; poseSkin();
  return { rows, leaks, t: Date.now(), ms: Math.round(performance.now() - T0) };
}
function strainSummary() {
  if (!STR) return null; let bad = 0; const by = {};
  for (let i = 0; i < NV; i++) if (STR[i] > 0.25) { bad++; const r = vwMerged(i); let bn = "", bw = -1; for (const k in r) if (r[k] > bw) { bw = r[k]; bn = k; } by[bn] = (by[bn] || 0) + 1; }
  return { pct: bad / NV * 100, worst: Object.entries(by).sort((a, b) => b[1] - a[1]).slice(0, 4) };
}
const PRESETS = {
  "Giơ tay lên": { Shoulder_R: [0, 0, 100], Shoulder_L: [0, 0, 100] },
  "Hạ tay": { Shoulder_R: [0, 0, -80], Shoulder_L: [0, 0, -80] },
  "Gập khuỷu": { Elbow_R: [0, 0, -100], Elbow_L: [0, 0, -100] },
  "Xoay cẳng tay": { Wrist_R: [120, 0, 0], Wrist_L: [120, 0, 0] },
  "Xoay cánh tay": { Shoulder_R: [90, 0, 0], Shoulder_L: [90, 0, 0] },
  "Nắm tay": Object.fromEntries(["R", "L"].flatMap(s => FINGERS.flatMap(f => FSEG.filter(i => i < 3).map(i => [f + "Finger" + i + "_" + s, [0, 0, -70]])))),
  "Gập hông": { Hip_R: [0, 0, 80], Hip_L: [0, 0, 80] },
  "Ngồi xổm": { Hip_R: [0, 0, 80], Hip_L: [0, 0, 80], Knee_R: [0, 0, -120], Knee_L: [0, 0, -120], Ankle_R: [0, 0, 40], Ankle_L: [0, 0, 40] },
  "Xoay đùi": { Hip_R: [60, 0, 0], Hip_L: [60, 0, 0] },
  "Vặn thân": { Spine1_M: [35, 0, 0], Chest_M: [35, 0, 0] },
  "Gập thân": { Spine1_M: [0, 0, 40], Chest_M: [0, 0, 30] },
  "Cúi cổ": { Neck_M: [0, 0, 35] },
};
function setPose(o) { for (const k in POSE) delete POSE[k]; for (const k in o) POSE[k] = o[k].slice(); applyPose(); }
function applyPose() { if (!SK) return; poseSkin(); if (strainOn) paintSkin(); syncScene(); }
function batteryRun() {
  const keep = JSON.stringify(POSE), kt = poseOpt.twist, rows = [];
  for (const [name, p] of Object.entries(PRESETS)) {
    for (const tw of (name === "Xoay cẳng tay" || name === "Xoay cánh tay" || name === "Xoay đùi") ? [true, false] : [true]) {
      poseOpt.twist = tw; for (const k in POSE) delete POSE[k]; for (const k in p) POSE[k] = p[k].slice(); poseSkin(); const s = strainSummary();
      rows.push([name + (tw ? "" : " (twist tắt)"), s.pct, s.worst.map(x => x[0]).join(", ")]);
    }
  }
  poseOpt.twist = kt; for (const k in POSE) delete POSE[k]; Object.assign(POSE, JSON.parse(keep)); poseSkin(); return rows;
}
let battery = null;

// ---- bảng điều khiển bước 4, 5
function poseSection() {
  const pres = ["Giơ tay lên", "Hạ tay", "Gập khuỷu", "Xoay cẳng tay", "Gập hông", "Ngồi xổm"].map(n => `<button data-spre="${n}">${n}</button>`).join("");
  return more("m4pose", "Xoay thử để lộ phần khuất", `<div class="chips">${pres}<button id="spReset">Về pose gốc</button></div>
    <div class="sub">Click một joint trên viewport rồi kéo thanh xoay ở góc phải.</div>
    <div class="row"><select id="spBone" aria-label="Chọn xương xoay">${buildSkeleton(LM).filter(b => !b.twist && b.name !== "root").map(b => `<option ${b.name === poseBone ? "selected" : ""}>${b.name}</option>`).join("")}</select><button id="spClr">Về 0</button>
    <label class="t"><input type="checkbox" id="spTw" ${poseOpt.twist ? "checked" : ""}> Dẫn động twist</label></div>`);
}
function wirePoseSection() {
  const on = (id, f) => { const e = $(id); if (e) e.addEventListener("click", f); };
  document.querySelectorAll("[data-spre]").forEach(b => b.addEventListener("click", () => { setPose(PRESETS[b.dataset.spre]); renderPanel(); }));
  on("spReset", () => { setPose({}); renderPanel(); });
  const bs = $("spBone"); if (!bs) return;
  bs.onchange = e => { poseBone = e.target.value; jointSel = poseBone; renderPanel(); };
  on("spClr", () => { delete POSE[poseBone]; applyPose(); renderPanel(); });
  $("spTw").onchange = e => { poseOpt.twist = e.target.checked; applyPose(); renderPanel(); };
}
function setSkTool(t) { skTool = t; if (t === 'island' && skinView === 'dom') skinView = 'one'; if (t === "brush" && skinView === "dom") skinView = "one"; if (t !== "brush") ring.visible = false; paintSkin(); renderPanel(); }
function boneList() { return SK ? SK.names.slice() : []; }
function testHtml() {
  if (!SK_TEST) return `<div class="row"><button id="doTest">Tự kiểm skin</button></div>`;
  const bad = SK_TEST.rows.filter(r => r[0] === "bad").length, warn = SK_TEST.rows.filter(r => r[0] === "warn").length;
  return `<div class="big ${bad ? "bad" : warn ? "warn" : "ok"}">${bad ? "✗ " + bad + " lỗi" : warn ? "! " + warn + " cảnh báo" : "✓ Skin qua tự kiểm"} <span class="sub">(${SK_TEST.rows.length} mục)</span></div>
    ${more("m4test", "Chi tiết tự kiểm", SK_TEST.rows.map(r => chk(r[0], r[1], r[2])).join("") + `<div class="row"><button id="doTest">Kiểm lại</button><span class="sub">kiểm lúc ${new Date(SK_TEST.t).toLocaleTimeString()} · ${SK_TEST.ms} ms · tự kiểm lại sau mỗi nét tô</span></div>`)}`;
}
function renderSkinPanel(p) {
  if (!SK) {
    p.innerHTML = `<h2>Skin</h2><div class="sub">Tính trọng số tự động từ bộ xương, sau đó tô chỉnh.</div>
      <div class="row"><select id="skMode" aria-label="Cách tính skin"><option value="pro">Cấp cao (thông minh + giới hạn theo cây xương)</option><option value="smart">Thông minh (nhìn thấy xương, tách trái/phải)</option><option value="classic">Cổ điển (gần nhất)</option></select></div>
      <div class="row"><button class="pri" id="doSkin" ${skinBusy ? "disabled" : ""}>${skinBusy ? "Đang tính…" : "Tính skin"}</button>${guestS() ? '<button id="useRefS" title="Lấy luôn skin có sẵn của mesh, không tính lại">Dùng skin khách</button>' : ""}</div>${gateHtml(4)}`;
    const sm = $("skMode"); if (sm) { sm.value = skinMode; sm.onchange = () => { skinMode = sm.value; }; }
    const b = $("doSkin"); if (b) b.onclick = computeSkin; return;
  }
  const stale = SK.LMsnap !== JSON.stringify({ LM, TW });
  const tools = [["pick", "Chọn joint (Q)"], ["brush", "Cọ tô (B)"], ["island", "Gán khối rời (I)"]].map(([t, n]) => `<button data-skt="${t}" ${skTool === t ? 'class="pri"' : ""}>${n}</button>`).join("");
  p.innerHTML = `<h2>Skin</h2>
    ${stale ? `<div class="big warn">! Khớp hoặc twist đã đổi</div><div class="row"><button class="pri" id="doSkin" ${skinBusy ? "disabled" : ""}>${skinBusy ? "Đang tính…" : "Tính lại skin"}</button>${guestS() ? '<button id="useRefS" title="Lấy luôn skin có sẵn của mesh, không tính lại">Dùng skin khách</button>' : ""}</div>` : ""}
    ${testHtml()}
    <div class="row">${tools}</div>
    ${hammerHtml()}
      ${window.__adoptNote ? `<div class="sub" style="color:var(--ok);margin:4px 0">✓ ${esc(window.__adoptNote)}</div>` : ""}
      <div class="row" id="skModeRow"><select id="skMode" aria-label="Cách tính skin"><option value="pro">Cấp cao</option><option value="smart">Thông minh</option><option value="classic">Cổ điển</option></select><button id="doSkin3" title="Tính lại skin theo cách đã chọn" aria-label="Tính lại skin">Tính lại</button><button id="useRefS3" ${guestS() ? "" : "disabled"} title="${guestS() ? "Lấy luôn skin có sẵn của mesh (khách), không tính lại" : "Mesh này chưa có skin khách: cần nạp từ FBX đã rig"}">Dùng skin khách</button>${SK_INFO ? `<span class="sub">lần tính: ${SK_INFO.mode}${SK_INFO.mode !== "classic" ? ", " + SK_INFO.visible + " đỉnh thấy xương, " + SK_INFO.fallback + " dự phòng" : ""}</span>` : ""}</div>
    ${skTool === "island" ? '<div class="sub">Chọn joint, rồi click một khối rời của mesh để gán cả khối 100% cho joint đó.</div>' : ""}
    ${skTool === "brush" ? `<div class="row"><select id="brMode" aria-label="Kiểu cọ"><option value="add" ${brush.mode === "add" ? "selected" : ""}>Cộng trọng số</option><option value="sub" ${brush.mode === "sub" ? "selected" : ""}>Trừ trọng số</option><option value="smooth" ${brush.mode === "smooth" ? "selected" : ""}>Làm mượt</option><option value="hammer" ${brush.mode === "hammer" ? "selected" : ""}>Hammer (phá mảng nhọn)</option></select>
      <label class="t"><input type="checkbox" id="brMir" ${brush.mirror ? "checked" : ""}> Đối xứng</label></div>
      <div class="row" style="flex-wrap:nowrap"><label for="brR" style="width:70px;font-size:12px">Bán kính</label><input id="brR" type="range" min="2" max="40" step="1" value="${brush.r}" style="flex:1"><span id="brRv" class="sub" style="width:44px;text-align:right">${brush.r} cm</span></div>
      <div class="row" style="flex-wrap:nowrap"><label for="brS" style="width:70px;font-size:12px">Cường độ</label><input id="brS" type="range" min="0.05" max="1" step="0.05" value="${brush.str}" style="flex:1"><span id="brSv" class="sub" style="width:44px;text-align:right">${brush.str}</span></div>` : ""}
    <h2>Xem trọng số</h2>
    <div class="row"><select id="skView" aria-label="Kiểu xem"><option value="dom">Xương chính</option><option value="one">Xương đang chọn</option><option value="ref">Skin khách</option><option value="diff">Khác skin khách</option></select></div>
    <div class="row"><button id="skPrev" aria-label="Xương trước">◀</button><select id="skBone" aria-label="Xương đang chọn">${boneList().map(n => `<option ${n === skinBone ? "selected" : ""}>${n}</option>`).join("")}</select><button id="skNext" aria-label="Xương sau">▶</button></div>
    <div class="sub">Click một joint trên viewport để chọn nó.</div>
    ${poseSection()}
    ${more("m4stats", "Thống kê và xuất", (() => { const q = skinStats(); return `<div class="kv"><span>Xương có skin</span><span>${SK.names.length}</span><span>Xương / đỉnh</span><span>${fix(q.infl, 2)}</span><span>Trùng skin khách</span><span>${fix(q.same * 100)}%</span><span>Lệch TB</span><span>${fix(q.l1 * 100)}%</span></div>
      <table><thead><tr><th>Lệch nhiều nhất</th><th>lệch</th><th>đỉnh</th></tr></thead><tbody>${q.worst.map(w => `<tr><td>${w[0]}</td><td>${fix(w[1] * 100)}%</td><td>${w[2]}</td></tr>`).join("")}</tbody></table>
      <div class="row"><button id="doSkin2">Tính lại skin</button><button id="expW">Xuất weights.json</button><button id="expGltf" title="glTF có skin để mở trong Pose Lab">Xuất glTF</button>${guestS() ? '<button id="useRefS2" title="Lấy luôn skin có sẵn của mesh">Dùng skin khách</button>' : ""}</div>`; })())}
    ${gateHtml(4)}`;
  const on = (id, f) => { const e = $(id); if (e) e.addEventListener("click", f); };
  on("doTest", () => { const b = $("doTest"); if (b) { b.disabled = true; b.textContent = "Đang kiểm…"; } setTimeout(runSelfTest, 30); });
  on("doSkin", computeSkin); on("doSkin2", computeSkin); on("doSkin3", computeSkin); on("expW", exportWeights); on("expGltf", () => exportGltf()); on("useRefS", () => adoptGuestSkin()); on("useRefS3", () => adoptGuestSkin()); on("useRefS2", () => adoptGuestSkin());
  { const sm = $("skMode"); if (sm) { sm.value = skinMode; sm.onchange = () => { skinMode = sm.value; }; } }
  const v = $("skView"); if (v) { v.value = skinView; v.onchange = () => { skinView = v.value; paintSkin(); }; }
  const b = $("skBone"); if (b) b.onchange = () => { skinBone = b.value; paintSkin(); };
  const step1 = d => { const L = boneList(), i = (L.indexOf(skinBone) + d + L.length) % L.length; skinBone = L[i]; if (skinView === "dom") skinView = "one"; renderPanel(); paintSkin(); };
  on("skPrev", () => step1(-1)); on("skNext", () => step1(1));
  document.querySelectorAll("[data-skt]").forEach(x => x.addEventListener("click", () => setSkTool(x.dataset.skt)));
  const bm = $("brMode"); if (bm) bm.onchange = () => brush.mode = bm.value;
  const bx = $("brMir"); if (bx) bx.onchange = () => brush.mirror = bx.checked;
  const br = $("brR"); if (br) br.oninput = () => { brush.r = +br.value; $("brRv").textContent = brush.r + " cm"; };
  const bs = $("brS"); if (bs) bs.oninput = () => { brush.str = +bs.value; $("brSv").textContent = brush.str; };
  wirePoseSection(); wireHammer();
}
async function exportWeights() {
  if (!SK) return;
  const out = { bones: SK.names, influences: 4, vertices: NV, indices: Array.from(SK.I), weights: Array.from(SK.W, v => +v.toFixed(4)) };
  const text = JSON.stringify(out);
  try { const d = await window.claude.use("downloads"); if (d) { await d.save({ filename: CFG.name + "_weights_m2.json", data: text }); saveMsg = "Đã xuất weights.json."; return renderPanelLight(); } } catch (e) {}
  try { await navigator.clipboard.writeText(text); saveMsg = "Đã chép weights.json vào clipboard."; } catch (e) { saveMsg = "Không xuất được weights.json."; }
  renderPanelLight();
}
let poseBone = "Elbow_R";
function renderPosePanel(p) {
  if (!SK) { p.innerHTML = '<h2>Thử khớp</h2><div class="sub">Cần tính skin trước.</div><div class="row"><button class="pri" id="doSkin2">Tính skin</button></div>' + gateHtml(5); const b = $("doSkin2"); if (b) b.onclick = async () => { await computeSkin(); }; return; }
  const sm = strainSummary();
  const pr = Object.keys(PRESETS).map(n => `<button data-pre="${n}">${n}</button>`).join("");
  const bl = (battery || []).map(r => `<tr><td>${r[0]}</td><td class="${r[1] > 5 ? "err-hi" : r[1] > 1.5 ? "err-mid" : ""}">${fix(r[1])}%</td><td>${r[2]}</td></tr>`).join("");
  const pct = sm ? sm.pct : 0;
  p.innerHTML = `<h2>Pose thử</h2><div class="chips">${pr}<button id="poseReset">Về pose gốc</button></div>
    <div class="sub">Click một joint trên viewport rồi kéo thanh xoay ở góc phải.</div>
    <div class="row"><label class="t"><input type="checkbox" id="pTw" ${poseOpt.twist ? "checked" : ""}> Dẫn động twist</label><label class="t"><input type="checkbox" id="pStr" ${strainOn ? "checked" : ""}> Tô biến dạng</label></div>
    <div class="big ${pct > 5 ? "warn" : "ok"}">Co/căng quá 25%: ${fix(pct)}%</div>
    ${sm && sm.worst.length && pct > 1 ? `<div class="sub">Vùng xấu: ${sm.worst.map(w => w[0]).join(", ")}</div>` : ""}
    ${hammerHtml()}
    ${more("m5bat", "Bộ pose căng", `<div class="row"><button id="pBat">Chạy bộ pose căng</button></div>${bl ? `<table><thead><tr><th>Pose</th><th>quá 25%</th><th>vùng xấu</th></tr></thead><tbody>${bl}</tbody></table>` : ""}`)}
    ${more("m5bone", "Chọn xương từ danh sách", `<div class="row"><select id="pBone" aria-label="Chọn xương xoay">${buildSkeleton(LM).filter(b => !b.twist && b.name !== "root").map(b => `<option ${b.name === poseBone ? "selected" : ""}>${b.name}</option>`).join("")}</select><button id="pClr">Về 0</button></div>`)}
    ${gateHtml(5)}`;
  const on = (id, f) => { const e = $(id); if (e) e.addEventListener("click", f); };
  document.querySelectorAll("[data-pre]").forEach(b => b.addEventListener("click", () => { setPose(PRESETS[b.dataset.pre]); renderPanel(); }));
  on("poseReset", () => { setPose({}); renderPanel(); });
  $("pBone").onchange = e => { poseBone = e.target.value; jointSel = poseBone; renderPanel(); };
  on("pClr", () => { delete POSE[poseBone]; applyPose(); renderPanel(); });
  $("pTw").onchange = e => { poseOpt.twist = e.target.checked; applyPose(); renderPanel(); };
  $("pStr").onchange = e => { strainOn = e.target.checked; paintSkin(); };
  on("pBat", () => { battery = batteryRun(); OPEN.m5bat = true; renderPanel(); });
  wireHammer();
}

// ================================================================ M3 sớm: chọn joint trong viewport + cọ tô skin
let skTool = "pick", brush = { mode: "add", r: 10, str: 0.35, mirror: true };
let skinUndo = [], skinRedo = [], stroke = null, painting = false, pickDown = null, lastDab = 0, mirrorIdx = null;
const selPt = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 13, sizeAttenuation: false, depthTest: false, color: 0xffffff }));
selPt.renderOrder = 12; selPt.visible = false; scene.add(selPt);
const ringPts = []; for (let k = 0; k < 64; k++) { const a = k / 64 * Math.PI * 2; ringPts.push(new THREE.Vector3(Math.cos(a), Math.sin(a), 0)); }
const ringGeo = new THREE.BufferGeometry().setFromPoints(ringPts), ring = new THREE.Group();   // vòng trắng + vòng đen mỏng bên ngoài để thấy trên mọi nền
const ringIn = new THREE.LineLoop(ringGeo, new THREE.LineBasicMaterial({ color: 0xffffff, depthTest: false })), ringOut = new THREE.LineLoop(ringGeo, new THREE.LineBasicMaterial({ color: 0x000000, depthTest: false }));
ringOut.scale.setScalar(1.05); ringIn.renderOrder = 11; ringOut.renderOrder = 11; ring.add(ringOut, ringIn);
ring.visible = false; ring.renderOrder = 11; scene.add(ring);

// ---- island = khối liên thông của mesh
const COMP = (() => {
  const par = Array.from({ length: NV }, (_, i) => i), f = a => { while (par[a] !== a) { par[a] = par[par[a]]; a = par[a]; } return a; };
  for (let t = 0; t < NT; t++) { const a = f(TRI[3 * t]), b = f(TRI[3 * t + 1]), c = f(TRI[3 * t + 2]); par[b] = a; par[c] = a; }
  const id = new Int32Array(NV), roots = new Map(), size = [];
  for (let i = 0; i < NV; i++) { const r = f(i); if (!roots.has(r)) { roots.set(r, size.length); size.push(0); } id[i] = roots.get(r); size[id[i]]++; }
  return { id, size };
})();
function assignIsland(e) {
  if (!SK || !skinBone || SK.idx[skinBone] === undefined) { saveMsg = "Chọn một joint có skin trước (click joint ở chế độ Chọn joint)."; renderPanelLight(); return; }
  const r = cv.getBoundingClientRect();
  ray.setFromCamera({ x: ((e.clientX - r.left) / r.width) * 2 - 1, y: -((e.clientY - r.top) / r.height) * 2 + 1 }, CAM());
  const hits = ray.intersectObject(skinMesh, false).filter(x => COMP.size[COMP.id[TRI[x.faceIndex * 3]]] < NV * 0.3);   // bỏ qua thân chính, lấy khối rời gần nhất dưới con trỏ
  if (!hits.length) { saveMsg = "Không có khối rời dưới con trỏ (thân chính không gán nguyên khối, dùng cọ)."; renderPanelLight(); return; }
  const h = hits[0], c = COMP.id[TRI[h.faceIndex * 3]], j = SK.idx[skinBone], m = new Map(), v = new Float64Array(SK.nb); v[j] = 1;
  for (let i = 0; i < NV; i++) if (COMP.id[i] === c) { m.set(i, [Array.from(SK.I.slice(i * 4, i * 4 + 4)), Array.from(SK.W.slice(i * 4, i * 4 + 4))]); setVec(i, Float64Array.from(v)); }
  host.pushSkin(m); skinRedo = []; dirtySkin = true; paintSkin();
  saveMsg = "Đã gán khối rời " + m.size + " đỉnh cho " + skinBone + " 100%."; scheduleSkinSave();
}
function denseFrom(I, W, nb) { const f = new Float32Array(nb * NV); for (let i = 0; i < NV; i++) for (let k = 0; k < 4; k++) if (W[i * 4 + k] > 0) f[I[i * 4 + k] * NV + i] = W[i * 4 + k]; return f; }
function updateSelPt() {
  const name = step === 4 ? skinBone : step === 5 ? poseBone : null;
  if (!name || step < 4) { selPt.visible = false; return; }
  const B = buildSkeleton(LM), b = B.find(x => x.name === name); if (!b) { selPt.visible = false; return; }
  const pos = step >= 4 && SK ? posedBones(B)[name] : b.pos;
  selPt.geometry.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); selPt.material.color.set(css("--accent")); selPt.visible = true;
}
// ---- phép tô trên ma trận dày SK.full
function getVec(i) { const v = new Float64Array(SK.nb); for (let j = 0; j < SK.nb; j++) v[j] = SK.full[j * NV + i]; return v; }
function setVec(i, v) {
  const idx = [...v.keys()].sort((a, b) => v[b] - v[a]).slice(0, 4).filter(j => v[j] > 0.005), s = idx.reduce((q, j) => q + v[j], 0) || 1;
  for (let j = 0; j < SK.nb; j++) SK.full[j * NV + i] = 0;
  for (let k = 0; k < 4; k++) { if (k < idx.length) { const j = idx[k]; SK.I[i * 4 + k] = j; SK.W[i * 4 + k] = v[j] / s; SK.full[j * NV + i] = v[j] / s; } else { SK.I[i * 4 + k] = 0; SK.W[i * 4 + k] = 0; } }
}
// ---- Hammer: trọng số đỉnh := (1-m)·cũ + m·trung bình cotan của lân cận (đỉnh ngoài tập đóng vai neo)
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
function lapMag(arr) {   // độ lệch của mỗi đỉnh so với trung bình cotan của lân cận (cm): lớn = mảng nhọn/gập gãy
  const o = new Float32Array(NV);
  for (let i = 0; i < NV; i++) { let sw = 0, cx = 0, cy = 0, cz = 0; for (let e = LAP.start[i]; e < LAP.start[i + 1]; e++) { const w = LAP.nw[e], j = LAP.nb[e]; sw += w; cx += w * arr[3 * j]; cy += w * arr[3 * j + 1]; cz += w * arr[3 * j + 2]; }
    o[i] = sw ? Math.hypot(arr[3 * i] - cx / sw, arr[3 * i + 1] - cy / sw, arr[3 * i + 2] - cz / sw) : 0; }
  return o;
}
const HAM_REST = lapMag(Float32Array.from(DATA.body.verts)), HAM_SPIKE = 2.0;   // mesh sạch: ≤ 1,8 cm ở mọi pose thử (trừ đáy chậu ~2,7); lỗi nách Zom1 3,9 cm
function strainedSet(thr) {   // đỉnh căng > thr, hoặc nhọn thêm > HAM_SPIKE cm so với lúc đứng yên, ở pose hiện tại + 1 vòng lân cận
  poseSkin(); const set = new Set(), D = lapMag(skinGeo.attributes.position.array);
  for (let i = 0; i < NV; i++) if (STR[i] > thr || D[i] - HAM_REST[i] > HAM_SPIKE) { set.add(i); for (let e = LAP.start[i]; e < LAP.start[i + 1]; e++) set.add(LAP.nb[e]); }
  return set;
}
function hammerFinish(snap, msg) {
  host.pushSkin(snap); if (skinUndo.length > 60) skinUndo.shift(); skinRedo = [];
  scheduleSkinSave(); scheduleSelfTest(); applyPose(); paintSkin(); saveMsg = msg; renderPanel();
}
const spikeMax = () => { const D = lapMag(skinGeo.attributes.position.array); let m = 0; for (let i = 0; i < NV; i++) m = Math.max(m, D[i] - HAM_REST[i]); return m; };
function hammerCurrent() {
  if (!SK) return; const set = strainedSet(0.25), n0 = strainSummary().pct, spikeMax0 = spikeMax();
  if (!set.size) { saveMsg = "Pose hiện tại không có đỉnh căng hoặc nhọn bất thường: chọn pose có lỗi rồi Hammer."; return renderPanelLight(); }
  const snap = new Map(); set.forEach(i => snap.set(i, snap4(i)));
  hammerVerts([...set], 3, () => 0.8); poseSkin();
  hammerFinish(snap, `Hammer pose hiện tại: ${set.size} đỉnh (căng hoặc nhọn); căng quá 25% ${fix(n0)}% → ${fix(strainSummary().pct)}%, nhọn tối đa ${fix(spikeMax0)} → ${fix(spikeMax())} cm.`);
}
function hammerAuto() {
  if (!SK) return; const keep = JSON.stringify(POSE), kt = poseOpt.twist; poseOpt.twist = true;
  const snap = new Map(), pct = () => { let w = 0; for (const p of Object.values(PRESETS)) { for (const k in POSE) delete POSE[k]; for (const k in p) POSE[k] = p[k].slice(); poseSkin(); w = Math.max(w, strainSummary().pct); } return w; };
  const spk = () => { let w = 0; for (const p of Object.values(PRESETS)) { for (const k in POSE) delete POSE[k]; for (const k in p) POSE[k] = p[k].slice(); poseSkin(); w = Math.max(w, spikeMax()); } return w; };
  const before = pct(), spike0 = spk(); let rounds = 0, touched = new Set();
  for (; rounds < 4; rounds++) {
    const union = new Set();
    for (const p of Object.values(PRESETS)) { for (const k in POSE) delete POSE[k]; for (const k in p) POSE[k] = p[k].slice(); strainedSet(0.25).forEach(i => union.add(i)); }
    if (!union.size) break;
    union.forEach(i => { if (!snap.has(i)) snap.set(i, snap4(i)); touched.add(i); });
    hammerVerts([...union], 2, () => 0.7);
  }
  const after = pct(), spike1 = spk();
  for (const k in POSE) delete POSE[k]; Object.assign(POSE, JSON.parse(keep)); poseOpt.twist = kt; poseSkin();
  if (!snap.size) { saveMsg = "Hammer tự động: không có đỉnh căng quá 25% ở bộ pose."; return renderPanelLight(); }
  hammerFinish(snap, `Hammer tự động: ${rounds} vòng, ${touched.size} đỉnh; căng quá 25% (pose xấu nhất) ${fix(before)}% → ${fix(after)}%, nhọn tối đa ${fix(spike0)} → ${fix(spike1)} cm.`);
}
const hammerHtml = () => `<div class="row"><button id="hammerNow" title="Làm phẳng trọng số quanh đỉnh đang căng quá 25% ở pose hiện tại">Hammer pose hiện tại</button><button id="hammerAuto" title="Lặp bộ pose, hammer các đỉnh căng tới khi hết (tối đa 4 vòng)">Hammer tự động</button></div>`;
const wireHammer = () => { const a = $("hammerNow"), b = $("hammerAuto"); if (a) a.onclick = hammerCurrent; if (b) b.onclick = hammerAuto; };
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
  ray.setFromCamera({ x: ((e.clientX - r.left) / r.width) * 2 - 1, y: -((e.clientY - r.top) / r.height) * 2 + 1 }, CAM());
  const h = ray.intersectObject(skinMesh, false)[0]; return h ? scene.worldToLocal(h.point.clone()) : null;
}
function brushHitFull(e) {
  const r = cv.getBoundingClientRect();
  ray.setFromCamera({ x: ((e.clientX - r.left) / r.width) * 2 - 1, y: -((e.clientY - r.top) / r.height) * 2 + 1 }, CAM());
  const h = ray.intersectObject(skinMesh, false)[0] || null; if (h) h.point = scene.worldToLocal(h.point.clone()); return h;
}
function paintAt(e) {
  if (!SK || (brush.mode !== "hammer" && (!skinBone || SK.idx[skinBone] === undefined))) return;
  const pt = brushHit(e); if (!pt) return;
  const PP = skinGeo.attributes.position.array, j = SK.idx[skinBone], jm = SK.idx[mirName(skinBone)], mi = brush.mirror && jm !== undefined && mirName(skinBone) !== skinBone ? getMirror() : null;
  if (brush.mode === "hammer") {   // không phụ thuộc xương đang chọn
    const mx = new Map(), M2 = brush.mirror ? getMirror() : null;
    for (let i = 0; i < NV; i++) { const d = Math.hypot(PP[3 * i] - pt.x, PP[3 * i + 1] - pt.y, PP[3 * i + 2] - pt.z); if (d > brush.r) continue; const m = Math.min(1, brush.str * (1 - (d / brush.r) ** 2) ** 2 * 1.6);
      mx.set(i, Math.max(mx.get(i) || 0, m)); if (M2) mx.set(M2[i], Math.max(mx.get(M2[i]) || 0, m)); }
    mx.forEach((_, i) => { if (!stroke.has(i)) stroke.set(i, snap4(i)); });
    hammerVerts([...mx.keys()], 1, i => mx.get(i)); paintSkin(); dirtySkin = true; return;
  }
  if (!SK || j === undefined) return;
  for (let i = 0; i < NV; i++) {
    const d = Math.hypot(PP[3 * i] - pt.x, PP[3 * i + 1] - pt.y, PP[3 * i + 2] - pt.z); if (d > brush.r) continue;
    const f = (1 - (d / brush.r) ** 2) ** 2, a = brush.str * f * 0.5;
    const touch = (vi, bj) => { if (!stroke.has(vi)) stroke.set(vi, [Array.from(SK.I.slice(vi * 4, vi * 4 + 4)), Array.from(SK.W.slice(vi * 4, vi * 4 + 4))]); dab(vi, bj, a, brush.mode); };
    touch(i, j); if (mi) touch(mi[i], jm);
  }
  paintSkin(); dirtySkin = true;
}
let dirtySkin = false;
function skinSnapshotOf(map) { const o = new Map(); map.forEach((_, i) => o.set(i, [Array.from(SK.I.slice(i * 4, i * 4 + 4)), Array.from(SK.W.slice(i * 4, i * 4 + 4))])); return o; }
function restoreSkin(map) { map.forEach(([I4, W4], i) => { for (let k = 0; k < 4; k++) { SK.I[i * 4 + k] = I4[k]; SK.W[i * 4 + k] = W4[k]; } for (let j = 0; j < SK.nb; j++) SK.full[j * NV + i] = 0; for (let k = 0; k < 4; k++) if (W4[k] > 0) SK.full[I4[k] * NV + i] = W4[k]; }); paintSkin(); }
function skinUndoStep() { const m = skinUndo.pop(); if (!m) return; skinRedo.push(skinSnapshotOf(m)); restoreSkin(m); scheduleSkinSave(); }
function skinRedoStep() { const m = skinRedo.pop(); if (!m) return; skinUndo.push(skinSnapshotOf(m)); restoreSkin(m); scheduleSkinSave(); }

// ---- chọn joint trực tiếp
let jointSel = null;
function renderJointBox() {
  const el = $("jbox"); if (!el) return;
  if (step < 4 || !SK || !jointSel) { el.hidden = true; return; }
  const P = POSE[jointSel] || [0, 0, 0];
  el.hidden = false;
  el.innerHTML = `<div class="jhead"><b>${jointSel}</b><span><button id="jClr">Về 0</button> <button id="jX" aria-label="Đóng" title="Đóng">×</button></span></div>` +
    [["Roll", 0], ["Gập A", 1], ["Gập B", 2]].map(([t, i]) => `<div class="jrow"><label for="jr${i}">${t}</label><input id="jr${i}" type="range" min="-180" max="180" step="1" value="${P[i]}"><span id="jv${i}">${P[i]}°</span></div>`).join("") +
    `<div class="sub" style="font-size:11px">Roll quanh xương; A và B là hai trục gập vuông góc theo khung xương.</div>`;
  [0, 1, 2].forEach(i => {
    const r = $("jr" + i);
    r.addEventListener("input", e => { const q = (POSE[jointSel] = POSE[jointSel] || [0, 0, 0]); q[i] = +e.target.value; $("jv" + i).textContent = q[i] + "°"; applyPose(); });
    r.addEventListener("change", () => { if (step === 5) renderPanel(); });
  });
  $("jClr").onclick = () => { delete POSE[jointSel]; applyPose(); renderJointBox(); if (step === 5) renderPanel(); };
  $("jX").onclick = () => { jointSel = null; renderJointBox(); };
}
function pickJoint(e) {
  const r = cv.getBoundingClientRect(), B = buildSkeleton(LM), PB = step >= 4 && SK ? posedBones(B) : null;
  let best = 16, name = null;
  for (const b of B) {
    if (b.name === "root" || b.name === "Weapon" || (step === 4 && (!SK || SK.idx[b.name] === undefined))) continue;
    if (step === 5 && b.twist) continue;
    const pp = PB ? PB[b.name] : b.pos, v = new THREE.Vector3(...pp).applyMatrix4(scene.matrixWorld).project(CAM()), px = r.left + (v.x + 1) / 2 * r.width, py = r.top + (1 - v.y) / 2 * r.height, d = Math.hypot(px - e.clientX, py - e.clientY);
    if (d < best) { best = d; name = b.name; }
  }
  if (!name) { if (jointSel) { jointSel = null; renderJointBox(); } return; }
  selectBoneByName(name);
}
function selectBoneByName(name) {
  if (name === "root" || name === "Weapon" || step < 4) return;
  if (step === 4 && (!SK || SK.idx[name] === undefined)) return;
  jointSel = /Twist/.test(name) ? null : name; if (jointSel) poseBone = name;
  if (step === 4) { skinBone = name; if (!/Twist/.test(name)) poseBone = name; if (skinView === "dom") skinView = "one"; paintSkin(); } else poseBone = name;
  syncScene(); renderPanel();
}
host.listen("pointerdown", e => {
  if (step < 4 || (e.pointerType !== "mouse" && !(TM.on && TM.mode !== "orbit")) || e.button !== 0 || e.altKey) return;
  if (step === 4 && skTool === "island" && SK) { assignIsland(e); }
  else if (step === 4 && skTool === "brush" && SK) { painting = true; stroke = new Map(); paintAt(e); lastDab = performance.now(); }
  else pickDown = [e.clientX, e.clientY];
});
host.listen("pointermove", e => {
  if (step === 4 && skTool === "brush" && SK && !e.altKey) { const h = brushHitFull(e); ring.visible = !!h; if (h) { ring.position.copy(h.point).addScaledVector(h.face.normal, 0.3); ring.lookAt(h.point.clone().add(h.face.normal)); ring.scale.setScalar(brush.r); ringIn.material.color.set(brush.mode === "sub" ? 0xff5a4d : 0xffffff); } } else ring.visible = false;
  if (painting && performance.now() - lastDab > 30) { paintAt(e); lastDab = performance.now(); }
});
window.addEventListener("pointerup", e => {
  if (!host.alive()) return;
  if (painting) { painting = false; const m = new Map(); stroke.forEach((v, i) => m.set(i, v)); if (m.size) { host.pushSkin(m); if (skinUndo.length > 60) skinUndo.shift(); skinRedo = []; scheduleSkinSave(); scheduleSelfTest(); } stroke = null; return; }
  if (pickDown) { const d = pickDown; pickDown = null; if (Math.hypot(e.clientX - d[0], e.clientY - d[1]) < 4 && e.target === cv) pickJoint(e); }
});
let skTimer = null;
function scheduleSkinSave() { saveMsg = "Đang lưu…"; renderPanelLight(); clearTimeout(skTimer); skTimer = setTimeout(saveSkin, 2500); }
async function saveSkin() {
  if (!SK) return;
  const doc = { names: SK.names, I: Array.from(SK.I), W: Array.from(SK.W, v => +v.toFixed(3)), sig: SK.LMsnap, nv: NV, at: Date.now() };
  try {
    if (db) await db.doc("rig/skin").set(doc); else localStorage.setItem("rig_skin", JSON.stringify(doc));
    dirtySkin = false; saveMsg = db ? "Đã lưu" : "Đã lưu (chỉ trình duyệt này)";
  } catch (e) { saveMsg = "Không lưu được skin: " + (e.message || e.code || e); }
  renderPanelLight();
}
function loadSkinDoc(d) {
  if (!d || !d.names || d.nv !== NV) return;
  const nb = d.names.length, I = Uint16Array.from(d.I), W = Float32Array.from(d.W);
  SK = { names: d.names, idx: Object.fromEntries(d.names.map((n, i) => [n, i])), I, W, nb, full: denseFrom(I, W, nb), LMsnap: d.sig };
  skinBone = skinBone || d.names[0]; skinMs = 0;
}


// ---- xuất glTF cho Pose (POSEEXPORT)
// glTF skinned: nút xương = joint (translation theo cha, mét), thân + quần áo skin theo SK, prop gắn cứng vào Weapon. Pose Lab đọc bằng GLTFLoader.
function buildGltf() {
  if (!SK) throw new Error("Cần tính skin (bước 4) trước khi xuất cho Pose Lab.");
  const S = 0.01, B = buildSkeleton(LM), byN = {}, jIdx = {}; B.forEach((b, i) => { byN[b.name] = b; jIdx[b.name] = i; });
  const nodes = B.map(b => ({ name: b.name, translation: (b.parent ? b.pos.map((v, k) => (v - byN[b.parent].pos[k]) * S) : b.pos.map(v => v * S)) }));
  B.forEach((b, i) => { if (b.parent) (nodes[jIdx[b.parent]].children = nodes[jIdx[b.parent]].children || []).push(i); });
  const rootIdx = B.findIndex(b => !b.parent), chunks = [], views = [], acc = []; let off = 0;
  const addView = (ta, target) => { const bytes = new Uint8Array(ta.buffer, ta.byteOffset, ta.byteLength), pad = (4 - (bytes.length % 4)) % 4, buf = new Uint8Array(bytes.length + pad); buf.set(bytes);
    chunks.push(buf); views.push(Object.assign({ buffer: 0, byteOffset: off, byteLength: bytes.length }, target ? { target } : {})); off += buf.length; return views.length - 1; };
  const addAcc = (ta, type, comp, count, extra) => { acc.push(Object.assign({ bufferView: addView(ta, extra && extra.target), componentType: comp, count, type }, extra && extra.mm ? { min: extra.mm[0], max: extra.mm[1] } : {})); return acc.length - 1; };
  const meshes = [], meshNodes = [];
  const bakeMesh = (name, verts, tris, jw) => {   // jw[i] = [[jointIdx, w] ...] (tối đa 4)
    const n = verts.length / 3, pos = new Float32Array(n * 3), nrm = new Float32Array(n * 3), J = new Uint16Array(n * 4), W = new Float32Array(n * 4);
    const mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9];
    for (let i = 0; i < n; i++) for (let k = 0; k < 3; k++) { const v = verts[3 * i + k] * S; pos[3 * i + k] = v; mn[k] = Math.min(mn[k], v); mx[k] = Math.max(mx[k], v); }
    const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(pos, 3)); g.setIndex(Array.from(tris)); g.computeVertexNormals(); nrm.set(g.attributes.normal.array); g.dispose();
    for (let i = 0; i < n; i++) { const L = (jw(i) || []).filter(x => x[1] > 0).slice(0, 4); let t = L.reduce((a, x) => a + x[1], 0);
      if (!L.length || t <= 0) { J[4 * i] = rootIdx; W[4 * i] = 1; continue; } L.forEach(([j, w], k) => { J[4 * i + k] = j; W[4 * i + k] = w / t; }); }
    const big = n > 65535, I = big ? Uint32Array.from(tris) : Uint16Array.from(tris);
    const prim = { attributes: { POSITION: addAcc(pos, "VEC3", 5126, n, { target: 34962, mm: [mn, mx] }), NORMAL: addAcc(nrm, "VEC3", 5126, n, { target: 34962 }), JOINTS_0: addAcc(J, "VEC4", 5123, n, { target: 34962 }), WEIGHTS_0: addAcc(W, "VEC4", 5126, n, { target: 34962 }) },
      indices: addAcc(I, "SCALAR", big ? 5125 : 5123, tris.length, { target: 34963 }), material: 0, mode: 4 };
    meshes.push({ name, primitives: [prim] }); meshNodes.push({ name, mesh: meshes.length - 1, skin: 0 });
  };
  const toJ = n => jIdx[n];
  bakeMesh(DATA.body.name || "Body", DATA.body.verts, DATA.body.tris, i => { const o = []; for (let k = 0; k < 4; k++) { const w = SK.W[i * 4 + k]; if (w > 0 && toJ(SK.names[SK.I[i * 4 + k]]) !== undefined) o.push([toJ(SK.names[SK.I[i * 4 + k]]), w]); } return o; });
  (DATA.clothes || []).forEach((c, ci) => { const CW = clothWeights(ci); bakeMesh(c.name || "Cloth" + ci, c.verts, c.tris, i => CW[i].filter(([b]) => toJ(SK.names[b]) !== undefined).map(([b, w]) => [toJ(SK.names[b]), w])); });
  const propJ = jIdx.Weapon !== undefined ? jIdx.Weapon : (jIdx.Prop_M !== undefined ? jIdx.Prop_M : jIdx.Chest_M);
  (DATA.props || []).forEach(p => bakeMesh(p.name || "Prop", p.verts, p.tris, () => [[propJ, 1]]));
  const ibm = new Float32Array(B.length * 16); B.forEach((b, i) => { const m = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -b.pos[0] * S, -b.pos[1] * S, -b.pos[2] * S, 1]; ibm.set(m, i * 16); });
  const ibmAcc = addAcc(ibm, "MAT4", 5126, B.length);
  const tIn = new Float32Array([1 / 30]), tOut = new Float32Array(nodes[rootIdx].translation);
  const inAcc = addAcc(tIn, "SCALAR", 5126, 1, { mm: [[1 / 30], [1 / 30]] }), outAcc = addAcc(tOut, "VEC3", 5126, 1);
  const all = nodes.concat(meshNodes), meshStart = nodes.length;
  const bin = new Uint8Array(off); let o2 = 0; chunks.forEach(c => { bin.set(c, o2); o2 += c.length; });
  let b64 = ""; for (let i = 0; i < bin.length; i += 0x8000) b64 += String.fromCharCode.apply(null, bin.subarray(i, i + 0x8000));
  return {
    asset: { version: "2.0", generator: "Rig Lab " + CFG.name }, scene: 0, scenes: [{ name: "Scene", nodes: [rootIdx].concat(meshNodes.map((_, i) => meshStart + i)) }],
    nodes: all, meshes, skins: [{ name: "Armature", joints: B.map((_, i) => i), inverseBindMatrices: ibmAcc, skeleton: rootIdx }],
    materials: [{ name: "Base", doubleSided: true, pbrMetallicRoughness: { baseColorFactor: [0.62, 0.66, 0.72, 1], metallicFactor: 0, roughnessFactor: 0.85 } }],
    animations: [{ name: "Rest", samplers: [{ input: inAcc, output: outAcc, interpolation: "LINEAR" }], channels: [{ sampler: 0, target: { node: rootIdx, path: "translation" } }] }],
    accessors: acc, bufferViews: views, buffers: [{ byteLength: bin.length, uri: "data:application/octet-stream;base64," + btoa(b64) }]
  };
}
window.DDC = window.DDC || {};
window.DDC.rigGltf = async function () { return { name: CFG.name, gltf: buildGltf() }; };
async function exportGltf() {
  try {
    const text = JSON.stringify(buildGltf()), name = CFG.name + "_rig.gltf", blob = new Blob([text], { type: "model/gltf+json" });
    try { if (window.claude && window.claude.use) { const d = await window.claude.use("downloads"); if (d) { await d.save({ filename: name, data: blob }); saveMsg = "Đã xuất " + name; return renderPanelLight(); } } } catch (e) {}
    const u = URL.createObjectURL(blob), a = document.createElement("a"); a.href = u; a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 4000);
    saveMsg = "Đã xuất " + name + " (" + Math.round(text.length / 1024) + " KB).";
  } catch (e) { saveMsg = e.message || String(e); }
  renderPanelLight();
}

// ---- dùng rig khách (ADOPTRIG)
// Rig có sẵn (xương + skin khách) đi kèm mesh: dùng thẳng thay vì rig lại. DATA.ref = xương khách (tên, cha, vị trí), DATA.refW = trọng số khách theo xương.
function guestJ() { return (DATA.ref || []).filter(b => b.pos && LM_ORDER.includes(b.name)).length >= 10; }
function guestS() { return guestJ() && Object.keys(DATA.refW || {}).length > 5; }
function adoptGuestJoints() {
  const by = {}; (DATA.ref || []).forEach(b => { if (b.pos) by[b.name] = b.pos; });
  let n = 0; for (const k of LM_ORDER) if (by[k]) { LM[k] = by[k].slice(); n++; }
  initFingers(LM, false); syncScene(); dirty(); commit(); saveMsg = "Đã đặt " + n + " khớp theo xương khách."; renderPanel();
}
function adoptGuestSkin() {
  const B = buildSkeleton(LM), segs = boneSegments(B), names = segs.map(x => x.name), idx = Object.fromEntries(names.map((n, i) => [n, i])), nb = names.length;
  const I = new Uint16Array(NV * 4), W = new Float32Array(NV * 4); let bare = 0, kept = 0;
  const fall = idx.Root_M !== undefined ? idx.Root_M : 0;
  for (let i = 0; i < NV; i++) {
    const a = Object.entries(REFW[i] || {}).filter(([b, w]) => idx[b] !== undefined && w > 0).sort((p, q) => q[1] - p[1]).slice(0, 4), t = a.reduce((x, p) => x + p[1], 0);
    if (!a.length || t <= 0) { I[i * 4] = fall; W[i * 4] = 1; bare++; continue; }
    a.forEach(([b, w], k) => { I[i * 4 + k] = idx[b]; W[i * 4 + k] = w / t; }); kept++;
  }
  SK = { names, idx, I, W, full: null, nb, LMsnap: JSON.stringify({ LM, TW }) };
  SK.full = denseFrom(I, W, nb); skinUndo = []; skinRedo = []; skinStale = false; skinBusy = false; if (!skinBone) skinBone = names[0]; setTimeout(scheduleSkinSave, 0);
  try { SK_TEST = skinSelfTest(); } catch (e) { SK_TEST = { rows: [["warn", "Tự kiểm lỗi", String(e.message || e)]], leaks: [], t: Date.now() }; }
  window.__adoptNote = "Đang dùng skin khách (" + kept + " đỉnh có trọng số" + (bare ? ", " + bare + " đỉnh gán Root_M" : "") + "). Tính lại skin sẽ thay nó.";
  saveMsg = "Đã dùng skin khách (" + kept + " đỉnh có trọng số" + (bare ? ", " + bare + " đỉnh không có nên gán Root_M" : "") + ").";
  paintSkin(); syncScene(); renderPanel();
}

syncScene(); renderAll(); resetHist();
const ready = initDb();
return {
  ready, renderPanel, renderAll, go, setMode, pick, setSel, applySel, pickLM, boxLM, pickJoint, selectBoneByName, gzStart, gzChange, gzEnd, syncScene,
  snapStr: snap, applySnap, skinSnapshotOf, restoreSkin, scheduleSkinSave, saveLM, saveSkin, exportRig, exportGltf, buildGltf, adoptGuestJoints, adoptGuestSkin, guestJ, guestS,
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
