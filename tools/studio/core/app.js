// AI Anim Studio — lõi: sự kiện, icon, lịch sử undo chung, sổ lệnh, kho lưu, workspace, khởi động.
// Mọi module (mesh, rig, pose…) đăng ký lệnh vào ST.cmd và tự khai báo vào ST.mods. Workspace (workspaces.js) chỉ là cấu hình:
// module nào nhận chuột, toolbox/shelf có lệnh nào, dock có tab nào, panel nào hiện.
(function () {
  const ST = window.ST = { mods: {}, ws: null, tool: "sel", char: null, clip: null };
  ST.$ = id => document.getElementById(id);
  ST.esc = t => String(t == null ? "" : t).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  ST.slug = s => String(s || "page").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "").slice(0, 80) || "page";

  // ---- sự kiện
  const L = {};
  ST.on = (n, f) => { (L[n] || (L[n] = [])).push(f); };
  ST.emit = (n, ...a) => { (L[n] || []).forEach(f => { try { f(...a); } catch (e) { console.error(e); } }); };

  // ---- cài đặt riêng máy này
  ST.pref = {
    get(k, d) { try { const v = localStorage.getItem("studio:" + k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem("studio:" + k, JSON.stringify(v)); } catch (e) {} },
  };

  // ---- icon (nét 24×24, cùng kiểu với các Lab)
  ST.IC = {
    obj: '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12l8-4.5M12 12v9M12 12L4 7.5"/>',
    vert: '<circle cx="6" cy="6" r="1.8"/><circle cx="18" cy="8" r="1.8"/><circle cx="10" cy="18" r="1.8"/><path d="M7.5 7l9 .8M17 9.5l-6 7M8.5 16.5L6.5 8" opacity=".5"/>',
    face: '<path d="M4 19L12 4l8 15z"/>',
    island: '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 12l9 5 9-5M3 16l9 5 9-5" opacity=".6"/>',
    sel: '<path d="M6 4l11 6-5 1.5L10 17z"/>', move: '<path d="M12 3v18M3 12h18M12 3l-3 3M12 3l3 3M12 21l-3-3M12 21l3-3M3 12l3-3M3 12l3 3M21 12l-3-3M21 12l-3 3"/>',
    rot: '<path d="M20 12a8 8 0 11-3-6.2"/><path d="M20 4v5h-5"/>', scl: '<path d="M5 19L19 5M13 5h6v6M5 13v6h6"/>',
    free: '<rect x="6" y="6" width="12" height="12" stroke-dasharray="2 2"/><rect x="3" y="3" width="4" height="4"/><rect x="17" y="3" width="4" height="4"/><rect x="3" y="17" width="4" height="4"/><rect x="17" y="17" width="4" height="4"/>',
    undo: '<path d="M9 14L4 9l5-5"/><path d="M4 9h11a5 5 0 010 10h-3"/>', redo: '<path d="M15 14l5-5-5-5"/><path d="M20 9H9a5 5 0 000 10h3"/>',
    wire: '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9" opacity=".6"/>', frame: '<path d="M4 8V5h3M17 5h3v3M20 16v3h-3M7 19H4v-3"/><circle cx="12" cy="12" r="2"/>',
    framesel: '<path d="M4 8V5h3M17 5h3v3M20 16v3h-3M7 19H4v-3"/><path d="M9 9h6v6H9z"/>',
    eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>', eyeoff: '<path d="M3 3l18 18M10.6 6.1A9.8 9.8 0 0112 6c6 0 10 6 10 6a17 17 0 01-3.2 3.7M6.4 7.5C3.6 9.3 2 12 2 12s4 7 10 7a9.7 9.7 0 004.1-.9"/>',
    lock: '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/>', unlock: '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 017.6-1.7"/>',
    trash: '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/>', plus: '<path d="M12 5v14M5 12h14"/>', orbit: '<path d="M12 3a9 9 0 109 9"/><path d="M12 3l3 3M12 3L9 6"/><circle cx="12" cy="12" r="2.4"/>',
    box: '<path d="M5 8V5h3M16 5h3v3M19 16v3h-3M8 19H5v-3"/><path d="M10 12h4"/>', cut: '<circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M7.5 16L18 4M16.5 16L6 4"/>',
    merge: '<path d="M4 6h5v12H4zM15 6h5v12h-5z"/><path d="M9 12h6M12 9l3 3-3 3"/>', weld: '<path d="M4 12h6M14 12h6"/><circle cx="12" cy="12" r="2"/>', flip: '<path d="M4 8h13l-3-3M20 16H7l3 3"/>',
    smooth: '<path d="M3 15c3-8 6 8 9 0s6 8 9 0"/>', copy: '<rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 012-2h9"/>', floor: '<path d="M3 19h18M7 19V9l5-5 5 5v10"/>',
    clean: '<path d="M5 19l9-9M14 10l-2-5 5 2 2 5-5-2z"/>', height: '<path d="M12 3v18M8 7l4-4 4 4M8 17l4 4 4-4"/>', flipx: '<path d="M12 3v18M7 8L3 12l4 4zM17 8l4 4-4 4z"/>', save: '<path d="M5 4h11l3 3v13H5z"/><path d="M8 4v5h7V4M8 20v-6h8v6"/>',
    all: '<path d="M5 12.5l4.5 4.5L19 7"/>', none: '<path d="M6 6l12 12M18 6L6 18"/>', invert: '<path d="M4 7h14l-3-3M20 17H6l3 3"/>', grow: '<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="8" opacity=".5"/>',
    sym: '<path d="M12 3v18" stroke-dasharray="2 2"/><path d="M9 8l-5 4 5 4zM15 8l5 4-5 4z"/>', soft: '<circle cx="12" cy="12" r="2.5"/><circle cx="12" cy="12" r="6" opacity=".6"/><circle cx="12" cy="12" r="9.5" opacity=".3"/>',
    front: '<path d="M4 12h16"/><path d="M12 4a8 8 0 010 16" opacity=".5"/><circle cx="12" cy="12" r="2"/>',
    view4: '<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/>',
    view1: '<rect x="3" y="3" width="18" height="18" rx="1.5"/>', grid: '<path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>', touch: '<path d="M9 11V5a1.6 1.6 0 013.2 0v5l3.3.7a2 2 0 011.5 2.3L16.4 19a2 2 0 01-2 1.6H11a2 2 0 01-1.6-.8L6 14.6a1.5 1.5 0 012.2-1.9z"/>',
    mesh: '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>', rig: '<circle cx="12" cy="5" r="2.3"/><path d="M12 8v7M6.5 10.5L12 8l5.5 2.5M9 21l3-6 3 6"/>',
    pose: '<circle cx="13" cy="4.5" r="2"/><path d="M13 7l-1 6 3 3v5M12 13l-4 2-1 6M13 8.5l4 2 2-3M13 8.5L8 9l-3-2"/>', open: '<path d="M3 7h6l2 2h10v10H3z"/>', ext: '<path d="M14 4h6v6M20 4l-9 9M18 14v6H4V6h6"/>',
    search: '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>', keys: '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M7 14h10"/>',
    joint: '<circle cx="12" cy="12" r="3.2"/><path d="M12 3v5.5M12 15.5V21M3 12h5.5M15.5 12H21" opacity=".6"/>',
    s1: '<text x="12" y="17" text-anchor="middle" font-size="14" font-family="sans-serif" stroke="none" fill="currentColor">1</text>',
    s2: '<text x="12" y="17" text-anchor="middle" font-size="14" font-family="sans-serif" stroke="none" fill="currentColor">2</text>',
    s3: '<text x="12" y="17" text-anchor="middle" font-size="14" font-family="sans-serif" stroke="none" fill="currentColor">3</text>',
    s4: '<text x="12" y="17" text-anchor="middle" font-size="14" font-family="sans-serif" stroke="none" fill="currentColor">4</text>',
    s5: '<text x="12" y="17" text-anchor="middle" font-size="14" font-family="sans-serif" stroke="none" fill="currentColor">5</text>',
    home: '<path d="M4 11l8-7 8 7v9h-5v-6H9v6H4z"/>',
    reset: '<path d="M4 12a8 8 0 108-8H8M8 1L5 4l3 3"/>', export: '<path d="M12 3v12M8 7l4-4 4 4M4 15v5h16v-5"/>', import: '<path d="M12 15V3M8 11l4 4 4-4M4 15v5h16v-5"/>',
  };
  ST.ic = n => `<svg class="i" viewBox="0 0 24 24" aria-hidden="true">${ST.IC[n] || ""}</svg>`;

  // ---- toast + hộp thoại nhỏ
  let toastT = 0;
  ST.toast = t => { const el = ST.$("toast"); el.textContent = t; el.classList.add("show"); clearTimeout(toastT); toastT = setTimeout(() => el.classList.remove("show"), 2600); };
  ST.dialog = (title, html, onReady) => {
    const d = ST.$("dialog"); ST.$("dlgT").textContent = title; ST.$("dlgB").innerHTML = html; d.classList.add("show");
    if (onReady) onReady(ST.$("dlgB"));
  };
  ST.closeDialog = () => ST.$("dialog").classList.remove("show");
  ST.ask = (title, label, value) => new Promise(res => {
    ST.dialog(title, `<div class="row"><label>${ST.esc(label)}</label><input type="number" id="askIn" value="${ST.esc(value)}" step="any"><button class="on" id="askOk">OK</button><button id="askNo">Huỷ</button></div>`, b => {
      const i = b.querySelector("#askIn"); i.focus(); i.select();
      const done = v => { ST.closeDialog(); res(v); };
      b.querySelector("#askOk").onclick = () => done(i.value); b.querySelector("#askNo").onclick = () => done(null);
      i.onkeydown = e => { e.stopPropagation(); if (e.key === "Enter") done(i.value); if (e.key === "Escape") done(null); };
    });
  });

  // ---- lịch sử undo/redo chung. owner = {snap(), restore(s)} của module đang sửa.
  ST.hist = {
    U: [], R: [], max: 60,
    push(owner, label) { this.U.push({ owner, label, s: owner.snap() }); if (this.U.length > this.max) this.U.shift(); this.R = []; ST.emit("hist"); },
    undo() { const m = ST.mod(); if (m.undo) { m.undo(); ST.emit("hist"); return; } const e = this.U.pop(); if (!e) return; this.R.push({ owner: e.owner, label: e.label, s: e.owner.snap() }); e.owner.restore(e.s); ST.emit("hist"); ST.toast("Hoàn tác: " + e.label); },
    redo() { const m = ST.mod(); if (m.undo) return; const e = this.R.pop(); if (!e) return; this.U.push({ owner: e.owner, label: e.label, s: e.owner.snap() }); e.owner.restore(e.s); ST.emit("hist"); ST.toast("Làm lại: " + e.label); },
  };

  // ---- sổ lệnh: một lệnh gọi được từ menu, shelf, toolbox, phím tắt, tìm lệnh (F3), cầu nối AI — ở mọi workspace
  // {id, label, menu, sep, icon, key, mod, keep, global, on(), check(), run(), tip}
  // mod = module chủ: chạy lệnh thì focus sang module đó (trừ keep: lệnh hiển thị / bật tắt), phím tắt ưu tiên module đang focus.
  ST.cmds = new Map();
  ST.cmd = def => { ST.cmds.set(def.id, def); return def; };
  ST.cmdOn = c => !!c && (!c.on || !!c.on());
  ST.run = (id, ...a) => {
    const c = ST.cmds.get(id); if (!c) return;
    if (c.mod && !c.keep && ST.focus !== c.mod && ST.mods[c.mod]) ST.setFocus(c.mod);
    if (!ST.cmdOn(c)) return;
    try { c.run(...a); } catch (e) { console.error(e); ST.toast("Lỗi: " + (e.message || e)); }
    ST.refresh();
  };
  ST.keyLabel = k => (Array.isArray(k) ? k[0] : k || "").split("+").map(s => s.length === 1 ? s.toUpperCase() : s[0].toUpperCase() + s.slice(1)).join("+");

  // ---- kho lưu: Home server /api/store/<ns>/… (file thật trong work/store), không có thì localStorage
  const enc = encodeURIComponent;
  ST.store = ns => {
    const url = p => "/api/store/" + enc(ns) + "/" + p.split("/").map(enc).join("/"), lk = p => "studio-store:" + ns + "/" + p;
    return {
      ns,
      async get(p) {
        try { const r = await fetch(url(p)); if (r.ok) { const j = await r.json(); return j.exists ? j.data : null; } } catch (e) {}
        try { return JSON.parse(localStorage.getItem(lk(p)) || "null"); } catch (e) { return null; }
      },
      async set(p, data) {
        try { const r = await fetch(url(p), { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) }); if (r.ok) return "disk"; } catch (e) {}
        localStorage.setItem(lk(p), JSON.stringify(data)); return "browser";
      },
      async del(p) {
        try { localStorage.removeItem(lk(p)); } catch (e) {}
        try { await fetch(url(p), { method: "DELETE" }); } catch (e) {}
      },
    };
  };
  ST.download = (name, text, type) => {
    const blob = new Blob([text], { type: type || "text/plain" }), u = URL.createObjectURL(blob), a = document.createElement("a");
    a.href = u; a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 4000);
  };
  ST.saveState = (text, cls) => { const el = ST.$("stSave"); el.textContent = text; el.className = cls || ""; };

  // ---- focus: module đang được sửa (mesh = mesh + xương, rig, pose). Chuột, gizmo, Channel Box, phím, Hoàn tác theo focus.
  // Module: focusIn() / focusOut(), layer(on) (hiện / ẩn đồ của nó, nạp lười), hit(x, y, pane) → click trúng đồ của nó không.
  ST.focus = null;
  ST.mod = () => ST.mods[ST.focus] || {};
  ST.setTool = t => { ST.tool = t; ST.emit("tool", t); ST.refresh(); };
  // W3b: Rig không còn là lớp riêng mà là chế độ sửa của nhân vật trong Cảnh (cùng lớp scene): đang focus Rig thì lõi Rig vẽ nhân vật,
  // rời Rig thì Cảnh vẽ (dùng khớp + skin của Rig). Trên màn hình chỉ một nhân vật.
  ST.LAYER_OF = { mesh: "scene", rig: "scene", pose: "anim" };
  ST.MOD_OF = { scene: "mesh", anim: "pose" };
  ST.LAYER_ALIAS = { rig: "scene" };   // link / lệnh cũ
  ST.setFocus = id => {
    if (!ST.mods[id] || id === ST.focus) return;
    const old = ST.mod(); if (old.focusOut) old.focusOut();
    ST.focus = id;
    const L = ST.LAYER_OF[id]; if (L && !ST.layerOn[L]) ST.showLayer(L, true);   // không sửa được lớp đang ẩn
    const m = ST.mod(); if (m.focusIn) m.focusIn();
    ST.emit("focus", id); ST.refresh();
  };
  // ---- lớp: ba bản của cùng nhân vật (cảnh mesh + xương, rig đang dựng, model của anim). Bật một lớp thì hai lớp kia ẩn (solo),
  // solo=false để hiện chồng. Không phụ thuộc workspace.
  ST.layerOn = { scene: true, anim: false };
  ST.showLayer = (id, on, solo) => {
    id = (ST.LAYER_ALIAS || {})[id] || id;
    if (!(id in ST.layerOn)) return;
    const ch = [];
    const set = (k, v) => { if (ST.layerOn[k] !== v) { ST.layerOn[k] = v; ch.push(k); } };
    set(id, !!on);
    if (on && solo !== false) Object.keys(ST.layerOn).forEach(k => { if (k !== id) set(k, false); });
    ch.forEach(k => { const m = ST.mods[ST.MOD_OF[k]]; if (m && m.layer) m.layer(ST.layerOn[k]); });
    if (ch.length) { ST.emit("layer", ch); ST.refresh(); }
  };
  // ---- workspace: chỉ là bố cục (panel, shelf, hộp công cụ, timeline) + module focus mặc định
  ST.setWS = id => {
    if (!ST.WS[id] || id === ST.ws) return;
    ST.ws = id; ST.pref.set("ws", id);
    const u = new URL(location.href); u.searchParams.set("ws", id); history.replaceState(null, "", u);
    ST.emit("ws", id);
    if (ST.WS[id].focus) ST.setFocus(ST.WS[id].focus);
    ST.refresh();
  };
  ST.refresh = () => ST.emit("ui");

  // ---- khởi động: /studio/<nhân vật>?clip=…&ws=…
  let readyRes; ST.ready = new Promise(r => readyRes = r);   // xong khi nhân vật (nếu có) đã nạp
  ST.boot = async () => {
    const parts = location.pathname.replace(/^\/studio\/?/, "").split("/").filter(Boolean), q = new URLSearchParams(location.search);
    ST.clip = q.get("clip") || null;
    ST.emit("init");
    const wsOf = x => ST.WS[x] ? x : (ST.WS_ALIAS || {})[x] || null;   // ?ws=mesh cũ → general
    let cid = parts[0]; const wsId = wsOf(q.get("ws")) || (!cid ? "general" : wsOf(ST.pref.get("ws", "general")) || "general");
    ST.setWS(wsId);
    if (ST.clip) ST.setFocus("pose");   // ?clip=… (từ Home): mở thẳng lớp Anim, workspace nào cũng vậy
    if (!ST.focus) ST.setFocus("mesh");
    if (!cid) {   // mở ở "/" hoặc Tệp → Mới: cảnh trống (như Maya / Blender), chọn Mở nhân vật hoặc Nhập FBX
      document.title = "Cảnh mới · Studio"; ST.$("charName").textContent = "Cảnh mới";
      ST.saveState("Cảnh trống"); ST.emit("empty"); ST.refresh(); readyRes(); return;
    }
    ST.saveState("Đang tải " + cid + "…");
    try {
      const r = await fetch("/api/char/" + enc(cid)); if (!r.ok) throw new Error((await r.json()).error || r.status);
      ST.char = await r.json();
    } catch (e) { ST.saveState("Không tải được nhân vật: " + (e.message || e), "err"); readyRes(); ST.run("file.open"); return; }
    ST.pref.set("char", ST.char.id); ST.emit("filled");
    document.title = ST.char.name + " · Studio";
    ST.$("charName").textContent = ST.char.name + (ST.clip ? " · " + ST.clip : "");
    await Promise.all((L.char || []).map(f => Promise.resolve().then(() => f(ST.char)).catch(e => console.error(e))));
    Object.keys(ST.layerOn).forEach(k => { const m = ST.mods[ST.MOD_OF[k]]; if (m && m.layer && ST.layerOn[k]) m.layer(true); });
    const m = ST.mod(); if (m.focusIn) m.focusIn();
    ST.emit("loaded"); ST.refresh(); readyRes();
  };
})();
