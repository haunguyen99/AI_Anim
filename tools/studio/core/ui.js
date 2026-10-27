// AI Anim Studio — giao diện vỏ: menu, shelf, hộp công cụ, tab workspace, dock (Outliner + Channel Box + panel module),
// timeline, dòng trạng thái, tìm lệnh (F3), phím tắt, kéo đổi kích thước panel. Tất cả vẽ lại từ sổ lệnh + workspace hiện tại.
(function () {
  const $ = ST.$, esc = ST.esc, ic = ST.ic, V = ST.view;
  ST.MENUS = ["File", "Edit", "Select", "Mesh", "Rig", "Skin", "Animate", "Physics", "Display", "Window", "Help"];
  const MENU_VI = { File: "Tệp", Edit: "Sửa", Select: "Chọn", Mesh: "Mesh", Rig: "Rig", Skin: "Skin", Animate: "Animate", Physics: "Physics", Display: "Hiển thị", Window: "Cửa sổ", Help: "Trợ giúp" };

  // ---------------------------------------------------------------- lệnh chung
  const C = ST.cmd;
  C({ id: "file.home", global: true, menu: "File", label: "Dự án (Home)", icon: "home", key: "ctrl+h", run: () => { (window.top || window).location.href = "/home"; } });
  C({ id: "file.new", global: true, menu: "File", sep: true, label: "Cảnh mới", icon: "plus", key: "ctrl+n", run: () => { location.href = "/"; } });
  C({ id: "file.open", global: true, menu: "File", label: "Mở nhân vật…", icon: "open", key: "ctrl+o", run: openChar });
  C({ id: "edit.undo", menu: "Edit", label: "Hoàn tác", icon: "undo", key: "ctrl+z", on: () => ST.mod().canUndo ? ST.mod().canUndo() : ST.hist.U.length > 0, run: () => ST.hist.undo() });
  C({ id: "edit.redo", menu: "Edit", label: "Làm lại", icon: "redo", key: ["ctrl+shift+z", "ctrl+y"], on: () => !ST.mod().undo && ST.hist.R.length > 0, run: () => ST.hist.redo() });
  C({ id: "edit.search", global: true, menu: "Edit", sep: true, label: "Tìm lệnh…", icon: "search", key: ["f3", "ctrl+k"], run: openPalette });
  const tool = (id, label, icon, key, extra) => C(Object.assign({ id: "tool." + id, menu: "Edit", label, icon, key, check: () => ST.tool === id, on: () => { const w = ST.WS[ST.ws]; return !w || !w.tools || w.tools.includes("tool." + id); }, run: () => ST.setTool(id) }, extra || {}));
  tool("sel", "Công cụ chọn", "sel", "q", { sep: true }); tool("move", "Dời", "move", "w"); tool("rot", "Xoay", "rot", "e"); tool("scl", "Scale", "scl", "r");
  tool("free", "Free Transform (hộp bao)", "free", "t");
  C({ id: "view.frameAll", menu: "Display", label: "Nhìn toàn bộ", icon: "frame", key: "a", run: () => V.frameAll() });
  C({ id: "view.frameSel", menu: "Display", label: "Nhìn vùng chọn", icon: "framesel", key: "f", run: () => V.frameSel() });
  C({ id: "view.toggle4", menu: "Display", sep: true, label: "1 khung / 4 khung", icon: "view4", key: "space", check: () => V.layout === "4", run: () => V.toggle4() });
  ["persp", "top", "front", "side"].forEach(id => C({ id: "view.cam." + id, menu: "Display", label: "Khung: " + V.panes[id].label, icon: "view1", check: () => V.layout === "1" && V.single === id, run: () => V.setLayout("1", id) }));
  C({ id: "view.grid", menu: "Display", sep: true, label: "Lưới sàn", icon: "grid", check: () => V.showGrid, run: () => { V.showGrid = !V.showGrid; ST.pref.set("grid", V.showGrid); } });
  C({ id: "view.touch", menu: "Display", label: "Chế độ cảm ứng", icon: "touch", check: () => V.TM.on, run: () => V.setTouch(!V.TM.on) });
  C({ id: "view.theme", menu: "Display", label: "Đổi sáng / tối", run: () => { const r = document.documentElement, dark = r.dataset.theme ? r.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches; r.dataset.theme = dark ? "light" : "dark"; ST.pref.set("theme", r.dataset.theme); } });
  const panel = (k, label) => C({ id: "win." + k, menu: "Window", label, check: () => ui()[k], run: () => { const u = ui(); u[k] = !u[k]; ST.pref.set("ui:" + ST.ws, u); applyLayout(); } });
  panel("outliner", "Outliner"); panel("dock", "Dock phải (Channel Box, Công cụ)"); panel("shelf", "Shelf"); panel("timeline", "Timeline");
  C({ id: "win.reset", menu: "Window", sep: true, label: "Bố cục mặc định của workspace", icon: "reset", run: () => { ST.pref.set("ui:" + ST.ws, null); ST.pref.set("size:" + ST.ws, null); applyLayout(); } });
  C({ id: "help.keys", global: true, menu: "Help", label: "Phím tắt", icon: "keys", key: "f1", run: showKeys });
  C({ id: "help.nav", menu: "Help", label: "Điều hướng camera", run: () => ST.dialog("Điều hướng camera (kiểu Maya)", `<div class="keys"><kbd>Alt + kéo trái</kbd><span>Xoay quanh</span><kbd>Kéo giữa</kbd><span>Pan</span><kbd>Kéo phải / Alt + kéo phải</kbd><span>Xoay / dolly</span><kbd>Lăn chuột</kbd><span>Zoom (khung dưới chuột)</span><kbd>Space</kbd><span>1 khung ⇄ 4 khung (khung dưới chuột)</span><kbd>A / F</kbd><span>Nhìn toàn bộ / vùng chọn</span></div>`) });

  // ---------------------------------------------------------------- bố cục theo workspace
  const ui = () => Object.assign({ outliner: true, dock: true, shelf: true, timeline: false }, (ST.WS[ST.ws] || {}).ui || {}, ST.pref.get("ui:" + ST.ws, null) || {});
  function applyLayout() {
    const u = ui(), w = ST.WS[ST.ws] || {}, sz = Object.assign({ dockW: 320, olW: 240 }, w.size || {}, ST.pref.get("size:" + ST.ws, null) || {});
    document.body.classList.toggle("noout", !u.outliner); document.body.classList.toggle("nodock", !u.dock);
    document.body.classList.toggle("noshelf", !u.shelf); document.body.classList.toggle("notl", !u.timeline);
    document.body.style.setProperty("--dockW", sz.dockW + "px"); document.body.style.setProperty("--olW", sz.olW + "px");
    ST.refresh();
  }
  function splitter(el, key, axis, sign) {
    el.addEventListener("pointerdown", e => {
      e.preventDefault(); el.setPointerCapture(e.pointerId);
      const sz = Object.assign({ dockW: 320, olW: 240 }, (ST.WS[ST.ws] || {}).size || {}, ST.pref.get("size:" + ST.ws, null) || {}), s0 = sz[key], p0 = axis === "x" ? e.clientX : e.clientY;
      const mv = ev => { const d = (axis === "x" ? ev.clientX : ev.clientY) - p0; sz[key] = Math.max(key === "olW" ? 160 : axis === "x" ? 220 : 80, Math.min(axis === "x" ? 640 : innerHeight - 260, s0 + d * sign)); document.body.style.setProperty("--" + key, sz[key] + "px"); };
      const up = () => { el.removeEventListener("pointermove", mv); el.removeEventListener("pointerup", up); ST.pref.set("size:" + ST.ws, sz); };
      el.addEventListener("pointermove", mv); el.addEventListener("pointerup", up);
    });
  }
  splitter($("splitR"), "dockW", "x", -1); splitter($("splitO"), "olW", "x", 1);

  // ---------------------------------------------------------------- menu
  const menusEl = $("menus"), pop = $("menuPop");
  let openMenu = null;
  menusEl.innerHTML = ST.MENUS.map(m => `<button data-m="${m}" aria-haspopup="menu">${MENU_VI[m]}</button>`).join("");
  function showMenu(name) {
    openMenu = name; menusEl.querySelectorAll("button").forEach(b => b.classList.toggle("open", b.dataset.m === name));
    const items = [...ST.cmds.values()].filter(c => c.menu === name && !c.hidden);
    pop.innerHTML = items.map(c => (c.sep ? '<div class="sep"></div>' : "") + (c.head ? `<div class="hd">${esc(c.head)}</div>` : "") +
      `<button class="mi" role="menuitem" data-c="${c.id}" ${ST.cmdOn(c) ? "" : "disabled"} title="${esc(c.tip || (c.ws && !c.ws.includes(ST.ws) ? "Dùng trong workspace " + c.ws.map(w => (ST.WS[w] || {}).label || w).join(", ") : ""))}">` +
      `<span class="ck">${c.check ? (c.check() ? "✓" : "") : ""}</span>${c.icon ? ic(c.icon) : '<svg class="i"></svg>'}<span>${esc(c.label)}</span>${c.key ? `<span class="k">${esc(ST.keyLabel(c.key))}</span>` : ""}</button>`).join("") || '<div class="hd">Trống</div>';
    const r = menusEl.querySelector(`[data-m="${name}"]`).getBoundingClientRect();
    pop.classList.add("show"); pop.style.left = Math.max(4, Math.min(r.left, innerWidth - pop.offsetWidth - 4)) + "px"; pop.style.top = r.bottom + 2 + "px";
  }
  function closeMenu() { openMenu = null; pop.classList.remove("show"); menusEl.querySelectorAll("button").forEach(b => b.classList.remove("open")); }
  menusEl.addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; openMenu === b.dataset.m ? closeMenu() : showMenu(b.dataset.m); });
  menusEl.addEventListener("pointerover", e => { const b = e.target.closest("button"); if (b && openMenu && openMenu !== b.dataset.m) showMenu(b.dataset.m); });
  pop.addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (!b || b.disabled) return; closeMenu(); ST.run(b.dataset.c); });
  document.addEventListener("pointerdown", e => { if (openMenu && !pop.contains(e.target) && !menusEl.contains(e.target)) closeMenu(); });

  // ---------------------------------------------------------------- shelf, hộp công cụ, tab workspace
  const btn = (id, cls) => { const c = ST.cmds.get(id); if (!c) return ""; const t = c.label + (c.key ? " (" + ST.keyLabel(c.key) + ")" : ""); return `<button data-c="${id}" class="${(c.check && c.check()) ? "on" : ""} ${cls || ""}" title="${esc(t)}" aria-label="${esc(c.label)}" ${ST.cmdOn(c) ? "" : "disabled"}>${ic(c.icon || "plus")}</button>`; };
  const strip = list => (list || []).map(id => id === "|" ? '<span class="gap"></span>' : btn(id)).join("");
  function renderBars() {
    const w = ST.WS[ST.ws] || {}, m = ST.mod();
    document.body.className = document.body.className.replace(/(^|\s)ws-[\w-]+/g, " ").trim() + " ws-" + ST.ws;
    if (m.shelfNode) { const n = m.shelfNode(); if (n && $("shelf").firstChild !== n) $("shelf").replaceChildren(n); }   // khối shelf riêng của module (vd thanh công cụ Pose)
    else $("shelf").innerHTML = strip(w.shelf);
    $("toolbox").innerHTML = strip(w.tools) + (w.modes ? '<span class="gap"></span>' + strip(w.modes) : "");
    $("wstabs").innerHTML = Object.values(ST.WS).map(x => `<button role="tab" aria-selected="${x.id === ST.ws}" class="${x.id === ST.ws ? "on" : ""}" data-ws="${x.id}" title="Workspace ${esc(x.label)}">${ic(x.icon)}<span>${esc(x.label)}</span></button>`).join("");
  }
  ["shelf", "toolbox"].forEach(k => $(k).addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (b && !b.disabled) ST.run(b.dataset.c); }));
  $("wstabs").addEventListener("click", e => { const b = e.target.closest("[data-ws]"); if (b) ST.setWS(b.dataset.ws); });

  // ---------------------------------------------------------------- Outliner (module trả các dòng)
  let renaming = null;
  function renderOutliner() {
    const m = ST.mod(), rows = m.outline ? m.outline() : [];
    $("olBody").innerHTML = rows.map(r => `<div class="olr ${r.grp ? "grp" : ""} ${r.sel ? "sel" : ""} ${r.act ? "act" : ""}" style="--d:${r.d || 0}" data-id="${esc(r.id)}">` +
      (r.fold !== undefined ? `<button data-a="fold" class="fold" title="${r.fold ? "Mở" : "Gập"}" aria-label="${r.fold ? "Mở" : "Gập"}" aria-expanded="${!r.fold}">${r.fold ? "▸" : "▾"}</button>` : '<span class="fold"></span>') +
      `<span class="nm" title="${esc(r.label)}${r.rename ? " · bấm đúp để đổi tên" : ""}">${r.icon ? ic(r.icon) : ""}${renaming === r.id ? `<input id="olRn" value="${esc(r.label)}">` : `<span class="tx">${esc(r.label)}</span>`}</span>` +
      (r.count !== undefined ? `<small>${esc(r.count)}</small>` : "") + (r.del ? `<button data-a="del" class="del" title="Xoá" aria-label="Xoá">${ic("trash")}</button>` : "") +
      (r.lock !== undefined ? `<button data-a="lock" class="lk ${r.lock ? "on" : "off"}" title="Khoá: không chọn, không sửa" aria-label="Khoá">${ic(r.lock ? "lock" : "unlock")}</button>` : "") +
      (r.vis !== undefined ? `<button data-a="vis" class="${r.vis ? "" : "off"}" title="Ẩn / hiện" aria-label="Ẩn hoặc hiện">${ic(r.vis ? "eye" : "eyeoff")}</button>` : "") + `</div>`).join("") ||
      '<div class="sub" style="padding:8px 10px">Trống.</div>';
  }
  const olB = $("olBody");
  olB.addEventListener("click", e => {
    const r = e.target.closest(".olr"), a = e.target.closest("[data-a]"); if (!r || e.target.closest("input")) return;
    if (r.classList.contains("grp") && !a) return;
    const m = ST.mod(); if (m.olAct) m.olAct(r.dataset.id, a ? a.dataset.a : "pick", e); ST.refresh();
  });
  olB.addEventListener("dblclick", e => { const r = e.target.closest(".olr"); if (!r || e.target.closest("button")) return; const m = ST.mod(); if (!m.outline || !(m.outline().find(x => String(x.id) === r.dataset.id) || {}).rename) return; renaming = r.dataset.id; renderOutliner(); const i = $("olRn"); if (i) { i.focus(); i.select(); } });
  const commitRn = (i, ok) => { const id = renaming; renaming = null; const m = ST.mod(); if (ok && m.olAct) m.olAct(id, "rename", null, i.value.trim()); ST.refresh(); };
  olB.addEventListener("keydown", e => { if (e.target.id !== "olRn") return; e.stopPropagation(); if (e.key === "Enter") commitRn(e.target, true); else if (e.key === "Escape") commitRn(e.target, false); });
  olB.addEventListener("focusout", e => { if (e.target.id === "olRn" && renaming !== null) commitRn(e.target, true); });

  // ---------------------------------------------------------------- dock: tab Channel Box + panel của module
  const attrB = $("attrBody");
  const curTab = () => { const w = ST.WS[ST.ws] || {}, tabs = w.tabs || []; const t = ST.pref.get("tab:" + ST.ws, tabs[0] && tabs[0][0]); return tabs.some(x => x[0] === t) ? t : tabs[0] && tabs[0][0]; };
  function renderAttr(force) {
    const w = ST.WS[ST.ws] || {}, tabs = w.tabs || [], t = curTab();
    $("attrTabs").innerHTML = tabs.map(([id, label]) => `<button role="tab" data-t="${id}" class="${id === t ? "on" : ""}">${esc(label)}</button>`).join("");
    if (!force && attrB.contains(document.activeElement) && /INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)) return;
    if (t === "channel") { attrB.dataset.key = ""; return chRender(); }
    if (ST.mod().panelNode) { const n = ST.mod().panelNode(t); if (n) { if (attrB.firstChild !== n || attrB.childNodes.length !== 1) attrB.replaceChildren(n); attrB.dataset.key = ""; return; } }
    const m = ST.mod(), key = ST.ws + ":" + t + ":" + (m.panelKey ? m.panelKey() : "");
    if (m.panelStatic && !force && attrB.dataset.key === key) return;   // module tự vẽ lại panel của nó (vd lõi Rig)
    attrB.innerHTML = m.panel ? m.panel(t) : ""; attrB.dataset.key = key;
    if (m.panelMounted) m.panelMounted(t);
  }
  $("attrTabs").addEventListener("click", e => { const b = e.target.closest("[data-t]"); if (!b) return; ST.pref.set("tab:" + ST.ws, b.dataset.t); renderAttr(true); });
  ["click", "change", "input"].forEach(ev => attrB.addEventListener(ev, e => { if (curTab() === "channel") return; const m = ST.mod(), f = m["panel_" + ev]; if (f) f.call(m, e); }));

  // Channel Box: provider = module.channel {title(), vals()→{t,r,s}|null, apply(vals, push), begin(), reset()}
  const CHROWS = [["X", "t", 0, 0.1], ["Y", "t", 1, 0.1], ["Z", "t", 2, 0.1], ["X", "r", 0, 0.5], ["Y", "r", 1, 0.5], ["Z", "r", 2, 0.5], ["X", "s", 0, 0.01], ["Y", "s", 1, 0.01], ["Z", "s", 2, 0.01]];
  const prov = () => ST.mod().channel || null;
  function chRender() {
    const P = prov(), v = P && P.vals(), title = P ? P.title() : "";
    let h = `<div class="chh"><b title="${esc(title)}">${esc(title || "Channel Box")}</b>${P && P.unit ? `<span class="sub">(${esc(P.unit)})</span>` : ""}</div>`;
    if (!v) { attrB.innerHTML = h + '<div class="chn">Chưa chọn gì.</div>'; return; }
    let last = "";
    for (const [lab, g, i, st] of CHROWS) {
      if (g !== last) { h += `<div class="chs">${g === "t" ? "Translate" : g === "r" ? "Rotate" : "Scale"}</div>`; last = g; }
      h += `<div class="chr"><label data-g="${g}" data-i="${i}" data-st="${st}" title="Kéo trái / phải để đổi (Shift chậm, Ctrl nhanh)">${g.toUpperCase()}${lab}</label><input type="number" data-g="${g}" data-i="${i}" step="${st}" value="${+v[g][i].toFixed(g === "s" ? 3 : 2)}"></div>`;
    }
    h += `<div class="row" style="margin-top:8px"><button data-a="rst" title="Coi trạng thái hiện tại là gốc: Rotate về 0, Scale về 1">Đặt lại 0/1</button></div>`;
    attrB.innerHTML = h;
  }
  ST.chRefresh = () => {
    if (curTab() !== "channel") return;
    const P = prov(), v = P && P.vals(), ins = attrB.querySelectorAll("input[data-g]");
    if (!v || !ins.length) return chRender();
    ins.forEach(el => { if (document.activeElement !== el) el.value = +v[el.dataset.g][+el.dataset.i].toFixed(el.dataset.g === "s" ? 3 : 2); });
    const b = attrB.querySelector(".chh b"); if (b) b.textContent = P.title();
  };
  const chRead = () => { const v = { t: [0, 0, 0], r: [0, 0, 0], s: [1, 1, 1] }; attrB.querySelectorAll("input[data-g]").forEach(el => { const x = parseFloat(String(el.value).replace(",", ".")); v[el.dataset.g][+el.dataset.i] = isFinite(x) ? x : (el.dataset.g === "s" ? 1 : 0); }); return v; };
  attrB.addEventListener("change", e => { if (curTab() === "channel" && e.target.matches("input[data-g]")) { prov() && prov().apply(chRead(), true); ST.chRefresh(); } });
  attrB.addEventListener("keydown", e => { if (e.target.matches("input")) { e.stopPropagation(); if (e.key === "Enter") e.target.blur(); } });
  attrB.addEventListener("click", e => { if (curTab() === "channel" && e.target.closest('[data-a="rst"]')) { prov() && prov().reset(); chRender(); } });
  let chDrag = null;
  attrB.addEventListener("pointerdown", e => {
    const l = e.target.closest("label[data-g]"); if (!l || curTab() !== "channel") return;
    const P = prov(), v = P && P.vals(); if (!v) return; e.preventDefault(); l.setPointerCapture(e.pointerId); P.begin();
    chDrag = { g: l.dataset.g, i: +l.dataset.i, st: +l.dataset.st, x0: e.clientX, v0: v[l.dataset.g][+l.dataset.i] };
  });
  attrB.addEventListener("pointermove", e => {
    if (!chDrag) return; const d = chDrag, k = e.shiftKey ? 0.1 : e.ctrlKey ? 10 : 1, P = prov(), nv = JSON.parse(JSON.stringify(P.vals()));
    nv[d.g][d.i] = d.v0 + (e.clientX - d.x0) * d.st * k; P.apply(nv, false); ST.chRefresh();
  });
  const chEnd = () => { if (chDrag) { chDrag = null; ST.refresh(); } };
  attrB.addEventListener("pointerup", chEnd); attrB.addEventListener("pointercancel", chEnd);

  // ---------------------------------------------------------------- timeline + dòng trạng thái
  function renderTimeline() { const m = ST.mod(); if (m.timelineNode) { const n = m.timelineNode(); if ($("timeline").firstChild !== n) $("timeline").replaceChildren(n); return; } $("timeline").innerHTML = m.timeline ? m.timeline() : '<span class="sub">Timeline</span><div class="tlbar"></div>'; }
  function renderStatus() { const m = ST.mod(); $("stInfo").textContent = m.info ? m.info() : ""; $("stHint").textContent = ST.hint || ""; }

  // ---------------------------------------------------------------- tìm lệnh (F3)
  const pal = $("palette"), palIn = $("palIn"), palList = $("palList");
  let palSel = 0, palItems = [];
  function openPalette() { pal.classList.add("show"); palIn.value = ""; palFill(); setTimeout(() => palIn.focus(), 10); }
  function palFill() {
    const q = palIn.value.trim().toLowerCase();
    palItems = [...ST.cmds.values()].filter(c => !c.hidden && c.id !== "edit.search" && (!q || (c.label + " " + (MENU_VI[c.menu] || "") + " " + c.menu + " " + c.id).toLowerCase().includes(q)));
    palItems.sort((a, b) => ST.cmdOn(b) - ST.cmdOn(a)); palSel = 0; palDraw();
  }
  function palDraw() { palList.innerHTML = palItems.slice(0, 60).map((c, i) => `<button class="it ${i === palSel ? "on" : ""}" data-i="${i}" ${ST.cmdOn(c) ? "" : "disabled"}>${c.icon ? ic(c.icon) : '<svg class="i"></svg>'}<span>${esc(c.label)}</span><small>${esc(MENU_VI[c.menu] || c.menu || "")}${c.key ? " · " + esc(ST.keyLabel(c.key)) : ""}</small></button>`).join("") || '<div class="sub" style="padding:10px">Không có lệnh nào.</div>'; }
  const palRun = i => { const c = palItems[i]; pal.classList.remove("show"); if (c) ST.run(c.id); };
  palIn.addEventListener("input", palFill);
  palIn.addEventListener("keydown", e => {
    e.stopPropagation();
    if (e.key === "Escape") pal.classList.remove("show");
    else if (e.key === "ArrowDown") { palSel = Math.min(palItems.length - 1, palSel + 1); palDraw(); e.preventDefault(); }
    else if (e.key === "ArrowUp") { palSel = Math.max(0, palSel - 1); palDraw(); e.preventDefault(); }
    else if (e.key === "Enter") palRun(palSel);
  });
  palList.addEventListener("click", e => { const b = e.target.closest("[data-i]"); if (b && !b.disabled) palRun(+b.dataset.i); });
  [pal, $("dialog")].forEach(m => m.addEventListener("pointerdown", e => { if (e.target === m) m.classList.remove("show"); }));

  function showKeys() {
    const rows = [...ST.cmds.values()].filter(c => c.key && !c.hidden);
    ST.dialog("Phím tắt", `<div class="keys">${rows.map(c => `<kbd>${esc((Array.isArray(c.key) ? c.key : [c.key]).map(ST.keyLabel).join(" / "))}</kbd><span>${esc(c.label)}${c.ws ? ` <span class="sub">(${esc(c.ws.map(w => (ST.WS[w] || {}).label || w).join(", "))})</span>` : ""}</span>`).join("")}</div>`);
  }
  async function openChar() {
    ST.dialog("Mở nhân vật", '<div class="sub">Đang tải danh sách…</div>');
    try {
      const L = await (await fetch("/api/chars")).json();
      $("dlgB").innerHTML = `<div class="list">${L.map(c => `<button class="it" data-id="${esc(c.id)}">${ic("mesh")}<span>${esc(c.name)}</span><small>${esc(c.id)}</small></button>`).join("")}</div>`;
      $("dlgB").onclick = e => { const b = e.target.closest("[data-id]"); if (!b) return; const u = new URL("/studio/" + encodeURIComponent(b.dataset.id), location.origin); u.searchParams.set("ws", ST.ws || "general"); location.href = u; };
    } catch (e) { $("dlgB").innerHTML = '<div class="sub">Không đọc được danh sách nhân vật (Home server).</div>'; }
  }

  // ---------------------------------------------------------------- phím tắt
  const combo = e => { const k = e.key === " " ? "space" : e.key.toLowerCase(); return (e.ctrlKey || e.metaKey ? "ctrl+" : "") + (e.altKey ? "alt+" : "") + (e.shiftKey && k.length > 1 || e.shiftKey && /[a-z]/.test(k) ? "shift+" : "") + k; };
  const keyMatch = (c, k) => c.key && (Array.isArray(c.key) ? c.key : [c.key]).includes(k);
  addEventListener("keydown", e => {
    if (/INPUT|TEXTAREA|SELECT/.test((e.target || {}).tagName || "")) return;
    if (e.key === "Escape") { closeMenu(); pal.classList.remove("show"); ST.closeDialog(); return; }
    if ($("dialog").classList.contains("show")) return;
    const k = combo(e), all = [...ST.cmds.values()].filter(c => keyMatch(c, k));
    const c = all.find(c => c.ws && c.ws.includes(ST.ws)) || all.find(c => !c.ws);
    if (!c) return;
    if (ST.mod().ownKeys && !c.global) return;   // workspace tự xử lý phím (Pose): Studio chỉ giữ phím chung
    e.preventDefault(); ST.run(c.id);
  });

  // ---------------------------------------------------------------- vẽ lại khi có thay đổi
  let rq = 0;
  ST.on("ui", () => { if (rq) return; rq = setTimeout(() => { rq = 0; renderBars(); renderOutliner(); renderAttr(); renderTimeline(); renderStatus(); if (openMenu) showMenu(openMenu); }, 0); });
  // ---------------------------------------------------------------- cảnh trống: ô gợi ý giữa viewport
  ST.on("empty", async () => {
    const el = $("empty"); el.hidden = false;
    el.innerHTML = `<b>Cảnh trống</b><div class="row"><button class="on" data-c="file.fbx">${ic("import")} Nhập FBX…</button><button data-c="file.open">${ic("open")} Mở nhân vật…</button></div><div class="sub">Mở nhanh:</div><div class="list" id="emptyList"><span class="sub">Đang tải…</span></div>`;
    let L = []; try { L = await (await fetch("/api/chars")).json(); } catch (e) {}
    const last = ST.pref.get("char", null); L.sort((a, b) => (b.id === last) - (a.id === last));
    $("emptyList").innerHTML = L.map(c => `<a class="it" href="/studio/${encodeURIComponent(c.id)}?ws=${encodeURIComponent(ST.ws || "general")}">${ic("mesh")}<span>${esc(c.name)}</span><small>${c.id === last ? "mở lần trước" : esc(c.id)}</small></a>`).join("") || '<span class="sub">Chưa có nhân vật.</span>';
  });
  $("empty").addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (b) ST.run(b.dataset.c); });
  ST.on("hist", () => ST.refresh());
  ST.on("ws", () => applyLayout());
  ST.on("init", () => { const t = ST.pref.get("theme", null); if (t) document.documentElement.dataset.theme = t; });
})();
