// AI Anim Studio — cầu nối Claude ↔ Studio: long-poll /api/studio/poll trên server Home, nhận lệnh, làm, trả kết quả.
// Claude gửi lệnh bằng tools/studio_cmd.py (server: tools/home/studio_bridge.py). Chạy ở mọi trình duyệt mở Studio.
// Lệnh: state · vis {name|"*", on: true|false|"toggle"} · select {mesh|joint|null} · joint {name, t?, r?, s?} · bindPose
//       ws {id} · run {id, args} · open {char, ws} · focus {id: mesh|rig|pose} · layer {id: scene|rig|anim, on, solo} · cmds {q?}
//       undo · redo · save · view {layout: 1|4, cam: persp|top|front|side, frame: all|sel} · snap (ảnh viewport PNG, base64)
//       rig {do: lms|lm|sel|step, name, xyz, names, n} · anim {do: info|joints|read|select|rot|pos|frame|play|key|unkey|versions|version, …}
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
        char: ST.char ? ST.char.id : null, name: ST.char ? ST.char.name : null, ws: ST.ws, focus: ST.focus, layers: Object.assign({}, ST.layerOn), tool: ST.tool, tab: ST.curTab ? ST.curTab() : null,
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
    view({ layout, cam, frame }) {
      const V = ST.view;
      if (layout || cam) { need(!cam || V.panes[cam], "Khung là persp, top, front hoặc side"); V.setLayout(String(layout || (cam ? "1" : V.layout)), cam || undefined); }
      if (frame === "all") V.frameAll(); else if (frame === "sel") V.frameSel();
      return { layout: V.layout, cam: V.single };
    },
    snap() {   // ảnh viewport (như đang thấy) để AI tự kiểm; vẽ lại ngay rồi đọc canvas trong cùng lượt
      const cv = ST.$("cv"); ST.view.renderNow();
      const url = cv.toDataURL("image/png"); return { w: cv.width, h: cv.height, png: url.slice(url.indexOf(",") + 1) };
    },
    async rig({ do: d, name, xyz, names, n }) {
      await want("rig"); const e = rigEng(), g = e.get();
      if (d === "lms" || !d) return Object.fromEntries(Object.entries(g.LM).filter(([, v]) => Array.isArray(v) && v.length === 3).map(([k, v]) => [k, r3(v)]));
      if (d === "lm") { need(g.LM[name], "Không có khớp " + name); need(Array.isArray(xyz) && xyz.length === 3, "xyz = x,y,z (cm)"); e.setLM(name, xyz.map(Number)); return { [name]: r3(e.get().LM[name]), mirror: g.mirror }; }
      if (d === "sel") { const L = names || []; L.forEach(k => need(g.LM[k], "Không có khớp " + k)); if (g.step !== 2) ST.run("rig.step2"); e.applySel(L, {}); return { sel: [...e.get().S] }; }
      if (d === "step") { need(n >= 1 && n <= 5, "Bước 1–5"); ST.run("rig.step" + n); return { step: e.get().step }; }
      throw new Error("rig: lms | lm | sel | step");
    },
    async anim(a) {
      await want("pose"); const A = poseEng().ai;
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
      throw new Error("anim: info | joints | read | select | rot | pos | frame | play | key | unkey | versions | version");
    },
    ws({ id }) { need(ST.WS[id], "Không có workspace " + id); ST.setWS(id); return { ws: ST.ws, focus: ST.focus }; },
    focus({ id }) { need(ST.mods[id] && ST.LAYER_OF[id], "Focus là mesh, rig hoặc pose"); ST.setFocus(id); return { focus: ST.focus, layers: Object.assign({}, ST.layerOn) }; },
    layer({ id, on, solo }) { need(id in ST.layerOn, "Lớp là scene, rig hoặc anim"); ST.showLayer(id, on === "toggle" ? !ST.layerOn[id] : on !== false, solo); return { layers: Object.assign({}, ST.layerOn) }; },
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
    open({ char, ws }) { const u = new URL("/studio/" + encodeURIComponent(char), location.origin); u.searchParams.set("ws", ws || ST.ws || "general"); setTimeout(() => { location.href = u; }, 50); return { opening: u.pathname + u.search }; },
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
