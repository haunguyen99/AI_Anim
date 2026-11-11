// Dock bên phải + menu Công cụ + danh sách anim ở timeline + Properties của layer ảnh (2026-10-31).
// Người dùng: "nút công cụ khi click sẽ sổ ra dãy bảng để click, click vào cái nào mới hiện ra cái đó ... Properties hiện vị trí
// xương thì cho ra ngoài cạnh phải luôn (có thể đóng thu nhỏ vào cạnh) ... Đổi Xương thành Properties (gồm cả vị trí ảnh layer,
// ảnh sau khi parent vẫn di chuyển được) ... thêm Weight tương tự Spine vào Công cụ ... và công cụ mesh khi click vào layer ảnh".
// "dấu X để xoá anim nằm trong danh sách anim, không cạnh nút play dễ bấm nhầm ... xoá cần hỏi lại double check".
// Dùng biến chung của index.html: player, cur, ed, mode, setMode, store, edPost, build, snapshot, stamp, setStatus, hhmmss,
// toWorld, pxWorld, curAnim, fpsOf, armDelete, $.
(() => {
  // ---------------- menu Công cụ: chọn một công cụ thì hiện nó dưới Properties ----------------
  const TOOLS = [
    { id: "anim", sec: "animBox", ic: "🎞", label: "Anim (tạo / xoá / mô tả)", mode: "anim" },
    { id: "note", sec: "noteBox", ic: "✎", label: "Ghi chú cho Claude (vẽ + Gen)", mode: "any" },
    { id: "param", sec: "parBox", ic: "🎚", label: "Tham số anim", mode: "anim" },
    { id: "phys", sec: "physBox", ic: "〰", label: "Physics (overlap)", mode: "anim" },
    { id: "mb", sec: "mbBox", ic: "▦", label: "Mesh / Bind (lưới, bind xương, weight)", mode: "any" },   // cả Animate: sửa weight ngay lúc anim
  ];
  const T = { active: store.get("tool", "") };
  function toolOk(t) { return !!$(t.sec) }
  function showTool(id, init) {
    const t = TOOLS.find(x => x.id === id);
    if (t && !init && t.mode !== "any" && t.mode !== mode) {
      setMode(t.mode);                       // đang sửa dở: nút tab hỏi lại, bấm lần nữa = bỏ sửa rồi đổi
      if (mode !== t.mode) return;
    }
    T.active = t ? id : ""; store.set("tool", T.active);
    for (const x of TOOLS) { const s = $(x.sec); if (s) { s.classList.toggle("active", x.id === T.active); s.classList.remove("closed") } }
    if ($("edPanel").classList.contains("docked")) dock(false);
    renderTools();
    if (t) $(t.sec)?.scrollIntoView({ block: "nearest" });
  }
  function renderTools() {
    $("toolList").innerHTML = TOOLS.filter(toolOk).map(t => `<div class="mi${t.id === T.active ? " on" : ""}" data-t="${t.id}">
      <span class="ic">${t.ic}</span><span class="nm">${t.label}</span><span class="tg">${t.mode === "setup" ? "Setup" : t.mode === "anim" ? "Animate" : ""}</span></div>`).join("")
      + `<div class="mi${!T.active ? " on" : ""}" data-t=""><span class="ic">✕</span><span class="nm">Đóng công cụ (chỉ Properties)</span></div>`;
    $("toolBtn").textContent = (TOOLS.find(t => t.id === T.active)?.label.split(" (")[0] || "Công cụ") + " ▾";
  }
  $("toolBtn").onclick = ev => { ev.stopPropagation(); renderTools(); $("toolList").hidden = !$("toolList").hidden };
  $("toolList").onclick = ev => { const m = ev.target.closest(".mi"); if (!m) return; $("toolList").hidden = true; showTool(m.dataset.t) };
  // nút ✕ trên tiêu đề mỗi công cụ
  function addClose() {
    for (const t of TOOLS) {
      const h = $(t.sec)?.querySelector(":scope > .secT"); if (!h || h.querySelector(".close")) continue;
      const b = document.createElement("button"); b.className = "close"; b.textContent = "✕"; b.title = "Đóng công cụ này";
      b.onclick = ev => { ev.stopPropagation(); showTool("") }; h.appendChild(b);
    }
  }

  // ---------------- dock: Properties luôn ở cạnh phải, thu vào cạnh được ----------------
  function dock(on) { $("edPanel").classList.toggle("docked", on); $("dockTab").hidden = !on; store.set("docked", on ? "1" : "0") }
  $("dockBtn").onclick = ev => { ev.stopPropagation(); dock(true) };
  $("dockTab").onclick = () => dock(false);

  // ---------------- danh sách anim ở timeline: đổi anim, ✕ xoá (hỏi lại 2 bước) ----------------
  function renderAnims() {
    if (!player) return;
    const sd = player.skeleton.data, a = curAnim(), F = fpsOf();
    $("amList").innerHTML = sd.animations.map(x => `<div class="mi${x.name === a ? " on" : ""}" data-a="${x.name}">
      <span class="nm">${x.name}</span><span class="tg">${Math.round(x.duration * F)}F</span>
      <button class="x" data-del="${x.name}" title="Xoá anim ${x.name} (bấm 2 lần để chắc chắn; Hoàn tác được)">✕</button></div>`).join("");
  }
  $("amBtn").onclick = ev => { ev.stopPropagation(); renderAnims(); $("amList").hidden = !$("amList").hidden };
  $("amList").onclick = ev => {
    ev.stopPropagation();
    const x = ev.target.closest("[data-del]");
    if (x) { armDelete(x, () => { $("amList").hidden = true; window.spineAnims.delAnim(x.dataset.del) }, "Xoá?"); return }
    const m = ev.target.closest(".mi"); if (!m) return;
    $("amList").hidden = true;
    $("animSel").value = m.dataset.a; $("animSel").onchange();
  };
  document.addEventListener("click", ev => {
    if (!ev.target.closest("#toolMenu")) $("toolList").hidden = true;
    if (!ev.target.closest("#animMenu")) $("amList").hidden = true;
  });

  // ---------------- Properties của layer ảnh (khi chọn ảnh, không chọn xương) ----------------
  const lp = document.createElement("div"); lp.id = "layerProps"; lp.hidden = true;
  lp.innerHTML = `<div class="row"><span class="lpT" id="lpName"></span><span id="lpInfo" class="mute"></span></div>
    <div class="fields">
      <label title="Vị trí ảnh trong hệ của xương cha">X<input id="lpX" type="number" step="1"></label>
      <label>Y<input id="lpY" type="number" step="1"></label>
      <label title="Góc ảnh (độ, chỉ ảnh thường)">Xoay<input id="lpR" type="number" step="0.5"></label>
      <label title="Scale X ảnh (chỉ ảnh thường)">Sc X<input id="lpSX" type="number" step="0.05"></label>
      <label title="Scale Y ảnh (chỉ ảnh thường)">Sc Y<input id="lpSY" type="number" step="0.05"></label>
    </div>
    <div id="lpHint" class="mute"></div>`;
  $("boneProps").after(lp);
  const L = { drag: null, saving: false };
  const slotObj = () => ed.slot && player?.skeleton?.findSlot(ed.slot);
  const isMesh = at => at instanceof spine.MeshAttachment, isRegion = at => at instanceof spine.RegionAttachment;
  function center(slot, at) {   // tâm ảnh (thế giới)
    if (isRegion(at)) { const v = new Float32Array(8); at.computeWorldVertices(slot, v, 0, 2); return [(v[0] + v[4]) / 2, (v[1] + v[5]) / 2] }
    const n = at.worldVerticesLength, v = new Float32Array(n); at.computeWorldVertices(slot, 0, n, v, 0, 2);
    let x = 0, y = 0; for (let i = 0; i < n; i += 2) { x += v[i]; y += v[i + 1] } return [x / (n / 2), y / (n / 2)];
  }
  function meshCenterLocal(at) {   // mesh không weight: tâm trong hệ xương
    let x = 0, y = 0; const v = at.vertices, n = v.length / 2; for (let i = 0; i < v.length; i += 2) { x += v[i]; y += v[i + 1] } return [x / n, y / n];
  }
  function renderLayer() {
    const show = !ed.sel && !!ed.slot;
    $("boneProps").hidden = show; lp.hidden = !show;
    if (!show) return;
    const s = slotObj(), at = s?.getAttachment();
    $("lpName").textContent = "Layer: " + (ed.slot || "");
    if (!at) { $("lpInfo").textContent = " · không có ảnh"; return }
    const weighted = isMesh(at) && !!at.bones;
    $("lpInfo").textContent = ` · ${isMesh(at) ? (weighted ? "mesh có weight" : "mesh") : "ảnh thường"} · cha: ${s.bone.data.name}`;
    const editable = mode === "setup";
    let x = 0, y = 0, r = 0, sx = 1, sy = 1;
    if (isRegion(at)) { x = at.x; y = at.y; r = at.rotation; sx = at.scaleX; sy = at.scaleY }
    else if (!weighted) [x, y] = meshCenterLocal(at);
    else { const c = center(s, at), l = s.bone.worldToLocal(new spine.Vector2(c[0], c[1])); x = l.x; y = l.y }
    for (const [id, v, ok] of [["lpX", x, true], ["lpY", y, true], ["lpR", r, isRegion(at)], ["lpSX", sx, isRegion(at)], ["lpSY", sy, isRegion(at)]]) {
      const el = $(id); el.disabled = !editable || !ok;
      if (document.activeElement !== el) el.value = (+v).toFixed(id === "lpSX" || id === "lpSY" ? 3 : 1);
    }
    $("lpHint").textContent = editable ? "Kéo ảnh trên hình (Q chỉ chọn): V dời" + (isRegion(at) ? " · C xoay · X scale" : "") + " (lưu vào file khi thả chuột, Ctrl+Z / Hoàn tác lùi)"
                                       : "Vị trí ảnh là dữ liệu setup: sang tab Setup để dời ảnh (giữ nguyên xương cha).";
  }
  setInterval(() => { try { renderLayer() } catch {} }, 200);

  // áp thay đổi lên attachment đang chạy (để xem ngay), rồi ghi file
  function applyRegion(at, f) { Object.assign(at, f); at.updateRegion() }
  function meshShift(slot, at, dx, dy, base) {   // dời cả lưới một đoạn (dx, dy) thế giới; base: đỉnh gốc lúc bắt đầu kéo
    const v = at.vertices;
    if (!at.bones) { const b = slot.bone, l0 = b.worldToLocal(new spine.Vector2(0, 0)), l1 = b.worldToLocal(new spine.Vector2(dx, dy)); const lx = l1.x - l0.x, ly = l1.y - l0.y;
      for (let i = 0; i < v.length; i += 2) { v[i] = base[i] + lx; v[i + 1] = base[i + 1] + ly } return }
    const bones = player.skeleton.bones;
    for (let i = 0, w = 0; i < at.bones.length;) {
      const n = at.bones[i++];
      for (let k = 0; k < n; k++, w += 3) { const b = bones[at.bones[i++]], l0 = b.worldToLocal(new spine.Vector2(0, 0)), l1 = b.worldToLocal(new spine.Vector2(dx, dy));
        v[w] = base[w] + (l1.x - l0.x); v[w + 1] = base[w + 1] + (l1.y - l0.y) }
    }
  }
  function meshJson(at) {   // đỉnh mesh dạng JSON Spine
    const v = Array.from(at.vertices, x => Math.round(x * 100) / 100);
    if (!at.bones) return v;
    const out = [];
    for (let i = 0, w = 0; i < at.bones.length;) { const n = at.bones[i++]; out.push(n); for (let k = 0; k < n; k++, w += 3) out.push(at.bones[i++], v[w], v[w + 1], Math.round(at.vertices[w + 2] * 1e4) / 1e4) }
    return out;
  }
  async function save(slot, at, what) {
    if (L.saving) return; L.saving = true;
    const body = { json: cur.json, slot: slot.data.name, attachment: at.name, skin: player.skeleton.skin?.name || "default", what };
    if (isRegion(at)) body.fields = { x: at.x, y: at.y, rotation: at.rotation, scaleX: at.scaleX, scaleY: at.scaleY };
    else body.vertices = meshJson(at);
    try { await edPost("/api/spine/attachment", body); stamp = null; await build(snapshot()); setStatus(`đã ${what} ảnh ${slot.data.name} · ${hhmmss()} (Ctrl+Z / Hoàn tác lùi)`, "ok") }
    catch (e) { setStatus("lưu vị trí ảnh lỗi: " + e.message, "bad") }
    L.saving = false;
  }
  for (const [id, k] of [["lpX", "x"], ["lpY", "y"], ["lpR", "rotation"], ["lpSX", "scaleX"], ["lpSY", "scaleY"]]) $(id).onchange = () => {
    const s = slotObj(), at = s?.getAttachment(), v = parseFloat($(id).value); if (!at || !isFinite(v) || mode !== "setup") return;
    if (isRegion(at)) { applyRegion(at, { [k]: v }); return save(s, at, "sửa") }
    // mesh: dời cả lưới tới vị trí nhập (X / Y = tâm lưới trong hệ xương cha)
    const c = center(s, at), l = s.bone.worldToLocal(new spine.Vector2(c[0], c[1])), want = { x: k === "x" ? v : l.x, y: k === "y" ? v : l.y };
    const w = s.bone.localToWorld(new spine.Vector2(want.x, want.y)), base = Float32Array.from(at.vertices);
    meshShift(s, at, w.x - c[0], w.y - c[1], base); save(s, at, "dời");
  };
  // kéo ảnh trên hình (tab Setup, đang chọn ảnh, không chọn xương)
  addEventListener("pointerdown", ev => {
    if (!player || mode !== "setup" || ed.sel || !ed.slot || ev.button !== 0 || ev.altKey || L.saving) return;
    if (window.spineSketch?.S.on || window.spineWeights?.W.paint || window.spineMesh?.open || window.spineMB?.grabs()) return;   // Mesh / Bind đang mở: chuột dành cho điểm lưới / xương
    if (!$("stage").contains(ev.target) || ev.target.closest("#edPanel,#verPanel,#helpPop,#claude,button,select,input,textarea")) return;
    const hit = window.spineSel?.pickSlot(ev); if (!hit || hit.data.name !== ed.slot) return;
    const at = hit.getAttachment(); if (!at || (!isRegion(at) && !isMesh(at))) return;
    if (ed.tool === "select") return;   // Q: chỉ chọn, không kéo ảnh
    const tool = isRegion(at) ? ed.tool : "translate";
    ev.stopImmediatePropagation(); ev.preventDefault();
    const v = toWorld(ev), c = center(hit, at);
    L.drag = { slot: hit, at, tool, v0: [v.x, v.y], c, moved: false,
               reg: isRegion(at) ? { x: at.x, y: at.y, rotation: at.rotation, scaleX: at.scaleX, scaleY: at.scaleY } : null,
               base: isMesh(at) ? Float32Array.from(at.vertices) : null };
    try { $("stage").setPointerCapture(ev.pointerId) } catch {}
  }, true);
  addEventListener("pointermove", ev => {
    const d = L.drag; if (!d) return;
    ev.stopImmediatePropagation();
    const v = toWorld(ev), dx = v.x - d.v0[0], dy = v.y - d.v0[1]; d.moved = true;
    if (d.reg) {
      const b = d.slot.bone;
      if (d.tool === "rotate") {
        const a0 = Math.atan2(d.v0[1] - d.c[1], d.v0[0] - d.c[0]), a1 = Math.atan2(v.y - d.c[1], v.x - d.c[0]);
        applyRegion(d.at, { rotation: d.reg.rotation + (a1 - a0) * 180 / Math.PI * (b.a * b.d - b.b * b.c < 0 ? -1 : 1) });
      } else if (d.tool === "scale") {
        const r0 = Math.hypot(d.v0[0] - d.c[0], d.v0[1] - d.c[1]) || 1, k = Math.hypot(v.x - d.c[0], v.y - d.c[1]) / r0;
        applyRegion(d.at, { scaleX: d.reg.scaleX * k, scaleY: d.reg.scaleY * k });
      } else {
        const l0 = b.worldToLocal(new spine.Vector2(d.v0[0], d.v0[1])), l1 = b.worldToLocal(new spine.Vector2(v.x, v.y));
        applyRegion(d.at, { x: d.reg.x + l1.x - l0.x, y: d.reg.y + l1.y - l0.y });
      }
    } else meshShift(d.slot, d.at, dx, dy, d.base);
  }, true);
  for (const t of ["pointerup", "pointercancel"]) addEventListener(t, ev => {
    const d = L.drag; if (!d) return;
    ev.stopImmediatePropagation(); L.drag = null;
    if (d.moved) save(d.slot, d.at, d.tool === "rotate" ? "xoay" : d.tool === "scale" ? "scale" : "dời");
  }, true);

  // ---------------- công cụ Lưới mesh: bấm vào layer ảnh là mở trình sửa lưới ----------------
  let lastSlot = null;
  function meshSync() {
    $("meshSel").textContent = ed.slot ? "đang chọn: " + ed.slot : "chưa chọn layer";
    $("meshGo").disabled = !ed.slot;
    lastSlot = ed.slot;
  }
  $("meshGo").onclick = () => { if (ed.slot && !window.spineMesh?.open) $("meshOpen")?.click() };
  setInterval(() => { try { meshSync() } catch {} }, 250);

  // ---------------- khởi động ----------------
  addClose(); setTimeout(addClose, 500);
  dock(store.get("docked", "0") === "1");
  showTool(T.active && TOOLS.some(t => t.id === T.active) ? T.active : "", true);
  setInterval(() => { const n = curAnim(); if ($("amName").textContent !== (n || "—")) $("amName").textContent = n || "—" }, 250);
  window.spineDock = { showTool, dock, TOOLS };
})();
