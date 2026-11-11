// Cột phiên bản bên trái (người dùng 2026-10-30: "thêm cạnh trái sẽ là preview các version đã gen (có thể ẩn), có thể click vào
// các version và tiếp tục gen từ bản click đó, sau đó sẽ thành bản mới nhất (không xóa bản ở giữa 2 bản)").
// Server chụp phiên bản khi AI ghi file (Claude gen) / file đổi ngoài Spine Live / nút Update; sửa tay chỉ vào tab History (2026-11-04). Bấm một bản = về bản đó (2026-10-31: không
// tạo bản mới; ô bản đó sáng xanh; sửa tiếp thì bản mới nối cuối danh sách). Ctrl+Z lùi được. Ảnh nhỏ: trang chụp khung xem (chỉ skeleton) của bản
// đang là file khi bản đó chưa có ảnh. Dùng biến chung: player, cur, ed, store, edPost, build, snapshot, stamp, setStatus, $.
(() => {
  const VS = { data: { head: null, versions: [] }, json: null, need: false, shotAt: 0, sig: "" };
  const panel = document.createElement("aside");
  panel.id = "verPanel";
  panel.innerHTML = `<div id="verHead"><b>Phiên bản</b><span id="verCount"></span><button id="verFold" title="Ẩn / hiện cột phiên bản">◀</button></div>
    <div id="verList"></div>`;
  document.querySelector("main").appendChild(panel);
  const st = document.createElement("style");
  st.textContent = `#verPanel{position:absolute;left:16px;top:56px;width:178px;max-height:calc(100% - 120px);z-index:4;display:flex;flex-direction:column;
      background:var(--raise);border:1px solid var(--line);border-radius:8px;box-shadow:0 2px 10px #0004;font-size:11px;overflow:hidden}
    #verHead{display:flex;gap:6px;align-items:center;padding:6px 8px;border-bottom:1px solid var(--line)} #verHead b{flex:1}
    #verCount{color:var(--mute)} #verFold{padding:0 6px}
    #verList{overflow:auto;padding:6px;display:flex;flex-direction:column;gap:6px}
    .ver{border:1px solid var(--line);border-radius:6px;padding:4px;cursor:pointer;background:var(--panel)}
    .ver:hover{border-color:var(--accent)} .ver.head{border-color:#4caf50;box-shadow:0 0 0 1px #4caf50 inset}
    .ver .th{width:100%;aspect-ratio:4/3;object-fit:contain;background:#0003;border-radius:4px;display:block}
    .ver .nt{display:flex;gap:4px;margin-top:3px} .ver .nt b{color:var(--accent)} .ver .wh{color:var(--mute);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .ver .cl{color:#b48cff} #verPanel.folded{width:auto} #verPanel.folded #verList,#verPanel.folded #verCount{display:none}`;
  document.head.appendChild(st);
  const fold = on => { panel.classList.toggle("folded", on); $("verFold").textContent = on ? "▶ Phiên bản" : "◀"; store.set("verFold", on ? "1" : "0") };
  $("verFold").onclick = () => fold(!panel.classList.contains("folded"));
  fold(store.get("verFold", "0") === "1");

  const esc = t => String(t || "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  async function load() {
    if (!cur) return;
    try { VS.data = await (await fetch("/api/spine/versions?json=" + encodeURIComponent(cur.json), { cache: "no-store" })).json(); VS.json = cur.json } catch { return }
    render();
    const h = VS.data.versions.find(v => v.id === VS.data.head);
    if (h && !h.thumb) VS.need = true;            // bản đang là file chưa có ảnh: chụp ở khung hình kế
  }
  function render() {
    const vs = VS.data.versions || [], sig = cur?.json + "|" + VS.data.head + "|" + vs.map(v => v.id + (v.thumb ? "t" : "")).join(",");
    if (sig === VS.sig) return; VS.sig = sig;
    $("verCount").textContent = vs.length ? vs.length + " bản" : "";
    $("verList").innerHTML = vs.slice().reverse().map(v => `<div class="ver ${v.id === VS.data.head ? "head" : ""}" data-id="${v.id}"
        title="#${v.id} · ${esc(v.t)} · ${esc(v.what)}\nBấm: về bản này (không tạo bản mới; sửa tiếp thì thành bản mới cuối danh sách)">
        ${v.thumb ? `<img class="th" loading="lazy" src="/api/spine/version/thumb?json=${encodeURIComponent(cur.json)}&id=${v.id}&t=${v.thumb ? 1 : 0}">` : '<div class="th"></div>'}
        <div class="nt"><b>#${v.id}</b><span>${esc((v.t || "").slice(11, 16))}</span></div>
        <div class="wh ${v.who === "claude" ? "cl" : ""}">${esc(v.who === "claude" ? "Claude: " : "")}${esc(v.what)}</div></div>`).join("")
      || '<div style="color:var(--mute)">chưa có phiên bản</div>';
    $("verList").querySelectorAll(".ver").forEach(el => el.onclick = () => restore(+el.dataset.id));
  }
  async function restore(id) {
    if (!cur || id === VS.data.head) return;
    if (ed.dirty.size) return setStatus("đang sửa dở: Key pose hoặc Bỏ sửa trước khi đổi phiên bản", "bad");
    try {
      const j = await edPost("/api/spine/version/restore", { json: cur.json, id });
      stamp = null; build(snapshot()); VS.sig = ""; setTimeout(load, 600);
      setStatus("đang ở bản #" + id + " (Ctrl+Z / Hoàn tác để về bản trước đó)", "ok");
    } catch (e) { setStatus("đổi phiên bản lỗi: " + e.message, "bad") }
  }
  // chụp ảnh nhỏ khung xem (gọi ở đầu overlay: skeleton đã vẽ, chưa có lớp xương / lưới)
  function grab(p) {
    if (!VS.need || !cur || VS.json !== cur.json || loading || Date.now() - VS.shotAt < 800) return;
    const head = VS.data.head; if (!head) return;
    VS.need = false; VS.shotAt = Date.now();
    // lúc draw() chạy skeleton chưa flush lên canvas: chụp ở microtask ngay sau khung hình (buffer chưa bị xoá)
    queueMicrotask(() => shot(p, head));
  }
  function shot(p, head) {
    try {
      const src = p.sceneRenderer.canvas, w = 200, h = Math.round(w * 3 / 4);
      const c = document.createElement("canvas"); c.width = w; c.height = h;
      const g = c.getContext("2d"); g.fillStyle = "#2a2e36"; g.fillRect(0, 0, w, h);
      const k = Math.min(w / src.width, h / src.height); const dw = src.width * k, dh = src.height * k;
      g.drawImage(src, (w - dw) / 2, (h - dh) / 2, dw, dh);
      const data = c.toDataURL("image/jpeg", 0.8);
      edPost("/api/spine/version/thumb", { json: cur.json, id: head, data }).then(() => { VS.sig = ""; load() }).catch(() => {});
    } catch {}
  }
  setInterval(() => { if (!document.hidden) load() }, 2000);
  window.spineVersions = { load, grab, VS };
})();
