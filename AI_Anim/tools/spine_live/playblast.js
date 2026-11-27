// Playblast (2026-11-27, người dùng: "tạo công cụ có thể playblast ở spinelive"): quay anim đang xem thành video mp4.
// Vẽ từng frame bằng runtime Spine thật (cầu nối `snap` của bridge.js: đủ IK, mesh, clipping, đổi ảnh slot, không làm phiền player đang xem),
// khung CỐ ĐỊNH theo hợp khung mọi frame đã chọn (video không nhảy), gửi tấm contact sheet lên server (spine_playblast.py)
// cắt ô + đánh số frame + ghép ffmpeg -> <thư mục skeleton>/preview/<anim>_playblast.mp4, xem ngay trong bảng.
// Không ghi vào file skeleton. Dùng biến chung của index.html: cur, curAnim, fpsOf, store, setStatus, hhmmss, $.
(() => {
  const P = { w: +store.get("pbW", "420"), fps: +store.get("pbFps", "30"), loops: +store.get("pbLoops", "1"), bg: store.get("pbBg", "#1c3a5c"),
              burn: store.get("pbBurn", "1") === "1", busy: false, stop: false };
  const box = document.createElement("div");
  box.id = "pbBox"; box.className = "sec tool";
  box.innerHTML = `
    <h3 class="secT">Playblast (quay video) <span id="pbInfo" class="mute" style="font-weight:400"></span></h3>
    <div class="row">
      <label title="Frame đầu">Từ F <input id="pbFrom" type="number" min="0" step="1" style="width:56px"></label>
      <label title="Frame cuối (gồm cả frame này)">Đến F <input id="pbTo" type="number" min="0" step="1" style="width:56px"></label>
      <label title="Lặp lại đoạn này mấy lần trong video (anim loop: 2-3 lần để xem chỗ nối)">Lặp <input id="pbLoops" type="number" min="1" max="10" step="1" style="width:44px">×</label>
    </div>
    <div class="row">
      <label title="Bề ngang video (px); chiều cao tự theo khung của anim">Rộng <input id="pbW" type="number" min="120" max="1200" step="20" style="width:64px"></label>
      <label title="Khung hình / giây">FPS <input id="pbFps" type="number" min="1" max="60" step="1" style="width:48px"></label>
      <label title="Màu nền video (mp4 không có alpha)">Nền <select id="pbBg">
        <option value="#1c3a5c">xanh đậm</option><option value="#303030">xám tối</option><option value="#ffffff">trắng</option><option value="#808080">xám</option><option value="#00b140">xanh lá (key)</option></select></label>
      <label title="Ghi số frame ở góc video"><input type="checkbox" id="pbBurn">Số frame</label>
    </div>
    <div class="row">
      <button id="pbGo" class="primary" title="Quay anim đang xem thành mp4 (không ghi vào file skeleton)">● Quay</button>
      <button id="pbStop" hidden title="Dừng quay">Dừng</button>
      <span id="pbMsg" class="mute"></span>
    </div>
    <div id="pbOut" hidden>
      <video id="pbVid" controls loop playsinline style="width:100%;border-radius:6px;background:#000"></video>
      <div class="row"><a id="pbLink" target="_blank" rel="noopener">Mở video</a><span id="pbPath" class="mute" style="word-break:break-all"></span></div>
    </div>`;
  ($("physBox") || $("noteBox")).after(box);

  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const even = v => Math.max(2, Math.round(v / 2) * 2);
  const msg = (t, bad) => { $("pbMsg").textContent = t; $("pbMsg").style.color = bad ? "var(--bad,#ff6b6b)" : "" };
  const nFrames = () => {   // số frame của anim đang xem
    const a = player?.skeleton?.data.animations.find(x => x.name === curAnim());
    return a ? Math.round(a.duration * fpsOf()) : 0;
  };
  function sync() {
    $("pbInfo").textContent = curAnim() ? "· " + curAnim() + " · " + nFrames() + "F" : "";
    if (P.busy) return;
    const n = nFrames(), key = (cur?.json || "") + "|" + curAnim();
    if (box._key !== key) {   // đổi anim / file: đoạn quay = cả anim
      box._key = key; $("pbFrom").value = 0; $("pbTo").value = n;
    }
  }
  for (const [id, k, t] of [["pbW", "w", "pbW"], ["pbFps", "fps", "pbFps"], ["pbLoops", "loops", "pbLoops"]]) {
    $(id).value = P[k]; $(id).onchange = () => { P[k] = +$(id).value || P[k]; store.set(t, String(P[k])) };
  }
  $("pbBg").value = P.bg; $("pbBg").onchange = () => { P.bg = $("pbBg").value; store.set("pbBg", P.bg) };
  $("pbBurn").checked = P.burn; $("pbBurn").onchange = () => { P.burn = $("pbBurn").checked; store.set("pbBurn", P.burn ? "1" : "0") };
  setInterval(() => { try { sync() } catch {} }, 400);

  async function post(body) {
    const r = await fetch("/api/spine/playblast", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const j = await r.json().catch(() => ({ ok: false, error: "server trả lời lỗi (HTTP " + r.status + ")" }));
    if (!j.ok) throw new Error(j.error || "lỗi playblast");
    return j;
  }
  const snap = async a => {
    const r = await window.spineBridge.OPS.snap(a);
    return r;
  };

  async function record() {
    if (P.busy) return;
    if (!player || !cur?.json) return msg("chưa mở skeleton", true);
    const anim = curAnim(), N = nFrames();
    let f0 = clamp(Math.round(+$("pbFrom").value || 0), 0, N), f1 = clamp(Math.round(+$("pbTo").value || N), 0, N);
    if (f1 < f0) [f0, f1] = [f1, f0];
    const loops = clamp(Math.round(+$("pbLoops").value || 1), 1, 10), fps = clamp(Math.round(+$("pbFps").value || 30), 1, 60);
    const range = []; for (let f = f0; f <= f1; f++) range.push(f);
    const seq = []; for (let i = 0; i < loops; i++) seq.push(...range);
    P.busy = true; P.stop = false; $("pbGo").disabled = true; $("pbStop").hidden = false; $("pbOut").hidden = true;
    let id = null;
    const t0 = performance.now();
    try {
      // 1) khung chung: hợp khung mọi frame (lô 24 frame, ô nhỏ)
      msg("đo khung hình…");
      let box4 = null;
      for (let i = 0; i < range.length; i += 24) {
        const b = (await snap({ json: cur.json, anim, frames: range.slice(i, i + 24), cell: [60, 90], cols: 6, nolabel: true })).box;
        box4 = box4 ? [Math.min(box4[0], b[0]), Math.min(box4[1], b[1]), Math.max(box4[2], b[2]), Math.max(box4[3], b[3])] : b;
        if (P.stop) throw new Error("đã dừng");
      }
      // kích thước ô: rộng = P.w, cao theo tỉ lệ khung (cộng viền 6% mỗi bên như snap), giới hạn 1600 px
      const pad = 1.12, bw = (box4[2] - box4[0]) * pad, bh = (box4[3] - box4[1]) * pad;
      let cw = even(clamp(+$("pbW").value || 420, 120, 1200)), ch = even(cw * bh / Math.max(bw, 1));
      if (ch > 1600) { ch = 1600; cw = even(ch * bw / Math.max(bh, 1)) }
      const cols = clamp(Math.floor(6144 / cw), 1, 6), rows = clamp(Math.floor(6144 / ch), 1, 6), batch = Math.min(24, cols * rows);
      id = (await post({ op: "start", json: cur.json, anim })).id;
      // 2) vẽ + gửi từng lô
      for (let i = 0; i < range.length; i += batch) {
        const fr = range.slice(i, i + batch);
        msg(`vẽ frame ${i + fr.length}/${range.length} (${cw}×${ch})…`);
        const r = await snap({ json: cur.json, anim, frames: fr, cell: [cw, ch], cols, box: box4, nolabel: true, bg: P.bg });
        await post({ op: "frames", id, png: r.png, cols, cw, ch, frames: fr });
        if (P.stop) throw new Error("đã dừng");
      }
      msg("ghép video (ffmpeg)…");
      const res = await post({ op: "finish", id, seq, fps, burn: $("pbBurn").checked }); id = null;
      $("pbOut").hidden = false;
      const url = res.url + "?t=" + Date.now();
      $("pbVid").src = url; $("pbLink").href = url; $("pbPath").textContent = res.video;
      $("pbVid").play().catch(() => {});
      msg(`xong: ${res.frames} frame · ${res.size[0]}×${res.size[1]} · ${(res.bytes / 1e6).toFixed(1)} MB · ${((performance.now() - t0) / 1000).toFixed(1)} s`);
      setStatus(`đã quay playblast ${anim} → ${res.video} · ${hhmmss()}`, "ok");
    } catch (e) {
      msg("lỗi: " + (e?.message || e), e?.message !== "đã dừng");
      if (id) post({ op: "cancel", id }).catch(() => {});
    }
    P.busy = false; $("pbGo").disabled = false; $("pbStop").hidden = true;
  }
  $("pbGo").onclick = record;
  $("pbStop").onclick = () => { P.stop = true; msg("đang dừng…") };
  window.spinePlayblast = { record, P };
})();
