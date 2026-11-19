// Công cụ Mesh / Bind (2026-10-31), như Spine, làm thẳng trên khung xem chính (không mở cửa sổ riêng).
// Góp ý người dùng (gom lại):
//  - gộp sửa lưới + bind + weight thành Mesh/Bind; không tạo cửa sổ mới, dùng preview ngoài cùng, thông tin để ở mục công cụ;
//  - Custom Mesh: layer phải tích "Mesh" mới có lưới (mặc định 4 điểm như ảnh); Add / Delete / Dời sửa trực tiếp (tự ghi,
//    Ctrl+Z lùi); mọi thứ về trace gom vào mục "Auto trace" (bấm mới hiện): Số điểm, trace, ok thì Áp dụng lưới;
//    trace bám sát ảnh nhất có thể mà không cắt vào ảnh (server spine_edit._trace_points);
//  - Bind: xương hiện trên preview, mục chỉ hiện xương đang chọn / đang bind; "Huỷ bind" xương đang chọn -> weight của nó
//    chia sang các xương còn lại; bind xong xương cha của layer chuyển sang xương bind chính (server);
//  - Fix Weight: chỉ xương đã bind; điểm to, chia múi đúng màu các xương đang bind, lưới tô màu theo weight; chỉnh % đổi màu ngay.
// Server: /api/spine/mesh/trace {points}, /mesh/tri, /mesh/apply, /bind, /weights, /parent.
// Dùng biến chung: player, cur, ed, mode, store, edPost, build, snapshot, stamp, setStatus, hhmmss, toWorld, pxWorld, weightCache, $.
(() => {
  const box = document.createElement("section");
  box.id = "mbBox"; box.className = "sec tool";   // 2026-10-31: dùng được cả tab Animate (sửa weight ngay lúc anim)
  box.innerHTML = `<h3 class="secT">Mesh / Bind</h3>
    <div class="row"><span id="mbLayer" class="lpT"></span><span id="mbType" class="mute"></span>
      <label class="pill" style="margin-left:auto" title="Chỉ hiện layer đang sửa (ẩn tạm các layer khác, không ghi file). Bấm ra chỗ trống (bỏ chọn layer) hoặc bỏ tích là hiện lại"><input type="checkbox" id="mbIso">Isolate</label></div>
    <div class="seg" id="mbTabs"><button data-m="mesh">Custom Mesh</button><button data-m="bind">Bind</button><button data-m="fix">Fix Weight</button></div>
    <div id="mbMesh" class="mbPane">
      <div class="row"><label class="pill" title="Tích để biến ảnh thành mesh (4 điểm như ảnh), rồi Add / Delete / Dời hoặc Auto trace"><input type="checkbox" id="mbIsMesh">Mesh</label>
        <div class="seg" id="mbTools"><button data-t="add" title="Thêm điểm (A): bấm gần viền = điểm viền, trong ảnh = điểm trong">Add</button><button data-t="del" title="Xoá điểm (D)">Delete</button><button data-t="move" title="Dời điểm (V): kéo">Dời</button></div></div>
      <div id="mbMeshInfo" class="mute"></div>
      <details id="mbTraceBox"><summary>Auto trace</summary>
        <label class="mbSl" title="Tổng số điểm của lưới (kéo là trace lại ngay để xem). Viền bám sát ảnh, không cắt vào ảnh">Số điểm
          <input id="mbPts" type="range" min="4" max="150" step="1" value="30"><input id="mbPtsN" type="number" min="4" max="150" value="30"></label>
        <div class="row"><button id="mbTrace">Trace</button><button id="mbApply" class="primary" title="Ghi lưới trace vào file (giữ weight cũ bằng nội suy)">Áp dụng lưới</button><button id="mbCancel" title="Bỏ kết quả trace, về lưới trong file">Huỷ</button></div>
      </details>
      <details id="mbRemeshBox"><summary>Remesh (giảm điểm)</summary>
        <div class="mute">Giảm điểm trên chính lưới đang có (giữ chỗ đã sửa tay): giữ góc / chỗ cong trước, viền mới luôn bao trọn viền cũ, điểm trong chọn lại cho rải đều.</div>
        <label class="mbSl" title="Tổng số điểm sau khi giảm (kéo là xem trước ngay)">Số điểm
          <input id="mbRmPts" type="range" min="4" max="200" step="1" value="40"><input id="mbRmPtsN" type="number" min="4" max="400" value="40"></label>
        <label class="mbSl" title="Phần trăm số điểm dành cho điểm trong (giúp uốn mượt ở khớp). Mặc định giữ tỉ lệ của lưới cũ">Điểm trong %
          <input id="mbRmIn" type="range" min="0" max="60" step="1" value="20"><input id="mbRmInN" type="number" min="0" max="60" value="20"></label>
        <div id="mbRmInfo" class="mute"></div>
        <div class="row"><button id="mbRemesh">Remesh</button><button id="mbRmApply" class="primary" title="Ghi lưới mới vào file (giữ weight cũ bằng nội suy)">Áp dụng lưới</button><button id="mbRmCancel" title="Bỏ kết quả, về lưới trong file">Huỷ</button></div>
      </details>
    </div>
    <div id="mbBind" class="mbPane">
      <div class="mute">Bấm xương trên hình để thêm (bấm lại để bỏ), rồi <b>Bind</b>. Layer đã bind: Bind chỉ <b>thêm xương với weight 0 %</b> (weight cũ giữ nguyên) để tự sơn vùng của nó ở Fix Weight. <b>Auto weight</b> = tính lại tự động cả mesh cho mọi xương đang bind. <b>✕</b> sau tên xương = huỷ bind.</div>
      <div id="mbChips" class="row"></div>
      <div class="row"><button id="mbBindGo" class="primary" title="Layer chưa bind: weight tự động cho các xương chọn. Layer đã bind: chỉ thêm các xương mới chọn với weight 0 % (weight cũ giữ nguyên), rồi sang Fix Weight sơn vùng của nó">Bind</button><button id="mbRebind" title="Auto weight: tính lại weight tự động cho TOÀN BỘ mesh theo mọi xương đang bind (+ xương mới chọn). Mất weight sửa tay (Hoàn tác được). Bấm 2 lần để chạy">Auto weight</button>
        <label title="Độ mềm khi trộn xương: cao = vùng chuyển giữa các xương rộng hơn">Mềm <input id="mbSoft" type="range" min="0.02" max="0.2" step="0.01" value="0.05"></label></div>
    </div>
    <div id="mbFix" class="mbPane">
      <div class="mute">Bấm điểm (giữ <kbd>Ctrl</kbd> chọn nhiều) hoặc <b>giữ chuột giữa quét khung</b> (<kbd>Shift</kbd> thêm, <kbd>Ctrl</kbd> bớt), rồi chỉnh % từng xương đang bind. Bấm tên xương để chỉ tô weight của xương đó.</div>
      <div id="mbFixBones" class="row"></div>
      <div class="row"><button id="mbSelAll" title="Chọn mọi điểm của lưới (Ctrl+A)">Chọn hết</button><button id="mbSelNone" title="Bỏ chọn điểm (Esc)">Bỏ chọn</button></div>
      <div id="mbVtx"></div>
      <div class="row" id="mbSmoothRow" title="Làm mượt weight: mỗi điểm trộn với trung bình các điểm kề trên lưới. Có điểm đang chọn thì chỉ làm mượt các điểm đó (điểm khác giữ nguyên làm mốc), không chọn thì cả lưới">
        <button id="mbSmooth">Auto smooth</button>
        <label>Mạnh <input id="mbSmK" type="range" min="0.1" max="1" step="0.05" value="0.5"></label>
        <label>Lần <input id="mbSmN" type="number" min="1" max="20" value="3" style="width:44px"></label></div>
      <div class="row"><button id="mbSave" class="primary">Lưu weight</button><button id="mbDrop">Bỏ</button><span id="mbFixInfo" class="mute"></span></div>
    </div>`;
  $("secBone").after(box);
  const st = document.createElement("style");
  st.textContent = `#mbBox .mbPane{display:none;flex-direction:column;gap:6px} #mbBox[data-m="mesh"] #mbMesh,#mbBox[data-m="bind"] #mbBind,#mbBox[data-m="fix"] #mbFix{display:flex}
    #mbTools{flex:1} #mbTools button:disabled{opacity:.4;cursor:not-allowed}
    #mbTraceBox{border:1px solid var(--line);border-radius:6px;padding:4px 8px} #mbTraceBox summary{cursor:pointer;font-weight:600}
    #mbTraceBox[open]{display:flex;flex-direction:column;gap:6px;padding-bottom:8px}
    #mbRemeshBox{border:1px solid var(--line);border-radius:6px;padding:4px 8px} #mbRemeshBox summary{cursor:pointer;font-weight:600}
    #mbRemeshBox[open]{display:flex;flex-direction:column;gap:6px;padding-bottom:8px}
    .mbSl{display:grid !important;grid-template-columns:auto 1fr 54px;gap:6px;align-items:center;color:var(--fg) !important} .mbSl input[type=range]{width:100%}
    .mbc{display:inline-flex;align-items:center;gap:5px;padding:2px 9px;border-radius:12px;font-size:11px;font-weight:600;cursor:pointer;border:2px solid transparent;color:#111}
    .mbc.sel{border-color:var(--fg);box-shadow:0 0 0 1px #000} .mbc.new{opacity:.75;border-style:dashed;border-color:#0006}
    .mbc .mbx{margin-left:2px;padding:0 3px;border-radius:8px;font-weight:700;opacity:.65} .mbc .mbx:hover{opacity:1;background:#0003}
    #mbVtx{display:flex;flex-direction:column;gap:4px} .mbw{display:grid;grid-template-columns:auto 1fr 52px 16px;gap:6px;align-items:center;font-size:11px}
    .mbw .sw{width:10px;height:10px;border-radius:50%} .mbw input[type=range]{width:100%} .mbw input[type=number]{width:52px} .mbw b{cursor:pointer;color:var(--mute)}
    #meshOpen,#meshTool{display:none !important}`;
  document.head.appendChild(st);

  const B = { m: store.get("mbMode", "mesh"), pick: [], chip: null, sel: [], per: null, world: null, slot: null, dirty: false, focus: null };
  const E = { slot: null, att: null, mesh: false, w: 0, h: 0, hull: [], inner: [], tris: [], tool: store.get("mbTool", "add"), sel: null, drag: null,
              preview: false, A: null, Ai: null, undo: [], triT: 0, trT: 0, saveT: 0, saving: false, again: false,
              rmBase: null, rmT: 0, rmFor: "" };
  const hue = i => (i * 137.508) % 360;
  function rgb(i) { const h = hue(i) / 60, c = 0.85, x = c * (1 - Math.abs(h % 2 - 1)); const [r, g, b] = h < 1 ? [c, x, 0] : h < 2 ? [x, c, 0] : h < 3 ? [0, c, x] : h < 4 ? [0, x, c] : h < 5 ? [x, 0, c] : [c, 0, x]; return [r + 0.15, g + 0.15, b + 0.15] }
  const css = i => { const c = rgb(i); return `rgb(${c.map(v => Math.min(255, v * 255 | 0))})` };
  const active = () => $("mbBox").classList.contains("active");
  const slotObj = () => ed.slot && player?.skeleton?.findSlot(ed.slot);
  const att = () => slotObj()?.getAttachment();
  const isMesh = a => a instanceof spine.MeshAttachment, isRegion = a => a instanceof spine.RegionAttachment;
  const say = (m, c) => { setStatus(m, c); setTimeout(() => setStatus(m, c), 1600) };   // giữ thông báo sau dòng "đã nạp" khi trang nạp lại
  const bIdx = n => player.skeleton.findBone(n).data.index;
  // skeleton riêng ở tư thế gốc: weight / toạ độ local của mesh tính theo setup, kể cả khi đang xem một frame anim
  let SS = null, SSd = null;
  function setupSk() {
    const sd = player.skeleton.data;
    if (SSd !== sd) { SS = new spine.Skeleton(sd); SSd = sd }
    if (player.skeleton.skin) SS.setSkin(player.skeleton.skin);
    SS.setToSetupPose(); SS.updateWorldTransform(spine.Physics.update);
    return SS;
  }

  function setM(m) {
    if (m !== B.m && E.preview) cancelPreview(true);
    B.m = m; store.set("mbMode", m); box.dataset.m = m;
    box.querySelectorAll("#mbTabs button").forEach(b => b.classList.toggle("primary", b.dataset.m === m));
    if (m === "bind") { B.pick = []; B.chip = null }
    if (m === "fix") loadPer(); else if (B.dirty) dropFix();
    if (m === "mesh") loadMesh(true);
    render();
  }
  box.querySelector("#mbTabs").onclick = ev => { const m = ev.target.closest("button")?.dataset.m; if (m) setM(m) };

  // ================= Custom Mesh: sửa lưới trên khung xem chính =================
  // px ảnh (y xuống, như uvs của Spine) <-> thế giới: affine khớp bình phương nhỏ nhất từ các điểm của attachment (tư thế setup)
  function fitAffine(src, dst) {
    const s = [[0, 0, 0], [0, 0, 0], [0, 0, 0]], bx = [0, 0, 0], by = [0, 0, 0];
    for (let i = 0; i < src.length; i++) { const v = [src[i][0], src[i][1], 1]; for (let r = 0; r < 3; r++) { for (let c = 0; c < 3; c++) s[r][c] += v[r] * v[c]; bx[r] += v[r] * dst[i][0]; by[r] += v[r] * dst[i][1] } }
    const [a, b, c] = s[0], [d, e, f] = s[1], [g, h, k] = s[2];
    const det = a * (e * k - f * h) - b * (d * k - f * g) + c * (d * h - e * g);
    const I = [[(e * k - f * h) / det, (c * h - b * k) / det, (b * f - c * e) / det], [(f * g - d * k) / det, (a * k - c * g) / det, (c * d - a * f) / det], [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]];
    const mul = v => I.map(r => r[0] * v[0] + r[1] * v[1] + r[2] * v[2]);
    const px = mul(bx), py = mul(by);
    return [px[0], px[1], px[2], py[0], py[1], py[2]];
  }
  const app = (M, p) => [M[0] * p[0] + M[1] * p[1] + M[2], M[3] * p[0] + M[4] * p[1] + M[5]];
  function invA(M) { const det = M[0] * M[4] - M[1] * M[3]; return [M[4] / det, -M[1] / det, (M[1] * M[5] - M[4] * M[2]) / det, -M[3] / det, M[0] / det, (M[3] * M[2] - M[0] * M[5]) / det] }
  function calcAffine() {
    const s = slotObj(), a = att(); if (!s || !a) return false;
    const src = [], dst = [];
    if (isRegion(a)) {   // offset của RegionAttachment: dưới-trái, trên-trái, trên-phải, dưới-phải
      const v = new Float32Array(8); a.computeWorldVertices(s, v, 0, 2);
      const P = [[0, E.h], [0, 0], [E.w, 0], [E.w, E.h]];
      for (let i = 0; i < 4; i++) { src.push(P[i]); dst.push([v[i * 2], v[i * 2 + 1]]) }
    } else if (isMesh(a)) {
      const n = a.worldVerticesLength, v = new Float32Array(n); a.computeWorldVertices(s, 0, n, v, 0, 2);
      for (let i = 0; i < n / 2; i++) { src.push([a.regionUVs[i * 2] * E.w, a.regionUVs[i * 2 + 1] * E.h]); dst.push([v[i * 2], v[i * 2 + 1]]) }
    } else return false;
    E.A = fitAffine(src, dst); E.Ai = invA(E.A); return true;
  }
  async function loadMesh(force) {
    const s = slotObj(), a = att();
    if (!s || !a || (!isRegion(a) && !isMesh(a))) { E.slot = null; E.hull = []; E.inner = []; E.tris = []; render(); return }
    if (!force && E.slot === s.data.name && E.att === a.name) return;
    try {
      const raw = await (await fetch("/spine-live/f/" + cur.json, { cache: "no-store" })).json();
      let aj = null;
      for (const sk of raw.skins || []) { const x = sk.attachments?.[s.data.name]?.[a.name]; if (x) { aj = x; break } }
      if (!aj) throw new Error("không thấy ảnh trong file");
      if (E.slot !== s.data.name) E.undo = [];
      E.slot = s.data.name; E.att = a.name; E.w = aj.width; E.h = aj.height; E.mesh = aj.type === "mesh";
      if (E.mesh) { const n = aj.uvs.length / 2, P = []; for (let i = 0; i < n; i++) P.push([aj.uvs[2 * i] * E.w, aj.uvs[2 * i + 1] * E.h]); E.hull = P.slice(0, aj.hull); E.inner = P.slice(aj.hull) }
      else { E.hull = [[0, 0], [E.w, 0], [E.w, E.h], [0, E.h]]; E.inner = [] }
      E.preview = false; E.sel = null; ed.dirty.delete("__mesh");
      calcAffine(); retri();
    } catch (e) { setStatus("nạp lưới lỗi: " + e.message, "bad") }
    render();
  }
  function retri() {
    clearTimeout(E.triT);
    E.triT = setTimeout(async () => {
      if (E.hull.length < 3) { E.tris = []; return }
      try { E.tris = (await edPost("/api/spine/mesh/tri", { hull: E.hull, inner: E.inner, w: E.w, h: E.h })).triangles } catch { E.tris = [] }
      meshInfo();
    }, 60);
  }
  function meshInfo() {
    $("mbMeshInfo").textContent = !E.slot ? "bấm chọn một layer ảnh trên hình" : !E.mesh ? "ảnh thường (4 góc): tích Mesh để tạo lưới"
      : `${E.hull.length + E.inner.length} điểm (viền ${E.hull.length}, trong ${E.inner.length}) · ${E.tris.length} tam giác${E.preview ? " · đang xem trace: Áp dụng lưới để ghi" : E.saving ? " · đang ghi…" : ""}`;
    $("mbIsMesh").checked = !!E.mesh; $("mbIsMesh").disabled = !E.slot || E.mesh;
    box.querySelectorAll("#mbTools button").forEach(b => b.disabled = !E.mesh);
    if ($("mbRemeshBox").open && E.mesh) rmLimits();
  }
  async function writeMesh(what) {   // ghi lưới hiện tại vào file (mỗi lần = một bước Hoàn tác của trang)
    if (!E.slot) return;
    if (E.saving) { E.again = true; return }
    E.saving = true; meshInfo();
    try {
      const j = await edPost("/api/spine/mesh/apply", { json: cur.json, slot: E.slot, attachment: E.att, hull: E.hull, inner: E.inner });
      stamp = null; await build(snapshot());
      say(`${what}: ${j.vertices} điểm, ${j.triangles} tam giác${j.weighted ? " (giữ weight cũ)" : ""} · ${hhmmss()} · Ctrl+Z lùi`, "ok");
      E.mesh = true; E.preview = false; ed.dirty.delete("__mesh");
    } catch (e) { setStatus("ghi lưới lỗi: " + e.message, "bad") }
    E.saving = false;
    if (E.again) { E.again = false; writeMesh(what) } else setTimeout(() => { calcAffine(); meshInfo() }, 500);
  }
  // sửa tay (Add / Delete / Dời): đang xem trace thì chỉ sửa bản xem; không thì tự ghi file sau 0.5 s
  function edit(fn) {
    E.undo.push(JSON.stringify([E.hull, E.inner, E.mesh])); if (E.undo.length > 100) E.undo.shift();
    fn(); retri(); meshInfo();
    if (E.preview) { ed.dirty.add("__mesh"); return }
    clearTimeout(E.saveT); E.saveT = setTimeout(() => writeMesh("đã sửa lưới"), 500);
  }
  function undoMesh() {
    if (!E.undo.length) return false;
    const [h, i, m] = JSON.parse(E.undo.pop());
    if (!m && E.mesh && !E.preview) { setStatus("lưới vừa tạo từ ảnh thường: dùng ↶ Hoàn tác ở đầu trang để về ảnh thường", ""); return true }
    E.hull = h; E.inner = i; retri(); meshInfo();
    if (!E.preview) { clearTimeout(E.saveT); E.saveT = setTimeout(() => writeMesh("hoàn tác lưới"), 300) }
    return true;
  }
  function setTool(t) { E.tool = t; store.set("mbTool", t); box.querySelectorAll("#mbTools button").forEach(b => b.classList.toggle("primary", b.dataset.t === t)) }
  box.querySelector("#mbTools").onclick = ev => { const t = ev.target.closest("button")?.dataset.t; if (t) setTool(t) };
  $("mbIsMesh").onchange = () => {   // ảnh thường -> mesh 4 góc
    if (!$("mbIsMesh").checked || !E.slot || E.mesh) return;
    E.hull = [[0, 0], [E.w, 0], [E.w, E.h], [0, E.h]]; E.inner = [];
    E.undo.push(JSON.stringify([E.hull, E.inner, false])); writeMesh("đã tạo mesh " + E.slot);
  };
  async function trace() {
    if (!E.slot) return setStatus("bấm chọn một layer ảnh trên hình trước", "bad");
    const n = +$("mbPts").value;
    try {
      const j = await edPost("/api/spine/mesh/trace", { json: cur.json, slot: E.slot, attachment: E.att, points: n });
      if (!E.preview) E.undo.push(JSON.stringify([E.hull, E.inner, E.mesh]));
      E.hull = j.hull; E.inner = j.inner; E.preview = true; E.rmBase = null; ed.dirty.add("__mesh"); retri(); meshInfo();
      const tot = j.hull.length + j.inner.length;
      setStatus(`trace: ${tot} điểm${tot > n ? " (tối thiểu để viền không cắt vào ảnh)" : ""} · ok thì bấm Áp dụng lưới`, "ok");
    } catch (e) { setStatus("trace lỗi: " + e.message, "bad") }
  }
  function cancelPreview(silent) { E.preview = false; E.rmBase = null; ed.dirty.delete("__mesh"); loadMesh(true); if (!silent) setStatus("bỏ kết quả trace", "") }
  // ---- Remesh (2026-11-03): giảm điểm trên lưới đang có, xem trước như trace, Áp dụng lưới mới ghi file ----
  // E.rmBase = lưới gốc của lượt remesh (lưới trong file, hoặc kết quả trace đang xem): kéo thanh nhiều lần vẫn giảm từ gốc này.
  const rmSync = (id, v) => { $(id).value = v; $(id + "N").value = v };
  function rmBaseNow() { return E.preview && E.rmBase ? E.rmBase : { hull: E.hull.map(p => [...p]), inner: E.inner.map(p => [...p]) } }
  function rmLimits() {   // thanh Số điểm: tối đa = số điểm lưới gốc; mặc định 60% và tỉ lệ điểm trong như lưới gốc
    const b = rmBaseNow(), tot = b.hull.length + b.inner.length; if (!tot) return;
    $("mbRmPts").max = tot; $("mbRmPtsN").max = tot;
    if (E.rmFor !== E.slot + "|" + tot) {
      E.rmFor = E.slot + "|" + tot;
      rmSync("mbRmPts", Math.max(4, Math.round(tot * 0.6)));
      rmSync("mbRmIn", Math.min(60, Math.round(b.inner.length / tot * 100)));
    }
    if (!(E.preview && E.rmBase)) $("mbRmInfo").textContent = `lưới gốc: ${tot} điểm (viền ${b.hull.length}, trong ${b.inner.length})`;   // đang xem remesh: giữ dòng kết quả
  }
  async function remesh() {
    if (!E.slot || !E.mesh) return setStatus("chọn một layer đã là mesh (Custom Mesh) trước", "bad");
    const base = rmBaseNow(), tot = base.hull.length + base.inner.length, n = +$("mbRmPts").value;
    if (n >= tot) return setStatus(`Số điểm (${n}) phải nhỏ hơn lưới gốc (${tot})`, "bad");
    try {
      const j = await edPost("/api/spine/mesh/remesh", { json: cur.json, slot: E.slot, attachment: E.att, hull: base.hull, inner: base.inner,
                                                        points: n, innerPct: +$("mbRmIn").value });
      if (!E.preview) { E.undo.push(JSON.stringify([E.hull, E.inner, E.mesh])); E.rmBase = base }
      else if (!E.rmBase) E.rmBase = base;
      E.hull = j.hull; E.inner = j.inner; E.preview = true; ed.dirty.add("__mesh"); retri(); meshInfo();
      const now = j.hull.length + j.inner.length;
      $("mbRmInfo").textContent = `${tot} → ${now} điểm (viền ${j.hull.length}, trong ${j.inner.length}) · ${j.triangles} tam giác · lưới phình ${j.grow_pct}%`
        + ` · điểm ảnh ngoài viền ${j.cut_px} px (lưới cũ ${j.old_cut_px})`;
      setStatus(`remesh ${E.slot}: ${tot} → ${now} điểm · ok thì bấm Áp dụng lưới`, "ok");
    } catch (e) { setStatus("remesh lỗi: " + e.message, "bad") }
  }
  $("mbRemesh").onclick = remesh;
  $("mbRmApply").onclick = () => { if (!E.preview || !E.rmBase) return setStatus("chưa có kết quả remesh: kéo Số điểm hoặc bấm Remesh", "bad"); writeMesh("đã remesh lưới") };
  $("mbRmCancel").onclick = () => { cancelPreview(true); setStatus("bỏ kết quả remesh", "") };
  $("mbRemeshBox").addEventListener("toggle", () => { if ($("mbRemeshBox").open) rmLimits() });
  for (const id of ["mbRmPts", "mbRmIn"]) {
    $(id).oninput = () => { rmSync(id, +$(id).value); clearTimeout(E.rmT); E.rmT = setTimeout(remesh, 200) };
    $(id + "N").onchange = () => { rmSync(id, Math.max(+$(id).min, Math.min(+$(id).max, +$(id + "N").value || 0))); remesh() };
  }
  $("mbTrace").onclick = trace;
  $("mbApply").onclick = () => { if (!E.preview) return setStatus("chưa có kết quả trace: kéo Số điểm hoặc bấm Trace", "bad"); writeMesh("đã áp dụng lưới trace") };
  $("mbCancel").onclick = () => cancelPreview();
  const ptsSync = v => { $("mbPts").value = v; $("mbPtsN").value = v; store.set("mbPts", String(v)) };
  ptsSync(+store.get("mbPts", "30"));
  $("mbPts").oninput = () => { ptsSync(+$("mbPts").value); clearTimeout(E.trT); E.trT = setTimeout(trace, 200) };
  $("mbPtsN").onchange = () => { ptsSync(Math.max(4, Math.min(150, +$("mbPtsN").value || 30))); trace() };

  // ================= Bind / Fix Weight =================
  function boundNames() {
    const a = att(); if (!isMesh(a) || !a.bones) return slotObj() ? [slotObj().bone.data.name] : [];
    const bs = player.skeleton.bones, out = new Set();
    for (let i = 0; i < a.bones.length;) { const n = a.bones[i++]; for (let k = 0; k < n; k++) out.add(bs[a.bones[i++]].data.name) }
    return [...out];
  }
  function worldVerts(s, a) { const n = a.worldVerticesLength, v = new Float32Array(n); a.computeWorldVertices(s, 0, n, v, 0, 2); return v }
  function readPer() {   // [{xương: w}] + vị trí thế giới (tư thế setup) của mesh đang chọn
    const s = slotObj(), a = att(); if (!s || !isMesh(a)) return null;
    const ss = setupSk().findSlot(s.data.name);
    const w = worldVerts(ss, a), bs = player.skeleton.bones, world = [];
    for (let i = 0; i < w.length; i += 2) world.push([w[i], w[i + 1]]);
    let per;
    if (!a.bones) per = world.map(() => ({ [s.bone.data.name]: 1 }));
    else { per = []; for (let i = 0, f = 0; i < a.bones.length;) { const n = a.bones[i++], d = {}; for (let k = 0; k < n; k++, f += 3) d[bs[a.bones[i++]].data.name] = a.vertices[f + 2]; per.push(d) } }
    return { per, world };
  }
  function loadPer() {
    B.per = null; B.sel = []; B.dirty = false; ed.dirty.delete("__weights");
    const r = readPer(); if (!r) return;
    B.per = r.per; B.world = r.world; B.slot = ed.slot;
    if (B.focus && !boundNames().includes(B.focus)) B.focus = null;
  }
  function applyRuntime() {   // dựng lại bones / vertices của attachment từ B.per (tư thế setup): xem biến dạng + màu ngay
    const s = slotObj(), a = att(); if (!s || !isMesh(a) || !B.per) return;
    const sk = setupSk(), bones = [], verts = [];
    B.per.forEach((d, i) => {
      const ent = Object.entries(d).filter(([, w]) => w > 0.0001); bones.push(ent.length);
      for (const [n, w] of ent) { const b = sk.findBone(n), l = b.worldToLocal(new spine.Vector2(B.world[i][0], B.world[i][1])); bones.push(b.data.index); verts.push(l.x, l.y, w) }
    });
    a.bones = bones; a.vertices = Float32Array.from(verts);
    try { weightCache.delete(a) } catch {}
  }
  function setW(bone, pct) {
    for (const i of B.sel) {
      const d = B.per[i], v = Math.max(0, Math.min(1, pct / 100)), others = Object.keys(d).filter(k => k !== bone);
      const rest = others.reduce((t, k) => t + d[k], 0);
      if (!others.length) { d[bone] = 1; continue }
      d[bone] = v;
      for (const k of others) d[k] = rest > 1e-6 ? d[k] / rest * (1 - v) : (1 - v) / others.length;
      for (const k of Object.keys(d)) if (d[k] < 0.0005 && k !== bone) delete d[k];
    }
    B.dirty = true; ed.dirty.add("__weights"); applyRuntime(); renderVtx();
  }
  function removeBone(bone) { for (const i of B.sel) { const d = B.per[i]; if (Object.keys(d).length < 2) continue; delete d[bone]; const t = Object.values(d).reduce((a, b) => a + b, 0); for (const k in d) d[k] /= t } B.dirty = true; ed.dirty.add("__weights"); applyRuntime(); render() }
  // Auto smooth (2026-11-03): mỗi lần lặp, điểm đích = (1 - k) * weight của nó + k * trung bình weight các điểm kề trên lưới
  // (cạnh tam giác). Có điểm chọn: chỉ các điểm đó đổi, điểm khác làm mốc. Mỗi điểm giữ tối đa 4 xương, tổng = 1.
  function smoothW() {
    const s = slotObj(), a = att();
    if (!s || !isMesh(a) || !B.per) return setStatus("chọn một mesh đã Bind trước", "bad");
    const n = B.per.length, nb = Array.from({ length: n }, () => new Set()), t = a.triangles;
    for (let i = 0; i < t.length; i += 3) for (let e = 0; e < 3; e++) { const p = t[i + e], q = t[i + (e + 1) % 3]; nb[p].add(q); nb[q].add(p) }
    const ids = B.sel.length ? [...B.sel] : [...Array(n).keys()];
    const k = +$("mbSmK").value, N = Math.max(1, Math.min(20, +$("mbSmN").value || 3));
    for (let it = 0; it < N; it++) {
      const next = ids.map(i => {
        if (!nb[i].size) return B.per[i];
        const avg = {};
        for (const j of nb[i]) for (const [b, w] of Object.entries(B.per[j])) avg[b] = (avg[b] || 0) + w / nb[i].size;
        const d = {};
        for (const b of new Set([...Object.keys(B.per[i]), ...Object.keys(avg)])) d[b] = (1 - k) * (B.per[i][b] || 0) + k * (avg[b] || 0);
        const top = Object.entries(d).filter(([, w]) => w > 0.005).sort((x, y) => y[1] - x[1]).slice(0, 4);
        const tot = top.reduce((u, [, w]) => u + w, 0) || 1;
        return Object.fromEntries(top.map(([b, w]) => [b, w / tot]));
      });
      ids.forEach((i, m) => { B.per[i] = next[m] });
    }
    B.dirty = true; ed.dirty.add("__weights"); applyRuntime(); render();
    setStatus(`đã làm mượt weight ${ids.length} điểm (${N} lần, mạnh ${k}) · chưa lưu: bấm Lưu weight, Bỏ để huỷ`, "ok");
  }
  $("mbSmooth").onclick = smoothW;
  $("mbSelAll").onclick = () => { if (B.per) { B.sel = [...B.per.keys()]; render() } };
  $("mbSelNone").onclick = () => { B.sel = []; render() };
  function dropFix() { B.dirty = false; ed.dirty.delete("__weights"); if (!ed.dirty.size) ed.pending = false; stamp = null; build(snapshot()) }
  $("mbDrop").onclick = dropFix;
  $("mbSave").onclick = async () => {
    const s = slotObj(), a = att(); if (!s || !B.per) return;
    try {
      await edPost("/api/spine/weights", { json: cur.json, slot: s.data.name, attachment: a.name, weights: B.per });
      B.dirty = false; ed.dirty.delete("__weights"); if (!ed.dirty.size) ed.pending = false; stamp = null; build(snapshot()); setTimeout(() => { loadPer(); render() }, 700);
      say("đã lưu weight " + s.data.name + " · " + hhmmss() + " (Ctrl+Z / Hoàn tác lùi)", "ok");
    } catch (e) { setStatus("lưu weight lỗi: " + e.message, "bad") }
  };
  // Bind (2026-11-05, người dùng: "chọn 1 xương và nhấn Bind thì sẽ là bind thêm chứ không phải chỉ bind 1 xương đấy"):
  // mesh đã có weight -> chỉ thêm xương mới (server "add": weight cũ giữ, xương mới nhận phần ở vùng gần nó);
  // mesh chưa có weight -> tính tự động cho các xương chọn. "Bind lại từ đầu" = tính lại cho mọi xương trong danh sách.
  async function doBind(fresh) {
    const s = slotObj(), a = att();
    if (!s) return setStatus("bấm chọn một layer ảnh trên hình trước", "bad");
    if (!isMesh(a)) return setStatus("layer này là ảnh thường: vào Custom Mesh, tích Mesh rồi Bind", "bad");
    const bound = a.bones ? boundNames() : [], add = B.pick.filter(n => !bound.includes(n));
    const bones = fresh ? [...new Set([...bound, ...B.pick])] : (bound.length ? add : B.pick);
    if (!bones.length) return setStatus(bound.length ? "bấm thêm xương mới trên hình rồi Bind (xương đang bind giữ nguyên)" : "bấm chọn ít nhất một xương trên hình", "bad");
    // Auto weight (2026-11-18, người dùng: "cần có thêm 1 nút auto weight lại trong phần bind"): hỏi lại 2 bước ngay trên nút
    // (không dùng confirm(): trình duyệt trong app có thể tự đóng hộp thoại)
    if (fresh && !armDelete($("mbRebind"), null, `Auto weight ${bones.length} xương?`)) return setStatus(`bấm Auto weight lần nữa để tính lại weight toàn bộ ${s.data.name} theo ${bones.length} xương (mất weight sửa tay, Hoàn tác được)`);
    try {
      const body = { json: cur.json, slot: s.data.name, attachment: a.name, bones, soft: +$("mbSoft").value };
      if (!fresh && bound.length) body.add = add;
      const j = await edPost("/api/spine/bind", body);
      B.pick = []; B.chip = null;
      stamp = null; await build(snapshot()); setTimeout(render, 700);
      const what = j.added?.length ? `đã thêm ${j.added.join(", ")} vào ${s.data.name} với weight 0 % (weight cũ giữ nguyên, giờ ${j.bones.length} xương) · sang Fix Weight sơn vùng cho nó` : (fresh ? `Auto weight ${s.data.name}: tính lại toàn bộ theo ${j.bones.length} xương` : `đã bind ${s.data.name} vào ${j.bones.length} xương`);
      say(`${what} · ${j.vertices} điểm${j.reparented ? " · cha mới: " + j.parent : ""} · ${hhmmss()} · Fix Weight để chỉnh từng điểm`, "ok");
    } catch (e) { setStatus("bind lỗi: " + e.message, "bad") }
  }
  $("mbBindGo").onclick = () => doBind(false);
  $("mbRebind").onclick = () => doBind(true);
  // Huỷ bind một xương (nút ✕ sau tên, 2026-11-05): weight của nó ở mỗi điểm chia sang các xương còn lại (theo tỉ lệ đang có;
  // điểm chỉ có xương đó thì về xương còn lại gần nhất); xương cha đang là xương bị huỷ thì chuyển sang xương bind chính còn lại.
  async function unbind(n) {
    const s = slotObj();
    if (!s || !n) return;
    const bound = att()?.bones ? boundNames() : [];
    if (!bound.includes(n)) { B.pick = B.pick.filter(x => x !== n); if (B.chip === n) B.chip = null; return render() }   // xương mới chọn, chưa bind: chỉ bỏ chọn
    if (bound.length < 2) return setStatus("không huỷ được xương bind cuối cùng", "bad");
    const r = readPer(); if (!r) return;
    const rest = bound.filter(x => x !== n), sk = player.skeleton;
    const near = p => rest.map(x => { const b = sk.findBone(x); return [x, segD(p, [b.worldX, b.worldY], tip(b))] }).sort((a, b) => a[1] - b[1])[0][0];
    r.per.forEach((d, i) => {
      delete d[n];
      const t = Object.values(d).reduce((a, b) => a + b, 0);
      if (t < 1e-6) { for (const k in d) delete d[k]; d[near(r.world[i])] = 1 }
      else for (const k in d) d[k] = d[k] / t;
    });
    try {
      await edPost("/api/spine/weights", { json: cur.json, slot: s.data.name, attachment: att().name, weights: r.per });
      if (s.bone.data.name === n) {
        const tot = {}; r.per.forEach(d => { for (const k in d) tot[k] = (tot[k] || 0) + d[k] });
        await edPost("/api/spine/parent", { json: cur.json, slot: s.data.name, bone: Object.entries(tot).sort((a, b) => b[1] - a[1])[0][0] });
      }
      if (B.chip === n) B.chip = null;
      stamp = null; await build(snapshot()); setTimeout(render, 700);
      say(`đã huỷ bind ${n} khỏi ${s.data.name} (weight chia sang ${rest.join(", ")}) · Ctrl+Z / Hoàn tác lùi`, "ok");
    } catch (e) { setStatus("huỷ bind lỗi: " + e.message, "bad") }
  }
  function toggle(list, n, multi) { return multi ? (list.includes(n) ? list.filter(x => x !== n) : [...list, n]) : (list.length === 1 && list[0] === n ? [] : [n]) }

  // ================= giao diện mục =================
  function chip(n, cls) { return `<span class="mbc ${cls}" data-b="${n}" style="background:${css(bIdx(n))}">${n}</span>` }
  function renderVtx() {
    if (!B.per || !B.sel.length) { $("mbVtx").innerHTML = B.per ? `<span class="mute">${B.per.length} điểm · bấm một điểm trên hình</span>` : '<span class="mute">layer cần là mesh và đã Bind</span>'; return }
    $("mbFixInfo").textContent = B.dirty ? "chưa lưu" : "";
    const agg = {};
    for (const i of B.sel) for (const [k, w] of Object.entries(B.per[i])) agg[k] = (agg[k] || 0) + w / B.sel.length;
    const keep = document.activeElement?.dataset?.b;   // đang kéo thanh của xương này: chỉ cập nhật số các thanh khác
    if (keep && $("mbVtx").querySelector(`[data-b="${keep}"]`)) {
      $("mbVtx").querySelectorAll("input[data-b]").forEach(el => { if (el !== document.activeElement) el.value = ((agg[el.dataset.b] || 0) * 100).toFixed(0) });
      return;
    }
    // 2026-11-03: hiện đủ mọi xương đang bind (xương chưa có ở điểm chọn = 0%), kéo thanh nào là gán xương đó cho cả nhóm điểm
    for (const n of boundNames()) agg[n] ??= 0;
    $("mbVtx").innerHTML = `<span class="mute">${B.sel.length} điểm đang chọn</span>` + Object.entries(agg).sort((x, y) => y[1] - x[1] || x[0].localeCompare(y[0])).map(([n, w]) =>
      `<div class="mbw"><span class="sw" style="background:${css(bIdx(n))}"></span><span title="${n}">${n}</span>
        <input type="number" min="0" max="100" step="1" value="${(w * 100).toFixed(0)}" data-b="${n}">${w > 0 ? `<b data-rm="${n}" title="Bỏ xương này khỏi điểm">✕</b>` : "<span></span>"}
        <input type="range" min="0" max="100" step="1" value="${(w * 100).toFixed(0)}" data-b="${n}" style="grid-column:2/4"></div>`).join("");
  }
  function render() {
    const s = slotObj(), a = att(), sk = player?.skeleton;
    $("mbLayer").textContent = s ? "Layer: " + s.data.name : "Bấm chọn một layer ảnh trên hình";
    $("mbType").textContent = a ? (isMesh(a) ? (a.bones ? " · mesh có weight" : " · mesh") : " · ảnh thường") + " · cha: " + s.bone.data.name : "";
    if (!sk) return;
    meshInfo();
    if (B.m === "bind") {
      const bound = boundNames(), all = [...new Set([...bound, ...B.pick])];
      const xb = n => `<b class="mbx" data-x="${n}" title="${bound.includes(n) ? "Huỷ bind " + n + " (weight chia sang các xương còn lại)" : "Bỏ chọn " + n}">✕</b>`;
      $("mbChips").innerHTML = all.length ? all.map(n => chip(n, (B.chip === n ? "sel " : "") + (bound.includes(n) ? "" : "new")).replace(/<\/span>$/, xb(n) + "</span>")).join("")
        : '<span class="mute">chưa chọn xương</span>';
    }
    if (B.m === "fix") {
      if (!B.per || B.slot !== s?.data.name) loadPer();
      $("mbFixBones").innerHTML = boundNames().map(n => chip(n, n === B.focus ? "sel" : "")).join("") || '<span class="mute">layer chưa bind</span>';
      renderVtx();
    }
  }
  $("mbChips").onclick = ev => {
    const x = ev.target.closest(".mbx"); if (x) { ev.stopPropagation(); return unbind(x.dataset.x) }
    const r = ev.target.closest(".mbc"); if (r) { B.chip = B.chip === r.dataset.b ? null : r.dataset.b; render() }
  };
  $("mbFixBones").onclick = ev => { const r = ev.target.closest(".mbc"); if (r) { B.focus = B.focus === r.dataset.b ? null : r.dataset.b; render() } };
  $("mbVtx").addEventListener("input", ev => { const b = ev.target.dataset?.b; if (!b) return; const v = +ev.target.value; ev.target.parentElement.querySelectorAll(`input[data-b="${b}"]`).forEach(x => { if (x !== ev.target) x.value = v }); setW(b, v) });
  $("mbVtx").addEventListener("click", ev => { const r = ev.target.dataset?.rm; if (r) removeBone(r) });

  // ================= chuột / phím trên khung xem =================
  function segD(p, a, b) { const dx = b[0] - a[0], dy = b[1] - a[1], L2 = dx * dx + dy * dy, t = L2 ? Math.max(0, Math.min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2)) : 0; return Math.hypot(p[0] - a[0] - dx * t, p[1] - a[1] - dy * t) }
  const tip = b => [b.worldX + (b.data.length || 0) * b.a, b.worldY + (b.data.length || 0) * b.c];
  const onStage = ev => $("stage").contains(ev.target) && !ev.target.closest("#edPanel,#verPanel,#helpPop,#claude,button,select,input,textarea");
  function inPoly(pt, P) { let c = false; for (let i = 0, j = P.length - 1; i < P.length; j = i++) if ((P[i][1] > pt[1]) !== (P[j][1] > pt[1]) && pt[0] < (P[j][0] - P[i][0]) * (pt[1] - P[i][1]) / (P[j][1] - P[i][1]) + P[i][0]) c = !c; return c }
  // Vị trí thế giới của các điểm lưới đang sửa (viền rồi tới trong). Lưới có weight bị bone setup / frame kéo lệch khỏi ảnh gốc,
  // nên affine cứng (E.A) không khớp mesh đang vẽ (viền xanh lá): lấy đỉnh thật của attachment, cộng phần người dùng vừa dời / sửa.
  function meshWorld() {
    const q = [...E.hull, ...E.inner], P = q.map(p => app(E.A, p)), s = slotObj(), a = att();
    if (!s || !a || !isMesh(a) || E.preview || a.regionUVs.length / 2 !== q.length) return P;
    const v = worldVerts(s, a);
    return P.map((p, i) => { const u = app(E.A, [a.regionUVs[2 * i] * E.w, a.regionUVs[2 * i + 1] * E.h]); return [v[2 * i] + p[0] - u[0], v[2 * i + 1] + p[1] - u[1]] });
  }
  function meshHit(w, px) {
    let best = null, bd = 10 * px;
    const P = meshWorld(), nh = E.hull.length;
    P.forEach((p, k) => { const d = Math.hypot(p[0] - w[0], p[1] - w[1]); if (d < bd) { bd = d; best = k < nh ? { list: "hull", i: k } : { list: "inner", i: k - nh } } });
    return best;
  }
  addEventListener("pointerdown", ev => {
    if (!active() || ev.button !== 0 || ev.altKey || !onStage(ev) || !player) return;
    const v = toWorld(ev), w = [v.x, v.y], px = pxWorld(player);
    if (B.m === "mesh") {
      if (!E.slot || !E.A || E.slot !== ed.slot || !E.mesh || E.saving) return;
      const hit = meshHit(w, px), q = app(E.Ai, w);
      if (E.tool === "del") {
        if (!hit) return;
        ev.stopImmediatePropagation(); ev.preventDefault();
        if (hit.list === "hull" && E.hull.length <= 3) return setStatus("viền cần ít nhất 3 điểm", "bad");
        edit(() => E[hit.list].splice(hit.i, 1)); return;
      }
      if (hit) {
        ev.stopImmediatePropagation(); ev.preventDefault();
        const dp = meshWorld()[hit.list === "hull" ? hit.i : E.hull.length + hit.i];   // giữ khoảng lệch giữa con trỏ và điểm đang vẽ
        E.drag = { ...hit, moved: false, off: [w[0] - dp[0], w[1] - dp[1]], snap: JSON.stringify([E.hull, E.inner, E.mesh]) }; E.sel = hit;
        try { $("stage").setPointerCapture(ev.pointerId) } catch {} return;
      }
      if (E.tool !== "add") return;
      ev.stopImmediatePropagation(); ev.preventDefault();
      q[0] = Math.max(0, Math.min(E.w, q[0])); q[1] = Math.max(0, Math.min(E.h, q[1]));
      let ei = -1, near = 10 * px;
      const MW = meshWorld();
      E.hull.forEach((a, i) => { const d = segD(w, MW[i], MW[(i + 1) % E.hull.length]); if (d < near) { near = d; ei = i } });
      if (ei < 0 && !inPoly(q, E.hull)) { let bd = Infinity; E.hull.forEach((a, i) => { const d = segD(w, MW[i], MW[(i + 1) % E.hull.length]); if (d < bd) { bd = d; ei = i } }) }
      if (ei >= 0) edit(() => E.hull.splice(ei + 1, 0, q)); else edit(() => E.inner.push(q));
      return;
    }
    if (B.m === "bind") {
      let best = null, bd = 12 * px;
      for (const b of player.skeleton.bones) { if (!b.active) continue; const d = segD(w, [b.worldX, b.worldY], tip(b)); if (d < bd) { bd = d; best = b } }
      if (!best) return;
      ev.stopImmediatePropagation(); ev.preventDefault();
      const bn = best.data.name;
      if (att()?.bones && boundNames().includes(bn)) B.chip = B.chip === bn ? null : bn;   // đã bind: chỉ làm sáng tên (✕ để huỷ)
      else { B.pick = toggle(B.pick, bn, true); B.chip = null }
      render(); return;
    }
    if (B.m === "fix" && B.per && slotObj()) {
      const wv = worldVerts(slotObj(), att()); let best = -1, bd = 12 * px;
      for (let i = 0; i < wv.length; i += 2) { const d = Math.hypot(wv[i] - w[0], wv[i + 1] - w[1]); if (d < bd) { bd = d; best = i / 2 } }
      if (best < 0) return;
      ev.stopImmediatePropagation(); ev.preventDefault();
      B.sel = toggle(B.sel, best, ev.ctrlKey || ev.metaKey); if (!B.sel.length) B.sel = [best]; render();
    }
  }, true);
  // Quét chọn điểm (2026-11-03, người dùng: "chọn nhiều point bằng cách nhấn chuột giữa và quét"): Fix Weight, giữ chuột giữa
  // kéo khung; Shift = thêm vào chọn, Ctrl = bớt. Ngoài Fix Weight chuột giữa vẫn dời khung nhìn (chuột phải / Alt + kéo luôn dời).
  const boxOn = ev => active() && B.m === "fix" && ev.button === 1 && onStage(ev) && !!player && !!B.per && !!slotObj();
  addEventListener("mousedown", ev => { if (boxOn(ev)) ev.preventDefault() }, true);   // chặn cuộn tự động của chuột giữa
  addEventListener("pointerdown", ev => {
    if (!boxOn(ev)) return;
    ev.stopImmediatePropagation(); ev.preventDefault();
    const v = toWorld(ev);
    B.box = { x0: v.x, y0: v.y, x1: v.x, y1: v.y, op: ev.shiftKey ? "add" : (ev.ctrlKey || ev.metaKey) ? "sub" : "set" };
    try { $("stage").setPointerCapture(ev.pointerId) } catch {}
  }, true);
  addEventListener("pointermove", ev => {
    if (!B.box) return;
    ev.stopImmediatePropagation();
    const v = toWorld(ev); B.box.x1 = v.x; B.box.y1 = v.y;
  }, true);
  for (const t of ["pointerup", "pointercancel"]) addEventListener(t, ev => {
    if (!B.box) return;
    ev.stopImmediatePropagation();
    const b = B.box; B.box = null;
    const s = slotObj(), a = att(); if (!s || !isMesh(a) || !B.per) return;
    const x0 = Math.min(b.x0, b.x1), x1 = Math.max(b.x0, b.x1), y0 = Math.min(b.y0, b.y1), y1 = Math.max(b.y0, b.y1);
    const wv = worldVerts(s, a), hit = [];
    for (let i = 0; i < wv.length; i += 2) if (wv[i] >= x0 && wv[i] <= x1 && wv[i + 1] >= y0 && wv[i + 1] <= y1) hit.push(i / 2);
    const cur = new Set(b.op === "set" ? [] : B.sel);
    for (const i of hit) b.op === "sub" ? cur.delete(i) : cur.add(i);
    B.sel = [...cur].sort((p, q) => p - q); render();
    setStatus(`quét ${hit.length} điểm · đang chọn ${B.sel.length} điểm`, "ok");
  }, true);
  addEventListener("pointermove", ev => {
    if (!E.drag) return;
    ev.stopImmediatePropagation();
    const v = toWorld(ev), o = E.drag.off || [0, 0], q = app(E.Ai, [v.x - o[0], v.y - o[1]]);
    E[E.drag.list][E.drag.i] = [Math.max(0, Math.min(E.w, q[0])), Math.max(0, Math.min(E.h, q[1]))];
    E.drag.moved = true;
  }, true);
  for (const t of ["pointerup", "pointercancel"]) addEventListener(t, ev => {
    if (!E.drag) return;
    ev.stopImmediatePropagation();
    const d = E.drag; E.drag = null;
    if (!d.moved) return;
    E.undo.push(d.snap); if (E.undo.length > 100) E.undo.shift();
    retri(); meshInfo();
    if (E.preview) { ed.dirty.add("__mesh"); return }
    clearTimeout(E.saveT); E.saveT = setTimeout(() => writeMesh("đã dời điểm"), 400);
  }, true);
  addEventListener("keydown", ev => {   // Fix Weight: Ctrl+A chọn hết điểm, Esc bỏ chọn
    if (!active() || B.m !== "fix" || !B.per) return;
    const el = document.activeElement;
    if (el && (el.tagName === "TEXTAREA" || el.tagName === "INPUT" || el.tagName === "SELECT")) return;
    if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "a") { ev.stopImmediatePropagation(); ev.preventDefault(); B.sel = [...B.per.keys()]; render() }
    else if (ev.key === "Escape" && B.sel.length) { ev.stopImmediatePropagation(); ev.preventDefault(); B.sel = []; render() }
  }, true);
  addEventListener("keydown", ev => {
    if (!active() || B.m !== "mesh") return;
    const el = document.activeElement;   // đang gõ chữ / số thì để ô nhập nhận phím (thanh trượt thì không)
    if (el && (el.tagName === "TEXTAREA" || (el.tagName === "INPUT" && el.type !== "range" && el.type !== "checkbox") || el.tagName === "SELECT")) return;
    const k = ev.key.toLowerCase();
    if ((ev.ctrlKey || ev.metaKey) && k === "z" && !ev.shiftKey) { if (undoMesh()) { ev.stopImmediatePropagation(); ev.preventDefault() } return }
    if (ev.ctrlKey || ev.metaKey || ev.altKey) return;
    if (E.mesh && (k === "a" || k === "d" || k === "v")) { ev.stopImmediatePropagation(); ev.preventDefault(); setTool({ a: "add", d: "del", v: "move" }[k]) }
    if ((k === "delete" || k === "backspace") && E.sel && E.mesh) { ev.stopImmediatePropagation(); ev.preventDefault(); const h = E.sel; E.sel = null; edit(() => E[h.list].splice(h.i, 1)) }
  }, true);

  // ================= lớp vẽ trên khung xem (gọi trong overlay của index.html) =================
  function pie(sr, x, y, r, parts) {   // điểm chia múi theo màu xương / tỉ lệ weight
    let a0 = Math.PI / 2;
    for (const [c, w] of parts) {
      const seg = Math.max(2, Math.ceil(w * 20)), da = w * 2 * Math.PI / seg, col = new spine.Color(c[0], c[1], c[2], 1);
      for (let k = 0; k < seg; k++) { const a1 = a0 + da; sr.triangle(true, x, y, x + Math.cos(a0) * r, y + Math.sin(a0) * r, x + Math.cos(a1) * r, y + Math.sin(a1) * r, col, col, col); a0 = a1 }
    }
  }
  function vColor(sk, d) { let r = 0, g = 0, b = 0; for (const [n, w] of Object.entries(d)) { const c = rgb(sk.findBone(n).data.index); r += c[0] * w; g += c[1] * w; b += c[2] * w } return [Math.min(1, r), Math.min(1, g), Math.min(1, b)] }
  // Isolate (2026-11-03): tích = chỉ hiện layer đang sửa (alpha slot khác = 0 mỗi khung, như ẩn tạm của cửa sổ Cây),
  // bỏ chọn layer (bấm chỗ trống), bỏ tích hoặc đóng Mesh / Bind = hiện lại. Không đụng layer người dùng ẩn bằng 👁.
  const iso = new Set();
  function isolate(p) {
    const on = active() && $("mbIso").checked && !!ed.slot && !!p.skeleton.findSlot(ed.slot);
    const userHidden = window.spineSel?.S?.hidden || new Set();
    for (const s of p.skeleton.slots) {
      const n = s.data.name;
      if (on && n !== ed.slot) { if (!iso.has(n)) iso.add(n); s.color.a = 0 }
      else if (iso.has(n)) { iso.delete(n); if (!userHidden.has(n)) s.color.a = s.data.color.a }
    }
  }
  $("mbIso").onchange = () => { store.set("mbIso", $("mbIso").checked ? "1" : ""); if (player) isolate(player) };
  $("mbIso").checked = store.get("mbIso", "") === "1";
  function draw(p, sr, px) {
    isolate(p);
    if (!active()) return;
    const sk = p.skeleton, s = slotObj(), a = s?.getAttachment();
    if (B.m === "mesh") {
      if (!E.slot || !E.A || E.slot !== s?.data.name) return;
      if (mode !== "setup" && !E.drag) calcAffine();   // tab Animate: lưới đi theo tư thế frame đang xem
      const P = meshWorld(), nh = E.hull.length;
      const tc = new spine.Color(0.3, 0.85, 1, E.mesh ? 0.6 : 0.3), hc = E.preview ? new spine.Color(1, 0.9, 0.2, 1) : new spine.Color(1, 0.6, 0.1, 1);
      for (const t of E.tris) for (const [x, y] of [[t[0], t[1]], [t[1], t[2]], [t[2], t[0]]]) if (P[x] && P[y]) sr.rectLine(true, P[x][0], P[x][1], P[y][0], P[y][1], 1 * px, tc);
      for (let i = 0; i < nh; i++) { const a1 = P[i], b1 = P[(i + 1) % nh]; sr.rectLine(true, a1[0], a1[1], b1[0], b1[1], 2 * px, hc) }
      if (!E.mesh) return;
      P.forEach((q, i) => {
        const hull = i < nh, sel = !!E.sel && (E.sel.list === "hull") === hull && E.sel.i === (hull ? i : i - nh);
        sr.circle(true, q[0], q[1], (sel ? 7 : 5.5) * px, new spine.Color(0, 0, 0, 0.8), 12);
        sr.circle(true, q[0], q[1], (sel ? 5.5 : 4) * px, sel ? new spine.Color(1, 1, 1, 1) : hull ? hc : new spine.Color(1, 0.25, 0.25, 1), 12);
      });
      return;
    }
    const only = B.m === "fix" ? new Set(boundNames()) : null, bnd = new Set(B.m === "bind" && a && a.bones ? boundNames() : []);
    for (const b of sk.bones) {   // Bind: mọi xương (xương chọn đậm); Fix Weight: chỉ xương đã bind
      if (!b.active || (only && !only.has(b.data.name))) continue;
      const c = rgb(b.data.index), on = B.m === "bind" ? (B.pick.includes(b.data.name) || bnd.has(b.data.name)) : (!B.focus || b.data.name === B.focus), t = tip(b);
      const col = new spine.Color(c[0], c[1], c[2], on ? 1 : 0.45);
      if (b.data.length) { sr.rectLine(true, b.worldX, b.worldY, t[0], t[1], (on ? 7 : 4) * px, new spine.Color(0, 0, 0, 0.5)); sr.rectLine(true, b.worldX, b.worldY, t[0], t[1], (on ? 5 : 2.5) * px, col) }
      sr.circle(true, b.worldX, b.worldY, (on ? 6 : 4) * px, col, 12);
    }
    if (!isMesh(a)) return;
    const w = worldVerts(s, a), tri = a.triangles;
    // weight theo đỉnh: bản đang sửa (Fix Weight) hoặc đọc từ attachment
    let per = B.m === "fix" && B.per && B.slot === s.data.name ? B.per : null;
    if (!per) { const r = readPer(); per = r ? r.per : null }
    if (!per) return;
    const focus = B.m === "fix" ? B.focus : null;
    // 2026-10-31: không tô màu lưới (phủ mờ khó nhìn điểm), chỉ cạnh lưới thật nhạt + viền ngoài nhẹ; màu weight nằm ở điểm
    const edge = new spine.Color(1, 1, 1, 0.12), hullC = new spine.Color(1, 1, 1, 0.55), nh = (a.hullLength || 0) / 2;
    for (let i = 0; i < tri.length; i += 3) for (const [x, y] of [[tri[i], tri[i + 1]], [tri[i + 1], tri[i + 2]], [tri[i + 2], tri[i]]]) sr.rectLine(true, w[x * 2], w[x * 2 + 1], w[y * 2], w[y * 2 + 1], 0.8 * px, edge);
    for (let i = 0; i < nh; i++) { const j = (i + 1) % nh; sr.rectLine(true, w[i * 2], w[i * 2 + 1], w[j * 2], w[j * 2 + 1], 1.5 * px, hullC) }
    const R = 8 * px;
    for (let i = 0; i < w.length / 2; i++) {   // điểm = bánh chia múi theo màu các xương đang bind (tỉ lệ = weight)
      const on = B.sel.includes(i), x = w[i * 2], y = w[i * 2 + 1];
      sr.circle(true, x, y, (on ? R + 3.5 * px : R + 1.5 * px), on ? new spine.Color(1, 1, 1, 1) : new spine.Color(0, 0, 0, 0.85), 18);
      // đang chọn một xương (bấm ô tên): múi của xương đó sáng rõ, các múi khác tối đi; vẫn là bánh nhiều màu
      pie(sr, x, y, R, Object.entries(per[i]).sort((a, b) => b[1] - a[1]).map(([n, ww]) => {
        const c = rgb(bIdx(n)), k = !focus || n === focus ? 1 : 0.3;
        return [[c[0] * k, c[1] * k, c[2] * k], ww];
      }));
    }
    if (B.box) {   // khung quét chọn (chuột giữa): trắng = chọn mới, xanh = thêm, đỏ = bớt
      const b = B.box, c = b.op === "add" ? new spine.Color(0.3, 0.9, 1, 1) : b.op === "sub" ? new spine.Color(1, 0.35, 0.35, 1) : new spine.Color(1, 1, 1, 1);
      const P = [[b.x0, b.y0], [b.x1, b.y0], [b.x1, b.y1], [b.x0, b.y1]];
      for (let i = 0; i < 4; i++) { const p = P[i], q = P[(i + 1) % 4]; sr.rectLine(true, p[0], p[1], q[0], q[1], 1.5 * px, c) }
    }
  }
  let last = "";
  setInterval(() => {
    if (!player) return;
    const sig = ed.slot + "|" + active() + "|" + B.m;
    if (sig === last) return;
    last = sig;
    if (B.dirty && B.slot !== ed.slot) { B.dirty = false; ed.dirty.delete("__weights") }
    if (E.preview && E.slot !== ed.slot) { E.preview = false; ed.dirty.delete("__mesh"); setStatus("bỏ kết quả trace chưa Áp dụng của " + E.slot, "") }
    if (active() && player && !player.paused) player.pause();
    if (active()) { if (B.m === "mesh") loadMesh(); if (B.m === "bind") { B.pick = []; B.chip = null } if (B.m === "fix") loadPer() }
    render();
  }, 200);
  setTool(E.tool); setM(B.m);
  window.spineMB = { draw, B, E, setM, meshWorld, grabs: () => active() };
})();
