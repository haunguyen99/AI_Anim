// AI Anim Studio — xương của nhân vật (chỉ xem, sửa xương là bước S3): vẽ joint + đoạn nối cha → con trong viewport,
// cây Skeleton trong Outliner (mở / gập), bấm một joint để tô sáng và xem toạ độ. Nguồn: /api/char → skeleton (cm, Y lên).
(function () {
  const V = ST.view, S = ST.mods.skel = { joints: [] };
  let byName = {}, kids = {}, open = new Set(), sel = null, show = ST.pref.get("skel:show", true);
  const grp = new THREE.Group(); grp.renderOrder = 25; V.cm.add(grp);
  const ptMat = new THREE.PointsMaterial({ size: 7, sizeAttenuation: false, color: 0x3fb6ff, depthTest: false, transparent: true });
  const lnMat = new THREE.LineBasicMaterial({ color: 0x3fb6ff, depthTest: false, transparent: true, opacity: 0.75 });
  const selMat = new THREE.PointsMaterial({ size: 12, sizeAttenuation: false, color: 0xff7a1a, depthTest: false, transparent: true });
  let pts = null, lines = null, selPt = null;

  function build() {
    [pts, lines, selPt].forEach(o => { if (o) { grp.remove(o); o.geometry.dispose(); } });
    const P = [], L = [];
    S.joints.forEach(j => { P.push(...j.pos); const p = byName[j.parent]; if (p) L.push(...p.pos, ...j.pos); });
    const gp = new THREE.BufferGeometry(); gp.setAttribute("position", new THREE.Float32BufferAttribute(P, 3)); pts = new THREE.Points(gp, ptMat); pts.renderOrder = 26;
    const gl = new THREE.BufferGeometry(); gl.setAttribute("position", new THREE.Float32BufferAttribute(L, 3)); lines = new THREE.LineSegments(gl, lnMat); lines.renderOrder = 25;
    const gs = new THREE.BufferGeometry(); gs.setAttribute("position", new THREE.Float32BufferAttribute(sel ? byName[sel].pos : [], 3)); selPt = new THREE.Points(gs, selMat); selPt.renderOrder = 27;
    [lines, pts, selPt].forEach(o => { o.raycast = () => {}; grp.add(o); });
    grp.visible = show && S.joints.length > 0 && ST.ws !== "rig";
  }
  ST.on("ws", () => { grp.visible = show && S.joints.length > 0 && ST.ws !== "rig"; });
  ST.on("char", ch => {
    S.joints = ch.skeleton || []; byName = {}; kids = {}; sel = null;
    S.joints.forEach(j => { byName[j.name] = j; (kids[j.parent || ""] || (kids[j.parent || ""] = [])).push(j); });
    open = new Set(ST.pref.get("skel:open:" + ch.id, null) || S.joints.filter(j => depth(j) < 2).map(j => j.name));
    build();
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
    sel = sel === n ? null : n; build();
    ST.hint = sel ? "Joint " + n + " · " + j.pos.map(v => v.toFixed(1)).join(", ") + " cm" + (j.parent ? " · cha " + j.parent : "") : "";
  };
  S.isMine = id => typeof id === "string" && id.startsWith("j:");
  S.bounds = () => { if (!sel) return null; const p = new THREE.Vector3(...byName[sel].pos).applyMatrix4(V.cm.matrixWorld); return new THREE.Box3().setFromCenterAndSize(p, new THREE.Vector3(0.3, 0.3, 0.3)); };

  ST.cmd({ id: "view.skel", menu: "Display", label: "Xương (joint)", icon: "joint", check: () => show, on: () => S.joints.length > 0, run: () => { show = !show; ST.pref.set("skel:show", show); build(); } });
})();
