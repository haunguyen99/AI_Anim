// AI Anim Studio — cầu nối Claude ↔ Studio: long-poll /api/studio/poll trên server Home, nhận lệnh, làm, trả kết quả.
// Claude gửi lệnh bằng tools/studio_cmd.py (server: tools/home/studio_bridge.py). Chạy ở mọi trình duyệt mở Studio.
// Lệnh: state · vis {name|"*", on: true|false|"toggle"} · select {mesh|joint|null} · joint {name, t?, r?, s?} · bindPose
//       ws {id} · run {id, args} · open {char, ws} · focus {id: mesh|rig|pose} · layer {id: scene|rig|anim, on, solo} · cmds {q?}
//       undo · redo · save · view {layout: 1|4, cam: persp|top|front|side, frame: all|sel} · snap (ảnh viewport PNG, base64)
//       rig {do: lms|lm|sel|step, name, xyz, names, n} · anim {do: info|joints|read|select|rot|pos|frame|play|key|unkey|versions|version, …}
//       obj {do: list|read|add|key|unkey|parent|set|del|select, …} (vật thể phụ của anim, modules/props.js; cm, trục Blender)
// Workspace chỉ là bố cục: mọi lệnh chạy được ở workspace nào cũng được (run tự focus sang module của lệnh).
// rig / anim tự focus + bật lớp + chờ lõi nạp xong (W2, docs/studio_design.md mục 11).
(function () {
  const B = ST.bridge = { cid: Math.random().toString(36).slice(2, 10), on: true, n: 0 };
  const M = () => ST.mods.mesh, S = () => ST.mods.skel;
  const need = (c, msg) => { if (!c) throw new Error(msg); };

  // ---- lõi Rig / Pose: focus + bật lớp + chờ nạp
  const rigEng = () => ST.rigEng && ST.rigEng(), poseEng = () => ST.poseEng && ST.poseEng();
  function rigState() {
    const e = rigEng(); if (!e || !ST.mods.rig.loaded()) return null;
    const g = e.get(); return { step: g.step, sel: [...g.S], skin: !!g.SK, mirror: g.mirror, gates: g.gates, save: g.saveMsg || "" };
  }
  function animState() { const e = poseEng(); try { return e && e.ai && ST.mods.pose.loaded() ? e.ai.info() : null; } catch (x) { return null; } }
  async function want(mod) {
    if (ST.focus !== mod) ST.setFocus(mod);
    const m = ST.mods[mod]; need(m, "Không có module " + mod);
    if (m.whenReady) need(await m.whenReady(), mod === "rig" ? "Rig chưa nạp được: " + (m.loadMsg ? m.loadMsg() : "") : "Anim chưa nạp được: " + (m.loadMsg ? m.loadMsg() : ""));
  }
  const r3 = a => a.map(v => +(+v).toFixed(2));

  const OPS = {
    state() {
      const m = M(), s = S();
      return {
        char: ST.char ? ST.char.id : null, name: ST.char ? ST.char.name : null, ws: ST.ws, focus: ST.focus, jointSel: (() => { try { return ST.mod().curJoint ? ST.mod().curJoint() : null; } catch (e) { return null; } })(), layers: Object.assign({}, ST.layerOn), tool: ST.tool, tab: ST.curTab ? ST.curTab() : null,
        meshes: m.objects().map(o => ({ name: o.name, vis: o.vis, lock: o.lock, tris: o.idx.length / 3, skin: !!o.skin })),
        joints: s.joints.length, joint: s.sel ? s.sel() : null, posed: s.posed ? s.posed() : false, save: (ST.$("stSave") || {}).textContent || "",
        undo: ST.hist.U.length ? ST.hist.U[ST.hist.U.length - 1].label : null, info: (ST.$("stInfo") || {}).textContent || "",
        rig: rigState(), anim: animState(),
      };
    },
    vis({ name, on }) {
      const m = M(), list = name === "*" || !name ? m.objects() : [m.byName(name)];
      need(list.every(Boolean), "Không có mesh " + name);
      if (on === "toggle") list.forEach(o => m.setVis([o], !o.vis)); else m.setVis(list, on !== false);
      return list.map(o => ({ name: o.name, vis: o.vis }));
    },
    select({ mesh, joint }) {
      ST.setFocus("mesh");   // mesh / xương của Cảnh (General); khớp ở Rig / Anim: rig sel, anim select
      if (joint !== undefined) { need(!joint || S().joints.some(j => j.name === joint), "Không có joint " + joint); S().select(joint || null); return { joint: S().sel() }; }
      const o = mesh ? M().byName(mesh) : null; need(!mesh || o, "Không có mesh " + mesh);
      if (S().sel()) S().select(null);
      if (o) M().olAct(o.id, "pick", {}); return { mesh: o ? o.name : null };
    },
    joint({ name, t, r, s }) {   // t: vị trí cm (tuyệt đối); r: xoay thêm (độ, quanh joint); s: scale thêm — joint con đi theo, mesh skin đi theo
      ST.setFocus("mesh");
      need(S().joints.some(j => j.name === name), "Không có joint " + name);
      S().select(name); const ch = S().channel, v = ch.vals();
      ch.apply({ t: t || v.t, r: r || [0, 0, 0], s: s || [1, 1, 1] }, true);
      const j = S().joints.find(x => x.name === name); return { name, pos: j.pos.map(x => +x.toFixed(2)), posed: S().posed() };
    },
    bindPose() { S().bindPose(); return { posed: S().posed() }; },
    undo() { const own = !!ST.mod().undo; ST.run("edit.undo"); return { focus: ST.focus, history: own ? "lõi " + ST.focus : "chung", next: own ? null : (ST.hist.U.length ? ST.hist.U[ST.hist.U.length - 1].label : null) }; },
    redo() { ST.run("edit.redo"); return {}; },
    save() { ST.run("file.save"); return { save: (ST.$("stSave") || {}).textContent || "" }; },
    view({ layout, cam, frame, az, el, d }) {
      const V = ST.view;
      if (layout || cam) { need(!cam || V.panes[cam], "Khung là persp, top, front hoặc side"); V.setLayout(String(layout || (cam ? "1" : V.layout)), cam || undefined); }
      if (frame === "all") V.frameAll(); else if (frame === "sel") V.frameSel();
      // góc camera persp cố định (để so với ảnh ref): az = độ quanh trục đứng tính từ +Z (trước mặt nhân vật) sang +X
      // (bên trái nhân vật), el = độ ngẩng từ trên xuống, d = khoảng cách (m), quanh tâm đang nhìn
      if (az !== undefined || el !== undefined || d !== undefined) {
        if (V.single !== "persp") V.setLayout("1", "persp");
        const p = V.panes.persp, c = p.cam, cur = c.position.clone().sub(p.target), r0 = cur.length();
        const A = THREE.MathUtils.degToRad(az !== undefined ? +az : Math.atan2(cur.x, cur.z) * 180 / Math.PI), E = THREE.MathUtils.degToRad(el !== undefined ? +el : Math.asin(cur.y / r0) * 180 / Math.PI), R = d !== undefined ? +d : r0;
        c.position.set(p.target.x + R * Math.sin(A) * Math.cos(E), p.target.y + R * Math.sin(E), p.target.z + R * Math.cos(A) * Math.cos(E)); c.lookAt(p.target); c.updateProjectionMatrix(); V.orbit.update();
      }
      return { layout: V.layout, cam: V.single, pos: ST.view.panes.persp.cam.position.toArray().map(v => +v.toFixed(3)), target: ST.view.panes.persp.target.toArray().map(v => +v.toFixed(3)) };
    },
    snap({ w, h } = {}) {   // ảnh viewport để AI tự kiểm; vẽ lại ngay rồi đọc canvas trong cùng lượt
      const V = ST.view, cv = ST.$("cv");
      if (cv.width >= 2 && cv.height >= 2 && !w) { V.renderNow(); const url = cv.toDataURL("image/png"); return { w: cv.width, h: cv.height, png: url.slice(url.indexOf(",") + 1) }; }
      // trang đang ẩn (khung 0 px) hoặc xin cỡ riêng: vẽ khung đang dùng ra cỡ W×H rồi trả canvas về như cũ
      const W = w || 1280, H = h || 720, R = V.renderer, cam = V.active.cam, X = V.extra, keep = cam.isPerspectiveCamera ? cam.aspect : [cam.left, cam.right, cam.top, cam.bottom];
      try {
        R.setSize(W, H, false);
        if (cam.isPerspectiveCamera) cam.aspect = W / H; else { cam.left = -W / H; cam.right = W / H; cam.top = 1; cam.bottom = -1; }
        cam.updateProjectionMatrix();
        R.setClearColor(getComputedStyle(document.documentElement).getPropertyValue("--view").trim() || "#15191f");
        R.autoClear = false; R.clear(); if (X) R.render(X.scene, cam); R.render(V.scene, cam); if (X) { R.clearDepth(); R.render(X.overlay, cam); }
        const url = cv.toDataURL("image/png"); return { w: W, h: H, offscreen: true, png: url.slice(url.indexOf(",") + 1) };
      } finally {
        R.autoClear = true;
        if (cam.isPerspectiveCamera) cam.aspect = keep; else [cam.left, cam.right, cam.top, cam.bottom] = keep;
        cam.updateProjectionMatrix(); V.resize();
      }
    },
    async rig({ do: d, name, xyz, names, n }) {
      await want("rig"); const e = rigEng(), g = e.get();
      if (d === "lms" || !d) return Object.fromEntries(Object.entries(g.LM).filter(([, v]) => Array.isArray(v) && v.length === 3).map(([k, v]) => [k, r3(v)]));
      if (d === "lm") { need(g.LM[name], "Không có khớp " + name); need(Array.isArray(xyz) && xyz.length === 3, "xyz = x,y,z (cm)"); e.setLM(name, xyz.map(Number)); return { [name]: r3(e.get().LM[name]), mirror: g.mirror }; }
      if (d === "sel") { const L = names || []; L.forEach(k => need(g.LM[k], "Không có khớp " + k)); if (g.step !== 2) ST.run("rig.step2"); e.applySel(L, {}); return { sel: [...e.get().S] }; }
      if (d === "step" && +n === 6) {   // bước 6 Vật lý = panel rig:s6 (modules/rig_setup.js); bố cục lưu cũ thiếu tab thì thêm vào
        const L = ST.tabs(); if (!L.includes("rig:s6")) ST.pref.set("tabs:" + ST.ws, L.concat("rig:s6"));
        ST.showTab("rig:s6"); ST.refresh(); return { step: 6, tab: ST.curTab() };
      }
      if (d === "step") { need(n >= 1 && n <= 5, "Bước 1–6"); ST.run("rig.step" + n); return { step: e.get().step }; }
      throw new Error("rig: lms | lm | sel | step");
    },
    async anim(a) {
      if (a.do === "clips") return ST.mods.pose.clipList();
      if (a.do === "clip") {   // đổi anim = tải lại trang (một anim mỗi trang); lệnh sau đợi trang mới kết nối lại
        const L = await ST.mods.pose.clipList(), c = L.find(x => x.id === a.id) || L.find(x => (x.name || "").toLowerCase() === String(a.id || "").toLowerCase());
        need(c, "Không có anim " + a.id + " (anim clips để xem danh sách)"); B.after = () => ST.mods.pose.goClip(c.id); return { opening: c.id };
      }
      await want("pose"); const A = poseEng().ai;
      if (["rot", "pos", "key", "unkey"].includes(a.do) && ST.mods.props) ST.mods.props.touchEngine();   // Hoàn tác sau đó: khớp trước vật thể
      switch (a.do || "info") {
        case "info": return A.info();
        case "joints": return A.joints();
        case "read": return A.read(a.names);
        case "select": return A.select(a.names || []);
        case "rot": return A.rot(a.name, a.r || [0, 0, 0], !!a.abs);
        case "pos": return A.pos(a.name, a.t || [0, 0, 0]);
        case "frame": return A.frame(a.f);
        case "play": return A.play(a.on !== false);
        case "key": if (a.f) A.frame(a.f); return A.key();
        case "unkey": if (a.f) A.frame(a.f); return A.unkey();
        case "versions": return A.versions();
        case "version": return A.version(a.v);
      }
      throw new Error("anim: clips | clip | info | joints | read | select | rot | pos | frame | play | key | unkey | versions | version");
    },
    async obj(a) {   // vật thể phụ của lớp Anim: mũi tên, hình nộm… (key riêng, không vào FBX)
      await want("pose"); const P = ST.mods.props; need(P, "Không có module vật thể phụ"); await P.ensure();
      const n = a.name, f = a.f ? +a.f : undefined;
      switch (a.do || "list") {
        case "list": return P.list(f);
        case "read": return P.read(n, f);
        case "add": return P.add({ name: n, mesh: a.mesh, box: a.box, capsule: a.capsule, bone: a.bone, f, at: a.at, color: a.color, hideSrc: a.hideSrc });
        case "key": return P.key(n, { f, at: a.at, move: a.move, along: a.along, rot: a.rot, aim: a.aim, par: a.par, interp: a.interp, vis: a.vis });
        case "unkey": return P.unkey(n, f);
        case "parent": return P.parent(n, a.par, f);
        case "set": return P.set(n, a);
        case "del": return P.del(n);
        case "select": { const id = n ? P.idOf(n) : null; need(!n || id, "Không có vật thể " + n); P.select(id); return { sel: n || null }; }
      }
      throw new Error("obj: list | read | add | key | unkey | parent | set | del | select");
    },
    ws({ id }) { need(ST.WS[id], "Không có workspace " + id); ST.setWS(id); return { ws: ST.ws, focus: ST.focus }; },
    focus({ id }) { need(ST.mods[id] && ST.LAYER_OF[id], "Focus là mesh, rig hoặc pose"); ST.setFocus(id); return { focus: ST.focus, layers: Object.assign({}, ST.layerOn) }; },
    layer({ id, on, solo }) { id = (ST.LAYER_ALIAS || {})[id] || id; need(id in ST.layerOn, "Lớp là scene (nhân vật, rig là chế độ sửa của nó) hoặc anim"); ST.showLayer(id, on === "toggle" ? !ST.layerOn[id] : on !== false, solo); return { layers: Object.assign({}, ST.layerOn) }; },
    cmds({ q }) {   // danh sách lệnh (để AI biết gọi gì): id, nhãn, menu, module, phím, dùng được ngay không
      const k = String(q || "").toLowerCase();
      return [...ST.cmds.values()].filter(c => !c.hidden && (!k || (c.id + " " + c.label + " " + (c.menu || "")).toLowerCase().includes(k)))
        .map(c => ({ id: c.id, label: c.label, menu: c.menu || "", mod: c.mod || "", key: c.key ? ST.keyLabel(c.key) : "", on: ST.cmdOn(c) }));
    },
    async run({ id, args }) {
      const c = ST.cmds.get(id); need(c, "Không có lệnh " + id);
      const m = c.mod && ST.mods[c.mod];
      if (m && !c.keep && ST.focus !== c.mod) ST.setFocus(c.mod);
      if (m && m.whenReady && !c.keep) await m.whenReady();   // lõi Rig / Pose nạp lười: chờ sẵn sàng hẳn rồi mới chạy
      need(ST.cmdOn(c), "Lệnh " + id + " chưa dùng được lúc này (thiếu dữ liệu hoặc vùng chọn)");
      ST.run(id, ...(args || [])); return { ran: id, focus: ST.focus };
    },
    open({ char, ws }) { const u = new URL("/studio/" + encodeURIComponent(char), location.origin); u.searchParams.set("ws", ws || ST.ws || "general"); B.after = () => { location.href = u; }; return { opening: u.pathname + u.search }; },
  };   // chỉ các lệnh có tên ở trên, không chạy mã tuỳ ý

  async function loop() {
    let wait = 0;
    while (B.on) {
      try {
        const r = await fetch("/api/studio/poll?" + meta(), { cache: "no-store" });
        if (!r.ok) throw new Error(r.status);
        const c = await r.json(); wait = 0;
        if (!c || !c.op) continue;
        let out;
        try {
          const f = OPS[c.op]; need(f, "Lệnh lạ: " + c.op);
          const res = await f(c.args || {}); ST.refresh();
          out = { id: c.id, ok: true, result: res === undefined ? null : JSON.parse(JSON.stringify(res)) };
        } catch (e) { out = { id: c.id, ok: false, error: String(e && e.message || e) }; }
        B.n++;
        await fetch("/api/studio/result", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(out) });
        if (B.after) { const f = B.after; B.after = null; f(); }   // đổi trang (open, anim clip) sau khi đã trả kết quả
      } catch (e) { wait = Math.min(10000, (wait || 500) * 2); await new Promise(r => setTimeout(r, wait)); }   // không có server Home: thử lại thưa dần
    }
  }
  // báo server: nhân vật / workspace / tab đang xem đổi (để lệnh đi đúng trang), và đóng tab thì rời ngay
  const meta = () => new URLSearchParams({ cid: B.cid, vis: document.visibilityState === "visible" ? "1" : "0", char: ST.char ? ST.char.id : "", ws: ST.ws || "" });
  const hello = () => { if (B.on) fetch("/api/studio/hello?" + meta(), { cache: "no-store" }).catch(() => {}); };
  ["char", "ws", "loaded"].forEach(ev => ST.on(ev, hello));
  document.addEventListener("visibilitychange", hello);
  addEventListener("pagehide", () => { B.on = false; fetch("/api/studio/bye?cid=" + B.cid, { keepalive: true, cache: "no-store" }).catch(() => {}); });
  ST.on("init", () => { if (location.protocol.startsWith("http")) loop(); });
})();
