// AI Anim Studio — xương của nhân vật: vẽ joint + đoạn nối cha → con trong viewport, cây joint trong Outliner (mở / gập).
// Workspace General: click joint trong viewport hoặc Outliner để chọn; gizmo / Channel Box dời, xoay, scale joint,
// joint con đi theo như Maya. Sửa được lưu ở doc skel/edit của kho <nhân vật>_mesh_lab (cạnh mesh/edit).
// Nguồn gốc: /api/char → skeleton (cm, Y lên).
(function () {
  const V = ST.view, S = ST.mods.skel = { joints: [] };
  let byName = {}, kids = {}, open = new Set(), sel = null, show = ST.pref.get("skel:show", true);
  const grp = new THREE.Group(); grp.renderOrder = 25; V.cm.add(grp);
  const ptMat = new THREE.PointsMaterial({ size: 7, sizeAttenuation: false, color: 0x3fb6ff, depthTest: false, transparent: true });
  const lnMat = new THREE.LineBasicMaterial({ color: 0x3fb6ff, depthTest: false, transparent: true, opacity: 0.75 });
  const selMat = new THREE.PointsMaterial({ size: 12, sizeAttenuation: false, color: 0xff7a1a, depthTest: false, transparent: true });
  let pts = null, lines = null, selPt = null, store = null, saveT = 0, JT = null, drag = null;
  const V3 = THREE.Vector3, M4 = THREE.Matrix4;

  function build() {
    [pts, lines, selPt].forEach(o => { if (o) { grp.remove(o); o.geometry.dispose(); } });
    const P = [], L = [];
    S.joints.forEach(j => { P.push(...j.pos); const p = byName[j.parent]; if (p) L.push(...p.pos, ...j.pos); });
    const gp = new THREE.BufferGeometry(); gp.setAttribute("position", new THREE.Float32BufferAttribute(P, 3)); pts = new THREE.Points(gp, ptMat); pts.renderOrder = 26;
    const gl = new THREE.BufferGeometry(); gl.setAttribute("position", new THREE.Float32BufferAttribute(L, 3)); lines = new THREE.LineSegments(gl, lnMat); lines.renderOrder = 25;
    const gs = new THREE.BufferGeometry(); gs.setAttribute("position", new THREE.Float32BufferAttribute(sel ? byName[sel].pos : [], 3)); selPt = new THREE.Points(gs, selMat); selPt.renderOrder = 27;
    [lines, pts, selPt].forEach(o => { o.raycast = () => {}; grp.add(o); });
    grp.visible = show && S.joints.length > 0 && ST.ws === "general";
  }
  ST.on("ws", () => { grp.visible = show && S.joints.length > 0 && ST.ws === "general"; });
  ST.on("char", async ch => {
    S.joints = (ch.skeleton || []).map(j => Object.assign({}, j, { pos: j.pos.slice(), bind: j.pos.slice(), D: new M4() })); byName = {}; kids = {}; sel = null; JT = null;
    S.joints.forEach(j => { byName[j.name] = j; (kids[j.parent || ""] || (kids[j.parent || ""] = [])).push(j); });
    open = new Set(ST.pref.get("skel:open:" + ch.id, null) || S.joints.filter(j => depth(j) < 2).map(j => j.name));
    store = ST.store(new URLSearchParams(location.search).get("ns") || ST.slug(ch.name) + "_mesh_lab");
    try {
      const s = await store.get("skel/edit");
      if (s && s.joints) Object.entries(s.joints).forEach(([n, p]) => { if (byName[n]) byName[n].pos = p.slice(); });
      if (s && s.D) Object.entries(s.D).forEach(([n, e]) => { if (byName[n]) byName[n].D.fromArray(e); });
    } catch (e) { console.error(e); }
    build(); ST.emit("skel:pose");
  });
  const depth = j => { let d = 0; while (j && j.parent && byName[j.parent]) { j = byName[j.parent]; d++; } return d; };
  const saveOpen = () => ST.char && ST.pref.set("skel:open:" + ST.char.id, [...open]);

  // dòng Outliner: nhóm Skeleton + cây joint (chỉ hiện con của joint đang mở)
  S.rows = () => {
    if (!S.joints.length) return [];
    const rows = [];   // như Maya: joint gốc nằm ngay cấp đầu; mắt ở joint gốc bật / tắt cả bộ xương
    const walk = (list, d) => list.forEach(j => {
      const k = kids[j.name] || [];
      rows.push({ id: "j:" + j.name, d, label: j.name, icon: "joint", sel: sel === j.name, fold: k.length ? (open.has(j.name) ? 0 : 1) : undefined, vis: d === 0 ? show : undefined, count: d === 0 ? S.joints.length : undefined });
      if (k.length && open.has(j.name)) walk(k, d + 1);
    });
    walk(kids[""] || [], 0);
    return rows;
  };
  S.olAct = (id, a) => {
    const n = id.slice(2), j = byName[n]; if (!j) return;
    if (a === "vis") { show = !show; ST.pref.set("skel:show", show); build(); return; }
    if (a === "fold") { open.has(n) ? open.delete(n) : open.add(n); saveOpen(); return; }
    S.select(n);
  };
  S.isMine = id => typeof id === "string" && id.startsWith("j:");
  S.bounds = () => { if (!sel) return null; const p = new THREE.Vector3(...byName[sel].pos).applyMatrix4(V.cm.matrixWorld); return new THREE.Box3().setFromCenterAndSize(p, new THREE.Vector3(0.3, 0.3, 0.3)); };

  // ---------------------------------------------------------------- chọn + sửa joint (workspace General)
  const editable = () => ST.ws === "general" && show && S.joints.length > 0;
  const sub = n => { const out = [], q = [n]; while (q.length) { const k = q.pop(); out.push(k); (kids[k] || []).forEach(c => q.push(c.name)); } return out; };
  S.sel = () => (sel && editable() ? sel : null);
  S.selPos = () => sel ? new V3(...byName[sel].pos) : null;
  S.select = n => {
    const nn = n && byName[n] ? n : null; if (nn !== sel) JT = null; sel = nn; build();
    ST.hint = sel ? "Joint " + sel + (byName[sel].parent ? " · cha " + byName[sel].parent : "") + " · " + (sub(sel).length - 1) + " joint con đi theo" : "";
    ST.emit("jsel", sel); ST.chRefresh && ST.chRefresh(); ST.refresh();
  };
  S.pickAt = (x, y, p) => {   // joint gần con trỏ nhất trong bán kính vài px (joint vẽ đè lên mesh nên ưu tiên joint)
    if (!editable()) return null;
    const R = V.TM && V.TM.on ? 26 : 10, w = new V3(); let best = null, bd = R;
    S.joints.forEach(j => { w.set(...j.pos).applyMatrix4(V.cm.matrixWorld); const s = V.toScreen(w, p); if (!s) return; const d = Math.hypot(s.x - x, s.y - y); if (d < bd) { bd = d; best = j.name; } });
    return best;
  };
  S.info = () => sel ? "Joint " + sel + " · " + byName[sel].pos.map(v => v.toFixed(1)).join(", ") + " cm" : "";

  // undo chung + lưu
  S.snap = () => ({ sel, p: S.joints.map(j => j.pos.slice()), d: S.joints.map(j => j.D.toArray()) });
  S.restore = s => { S.joints.forEach((j, i) => { if (s.p[i]) j.pos = s.p[i].slice(); if (s.d && s.d[i]) j.D.fromArray(s.d[i]); }); JT = null; ST.emit("skel:pose"); sel = s.sel && byName[s.sel] ? s.sel : null; build(); changed(); ST.chRefresh && ST.chRefresh(); ST.emit("jsel", sel); };
  function changed() { ST.saveState("Chưa lưu…", "dirty"); clearTimeout(saveT); saveT = setTimeout(save, 1200); }
  async function save() {
    clearTimeout(saveT); if (!store) return;
    const joints = {}, D = {}; S.joints.forEach(j => { joints[j.name] = j.pos.map(v => +v.toFixed(3)); if (!isId(j.D)) D[j.name] = j.D.toArray().map(v => +v.toFixed(6)); });
    try { const w = await store.set("skel/edit", { v: 2, at: new Date().toISOString(), joints, D }); ST.saveState(w === "disk" ? "Đã lưu xương vào dự án (work/store/" + store.ns + ")" : "Đã lưu xương (chỉ trình duyệt này)", w === "disk" ? "" : "dirty"); }
    catch (e) { ST.saveState("Không lưu được xương: " + (e.message || e), "err"); }
  }
  S.save = save;

  // biến đổi: ma trận cm áp lên joint đang chọn + mọi joint con (quanh vị trí joint lúc chọn)
  function ensureJT() { if (!JT && sel) JT = { c0: S.selPos(), A: new M4() }; return JT; }
  // D = biến đổi từ bind tới hiện tại (cm, world) của mỗi joint = ma trận skin: mesh skin đỉnh v → Σ w·D·v (bind)
  const base = () => { const B = {}; sub(sel).forEach(n => { B[n] = { p: byName[n].pos.slice(), D: byName[n].D.clone() }; }); return B; };
  function applyM(Mx, B) { const v = new V3(); Object.entries(B).forEach(([n, b]) => { v.set(...b.p).applyMatrix4(Mx); byName[n].pos = [v.x, v.y, v.z]; byName[n].D = Mx.clone().multiply(b.D); }); build(); ST.emit("skel:pose"); }
  const isId = m => m.elements.every((v, i) => Math.abs(v - (i % 5 === 0 ? 1 : 0)) < 1e-6);
  S.posed = () => S.joints.some(j => !isId(j.D));
  S.skinMat = n => byName[n] ? byName[n].D : null;
  S.bindPose = () => { if (!S.posed()) return ST.toast("Xương đang ở bind pose."); ST.hist.push(S, "Về Bind Pose"); S.joints.forEach(j => { j.pos = j.bind.slice(); j.D = new M4(); }); JT = null; build(); ST.emit("skel:pose"); changed(); ST.emit("jsel", sel); ST.toast("Đã về bind pose."); };
  S.gzStart = () => { if (!sel) return; ST.hist.push(S, "Sửa joint"); ensureJT(); drag = { B: base(), A0: JT.A.clone() }; };
  S.gzChange = Mx => { if (!drag) return; applyM(Mx, drag.B); JT.A = Mx.clone().multiply(drag.A0); ST.chRefresh && ST.chRefresh(); };
  S.gzEnd = () => { if (!drag) return; drag = null; changed(); ST.refresh(); };
  const rad = d => d * Math.PI / 180, deg = r => r * 180 / Math.PI;
  S.channel = {
    unit: "cm",
    title: () => sel ? "Joint " + sel : "",
    vals() {
      if (!S.sel()) return null; const p = byName[sel].pos;
      if (!JT) return { t: p.slice(), r: [0, 0, 0], s: [1, 1, 1] };
      const L = JT.A.clone().setPosition(0, 0, 0), q = new THREE.Quaternion(), tp = new V3(), sc = new V3(); L.decompose(tp, q, sc);
      const e = new THREE.Euler().setFromQuaternion(q, "XYZ"); return { t: p.slice(), r: [deg(e.x), deg(e.y), deg(e.z)], s: [sc.x, sc.y, sc.z] };
    },
    apply(vals, push) {
      const T = ensureJT(); if (!T) return; if (push) ST.hist.push(S, "Channel Box joint");
      const R = new M4().makeRotationFromEuler(new THREE.Euler(rad(vals.r[0]), rad(vals.r[1]), rad(vals.r[2]), "XYZ")), Sc = new M4().makeScale(...vals.s.map(x => Math.abs(x) < 1e-3 ? (x < 0 ? -1e-3 : 1e-3) : x));
      const Anew = new M4().makeTranslation(...vals.t).multiply(R).multiply(Sc).multiply(new M4().makeTranslation(-T.c0.x, -T.c0.y, -T.c0.z));
      applyM(Anew.clone().multiply(T.A.clone().invert()), base()); T.A = Anew; changed(); ST.emit("jsel", sel);
    },
    begin() { ST.hist.push(S, "Channel Box joint"); },
    reset() { JT = null; },
  };

  ST.cmd({ id: "skin.bindPose", menu: "Skin", label: "Về Bind Pose", icon: "reset", on: () => S.joints.length > 0 && S.posed(), run: () => S.bindPose() });
  ST.cmd({ id: "view.skel", menu: "Display", label: "Xương (joint)", icon: "joint", check: () => show, on: () => S.joints.length > 0, run: () => { show = !show; ST.pref.set("skel:show", show); build(); } });
})();
