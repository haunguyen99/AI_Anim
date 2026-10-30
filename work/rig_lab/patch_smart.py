# Skin thông minh: hạt giống chỉ lấy xương "nhìn thấy" từ trong mesh (tia đỉnh → điểm gần nhất trên đoạn xương không xuyên bề mặt, hướng vào trong)
# + tách trái/phải (đỉnh |x|>4 không nhận xương bên kia) + skin quần áo làm mượt từ 6 đỉnh thân gần nhất. Giữ chế độ "cổ điển" để so.
# python work/rig_lab/patch_smart.py  (chạy một lần)
import os
R = os.path.dirname(os.path.abspath(__file__))
p = f"{R}/template.html"
s = open(p, encoding="utf8").read()
if "skinMode" in s:
    raise SystemExit("đã patch")

def sub(old, new):
    global s
    n = s.count(old); assert n == 1, (n, old[:80])
    s = s.replace(old, new)

# 1. chế độ + hàm nhìn thấy
sub("let SK = null, skinBusy = false, skinStale = false, skinMs = 0;", '''let SK = null, skinBusy = false, skinStale = false, skinMs = 0;
let skinMode = "smart";   // "smart" = nhìn thấy xương + tách trái/phải; "classic" = gần nhất theo khoảng cách
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
}''')

# 2. chọn hạt giống
old_seed = "  for (let i = 0; i < NV; i++) { let best = 1e9, bj = 0; for (let j = 0; j < nb; j++) { const d = distSeg(bodyV[i], segs[j].a, segs[j].b), db = d * (segs[j].bias || 1); if (db < best) { best = db; bj = j; } } dmin[i] = Math.max(distSeg(bodyV[i], segs[bj].a, segs[bj].b), 0.5); near[i] = bj; }"
new_seed = '''  const smart = skinMode === "smart"; let nVis = 0, nFall = 0;
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
  SK_INFO = { mode: skinMode, visible: nVis, fallback: nFall };'''
sub(old_seed, new_seed)
sub("async function computeSkin() {", "let SK_INFO = null;\nasync function computeSkin() {")

# 3. chọn xương cuối cùng: tách bên
sub("    const a = []; for (let j = 0; j < nb; j++) a.push([j, Wt[j * NV + i]]);",
    "    const a = []; for (let j = 0; j < nb; j++) { if (skinMode === \"smart\" && otherSide(segs[j].name, bodyV[i][0])) continue; a.push([j, Wt[j * NV + i]]); }")

