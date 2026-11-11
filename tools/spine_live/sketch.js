// Vẽ góp ý lên khung xem, nằm trong mục "Ghi chú cho Claude" của bảng công cụ (2026-10-31).
// Người dùng: "vẽ góp ý hiện tại đang lỗi, hãy fix lại và cho chung vào với UI Ghi chú note để gen tại thanh công cụ bên phải".
// Bấm "✎ Vẽ lên hình" -> kéo chuột trên hình để vẽ (Esc tắt). Nét lưu theo toạ độ skeleton (không lệch khi zoom / pan).
// Gửi ghi chú / Gen (index.html) gọi spineSketch.payload(): nét + xương gần nhất + layer dưới nét + ảnh khung xem.
// Claude đọc bằng tools/spine_live_cmd.py notes. Ghi chú vẽ còn mở hiện mờ trên hình khi đang vẽ.
(() => {
  const COLS = { "đỏ": [1, 0.18, 0.18], "vàng": [1, 0.85, 0.1], "xanh": [0.2, 0.75, 1] };
  const S = { on: false, color: "đỏ", strokes: [], cur: null, open: [], shot: null };
  const stage = $("stage");
  $("skCols").innerHTML = Object.entries(COLS).map(([k, c]) => `<span class="sw" data-c="${k}" title="nét ${k}" style="background:rgb(${c.map(v => v * 255 | 0)})"></span>`).join("");
  function info() {
    const n = S.strokes.length, o = S.open.filter(x => (x.anim || "") === curAnim()).length;
    $("skInfo").textContent = [n ? n + " nét sẽ gửi kèm" : "", o ? o + " góp ý vẽ đang chờ Claude" : ""].filter(Boolean).join(" · ");
    $("skDraw").classList.toggle("on", S.on); $("skDraw").textContent = S.on ? "✎ Đang vẽ (Esc)" : "✎ Vẽ lên hình";
    $("skCols").querySelectorAll(".sw").forEach(e => e.classList.toggle("sel", e.dataset.c === S.color));
  }
  function setOn(on) {
    S.on = on; stage.classList.toggle("sketching", on);
    if (on && player && !player.paused) player.pause();
    if (on) loadOpen();
    info();
  }
  $("skDraw").onclick = () => setOn(!S.on);
  $("skCols").onclick = ev => { const c = ev.target.dataset?.c; if (c) { S.color = c; info() } };
  $("skUndo").onclick = () => { S.strokes.pop(); info() };
  $("skClear").onclick = () => { S.strokes = []; info() };

  // vẽ: nghe ở window (capture) để chạy trước chế độ chọn / kéo xương
  const onStage = ev => S.on && player && stage.contains(ev.target) && !ev.target.closest?.("#edPanel,#verPanel,#helpPop,#claude,.spine-player-controls,button,select,input,textarea");
  addEventListener("pointerdown", ev => {
    if (!onStage(ev) || ev.button !== 0 || ev.altKey) return;
    ev.stopImmediatePropagation(); ev.preventDefault();
    const v = toWorld(ev);
    S.cur = { color: S.color, pts: [[v.x, v.y]] };
    try { stage.setPointerCapture(ev.pointerId) } catch {}
  }, true);
  addEventListener("pointermove", ev => {
    if (!S.cur) return;
    ev.stopImmediatePropagation();
    const v = toWorld(ev), last = S.cur.pts[S.cur.pts.length - 1];
    if (Math.hypot(v.x - last[0], v.y - last[1]) >= 2.5 * pxWorld(player)) S.cur.pts.push([v.x, v.y]);
  }, true);
  for (const t of ["pointerup", "pointercancel"]) addEventListener(t, ev => {
    if (!S.cur) return;
    ev.stopImmediatePropagation();
    if (S.cur.pts.length > 1) S.strokes.push(S.cur);
    S.cur = null; info();
  }, true);
  addEventListener("keydown", ev => {
    if (!S.on || /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || "")) return;
    if (ev.key === "Escape") { ev.stopImmediatePropagation(); setOn(false) }
    else if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "z" && S.strokes.length) { ev.stopImmediatePropagation(); ev.preventDefault(); S.strokes.pop(); info() }
  }, true);

  // lớp vẽ (gọi trong overlay của index.html)
  function line(sr, pts, px, w, c) { for (let i = 1; i < pts.length; i++) sr.rectLine(true, pts[i - 1][0], pts[i - 1][1], pts[i][0], pts[i][1], w * px, c) }
  function draw(p, sr, px) {
    const a = curAnim();
    if (S.on) for (const n of S.open) {
      if ((n.anim || "") !== a) continue;
      for (const s of n.sketch?.strokes || []) { const c = COLS[s.color] || COLS["đỏ"]; line(sr, s.pts, px, 3, new spine.Color(c[0], c[1], c[2], 0.35)) }
    }
    for (const s of [...S.strokes, ...(S.cur ? [S.cur] : [])]) {
      const c = COLS[s.color];
      line(sr, s.pts, px, 6, new spine.Color(0, 0, 0, 0.55)); line(sr, s.pts, px, 3.5, new spine.Color(c[0], c[1], c[2], 1));
    }
    if (S.shot) { const done = S.shot; S.shot = null; queueMicrotask(() => done(p.sceneRenderer.canvas)) }   // chụp ngay sau khung hình
  }

  // mô tả nét: điểm đầu / cuối / giữa, dài, hướng, xương gần nhất (đoạn đầu -> đuôi xương), layer dưới điểm giữa
  function segDist(p, a, b) {
    const dx = b[0] - a[0], dy = b[1] - a[1], L2 = dx * dx + dy * dy;
    const t = L2 ? Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2)) : 0;
    return Math.hypot(p[0] - a[0] - dx * t, p[1] - a[1] - dy * t);
  }
  function nearBones(pt, k = 3) {
    return player.skeleton.bones.filter(b => b.active).map(b => {
      const h = [b.worldX, b.worldY], t = [b.worldX + (b.data.length || 0) * b.a, b.worldY + (b.data.length || 0) * b.c];
      return { bone: b.data.name, d: Math.round(segDist(pt, h, t) * 10) / 10 };
    }).sort((x, y) => x.d - y.d).slice(0, k);
  }
  function slotAt(pt) {   // layer có khung nhỏ nhất chứa điểm (khung to như mũ / thân trùm lên mọi thứ)
    const sk = player.skeleton, v = new Float32Array(8192);
    let best = null, area = Infinity;
    for (const s of sk.drawOrder) {
      const at = s.getAttachment(); if (!at || !s.bone.active) continue;
      let n = 0;
      if (at instanceof spine.RegionAttachment) { at.computeWorldVertices(s, v, 0, 2); n = 8 }
      else if (at instanceof spine.MeshAttachment) { n = at.worldVerticesLength; if (n > v.length) continue; at.computeWorldVertices(s, 0, n, v, 0, 2) }
      else continue;
      let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
      for (let j = 0; j < n; j += 2) { x0 = Math.min(x0, v[j]); x1 = Math.max(x1, v[j]); y0 = Math.min(y0, v[j + 1]); y1 = Math.max(y1, v[j + 1]) }
      const ar = (x1 - x0) * (y1 - y0);
      if (pt[0] >= x0 && pt[0] <= x1 && pt[1] >= y0 && pt[1] <= y1 && ar < area) { area = ar; best = s.data.name }
    }
    return best;
  }
  const R = v => Math.round(v * 10) / 10;
  function describe(s) {
    const P = s.pts, a = P[0], b = P[P.length - 1], c = P[Math.floor(P.length / 2)];
    let L = 0; for (let i = 1; i < P.length; i++) L += Math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]);
    return { color: s.color, pts: P.map(q => [R(q[0]), R(q[1])]), start: [R(a[0]), R(a[1])], end: [R(b[0]), R(b[1])], mid: [R(c[0]), R(c[1])],
             length: R(L), angle: R(Math.atan2(b[1] - a[1], b[0] - a[0]) * 180 / Math.PI),
             near_start: nearBones(a), near_end: nearBones(b), near_mid: nearBones(c), layer_mid: slotAt(c) };
  }
  function shoot() {   // ảnh khung xem kèm nét vẽ (JPEG, cạnh dài tối đa 1400 px); pane ẩn không có khung hình thì bỏ ảnh
    return new Promise(res => {
      const t = setTimeout(() => { S.shot = null; res("") }, 1200);
      S.shot = src => {
        clearTimeout(t);
        try {
          const k = Math.min(1, 1400 / Math.max(src.width, src.height)), c = document.createElement("canvas");
          c.width = Math.round(src.width * k); c.height = Math.round(src.height * k);
          const g = c.getContext("2d"); g.fillStyle = "#2a2e36"; g.fillRect(0, 0, c.width, c.height); g.drawImage(src, 0, 0, c.width, c.height);
          res(c.toDataURL("image/jpeg", 0.85));
        } catch { res("") }
      };
    });
  }
  // gọi từ Gửi ghi chú / Gen: {} khi không có nét
  async function payload() {
    if (!S.strokes.length || !player) return {};
    return { sketch: { strokes: S.strokes.map(describe) }, image: await shoot() };
  }
  function sent() { S.strokes = []; setOn(false); loadOpen() }
  async function loadOpen() {
    if (!cur) return;
    try { S.open = (await (await fetch("/api/spine/notes?json=" + encodeURIComponent(cur.json), { cache: "no-store" })).json()).filter(n => n.sketch) } catch { S.open = [] }
    info();
  }
  setInterval(() => { if (!document.hidden) loadOpen() }, 5000);
  info();
  window.spineSketch = { draw, S, setOn, payload, sent, has: () => S.strokes.length > 0 };
})();
