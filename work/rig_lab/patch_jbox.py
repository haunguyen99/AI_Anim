# Một lần: thanh xoay (Roll, Gập A, Gập B) chuyển ra viewport, chỉ hiện khi đã chọn joint (bước 4 và 5)
import re
p = "template.html"
L = open(p, encoding="utf8").read().split("\n")
out = []
for ln in L:
    if 'id="ps${i}"' in ln or 'id="sp${i}"' in ln or "Trục theo khung của từng xương" in ln:
        continue
    if '$("ps" + i)' in ln or '$("ps0").addEventListener' in ln or 'const el = $("sp" + i)' in ln:
        continue
    out.append(ln)
s = "\n".join(out)


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


rep('<div class="vbar2" id="vopts"></div>', '<div class="vbar2" id="vopts"></div>\n    <div class="jbox" id="jbox" hidden></div>')
rep(".vhelp{", ".jbox{position:absolute;right:8px;top:62px;width:270px;max-width:calc(100% - 16px);background:color-mix(in srgb,var(--panel) 92%,transparent);border:1px solid var(--line);border-radius:8px;padding:8px 10px;z-index:3;font-size:12px}\n.jbox .jhead{display:flex;justify-content:space-between;align-items:center;gap:6px;margin-bottom:4px}\n.jbox .jrow{display:flex;align-items:center;gap:8px}.jbox .jrow label{width:84px}.jbox .jrow input{flex:1;min-width:0}.jbox .jrow span{width:36px;text-align:right;font-family:var(--mono)}\n.vhelp{")
rep("bs.onchange = e => { poseBone = e.target.value; renderPanel(); };", "bs.onchange = e => { poseBone = e.target.value; jointSel = poseBone; renderPanel(); };")
rep('$("pBone").onchange = e => { poseBone = e.target.value; renderPanel(); };', '$("pBone").onchange = e => { poseBone = e.target.value; jointSel = poseBone; renderPanel(); };')
rep("  wirePanel();\n}", "  wirePanel(); renderJointBox();\n}")
rep("function pickJoint(e) {", '''let jointSel = null;
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
function pickJoint(e) {''')
rep("  if (!name) return;\n  if (step === 4) { skinBone = name;", "  if (!name) { if (jointSel) { jointSel = null; renderJointBox(); } return; }\n  jointSel = /Twist/.test(name) ? null : name; if (jointSel) poseBone = name;\n  if (step === 4) { skinBone = name;")
rep("function go(n) { step = n; showSkinFor();", "function go(n) { step = n; if (n < 4) jointSel = null; showSkinFor();")
open(p, "w", encoding="utf8").write(s)
