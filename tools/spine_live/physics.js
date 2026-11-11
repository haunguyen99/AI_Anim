// Physics (overlap) cho Spine Live - như plugin Overlappy của Maya (người dùng 2026-10-30): chọn xương, chỉnh Mềm / Mạnh,
// tích Cycle / Hierarchy..., bấm Physic -> nướng key xoay mỗi frame cho các xương đó trong anim đang xem (một bước Hoàn tác).
// Cách tính: với mỗi xương, một "đầu xương ảo" (điểm ở đầu xương) bị kéo về đầu xương thật bằng lò xo có giảm chấn, luôn
// cách gốc đúng độ dài xương; độ lệch góc giữa đầu ảo và đầu thật = góc overlap, cộng vào key xoay đang có.
// Hierarchy: xử lý cha trước con, con lấy mẫu chuyển động ĐÃ có overlap của cha (sóng truyền dọc chuỗi như tóc / khăn).
// Cycle: chạy nhiều vòng loop rồi lấy vòng cuối, nối đầu - cuối cho loop liền. Dùng biến chung: player, cur, ed, fpsOf,
// curAnim, edPost, animReloadLive, setStatus, hhmmss, store, $.
(() => {
  const P = { bones: [], soft: +store.get("phSoft", "0.5"), scale: +store.get("phScale", "1"), cycle: store.get("phCycle", "1") === "1",
              hier: store.get("phHier", "1") === "1", step: +store.get("phStep", "1"), grav: +store.get("phGrav", "0"),
              wind: +store.get("phWind", "0"), damp: +store.get("phDamp", "0.3") };
  const box = document.createElement("div");
  box.id = "physBox"; box.className = "sec tool animOnly";
  box.innerHTML = `
    <h3 class="secT">Physics (overlap) <span id="phInfo" class="mute" style="font-weight:400"></span></h3>
    <div id="phList" class="row"></div>
    <div class="row">
      <button id="phAdd" title="Thêm xương đang chọn (Hierarchy bật: kèm mọi xương con)">+ xương đang chọn</button>
      <button id="phClear" title="Bỏ chọn hết">Bỏ hết</button>
    </div>
    <label class="phRow" title="0 = cứng, bám sát; 1 = rất mềm, trễ nhiều">Mềm <input id="phSoft" type="range" min="0" max="1" step="0.05"><span id="phSoftV"></span></label>
    <label class="phRow" title="Độ mạnh: nhân góc overlap (0 = tắt, 1 = như mô phỏng, 2 = gấp đôi)">Mạnh <input id="phScale" type="range" min="0" max="2" step="0.05"><span id="phScaleV"></span></label>
    <label class="phRow" title="Giảm chấn: thấp = lắc lâu, cao = dừng nhanh">Giảm chấn <input id="phDamp" type="range" min="0.05" max="1" step="0.05"><span id="phDampV"></span></label>
    <div class="row">
      <label title="Anim loop: mô phỏng nhiều vòng, lấy vòng cuối, nối đầu - cuối liền"><input type="checkbox" id="phCycle">Cycle</label>
      <label title="Gồm cả các xương con của xương được thêm; xử lý cha trước con, con chịu overlap của cha"><input type="checkbox" id="phHier">Hierarchy</label>
      <label title="Bake key mỗi n frame">Bake <select id="phStep"><option value="1">mỗi frame</option><option value="2">mỗi 2 frame</option></select></label>
    </div>
    <div class="row">
      <label title="Trọng lực kéo đầu xương xuống (px/s², 0 = không)">Trọng lực <input id="phGrav" type="number" step="100" style="width:64px"></label>
      <label title="Gió theo trục ngang (px/s², âm = thổi sang trái)">Gió <input id="phWind" type="number" step="100" style="width:64px"></label>
    </div>
    <button id="phOff" title="Trả các xương đã chọn về key gốc trước lần Physics đầu tiên (Ctrl+Z lùi)">Bỏ physics</button>
    <button id="phRun" class="primary" title="Nướng key overlap cho các xương đã chọn trong anim đang xem (Ctrl+Z lùi)">Physic ▶</button>`;
  document.getElementById("noteBox").after(box);
  const st = document.createElement("style");
  st.textContent = `
    #physBox .phRow{display:flex;gap:6px;align-items:center} #physBox .phRow input[type=range]{flex:1}
    #phList .pc{display:inline-flex;gap:3px;align-items:center;padding:1px 6px;border-radius:10px;border:1px solid #6fd3ff;background:#6fd3ff22}
    #phList .pc b{cursor:pointer;color:#ff6b6b}`;
  document.head.appendChild(st);

  // ---- điều khiển ----
  const bind = (id, key, num, fmt) => {
    const el = $(id);
    if (el.type === "checkbox") { el.checked = P[key]; el.onchange = () => { P[key] = el.checked; store.set(store_key(key), el.checked ? "1" : "0") } }
    else { el.value = P[key]; const show = () => { if ($(id + "V")) $(id + "V").textContent = fmt ? fmt(P[key]) : P[key] };
      show(); el.oninput = el.onchange = () => { P[key] = num ? +el.value : el.value; store.set(store_key(key), String(el.value)); show() } }
  };
  const store_key = k => "ph" + k[0].toUpperCase() + k.slice(1);
  bind("phSoft", "soft", true, v => (+v).toFixed(2)); bind("phScale", "scale", true, v => (+v).toFixed(2));
  bind("phDamp", "damp", true, v => (+v).toFixed(2));
  bind("phCycle", "cycle"); bind("phHier", "hier"); bind("phStep", "step", true);
  bind("phGrav", "grav", true); bind("phWind", "wind", true);

  function descendants(b, out) { out.push(b.data.name); for (const c of b.children) descendants(c, out); return out }
  function renderList() {
    $("phList").innerHTML = P.bones.length ? P.bones.map(n => `<span class="pc">${n}<b data-n="${n}" title="Bỏ">✕</b></span>`).join("")
      : '<span style="color:var(--mute)">chọn xương trên hình rồi bấm "+ xương đang chọn"</span>';
    $("phList").querySelectorAll("b[data-n]").forEach(x => x.onclick = () => { P.bones = P.bones.filter(n => n !== x.dataset.n); renderList() });
    $("phInfo").textContent = P.bones.length ? " · " + P.bones.length + " xương" : "";
  }
  $("phAdd").onclick = () => {
    if (!player || !ed.sel) return setStatus("chọn một xương trên hình trước", "bad");
    const add = P.hier ? descendants(ed.sel, []) : [ed.sel.data.name];
    for (const n of add) if (!P.bones.includes(n)) P.bones.push(n);
    renderList();
  };
  $("phClear").onclick = () => { P.bones = []; renderList() };
  renderList();

  // ---- mô phỏng ----
  const wrap = a => ((a + 540) % 360) - 180;
  // overlap đã nướng lần trước (lưu trong file: spineLive.physics[anim][bone] = {fps, offs, src}): trừ ra khi tính lại
  async function stored() {
    const raw = await (await fetch("/spine-live/f/" + cur.json, { cache: "no-store" })).json();
    return { raw, old: raw.spineLive?.physics?.[curAnim()] || {} };
  }
  function simulate(old = {}) {
    const sd = player.skeleton.data, anim = sd.findAnimation(curAnim());
    if (!anim) throw new Error("chưa có anim");
    const F = fpsOf(), N = Math.round(anim.duration * F);
    if (N < 2) throw new Error("anim quá ngắn (" + N + " frame)");
    const sk = new spine.Skeleton(sd);
    const ikBones = new Set(); for (const c of sk.ikConstraints) c.bones.forEach(b => ikBones.add(b.data.name));
    const order = P.bones.map(n => sk.findBone(n)).filter(Boolean).sort((a, b) => a.data.index - b.data.index);
    const skipped = order.filter(b => ikBones.has(b.data.name)).map(b => b.data.name);
    const targets = order.filter(b => !ikBones.has(b.data.name));
    const offs = {};                                   // tên xương -> góc overlap (local, độ) theo frame 0..N
    const tset = new Set(targets.map(b => b.data.name));
    const oldAt = (n, f) => { const o = old[n]?.offs; if (!o || !tset.has(n)) return 0; const i = Math.floor(f), u = f - i;
      const a0 = o[Math.min(o.length - 1, Math.max(0, i))], a1 = o[Math.min(o.length - 1, Math.max(0, i + 1))]; return a0 + (a1 - a0) * u };
    const pose = f => {                                // pose ở frame f (thực) + overlap của các xương đã tính
      sk.setToSetupPose();
      anim.apply(sk, f / F, f / F, false, null, 1, spine.MixBlend.setup, spine.MixDirection.mixIn);
      for (const n of tset) { const v = oldAt(n, f); if (v) sk.findBone(n).rotation -= v }   // về chuyển động gốc (bỏ overlap cũ)
      for (const n in offs) { const o = offs[n], i = Math.floor(f), u = f - i, b = sk.findBone(n);
        const a0 = o[Math.min(N, Math.max(0, i))], a1 = o[Math.min(N, Math.max(0, i + 1))]; b.rotation += a0 + (a1 - a0) * u }
      sk.updateWorldTransform(2);
    };
    const w = 2 * Math.PI * (0.6 + (1 - P.soft) * 7), z = P.damp, sub = 6, dt = 1 / F;
    const base = {};
    for (const b of targets) {
      const L = b.data.length > 1 ? b.data.length : 40;
      const smp = [];
      for (let f = 0; f <= N; f++) {
        pose(f);
        const px = b.worldX, py = b.worldY, n = Math.hypot(b.a, b.c) || 1;
        smp.push({ px, py, tx: px + L * b.a / n, ty: py + L * b.c / n, loc: b.rotation - b.data.rotation,
                   flip: b.parent && (b.parent.a * b.parent.d - b.parent.b * b.parent.c) < 0 ? -1 : 1 });
      }
      base[b.data.name] = smp.map(s => s.loc);
      const at = (f) => { const i = Math.floor(f), u = f - i, A = smp[Math.min(N, i)], B = smp[Math.min(N, i + 1)];
        return { px: A.px + (B.px - A.px) * u, py: A.py + (B.py - A.py) * u, tx: A.tx + (B.tx - A.tx) * u, ty: A.ty + (B.ty - A.ty) * u } };
      let sx = smp[0].tx, sy = smp[0].ty, vx = 0, vy = 0;
      const loops = P.cycle ? 4 : 1, rec = [];
      for (let lp = 0; lp < loops; lp++) {
        const last = lp === loops - 1;
        for (let f = 0; f < N + (last ? 1 : 0); f++) {
          const q = at(f);
          if (last) rec.push(wrap(Math.atan2(sy - q.py, sx - q.px) * 180 / Math.PI - Math.atan2(q.ty - q.py, q.tx - q.px) * 180 / Math.PI));
          if (f === N) break;
          for (let s = 0; s < sub; s++) {
            const g = at(f + (s + 1) / sub), h = dt / sub;
            const ax = w * w * (g.tx - sx) - 2 * z * w * vx + P.wind, ay = w * w * (g.ty - sy) - 2 * z * w * vy - P.grav;
            vx += ax * h; vy += ay * h; sx += vx * h; sy += vy * h;
            const dx = sx - g.px, dy = sy - g.py, d = Math.hypot(dx, dy) || 1e-6, ux = dx / d, uy = dy / d;
            sx = g.px + ux * L; sy = g.py + uy * L;
            const vr = vx * ux + vy * uy; vx -= vr * ux; vy -= vr * uy;   // bỏ vận tốc dọc xương (giữ độ dài)
          }
        }
      }
      if (P.cycle) { const dl = rec[N] - rec[0]; for (let f = 0; f <= N; f++) rec[f] -= dl * f / N }   // nối loop
      offs[b.data.name] = rec.map((v, f) => v * P.scale * smp[f].flip);
    }
    return { N, F, offs, base, skipped, targets: targets.map(b => b.data.name) };
  }

  $("phRun").onclick = async () => {
    if (!player || !cur) return;
    if (!P.bones.length) return setStatus("chưa chọn xương cho Physics", "bad");
    if (ed.dirty.size) return setStatus("đang sửa dở: Key pose hoặc Bỏ sửa trước khi chạy Physics", "bad");
    let r, S;
    try { S = await stored(); r = simulate(S.old) } catch (e) { return setStatus("Physics lỗi: " + e.message, "bad") }
    if (!r.targets.length) return setStatus("các xương đã chọn đều nằm trong chuỗi IK (IK quyết định góc): " + r.skipped.join(", "), "bad");
    const fr = []; for (let f = 0; f < r.N; f += P.step) fr.push(f); if (fr[fr.length - 1] !== r.N) fr.push(r.N);
    const items = r.targets.map(n => ({ bone: n, channel: "rotate",
      keys: fr.map(f => ({ time: +(f / r.F).toFixed(4), value: +(r.base[n][f] + r.offs[n][f]).toFixed(3) })) }));
    const peak = Math.max(...r.targets.map(n => Math.max(...r.offs[n].map(Math.abs))));
    try {
      const physics = {};
      for (const n of r.targets) physics[n] = { offs: r.offs[n], src: S.old[n] ? null : (S.raw.animations?.[curAnim()]?.bones?.[n]?.rotate || []) };
      await edPost("/api/spine/timelines", { json: cur.json, anim: curAnim(), items, physics,
        what: "Physics " + r.targets.length + " xương (mềm " + P.soft + ", mạnh " + P.scale + ")" });
      await animReloadLive(curAnim());
      setStatus("đã nướng overlap cho " + r.targets.join(", ") + " · lệch lớn nhất " + peak.toFixed(1) + "° · " + fr.length + " key / xương"
        + (r.skipped.length ? " · bỏ qua (IK): " + r.skipped.join(", ") : "") + " · Ctrl+Z lùi · " + hhmmss(), "ok");
    } catch (e) { setStatus("ghi Physics lỗi: " + e.message, "bad") }
  };
  $("phOff").onclick = async () => {
    if (!player || !cur || !P.bones.length) return setStatus("chọn xương trước", "bad");
    try {
      const S = await stored(), names = P.bones.filter(n => S.old[n]);
      if (!names.length) return setStatus("các xương đã chọn chưa có Physics", "bad");
      const physics = {}; names.forEach(n => physics[n] = null);
      await edPost("/api/spine/timelines", { json: cur.json, anim: curAnim(), physics, what: "Bỏ physics " + names.join(", "),
        items: names.map(n => ({ bone: n, channel: "rotate", keys: S.old[n].src || [] })) });
      await animReloadLive(curAnim());
      setStatus("đã bỏ physics: " + names.join(", ") + " (về key gốc) · Ctrl+Z lùi", "ok");
    } catch (e) { setStatus("bỏ physics lỗi: " + e.message, "bad") }
  };
  window.spinePhysics = { P, simulate, stored, renderList };
})();
