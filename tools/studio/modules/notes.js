// AI Anim Studio — vẽ ghi chú lên viewport (mọi chế độ: General, Rig, Anim). Bấm ✎, vẽ khoanh bằng chuột / bút, gõ một dòng, Lưu:
// lưu ảnh khung nhìn + nét vẽ, nét vẽ (toạ độ 0..1), camera, chế độ đang sửa, bước Rig / anim + frame, khớp đang chọn.
// Kho: <nhân vật>_studio (cạnh <nhân vật>_mesh_lab / _rig_lab), nhóm `notes` (nhẹ, liệt kê được) + `noteimg` (ảnh JPEG).
// Claude đọc bằng `tools/studio_cmd.py notes` (đọc thẳng file trong work/store, ghi ảnh ra thư mục), đánh dấu xong bằng `note-done`.
(function () {
  const V = ST.view, esc = ST.esc, ic = ST.ic, $ = ST.$;
  const N = ST.mods.notes = { id: "notes" };
  const COLORS = ["#ff4d4d", "#ffd23f", "#3ddc97", "#4db3ff"];
  let on = false, color = COLORS[0], strokes = [], cur = null, list = null, viewing = null;
  const q = new URLSearchParams(location.search);
  const ns = () => q.get("ns") ? q.get("ns") + "_notes" : (ST.char ? ST.slug(ST.char.name) : ST.clip ? ST.slug(ST.clip) : "scene") + "_studio";
  const api = (col, id) => "/api/store/" + encodeURIComponent(ns()) + "/" + col + (id ? "/" + encodeURIComponent(id) : "");

  // ---- lớp vẽ + thanh công cụ trong viewport
  const vp = $("vp"), cv = document.createElement("canvas"); cv.id = "noteCv"; vp.appendChild(cv);
  const bar = document.createElement("div"); bar.id = "noteBar"; bar.setAttribute("role", "toolbar"); bar.setAttribute("aria-label", "Vẽ ghi chú"); vp.appendChild(bar);
  function drawBar() {
    bar.classList.toggle("on", on || !!viewing);
    if (viewing) {
      bar.innerHTML = `<span class="sub" title="${esc(viewing.text)}">${ic("eye")} ${esc(viewing.text || "(không chữ)")}</span><button data-a="close" title="Đóng nét vẽ của ghi chú">${ic("x")}</button>`;
      return;
    }
    bar.innerHTML = !on ? `<button data-a="start" title="Vẽ ghi chú lên viewport (khoanh chỗ cần sửa rồi lưu kèm một dòng chữ)">✎ Vẽ</button>` :
      COLORS.map(c => `<button class="sw ${c === color ? "on" : ""}" data-c="${c}" style="background:${c}" aria-label="Màu ${c}"></button>`).join("") +
      `<button data-a="undo" title="Bỏ nét cuối">${ic("undo")}</button><button data-a="clear" title="Xoá hết nét">${ic("trash")}</button>` +
      `<input id="noteText" type="text" placeholder="Ghi chú: sai gì, sửa thế nào" aria-label="Ghi chú">` +
      `<button class="on" data-a="save" title="Lưu ảnh khung nhìn + nét vẽ + ghi chú">Lưu</button><button data-a="cancel" title="Thôi vẽ">Huỷ</button>`;
    const t = $("noteText"); if (t) { t.onkeydown = e => { e.stopPropagation(); if (e.key === "Enter") save(); if (e.key === "Escape") stop(); }; setTimeout(() => t.focus(), 0); }
  }
  bar.addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    if (b.dataset.c) { color = b.dataset.c; drawBar(); return; }
    ({ start, cancel: stop, undo: () => { strokes.pop(); paint(); }, clear: () => { strokes = []; paint(); }, save, close: () => { viewing = null; paint(); drawBar(); } })[b.dataset.a]();
  });
  function size() { const r = vp.getBoundingClientRect(), d = devicePixelRatio || 1; cv.width = Math.max(1, r.width * d); cv.height = Math.max(1, r.height * d); cv.style.width = r.width + "px"; cv.style.height = r.height + "px"; paint(); }
  new ResizeObserver(size).observe(vp);
  function paint(target, W, H) {   // vẽ các nét (0..1) lên canvas 2D
    const c = target || cv.getContext("2d"), w = W || cv.width, h = H || cv.height, list = viewing ? viewing.strokes : strokes.concat(cur ? [cur] : []);
    if (!target) c.clearRect(0, 0, w, h);
    const k = Math.max(w, h) / 900;
    for (const s of list || []) {
      if (!s.pts.length) continue;
      c.strokeStyle = s.c; c.lineWidth = Math.max(2, 4 * k); c.lineCap = c.lineJoin = "round"; c.beginPath();
      s.pts.forEach(([x, y], i) => i ? c.lineTo(x * w, y * h) : c.moveTo(x * w, y * h));
      if (s.pts.length === 1) c.lineTo(s.pts[0][0] * w + 0.5, s.pts[0][1] * h);
      c.stroke();
    }
  }
  const rel = e => { const r = vp.getBoundingClientRect(); return [(e.clientX - r.left) / r.width, (e.clientY - r.top) / r.height]; };
  cv.addEventListener("pointerdown", e => { if (!on || e.button !== 0) return; e.preventDefault(); try { cv.setPointerCapture(e.pointerId); } catch (x) {} cur = { c: color, pts: [rel(e)] }; paint(); });
  cv.addEventListener("pointermove", e => { if (!cur) return; cur.pts.push(rel(e)); paint(); });
  const end = () => { if (!cur) return; if (cur.pts.length) strokes.push({ c: cur.c, pts: cur.pts.map(p => p.map(v => +v.toFixed(4))) }); cur = null; paint(); };
  cv.addEventListener("pointerup", end); cv.addEventListener("pointercancel", end);

  function start() { if (!ST.char && !ST.clip) return ST.toast("Mở nhân vật hoặc anim trước."); viewing = null; on = true; strokes = []; document.body.classList.add("noting"); paint(); drawBar(); }
  function stop() { on = false; strokes = []; cur = null; document.body.classList.remove("noting"); paint(); drawBar(); }

  // ---- bối cảnh lúc lưu: đủ để Claude (và người khác) mở lại đúng chỗ
  function context() {
    const p = V.active, cam = p.cam, ctx = { ws: ST.ws, focus: ST.focus, layers: Object.assign({}, ST.layerOn), tab: ST.curTab ? ST.curTab() : null,
      char: ST.char ? ST.char.id : null, joint: null,
      view: { layout: V.layout, pane: p.id, pos: cam.position.toArray().map(v => +v.toFixed(4)), quat: cam.quaternion.toArray().map(v => +v.toFixed(5)),
        target: p.target.toArray().map(v => +v.toFixed(4)), zoom: +(cam.zoom || 1).toFixed(4), fov: cam.fov || null, aspect: +(p.rect.w / Math.max(1, p.rect.h)).toFixed(4) } };
    try { const m = ST.mod(); ctx.joint = m.curJoint ? m.curJoint() : null; } catch (e) {}
    try { if (ST.focus === "rig" && ST.rigEng && ST.rigEng()) { const g = ST.rigEng().get(); ctx.rig = { step: g.step, sel: [...g.S] }; } } catch (e) {}
    try { if (ST.layerOn.anim && ST.poseEng && ST.poseEng() && ST.poseEng().ai) { const a = ST.poseEng().ai.info(); ctx.anim = { clip: a.clip, version: a.version, frame: a.frame, sel: a.sel }; } } catch (e) {}
    return ctx;
  }
  function snapshot() {   // ảnh khung nhìn (như đang thấy) + nét vẽ, JPEG
    const src = $("cv"); if (src.width < 2 || src.height < 2) return null;
    V.renderNow();
    const out = document.createElement("canvas"), sc = Math.min(1, 1600 / Math.max(src.width, src.height));
    out.width = Math.round(src.width * sc); out.height = Math.round(src.height * sc);
    const c = out.getContext("2d"); c.drawImage(src, 0, 0, out.width, out.height); paint(c, out.width, out.height);
    return out.toDataURL("image/jpeg", 0.85);
  }
  async function save() {
    const text = ($("noteText") || {}).value ? $("noteText").value.trim() : "";
    if (!strokes.length && !text) return ST.toast("Vẽ khoanh chỗ cần sửa hoặc gõ ghi chú trước khi lưu.");
    const id = new Date().toISOString().replace(/[-:T.Z]/g, "").slice(0, 14) + Math.random().toString(36).slice(2, 5);
    const doc = { id, at: new Date().toISOString(), text, status: "open", strokes, ctx: context() }, img = snapshot();
    try {
      const put = (col, data) => fetch(api(col, id), { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) }).then(r => { if (!r.ok) throw new Error(r.status); });
      if (img) await put("noteimg", { img }); await put("notes", Object.assign(doc, { img: !!img }));
      ST.toast("Đã lưu ghi chú. Nhắn Claude để sửa (Claude đọc được ảnh + nét vẽ)."); list = null; stop(); ST.showTab && ST.showTab(ST.tabs && ST.tabs().includes("pose:feedback") ? "pose:feedback" : "notes:list"); ST.refresh();
    } catch (e) { ST.toast("Không lưu được ghi chú (Home server?): " + (e.message || e)); }
  }

  // ---- danh sách (panel dock "Ghi chú vẽ")
  async function load() {
    try { const r = await fetch(api("notes")); const j = await r.json(); list = (j.docs || []).map(d => d.data).filter(Boolean).sort((a, b) => b.at.localeCompare(a.at)); }
    catch (e) { list = []; }
    ST.refresh();
  }
  const where = c => !c ? "" : [({ mesh: "General", rig: "Rig", pose: "Anim" }[c.focus] || c.focus), c.rig ? "bước " + c.rig.step : "", c.anim ? c.anim.version + " F" + c.anim.frame : "", c.joint || ""].filter(Boolean).join(" · ");
  let editing = null;   // id ghi chú đang sửa chữ
  // Góp ý theo phiên bản (user 2026-10-29 "các phiên bản đang dùng chung dữ liệu fb"): ở Pose chỉ hiện, đếm và gửi ghi chú vẽ
  // của đúng anim + phiên bản đang mở (ctx.anim); nút "Cả phiên bản khác" để xem hết. Ngoài Pose: như cũ, hiện tất cả.
  let showAll = false;
  const curAnim = () => { try { if (ST.curTab && ST.curTab() === "pose:feedback" && ST.poseEng && ST.poseEng() && ST.poseEng().ai) { const a = ST.poseEng().ai.info(); return a && a.version ? a : null; } } catch (e) {} return null; };
  const sameVer = (n, a) => !!(n.ctx && n.ctx.anim && n.ctx.anim.version === a.version && (!n.ctx.anim.clip || !a.clip || n.ctx.anim.clip === a.clip));
  const vis = () => { const a = curAnim(); return !list ? [] : !a || showAll ? list : list.filter(n => sameVer(n, a)); };
  N.panel = () => {
    if (list === null) { load(); return '<div class="sub" style="padding:10px">Đang tải ghi chú…</div>'; }
    const a = curAnim(), L = vis(), hid = list.length - (a ? list.filter(n => sameVer(n, a)).length : list.length);
    const open = L.filter(n => n.status !== "done"), unsent = open.filter(n => !n.sent);
    const head = `<div class="row nhead" style="padding:8px 10px;flex-wrap:wrap"><button data-n="new" title="Khoanh chỗ cần sửa trên viewport, gõ một dòng rồi Lưu">✎ Vẽ ghi chú mới</button>` +
      `<span class="wdot" title="${watching ? "Claude đang canh: bấm Gửi là AI nhận ngay" : "Claude không canh: gửi xong nhắn Claude bất kỳ câu nào (hoặc /check_fb)"}">${watching ? "●" : "○"}</span>` +   // trạng thái bộ canh gọn một chấm (user 2026-10-29 "chiếm nhiều diện tích")
      `<span class="sub">${open.length} đang mở${open.length - unsent.length ? " · " + (open.length - unsent.length) + " đã gửi, chờ AI" : ""}${a ? " · bản " + esc(a.version) : ""}</span>` +
      (a && hid ? `<button data-n="allv" title="${showAll ? "Chỉ hiện ghi chú của phiên bản đang mở" : "Hiện cả ghi chú của các phiên bản khác"}">${showAll ? "Chỉ bản " + esc(a.version) : "Cả phiên bản khác (" + hid + ")"}</button>` : "") + `</div>`;
    // chân panel (dockfoot, user 2026-10-29): nút Gửi cho AI + trạng thái bộ canh luôn ở cạnh dưới; trong tab Góp ý của Pose nút này ẩn (đã có Gửi tất cả)
    const foot = `<div class="nfoot dockfoot" style="padding:8px 10px"><div class="row" style="flex-wrap:wrap"><button class="on" data-n="send" ${unsent.length ? "" : "disabled"} title="Đánh dấu các ghi chú đang mở là đã gửi; rồi nhắn Claude /check_fb (lệnh được chép sẵn)">Gửi cho AI${unsent.length ? " (" + unsent.length + ")" : ""}</button></div>` +
      `<p class="note" style="margin:4px 0 0" title="Bộ canh chạy trong phiên chat Claude của dự án này; Claude tự bật khi có trang Studio mở">${watching ? "● Claude đang canh: bấm Gửi là AI nhận ngay" : "○ Claude không canh: gửi xong nhắn Claude bất kỳ câu nào (hoặc /check_fb)"}</p>` +
      (sentMsg && unsent.length === 0 && open.some(n => n.sent && !n.picked) ? `<p class="note" style="margin:4px 0 0">${sentMsg}</p>` : "") + `</div>`;
    if (!L.length) return `<div class="nwrap">${head}<p class="note" style="padding:0 10px">${a ? "Phiên bản " + esc(a.version) + " chưa có ghi chú vẽ." : "Chưa có ghi chú."} Bấm ✎ ở góc viewport, khoanh chỗ cần sửa, gõ một dòng rồi Lưu.</p>${foot}</div>`;
    return `<div class="nwrap">` + head + `<div class="notes">${L.map(n => `<div class="nt ${n.status === "done" ? "done" : ""}" data-id="${esc(n.id)}" style="cursor:pointer" title="Bấm để mở lại góc nhìn, frame + nét vẽ">
      ${n.img ? `<img alt="Ảnh ghi chú" data-n="view" hidden>` : ""}
      <div class="nb">${n.id === editing ? `<textarea class="nedit" rows="3" style="width:100%" onkeydown="event.stopPropagation()">${esc(n.text || "")}</textarea><div class="row"><button class="on" data-n="esave">Lưu</button><button data-n="ecancel">Huỷ</button></div>` : `<b>${esc(n.text || "(không chữ)")}</b>`}<small>${esc(String(n.at).slice(0, 16).replace("T", " "))} · ${esc(where(n.ctx))}${n.status === "done" ? " · AI đã sửa" : n.picked ? " · AI đã nhận, đang sửa" : n.sent ? " · đã gửi AI" : ""}</small>
      <button data-n="menu" class="nkebab" title="Sửa / Đã sửa / Xoá" aria-label="Thao tác ghi chú">⋯</button><div class="row nmenu" style="display:none"><button data-n="edit" title="Sửa chữ của ghi chú">Sửa</button><button data-n="done" title="${n.status === "done" ? "Mở lại" : "Đánh dấu đã sửa"}">${n.status === "done" ? "Mở lại" : "Đã sửa"}</button><button data-n="del" class="bad" title="Xoá ghi chú">${ic("trash")}</button></div></div></div>`).join("")}</div>${foot}</div>`;
  };
  N.panelKey = () => (curAnim() || {}).version + (showAll ? "A" : "") + (list ? list.map(n => n.id + n.status + (n.sent ? "s" : "") + (n.picked ? "p" : "") + (n.text || "").length).join(",") : "-") + "e" + editing + sentMsg.length + (watching ? "w" : "");
  N.panelStatic = true;
  N.panelMounted = () => {   // ảnh nhỏ: đọc doc noteimg
    if (!list) return;
    $("attrBody").querySelectorAll(".nt img[hidden]").forEach(async im => {
      const id = im.closest(".nt").dataset.id;
      try { const j = await (await fetch(api("noteimg", id))).json(); if (j.data && j.data.img) { im.src = j.data.img; im.hidden = false; } } catch (e) {}
    });
  };
  N.panel_click = async e => {
    const b = e.target.closest("[data-n]");
    // bấm vào thân ghi chú (không phải nút / ô sửa) = mở lại góc nhìn + frame + nét vẽ (thay nút Xem, user 2026-10-29)
    if (!b) { const nt = e.target.closest(".nt"); if (!nt || e.target.closest("textarea")) return; const n = list && list.find(x => x.id === nt.dataset.id); if (n && n.id !== editing) view(n); return; }
    if (b.dataset.n === "new") return start();
    if (b.dataset.n === "allv") { showAll = !showAll; ST.refresh(); return; }
    if (b.dataset.n === "send") return send();
    if (b.dataset.n === "menu") {   // menu ⋯ ở góc ghi chú (user 2026-10-29 "icon 3 chấm ở góc này")
      const m = b.parentElement.querySelector(".nmenu"), open = m.style.display === "none";
      document.querySelectorAll(".nmenu").forEach(x => x.style.display = "none"); if (!open) return;
      const r = b.getBoundingClientRect(); m.style.display = "flex";   // menu nổi (fixed), không bị khung cuộn cắt
      m.style.top = Math.min(r.bottom + 4, innerHeight - m.offsetHeight - 8) + "px"; m.style.left = Math.max(8, r.right - m.offsetWidth) + "px";
      const out = ev => { if (!m.contains(ev.target) && ev.target !== b) { m.style.display = "none"; document.removeEventListener("pointerdown", out, true); } };
      document.addEventListener("pointerdown", out, true); return; }
    const id = b.closest(".nt").dataset.id, n = list.find(x => x.id === id); if (!n) return;
    if (b.dataset.n === "view") return view(n);
    // sửa chữ tại chỗ (user 2026-10-29 "các fb cần có tính năng xóa, sửa")
    if (b.dataset.n === "edit") { editing = id; ST.refresh(); setTimeout(() => { const t = document.querySelector('.nt[data-id="' + id + '"] textarea.nedit'); if (t) t.focus(); }, 0); return; }
    if (b.dataset.n === "ecancel") { editing = null; ST.refresh(); return; }
    if (b.dataset.n === "esave") { const t = b.closest(".nt").querySelector("textarea.nedit"); n.text = t ? t.value.trim() : n.text; n.editedAt = new Date().toISOString(); editing = null;
      await fetch(api("notes", id), { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(n) }); ST.refresh(); return; }
    if (b.dataset.n === "done") { n.status = n.status === "done" ? "open" : "done"; await fetch(api("notes", id), { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(n) }); ST.refresh(); return; }
    if (b.dataset.n === "del") { await fetch(api("notes", id), { method: "DELETE" }); await fetch(api("noteimg", id), { method: "DELETE" }); list = list.filter(x => x !== n); ST.refresh(); }
  };
  function view(n) {   // về đúng chế độ, góc nhìn, bước / frame rồi hiện nét vẽ (đóng bằng ✕ trên thanh)
    const c = n.ctx || {};
    try {
      if (c.focus && c.focus !== ST.focus) ST.setFocus(c.focus);
      if (c.rig && c.rig.step && ST.cmds.get("rig.step" + c.rig.step)) ST.run("rig.step" + c.rig.step);
      if (c.anim && ST.poseEng && ST.poseEng() && ST.poseEng().ai) ST.poseEng().ai.frame(c.anim.frame);
      const v = c.view; if (v) {
        V.setLayout("1", v.pane); const p = V.panes[v.pane];
        p.cam.position.fromArray(v.pos); p.cam.quaternion.fromArray(v.quat); if (v.zoom) p.cam.zoom = v.zoom; if (v.fov && p.cam.isPerspectiveCamera) p.cam.fov = v.fov;
        p.target.fromArray(v.target); p.cam.updateProjectionMatrix(); V.orbit.update();
      }
    } catch (e) { console.error(e); }
    stop(); viewing = n; paint(); drawBar();
  }
  let sentMsg = "";
  async function send() {
    const L = vis().filter(n => n.status !== "done" && !n.sent), at = new Date().toISOString();   // Pose: chỉ ghi chú của phiên bản đang mở
    for (const n of L) { n.sent = at; await fetch(api("notes", n.id), { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(n) }); }
    let copied = false; try { await navigator.clipboard.writeText("/check_fb"); copied = true; } catch (e) {}
    sentMsg = "Đã gửi " + L.length + " ghi chú. Nếu Claude đang mở phiên chat có bộ canh ghi chú, Claude tự nhận trong vài giây (dòng ghi chú chuyển \"AI đã nhận\"); không thì nhắn Claude <b>/check_fb</b>" + (copied ? " (đã chép sẵn)" : "") + ".";
    ST.toast("Đã gửi " + L.length + " ghi chú cho AI."); ST.refresh();
  }
  N.reload = () => { list = null; ST.refresh(); };
  N.sendAll = send;   // tab "Góp ý cho AI" của Pose: một nút gửi cả ghi chú vẽ lẫn điều chỉnh key
  N.unsentCount = () => vis().filter(n => n.status !== "done" && !n.sent).length;
  const myTab = () => ST.curTab && ["notes:list", "pose:feedback"].includes(ST.curTab());
  let lastVer;   // đổi phiên bản Pose thì vẽ lại danh sách ghi chú theo bản mới
  setInterval(() => { if (!myTab()) return; const v = (curAnim() || {}).version; if (v !== lastVer) { lastVer = v; ST.refresh(); } }, 400);
  // ghi chú đã gửi, chưa xong: đọc lại mỗi 4 s khi panel đang mở, để thấy "AI đã nhận" / "AI đã sửa" ngay
  setInterval(() => { if (myTab() && list && list.some(n => n.sent && n.status !== "done") && document.visibilityState === "visible") load(); }, 4000);
  // nhịp tim bộ canh (tools/notes_watch.py ghi work/store/_sys/watch/notes.json mỗi 2 s)
  let watching = false;
  async function watchBeat() {
    if (document.visibilityState !== "visible") return;
    let w = false;
    try { const j = await (await fetch("/api/store/_sys/watch/notes")).json(); w = !!(j.data && Date.now() / 1000 - j.data.beat < 10); } catch (e) {}
    if (w !== watching) { watching = w; if (myTab()) ST.refresh(); }
  }
  watchBeat(); setInterval(watchBeat, 4000);
  N.watching = () => watching;
  N.list = () => list;

  ST.cmd({ id: "notes.draw", menu: "Window", sep: true, label: "Vẽ ghi chú lên viewport", icon: "pen", keep: true, global: true, check: () => on, run: () => on ? stop() : start() });
  ST.on("char", () => { list = null; }); ST.on("init", () => { drawBar(); size(); });
  addEventListener("keydown", e => { if (on && e.key === "Escape" && !/INPUT|TEXTAREA/.test((e.target || {}).tagName || "")) stop(); });
})();
