// Cửa sổ nổi kéo được cho Properties + History (2026-11-04, người dùng: "cửa sổ history đang bị che quá nhiều, chuyển properties và
// history thành loại có thể di chuyển tự do được, khi thu lại vẫn thu về cạnh, và xổ ra sẽ ở vị trí gần nhất trước đó").
// Kéo thanh tiêu đề (Properties: dòng "Properties"; History: thanh "History") để dời; vị trí nhớ theo trình duyệt (store "pos.<tên>"),
// luôn giữ trong khung xem. Thu (⟩) vẫn về tab ở cạnh phải như cũ; mở lại về đúng vị trí đã đặt. Chưa kéo lần nào: Properties ở góc
// phải trên, History ngay dưới Properties (history.js đặt). Kéo xong thì chặn cú bấm (tiêu đề Properties bấm là thu / mở mục).
// Lỗi bản đầu (người dùng: "đang lỗi không thể di chuyển ... có thể di chuyển trong mọi lúc mọi tình huống"): bắt đầu kéo đổi class
// -> MutationObserver "mở lại" trả cửa sổ về vị trí cũ và lưu luôn vị trí cũ; trang cũng tự đổi class Properties (chế độ / công cụ)
// -> đang kéo bị giật về. Giờ: chỉ trả về vị trí đã nhớ lúc cửa sổ chuyển từ ẩn / thu sang hiện, không đổi class khi kéo, bắt
// pointerdown ở tầng window (capture, trước công cụ khác), chặn bôi đen chữ.
// Dùng biến chung: store, $.
(() => {
  const main = document.querySelector("main");
  const st = document.createElement("style");
  st.textContent = `.flt-h{cursor:move;user-select:none;-webkit-user-select:none;touch-action:none} .flt-h button,.flt-h input{cursor:pointer}
    .flt[data-dragging]{opacity:.92;box-shadow:0 6px 24px #0008}`;
  document.head.appendChild(st);

  function clamp(el, x, y) {
    const m = main.getBoundingClientRect(), w = el.offsetWidth || 200;
    return [Math.max(40 - w, Math.min(m.width - 40, x)), Math.max(0, Math.min(m.height - 28, y))];
  }
  function apply(el, x, y) {
    [x, y] = clamp(el, x, y);
    el.style.left = x + "px"; el.style.top = y + "px"; el.style.right = "auto";
    return [x, y];
  }
  const shown = el => !el.hidden && !el.classList.contains("docked") && !el.classList.contains("folded");
  const ALL = [];
  function makeFloat(el, handle, name) {
    if (!el || !handle) return;
    el.classList.add("flt"); handle.classList.add("flt-h");
    const key = "pos." + name;
    const saved = () => { try { return JSON.parse(store.get(key, "null")) } catch { return null } };
    const restore = () => { const p = saved(); if (p && !S.drag) { apply(el, p.x, p.y); el.dataset.moved = "1" } };
    const S = { el, handle, drag: null, justMoved: false, wasShown: shown(el) };
    // mở lại (ẩn / thu -> hiện): về vị trí đã nhớ; class khác đổi (chế độ, công cụ...) thì bỏ qua
    new MutationObserver(() => { const now = shown(el); if (now && !S.wasShown) restore(); S.wasShown = now })
      .observe(el, { attributes: true, attributeFilter: ["hidden", "class"] });
    addEventListener("resize", () => { if (el.dataset.moved && !S.drag) apply(el, parseFloat(el.style.left) || 0, parseFloat(el.style.top) || 0) });
    ALL.push(S);
    restore();
    return { restore, reset: () => { store.set(key, "null"); delete el.dataset.moved; el.style.left = el.style.top = el.style.right = "" }, S };
  }
  // một bộ bắt chuột chung ở tầng window (capture): chạy trước mọi công cụ khác của trang, kéo được trong mọi chế độ
  addEventListener("pointerdown", ev => {
    // bấm vào cửa sổ nào thì cửa sổ đó nổi lên trên (2 cửa sổ chồng nhau vẫn với tới được tiêu đề cửa sổ dưới)
    const top = ALL.find(s => s.el.contains(ev.target));
    if (top) for (const s of ALL) s.el.style.zIndex = s === top ? "8" : "6";
    if (ev.button !== 0) return;
    const S = ALL.find(s => s.handle.contains(ev.target)); if (!S) return;
    if (S.el.closest("#rightCol")) return;                 // đang gắn trong cột phải (layout.js): không kéo
    if (ev.target.closest("button,input,select,label,a")) return;
    ev.preventDefault();                                   // không bôi đen chữ, không kéo-thả chữ
    getSelection()?.removeAllRanges?.();
    const r = S.el.getBoundingClientRect(), m = main.getBoundingClientRect();
    S.drag = { dx: ev.clientX - r.left, dy: ev.clientY - r.top, x0: ev.clientX, y0: ev.clientY, mx: m.left, my: m.top, moved: false, id: ev.pointerId };
    try { S.handle.setPointerCapture(ev.pointerId) } catch {}
  }, true);
  addEventListener("pointermove", ev => {
    const S = ALL.find(s => s.drag && s.drag.id === ev.pointerId); if (!S) return;
    const d = S.drag;
    if (!d.moved && Math.hypot(ev.clientX - d.x0, ev.clientY - d.y0) < 3) return;
    d.moved = true; S.el.dataset.dragging = "1";
    ev.preventDefault(); ev.stopImmediatePropagation();
    apply(S.el, ev.clientX - d.mx - d.dx, ev.clientY - d.my - d.dy);
  }, true);
  const end = ev => {
    const S = ALL.find(s => s.drag && s.drag.id === ev.pointerId); if (!S) return;
    const d = S.drag; S.drag = null; delete S.el.dataset.dragging;
    try { S.handle.releasePointerCapture(ev.pointerId) } catch {}
    if (!d.moved) return;
    S.el.dataset.moved = "1"; S.justMoved = true; setTimeout(() => S.justMoved = false, 0);
    store.set("pos." + (S.el.id === "edPanel" ? "props" : S.el.id === "histPanel" ? "hist" : S.el.id),
              JSON.stringify({ x: parseFloat(S.el.style.left), y: parseFloat(S.el.style.top) }));
  };
  addEventListener("pointerup", end, true); addEventListener("pointercancel", end, true);
  // kéo xong: không để cú bấm thu / mở mục (panel.js) chạy
  addEventListener("click", ev => { if (ALL.some(s => s.justMoved && s.handle.contains(ev.target))) { ev.stopImmediatePropagation(); ev.preventDefault() } }, true);

  const props = makeFloat($("edPanel"), $("secBone")?.querySelector(":scope > .secT"), "props");
  const hist = makeFloat($("histPanel"), $("histHead"), "hist");
  window.spineFloat = { makeFloat, props, hist, ALL };
})();
