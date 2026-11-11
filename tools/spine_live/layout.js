// Bố cục không che hình (2026-11-05, người dùng: "sửa lại UI của spine live sao cho thân thiện logic hơn"; chọn: không che hình,
// xếp lại thanh trên, Properties theo nhóm, timeline dễ đọc). Khảo sát trước đó: ở khung 775 px cột Phiên bản (178 px) + Properties
// (300 px) + thanh Claude phủ gần 2/3 khung hình.
//  - Cột trái = Phiên bản, cột phải = Properties (+ công cụ) trên, History dưới; khung hình nằm giữa (#stage co theo --padL / --padR).
//  - Vẫn giữ cửa sổ nổi (người dùng 2026-11-04): nút ⧉ trên tiêu đề thả Properties / History ra kéo tự do; ⇥ gắn lại vào cột.
//  - Thu (⟩) Properties / History như cũ; thu cả hai thì cột phải biến mất, hình rộng ra. Khung hẹp (< 860 px) tự thu Phiên bản
//    thành dải dọc (không ghi nhớ; rộng ra thì về như người dùng đặt).
//  - Thanh Claude thành một dòng dưới đáy khung hình; nhãn SETUP / ANIMATE lên góc trên trái khung hình.
//  - Nút Update (đưa bản sửa tay vào Phiên bản) chuyển lên đầu cột Phiên bản; Graph ▾ ra sau nút zoom timeline.
// Dùng biến chung: store, $.
(() => {
  const main = document.querySelector("main"), body = document.body;
  const st = document.createElement("style");
  st.textContent = `
    main{--padL:0px;--padR:0px}
    #stage{left:var(--padL) !important;right:var(--padR) !important}
    /* cột trái: Phiên bản */
    #verPanel{left:0 !important;top:0 !important;bottom:0;max-height:none !important;border-radius:0 !important;border-width:0 1px 0 0 !important;box-shadow:none !important;width:178px}
    #verPanel.folded{width:30px !important}
    #verPanel.folded #verHead{writing-mode:vertical-rl;border-bottom:0;padding:8px 4px;gap:8px;height:100%;justify-content:flex-start}
    #verPanel.folded #verHead b,#verPanel.folded #edPublish{display:none}
    #verPanel.folded #verFold{writing-mode:vertical-rl;padding:8px 2px}
    #verHead #edPublish{margin:0;padding:1px 7px;font-size:11px}
    /* cột phải: Properties + History */
    #rightCol{position:absolute;right:0;top:0;bottom:0;width:300px;z-index:6;display:flex;flex-direction:column;gap:0;
      background:var(--raise);border-left:1px solid var(--line);min-height:0}
    #rightCol[hidden]{display:none !important}
    #rightCol > #edPanel{position:static !important;width:auto !important;max-height:none !important;flex:0 1 auto;min-height:0;overflow:auto;
      border:0 !important;border-radius:0 !important;box-shadow:none !important;left:auto !important;top:auto !important}
    #rightCol > #histPanel{position:static !important;width:auto !important;max-height:none !important;flex:1 1 140px;min-height:110px;
      border:0 !important;border-top:1px solid var(--line) !important;border-radius:0 !important;box-shadow:none !important;left:auto !important;top:auto !important}
    #rightCol > #edPanel .flt-h,#rightCol > #histPanel .flt-h{cursor:default}
    .layBtn{padding:0 6px !important;margin-left:4px;font-size:11px}
    /* lớp phủ trong khung hình: tránh hai cột */
    #claude{left:calc(var(--padL) + 12px) !important;right:calc(var(--padR) + 12px);top:auto !important;bottom:10px;max-width:none !important}
    #claudeBar{align-items:center;padding:4px 10px}
    #claudeBar span{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    #claudeLog{position:absolute;bottom:calc(100% + 4px);left:0;right:0;margin:0}
    #claudeX{right:-6px;top:-6px}
    #modeBadge{left:calc(var(--padL) + 12px) !important;top:10px !important;bottom:auto !important}
    #msg{left:calc(var(--padL) + 16px) !important;right:calc(var(--padR) + 16px) !important}
    #legend{right:calc(var(--padR) + 12px) !important}
    #helpPop{right:calc(var(--padR) + 12px) !important}
    #dockTab,#histTab{z-index:7}
    /* tab mở lại khi thu: nằm trong cột (ngang); thu cả hai thì cột thành dải dọc 28 px */
    #rightCol > #dockTab,#rightCol > #histTab{position:static;writing-mode:horizontal-tb;border-radius:0;border:0;border-bottom:1px solid var(--line);padding:5px 8px;text-align:left}
    #rightCol.tabsOnly{width:28px}
    #rightCol.tabsOnly > #dockTab,#rightCol.tabsOnly > #histTab{writing-mode:vertical-rl;padding:10px 4px;text-align:center}
    /* thanh trên: nhóm theo việc */
    header .hsep{width:1px;align-self:stretch;margin:2px 2px;background:var(--line)}
    header #status{order:0}
    @media (max-width:900px){#fpBtn{max-width:190px} #status{display:none}}
    /* Properties theo nhóm */
    #edPanel .pg{margin:4px 0 -2px;font-size:10px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--mute)}
    /* timeline */
    #tlNum{font-size:14px;min-width:84px;padding:3px 6px;border-radius:6px;background:var(--raise);border:1px solid var(--line)}
    #amBtn .amLen{color:var(--mute);font-weight:400;margin-left:4px}
    #tlBar .tsep{width:1px;height:22px;background:var(--line)}`;
  document.head.appendChild(st);

  // ---- cột phải ----
  const col = document.createElement("aside"); col.id = "rightCol";
  main.appendChild(col);
  const ED = $("edPanel"), HI = $("histPanel");
  const docked = { props: store.get("lay.props", "1") === "1", hist: store.get("lay.hist", "1") === "1" };
  function headOf(el) { return el === ED ? $("secBone")?.querySelector(":scope > .secT") : $("histHead") }
  function addBtn(el, key) {
    const h = headOf(el); if (!h || h.querySelector(".layBtn")) return;
    const b = document.createElement("button"); b.className = "layBtn";
    const fold = h.querySelector("#dockBtn, #histFold");
    h.insertBefore(b, fold || null);
    const upd = () => { b.textContent = docked[key] ? "⧉" : "⇥"; b.title = docked[key] ? "Thả ra thành cửa sổ nổi (kéo tự do)" : "Gắn lại vào cột phải" };
    b.onclick = ev => { ev.stopPropagation(); docked[key] = !docked[key]; store.set("lay." + key, docked[key] ? "1" : "0"); place(); upd() };
    upd();
  }
  function place() {
    for (const [el, key] of [[ED, "props"], [HI, "hist"]]) {
      if (!el) continue;
      if (docked[key]) { if (el.parentElement !== col) col.appendChild(el) }
      else if (el.parentElement === col) { main.appendChild(el); window.spineFloat?.[key]?.restore?.() }
    }
    // tab mở lại: theo panel của nó (trong cột thì vào cột, nổi thì về cạnh phải khung như cũ)
    const DT = $("dockTab"), HT = $("histTab");
    if (DT) docked.props ? (DT.parentElement !== col && col.prepend(DT)) : (DT.parentElement === col && main.appendChild(DT));
    if (HT) docked.hist ? (HT.parentElement !== col && col.appendChild(HT)) : (HT.parentElement === col && main.appendChild(HT));
    // thứ tự trong cột: [tab Properties] Properties  History [tab History]
    for (const el of [DT, ED, HI, HT]) if (el && el.parentElement === col) col.appendChild(el);
    sync();
  }
  const vis = el => el && !el.hidden && !el.classList.contains("docked") && !el.classList.contains("folded") && el.offsetParent !== null;
  let narrowAuto = false, wasNarrow = null;
  function sync() {
    const open = [...col.children].filter(c => !c.hidden && !c.classList.contains("docked") && !c.classList.contains("folded"));
    const panels = open.filter(c => c === ED || c === HI);
    const any = open.length > 0;
    col.hidden = !any; col.classList.toggle("tabsOnly", any && !panels.length);
    const V = $("verPanel");
    // khung hẹp: tự thu Phiên bản MỘT LẦN khi khung chuyển rộng -> hẹp (hoặc lúc mở trang), không ghi nhớ.
    // 2026-11-05 (người dùng: "cửa sổ phiên bản đang không xổ ra được"): trước đây sync() thu lại mỗi lần chạy, nên khung
    // trình duyệt trong app (775 px < 860) bấm ▶ xổ ra là bị thu ngay. Người dùng bấm mở trong khung hẹp thì giữ nguyên.
    if (V) {
      const narrow = main.clientWidth < 860, userFold = store.get("verFold", "0") === "1";
      if (narrow && wasNarrow !== true && !V.classList.contains("folded")) { narrowAuto = true; V.classList.add("folded"); $("verFold").textContent = "▶ Phiên bản" }
      else if (!narrow && narrowAuto && !userFold) { narrowAuto = false; V.classList.remove("folded"); $("verFold").textContent = "◀" }
      wasNarrow = narrow;
    }
    main.style.setProperty("--padL", (V && V.offsetParent !== null ? V.offsetWidth : 0) + "px");
    main.style.setProperty("--padR", (any ? col.offsetWidth : 0) + "px");
  }
  // nút Thu của Phiên bản: người dùng bấm thì bỏ chế độ tự thu
  $("verFold")?.addEventListener("click", () => { narrowAuto = false; setTimeout(sync, 0) });
  new MutationObserver(sync).observe(col, { subtree: false, childList: true, attributes: true, attributeFilter: ["class", "hidden"] });
  for (const el of [ED, HI, $("verPanel"), $("dockTab"), $("histTab")]) if (el) new MutationObserver(sync).observe(el, { attributes: true, attributeFilter: ["class", "hidden"] });
  addEventListener("resize", sync);
  new ResizeObserver(sync).observe(main);


  // ---- Update lên đầu cột Phiên bản ----
  const pub = $("edPublish"), vh = $("verHead");
  if (pub && vh) { vh.insertBefore(pub, $("verFold")); pub.textContent = "⬆ Update" }

  // ---- thanh trên: thứ tự theo việc ----
  const hd = document.querySelector("header");
  const sep = () => { const s = document.createElement("span"); s.className = "hsep"; return s };
  const undo = $("edUndo")?.parentElement, zoom = $("zOut")?.parentElement, reload = $("reload");
  if (undo && zoom && reload) {
    $("edUndo").textContent = "↶"; $("edUndo").title = "Hoàn tác lần ghi file gần nhất (Ctrl+Z)"; $("edRedo").title = "Làm lại (Ctrl+Y)";
    // File · Setup/Animate | ↶ ↷ | Công cụ · Hiển thị | − Vừa + | trạng thái … Theo Claude · Cây · ⟳ · ?
    $("modeTabs").after(sep(), undo, sep());
    $("viewMenu").after(sep(), zoom);
    const tail = [$("status"), $("follow")?.closest("label"), $("outBtn"), reload, $("helpBtn")].filter(Boolean);
    for (const el of tail) hd.appendChild(el);
  }

  // ---- timeline: Graph sau nút zoom, tên anim kèm độ dài ----
  const g = $("tlGraph"), tin = $("tlIn");
  if (g && tin) { const s = document.createElement("span"); s.className = "tsep"; tin.after(s, g) }
  const amLen = document.createElement("span"); amLen.className = "amLen"; $("amName")?.after(amLen);
  setInterval(() => {
    try {
      const e = player?.animationState?.getCurrent(0), fps = player?.skeleton?.data?.fps || 30;
      const t = e ? Math.round(e.animation.duration * fps) + "F" : "";
      if (amLen.textContent !== t) amLen.textContent = t;
    } catch {}
  }, 300);

  addBtn(ED, "props"); addBtn(HI, "hist");
  place();
  setTimeout(sync, 300); setInterval(sync, 1500);
  window.spineLayout = { sync, place, docked };
})();
