# Một lần: thao tác viewport kiểu Maya.
# Alt+LMB xoay, Alt+MMB kéo, Alt+RMB hoặc lăn chuột zoom; LMB chọn (click hoặc kéo khung);
# Shift = đảo chọn, Ctrl = bỏ chọn, Ctrl+Shift = thêm; Q chọn, W dời, E xoay, R co giãn; F nhìn vào vùng chọn, A nhìn toàn bộ.
p = "template.html"
s = open(p, encoding="utf8").read()


def rep(a, b):
    global s
    assert a in s, a[:60]
    s = s.replace(a, b, 1)


a = s.index("// chọn khớp: click")
b = s.index("// ---------------------------------------------------------------- lưu")
s = s[:a] + r'''// ---- thao tác kiểu Maya
// Alt+LMB xoay · Alt+MMB kéo · Alt+RMB / lăn chuột zoom · LMB click hoặc kéo khung để chọn
// Shift đảo chọn · Ctrl bỏ chọn · Ctrl+Shift thêm · Q chọn, W dời, E xoay, R co giãn · F nhìn vào vùng chọn · A nhìn toàn bộ
const MAYA = { LEFT: THREE.MOUSE.ROTATE, MIDDLE: THREE.MOUSE.PAN, RIGHT: THREE.MOUSE.DOLLY }, NONE = { LEFT: -1, MIDDLE: -1, RIGHT: -1 };
const ray = new THREE.Raycaster(); let down = null, boxing = false;
const boxEl = document.createElement("div");
boxEl.style.cssText = "position:absolute;border:1px dashed var(--accent);background:color-mix(in srgb,var(--accent) 14%,transparent);display:none;pointer-events:none";
vp.appendChild(boxEl);
function applySel(keys, e) {   // quy tắc chọn của Maya
  const ctrl = e.ctrlKey || e.metaKey, sh = e.shiftKey;
  if (!ctrl && !sh) { setSel(keys, false); return; }
  const cur = new Set(S);
  keys.forEach(k => { if (ctrl && sh) cur.add(k); else if (ctrl) cur.delete(k); else (cur.has(k) ? cur.delete(k) : cur.add(k)); });
  S.clear(); cur.forEach(k => S.add(k)); sel = keys.length && cur.has(keys[keys.length - 1]) ? keys[keys.length - 1] : ([...S].pop() || null);
  syncScene(); renderPanelLight();
}
cv.addEventListener("pointerdown", e => {
  if (e.pointerType === "mouse") orbit.mouseButtons = e.altKey ? MAYA : NONE;
  down = [e.clientX, e.clientY]; boxing = false;
  if (step === 2 && e.pointerType === "mouse" && e.button === 0 && !e.altKey && !tc.axis) boxing = true;
}, true);
cv.addEventListener("wheel", () => { orbit.mouseButtons = MAYA; }, true);
cv.addEventListener("pointermove", e => {
  if (!boxing || !down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) < 4) return;
  const r = vp.getBoundingClientRect(), x0 = down[0] - r.left, y0 = down[1] - r.top, x1 = e.clientX - r.left, y1 = e.clientY - r.top;
  Object.assign(boxEl.style, { display: "block", left: Math.min(x0, x1) + "px", top: Math.min(y0, y1) + "px", width: Math.abs(x1 - x0) + "px", height: Math.abs(y1 - y0) + "px" });
});
window.addEventListener("pointerup", e => {
  if (!down) return;
  const moved = Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 4, was = boxing, d0 = down;
  down = null; boxing = false; boxEl.style.display = "none";
  if (step !== 2 || !was || (e.target !== cv && !moved)) return;
  const r = cv.getBoundingClientRect();
  if (moved) {
    const xa = Math.min(d0[0], e.clientX), xb = Math.max(d0[0], e.clientX), ya = Math.min(d0[1], e.clientY), yb = Math.max(d0[1], e.clientY), hit = [];
    for (const k of LM_ORDER) {
      const m = lmMesh[k]; if (!m.visible) continue;
      const v = m.position.clone().project(cam), px = r.left + (v.x + 1) / 2 * r.width, py = r.top + (1 - v.y) / 2 * r.height;
      if (px >= xa && px <= xb && py >= ya && py <= yb) hit.push(k);
    }
    applySel(hit, e); return;
  }
  ray.setFromCamera({ x: ((e.clientX - r.left) / r.width) * 2 - 1, y: -((e.clientY - r.top) / r.height) * 2 + 1 }, cam);
  const h = ray.intersectObjects(Object.values(lmMesh).filter(m => m.visible), false)[0];
  if (h) applySel([h.object.userData.key], e);
  else if (!(e.shiftKey || e.ctrlKey || e.metaKey)) pick(null);
});
function frameView(keys) {   // F / A: đưa tâm nhìn tới điểm, giữ hướng nhìn
  let c, d;
  if (keys && keys.length) { c = new THREE.Vector3(); keys.forEach(k => c.add(new THREE.Vector3(...LM[k]))); c.multiplyScalar(1 / keys.length); d = keys.length === 1 ? 140 : Math.max(140, cam.position.distanceTo(orbit.target) * .6); }
  else { c = TARGET.clone(); d = Math.max(115 / Math.tan(cam.fov * Math.PI / 360), 205 / (Math.tan(cam.fov * Math.PI / 360) * cam.aspect)); }
  const u = cam.position.clone().sub(orbit.target).normalize();
  orbit.target.copy(c); cam.position.copy(c).addScaledVector(u, d); orbit.update();
}

''' + s[b:]
# tool mode: select hides gizmo
rep("function setMode(m) { mode = m; tc.setMode(m); renderSel(); }",
    "function setMode(m) { mode = m; if (m !== 'select') tc.setMode(m); syncScene(); renderSel(); }")
