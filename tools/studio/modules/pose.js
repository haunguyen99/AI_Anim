// AI Anim Studio — module Pose (S4, lớp Anim): lõi Pose Lab (modules/pose_engine.js, sinh bằng port_pose.py) chạy trong viewport chung.
// Giao diện Pose Lab dựng lại từ HTML gốc rồi đặt vào vỏ Studio: thanh công cụ → shelf, Khớp / Vật lý / Ghi chú / Phiên bản → tab dock,
// timeline (key, lane, Timing, transport) → vùng timeline, HUD / camera / ref / vẽ ghi chú → lớp phủ viewport. Một anim mỗi lần
// (đổi anim = tải lại với ?clip=…), lưu cùng kho với Pose Lab cũ (<tiêu đề trang>_pose_lab).
// W1: dùng được ở mọi workspace. Lớp Anim hiện = vẽ cảnh Pose + chạy khung hình; focus Pose = nhận chuột / phím / gizmo.
// Khối giao diện (data-park) khi không gắn vào vùng nào thì nằm trong #poseStash: lõi tìm phần tử theo id nên chúng phải luôn trong trang.
(function () {
  const V = ST.view, esc = ST.esc, ic = ST.ic, $ = ST.$;
  const M = ST.mods.pose = { id: "pose", ownKeys: true };
  let eng = null, state = "none", err = "", clipInfo = null, clips = null, parts = null, scenes = null, open = null, stash = null;
  const q = new URLSearchParams(location.search);
  const cvEl = $("cv");

  // ---- anim cần mở: ?clip, anim của Home, lần trước, hoặc anim đầu tiên của nhân vật
  async function loadClips() {
    if (clips) return clips;
    try { clips = await (await fetch("/api/poses" + (ST.char ? "?char=" + encodeURIComponent(ST.char.id) : ""))).json(); } catch (e) { clips = []; }
    return clips;
  }
  const prefKey = () => "pose:clip:" + (ST.char ? ST.char.id : "_");
  async function pickClip() {
    const L = await loadClips(), want = q.get("clip") || ST.clip || ST.pref.get(prefKey(), null);
    return (L.find(c => c.id === want) || L[0] || {}).id || null;
  }
  const goClip = id => { const u = new URL(location.href); u.searchParams.set("clip", id); if (ST.ws) u.searchParams.set("ws", ST.ws); ST.pref.set(prefKey(), id); location.href = u; };

  // ---- dựng giao diện Pose Lab, chia khối cho các vùng của Studio
  function buildDom() {
    stash = document.createElement("div"); stash.id = "poseStash"; stash.hidden = true; document.body.appendChild(stash);
    const w = document.createElement("div"); w.innerHTML = ST.POSE_HTML;
    const wrap = (cls, node, inner) => { const d = document.createElement("div"); d.className = "pz " + cls; d.dataset.park = "poseStash"; if (inner) { const i = document.createElement("div"); i.className = inner; i.appendChild(node); d.appendChild(i); } else d.appendChild(node); stash.appendChild(d); return d; };
    const viewer = w.querySelector("#viewer"), tm = viewer.querySelector("#p_tmBar"); if (tm) tm.remove();
    const side = w.querySelector("aside.side"), first = side.firstElementChild, phys = side.querySelector("#physBox");
    const notes = document.createElement("div"); [...side.children].slice(1).forEach(c => notes.appendChild(c));
    phys.open = true; phys.hidden = false;
    parts = {
      shelf: wrap("pzshelf", w.querySelector("header.top")),
      overlay: wrap("pzov", viewer),
      joint: wrap("pzdock", first, "side"),
      phys: wrap("pzdock", phys, "side"),
      notes: wrap("pzdock", notes, "side"),
      versions: wrap("pzdock", w.querySelector("nav.list")),
      timeline: wrap("pztl", w.querySelector("footer.timeline")),
      viewer,
    };
    const rest = w.querySelector(".app"); if (rest) { rest.hidden = true; stash.appendChild(rest); }   // phần còn lại (giữ id cho lõi)
    // chọn anim ở đầu tab Phiên bản
    const pick = document.createElement("div"); pick.className = "row"; pick.style.cssText = "padding:6px 10px";
    pick.innerHTML = `<label class="sub">Anim</label><select id="poseClip" style="flex:1"></select><button id="poseOld" title="Mở Pose Lab cũ của anim này">${ic("ext")}</button>`;
    parts.versions.prepend(pick);
  }
  function fillPicker() {
    const s = $("poseClip"); if (!s || !clips) return;
    s.innerHTML = clips.map(c => `<option value="${esc(c.id)}" ${clipInfo && c.id === clipInfo.id ? "selected" : ""}>${esc(c.name)} · ${c.versions} bản${ST.char ? "" : " · " + esc(c.character)}</option>`).join("");
    s.onchange = () => goClip(s.value);
    const o = $("poseOld"); if (o) o.onclick = () => clipInfo && window.open("/lab/pose/" + encodeURIComponent(clipInfo.id), "_blank");
  }

  // ---- host: những gì lõi Pose cần từ Studio
  // ---- W3a: model sống = nhân vật hiện tại (mesh đã sửa + khớp + skin của Rig), dựng bằng lõi Rig, cho phiên bản dạng key làm từ rig Studio.
  // Chọn theo phiên bản (doc studio/model của kho Pose, chung mọi máy): mặc định sống, trừ anim đã xuất (stage export) giữ model chụp.
  let choices = {}, liveSig = null, liveUrl = null, rigSaves = 0;
  const vkey = p => p.clip + "-" + p.version;
  const eligible = p => !!(ST.char && p && p.mode === "keys" && (p.model === "live" || /_rig_v\d+\.json$/.test(p.glb || "")));
  const modelOf = p => !eligible(p) ? "snap" : choices[vkey(p)] || (clipInfo && clipInfo.stage === "export" ? "snap" : "live");
  const sigNow = () => (ST.mods.mesh.ver ? ST.mods.mesh.ver() : 0) + ":" + rigSaves;
  ST.on("rig:skeleton", () => { rigSaves++; }); ST.on("rig:skin", () => { rigSaves++; });
  const modelStore = () => ST.store(q.get("ns") ? q.get("ns") + "_pose" : clipInfo.ns);
  async function liveModel(p) {
    if (modelOf(p) !== "live") return null;
    try {
      const R = ST.mods.rig; if (!(await R.whenReady())) throw new Error(R.loadMsg ? R.loadMsg() : "rig chưa nạp được");
      const g = ST.rigEng().buildGltf(); liveSig = sigNow();
      if (liveUrl) URL.revokeObjectURL(liveUrl);
      return (liveUrl = URL.createObjectURL(new Blob([JSON.stringify(g)], { type: "model/gltf+json" })));
    } catch (e) { ST.toast("Không dựng được model từ rig (" + (e.message || e) + "): dùng model chụp của phiên bản."); return null; }
  }
  // rig / mesh đã đổi từ lần dựng trước: dựng lại khi quay lại lớp Anim
  function refreshLive() { if (eng && eng.isLive() && liveSig !== sigNow()) { ST.toast("Rig / mesh đã đổi: dựng lại model của anim…"); eng.reopen(); } }

  function makeHost(ns) {
    const alive = () => ST.focus === "pose" && ST.layerOn.anim;   // chuột / phím / gizmo của lõi
    const paneRect = () => { const r = cvEl.getBoundingClientRect(), p = V.active.rect; return { left: r.left + p.x, top: r.top + p.y, width: p.w, height: p.h, right: r.left + p.x + p.w, bottom: r.top + p.y + p.h, x: r.left + p.x, y: r.top + p.y }; };
    const canvas = {
      getBoundingClientRect: paneRect,
      get clientWidth() { return V.active.rect.w; }, get clientHeight() { return V.active.rect.h; },
      get width() { return cvEl.width; }, get height() { return cvEl.height; },
      addEventListener: (t, f, o) => cvEl.addEventListener(t, e => { if (alive()) f(e); }, o),
      setPointerCapture: id => cvEl.setPointerCapture(id), style: cvEl.style,
    };
    return {
      canvas, viewer: parts.viewer, renderer: V.renderer, orbit: V.orbit, gizmo: V.gizmo.tc,
      cam: () => V.active.cam, alive, liveModel, setOrtho: on => V.setOrtho(on),
      panes: {   // nút [ ] của thanh Pose = lệnh Cửa sổ → Outliner / Dock phải của Studio
        toggle: k => ST.run(k === "list" ? "win.outliner" : "win.dock"),
        on: k => !document.body.classList.contains(k === "list" ? "noout" : "nodock"),
        onChange: f => new MutationObserver(f).observe(document.body, { attributes: true, attributeFilter: ["class"] }),
      },
      scenes: (s, o) => { scenes = { scene: s, overlay: o }; if (ST.layerOn.anim) V.extra = scenes; },
      resize: () => V.resize(), renderNow: () => V.renderNow(),
      onFrame: f => V.onFrame(now => { if (ST.layerOn.anim && parts && parts.overlay.isConnected) f(now); }),   // lớp hiện là chạy (phát anim cả khi đang sửa thứ khác)
      downloads: { save: async ({ filename, data }) => { const b = data instanceof Blob ? data : new Blob([data]), u = URL.createObjectURL(b), x = document.createElement("a"); x.href = u; x.download = filename; document.body.appendChild(x); x.click(); x.remove(); setTimeout(() => URL.revokeObjectURL(u), 4000); } },
      db: ST.poseDB(q.get("ns") ? q.get("ns") + "_pose" : ns),   // ?ns= để thử trên kho riêng
    };
  }

  async function ensure() {
    if (eng || state === "loading") return;
    state = "loading"; await ST.ready;
    const id = await pickClip();
    if (!id) { state = "noclip"; ST.refresh(); return; }
    ST.refresh();
    try {
      const r = await fetch("/api/poses/" + encodeURIComponent(id)); clipInfo = await r.json(); if (!r.ok) throw new Error(clipInfo.error || r.status);
      const POSES = new Function("return " + clipInfo.js)();
      try { choices = (await modelStore().get("studio/model")) || {}; } catch (e) { choices = {}; }
      const fix = o => { for (const k in o) { const v = o[k]; if (typeof v === "string" && /^(models|refs|fbx)\//.test(v)) o[k] = "/work/pose_lab/" + v; else if (v && typeof v === "object") fix(v); } };
      POSES.forEach(fix);
      ST.pref.set(prefKey(), id);
      if (!parts) buildDom();
      window.__rigSetup = null;   // bước 6 Vật lý của Rig (khớp điều khiển, giới hạn, collider, khối lượng): lõi Pose đọc thay CHAR_PHYS
      if (ST.char) try { window.__rigSetup = await ST.store(ST.rigNs()).get("rig/setup"); } catch (e) {}
      eng = ST.poseEngine(POSES, makeHost(clipInfo.ns)); ST.poseEng = () => eng; ST.poseScenes = () => scenes;   // lõi Pose cho script / Claude
      state = "ready"; fillPicker();
      if (!ST.char) { const e = $("empty"); if (e) e.hidden = true; ST.$("charName").textContent = clipInfo.name; }
      else ST.$("charName").textContent = ST.char.name + " · " + clipInfo.name;
      // công cụ chung của Studio (Q / W / E ở hộp công cụ) ↔ chế độ gizmo của lõi Pose, hai chiều
      ["mSel", "mMove", "mRot"].forEach((id, i) => { const b = $(id); if (b) b.addEventListener("click", () => { const t = ["sel", "move", "rot"][i]; if (ST.tool !== t) { ST.tool = t; ST.refresh(); } }); });
      applyLayer(ST.layerOn.anim); if (ST.focus === "pose") M.focusIn();
    } catch (e) { console.error(e); state = "error"; err = e.message || String(e); }
    ST.refresh();
  }

  // ---- lớp Anim (vẽ cảnh Pose + lớp phủ) và focus (chuột, gizmo)
  let encSaved = null, tcSaved = null;
  function applyLayer(on) {
    if (on) {
      if (encSaved === null) { encSaved = V.renderer.outputEncoding; V.renderer.outputEncoding = THREE.sRGBEncoding; }
      if (scenes) V.extra = scenes;
      if (parts) { $("vp").appendChild(parts.overlay); parts.overlay.hidden = false; }
    } else {
      V.extra = null; if (eng) eng.stopPlay();
      if (encSaved !== null) { V.renderer.outputEncoding = encSaved; encSaved = null; }
      if (parts) { parts.overlay.hidden = true; stash.appendChild(parts.overlay); }
      if (ST.focus === "pose") V.gizmo.detach();
    }
  }
  M.layer = on => { applyLayer(on); if (on && !eng) ensure(); if (on) refreshLive(); ST.refresh(); };
  M.focusIn = () => {
    if (!eng) { ensure(); return; }
    refreshLive();
    const tc = V.gizmo.tc; if (!tcSaved) tcSaved = { space: tc.space, size: tc.size };
    V.gizmo.detach(); tc.setSpace($("mSpace") && /world/.test($("mSpace").textContent) ? "world" : "local");
    const md = POSE_MODE[ST.tool]; if (md && md !== eng.get().mode) eng.setMode(md);   // giữ công cụ đang chọn khi chuyển sang Pose
    const g = eng.get(); if (g.sel) eng.setSelection([...g.selSet], g.sel);   // gắn lại gizmo vào khớp đang chọn
    ST.refresh();
  };
  const POSE_MODE = { sel: "select", move: "translate", rot: "rotate" };
  addEventListener("keydown", e => {   // Q / W / E trong lõi Pose → đánh dấu đúng công cụ ở hộp công cụ Studio
    if (ST.focus !== "pose" || !eng || e.ctrlKey || e.metaKey || e.altKey || /INPUT|TEXTAREA|SELECT/.test((e.target || {}).tagName || "")) return;
    const t = { q: "sel", w: "move", e: "rot" }[e.key.toLowerCase()]; if (t && ST.tool !== t) setTimeout(() => { ST.tool = t; ST.refresh(); }, 0);
  });
  ST.on("tool", t => { if (ST.focus !== "pose" || !eng || !eng.get().model) return; if (t === "scl") { ST.toast("Rig không cho scale khớp: dùng W (dời) hoặc E (xoay)."); return; } const md = POSE_MODE[t]; if (md && md !== eng.get().mode) eng.setMode(md); });
  M.focusOut = () => {
    const tc = V.gizmo.tc; tc.detach();
    if (tcSaved) { tc.setSpace(tcSaved.space || "world"); tc.setSize(tcSaved.size || 0.85); tcSaved = null; }
  };
  M.loaded = () => !!eng && !!eng.get().model;
  M.clipList = async () => (await loadClips()).map(c => ({ id: c.id, name: c.name, character: c.character, stage: c.stage, versions: c.versions, open: !!(clipInfo && c.id === clipInfo.id) }));
  M.goClip = id => goClip(id);   // tải lại trang với ?clip=…
  // W3c: khớp dùng chung (khớp có chấm chọn của model anim)
  M.curJoint = () => eng ? eng.get().sel : null;
  M.hasJoint = n => !!(eng && eng.get().markers[n]);
  M.selectJoint = async n => { if (!(await M.whenReady())) return; if (eng.get().markers[n]) eng.select(n); };
  // chờ lõi nạp xong (cầu nối AI gọi lệnh ngay sau khi focus)
  M.whenReady = async () => {
    ensure(); const busy = () => ["none", "loading"].includes(state) || (state === "ready" && !(eng && eng.get().model));
    for (let i = 0; i < 400 && busy(); i++) await new Promise(r => setTimeout(r, 100));
    return state === "ready";
  };
  M.loadMsg = () => ({ loading: "Đang nạp anim…", noclip: "Chưa có anim: tạo ở Home hoặc /new_clip", error: "Lỗi nạp anim: " + err }[state] || "Chưa nạp: bấm mắt để nạp");
  M.nodeLabel = () => "Anim" + (clipInfo ? " · " + clipInfo.name : "");
  M.shelfMsg = () => "Pose: " + M.loadMsg();
  // click trúng khớp (chấm) hoặc model của anim → viewport chuyển focus sang Pose
  M.hit = (x, y, p) => {
    if (!eng || !ST.layerOn.anim) return false;
    const g = eng.get(); if (!g.model) return false;
    if (PR() && PR().hit(x, y, p)) return true;
    const w = new THREE.Vector3(), R = V.TM && V.TM.on ? 26 : 12;
    if (Object.values(g.markers).some(m => { if (!m.visible) return false; m.getWorldPosition(w); const s = V.toScreen(w, p); return s.z < 1 && Math.hypot(s.x - x, s.y - y) < R; })) return true;
    return V.raycaster(x, y, p).intersectObject(g.model, true).length > 0;
  };

  // ---- vùng giao diện
  const msg = html => { const d = document.createElement("div"); d.className = "note"; d.style.padding = "10px 12px"; d.innerHTML = html; return d; };
  M.shelfNode = () => parts && eng ? parts.shelf : null;
  M.timelineNode = () => parts && eng ? parts.timeline : msg('<span class="sub">Timeline</span>');
  M.panelNode = t => {
    if (state === "none") setTimeout(ensure, 0);   // panel Pose mở ở workspace nào cũng nạp anim (lớp vẫn ẩn nếu đang tắt)
    if (state === "loading" || state === "none") return msg("Đang nạp anim…");
    if (state === "error") return msg(`<span class="s-bad">Không nạp được anim: ${esc(err)}</span>`);
    if (state === "noclip") return msg(ST.char ? esc(ST.char.name) + " chưa có anim nào trong Pose Lab. Tạo anim ở Home (/home) hoặc gõ /new_clip." : "Chưa có anim nào trong Pose Lab.");
    if (t === "phys" && $("physBox") && $("physBox").hidden) return msg("Vật lý dùng cho phiên bản dạng key (làm trên trang). Phiên bản này là anim nướng sẵn: mở phiên bản key ở tab Phiên bản.");
    if (t === "feedback") return feedbackNode();
    return { joint: parts.joint, phys: parts.phys, notes: parts.notes, versions: parts.versions }[t] || parts.joint;
  };
  // ---- tab "Góp ý cho AI" (user 2026-10-28: gộp "Ghi chú vẽ" + "Điều chỉnh gửi AI"): ghi chú vẽ trên, điều chỉnh key dưới,
  // một nút gửi cả hai. Khối ghi chú vẽ do module notes vẽ (HTML), khối điều chỉnh là DOM của lõi Pose (parts.notes).
  let fb = null;
  function feedbackNode() {
    const N = ST.mods.notes;
    if (!fb) {
      fb = document.createElement("div"); fb.className = "fbwrap"; fb.dataset.park = "poseStash";
      fb.innerHTML = `<section class="fbsec"><h3>Ghi chú vẽ</h3><div class="fbnotes" id="fbNotes"></div></section>
        <section class="fbsec"><h3>Điều chỉnh key</h3><div id="fbAdj"></div></section>
        <div class="fbfoot dockfoot"><div class="pz pzdock" id="fbCompose"></div>
          <div class="fbtop"><button class="on" id="fbSendAll">${ic("send")} Gửi tất cả cho AI</button><span class="sub" id="fbCount"></span></div></div>`;   // chân panel ghim đáy (user 2026-10-29): khối soạn điều chỉnh + nút gửi
    }
    const notesBox = fb.querySelector("#fbNotes"), adj = fb.querySelector("#fbAdj");
    notesBox.innerHTML = N && N.panel ? N.panel() : '<p class="sub" style="padding:0 10px">Không có module ghi chú vẽ.</p>';
    if (N && N.panelMounted) setTimeout(() => N.panelMounted(), 0);   // ảnh nhỏ của ghi chú
    if (adj.firstChild !== parts.notes) adj.replaceChildren(parts.notes);
    const cp = parts.notes.querySelector(".compose"), cpBox = fb.querySelector("#fbCompose");   // ô ghi chú + Lưu / Gửi + vòng review: xuống chân panel, danh sách cuộn phía trên
    if (cp && cp.parentElement !== cpBox) cpBox.appendChild(cp);
    const sa = fb.querySelector("#fbSendAll"), cpRow = cp && cp.querySelector(".row");   // Lưu + Gửi tất cả cùng một hàng (user 2026-10-29 "gộp vào 1 dòng cho gọn")
    if (cpRow && sa.parentElement !== cpRow) cpRow.appendChild(sa);
    const nAdj = $("adjCount") ? $("adjCount").textContent.trim() : "", hs = notesBox.querySelector(".nhead .sub");   // số điều chỉnh ghép vào hàng đầu
    if (hs && nAdj) hs.textContent += " · " + nAdj + " điều chỉnh";
    const nOpen = N && N.unsentCount ? N.unsentCount() : 0, aiBtn = $("aiSend"), canAdj = !!(aiBtn && !aiBtn.disabled);
    sa.disabled = !nOpen && !canAdj;
    fb.querySelector("#fbCount").textContent = (nOpen ? nOpen + " ghi chú vẽ" : "") + (nOpen && canAdj ? " + " : "") + (canAdj ? "điều chỉnh key" : "") + (nOpen || canAdj ? " chờ gửi" : "Chưa có gì để gửi");
    sa.title = fb.querySelector("#fbCount").textContent;   // dòng đếm thu vào tooltip của nút
    return fb;
  }
  async function sendAll() {
    const N = ST.mods.notes, aiBtn = $("aiSend");
    if (N && N.sendAll) await N.sendAll();
    if (aiBtn && !aiBtn.disabled) aiBtn.click();
    ST.refresh();
  }
  M.panel_click = (e, sub) => {
    if (sub !== "feedback") return;
    if (e.target.closest("#fbSendAll")) return sendAll();
    if (e.target.closest("#fbNotes") && ST.mods.notes && ST.mods.notes.panel_click) return ST.mods.notes.panel_click(e);
  };
  M.info = () => { if (!eng) return "Pose · " + ({ loading: "đang nạp", noclip: "chưa có anim", error: "lỗi" }[state] || ""); const g = eng.get(); return (clipInfo ? clipInfo.name : "") + " · " + (g.P ? g.P.version : "") + (eng.isLive() ? " · nhân vật hiện tại" : "") + " · F" + g.frame + "/" + (g.P ? g.P.frames : 1) + (g.sel ? " · " + g.sel : ""); };
  M.frameAll = () => { if (!eng || !eng.frameAll || !eng.get().model || !V.active.cam.isPerspectiveCamera) return false; eng.frameAll(); return true; };   // khung phối cảnh theo lõi Pose; khung trực giao dùng bounds
  // vật thể phụ (modules/props.js) đang chọn: Hoàn tác đi vào vật thể trước
  const PR = () => ST.mods.props;
  M.undo = () => eng && eng.undo();   // bấm #undo của lõi; modules/props.js bắt trước nếu sửa cuối là vật thể phụ
  M.canUndo = () => (PR() && PR().canUndo()) || (!!eng && eng.canUndo());
  M.store = () => clipInfo ? modelStore() : null;   // kho Pose của anim (vật thể phụ lưu ở props/<clip>-<version>)
  M.pointerDown = (e, p) => !!(PR() && ST.layerOn.anim && eng && eng.get().model && PR().pointerDown(e, p));
  M.bounds = selOnly => {   // vùng chọn: theo khớp; toàn bộ: lấy mẫu đỉnh mesh đã pose (đồ cầm tay như chùy vươn xa ngoài khớp)
    if (!eng || !eng.get().model) return null; const g = eng.get(), b = new THREE.Box3(), w = new THREE.Vector3();
    if (selOnly && g.selSet.size) { [...g.selSet].forEach(n => { const m = g.markers[n]; if (m) b.expandByPoint(m.getWorldPosition(w)); }); return b.isEmpty() ? null : b.expandByScalar(0.25); }
    g.model.updateMatrixWorld(true);
    g.model.traverse(o => {
      if (!o.isMesh || !o.visible) return;
      const pos = o.geometry.attributes.position; if (!pos) return;
      if (o.isSkinnedMesh) { const st = Math.max(1, Math.floor(pos.count / 2500)); for (let i = 0; i < pos.count; i += st) { w.fromBufferAttribute(pos, i); o.boneTransform(i, w); b.expandByPoint(w.applyMatrix4(o.matrixWorld)); } }
      else b.expandByObject(o);
    });
    if (b.isEmpty()) Object.values(g.markers).forEach(m => b.expandByPoint(m.getWorldPosition(w)));
    return b.isEmpty() ? null : b.expandByScalar(0.05);
  };

  // ---- Outliner: cây khớp của model (khớp có điểm chọn), bấm để chọn, Shift để thêm
  M.outline = () => {
    if (!eng || !eng.get().model) return [];
    const g = eng.get(), names = Object.keys(g.markers), set = new Set(names), par = {};
    if (!open) open = new Set(ST.pref.get("pose:open", null) || names);
    names.forEach(n => { let p = null; for (let o = g.B[n].parent; o; o = o.parent) if (set.has(o.name)) { p = o.name; break; } par[n] = p; });
    const kids = {}; names.forEach(n => (kids[par[n] || ""] || (kids[par[n] || ""] = [])).push(n));
    const rows = [], walk = (L, d) => L.forEach(n => { const k = kids[n] || []; rows.push({ id: "j:" + n, d, label: eng.NAMES[n] ? n + " · " + eng.NAMES[n] : n, icon: "joint", sel: g.selSet.has(n), act: g.sel === n, fold: k.length ? (open.has(n) ? 0 : 1) : undefined }); if (k.length && open.has(n)) walk(k, d + 1); });
    walk(kids[""] || [], 0);
    return rows;
  };
  M.olAct = (id, a, e, val) => {
    if (!eng) return; const n = String(id).slice(2);
    if (String(id).startsWith("o:")) return PR() && PR().olAct(id, a, e, val);   // vật thể phụ
    if (a === "fold") { open.has(n) ? open.delete(n) : open.add(n); ST.pref.set("pose:open", [...open]); return; }
    const g = eng.get();
    if (ST.addSel(e)) { const s = new Set(g.selSet); s.has(n) ? s.delete(n) : s.add(n); eng.setSelection([...s], n); } else eng.select(n);
  };
  ST.on("prerender", () => { if (ST.layerOn.anim && eng) { const g = eng.get(); const sig = (g.model ? g.model.uuid : "-") + ":" + g.frame + ":" + g.sel + ":" + g.selSet.size + ":" + g.playing; if (sig !== M._sig) { M._sig = sig; ST.refresh(); } } });

  // playblast → Review (như nút 🎞 của Home cũ): quay trên trang, server lưu webm + nén + thêm version Review
  ST.cmd({ id: "pose.playblast", mod: "pose", menu: "Animate", sep: true, label: "Quay playblast và gửi sang Review…", icon: "export", on: () => !!eng && !!window.DDC && !!window.DDC.askPlayblast, run: async () => {
    try {
      const o = await window.DDC.askPlayblast(); if (!o) return;
      ST.toast("Đang quay playblast…"); const r = await window.DDC.playblast(o);
      const b64 = b => new Promise(res => { const f = new FileReader(); f.onload = () => res(String(f.result).split(",")[1]); f.readAsDataURL(b); });
      ST.toast("Đang lưu và nén video…");
      const j = await (await fetch("/api/playblast", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ clip: clipInfo.id, n: r.n, fps: r.fps, w: r.w, h: r.h, views: r.views, webm_b64: await b64(r.webm), thumb_b64: r.thumb ? await b64(r.thumb) : "" }) })).json();
      if (!j.ok) throw new Error(j.error); ST.toast("Đã thêm version " + j.id.version + " vào Review Lab");
    } catch (e) { ST.toast("Không gửi được: " + (e.message || e)); }
  } });
  // W3a: anim chạy trên nhân vật hiện tại hay model chụp của phiên bản
  ST.cmd({ id: "pose.liveModel", mod: "pose", menu: "Animate", sep: true, label: "Model: nhân vật hiện tại (mesh + rig + skin)", icon: "rig",
    tip: "Bật: anim dùng mesh, khớp, skin đang có trong Studio (sửa rig là anim thấy ngay). Tắt: dùng model chụp lúc tạo phiên bản. Key vẫn lưu như cũ.",
    on: () => !!eng && eligible(eng.get().P), check: () => !!eng && eng.isLive(),
    run: async () => {
      const P = eng.get().P, k = vkey(P), next = modelOf(P) === "live" ? "snap" : "live";
      if (next === "snap" && !(await fetch(P.glb, { method: "HEAD" }).then(r => r.ok).catch(() => false))) return ST.toast("Phiên bản này không còn file model chụp trên máy (" + P.glb.split("/").pop() + "): giữ nhân vật hiện tại.");
      choices[k] = next;
      try { await modelStore().set("studio/model", choices); } catch (e) { console.error(e); }
      ST.toast(choices[k] === "live" ? "Anim dùng nhân vật hiện tại." : "Anim dùng model chụp của phiên bản."); eng.reopen();
    } });
  ST.cmd({ id: "pose.oldlab", mod: "pose", keep: true, menu: "Animate", label: "Mở Pose Lab cũ của anim này", icon: "ext", on: () => !!clipInfo, run: () => window.open("/lab/pose/" + encodeURIComponent(clipInfo.id), "_blank") });
  ST.cmd({ id: "pose.clip", menu: "Animate", label: "Đổi anim…", icon: "pose", global: true, run: async () => {
    await loadClips();
    ST.dialog("Mở anim", (clips || []).length ? `<div class="list">${clips.map(c => `<button class="it" data-id="${esc(c.id)}">${ic("pose")}<span>${esc(c.name)}</span><small>${c.versions} bản · ${esc(c.stage)}</small></button>`).join("")}</div>` : '<p class="note">Chưa có anim nào.</p>', b => { b.onclick = e => { const x = e.target.closest("[data-id]"); if (x) goClip(x.dataset.id); }; });
  } });
})();
