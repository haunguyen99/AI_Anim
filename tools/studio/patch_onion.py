"""Vá onion skin kiểu Maya Ghost vào lõi Pose (2026-10-28, user: "Tính năng bóng mờ cần làm giống ghost của maya").
Áp CÙNG một bản vá vào work/pose_lab/index.html (template) và tools/studio/modules/pose_engine.js (bản Studio), không chạy
port_pose.py: pose_engine.js có sửa tay của đồng đội (khăn/kunai Ninja) chưa có trong template, sinh lại sẽ mất.
Chạy: python -I tools/studio/patch_onion.py   (chạy lại an toàn: bỏ qua file đã vá)"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FILES = [os.path.join(ROOT, "work", "pose_lab", "index.html"), os.path.join(ROOT, "tools", "studio", "modules", "pose_engine.js")]

ONION = r'''// ---------------------------------------------------------------- onion skin kiểu Maya Ghost (user 2026-10-28)
// Bóng mờ = pose ở các key (hoặc frame) TRƯỚC (cam) và SAU (xanh) frame đang xem, càng xa càng mờ. Chế độ "Pose gốc" = bóng cũ
// (pose key chưa cộng điều chỉnh / vật lý). Mỗi bóng là một bản model nạp thêm (không mixer), nạp lười khi cần.
const ONION = { mode: "k1", src: null, list: [], loading: null, off: 0 };
try { ONION.mode = localStorage.getItem("pl:onion") || "k1"; } catch (e) {}
const onionOn = () => $("tGhost") && $("tGhost").classList.contains("on") && ONION.mode !== "orig";
function onionReset(src) { ONION.list.forEach(o => scene.remove(o.root)); ONION.list = []; ONION.src = src; ONION.loading = null; }
function onionFrames(f) {
  const m = ONION.mode, n = NFR();
  if (m === "orig") return [];
  if (m[0] === "k") {
    const c = +m.slice(1), ks = keyList();
    return ks.filter(k => k < f).slice(-c).reverse().map((k, i) => ({ f: k, side: -1, i })).concat(ks.filter(k => k > f).slice(0, c).map((k, i) => ({ f: k, side: 1, i })));
  }
  const step = +m.slice(1), out = [];
  for (let i = 1; i <= 3; i++) { if (f - i * step >= 1) out.push({ f: f - i * step, side: -1, i: i - 1 }); if (f + i * step <= n) out.push({ f: f + i * step, side: 1, i: i - 1 }); }
  return out;
}
function onionEnsure(n) {
  if (ONION.list.length >= n || !ONION.src) return Promise.resolve();
  if (ONION.loading) return ONION.loading;
  const src = ONION.src;
  return (ONION.loading = (async () => {
    while (ONION.list.length < n) {
      const g = await loadGlb(src); if (src !== ONION.src) return;
      const root = g.scene, bones = {};
      root.traverse(o => { if (o.isBone) bones[o.name] = o; if (o.isMesh) { o.frustumCulled = false; o.material = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .2, depthWrite: false, skinning: !!o.isSkinnedMesh }); o.renderOrder = 2; } });
      root.visible = false; scene.add(root); ONION.list.push({ root, bones });
    }
    ONION.loading = null;
  })());
}
function onionUpdate(f) {          // gọi trong goto TRƯỚC khi dựng frame f (sampleAt ghi vào B; frame f dựng lại ngay sau)
  const show = onionOn() && !playing && !ONION.off, list = show ? onionFrames(f) : [];
  if (list.length > ONION.list.length) onionEnsure(list.length).then(() => { if (model) goto(frame); });
  ONION.list.forEach((o, k) => {
    const it = list[k]; if (!it) { o.root.visible = false; return; }
    sampleAt(it.f);
    for (const n in o.bones) if (B[n]) { o.bones[n].position.copy(B[n].position); o.bones[n].quaternion.copy(B[n].quaternion); }
    const col = it.side < 0 ? 0xff8a3d : 0x3da5ff, op = [0.3, 0.17, 0.09][it.i] || 0.07;
    o.root.traverse(m => { if (m.isMesh) { m.material.color.setHex(col); m.material.opacity = op; } });
    o.root.visible = true; o.root.updateMatrixWorld(true);
  });
}
function goto(f, first) {'''

REPL = [
    # 1. khối onion ngay trước goto
    ("function goto(f, first) {", ONION, 1),
    # 2. goto: dựng onion trước khi dựng frame hiện tại
    ("  if (!first) stashDraft();\n  frame = f; sampleAt(f);", "  if (!first) stashDraft();\n  onionUpdate(f);\n  frame = f; sampleAt(f);", 1),
    # 3. mở model: nhớ nguồn cho onion; bóng cũ chỉ hiện ở chế độ Pose gốc
    ("    ghost.visible = $(\"tGhost\").classList.contains(\"on\");\n    scene.add(model, ghost);",
     "    ghost.visible = $(\"tGhost\").classList.contains(\"on\") && ONION.mode === \"orig\";\n    scene.add(model, ghost); onionReset(src);", 1),
    # 4. nút bóng mờ + ô chọn chế độ
    ("$(\"tGhost\").onclick = () => { const on = !$(\"tGhost\").classList.contains(\"on\"); $(\"tGhost\").classList.toggle(\"on\", on); if (ghost) ghost.visible = on; };",
     "$(\"tGhost\").onclick = () => { const on = !$(\"tGhost\").classList.contains(\"on\"); $(\"tGhost\").classList.toggle(\"on\", on); if (ghost) ghost.visible = on && ONION.mode === \"orig\"; goto(frame); };\n"
     "(function () {   // ô chọn chế độ bóng mờ cạnh nút (như Ghost Options của Maya)\n"
     "  const b = $(\"tGhost\"); if (!b || $(\"tGhostMode\")) return;\n"
     "  const s = document.createElement(\"select\"); s.id = \"tGhostMode\"; s.className = \"ghostmode\"; s.style.cssText = \"height:28px;margin:0 4px 0 2px;font-size:12px;padding:0 4px\";\n"
     "  s.title = \"Bóng mờ như Ghost của Maya: key / frame trước (cam) và sau (xanh). Pose gốc = pose key chưa cộng điều chỉnh\";\n"
     "  s.innerHTML = [[\"k1\", \"1 key\"], [\"k2\", \"2 key\"], [\"k3\", \"3 key\"], [\"f2\", \"±2 F\"], [\"f4\", \"±4 F\"], [\"orig\", \"Pose gốc\"]].map(([v, t]) => `<option value=\"${v}\">${t}</option>`).join(\"\");\n"
     "  s.value = ONION.mode;\n"
     "  s.onchange = () => { ONION.mode = s.value; try { localStorage.setItem(\"pl:onion\", s.value); } catch (e) {} if (!b.classList.contains(\"on\")) b.click(); else { if (ghost) ghost.visible = ONION.mode === \"orig\"; goto(frame); } };\n"
     "  b.after(s);\n"
     "})();", 1),
    # 5. playblast / ảnh: ẩn onion (2 chỗ playblast)
    ("stopPlay(); if (ghost) ghost.visible = false; gizmo.detach();", "stopPlay(); if (ghost) ghost.visible = false; ONION.off++; goto(frame); gizmo.detach();", 2),
    ("if (ghost) ghost.visible = wasGhost; renderer.setSize(wasSize.x, wasSize.y, false);", "if (ghost) ghost.visible = wasGhost; ONION.off = Math.max(0, ONION.off - 1); renderer.setSize(wasSize.x, wasSize.y, false);", 2),
    ("const vis = [ghost.visible, grid.visible]; ghost.visible = false; grid.visible = false;", "const vis = [ghost.visible, grid.visible]; ghost.visible = false; grid.visible = false; ONION.list.forEach(o => o.root.visible = false);", 1),
]

for p in FILES:
    raw = open(p, "rb").read().decode("utf8"); crlf = "\r\n" in raw; s = raw.replace("\r\n", "\n")
    if "onionUpdate(" in s: print("đã vá:", os.path.relpath(p, ROOT)); continue
    for old, new, n in REPL:
        c = s.count(old); assert c == n, "%s: '%s…' khớp %d chỗ (cần %d)" % (os.path.basename(p), old[:50], c, n)
        s = s.replace(old, new)
    if crlf: s = s.replace("\n", "\r\n")
    open(p, "wb").write(s.encode("utf8")); print("vá xong:", os.path.relpath(p, ROOT))
