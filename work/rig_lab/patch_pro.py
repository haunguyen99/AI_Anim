# Skin cấp cao ("pro", mặc định): ngoài "thông minh", mỗi đỉnh chỉ nhận xương cách xương trội của nó ≤ 2 bước trên cây xương
# (vai không ảnh hưởng đầu: Đầu→Cổ→Ngực→Bả vai→Vai = 4 bước), bỏ trọng số < 0,03. Tự kiểm thêm mục "Xương xa trên cây xương".
import os
R = os.path.dirname(os.path.abspath(__file__)); p = f"{R}/template.html"; s = open(p, encoding="utf8").read()
assert '"pro"' not in s
def sub(old, new):
    global s
    assert s.count(old) == 1, old[:70]; s = s.replace(old, new)
sub('let skinMode = "smart";', 'let skinMode = "pro";')
sub('  const smart = skinMode === "smart"; let nVis', '  const smart = skinMode !== "classic"; let nVis')
# hàm bước trên cây
sub("let SK_INFO = null;\nasync function computeSkin() {", '''let SK_INFO = null;
function treeHops(B) {   // số bước giữa hai xương trên cây xương (xương twist tính như khớp đầu đoạn)
  const par = {}; B.forEach(b => par[b.name] = b.parent); const base = n => n.replace(/Twist\d+/, ""), memo = new Map();
  const anc = n => { const o = []; while (n) { o.push(n); n = par[n]; } return o; };
  return (a, b) => { a = base(a); b = base(b); const key = a + "|" + b; if (memo.has(key)) return memo.get(key);
    const A = anc(a), C = anc(b); let h = 99; for (let i = 0; i < A.length; i++) { const j = C.indexOf(A[i]); if (j >= 0) { h = i + j; break; } } memo.set(key, h); return h; };
}
async function computeSkin() {''')
sub("  const names = segs.map(s => s.name), I = new Uint16Array(NV * 4), W = new Float32Array(NV * 4);\n  for (let i = 0; i < NV; i++) {\n    const a = [];",
    "  const names = segs.map(s => s.name), I = new Uint16Array(NV * 4), W = new Float32Array(NV * 4), hops = treeHops(B), pro = skinMode === \"pro\";\n  for (let i = 0; i < NV; i++) {\n    const a = [];")
sub('skinMode === "smart" && (otherSide(segs[j].name', 'skinMode !== "classic" && (otherSide(segs[j].name')
sub("    a.sort((x, y) => y[1] - x[1]); const top = a.slice(0, 4).filter(x => x[1] > 0.01),",
    "    a.sort((x, y) => y[1] - x[1]);\n    if (pro && a.length) { const dom = segs[a[0][0]].name; for (let k = a.length - 1; k > 0; k--) if (hops(segs[a[k][0]].name, dom) > 2 || a[k][1] < 0.03) a.splice(k, 1); }   // cấp cao: chỉ xương gần xương trội ≤ 2 bước\n    const top = a.slice(0, 4).filter(x => x[1] > 0.01),")
# UI
sub('<option value="smart">Thông minh (nhìn thấy xương, tách trái/phải)</option><option value="classic">Cổ điển (gần nhất)</option>',
    '<option value="pro">Cấp cao (thông minh + giới hạn theo cây xương)</option><option value="smart">Thông minh (nhìn thấy xương, tách trái/phải)</option><option value="classic">Cổ điển (gần nhất)</option>')
sub('<option value="smart">Thông minh</option><option value="classic">Cổ điển</option></select>${SK_INFO ? `<span class="sub">lần tính: ${SK_INFO.mode}${SK_INFO.mode === "smart" ?',
    '<option value="pro">Cấp cao</option><option value="smart">Thông minh</option><option value="classic">Cổ điển</option></select>${SK_INFO ? `<span class="sub">lần tính: ${SK_INFO.mode}${SK_INFO.mode !== "classic" ?')
# tự kiểm
sub("  // 3. rò rỉ:", '''  // 2b. xương xa trên cây: ảnh hưởng > 0,02 của xương cách xương trội > 2 bước (vai → đầu)
  { const hp = treeHops(B); let far = 0; const by = {};
    for (let i = 0; i < NV; i++) { let dom = -1, dw = -1; for (let k = 0; k < 4; k++) if (SK.W[i * 4 + k] > dw) { dw = SK.W[i * 4 + k]; dom = SK.I[i * 4 + k]; }
      for (let k = 0; k < 4; k++) { const w = SK.W[i * 4 + k]; if (w <= 0.02 || SK.I[i * 4 + k] === dom) continue; if (hp(SK.names[SK.I[i * 4 + k]], SK.names[dom]) > 2) { far++; const key = SK.names[SK.I[i * 4 + k]] + " ← " + SK.names[dom]; by[key] = (by[key] || 0) + 1; } } }
    rows.push([far ? "warn" : "ok", "Không ảnh hưởng xa trên cây xương", far ? far + " ảnh hưởng cách > 2 bước: " + Object.entries(by).sort((a, b) => b[1] - a[1]).slice(0, 3).map(e => e[0] + " ×" + e[1]).join(", ") : "mọi ảnh hưởng ≤ 2 bước (vai không kéo đầu)"]); }
  // 3. rò rỉ:''')
open(p, "w", encoding="utf8").write(s); print("ok")
