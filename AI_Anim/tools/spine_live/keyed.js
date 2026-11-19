// Keypose đã sửa: frame người dùng đã Key pose trên Spine Live (server ghi sổ work/store/_sys/spine_live/keyed.json,
// Hoàn tác key thì gỡ đúng lần đó). Timeline tô nổi các frame này (cam; bỏ tích = mờ).
// Gen gửi Claude hai danh sách: các key đã keypose lại + các keypose được tích để gen tiếp (vd walk cycle sửa F1, F4, F12).
(() => {
  const K = { data: {}, json: null, off: new Set(), sig: "" };
  const offKey = f => (cur?.json || "") + "|" + curAnim() + "|" + f;
  // keypose đã dùng để gen (used, do spine_live_cmd note-done đặt) ẩn khỏi danh sách + timeline; Hoàn tác bản gen thì hiện lại
  const list = () => ((cur && K.json === cur.json && K.data[curAnim()]) || []).filter(e => !e.used);
  const frames = () => list().map(e => e.frame);
  const isOn = f => !K.off.has(offKey(f));
  const checked = () => frames().filter(isOn);

  async function load() {
    if (!cur) return;
    try { K.data = await (await fetch("/api/spine/keyed?json=" + encodeURIComponent(cur.json))).json(); K.json = cur.json } catch {}
    K.sig = ""; render();
  }
  function render() {
    const box = $("genKeys"); if (!box) return;
    const L = list(), sig = [cur?.json, curAnim(), L.map(e => e.frame + ":" + isOn(e.frame) + ":" + e.t).join(","), curFrame(), ed.dirty.size].join("|");
    if (sig === K.sig) return; K.sig = sig;
    box.innerHTML = L.length ? L.map(e => `<label class="gk ${isOn(e.frame) ? "on" : ""}" title="Key lúc ${e.t} · ${e.bones.length} xương: ${e.bones.join(", ")}">`
      + `<input type="checkbox" data-f="${e.frame}" ${isOn(e.frame) ? "checked" : ""}><span data-seek="${e.frame}">F${e.frame}</span>`
      + `<b class="gkx" data-del="${e.frame}" title="Xoá keypose F${e.frame}: xoá key thật của ${e.bones.join(", ")} ở frame này (Hoàn tác được)">✕</b></label>`).join("")
      : '<span style="color:var(--mute)">chưa có frame nào được Key pose trong anim này</span>';
    box.querySelectorAll("input[data-f]").forEach(i => i.onchange = () => {
      const k = offKey(+i.dataset.f); i.checked ? K.off.delete(k) : K.off.add(k); render() });
    box.querySelectorAll("[data-del]").forEach(x => x.onclick = async ev => {
      ev.preventDefault(); ev.stopPropagation();
      if (ed.dirty.size) return setStatus("đang sửa dở: Key pose hoặc Bỏ sửa trước", "bad");
      const f = +x.dataset.del;
      try {
        const j = await edPost("/api/spine/keyed/delete", { json: cur.json, anim: curAnim(), frame: f });
        await animReloadLive(curAnim());
        setStatus("đã xoá keypose F" + f + " (" + j.removed + " key) · Ctrl+Z lấy lại", "ok");
      } catch (e) { setStatus("xoá keypose lỗi: " + e.message, "bad") }
    });
    box.querySelectorAll("[data-seek]").forEach(s => s.onclick = ev => {
      ev.preventDefault(); if (tlBlocked()) return; seekTime(+s.dataset.seek / fpsOf()) });
    const n = checked().length, f = curFrame(), withCur = ed.dirty.size && !frames().includes(f);
    $("genInfo").textContent = L.length ? " " + n + " / " + L.length + " đã tích" : "";
    $("edGen").textContent = n || withCur ? "Gen từ " + (n + (withCur ? 1 : 0)) + " keypose đã tích (Claude)" : "Gen tiếp từ frame này (Claude)";
  }
  setInterval(() => { try { render() } catch {} }, 400);
  $("genAll").onclick = () => { for (const f of frames()) K.off.delete(offKey(f)); render() };
  $("genClear").onclick = async () => {
    if (!cur || !list().length || !confirm("Xoá đánh dấu " + list().length + " keypose của anim " + curAnim() + "? (không sửa file anim)")) return;
    try { await edPost("/api/spine/keyed/clear", { json: cur.json, anim: curAnim() }); load(); setStatus("đã xoá đánh dấu keypose", "ok") }
    catch (e) { setStatus("xoá đánh dấu lỗi: " + e.message, "bad") }
  };
  // timeline: "under" = cột tô sau thước, "over" = dấu cam trên hàng key
  function tlPaint(g, X, f0, f1, H, layer) {
    const ppf = tl.ppf;
    for (const e of list()) {
      const f = e.frame; if (f < f0 - 1 || f > f1 + 1) continue;
      const on = isOn(f), x = X(f);
      if (layer === "under") {
        const w = Math.max(6, ppf);
        g.fillStyle = on ? "rgba(255,122,40,0.28)" : "rgba(255,122,40,0.10)"; g.fillRect(x - w / 2, 0, w, H);
        g.strokeStyle = on ? "#ff7a28" : "#ff7a2870"; g.lineWidth = 2; g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); g.lineWidth = 1;
      } else {
        const y = H - 11, s = on ? 7 : 5;
        g.fillStyle = "#fff"; g.beginPath(); g.moveTo(x, y - s - 1.5); g.lineTo(x + s + 1.5, y); g.lineTo(x, y + s + 1.5); g.lineTo(x - s - 1.5, y); g.closePath(); g.fill();
        g.fillStyle = on ? "#ff7a28" : "#ff7a2899"; g.beginPath(); g.moveTo(x, y - s); g.lineTo(x + s, y); g.lineTo(x, y + s); g.lineTo(x - s, y); g.closePath(); g.fill();
      }
    }
  }
  window.spineKeyed = { load, list, frames, checked, isOn, render, tlPaint };
})();