# 4. quần áo: k đỉnh thân gần nhất, trọng số 1/(d+0.5)^2
sub('''const CLOTH_MAP = clothMeshes.map(m => {   // đỉnh quần áo → đỉnh thân gần nhất (cùng bên trái/phải)
  const a = m.geometry.attributes.position.array, o = new Int32Array(a.length / 3);
  for (let i = 0; i < o.length; i++) { let best = 1e9, bj = 0; const x = a[3 * i], y = a[3 * i + 1], z = a[3 * i + 2];
    for (let j = 0; j < bodyV.length; j++) { const b = bodyV[j]; let d = (x - b[0]) ** 2 + (y - b[1]) ** 2 + (z - b[2]) ** 2; if (x * b[0] < 0 && Math.abs(x) > 4 && Math.abs(b[0]) > 4) d += 1e4; if (d < best) { best = d; bj = j; } }
    o[i] = bj; }
  return { rest: Float32Array.from(a), map: o };
});''', '''const CLOTH_K = 6;
const CLOTH_MAP = clothMeshes.map(m => {   // đỉnh quần áo → 6 đỉnh thân gần nhất (cùng bên trái/phải), trọng số 1/(d+0.5)²
  const a = m.geometry.attributes.position.array, n = a.length / 3, nn = new Int32Array(n * CLOTH_K), nw = new Float32Array(n * CLOTH_K);
  for (let i = 0; i < n; i++) { const x = a[3 * i], y = a[3 * i + 1], z = a[3 * i + 2], c = [];
    for (let j = 0; j < bodyV.length; j++) { const b = bodyV[j]; if (x * b[0] < 0 && Math.abs(x) > SIDE_X && Math.abs(b[0]) > SIDE_X) continue; c.push([(x - b[0]) ** 2 + (y - b[1]) ** 2 + (z - b[2]) ** 2, j]); }
    c.sort((p, q) => p[0] - q[0]);
    for (let k = 0; k < CLOTH_K; k++) { const e = c[Math.min(k, c.length - 1)]; nn[i * CLOTH_K + k] = e[1]; nw[i * CLOTH_K + k] = 1 / (Math.sqrt(e[0]) + 0.5) ** 2; } }
  return { rest: Float32Array.from(a), nn, nw };
});
function clothInfl(c, i) {   // 4 xương mạnh nhất của đỉnh quần áo i = trung bình có trọng số của 6 đỉnh thân gần nhất
  const { nn, nw } = CLOTH_MAP[c], acc = {}; let tot = 0;
  for (let k = 0; k < CLOTH_K; k++) { const j = nn[i * CLOTH_K + k], wk = nw[i * CLOTH_K + k]; tot += wk;
    for (let m = 0; m < 4; m++) { const w = SK.W[j * 4 + m]; if (w > 0) acc[SK.I[j * 4 + m]] = (acc[SK.I[j * 4 + m]] || 0) + w * wk; } }
  const top = Object.entries(acc).sort((p, q) => q[1] - p[1]).slice(0, 4), sum = top.reduce((s, e) => s + e[1], 0) || 1;
  return top.map(([b, w]) => [+b, w / sum]);
}''')
sub('''    const g = m.geometry, pos = g.attributes.position.array, { rest, map } = CLOTH_MAP[c], v = new THREE.Vector3(), o = new THREE.Vector3();
    for (let i = 0; i < map.length; i++) { const j = map[i]; o.set(0, 0, 0);
      for (let k = 0; k < 4; k++) { const w = SK.W[j * 4 + k]; if (w <= 0) continue; v.set(rest[3 * i], rest[3 * i + 1], rest[3 * i + 2]).applyMatrix4(M[SK.I[j * 4 + k]]); o.addScaledVector(v, w); }
      pos[3 * i] = o.x; pos[3 * i + 1] = o.y; pos[3 * i + 2] = o.z; }''',
    '''    const g = m.geometry, pos = g.attributes.position.array, { rest } = CLOTH_MAP[c], v = new THREE.Vector3(), o = new THREE.Vector3();
    for (let i = 0; i < rest.length / 3; i++) { o.set(0, 0, 0);
      for (const [b, w] of clothInfl(c, i)) { v.set(rest[3 * i], rest[3 * i + 1], rest[3 * i + 2]).applyMatrix4(M[b]); o.addScaledVector(v, w); }
      pos[3 * i] = o.x; pos[3 * i + 1] = o.y; pos[3 * i + 2] = o.z; }''')

# 5. giao diện: chọn chế độ
sub('''<div class="row"><button class="pri" id="doSkin" ${skinBusy ? "disabled" : ""}>${skinBusy ? "Đang tính…" : "Tính skin"}</button></div>${gateHtml(4)}`;
    const b = $("doSkin"); if (b) b.onclick = computeSkin; return;''',
    '''<div class="row"><select id="skMode" aria-label="Cách tính skin"><option value="smart">Thông minh (nhìn thấy xương, tách trái/phải)</option><option value="classic">Cổ điển (gần nhất)</option></select></div>
      <div class="row"><button class="pri" id="doSkin" ${skinBusy ? "disabled" : ""}>${skinBusy ? "Đang tính…" : "Tính skin"}</button></div>${gateHtml(4)}`;
    const sm = $("skMode"); if (sm) { sm.value = skinMode; sm.onchange = () => { skinMode = sm.value; }; }
    const b = $("doSkin"); if (b) b.onclick = computeSkin; return;''')
sub('''<div class="row"><button id="doSkin2">Tính lại skin</button><button id="expW">Xuất weights.json</button></div>`; })())}''',
    '''<div class="row"><select id="skMode" aria-label="Cách tính skin"><option value="smart">Thông minh</option><option value="classic">Cổ điển</option></select>${SK_INFO ? `<span class="sub">lần tính: ${SK_INFO.mode}${SK_INFO.mode === "smart" ? ", " + SK_INFO.visible + " đỉnh thấy xương, " + SK_INFO.fallback + " dự phòng" : ""}</span>` : ""}</div>
      <div class="row"><button id="doSkin2">Tính lại skin</button><button id="expW">Xuất weights.json</button></div>`; })())}''')
sub('  on("doSkin", computeSkin); on("doSkin2", computeSkin); on("expW", exportWeights);',
    '  on("doSkin", computeSkin); on("doSkin2", computeSkin); on("expW", exportWeights);\n  { const sm = $("skMode"); if (sm) { sm.value = skinMode; sm.onchange = () => { skinMode = sm.value; }; } }')

open(p, "w", encoding="utf8").write(s)
print("ok")
