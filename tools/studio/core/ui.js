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
  // công cụ chọn / dời / xoay / scale áp lên module đang focus; Free Transform chỉ có ở mesh
  const tool = (id, label, icon, key, extra) => C(Object.assign({ id: "tool." + id, menu: "Edit", label, icon, key, keep: true, check: () => ST.tool === id, run: () => ST.setTool(id) }, extra || {}));
  tool("sel", "Công cụ chọn", "sel", "q", { sep: true }); tool("move", "Dời", "move", "w"); tool("rot", "Xoay", "rot", "e"); tool("scl", "Scale", "scl", "r");
  tool("free", "Free Transform (hộp bao)", "free", "t", { mod: "mesh", keep: false });
  C({ id: "view.frameAll", menu: "Display", label: "Nhìn toàn bộ", icon: "frame", key: "a", run: () => V.frameAll() });
  C({ id: "view.frameSel", menu: "Display", label: "Nhìn vùng chọn", icon: "framesel", key: "f", run: () => V.frameSel() });
  C({ id: "view.toggle4", menu: "Display", sep: true, label: "1 khung / 4 khung", icon: "view4", key: "space", check: () => V.layout === "4", run: () => V.toggle4() });
  ["persp", "top", "front", "side"].forEach(id => C({ id: "view.cam." + id, menu: "Display", label: "Khung: " + V.panes[id].label, icon: "view1", check: () => V.layout === "1" && V.single === id, run: () => V.setLayout("1", id) }));
  C({ id: "view.grid", menu: "Display", sep: true, label: "Lưới sàn", icon: "grid", check: () => V.showGrid, run: () => { V.showGrid = !V.showGrid; ST.pref.set("grid", V.showGrid); } });
  C({ id: "view.touch", menu: "Display", label: "Chế độ cảm ứng", icon: "touch", check: () => V.TM.on, run: () => V.setTouch(!V.TM.on) });
  C({ id: "view.theme", menu: "Display", label: "Đổi sáng / tối", run: () => { const r = document.documentElement, dark = r.dataset.theme ? r.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches; r.dataset.theme = dark ? "light" : "dark"; ST.pref.set("theme", r.dataset.theme); } });
  const panel = (k, label) => C({ id: "win." + k, menu: "Window", label, keep: true, check: () => ui()[k], run: () => { const u = ui(); u[k] = !u[k]; ST.pref.set("ui:" + ST.ws, u); applyLayout(); } });
  panel("outliner", "Outliner"); panel("dock", "Dock phải (Channel Box, panel)"); panel("shelf", "Shelf"); panel("timeline", "Timeline");
  C({ id: "win.reset", menu: "Window", label: "Bố cục mặc định của workspace", icon: "reset", keep: true, run: () => { ["ui:", "size:", "tabs:"].forEach(k => ST.pref.set(k + ST.ws, null)); applyLayout(); } });
  // mọi panel mở được ở mọi workspace: bật / tắt tab trong dock của workspace đang dùng (lưu theo workspace)
  ST.on("init", () => Object.entries(ST.PANELS || {}).forEach(([id, p], i) => C({ id: "panel." + id, menu: "Window", sep: i === 0, head: i === 0 ? "Panel trong dock" : undefined, label: p.label, keep: true,
    check: () => tabList().includes(id), run: () => { const L = tabList(), on = L.includes(id); ST.pref.set("tabs:" + ST.ws, on ? L.filter(x => x !== id) : L.concat(id)); if (!on) { ST.pref.set("tab:" + ST.ws, id); if (p.mod && !p.nofocus) ST.setFocus(p.mod); } ST.refresh(); } })));
  // lớp: cảnh (mesh + xương), rig, anim — bật một lớp thì hai lớp kia ẩn
  [["scene", "Lớp Nhân vật (mesh + xương + rig)"], ["anim", "Lớp Anim"]].forEach(([k, label], i) => C({ id: "layer." + k, menu: "Display", sep: i === 0, label, icon: "eye", keep: true, check: () => ST.layerOn[k], on: () => k === "anim" ? !!(ST.char || ST.clip) : !!ST.char, run: () => ST.showLayer(k, !ST.layerOn[k]) }));
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
      `<button class="mi" role="menuitem" data-c="${c.id}" ${ST.cmdOn(c) ? "" : "disabled"} title="${esc(c.tip || "")}">` +
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
  // khối giao diện của module (data-park = id chỗ cất) phải luôn nằm trong trang: cất lại trước khi thay nội dung vùng
  const park = el => { [...el.children].forEach(c => { const s = c.dataset && c.dataset.park && document.getElementById(c.dataset.park); if (s) s.appendChild(c); }); };
  const mount = (el, n) => { if (el.firstChild === n && el.childNodes.length === 1) return; park(el); el.replaceChildren(n); };
  const fill = (el, html) => { park(el); el.innerHTML = html; };
  function renderBars() {
    const w = ST.WS[ST.ws] || {};
    document.body.className = document.body.className.replace(/(^|\s)(ws|fx)-[\w-]+/g, " ").trim() + " ws-" + ST.ws + " fx-" + ST.focus;
    const sm = typeof w.shelf === "string" && w.shelf[0] === "@" ? ST.mods[w.shelf.slice(1)] : null;   // khối shelf của module (vd thanh công cụ Pose Lab)
    document.body.classList.toggle("shelf-mod", !!sm);
    if (sm) { const n = sm.shelfNode && sm.shelfNode(); if (n) mount($("shelf"), n); else fill($("shelf"), '<span class="sub" style="padding:0 10px">' + esc(sm.shelfMsg ? sm.shelfMsg() : "") + "</span>"); $("shelf").dataset.mod = w.shelf.slice(1); }
    else { fill($("shelf"), strip(w.shelf)); $("shelf").dataset.mod = ""; }
    $("toolbox").innerHTML = strip(w.tools) + (w.modes ? '<span class="gap"></span>' + strip(w.modes) : "");
    $("wstabs").innerHTML = Object.values(ST.WS).map(x => `<button role="tab" aria-selected="${x.id === ST.ws}" class="${x.id === ST.ws ? "on" : ""}" data-ws="${x.id}" title="Workspace ${esc(x.label)}">${ic(x.icon)}<span>${esc(x.label)}</span></button>`).join("");
  }
  ["shelf", "toolbox"].forEach(k => $(k).addEventListener("click", e => { const b = e.target.closest("[data-c]"); if (b && !b.disabled) ST.run(b.dataset.c); }));
  // bấm vào khối của module (shelf / timeline / panel dock) = làm việc với module đó → focus
  const focusFrom = el => el.addEventListener("pointerdown", () => { const m = el.dataset.mod; if (m && ST.focus !== m) ST.setFocus(m); }, true);
  $("wstabs").addEventListener("click", e => { const b = e.target.closest("[data-ws]"); if (b) ST.setWS(b.dataset.ws); });

  // ---------------------------------------------------------------- Outliner (module trả các dòng)
  // dòng = mesh + cây khớp của nhân vật ở cấp đầu, rồi nút Rig và Anim. W3c: cây khớp dùng chung cho General / Rig / Anim
  // (bấm khớp = chọn ở chế độ đang sửa); nút Rig / Anim không lặp lại cây riêng (Anim có cây riêng khi không có nhân vật).
  let renaming = null, olRows = [];
  const LAYER_NODES = [["rig", "rig", "Rig", "rig"], ["anim", "pose", "Anim", "pose"]];
  function outlineRows() {
    const rows = [], ms = ST.mods.mesh;
    const fm = ST.mod(), jointMode = ST.focus !== "mesh" && fm.hasJoint, cur = jointMode && fm.curJoint ? fm.curJoint() : null;
    if (ms && ms.outline) ms.outline().forEach(r => {
      const j = typeof r.id === "string" && r.id.startsWith("j:") ? r.id.slice(2) : null;
      if (j && jointMode) rows.push(Object.assign({}, r, { m: "mesh", sel: cur === j, dim: !fm.hasJoint(j), del: false }));   // khớp: theo chế độ đang sửa
      else rows.push(Object.assign({}, r, { m: "mesh", dim: !ST.layerOn.scene }));
    });
    const sharedTree = !!(ST.mods.skel && ST.mods.skel.joints.length);
    LAYER_NODES.forEach(([L, mid, label, icon]) => {
      const m = ST.mods[mid]; if (!m || !(L === "anim" ? (ST.char || ST.clip) : ST.char)) return;
      const open = ST.pref.get("ol:open:" + L, false), lay = ST.LAYER_OF[mid], on = ST.layerOn[lay];
      const ownTree = !(sharedTree || L === "rig");   // W3c: chỉ Anim không có nhân vật mới có cây riêng
      rows.push({ id: "@" + L, m: mid, node: L, d: 0, label: m.nodeLabel ? m.nodeLabel() : label, icon, vis: L === "rig" ? undefined : on, fold: ownTree ? (open ? 0 : 1) : undefined, act: ST.focus === mid,
        tip: L === "rig" ? "Bấm: sửa rig của nhân vật (khớp, skin, thử khớp)" : "Bấm: làm việc với lớp " + label + " · mắt: bật lớp (Shift: hiện chồng)" });
      if (!open || !ownTree) return;
      const kids = m.loaded && m.loaded() && m.outline ? m.outline() : null;
      if (kids) kids.forEach(r => rows.push(Object.assign({}, r, { m: mid, d: (r.d || 0) + 1, dim: !on })));
      else rows.push({ id: "@" + L + ":hint", m: mid, d: 1, label: m.loadMsg ? m.loadMsg() : "Chưa nạp: bấm mắt để nạp", grp: true });
    });
    return rows;
  }
  function renderOutliner() {
    const rows = olRows = outlineRows();
    $("olBody").innerHTML = rows.map(r => `<div class="olr ${r.grp ? "grp" : ""} ${r.sel ? "sel" : ""} ${r.act ? "act" : ""} ${r.dim ? "dim" : ""} ${r.node ? "node" : ""}" style="--d:${r.d || 0}" data-id="${esc(r.id)}" data-m="${esc(r.m || "")}">` +
      (r.fold !== undefined ? `<button data-a="fold" class="fold" title="${r.fold ? "Mở" : "Gập"}" aria-label="${r.fold ? "Mở" : "Gập"}" aria-expanded="${!r.fold}">${r.fold ? "▸" : "▾"}</button>` : '<span class="fold"></span>') +
      `<span class="nm" title="${esc(r.tip || r.label)}${r.rename ? " · bấm đúp để đổi tên" : ""}">${r.icon ? ic(r.icon) : ""}${renaming === r.m + "|" + r.id ? `<input id="olRn" value="${esc(r.label)}">` : `<span class="tx">${esc(r.label)}</span>`}</span>` +
      (r.count !== undefined ? `<small>${esc(r.count)}</small>` : "") + (r.del ? `<button data-a="del" class="del" title="Xoá" aria-label="Xoá">${ic("trash")}</button>` : "") +
      (r.lock !== undefined ? `<button data-a="lock" class="lk ${r.lock ? "on" : "off"}" title="Khoá: không chọn, không sửa" aria-label="Khoá">${ic(r.lock ? "lock" : "unlock")}</button>` : "") +
      (r.vis !== undefined ? `<button data-a="vis" class="${r.vis ? "" : "off"}" title="Ẩn / hiện" aria-label="Ẩn hoặc hiện">${ic(r.vis ? "eye" : "eyeoff")}</button>` : "") + `</div>`).join("") ||
      '<div class="sub" style="padding:8px 10px">Trống.</div>';
  }
  const olB = $("olBody");
  const rowOf = el => olRows.find(x => String(x.id) === el.dataset.id && (x.m || "") === el.dataset.m);
  olB.addEventListener("click", e => {
    const el = e.target.closest(".olr"), b = e.target.closest("[data-a]"); if (!el || e.target.closest("input")) return;
    const r = rowOf(el), a = b ? b.dataset.a : "pick"; if (!r || (r.grp && !b)) return;
    if (r.node) {   // nút lớp Rig / Anim
      if (a === "fold") ST.pref.set("ol:open:" + r.node, !ST.pref.get("ol:open:" + r.node, false));
      else if (a === "vis") { const lay = ST.LAYER_OF[r.m]; ST.showLayer(lay, !ST.layerOn[lay], !e.shiftKey); }
      else ST.setFocus(r.m);
      ST.refresh(); return;
    }
    const m = ST.mods[r.m]; if (!m) return;
    const j = r.m === "mesh" && typeof r.id === "string" && r.id.startsWith("j:") ? r.id.slice(2) : null;
    if (j && a === "pick" && ST.focus !== "mesh" && ST.mod().selectJoint) {   // W3c: khớp trong cây chung → chọn ở chế độ đang sửa
      const fm = ST.mod();
      if (fm.hasJoint(j)) { ST.jsel = j; Promise.resolve(fm.selectJoint(j)).then(() => ST.refresh()); return; }
      ST.toast(j + " không có ở " + ({ rig: "bước Rig này", pose: "model anim này" }[ST.focus] || ST.focus) + " (dòng mờ). Bấm một mesh để về General."); return;
    }
    if (a !== "vis" && a !== "fold" && a !== "lock") ST.setFocus(r.m);
    if (m.olAct) m.olAct(r.id, a, e); ST.refresh();
  });
  olB.addEventListener("dblclick", e => { const el = e.target.closest(".olr"); if (!el || e.target.closest("button")) return; const r = rowOf(el); if (!r || !r.rename) return; renaming = r.m + "|" + r.id; renderOutliner(); const i = $("olRn"); if (i) { i.focus(); i.select(); } });
  const commitRn = (i, ok) => { const k = renaming; renaming = null; if (!k) return; const j = k.indexOf("|"), m = ST.mods[k.slice(0, j)]; if (ok && m && m.olAct) m.olAct(k.slice(j + 1), "rename", null, i.value.trim()); ST.refresh(); };
  olB.addEventListener("keydown", e => { if (e.target.id !== "olRn") return; e.stopPropagation(); if (e.key === "Enter") commitRn(e.target, true); else if (e.key === "Escape") commitRn(e.target, false); });
  olB.addEventListener("focusout", e => { if (e.target.id === "olRn" && renaming !== null) commitRn(e.target, true); });

  // ---------------------------------------------------------------- dock: tab Channel Box + panel của module
  const attrB = $("attrBody");
  // tab = panel trong ST.PANELS ("<module>:<tab>"); danh sách mặc định của workspace, Cửa sổ → Panel để thêm / bớt
  const tabList = () => (ST.pref.get("tabs:" + ST.ws, null) || (ST.WS[ST.ws] || {}).tabs || []).filter(id => ST.PANELS[id] && (!ST.PANELS[id].mod || ST.mods[ST.PANELS[id].mod]));
  const curTab = () => { const L = tabList(), t = ST.pref.get("tab:" + ST.ws, L[0]); return L.includes(t) ? t : L[0]; };
  const panelOf = t => { const p = ST.PANELS[t] || {}; return { m: p.mod ? ST.mods[p.mod] : null, mid: p.mod || "", sub: t && t.includes(":") ? t.slice(t.indexOf(":") + 1) : t }; };
  ST.tabs = tabList; ST.curTab = curTab;
  ST.showTab = id => { if (tabList().includes(id) && curTab() !== id) { ST.pref.set("tab:" + ST.ws, id); ST.refresh(); } };   // module chọn tab của nó nếu workspace đang có
  function renderAttr(force) {
    const L = tabList(), t = curTab(), mixed = new Set(L.map(x => ST.PANELS[x].mod || "")).size > 1;
    $("attrTabs").innerHTML = L.map(id => { const p = ST.PANELS[id]; return `<button role="tab" data-t="${esc(id)}" class="${id === t ? "on" : ""}" title="${esc(p.label)}">${esc(mixed && p.mod ? p.label : p.short || p.label)}</button>`; }).join("");
    if (!force && attrB.contains(document.activeElement) && /INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)) return;
    if (!t) { fill(attrB, '<div class="sub" style="padding:10px">Không có panel. Cửa sổ → Panel để thêm.</div>'); attrB.dataset.key = ""; attrB.dataset.mod = ""; return; }
    if (t === "channel") { park(attrB); attrB.dataset.key = ""; attrB.dataset.mod = ""; return chRender(); }
    const { m, mid, sub } = panelOf(t); attrB.dataset.mod = ST.PANELS[t].nofocus ? "" : mid; if (!m) return;
    if (m.panelNode) { const n = m.panelNode(sub); if (n) { mount(attrB, n); attrB.dataset.key = ""; return; } }
    const key = t + ":" + (m.panelKey ? m.panelKey() : "");
    if (m.panelStatic && !force && attrB.dataset.key === key) return;   // module tự vẽ lại panel của nó (vd lõi Rig)
    fill(attrB, m.panel ? m.panel(sub) : ""); attrB.dataset.key = key;
    if (m.panelMounted) m.panelMounted(sub);
  }
  $("attrTabs").addEventListener("click", e => { const b = e.target.closest("[data-t]"); if (!b) return; ST.pref.set("tab:" + ST.ws, b.dataset.t); const p = ST.PANELS[b.dataset.t]; if (p && p.mod && !p.nofocus) ST.setFocus(p.mod); renderAttr(true); });
  ["click", "change", "input"].forEach(ev => attrB.addEventListener(ev, e => { const t = curTab(); if (t === "channel") return; const { m, sub } = panelOf(t), f = m && m["panel_" + ev]; if (f) f.call(m, e, sub); }));
  focusFrom(attrB); focusFrom($("shelf")); focusFrom($("timeline"));

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
  // timeline: của module có timeline (Pose), không phụ thuộc focus
  function renderTimeline() {
    const mid = (ST.WS[ST.ws] || {}).timeline || "pose", m = ST.mods[mid], n = m && m.timelineNode && m.timelineNode();
    $("timeline").dataset.mod = n ? mid : ""; document.body.classList.toggle("tl-mod", !!n);
    if (n) { mount($("timeline"), n); return; }
    fill($("timeline"), '<span class="sub">Timeline: mở anim (Animate → Đổi anim…) hoặc bật lớp Anim</span><div class="tlbar"></div>');
  }
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
    const rows = [...ST.cmds.values()].filter(c => c.key && !c.hidden), ML = { mesh: "khi đang sửa mesh / xương", rig: "khi đang sửa rig", pose: "khi đang sửa anim" };
    ST.dialog("Phím tắt", `<div class="keys">${rows.map(c => `<kbd>${esc((Array.isArray(c.key) ? c.key : [c.key]).map(ST.keyLabel).join(" / "))}</kbd><span>${esc(c.label)}${c.mod && ML[c.mod] && !c.keep ? ` <span class="sub">(${esc(ML[c.mod])})</span>` : ""}</span>`).join("")}</div>`);
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
    // lệnh của module đang focus trước, rồi lệnh chung; phím của module khác không chạy (1–5, B, I trùng giữa Mesh / Rig)
    const c = all.find(c => c.mod === ST.focus) || all.find(c => !c.mod || c.keep);
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
  ST.on("focus", () => ST.refresh());
  ST.on("init", () => { const t = ST.pref.get("theme", null); if (t) document.documentElement.dataset.theme = t; });
})();
