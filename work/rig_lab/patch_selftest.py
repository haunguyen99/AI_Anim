# Tự kiểm skin sau khi tính (và nút Kiểm lại): xương 0 đỉnh, ảnh hưởng chéo trái/phải, rò rỉ (xoay từng khớp, đỉnh xa nhánh con mà vẫn dịch), cạnh giãn.
# Kèm cắt trọng số xa (smart): bỏ ảnh hưởng của xương cách đỉnh > 2,5× khoảng cách tới xương hạt giống + 12 cm.
import os
R = os.path.dirname(os.path.abspath(__file__)); p = f"{R}/template.html"; s = open(p, encoding="utf8").read()
assert "skinSelfTest" not in s
def sub(old, new):
    global s
    assert s.count(old) == 1, old[:70]; s = s.replace(old, new)

# 1. cắt trọng số xa
sub('if (skinMode === "smart" && otherSide(segs[j].name, bodyV[i][0])) continue; a.push([j, Wt[j * NV + i]]); }',
    'if (skinMode === "smart" && (otherSide(segs[j].name, bodyV[i][0]) || (j !== near[i] && distSeg(bodyV[i], segs[j].a, segs[j].b) > 2.5 * dmin[i] + 12))) continue; a.push([j, Wt[j * NV + i]]); }')

# 2. bộ kiểm
anchor = "function strainSummary() {"; assert s.count(anchor) == 1
fn = '''let SK_TEST = null;
function skinSelfTest() {
  if (!SK) return null;
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
  // 3. rò rỉ: xoay từng khớp 50°, đỉnh dịch > 1 cm mà cách mọi đoạn xương nhánh con > 15 cm
  const leaks = [], zero = [], rest = DATA.body.verts, pos = skinGeo.attributes.position.array, joints = B.filter(b => !b.twist && b.name !== "root" && (kids[b.name] || []).length);
  for (const b of joints) {
    const S = sub(b.name), mine = segs.filter(g => S.has(g.name) || S.has(g.name.replace(/Twist\d+/, "")));
    let worst = 0, wI = -1, moved = 0;
    for (const ax of [[0, 0, 50], [0, 50, 0]]) {
      for (const k in POSE) delete POSE[k]; POSE[b.name] = ax.slice(); poseSkin();
      for (let i = 0; i < NV; i++) { const d = Math.hypot(pos[3 * i] - rest[3 * i], pos[3 * i + 1] - rest[3 * i + 1], pos[3 * i + 2] - rest[3 * i + 2]); if (d < 1) continue; moved++;
        let near = 1e9; for (const g of mine) near = Math.min(near, distSeg(bodyV[i], g.a, g.b)); if (near > 15 && d > worst) { worst = d; wI = i; } }
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
  return { rows, leaks, t: Date.now() };
}
'''
s = s.replace(anchor, fn + anchor)

# 3. tự chạy sau khi tính + hiện trong panel
sub("  paintSkin(); syncScene(); renderPanel();\n}\nfunction vw(i)", "  try { SK_TEST = skinSelfTest(); } catch (e) { SK_TEST = { rows: [[\"warn\", \"Tự kiểm lỗi\", String(e.message || e)]], leaks: [], t: Date.now() }; }\n  paintSkin(); syncScene(); renderPanel();\n}\nfunction vw(i)")
sub('    <div class="row">${tools}</div>\n    ${skTool === "island"', '''    ${testHtml()}
    <div class="row">${tools}</div>
    ${skTool === "island"''')
sub("function renderSkinPanel(p) {", '''function testHtml() {
  if (!SK_TEST) return `<div class="row"><button id="doTest">Tự kiểm skin</button></div>`;
  const bad = SK_TEST.rows.filter(r => r[0] === "bad").length, warn = SK_TEST.rows.filter(r => r[0] === "warn").length;
  return `<div class="big ${bad ? "bad" : warn ? "warn" : "ok"}">${bad ? "✗ " + bad + " lỗi" : warn ? "! " + warn + " cảnh báo" : "✓ Skin qua tự kiểm"} <span class="sub">(${SK_TEST.rows.length} mục)</span></div>
    ${more("m4test", "Chi tiết tự kiểm", SK_TEST.rows.map(r => chk(r[0], r[1], r[2])).join("") + `<div class="row"><button id="doTest">Kiểm lại</button></div>`)}`;
}
function renderSkinPanel(p) {''')
sub('  on("doSkin", computeSkin); on("doSkin2", computeSkin);', '  on("doTest", () => { SK_TEST = skinSelfTest(); renderPanel(); });\n  on("doSkin", computeSkin); on("doSkin2", computeSkin);')
open(p, "w", encoding="utf8").write(s); print("ok")
