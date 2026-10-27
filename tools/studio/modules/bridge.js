// AI Anim Studio — cầu nối Claude ↔ Studio: long-poll /api/studio/poll trên server Home, nhận lệnh, làm, trả kết quả.
// Claude gửi lệnh bằng tools/studio_cmd.py (server: tools/home/studio_bridge.py). Chạy ở mọi trình duyệt mở Studio.
// Lệnh: state · vis {name|"*", on: true|false|"toggle"} · select {mesh|joint|null} · joint {name, t?, r?, s?} · bindPose
//       ws {id} · run {id, args} · open {char, ws}
(function () {
  const B = ST.bridge = { cid: Math.random().toString(36).slice(2, 10), on: true, n: 0 };
  const M = () => ST.mods.mesh, S = () => ST.mods.skel;
  const need = (c, msg) => { if (!c) throw new Error(msg); };

  const OPS = {
    state() {
      const m = M(), s = S();
      return {
        char: ST.char ? ST.char.id : null, name: ST.char ? ST.char.name : null, ws: ST.ws, tool: ST.tool,
        meshes: m.objects().map(o => ({ name: o.name, vis: o.vis, lock: o.lock, tris: o.idx.length / 3, skin: !!o.skin })),
        joints: s.joints.length, joint: s.sel ? s.sel() : null, posed: s.posed ? s.posed() : false, save: (ST.$("stSave") || {}).textContent || "",
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
      if (ST.ws !== "general") ST.setWS("general");
      need(S().joints.some(j => j.name === name), "Không có joint " + name);
      S().select(name); const ch = S().channel, v = ch.vals();
      ch.apply({ t: t || v.t, r: r || [0, 0, 0], s: s || [1, 1, 1] }, true);
      const j = S().joints.find(x => x.name === name); return { name, pos: j.pos.map(x => +x.toFixed(2)), posed: S().posed() };
    },
    bindPose() { S().bindPose(); return { posed: S().posed() }; },
    ws({ id }) { ST.setWS(id); return { ws: ST.ws }; },
    run({ id, args }) { need(ST.cmds.get(id), "Không có lệnh " + id); ST.run(id, ...(args || [])); return { ran: id }; },
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
