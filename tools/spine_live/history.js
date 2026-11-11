// Tab History cạnh phải (2026-11-04, người dùng: "tạo thêm 1 tab history cạnh phải tương tự như properties có thể ẩn vào trong,
// trong đó là history chỉnh sửa như photoshop và có thể nhấn vào đấy để back lại (toàn bộ chỉnh sửa: key, pose, mesh, weight...)").
// Dữ liệu = sổ Hoàn tác / Làm lại của server (mỗi lần ghi file: Key, curve, lưới, weight, setup, Claude gen...; GET /api/spine/history,
// biến chung `hist` của index.html). Dòng trên cùng "Mở đầu" = trạng thái trước lần ghi cũ nhất còn giữ; mỗi dòng sau = trạng thái
// SAU lần ghi đó; dòng sáng = đang ở đây; các dòng mờ phía dưới = đã lùi qua (Làm lại được), như Photoshop: bấm dòng mờ là tới,
// sửa mới thì các dòng mờ mất. Bấm một dòng: POST /api/spine/history/goto {undo: n | redo: n}.
// Dùng biến chung: hist, histLoad, histLabel, cur, ed, store, edPost, build, snapshot, stamp, setStatus, $.
(() => {
  const panel = document.createElement("aside");
  panel.id = "histPanel";
  panel.innerHTML = `<div id="histHead"><b>History</b><span id="histCount"></span>
      <button id="histFold" title="Thu tab History vào cạnh phải">⟩</button></div><div id="histList"></div>`;
  document.querySelector("main").appendChild(panel);
  const tab = document.createElement("button");
  tab.id = "histTab"; tab.textContent = "◀ History"; tab.title = "Mở lại tab History"; tab.hidden = true;
  document.querySelector("main").appendChild(tab);
  const st = document.createElement("style");
  st.textContent = `#histPanel{position:absolute;top:12px;right:12px;width:260px;max-height:min(60%,520px);z-index:6;display:flex;flex-direction:column;
      background:var(--raise);border:1px solid var(--line);border-radius:8px;box-shadow:0 2px 10px #0004;font-size:11px;overflow:hidden}
    #histPanel.folded{display:none}
    #histHead{display:flex;gap:6px;align-items:center;padding:6px 8px;border-bottom:1px solid var(--line)} #histHead b{flex:1}
    #histCount{color:var(--mute)} #histFold{padding:0 6px}
    #histList{overflow:auto;padding:4px 0}
    .hrow{display:flex;gap:6px;align-items:center;padding:3px 8px;cursor:pointer;white-space:nowrap}
    .hrow:hover{background:var(--panel)} .hrow .ic{width:16px;text-align:center;opacity:.85} .hrow .nm{flex:1;overflow:hidden;text-overflow:ellipsis}
    .hrow .tm{color:var(--mute);font-size:10px} .hrow.cur{background:color-mix(in srgb,var(--accent) 28%,transparent);font-weight:600}
    .hrow.fut{opacity:.42} .hrow.cl .nm{color:#b48cff}
    #histTab{position:absolute;right:0;top:62%;z-index:6;writing-mode:vertical-rl;padding:10px 4px;border-radius:8px 0 0 8px;border-right:0}`;
  document.head.appendChild(st);

  const H = { sig: "", busy: false };
  const fold = on => { panel.classList.toggle("folded", on); tab.hidden = !on; store.set("histFold", on ? "1" : "0") };
  $("histFold").onclick = () => fold(true);
  tab.onclick = () => fold(false);
  fold(store.get("histFold", "0") === "1");

  const esc = t => String(t || "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  function icon(e) {
    const w = (e.what || "").toLowerCase();
    if (e.who === "claude") return "✦";
    if (/hoàn tác|làm lại|lịch sử|về bản/.test(w)) return "↶";
    if (/key|keypose|dán|paste/.test(w)) return "◆";
    if (/curve|graph|tay cầm/.test(w)) return "〰";
    if (/lưới|mesh|trace|remesh/.test(w)) return "▦";
    if (/weight|bind/.test(w)) return "⚖";
    if (/setup|parent|ảnh|attachment/.test(w)) return "⚙";
    if (/anim/.test(w)) return "🎞";
    return "•";
  }
  // vị trí mặc định (chưa kéo lần nào, float.js): ngay dưới Properties ở cạnh phải (2026-11-04: đặt cạnh trái Properties che hình
  // quá nhiều); Properties cao quá (đang mở công cụ) không còn chỗ thì sang cạnh trái Properties; Properties thu / ẩn: góc phải trên
  function place() {
    if (panel.dataset.moved) return;
    const ep = $("edPanel"), H = document.querySelector("main").clientHeight;
    const s = panel.style; s.left = ""; s.right = "12px";
    if (!ep || ep.hidden || ep.classList.contains("docked")) { s.top = "12px"; s.maxHeight = "min(60%,520px)"; return }
    const below = ep.offsetTop + ep.offsetHeight + 8, room = H - below - 12;
    if (room >= 160) { s.top = below + "px"; s.maxHeight = Math.min(room, 520) + "px"; s.right = (parseFloat(getComputedStyle(ep).right) || 12) + "px" }
    else { s.top = "12px"; s.maxHeight = "min(60%,520px)"; s.right = (ep.offsetWidth + 24) + "px" }
  }
  function rows() {
    const u = hist.data.undo || [], r = hist.data.redo || [], n = u.length, out = [];
    out.push({ label: "Mở đầu", ic: "▣", undo: n, cur: n === 0, t: u[n - 1]?.t });
    for (let j = 0; j < n; j++) { const e = u[n - 1 - j]; out.push({ e, undo: n - 1 - j, cur: j === n - 1 }) }
    for (let k = 0; k < r.length; k++) out.push({ e: r[k], redo: k + 1, fut: true });
    return out;
  }
  function render() {
    place();
    if (!cur) return;
    const u = hist.data.undo || [], r = hist.data.redo || [];
    const sig = cur.json + "|" + u.map(e => e.t + e.what).join(",") + "|" + r.map(e => e.t + e.what).join(",");
    if (sig === H.sig) return; H.sig = sig;
    const rs = rows();
    $("histCount").textContent = u.length + r.length ? (u.length + r.length) + " bước" : "";
    $("histList").innerHTML = rs.map((x, i) => {
      const e = x.e, nm = e ? (e.who === "claude" ? "Claude: " : "") + e.what : x.label;
      return `<div class="hrow${x.cur ? " cur" : ""}${x.fut ? " fut" : ""}${e?.who === "claude" ? " cl" : ""}" data-i="${i}"
        title="${esc(nm)} · ${esc(e?.t || "")}\n${x.cur ? "đang ở đây" : x.fut ? "bấm: làm lại tới bước này" : "bấm: lùi về trạng thái sau bước này"}">
        <span class="ic">${x.ic || icon(e)}</span><span class="nm">${esc(nm)}</span><span class="tm">${esc((e?.t || "").slice(11, 16))}</span></div>`;
    }).join("");
    const curRow = $("histList").querySelector(".hrow.cur"); curRow?.scrollIntoView({ block: "nearest" });
    $("histList").querySelectorAll(".hrow").forEach(el => el.onclick = () => go(rs[+el.dataset.i]));
  }
  async function go(x) {
    if (!x || x.cur || H.busy || !cur) return;
    if (ed.dirty.size) return setStatus("đang sửa dở: Key pose hoặc Bỏ sửa trước khi đổi bước lịch sử", "bad");
    const body = x.fut ? { json: cur.json, redo: x.redo } : { json: cur.json, undo: x.undo };
    if (!body.undo && !body.redo) return;
    H.busy = true;
    try {
      await edPost("/api/spine/history/goto", body);
      ed.dirty.clear(); stamp = null; build(snapshot()); await histLoad(); H.sig = ""; render();
      setStatus(`lịch sử: ${x.fut ? "tới" : "lùi"} ${body.undo || body.redo} bước → ${x.e ? x.e.what : "mở đầu"} (bấm dòng khác để đổi; sửa mới thì các bước mờ mất)`, "ok");
    } catch (e) { setStatus("đổi bước lịch sử lỗi: " + e.message, "bad") }
    H.busy = false;
  }
  setInterval(() => { if (!document.hidden) render() }, 400);
  window.spineHistory = { render, H };
})();
