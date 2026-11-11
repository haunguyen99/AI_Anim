// Spine Live: weight như Spine (tab Setup). Chọn xương -> "+ xương" vào danh sách bind; chọn mesh -> Bind (weight tự động);
// Sơn weight (W): chọn xương trong danh sách, kéo cọ trên mesh: Thêm / Bớt / Làm mượt; xem ngay biến dạng + màu weight.
// Lưu weight ghi file (POST /api/spine/weights). Ctrl+Z lùi từng nét cọ. Sửa dở: ed.dirty có "__weights" để trang không nạp đè.
// Dùng biến chung của index.html: player, cur, ed, mode, toWorld, pxWorld, edPost, build, snapshot, stamp, setStatus, hhmmss, weightCache.
(() => {
  const Wt = { list: [], paint: false, bone: null, mode: "add", strength: 0.35, size: 40, sess: null, undo: [], down: false, cursor: null };
  const sec = document.createElement("section"); sec.id = "wSec"; sec.className = "sec tool setupOnly";
  sec.innerHTML = `
    <h3 class="secT">Weight</h3><div class="row"><span id="wMesh" class="mute">bấm chọn một mesh trên hình</span></div>
    <div class="row" title="Xương sẽ bind / đang bind. Bấm tên: sơn weight của xương đó; ×: bỏ khỏi danh sách"><span>Xương:</span><span id="wChips"></span></div>
    <div class="row">
      <button id="wAdd" title="Thêm xương đang chọn vào danh sách bind">+ xương đang chọn</button>
      <button id="wBind" title="Bind mesh vào các xương trong danh sách, weight tự động theo khoảng cách (như Bind của Spine)">Bind</button>
    </div>
    <div class="row">
      <button id="wPaint" title="Bật / tắt cọ sơn weight (phím W)">Sơn weight (W)</button>
      <select id="wMode"><option value="add">Thêm</option><option value="sub">Bớt</option><option value="smooth">Làm mượt</option></select>
    </div>
    <div class="row">
      <label title="Độ mạnh mỗi lần quét">Mạnh <input id="wStr" type="range" min="0.02" max="1" step="0.02" value="0.35"></label>
      <label title="Cỡ cọ (px màn hình)">Cỡ <input id="wSize" type="range" min="8" max="200" step="2" value="40"></label>
    </div>
    <div class="row">
      <button id="wSave" class="primary" title="Ghi weight đã sơn vào file">Lưu weight</button>
      <button id="wDrop" title="Bỏ weight đã sơn, nạp lại từ file">Bỏ</button>
    </div>`;
  document.getElementById("secBone").after(sec);
  const st = document.createElement("style");
  st.textContent = `
    #wChips{display:inline-flex;flex-wrap:wrap;gap:4px} .wChip{display:inline-flex;gap:3px;align-items:center;padding:1px 6px;border-radius:10px;background:#ffffff14;cursor:pointer}
    .wChip.on{background:#ffd21a;color:#000;font-weight:600} .wChip i{font-style:normal;opacity:.6} .wChip i:hover{opacity:1}
    #wPaint.on{border-color:#ffd21a;color:#ffd21a;font-weight:600} #wSec input[type=range]{width:80px}`;
  document.head.appendChild(st);
  const q = s => sec.querySelector(s);

  function slotAt() { const s = ed.slot && player?.skeleton?.findSlot(ed.slot); const at = s?.getAttachment(); return s && at ? { s, at } : null }
  function onSelect() {   // đổi mesh: danh sách bind = xương mesh đang bind
    const o = slotAt();
    if (o && Wt.sess && Wt.sess.slot !== o.s.data.name && Wt.sess.dirty) { setStatus("mesh trước còn weight chưa lưu: Lưu weight hoặc Bỏ", "bad") }
    if (o && o.at instanceof spine.MeshAttachment) Wt.list = window.spineSel.boundBones(o.at).length ? window.spineSel.boundBones(o.at) : [o.s.bone.data.name];
    render();
  }
  function render() {
    const o = slotAt();
    q("#wMesh").textContent = !o ? "bấm chọn một mesh trên hình (hoặc tab Layer)" : o.at instanceof spine.MeshAttachment
      ? `${o.s.data.name}: ${o.at.worldVerticesLength / 2} đỉnh, ${o.at.bones ? "đã bind " + window.spineSel.boundBones(o.at).length + " xương" : "chưa bind"}${Wt.sess?.dirty ? " · weight chưa lưu" : ""}`
      : `${o.s.data.name} là ảnh (region): mở Lưới… → Áp dụng để thành mesh rồi bind`;
    q("#wChips").innerHTML = Wt.list.map(n => `<span class="wChip ${n === Wt.bone ? "on" : ""}" data-b="${n}">${n}<i data-x="${n}">×</i></span>`).join("") || '<span style="color:var(--mute)">(chưa có)</span>';
    q("#wChips").querySelectorAll(".wChip").forEach(c => c.onclick = ev => {
      if (ev.target.dataset.x) { Wt.list = Wt.list.filter(n => n !== ev.target.dataset.x); if (Wt.bone === ev.target.dataset.x) Wt.bone = null }
      else { Wt.bone = c.dataset.b; const sel = document.getElementById("wBone"); sel.value = Wt.bone; store.set("wBone", Wt.bone) }
      render();
    });
    q("#wPaint").classList.toggle("on", Wt.paint);
  }
  q("#wAdd").onclick = () => { if (!ed.sel) return setStatus("bấm chọn một xương trước (khớp xương trên hình hoặc tab Xương)", "bad");
    const n = ed.sel.data.name; if (!Wt.list.includes(n)) Wt.list.push(n); Wt.bone = Wt.bone || n; render() };
  q("#wBind").onclick = async () => {
    const o = slotAt(); if (!o) return setStatus("chọn một mesh trước", "bad");
    if (!Wt.list.length) return setStatus("thêm ít nhất một xương vào danh sách", "bad");
    if (ed.dirty.size) return setStatus("đang có chỉnh sửa chưa ghi: lưu hoặc Bỏ trước khi bind", "bad");
    try { const j = await edPost("/api/spine/bind", { json: cur.json, slot: o.s.data.name, attachment: o.at.name, bones: Wt.list });
      endSess(); stamp = null; build(snapshot()); setStatus(`đã bind ${o.s.data.name} vào ${j.bones.join(", ")} (weight tự động) · ${hhmmss()}`, "ok") }
    catch (e) { setStatus("bind lỗi: " + e.message, "bad") }
  };
  function setPaint(on) {
    if (on && mode !== "setup") return setStatus("sơn weight ở tab Setup", "bad");
    Wt.paint = on; if (on && !Wt.bone && Wt.list.length) Wt.bone = Wt.list[0];
    if (on && Wt.bone) { document.getElementById("wBone").value = Wt.bone; store.set("wBone", Wt.bone) }
    render(); setStatus(on ? "sơn weight: kéo trên mesh đang chọn · xương " + (Wt.bone || "(chọn trong danh sách)") : "tắt cọ sơn weight", "ok");
  }
  q("#wPaint").onclick = () => setPaint(!Wt.paint);
  q("#wMode").onchange = () => Wt.mode = q("#wMode").value;
  q("#wStr").oninput = () => Wt.strength = +q("#wStr").value;
  q("#wSize").oninput = () => Wt.size = +q("#wSize").value;
  document.addEventListener("keydown", ev => { if (ev.key.toLowerCase() === "w" && !ev.ctrlKey && !ev.metaKey && mode === "setup" && !/^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName)) setPaint(!Wt.paint) });

  // ---- phiên sơn: bảng weight [đỉnh] -> Map(chỉ số xương -> w), vị trí thế giới ở setup ----
  function startSess(o) {
    const at = o.at, sk = player.skeleton, n = at.worldVerticesLength / 2, world = new Float32Array(n * 2);
    at.computeWorldVertices(o.s, 0, n * 2, world, 0, 2);
    const table = [];
    if (at.bones) { for (let i = 0, v = 0, f = 0; v < n; v++) { const m = new Map(), c = at.bones[i++]; for (let k = 0; k < c; k++, f += 3) m.set(at.bones[i++], (m.get(at.bones[i - 1]) || 0) + at.vertices[f + 2]); table.push(m) } }
    else for (let v = 0; v < n; v++) table.push(new Map([[o.s.bone.data.index, 1]]));
    const nb = Array.from({ length: n }, () => new Set());
    for (let k = 0; k < at.triangles.length; k += 3) { const t = at.triangles; for (const [a, b] of [[t[k], t[k + 1]], [t[k + 1], t[k + 2]], [t[k + 2], t[k]]]) { nb[a].add(b); nb[b].add(a) } }
    Wt.sess = { slot: o.s.data.name, at, n, world, table, nb, dirty: false };
    Wt.undo = [];
  }
  function endSess() { Wt.sess = null; Wt.undo = []; ed.dirty.delete("__weights") }
  function rebuild() {   // bảng weight -> mảng bones / vertices của attachment (xem ngay)
    const { at, table, world } = Wt.sess, bs = player.skeleton.bones, B = [], V = [];
    table.forEach((m, v) => {
      const e = [...m].filter(([, w]) => w > 0.002); const tot = e.reduce((s, [, w]) => s + w, 0) || 1;
      B.push(e.length);
      for (const [bi, w] of e) { const lp = bs[bi].worldToLocal(new spine.Vector2(world[v * 2], world[v * 2 + 1])); B.push(bi); V.push(lp.x, lp.y, w / tot) }
    });
    at.bones = B; at.vertices = V;
    weightCache.delete(at);
  }
  function segDist(b, x, y) {
    const L = b.data.length, dx = b.a * L, dy = b.c * L;
    if (L <= 0) return Math.hypot(x - b.worldX, y - b.worldY);
    const u = Math.max(0, Math.min(1, ((x - b.worldX) * dx + (y - b.worldY) * dy) / (dx * dx + dy * dy)));
    return Math.hypot(b.worldX + dx * u - x, b.worldY + dy * u - y);
  }
  function dab(ev) {   // một lần quét cọ tại con trỏ
    const S0 = Wt.sess, sk = player.skeleton, bone = sk.findBone(Wt.bone); if (!bone) return;
    const bi = bone.data.index, v = toWorld(ev), R = Wt.size * pxWorld(player);
    const slot = sk.findSlot(S0.slot), n = S0.n, cur = new Float32Array(n * 2);
    S0.at.computeWorldVertices(slot, 0, n * 2, cur, 0, 2);
    const listIdx = Wt.list.map(nm => sk.findBone(nm)?.data.index).filter(i => i !== undefined);
    const avg = Wt.mode === "smooth" ? S0.table.map((m, i) => { const a = new Map(); let c = 0; for (const j of S0.nb[i]) { c++; for (const [k, w] of S0.table[j]) a.set(k, (a.get(k) || 0) + w) } for (const [k, w] of a) a.set(k, w / (c || 1)); return a }) : null;
    let hit = 0;
    for (let i = 0; i < n; i++) {
      const d = Math.hypot(cur[i * 2] - v.x, cur[i * 2 + 1] - v.y); if (d > R) continue;
      const x = d / R, f = Wt.strength * (1 - x * x) ** 2, m = S0.table[i]; hit++;
      if (Wt.mode === "smooth") { const a = avg[i]; const keys = new Set([...m.keys(), ...a.keys()]); for (const k of keys) m.set(k, (m.get(k) || 0) * (1 - f) + (a.get(k) || 0) * f) }
      else {
        const w0 = m.get(bi) || 0, w1 = Wt.mode === "add" ? w0 + f * (1 - w0) : w0 * (1 - f);
        const rest = 1 - w0, rest1 = 1 - w1;
        if (rest > 1e-6) { for (const [k, w] of m) if (k !== bi) m.set(k, w * rest1 / rest) }
        else if (rest1 > 1e-6) {   // đỉnh đang 100% xương này mà bớt: phần dư sang xương gần nhất trong danh sách
          const others = listIdx.filter(k => k !== bi); if (!others.length) continue;
          const near = others.reduce((a, k) => segDist(sk.bones[k], S0.world[i * 2], S0.world[i * 2 + 1]) < segDist(sk.bones[a], S0.world[i * 2], S0.world[i * 2 + 1]) ? k : a);
          m.set(near, (m.get(near) || 0) + rest1);
        }
        m.set(bi, w1);
      }
      let tot = 0; for (const [k, w] of m) { if (w < 0.002) m.delete(k); else tot += w } for (const [k, w] of m) m.set(k, w / (tot || 1));
    }
    if (hit) { S0.dirty = true; ed.dirty.add("__weights"); rebuild() }
  }
  // ---- chuột: khi cọ bật, kéo trên khung xem = sơn (gọi từ pointerdown của chế độ Sửa trong index.html) ----
  function paintDown(ev) {
    if (!Wt.paint || mode !== "setup" || ev.button !== 0) return false;
    const o = slotAt();
    if (!o || !(o.at instanceof spine.MeshAttachment)) { setStatus("chọn một mesh để sơn (bấm vào hình khi tắt cọ, hoặc tab Layer)", "bad"); return true }
    if (!Wt.bone) { setStatus("bấm tên một xương trong danh sách để sơn weight của nó", "bad"); return true }
    if (!Wt.sess || Wt.sess.slot !== o.s.data.name || Wt.sess.at !== o.at) startSess(o);
    Wt.undo.push(Wt.sess.table.map(m => new Map(m))); if (Wt.undo.length > 100) Wt.undo.shift();
    Wt.down = true; dab(ev); render(); return true;
  }
  document.getElementById("stage").addEventListener("pointermove", ev => {
    Wt.cursor = Wt.paint && mode === "setup" && player ? toWorld(ev) : null;
    if (Wt.down) dab(ev);
  });
  for (const t of ["pointerup", "pointercancel", "pointerleave"]) document.getElementById("stage").addEventListener(t, () => { if (Wt.down) { Wt.down = false; render() } });
  function undo() {   // Ctrl+Z: lùi một nét cọ
    if (!Wt.sess || !Wt.undo.length) return false;
    Wt.sess.table = Wt.undo.pop(); rebuild();
    if (!Wt.undo.length) { Wt.sess.dirty = false; ed.dirty.delete("__weights") }
    render(); setStatus("weight: lùi một nét cọ (còn " + Wt.undo.length + ")", "ok"); return true;
  }
  q("#wSave").onclick = async () => {
    if (!Wt.sess?.dirty) return setStatus("chưa sơn gì để lưu", "");
    const bs = player.skeleton.bones;
    const weights = Wt.sess.table.map(m => Object.fromEntries([...m].map(([k, w]) => [bs[k].data.name, +w.toFixed(4)])));
    try { const j = await edPost("/api/spine/weights", { json: cur.json, slot: Wt.sess.slot, attachment: Wt.sess.at.name, weights });
      endSess(); stamp = null; build(snapshot()); setStatus("đã lưu weight " + j.vertices + " đỉnh · " + hhmmss() + " (Ctrl+Z để hoàn tác)", "ok") }
    catch (e) { setStatus("lưu weight lỗi: " + e.message, "bad") }
  };
  q("#wDrop").onclick = () => { if (!Wt.sess) return; endSess(); stamp = null; build(snapshot()); setStatus("đã bỏ weight chưa lưu", "ok") };
  // vòng cọ trên khung xem
  const CUR = new spine.Color(1, 0.82, 0.1, 0.9);
  function drawCursor(p, sr, px) {
    if (!Wt.paint || !Wt.cursor || mode !== "setup") return;
    const R = Wt.size * px, c = Wt.cursor, N = 40;
    for (let i = 0; i < N; i++) { const a = i / N * Math.PI * 2, b = (i + 1) / N * Math.PI * 2; sr.rectLine(true, c.x + Math.cos(a) * R, c.y + Math.sin(a) * R, c.x + Math.cos(b) * R, c.y + Math.sin(b) * R, 1.5 * px, CUR) }
  }
  setInterval(() => { if (mode === "setup" && !sec.hidden) render() }, 400);
  window.spineWeights = { paintDown, undo, drawCursor, onSelect, endSess, W: Wt, isDirty: () => !!Wt.sess?.dirty };
})();
