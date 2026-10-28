// AI Anim Studio — module Mesh: chuyển từ Mesh Lab (work/mesh_lab/template.html). Sửa mesh cơ bản trước khi rig:
// chọn mesh / điểm / mặt / khối rời, dời xoay scale (mềm + đối xứng X), Free Transform, tách gộp hàn dọn, đặt sàn, chiều cao, kiểm tra.
// Dữ liệu cm, +Y lên, nằm trong ST.view.cm. Lưu cùng chỗ Mesh Lab cũ (kho <nhân vật>_mesh_lab, doc mesh/edit) nên Rig Lab vẫn đọc được.
(function () {
  const V = ST.view, esc = ST.esc, ic = ST.ic, V3 = THREE.Vector3, M4 = THREE.Matrix4;
  const M = ST.mods.mesh = { id: "mesh" };
  const COLORS = [0x9bb0d0, 0xd0b08a, 0x9fcfa8, 0xd09fb8, 0xb9a9e0, 0xd7d08a];
  let OBJ = [], active = null, selO = new Set(), selV = new Set(), selF = new Set();
  let mode = "o", showWire = ST.pref.get("mesh:wire", true), soft = { on: false, r: 12 }, sym = false, frontOnly = true, uid = 1, style = "edit";
  let weldEps = 0.05, ver = 0, editAt = null, dirty = false, saveT = 0, store = null, ORIG = null, TS = null;
  M.objects = () => OBJ; M.ver = () => ver; M.isDirty = () => dirty; M.editAt = () => editAt;   // module Rig dùng mesh đã sửa
  const foc = () => ST.focus === "mesh";   // đang sửa mesh / xương (focus), lớp Cảnh đang hiện

  const root = V.cm;
  const selPts = new THREE.Points(new THREE.BufferGeometry(), new THREE.PointsMaterial({ size: 7, sizeAttenuation: false, color: 0xff7a1a, depthTest: false, transparent: true }));
  selPts.renderOrder = 20; root.add(selPts);
  const selMesh = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshBasicMaterial({ color: 0xff7a1a, transparent: true, opacity: 0.55, side: THREE.DoubleSide, depthTest: false }));
  selMesh.renderOrder = 19; root.add(selMesh);

  // ---------------------------------------------------------------- đối tượng
  const nV = o => o.pos.length / 3, nT = o => o.idx.length / 3, get = id => OBJ.find(o => o.id === id);
  function makeObj(name, pos, idx, extra) {
    const o = Object.assign({ id: uid++, name, pos, idx, vis: true, lock: false }, extra || {});
    o.color = o.color || COLORS[(o.id - 1) % COLORS.length];
    buildGeo(o); OBJ.push(o); return o;
  }
  function disposeObj(o) { root.remove(o.mesh); o.mesh.geometry.dispose(); o.mesh.material.dispose(); o.wire.material.dispose(); o.pts.material.dispose(); }
  function buildGeo(o) {
    if (o.mesh) disposeObj(o);
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(o.pos, 3)); g.setIndex(new THREE.BufferAttribute(o.idx, 1));
    g.computeVertexNormals(); g.computeBoundingSphere(); g.computeBoundingBox();
    o.mesh = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: o.color, side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 }));
    o.mesh.userData.oid = o.id;
    o.wire = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: 0x1b2230, wireframe: true, transparent: true, opacity: 0.22, depthWrite: false }));
    o.pts = new THREE.Points(g, new THREE.PointsMaterial({ size: 3.5, sizeAttenuation: false, color: 0x1b2230 }));
    o.mesh.add(o.wire); o.mesh.add(o.pts); root.add(o.mesh); o.mirror = null; o.adj = null; o.def = null;
    applyVis(o); if (o.skin) deform(o, posed());
  }

  // ---------------------------------------------------------------- skin FBX: mesh đi theo joint (workspace General)
  // o.pos luôn là mesh bind (lưu, Rig đọc); khi xương đang pose, hình hiển thị = Σ w·D·v với D = ST.mods.skel.skinMat(xương).
  const posed = () => !!(ST.mods.skel && ST.mods.skel.posed && ST.mods.skel.posed());
  let RIGSKIN = null;   // skin đã dựng ở workspace Rig (doc rig/skin): dùng cho mesh thân thay skin khách của FBX
  function skinOf(name, n) {   // weights của FBX: {xương: [[đỉnh], [w]]} → 4 ảnh hưởng mạnh nhất mỗi đỉnh, chuẩn hoá
    if (RIGSKIN && RIGSKIN.nv === n && RIGSKIN.names) return { bones: RIGSKIN.names, B: Uint16Array.from(RIGSKIN.I), W: Float32Array.from(RIGSKIN.W) };
    if (ST.rigState && ST.rigState.source !== "guest") return null;   // đã xoá xương (mesh tĩnh) hoặc đã rig nhưng chưa có skin: không dùng skin của FBX
    const m = (ORIG || []).find(x => x.name === name && x.weights); if (!m || m.verts.length / 3 !== n) return null;
    const bones = Object.keys(m.weights), per = Array.from({ length: n }, () => []);
    bones.forEach((b, bi) => { const [ix, ws] = m.weights[b]; ix.forEach((v, k) => { if (v < n && ws[k] > 0) per[v].push([bi, ws[k]]); }); });
    const B = new Uint16Array(n * 4), W = new Float32Array(n * 4);
    per.forEach((l, v) => { l.sort((a, c) => c[1] - a[1]); const top = l.slice(0, 4), s = top.reduce((a, x) => a + x[1], 0) || 1; top.forEach(([bi, w], k) => { B[4 * v + k] = bi; W[4 * v + k] = w / s; }); });
    return { bones, B, W };
  }
  const ID16 = new M4().elements;
  function deform(o, on) {
    const g = o.mesh.geometry, attr = g.attributes.position;
    if (!on || !o.skin) { if (attr.array !== o.pos) { g.setAttribute("position", new THREE.BufferAttribute(o.pos, 3)); g.computeVertexNormals(); g.computeBoundingSphere(); g.computeBoundingBox(); } return; }
    const n = nV(o), P = o.pos, out = o.def && o.def.length === P.length ? o.def : (o.def = new Float32Array(P.length)), { bones, B, W } = o.skin;
    const E = bones.map(b => { const m = ST.mods.skel.skinMat(b); return m ? m.elements : ID16; });
    for (let i = 0; i < n; i++) {
      const x = P[3 * i], y = P[3 * i + 1], z = P[3 * i + 2]; let ox = 0, oy = 0, oz = 0, ws = 0;
      for (let k = 0; k < 4; k++) { const w = W[4 * i + k]; if (!w) continue; const e = E[B[4 * i + k]]; ox += w * (e[0] * x + e[4] * y + e[8] * z + e[12]); oy += w * (e[1] * x + e[5] * y + e[9] * z + e[13]); oz += w * (e[2] * x + e[6] * y + e[10] * z + e[14]); ws += w; }
      if (ws < 1e-6) { ox = x; oy = y; oz = z; }
      out[3 * i] = ox; out[3 * i + 1] = oy; out[3 * i + 2] = oz;
    }
    if (attr.array !== out) g.setAttribute("position", new THREE.BufferAttribute(out, 3)); else attr.needsUpdate = true;
    g.computeVertexNormals(); g.computeBoundingSphere(); g.computeBoundingBox();
  }
  ST.on("skel:pose", () => { const on = posed(); OBJ.forEach(o => deform(o, on)); placePivot && placePivot(); });
  const frozen = () => posed() && (mode === "o" ? [...selO].some(i => (get(i) || {}).skin) : !!(active && active.skin));   // mesh skin đang pose: không sửa đỉnh
  function touchGeo(o, full) { const g = o.mesh.geometry; g.attributes.position.needsUpdate = true; g.computeVertexNormals(); if (full) { g.computeBoundingSphere(); g.computeBoundingBox(); } }
  function applyVis(o) {
    const edit = style === "edit", mat = o.mesh.material;
    o.mesh.visible = o.vis && style !== "hidden"; o.wire.visible = edit && showWire; o.pts.visible = edit && mode === "v" && o === active;
    mat.transparent = style === "rig"; mat.opacity = style === "rig" ? 0.35 : 1; mat.depthWrite = style !== "rig"; mat.color.setHex(o.color);
    mat.emissive.setHex(edit && selO.has(o.id) && mode === "o" ? 0x2a3f7a : 0x000000);
  }
  function allVis() { OBJ.forEach(applyVis); }
  function removeObj(o) { disposeObj(o); OBJ = OBJ.filter(x => x !== o); selO.delete(o.id); if (active === o) active = OBJ[0] || null; }
  M.display = s => { style = s; allVis(); refreshSel(); };
  const shownNow = () => ST.layerOn.scene && ST.focus !== "rig";   // W3b: đang sửa rig thì lõi Rig vẽ nhân vật
  M.layer = () => M.display(shownNow() ? "edit" : "hidden");   // lớp Nhân vật (mesh + xương)
  ST.on("focus", () => { const want = shownNow() ? "edit" : "hidden"; if (style !== want) M.display(want); });

  // ---------------------------------------------------------------- undo (lịch sử chung)
  M.snap = () => ({ act: active && active.id, sel: [...selO], sv: [...selV], sf: [...selF], mode, o: OBJ.map(o => ({ id: o.id, name: o.name, vis: o.vis, lock: o.lock, color: o.color, pos: o.pos.slice(), idx: o.idx.slice(), skin: o.skin || null, piv: o.piv || null, zero: o.zero || null })), cp: cPiv });
  M.restore = s => {
    OBJ.slice().forEach(disposeObj); OBJ = []; TS = null;
    s.o.forEach(d => { const o = Object.assign({}, d); buildGeo(o); OBJ.push(o); });
    active = get(s.act) || OBJ[0] || null; selO = new Set(s.sel.filter(i => get(i))); clearSel(); cPiv = s.cp || null;
    if (active && (s.act === active.id)) { const n = nV(active), t = nT(active); selV = new Set((s.sv || []).filter(i => i < n)); selF = new Set((s.sf || []).filter(f => f < t)); }   // giữ vùng chọn điểm/mặt
    allVis(); changed(); refreshSel();
  };
  const pushUndo = label => ST.hist.push(M, label || "Sửa mesh");
  function changed() { ver++; dirty = true; ST.saveState("Chưa lưu…", "dirty"); clearTimeout(saveT); saveT = setTimeout(save, 1500); }

  // ---------------------------------------------------------------- chọn
  function clearSel() { selV = new Set(); selF = new Set(); }
  function facesOfVerts(o, vs, all) {
    const f = new Set(), I = o.idx;
    for (let t = 0; t < I.length / 3; t++) { const a = vs.has(I[3 * t]), b = vs.has(I[3 * t + 1]), c = vs.has(I[3 * t + 2]); if (all ? (a && b && c) : (a || b || c)) f.add(t); }
    return f;
  }
  function vertsOfFaces(o, fs) { const v = new Set(); fs.forEach(t => { v.add(o.idx[3 * t]); v.add(o.idx[3 * t + 1]); v.add(o.idx[3 * t + 2]); }); return v; }
  function setVerts(vs) { selV = new Set(vs); selF = active ? facesOfVerts(active, selV, true) : new Set(); refreshSel(); }
  function setFaces(fs) { selF = new Set(fs); selV = active ? vertsOfFaces(active, selF) : new Set(); refreshSel(); }
  function adjacency(o) {
    if (o.adj) return o.adj;
    const vf = Array.from({ length: nV(o) }, () => []);
    for (let t = 0; t < nT(o); t++) for (let k = 0; k < 3; k++) vf[o.idx[3 * t + k]].push(t);
    return (o.adj = vf);
  }
  function islandFrom(o, f0) {
    const vf = adjacency(o), seen = new Set([f0]), q = [f0];
    while (q.length) { const t = q.pop(); for (let k = 0; k < 3; k++) for (const u of vf[o.idx[3 * t + k]]) if (!seen.has(u)) { seen.add(u); q.push(u); } }
    return seen;
  }
  const selSig = () => mode === "o" ? "o:" + [...selO].sort().join(",") : mode + ":" + (active ? active.id : 0) + ":" + selV.size + ":" + (() => { let h = 0; selV.forEach(i => h = (h * 31 + i) % 1000003); return h; })();
  function overlayPositions() {
    const o = active, P = [], F = [];
    if (o && mode !== "o" && style === "edit") {
      selV.forEach(i => P.push(o.pos[3 * i], o.pos[3 * i + 1], o.pos[3 * i + 2]));
      selF.forEach(t => { for (let k = 0; k < 3; k++) { const i = o.idx[3 * t + k]; F.push(o.pos[3 * i], o.pos[3 * i + 1], o.pos[3 * i + 2]); } });
    }
    selPts.geometry.dispose(); selPts.geometry = new THREE.BufferGeometry(); selPts.geometry.setAttribute("position", new THREE.Float32BufferAttribute(P, 3));
    selMesh.geometry.dispose(); selMesh.geometry = new THREE.BufferGeometry(); selMesh.geometry.setAttribute("position", new THREE.Float32BufferAttribute(F, 3));
  }
  function refreshSel() {
    if (TS && TS.sig !== selSig()) TS = null;
    overlayPositions();
    const edit = style === "edit";
    selPts.visible = edit && (mode === "v" || mode === "f" || mode === "i"); selMesh.visible = edit && (mode === "f" || mode === "i");
    placePivot(); ST.chRefresh && ST.chRefresh(); ST.refresh();
  }
  function selCenter() {
    const c = new V3(); let n = 0;
    if (mode === "o") selO.forEach(id => { const o = get(id); if (!o || !o.vis) return; o.mesh.geometry.computeBoundingBox(); c.add(o.mesh.geometry.boundingBox.getCenter(new V3())); n++; });
    else if (active) selV.forEach(i => { c.x += active.pos[3 * i]; c.y += active.pos[3 * i + 1]; c.z += active.pos[3 * i + 2]; n++; });
    return n ? c.multiplyScalar(1 / n) : null;
  }
  // ---------------------------------------------------------------- pivot kiểu Maya: mỗi mesh một pivot (o.piv, cm; null = tâm hộp bao), vùng điểm/mặt có pivot tạm (cPiv)
  // Giữ D hoặc bật/tắt Insert: gizmo chỉ dời pivot, không dời mesh. Xoay / scale (gizmo, Channel Box) quay quanh pivot.
  let cPiv = null, pivEdit = false, pivHold = false;
  const pivOn = () => pivEdit || pivHold;
  const refObj = () => mode === "o" ? (active && selO.has(active.id) ? active : get([...selO][0])) : null;
  const zeroOf = () => { const o = refObj(); return o && o.zero ? o.zero.clone() : new V3(); };   // Freeze: Translate trong Channel Box tính từ đây
  function pivotPoint() {
    if (mode === "o") { const o = refObj(); if (o && o.piv) return o.piv.clone(); return selCenter(); }
    if (cPiv && cPiv.sig === selSig()) return cPiv.p.clone();
    return selCenter();
  }
  function setPiv(p) {
    if (mode === "o") selO.forEach(id => { const o = get(id); if (o && !o.lock) o.piv = p ? p.clone() : null; });
    else cPiv = p ? { sig: selSig(), p: p.clone() } : null;
    TS = null;
  }
  const SK = () => (ST.mods.skel && ST.mods.skel.sel() ? ST.mods.skel : null);   // joint đang chọn thì gizmo / Channel Box sửa joint
  function placePivot() {
    const G = V.gizmo;
    if (style !== "edit" || !foc()) { if (foc()) G.detach(); buildFree(); return; }
    const sk = SK();
    if (sk) { const t = ST.tool; if (t === "move" || t === "rot" || t === "scl") G.place(sk.selPos(), root, t === "move" ? "translate" : t === "rot" ? "rotate" : "scale"); else G.detach(); buildFree(); return; }
    if (frozen()) { G.detach(); buildFree(); return; }
    const t = pivOn() ? "move" : ST.tool, c = t === "sel" || t === "free" ? null : pivotPoint(), lockedObj = mode === "o" && [...selO].every(i => (get(i) || {}).lock);
    if (!c || lockedObj || (mode !== "o" && active && active.lock)) G.detach();
    else G.place(c, root, t === "move" ? "translate" : t === "rot" ? "rotate" : "scale");
    buildFree();
  }
  ST.on("tool", () => { if (foc()) placePivot(); });
  ST.on("jsel", n => { if (n) { selO.clear(); clearSel(); TS = null; allVis(); } refreshSel(); });

  // ---------------------------------------------------------------- biến đổi: falloff mềm + đối xứng X (dùng cho gizmo, Channel Box, Free Transform)
  function mirrorMap(o) {
    if (o.mirror) return o.mirror;
    const n = nV(o), q = 0.4, key = (x, y, z) => Math.round(x / q) + "," + Math.round(y / q) + "," + Math.round(z / q), H = new Map();
    for (let i = 0; i < n; i++) { const k = key(o.pos[3 * i], o.pos[3 * i + 1], o.pos[3 * i + 2]); (H.get(k) || H.set(k, []).get(k)).push(i); }
    const m = new Int32Array(n).fill(-1);
    for (let i = 0; i < n; i++) {
      const x = -o.pos[3 * i], y = o.pos[3 * i + 1], z = o.pos[3 * i + 2]; let best = -1, bd = 0.35 * 0.35;
      for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) for (let dz = -1; dz <= 1; dz++) {
        const c = H.get(key(x + dx * q, y + dy * q, z + dz * q)); if (!c) continue;
        for (const j of c) { const d = (o.pos[3 * j] - x) ** 2 + (o.pos[3 * j + 1] - y) ** 2 + (o.pos[3 * j + 2] - z) ** 2; if (d < bd) { bd = d; best = j; } }
      }
      m[i] = best;
    }
    return (o.mirror = m);
  }
  function falloff(o, src, r) {
    const n = nV(o), w = new Float32Array(n), P = o.pos, S = [...src];
    for (let i = 0; i < n; i++) {
      let d2 = Infinity; for (const j of S) { const d = (P[3 * i] - P[3 * j]) ** 2 + (P[3 * i + 1] - P[3 * j + 1]) ** 2 + (P[3 * i + 2] - P[3 * j + 2]) ** 2; if (d < d2) d2 = d; }
      const t = Math.sqrt(d2) / r; w[i] = t >= 1 ? 0 : (1 - t * t) * (1 - t * t);
    }
    return w;
  }
  function buildAffected() {
    const list = [];
    if (mode === "o") { selO.forEach(id => { const o = get(id); if (o && o.vis && !o.lock) for (let i = 0; i < nV(o); i++) list.push({ o, i, w: 1, m: 0 }); }); return list; }
    const o = active; if (!o) return list;
    const S = selV, P = new Set();
    if (sym) { const mm = mirrorMap(o); S.forEach(i => { const j = mm[i]; if (j >= 0 && j !== i && !S.has(j)) P.add(j); }); }
    const w0 = soft.on && S.size ? falloff(o, S, soft.r) : null, w1 = soft.on && P.size ? falloff(o, P, soft.r) : null;
    for (let i = 0; i < nV(o); i++) {
      if (S.has(i)) list.push({ o, i, w: 1, m: 0 });
      else if (P.has(i)) list.push({ o, i, w: 1, m: 1 });
      else { const a = w0 ? w0[i] : 0, b = w1 ? w1[i] : 0; if (a > 0 || b > 0) list.push({ o, i, w: Math.max(a, b), m: b > a ? 1 : 0 }); }
    }
    return list;
  }
  function affSnapshot() {
    const aff = buildAffected(); aff.forEach(a => { a.p0 = new V3(a.o.pos[3 * a.i], a.o.pos[3 * a.i + 1], a.o.pos[3 * a.i + 2]); });
    aff.pv = mode === "o" ? [...selO].map(get).filter(o => o && o.piv && o.vis && !o.lock).map(o => ({ o, p0: o.piv.clone() })) : cPiv && cPiv.sig === selSig() ? [{ p0: cPiv.p.clone() }] : [];
    return aff;
  }
  function xformApply(Mx, aff) {
    const R = new M4().makeScale(-1, 1, 1), Mm = R.clone().multiply(Mx).multiply(R), tmp = new V3(), os = new Set();
    for (const a of aff) {
      tmp.copy(a.p0).applyMatrix4(a.m ? Mm : Mx); const P = a.o.pos, i = a.i;
      P[3 * i] = a.p0.x + (tmp.x - a.p0.x) * a.w; P[3 * i + 1] = a.p0.y + (tmp.y - a.p0.y) * a.w; P[3 * i + 2] = a.p0.z + (tmp.z - a.p0.z) * a.w; os.add(a.o);
    }
    os.forEach(o => touchGeo(o, false));
    (aff.pv || []).forEach(v => { const p = v.p0.clone().applyMatrix4(Mx); if (v.o) v.o.piv = p; else if (cPiv) cPiv.p = p; });
  }
  function xformEnd(aff) { new Set(aff.map(a => a.o)).forEach(o => { touchGeo(o, true); o.mirror = null; }); changed(); refreshSel(); }
  function ensureTS() { if (!TS) { const c = pivotPoint(); if (!c) return null; TS = { c0: c.clone(), A: new M4(), sig: selSig() }; } return TS; }

  // gizmo chung → ma trận chênh lệch trong toạ độ cm
  let drag = null;
  M.gzStart = () => { if (SK()) return SK().gzStart(); if (pivOn()) { pushUndo("Dời pivot"); drag = { piv: pivotPoint() }; return; } pushUndo("Biến đổi"); ensureTS(); drag = { aff: affSnapshot(), A0: TS ? TS.A.clone() : new M4() }; };
  M.gzChange = Mx => { if (SK()) return SK().gzChange(Mx); if (!drag) return; if (drag.piv) { setPiv(drag.piv.clone().applyMatrix4(Mx)); ST.chRefresh(); return; } xformApply(Mx, drag.aff); if (TS) TS.A = Mx.clone().multiply(drag.A0); overlayPositions(); ST.chRefresh(); };
  M.gzEnd = () => { if (SK()) return SK().gzEnd(); if (!drag) return; if (drag.piv) { drag = null; changed(); refreshSel(); return; } const aff = drag.aff; drag = null; xformEnd(aff); };

  // Channel Box: phép biến đổi cộng dồn của vùng chọn (quanh tâm lúc chọn)
  const rad = d => d * Math.PI / 180, deg = r => r * 180 / Math.PI;
  const MCH = {
    unit: "cm",
    title: () => mode === "o" ? (selO.size > 1 ? selO.size + " mesh" : (active && selO.size ? active.name : "")) : (active ? active.name + " · " + (mode === "v" ? selV.size + " điểm" : selF.size + " mặt") : ""),
    vals() {
      if (frozen()) return null;
      const c = pivotPoint(); if (!c) return null;
      const z = zeroOf();
      if (!TS) return { t: [c.x - z.x, c.y - z.y, c.z - z.z], r: [0, 0, 0], s: [1, 1, 1] };
      const t = TS.c0.clone().applyMatrix4(TS.A).sub(z), L = TS.A.clone().setPosition(0, 0, 0), q = new THREE.Quaternion(), p = new V3(), sc = new V3();
      L.decompose(p, q, sc); const e = new THREE.Euler().setFromQuaternion(q, "XYZ");
      return { t: [t.x, t.y, t.z], r: [deg(e.x), deg(e.y), deg(e.z)], s: [sc.x, sc.y, sc.z] };
    },
    apply(vals, push) {
      const T = ensureTS(); if (!T) return;
      const R = new M4().makeRotationFromEuler(new THREE.Euler(rad(vals.r[0]), rad(vals.r[1]), rad(vals.r[2]), "XYZ")), S = new M4().makeScale(...vals.s.map(x => Math.abs(x) < 1e-3 ? (x < 0 ? -1e-3 : 1e-3) : x));
      const z = zeroOf(), Anew = new M4().makeTranslation(vals.t[0] + z.x, vals.t[1] + z.y, vals.t[2] + z.z).multiply(R).multiply(S).multiply(new M4().makeTranslation(-T.c0.x, -T.c0.y, -T.c0.z));
      const D = Anew.clone().multiply(T.A.clone().invert());
      if (push) pushUndo("Channel Box");
      const aff = affSnapshot(); xformApply(D, aff); T.A = Anew;
      new Set(aff.map(a => a.o)).forEach(o => { touchGeo(o, true); o.mirror = null; });
      overlayPositions(); placePivot(); changed();
    },
    begin() { pushUndo("Channel Box"); },
    reset() { TS = null; },
  };
  const chOf = () => SK() ? ST.mods.skel.channel : MCH;
  M.channel = { unit: "cm", title: () => chOf().title(), vals: () => chOf().vals(), apply: (v, p) => { chOf().apply(v, p); placePivot(); }, begin: () => chOf().begin(), reset: () => chOf().reset() };

  // ---------------------------------------------------------------- chọn bằng chuột (viewport gọi pick / box)
  const camLocal = p => root.worldToLocal(p.cam.position.clone());
  function hitObjects(x, y, p, only) {
    const meshes = (only ? [only] : OBJ.filter(o => o.vis && !o.lock)).map(o => o.mesh);
    return V.raycaster(x, y, p).intersectObjects(meshes, false)[0] || null;
  }
  const W = new V3();
  function screenOf(o, i, p) { W.set(o.pos[3 * i], o.pos[3 * i + 1], o.pos[3 * i + 2]).applyMatrix4(root.matrixWorld); return V.toScreen(W, p); }
  function facer(o, p) {   // mặt trước theo pháp tuyến đỉnh (không chọn xuyên mesh)
    const nrm = o.mesh.geometry.attributes.normal;
    if (p.cam.isPerspectiveCamera) { const c = camLocal(p); return i => nrm.getX(i) * (c.x - o.pos[3 * i]) + nrm.getY(i) * (c.y - o.pos[3 * i + 1]) + nrm.getZ(i) * (c.z - o.pos[3 * i + 2]) > 0; }
    const d = p.cam.getWorldDirection(new V3()).negate(); return i => nrm.getX(i) * d.x + nrm.getY(i) * d.y + nrm.getZ(i) * d.z > 0;
  }
  M.canBox = () => mode !== "o" && ST.tool === "sel";
  // mặt nạ chọn kiểu Maya (thanh trên): loại nào tắt thì click / kéo khung trong viewport bỏ qua loại đó; Outliner vẫn chọn được
  const mask = Object.assign({ joint: true, mesh: true }, ST.pref.get("selmask", null) || {});
  // click có trúng joint / mesh của lớp Cảnh không (viewport dùng để chuyển focus sang mesh)
  M.hit = (x, y, p) => style === "edit" && !!((mask.joint && ST.mods.skel && ST.mods.skel.pickAt(x, y, p)) || (mask.mesh && hitObjects(x, y, p)));
  M.pick = (x, y, e, p) => {
    if (style !== "edit") return;
    const add = ST.addSel(e), sk = ST.mods.skel;
    if (mode === "o" && sk) { const jn = mask.joint ? sk.pickAt(x, y, p) : null; if (jn) { sk.select(jn); return; } if (sk.sel()) sk.select(null); }
    if (mode === "o") {
      const h = mask.mesh ? hitObjects(x, y, p) : null;
      if (!h) { if (!add) selO.clear(); } else { const o = get(h.object.userData.oid); if (add) { selO.has(o.id) ? selO.delete(o.id) : selO.add(o.id); } else selO = new Set([o.id]); active = o; }
      allVis(); refreshSel(); return;
    }
    if (!active) return;
    const h = hitObjects(x, y, p, active);
    if (mode === "v") {
      const R = V.TM.on ? 30 : 14, face = facer(active, p); let best = -1, bd = R;
      for (let i = 0; i < nV(active); i++) { if (frontOnly && !face(i)) continue; const s = screenOf(active, i, p), d = Math.hypot(s.x - x, s.y - y); if (d < bd) { bd = d; best = i; } }
      if (best >= 0) { const s = new Set(add ? selV : []); add && s.has(best) ? s.delete(best) : s.add(best); setVerts(s); return; }
    } else if (h) {
      const t = h.faceIndex;
      if (mode === "f") { const s = new Set(add ? selF : []); add && s.has(t) ? s.delete(t) : s.add(t); setFaces(s); return; }
      if (mode === "i") { const isl = islandFrom(active, t), s = new Set(add ? selF : []); const rm = add && selF.has(t); isl.forEach(f => rm ? s.delete(f) : s.add(f)); setFaces(s); return; }
    }
    const other = hitObjects(x, y, p);
    if (other && get(other.object.userData.oid) !== active) { active = get(other.object.userData.oid); selO = new Set([active.id]); clearSel(); allVis(); refreshSel(); return; }
    if (!add) { clearSel(); refreshSel(); }
  };
  M.box = (x0, y0, x1, y1, e, p) => {
    if (!active || style !== "edit") return;
    const xa = Math.min(x0, x1), xb = Math.max(x0, x1), ya = Math.min(y0, y1), yb = Math.max(y0, y1), vs = new Set(), face = facer(active, p);
    for (let i = 0; i < nV(active); i++) { if (frontOnly && !face(i)) continue; const s = screenOf(active, i, p); if (s.x >= xa && s.x <= xb && s.y >= ya && s.y <= yb) vs.add(i); }
    const base = ST.addSel(e) ? new Set(selV) : new Set(); vs.forEach(i => base.add(i));
    if (mode === "f" || mode === "i") setFaces(facesOfVerts(active, base, true)); else setVerts(base);
  };

  // ---------------------------------------------------------------- thao tác trên mesh
  function compact(pos, idx) {
    const n = pos.length / 3, map = new Int32Array(n).fill(-1); let k = 0;
    for (let i = 0; i < idx.length; i++) if (map[idx[i]] < 0) map[idx[i]] = k++;
    const np = new Float32Array(k * 3); for (let i = 0; i < n; i++) if (map[i] >= 0) { np[3 * map[i]] = pos[3 * i]; np[3 * map[i] + 1] = pos[3 * i + 1]; np[3 * map[i] + 2] = pos[3 * i + 2]; }
    const ni = new Uint32Array(idx.length); for (let i = 0; i < idx.length; i++) ni[i] = map[idx[i]];
    return { pos: np, idx: ni };
  }
  function setTopology(o, pos, idx) { const c = compact(pos, idx); o.pos = c.pos; o.idx = c.idx; o.skin = null; buildGeo(o); clearSel(); TS = null; }
  const say = t => ST.toast(t);
  function opDelete() {
    if (mode === "o") { if (!selO.size) return; pushUndo("Xoá mesh"); [...selO].forEach(id => removeObj(get(id))); selO.clear(); clearSel(); changed(); refreshSel(); return; }
    const o = active; if (!o) return; const del = mode === "v" ? facesOfVerts(o, selV, false) : selF; if (!del.size) return say("Chưa chọn gì để xoá.");
    pushUndo("Xoá mặt"); const keep = []; for (let t = 0; t < nT(o); t++) if (!del.has(t)) keep.push(o.idx[3 * t], o.idx[3 * t + 1], o.idx[3 * t + 2]);
    setTopology(o, o.pos, Uint32Array.from(keep)); changed(); say("Đã xoá " + del.size + " mặt."); refreshSel();
  }
  function opSeparate() {
    const o = active; if (!o || mode === "o" || !selF.size) return say("Chọn mặt, khối hoặc điểm trước.");
    if (selF.size === nT(o)) return say("Đã chọn cả mesh, không cần tách.");
    pushUndo("Tách mesh"); const a = [], b = [];
    for (let t = 0; t < nT(o); t++) (selF.has(t) ? a : b).push(o.idx[3 * t], o.idx[3 * t + 1], o.idx[3 * t + 2]);
    const c = compact(o.pos, Uint32Array.from(a)); setTopology(o, o.pos, Uint32Array.from(b));
    const n = makeObj(o.name + "_tach", c.pos, c.idx); active = n; selO = new Set([n.id]); clearSel(); mode = "o"; allVis(); changed(); say("Đã tách " + (a.length / 3) + " mặt thành mesh mới."); refreshSel();
  }
  function opMerge() {
    const Ls = [...selO].map(get).filter(Boolean); if (Ls.length < 2) return say("Chọn từ 2 mesh trở lên (chế độ mesh, Shift để chọn thêm).");
    pushUndo("Gộp mesh"); let np = 0, ni = 0; Ls.forEach(o => { np += o.pos.length; ni += o.idx.length; });
    const pos = new Float32Array(np), idx = new Uint32Array(ni); let po = 0, io = 0, base = 0;
    Ls.forEach(o => { pos.set(o.pos, po); for (let i = 0; i < o.idx.length; i++) idx[io + i] = o.idx[i] + base; po += o.pos.length; io += o.idx.length; base += nV(o); });
    const m = makeObj(Ls[0].name, pos, idx); Ls.forEach(removeObj); active = m; selO = new Set([m.id]); allVis(); changed(); say("Đã gộp " + Ls.length + " mesh."); refreshSel();
  }
  function weldO(o, eps, only) {
    const n = nV(o), q = Math.max(eps, 1e-4), key = (x, y, z) => Math.floor(x / q) + "," + Math.floor(y / q) + "," + Math.floor(z / q), H = new Map(), rep = new Int32Array(n);
    for (let i = 0; i < n; i++) {
      rep[i] = i; if (only && !only.has(i)) continue;
      const x = o.pos[3 * i], y = o.pos[3 * i + 1], z = o.pos[3 * i + 2], cx = Math.floor(x / q), cy = Math.floor(y / q), cz = Math.floor(z / q); let found = -1;
      for (let dx = -1; dx <= 1 && found < 0; dx++) for (let dy = -1; dy <= 1 && found < 0; dy++) for (let dz = -1; dz <= 1 && found < 0; dz++) {
        const c = H.get((cx + dx) + "," + (cy + dy) + "," + (cz + dz)); if (!c) continue;
        for (const j of c) if ((o.pos[3 * j] - x) ** 2 + (o.pos[3 * j + 1] - y) ** 2 + (o.pos[3 * j + 2] - z) ** 2 <= eps * eps) { found = j; break; }
      }
      if (found >= 0) rep[i] = rep[found]; else (H.get(key(x, y, z)) || H.set(key(x, y, z), []).get(key(x, y, z))).push(i);
    }
    let merged = 0; for (let i = 0; i < n; i++) if (rep[i] !== i) merged++;
    const keep = []; for (let t = 0; t < nT(o); t++) { const a = rep[o.idx[3 * t]], b = rep[o.idx[3 * t + 1]], c = rep[o.idx[3 * t + 2]]; if (a !== b && b !== c && a !== c) keep.push(a, b, c); }
    return { merged, idx: Uint32Array.from(keep) };
  }
  function opWeld() {
    const o = active; if (!o) return; const eps = weldEps || 0.05;
    pushUndo("Hàn điểm"); const r = weldO(o, eps, mode !== "o" && selV.size ? selV : null);
    setTopology(o, o.pos, r.idx); changed(); say(r.merged ? "Đã hàn " + r.merged + " điểm trùng." : "Không có điểm nào trong " + eps + " cm."); refreshSel();
  }
  function opFlip() {
    const o = active; if (!o) return; const fs = mode !== "o" && selF.size ? selF : null; pushUndo("Lật pháp tuyến");
    for (let t = 0; t < nT(o); t++) if (!fs || fs.has(t)) { const b = o.idx[3 * t + 1]; o.idx[3 * t + 1] = o.idx[3 * t + 2]; o.idx[3 * t + 2] = b; }
    buildGeo(o); changed(); say("Đã lật pháp tuyến " + (fs ? fs.size + " mặt" : "cả mesh") + "."); refreshSel();
  }
  function opSmooth() {
    const o = active; if (!o || mode === "o" || !selV.size) return say("Chọn điểm hoặc mặt cần làm mượt.");
    pushUndo("Làm mượt"); const vf = adjacency(o), P = o.pos, np = P.slice();
    for (let pass = 0; pass < 2; pass++) {
      selV.forEach(i => {
        const nb = new Set(); vf[i].forEach(t => { for (let k = 0; k < 3; k++) { const j = o.idx[3 * t + k]; if (j !== i) nb.add(j); } }); if (!nb.size) return;
        let x = 0, y = 0, z = 0; nb.forEach(j => { x += P[3 * j]; y += P[3 * j + 1]; z += P[3 * j + 2]; }); x /= nb.size; y /= nb.size; z /= nb.size;
        np[3 * i] = P[3 * i] * 0.5 + x * 0.5; np[3 * i + 1] = P[3 * i + 1] * 0.5 + y * 0.5; np[3 * i + 2] = P[3 * i + 2] * 0.5 + z * 0.5;
      }); P.set(np);
    }
    touchGeo(o, true); changed(); refreshSel();
  }
  function opDuplicate() { const o = active; if (!o) return; pushUndo("Nhân bản"); const n = makeObj(o.name + "_copy", o.pos.slice(), o.idx.slice(), { piv: o.piv || null, zero: o.zero || null }); active = n; selO = new Set([n.id]); allVis(); changed(); say("Đã nhân bản."); refreshSel(); }
  function opFlipX() {
    const Ls = mode === "o" && selO.size ? [...selO].map(get) : active ? [active] : []; if (!Ls.length) return; pushUndo("Lật trái/phải");
    Ls.forEach(o => { for (let i = 0; i < nV(o); i++) o.pos[3 * i] = -o.pos[3 * i]; for (let t = 0; t < nT(o); t++) { const b = o.idx[3 * t + 1]; o.idx[3 * t + 1] = o.idx[3 * t + 2]; o.idx[3 * t + 2] = b; } buildGeo(o); });
    clearSel(); changed(); say("Đã lật trái/phải (trục X)."); refreshSel();
  }
  function bboxCm(list) { const b = new THREE.Box3(), v = new V3(); (list || OBJ.filter(o => o.vis)).forEach(o => { for (let i = 0; i < nV(o); i++) b.expandByPoint(v.set(o.pos[3 * i], o.pos[3 * i + 1], o.pos[3 * i + 2])); }); return b; }
  const sceneH = () => { const b = bboxCm(); return b.isEmpty() ? 0 : b.max.y - b.min.y; };
  function opGround() {
    const b = bboxCm(); if (b.isEmpty()) return; pushUndo("Đặt xuống sàn"); const cx = (b.min.x + b.max.x) / 2, cz = (b.min.z + b.max.z) / 2;
    OBJ.forEach(o => { for (let i = 0; i < nV(o); i++) { o.pos[3 * i] -= cx; o.pos[3 * i + 1] -= b.min.y; o.pos[3 * i + 2] -= cz; } touchGeo(o, true); o.mirror = null; });
    changed(); say("Đã đặt chân xuống sàn (Y=0), tâm về X=Z=0."); refreshSel(); V.frameAll();
  }
  async function opHeight(hv) {
    const b = bboxCm(); if (b.isEmpty()) return;
    const h = +(hv != null ? hv : await ST.ask("Chiều cao cả cảnh", "cm", sceneH().toFixed(1))); if (!(h > 0)) return;
    const f = h / (b.max.y - b.min.y), cx = (b.min.x + b.max.x) / 2, cz = (b.min.z + b.max.z) / 2; pushUndo("Chiều cao");
    OBJ.forEach(o => { for (let i = 0; i < nV(o); i++) { o.pos[3 * i] = cx + (o.pos[3 * i] - cx) * f; o.pos[3 * i + 1] = b.min.y + (o.pos[3 * i + 1] - b.min.y) * f; o.pos[3 * i + 2] = cz + (o.pos[3 * i + 2] - cz) * f; } touchGeo(o, true); o.mirror = null; });
    changed(); say("Đã scale cả cảnh lên " + h + " cm (×" + f.toFixed(3) + ")."); refreshSel(); V.frameAll();
  }
  function stats(o) {
    const n = nV(o), t = nT(o), used = new Uint8Array(n); let degen = 0, dupF = 0; const E = new Map(), F = new Set();
    for (let f = 0; f < t; f++) {
      const a = o.idx[3 * f], b = o.idx[3 * f + 1], c = o.idx[3 * f + 2]; used[a] = used[b] = used[c] = 1;
      const ax = o.pos[3 * a], ay = o.pos[3 * a + 1], az = o.pos[3 * a + 2], ux = o.pos[3 * b] - ax, uy = o.pos[3 * b + 1] - ay, uz = o.pos[3 * b + 2] - az, vx = o.pos[3 * c] - ax, vy = o.pos[3 * c + 1] - ay, vz = o.pos[3 * c + 2] - az;
      const cx = uy * vz - uz * vy, cy = uz * vx - ux * vz, cz = ux * vy - uy * vx; if (a === b || b === c || a === c || cx * cx + cy * cy + cz * cz < 1e-12) degen++;
      const k = [a, b, c].sort((x, y) => x - y).join("_"); F.has(k) ? dupF++ : F.add(k);
      [[a, b], [b, c], [c, a]].forEach(([p, q]) => { const e = p < q ? p + "_" + q : q + "_" + p; E.set(e, (E.get(e) || 0) + 1); });
    }
    let loose = 0; for (let i = 0; i < n; i++) if (!used[i]) loose++;
    let open = 0, nonman = 0; E.forEach(v => { if (v === 1) open++; else if (v > 2) nonman++; });
    const w = weldO(o, 0.001, null), parent = new Int32Array(n).map((_, i) => i), find = x => { while (parent[x] !== x) { parent[x] = parent[parent[x]]; x = parent[x]; } return x; };
    for (let f = 0; f < t; f++) { const a = find(o.idx[3 * f]), b = find(o.idx[3 * f + 1]), c = find(o.idx[3 * f + 2]); parent[b] = a; parent[find(c)] = find(a); }
    const roots = new Set(); for (let f = 0; f < t; f++) roots.add(find(o.idx[3 * f]));
    return { n, t, loose, degen, dupF, open, nonman, dupV: w.merged, islands: roots.size };
  }
  let statCache = { o: null, sig: "", st: null };
  function statsOf(o) { const sig = o.id + ":" + ver; if (statCache.o !== o || statCache.sig !== sig) statCache = { o, sig, st: stats(o) }; return statCache.st; }
  function opClean() {
    const o = active; if (!o) return; pushUndo("Dọn mesh"); const s = stats(o), seen = new Set(), keep = [];
    for (let f = 0; f < nT(o); f++) {
      const a = o.idx[3 * f], b = o.idx[3 * f + 1], c = o.idx[3 * f + 2]; if (a === b || b === c || a === c) continue;
      const ux = o.pos[3 * b] - o.pos[3 * a], uy = o.pos[3 * b + 1] - o.pos[3 * a + 1], uz = o.pos[3 * b + 2] - o.pos[3 * a + 2], vx = o.pos[3 * c] - o.pos[3 * a], vy = o.pos[3 * c + 1] - o.pos[3 * a + 1], vz = o.pos[3 * c + 2] - o.pos[3 * a + 2];
      const cx = uy * vz - uz * vy, cy = uz * vx - ux * vz, cz = ux * vy - uy * vx; if (cx * cx + cy * cy + cz * cz < 1e-12) continue;
      const k = [a, b, c].sort((x, y) => x - y).join("_"); if (seen.has(k)) continue; seen.add(k); keep.push(a, b, c);
    }
    setTopology(o, o.pos, Uint32Array.from(keep)); changed(); say("Đã dọn: " + s.degen + " mặt hỏng, " + s.dupF + " mặt trùng, " + s.loose + " điểm lẻ."); refreshSel();
  }
  const allIdx = n => Array.from({ length: n }, (_, i) => i);
  function selectAll() { if (mode === "o") { selO = new Set(OBJ.filter(o => o.vis && !o.lock).map(o => o.id)); allVis(); refreshSel(); } else if (active) { mode === "v" ? setVerts(new Set(allIdx(nV(active)))) : setFaces(new Set(allIdx(nT(active)))); } }
  function selectNone() { selO.clear(); clearSel(); allVis(); refreshSel(); }
  function selectInvert() { if (!active || mode === "o") return; if (mode === "v") setVerts(new Set(allIdx(nV(active)).filter(i => !selV.has(i)))); else setFaces(new Set(allIdx(nT(active)).filter(t => !selF.has(t)))); }
  function selectGrow() { const o = active; if (!o || mode === "o" || !selV.size) return; const vf = adjacency(o), n = new Set(selV); selV.forEach(i => vf[i].forEach(t => { for (let k = 0; k < 3; k++) n.add(o.idx[3 * t + k]); })); mode === "v" ? setVerts(n) : setFaces(facesOfVerts(o, n, false)); }
  function setMode(m) {
    if (m !== "o" && posed() && active && active.skin) return say("Xương đang pose: Skin → Về Bind Pose rồi mới sửa điểm / mặt.");
    mode = m; if (m === "o") clearSel(); else if (active) { selO = new Set([active.id]); if (selF.size && m !== "v") selV = vertsOfFaces(active, selF); }
    allVis(); refreshSel();
  }

  // ---------------------------------------------------------------- lưu / nạp / xuất
  const ser = () => ({ v: 1, at: new Date().toISOString(), meshes: OBJ.map(o => ({ name: o.name, vis: o.vis, lock: o.lock, verts: Array.from(o.pos, v => +v.toFixed(3)), tris: Array.from(o.idx), piv: o.piv ? o.piv.toArray().map(v => +v.toFixed(3)) : undefined, zero: o.zero ? o.zero.toArray().map(v => +v.toFixed(3)) : undefined })) });
  async function save() {
    clearTimeout(saveT); if (!dirty || !store) return;
    try { const doc = ser(), w = await store.set("mesh/edit", doc); editAt = doc.at; dirty = false; ST.saveState(w === "disk" ? "Đã lưu vào dự án (work/store/" + store.ns + ")" : "Đã lưu (chỉ trình duyệt này)", w === "disk" ? "" : "dirty"); }
    catch (e) { ST.saveState("Không lưu được: " + (e.message || e), "err"); }
  }
  M.save = save;
  function loadMeshes(list) {
    OBJ.slice().forEach(disposeObj); OBJ = []; selO.clear(); clearSel(); TS = null;
    list.forEach((m, i) => makeObj(m.name, Float32Array.from(m.verts), Uint32Array.from(m.tris), { vis: m.vis !== false, lock: !!m.lock, color: COLORS[i % COLORS.length], skin: skinOf(m.name, m.verts.length / 3), piv: m.piv ? new V3().fromArray(m.piv) : null, zero: m.zero ? new V3().fromArray(m.zero) : null }));
    active = OBJ[OBJ.length - 1] || null; if (active) selO = new Set([active.id]); allVis();
  }
  // Nhập mesh từ FBX (đã đổi cm, Y lên ở server): "replace" thay mesh trùng tên (giữ màu, ẩn/khoá), còn lại thêm mới
  M.importMeshes = (list, how) => {
    pushUndo("Nhập FBX"); let rep = 0, add = 0;
    list.forEach(m => {
      const pos = Float32Array.from(m.verts), idx = Uint32Array.from(m.tris), o = how === "replace" && OBJ.find(x => x.name === m.name);
      if (o) { o.pos = pos; o.idx = idx; buildGeo(o); rep++; } else { makeObj(m.name, pos, idx); add++; }
    });
    clearSel(); TS = null; mode = "o"; allVis(); changed(); refreshSel(); V.frameAll();
    return { rep, add };
  };
  function resetAll() { if (!ORIG) return; pushUndo("Về mesh gốc"); loadMeshes(ORIG); changed(); say("Đã về mesh gốc."); refreshSel(); V.frameAll(); }
  const baseName = () => ((ST.char && ST.char.name) || "mesh").replace(/[^A-Za-z0-9_\-]+/g, "_");
  function exportOBJ() {
    let s = "# AI Anim Studio, cm, +Y up\n", off = 1;
    OBJ.filter(o => o.vis).forEach(o => { s += "o " + o.name + "\n"; for (let i = 0; i < nV(o); i++) s += "v " + o.pos[3 * i].toFixed(4) + " " + o.pos[3 * i + 1].toFixed(4) + " " + o.pos[3 * i + 2].toFixed(4) + "\n"; for (let t = 0; t < nT(o); t++) s += "f " + (o.idx[3 * t] + off) + " " + (o.idx[3 * t + 1] + off) + " " + (o.idx[3 * t + 2] + off) + "\n"; off += nV(o); });
    ST.download(baseName() + ".obj", s); say("Đã xuất " + baseName() + ".obj");
  }
  function exportRig() {
    const out = OBJ.filter(o => o.vis).map(o => ({ name: o.name, verts: Array.from(o.pos, v => +v.toFixed(3)), tris: Array.from(o.idx) }));
    ST.download(baseName() + "_mesh_cm.json", JSON.stringify(out), "application/json"); say("Đã xuất " + baseName() + "_mesh_cm.json (cho Rig).");
  }
  ST.on("char", async ch => {
    // ?ns=<kho> để thử trên kho riêng, không đụng bản sửa thật mà Rig Lab đọc
    ORIG = ch.meshes; store = ST.store(new URLSearchParams(location.search).get("ns") || ST.slug(ch.name) + "_mesh_lab");
    let src = ORIG, from = "gốc";
    try { const s = await store.get("mesh/edit"); if (s && s.meshes && s.meshes.length) { src = s.meshes; editAt = s.at || "edit"; from = "đã sửa " + String(s.at || "").slice(0, 16).replace("T", " "); } } catch (e) { console.error(e); }
    RIGSKIN = null; try { const d = await ST.store(ST.rigNs()).get("rig/skin"); if (d && d.names && d.nv) RIGSKIN = d; } catch (e) {}
    try { const k = await ST.store(ST.rigNs()).get("rig/skeleton"); ST.rigState = { source: k && k.source === "none" ? "none" : k && k.joints && k.joints.length ? "rig" : "guest" }; } catch (e) {}
    loadMeshes(src); ST.saveState("Đã nạp bản " + from);
  });
  ST.on("rig:skin", d => {   // vừa tính / tô skin ở Rig: mesh ở General đi theo skin mới
    if (!d || !d.names) return; RIGSKIN = d; const on = posed();
    OBJ.forEach(o => { const k = skinOf(o.name, nV(o)); if (k) { o.skin = k; deform(o, on); } });
  });
  ST.on("rig:cleared", () => {   // xoá xương: mesh tĩnh về tư thế bind, không skin
    if (ST.rigState && ST.rigState.source === "none") { RIGSKIN = null; OBJ.forEach(o => { o.skin = null; deform(o, false); }); }
    refreshSel();
  });
  ST.on("loaded", () => { V.frameAll(); refreshSel(); });
  addEventListener("beforeunload", e => { if (dirty) { save(); e.preventDefault(); e.returnValue = ""; } });
  M.bounds = selOnly => {
    let b;
    if (selOnly) {
      if (mode === "o") b = bboxCm(OBJ.filter(o => selO.has(o.id) && o.vis));
      else if (active && selV.size) { b = new THREE.Box3(); const v = new V3(); selV.forEach(i => b.expandByPoint(v.set(active.pos[3 * i], active.pos[3 * i + 1], active.pos[3 * i + 2]))); }
      if (!b || b.isEmpty()) return null;
    } else b = bboxCm();
    if (b.isEmpty()) return null;
    return b.applyMatrix4(root.matrixWorld);
  };

  // ---------------------------------------------------------------- Free Transform: hộp bao vùng chọn + tay nắm (mặt = giãn một trục, góc = scale đều, tâm = dời)
  const FREE = { group: new THREE.Group(), box: null, hs: [] }; FREE.group.visible = false; root.add(FREE.group);
  const FCOL = 0xff7a1a;
  function selBox() {
    const b = new THREE.Box3(), v = new V3();
    if (mode === "o") selO.forEach(id => { const o = get(id); if (!o || !o.vis || o.lock) return; for (let i = 0; i < nV(o); i++) b.expandByPoint(v.set(o.pos[3 * i], o.pos[3 * i + 1], o.pos[3 * i + 2])); });
    else if (active) selV.forEach(i => b.expandByPoint(v.set(active.pos[3 * i], active.pos[3 * i + 1], active.pos[3 * i + 2])));
    if (b.isEmpty()) return null;
    ["x", "y", "z"].forEach(a => { if (b.max[a] - b.min[a] < 0.5) { const m = (b.max[a] + b.min[a]) / 2; b.min[a] = m - 0.25; b.max[a] = m + 0.25; } });
    return b;
  }
  function buildFree() {
    FREE.group.children.slice().forEach(c => { FREE.group.remove(c); if (c.geometry) c.geometry.dispose(); if (c.material) c.material.dispose(); }); FREE.hs = [];
    const b = ST.tool === "free" && foc() && style === "edit" ? selBox() : null; FREE.box = b; FREE.group.visible = !!b; if (!b) return;
    const c = b.getCenter(new V3()), sz = b.getSize(new V3());
    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(sz.x, sz.y, sz.z)), new THREE.LineBasicMaterial({ color: FCOL, depthTest: false, transparent: true, opacity: 0.9 }));
    edges.position.copy(c); edges.renderOrder = 28; edges.raycast = () => {}; FREE.group.add(edges);
    const mk = (geo, pos, data) => { const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: data.t === "center" ? 0x2f9bff : FCOL, depthTest: false, transparent: true })); m.position.copy(pos); m.renderOrder = 30; m.userData = data; FREE.group.add(m); FREE.hs.push(m); };
    const sph = new THREE.SphereGeometry(1, 10, 8), cube = new THREE.BoxGeometry(1.5, 1.5, 1.5);
    for (const x of [0, 1]) for (const y of [0, 1]) for (const z of [0, 1]) mk(sph, new V3(x ? b.max.x : b.min.x, y ? b.max.y : b.min.y, z ? b.max.z : b.min.z), { t: "corner", sg: [x, y, z] });
    for (let ax = 0; ax < 3; ax++) for (const sg of [0, 1]) { const p = c.clone(); p.setComponent(ax, sg ? b.max.getComponent(ax) : b.min.getComponent(ax)); mk(cube, p, { t: "face", ax, sg }); }
    mk(sph, c, { t: "center" });
  }
  ST.on("prerender", () => {   // tay nắm giữ cỡ ~6 px trên màn hình (theo khung đang dùng)
    if (!FREE.group.visible || !V.active) return; const w = new V3();
    FREE.hs.forEach(h => { h.getWorldPosition(w); h.scale.setScalar(Math.max(0.05, V.worldPerPixel(w) * 100 * 6)); });
  });
  let fdrag = null;
  const invRoot = () => new M4().copy(root.matrixWorld).invert();
  function rayLocal(e, p) { const r = V.raycaster(e.clientX, e.clientY, p).ray.clone(); r.applyMatrix4(invRoot()); r.direction.normalize(); return r; }
  function closestOnAxis(r, O, D) {
    const w0 = O.clone().sub(r.origin), a = D.dot(D), b = D.dot(r.direction), c = r.direction.dot(r.direction), d = D.dot(w0), e2 = r.direction.dot(w0), den = a * c - b * b;
    return Math.abs(den) < 1e-9 ? 0 : (b * e2 - c * d) / den;
  }
  function planeHit(r, P, p) { const n = p.cam.getWorldDirection(new V3()); return r.intersectPlane(new THREE.Plane().setFromNormalAndCoplanarPoint(n, P), new V3()); }
  M.pointerDown = (e, p) => {
    if (ST.tool !== "free" || !FREE.group.visible || e.button !== 0) return false;
    const rc = V.raycaster(e.clientX, e.clientY, p), hit = rc.intersectObjects(FREE.hs, false)[0]; if (!hit) return false;
    const b = FREE.box.clone(); pushUndo("Free Transform"); ensureTS();
    fdrag = { h: hit.object.userData, b, c: b.getCenter(new V3()), aff: affSnapshot(), A0: TS.A.clone(), p }; V.orbit.enabled = false;
    return true;
  };
  addEventListener("pointermove", e => {
    const d = fdrag; if (!d) return; const r = rayLocal(e, d.p), h = d.h, b = d.b, c = d.c; let Mx = new M4();
    const anchorAt = (ax, sg) => e.altKey ? c.getComponent(ax) : (sg ? b.min.getComponent(ax) : b.max.getComponent(ax));
    if (h.t === "face") {
      const ax = h.ax, hp = h.sg ? b.max.getComponent(ax) : b.min.getComponent(ax), an = anchorAt(ax, h.sg), O = c.clone(); O.setComponent(ax, hp);
      const D = new V3(); D.setComponent(ax, 1); const np = hp + closestOnAxis(r, O, D), den = hp - an; if (Math.abs(den) < 1e-6) return;
      const sc = Math.max(0.01, (np - an) / den), S = new V3(1, 1, 1); if (e.shiftKey) S.set(sc, sc, sc); else S.setComponent(ax, sc);
      const pv = c.clone(); pv.setComponent(ax, an);
      Mx = new M4().makeTranslation(pv.x, pv.y, pv.z).multiply(new M4().makeScale(S.x, S.y, S.z)).multiply(new M4().makeTranslation(-pv.x, -pv.y, -pv.z));
    } else if (h.t === "corner") {
      const cp = new V3(h.sg[0] ? b.max.x : b.min.x, h.sg[1] ? b.max.y : b.min.y, h.sg[2] ? b.max.z : b.min.z), an = e.altKey ? c.clone() : new V3(h.sg[0] ? b.min.x : b.max.x, h.sg[1] ? b.min.y : b.max.y, h.sg[2] ? b.min.z : b.max.z);
      const P = planeHit(r, cp, d.p); if (!P) return; const dv = cp.clone().sub(an), den = dv.dot(dv); if (den < 1e-9) return;
      const sc = Math.max(0.01, P.clone().sub(an).dot(dv) / den);
      Mx = new M4().makeTranslation(an.x, an.y, an.z).multiply(new M4().makeScale(sc, sc, sc)).multiply(new M4().makeTranslation(-an.x, -an.y, -an.z));
    } else { const P = planeHit(r, c, d.p); if (!P) return; const dl = P.sub(c); Mx = new M4().makeTranslation(dl.x, dl.y, dl.z); }
    xformApply(Mx, d.aff); TS.A = Mx.clone().multiply(d.A0); overlayPositions(); buildFree(); ST.chRefresh();
  });
  addEventListener("pointerup", () => { if (!fdrag) return; const aff = fdrag.aff; fdrag = null; V.orbit.enabled = true; xformEnd(aff); });

  // ---------------------------------------------------------------- Outliner, panel, trạng thái
  M.outline = () => {
    const rows = [];   // như Maya: mesh và xương nằm ngay cấp đầu, không có dòng nhân vật / nhóm Mesh
    const sk = ST.mods.skel ? ST.mods.skel.rows() : [];
    OBJ.forEach(o => rows.push({ id: o.id, d: 0, label: o.name, icon: "mesh", vis: o.vis, lock: o.lock, count: nT(o), sel: selO.has(o.id), act: o === active, del: true, rename: true }));
    return rows.concat(sk);
  };
  M.olAct = (id, a, e, val) => {
    if (ST.mods.skel && ST.mods.skel.isMine(id)) return ST.mods.skel.olAct(id, a);
    const o = get(+id); if (!o) return;
    if (a === "vis") { o.vis = !o.vis; applyVis(o); dirty = true; changed(); refreshSel(); visToRig(); return; }
    if (a === "lock") { o.lock = !o.lock; if (o.lock) { selO.delete(o.id); if (active === o) { active = OBJ.find(x => !x.lock && x.vis) || null; clearSel(); } } changed(); allVis(); refreshSel(); return; }
    if (a === "del") { pushUndo("Xoá mesh"); removeObj(o); clearSel(); changed(); refreshSel(); return; }
    if (a === "rename") { if (val && val !== o.name) { pushUndo("Đổi tên"); o.name = val; changed(); } return; }
    if (o.lock) return;
    if (ST.mods.skel && ST.mods.skel.sel()) ST.mods.skel.select(null);   // chọn mesh thì bỏ chọn joint
    if (ST.addSel(e)) { selO.has(o.id) ? selO.delete(o.id) : selO.add(o.id); } else selO = new Set([o.id]);
    if (active !== o) { active = o; clearSel(); }
    allVis(); refreshSel();
  };
  M.info = () => {
    if (SK()) return ST.mods.skel.info();
    const o = active, h = sceneH();
    return (o ? o.name + " · " + nV(o) + " điểm · " + nT(o) + " tam giác" : "Chưa có mesh") +
      (mode !== "o" ? " · chọn " + (mode === "v" ? selV.size + " điểm" : selF.size + " mặt") : selO.size ? " · chọn " + selO.size + " mesh" : "") + " · cao " + h.toFixed(1) + " cm";
  };
  const chk = (ok, bad, txt, detail) => `<i class="${bad ? "s-bad" : ok ? "s-ok" : "s-warn"}">${bad ? "✗" : ok ? "✓" : "!"}</i><span>${txt}${detail ? `<br><small class="sub">${detail}</small>` : ""}</span>`;
  M.panel = tab => {
    if (tab === "check") {
      const o = active, st = o ? statsOf(o) : null, h = sceneH();
      if (!st) return '<div class="sub">Chưa có mesh.</div>';
      return `<h2>Kiểm tra · ${esc(o.name)}</h2><div class="chk">${chk(!st.loose, false, st.loose + " điểm lẻ (không thuộc mặt nào)")}${chk(!st.degen, st.degen > 0, st.degen + " mặt hỏng (diện tích 0)")}${chk(!st.dupF, false, st.dupF + " mặt trùng")}
        ${chk(!st.dupV, false, st.dupV + " điểm trùng vị trí", st.dupV ? "Hàn điểm gần để nối lại" : "")}${chk(!st.nonman, st.nonman > 0, st.nonman + " cạnh chung > 2 mặt")}${chk(true, false, st.islands + " khối rời · " + st.open + " cạnh hở")}</div>
        <div class="kv" style="margin-top:8px"><span>Điểm / tam giác</span><span>${st.n} / ${st.t}</span><span>Cao cảnh</span><span>${h.toFixed(1)} cm</span></div>
        <div class="row" style="margin-top:10px"><button data-o="clean">${ic("clean")}Dọn mesh</button></div>`;
    }
    return `<h2>Chọn</h2>
      <div class="row"><label><input type="checkbox" data-k="front" ${frontOnly ? "checked" : ""}> Chỉ mặt trước</label><label><input type="checkbox" data-k="sym" ${sym ? "checked" : ""}> Đối xứng X</label></div>
      <div class="row"><label><input type="checkbox" data-k="soft" ${soft.on ? "checked" : ""}> Chọn mềm (B)</label><input type="range" data-k="r" min="2" max="60" step="1" value="${soft.r}" ${soft.on ? "" : "disabled"}><span class="sub" id="mSr">${soft.r} cm</span></div>
      <h2>Hàn điểm</h2>
      <div class="row"><input type="number" data-k="eps" value="${weldEps}" step="0.01" min="0.001" title="Khoảng cách tối đa (cm)"><span class="sub">cm</span><button data-o="weld">${ic("weld")}Hàn điểm gần</button></div>
      <h2>Cảnh</h2>
      <div class="row"><button data-o="ground">${ic("floor")}Đặt xuống sàn</button><input type="number" data-k="h" value="${sceneH().toFixed(1)}" step="1" min="1"><span class="sub">cm</span><button data-o="height" title="Scale cả cảnh về chiều cao này">${ic("height")}</button></div>
      <h2>Lưu và xuất</h2>
      <div class="row"><button data-o="obj">${ic("export")}OBJ</button><button data-o="rig" title="mesh_cm.json: định dạng Rig Lab đọc">${ic("export")}Cho Rig</button><button data-o="reset" class="bad" title="Bỏ mọi chỉnh sửa, về mesh gốc">Về bản gốc</button></div>
      <p class="note">Bản sửa tự lưu vào kho <code>${esc(store ? store.ns : "")}</code>; Rig Lab đọc trực tiếp bản này.</p>`;
  };
  let hInput = null;
  M.panel_click = e => {
    const b = e.target.closest("[data-o]"); if (!b) return;
    const k = b.dataset.o;
    if (k === "height") return opHeight(+(hInput || sceneH()));
    ({ weld: opWeld, ground: opGround, obj: exportOBJ, rig: exportRig, reset: resetAll, clean: opClean })[k]();
    ST.refresh();
  };
  M.panel_change = e => {
    const k = e.target.dataset.k; if (!k) return;
    if (k === "front") frontOnly = e.target.checked; else if (k === "sym") sym = e.target.checked;
    else if (k === "soft") { soft.on = e.target.checked; ST.refresh(); }
    else if (k === "eps") weldEps = +e.target.value || 0.05; else if (k === "h") hInput = +e.target.value;
  };
  M.panel_input = e => { if (e.target.dataset.k === "r") { soft.r = +e.target.value; const s = document.getElementById("mSr"); if (s) s.textContent = soft.r + " cm"; } };

  // ---------------------------------------------------------------- focus (đang sửa mesh / xương)
  M.focusIn = () => { placePivot(); };
  // W3c: khớp dùng chung (xương của Cảnh)
  M.curJoint = () => ST.mods.skel && ST.mods.skel.sel ? ST.mods.skel.sel() : null;
  M.hasJoint = n => !!(ST.mods.skel && ST.mods.skel.has && ST.mods.skel.has(n));
  M.selectJoint = (n, carry) => { const sk = ST.mods.skel; if (!sk || !sk.has(n)) return; if (carry && (selO.size || selV.size || selF.size)) return; sk.select(n); };
  M.focusOut = () => { V.gizmo.detach(); pivHold = false; buildFree(); };

  // ---------------------------------------------------------------- lệnh (menu, shelf, phím)
  const C = (o) => ST.cmd(Object.assign({ mod: "mesh" }, o));
  const md = (m, label, icon, key) => C({ id: "mesh.mode." + m, menu: "Select", label, icon, key, check: () => mode === m, run: () => setMode(m) });
  md("o", "Chọn mesh", "obj", "1"); md("v", "Chọn điểm", "vert", "2"); md("f", "Chọn mặt", "face", "3"); md("i", "Chọn khối rời", "island", "4");
  const mk = (k, label, icon) => C({ id: "selmask." + k, menu: "Select", keep: true, head: k === "joint" ? "Chọn được trong viewport" : undefined, sep: k === "joint", label, icon,
    tip: "Bật / tắt: click trong viewport có chọn được " + label.toLowerCase() + " không", check: () => mask[k],
    run: () => { mask[k] = !mask[k]; ST.pref.set("selmask", mask); say(label + (mask[k] ? ": chọn được trong viewport." : ": không chọn được trong viewport (Outliner vẫn chọn được).")); } });
  mk("joint", "Joint", "joint"); mk("mesh", "Mesh", "mesh");
  C({ id: "selmask.all", menu: "Select", keep: true, label: "Chọn được tất cả", icon: "all", run: () => { mask.joint = mask.mesh = true; ST.pref.set("selmask", mask); say("Chọn được mọi loại trong viewport."); } });
  C({ id: "sel.all", menu: "Select", sep: true, label: "Chọn tất cả", icon: "all", key: "ctrl+a", run: selectAll });
  C({ id: "sel.none", menu: "Select", label: "Bỏ chọn", icon: "none", key: "ctrl+shift+a", run: selectNone });
  C({ id: "sel.invert", menu: "Select", label: "Đảo vùng chọn", icon: "invert", key: "ctrl+i", run: selectInvert });
  C({ id: "sel.grow", menu: "Select", label: "Nới rộng một vòng", icon: "grow", key: ">", run: selectGrow });
  C({ id: "sel.front", menu: "Select", sep: true, label: "Chỉ chọn mặt trước", icon: "front", check: () => frontOnly, run: () => { frontOnly = !frontOnly; } });
  C({ id: "sel.sym", menu: "Select", label: "Đối xứng X", icon: "sym", check: () => sym, run: () => { sym = !sym; } });
  C({ id: "sel.soft", menu: "Select", label: "Chọn mềm (falloff)", icon: "soft", key: "b", check: () => soft.on, run: () => { soft.on = !soft.on; } });
  C({ id: "mesh.freeze", menu: "Mesh", label: "Freeze Transformations", icon: "reset", tip: "Giữ mesh tại chỗ, đưa Translate / Rotate về 0 và Scale về 1 (như Maya)", on: () => mode === "o" && selO.size > 0, run: opFreeze });
  function opFreeze() {
    const os = [...selO].map(get).filter(o => o && !o.lock); if (!os.length) return say("Chọn mesh trước (chế độ chọn mesh).");
    pushUndo("Freeze Transformations");
    os.forEach(o => { o.zero = (o.piv ? o.piv.clone() : (o.mesh.geometry.computeBoundingBox(), o.mesh.geometry.boundingBox.getCenter(new V3()))); });
    TS = null; changed(); refreshSel(); say("Đã freeze " + os.length + " mesh: Translate / Rotate = 0, Scale = 1.");
  }
  const pivCmd = (label, fn) => () => { if (!selCenter()) return say("Chọn mesh hoặc điểm / mặt trước."); pushUndo(label); fn(); changed(); refreshSel(); };
  C({ id: "mesh.pivEdit", menu: "Mesh", sep: true, label: "Sửa pivot (giữ D)", icon: "move", key: "insert", check: () => pivOn(), run: () => { pivEdit = !pivEdit; say(pivEdit ? "Sửa pivot: kéo gizmo để dời pivot. Insert lần nữa để thôi." : "Thôi sửa pivot."); refreshSel(); } });
  C({ id: "mesh.pivCenter", menu: "Mesh", label: "Pivot về tâm (Center Pivot)", icon: "frame", run: pivCmd("Pivot về tâm", () => setPiv(null)) });
  C({ id: "mesh.pivBottom", menu: "Mesh", label: "Pivot về đáy giữa", icon: "floor", run: pivCmd("Pivot về đáy", () => { const b = selBox(); if (b) setPiv(new V3((b.min.x + b.max.x) / 2, b.min.y, (b.min.z + b.max.z) / 2)); }) });
  C({ id: "mesh.pivOrigin", menu: "Mesh", label: "Pivot về gốc toạ độ", icon: "reset", run: pivCmd("Pivot về gốc", () => setPiv(new V3())) });
  const typing = e => /INPUT|TEXTAREA|SELECT/.test((e.target || {}).tagName || "");
  addEventListener("keydown", e => { if (e.repeat || typing(e) || e.ctrlKey || e.metaKey || e.altKey || e.key.toLowerCase() !== "d" || ST.mod() !== M) return; pivHold = true; refreshSel(); });
  addEventListener("keyup", e => { if (e.key.toLowerCase() !== "d" || !pivHold) return; pivHold = false; refreshSel(); });
  addEventListener("blur", () => { if (pivHold) { pivHold = false; refreshSel(); } });
  C({ id: "mesh.delete", menu: "Mesh", sep: true, label: "Xoá", icon: "trash", key: ["delete", "backspace"], run: opDelete });
  C({ id: "mesh.separate", menu: "Mesh", sep: true, label: "Tách mesh", icon: "cut", key: "p", run: opSeparate });
  C({ id: "mesh.merge", menu: "Mesh", label: "Gộp mesh", icon: "merge", key: "ctrl+j", run: opMerge });
  C({ id: "mesh.dup", menu: "Mesh", label: "Nhân bản", icon: "copy", key: "ctrl+d", run: opDuplicate });
  C({ id: "mesh.flip", menu: "Mesh", sep: true, label: "Lật pháp tuyến", icon: "flip", run: opFlip });
  C({ id: "mesh.smooth", menu: "Mesh", label: "Làm mượt", icon: "smooth", run: opSmooth });
  C({ id: "mesh.flipx", menu: "Mesh", label: "Lật trái/phải (X)", icon: "flipx", run: opFlipX });
  C({ id: "mesh.weld", menu: "Mesh", sep: true, label: "Hàn điểm gần", icon: "weld", run: opWeld });
  C({ id: "mesh.clean", menu: "Mesh", label: "Dọn mesh", icon: "clean", run: opClean });
  C({ id: "mesh.ground", menu: "Mesh", sep: true, label: "Đặt xuống sàn", icon: "floor", run: opGround });
  C({ id: "mesh.height", menu: "Mesh", label: "Chiều cao cả cảnh…", icon: "height", run: () => opHeight() });
  C({ id: "mesh.wire", menu: "Display", sep: true, keep: true, label: "Lưới mesh (wireframe)", icon: "wire", key: "v", check: () => showWire, run: () => { showWire = !showWire; ST.pref.set("mesh:wire", showWire); allVis(); } });
  ST.cmd({ id: "file.save", menu: "File", sep: true, label: "Lưu ngay", icon: "save", key: "ctrl+s", on: () => !!store, run: () => { dirty = true; save(); } });
  C({ id: "file.obj", menu: "File", label: "Xuất OBJ", icon: "export", run: exportOBJ });
  C({ id: "file.rigjson", menu: "File", label: "Xuất mesh_cm.json (cho Rig)", icon: "export", run: exportRig });
  C({ id: "file.reset", menu: "File", label: "Về mesh gốc", icon: "reset", run: resetAll });
  // ẩn / hiện như Maya: Ctrl+H ẩn mesh đang chọn, Shift+H hiện mesh đang chọn (chọn trong Outliner), Ctrl+Shift+H hiện tất cả
  M.setVis = (list, v) => { list = list.filter(o => o && o.vis !== v); if (!list.length) return 0; list.forEach(o => { o.vis = v; applyVis(o); }); dirty = true; changed(); refreshSel(); visToRig(); return list.length; };
  const visToRig = () => { const r = ST.mods.rig; if (r && r.syncVis) r.syncVis(); };
  M.byName = n => OBJ.find(o => o.name === n) || null;
  const selObjs = () => [...selO].map(get).filter(Boolean);
  C({ id: "mesh.hide", menu: "Display", sep: true, label: "Ẩn mesh đang chọn", icon: "eyeoff", key: "ctrl+h", on: () => selO.size > 0, run: () => say("Đã ẩn " + M.setVis(selObjs(), false) + " mesh.") });
  C({ id: "mesh.showSel", menu: "Display", label: "Hiện mesh đang chọn", icon: "eye", key: "shift+h", on: () => selO.size > 0, run: () => say("Đã hiện " + M.setVis(selObjs(), true) + " mesh.") });
  C({ id: "mesh.showAll", menu: "Display", label: "Hiện tất cả mesh", icon: "eye", key: "ctrl+shift+h", run: () => say("Đã hiện " + M.setVis(OBJ, true) + " mesh.") });
})();
