# Skin khố theo vùng cho lớp quần áo (cfg.clothSkirt): đảo (island) quần áo có tâm cao giữa gối và eo = khố.
# Trên (y ≥ Root+8) theo thân; dưới = Root_M + Hip_R/Hip_L (Hip tăng theo độ thấp tới 55% ở độ cao gối, chia trái/phải mượt trong ±8 cm quanh trục).
import os
R = os.path.dirname(os.path.abspath(__file__)); p = f"{R}/template.html"; s = open(p, encoding="utf8").read()
assert "applySkirt" not in s
old = "  const base = cur;\n"; assert s.count(old) == 1
s = s.replace(old, "  if (CFG.clothSkirt) applySkirt(c, cur);\n")
anchor = "function clothWeights(c) {"; assert s.count(anchor) == 1
fn = '''const CLOTH_ISL = CLOTH_ADJ.map(adj => { const seen = new Uint8Array(adj.length), out = [];
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
'''
s = s.replace(anchor, fn + anchor)
open(p, "w", encoding="utf8").write(s); print("ok")
