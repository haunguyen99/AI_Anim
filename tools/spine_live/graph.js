// Spine Live: graph editor xổ dưới timeline (kiểu Spine / SyncSketch).
// Curve các kênh của xương đang chọn (xoay, dời X / Y, scale), trục ngang khớp timeline.
// Kéo key: đổi giá trị (dọc) và frame (ngang); kéo tay cầm bezier; nhấp đúp: thêm key; Delete: xoá key.
// Chọn nhiều key (người dùng 2026-10-30): kéo trên chỗ trống = khung quét; Shift + bấm / quét = thêm / bớt; Ctrl+A = chọn hết;
// kéo một key đang chọn = dời cả nhóm; Delete / nút curve áp cho cả nhóm; mỗi lần thả chuột = một lần ghi (một bước Hoàn tác).
// Mỗi lần thả chuột / bấm nút: ghi cả kênh vào JSON (POST /api/spine/timeline, có backup, Ctrl+Z lùi được).
// Dùng biến chung của index.html: player, cur, ed, tl, TL_PAD, fpsOf, edPost, build, snapshot, stamp, setStatus.
(() => {
  const CH = [   // [kênh, trường, nhãn, màu]
    ["rotate", "value", "Xoay", "#ffd21a"], ["translate", "x", "Dời X", "#ff5a4f"], ["translate", "y", "Dời Y", "#3ddc6a"],
    ["scale", "x", "Scale X", "#ff9de6"], ["scale", "y", "Scale Y", "#6fd3ff"],
    ["shear", "x", "Shear X", "#ffb35a"], ["shear", "y", "Shear Y", "#b48cff"]];
  const G = { open: false, raw: null, rawFor: null, sel: null, drag: null, show: new Set(["rotate.value", "translate.x", "translate.y", "scale.x", "scale.y", "shear.x", "shear.y"]),
              y0: 0, y1: 1, hover: null, ms: [], box: null };   // ms: key đang chọn [{id, k}] (k = chính object key)
  // ---- biểu tượng kiểu curve (2026-11-04: "UI của các chức năng mượt, vừa,... cần đổi lại thành các nút như hình") ----
  const svg = (body) => `<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`;
  const dot = (x, y) => `<rect x="${x - 1.6}" y="${y - 1.6}" width="3.2" height="3.2" fill="currentColor" stroke="none"/>`;
  const CVI = window.CVI = {
    stepped: svg(`<path d="M2.5 13.5H9.5V2.5H13.5"/>${dot(2.5, 13.5)}${dot(13.5, 2.5)}`),
    linear: svg(`<path d="M2.5 13.5L13.5 2.5"/>${dot(2.5, 13.5)}${dot(13.5, 2.5)}`),
    bezier: svg(`<path d="M2.5 13.5C8.5 13.5 7.5 2.5 13.5 2.5"/>${dot(2.5, 13.5)}${dot(13.5, 2.5)}`),
    smooth: svg(`<path d="M2 12C4.5 4 7 4 8 8S11.5 12 14 4"/><path d="M5.5 8H10.5" stroke-dasharray="1.5 1.5"/>${dot(8, 8)}`),
    del: svg(`<path d="M3 4.5H13M6.5 4.5V3H9.5V4.5M4.5 4.5L5.2 13.5H10.8L11.5 4.5"/>`),
    fit: svg(`<path d="M2.5 5.5V2.5H5.5M10.5 2.5H13.5V5.5M13.5 10.5V13.5H10.5M5.5 13.5H2.5V10.5"/><path d="M8 5V11"/>`),
  };
  const cst = document.createElement("style");
  cst.textContent = `.cvseg{display:inline-flex;gap:2px;padding:2px;border-radius:7px;background:#0003}
    .cvi{width:28px;height:24px;padding:0;display:inline-flex;align-items:center;justify-content:center;border-radius:5px;color:var(--fg)}
    .cvi.on{background:#2a7fd4;border-color:#4aa3ff;color:#fff}`;
  document.head.appendChild(cst);
  // Properties: ô chọn curve khi Key (Ease / Linear / Stepped) -> 3 nút biểu tượng; ô select giữ giá trị (ẩn), các chỗ Key vẫn đọc nó
  (() => {
    const sel = document.getElementById("edCurve"); if (!sel) return;
    const grp = document.createElement("span"); grp.className = "cvseg"; grp.id = "edCurveIcons";
    grp.innerHTML = [["stepped", "Stepped: key mới giữ nguyên tới key sau"], ["linear", "Linear: key mới nối thẳng"], ["ease", "Bezier (ease): key mới nối mượt"]]
      .map(([v, t]) => `<button class="cvi" data-v="${v}" title="${t}">${CVI[v === "ease" ? "bezier" : v]}</button>`).join("");
    sel.after(grp); sel.hidden = true;
    const sync = () => grp.querySelectorAll(".cvi").forEach(b => b.classList.toggle("on", b.dataset.v === sel.value));
    grp.onclick = ev => { const b = ev.target.closest(".cvi"); if (!b) return; sel.value = b.dataset.v; sel.dispatchEvent(new Event("change")); sync() };
    sel.addEventListener("change", sync); sync();
  })();
  // ---- DOM ----
  document.body.style.gridTemplateRows = "auto minmax(0,1fr) auto auto";
  const wrap = document.createElement("section"); wrap.id = "graphWrap"; wrap.hidden = true; wrap.className = "animOnly";
  wrap.innerHTML = `
    <div id="gBar">
      <b id="gTitle">Graph</b>
      <span id="gChans"></span>
      <span class="gsep"></span>
      <span class="cvseg">
      <button class="cvi" data-k="stepped" title="Stepped: giữ nguyên tới key sau">${CVI.stepped}</button><button class="cvi" data-k="linear" title="Linear: đoạn sau key thẳng">${CVI.linear}</button><button class="cvi" data-k="bezier" title="Bezier: ease vào / ra (tay cầm nằm ngang)">${CVI.bezier}</button><button class="cvi" data-k="smooth" title="Mượt: tay cầm hai bên key theo độ dốc hai key kề">${CVI.smooth}</button>
      </span>
      <button class="cvi" id="gDel" title="Xoá key đang chọn (Delete)">${CVI.del}</button>
      <button class="cvi" id="gFitY" title="Vừa trục dọc">${CVI.fit}</button>
      <button id="gReduce" title="Giảm key: bỏ key thừa kiểu mocap, chỉ giữ key chính, chuyển động giữ y nguyên (lệch ≤ 0.15° / 0.3 px mỗi frame). Xương đang chọn, hoặc cả anim nếu chưa chọn xương. Chỉ anim đang mở · Hoàn tác được">Giảm key</button>
      <span id="gInfo"></span>
    </div>
    <canvas id="graph" tabindex="0" title="Kéo key / tay cầm · kéo chỗ trống: quét chọn nhiều key (Shift: thêm / bớt, Ctrl+A: hết) · nhấp đúp: thêm key · Delete: xoá key · cuộn: giãn ngang · Alt+cuộn: giãn dọc · Ctrl+cuộn: cả hai · kéo chuột phải / giữa: dời"></canvas>`;
  document.querySelector("#tlBar").after(wrap);
  const st = document.createElement("style");
  st.textContent = `#graphWrap{background:var(--panel);border-top:1px solid var(--line);padding:4px 12px 8px}
    #gBar{display:flex;gap:6px;align-items:center;flex-wrap:wrap;font-size:12px;margin-bottom:4px}
    #gBar .gsep{width:1px;height:16px;background:var(--line)} #gInfo{color:var(--mute);margin-left:auto}
    #gChans label{margin-right:6px} #graph{display:block;width:100%;height:220px;border-radius:6px;outline:none;cursor:default}
    #tlGraph.on{border-color:var(--accent);color:var(--accent)}`;
  document.head.appendChild(st);
  const btn = document.createElement("button"); btn.id = "tlGraph"; btn.textContent = "Graph ▾";
  btn.title = "Xổ graph editor: chỉnh curve của xương đang chọn";
  document.querySelector("#tlFit").after(btn);
  const cv = wrap.querySelector("#graph");
  btn.onclick = () => { G.open = !G.open; wrap.hidden = !G.open; btn.classList.toggle("on", G.open); btn.textContent = G.open ? "Graph ▴" : "Graph ▾"; G.fitY = true };

  // ---- dữ liệu ----
  async function ensureRaw() {
    if (!player || !cur || G.rawFor === player) return;
    G.rawFor = player;
    try { G.raw = await (await fetch("/spine-live/f/" + cur.json, { cache: "no-store" })).json() } catch { G.raw = null }
    G.fitY = true;
  }
  const F = () => fpsOf();
  const T = k => k.time || 0;
  const curAnimName = () => player?.animationState?.getCurrent(0)?.animation.name || "";
  function chans() {   // kênh của xương đang chọn: [{kind, field, fi, label, color, keys}]
    const b = ed.sel?.data.name, an = G.raw?.animations?.[curAnimName()];
    if (!b || !an) return [];
    const tl0 = an.bones?.[b] || {};
    return CH.filter(([k]) => tl0[k]?.length).map(([kind, field, label, color]) => ({
      kind, field, fi: kind === "rotate" ? 0 : field === "x" ? 0 : 1, label, color, keys: tl0[kind], id: kind + "." + field }));
  }
  const nf = k => ({ rotate: 1, translate: 2, scale: 2, shear: 2 })[k] || 1;
  const dv = (kind, field) => kind === "scale" ? 1 : 0;
  const val = (k, c) => k[c.field] ?? dv(c.kind, c.field);
  function bez(c, t1, v1, t2, v2, t) {   // giá trị curve bezier (thời gian, giá trị tuyệt đối) tại t
    const [cx1, cy1, cx2, cy2] = c; let lo = 0, hi = 1;
    for (let i = 0; i < 40; i++) { const s = (lo + hi) / 2, x = (1 - s) ** 3 * t1 + 3 * (1 - s) ** 2 * s * cx1 + 3 * (1 - s) * s * s * cx2 + s ** 3 * t2; x < t ? lo = s : hi = s }
    const s = (lo + hi) / 2; return (1 - s) ** 3 * v1 + 3 * (1 - s) ** 2 * s * cy1 + 3 * (1 - s) * s * s * cy2 + s ** 3 * v2;
  }
  function evalAt(c, t) {
    const ks = c.keys; if (!ks.length) return dv(c.kind, c.field);
    if (t <= T(ks[0])) return val(ks[0], c);
    for (let i = 0; i + 1 < ks.length; i++) {
      const a = ks[i], b = ks[i + 1]; if (t > T(b)) continue;
      if (a.curve === "stepped") return val(a, c);
      if (Array.isArray(a.curve)) return bez(a.curve.slice(c.fi * 4, c.fi * 4 + 4), T(a), val(a, c), T(b), val(b, c), t);
      return val(a, c) + (val(b, c) - val(a, c)) * (t - T(a)) / ((T(b) - T(a)) || 1);
    }
    return val(ks[ks.length - 1], c);
  }

  // ---- toạ độ: ngang khớp timeline ----
  function geo() {
    const r = cv.getBoundingClientRect(), tr = document.getElementById("tl").getBoundingClientRect();
    return { L: tr.left - r.left, W: r.width, H: r.height, top: 10, bot: r.height - 16 };
  }
  const sx = (g, t) => g.L + TL_PAD + (t * F() - tl.off) * tl.ppf;
  const tx = (g, x) => ((x - g.L - TL_PAD) / tl.ppf + tl.off) / F();
  const sy = (g, v) => g.bot - (v - G.y0) / ((G.y1 - G.y0) || 1) * (g.bot - g.top);
  const vy = (g, y) => G.y0 + (g.bot - y) / (g.bot - g.top) * ((G.y1 - G.y0) || 1);
  function fitY(cs) {
    let lo = Infinity, hi = -Infinity;
    for (const c of cs) { if (!G.show.has(c.id)) continue;
      for (const k of c.keys) { lo = Math.min(lo, val(k, c)); hi = Math.max(hi, val(k, c));
        if (Array.isArray(k.curve)) { const q = k.curve.slice(c.fi * 4, c.fi * 4 + 4); lo = Math.min(lo, q[1], q[3]); hi = Math.max(hi, q[1], q[3]) } } }
    if (!isFinite(lo)) { lo = -1; hi = 1 }
    if (hi - lo < 1) { const m = (hi + lo) / 2; lo = m - 0.5; hi = m + 0.5 }
    const p = (hi - lo) * 0.12; G.y0 = lo - p; G.y1 = hi + p; G.fitY = false;
  }

  // ---- vẽ ----
  function draw() {
    if (!G.open || document.hidden) return;
    ensureRaw();
    const dpr = devicePixelRatio || 1, W = cv.clientWidth, H = cv.clientHeight;
    if (!W) return;
    if (cv.width !== Math.round(W * dpr) || cv.height !== Math.round(H * dpr)) { cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr) }
    const c2 = cv.getContext("2d"); c2.setTransform(dpr, 0, 0, dpr, 0, 0);
    const css = getComputedStyle(document.body), col = n => css.getPropertyValue(n).trim() || "#888";
    c2.fillStyle = col("--raise"); c2.fillRect(0, 0, W, H);
    const g = geo(), cs = chans();
    // tên kênh + ô bật / tắt
    const ids = cs.map(c => c.id).join(",");
    if (G.chanIds !== ids) {
      G.chanIds = ids;
      document.getElementById("gChans").innerHTML = cs.map(c => `<label style="color:${c.color}"><input type="checkbox" data-id="${c.id}" ${G.show.has(c.id) ? "checked" : ""}>${c.label}</label>`).join("");
      document.querySelectorAll("#gChans input").forEach(i => i.onchange = () => { i.checked ? G.show.add(i.dataset.id) : G.show.delete(i.dataset.id); G.fitY = true });
      G.fitY = true;
    }
    document.getElementById("gTitle").textContent = ed.sel ? "Graph: " + ed.sel.data.name + " · " + curAnimName() : "Graph: bấm chọn một xương";
    if (!cs.length) {
      c2.fillStyle = col("--mute"); c2.font = "12px system-ui"; c2.fillText(ed.sel ? "Xương này chưa có key trong anim (Key pose để tạo)" : "Chọn xương để xem curve", 16, 24); return;
    }
    if (G.fitY) fitY(cs);
    const N = tlTotal();
    c2.fillStyle = col("--bg"); c2.fillRect(sx(g, 0), 0, sx(g, N / F()) - sx(g, 0), H);
    // lưới dọc theo frame (cùng bước với timeline) + lưới ngang giá trị
    const step = [1, 2, 5, 10, 20, 50, 100].find(s => s * tl.ppf >= 34) || 200;
    c2.strokeStyle = col("--line"); c2.lineWidth = 1; c2.font = "10px ui-monospace,Consolas,monospace";
    for (let f = Math.max(0, Math.floor(tl.off / step) * step); f <= N; f += step) { const x = Math.round(sx(g, f / F())) + 0.5; c2.beginPath(); c2.moveTo(x, 0); c2.lineTo(x, H); c2.stroke() }
    const vr = G.y1 - G.y0, vs = [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500].find(s => (g.bot - g.top) * s / vr >= 26) || 1000;
    c2.fillStyle = col("--mute"); c2.textAlign = "left"; c2.textBaseline = "middle";
    for (let v = Math.ceil(G.y0 / vs) * vs; v <= G.y1; v += vs) { const y = Math.round(sy(g, v)) + 0.5;
      c2.globalAlpha = Math.abs(v) < 1e-9 ? 0.9 : 0.45; c2.beginPath(); c2.moveTo(0, y); c2.lineTo(W, y); c2.stroke(); c2.globalAlpha = 1;
      c2.fillText(String(+v.toFixed(2)), 4, y - 6) }
    // curve
    for (const c of cs) {
      if (!G.show.has(c.id)) continue;
      const ks = c.keys; c2.strokeStyle = c.color; c2.lineWidth = 2; c2.beginPath();
      c2.moveTo(0, sy(g, val(ks[0], c))); c2.lineTo(sx(g, T(ks[0])), sy(g, val(ks[0], c)));
      for (let i = 0; i + 1 < ks.length; i++) {
        const a = ks[i], b = ks[i + 1], x2 = sx(g, T(b)), y2 = sy(g, val(b, c));
        if (a.curve === "stepped") { c2.lineTo(x2, sy(g, val(a, c))); c2.lineTo(x2, y2) }
        else if (Array.isArray(a.curve)) { const q = a.curve.slice(c.fi * 4, c.fi * 4 + 4); c2.bezierCurveTo(sx(g, q[0]), sy(g, q[1]), sx(g, q[2]), sy(g, q[3]), x2, y2) }
        else c2.lineTo(x2, y2);
      }
      c2.lineTo(W, sy(g, val(ks[ks.length - 1], c))); c2.stroke(); c2.lineWidth = 1;
      // key + tay cầm của key đang chọn
      ks.forEach((k, i) => {
        const x = sx(g, T(k)), y = sy(g, val(k, c)), prim = G.sel && G.sel.id === c.id && G.sel.i === i, on = prim || isSel(c, k);
        if (prim && G.ms.length <= 1) {
          c2.strokeStyle = "#fff"; c2.fillStyle = "#fff";
          for (const h of handles(c, i)) { c2.beginPath(); c2.moveTo(x, y); c2.lineTo(sx(g, h.t), sy(g, h.v)); c2.stroke(); c2.beginPath(); c2.arc(sx(g, h.t), sy(g, h.v), 4.5, 0, 7); c2.fill() }
        }
        c2.fillStyle = "#000"; c2.fillRect(x - 5, y - 5, 10, 10); c2.fillStyle = on ? "#fff" : c.color; c2.fillRect(x - 3.5, y - 3.5, 7, 7);
      });
    }
    if (G.box) {   // khung quét
      const b = G.box; c2.fillStyle = "rgba(111,211,255,0.12)"; c2.strokeStyle = "#6fd3ff"; c2.setLineDash([4, 3]);
      c2.fillRect(Math.min(b.x0, b.x1), Math.min(b.y0, b.y1), Math.abs(b.x1 - b.x0), Math.abs(b.y1 - b.y0));
      c2.strokeRect(Math.min(b.x0, b.x1) + 0.5, Math.min(b.y0, b.y1) + 0.5, Math.abs(b.x1 - b.x0), Math.abs(b.y1 - b.y0)); c2.setLineDash([]);
    }
    // đầu phát
    const x = sx(g, player.playTime || 0); c2.strokeStyle = "#ff3b30"; c2.lineWidth = 2; c2.beginPath(); c2.moveTo(x, 0); c2.lineTo(x, H); c2.stroke(); c2.lineWidth = 1;
    const s = G.sel && cs.find(c => c.id === G.sel.id), k = s?.keys[G.sel.i];
    // nút kiểu curve sáng theo key đang chọn
    const ktype = !k ? "" : k.curve === "stepped" ? "stepped" : Array.isArray(k.curve) ? "bezier" : (G.sel.i + 1 < s.keys.length ? "linear" : "");
    wrap.querySelectorAll(".cvseg .cvi").forEach(b => b.classList.toggle("on", b.dataset.k === ktype));
    document.getElementById("gInfo").textContent = G.ms.length > 1 ? G.ms.length + " key đang chọn · kéo một key để dời cả nhóm · Delete xoá" : k ? `${s.label} · F${Math.round(T(k) * F())} = ${(+val(k, s)).toFixed(2)} · ${k.curve === "stepped" ? "stepped" : Array.isArray(k.curve) ? "bezier" : (G.sel.i + 1 < s.keys.length ? "linear" : "key cuối")}` : "";
  }
  const isSel = (c, k) => G.ms.some(m => m.id === c.id && m.k === k);
  function selList() {   // [{c, i, k}] của key đang chọn còn tồn tại
    const cs = chans(), out = [];
    for (const m of G.ms) { const c = cs.find(q => q.id === m.id); const i = c ? c.keys.indexOf(m.k) : -1; if (i >= 0) out.push({ c, i, k: m.k }) }
    return out;
  }
  function selectOne(c, i, add) {
    const k = c.keys[i];
    if (add) { if (isSel(c, k)) G.ms = G.ms.filter(m => !(m.id === c.id && m.k === k)); else G.ms.push({ id: c.id, k }) }
    else if (!isSel(c, k)) G.ms = [{ id: c.id, k }];
    G.sel = { id: c.id, i };
  }
  function handles(c, i) {   // tay cầm ra (curve của key i) và vào (curve của key i-1)
    const ks = c.keys, out = [];
    if (Array.isArray(ks[i].curve) && i + 1 < ks.length) out.push({ side: "out", i, t: ks[i].curve[c.fi * 4], v: ks[i].curve[c.fi * 4 + 1] });
    if (i > 0 && Array.isArray(ks[i - 1].curve)) out.push({ side: "in", i: i - 1, t: ks[i - 1].curve[c.fi * 4 + 2], v: ks[i - 1].curve[c.fi * 4 + 3] });
    return out;
  }
  (function loop() { try { draw() } catch (e) { console.warn(e) } requestAnimationFrame(loop) })();
  setInterval(() => { try { if (G.open) draw() } catch {} }, 250);

  // ---- sửa ----
  function toBezier(k, k2, kind) {   // đoạn linear -> bezier tương đương (để kéo tay cầm)
    if (Array.isArray(k.curve)) return;
    const c = []; const flds = kind === "rotate" ? ["value"] : ["x", "y"];
    for (const f of flds) { const v1 = k[f] ?? dv(kind, f), v2 = k2[f] ?? dv(kind, f), t1 = T(k), t2 = T(k2);
      c.push(t1 + (t2 - t1) / 3, k.curve === "stepped" ? v1 : v1 + (v2 - v1) / 3, t1 + 2 * (t2 - t1) / 3, k.curve === "stepped" ? v1 : v1 + 2 * (v2 - v1) / 3) }
    k.curve = c;
  }
  function linkOpposite(c, h, t, v) {   // tay cầm bên kia của cùng key: cùng độ dốc (thẳng hàng qua key)
    const ks = c.keys, fi = c.fi;
    const ki = h.side === "out" ? h.i : h.i + 1, key = ks[ki];      // key mà tay cầm đang kéo bám vào
    const tk = T(key), vk = val(key, c);
    if (Math.abs(t - tk) < 1e-6) return;
    const s = (v - vk) / (t - tk);
    let seg, o;   // đoạn chứa tay cầm bên kia + vị trí trong curve
    if (h.side === "out") { if (ki < 1) return; seg = ks[ki - 1]; o = fi * 4 + 2 }
    else { if (ki + 1 >= ks.length) return; seg = ks[ki]; o = fi * 4 }
    if (seg.curve === "stepped") return;                              // stepped: không có tay cầm
    if (!Array.isArray(seg.curve)) toBezier(seg, ks[ks.indexOf(seg) + 1], c.kind);
    const t2 = seg.curve[o]; seg.curve[o + 1] = vk + s * (t2 - tk);
  }
  function hit(ev) {
    const g = geo(), r = cv.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top, cs = chans();
    if (G.sel) { const c = cs.find(q => q.id === G.sel.id); if (c && c.keys[G.sel.i]) for (const h of handles(c, G.sel.i)) if (Math.hypot(sx(g, h.t) - x, sy(g, h.v) - y) < 8) return { type: "handle", c, h } }
    let best = null, bd = 9;
    for (const c of cs) { if (!G.show.has(c.id)) continue; c.keys.forEach((k, i) => { const d = Math.hypot(sx(g, T(k)) - x, sy(g, val(k, c)) - y); if (d < bd) { bd = d; best = { type: "key", c, i } } }) }
    return best;
  }
  function blocked() { if (ed.dirty.size) { setStatus("đang có xương sửa chưa key: Key pose hoặc Bỏ sửa trước khi chỉnh curve", "bad"); return true } return false }
  // Realtime (người dùng 2026-10-30: "sửa key ở graph editor không thể chỉnh realtime với bên trên"): dựng lại anim đang
  // xem từ dữ liệu graph đang sửa (SkeletonJson.readAnimation) rồi thay timeline của anim trong player, áp ngay tại frame
  // đang xem. Gọi mỗi nhịp kéo (gộp theo khung hình) và sau mỗi lần ghi; không nạp lại cả player nữa.
  let livePending = false;
  function liveApply() {
    if (!player || !G.raw) return;
    const name = curAnimName(), map = G.raw.animations?.[name], sd = player.skeleton.data;
    const anim = sd.findAnimation(name); if (!map || !anim) return;
    const n0 = sd.animations.length;
    new spine.SkeletonJson({}).readAnimation(map, name, sd);
    const na = sd.animations.splice(n0, 1)[0]; if (!na) return;
    anim.setTimelines(na.timelines); anim.duration = na.duration;
    const st = player.animationState; st.animationsChanged = true;
    tl.cache = new WeakMap();
    const e = st.getCurrent(0);
    if (e) { e.timelinesRotation.length = 0; player.skeleton.setBonesToSetupPose(); setTrack(e, player.playTime || 0); st.apply(player.skeleton); player.skeleton.updateWorldTransform(2) }
  }
  function liveSoon() { if (livePending) return; livePending = true; requestAnimationFrame(() => { livePending = false; try { liveApply() } catch (e) { console.warn("graph live", e) } }) }
  async function save(c, what) {
    try {
      liveApply();
      await edPost("/api/spine/timeline", { json: cur.json, anim: curAnimName(), bone: ed.sel.data.name, channel: c.kind, keys: c.keys });
      // file vừa ghi chính là thứ đang hiện: nhận dấu thời gian mới để trang không nạp lại cả player (chớp, mất chọn)
      try { stamp = (await (await fetch("/api/spine/stat?json=" + encodeURIComponent(cur.json), { cache: "no-store" })).json()).t } catch {}
      setStatus("đã ghi curve " + c.kind + " của " + ed.sel.data.name + (what ? " (" + what + ")" : "") + " · " + hhmmss(), "ok");
      window.histLoad?.();
    } catch (e) { setStatus("ghi curve lỗi: " + e.message, "bad"); G.rawFor = null; stamp = null; build(snapshot()) }
  }
  async function saveMany(kinds, what) {   // ghi mọi kênh (rotate / translate / scale) bị đổi của xương đang chọn, một lần
    try {
      liveApply();
      const an = G.raw.animations[curAnimName()], bone = ed.sel.data.name, tl0 = an.bones[bone] || {};
      const items = [...kinds].map(kind => ({ bone, channel: kind, keys: tl0[kind] || [] }));
      await edPost("/api/spine/timelines", { json: cur.json, anim: curAnimName(), items, what: "Graph: " + what + " (" + bone + ")" });
      try { stamp = (await (await fetch("/api/spine/stat?json=" + encodeURIComponent(cur.json), { cache: "no-store" })).json()).t } catch {}
      setStatus("đã ghi " + what + " · " + bone + " · " + hhmmss(), "ok");
      window.histLoad?.();
    } catch (e) { setStatus("ghi curve lỗi: " + e.message, "bad"); G.rawFor = null; stamp = null; build(snapshot()) }
  }
  function multiStart(ev) {   // chụp trạng thái của mọi key đang chọn (và curve key kề trước) để dời từ gốc mỗi nhịp kéo
    const g = geo(), r = cv.getBoundingClientRect(), sl = selList();
    const objs = new Map();   // key object -> {t, curve, prev, prevCurve, fields: {field: v0}, kind, list}
    for (const { c, i, k } of sl) {
      if (!objs.has(k)) objs.set(k, { t: T(k), curve: Array.isArray(k.curve) ? k.curve.slice() : k.curve, prev: c.keys[i - 1] || null,
        prevCurve: c.keys[i - 1] && Array.isArray(c.keys[i - 1].curve) ? c.keys[i - 1].curve.slice() : null, fields: {}, kind: c.kind, list: c.keys });
      objs.get(k).fields[c.fi] = { f: c.field, v: val(k, c) };
    }
    return { objs, t0: tx(g, ev.clientX - r.left), v0: vy(g, ev.clientY - r.top), lastDt: 0 };
  }
  function multiApply(M, dt, dvv) {
    for (const [k, o] of M.objs) {   // về gốc
      k.time = +o.t.toFixed(4); if (o.curve !== undefined) k.curve = Array.isArray(o.curve) ? o.curve.slice() : o.curve; else delete k.curve;
      for (const fi in o.fields) k[o.fields[fi].f] = o.fields[fi].v;
      if (o.prev && o.prevCurve) o.prev.curve = o.prevCurve.slice();
    }
    for (const [k, o] of M.objs) {
      k.time = +(o.t + dt).toFixed(4);
      for (const fi in o.fields) {
        k[o.fields[fi].f] = o.fields[fi].v + dvv;
        if (Array.isArray(k.curve)) k.curve[fi * 4 + 1] += dvv;
        if (o.prev && Array.isArray(o.prev.curve) && !M.objs.has(o.prev)) o.prev.curve[fi * 4 + 3] += dvv;
      }
      if (Array.isArray(k.curve)) for (let j = 0; j < k.curve.length; j += 4) k.curve[j] += dt;
      if (o.prev && Array.isArray(o.prev.curve) && !M.objs.has(o.prev)) for (let j = 2; j < o.prev.curve.length; j += 4) o.prev.curve[j] += dt;
    }
    for (const o of M.objs.values()) { const L = o.list; for (let i = 1; i < L.length; i++) if (T(L[i]) <= T(L[i - 1]) + 1e-4) return false }
    return [...M.objs.keys()].every(k => T(k) >= 0);
  }
  cv.addEventListener("pointerdown", ev => {
    if (document.activeElement && /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) document.activeElement.blur();
    if (ev.button === 1 && ev.altKey) {   // Alt + kéo chuột giữa lên / xuống: giãn trục dọc quanh điểm bấm (2026-11-04)
      ev.preventDefault(); const g = geo(), r = cv.getBoundingClientRect();
      G.zy = { y: ev.clientY, y0: G.y0, y1: G.y1, v: vy(g, ev.clientY - r.top) }; try { cv.setPointerCapture(ev.pointerId) } catch {} return;
    }
    if (ev.button === 1 || ev.button === 2) {   // chuột giữa / phải: dời khung (ngang = frame, dọc = giá trị)
      ev.preventDefault(); G.pan = { x: ev.clientX, y: ev.clientY, off: tl.off, y0: G.y0, y1: G.y1 }; try { cv.setPointerCapture(ev.pointerId) } catch {} return;
    }
    if (ev.button !== 0 || !player || blocked()) return;
    cv.focus();
    const h = hit(ev), r = cv.getBoundingClientRect();
    if (!h) {   // chỗ trống: khung quét (Shift: thêm vào lựa chọn)
      if (!ev.shiftKey) { G.ms = []; G.sel = null }
      G.box = { x0: ev.clientX - r.left, y0: ev.clientY - r.top, x1: ev.clientX - r.left, y1: ev.clientY - r.top, add: ev.shiftKey };
      try { cv.setPointerCapture(ev.pointerId) } catch {} return;
    }
    if (h.type === "key") {
      selectOne(h.c, h.i, ev.shiftKey);
      if (ev.shiftKey) return;
      if (G.ms.length > 1) { G.drag = { type: "multi", M: multiStart(ev), moved: false }; try { cv.setPointerCapture(ev.pointerId) } catch {} return }
    }
    G.drag = { ...h, moved: false }; try { cv.setPointerCapture(ev.pointerId) } catch {}
  });
  cv.addEventListener("pointermove", ev => {
    if (G.zy) { const f = Math.pow(1.01, ev.clientY - G.zy.y), v = G.zy.v; G.y0 = v + (G.zy.y0 - v) * f; G.y1 = v + (G.zy.y1 - v) * f; return }
    if (G.pan) {
      const g = geo(), k = (G.pan.y1 - G.pan.y0) / (g.bot - g.top), dy = (ev.clientY - G.pan.y) * k;
      tl.fit = false; tl.off = G.pan.off - (ev.clientX - G.pan.x) / tl.ppf; G.y0 = G.pan.y0 + dy; G.y1 = G.pan.y1 + dy; return;
    }
    if (G.box) { const r = cv.getBoundingClientRect(); G.box.x1 = ev.clientX - r.left; G.box.y1 = ev.clientY - r.top; return }
    const d = G.drag; if (!d) return;
    if (d.type === "multi") {   // dời cả nhóm: frame (làm tròn) + giá trị; Shift: chỉ giá trị; chặn vượt key kề
      const g = geo(), r = cv.getBoundingClientRect(), M = d.M;
      let dt = ev.shiftKey ? 0 : Math.round((tx(g, ev.clientX - r.left) - M.t0) * F()) / F();
      const dvv = vy(g, ev.clientY - r.top) - M.v0;
      if (!multiApply(M, dt, dvv)) { dt = M.lastDt; multiApply(M, dt, dvv) } else M.lastDt = dt;
      d.moved = true; liveSoon(); return;
    }
    const g = geo(), r = cv.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top, ks = d.c.keys, fi = d.c.fi;
    if (d.type === "key") {
      const k = ks[d.i], v = vy(g, y), dvv = v - val(k, d.c);
      let t = Math.round(tx(g, x) * F()) / F();
      const lo = d.i > 0 ? T(ks[d.i - 1]) + 1 / F() : 0, hi = d.i + 1 < ks.length ? T(ks[d.i + 1]) - 1 / F() : Infinity;
      if (ev.shiftKey) t = T(k);   // Shift: chỉ đổi giá trị
      t = Math.max(lo, Math.min(hi, t)); const dt = t - T(k);
      k[d.c.field] = v; k.time = +t.toFixed(4);
      if (Array.isArray(k.curve)) { for (let j = 0; j < k.curve.length; j += 4) k.curve[j] += dt; k.curve[fi * 4 + 1] += dvv }
      const p = ks[d.i - 1]; if (p && Array.isArray(p.curve)) { for (let j = 2; j < p.curve.length; j += 4) p.curve[j] += dt; p.curve[fi * 4 + 3] += dvv }
    } else {
      const h = d.h, k = ks[h.i], k2 = ks[h.i + 1]; toBezier(k, k2, d.c.kind);
      const t = Math.max(T(k), Math.min(T(k2), tx(g, x))), v = vy(g, y);
      const o = fi * 4 + (h.side === "out" ? 0 : 2);
      k.curve[o] = t; k.curve[o + 1] = v;
      // 2026-11-04 ("curve của các point mặc định sẽ không tách được, chỉ khi ... giữ Alt và di chuyển thì curve mới đc tách ra"):
      // mặc định tay cầm hai bên key dính liền (thẳng hàng qua key, mỗi bên giữ độ dài thời gian của nó); Alt = chỉnh riêng một bên
      if (!ev.altKey) linkOpposite(d.c, h, t, v);
      d.broke = d.broke || ev.altKey;
    }
    d.moved = true; liveSoon();
  });
  cv.addEventListener("contextmenu", ev => ev.preventDefault());
  cv.addEventListener("pointerup", () => {
    if (G.zy) { G.zy = null; return }
    if (G.pan) { G.pan = null; return }
    if (G.box) {   // chọn mọi key trong khung (kênh đang hiện)
      const b = G.box, g = geo(), x0 = Math.min(b.x0, b.x1), x1 = Math.max(b.x0, b.x1), y0 = Math.min(b.y0, b.y1), y1 = Math.max(b.y0, b.y1);
      G.box = null;
      if (x1 - x0 < 3 && y1 - y0 < 3) return;
      for (const c of chans()) { if (!G.show.has(c.id)) continue;
        c.keys.forEach((k, i) => { const x = sx(g, T(k)), y = sy(g, val(k, c));
          if (x >= x0 && x <= x1 && y >= y0 && y <= y1 && !isSel(c, k)) { G.ms.push({ id: c.id, k }); G.sel = { id: c.id, i } } }) }
      setStatus(G.ms.length + " key đang chọn", "ok"); return;
    }
    const d = G.drag; G.drag = null; if (!d?.moved) return;
    if (d.type === "multi") return saveMany(new Set([...d.M.objs.values()].map(o => o.kind)), "dời " + d.M.objs.size + " key");
    save(d.c, d.type === "key" ? "dời key" : "tay cầm");
  });
  cv.addEventListener("dblclick", ev => {   // thêm key ở frame dưới con trỏ, trên kênh gần nhất
    if (!player || blocked()) return;
    const g = geo(), r = cv.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top, cs = chans().filter(c => G.show.has(c.id));
    if (!cs.length) return;
    const t = Math.round(tx(g, x) * F()) / F();
    const c = cs.reduce((a, b) => Math.abs(sy(g, evalAt(b, t)) - y) < Math.abs(sy(g, evalAt(a, t)) - y) ? b : a);
    const ks = c.keys; if (ks.some(k => Math.abs(T(k) - t) < 1e-4)) return;
    const flds = c.kind === "rotate" ? ["value"] : ["x", "y"], nk = { time: +t.toFixed(4) };
    for (const f of flds) nk[f] = +evalAt({ ...c, field: f, fi: f === "y" ? 1 : 0 }, t).toFixed(4);
    const i = ks.filter(k => T(k) < t).length; ks.splice(i, 0, nk);
    // đoạn trước bị chia đôi: đặt lại thành bezier ease (giữ dáng gần đúng) cho cả hai đoạn
    for (const j of [i - 1, i]) if (j >= 0 && j + 1 < ks.length && (Array.isArray(ks[j].curve) || j === i)) { ks[j].curve = undefined; smooth(c, j, true) }
    G.sel = { id: c.id, i }; save(c, "thêm key F" + Math.round(t * F()));
  });
  function smooth(c, i, onlyOut) {   // tay cầm theo độ dốc hai key kề (Catmull-Rom), cho mọi trường của kênh
    const ks = c.keys, flds = c.kind === "rotate" ? ["value"] : ["x", "y"];
    const slope = (j, f) => { const a = ks[Math.max(0, j - 1)], b = ks[Math.min(ks.length - 1, j + 1)]; return (T(b) - T(a)) ? ((b[f] ?? dv(c.kind, f)) - (a[f] ?? dv(c.kind, f))) / (T(b) - T(a)) : 0 };
    for (const j of onlyOut ? [i] : [i - 1, i]) {
      if (j < 0 || j + 1 >= ks.length) continue;
      const a = ks[j], b = ks[j + 1], d = T(b) - T(a), cc = [];
      for (const f of flds) { const va = a[f] ?? dv(c.kind, f), vb = b[f] ?? dv(c.kind, f);
        cc.push(T(a) + d / 3, va + slope(j, f) * d / 3, T(b) - d / 3, vb - slope(j + 1, f) * d / 3) }
      a.curve = cc;
    }
  }
  function curveOne(c, i, kind) {
    const ks = c.keys, k = ks[i];
    if (kind === "smooth") return smooth(c, i, false);
    if (i + 1 >= ks.length) return;
    if (kind === "linear") delete k.curve;
    else if (kind === "stepped") k.curve = "stepped";
    else { const k2 = ks[i + 1], flds = c.kind === "rotate" ? ["value"] : ["x", "y"], d = T(k2) - T(k), cc = [];
      for (const f of flds) cc.push(T(k) + d / 3, k[f] ?? dv(c.kind, f), T(k2) - d / 3, k2[f] ?? dv(c.kind, f));
      k.curve = cc }
  }
  wrap.querySelectorAll("#gBar button[data-k]").forEach(b => b.onclick = () => {
    if (G.ms.length > 1 && !blocked()) {
      const sl = selList(); sl.sort((a, b2) => b2.i - a.i);
      for (const { c, i } of sl) curveOne(c, i, b.dataset.k);
      return saveMany(new Set(sl.map(x => x.c.kind)), b.dataset.k + " cho " + sl.length + " key");
    }
    if (!G.sel || blocked()) return setStatus("chọn một key trên graph trước", "bad");
    const c = chans().find(q => q.id === G.sel.id); if (!c) return;
    const ks = c.keys, i = G.sel.i, k = ks[i], kind = b.dataset.k;
    if (kind === "smooth") smooth(c, i, false);
    else if (i + 1 >= ks.length) return setStatus("key cuối không có đoạn sau", "bad");
    else if (kind === "linear") delete k.curve;
    else if (kind === "stepped") k.curve = "stepped";
    else { const k2 = ks[i + 1], flds = c.kind === "rotate" ? ["value"] : ["x", "y"], d = T(k2) - T(k), cc = [];
      for (const f of flds) cc.push(T(k) + d / 3, k[f] ?? dv(c.kind, f), T(k2) - d / 3, k2[f] ?? dv(c.kind, f));
      k.curve = cc }
    save(c, kind);
  });
  function delKey() {
    if (G.ms.length > 1 && !blocked()) {
      const sl = selList(), kinds = new Set(sl.map(x => x.c.kind)), objs = new Set(sl.map(x => x.k));
      for (const c of chans()) if (kinds.has(c.kind)) { const keep = c.keys.filter(k => !objs.has(k)); c.keys.splice(0, c.keys.length, ...keep) }
      G.ms = []; G.sel = null; return saveMany(kinds, "xoá " + objs.size + " key");
    }
    if (!G.sel || blocked()) return;
    const c = chans().find(q => q.id === G.sel.id); if (!c) return;
    c.keys.splice(G.sel.i, 1); G.sel = null; save(c, "xoá key");
  }
  wrap.querySelector("#gDel").onclick = delKey;
  wrap.querySelector("#gFitY").onclick = () => G.fitY = true;
  // Giảm key (2026-11-05): server lấy mẫu từng frame rồi dựng lại ít key nhất (tools/spine/key_reduce.py), chỉ anim đang mở
  wrap.querySelector("#gReduce").onclick = async () => {
    const anim = curAnimName(), bone = ed.sel?.data.name;
    if (!anim) return setStatus("chưa có anim đang phát", "bad");
    if (!bone && !confirm(`Giảm key cho mọi xương của anim ${anim}?`)) return;
    try {
      const j = await edPost("/api/spine/reduce", { json: cur.json, anim, bones: bone ? [bone] : [] });
      if (!j.channels) return setStatus(`không có kênh nào cần giảm (${bone || anim})`, "");
      G.rawFor = null; stamp = null; await build(snapshot());
      setStatus(`giảm key ${bone || "cả anim " + anim}: ${j.before} → ${j.after} key (${j.channels} kênh) · chuyển động giữ nguyên · ${hhmmss()} · Ctrl+Z để hoàn tác`, "ok");
      window.histLoad?.();
    } catch (e) { setStatus("giảm key lỗi: " + e.message, "bad") }
  };
  cv.addEventListener("keydown", ev => {
    if (ev.key === "Delete" || ev.key === "Backspace") { ev.preventDefault(); ev.stopPropagation(); delKey() }
    else if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "a") {   // chọn hết key của các kênh đang hiện
      ev.preventDefault(); ev.stopPropagation();
      G.ms = []; for (const c of chans()) if (G.show.has(c.id)) for (const k of c.keys) G.ms.push({ id: c.id, k });
      setStatus(G.ms.length + " key đang chọn", "ok");
    } else if (ev.key === "Escape") { G.ms = []; G.sel = null }
  });
  cv.addEventListener("wheel", ev => {   // cuộn: giãn timeline (dùng chung với thanh timeline); Alt+cuộn: giãn trục dọc
    ev.preventDefault();
    if (ev.altKey || ev.ctrlKey) { const g = geo(), r = cv.getBoundingClientRect(), v = vy(g, ev.clientY - r.top), f = Math.pow(1.0018, ev.deltaY);
      G.y0 = v + (G.y0 - v) * f; G.y1 = v + (G.y1 - v) * f; if (ev.altKey) return }   // Alt: chỉ trục dọc; Ctrl: cả hai
    document.getElementById("tl").dispatchEvent(new WheelEvent("wheel", { clientX: ev.clientX, clientY: 0, deltaY: ev.deltaY, deltaX: ev.deltaX, shiftKey: ev.shiftKey, bubbles: true, cancelable: true }));
  }, { passive: false });
  G.linkOpposite = linkOpposite;   // để kiểm thử
  window.spineGraph = G;
})();
