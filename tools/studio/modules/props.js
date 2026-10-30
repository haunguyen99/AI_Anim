// AI Anim Studio — vật thể phụ của lớp Anim (2026-10-29): mũi tên bay, hình nộm mục tiêu… để xem trước hiệu ứng do code game làm.
// Mỗi vật thể có hình (bản sao một mesh của anim / của Cảnh, hoặc hộp / capsule) và key riêng: vị trí + hướng, theo một cha
// (một xương của model anim, hoặc world). Đổi cha ở một key = gắn / thả, giữ nguyên chỗ ở frame đó; đoạn trước key đổi cha đi theo cha cũ.
// Lưu theo phiên bản anim trong kho Pose (doc props/<clip>-<version>). Vẽ trong cảnh của lõi Pose (thấy khi phát và trong playblast);
// không phải xương nên FBX nhân vật không có chúng. Cầu nối: obj add | list | key | unkey | parent | set | del (modules/bridge.js).
(function () {
  const esc = ST.esc, ic = ST.ic, V = ST.view;
  const P = ST.mods.props = { id: "props" };
  const V3 = THREE.Vector3, Q = THREE.Quaternion;
  const eng = () => ST.poseEng && ST.poseEng();
  const need = (c, m) => { if (!c) throw new Error(m); };
  let objs = [], docKey = null, loading = null, sel = null, edit = null, undoS = [], dirty = 0, saveT = 0, saved = "";
  const live = new Map();   // id → { root, mesh, sig }
  let group = null, hidSrc = new Set();
  const QC = new Q().setFromAxisAngle(new V3(1, 0, 0), Math.PI / 2), QCi = QC.clone().invert();   // Studio (Y lên) ↔ Blender (Z lên)

  // ---- đơn vị cho AI: cm, trục Blender (X, Y = −Z Studio, Z lên), như anim read
  const toB = v => [v.x * 100, -v.z * 100, v.y * 100].map(x => +x.toFixed(2));
  const fromB = a => new V3(+a[0] / 100, +a[2] / 100, -a[1] / 100);
  const dirB = v => [v.x, -v.z, v.y].map(x => +x.toFixed(4));
  const qToB = q => { const e = new THREE.Euler().setFromQuaternion(QC.clone().multiply(q).multiply(QCi), "XYZ"); return [e.x, e.y, e.z].map(x => +THREE.MathUtils.radToDeg(x).toFixed(2)); };
  const qFromB = a => QCi.clone().multiply(new Q().setFromEuler(new THREE.Euler(...a.map(x => THREE.MathUtils.degToRad(+x || 0)), "XYZ"))).multiply(QC);

  // ---- kho: một doc mỗi phiên bản anim
  const pose = () => ST.mods.pose;
  const curKey = () => { const e = eng(); const g = e && e.get(); return g && g.P ? g.P.clip + "-" + g.P.version : null; };
  function load(k) {
    if (docKey && objs.length) flush();
    docKey = k; objs = []; sel = null; edit = null; undoS = []; saved = "[]"; rebuildAll();
    if (!k || !pose().store) return Promise.resolve();
    const my = loading = (async () => {
      let d = null; try { d = await pose().store().get("props/" + k); } catch (e) {}
      if (loading === my) loading = null;
      if (docKey !== k) return;
      objs = (d && Array.isArray(d.objs)) ? d.objs : []; saved = JSON.stringify(objs); rebuildAll(); ST.refresh();
    })();
    return my;
  }
  // chờ đúng doc của phiên bản đang mở (cầu nối gọi ngay sau khi đổi phiên bản)
  P.ensure = async () => { for (let i = 0; i < 5; i++) { if (curKey() !== docKey && !loading) load(curKey()); if (!loading) break; await loading; } };
  function changed(label) { dirty++; clearTimeout(saveT); saveT = setTimeout(flush, 350); rebuildAll(); ST.refresh(); if (label) P.lastLabel = label; }
  async function flush() {
    if (!docKey || !pose().store) return; const s = JSON.stringify(objs); if (s === saved) return;
    try { await pose().store().set("props/" + docKey, { objs, at: new Date().toISOString() }); saved = s; } catch (e) { ST.toast("Không lưu được vật thể phụ: " + (e.message || e)); }
  }
  P.flush = flush;
  // Hoàn tác chung với lõi Pose: hàng thứ tự ord ("P" = sửa vật thể, "E" = sửa khớp / key của lõi). Mọi đường Hoàn tác ở Pose (Ctrl+Z,
  // nút ↶ của thanh công cụ Pose, Sửa → Hoàn tác, cầu nối undo) đều bấm nút #undo của lõi: bắt nút đó trước, bước cuối là vật thể (hoặc lõi
  // hết bước) thì hoàn tác vật thể, không thì để lõi làm và bỏ bước "E" cuối. Lõi xoá hàng hoàn tác khi đổi frame → bỏ mọi "E".
  let ord = [], ordFrame = null;
  const pushUndo = () => { undoS.push(JSON.stringify(objs)); if (undoS.length > 60) undoS.shift(); ord.push("P"); if (ord.length > 200) ord.shift(); };
  P.touchEngine = () => { ord.push("E"); if (ord.length > 200) ord.shift(); };   // sửa khớp / key của lõi Pose
  P.undoOrder = () => ord.slice();   // để kiểm (cầu nối / thử)
  const dropLast = t => { const i = ord.lastIndexOf(t); if (i >= 0) ord.splice(i, 1); };
  // kéo gizmo vật thể: lõi Pose cũng ghi một bước hoàn tác (tư thế không đổi) → "D"; hoàn tác lần kéo đó thì bỏ luôn bước của lõi
  const engPop = () => { const b = document.getElementById("undo"); if (b && b.onclick && eng() && eng().canUndo()) b.onclick();  };   // gọi thẳng: click() lồng trong click của chính nút bị trình duyệt bỏ qua
  P.canUndo = () => undoS.length > 0;
  P.undo = () => {
    if (!undoS.length) return false; objs = JSON.parse(undoS.pop());
    const t = ord.length && ord[ord.length - 1] !== "E" ? ord.pop() : (dropLast("P"), null); if (t === "D") engPop(); if (sel && !byId(sel)) select(null); edit = null; changed();
    if (sel) { const L = live.get(sel); if (L && V.gizmo.tc.object !== L.root) select(sel); }
    ST.toast("Hoàn tác: vật thể phụ" + (P.lastLabel ? " (" + P.lastLabel + ")" : "")); return true;
  };
  const propsFirst = () => undoS.length > 0 && (ord[ord.length - 1] !== "E" || !(eng() && eng().canUndo()));
  document.addEventListener("click", e => {   // nút #undo của lõi Pose (Ctrl+Z của lõi cũng bấm nút này)
    if (!e.target.closest || !e.target.closest("#undo")) return;
    if (!propsFirst()) { dropLast("E"); return; }   // lõi Pose hoàn tác bước khớp của nó
    e.stopImmediatePropagation(); e.preventDefault(); P.undo();
  }, true);
  ST.on("prerender", () => { const g = eng() && eng().get(); if (g && g.frame !== ordFrame) { ordFrame = g.frame; ord = ord.filter(t => t !== "E").map(t => t === "D" ? "P" : t); } });   // lõi xoá hàng của nó khi đổi frame
  document.addEventListener("keydown", e => {   // phím sửa key của lõi (S, Delete, Ctrl+V) = sửa khớp
    if (ST.focus !== "pose" || /INPUT|TEXTAREA|SELECT/.test((e.target || {}).tagName || "")) return;
    const k = e.key.toLowerCase(); if ((!e.ctrlKey && !e.metaKey && (k === "s" || e.key === "Delete")) || ((e.ctrlKey || e.metaKey) && k === "v")) P.touchEngine();
  }, true);

  const byId = id => objs.find(o => o.id === id);
  const byName = n => objs.find(o => o.name === n) || objs.find(o => o.id === n);
  const objOf = n => { const o = byName(n); need(o, "Không có vật thể " + n + (objs.length ? " (có: " + objs.map(x => x.name).join(", ") + ")" : " (chưa có vật thể nào)")); return o; };
  const frames = () => { const g = eng() && eng().get(); return g && g.P ? g.P.frames || 1 : 1; };
  const curF = () => { const g = eng() && eng().get(); return g ? g.frame : 1; };
  const clampF = f => Math.max(1, Math.min(frames(), Math.round(+f) || 1));
  const keysOf = o => Object.keys(o.keys).map(Number).sort((a, b) => a - b);

  // ---- cha: xương của model anim (vị trí + hướng thế giới, bỏ scale) ở frame f; null = world
  let cache = {}, cacheSig = "";
  function parTR(par, f) {
    if (!par) return null;
    const e = eng(), g = e && e.get(); if (!g || !g.model || !g.B[par]) return null;
    if (f === g.frame) { const p = new V3(), q = new Q(), s = new V3(); g.B[par].updateWorldMatrix(true, false); g.B[par].matrixWorld.decompose(p, q, s); return { p, q }; }
    const c = cache[f] || (cache[f] = {});
    if (!c[par]) {
      const names = new Set([par]); objs.forEach(o => Object.values(o.keys).forEach(k => { if (k.par) names.add(k.par); }));
      Object.assign(c, e.sampleBones ? e.sampleBones(f, [...names].filter(n => !c[n])) : {});
    }
    return c[par] || null;
  }
  const compose = (tr, p, q) => tr ? { p: p.clone().applyQuaternion(tr.q).add(tr.p), q: tr.q.clone().multiply(q) } : { p: p.clone(), q: q.clone() };
  const relTo = (tr, w) => { if (!tr) return { p: w.p.clone(), q: w.q.clone() }; const qi = tr.q.clone().invert(); return { p: w.p.clone().sub(tr.p).applyQuaternion(qi), q: qi.multiply(w.q) }; };
  const kP = k => new V3().fromArray(k.p), kQ = k => new Q().fromArray(k.q);
  const keyWorld = (k, f) => compose(parTR(k.par, f), kP(k), kQ(k));   // key k với cha của nó ở frame f
  function inSpace(k, kf, par) {   // key k (ở frame kf) đổi sang không gian cha par, dùng tư thế ở chính frame của key
    if ((k.par || null) === (par || null)) return { p: kP(k), q: kQ(k) };
    return relTo(parTR(par, kf), keyWorld(k, kf));
  }
  const hermite = (p0, p1, m0, m1, t) => { const t2 = t * t, t3 = t2 * t; return p0.clone().multiplyScalar(2 * t3 - 3 * t2 + 1).add(m0.clone().multiplyScalar(t3 - 2 * t2 + t)).add(p1.clone().multiplyScalar(-2 * t3 + 3 * t2)).add(m1.clone().multiplyScalar(t3 - t2)); };
  // thế giới của vật thể ở frame f: {p, q, vis, par (cha của đoạn đang chạy)}
  function evalAt(o, f) {
    const ks = keysOf(o); if (!ks.length) return null;
    let ia = -1; for (let i = 0; i < ks.length; i++) if (ks[i] <= f) ia = i;
    if (ia < 0) { const k = o.keys[ks[0]]; return Object.assign(keyWorld(k, f), { vis: k.v !== false, par: k.par || null }); }
    const fa = ks[ia], A = o.keys[fa], vis = A.v !== false, par = A.par || null;
    const mode = A.i || o.interp || "linear";
    if (ia === ks.length - 1 || fa === f || mode === "step") return Object.assign(keyWorld(A, f), { vis, par });
    const fb = ks[ia + 1], Bk = o.keys[fb], t = (f - fa) / (fb - fa);
    const a = { p: kP(A), q: kQ(A) }, b = inSpace(Bk, fb, par);
    let p;
    if (mode === "spline") {   // Hermite, tiếp tuyến theo key hai bên (đổi về cùng không gian), tính theo khoảng frame
      const pr = ia > 0 ? inSpace(o.keys[ks[ia - 1]], ks[ia - 1], par) : null, nx = ia + 2 < ks.length ? inSpace(o.keys[ks[ia + 2]], ks[ia + 2], par) : null;
      const span = fb - fa;
      const m0 = pr ? b.p.clone().sub(pr.p).multiplyScalar(span / (fb - ks[ia - 1])) : b.p.clone().sub(a.p);
      const m1 = nx ? nx.p.clone().sub(a.p).multiplyScalar(span / (ks[ia + 2] - fa)) : b.p.clone().sub(a.p);
      p = hermite(a.p, b.p, m0, m1, t);
    } else p = a.p.clone().lerp(b.p, t);
    const q = a.q.clone().slerp(b.q, mode === "spline" ? t * t * (3 - 2 * t) : t);
    return Object.assign(compose(parTR(par, f), p, q), { vis, par });
  }
  const parAt = (o, f) => { const ks = keysOf(o); let k = null; for (const x of ks) if (x <= f) k = o.keys[x]; return ((k || o.keys[ks[0]] || {}).par) || null; };

  // ---- hình
  function primGeo(o) {
    if (o.kind === "box") { const [x, y, z] = (o.size || [20, 20, 20]).map(v => v / 100); const g = new THREE.BoxGeometry(x, y, z); g.translate(0, y / 2, 0); return g; }
    if (o.kind === "capsule") {   // gốc ở chân, cao h, bán kính r (cm)
      const r = (o.r || 25) / 100, h = Math.max(2 * r, (o.h || 180) / 100), pts = [];
      for (let i = 0; i <= 8; i++) { const a = -Math.PI / 2 + i / 8 * Math.PI / 2; pts.push(new THREE.Vector2(Math.max(1e-4, r * Math.cos(a)), r + r * Math.sin(a))); }
      for (let i = 0; i <= 8; i++) { const a = i / 8 * Math.PI / 2; pts.push(new THREE.Vector2(Math.max(1e-4, r * Math.cos(a)), h - r + r * Math.sin(a))); }
      return new THREE.LatheGeometry(pts, 20);
    }
    const g = new THREE.BufferGeometry(), G = o.geo || {};
    g.setAttribute("position", new THREE.Float32BufferAttribute(G.p || [], 3));
    if (G.uv) g.setAttribute("uv", new THREE.Float32BufferAttribute(G.uv, 2));
    if (G.i) g.setIndex(G.i);
    g.computeVertexNormals(); return g;
  }
  function findSrcMesh(name) {   // mesh nguồn: trong model anim trước, rồi mesh của Cảnh (gồm mesh nhập FBX)
    const g = eng() && eng().get(); let m = null;
    if (g && g.model) g.model.traverse(x => { if (!m && x.isMesh && x.name === name) m = x; });
    if (m) return { mesh: m, from: "anim" };
    const s = ST.mods.mesh && ST.mods.mesh.byName ? ST.mods.mesh.byName(name) : null;
    return s && s.mesh ? { mesh: s.mesh, from: "scene" } : null;
  }
  function material(o) {
    if (o.kind === "mesh" && o.src) { const s = findSrcMesh(o.src); if (s && s.from === "anim" && s.mesh.material && !Array.isArray(s.mesh.material)) { const m = s.mesh.material.clone(); m.skinning = false; return m; } }
    return new THREE.MeshStandardMaterial({ color: new THREE.Color(o.color || (o.kind === "mesh" ? "#c8b48a" : "#d9734a")), roughness: 0.7, metalness: 0.05 });
  }
  function rebuildAll() {
    const e = eng(), sc = ST.poseScenes && ST.poseScenes();
    if (!sc || !sc.scene) return;
    if (!group) { group = new THREE.Group(); group.name = "__props"; }
    if (group.parent !== sc.scene) sc.scene.add(group);
    if (sc.scene.onBeforeRender !== beforeRender) { const prev = sc.scene.onBeforeRender; sc.scene.onBeforeRender = beforeRender; beforeRender.prev = prev && prev !== beforeRender ? prev : null; }
    const ids = new Set(objs.map(o => o.id));
    for (const [id, L] of live) if (!ids.has(id)) { if (V.gizmo.tc.object === L.root) V.gizmo.tc.detach(); group.remove(L.root); L.mesh.geometry.dispose(); live.delete(id); }
    objs.forEach(o => {
      const sig = JSON.stringify([o.kind, o.size, o.r, o.h, o.color, o.src, o.geo ? o.geo.p.length : 0]);
      let L = live.get(o.id);
      if (L && L.sig === sig) { L.root.name = o.name; return; }
      if (L) { group.remove(L.root); L.mesh.geometry.dispose(); }
      const root = new THREE.Object3D(); root.name = o.name; root.userData.prop = o.id;
      const mesh = new THREE.Mesh(primGeo(o), material(o)); mesh.userData.prop = o.id; mesh.castShadow = true; root.add(mesh); group.add(root);
      live.set(o.id, L = { root, mesh, sig });
    });
    if (e) update();
  }
  // ---- mỗi lần vẽ cảnh Pose (viewport, phát, playblast): đặt vật thể theo frame đang hiện
  function beforeRender(...a) { if (beforeRender.prev) beforeRender.prev.apply(this, a); update(); }
  function update() {
    const e = eng(), g = e && e.get(); if (!g || !g.model) return;
    const k = curKey(); if (k !== docKey) { if (!loading) load(k); return; }
    const sig = g.model.uuid + ":" + g.frame + ":" + dirty; if (sig !== cacheSig) { cache = {}; cacheSig = sig; }
    const hide = new Set();
    objs.forEach(o => {
      const L = live.get(o.id); if (!L) return;
      if (edit && edit.id === o.id && edit.f === g.frame) { L.root.visible = !o.off; return; }   // đang kéo gizmo: giữ chỗ kéo
      if (edit && edit.id === o.id) edit = null;   // đổi frame: bỏ phần kéo chưa key
      const w = evalAt(o, g.frame); if (!w) { L.root.visible = false; return; }
      L.root.position.copy(w.p); L.root.quaternion.copy(w.q); L.root.visible = w.vis && !o.off; L.root.updateMatrixWorld(true);
      if (o.hideSrc && o.src && !o.off) hide.add(o.src);   // vật thể thay mesh gốc cả khi đang ẩn theo key (Reload: tên chưa có trên rãnh tới F20)
    });
    g.model.traverse(x => { if (!x.isMesh) return; if (hide.has(x.name)) { if (x.visible) { x.visible = false; hidSrc.add(x); } } else if (hidSrc.has(x)) { x.visible = true; hidSrc.delete(x); } });
  }
  P.update = update;

  // ---- thao tác (dùng chung cho panel, Outliner, cầu nối)
  const uid = () => "o" + Math.random().toString(36).slice(2, 8);
  const uniq = n => { let s = n || "obj", i = 2; while (objs.some(o => o.name === s)) s = (n || "obj") + "_" + i++; return s; };
  const round = (a, d) => Array.from(a, v => +(+v).toFixed(d));
  function copyGeo(src, par, f) {   // đỉnh đã pose của mesh nguồn (frame đang xem) → toạ độ của vật thể (= cha ở frame f, hoặc tâm hộp bao)
    const m = src.mesh; m.updateWorldMatrix(true, false);
    const pos = m.geometry.attributes.position, uv = m.geometry.attributes.uv, n = pos.count, W = [], v = new V3();
    for (let i = 0; i < n; i++) { v.fromBufferAttribute(pos, i); if (m.isSkinnedMesh) m.boneTransform(i, v); v.applyMatrix4(m.matrixWorld); W.push(v.clone()); }
    let tr = parTR(par, f);
    if (!tr) { const b = new THREE.Box3(); W.forEach(x => b.expandByPoint(x)); tr = { p: b.getCenter(new V3()), q: new Q() }; }
    const qi = tr.q.clone().invert(), p = [];
    W.forEach(x => { const l = x.clone().sub(tr.p).applyQuaternion(qi); p.push(l.x, l.y, l.z); });
    const idx = m.geometry.index ? Array.from(m.geometry.index.array) : null;
    return { geo: { p: round(p, 5), i: idx, uv: uv ? round(uv.array, 4) : null }, tr };
  }
  function domBone(m) {   // xương có trọng số lớn nhất của mesh skin (vd mũi tên → slingshot_1)
    if (!m.isSkinnedMesh || !m.geometry.attributes.skinIndex) return null;
    const si = m.geometry.attributes.skinIndex, sw = m.geometry.attributes.skinWeight, acc = {};
    for (let i = 0; i < si.count; i++) for (let k = 0; k < 4; k++) { const w = sw.array[i * 4 + k]; if (w > 0) { const b = m.skeleton.bones[si.array[i * 4 + k]]; if (b) acc[b.name] = (acc[b.name] || 0) + w; } }
    return Object.entries(acc).sort((a, b) => b[1] - a[1]).map(x => x[0])[0] || null;
  }
  function ready() { const g = eng() && eng().get(); need(g && g.model, "Anim chưa nạp xong"); need(curKey() === docKey && !loading, "Vật thể của phiên bản đang nạp, thử lại"); return g; }
  P.add = ({ name, mesh, box, capsule, bone, f, at, color, hideSrc } = {}) => {
    const g = ready(); f = clampF(f || g.frame);
    const o = { id: uid(), name: uniq(name || (mesh ? mesh.replace(/^.*_/, "") : box ? "box" : "dummy")), kind: mesh ? "mesh" : box ? "box" : "capsule", interp: "linear", keys: {} };
    if (color) o.color = color;
    let par = null, tr = null;
    if (mesh) {
      const s = findSrcMesh(mesh); need(s, "Không có mesh " + mesh + " trong model anim hay Cảnh");
      par = bone === undefined ? (s.from === "anim" ? domBone(s.mesh) : null) : (bone === "world" ? null : bone);
      if (par) need(g.B[par], "Không có xương " + par);
      if (f !== g.frame) need(!par, "Bản sao mesh lấy hình ở frame đang xem: chuyển tới F" + f + " trước (anim frame " + f + ")");
      const c = copyGeo(s, par, f); o.src = mesh; o.geo = c.geo; tr = c.tr; o.hideSrc = hideSrc !== undefined ? !!hideSrc : s.from === "anim";
      o.keys[f] = { par, p: par ? [0, 0, 0] : round(tr.p.toArray(), 5), q: [0, 0, 0, 1] };
    } else {
      if (box) o.size = (Array.isArray(box) ? box : [20, 20, 20]).map(Number); else { const c = Array.isArray(capsule) ? capsule : [25, 180]; o.r = +c[0]; o.h = +c[1]; }
      par = bone && bone !== "world" ? bone : null; if (par) need(g.B[par], "Không có xương " + par);
      const t0 = parTR(par, f), w = { p: at ? fromB(at) : t0 ? t0.p.clone() : new V3(), q: t0 && !at ? t0.q.clone() : new Q() };   // gắn xương, không --at: đặt đúng ở xương
      const l = relTo(parTR(par, f), w); o.keys[f] = { par, p: round(l.p.toArray(), 5), q: round(l.q.toArray(), 6) };
    }
    pushUndo(); objs.push(o); sel = o.id; changed("Thêm " + o.name); return describe(o);
  };
  function worldNow(o, f) {   // thế giới ở frame f; đang kéo gizmo ở chính frame đó thì lấy chỗ kéo
    const L = live.get(o.id);
    if (edit && edit.id === o.id && edit.f === f && L) return { p: L.root.position.clone(), q: L.root.quaternion.clone(), vis: true };
    return evalAt(o, f) || { p: new V3(), q: new Q(), vis: true };
  }
  const axisOf = o => { const a = o.axis || "+z", v = new V3(); v[a.slice(-1)] = a[0] === "-" ? -1 : 1; return v; };
  // đặt key ở frame f: chỉnh vị trí / hướng thế giới theo tuỳ chọn, cha = par (nếu có) hoặc cha của key / đoạn đang chạy
  P.key = (n, { f, at, move, along, rot, aim, par, interp, vis } = {}) => {
    ready(); const o = objOf(n); f = clampF(f || curF());
    const w = worldNow(o, f), old = o.keys[f];
    if (at) w.p.copy(fromB(at));
    if (move) w.p.add(fromB(move));
    if (along) w.p.add(axisOf(o).applyQuaternion(w.q).multiplyScalar(+along / 100));
    if (rot) w.q.copy(qFromB(rot));
    if (aim) { const d = fromB(aim).sub(w.p); need(d.lengthSq() > 1e-8, "Điểm nhắm trùng vị trí vật thể"); const cur = axisOf(o).applyQuaternion(w.q); w.q.premultiply(new Q().setFromUnitVectors(cur.normalize(), d.normalize())); }
    const P2 = par !== undefined ? (par === "world" || !par ? null : par) : (old ? old.par || null : parAt(o, f));
    if (P2) need(eng().get().B[P2], "Không có xương " + P2);
    const l = relTo(parTR(P2, f), w);
    pushUndo();
    const k = { par: P2, p: round(l.p.toArray(), 5), q: round(l.q.normalize().toArray(), 6) };
    if (old && old.i) k.i = old.i; if (old && old.v === false) k.v = false;
    if (interp) k.i = interp; if (vis !== undefined) k.v = !!vis;
    o.keys[f] = k; if (edit && edit.id === o.id) edit = null;
    changed("Key " + o.name + " F" + f); return describe(o, f);
  };
  P.unkey = (n, f) => { ready(); const o = objOf(n); f = clampF(f || curF()); need(o.keys[f], o.name + " không có key F" + f); need(keysOf(o).length > 1, "Key cuối cùng: xoá vật thể bằng obj del"); pushUndo(); delete o.keys[f]; changed(); return describe(o); };
  P.parent = (n, par, f) => P.key(n, { f, par: par || "world" });   // gắn / thả ở frame f, giữ nguyên chỗ
  P.set = (n, a = {}) => {
    ready(); const o = objOf(n); pushUndo();
    if (a.rename) { need(!objs.some(x => x !== o && x.name === a.rename), "Đã có vật thể " + a.rename); o.name = a.rename; }
    if (a.interp) { need(["step", "linear", "spline"].includes(a.interp), "interp: step | linear | spline"); o.interp = a.interp; Object.values(o.keys).forEach(k => delete k.i); }
    if (a.hideSrc !== undefined) o.hideSrc = !!a.hideSrc;
    if (a.color) o.color = a.color;
    if (a.axis) { need(/^[+-]?[xyz]$/.test(a.axis), "axis: +x | -x | +y | -y | +z | -z"); o.axis = a.axis.length === 1 ? "+" + a.axis : a.axis; }
    if (a.size && o.kind === "box") o.size = a.size.map(Number);
    if (a.capsule && o.kind === "capsule") { o.r = +a.capsule[0]; o.h = +a.capsule[1]; }
    if (a.off !== undefined) o.off = !!a.off;
    changed(); return describe(o);
  };
  P.del = n => { ready(); const o = objOf(n); pushUndo(); objs = objs.filter(x => x !== o); if (sel === o.id) { sel = null; V.gizmo.tc.detach(); } changed("Xoá " + o.name); return { deleted: o.name, left: objs.map(x => x.name) }; };
  function describe(o, f) {
    f = f || curF(); const w = evalAt(o, f) || { p: new V3(), q: new Q(), vis: true }, ax = axisOf(o).applyQuaternion(w.q);
    const b = new THREE.Box3(), L = live.get(o.id); if (L) b.setFromObject(L.mesh);
    return { name: o.name, kind: o.kind, src: o.src || null, interp: o.interp, hideSrc: !!o.hideSrc, axis: o.axis || "+z", off: !!o.off,
      keys: keysOf(o).map(k => ({ f: k, par: o.keys[k].par || "world", i: o.keys[k].i || undefined, v: o.keys[k].v === false ? false : undefined })),
      at: { f, pos: toB(w.p), rot: qToB(w.q), fwd: dirB(ax), vis: !!w.vis && !o.off, par: parAt(o, f) || "world", size_cm: b.isEmpty() ? null : toB(b.getSize(new V3())).map(Math.abs) } };
  }
  P.list = f => { ready(); return { version: docKey, frame: f || curF(), objs: objs.map(o => describe(o, f)) }; };
  P.read = (n, f) => { ready(); const o = objOf(n); const fs = f ? [clampF(f)] : Array.from({ length: frames() }, (_, i) => i + 1); return fs.map(x => { const w = evalAt(o, x); return { f: x, pos: toB(w.p), fwd: dirB(axisOf(o).applyQuaternion(w.q)), vis: w.vis && !o.off, par: parAt(o, x) || "world" }; }); };
  P.count = () => objs.length;
  P.idOf = n => { const o = byName(n); return o ? o.id : null; };

  // ---- chọn + gizmo (lớp Anim): bấm vật thể trong viewport / Outliner / panel
  P.sel = () => sel;
  P.selKeys = () => { const o = sel && objs.find(x => x.id === sel); return o ? { name: o.name, keys: keysOf(o) } : null; };   // timeline: key của vật thể đang chọn
  function select(id) {
    sel = id; const L = id && live.get(id), tc = V.gizmo.tc;
    if (L) {
      const e = eng(); if (e && e.get().sel) e.select(null);
      tc.attach(L.root); tc.setMode(ST.tool === "rot" ? "rotate" : "translate"); tc.setSpace("world");
    } else if (tc.object && tc.object.userData.prop) tc.detach();
    { const e = eng(); if (e && e.renderStrip) e.renderStrip(); }   // timeline đổi ngay sang key của vật thể đang chọn
    ST.refresh();
  }
  P.select = select;
  P.hit = (x, y, p) => {
    if (!group || !ST.layerOn.anim || !objs.length) return null;
    const meshes = [...live.values()].filter(L => L.root.visible).map(L => L.mesh);
    const h = V.raycaster(x, y, p).intersectObjects(meshes, false)[0]; return h ? h.object.userData.prop : null;
  };
  P.pointerDown = (e, p) => {
    if (e.button !== 0) return false;
    const id = P.hit(e.clientX, e.clientY, p);
    if (id) { select(id); return true; }
    if (sel) { sel = null; if (V.gizmo.tc.object && V.gizmo.tc.object.userData.prop) V.gizmo.tc.detach(); }
    return false;
  };
  ST.on("tool", t => { const tc = V.gizmo.tc; if (sel && tc.object && tc.object.userData.prop && (t === "move" || t === "rot")) tc.setMode(t === "rot" ? "rotate" : "translate"); });
  V.gizmo.tc.addEventListener("dragging-changed", e => {
    const tc = V.gizmo.tc, id = tc.object && tc.object.userData.prop; if (!id) { if (e.value && tc.object) P.touchEngine(); return; }   // kéo khớp
    if (e.value) { edit = { id, f: curF() }; }
    else if (edit && edit.id === id) { try { P.key(id, { f: edit.f }); if (ord[ord.length - 1] === "P") ord[ord.length - 1] = "D"; } catch (x) { ST.toast(x.message || String(x)); } }   // thả chuột = key frame này (như Auto key)
  });
  ST.on("prerender", () => {
    const e = eng(); if (!e) return; const g = e.get();
    if (sel && g.sel) sel = null;   // chọn khớp thì bỏ chọn vật thể
    if (curKey() !== docKey && !loading && g.model) load(curKey());
  });

  // ---- Outliner (dưới nút Anim)
  P.outline = () => objs.map(o => ({ id: "o:" + o.id, label: o.name + (o.src ? " · " + o.src : o.kind === "box" ? " · hộp" : o.kind === "capsule" ? " · capsule" : ""), icon: "mesh", sel: sel === o.id, act: sel === o.id, vis: !o.off, del: true, rename: true, count: keysOf(o).length + " key" }));
  P.olAct = (id, a, e, val) => {
    const o = byId(String(id).slice(2)); if (!o) return;
    if (a === "vis") { o.off = !o.off; changed(); return; }
    if (a === "del") { P.del(o.id); return; }
    if (a === "rename") { if (val) try { P.set(o.id, { rename: val }); } catch (x) { ST.toast(x.message); } return; }
    if (ST.focus !== "pose") ST.setFocus("pose");
    select(o.id); if (ST.tabs && ST.tabs().includes("props:list")) ST.showTab("props:list");
  };

  // ---- panel dock "Vật thể"
  P.panel = () => {
    const g = eng() && eng().get();
    if (!g || !g.model) return '<div class="note" style="padding:10px 12px">Mở một anim (lớp Anim) để thêm vật thể phụ.</div>';
    const f = g.frame, o = sel && byId(sel), meshes = []; g.model.traverse(x => { if (x.isMesh && !x.userData.prop) meshes.push(x.name); });
    (ST.mods.mesh && ST.mods.mesh.objects ? ST.mods.mesh.objects() : []).forEach(m => { if (!meshes.includes(m.name)) meshes.push(m.name); });
    const bones = Object.keys(g.markers || {});
    let h = `<div class="pp"><p class="sub" style="margin:0 0 8px">Vật thể xem trước (mũi tên, mục tiêu…): có key riêng, thấy khi phát và trong playblast, không vào FBX. Lưu theo phiên bản ${esc(docKey || "")}.</p>
      <div class="row"><select id="ppMesh" style="flex:1">${meshes.map(n => `<option>${esc(n)}</option>`).join("")}</select><button data-pa="addMesh" title="Bản sao mesh ở frame này, gắn vào xương skin chính của nó">${ic("plus")} Bản sao</button></div>
      <div class="row" style="margin-top:6px"><button data-pa="addBox">${ic("plus")} Hộp</button><button data-pa="addCap" title="Capsule cao 180 cm làm hình nộm">${ic("plus")} Hình nộm</button></div>`;
    h += `<div class="pplist" style="margin-top:10px">${objs.map(x => `<div class="olr ${x.id === sel ? "sel" : ""}" data-pid="${esc(x.id)}" style="cursor:pointer;padding:3px 6px">${esc(x.name)} <small class="sub">${keysOf(x).map(k => "F" + k).join(" ")}</small></div>`).join("") || '<p class="sub">Chưa có vật thể.</p>'}</div>`;
    if (o) {
      const w = describe(o, f), k = o.keys[f], par = parAt(o, f);
      h += `<div class="ppsel" style="margin-top:10px;border-top:1px solid var(--line);padding-top:8px">
        <b>${esc(o.name)}</b> <span class="sub">F${f}${k ? " · có key" : ""} · cha: ${esc(par || "world")}</span>
        <div class="sub" style="margin:4px 0">Vị trí ${w.at.pos.join(", ")} cm · hướng ${w.at.fwd.join(", ")}</div>
        <div class="row"><button data-pa="key" class="on">${ic("key")} Key F${f}</button><button data-pa="unkey" ${k ? "" : "disabled"}>Xoá key</button></div>
        <div class="row" style="margin-top:6px"><label class="sub">Cha từ F${f}</label><select id="ppPar" style="flex:1"><option value="world">world (thả ra)</option>${bones.map(b => `<option ${b === par ? "selected" : ""}>${esc(b)}</option>`).join("")}</select><button data-pa="parent" title="Đặt key ở frame này với cha mới, giữ nguyên chỗ">Đổi cha</button></div>
        <div class="row" style="margin-top:6px"><label class="sub">Nội suy</label><select id="ppInterp">${["step", "linear", "spline"].map(x => `<option ${x === o.interp ? "selected" : ""}>${x}</option>`).join("")}</select>
          ${o.src ? `<label class="sub"><input type="checkbox" id="ppHide" ${o.hideSrc ? "checked" : ""}> ẩn mesh gốc</label>` : ""}</div>
        <div class="row" style="margin-top:6px"><button data-pa="del">${ic("trash")} Xoá vật thể</button></div>
        <p class="sub" style="margin:6px 0 0">Kéo gizmo (W / E) rồi thả = key frame này.</p></div>`;
    }
    return h + "</div>";
  };
  P.panel_click = e => {
    if (ST.focus !== "pose") ST.setFocus("pose");
    const r = e.target.closest("[data-pid]"); if (r) { select(r.dataset.pid); return; }
    const b = e.target.closest("[data-pa]"); if (!b) return;
    const a = b.dataset.pa, $ = ST.$;
    try {
      if (a === "addMesh") P.add({ mesh: $("ppMesh").value });
      else if (a === "addBox") P.add({ box: [20, 20, 20] });
      else if (a === "addCap") P.add({ capsule: [25, 180], name: "dummy" });
      else if (a === "key") P.key(sel);
      else if (a === "unkey") P.unkey(sel);
      else if (a === "parent") P.parent(sel, $("ppPar").value);
      else if (a === "del") P.del(sel);
      if (sel && a.startsWith("add")) select(sel);
    } catch (x) { ST.toast(x.message || String(x)); }
    ST.refresh();
  };
  P.panel_change = e => {
    try {
      if (e.target.id === "ppInterp") P.set(sel, { interp: e.target.value });
      else if (e.target.id === "ppHide") P.set(sel, { hideSrc: e.target.checked });
    } catch (x) { ST.toast(x.message || String(x)); }
  };
  P.loaded = () => !!(eng() && eng().get().model);
})();
