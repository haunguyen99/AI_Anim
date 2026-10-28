// AI Anim Studio — workspace Rig, bước 6 "Vật lý": những gì Pose cần từ rig, đặt ở Rig thay vì viết cứng trong Pose Lab
// (user 2026-10-27): khớp điều khiển (khớp nào có điểm chọn / dời được trong Pose), giới hạn khớp (gập / dạng / xoắn, độ),
// collider (capsule lõi mỗi đoạn thân, cm) và khối lượng (kg) mỗi bộ phận. Lưu doc rig/setup của kho <nhân vật>_rig_lab;
// Pose đọc doc này (window.__rigSetup) thay cho CHAR_PHYS khi nhân vật có nó.
// Đoạn thân = như Pose (BODY_SEG): đỉnh skin vào joint phụ / bả vai tính vào đoạn cha; collider tự tính như Pose (bán kính =
// bách phân 40 khoảng cách các đỉnh có trọng số chính trên đoạn, 10–90 % dọc đoạn), khối lượng = thể tích capsule × khối riêng.
(function () {
  const esc = ST.esc, V = ST.view;
  const RS = ST.rigSetup = { ver: 0 };
  let doc = null, eng = null, saveT = 0, grp = null, selSeg = null, limSel = "Shoulder_R", calc = null;

  const SEG = { Root_M: "Spine1_M", Spine1_M: "Chest_M", Chest_M: "Neck_M", Neck_M: "Head_M", Head_M: "HeadEnd_M" };
  for (const s of "LR") Object.assign(SEG, { ["Shoulder_" + s]: "Elbow_" + s, ["Elbow_" + s]: "Wrist_" + s, ["Wrist_" + s]: "MiddleFinger2_" + s,
    ["Hip_" + s]: "Knee_" + s, ["Knee_" + s]: "Ankle_" + s, ["Ankle_" + s]: "ToesEnd_" + s });
  const SEG_VI = { Root_M: "Hông", Spine1_M: "Bụng", Chest_M: "Ngực", Neck_M: "Cổ", Head_M: "Đầu", Shoulder: "Cánh tay", Elbow: "Cẳng tay", Wrist: "Bàn tay",
    Hip: "Đùi", Knee: "Cẳng chân", Ankle: "Bàn chân" };
  const side = n => n.endsWith("_R") ? " phải" : n.endsWith("_L") ? " trái" : "";
  const segName = k => (SEG_VI[k] || SEG_VI[k.replace(/_[LR]$/, "")] || k) + side(k);
  // giới hạn mặc định (độ): gập quanh trục Z local của xương lo/hi, dạng lo/hi, xoắn lo/hi; thân / tay / chân theo số đo trên Gaygor (Pose Lab)
  const LIM = { Spine1_M: [-35, 35, -25, 25, -33, 30], Chest_M: [-35, 35, -25, 25, -30, 30], Neck_M: [-40, 40, -30, 30, -40, 40], Head_M: [-40, 40, -30, 30, -50, 50],
    Scapula: [-20, 20, -20, 20, -10, 10], Shoulder: [-90, 90, -90, 90, -80, 80], Elbow: [-36, 108, -10, 10, -15, 15], Wrist: [-70, 70, -40, 40, -60, 60],
    Hip: [-90, 90, -50, 50, -40, 40], Knee: [-90, 60, -8, 8, -15, 15], Ankle: [-45, 45, -60, 25, -20, 45], Toes: [-40, 40, -5, 5, -5, 5],
    Finger1: [-10, 90, -20, 20, -10, 10], Finger: [-5, 100, -5, 5, -5, 5], Thumb1: [-30, 60, -30, 30, -30, 30], extra: [-30, 30, -30, 30, -20, 20] };
  function limDefault(n) {
    if (LIM[n]) return LIM[n].slice();
    const b = n.replace(/_[LR]$/, "");
    if (/^ThumbFinger1$/.test(b)) return LIM.Thumb1.slice();
    if (/Finger1$/.test(b)) return LIM.Finger1.slice();
    if (/Finger\d$/.test(b)) return LIM.Finger.slice();
    if (/^joint\d+$/.test(b)) return LIM.extra.slice();
    return LIM[b] ? LIM[b].slice() : null;
  }
  const noCtl = n => n === "root" || /End(_|$)|Twist/.test(n);

  // ---- dữ liệu
  const store = () => ST.store(ST.rigNs());
  RS.load = async () => { try { doc = await store().get("rig/setup"); } catch (e) { doc = null; } return doc; };
  function save() {
    clearTimeout(saveT); saveT = setTimeout(async () => {
      doc.at = new Date().toISOString();
      try { await store().set("rig/setup", doc); ST.saveState("Đã lưu cài đặt vật lý (work/store/" + ST.rigNs() + ")"); } catch (e) { ST.saveState("Không lưu được: " + (e.message || e), "err"); }
      RS.ver++; ST.emit("rig:setup", doc);
    }, 500);
  }
  function skel() { return eng ? eng.buildSkeleton() : []; }
  function compute() {      // capsule + khối lượng mặc định từ mesh thân + skin hiện tại (cm, kg)
    const g = eng.get(), SK = g.SK, D = g.DATA, B = {}; skel().forEach(b => B[b.name] = b);
    const par = n => (B[n] || {}).parent;
    const groupOf = n => { for (let x = n; x; x = par(x)) if (SEG[x]) return x; return null; };   // joint phụ, ngón… tính vào đoạn cha gần nhất
    const out = {};
    if (!SK) return out;
    const V3 = THREE.Vector3, P = D.body.verts, NV = P.length / 3, own = {};
    for (let i = 0; i < NV; i++) {
      let bi = 0, bw = 0; for (let k = 0; k < 4; k++) if (SK.W[i * 4 + k] > bw) { bw = SK.W[i * 4 + k]; bi = SK.I[i * 4 + k]; }
      const nm = SK.names[bi], gk = /^Scapula_/.test(nm) ? null : SEG[nm] ? nm : groupOf(nm); if (!gk) continue;
      (own[gk] || (own[gk] = [])).push(i);
    }
    for (const [k, e] of Object.entries(SEG)) {
      if (!B[k] || !B[e]) continue;
      const A = new V3(...B[k].pos), E = new V3(...B[e].pos), ab = E.clone().sub(A), L2 = Math.max(ab.lengthSq(), 1e-6), ds = [], p = new V3();
      for (const i of own[k] || []) { p.set(P[3 * i], P[3 * i + 1], P[3 * i + 2]); const t = p.clone().sub(A).dot(ab) / L2; if (t > 0.1 && t < 0.9) ds.push(p.distanceTo(A.clone().addScaledVector(ab, t))); }
      ds.sort((x, y) => x - y);
      out[k] = { r: ds.length >= 8 ? +ds[Math.floor(ds.length * 0.4)].toFixed(1) : null, len: +Math.sqrt(L2).toFixed(1) };
    }
    for (const [k, o] of Object.entries(out)) {   // đoạn ít đỉnh của riêng nó (vd bụng nằm giữa hông và ngực): trung bình đoạn trên / dưới
      if (o.r != null) continue;
      const up = Object.keys(SEG).find(x => SEG[x] === k), nb = [out[up], out[SEG[k]]].filter(x => x && x.r != null).map(x => x.r);
      o.r = nb.length ? +(nb.reduce((a, b) => a + b, 0) / nb.length).toFixed(1) : 2;
    }
    for (const k in out) {   // như Pose: đoạn dày hơn đoạn đối xứng 30 % (giáp bọc) lấy bán kính đoạn kia
      const m = /_[LR]$/.test(k) ? k.slice(0, -1) + (k.endsWith("L") ? "R" : "L") : null;
      if (m && out[m] && out[k].r > 1.3 * out[m].r) out[k].r = out[m].r;
    }
    return out;
  }
  const capMass = (r, len, rho) => { const R = r / 100, L = len / 100; return rho * (Math.PI * R * R * L + 4 / 3 * Math.PI * R ** 3); };
  function ensure() {     // doc đủ trường cho bộ xương hiện tại (thêm khớp mới, giữ giá trị người dùng đã sửa)
    if (!doc) doc = { v: 1, joints: {}, limits: {}, colliders: {}, mass: {}, rho: 1000 };
    calc = compute();
    for (const b of skel()) {
      if (noCtl(b.name)) continue;
      if (!doc.joints[b.name]) doc.joints[b.name] = { ctl: true, move: true };
      if (!doc.limits[b.name]) { const l = limDefault(b.name); if (l) doc.limits[b.name] = l; }
    }
    for (const [k, c] of Object.entries(calc)) {
      if (!doc.colliders[k]) doc.colliders[k] = { on: true, r: c.r, auto: true };
      if (doc.colliders[k].auto) doc.colliders[k].r = c.r;
      if (doc.mass[k] == null || doc.massAuto !== false && !(doc.massSet || {})[k]) doc.mass[k] = +capMass(doc.colliders[k].r, c.len, doc.rho).toFixed(1);
    }
  }

  // ---- viewport: capsule collider (cm, trong nhóm rig của Rig)
  function drawCaps(show) {
    if (grp) { grp.parent && grp.parent.remove(grp); grp.traverse(o => { if (o.geometry) o.geometry.dispose(); }); grp = null; }
    if (!show || !eng || !doc) return;
    const root = ST.rigRoot && ST.rigRoot(); if (!root) return;
    grp = new THREE.Group(); grp.renderOrder = 30; root.add(grp);
    const B = {}; skel().forEach(b => B[b.name] = b);
    for (const [k, c] of Object.entries(doc.colliders)) {
      if (!c.on || !B[k] || !B[SEG[k]]) continue;
      const A = new THREE.Vector3(...B[k].pos), E = new THREE.Vector3(...B[SEG[k]].pos), d = E.clone().sub(A), L = d.length(); if (L < 1e-3) continue;
      const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.clone().divideScalar(L)), r = c.r, pts = [];
      const ring = y => { for (let i = 0; i <= 24; i++) { const t = i / 24 * Math.PI * 2; pts.push([Math.cos(t) * r, y, Math.sin(t) * r]); } };
      const seg = []; const push = (a, b) => seg.push(...a, ...b);
      ring(0); for (let i = 0; i < 24; i++) push(pts[i], pts[i + 1]); pts.length = 0; ring(L); for (let i = 0; i < 24; i++) push(pts[i], pts[i + 1]);
      for (let i = 0; i < 4; i++) { const t = i / 4 * Math.PI * 2, x = Math.cos(t) * r, z = Math.sin(t) * r; push([x, 0, z], [x, L, z]);
        for (let j = 0; j < 8; j++) { const a0 = j / 8 * Math.PI / 2, a1 = (j + 1) / 8 * Math.PI / 2;   // nắp bán cầu hai đầu
          push([x * Math.cos(a0), -r * Math.sin(a0), z * Math.cos(a0)], [x * Math.cos(a1), -r * Math.sin(a1), z * Math.cos(a1)]);
          push([x * Math.cos(a0), L + r * Math.sin(a0), z * Math.cos(a0)], [x * Math.cos(a1), L + r * Math.sin(a1), z * Math.cos(a1)]); } }
      const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(seg, 3));
      const on = k === selSeg, col = k.endsWith("_R") ? 0xff6a6a : k.endsWith("_L") ? 0x5aa8ff : 0xffd24a;
      const ln = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ color: on ? 0xffffff : col, transparent: true, opacity: on ? 1 : 0.7, depthTest: false }));
      ln.position.copy(A); ln.quaternion.copy(q); ln.renderOrder = 30; ln.raycast = () => {}; grp.add(ln);
    }
  }

  // ---- panel bước 6
  const num = (v, a) => `<input type="number" step="${a || 1}" value="${v}" style="width:4.2em">`;
  RS.panel = () => {
    if (!eng) return '<div class="sub">Đang nạp rig…</div>';
    if (!eng.get().SK) return '<p class="note">Cần skin (bước 4) trước: collider và khối lượng tính từ đỉnh skin vào từng đoạn.</p>';
    ensure();
    const J = skel().filter(b => !noCtl(b.name)), tot = Object.values(doc.mass).reduce((a, b) => a + b, 0);
    const lim = doc.limits[limSel] || [0, 0, 0, 0, 0, 0], limOpts = Object.keys(doc.limits).map(n => `<option ${n === limSel ? "selected" : ""}>${esc(n)}</option>`).join("");
    const rows = (list, f) => list.map(f).join("");
    return `<h2>6 · Vật lý</h2><p class="note">Pose đọc phần này: khớp nào chọn / dời được, giới hạn khớp cho ragdoll, collider và khối lượng cho va chạm / tác động.</p>
<details open><summary><b>Khớp điều khiển</b> <span class="sub">(${J.filter(b => doc.joints[b.name].ctl).length}/${J.length} có điểm trong Pose)</span></summary>
<div class="row"><button data-s="ctlAll">Bật hết</button><button data-s="ctlBody">Chỉ thân, tay, chân</button><button data-s="moveNone">Chỉ xoay (trừ hông, cổ chân, cổ tay)</button></div>
<table class="tbl"><thead><tr><th>Khớp</th><th>Điều khiển</th><th>Dời được</th></tr></thead><tbody>${rows(J, b => { const j = doc.joints[b.name];
  return `<tr><td>${esc(b.name)}</td><td><input type="checkbox" data-c="ctl" data-n="${esc(b.name)}" ${j.ctl ? "checked" : ""} aria-label="Điều khiển ${esc(b.name)}"></td><td><input type="checkbox" data-c="move" data-n="${esc(b.name)}" ${j.move ? "checked" : ""} ${j.ctl ? "" : "disabled"} aria-label="Dời ${esc(b.name)}"></td></tr>`; })}</tbody></table></details>
<details open><summary><b>Giới hạn khớp</b> <span class="sub">(độ, quanh tư thế nghỉ)</span></summary>
<div class="row"><select id="limSel" aria-label="Khớp">${limOpts}</select><button data-s="limMirror" title="Chép sang khớp cùng tên bên kia">Đối xứng</button><button data-s="limReset">Mặc định</button></div>
<table class="tbl"><thead><tr><th></th><th>Thấp</th><th>Cao</th></tr></thead><tbody>${["Gập", "Dạng", "Xoắn"].map((l, i) => `<tr><td>${l}</td><td data-l="${2 * i}">${num(lim[2 * i])}</td><td data-l="${2 * i + 1}">${num(lim[2 * i + 1])}</td></tr>`).join("")}</tbody></table></details>
<details open><summary><b>Collider</b> <span class="sub">(capsule lõi, cm; vẽ trong viewport)</span></summary>
<div class="row"><button data-s="colAuto">Tính lại theo mesh</button></div>
<table class="tbl"><thead><tr><th>Đoạn</th><th>Bật</th><th>Bán kính</th><th>Dài</th></tr></thead><tbody>${rows(Object.keys(doc.colliders), k => { const c = doc.colliders[k];
  return `<tr class="${k === selSeg ? "sel" : ""}" data-seg="${esc(k)}"><td>${esc(segName(k))}</td><td><input type="checkbox" data-c="col" data-n="${esc(k)}" ${c.on ? "checked" : ""} aria-label="Bật collider ${esc(segName(k))}"></td><td data-r="${esc(k)}">${num(c.r, 0.5)}${c.auto ? "" : " ✎"}</td><td class="sub">${calc[k] ? calc[k].len : "—"}</td></tr>`; })}</tbody></table></details>
<details open><summary><b>Khối lượng</b> <span class="sub">(kg · tổng ${tot.toFixed(1)} kg)</span></summary>
<div class="row"><label class="sub">Khối riêng</label>${num(doc.rho, 50).replace("<input", '<input id="rho" aria-label="Khối riêng kg/m3"')}<span class="sub">kg/m³</span><button data-s="massAuto">Tính theo collider</button></div>
<table class="tbl"><tbody>${rows(Object.keys(doc.mass), k => `<tr data-seg="${esc(k)}"><td>${esc(segName(k))}</td><td data-m="${esc(k)}">${num(doc.mass[k], 0.5)}${(doc.massSet || {})[k] ? " ✎" : ""}</td></tr>`)}</tbody></table></details>`;
  };
  RS.mounted = () => { drawCaps(true); };
  RS.hide = () => drawCaps(false);
  const redraw = () => { RS.ver++; ST.refresh(); setTimeout(() => drawCaps(true), 0); };
  RS.change = e => {
    const t = e.target; if (!doc) return;
    if (t.dataset.c === "ctl") { doc.joints[t.dataset.n].ctl = t.checked; save(); return redraw(); }
    if (t.dataset.c === "move") { doc.joints[t.dataset.n].move = t.checked; save(); return; }
    if (t.dataset.c === "col") { doc.colliders[t.dataset.n].on = t.checked; save(); return drawCaps(true); }
    if (t.id === "limSel") { limSel = t.value; RS.ver++; return ST.refresh(); }
    if (t.id === "rho") { doc.rho = +t.value || 1000; doc.massSet = {}; save(); return redraw(); }
    const l = t.closest("[data-l]"), r = t.closest("[data-r]"), m = t.closest("[data-m]");
    if (l && doc.limits[limSel]) { doc.limits[limSel][+l.dataset.l] = +t.value; save(); return; }
    if (r) { const c = doc.colliders[r.dataset.r]; c.r = Math.max(0.3, +t.value || c.r); c.auto = false; if (!(doc.massSet || {})[r.dataset.r]) doc.mass[r.dataset.r] = +capMass(c.r, calc[r.dataset.r].len, doc.rho).toFixed(1); save(); return redraw(); }
    if (m) { (doc.massSet || (doc.massSet = {}))[m.dataset.m] = true; doc.mass[m.dataset.m] = Math.max(0, +t.value || 0); save(); return redraw(); }
  };
  RS.click = e => {
    const b = e.target.closest("[data-s]"), row = e.target.closest("tr[data-seg]");
    if (row && !e.target.closest("input")) { selSeg = row.dataset.seg === selSeg ? null : row.dataset.seg; return redraw(); }
    if (!b || !doc) return;
    const J = skel().filter(x => !noCtl(x.name)).map(x => x.name), a = b.dataset.s;
    if (a === "ctlAll") J.forEach(n => doc.joints[n].ctl = true);
    if (a === "ctlBody") J.forEach(n => doc.joints[n].ctl = !/Finger|^joint\d|^Toes/.test(n));
    if (a === "moveNone") J.forEach(n => doc.joints[n].move = /^(Root_M|Ankle_|Wrist_)/.test(n));
    if (a === "limReset") { const l = limDefault(limSel); if (l) doc.limits[limSel] = l; }
    if (a === "limMirror") { const m = /_[LR]$/.test(limSel) ? limSel.slice(0, -1) + (limSel.endsWith("L") ? "R" : "L") : null; if (m && doc.limits[m]) doc.limits[m] = doc.limits[limSel].slice(); else return ST.toast("Khớp này không có cặp trái / phải."); }
    if (a === "colAuto") for (const c of Object.values(doc.colliders)) c.auto = true;
    if (a === "massAuto") doc.massSet = {};
    save(); redraw();
  };
  RS.bind = e => { eng = e; doc = null; RS.load().then(() => { if (eng && eng.get().SK) { ensure(); save(); } RS.ver++; ST.refresh(); }); };
  RS.unbind = () => { drawCaps(false); eng = null; doc = null; };
})();
