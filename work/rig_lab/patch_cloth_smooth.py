# Skin quần áo: sau khi lấy trung bình 6 đỉnh thân gần nhất, làm mượt thêm 3 lượt trên cạnh lưới của chính lớp quần áo
import os
R = os.path.dirname(os.path.abspath(__file__)); p = f"{R}/template.html"; s = open(p, encoding="utf8").read()
assert "clothWeights" not in s
a = s.index("function clothInfl(c, i) {"); b = s.index("}\n", s.index("return top.map(([b, w]) => [+b, w / sum]);")) + 2
new = '''const CLOTH_ADJ = clothMeshes.map(m => { const idx = m.geometry.index.array, n = m.geometry.attributes.position.count, adj = Array.from({ length: n }, () => new Set());
  for (let t = 0; t < idx.length; t += 3) for (let e = 0; e < 3; e++) { const x = idx[t + e], y = idx[t + (e + 1) % 3]; adj[x].add(y); adj[y].add(x); }
  return adj.map(s => [...s]); });
function clothWeights(c) {   // mỗi đỉnh quần áo: 4 xương mạnh nhất; 6 đỉnh thân gần nhất → làm mượt 3 lượt trên lưới quần áo
  const { nn, nw } = CLOTH_MAP[c], n = nn.length / CLOTH_K, adj = CLOTH_ADJ[c];
  let cur = Array.from({ length: n }, (_, i) => { const acc = new Map(); let tot = 0;
    for (let k = 0; k < CLOTH_K; k++) { const j = nn[i * CLOTH_K + k], wk = nw[i * CLOTH_K + k]; tot += wk;
      for (let m = 0; m < 4; m++) { const w = SK.W[j * 4 + m]; if (w > 0) acc.set(SK.I[j * 4 + m], (acc.get(SK.I[j * 4 + m]) || 0) + w * wk); } }
    acc.forEach((w, b) => acc.set(b, w / tot)); return acc; });
  const base = cur;
  for (let it = 0; it < 3; it++) cur = cur.map((m, i) => { const o = new Map(); m.forEach((w, b) => o.set(b, w * 0.5));
    const nb = adj[i]; if (nb.length) { const f = 0.5 / nb.length; nb.forEach(j => cur[j].forEach((w, b) => o.set(b, (o.get(b) || 0) + w * f))); } else m.forEach((w, b) => o.set(b, w * 2));
    return o; });
  return cur.map(m => { const top = [...m.entries()].sort((p, q) => q[1] - p[1]).slice(0, 4), sum = top.reduce((s, e) => s + e[1], 0) || 1; return top.map(([b, w]) => [b, w / sum]); });
}
'''
s = s[:a] + new + s[b:]
old = "    for (let i = 0; i < rest.length / 3; i++) { o.set(0, 0, 0);\n      for (const [b, w] of clothInfl(c, i)) {"
assert s.count(old) == 1
s = s.replace(old, "    const CW = clothWeights(c);\n    for (let i = 0; i < rest.length / 3; i++) { o.set(0, 0, 0);\n      for (const [b, w] of CW[i]) {")
open(p, "w", encoding="utf8").write(s); print("ok")
