// Cầu nối lệnh Claude <-> Spine Live (2026-10-31, server: tools/home/spine_bridge.py, CLI: tools/spine_live_cmd.py).
// Trang long-poll lệnh có tên, chạy bằng runtime Spine thật (đúng inherit, IK, mesh, physics) trên skeleton nạp riêng
// từ file được chỉ định (không đụng player đang hiện), rồi trả kết quả. Không có eval.
//   pose    {json, anim, frames, bones}          góc / vị trí thế giới + giá trị local của xương theo frame
//   measure {json, anim, from?, attach?, slots?, rot?, top?}   loop, nối với anim khác, độ giật, vật bám, slot
//   snap    {json, anim, frames, cell?, cols?, bones?, bg?}     contact sheet PNG (dataURL) vẽ bằng WebGL
(() => {
  const cid = Math.random().toString(36).slice(2, 9);
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const cache = new Map();   // json -> {t, sd} (dữ liệu xương, không texture)

  const atlasFound = new Map();   // json -> atlas tìm thấy cạnh file (bản export: <tên>.atlas.txt / .atlas)
  function atlasOf(json) {
    const s = (typeof list !== "undefined" ? list : []).find(x => x.json === json);
    return s ? s.atlas : atlasFound.get(json) || json.replace(/[^/]*$/, "") + "images/_auto.atlas";
  }
  async function findAtlas(json) {   // file ngoài danh sách (vd export/): thử <tên>.atlas.txt, <tên>.atlas cạnh JSON
    if ((typeof list !== "undefined" ? list : []).some(x => x.json === json) || atlasFound.has(json)) return;
    for (const ext of [".atlas.txt", ".atlas"]) {
      const u = json.replace(/\.json$/, ext);
      try { if ((await fetch("/spine-live/f/v" + Date.now() + "/" + u, { cache: "no-store" })).ok) { atlasFound.set(json, u); return } } catch {}
    }
  }
  async function stampOf(json) {
    try { return (await (await fetch("/api/spine/stat?json=" + encodeURIComponent(json), { cache: "no-store" })).json()).t } catch { return 0 }
  }
  async function data(json) {   // SkeletonData (texture giả: chỉ cần hình học)
    if (!json) throw new Error("thiếu json");
    await findAtlas(json);
    const t = await stampOf(json), c = cache.get(json);
    if (c && c.t === t) return c.sd;
    const base = "/spine-live/f/v" + Date.now() + "/";
    const [js, at] = await Promise.all([base + json, base + atlasOf(json)].map(async u => {
      const r = await fetch(u, { cache: "no-store" }); if (!r.ok) throw new Error("HTTP " + r.status + " " + u); return r.text() }));
    const atlas = new spine.TextureAtlas(at);
    for (const p of atlas.pages) p.setTexture({ setFilters() {}, setWraps() {}, getImage() { return { width: p.width, height: p.height } }, dispose() {} });
    const sd = new spine.SkeletonJson(new spine.AtlasAttachmentLoader(atlas)).readSkeletonData(JSON.parse(js));
    cache.set(json, { t, sd });
    return sd;
  }
  function animOf(sd, name) {
    const a = name ? sd.findAnimation(name) : sd.animations[0];
    if (!a) throw new Error("không có anim " + name + " (có: " + sd.animations.map(x => x.name).join(", ") + ")");
    return a;
  }
  function poser(sd, anim) {
    const sk = new spine.Skeleton(sd);
    const fps = sd.fps || 30;
    const at = f => {
      sk.setToSetupPose();
      // loop = false: frame cuối là pose cuối thật (loop = true lấy t % duration -> F cuối = F0, đo loop luôn ra 0)
      if (anim) anim.apply(sk, 0, f / fps, false, null, 1, spine.MixBlend.setup, spine.MixDirection.mixIn);
      sk.updateWorldTransform(spine.Physics.update);
      return sk;
    };
    return { sk, fps, at, n: anim ? Math.round(anim.duration * fps) : 0 };
  }
  const tip = b => [b.worldX + (b.data.length || 0) * b.a, b.worldY + (b.data.length || 0) * b.c];
  const r2 = v => Math.round(v * 100) / 100;
  const dist = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);

  const OPS = {
    ping: async () => ({ cid, file: cur?.json, anim: curAnim?.(), frame: curFrame?.(), visible: !document.hidden }),

    async pose(a) {
      const sd = await data(a.json), anim = a.anim ? animOf(sd, a.anim) : null, P = poser(sd, anim);
      const names = a.bones?.length ? a.bones : sd.bones.map(b => b.name);
      const frames = a.frames?.length ? a.frames : [0];
      const out = {};
      for (const f of frames) {
        const sk = P.at(f), row = {};
        for (const n of names) {
          const b = sk.findBone(n); if (!b) { row[n] = null; continue }
          const d = b.data, t = tip(b);
          row[n] = { wx: r2(b.worldX), wy: r2(b.worldY), wrot: r2(b.getWorldRotationX()), tip: [r2(t[0]), r2(t[1])],
                     rot: r2(b.rotation), x: r2(b.x), y: r2(b.y), sx: r2(b.scaleX), sy: r2(b.scaleY),
                     drot: r2(b.rotation - d.rotation), dx: r2(b.x - d.x), dy: r2(b.y - d.y) };
        }
        out["F" + f] = row;
      }
      return { anim: anim?.name || "(setup)", fps: P.fps, frames: P.n, pose: out };
    },

    async measure(a) {
      const sd = await data(a.json), anim = animOf(sd, a.anim), P = poser(sd, anim), N = P.n;
      const bones = sd.bones.map(b => b.name);
      const track = (pp, n) => { const T = []; for (let f = 0; f <= n; f++) { const sk = pp.at(f); T.push(sk.bones.map(tip)) } return T };
      const T = track(P, N);
      const worst = (A, B) => { let m = 0, w = ""; A.forEach((p, i) => { const d = dist(p, B[i]); if (d > m) { m = d; w = bones[i] } }); return { px: r2(m), bone: w } };
      const vel = (T, i, j) => T[i].map((p, k) => [p[0] - T[j][k][0], p[1] - T[j][k][1]]);
      const res = { anim: anim.name, frames: N, fps: P.fps, loop_seam: worst(T[0], T[N]) };
      if (a.from) {   // nối với anim khác: đầu / cuối anim này so với F0 của anim kia (vị trí + vận tốc)
        const B = poser(sd, animOf(sd, a.from)), NB = B.n, TB = track(B, NB);
        res.join = { with: a.from,
          start_pos: worst(T[0], TB[0]), start_vel: worst(vel(T, 1, 0), vel(TB, 1, 0)),
          end_pos: worst(T[N], TB[0]), end_vel: worst(vel(T, N, N - 1), vel(TB, NB, NB - 1)) };
      }
      // độ giật: gia tốc đầu xương (px / frame²) lớn nhất
      const acc = bones.map((n, k) => { let m = 0, mf = 0, sp = 0;
        for (let f = 1; f < N; f++) { const g = Math.hypot(T[f + 1][k][0] - 2 * T[f][k][0] + T[f - 1][k][0], T[f + 1][k][1] - 2 * T[f][k][1] + T[f - 1][k][1]); if (g > m) { m = g; mf = f } }
        for (let f = 1; f <= N; f++) sp = Math.max(sp, dist(T[f][k], T[f - 1][k]));
        return { bone: n, accel: r2(m), at: mf, speed: r2(sp) } });
      res.jerkiest = acc.sort((x, y) => y.accel - x.accel).slice(0, a.top || 8);
      if (a.attach?.length) {   // "a:b": đầu xương a trôi bao nhiêu trong hệ của xương b (vật bám tay...)
        res.attach = a.attach.map(pair => {
          const [x, y] = pair.split(":"); let base = null, m = 0, mf = 0;
          for (let f = 0; f <= N; f++) { const sk = P.at(f), bx = sk.findBone(x), by = sk.findBone(y); if (!bx || !by) throw new Error("không có xương " + pair);
            const t = tip(bx), l = by.worldToLocal(new spine.Vector2(t[0], t[1])); if (!base) base = [l.x, l.y];
            const d = dist([l.x, l.y], base); if (d > m) { m = d; mf = f } }
          return { pair, drift_px: r2(m), at: mf } });
      }
      if (a.slots?.length) {   // ảnh của slot theo frame (chớp mắt...)
        res.slots = {};
        for (const s of a.slots) { const ch = []; let prev;
          for (let f = 0; f <= N; f++) { const sk = P.at(f), sl = sk.findSlot(s); if (!sl) throw new Error("không có slot " + s);
            const nm = sl.getAttachment()?.name || "-"; if (nm !== prev) { ch.push("F" + f + ":" + nm); prev = nm } }
          res.slots[s] = ch.join(" ") }
      }
      if (a.rot?.length) {   // biên độ góc local so với setup
        res.rot = {};
        for (const n of a.rot) { let lo = 1e9, hi = -1e9, fl = 0, fh = 0;
          for (let f = 0; f <= N; f++) { const b = P.at(f).findBone(n); if (!b) throw new Error("không có xương " + n); const v = b.rotation - b.data.rotation;
            if (v < lo) { lo = v; fl = f } if (v > hi) { hi = v; fh = f } }
          res.rot[n] = `${r2(lo)}° @F${fl} .. ${r2(hi)}° @F${fh}` }
      }
      return res;
    },

    async snap(a) { return snapSheet(a) },
  };

  // ---- snap: render WebGL thật (canvas riêng, giữ buffer) -> contact sheet 2D ----
  const GL = { json: null, t: null };
  async function glFor(json, W, H) {
    await findAtlas(json);
    const t = await stampOf(json);
    if (!GL.canvas) {
      GL.canvas = document.createElement("canvas");
      GL.ctx = new spine.ManagedWebGLRenderingContext(GL.canvas, { alpha: true, preserveDrawingBuffer: true, premultipliedAlpha: false });
      GL.r = new spine.SceneRenderer(GL.canvas, GL.ctx, true);
    }
    GL.canvas.width = W; GL.canvas.height = H;
    if (GL.json !== json || GL.t !== t) {
      try { GL.am?.dispose?.() } catch (e) { console.warn("snap: bỏ qua lỗi dọn asset cũ", e) }   // lần nạp trước hỏng để lại asset rỗng
      GL.json = GL.t = null;
      const base = "/spine-live/f/v" + Date.now() + "/";
      GL.am = new spine.AssetManager(GL.ctx, base);
      GL.am.loadText(json); GL.am.loadTextureAtlas(atlasOf(json));
      for (let i = 0; i < 400 && !GL.am.isLoadingComplete(); i++) await sleep(25);
      if (GL.am.hasErrors()) throw new Error("nạp ảnh lỗi: " + JSON.stringify(GL.am.getErrors()));
      GL.sd = new spine.SkeletonJson(new spine.AtlasAttachmentLoader(GL.am.require(atlasOf(json)))).readSkeletonData(JSON.parse(GL.am.require(json)));
      GL.json = json; GL.t = t;
    }
    return GL;
  }
  async function snapSheet(a) {
    const [cw, ch] = a.cell || [360, 420], cols = a.cols || Math.min(4, (a.frames || [0]).length);
    const G = await glFor(a.json, cw, ch), sd = G.sd, anim = a.anim ? animOf(sd, a.anim) : null, P = poser(sd, anim);
    const frames = a.frames?.length ? a.frames : [0];
    // khung chung cho mọi frame (để so chuyển động)
    let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
    const off = new spine.Vector2(), size = new spine.Vector2();
    for (const f of frames) { P.at(f).getBounds(off, size, []); x0 = Math.min(x0, off.x); y0 = Math.min(y0, off.y); x1 = Math.max(x1, off.x + size.x); y1 = Math.max(y1, off.y + size.y) }
    const pad = 0.06, bw = (x1 - x0) * (1 + 2 * pad), bh = (y1 - y0) * (1 + 2 * pad);
    const zoom = Math.max(bw / cw, bh / (ch - 18));
    const rows = Math.ceil(frames.length / cols), sheet = document.createElement("canvas");
    sheet.width = cols * cw; sheet.height = rows * ch;
    const g2 = sheet.getContext("2d"); g2.fillStyle = a.bg || "#1c3a5c"; g2.fillRect(0, 0, sheet.width, sheet.height);
    const gl = G.ctx.gl, cam = G.r.camera;
    for (let i = 0; i < frames.length; i++) {
      const sk = P.at(frames[i]);
      gl.viewport(0, 0, cw, ch); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
      cam.setViewport(cw, ch - 18); cam.zoom = zoom; cam.position.x = (x0 + x1) / 2; cam.position.y = (y0 + y1) / 2 - 9 * zoom; cam.update();
      G.r.begin(); G.r.drawSkeleton(sk, false); if (a.bones) G.r.drawSkeletonDebug(sk, false); G.r.end();
      const cx = (i % cols) * cw, cy = Math.floor(i / cols) * ch;
      g2.drawImage(G.canvas, 0, 0, cw, ch, cx, cy, cw, ch);
      g2.fillStyle = "#000a"; g2.fillRect(cx, cy, cw, 18); g2.fillStyle = "#fff"; g2.font = "12px ui-monospace,Consolas,monospace";
      g2.fillText(`${anim?.name || "setup"} F${frames[i]}`, cx + 6, cy + 13);
      g2.strokeStyle = "#0006"; g2.strokeRect(cx + 0.5, cy + 0.5, cw - 1, ch - 1);
    }
    return { png: sheet.toDataURL("image/png"), w: sheet.width, h: sheet.height, frames, zoom: r2(zoom) };
  }

  async function loop() {
    for (;;) {
      try {
        const r = await fetch(`/api/spine/br/poll?cid=${cid}&vis=${document.hidden ? 0 : 1}`, { cache: "no-store" });
        const cmd = await r.json();
        if (!cmd || !cmd.op) continue;
        let out;
        try {
          if (!OPS[cmd.op]) throw new Error("không có lệnh " + cmd.op + " (có: " + Object.keys(OPS).join(", ") + ")");
          out = { ok: true, result: await OPS[cmd.op](cmd.args || {}) };
        } catch (e) { out = { ok: false, error: String(e?.message || e) } }
        await fetch("/api/spine/br/result", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: cmd.id, ...out }) });
      } catch { await sleep(1500) }
    }
  }
  addEventListener("pagehide", () => { try { fetch("/api/spine/br/bye?cid=" + cid, { keepalive: true }) } catch {} });
  loop();
  window.spineBridge = { cid, OPS };
})();
