// AI Anim Studio — module Rig (S3, lớp Rig): lõi Rig Lab (modules/rig_engine.js, sinh từ template bằng port_rig.py) chạy trong viewport chung.
// Dùng được ở mọi workspace (W1): Năm bước của Rig Lab là năm panel dock (1 Mesh · 2 Khớp · 3 Xương · 4 Skin · 5 Thử khớp). Chọn khớp bằng click / khung, dời bằng gizmo chung,
// undo chung, Outliner = cây xương đang dựng, Channel Box = toạ độ khớp. Lưu cùng kho với Rig Lab cũ (<nhân vật>_rig_lab).
(function () {
  const V = ST.view, esc = ST.esc, ic = ST.ic;
  const M = ST.mods.rig = { id: "rig", panelStatic: true };
  let eng = null, key = null, root = null, state = "none", err = "", live = null, raw = {}, open = null;
  const cvEl = ST.$("cv");
  const TOOL2MODE = { sel: "select", move: "translate", rot: "rotate", scl: "scale" }, MODE2TOOL = { select: "sel", translate: "move", rotate: "rot", scale: "scl" };
  const step = () => eng ? eng.get().step : 0;
  const act = () => ST.focus === "rig" && ST.layerOn.scene;   // lõi Rig nhận chuột / gizmo khi đang focus và lớp Rig hiện
  // tab dock theo bước: workspace có tab bước đó thì chọn; chỉ có một tab Rig (vd General) thì tab đó đổi sang bước mới
  const syncTab = n => {
    const id = "rig:s" + n, L = ST.tabs ? ST.tabs() : [], cur = ST.curTab ? ST.curTab() : null;
    if (L.includes(id)) return ST.showTab(id);
    const old = cur && cur.startsWith("rig:s") ? cur : L.find(x => x.startsWith("rig:s"));
    if (old) { ST.pref.set("tabs:" + ST.ws, L.map(x => x === old ? id : x)); if (cur === old) ST.pref.set("tab:" + ST.ws, id); }
  };

  // ---- mesh đã sửa ở workspace General → DATA (giống MESHLINK của Rig Lab: thay theo tên, dời landmark nếu thân đổi cỡ / vị trí)
  const bbox = a => { const mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9]; for (let i = 0; i < a.length; i += 3) for (let k = 0; k < 3; k++) { mn[k] = Math.min(mn[k], a[i + k]); mx[k] = Math.max(mx[k], a[i + k]); } return { mn, mx }; };
  // skin khách đánh theo số thứ tự đỉnh của mesh gốc; mesh sửa ở General có thể đổi thứ tự / số đỉnh (hàn, tách, gộp, nhập lại):
  // mỗi đỉnh mới lấy trọng số của đỉnh gốc gần nhất (đưa về toạ độ gốc nếu thân đã dời / đổi cỡ)
  function remapW(W, oldV, newV, c0, c1, f) {
    const n0 = oldV.length / 3, n1 = newV.length / 3, cell = 2, H = new Map(), key = (x, y, z) => x + "," + y + "," + z;
    for (let i = 0; i < n0; i++) { const k = key(Math.floor(oldV[3 * i] / cell), Math.floor(oldV[3 * i + 1] / cell), Math.floor(oldV[3 * i + 2] / cell)); (H.get(k) || H.set(k, []).get(k)).push(i); }
    const per = Array.from({ length: n0 }, () => []);
    for (const b in W) { const [ix, ws] = W[b]; ix.forEach((v, k) => { if (v < n0) per[v].push([b, ws[k]]); }); }
    const out = {};
    for (let j = 0; j < n1; j++) {
      const x = c0[0] + (newV[3 * j] - c1[0]) / f, y = c0[1] + (newV[3 * j + 1] - c1[1]) / f, z = c0[2] + (newV[3 * j + 2] - c1[2]) / f;
      const gx = Math.floor(x / cell), gy = Math.floor(y / cell), gz = Math.floor(z / cell); let best = -1, bd = Infinity;
      for (let r = 1; r <= 8 && best < 0; r *= 2)
        for (let dx = -r; dx <= r; dx++) for (let dy = -r; dy <= r; dy++) for (let dz = -r; dz <= r; dz++) {
          const c = H.get(key(gx + dx, gy + dy, gz + dz)); if (!c) continue;
          for (const i of c) { const d = (oldV[3 * i] - x) ** 2 + (oldV[3 * i + 1] - y) ** 2 + (oldV[3 * i + 2] - z) ** 2; if (d < bd) { bd = d; best = i; } }
        }
      if (best >= 0) per[best].forEach(([b, w]) => { const o = out[b] || (out[b] = [[], []]); o[0].push(j); o[1].push(w); });
    }
    return out;
  }
  function meshApply(D) {
    const ms = ST.mods.mesh, at = ms.editAt && ms.editAt();
    window.__meshAt = null; window.__meshT = null;
    if (!at) return D;
    const by = {}; ms.objects().forEach(o => { if (o.vis) by[o.name] = { verts: Array.from(o.pos), tris: Array.from(o.idx) }; });
    const bn = D.body.name; if (!bn || !by[bn]) return D;
    const o0 = bbox(D.body.verts), o1 = bbox(by[bn].verts), f = (o1.mx[1] - o1.mn[1]) / Math.max(1e-6, o0.mx[1] - o0.mn[1]);
    const c0 = [(o0.mn[0] + o0.mx[0]) / 2, o0.mn[1], (o0.mn[2] + o0.mx[2]) / 2], c1 = [(o1.mn[0] + o1.mx[0]) / 2, o1.mn[1], (o1.mn[2] + o1.mx[2]) / 2];
    const T = p => [c1[0] + (p[0] - c0[0]) * f, c1[1] + (p[1] - c0[1]) * f, c1[2] + (p[2] - c0[2]) * f];
    const take = (o, m) => { o.verts = m.verts; o.tris = m.tris; };
    if (D.refW && Object.keys(D.refW).length) D.refW = remapW(D.refW, D.body.verts, by[bn].verts, c0, c1, f);   // skin khách theo VỊ TRÍ đỉnh, không theo số thứ tự
    take(D.body, by[bn]);
    (D.clothes || []).forEach(c => { if (by[c.name]) take(c, by[c.name]); });
    // prop đặt vào tay bằng xf (build_char.py, chars/<id>.json props): mesh trong kho vẫn ở gốc, dời lại như lúc dựng
    const xf = (v, m) => { if (!m) return v; const o = new Array(v.length); for (let i = 0; i < v.length; i += 3) for (let k = 0; k < 3; k++) o[i + k] = m[k] * v[i] + m[3 + k] * v[i + 1] + m[6 + k] * v[i + 2] + m[9 + k]; return o; };
    // kho đã dời prop vào tay (trùng bản trang) thì giữ nguyên, còn ở gốc FBX thì dời theo xf
    (D.props || []).forEach(p => { if (!by[p.name]) return; const v0 = p.verts.slice(0, 3); take(p, by[p.name]);
      if (p.xf && Math.hypot(p.verts[0] - v0[0], p.verts[1] - v0[1], p.verts[2] - v0[2]) > 1) p.verts = xf(p.verts, p.xf); });
    if (Math.abs(f - 1) > 1e-4 || c0.some((v, i) => Math.abs(v - c1[i]) > 1e-3)) {
      for (const k in D.auto.landmarks) D.auto.landmarks[k] = T(D.auto.landmarks[k]).map(v => +v.toFixed(3));
      if (D.auto.H) D.auto.H = +(D.auto.H * f).toFixed(3);
      (D.ref || []).forEach(b => { if (b.pos) b.pos = T(b.pos); });
      window.__meshT = { f, c0, c1 };
    }
    window.__meshAt = at;
    window.__meshLM = L => { const t = window.__meshT; if (!t) return L; const o = {}; for (const k in L) o[k] = Array.isArray(L[k]) && L[k].length === 3 ? [t.c1[0] + (L[k][0] - t.c0[0]) * t.f, t.c1[1] + (L[k][1] - t.c0[1]) * t.f, t.c1[2] + (L[k][2] - t.c0[2]) * t.f].map(v => +v.toFixed(3)) : L[k]; return o; };
    return D;
  }

  // ---- khớp của rig → kho (doc rig/skeleton) để workspace General vẽ / chọn / pose đúng bộ khớp đã dựng, không phải xương khách
  let skelT = 0;
  function saveSkel() {
    clearTimeout(skelT); skelT = setTimeout(async () => {
      if (!eng) return;
      const joints = eng.buildSkeleton().map(b => ({ name: b.name, parent: b.parent, pos: b.pos.map(v => +v.toFixed(3)) }));
      try { await ST.store(ST.rigNs()).set("rig/skeleton", { v: 1, source: "rig", at: new Date().toISOString(), joints }); ST.emit("rig:skeleton", joints); } catch (e) { console.error(e); }
    }, 300);
  }

  // ---- host: những gì lõi Rig cần từ Studio
  function makeHost(grp) {
    const me = { on: true }, downL = [];
    const store = ST.store(ST.rigNs());
    const db = { isLocal: true, doc: p => ({ get: async () => { const d = await store.get(p); return { exists: d != null, data: () => d }; },
      set: async d => { const w = await store.set(p, d); if (p === "rig/landmarks") saveSkel(); if (p === "rig/skin") ST.emit("rig:skin", d); return w; } }) };   // General dùng khớp + skin của rig
    const lmOwner = { snap: () => eng.snapStr(), restore: s => eng.applySnap(s) };
    const push = (owner, label, s) => { ST.hist.U.push({ owner, label, s }); if (ST.hist.U.length > ST.hist.max) ST.hist.U.shift(); ST.hist.R = []; ST.emit("hist"); };
    return {
      me, downL, root: grp, db, TM: V.TM,
      cam: () => V.active.cam,
      cv: { getBoundingClientRect: () => { const r = cvEl.getBoundingClientRect(), p = V.active.rect; return { left: r.left + p.x, top: r.top + p.y, width: p.w, height: p.h, right: r.left + p.x + p.w, bottom: r.top + p.y + p.h }; } },
      raycaster: (x, y, p) => V.raycaster(x, y, p), toScreen: (w, p) => V.toScreen(w, p),
      alive: () => me.on && act(),
      listen(t, f) { if (t === "pointerdown") downL.push(f); else cvEl.addEventListener(t, e => { if (me.on && act()) f(e); }); },
      placeGizmo(c, mode) { if (!me.on || !act()) return; if (!c) V.gizmo.detach(); else V.gizmo.place(c, grp, mode); },
      onMode(m) { const t = MODE2TOOL[m]; if (t && ST.tool !== t) { ST.tool = t; ST.refresh(); } },
      pushLM: before => push(lmOwner, "Rig: khớp", before),
      pushSkin: m => push({ snap: () => eng.skinSnapshotOf(m), restore: x => { eng.restoreSkin(x); eng.scheduleSkinSave(); } }, "Rig: skin", m),
      refresh: () => { if (eng && !onS6()) syncTab(step()); ST.refresh(); },   // tab dock theo bước của lõi (trừ khi đang ở panel 6 Vật lý)
    };
  }

  async function ensure() {
    if (!ST.char) { state = "none"; return; }
    const ms = ST.mods.mesh; if (ms.isDirty && ms.isDirty()) await ms.save();
    const k = ST.char.id + ":" + (ms.editAt ? ms.editAt() : "") + ":" + (ms.ver ? ms.ver() : 0);
    if (eng && key === k) return;
    dispose(); state = "loading"; ST.refresh();
    try {
      if (!raw[ST.char.id]) {
        const r = await fetch("/api/rigdata/" + encodeURIComponent(ST.char.id)), j = await r.json();
        if (!r.ok) { state = j.build ? "nodata" : "error"; err = j.build ? "" : (j.error || r.status); ST.refresh(); return; }
        raw[ST.char.id] = JSON.stringify(j);
      }
      const D = meshApply(JSON.parse(raw[ST.char.id]));
      const st = await ST.store(ST.rigNs()).get("rig/skeleton");
      if (st && st.source === "none") { D.ref = []; D.refW = {}; }   // đã xoá xương ở Outliner: rig lại từ mesh, không gợi ý xương / skin của FBX
      root = new THREE.Group(); root.name = "rig"; root.visible = act(); V.cm.add(root);
      const host = makeHost(root); live = host;
      eng = ST.rigEngine(D, host); key = k; ST.rigEng = () => eng; ST.rigRoot = () => root;   // lõi Rig cho script / Claude (studio_cmd)
      await eng.ready; state = "ready"; ST.rigSetup.bind(eng); if (!st || st.source !== "none") saveSkel();   // vừa xoá xương: chỉ hiện lại khi lưu khớp mới
      if (!open) open = new Set(ST.pref.get("rig:open:" + ST.char.id, null) || ["root", "Root_M", "Spine1_M", "Chest_M"]);
      eng.setMode(TOOL2MODE[ST.tool] || "select"); syncVis(); eng.syncScene(); root.visible = act();   // W3b: ẩn / hiện theo mesh của Cảnh
    } catch (e) { console.error(e); state = "error"; err = e.message || String(e); }
    ST.refresh();
  }
  function dispose() {
    if (live) live.me.on = false;
    if (root) { V.cm.remove(root); root.traverse(o => { if (o.geometry) o.geometry.dispose(); }); }
    V.gizmo.detach(); ST.rigSetup.unbind(); eng = null; root = null; live = null; key = null;
  }
  async function buildData() {
    state = "building"; ST.refresh();
    try {
      const r = await fetch("/api/rig/build", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: ST.char.id }) });
      const j = await r.json(); if (!j.ok) throw new Error(j.error);
      delete raw[ST.char.id]; key = null; await ensure(); ST.toast("Đã dựng dữ liệu rig cho " + ST.char.name);
    } catch (e) { state = "nodata"; err = e.message || String(e); ST.refresh(); }
  }

  // ---- W3b: Rig là chế độ sửa của nhân vật trong Cảnh. Focus Rig = lõi Rig vẽ nhân vật (mesh Cảnh + xương Cảnh ẩn), rời Rig = Cảnh vẽ lại.
  // Ẩn / hiện mesh (mắt Outliner, Ctrl+H) là của mesh trong Cảnh, áp sang lõi Rig theo tên.
  function syncVis() {
    if (!eng) return; const g = eng.get(), on = n => { const o = ST.mods.mesh.byName(n); return !o || o.vis; };
    g.vis.body = on(g.DATA.body.name); g.vis.cloth = (g.DATA.clothes || []).length ? g.DATA.clothes.some(c => on(c.name)) : g.vis.cloth;
    (g.DATA.props || []).forEach((p, i) => { g.vis.props[i] = on(p.name); });
  }
  M.syncVis = () => { syncVis(); if (eng) eng.syncScene(); };
  M.focusIn = () => { if (root) root.visible = act(); ensure().then(() => { if (root) root.visible = act(); if (eng && ST.focus === "rig") { syncVis(); eng.setMode(TOOL2MODE[ST.tool] || "select"); eng.syncScene(); } ST.refresh(); }); };
  M.focusOut = () => { if (root) root.visible = false; V.gizmo.detach(); ST.rigSetup.hide(); };
  ST.on("layer", () => { if (root) root.visible = act(); });
  ST.on("ws", () => { if (eng) syncTab(step()); });   // đổi workspace: tab Rig theo bước đang làm, không kéo lõi về bước của tab cũ
  M.loaded = () => !!eng;
  // W3c: khớp dùng chung — bước 2 = khớp (landmark), bước 4–5 = xương
  const boneNames = () => eng ? eng.buildSkeleton().map(b => b.name) : [];
  M.curJoint = () => { if (!eng) return null; const g = eng.get(); return (g.step === 2 || g.step === 3) ? g.sel : g.step >= 4 ? (g.step === 5 ? g.poseBone || g.jointSel : g.jointSel) : null; };
  M.hasJoint = n => { if (!eng) return false; const g = eng.get(); return (g.step === 2 || g.step === 3) ? Array.isArray(g.LM[n]) : boneNames().includes(n); };
  M.selectJoint = async n => {
    if (!(await M.whenReady())) return; const g = eng.get();
    if ((g.step === 2 || g.step === 3)) { if (Array.isArray(g.LM[n])) eng.applySel([n], {}); }
    else if (g.step >= 4 && boneNames().includes(n)) eng.selectBoneByName(n);
    eng.syncScene();
  };
  // chờ lõi nạp xong (cầu nối AI gọi lệnh ngay sau khi focus)
  M.whenReady = async () => {
    if (!ST.char) return false; ensure(); const busy = () => ["none", "loading", "building"].includes(state);
    for (let i = 0; i < 400 && busy(); i++) await new Promise(r => setTimeout(r, 100));
    return state === "ready";
  };
  M.loadMsg = () => !ST.char ? "Chưa mở nhân vật" : ({ loading: "Đang nạp rig…", building: "Đang dựng dữ liệu rig…", nodata: "Chưa có dữ liệu rig: mở panel Rig để dựng", error: "Lỗi nạp rig: " + err }[state] || "Chưa nạp: bấm Rig để nạp");
  M.nodeLabel = () => eng ? "Rig · bước " + step() + "/5" : "Rig";
  ST.on("tool", t => { if (ST.focus === "rig" && eng) { eng.setMode(TOOL2MODE[t] || "select"); if (step() === 4 && t === "sel") eng.setSkTool("pick"); } });
  ST.on("char", () => { dispose(); raw = {}; open = null; state = "none"; });
  ST.on("rig:cleared", () => { dispose(); raw = {}; state = "none"; if (ST.focus === "rig") ensure(); });   // xoá / khôi phục xương ở General: dựng lại lõi Rig

  // ---- chuột (viewport gọi)
  M.canBox = () => (step() === 2 || step() === 3);
  // click trúng khớp (bước 2) hoặc mesh của rig → viewport chuyển focus sang Rig
  M.hit = (x, y, p) => {
    if (!eng || !root || !root.visible) return false;
    const g = eng.get(), w = new THREE.Vector3(), R = V.TM && V.TM.on ? 26 : 12;
    if ((step() === 2 || step() === 3) && Object.values(g.LM).some(q => { if (!Array.isArray(q)) return false; const s = V.toScreen(w.set(q[0], q[1], q[2]).applyMatrix4(V.cm.matrixWorld), p); return Math.hypot(s.x - x, s.y - y) < R; })) return true;
    const ms = []; root.traverse(o => { if (o.isMesh && o.visible) ms.push(o); });
    return V.raycaster(x, y, p).intersectObjects(ms, false).length > 0;
  };
  M.pick = (x, y, e, p) => { if (!eng) return; const s = step(); if (s === 2 || s === 3) eng.pickLM(x, y, e, p); else if (s >= 4) eng.pickJoint(e); };
  M.box = (x0, y0, x1, y1, e, p) => { if (eng && (step() === 2 || step() === 3)) eng.boxLM(x0, y0, x1, y1, e, p); };
  M.pointerDown = (e, p) => { if (eng && onS6() && ST.rigSetup.pointerDown(e, p)) return true; if (!eng || !eng.wantsSkinPointer(e)) return false; live.downL.forEach(f => f(e)); return true; };
  M.gzStart = () => eng && eng.gzStart(); M.gzChange = Mx => eng && eng.gzChange(Mx); M.gzEnd = () => eng && eng.gzEnd();
  M.bounds = selOnly => {
    if (!eng) return ST.mods.mesh.bounds(false);
    const g = eng.get(), b = new THREE.Box3(), v = new THREE.Vector3();
    if (selOnly) { if (!g.S.size) return null; g.S.forEach(k => b.expandByPoint(v.set(...g.LM[k]))); b.expandByScalar(15); }
    else { const vs = g.DATA.body.verts; for (let i = 0; i < vs.length; i += 3) b.expandByPoint(v.set(vs[i], vs[i + 1], vs[i + 2])); }
    return b.applyMatrix4(V.cm.matrixWorld);
  };

  // ---- Channel Box: toạ độ khớp đang chọn (cm); nhiều khớp = tâm, nhập số thì dời cả nhóm (đối xứng R→L nếu bật)
  M.channel = {
    unit: "cm",
    title: () => { if (!eng) return ""; const g = eng.get(); return g.S.size > 1 ? g.S.size + " khớp" : g.sel || ""; },
    vals() { if (!eng || ![2, 3].includes(step())) return null; const g = eng.get(); if (!g.S.size) return null; const c = g.S.size === 1 ? g.LM[g.sel] : eng.centroid().toArray(); return { t: c.slice(), r: [0, 0, 0], s: [1, 1, 1] }; },
    apply(vals, push) {
      const cur = this.vals(); if (!cur) return;
      const d = vals.t.map((x, i) => x - cur.t[i]); if (d.every(x => Math.abs(x) < 1e-6)) return;
      eng.gzStart("translate"); eng.gzChange(new THREE.Matrix4().makeTranslation(d[0], d[1], d[2])); if (push) eng.gzEnd();
    },
    begin() {}, reset() {},
  };

  // ---- Outliner: mesh của rig + cây xương đang dựng (bấm để chọn khớp ở bước 2, chọn xương ở bước 4–5)
  M.outline = () => {
    if (!eng) return [];
    if (!open) open = new Set(ST.pref.get("rig:open:" + ST.char.id, null) || ["root", "Root_M", "Spine1_M", "Chest_M"]);
    const g = eng.get(), rows = [];   // W3b: mesh chỉ có một dòng (ở cấp đầu, của Cảnh); dưới nút Rig là cây xương đang dựng
    const B = eng.buildSkeleton(), kids = {}; B.forEach(b => (kids[b.parent || ""] || (kids[b.parent || ""] = [])).push(b));
    const s = g.step, on = n => s === 2 || s === 3 ? g.S.has(n) : s >= 4 ? (n === g.skinBone && s === 4) || n === g.jointSel || (s === 5 && n === g.poseBone) : false;
    const walk = (list, d) => list.forEach(b => { const k = kids[b.name] || []; rows.push({ id: "j:" + b.name, d, label: b.name, icon: "joint", sel: on(b.name), fold: k.length ? (open.has(b.name) ? 0 : 1) : undefined, count: d === 0 ? B.length : undefined }); if (k.length && open.has(b.name)) walk(k, d + 1); });
    walk(kids[""] || [], 0);
    return rows;
  };
  M.olAct = (id, a, e) => {
    if (!eng) return; id = String(id);
    if (id.startsWith("m:")) { if (a === "vis") { const g = eng.get(); if (id === "m:body") eng.set("visBody", !g.vis.body); else if (id.startsWith("m:cloth")) eng.set("visCloth", !g.vis.cloth); else eng.set("visProps", !g.vis.props.every(Boolean)); } return; }
    const n = id.slice(2);
    if (a === "fold") { open.has(n) ? open.delete(n) : open.add(n); ST.pref.set("rig:open:" + ST.char.id, [...open]); return; }
    const s = step();
    if (s === 2 || s === 3) { if (eng.LM_ORDER.includes(n)) eng.applySel([n], { shiftKey: ST.addSel(e), ctrlKey: e && e.ctrlKey, metaKey: e && e.metaKey }); }
    else if (s >= 4) eng.selectBoneByName(n);
    else ST.toast("Chọn khớp ở tab 2 Khớp, chọn xương ở tab 4 Skin / 5 Thử khớp");
  };

  // ---- dock: 5 bước = 5 tab
  const onS6 = () => !!ST.curTab && ST.curTab() === "rig:s6";
  M.panelKey = () => state + ":" + (eng ? step() : 0) + (onS6() ? ":s6:" + ST.rigSetup.ver : "");
  M.panel = tab => {
    if (ST.char && state === "none") setTimeout(ensure, 0);   // panel Rig mở ở workspace nào cũng nạp lõi (lớp vẫn ẩn nếu đang tắt)
    if (!ST.char) return '<p class="note">Cảnh trống: mở nhân vật (Ctrl+O) hoặc nhập FBX (Ctrl+Shift+I) trước.</p>';
    if (state === "loading" || state === "none") return '<div class="sub">Đang nạp rig…</div>';
    if (state === "building") return '<div class="sub">Đang dựng dữ liệu rig (gợi ý khớp từ mesh, mẫu ngón từ xương khách)… khoảng vài chục giây.</div>';
    if (state === "nodata") return `<h2>Rig</h2><p class="note">${esc(ST.char.name)} chưa có dữ liệu rig. Studio dựng từ mesh thân + xương khách trong FBX (gợi ý khớp tự động, mẫu ngón theo xương khách).</p>${err ? `<p class="note s-bad">${esc(err)}</p>` : ""}<div class="row"><button class="on" data-rig="build">${ic("rig")} Dựng dữ liệu rig</button></div>`;
    if (state === "error") return `<p class="note s-bad">Không nạp được rig: ${esc(err)}</p>`;
    if (tab === "s6") return '<div class="rigp">' + ST.rigSetup.panel() + "</div>";   // bước 6 Vật lý: modules/rig_setup.js
    return '<div id="jbox" class="jbox" hidden></div><div id="panel" class="rigp"></div>';
  };
  M.panelMounted = tab => {
    if (!eng || state !== "ready") return;
    if (tab === "s6") return ST.rigSetup.mounted();
    ST.rigSetup.hide();
    const n = +String(tab).slice(1) || 2;
    if (step() !== n) eng.go(n); else eng.renderPanel();
  };
  M.panel_click = e => { if (onS6()) return ST.rigSetup.click(e); const b = e.target.closest("[data-rig]"); if (b && b.dataset.rig === "build") buildData(); };
  M.panel_change = e => { if (onS6()) ST.rigSetup.change(e); };
  M.info = () => {
    if (!ST.char) return "Cảnh trống";
    if (!eng) return ST.char.name + " · rig " + ({ loading: "đang nạp", nodata: "chưa có dữ liệu", building: "đang dựng", error: "lỗi" }[state] || "");
    const g = eng.get(); return ST.char.name + " · Rig bước " + g.step + "/5" + (g.S.size ? " · chọn " + g.S.size + " khớp" : "") + (g.saveMsg ? " · " + g.saveMsg : "");
  };

  // ---- lệnh
  const C = o => ST.cmd(Object.assign({ mod: "rig" }, o)), R = () => !!eng;
  ["1 Mesh", "2 Khớp", "3 Xương", "4 Skin", "5 Thử khớp"].forEach((l, i) => C({ id: "rig.step" + (i + 1), menu: "Rig", sep: i === 0, icon: "s" + (i + 1), label: "Bước " + l, key: String(i + 1), on: R, check: () => step() === i + 1, run: () => { syncTab(i + 1); eng.go(i + 1); if (ST.jsel && !M.curJoint()) M.selectJoint(ST.jsel); ST.refresh(); } }));   // W3c: bước có chọn khớp lấy khớp dùng chung
  C({ id: "rig.mirror", menu: "Rig", sep: true, label: "Đối xứng R → L", icon: "sym", on: R, check: () => eng && eng.get().mirror, run: () => eng.set("mirror", !eng.get().mirror) });
  C({ id: "rig.reset", menu: "Rig", label: "Khớp về gợi ý tự động", icon: "reset", on: R, run: () => { const g = eng.get(); for (const k in g.DATA.auto.landmarks) g.LM[k] = g.DATA.auto.landmarks[k].slice(); eng.initFingers(g.LM, true); eng.syncScene(); eng.dirty(); eng.commit(); eng.renderPanel(); } });
  // FBX đã có xương + skin: dùng luôn làm rig (đặt khớp theo xương khách + dùng skin khách), không cần đặt khớp / tô skin lại
  const useFbx = () => { eng.go(2); eng.adoptGuestJoints(); eng.go(4); eng.adoptGuestSkin(); ST.toast("Đã dùng joint + skin của FBX làm rig."); };
  ST.cmd({ id: "rig.useFbx", menu: "Rig", label: "Dùng joint + skin của FBX", icon: "rig", mod: "rig",
    on: () => !eng || (eng.guestJ() && eng.guestS()),
    run: async () => {
      await M.whenReady();   // lõi Rig nạp lười (W1): chờ xong rồi dùng
      if (!eng || !eng.guestJ() || !eng.guestS()) return ST.toast("Nhân vật này không có xương + skin từ FBX (hoặc đã xoá xương).");
      useFbx();
    } });
  C({ id: "rig.guestJ", menu: "Rig", label: "Đặt khớp theo xương khách", icon: "rig", on: () => R() && eng.guestJ(), run: () => eng.adoptGuestJoints() });
  C({ id: "rig.export", menu: "Rig", sep: true, label: "Xuất rig.json", icon: "export", on: R, run: () => eng.exportRig() });
  C({ id: "rig.build", menu: "Rig", label: "Dựng lại dữ liệu rig", on: () => !!ST.char && state !== "building", run: buildData });
  C({ id: "skin.compute", menu: "Skin", label: "Tính skin", icon: "soft", on: R, run: () => { syncTab(4); eng.go(4); eng.computeSkin(); } });
  C({ id: "skin.guest", menu: "Skin", label: "Dùng skin khách", on: () => R() && eng.guestS(), run: () => { eng.go(4); eng.adoptGuestSkin(); } });
  C({ id: "skin.pick", menu: "Skin", sep: true, label: "Chọn joint", icon: "joint", on: () => R() && !!eng.get().SK, check: () => eng && eng.get().skTool === "pick", run: () => eng.setSkTool("pick") });
  C({ id: "skin.brush", menu: "Skin", label: "Cọ tô weight", icon: "smooth", key: "b", on: () => R() && !!eng.get().SK, check: () => eng && eng.get().skTool === "brush", run: () => { if (step() !== 4) eng.go(4); eng.setSkTool("brush"); } });
  C({ id: "skin.island", menu: "Skin", label: "Gán khối rời", icon: "island", key: "i", on: () => R() && !!eng.get().SK, check: () => eng && eng.get().skTool === "island", run: () => { if (step() !== 4) eng.go(4); eng.setSkTool("island"); } });
  C({ id: "skin.hammer", menu: "Skin", sep: true, label: "Hammer pose hiện tại", on: () => R() && !!eng.get().SK, run: () => eng.hammerCurrent() });
  C({ id: "skin.hammerAuto", menu: "Skin", label: "Hammer tự động", on: () => R() && !!eng.get().SK, run: () => eng.hammerAuto() });
  C({ id: "skin.test", menu: "Skin", label: "Tự kiểm skin", on: () => R() && !!eng.get().SK, run: () => eng.runSelfTest() });
  C({ id: "skin.weights", menu: "Skin", sep: true, label: "Xuất weights.json", icon: "export", on: () => R() && !!eng.get().SK, run: () => eng.exportWeights() });
  C({ id: "rig.gltf", menu: "File", label: "Xuất glTF (rig + skin)", icon: "export", on: () => R() && !!eng.get().SK, run: () => eng.exportGltf() });
  C({ id: "rig.toPose", menu: "Rig", label: "Gửi rig sang Pose…", icon: "pose", on: () => R() && !!eng.get().SK, run: sendToPose });
  const vis = (id, label, k, getv) => C({ id: "rig.v." + id, menu: "Display", keep: true, label, on: R, check: () => eng && getv(eng.get()), run: () => eng.set(k, !getv(eng.get())) });
  // thân / quần áo / prop: mắt mesh trong Outliner (W3b)
  vis("wire", "Rig: lưới mesh", "showWire", g => g.showWire); vis("skel", "Rig: xương (bước 2)", "showSkel", g => g.showSkel); vis("fing", "Rig: khớp ngón", "showFing", g => g.showFing); vis("ref", "Rig: xương khách (đối chiếu)", "showRef", g => g.showRef);

  // ---- gửi rig sang Pose: tạo base pose 1 khung cho một anim của nhân vật (POST /api/rig/to-pose, như nút ➤ của Home)
  async function sendToPose() {
    let clips = [], proj = "";
    try {
      const s = await (await fetch("/api/state")).json();
      clips = (s.clips || []).filter(c => c.labs && (c.labs.mesh === ST.char.id || c.labs.rig === ST.char.id || c.labs.studio === ST.char.id));
      const p = (s.projects || []).find(p => (p.characters || []).some(n => n.toLowerCase() === ST.char.name.toLowerCase())); proj = p ? p.id : "";
    } catch (e) {}
    const post = async (url, body) => { const j = await (await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })).json(); if (!j.ok) throw new Error(j.error); return j; };
    // không có anim nào thì vẫn gửi được: tạo anim mới (như form Home) rồi gửi base pose vào đó
    const form = `<div class="row"><input type="text" id="tpName" placeholder="Tên anim mới, vd: idle" style="flex:1" aria-label="Tên anim mới"><button data-a="new">${ic("pose")} Tạo anim và gửi</button></div>`;
    ST.dialog("Gửi rig sang Pose", (clips.length ? `<p class="note">Tạo base pose (1 khung) từ rig + skin hiện tại trong Pose Lab của anim:</p><div class="list">${clips.map(c => `<button class="it" data-clip="${esc(c.id)}">${ic("pose")}<span>${esc(c.name || c.id)}</span><small>${esc(c.stage || "")}${c.id === ST.clip ? " · đang mở" : ""}</small></button>`).join("")}</div><p class="note">Hoặc tạo anim mới:</p>` : `<p class="note">${esc(ST.char.name)} chưa có anim nào. Đặt tên anim để tạo và gửi base pose vào đó:</p>`) + form, b => {
      const send = async cid => {
        b.innerHTML = '<div class="sub">Đang dựng glTF và gửi…</div>';
        const j = await post("/api/rig/to-pose", { clip: cid, gltf: eng.buildGltf() });
        ST.closeDialog(); ST.toast("Đã tạo base pose " + j.id + " cho " + cid);
      };
      const fail = e => { b.innerHTML = `<p class="note s-bad">Không gửi được: ${esc(e.message || e)}</p>`; };
      const create = async () => {
        const inp = b.querySelector("#tpName"), name = inp.value.trim(); if (!name) return inp.focus();
        try { const j = await post("/api/clip", { character: ST.char.name, clip: name, project: proj }); await send(j.id); } catch (e) { fail(e); }
      };
      b.querySelector("#tpName").onkeydown = e => { if (e.key === "Enter") create(); };
      b.onclick = async e => {
        if (e.target.closest('[data-a="new"]')) return create();
        const x = e.target.closest("[data-clip]"); if (!x) return;
        try { await send(x.dataset.clip); } catch (e2) { fail(e2); }
      };
    });
  }
})();
