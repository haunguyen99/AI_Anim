# Làm template.html chạy theo cấu hình nhân vật (DATA.cfg) + lớp quần áo skin theo thân. Mặc định (không cfg) = Gaygor như cũ.
# python work/rig_lab/patch_cfg.py   (chạy một lần; kiểm từng đoạn thay đúng 1 chỗ)
import os
R = os.path.dirname(os.path.abspath(__file__))
p = f"{R}/template.html"
s = open(p, encoding="utf8").read()
if "const CFG =" in s:
    raise SystemExit("đã patch")

def sub(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:70])
    s = s.replace(old, new)

sub("<title>Gaygor Rig Lab</title>", "<title>__NAME__ Rig Lab</title>")
sub("<h1>Gaygor Rig Lab</h1>", "<h1>__NAME__ Rig Lab</h1>")

# cấu hình + danh sách khớp
sub('const SIDE_J = ["Scapula", "Shoulder", "Elbow", "Wrist", "Hip", "Knee", "Ankle", "Toes", "ToesEnd"];',
    '''const CFG = Object.assign({ name: "Gaygor", fingers: ["Middle", "Thumb", "Index", "Ring", "Pinky"], fseg: 3, toes: true, dress: true, prop: true, weapon: true, headEnd: true }, DATA.cfg || {});
const SIDE_J = ["Scapula", "Shoulder", "Elbow", "Wrist", "Hip", "Knee", "Ankle", ...(CFG.toes ? ["Toes", "ToesEnd"] : [])];
const LEG_J = ["Hip", "Knee", "Ankle", ...(CFG.toes ? ["Toes", "ToesEnd"] : [])];''')
sub('const CENTER = ["Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M", "HeadEnd_M", "DressFront_M", "DressBack_M", "Prop_M", "Weapon"];',
    '''const CENTER = ["Root_M", "Spine1_M", "Chest_M", "Neck_M", "Head_M", ...(CFG.headEnd ? ["HeadEnd_M"] : []), ...(CFG.dress ? ["DressFront_M", "DressBack_M"] : []), ...(CFG.prop ? ["Prop_M"] : []), ...(CFG.weapon ? ["Weapon"] : [])];
const NC = CFG.headEnd ? 6 : 5;   // số khớp thân giữa (cột sống + đầu)''')
sub('const FINGERS = ["Middle", "Thumb", "Index", "Ring", "Pinky"];', 'const FINGERS = CFG.fingers, FSEG = [1, 2, 3].filter(i => i <= CFG.fseg);')
sub('const FKEYS = FINGERS.flatMap(f => [1, 2, 3].map(i => f + "Finger" + i));', 'const FKEYS = FINGERS.flatMap(f => FSEG.map(i => f + "Finger" + i));')
sub('const LM_ORDER = [...CENTER.slice(0, 6), ...["Scapula", "Shoulder", "Elbow", "Wrist"].map(n => n + "_R"), ...["Hip", "Knee", "Ankle", "Toes", "ToesEnd"].map(n => n + "_R"),',
    'const LM_ORDER = [...CENTER.slice(0, NC), ...["Scapula", "Shoulder", "Elbow", "Wrist"].map(n => n + "_R"), ...LEG_J.map(n => n + "_R"),')
sub('...["Scapula", "Shoulder", "Elbow", "Wrist"].map(n => n + "_L"), ...["Hip", "Knee", "Ankle", "Toes", "ToesEnd"].map(n => n + "_L"), ...CENTER.slice(6),',
    '...["Scapula", "Shoulder", "Elbow", "Wrist"].map(n => n + "_L"), ...LEG_J.map(n => n + "_L"), ...CENTER.slice(NC),')

# skeleton
sub('[["Root_M", "root"], ["Spine1_M", "Root_M"], ["Chest_M", "Spine1_M"], ["Neck_M", "Chest_M"], ["Head_M", "Neck_M"], ["HeadEnd_M", "Head_M"]].forEach(',
    '[["Root_M", "root"], ["Spine1_M", "Root_M"], ["Chest_M", "Spine1_M"], ["Neck_M", "Chest_M"], ["Head_M", "Neck_M"], ...(CFG.headEnd ? [["HeadEnd_M", "Head_M"]] : [])].forEach(')
