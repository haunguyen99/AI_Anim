// AI Anim Studio — workspace Rig (S3): lõi Rig Lab (modules/rig_engine.js, sinh từ template bằng port_rig.py) chạy trong viewport chung.
// Năm bước của Rig Lab là năm tab dock (1 Mesh · 2 Khớp · 3 Xương · 4 Skin · 5 Thử khớp). Chọn khớp bằng click / khung, dời bằng gizmo chung,
// undo chung, Outliner = cây xương đang dựng, Channel Box = toạ độ khớp. Lưu cùng kho với Rig Lab cũ (<nhân vật>_rig_lab).
(function () {
  const V = ST.view, esc = ST.esc, ic = ST.ic;
  const M = ST.mods.rig = { id: "rig", panelStatic: true };
  let eng = null, key = null, root = null, state = "none", err = "", live = null, raw = {}, open = null;
  const cvEl = ST.$("cv");
  const TOOL2MODE = { sel: "select", move: "translate", rot: "rotate", scl: "scale" }, MODE2TOOL = { select: "sel", translate: "move", rotate: "rot", scale: "scl" };
  const step = () => eng ? eng.get().step : 0;

  // ---- mesh đã sửa ở workspace General → DATA (giống MESHLINK của Rig Lab: thay theo tên, dời landmark nếu thân đổi cỡ / vị trí)
  const bbox = a => { const mn = [1e9, 1e9, 1e9], mx = [-1e9, -1e9, -1e9]; for (let i = 0; i < a.length; i += 3) for (let k = 0; k < 3; k++) { mn[k] = Math.min(mn[k], a[i + k]); mx[k] = Math.max(mx[k], a[i + k]); } return { mn, mx }; };
  function meshApply(D) {
    const ms = ST.mods.mesh, at = ms.editAt && ms.editAt();
    window.__meshAt = null; window.__meshT = null;
    if (!at) return D;
    const by = {}; ms.objects().forEach(o => { if (o.vis) by[o.name] = { verts: Array.from(o.pos), tris: Array.from(o.idx) }; });
    const bn = D.body.name; if (!bn || !by[bn]) return D;
    const o0 = bbox(D.body.verts), o1 = bbox(by[bn].verts), f = (o1.mx[1] - o1.mn[1]) / Math.max(1e-6, o0.mx[1] - o0.mn[1]);
    const c0 = [(o0.mn[0] + o0.mx[0]) / 2, o0.mn[1], (o0.mn[2] + o0.mx[2]) / 2], c1 = [(o1.mn[0] + o1.mx[0]) / 2, o1.mn[1], (o1.mn[2] + o1.mx[2]) / 2];
    const T = p => [c1[0] + (p[0] - c0[0]) * f, c1[1] + (p[1] - c0[1]) * f, c1[2] + (p[2] - c0[2]) * f];
    const same = D.body.verts.length === by[bn].verts.length, take = (o, m) => { o.verts = m.verts; o.tris = m.tris; };
    take(D.body, by[bn]);
    (D.clothes || []).forEach(c => { if (by[c.name]) take(c, by[c.name]); });
    (D.props || []).forEach(p => { if (by[p.name]) take(p, by[p.name]); });
    if (Math.abs(f - 1) > 1e-4 || c0.some((v, i) => Math.abs(v - c1[i]) > 1e-3)) {
      for (const k in D.auto.landmarks) D.auto.landmarks[k] = T(D.auto.landmarks[k]).map(v => +v.toFixed(3));
      if (D.auto.H) D.auto.H = +(D.auto.H * f).toFixed(3);
      (D.ref || []).forEach(b => { if (b.pos) b.pos = T(b.pos); });
      window.__meshT = { f, c0, c1 };
    }
    if (!same) D.refW = {};
    window.__meshAt = at;
    window.__meshLM = L => { const t = window.__meshT; if (!t) return L; const o = {}; for (const k in L) o[k] = Array.isArray(L[k]) && L[k].length === 3 ? [t.c1[0] + (L[k][0] - t.c0[0]) * t.f, t.c1[1] + (L[k][1] - t.c0[1]) * t.f, t.c1[2] + (L[k][2] - t.c0[2]) * t.f].map(v => +v.toFixed(3)) : L[k]; return o; };
    return D;
  }

  // ---- host: những gì lõi Rig cần từ Studio
  function makeHost(grp) {
    const me = { on: true }, downL = [];
    const store = ST.store(new URLSearchParams(location.search).get("ns") ? new URLSearchParams(location.search).get("ns") + "_rig" : ST.slug(ST.char.name) + "_rig_lab");
    const db = { isLocal: true, doc: p => ({ get: async () => { const d = await store.get(p); return { exists: d != null, data: () => d }; }, set: d => store.set(p, d) }) };
    const lmOwner = { snap: () => eng.snapStr(), restore: s => eng.applySnap(s) };
    const push = (owner, label, s) => { ST.hist.U.push({ owner, label, s }); if (ST.hist.U.length > ST.hist.max) ST.hist.U.shift(); ST.hist.R = []; ST.emit("hist"); };
    return {
      me, downL, root: grp, db, TM: V.TM,
      cam: () => V.active.cam,
      cv: { getBoundingClientRect: () => { const r = cvEl.getBoundingClientRect(), p = V.active.rect; return { left: r.left + p.x, top: r.top + p.y, width: p.w, height: p.h, right: r.left + p.x + p.w, bottom: r.top + p.y + p.h }; } },
      raycaster: (x, y, p) => V.raycaster(x, y, p), toScreen: (w, p) => V.toScreen(w, p),
      alive: () => me.on && ST.ws === "rig",
      listen(t, f) { if (t === "pointerdown") downL.push(f); else cvEl.addEventListener(t, e => { if (me.on && ST.ws === "rig") f(e); }); },
      placeGizmo(c, mode) { if (!me.on || ST.ws !== "rig") return; if (!c) V.gizmo.detach(); else V.gizmo.place(c, grp, mode); },
      onMode(m) { const t = MODE2TOOL[m]; if (t && ST.tool !== t) { ST.tool = t; ST.refresh(); } },
      pushLM: before => push(lmOwner, "Rig: khớp", before),
      pushSkin: m => push({ snap: () => eng.skinSnapshotOf(m), restore: x => { eng.restoreSkin(x); eng.scheduleSkinSave(); } }, "Rig: skin", m),
      refresh: () => { if (eng) ST.pref.set("tab:rig", "s" + step()); ST.refresh(); },   // tab dock theo bước của lõi
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
      root = new THREE.Group(); root.name = "rig"; V.cm.add(root);
      const host = makeHost(root); live = host;
      eng = ST.rigEngine(D, host); key = k;
      await eng.ready; state = "ready";
      if (!open) open = new Set(ST.pref.get("rig:open:" + ST.char.id, null) || ["root", "Root_M", "Spine1_M", "Chest_M"]);
      eng.setMode(TOOL2MODE[ST.tool] || "select");
    } catch (e) { console.error(e); state = "error"; err = e.message || String(e); }
    ST.refresh();
  }
  function dispose() {
    if (live) live.me.on = false;
    if (root) { V.cm.remove(root); root.traverse(o => { if (o.geometry) o.geometry.dispose(); }); }
    V.gizmo.detach(); eng = null; root = null; live = null; key = null;
  }
  async function buildData() {
    state = "building"; ST.refresh();
    try {
      const r = await fetch("/api/rig/build", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: ST.char.id }) });
      const j = await r.json(); if (!j.ok) throw new Error(j.error);
      delete raw[ST.char.id]; key = null; await ensure(); ST.toast("Đã dựng dữ liệu rig cho " + ST.char.name);
    } catch (e) { state = "nodata"; err = e.message || String(e); ST.refresh(); }
  }

  // ---- workspace
  M.enter = () => { ST.mods.mesh.display("hidden"); if (root) root.visible = true; ensure().then(() => { if (root) root.visible = ST.ws === "rig"; if (eng) { eng.syncScene(); } }); };
  M.leave = () => { if (root) root.visible = false; V.gizmo.detach(); };
  ST.on("tool", t => { if (ST.ws === "rig" && eng) { eng.setMode(TOOL2MODE[t] || "select"); if (step() === 4 && t === "sel") eng.setSkTool("pick"); } });
  ST.on("char", () => { dispose(); raw = {}; open = null; state = "none"; });

  // ---- chuột (viewport gọi)
  M.canBox = () => step() === 2;
  M.pick = (x, y, e, p) => { if (!eng) return; const s = step(); if (s === 2) eng.pickLM(x, y, e, p); else if (s >= 4) eng.pickJoint(e); };
  M.box = (x0, y0, x1, y1, e, p) => { if (eng && step() === 2) eng.boxLM(x0, y0, x1, y1, e, p); };
  M.pointerDown = (e, p) => { if (!eng || !eng.wantsSkinPointer(e)) return false; live.downL.forEach(f => f(e)); return true; };
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
    vals() { if (!eng || step() !== 2) return null; const g = eng.get(); if (!g.S.size) return null; const c = g.S.size === 1 ? g.LM[g.sel] : eng.centroid().toArray(); return { t: c.slice(), r: [0, 0, 0], s: [1, 1, 1] }; },
    apply(vals, push) {
      const cur = this.vals(); if (!cur) return;
      const d = vals.t.map((x, i) => x - cur.t[i]); if (d.every(x => Math.abs(x) < 1e-6)) return;
      eng.gzStart(); eng.gzChange(new THREE.Matrix4().makeTranslation(d[0], d[1], d[2])); if (push) eng.gzEnd();
    },
    begin() {}, reset() {},
  };

  // ---- Outliner: mesh của rig + cây xương đang dựng (bấm để chọn khớp ở bước 2, chọn xương ở bước 4–5)
  M.outline = () => {
    if (!eng) return ST.mods.mesh.outline ? ST.mods.mesh.outline().filter(r => typeof r.id === "number") .map(r => Object.assign({}, r, { del: false, rename: false, lock: undefined })) : [];
    if (!open) open = new Set(ST.pref.get("rig:open:" + ST.char.id, null) || ["root", "Root_M", "Spine1_M", "Chest_M"]);
    const g = eng.get(), rows = [{ id: "m:body", d: 0, label: g.DATA.body.name || "Body", icon: "mesh", vis: g.vis.body }];
    (g.DATA.clothes || []).forEach((c, i) => rows.push({ id: "m:cloth" + i, d: 0, label: c.name, icon: "mesh", vis: g.vis.cloth }));
    (g.DATA.props || []).forEach((c, i) => rows.push({ id: "m:prop" + i, d: 0, label: c.name, icon: "mesh", vis: g.vis.props[i] }));
    const B = eng.buildSkeleton(), kids = {}; B.forEach(b => (kids[b.parent || ""] || (kids[b.parent || ""] = [])).push(b));
    const s = g.step, on = n => s === 2 ? g.S.has(n) : s >= 4 ? (n === g.skinBone && s === 4) || n === g.jointSel || (s === 5 && n === g.poseBone) : false;
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
    if (s === 2) { if (eng.LM_ORDER.includes(n)) eng.applySel([n], { shiftKey: ST.addSel(e), ctrlKey: e && e.ctrlKey, metaKey: e && e.metaKey }); }
    else if (s >= 4) eng.selectBoneByName(n);
    else ST.toast("Chọn khớp ở tab 2 Khớp, chọn xương ở tab 4 Skin / 5 Thử khớp");
  };

  // ---- dock: 5 bước = 5 tab
  M.panelKey = () => state + ":" + (eng ? step() : 0);
  M.panel = tab => {
    if (!ST.char) return '<p class="note">Cảnh trống: mở nhân vật (Ctrl+O) hoặc nhập FBX (Ctrl+Shift+I) trước.</p>';
    if (state === "loading" || state === "none") return '<div class="sub">Đang nạp rig…</div>';
    if (state === "building") return '<div class="sub">Đang dựng dữ liệu rig (gợi ý khớp từ mesh, mẫu ngón từ xương khách)… khoảng vài chục giây.</div>';
    if (state === "nodata") return `<h2>Rig</h2><p class="note">${esc(ST.char.name)} chưa có dữ liệu rig. Studio dựng từ mesh thân + xương khách trong FBX (gợi ý khớp tự động, mẫu ngón theo xương khách).</p>${err ? `<p class="note s-bad">${esc(err)}</p>` : ""}<div class="row"><button class="on" data-rig="build">${ic("rig")} Dựng dữ liệu rig</button></div>`;
    if (state === "error") return `<p class="note s-bad">Không nạp được rig: ${esc(err)}</p>`;
    return '<div id="jbox" class="jbox" hidden></div><div id="panel" class="rigp"></div>';
  };
  M.panelMounted = tab => {
    if (!eng || state !== "ready") return;
    const n = +String(tab).slice(1) || 2;
    if (step() !== n) eng.go(n); else eng.renderPanel();
  };
  M.panel_click = e => { const b = e.target.closest("[data-rig]"); if (b && b.dataset.rig === "build") buildData(); };
  M.info = () => {
    if (!ST.char) return "Cảnh trống";
    if (!eng) return ST.char.name + " · rig " + ({ loading: "đang nạp", nodata: "chưa có dữ liệu", building: "đang dựng", error: "lỗi" }[state] || "");
    const g = eng.get(); return ST.char.name + " · Rig bước " + g.step + "/5" + (g.S.size ? " · chọn " + g.S.size + " khớp" : "") + (g.saveMsg ? " · " + g.saveMsg : "");
  };
  M.timeline = () => '<span class="sub">Timeline (Pose, S4)</span><div class="tlbar"></div>';

  // ---- lệnh
  const C = o => ST.cmd(Object.assign({ ws: ["rig"] }, o)), R = () => !!eng;
  ["1 Mesh", "2 Khớp", "3 Xương", "4 Skin", "5 Thử khớp"].forEach((l, i) => C({ id: "rig.step" + (i + 1), menu: "Rig", sep: i === 0, icon: "s" + (i + 1), label: "Bước " + l, key: String(i + 1), on: R, check: () => step() === i + 1, run: () => { ST.pref.set("tab:rig", "s" + (i + 1)); eng.go(i + 1); ST.refresh(); } }));
  C({ id: "rig.mirror", menu: "Rig", sep: true, label: "Đối xứng R → L", icon: "sym", on: R, check: () => eng && eng.get().mirror, run: () => eng.set("mirror", !eng.get().mirror) });
  C({ id: "rig.reset", menu: "Rig", label: "Khớp về gợi ý tự động", icon: "reset", on: R, run: () => { const g = eng.get(); for (const k in g.DATA.auto.landmarks) g.LM[k] = g.DATA.auto.landmarks[k].slice(); eng.initFingers(g.LM, true); eng.syncScene(); eng.dirty(); eng.commit(); eng.renderPanel(); } });
  C({ id: "rig.guestJ", menu: "Rig", label: "Đặt khớp theo xương khách", icon: "rig", on: () => R() && eng.guestJ(), run: () => eng.adoptGuestJoints() });
  C({ id: "rig.export", menu: "Rig", sep: true, label: "Xuất rig.json", icon: "export", on: R, run: () => eng.exportRig() });
  C({ id: "rig.build", menu: "Rig", label: "Dựng lại dữ liệu rig", on: () => !!ST.char && state !== "building", run: buildData });
  C({ id: "skin.compute", menu: "Skin", label: "Tính skin", icon: "soft", on: R, run: () => { ST.pref.set("tab:rig", "s4"); eng.go(4); eng.computeSkin(); } });
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
  const vis = (id, label, k, getv) => C({ id: "rig.v." + id, menu: "Display", label, on: R, check: () => eng && getv(eng.get()), run: () => eng.set(k, !getv(eng.get())) });
  vis("body", "Rig: thân", "visBody", g => g.vis.body); vis("cloth", "Rig: quần áo", "visCloth", g => g.vis.cloth); vis("props", "Rig: prop", "visProps", g => g.vis.props.every(Boolean));
  vis("wire", "Rig: lưới mesh", "showWire", g => g.showWire); vis("skel", "Rig: xương (bước 2)", "showSkel", g => g.showSkel); vis("fing", "Rig: khớp ngón", "showFing", g => g.showFing); vis("ref", "Rig: xương khách (đối chiếu)", "showRef", g => g.showRef);

  // ---- gửi rig sang Pose: tạo base pose 1 khung cho một anim của nhân vật (POST /api/rig/to-pose, như nút ➤ của Home)
  async function sendToPose() {
    let clips = [];
    try { const s = await (await fetch("/api/state")).json(); clips = (s.clips || []).filter(c => c.labs && (c.labs.mesh === ST.char.id || c.labs.rig === ST.char.id || c.labs.studio === ST.char.id)); } catch (e) {}
    ST.dialog("Gửi rig sang Pose", clips.length ? `<p class="note">Tạo base pose (1 khung) từ rig + skin hiện tại trong Pose Lab của anim:</p><div class="list">${clips.map(c => `<button class="it" data-clip="${esc(c.id)}">${ic("pose")}<span>${esc(c.name || c.id)}</span><small>${esc(c.stage || "")}${c.id === ST.clip ? " · đang mở" : ""}</small></button>`).join("")}</div>` : `<p class="note">${esc(ST.char.name)} chưa có anim nào. Tạo anim ở Home (/home) trước.</p>`, b => {
      b.onclick = async e => {
        const x = e.target.closest("[data-clip]"); if (!x) return;
        b.innerHTML = '<div class="sub">Đang dựng glTF và gửi…</div>';
        try {
          const r = await fetch("/api/rig/to-pose", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ clip: x.dataset.clip, gltf: eng.buildGltf() }) });
          const j = await r.json(); if (!j.ok) throw new Error(j.error);
          ST.closeDialog(); ST.toast("Đã tạo base pose " + j.id + " cho " + x.dataset.clip);
        } catch (err2) { b.innerHTML = `<p class="note s-bad">Không gửi được: ${esc(err2.message || err2)}</p>`; }
      };
    });
  }
})();
