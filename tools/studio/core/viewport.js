// AI Anim Studio — viewport chung: một renderer, 1 hoặc 4 khung (persp / top / front / side), điều hướng kiểu Maya,
// gizmo TransformControls dùng chung, chọn bằng click / khung kéo, chế độ cảm ứng.
// Cảnh tính bằng mét (như glTF, Unity). Module làm việc bằng cm (Mesh, Rig) đặt đồ vào V.cm (nhóm scale 0,01).
(function () {
  const V = ST.view = {};
  const vp = ST.$("vp"), cv = ST.$("cv"), panesEl = ST.$("panes"), marq = ST.$("marq");
  const R = new THREE.WebGLRenderer({ canvas: cv, antialias: true });
  R.setPixelRatio(Math.min(devicePixelRatio, 2)); R.setScissorTest(true);
  const scene = V.scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x556070, 0.95));
  const dl = new THREE.DirectionalLight(0xffffff, 0.6); dl.position.set(2, 4, 5); scene.add(dl);
  const grid = V.grid = new THREE.GridHelper(4, 40, 0x6b7380, 0x9aa1ad); grid.material.transparent = true; grid.material.opacity = 0.4; scene.add(grid);
  V.world = new THREE.Group(); scene.add(V.world);
  V.cm = new THREE.Group(); V.cm.scale.setScalar(0.01); V.world.add(V.cm); V.cm.updateMatrixWorld(true);
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

  // ---- khung nhìn
  const AX = { top: [0, 1, 0], front: [0, 0, 1], side: [1, 0, 0] };
  function mkPane(id, label) {
    const p = { id, label, target: new THREE.Vector3(0, 0.9, 0), rect: { x: 0, y: 0, w: 1, h: 1 } };
    if (id === "persp") { p.cam = new THREE.PerspectiveCamera(30, 1, 0.01, 200); p.cam.position.set(1.6, 1.5, 4.6); }
    else {
      p.cam = new THREE.OrthographicCamera(-1, 1, 1, -1, -100, 100);
      if (id === "top") p.cam.up.set(0, 0, -1);
      p.cam.position.copy(p.target).add(new THREE.Vector3(...AX[id]).multiplyScalar(20));
    }
    p.cam.lookAt(p.target);
    const el = document.createElement("div"); el.className = "pane"; el.innerHTML = `<span class="pl">${label}</span>`; panesEl.appendChild(el); p.el = el;
    return p;
  }
  const P = V.panes = { top: mkPane("top", "top"), persp: mkPane("persp", "persp"), front: mkPane("front", "front"), side: mkPane("side", "side · phải") };
  V.layout = ST.pref.get("layout", "1"); V.single = ST.pref.get("single", "persp");
  V.visible = () => V.layout === "4" ? [P.top, P.persp, P.front, P.side] : [P[V.single] || P.persp];
  function layoutPanes() {
    const r = vp.getBoundingClientRect(), W = r.width, H = r.height;
    Object.values(P).forEach(p => { p.on = false; p.el.style.display = "none"; });
    const set = (p, x, y, w, h) => { p.on = true; p.rect = { x, y, w, h }; Object.assign(p.el.style, { display: "block", left: x + "px", top: y + "px", width: w + "px", height: h + "px" }); };
    if (V.layout === "4") { const w2 = Math.floor(W / 2), h2 = Math.floor(H / 2); set(P.top, 0, 0, w2, h2); set(P.persp, w2, 0, W - w2, h2); set(P.front, 0, h2, w2, H - h2); set(P.side, w2, h2, W - w2, H - h2); }
    else set(P[V.single] || P.persp, 0, 0, W, H);
    if (!V.active || !V.active.on) activate(V.visible()[V.layout === "4" ? 1 : 0]);
    Object.values(P).forEach(p => p.el.classList.toggle("act", V.layout === "4" && p === V.active));
  }
  V.paneAt = (x, y) => { const r = vp.getBoundingClientRect(), lx = x - r.left, ly = y - r.top; return V.visible().find(p => lx >= p.rect.x && lx < p.rect.x + p.rect.w && ly >= p.rect.y && ly < p.rect.y + p.rect.h) || null; };
  V.ndc = (x, y, p) => { const r = vp.getBoundingClientRect(); p = p || V.active; return new THREE.Vector2(((x - r.left - p.rect.x) / p.rect.w) * 2 - 1, -((y - r.top - p.rect.y) / p.rect.h) * 2 + 1); };
  const rc = new THREE.Raycaster();
  V.raycaster = (x, y, p) => { p = p || V.active; rc.setFromCamera(V.ndc(x, y, p), p.cam); return rc; };
  V.toScreen = (w, p) => { p = p || V.active; const v = w.clone().project(p.cam), r = vp.getBoundingClientRect(); return { x: r.left + p.rect.x + (v.x + 1) / 2 * p.rect.w, y: r.top + p.rect.y + (1 - v.y) / 2 * p.rect.h, z: v.z }; };
  V.worldPerPixel = (w, p) => { p = p || V.active; const c = p.cam; return c.isPerspectiveCamera ? 2 * c.position.distanceTo(w) * Math.tan(c.fov * Math.PI / 360) / p.rect.h : (c.top - c.bottom) / c.zoom / p.rect.h; };

  // ---- điều hướng: OrbitControls dùng chung, đổi camera theo khung dưới chuột
  const orbit = V.orbit = new THREE.OrbitControls(P.persp.cam, cv);
  orbit.enableDamping = false; orbit.screenSpacePanning = true;
  const MB = THREE.MOUSE, NONE = -1;
  orbit.mouseButtons = { LEFT: NONE, MIDDLE: MB.PAN, RIGHT: MB.ROTATE };
  // TransformControls gắn vào một div ẩn: nó tự tính chuột theo cả canvas (sai khi chia 4 khung), nên viewport tự gọi
  // tc.pointerHover / pointerDown / pointerMove / pointerUp với toạ độ theo khung đang dùng.
  const tc = new THREE.TransformControls(P.persp.cam, document.createElement("div")); tc.setSize(0.85); tc.setSpace("world"); scene.add(tc);
  V.gzEnabled = true;
  function activate(p) {
    if (!p || V.active === p) return;
    V.active = p; orbit.object = p.cam; orbit.target = p.target; orbit.enableRotate = !!p.cam.isPerspectiveCamera; tc.camera = p.cam;
    Object.values(P).forEach(q => q.el.classList.toggle("act", V.layout === "4" && q === p));
  }
  V.activate = activate;
  V.setLayout = (lay, single) => {
    V.layout = lay; if (single) V.single = single; ST.pref.set("layout", V.layout); ST.pref.set("single", V.single);
    V.active = null; layoutPanes(); ST.refresh();
  };
  V.toggle4 = () => { if (V.layout === "4") { const p = V.hover || V.active; V.setLayout("1", p ? p.id : "persp"); } else V.setLayout("4"); };

  // ---- nhìn khung bao (Box3 thế giới) trong một khung hoặc mọi khung
  V.frame = (box, panes, keepDir) => {
    if (!box || box.isEmpty()) return;
    const c = box.getCenter(new THREE.Vector3()), s = box.getSize(new THREE.Vector3());
    (panes || [V.active]).forEach(p => {
      const cam = p.cam, asp = p.rect.w / Math.max(1, p.rect.h);
      if (cam.isPerspectiveCamera) {
        const d = Math.max(s.y, s.x / asp, 0.3) / Math.tan(cam.fov * Math.PI / 360) * 0.62 + s.z;
        const dir = keepDir ? cam.position.clone().sub(p.target).normalize() : new THREE.Vector3(0.33, 0.1, 1).normalize();
        p.target.copy(c); cam.position.copy(c).addScaledVector(dir, d); cam.near = Math.max(0.005, d / 200); cam.far = d * 60;
      } else {
        const a = new THREE.Vector3(...AX[p.id]), w = p.id === "side" ? s.z : s.x, h = p.id === "top" ? s.z : s.y;
        p.target.copy(c); cam.position.copy(c).addScaledVector(a, 20); cam.zoom = 2 / (Math.max(h, w / asp, 0.05) * 1.2);
      }
      cam.lookAt(p.target); cam.updateProjectionMatrix();
    });
    orbit.update();
  };
  V.frameAll = () => { const m = ST.mod(); const b = m.bounds ? m.bounds(false) : null; V.frame(b, V.visible()); };
  V.frameSel = () => { const m = ST.mod(); const b = (ST.ws !== "rig" && ST.mods.skel && ST.mods.skel.bounds()) || (m.bounds && m.bounds(true)) || (m.bounds && m.bounds(false)); V.frame(b, [V.active], true); };

  // ---- vẽ
  function resize() { const r = vp.getBoundingClientRect(); R.setSize(r.width, r.height, false); layoutPanes(); }
  addEventListener("resize", resize); new ResizeObserver(resize).observe(vp);
  // cảnh phụ của workspace (vd lõi Pose: cảnh + lớp phủ riêng, mét): vẽ trước / sau cảnh chung trong cùng khung
  V.extra = null;   // { scene, overlay }
  const frameCbs = [];
  V.onFrame = f => frameCbs.push(f);
  function drawAll() {
    const r = vp.getBoundingClientRect(), H = r.height; if (r.width < 2 || H < 2) return;
    R.setScissorTest(true);
    R.setClearColor(css("--view") || "#15191f");
    const X = V.extra;
    for (const p of V.visible()) {
      const { x, y, w, h } = p.rect, asp = w / Math.max(1, h), cam = p.cam;
      if (cam.isPerspectiveCamera) { if (cam.aspect !== asp) { cam.aspect = asp; cam.updateProjectionMatrix(); } }
      else if (cam.right !== asp) { cam.left = -asp; cam.right = asp; cam.top = 1; cam.bottom = -1; cam.updateProjectionMatrix(); }
      grid.visible = V.showGrid && !X;
      R.setViewport(x, H - y - h, w, h); R.setScissor(x, H - y - h, w, h);
      if (tc.camera !== cam) tc.camera = cam;
      if (X) { R.autoClear = false; R.clear(); R.render(X.scene, cam); R.render(scene, cam); R.clearDepth(); R.render(X.overlay, cam); R.autoClear = true; }
      else R.render(scene, cam);
    }
    if (V.active && tc.camera !== V.active.cam) tc.camera = V.active.cam;
  }
  V.renderNow = drawAll;
  (function frame(now) {
    requestAnimationFrame(frame);
    const r = vp.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return;
    orbit.update(); frameCbs.forEach(f => { try { f(now); } catch (e) { console.error(e); } }); ST.emit("prerender");
    drawAll();
  })();
  // renderer cho mã chụp ảnh của lõi (setSize tắt cắt khung, vẽ cả canvas); V.resize trả lại cỡ viewport
  V.renderer = new Proxy(R, {
    get(t, k) { if (k === "setSize") return (w, h, u) => { t.setScissorTest(false); t.setSize(w, h, u); t.setViewport(0, 0, w, h); }; const v = t[k]; return typeof v === "function" ? v.bind(t) : v; },
    set(t, k, v) { t[k] = v; return true; },
  });
  V.resize = () => resize();
  V.showGrid = ST.pref.get("grid", true);

  // ---- gizmo dùng chung: module đặt tâm (toạ độ của parent), nhận ma trận chênh lệch M trong toạ độ parent
  const pivot = new THREE.Object3D();
  const G = V.gizmo = { tc, pivot, dragging: false, owner: null };
  G.place = (center, parent, mode) => {
    tc.detach(); if (!center) return;
    if (pivot.parent !== parent) parent.add(pivot);
    pivot.position.copy(center); pivot.rotation.set(0, 0, 0); pivot.scale.set(1, 1, 1); pivot.updateMatrixWorld(true);
    tc.attach(pivot); tc.setMode(mode);
  };
  G.detach = () => tc.detach();
  let inv0 = null;
  tc.addEventListener("mouseDown", () => { if (!tc.object) return; G.owner = ST.mod(); pivot.updateMatrix(); inv0 = pivot.matrix.clone().invert(); G.dragging = true; G.owner.gzStart && G.owner.gzStart(); });
  tc.addEventListener("objectChange", () => { if (!G.dragging || !inv0) return; pivot.updateMatrix(); const M = pivot.matrix.clone().multiply(inv0); G.owner.gzChange && G.owner.gzChange(M); });
  tc.addEventListener("mouseUp", () => { if (!G.dragging) return; G.dragging = false; G.justDragged = true; inv0 = null; G.owner && G.owner.gzEnd && G.owner.gzEnd(); });
  tc.addEventListener("dragging-changed", e => { orbit.enabled = !e.value; });

  // ---- chế độ cảm ứng (iPad / điện thoại)
  const TM = V.TM = { on: false, mode: "orbit", add: false };
  ST.addSel = e => (e && e.shiftKey) || TM.add;
  const bar = ST.$("tmBar");
  bar.innerHTML = `<button data-m="orbit" title="Xoay / zoom camera (1 ngón xoay, 2 ngón zoom + kéo)" aria-label="Xoay camera">${ST.ic("orbit")}</button><button data-m="sel" title="Chạm để chọn, kéo gizmo để chỉnh" aria-label="Chọn">${ST.ic("sel")}</button><button data-m="box" title="Kéo khung chọn nhiều" aria-label="Chọn khung">${ST.ic("box")}</button><button data-add="1" title="Thêm vào vùng chọn (như giữ Shift)" aria-label="Thêm vào chọn">${ST.ic("plus")}</button>`;
  V.applyTM = () => {
    document.body.classList.toggle("tm", TM.on);
    bar.querySelectorAll("button[data-m]").forEach(b => b.classList.toggle("on", b.dataset.m === TM.mode)); bar.querySelector("[data-add]").classList.toggle("on", TM.add);
    orbit.touches = { ONE: TM.on && TM.mode !== "orbit" ? NONE : THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_PAN };
    tc.setSize(TM.on ? 1.3 : 0.85); V.gzEnabled = !(TM.on && TM.mode === "orbit");
    setTimeout(resize, 30);
  };
  bar.addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; if (b.dataset.m) TM.mode = b.dataset.m; else TM.add = !TM.add; V.applyTM(); });
  { const s = ST.pref.get("touch", null); TM.on = s === null ? matchMedia("(pointer:coarse)").matches : !!s; V.applyTM(); }
  V.setTouch = on => { TM.on = on; ST.pref.set("touch", on); V.applyTM(); ST.refresh(); };

  // ---- chuột: Alt+trái xoay, Alt+phải dolly, giữa pan, phải xoay; trái = chọn / gizmo / khung kéo (module quyết định)
  let down = null, boxing = false, gzPane = null;
  const ptr = (e, p, button) => { const n = V.ndc(e.clientX, e.clientY, p); return { x: n.x, y: n.y, button }; };
  cv.addEventListener("pointerdown", e => {
    const p = V.paneAt(e.clientX, e.clientY); if (p) activate(p);
    if (e.pointerType === "mouse") orbit.mouseButtons = { LEFT: e.altKey ? MB.ROTATE : NONE, MIDDLE: MB.PAN, RIGHT: e.altKey ? MB.DOLLY : MB.ROTATE };
    else orbit.touches = { ONE: TM.on && TM.mode === "orbit" ? THREE.TOUCH.ROTATE : (TM.on ? NONE : THREE.TOUCH.ROTATE), TWO: THREE.TOUCH.DOLLY_PAN };
    const orbitHere = e.altKey || e.button !== 0 || (TM.on && TM.mode === "orbit" && e.pointerType !== "mouse");
    down = null; boxing = false; G.justDragged = false;
    if (orbitHere) return;
    if (tc.object && V.gzEnabled && V.active) {   // gizmo trước: trúng trục thì kéo gizmo
      tc.camera = V.active.cam; tc.updateMatrixWorld(); tc.pointerHover(ptr(e, V.active, 0));
      if (tc.axis) { gzPane = V.active; tc.pointerDown(ptr(e, gzPane, 0)); cv.setPointerCapture(e.pointerId); e.stopImmediatePropagation(); e.preventDefault(); return; }
    }
    const m = ST.mod();
    if (m.pointerDown && m.pointerDown(e, V.active)) { e.stopImmediatePropagation(); e.preventDefault(); return; }
    down = { x: e.clientX, y: e.clientY, p: V.active };
    if (!tc.axis && m.box && (!m.canBox || m.canBox()) && (!TM.on || TM.mode === "box" || e.pointerType === "mouse")) boxing = true;
  }, { capture: true });
  cv.addEventListener("pointermove", e => {
    if (gzPane) { tc.pointerMove(ptr(e, gzPane, -1)); return; }
    if (!e.buttons) {
      const p = V.paneAt(e.clientX, e.clientY); V.hover = p; if (p && !G.dragging) activate(p);
      if (p && tc.object && V.gzEnabled) { tc.camera = p.cam; tc.pointerHover(ptr(e, p, 0)); }
    }
    if (!boxing || !down || Math.hypot(e.clientX - down.x, e.clientY - down.y) < 5) return;
    const r = vp.getBoundingClientRect();
    Object.assign(marq.style, { display: "block", left: Math.min(down.x, e.clientX) - r.left + "px", top: Math.min(down.y, e.clientY) - r.top + "px", width: Math.abs(e.clientX - down.x) + "px", height: Math.abs(e.clientY - down.y) + "px" });
  }, { capture: true });
  addEventListener("pointerup", e => {
    if (gzPane) { const p = gzPane; gzPane = null; tc.pointerUp(ptr(e, p, 0)); G.justDragged = false; return; }
    if (!down) return; const d0 = down, was = boxing, moved = Math.hypot(e.clientX - d0.x, e.clientY - d0.y) > 5;
    down = null; boxing = false; marq.style.display = "none";
    if (G.dragging || G.justDragged) { G.justDragged = false; return; }
    if (e.target !== cv) return;
    const m = ST.mod();
    if (was && moved) { m.box && m.box(d0.x, d0.y, e.clientX, e.clientY, e, d0.p); ST.refresh(); return; }
    if (moved || e.altKey || tc.axis) return;
    if (TM.on && TM.mode === "orbit" && e.pointerType !== "mouse") return;
    m.pick && m.pick(e.clientX, e.clientY, e, d0.p); ST.refresh();
  });
  cv.addEventListener("contextmenu", e => e.preventDefault());
  cv.addEventListener("pointerleave", () => { V.hover = null; });

  ST.on("init", () => { resize(); });
})();
