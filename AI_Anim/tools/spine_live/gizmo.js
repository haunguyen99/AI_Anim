// Trục xoay / dời (gizmo) như Spine, hiện khi chọn xương hoặc ảnh (ảnh: gizmo ở xương của ảnh).
// Chỉ hiện phần của công cụ đang chọn: C = vòng xanh dương (xoay); V = mũi tên đỏ X / xanh lá Y (trục của xương cha,
// đúng hệ ô X / Y) + ô vàng giữa (dời tự do); X = mũi tên đầu vuông theo trục xương + ô giữa (scale đều);
// Z = mũi tên đầu tròn theo trục xương (X: Shear X, Y: Shear Y, 2026-11-05 "thêm chức năng Shear như Spine là Z"); Q = không có.
// Xương trong chuỗi IK: gizmo nằm ở tay cầm IK (kéo xương đó cũng là dời tay cầm).
(() => {
  const R = 78, L = 58, HIT = 8;               // bán kính vòng xoay, độ dài mũi tên, vùng bắt (px màn hình)
  const RGB = { x: [1, 0.27, 0.27], y: [0.33, 0.9, 0.33], rot: [0.27, 0.68, 1], xy: [1, 0.85, 0.12] };
  const col = (k, a) => new spine.Color(RGB[k][0], RGB[k][1], RGB[k][2], a);
  const EDGE = new spine.Color(0, 0, 0, 0.6), WHITE = new spine.Color(1, 1, 1, 0.95);
  const G = { hover: null };

  function target() {
    if (!ed.on || !player) return null;
    let b = ed.sel;
    if (!b && ed.slot) b = player.skeleton.findSlot(ed.slot)?.bone || null;
    if (!b || !b.active) return null;
    const ik = ikOf(b);
    return ik ? ik.target : b;
  }
  function axes(b) {   // trục X / Y local của xương cha trong hệ world (x, y của xương tính theo hệ này)
    const P = b.parent, n = (x, y) => { const l = Math.hypot(x, y) || 1; return [x / l, y / l] };
    if (ed.tool === "scale" || ed.tool === "shear") return [n(b.a, b.c), n(b.b, b.d)];   // scale / shear: trục của chính xương
    return P ? [n(P.a, P.c), n(P.b, P.d)] : [[1, 0], [0, 1]];
  }
  // mỗi công cụ chỉ có phần gizmo của nó (người dùng 2026-11-02): C = vòng xoay, V = mũi tên + ô dời, X = mũi tên đầu vuông + ô giữa,
  // Q (chọn) = không có gizmo
  const parts = () => ed.tool === "select" ? null : ed.tool === "rotate" ? "rot" : "axes";
  function hit(ev) {
    const b = target(), P = parts(); if (!b || !P) return null;
    const v = toWorld(ev), px = pxWorld(player), dx = v.x - b.worldX, dy = v.y - b.worldY, d = Math.hypot(dx, dy) / px;
    if (P === "rot") return Math.abs(d - R) < HIT ? "rot" : null;
    if (d < 9) return "xy";
    const [ax, ay] = axes(b);
    for (const [k, [ux, uy]] of [["x", ax], ["y", ay]]) {
      const t = (dx * ux + dy * uy) / px, n = Math.abs(dx * uy - dy * ux) / px;
      if (t > 9 && t < L + 14 && n < HIT) return k;
    }
    return null;
  }
  function hover(ev) {
    const h = ed.on && player ? hit(ev) : null;
    if (h !== G.hover) { G.hover = h; $("stage").style.cursor = h ? (h === "rot" ? "grab" : "move") : "" }
  }
  // bấm trúng gizmo: bắt đầu kéo (trả true để trang khỏi xử lý chọn xương / ảnh)
  function down(ev) {
    const h = hit(ev); if (!h) return false;
    const b = target(), prevSel = ed.sel;
    if (!player.paused) player.pause();
    const v = toWorld(ev), P = b.parent, lp0 = P ? P.worldToLocal(new spine.Vector2(v.x, v.y)) : { x: v.x, y: v.y };
    edPush(b);
    const scale = ed.tool === "scale" && h !== "rot", shear = ed.tool === "shear" && h !== "rot";
    ed.drag = { b, move: h !== "rot" && !scale && !shear, scale, shear, sx0: b.scaleX, sy0: b.scaleY, shx0: b.shearX, shy0: b.shearY, wx0: v.x, wy0: v.y,
                axis: h === "x" || h === "y" ? h : null, gizmo: h, prevSel, hitBone: null,
                r0: b.rotation, x0: b.x, y0: b.y, lx: lp0.x, ly: lp0.y,
                a0: Math.atan2(v.y - b.worldY, v.x - b.worldX), flip: P && P.a * P.d - P.b * P.c < 0 ? -1 : 1, moved: false };
    try { $("stage").setPointerCapture(ev.pointerId) } catch {}
    edRefresh();
    return true;
  }
  // thả gizmo: giữ nguyên lựa chọn (ảnh vẫn là ảnh); bấm ô giữa không kéo = như bấm lại xương đang chọn (bỏ chọn)
  function up(d) {
    if (!d.moved && d.gizmo === "xy" && d.prevSel) ed.sel = null;
    else ed.sel = d.prevSel;
  }

  function ring(sr, x, y, r, w, c) {
    const N = 72;
    for (let i = 0; i < N; i++) {
      const a0 = i / N * 2 * Math.PI, a1 = (i + 1) / N * 2 * Math.PI;
      sr.rectLine(true, x + Math.cos(a0) * r, y + Math.sin(a0) * r, x + Math.cos(a1) * r, y + Math.sin(a1) * r, w, c);
    }
  }
  function arrow(sr, x, y, ux, uy, px, w, c) {
    const nx = -uy, ny = ux, s0 = 10 * px, s1 = L * px, hl = 13 * px, hw = 6 * px;
    sr.rectLine(true, x + ux * s0, y + uy * s0, x + ux * s1, y + uy * s1, w, c);
    const bx = x + ux * s1, by = y + uy * s1;
    if (ed.tool === "scale") { const q = hw * 1.1; sr.rect(true, bx - q, by - q, 2 * q, 2 * q, c); return }   // đầu vuông = scale
    if (ed.tool === "shear") { sr.circle(true, bx, by, hw * 1.2, c, 16); return }                              // đầu tròn = shear
    sr.triangle(true, bx + nx * hw, by + ny * hw, bx - nx * hw, by - ny * hw, bx + ux * hl, by + uy * hl, c, c, c);
  }
  function draw(p, sr, px) {
    const b = target(), P = parts(); if (!b || !P) return;
    const x = b.worldX, y = b.worldY, [ax, ay] = axes(b), act = ed.drag ? ed.drag.gizmo || (ed.drag.move || ed.drag.scale || ed.drag.shear ? "xy" : "rot") : G.hover;
    const w = k => (act === k ? 3.4 : 2.2) * px;
    if (P === "rot") {   // C: chỉ vòng xoay + vạch hướng xương
      ring(sr, x, y, R * px, w("rot") + 2 * px, EDGE);
      ring(sr, x, y, R * px, w("rot"), act === "rot" ? WHITE : col("rot", 0.9));
      const ang = Math.atan2(b.c, b.a), cx = Math.cos(ang), cy = Math.sin(ang);
      sr.rectLine(true, x + cx * (R - 10) * px, y + cy * (R - 10) * px, x + cx * (R + 10) * px, y + cy * (R + 10) * px, 3 * px, col("rot", 1));
      return;
    }
    // V / X: mũi tên X / Y (X: đầu vuông, theo trục xương) + ô giữa
    for (const [k, [ux, uy]] of [["x", ax], ["y", ay]]) {
      arrow(sr, x, y, ux, uy, px, w(k) + 2 * px, EDGE);
      arrow(sr, x, y, ux, uy, px, w(k), act === k ? WHITE : col(k, 1));
    }
    const s = (act === "xy" ? 7 : 5.5) * px;
    sr.rect(true, x - s - 1.5 * px, y - s - 1.5 * px, 2 * s + 3 * px, 2 * s + 3 * px, EDGE);
    sr.rect(true, x - s, y - s, 2 * s, 2 * s, act === "xy" ? WHITE : col("xy", 1));
  }
  window.spineGizmo = { draw, down, up, hover, hit, target };
})();