sub('for (const f of FINGERS) for (const i of [1, 2, 3]) add(',  'for (const f of FINGERS) for (const i of FSEG) add(')
sub('  add("Prop_M", "Chest_M", P("Prop_M")); add("DressFront_M", "Root_M", P("DressFront_M")); add("DressBack_M", "Root_M", P("DressBack_M"));',
    '  if (CFG.prop) add("Prop_M", "Chest_M", P("Prop_M")); if (CFG.dress) { add("DressFront_M", "Root_M", P("DressFront_M")); add("DressBack_M", "Root_M", P("DressBack_M")); }')
sub('''for (const s of ["R", "L"]) for (const [i, n] of ["Hip", "Knee", "Ankle", "Toes", "ToesEnd"].entries())
    add(n + "_" + s, i ? ["Hip", "Knee", "Ankle", "Toes"][i - 1] + "_" + s : "Root_M", P(n + "_" + s));
  add("Weapon", "root", P("Weapon"));''',
    '''for (const s of ["R", "L"]) for (const [i, n] of LEG_J.entries())
    add(n + "_" + s, i ? LEG_J[i - 1] + "_" + s : "Root_M", P(n + "_" + s));
  if (CFG.weapon) add("Weapon", "root", P("Weapon"));''')

# kiểm tra bước 1/3
sub('let asym = 0; for (const n of ["Scapula", "Shoulder", "Elbow", "Wrist", "Hip", "Knee", "Ankle", "Toes", "ToesEnd"]) {', 'let asym = 0; for (const n of SIDE_J) {')
sub('''  const ground = Math.min(idx.ToesEnd_R.pos[1], idx.ToesEnd_L.pos[1]);
  out.push([Math.abs(ground) < 1.5 ? "ok" : "warn", "Mũi chân chạm sàn (y = 0)", `y = ${fix(ground)} cm`]);''',
    '''  if (CFG.toes) { const ground = Math.min(idx.ToesEnd_R.pos[1], idx.ToesEnd_L.pos[1]);
    out.push([Math.abs(ground) < 1.5 ? "ok" : "warn", "Mũi chân chạm sàn (y = 0)", `y = ${fix(ground)} cm`]); }
  else { const a = Math.min(idx.Ankle_R.pos[1], idx.Ankle_L.pos[1]); out.push([a > 2 && a < 20 ? "ok" : "warn", "Cổ chân cao trên sàn", `y = ${fix(a)} cm`]); }''')
sub('front = LM.ToesEnd_R[2] > LM.Ankle_R[2],', 'front = CFG.toes ? LM.ToesEnd_R[2] > LM.Ankle_R[2] : footFront(),')
sub('function dist(a, b) {', '''function footFront() { const f = bodyV.filter(v => v[1] < 8 && v[0] < 0); return f.length ? f.reduce((s, v) => s + v[2], 0) / f.length > LM.Ankle_R[2] - 0.5 : true; }
function dist(a, b) {''')
sub('''[DATA.props.length ? "warn" : "ok", "Phần rời (island)", DATA.props.length ? "1 prop rời: gắn vào xương Weapon" : "không có"],''',
    '''[DATA.props.length ? "warn" : "ok", "Phần rời (island)", DATA.props.length ? "1 prop rời: gắn vào xương Weapon" : "không có"],
      ...(DATA.clothes || []).map(c => ["ok", "Lớp mặc thêm", c.name + " · " + (c.verts.length / 3 | 0) + " đỉnh · skin theo thân"]),''')

# đối chiếu rig khách: pos null = chỉ có tên
sub('DATA.ref.forEach(b => { if (b.parent && b.parent !== "root" && idx[b.parent]) pos.push(', 'DATA.ref.forEach(b => { if (b.pos && b.parent && b.parent !== "root" && idx[b.parent] && idx[b.parent].pos) pos.push(')
sub('return DATA.ref.filter(r => r.name !== "root" && idx[r.name]).map(', 'return DATA.ref.filter(r => r.pos && r.name !== "root" && idx[r.name]).map(')
sub('mean = errs.reduce((s, e) => s + e[1], 0) / errs.length;', 'mean = errs.length ? errs.reduce((s, e) => s + e[1], 0) / errs.length : 0;')
sub('''${more("m3b", "Đối chiếu rig khách", `<div class="kv">''', '''${!errs.length ? more("m3b", "Rig khách", `<div class="sub">Chỉ đối chiếu tên xương, không có vị trí đáp án (mesh khác tỉ lệ rig cũ).</div>`) : more("m3b", "Đối chiếu rig khách", `<div class="kv">''')

