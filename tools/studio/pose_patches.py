"""Bản vá Studio cho lõi Pose (modules/pose_engine.js), áp sau khi port_pose.py dựng lõi từ work/pose_lab/index.html.
Trước đây các bản vá này sửa thẳng pose_engine.js nên chạy lại port_pose.py là mất (2026-10-29: chuyển hết vào đây).
Mỗi mục (cũ, mới): đoạn "cũ" phải có đúng một lần trong lõi vừa dựng. Thêm bản vá mới cho lõi Pose của Studio: thêm một mục vào
cuối PATCHES (không sửa tay pose_engine.js), chạy lại `.venv/Scripts/python.exe -I tools/studio/port_pose.py`.
Nội dung: kho đổi được (setNS), camera Orthographic, nhớ góc camera, độ mờ khớp + khớp sắp chọn, timeline theo đối tượng chọn,
playblast theo góc đang xem / Gate, nút [ ] của Studio, đổi anim tại chỗ (swapClip)…
"""

PATCHES = [
    (r'''  const db = { isLocal: true, ns: NS, doc: path => { const [c, ...r] = path.split("/"); return docRef(c, r.join("/")); }, collection: colRef };
  db.ping = async function () {
''',
     r'''  const db = { isLocal: true, ns: NS, doc: path => { const [c, ...r] = path.split("/"); return docRef(c, r.join("/")); }, collection: colRef };
  // Studio đổi anim tại chỗ (user 2026-10-29: "chỉ load lại key thôi"): đổi kho, các onSnapshot đang nghe nhận ngay dữ liệu của kho mới
  db.setNS = ns => { NS = ns; db.ns = ns; return Promise.all(Object.keys(watchers).map(c => { watchers[c].last = null; return tick(c); })); };
  db.ping = async function () {
'''),
    (r'''const CAM = host.cam;
// ---------------------------------------------------------------- data
''',
     r'''const CAM = host.cam;
// camera Orthographic ở các góc thẳng (user 2026-10-29): cỡ 1 pixel màn hình (m) tại điểm cách camera d, đổi tỉ lệ khung, kéo xa / lại gần
const pxAt = d => { const c = CAM(), h = Math.max(1, canvas.clientHeight); return c.isOrthographicCamera ? (c.top - c.bottom) / c.zoom / h : 2 * Math.tan(THREE.MathUtils.degToRad(c.fov) / 2) * d / h; };
const camAspect = a => { const c = CAM(); if (c.isOrthographicCamera) { c.left = -a; c.right = a; c.top = 1; c.bottom = -1; } else c.aspect = a; c.updateProjectionMatrix(); };
const camDolly = k => { const c = CAM(), t = orbit.target; if (c.isOrthographicCamera) { c.zoom /= k; c.updateProjectionMatrix(); } else { c.position.sub(t).multiplyScalar(k).add(t); c.lookAt(t); } };
// ---------------------------------------------------------------- data
'''),
    (r'''// joint + a thin stick to its parent joint. Opacity 50 % by default, fading with CAM() distance (near = clearest),
''',
     r'''// joint + a thin stick to its parent joint. Opacity 20 % by default (JOINT_BASE), fading with CAM() distance (near = clearest),
'''),
    (r'''const DOT_PX = 3.5, STICK_PX = 0.8;
''',
     r'''const DOT_PX = 3.5, STICK_PX = 0.8, JOINT_BASE = 0.2;   // độ đậm khớp khi chuột chưa lại gần (trước 0.5); rê tới / chọn = 100 %
'''),
    (r'''const COL = { joint: new THREE.Color(css("--joint")), edit: new THREE.Color(css("--edit")), sel: new THREE.Color(css("--accent")) };
''',
     r'''const COL = { joint: new THREE.Color(css("--joint")), edit: new THREE.Color(css("--edit")), sel: new THREE.Color(css("--accent")), hot: new THREE.Color(0xffffff) };
'''),
    (r'''let sticks = {}, selSet = new Set(), hoverXY = null, multiQ0 = null;
''',
     r'''let sticks = {}, selSet = new Set(), hoverXY = null, multiQ0 = null, hotEl = null, hotN = null;
'''),
    (r'''  const c = CAMS[k]; curCam = k; if (typeof renderRef === "function") renderRef();
''',
     r'''  const c = CAMS[k]; curCam = k; if (host.camName) host.camName(k); if (typeof renderRef === "function") renderRef();
'''),
    (r'''  CAM().position.copy(new V3(...c.pos).sub(new V3(...c.tgt)).multiplyScalar(camFit).add(t)); orbit.target.copy(t); orbit.update();
''',
     r'''  if (host.setOrtho) host.setOrtho(k !== "persp");   // Studio: góc thẳng = camera Orthographic, 3/4 = phối cảnh
  const cam = CAM(), off = new V3(...c.pos).sub(new V3(...c.tgt)).multiplyScalar(camFit);
  if (cam.isOrthographicCamera) { cam.zoom = 1 / (off.length() * Math.tan(THREE.MathUtils.degToRad(30) / 2)); cam.position.copy(t).addScaledVector(off.normalize(), Math.max(20, 8 * camFit)); cam.up.set(0, 1, 0); cam.lookAt(t); cam.updateProjectionMatrix(); }
  else cam.position.copy(off.add(t));
  orbit.target.copy(t); orbit.update();
'''),
    (r'''orbit.addEventListener("start", () => document.querySelectorAll(".cams button").forEach(b => b.classList.remove("on")));
''',
     r'''orbit.addEventListener("start", () => { document.querySelectorAll(".cams button").forEach(b => b.classList.remove("on")); if (curCam !== "persp" && CAM().isPerspectiveCamera) { curCam = "persp"; $("camTag").innerHTML = "Camera: <b>persp (tự do)</b>"; } if (host.camName) host.camName("free"); });
'''),
    (r'''    camFit = P.camFit || Math.max(0.6, Math.min(4, top / 1.75)); setCam(curCam);   // POSES camFit when a prop sticks out above the joints
''',
     r'''    camFit = P.camFit || Math.max(0.6, Math.min(4, top / 1.75)); if (!camInit) { camInit = true; setCam(curCam); }   // chỉ lần đầu: đổi phiên bản giữ nguyên camera (user 2026-10-29)   // POSES camFit when a prop sticks out above the joints
'''),
    (r'''}
function renderStrip() {
''',
     r'''}
// timeline theo đối tượng đang chọn (user 2026-10-29 "key trên timeline đang hiển thị chung cho tất cả đối tượng"):
// chọn vật thể phụ = key riêng của nó; chọn khớp = key cả người nhưng key mà khớp đó giữ nguyên (so key trước) vẽ rỗng; không chọn = như cũ
const boneDiff = (a, b) => { if (!a || !b) return !!(a || b); const d = Math.abs(a[0] * b[0] + a[1] * b[1] + a[2] * b[2] + a[3] * b[3]); return d < 0.99999 || Math.hypot(a[4] - b[4], a[5] - b[5], a[6] - b[6]) > 1e-4; };
function keyFilter() {
  const pk = host.propKeys ? host.propKeys() : null;
  if (pk) return { kind: "prop", name: pk.name, keys: new Set(pk.keys) };
  const js = [...selSet].filter(n => B[n]); if (!js.length || !keysMode()) return null;
  const ks = [...KEYS.keys()].sort((a, b) => a - b), moved = new Set();
  ks.forEach((f, i) => { const a = i ? (KEYS.get(ks[i - 1]).pose || {}) : null, b = KEYS.get(f).pose || {}; if (!a || js.some(n => boneDiff(a[n], b[n]))) moved.add(f); });
  return { kind: "joint", name: js.map(n => NAMES[n] || n).join(", "), keys: moved };
}
let stripSig = "";
const stripSigNow = () => { const pk = host.propKeys ? host.propKeys() : null; return (pk ? pk.name + ":" + pk.keys.join(",") : "") + "|" + [...selSet].join(","); };
function renderStrip() {
'''),
    (r'''  if (!model) return;
  const saved = new Set(mine().filter(a => a.status !== "done").map(a => a.frame || 1));
''',
     r'''  if (!model) return;
  const KF = keyFilter(); stripSig = stripSigNow();
  { let tag = $("kfTag"); if (!tag) { tag = document.createElement("span"); tag.id = "kfTag"; tag.className = "kftag"; $("fcount").after(tag); }
    tag.hidden = !KF; tag.textContent = KF ? (KF.kind === "prop" ? "Key: " + KF.name : "Key: " + KF.name + " (rỗng = khớp giữ nguyên)") : "";
    tag.title = KF ? (KF.kind === "prop" ? "Timeline đang hiện key của vật thể " + KF.name + ". Bỏ chọn để thấy key cả người." : "Key đặc = khớp đang chọn đổi so với key trước, rỗng = giữ nguyên. Bỏ chọn để thấy mọi key.") : ""; }
  const saved = new Set(mine().filter(a => a.status !== "done").map(a => a.frame || 1));
'''),
    (r'''    if (km) { c.classList.toggle("key", f === cyc(f) && KEYS.has(f)); c.classList.toggle("knew", f === cyc(f) && KEYS.has(f) && NEWK.has(f)); c.classList.toggle("loopend", f !== cyc(f) && KEYS.has(cyc(f)));
''',
     r'''    if (KF && KF.kind === "prop") { c.classList.toggle("key", KF.keys.has(f)); c.classList.add("kprop"); c.classList.remove("knew", "loopend", "khold", "kdrop"); }
    else if (km) { c.classList.remove("kprop"); c.classList.toggle("key", f === cyc(f) && KEYS.has(f)); c.classList.toggle("knew", f === cyc(f) && KEYS.has(f) && NEWK.has(f) && !KF); c.classList.toggle("loopend", f !== cyc(f) && KEYS.has(cyc(f)));
              c.classList.toggle("khold", !!KF && f === cyc(f) && KEYS.has(f) && !KF.keys.has(f));
'''),
    (r'''              c.classList.toggle("kdrop", !!keyDrag && keyDrag.to === f); }
    c.querySelectorAll(".dot").forEach(d => d.remove());
''',
     r'''              c.classList.toggle("kdrop", !!keyDrag && keyDrag.to === f); }
    else c.classList.remove("kprop", "khold");
    c.querySelectorAll(".dot").forEach(d => d.remove());
'''),
    (r'''  if (keysMode() && (e.button === 1 || e.shiftKey || TM.add) && KEYS.has(cyc(f))) {     // Shift / middle drag = move the key
''',
     r'''  if (keysMode() && !(host.propKeys && host.propKeys()) && (e.button === 1 || e.shiftKey || TM.add) && KEYS.has(cyc(f))) {     // Shift / middle drag = move the key (không khi timeline đang hiện key vật thể)
'''),
    (r'''  const pxW = 2 * Math.tan(THREE.MathUtils.degToRad(CAM().fov) / 2) / Math.max(1, canvas.clientHeight);
''',
     r'''  // khớp sẽ được chọn nếu bấm ngay (user 2026-10-29: rê chuột thì nhiều khớp cùng sáng, không biết bấm trúng khớp nào):
  // đúng luật của pickAt, tô trắng + to hơn + tên cạnh chuột
  let hot = null; try { hot = show && hoverXY && !gizmo.dragging && !(marq && marq.on) ? pickAt(hoverXY[0], hoverXY[1]) : null; } catch (e) {}
  hotTag(hot);
'''),
    (r'''    let o = 0.5 * (1 - 0.55 * far);                                        // default 50 %, fading with distance
''',
     r'''    let o = JOINT_BASE * (1 - 0.55 * far);                                 // mặc định mờ (user 2026-10-29 "độ mờ của khớp ban đầu mờ hơn nữa"), nhạt dần theo khoảng cách
'''),
    (r'''    if (on) o = 1;
''',
     r'''    if (on || n === hot) o = 1;
'''),
    (r'''    m.material.color.copy(on ? COL.sel : edited.has(n) ? COL.edit : COL.joint);
''',
     r'''    m.material.color.copy(n === hot && !on ? COL.hot : on ? COL.sel : edited.has(n) ? COL.edit : COL.joint);
'''),
    (r'''    SZ[n] = D[n] * pxW;                                                    // world size of 1 screen pixel there
    m.scale.setScalar(SZ[n] * DOT_PX * (n === sel ? 1.5 : on ? 1.25 : 1));
''',
     r'''    SZ[n] = pxAt(D[n]);                                                    // world size of 1 screen pixel there
    m.scale.setScalar(SZ[n] * DOT_PX * (n === sel ? 1.5 : n === hot ? 1.7 : on ? 1.25 : 1));
'''),
    (r'''const visJoints = () => $("tJoints").classList.contains("on") ? Object.keys(markers) : [];
function pickAt(x, y) {
''',
     r'''const visJoints = () => $("tJoints").classList.contains("on") ? Object.keys(markers) : [];
function hotTag(n) {   // tên khớp sắp chọn, cạnh con trỏ
  if (!hotEl) { hotEl = document.createElement("div"); hotEl.className = "jhot"; hotEl.style.cssText = "position:absolute;pointer-events:none;z-index:7;padding:1px 6px;border-radius:4px;background:#000c;color:#fff;font:11px/1.5 system-ui,sans-serif;white-space:nowrap;display:none"; viewer.appendChild(hotEl); }
  if (n !== hotN) { hotN = n; hotEl.textContent = n ? (NAMES[n] || n) : ""; }
  canvas.style.cursor = n ? "pointer" : "";
  if (!n || !hoverXY) { hotEl.style.display = "none"; return; }
  const r = canvas.getBoundingClientRect(), vr = viewer.getBoundingClientRect();
  hotEl.style.display = "block"; hotEl.style.left = (r.left - vr.left + hoverXY[0] + 14) + "px"; hotEl.style.top = (r.top - vr.top + hoverXY[1] + 10) + "px";
}
function pickAt(x, y) {
'''),
    (r'''canvas.addEventListener("pointerleave", () => { hoverXY = null; });
''',
     r'''canvas.addEventListener("pointerleave", () => { hoverXY = null; hotTag(null); });
'''),
    (r'''    o.mesh.position.copy(pos); o.mesh.scale.setScalar(CAM().position.distanceTo(pos) * pxW * 6 * (poleSel === k ? 1.5 : 1));
''',
     r'''    o.mesh.position.copy(pos); o.mesh.scale.setScalar(pxAt(CAM().position.distanceTo(pos)) * 6 * (poleSel === k ? 1.5 : 1));
'''),
    (r'''  if (e.target.matches("textarea, input")) return;
''',
     r'''  if (e.target.matches && e.target.matches("textarea, input")) return;
'''),
    (r'''      c.fillStyle = "#fff"; c.font = "bold 15px sans-serif"; c.fillText(P.clip.replace(/_/g, " ") + " · " + P.version + " · góc " + CAMS[k].label, 8, 18);
      renderer.setSize(cw, ch, false); CAM().aspect = cw / ch; CAM().updateProjectionMatrix();
      frames.forEach((f, i) => {
''',
     r'''      c.fillStyle = "#fff"; c.font = "bold 15px sans-serif"; c.fillText(P.clip.replace(/_/g, " ") + " · " + P.version + " · góc " + CAMS[k].label, 8, 18);
      renderer.setSize(cw, ch, false); camAspect(cw / ch);
      frames.forEach((f, i) => {
'''),
    (r'''        { const t = orbit.target; CAM().position.sub(t).multiplyScalar(1.5).add(t); CAM().lookAt(t); }   // square cell: pull back so the 2.5 m mace stays in frame (polish_v2 review cropped it at F33)
''',
     r'''        camDolly(1.5);   // square cell: pull back so the 2.5 m mace stays in frame (polish_v2 review cropped it at F33)
'''),
    (r'''$("tList").onclick = () => { PANES.list = !PANES.list; applyPanes(); };
$("tSide").onclick = () => { PANES.side = !PANES.side; applyPanes(); };
applyPanes();
''',
     r'''if (host.panes) {   // Studio (user 2026-10-29 "hai nút này đang không hoạt động"): [ = cột trái (Outliner / Phiên bản), ] = dock phải của Studio
  const sync = () => { $("tList").classList.toggle("on", host.panes.on("list")); $("tSide").classList.toggle("on", host.panes.on("side")); };
  $("tList").onclick = () => { host.panes.toggle("list"); sync(); };
  $("tSide").onclick = () => { host.panes.toggle("side"); sync(); };
  $("tList").title = "Ẩn / hiện cột trái (Outliner, Phiên bản) ( [ )"; $("tSide").title = "Ẩn / hiện dock phải (Khớp, Vật lý, Góp ý cho AI) ( ] )";
  host.panes.onChange(sync); sync();
} else {
  $("tList").onclick = () => { PANES.list = !PANES.list; applyPanes(); };
  $("tSide").onclick = () => { PANES.side = !PANES.side; applyPanes(); };
  applyPanes();
}
'''),
    (r'''host.onFrame(now => { tickPlay(now || performance.now()); if (model) placeMarkers(); if (model && trailOn) trailUpdate(); });
setCam("right"); renderPoses(); openPose(POSES[0]);
''',
     r'''host.onFrame(now => { tickPlay(now || performance.now()); if (model) placeMarkers(); if (model && trailOn) trailUpdate(); if (model && stripSigNow() !== stripSig) renderStrip(); });
// góc camera đã lưu (Studio, host.savedView): dùng lại thay cho góc Right mặc định, kể cả khi model nạp xong
let camInit = false;
{ const sv = host.savedView ? host.savedView() : null;
  if (sv && host.applyView && host.applyView(sv)) { camInit = true; const k = sv.cam; curCam = k && CAMS[k] ? k : "persp";
    $("camTag").innerHTML = "Camera: <b></b>"; $("camTag").querySelector("b").textContent = k && CAMS[k] ? CAMS[k].label : "persp (tự do)";
    document.querySelectorAll(".cams button").forEach(b => b.classList.toggle("on", b.dataset.cam === k)); }
  else setCam("right"); }
renderPoses(); openPose(POSES[0]);
'''),
    (r'''/*PLAYBLAST*/
// Quay playblast: mỗi frame goto(f) rồi vẽ N CAM() cạnh nhau (chỉ scene, không overlay) vào canvas ghép, MediaRecorder thu theo nhịp fps.
''',
     r'''/*PLAYBLAST*/
// góc "Đang xem" (user 2026-10-29 "playblast đưa nhân vật về chính giữa, không lấy được view mong muốn"): chụp camera viewport lúc mở hộp,
// quay đúng góc đó (Gate bật: ô theo tỉ lệ Gate, khung = phần trong Gate), xong / huỷ thì trả viewport về đúng góc cũ
const viewSnap = () => { const c = CAM(); return { ortho: !!c.isOrthographicCamera, pos: c.position.clone(), q: c.quaternion.clone(), up: c.up.clone(), tgt: orbit.target.clone(), zoom: c.zoom, fov: c.fov, cam: curCam, tag: $("camTag").innerHTML }; };
function viewSet(v, frac) {
  if (host.setOrtho) host.setOrtho(v.ortho);
  const c = CAM(); c.up.copy(v.up); c.position.copy(v.pos); c.quaternion.copy(v.q); orbit.target.copy(v.tgt);
  if (c.isOrthographicCamera) c.zoom = v.zoom / (frac || 1);
  else if (v.fov) c.fov = frac ? 2 * THREE.MathUtils.radToDeg(Math.atan(Math.tan(THREE.MathUtils.degToRad(v.fov) / 2) * frac)) : v.fov;
  c.updateProjectionMatrix(); curCam = v.cam; $("camTag").innerHTML = v.tag;
  document.querySelectorAll(".cams button").forEach(b => b.classList.toggle("on", b.dataset.cam === v.cam));
}
const pbGate = () => host.gate ? host.gate() : null;   // { A: rộng/cao, frac: cao Gate / cao khung } hoặc null
const pbLabel = k => k === "view" ? "Đang xem" : CAMS[k].label;
// Quay playblast: mỗi frame goto(f) rồi vẽ N CAM() cạnh nhau (chỉ scene, không overlay) vào canvas ghép, MediaRecorder thu theo nhịp fps.
'''),
    (r'''  if (!mime) throw new Error("Trình duyệt không quay được video (MediaRecorder).");
  const wasFrame = frame, wasCam = curCam, wasGhost = ghost && ghost.visible, wasSize = renderer.getSize(new THREE.Vector2()), prog = opt.onProgress || (() => {});
''',
     r'''  if (!mime) throw new Error("Trình duyệt không quay được video (MediaRecorder).");
  const VIEW = opt.view || viewSnap(), G = pbGate();
  const wasFrame = frame, wasCam = curCam, wasGhost = ghost && ghost.visible, wasSize = renderer.getSize(new THREE.Vector2()), prog = opt.onProgress || (() => {});
'''),
    (r'''      renderer.setSize(cw, ch, false); CAM().aspect = cw / ch; CAM().updateProjectionMatrix();
''',
     r'''      renderer.setSize(cw, ch, false); camAspect(cw / ch);
'''),
    (r'''      cams.forEach((k, i) => { setCam(k); if (dist !== 1) { const t = orbit.target; CAM().position.sub(t).multiplyScalar(dist).add(t); CAM().lookAt(t); } renderer.setClearColor(bg, 1); renderer.clear(); renderer.render(scene, CAM()); ctx.drawImage(renderer.domElement, i * cw, 0, cw, ch); });
''',
     r'''      cams.forEach((k, i) => { if (k === "view") viewSet(VIEW, G && G.frac); else { setCam(k); if (dist !== 1) camDolly(dist); } renderer.setClearColor(bg, 1); renderer.clear(); renderer.render(scene, CAM()); ctx.drawImage(renderer.domElement, i * cw, 0, cw, ch); });
'''),
    (r'''    msg.remove(); if (ghost) ghost.visible = wasGhost; ONION.off = Math.max(0, ONION.off - 1); renderer.setSize(wasSize.x, wasSize.y, false); resize(); setCam(wasCam); goto(wasFrame); renderer.setClearColor(0x000000, 0);
''',
     r'''    msg.remove(); if (ghost) ghost.visible = wasGhost; ONION.off = Math.max(0, ONION.off - 1); renderer.setSize(wasSize.x, wasSize.y, false); resize(); viewSet(VIEW); goto(wasFrame); renderer.setClearColor(0x000000, 0);
'''),
    (r'''  return { webm: new Blob(chunks, { type: "video/webm" }), thumb, n, fps, w: cw * cams.length, h: ch, views: cams.map(k => CAMS[k].label.toLowerCase()).join(" | ") };
''',
     r'''  return { webm: new Blob(chunks, { type: "video/webm" }), thumb, n, fps, w: cw * cams.length, h: ch, views: cams.map(k => pbLabel(k).toLowerCase()).join(" | ") };
'''),
    (r'''    const wasCam = curCam; let dist = saved.dist >= 0.3 && saved.dist <= 3 ? saved.dist : 1;
    const order = ["right", "left", "front", "back", "top", "bottom", "persp"], on = new Set(saved.cams || ["right", "left", "front", "top"]);
    const sizes = { s: [300, 400, "Nhỏ"], m: [450, 600, "Vừa"], l: [600, 800, "Lớn"] }; let sz = saved.size && sizes[saved.size] ? saved.size : "m";
''',
     r'''    const view0 = viewSnap(), G = pbGate(); let dist = saved.dist >= 0.3 && saved.dist <= 3 ? saved.dist : 1;
    const order = ["view", "right", "left", "front", "back", "top", "bottom", "persp"], on = new Set(saved.cams || ["view"]);
    const ev = n => Math.max(2, Math.round(n / 2) * 2), cell = h => G ? [ev(h * G.A), h] : [h * 3 / 4, h];   // Gate bật: ô theo tỉ lệ Gate
    const sizes = { s: [...cell(400), "Nhỏ"], m: [...cell(600), "Vừa"], l: [...cell(800), "Lớn"] }; let sz = saved.size && sizes[saved.size] ? saved.size : "m";
    const back = () => viewSet(view0);
'''),
    (r'''    const prev = () => {   // xem thử khoảng cách ngay trên viewport (CAM() đầu tiên đã chọn)
      const k = order.find(x => on.has(x)) || wasCam; setCam(k); if (dist !== 1) { const t = orbit.target; CAM().position.sub(t).multiplyScalar(dist).add(t); CAM().lookAt(t); }
''',
     r'''    const prev = () => {   // xem thử ngay trên viewport: CAM() đầu tiên đã chọn ("Đang xem" = giữ nguyên góc của người dùng)
      const k = order.find(x => on.has(x)); if (!k || k === "view") return back(); setCam(k); if (dist !== 1) camDolly(dist);
'''),
    (r'''      cams.innerHTML = order.map(k => `<label style="display:flex;gap:6px;align-items:center;padding:6px 8px;border:1px solid var(--line,#2c3441);border-radius:8px;cursor:pointer;${on.has(k) ? "background:color-mix(in srgb,var(--accent,#2fb67d) 18%,transparent)" : ""}"><input type="checkbox" data-k="${k}" ${on.has(k) ? "checked" : ""}> ${CAMS[k].label}</label>`).join("");
''',
     r'''      cams.innerHTML = order.map(k => `<label style="display:flex;gap:6px;align-items:center;padding:6px 8px;border:1px solid var(--line,#2c3441);border-radius:8px;cursor:pointer;${on.has(k) ? "background:color-mix(in srgb,var(--accent,#2fb67d) 18%,transparent)" : ""}"><input type="checkbox" data-k="${k}" ${on.has(k) ? "checked" : ""}> ${pbLabel(k)}${k === "view" ? ' <small style="color:var(--muted,#8d97a8)">(góc viewport' + (G ? ", khung Gate" : "") + ")</small>" : ""}</label>`).join("");
'''),
    (r'''      const [w, h] = sizes[sz], n = on.size; info.textContent = n ? "Video " + (w * n) + "×" + h + " · " + (P.frames || 1) + " frame · " + (P.fps || 30) + " fps" : "Chọn ít nhất một CAM().";
''',
     r'''      const [w, h] = sizes[sz], n = on.size; info.textContent = n ? "Video " + (w * n) + "×" + h + " · " + (P.frames || 1) + " frame · " + (P.fps || 30) + " fps" + (on.has("view") ? (G ? " · ô theo Gate" : " · bật Gate để quay đúng khung") : "") : "Chọn ít nhất một CAM().";
'''),
    (r'''      else if (e.target.closest("#pbNo") || e.target === ov) { ov.remove(); setCam(wasCam); res(null); }
''',
     r'''      else if (e.target.closest("#pbNo") || e.target === ov) { ov.remove(); back(); res(null); }
'''),
    (r'''        ov.remove(); setCam(wasCam); res({ cams: list, cw: sizes[sz][0], ch: sizes[sz][1], dist });
''',
     r'''        ov.remove(); back(); res({ cams: list, cw: sizes[sz][0], ch: sizes[sz][1], dist, view: view0 });
'''),
    (r'''  canUndo: () => undoStack.length > 0, openPose, reopen: () => openPose(P), isLive: () => !!LIVE, stopPlay, frameAll: typeof frameAll === "function" ? frameAll : null, setCam, NAMES, JOINTS: () => JOINTS,
  sampleBones, ai: AI };
''',
     r'''  canUndo: () => undoStack.length > 0, openPose, reopen: () => openPose(P),
  // đổi sang anim khác không tải lại trang: lưu key đang dở, đổi kho, thay danh sách phiên bản, mở phiên bản đầu
  swapClip: async (list, ns) => { if (keysMode() && (dirtyKeys.size || animDirty)) { clearTimeout(flushT); await flush(); } stopPlay();
    if (ns && db && db.setNS) await db.setNS(ns); POSES.splice(0, POSES.length, ...list); await openPose(POSES[0]); renderPoses(); }, isLive: () => !!LIVE, stopPlay, frameAll: typeof frameAll === "function" ? frameAll : null, setCam, NAMES, JOINTS: () => JOINTS,
  sampleBones, ai: AI, renderStrip: () => { if (model) renderStrip(); } };
'''),
]
