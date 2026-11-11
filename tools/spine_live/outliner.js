// Spine Live: chọn layer (slot / mesh) trên khung xem + khung sáng, và cửa sổ nổi Layer / Xương (như Tree của Spine).
// Bấm vào hình: chọn layer trên cùng có điểm ảnh không trong suốt dưới con trỏ (mesh, region, đã bind hay chưa).
// Khung sáng: viền hull (mesh) / khung ảnh (region) + nhãn tên layer, xương của slot và các xương đang bind.
// Dùng biến chung của index.html: player, cur, ed, store, pxWorld, toWorld, edRefresh, setStatus.
(() => {
  const S = { imgs: new Map(), hidden: new Set(), tab: store.get("outTab", "slots"), sig: "" };
  // ---- ảnh để thử độ trong suốt khi bấm ----
  function imagesDir() { return cur?.atlas?.endsWith("_auto.atlas") ? cur.atlas.slice(0, cur.atlas.lastIndexOf("/")) : null }
  function alphaAt(name, u, v) {   // độ đục tại uv của ảnh rời (null = chưa có ảnh: coi như trúng)
    const dir = imagesDir(); if (!dir) return null;
    let e = S.imgs.get(name);
    if (!e) {
      e = { ok: false }; S.imgs.set(name, e);
      const im = new Image(); im.onload = () => { const c = document.createElement("canvas"); c.width = im.naturalWidth; c.height = im.naturalHeight;
        const g = c.getContext("2d"); g.drawImage(im, 0, 0); e.data = g.getImageData(0, 0, c.width, c.height); e.ok = true };
      im.src = "/spine-live/f/" + dir + "/" + name + ".png";
    }
    if (!e.ok) return null;
    const x = Math.max(0, Math.min(e.data.width - 1, Math.round(u * e.data.width))), y = Math.max(0, Math.min(e.data.height - 1, Math.round(v * e.data.height)));
    return e.data.data[(y * e.data.width + x) * 4 + 3];
  }
  let buf = new Float32Array(64);
  function geom(slot) {   // [world xy, uvs, triangles] của attachment hiện tại của slot
    const at = slot.getAttachment(); if (!at) return null;
    if (at instanceof spine.RegionAttachment) {
      if (buf.length < 8) buf = new Float32Array(8);
      at.computeWorldVertices(slot, buf, 0, 2);
      return { at, w: Array.from(buf.slice(0, 8)), uv: Array.from(at.uvs), tri: [0, 1, 2, 2, 3, 0], hull: 4 };
    }
    if (at instanceof spine.MeshAttachment) {
      const n = at.worldVerticesLength; if (buf.length < n) buf = new Float32Array(n);
      at.computeWorldVertices(slot, 0, n, buf, 0, 2);
      return { at, w: Array.from(buf.slice(0, n)), uv: Array.from(at.uvs), tri: at.triangles, hull: (at.hullLength || n) / 2 };
    }
    return null;
  }
  function pickSlot(ev) {
    if (!player) return null;
    const v = toWorld(ev), sk = player.skeleton;
    for (let i = sk.drawOrder.length - 1; i >= 0; i--) {
      const slot = sk.drawOrder[i];
      if (!slot.bone.active || S.hidden.has(slot.data.name) || slot.color.a <= 0.01) continue;
      const g = geom(slot); if (!g) continue;
      const t = g.tri, W = g.w, U = g.uv;
      for (let k = 0; k < t.length; k += 3) {
        const a = t[k], b = t[k + 1], c = t[k + 2];
        const x1 = W[a * 2], y1 = W[a * 2 + 1], x2 = W[b * 2], y2 = W[b * 2 + 1], x3 = W[c * 2], y3 = W[c * 2 + 1];
        const det = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3); if (Math.abs(det) < 1e-9) continue;
        const l1 = ((y2 - y3) * (v.x - x3) + (x3 - x2) * (v.y - y3)) / det, l2 = ((y3 - y1) * (v.x - x3) + (x1 - x3) * (v.y - y3)) / det, l3 = 1 - l1 - l2;
        if (l1 < -1e-4 || l2 < -1e-4 || l3 < -1e-4) continue;
        const u = l1 * U[a * 2] + l2 * U[b * 2] + l3 * U[c * 2], vv = l1 * U[a * 2 + 1] + l2 * U[b * 2 + 1] + l3 * U[c * 2 + 1];
        const al = alphaAt(g.at.path || g.at.name, u, vv);
        if (al === null || al > 20) return slot;
        break;   // trúng vùng trong suốt của layer này: thử layer bên dưới
      }
    }
    return null;
  }
  function boundBones(at) {   // tên các xương mesh đang bind (weight)
    if (!(at instanceof spine.MeshAttachment) || !at.bones) return [];
    const s = new Set(), bs = player.skeleton.bones;
    for (let i = 0; i < at.bones.length;) { const n = at.bones[i++]; for (let k = 0; k < n; k++) s.add(bs[at.bones[i++]].data.name) }
    return [...s];
  }
  // ---- khung sáng quanh layer đang chọn ----
  const HL = new spine.Color(0.4, 1, 0.35, 1), HLE = new spine.Color(0, 0, 0, 0.8);
  function draw(p, sr, px) {
    for (const name of S.hidden) { const s = p.skeleton.findSlot(name); if (s) s.color.a = 0 }
    if (!ed.slot) return;
    const slot = p.skeleton.findSlot(ed.slot); if (!slot) return;
    const g = geom(slot); if (!g) return;
    const W = g.w, h = g.hull;
    for (const [w, c] of [[5, HLE], [2.5, HL]])
      for (let i = 0; i < h; i++) { const j = (i + 1) % h; sr.rectLine(true, W[i * 2], W[i * 2 + 1], W[j * 2], W[j * 2 + 1], w * px, c) }
    let minx = Infinity, maxy = -Infinity; for (let i = 0; i < W.length; i += 2) { minx = Math.min(minx, W[i]); maxy = Math.max(maxy, W[i + 1]) }
    S.labelAt = { x: minx, y: maxy };
  }
  // nhãn HTML trên khung xem (tên layer + xương)
  const tag = document.createElement("div"); tag.id = "selTag"; tag.hidden = true; document.querySelector("main").appendChild(tag);
  function placeTag() {
    if (!player || !ed.slot || !S.labelAt) { tag.hidden = true; return }
    const slot = player.skeleton.findSlot(ed.slot); if (!slot) { tag.hidden = true; return }
    const at = slot.getAttachment(), bb = boundBones(at);
    const cv = player.sceneRenderer.canvas, r = cv.getBoundingClientRect(), m = document.querySelector("main").getBoundingClientRect();
    const sc = player.sceneRenderer.camera.worldToScreen(new spine.Vector3(S.labelAt.x, S.labelAt.y, 0), r.width, r.height);
    tag.hidden = false; tag.style.left = (r.left - m.left + sc.x) + "px"; tag.style.top = (r.top - m.top + (r.height - sc.y) - 26) + "px";
    tag.textContent = `${slot.data.name}${at && at.name !== slot.data.name ? " / " + at.name : ""} · ${at instanceof spine.MeshAttachment ? (bb.length ? "mesh, bind: " + bb.join(", ") : "mesh, chưa bind (xương " + slot.bone.data.name + ")") : "region · xương " + slot.bone.data.name}`;
  }

  // ---- cửa sổ nổi: Layer / Xương ----
  const win = document.createElement("div"); win.id = "outWin"; win.hidden = store.get("outOpen", "0") !== "1";
  win.innerHTML = `<div id="owHead"><b>Cây</b><span id="owTabs"><button data-t="slots">Layer</button><button data-t="bones">Xương</button><button data-t="weight">Weight</button></span><button id="owClose" title="Ẩn cửa sổ">×</button></div>
    <div id="owBody"></div>`;
  document.querySelector("main").appendChild(win);
  const st = document.createElement("style");
  st.textContent = `#outWin{position:absolute;z-index:8;width:270px;max-height:min(70vh,560px);display:flex;flex-direction:column;background:var(--raise);border:1px solid var(--line);border-radius:8px;box-shadow:0 4px 18px #0006;font-size:12px}
    #owHead{display:flex;gap:6px;align-items:center;padding:6px 8px;border-bottom:1px solid var(--line);cursor:move;user-select:none}
    #owHead b{margin-right:auto} #owTabs{display:inline-flex;border:1px solid var(--line);border-radius:6px;overflow:hidden}
    #owTabs button{border:0;border-radius:0;padding:2px 10px} #owTabs button.on{background:var(--accent);color:#000;font-weight:600}
    #owClose{padding:0 7px} #owBody{overflow:auto;padding:4px 0}
    .owSec{padding:6px 10px;border-bottom:1px solid var(--line)} .owSec h4{margin:0 0 4px;font-size:12px}
    .owNote{color:var(--mute);font-size:11px;line-height:1.35;margin:3px 0} .owBtns{display:flex;flex-wrap:wrap;gap:5px;margin-top:6px}
    .owBar{height:5px;border-radius:3px;background:#ffd21a;display:inline-block;vertical-align:middle;margin-left:6px}
    .owKind{display:inline-block;padding:0 6px;border-radius:4px;font-size:10px;font-weight:700;margin-right:6px}
    .owKind.p{background:#3a7bd5;color:#fff} .owKind.b{background:#ffd21a;color:#000}
    .owRow{display:flex;gap:6px;align-items:center;padding:3px 8px;cursor:pointer;white-space:nowrap}
    .owRow:hover{background:#ffffff10} .owRow.on{background:color-mix(in srgb,var(--accent) 28%,transparent);color:var(--fg)}
    .owRow .tg{font-size:10px;padding:0 5px;border-radius:4px;background:#ffffff18;color:var(--mute)} .owRow .eye{opacity:.8;width:16px;text-align:center}
    .owRow .eye.off{opacity:.3} .owRow .nm{overflow:hidden;text-overflow:ellipsis}
    #selTag{position:absolute;z-index:4;pointer-events:none;padding:2px 8px;border-radius:5px;background:#1d6b1ae6;color:#fff;font-size:12px;white-space:nowrap}
    #outBtn.on{border-color:var(--accent);color:var(--accent)}`;
  document.head.appendChild(st);
  const pos = JSON.parse(store.get("outPos", "null") || "null") || { left: 16, top: 150 };
  Object.assign(win.style, { left: pos.left + "px", top: pos.top + "px" });
  const btn = document.createElement("button"); btn.id = "outBtn"; btn.textContent = "Cây ▣"; btn.title = "Bật / ẩn cửa sổ Layer / Xương (phím T)";
  document.getElementById("reload").before(btn);
  function setOpen(o) { win.hidden = !o; store.set("outOpen", o ? "1" : "0"); btn.classList.toggle("on", o); S.sig = "" }
  btn.onclick = () => setOpen(win.hidden); setOpen(!win.hidden);
  win.querySelector("#owClose").onclick = () => setOpen(false);
  document.addEventListener("keydown", ev => { if (ev.key.toLowerCase() === "t" && !ev.ctrlKey && !ev.metaKey && !/^(INPUT|TEXTAREA|SELECT)$/.test(ev.target.tagName)) setOpen(win.hidden) });
  // kéo cửa sổ
  let drag = null;
  win.querySelector("#owHead").addEventListener("pointerdown", ev => { if (ev.target.closest("button")) return; drag = { x: ev.clientX - win.offsetLeft, y: ev.clientY - win.offsetTop }; win.querySelector("#owHead").setPointerCapture(ev.pointerId) });
  win.querySelector("#owHead").addEventListener("pointermove", ev => { if (!drag) return; win.style.left = Math.max(0, ev.clientX - drag.x) + "px"; win.style.top = Math.max(0, ev.clientY - drag.y) + "px" });
  win.querySelector("#owHead").addEventListener("pointerup", () => { if (drag) store.set("outPos", JSON.stringify({ left: win.offsetLeft, top: win.offsetTop })); drag = null });
  win.querySelectorAll("#owTabs button").forEach(b => b.onclick = () => { S.tab = b.dataset.t; store.set("outTab", S.tab); S.sig = "" });
  function weightStats(at) {   // mesh có weight: theo từng xương -> tổng weight + số đỉnh chịu ảnh hưởng
    const st = new Map(), bs = player.skeleton.bones;
    if (!(at instanceof spine.MeshAttachment) || !at.bones) return st;
    for (let i = 0, f = 0; i < at.bones.length;) { const n = at.bones[i++]; for (let k = 0; k < n; k++, f += 3) {
      const nm = bs[at.bones[i++]].data.name, e = st.get(nm) || { sum: 0, cnt: 0 }; e.sum += at.vertices[f + 2]; e.cnt++; st.set(nm, e) } }
    return st;
  }
  function weightTab(sk) {
    const slot = ed.slot && sk.findSlot(ed.slot), at = slot?.getAttachment();
    if (!slot) return `<div class="owSec"><div class="owNote">Bấm vào một ảnh / mesh trên hình (hoặc tab Layer) để xem nó đang gắn với xương nào.</div></div>`;
    const isMesh = at instanceof spine.MeshAttachment, bound = isMesh && !!at.bones, sel = ed.sel?.data.name;
    const kind = !at ? "trống" : isMesh ? (bound ? "mesh đã bind" : "mesh chưa bind") : at instanceof spine.RegionAttachment ? "ảnh (region)" : "khác";
    let h = `<div class="owSec"><h4>${slot.data.name}${at && at.name !== slot.data.name ? " / " + at.name : ""} <span class="tg">${kind}</span></h4>`;
    h += `<div><span class="owKind p">PARENT</span><b data-bone="${slot.bone.data.name}" style="cursor:pointer">${slot.bone.data.name}</b></div>`;
    h += `<div class="owNote">${bound ? "Mesh đã bind: biến dạng theo các xương bind bên dưới; xương cha chỉ quyết định slot thuộc về đâu, không làm ảnh dời."
      : isMesh ? "Mesh chưa bind: mọi đỉnh đi theo xương cha, như một ảnh cứng. Bind để biến dạng theo nhiều xương."
      : "Ảnh thường đi theo xương cha. Muốn biến dạng theo nhiều xương: Lưới… (tab Setup) → Áp dụng để thành mesh, rồi Bind."}</div>`;
    if (bound) {
      const stt = [...weightStats(at)].sort((x, y) => y[1].sum - x[1].sum), tot = stt.reduce((t, [, e]) => t + e.sum, 0) || 1;
      h += `<div style="margin-top:6px"><span class="owKind b">BIND</span>${stt.length} xương</div>`;
      for (const [nm, e] of stt) h += `<div class="owRow ${sel === nm ? "on" : ""}" data-bone="${nm}" title="${e.cnt} đỉnh chịu ảnh hưởng"><span class="nm">${nm}</span><span class="tg">${Math.round(e.sum / tot * 100)}% · ${e.cnt} đỉnh</span><span class="owBar" style="width:${Math.max(3, e.sum / tot * 70)}px"></span></div>`;
    }
    h += `</div><div class="owSec"><h4>Gắn lại</h4>`;
    h += `<div class="owNote">Xương đang chọn: <b>${sel || "(chưa chọn: bấm khớp xương trên hình hoặc tab Xương)"}</b></div>`;
    h += `<div class="owBtns"><button id="owParent" ${!sel || sel === slot.bone.data.name ? "disabled" : ""} title="Đổi xương cha của ảnh sang xương đang chọn; ảnh đứng yên chỗ cũ">Parent → ${sel || "…"}</button></div>`;
    const list = window.spineWeights?.W.list || [];
    h += `<div class="owNote" style="margin-top:8px">Bind vào: ${list.length ? list.map(n => `<span class="tg" data-unb="${n}" title="Bấm để bỏ" style="cursor:pointer">${n} ×</span>`).join(" ") : "(chưa có xương nào)"}</div>`;
    h += `<div class="owBtns"><button id="owAddB" ${sel ? "" : "disabled"}>+ ${sel || "xương"}</button>`;
    h += `<button id="owBind" class="primary" ${isMesh && list.length ? "" : "disabled"} title="${isMesh ? "Bind mesh vào các xương trong danh sách, weight tự động" : "Chỉ bind được mesh (như Spine)"}">Bind</button></div>`;
    if (!isMesh) h += `<div class="owNote">Bind chỉ dùng được với mesh, như Spine.</div>`;
    return h + `</div>`;
  }
  function render() {
    if (win.hidden || !player?.skeleton) return;
    const sk = player.skeleton, s0 = ed.slot && sk.findSlot(ed.slot), at0 = s0?.getAttachment();
    const sig = [S.tab, ed.slot, ed.sel?.data.name, [...S.hidden].join(","), sk.bones.length, sk.drawOrder.map(s => s.getAttachment()?.name).join(","),
                 (window.spineWeights?.W.list || []).join(","), at0?.bones?.length, at0?.vertices?.length, s0?.bone.data.name].join("|");
    if (sig === S.sig) return; S.sig = sig;
    win.querySelectorAll("#owTabs button").forEach(b => b.classList.toggle("on", b.dataset.t === S.tab));
    const body = win.querySelector("#owBody"); let h = "";
    if (S.tab === "slots") {
      for (let i = sk.drawOrder.length - 1; i >= 0; i--) {   // trên cùng trước, như danh sách layer
        const s = sk.drawOrder[i], at = s.getAttachment(), nm = s.data.name;
        const type = !at ? "trống" : at instanceof spine.MeshAttachment ? (at.bones ? "mesh · " + boundBones(at).length + " xương" : "mesh") : at instanceof spine.RegionAttachment ? "ảnh" : at instanceof spine.ClippingAttachment ? "clip" : "khác";
        h += `<div class="owRow ${ed.slot === nm ? "on" : ""}" data-slot="${nm}"><span class="eye ${S.hidden.has(nm) ? "off" : ""}" data-eye="${nm}" title="Ẩn / hiện tạm (không ghi file)">👁</span><span class="nm">${nm}</span><span class="tg">${type}</span></div>`;
      }
    } else if (S.tab === "bones") {
      const ik = new Set(), tgt = new Set(); for (const c of sk.ikConstraints) { c.bones.forEach(b => ik.add(b)); tgt.add(c.target) }
      const walk = (b, d) => { h += `<div class="owRow ${ed.sel === b ? "on" : ""}" data-bone="${b.data.name}" style="padding-left:${8 + d * 14}px"><span class="nm">${b.data.name}</span>${tgt.has(b) ? '<span class="tg">IK</span>' : ik.has(b) ? '<span class="tg">chuỗi IK</span>' : ""}</div>`; b.children.forEach(c => walk(c, d + 1)) };
      sk.bones.filter(b => !b.parent).forEach(b => walk(b, 0));
    } else h = weightTab(sk);
    body.innerHTML = h;
    body.querySelectorAll("[data-eye]").forEach(e => e.onclick = ev => { ev.stopPropagation(); const n = e.dataset.eye;
      if (S.hidden.has(n)) { S.hidden.delete(n); const s = player.skeleton.findSlot(n); if (s) s.color.a = s.data.color.a } else S.hidden.add(n); S.sig = "" });
    body.querySelectorAll("[data-slot]").forEach(e => e.onclick = ev => select({ slot: e.dataset.slot, add: ev.ctrlKey || ev.metaKey }));
    body.querySelectorAll("[data-bone]").forEach(e => e.onclick = ev => select({ bone: e.dataset.bone, add: ev.ctrlKey || ev.metaKey }));
    body.querySelectorAll("[data-unb]").forEach(e => e.onclick = () => { const W = window.spineWeights.W; W.list = W.list.filter(n => n !== e.dataset.unb); S.sig = "" });
    const pb = body.querySelector("#owParent"); if (pb) pb.onclick = () => doParent();
    const ab = body.querySelector("#owAddB"); if (ab) ab.onclick = () => { const W = window.spineWeights.W, n = ed.sel?.data.name; if (n && !W.list.includes(n)) W.list.push(n); S.sig = "" };
    const bb = body.querySelector("#owBind"); if (bb) bb.onclick = () => document.getElementById("wBind").click();
  }
  async function doParent() {
    const slot = ed.slot, bone = ed.sel?.data.name; if (!slot || !bone || !cur) return;
    if (ed.dirty.size) return setStatus("đang có chỉnh sửa chưa ghi: lưu hoặc Bỏ trước khi đổi parent", "bad");
    try { const j = await edPost("/api/spine/parent", { json: cur.json, slot, bone });
      stamp = null; build(snapshot()); setStatus(`đã đổi parent của ${j.slot}: ${j.from} → ${j.bone} (ảnh giữ nguyên chỗ) · ${hhmmss()} · Ctrl+Z để hoàn tác`, "ok") }
    catch (e) { setStatus("đổi parent lỗi: " + e.message, "bad") }
  }
  // chọn / bỏ chọn: bấm lại đúng ảnh / xương đang chọn thì bỏ chọn. Chỉ giữ một lựa chọn (người dùng 2026-11-02):
  // chọn ảnh bỏ xương, chọn xương bỏ ảnh; giữ Ctrl (o.add) thì giữ lựa chọn kia (xương + ảnh cùng lúc, vd để Parent)
  function select(o) {
    if (o.slot !== undefined) { if (ed.slot === o.slot) ed.slot = null; else { ed.slot = o.slot; if (!o.add) ed.sel = null } }
    if (o.bone !== undefined) { const b = player.skeleton.findBone(o.bone); ed.sel = ed.sel === b ? null : b; if (ed.sel && !o.add) ed.slot = null }
    S.sig = ""; edRefresh(); window.spineWeights?.onSelect?.();
  }
  setInterval(() => { try { render(); placeTag() } catch (e) { console.warn(e) } }, 120);
  window.spineSel = { pickSlot, draw, select, boundBones, geom, S };
})();