# xuất
sub('character: "Gaygor", template: "biped"', 'character: CFG.name, template: "biped"')
sub('filename: "Gaygor_rig_m1.json"', 'filename: CFG.name + "_rig_m1.json"')
sub('filename: "Gaygor_weights_m2.json"', 'filename: CFG.name + "_weights_m2.json"')
sub('spine: () => CENTER.slice(0, 6),', 'spine: () => CENTER.slice(0, NC),')
sub('[1, 2].map(i => [f + "Finger" + i + "_" + s, [0, 0, -70]])', 'FSEG.filter(i => i < 3).map(i => [f + "Finger" + i + "_" + s, [0, 0, -70]])')

# lớp quần áo
sub('const propMeshes = DATA.props.map(', '''const clothMeshes = (DATA.clothes || []).map(c => { const m = meshFrom(c, 0xc9a77a, 0.4); scene.add(m); return m; });
const propMeshes = DATA.props.map(''')
sub('const vis = { body: true, props: DATA.props.map(() => true) };', 'const vis = { body: true, cloth: true, props: DATA.props.map(() => true) };')
sub('  propMeshes.forEach((m, i) => m.visible = vis.props[i]);', '''  propMeshes.forEach((m, i) => m.visible = vis.props[i]);
  clothMeshes.forEach(m => { m.visible = vis.cloth; m.material.opacity = step >= 4 ? 0.35 : 0.4; m.userData.wire.visible = showWire; });''')
sub('''    DATA.props.map((x, i) => `<label class="t"><input type="checkbox" class="ovp"''', '''    (clothMeshes.length ? `<label class="t"><input type="checkbox" id="ocloth" ${vis.cloth ? "checked" : ""}> Quần áo (QA)</label>` : "") + DATA.props.map((x, i) => `<label class="t"><input type="checkbox" class="ovp"''')
sub('  document.querySelectorAll(".ovp").forEach(', '  { const c = $("ocloth"); if (c) c.onchange = () => { vis.cloth = c.checked; syncScene(); }; }\n  document.querySelectorAll(".ovp").forEach(')

# skin truyền sang quần áo
sub('function poseSkin() {\n  if (!SK) return null;', '''const CLOTH_MAP = clothMeshes.map(m => {   // đỉnh quần áo → đỉnh thân gần nhất (cùng bên trái/phải)
  const a = m.geometry.attributes.position.array, o = new Int32Array(a.length / 3);
  for (let i = 0; i < o.length; i++) { let best = 1e9, bj = 0; const x = a[3 * i], y = a[3 * i + 1], z = a[3 * i + 2];
    for (let j = 0; j < bodyV.length; j++) { const b = bodyV[j]; let d = (x - b[0]) ** 2 + (y - b[1]) ** 2 + (z - b[2]) ** 2; if (x * b[0] < 0 && Math.abs(x) > 4 && Math.abs(b[0]) > 4) d += 1e4; if (d < best) { best = d; bj = j; } }
    o[i] = bj; }
  return { rest: Float32Array.from(a), map: o };
});
function poseCloth(M) {
  clothMeshes.forEach((m, c) => {
    const g = m.geometry, pos = g.attributes.position.array, { rest, map } = CLOTH_MAP[c], v = new THREE.Vector3(), o = new THREE.Vector3();
    for (let i = 0; i < map.length; i++) { const j = map[i]; o.set(0, 0, 0);
      for (let k = 0; k < 4; k++) { const w = SK.W[j * 4 + k]; if (w <= 0) continue; v.set(rest[3 * i], rest[3 * i + 1], rest[3 * i + 2]).applyMatrix4(M[SK.I[j * 4 + k]]); o.addScaledVector(v, w); }
      pos[3 * i] = o.x; pos[3 * i + 1] = o.y; pos[3 * i + 2] = o.z; }
    g.attributes.position.needsUpdate = true; g.computeVertexNormals(); g.computeBoundingSphere();
    m.userData.wire.geometry.dispose(); m.userData.wire.geometry = new THREE.WireframeGeometry(g);
  });
}
function poseSkin() {
  if (!SK) return null;''')
sub('  skinGeo.attributes.position.needsUpdate = true; skinGeo.computeVertexNormals();', '  poseCloth(M);\n  skinGeo.attributes.position.needsUpdate = true; skinGeo.computeVertexNormals();')

open(p, "w", encoding="utf8").write(s)
print("ok", len(s))
