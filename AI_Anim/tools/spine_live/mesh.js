// Spine Live: sửa lưới mesh kiểu Spine (Edit Mesh): trên ảnh của attachment, ở toạ độ px ảnh.
// Dời / Thêm / Xoá điểm (gần viền = điểm viền, trong = điểm trong), Auto trace (server, OpenCV), xem trước tam giác,
// Áp dụng: server chia tam giác, giữ weight bằng nội suy từ lưới cũ (region -> mesh: gắn xương của slot), ghi file + backup.
// Dùng biến chung của index.html: player, cur, ed, edPost, build, snapshot, stamp, setStatus, hhmmss.
(() => {
  const M = { open: false, raw: null, slot: null, att: null, img: null, w: 0, h: 0, hull: [], inner: [], tris: [], undo: [], redo: [],
              tool: "move", sel: null, drag: null, k: 1, ox: 0, oy: 0, pan: null, triTimer: 0 };
  const box = document.createElement("div"); box.id = "meshEd"; box.hidden = true;
  box.innerHTML = `
    <div id="mBar">
      <b>Custom Mesh</b>
      <select id="mSlot" title="Slot / attachment để sửa lưới"></select>
      <span class="msep"></span>
      <button data-t="add" title="Thêm điểm (A): bấm gần viền = chèn điểm viền, bấm bên trong = điểm trong">Add (thêm)</button>
      <button data-t="del" title="Xoá điểm (D): bấm vào điểm, hoặc chọn rồi Delete">Delete (xoá)</button>
      <button data-t="move" title="Dời điểm (V): kéo">Dời</button>
      <span class="msep"></span>
      <label title="Mật độ điểm khi Auto trace: kéo là trace lại ngay (1 = ít điểm, 10 = dày)">Mật độ <input id="mDens" type="range" min="1" max="10" step="1" value="4"><i id="mDensV">4</i></label>
      <span class="msep"></span>
      <label title="Độ bám viền khi trace (px): nhỏ = sát hơn, nhiều điểm hơn">Bám <input id="mDetail" type="range" min="1" max="15" step="0.5" value="4"><i id="mDetailV">4</i></label>
      <label title="Cạnh viền dài nhất (px)">Cạnh <input id="mEdge" type="number" min="20" max="600" step="10" value="120"></label>
      <label title="Khoảng cách điểm trong khi trace (px, 0 = không thêm)">Điểm trong <input id="mSpace" type="number" min="0" max="400" step="5" value="0"></label>
      <button id="mTrace" class="primary" title="Tự dò viền theo độ trong suốt của ảnh (thay điểm hiện tại)">Auto trace</button>
      <details id="mAdv"><summary>chi tiết</summary>
      </details>
      <button id="mClearIn" title="Xoá mọi điểm trong">Xoá điểm trong</button>
      <button id="mReset" title="Về lưới đang có trong file">Về ban đầu</button>
      <span class="msep"></span>
      <button id="mApply" class="primary" title="Ghi lưới vào file JSON (giữ weight bằng nội suy từ lưới cũ)">Áp dụng</button>
      <button id="mClose">Đóng</button>
    </div>
    <div id="mInfo"></div>
    <canvas id="mCv" tabindex="0"></canvas>
    <div id="mHelp">Kéo điểm: dời · Thêm: bấm gần viền = điểm viền, bên trong = điểm trong · Xoá / Delete · Ctrl+Z lùi · cuộn: zoom · kéo chuột giữa / phải: dời khung · cam = viền, đỏ = điểm trong, xanh = tam giác</div>`;
  document.querySelector("main").appendChild(box);
  const st = document.createElement("style");
  st.textContent = `#meshEd{position:absolute;inset:12px 324px 12px 12px;z-index:20;display:flex;flex-direction:column;gap:6px;padding:10px;border-radius:10px;background:var(--panel);border:1px solid var(--accent);box-shadow:0 6px 30px #0008}
    #mBar{display:flex;gap:6px;align-items:center;flex-wrap:wrap;font-size:12px} #mBar .msep{width:1px;height:18px;background:var(--line)}
    #mBar button.on{border-color:var(--accent);color:var(--accent);font-weight:600} #mBar input[type=number]{width:56px} #mBar input[type=range]{width:90px}
    body:has(#edPanel.docked) #meshEd{right:12px} #mAdv{display:inline-flex} #mAdv[open]{gap:6px} #mAdv summary{cursor:pointer;color:var(--mute)}
    #mInfo{font-size:12px;color:var(--mute)} #mHelp{font-size:11px;color:var(--mute)}
    #mCv{flex:1;min-height:0;width:100%;border-radius:6px;background:conic-gradient(#0000 25%,#8882 0 50%,#0000 0 75%,#8882 0) 0 0/20px 20px;outline:none}`;
  document.head.appendChild(st);
  const openBtn = document.createElement("button"); openBtn.id = "meshOpen"; openBtn.textContent = "Lưới…"; openBtn.className = "setupOnly";
  openBtn.title = "Sửa lưới mesh (thêm / dời / xoá điểm, auto trace, đổi region thành mesh)";
  document.getElementById("edReset").closest(".row").append(openBtn);
  const cv = box.querySelector("#mCv"), $m = s => box.querySelector(s);

  // ---- mở / nạp ----
  function imagesDir() { return cur?.atlas?.endsWith("_auto.atlas") ? cur.atlas.slice(0, cur.atlas.lastIndexOf("/")) : null }
  async function open() {
    if (!player || !cur) return;
    if (ed.dirty.size) return setStatus("đang có xương sửa chưa key: Key pose hoặc Bỏ sửa trước khi sửa lưới", "bad");
    if (!imagesDir()) return setStatus("sửa lưới chỉ làm được trên file build có thư mục images/ (không phải bản export)", "bad");
    M.raw = await (await fetch("/spine-live/f/" + cur.json, { cache: "no-store" })).json();
    const skin = M.raw.skins?.[0]?.attachments || {}, opts = [];
    for (const s of M.raw.slots || []) for (const [an, a] of Object.entries(skin[s.name] || {}))
      if (!a.type || a.type === "region" || a.type === "mesh") opts.push({ slot: s.name, att: an, mesh: a.type === "mesh", bone: s.bone });
    const sel = $m("#mSlot");
    sel.innerHTML = opts.map((o, i) => `<option value="${i}">${o.slot}${o.att !== o.slot ? " / " + o.att : ""}${o.mesh ? " (mesh)" : " (region)"}</option>`).join("");
    M.opts = opts;
    const want = ed.slot && opts.findIndex(o => o.slot === ed.slot) >= 0 ? opts.findIndex(o => o.slot === ed.slot)   // layer đang chọn
      : opts.findIndex(o => o.slot === M.slot) >= 0 ? opts.findIndex(o => o.slot === M.slot)
      : Math.max(0, opts.findIndex(o => ed.sel && o.bone === ed.sel.data.name && o.mesh), opts.findIndex(o => ed.sel && o.bone === ed.sel.data.name));
    sel.value = String(Math.max(0, want));
    M.open = true; box.hidden = false; await pick(); cv.focus();
  }
  async function pick() {
    const o = M.opts[+$m("#mSlot").value]; if (!o) return;
    M.slot = o.slot; M.att = o.att;
    const a = M.raw.skins[0].attachments[o.slot][o.att];
    M.img = new Image(); M.img.src = "/spine-live/f/" + imagesDir() + "/" + (a.path || o.att) + ".png?" + Date.now();
    await M.img.decode().catch(() => {});
    M.w = a.width || M.img.naturalWidth; M.h = a.height || M.img.naturalHeight;
    if (a.type === "mesh") {
      const n = a.uvs.length / 2, pts = []; for (let i = 0; i < n; i++) pts.push([a.uvs[2 * i] * M.w, a.uvs[2 * i + 1] * M.h]);
      M.hull = pts.slice(0, a.hull); M.inner = pts.slice(a.hull);
    } else { M.hull = [[0, 0], [M.w, 0], [M.w, M.h], [0, M.h]]; M.inner = [] }
    M.orig = JSON.stringify([M.hull, M.inner]); M.undo = []; M.sel = null; fit(); retri();
  }
  function fit() { const W = cv.clientWidth, H = cv.clientHeight; M.k = Math.min(W / M.w, H / M.h) * 0.9; M.ox = (W - M.w * M.k) / 2; M.oy = (H - M.h * M.k) / 2 }
  const S = p => [M.ox + p[0] * M.k, M.oy + p[1] * M.k];
  const P = (x, y) => [(x - M.ox) / M.k, (y - M.oy) / M.k];
  function push() { M.undo.push(JSON.stringify([M.hull, M.inner])); M.redo = []; if (M.undo.length > 200) M.undo.shift() }
  function retri() {   // xem trước tam giác (server chia, cùng cách lúc Áp dụng)
    clearTimeout(M.triTimer);
    M.triTimer = setTimeout(async () => {
      try { const j = await edPost("/api/spine/mesh/tri", { hull: M.hull, inner: M.inner, w: M.w, h: M.h }); M.tris = j.triangles; M.missing = j.missing }
      catch (e) { M.tris = []; M.missing = []; $m("#mInfo").textContent = "chưa chia được tam giác: " + e.message }
    }, 120);
  }

  // ---- vẽ ----
  function draw() {
    if (!M.open) return;
    const dpr = devicePixelRatio || 1, W = cv.clientWidth, H = cv.clientHeight;
    if (cv.width !== Math.round(W * dpr) || cv.height !== Math.round(H * dpr)) { cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr) }
    const g = cv.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, W, H);
    if (M.img?.complete) g.drawImage(M.img, M.ox, M.oy, M.w * M.k, M.h * M.k);
    g.strokeStyle = "#ffffff40"; g.strokeRect(M.ox, M.oy, M.w * M.k, M.h * M.k);
    const pts = M.hull.concat(M.inner);
    g.strokeStyle = "#3ad0ffcc"; g.lineWidth = 1;
    for (const t of M.tris || []) { if (t.some(i => !pts[i])) continue; g.beginPath(); g.moveTo(...S(pts[t[0]])); g.lineTo(...S(pts[t[1]])); g.lineTo(...S(pts[t[2]])); g.closePath(); g.stroke() }
    if (M.hull.length) { g.strokeStyle = "#ff8c1a"; g.lineWidth = 2; g.beginPath(); g.moveTo(...S(M.hull[0])); for (const p of M.hull.slice(1)) g.lineTo(...S(p)); g.closePath(); g.stroke(); g.lineWidth = 1 }
    const dot = (p, c, on) => { const [x, y] = S(p); g.fillStyle = "#000"; g.beginPath(); g.arc(x, y, on ? 6 : 4.5, 0, 7); g.fill(); g.fillStyle = on ? "#fff" : c; g.beginPath(); g.arc(x, y, on ? 4.5 : 3.2, 0, 7); g.fill() };
    M.hull.forEach((p, i) => dot(p, "#ff8c1a", M.sel?.list === "hull" && M.sel.i === i));
    M.inner.forEach((p, i) => dot(p, "#ff3b5c", M.sel?.list === "inner" && M.sel.i === i));
    box.querySelectorAll("#mBar button[data-t]").forEach(b => b.classList.toggle("on", b.dataset.t === M.tool));
    const miss = M.missing?.length ? ` · ${M.missing.length} cạnh viền chưa có tam giác (viền tự cắt?)` : "";
    $m("#mInfo").textContent = `${M.slot} · ảnh ${M.w}×${M.h} · ${M.hull.length + M.inner.length} đỉnh (viền ${M.hull.length}, trong ${M.inner.length}) · ${(M.tris || []).length} tam giác${miss}`;
  }
  (function loop() { try { draw() } catch (e) { console.warn(e) } requestAnimationFrame(loop) })();

  // ---- thao tác ----
  function nearest(x, y, lim = 9) {
    let best = null, bd = lim;
    for (const list of ["inner", "hull"]) M[list].forEach((p, i) => { const [sx, sy] = S(p), d = Math.hypot(sx - x, sy - y); if (d < bd) { bd = d; best = { list, i } } });
    return best;
  }
  function edgeAt(x, y, lim = 10) {   // cạnh viền gần nhất trong lim px màn hình
    let best = null, bd = lim;
    for (let i = 0; i < M.hull.length; i++) {
      const [ax, ay] = S(M.hull[i]), [bx, by] = S(M.hull[(i + 1) % M.hull.length]), dx = bx - ax, dy = by - ay;
      const u = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / ((dx * dx + dy * dy) || 1))), d = Math.hypot(ax + dx * u - x, ay + dy * u - y);
      if (d < bd) { bd = d; best = i }
    }
    return best;
  }
  function inside(p) { let c = false; const h = M.hull; for (let i = 0, j = h.length - 1; i < h.length; j = i++) { const [xi, yi] = h[i], [xj, yj] = h[j]; if ((yi > p[1]) !== (yj > p[1]) && p[0] < (xj - xi) * (p[1] - yi) / (yj - yi) + xi) c = !c } return c }
  function del(s) {
    if (!s) return;
    if (s.list === "hull" && M.hull.length <= 3) return setStatus("viền cần ít nhất 3 điểm", "bad");
    push(); M[s.list].splice(s.i, 1); M.sel = null; retri();
  }
  cv.addEventListener("pointerdown", ev => {
    const r = cv.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top;
    if (ev.button === 1 || ev.button === 2) { M.pan = { x: ev.clientX, y: ev.clientY, ox: M.ox, oy: M.oy }; try { cv.setPointerCapture(ev.pointerId) } catch {} ev.preventDefault(); return }
    if (ev.button !== 0) return;
    const hitP = nearest(x, y);
    if (M.tool === "del") { del(hitP); return }
    if (M.tool === "add" && !hitP) {
      const p = P(x, y).map(v => +v.toFixed(2)), e = edgeAt(x, y);
      push();
      if (e !== null) { M.hull.splice(e + 1, 0, p); M.sel = { list: "hull", i: e + 1 } }
      else if (inside(p)) { M.inner.push(p); M.sel = { list: "inner", i: M.inner.length - 1 } }
      else { M.undo.pop(); return setStatus("bấm gần viền để chèn điểm viền, hoặc bên trong lưới để thêm điểm trong", "bad") }
      retri(); return;
    }
    M.sel = hitP;
    if (hitP) { push(); M.drag = { moved: false }; try { cv.setPointerCapture(ev.pointerId) } catch {} }
  });
  cv.addEventListener("pointermove", ev => {
    if (M.pan) { M.ox = M.pan.ox + ev.clientX - M.pan.x; M.oy = M.pan.oy + ev.clientY - M.pan.y; return }
    if (!M.drag || !M.sel) return;
    const r = cv.getBoundingClientRect(), p = P(ev.clientX - r.left, ev.clientY - r.top);
    M[M.sel.list][M.sel.i] = [+Math.max(0, Math.min(M.w, p[0])).toFixed(2), +Math.max(0, Math.min(M.h, p[1])).toFixed(2)];
    M.drag.moved = true;
  });
  for (const t of ["pointerup", "pointercancel"]) cv.addEventListener(t, () => {
    if (M.pan) { M.pan = null; return }
    if (M.drag) { if (!M.drag.moved) M.undo.pop(); else retri(); M.drag = null }
  });
  cv.addEventListener("contextmenu", ev => ev.preventDefault());
  cv.addEventListener("wheel", ev => {
    ev.preventDefault(); const r = cv.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top, f = Math.pow(1.0015, -ev.deltaY);
    M.ox = x + (M.ox - x) * f; M.oy = y + (M.oy - y) * f; M.k *= f;
  }, { passive: false });
  // trình sửa lưới đang mở: phím tắt luôn vào đây (kể cả khi focus ở nút Trace / ô số), không xuống trang
  window.addEventListener("keydown", ev => {
    if (!M.open || ev.target === cv || /^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName)) return;
    const kk = ev.key.toLowerCase();
    if ((ev.ctrlKey || ev.metaKey) && (kk === "z" || kk === "y") || ev.key === "Delete" || ev.key === "Escape") {
      ev.preventDefault(); ev.stopImmediatePropagation(); cv.dispatchEvent(new KeyboardEvent("keydown", { key: ev.key, ctrlKey: ev.ctrlKey, metaKey: ev.metaKey, shiftKey: ev.shiftKey }));
    }
  }, true);
  cv.addEventListener("keydown", ev => {
    ev.stopPropagation();   // phím trong trình sửa lưới không đi xuống trang (Ctrl+Z, Delete...)
    const kk = ev.key.toLowerCase();
    if ((ev.ctrlKey || ev.metaKey) && (kk === "y" || (kk === "z" && ev.shiftKey))) { ev.preventDefault(); const u = M.redo.pop(); if (u) { M.undo.push(JSON.stringify([M.hull, M.inner])); [M.hull, M.inner] = JSON.parse(u); M.sel = null; retri() } }
    else if ((ev.ctrlKey || ev.metaKey) && kk === "z") { ev.preventDefault(); const u = M.undo.pop(); if (u) { M.redo.push(JSON.stringify([M.hull, M.inner])); [M.hull, M.inner] = JSON.parse(u); M.sel = null; retri(); setStatus("lưới: hoàn tác (còn " + M.undo.length + " bước)", "ok") } else setStatus("lưới: không còn bước để hoàn tác", "") }
    else if (ev.key === "Delete" || ev.key === "Backspace") { ev.preventDefault(); del(M.sel) }
    else if (kk === "escape") close();
    else if (kk === "v" || kk === "m") M.tool = "move"; else if (kk === "a") M.tool = "add"; else if (kk === "d") M.tool = "del";
    else if (kk === "f") fit();
  });
  box.querySelectorAll("#mBar button[data-t]").forEach(b => b.onclick = () => { M.tool = b.dataset.t; cv.focus() });
  // Mật độ (2026-10-31: "auto trace có thể điều chỉnh độ nhiều của point, realtime"): 1 thưa -> 10 dày
  let densT = 0;
  function densApply() {
    const d = +$m("#mDens").value, big = Math.max(M.w || 300, M.h || 300);
    $m("#mDensV").textContent = d;
    $m("#mDetail").value = (9 - 0.8 * (d - 1)).toFixed(1); $m("#mDetailV").textContent = $m("#mDetail").value;
    $m("#mEdge").value = Math.round(Math.max(30, big / (1.2 + d * 0.9)));
    $m("#mSpace").value = d <= 2 ? 0 : Math.round(big / (1 + d * 1.1));
  }
  $m("#mDens").oninput = () => { densApply(); clearTimeout(densT); densT = setTimeout(() => $m("#mTrace").click(), 220) };
  $m("#mDetail").oninput = () => $m("#mDetailV").textContent = $m("#mDetail").value;
  $m("#mSlot").onchange = () => pick();
  $m("#mTrace").onclick = async () => {
    try {
      const j = await edPost("/api/spine/mesh/trace", { json: cur.json, slot: M.slot, attachment: M.att, detail: +$m("#mDetail").value, maxEdge: +$m("#mEdge").value, spacing: +$m("#mSpace").value });
      push(); M.hull = j.hull; M.inner = j.inner; M.sel = null; retri();
      setStatus("auto trace: " + j.hull.length + " điểm viền, " + j.inner.length + " điểm trong", "ok");
    } catch (e) { setStatus("trace lỗi: " + e.message, "bad") }
  };
  $m("#mClearIn").onclick = () => { if (!M.inner.length) return; push(); M.inner = []; M.sel = null; retri() };
  $m("#mReset").onclick = () => { push(); [M.hull, M.inner] = JSON.parse(M.orig); M.sel = null; retri() };
  $m("#mApply").onclick = async () => {
    try {
      const j = await edPost("/api/spine/mesh/apply", { json: cur.json, slot: M.slot, attachment: M.att, hull: M.hull, inner: M.inner });
      setStatus(`đã ghi lưới ${M.slot}: ${j.vertices} đỉnh, ${j.triangles} tam giác${j.weighted ? ", giữ weight cũ (nội suy)" : ""}${j.droppedDeform ? ", bỏ " + j.droppedDeform + " deform cũ" : ""} · ${hhmmss()}`, "ok");
      close(); stamp = null; build(snapshot());
    } catch (e) { setStatus("ghi lưới lỗi: " + e.message, "bad") }
  };
  function close() { M.open = false; box.hidden = true }
  $m("#mClose").onclick = close;
  openBtn.onclick = () => M.open ? close() : open();
  M.close = close;
  window.spineMesh = M;
})();