rep("  if (S.size && step === 2) { if (!dragging) resetPivot(); tc.attach(pivot); } else tc.detach();",
    "  if (S.size && step === 2 && mode !== 'select') { if (!dragging) resetPivot(); tc.attach(pivot); } else tc.detach();")
rep('let mode = "translate";\n', '')
rep("const S = new Set();", 'const S = new Set();\nlet mode = "translate";')
rep('[["translate", "Dời (W)"], ["rotate", "Xoay (E)"], ["scale", "Co giãn (R)"]]', '[["select", "Chọn (Q)"], ["translate", "Dời (W)"], ["rotate", "Xoay (E)"], ["scale", "Co giãn (R)"]]')
rep('Chưa chọn khớp nào. Click một chấm; Shift/Ctrl+click để thêm; Shift+kéo khung để chọn nhiều.',
    'Chưa chọn khớp nào. Click một chấm hoặc kéo khung trên vùng trống. Shift đảo chọn, Ctrl bỏ chọn, Ctrl+Shift thêm.')
# phím tắt
a = s.index('window.addEventListener("keydown"')
b = s.index('window.matchMedia("(prefers-color-scheme: dark)")')
s = s[:a] + '''window.addEventListener("keydown", e => {
  if (/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) || e.altKey || e.ctrlKey || e.metaKey) return;
  const k = e.key.toLowerCase();
  if (k === "a") frameView(null);
  if (step !== 2) return;
  if (k === "q") setMode("select"); if (k === "w") setMode("translate"); if (k === "e") setMode("rotate"); if (k === "r") setMode("scale");
  if (k === "f") frameView([...S]); if (k === "escape") pick(null);
});
''' + s[b:]
# gợi ý ngay trên viewport
rep('<div class="vbar2" id="vopts"></div>', '<div class="vbar2" id="vopts"></div>\n    <div class="vhelp">Alt+chuột trái xoay · Alt+chuột giữa kéo · Alt+chuột phải hoặc lăn zoom · F nhìn vùng chọn · A nhìn toàn bộ</div>')
rep(".vbar2{", ".vhelp{position:absolute;right:8px;top:8px;font-size:11px;color:var(--mute);background:color-mix(in srgb,var(--panel) 80%,transparent);padding:3px 8px;border-radius:6px;max-width:45%}\n.vbar2{")
open(p, "w", encoding="utf8").write(s)
