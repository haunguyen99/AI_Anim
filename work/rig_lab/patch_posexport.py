"""Rig Lab → Pose Lab: xuất glTF có skin (xương theo bộ xương hiện tại, skin đã tính, mét, +Y lên) để Pose Lab mở làm base pose.
Thêm hàm buildGltf() + window.DDC.rigGltf() (vỏ ứng dụng gọi) + nút "Xuất glTF" ở mục Thống kê và xuất (bước 4). Idempotent (/*POSEEXPORT*/)."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")
s = open(P, encoding="utf8").read()
if "/*POSEEXPORT*/" in s:
    print("already patched"); raise SystemExit

JS = r"""
/*POSEEXPORT*/
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
"""

def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)

rep('<div class="row"><button id="doSkin2">Tính lại skin</button><button id="expW">Xuất weights.json</button></div>',
    '<div class="row"><button id="doSkin2">Tính lại skin</button><button id="expW">Xuất weights.json</button><button id="expGltf" title="glTF có skin để mở trong Pose Lab">Xuất glTF</button></div>')
rep('on("expW", exportWeights);', 'on("expW", exportWeights); on("expGltf", () => exportGltf());')
k = s.rfind("</script>")
s = s[:k] + JS + s[k:]
open(P, "w", encoding="utf8", newline="").write(s)
print("ok")
