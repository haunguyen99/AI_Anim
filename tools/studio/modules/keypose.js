// AI Anim Studio — panel Key Pose: ảnh key pose (giai đoạn 0 / bước C2b) của ĐÚNG anim đang mở (user 2026-10-30
// "Thêm tool review ảnh vào studio. mỗi anim sẽ có danh sách keypose tương ứng").
// Dữ liệu chung với trang Home /keypose (tools/home/keypose.py): ảnh ở work/<dự án>/<job>/keys/, đánh dấu ★/✕ + ghi chú ở
// kho keypose/marks/<p__job>, yêu cầu tạo thêm ảnh ở keypose/requests (bộ canh notes_watch.py bắt kind keypose_req).
// Theo pha (user 2026-10-30 "mỗi pha ... là một keypose"): keys/keypose.json "clips": {anim: {frames, fps, phases: [{f, name,
// desc, key|null}]}} chép từ cột Key pose của bảng pha trong bản phân tích. Pha có key = một ảnh (thiếu ảnh: nút Tạo ảnh theo
// mô tả pha), key null = pha chuyển tiếp. ▶ Chạy ảnh: ảnh các pha phủ viewport, đổi theo timeline Pose (bậc thang, như blocking),
// không cần xuất video (user "viết tool để ảnh chạy luôn thay vì phải chuyển ảnh thành video").
// Chưa có pha: danh sách key như cũ (gắn / bỏ, server đoán theo tên). Ghim một ảnh lên góc viewport để dựng pose theo.
(function () {
  const esc = ST.esc, $ = ST.$;
  const K = ST.mods.keypose = { id: "keypose" };
  const NS = "/api/store/keypose";
  let data = null, marks = {}, reqs = [], loadedFor = null, busy = false, err = "", pick = {}, showOther = false, pin = null;
  const IK = () => ST.ws === "imagekey";   // workspace Image Key: chỉ ảnh, không model 3D, tự giữ anim + timeline ảnh
  const poseClip = () => { const p = ST.mods.pose; return p && p.clipId ? p.clipId() : null; };
  const ikPref = () => "kp:clip:" + (ST.char ? ST.char.id : "");
  const clipId = () => IK() ? (K.cur || null) : poseClip();
  const docId = j => j.replace(/\//g, "__");
  const who = () => { try { return localStorage.getItem("kp_who") || ""; } catch (e) { return ""; } };
  const post = (url, body) => api(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  async function api(url, opt) { const r = await fetch(url, opt); const j = await r.json(); if (!r.ok || j.error) throw new Error(j.error || r.status); return j; }
  const myTab = () => ST.curTab && ST.curTab() === "keypose:list";
  const oldSrv = m => /404/.test(m) ? " (server Home cũ: tắt và bật lại tools/home/start.bat)" : "";

  async function load() {
    const id = clipId();
    if (!id) { data = null; loadedFor = null; return; }
    if (busy) return; busy = true;
    try {
      const d = await api("/api/keypose/clip?id=" + encodeURIComponent(id));
      let m = {}, r = [];
      if (d.job) {
        const [mm, rr] = await Promise.all([api(`${NS}/marks/${docId(d.job)}`).catch(() => ({})), api(`${NS}/requests`).catch(() => ({ docs: [] }))]);
        const ks = new Set(d.keys.map(k => k.key).concat((d.phases || []).map(p => p.key).filter(Boolean)));
        m = mm.data || {}; r = (rr.docs || []).map(x => ({ id: x.id, ...x.data })).filter(x => x.job === d.job && (x.clip === id || ks.has(x.key)))
          .sort((a, b) => (b.at || "").localeCompare(a.at || ""));
      }
      const sig = JSON.stringify([d, m, r]);
      err = ""; loadedFor = id;
      if (sig !== load.sig) { const first = !load.sig; load.sig = sig; data = d; marks = m; reqs = r; if (myTab() || IK()) ST.refresh(); if (IK() && !first) anims(true); }
      if (P.on) P.draw();
    } catch (e) { err = e.message || String(e); loadedFor = id; data = null; if (myTab()) ST.refresh(); }
    busy = false;
  }
  const mk = n => marks[n] || {};
  // góc nhìn (user 2026-10-30 "lõi ... đầy đủ các góc cơ bản ... nhân vật nào cần những góc nào người dùng sẽ lựa chọn"):
  // ảnh <key>__<góc>_rN; không hậu tố = góc chính. data.views = {main, use[], all[], camref{}}; K.vw = góc đang xem (Image Key)
  const VL = { right: "Phải", left: "Trái", front: "Trước", back: "Sau", top: "Trên", q34: "3/4" };
  const vmain = () => (data && data.views && data.views.main) || "right";
  const vuse = () => (data && data.views && data.views.use) || [vmain()];
  const cv = () => IK() && K.vw && vuse().includes(K.vw) ? K.vw : vmain();
  const groupV = (key, v) => { const g = data && data.keys.find(k => k.key === key); if (!g) return null; const L = g.images.filter(i => (i.view || vmain()) === v); return L.length ? { key, images: L } : null; };
  // ảnh đại diện của key ở một góc: ảnh đang bấm xem → ★ mới nhất → (ngoài Image Key: mới nhất chưa loại) → mới nhất
  const chosenV = (key, v) => { const k = groupV(key, v); if (!k) return null; const L = k.images;
    return L.slice().reverse().find(i => mk(i.name).mark === "star") || (IK() ? null : L.slice().reverse().find(i => mk(i.name).mark !== "reject")) || L[L.length - 1]; };
  const bestV = (key, v) => { const k = groupV(key, v); if (!k) return null; return k.images.find(i => i.name === pick[key + "@" + v]) || chosenV(key, v); };
  const group = key => groupV(key, cv()), chosen = key => chosenV(key, cv()), best = key => bestV(key, cv());
  const imgOf = n => data && data.keys.flatMap(k => k.images).find(i => i.name === n);
  const lastF = () => Math.max(1, ...((data && data.phases) || []).map(p => p.f || 1));
  const frames = () => { if (!IK()) try { const g = ST.poseEng && ST.poseEng() && ST.poseEng().get(); if (g && g.P && g.P.frames) return g.P.frames; } catch (e) {} return (data && data.frames) || lastF(); };
  const fps = () => { if (IK()) return (data && data.fps) || 30; try { const g = ST.poseEng && ST.poseEng() && ST.poseEng().get(); if (g && g.P && g.P.fps) return g.P.fps; } catch (e) {} return (data && data.fps) || 30; };

  // ---- một key: ảnh lớn + dải bản + nút
  function keyCard(key, opts) {
    const k = group(key), s = best(key);
    if (!k || !s) {
      const v = cv(), mainImg = v !== vmain() ? chosenV(key, vmain()) : null;
      if (mainImg) return `<div class="kpmiss"><span class="sub">Chưa có góc <b>${VL[v]}</b> của <code>${esc(key)}</code></span><button class="on" data-k="makeview" data-key="${esc(key)}" data-n="${esc(mainImg.name)}" title="AI dựng lại đúng pose của ảnh ${esc(mainImg.name)} (góc ${VL[vmain()]}) nhìn từ góc ${VL[v]}">Tạo góc ${VL[v]}</button></div>`;
      if (v !== vmain()) return `<div class="kpmiss"><span class="sub">Cần ảnh góc chính (${VL[vmain()]}) trước khi tạo góc ${VL[v]}.</span></div>`;
      return `<div class="kpmiss"><span class="sub">Chưa có ảnh <code>${esc(key)}</code></span><button class="on" data-k="make" data-key="${esc(key)}" title="Nhờ AI tạo ảnh theo mô tả của pha">Tạo ảnh</button></div>`;
    }
    const m = mk(s.name);
    const ch = chosen(key), isCh = ch && ch.name === s.name;
    return `<div class="kpimg ${m.mark || ""} ${isCh ? "chosen" : ""}"><img src="${esc(s.url)}" alt="${esc(s.name)}" data-k="zoom" title="Bấm để phóng to">${IK() ? `<button class="kpstar ${isCh ? "on" : ""}" data-k="choose" data-key="${esc(key)}" data-n="${esc(s.name)}" title="${isCh ? "Bản đang dùng cho pha này" + (m.mark === "star" ? " (bạn đã chọn)" : " (mặc định: bản mới nhất)") : "Dùng bản này cho pha"}">★</button>` : ""}</div>
      ${k.images.length > 1 ? `<div class="kpstrip">${k.images.map(i => `<img src="${esc(i.url)}" alt="${esc(i.name)}" title="${esc(i.name)}${IK() ? " · bấm để xem; ★ trên ảnh lớn để dùng bản này" : ""}" data-k="pick" data-key="${esc(key)}" data-n="${esc(i.name)}" class="${i.name === s.name ? "on" : ""} ${mk(i.name).mark || ""} ${ch && i.name === ch.name ? "chosen" : ""}" loading="lazy">`).join("")}</div>` : ""}
      <div class="row kpacts" data-n="${esc(s.name)}" data-key="${esc(key)}"><span class="kpname" title="${esc(s.name)}">${esc(s.name)}</span>
        <button class="${m.mark === "star" ? "on star" : ""}" data-k="star" title="Chọn ảnh này cho key (trình chạy ảnh dùng ảnh ★)">★</button>
        <button class="${m.mark === "reject" ? "on bad" : ""}" data-k="reject" title="Loại ảnh này">✕</button>
        <button data-k="redo" title="Nhờ AI tạo ảnh mới dựa trên ảnh này">↻ Sửa</button>
        <button class="${pin === s.name ? "on" : ""}" data-k="pin" title="Ghim ảnh lên góc viewport để dựng pose theo">Ghim</button></div>
      <textarea class="kpnote" onkeydown="event.stopPropagation()" data-n="${esc(s.name)}" rows="1" placeholder="Ghi chú cho ảnh này…">${esc(m.note || "")}</textarea>`;
  }
  function curPhaseHtml() {
    const F = frames(), f = Math.max(1, Math.min(F, P.pf || 1)), cur = phaseAt(f), t = at(f);
    const ps = data.phases.filter(p => p.f != null).sort((a, b) => a.f - b.f);
    const chips = `<div class="kpchips">${ps.map(p => `<button class="${cur && p.i === cur.i ? "on" : ""} ${p.key ? (group(p.key) ? "" : "miss") : "tw"}" data-k="goph" data-f="${p.f}" title="${esc(p.desc || "")}">F${p.f} ${esc(p.name || "")}</button>`).join("")}</div>`;
    if (!cur) return chips;
    const head = `<div class="row kpkh"><input class="kpf" type="number" min="1" max="${F}" value="${cur.f}" data-i="${cur.i}" title="Frame của pha (đổi là thanh chạy đổi nhịp)" onkeydown="event.stopPropagation()"><b>${esc(cur.name || "")}</b>${cur.key ? `<code class="sub">${esc(cur.key)}</code>` : `<span class="sub">chuyển tiếp</span>`}${vuse().length > 1 ? `<span class="kpvtag">${VL[cv()]}</span>` : ""}</div>
      ${cur.desc ? `<div class="sub kpdesc">${esc(cur.desc)}</div>` : ""}`;
    const key = cur.key || (t && t.key);
    const note = !cur.key ? `<div class="sub">Pha chuyển tiếp: không có ảnh riêng, đang giữ ảnh của <code>${esc(t ? t.key : "")}</code> (AI dựng pose này ở blocking).</div>` : "";
    return chips + `<section class="kpph kpkey ${cur.key ? "" : "tween"}" data-i="${cur.i}" data-key="${esc(key || "")}">${head}${note}${key ? keyCard(key) : ""}</section>`;
  }
  function phasesHtml() {
    if (IK()) return curPhaseHtml();
    const seen = new Set(), F = frames();
    return data.phases.map(p => {
      const head = `<div class="row kpkh"><input class="kpf" type="number" min="1" max="${F}" value="${p.f == null ? "" : p.f}" data-i="${p.i}" title="Frame của pha (đổi là trình chạy ảnh đổi nhịp)" onkeydown="event.stopPropagation()"><b>${esc(p.name || "")}</b>${p.key ? `<code class="sub">${esc(p.key)}</code>` : `<span class="sub">chuyển tiếp</span>`}</div>
        ${p.desc ? `<div class="sub kpdesc">${esc(p.desc)}</div>` : ""}`;
      if (!p.key) return `<section class="kpph tween" data-i="${p.i}">${head}</section>`;
      if (seen.has(p.key)) { const s = best(p.key); return `<section class="kpph same" data-i="${p.i}">${head}<div class="row kpsame">${s ? `<img src="${esc(s.url)}" alt="${esc(s.name)}" data-k="zoom">` : ""}<span class="sub">Dùng lại ảnh của <code>${esc(p.key)}</code></span></div></section>`; }
      seen.add(p.key);
      return `<section class="kpph kpkey" data-i="${p.i}" data-key="${esc(p.key)}">${head}${keyCard(p.key)}</section>`;
    }).join("");
  }

  K.panel = sub => {
    if (sub === "anims") return K.panelAnims();
    const id = clipId();
    if (!id) return `<div class="sub" style="padding:10px">${IK() ? "Chọn một anim ở cột trái." : "Mở một anim (Outliner → Anim) để xem key pose của nó."}</div>`;
    if (loadedFor !== id) { load(); return '<div class="sub" style="padding:10px">Đang tải key pose…</div>'; }
    if (err) return `<div class="s-bad" style="padding:10px">${/fetch/i.test(err) ? "Mất kết nối server Home (đang bật lại?). Tự thử lại mỗi 4 giây." : "Không đọc được Image Key: " + esc(err) + oldSrv(err)}</div>`;
    if (!data || !data.job) return `<div class="kpwrap"><p class="note" style="padding:10px">Anim này chưa có ảnh key pose. Ảnh nằm ở <code>work/&lt;dự án&gt;/&lt;job&gt;/keys/</code> (job trùng tên đầu của anim, vd <code>sdr03</code> cho <code>sdr03_shoot</code>). Nhờ Claude tạo ảnh key pose (giai đoạn 0 / bước C2b).</p></div>`;
    const w = ST.mods.notes && ST.mods.notes.watching ? ST.mods.notes.watching() : data.watching;
    const ph = data.phases && data.phases.length, keyed = ph ? data.phases.filter(p => p.key) : [], miss = keyed.filter(p => !group(p.key)).length;
    const head = `<div class="row kphead">${ph && !IK() ? `<button class="on" data-k="play" title="Phủ ảnh các pha lên viewport, đổi theo timeline của anim: chạy / tua bằng timeline (bấm lần nữa để tắt)">${P.on ? "■ Tắt ảnh" : "▶ Chạy ảnh"}</button>` : ""}
      <button data-k="req" title="Nhờ AI tạo thêm ảnh (key có sẵn hoặc key mới)">+ Yêu cầu ảnh</button>
      <span class="wdot" title="${w ? "Claude đang canh: yêu cầu gửi đi được nhận ngay" : "Claude không canh: yêu cầu vẫn lưu, nhắn Claude để làm"}">${w ? "●" : "○"}</span>
      <span class="sub">${ph ? data.phases.length + " pha · " + new Set(keyed.map(p => p.key)).size + " key" + (miss ? " · thiếu " + miss + " ảnh" : "") : data.keys.length + " key" + (data.guessed ? " · đoán theo tên" : "")}</span>
      <a class="sub" href="/keypose?job=${encodeURIComponent(data.job)}" target="_blank" title="Trang Key Pose đầy đủ của ${esc(data.job)}">${esc(data.job.split("/").pop())} ↗</a></div>`;
    let body;
    if (ph) {
      const extra = (data.extra || []).map(k => `<section class="kpph kpkey" data-key="${esc(k)}"><div class="row kpkh"><input class="kpf" type="number" min="1" placeholder="F" data-key="${esc(k)}" title="Gõ frame để đưa key này vào bảng pha" onkeydown="event.stopPropagation()"><b>${esc(k)}</b><span class="sub">chưa đặt vào pha</span><button class="kpx" data-k="unassign" title="Bỏ key này khỏi anim">×</button></div>${keyCard(k)}</section>`).join("");
      body = phasesHtml() + (extra ? `<div class="sub" style="margin-top:4px">Key gắn thêm (gõ frame để đặt vào bảng pha):</div>${extra}` : "");
    } else {
      body = data.keys.map(k => `<section class="kpkey" data-key="${esc(k.key)}"><div class="row kpkh"><b>${esc(k.key)}</b><span class="sub">${k.images.length} ảnh</span><button class="kpx" data-k="unassign" title="Bỏ key này khỏi anim (ảnh vẫn giữ)">×</button></div>${keyCard(k.key)}</section>`).join("")
        || `<p class="note" style="padding:0 10px">Chưa gắn key nào vào anim này.${data.other.length ? " Gắn từ danh sách bên dưới." : ""}</p>`;
      body += `<p class="note" style="margin:2px 0">Anim chưa có bảng pha. Nhờ Claude chép cột Key pose của bản phân tích vào <code>keys/keypose.json</code> để có ▶ Chạy ảnh.</p>`;
    }
    const L = { sent: "Đã gửi", picked: "AI đã nhận", working: "Đang tạo", done: "Xong", error: "Lỗi" };
    const rq = reqs.filter(r => r.status !== "done" || Date.now() - Date.parse(r.at || 0) < 864e5).slice(0, 6).map(r => {
      const st = r.status || (r.picked ? "picked" : "sent");
      return `<div class="kpreq"><span class="st ${st}">${L[st] || st}${st === "working" && r.progress ? " " + esc(r.progress) : ""}</span> <b>${esc(r.key)}</b> · ${r.n} ảnh<div class="sub">${esc(r.text)}</div>${r.error ? `<div class="s-bad">${esc(r.error)}</div>` : ""}${r.reply ? `<div class="sub">AI: ${esc(r.reply)}</div>` : ""}</div>`;
    }).join("");
    const other = data.other.length ? `<div class="kpother"><button data-k="other" class="kplink">${showOther ? "▾" : "▸"} Key khác của ${esc(data.job.split("/").pop())} (${data.other.length})</button>
      ${showOther ? `<div class="kpogrid">${data.other.map(o => `<div class="kpo" data-key="${esc(o.key)}"><img src="${esc(o.url)}" alt="${esc(o.key)}" data-k="zoom" loading="lazy"><span title="${esc(o.key)}">${esc(o.key)}</span><button data-k="assign" title="Gắn key này vào anim đang mở">+ Gắn</button></div>`).join("")}</div>` : ""}</div>` : "";
    const N = ST.mods.notes, fbk = IK() && N && N.panel ? `<section class="kpfb"><h3>Góp ý vẽ trên ảnh</h3><div id="kpNotes">${N.panel()}</div></section>` : "";
    return `<div class="kpwrap${fbk ? " kpik" : ""}">${head}${rq ? `<div class="kpreqs">${rq}</div>` : ""}<div class="kpkeys">${body}</div>${other}${fbk}</div>`;
  };
  let rev = 0;
  K.panelKey = () => rev + "|" + cv() + (P.grid ? "g" : "") + (IK() && ST.mods.notes && ST.mods.notes.panelKey ? ST.mods.notes.panelKey() : "") + ST.ws + animsKey() + P.on + (IK() && data ? "p" + ((phaseAt(Math.max(1, P.pf || 1)) || {}).i) : "") + clipId() + "|" + (load.sig || "").length + "|" + (load.sig || "").slice(-40) + JSON.stringify(pick) + showOther + pin + err + (ST.mods.notes && ST.mods.notes.watching ? ST.mods.notes.watching() : "");
  K.panelStatic = true;
  K.panelMounted = sub => { if (sub !== "anims" && IK() && ST.mods.notes && ST.mods.notes.panelMounted) ST.mods.notes.panelMounted(); };

  async function saveMark(n, patch) {
    marks[n] = Object.assign({}, mk(n), patch, { by: who() || mk(n).by || "" }); rev++; ST.refresh();
    await api(`${NS}/marks/${docId(data.job)}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ [n]: marks[n] }) });
    load.sig = ""; await load(); ST.refresh();
  }
  async function write(url, body) {
    try { await post(url, Object.assign({ clip: clipId() }, body)); }
    catch (e) { return ST.toast("Không lưu được: " + e.message + oldSrv(e.message)); }
    load.sig = ""; await load(); ST.refresh();
  }
  function zoom(url, cap) {
    let lb = $("kpLb");
    if (!lb) { lb = document.createElement("div"); lb.id = "kpLb"; lb.innerHTML = "<figure><img alt=''><figcaption></figcaption></figure>"; lb.onclick = () => lb.classList.remove("on"); document.body.appendChild(lb);
      addEventListener("keydown", e => { if (e.key === "Escape") lb.classList.remove("on"); }); }
    lb.querySelector("img").src = url; lb.querySelector("figcaption").textContent = cap || ""; lb.classList.add("on");
  }
  function setPin(n) {
    pin = pin === n ? null : n;
    let el = $("kpPin");
    if (!pin) { if (el) el.remove(); ST.refresh(); return; }
    const im = imgOf(pin); if (!im) return;
    if (!el) { el = document.createElement("div"); el.id = "kpPin"; $("vp").appendChild(el); }
    el.innerHTML = `<img src="${esc(im.url)}" alt="${esc(pin)}" title="Bấm để phóng to"><div class="row"><span class="sub">${esc(pin)}</span><button title="Bỏ ghim">×</button></div>`;
    el.querySelector("img").onclick = () => zoom(im.url, pin);
    el.querySelector("button").onclick = () => setPin(pin);
    ST.refresh();
  }

  // ---- trình chạy ảnh (animatic): ảnh của pha có key giữ từ frame của pha tới pha có key kế tiếp.
  // Dùng chung timeline của Pose (user 2026-10-30 "sao không cho nó dùng chung timeline với pose luôn"): không có thanh chạy
  // riêng; chạy / dừng / tua / Space bằng timeline của anim, ảnh đổi theo frame hiện tại. Thanh "Đậm" cho thấy pose 3D bên dưới.
  const P = { on: false, own: false, playing: false, loop: true, frame: 0, op: 1, t: 0, t0: 0, f0: 1, z: 1, x: 0, y: 0 };
  P.view = () => document.querySelectorAll("#kpPlay .kpstage img").forEach(im => { im.style.transform = `translate(${P.x}px, ${P.y}px) scale(${P.z})`; });
  function track(v) {   // [{f, key, name, img}] theo frame, chỉ pha có key, ảnh ở góc v (mặc định góc đang xem)
    v = v || cv();
    return (data && data.phases || []).filter(p => p.key && p.f != null).sort((a, b) => a.f - b.f).map(p => ({ f: p.f, key: p.key, name: p.name, img: bestV(p.key, v) }));
  }
  function at(f, v) { const T = track(v); let cur = T[0] || null; for (const t of T) if (t.f <= f) cur = t; return cur; }
  function phaseAt(f) { let cur = null; for (const p of (data && data.phases || []).filter(p => p.f != null).sort((a, b) => a.f - b.f)) if (p.f <= f) cur = p; return cur; }
  function tlFrame() { try { const g = ST.poseEng && ST.poseEng() && ST.poseEng().get(); return g && g.frame ? g.frame : 1; } catch (e) { return 1; } }
  P.open = () => {
    let el = $("kpPlay");
    if (!el) {
      el = document.createElement("div"); el.id = "kpPlay"; $("vp").appendChild(el);
      el.innerHTML = `<div class="kpstage"><img alt=""><div class="kpgrid"></div><div class="kpempty sub"></div></div><div class="kpbadge"></div><div class="kpviews"></div>
        <div class="kptools"><span class="sub" title="Lăn chuột: phóng to / thu nhỏ ảnh · kéo: dời ảnh · nhấp đúp: về khít khung">🔍 lăn chuột</span><label class="sub kpop" title="Độ đậm của ảnh: kéo nhỏ để thấy pose 3D bên dưới (khi đó chuột điều khiển camera 3D)">Đậm <input type="range" min="0.15" max="1" step="0.05" value="1" data-p="op"></label><button data-p="close" title="Đóng (Esc)">×</button></div>
        <div class="kpbar"><button data-p="play" title="Chạy / dừng (Space)">▶</button><button data-p="prev" title="Pha trước (←)">⏮</button><button data-p="next" title="Pha sau (→)">⏭</button>
          <div class="kpscrub"><input type="range" min="1" value="1" data-p="scrub" aria-label="Frame"><div class="kpticks"></div></div><span class="kpfr"></span>
          <label class="sub"><input type="checkbox" data-p="loop" checked> Lặp</label></div>`;
      el.querySelector("[data-p=close]").onclick = () => P.close();
      el.querySelector(".kpviews").addEventListener("click", e => { const b = e.target.closest("[data-v]"); if (!b) return;
        if (b.dataset.v === "grid") { P.grid = !P.grid; ST.pref.set("kp:grid", P.grid); } else if (b.dataset.v === "cfg") return viewsDialog(); else { K.vw = b.dataset.v; ST.pref.set("kp:view", K.vw); }
        P.draw(); ST.refresh(); });
      el.querySelector("[data-p=op]").addEventListener("input", e => { P.op = +e.target.value; P.style(); });
      el.querySelector("[data-p=play]").onclick = () => P.toggle();
      el.querySelector("[data-p=prev]").onclick = () => P.jump(-1);
      el.querySelector("[data-p=next]").onclick = () => P.jump(1);
      el.querySelector("[data-p=scrub]").addEventListener("input", e => { P.stop(); P.frame = +e.target.value; P.draw(); });
      el.querySelector("[data-p=loop]").addEventListener("change", e => { P.loop = e.target.checked; });
      el.addEventListener("keydown", e => e.stopPropagation());
      // phóng to / dời ảnh (user 2026-10-30 "không zoom ra vào được khi bật ảnh"): lăn chuột = zoom quanh con trỏ, kéo = dời,
      // nhấp đúp = về khít khung. Khi kéo Đậm nhỏ (thấy 3D), chuột trả lại cho camera 3D.
      const st = el.querySelector(".kpstage");
      st.addEventListener("wheel", e => { e.preventDefault(); e.stopPropagation(); const r = st.getBoundingClientRect(), cx = e.clientX - r.left - r.width / 2, cy = e.clientY - r.top - r.height / 2;
        const k = Math.exp(-e.deltaY * 0.0015), z = Math.max(0.2, Math.min(12, P.z * k)), q = z / P.z; P.x = cx - (cx - P.x) * q; P.y = cy - (cy - P.y) * q; P.z = z; P.view(); }, { passive: false });
      st.addEventListener("pointerdown", e => { if (e.button > 1) return; e.preventDefault(); e.stopPropagation(); st.setPointerCapture(e.pointerId); const x0 = e.clientX - P.x, y0 = e.clientY - P.y;
        const mv = ev => { P.x = ev.clientX - x0; P.y = ev.clientY - y0; P.view(); }, up = () => { st.removeEventListener("pointermove", mv); st.removeEventListener("pointerup", up); };
        st.addEventListener("pointermove", mv); st.addEventListener("pointerup", up); });
      st.addEventListener("dblclick", e => { e.stopPropagation(); P.z = 1; P.x = P.y = 0; P.view(); });
      st.addEventListener("click", e => { const fg = e.target.closest(".kpgrid figure"); if (fg && fg.dataset.v !== K.vw) { K.vw = fg.dataset.v; ST.pref.set("kp:view", K.vw); P.draw(); ST.refresh(); } });
    }
    if (loadedFor !== clipId()) load();
    P.on = true; P.own = IK(); P.playing = false; if (!P.own) P.frame = 0; else P.frame = P.frame || 1;
    el.classList.add("on"); el.classList.toggle("own", P.own); P.style(); P.tick(); P.draw();
  };
  P.style = () => { const el = $("kpPlay"); if (!el) return; const op = P.own ? 1 : P.op; el.classList.toggle("see", op < 1); el.querySelector(".kpstage img").style.opacity = op; };
  P.close = () => { P.stop(); P.on = false; clearTimeout(P.t); const el = $("kpPlay"); if (el) el.classList.remove("on"); if (myTab()) ST.refresh(); };
  P.syncPanel = () => { const f = Math.max(1, P.frame || 1), a = phaseAt(P.pf || 1), b = phaseAt(f); P.pf = f; if (P.own && (a && a.i) !== (b && b.i) && myTab()) ST.refresh(); };
  P.stop = () => { const was = P.playing; P.playing = false; if (was) P.syncPanel(); const b = document.querySelector("#kpPlay [data-p=play]"); if (b) b.textContent = "▶"; };
  P.toggle = () => { if (!P.own) return; if (P.playing) return P.stop(); if (P.frame >= frames()) P.frame = 1;
    P.playing = true; P.t0 = performance.now(); P.f0 = P.frame; document.querySelector("#kpPlay [data-p=play]").textContent = "⏸"; P.tick(); };
  P.jump = d => { P.stop(); const fs = [...new Set(track().map(t => t.f))]; if (!fs.length) return;
    const i = fs.findIndex(f => f > P.frame), cur = i < 0 ? fs.length - 1 : i - 1; P.frame = fs[Math.max(0, Math.min(fs.length - 1, cur + d))] || 1; P.draw(); };
  P.tick = () => {   // Pose: đọc frame của timeline Pose; Image Key: tự chạy theo fps. setTimeout thay rAF: vẫn chạy khi khung không vẽ lại
    clearTimeout(P.t); if (!P.on) return;
    if (!P.own) { const f = tlFrame(); if (f !== P.frame) { P.frame = f; P.draw(); } P.t = setTimeout(P.tick, 15); return; }
    if (!P.playing) return;
    const N = frames(); let f = P.f0 + Math.floor((performance.now() - P.t0) / 1000 * fps());
    if (f > N) { if (P.loop) { P.t0 = performance.now(); P.f0 = 1; f = 1; } else { f = N; P.stop(); } }
    if (f !== P.frame) { P.frame = f; P.draw(); }
    P.t = setTimeout(P.tick, 15);
  };
  P.draw = () => {
    const el = $("kpPlay"); if (!el) return;
    if (!data) { el.querySelector(".kpstage img").removeAttribute("src"); el.querySelector(".kpbadge").innerHTML = ""; el.querySelector(".kpempty").textContent = clipId() ? "Đang tải…" : "Chọn một anim ở cột trái."; return; }
    const N = frames(), f = Math.max(1, Math.min(N, P.frame || 1)), t = at(f), ph = phaseAt(f), want = ph && ph.key && ph.key !== (t && t.key) ? ph.key : null;
    const im = el.querySelector(".kpstage img"), src = t && t.img ? t.img.url : "", U = vuse(), grid = P.own && P.grid && U.length > 1;
    if (im.getAttribute("src") !== src) { if (src) im.setAttribute("src", src); else im.removeAttribute("src"); }
    el.classList.toggle("grid", grid);
    const gd = el.querySelector(".kpgrid"), G = grid ? U.slice(0, 4) : [];
    const gsig = G.map(v => { const tv = at(f, v); return v + (tv && tv.img ? tv.img.url : ""); }).join("|") + cv();
    if (gd.dataset.sig !== gsig) { gd.dataset.sig = gsig; gd.style.gridTemplateColumns = G.length > 1 ? "1fr 1fr" : "1fr";
      gd.innerHTML = G.map(v => { const tv = at(f, v); return `<figure class="${v === cv() ? "on" : ""}" data-v="${v}"><figcaption>${VL[v]}</figcaption>${tv && tv.img ? `<img src="${esc(tv.img.url)}" alt="${esc(tv.img.name)}" draggable="false">` : `<span class="sub">chưa có ảnh góc ${VL[v]}</span>`}</figure>`; }).join(""); P.view(); }
    if (P.own) el.querySelector(".kpviews").innerHTML = (U.length > 1 ? U.map(v => `<button class="${v === cv() ? "on" : ""}" data-v="${v}" title="Xem góc ${VL[v]}${v === vmain() ? " (góc chính)" : ""}">${VL[v]}</button>`).join("")
      + `<button class="${grid ? "on" : ""}" data-v="grid" title="Hiện ${Math.min(4, U.length)} góc cùng lúc">⊞</button>` : "") + `<button data-v="cfg" title="Chọn các góc dùng cho nhân vật này">⚙ Góc</button>`;
    const missing = ph && ph.key && !group(ph.key) && !grid;
    el.querySelector(".kpempty").textContent = !data.job ? "Anim này chưa có ảnh key pose." : !(data.phases || []).length ? "Anim này chưa có bảng pha (cột Key pose của bản phân tích)." : !src ? (cv() !== vmain() ? `Góc ${VL[cv()]} của pha này chưa có ảnh: bấm Tạo góc ${VL[cv()]} ở panel bên phải.` : "Pha này chưa có ảnh: bấm Tạo ảnh ở panel bên phải.") : "";
    if (P.own) { const sc = el.querySelector("[data-p=scrub]"); sc.max = N; sc.value = f; el.querySelector(".kpfr").textContent = `F${f}/${N} · ${fps()} fps · ${(N / fps()).toFixed(2)} s`;
      el.querySelector(".kpticks").innerHTML = (data.phases || []).filter(p => p.f != null).map(p => `<i class="${p.key ? (group(p.key) ? "k" : "miss") : "tw"}" style="left:${N > 1 ? (p.f - 1) / (N - 1) * 100 : 0}%" title="F${p.f} · ${esc(p.name || "")}"></i>`).join(""); }
    if (!P.playing) P.syncPanel();   // đang chạy: panel đứng yên ở pha lúc bấm chạy
    el.querySelector(".kpbadge").innerHTML = `<b>F${f}</b> / ${N} · ${esc(ph ? ph.name : "")}${ph && !ph.key ? ' <span class="sub">(chuyển tiếp, giữ ảnh trước)</span>' : ""}${missing || want ? ` <span class="s-bad">thiếu ảnh ${esc(ph.key)}</span>` : ""}${t && t.img ? ` <span class="sub">${esc(t.img.name)}</span>` : ""}`;
  };
  // góp ý vẽ trên ảnh (notes.js): chụp ảnh đang phủ như đang thấy (zoom / dời) + bối cảnh để AI biết sửa ảnh nào
  K.shot = () => {
    const el = $("kpPlay"), ims = el ? [...el.querySelectorAll(el.classList.contains("grid") ? ".kpgrid img" : ".kpstage > img")].filter(i => i.naturalWidth) : [];
    if (!P.on || !ims.length || P.op < 1) return null;
    const vp = $("vp").getBoundingClientRect(), sc = Math.min(1, 1600 / Math.max(vp.width, vp.height));
    const c = document.createElement("canvas"); c.width = Math.round(vp.width * sc); c.height = Math.round(vp.height * sc);
    const g = c.getContext("2d"); g.fillStyle = getComputedStyle(el).backgroundColor || "#222"; g.fillRect(0, 0, c.width, c.height);
    for (const im of ims) { const r = im.getBoundingClientRect(); g.drawImage(im, (r.left - vp.left) * sc, (r.top - vp.top) * sc, r.width * sc, r.height * sc); }
    return c;
  };
  K.ctx = () => {
    if (!P.on || !data) return null;
    const f = Math.max(1, Math.min(frames(), P.frame || 1)), t = at(f), ph = phaseAt(f);
    return { clip: clipId(), job: data.job, frame: f, phase: ph ? ph.name : "", phaseKey: ph ? ph.key : null, key: t ? t.key : null, image: t && t.img ? t.img.name : null, view: cv(),
      grid: P.grid && vuse().length > 1 ? vuse().slice(0, 4).map(v => { const tv = at(f, v); return { view: v, image: tv && tv.img ? tv.img.name : null }; }) : null,
      zoom: +P.z.toFixed(3), pan: [Math.round(P.x), Math.round(P.y)] };
  };
  // workspace Image Key (user 2026-10-30 "chỉ phục vụ việc tạo ảnh key cho các anim theo tài liệu ... không cần hiển thị model 3D"):
  // body.ws-imagekey ẩn khung 3D, ảnh luôn phủ với timeline ảnh riêng, anim chọn ở cột trái (panel keypose:anims), không nạp lõi Pose.
  let byWS = false;
  K.vw = ST.pref.get("kp:view", null); P.grid = !!ST.pref.get("kp:grid", false);
  function enterIK() {
    document.body.classList.add("ws-imagekey");
    if (!K.cur) K.cur = ST.pref.get(ikPref(), null) || poseClip() || ST.clip || null;
    if (ST.pref.get("ltab:imagekey", null) == null) ST.pref.set("ltab:imagekey", "keypose:anims");
    loadedFor = null; load.sig = ""; byWS = !P.on || byWS; P.close(); P.open(); anims(true);
  }
  function leaveIK() { document.body.classList.remove("ws-imagekey"); loadedFor = null; load.sig = ""; if (byWS) { byWS = false; P.close(); } else if (P.on) P.open(); }
  ST.on("ws", id => id === "imagekey" ? enterIK() : document.body.classList.contains("ws-imagekey") && leaveIK());
  ST.on("init", () => { if (ST.ws === "imagekey") enterIK(); });
  ST.on("char", () => { alist = null; if (IK()) { K.cur = ST.pref.get(ikPref(), null) || K.cur; anims(true); } });
  K.pickClip = id => { K.cur = id; ST.pref.set(ikPref(), id); loadedFor = null; load.sig = ""; pick = {}; P.frame = 1; P.z = 1; P.x = P.y = 0; P.view(); P.stop(); load(); P.draw(); ST.refresh(); };
  K.goto = c => { if (!c) return; if (IK() && c.clip && c.clip !== K.cur) K.pickClip(c.clip); if (c.frame) { P.stop(); P.frame = c.frame; } if (c.zoom) { P.z = c.zoom; [P.x, P.y] = c.pan || [0, 0]; P.view(); } P.draw(); };

  // cột trái: anim của nhân vật + tình trạng ảnh key (số pha, thiếu ảnh)
  let alist = null, alistBusy = false, areqs = [];
  const AST = { sent: "Đã gửi", picked: "AI đã nhận", analysis: "Đang phân tích", review: "Chờ duyệt phân tích", images: "Đang tạo ảnh", done: "Xong", error: "Lỗi" };
  async function loadReqs() {
    try { const j = await api(`${NS}/animreqs`); const me = ST.char ? ST.char.id : "";
      const L = (j.docs || []).map(x => ({ id: x.id, ...x.data })).filter(r => r.char === me && (r.status !== "done" || Date.now() - Date.parse(r.done_at || r.at || 0) < 864e5))
        .sort((a, b) => (a.at || "").localeCompare(b.at || ""));
      const was = JSON.stringify(areqs); areqs = L;
      if (JSON.stringify(L) !== was) { if (L.some(r => r.status === "done") && was.includes('"images"')) anims(true); ST.refresh(); }
    } catch (e) {}
  }
  setInterval(() => { if (IK() && document.visibilityState === "visible") loadReqs(); }, 5000);
  function newAnimDialog() {
    if (!ST.char) return ST.toast("Mở nhân vật trước.");
    ST.dialog("Anim mới · " + ST.char.name, `<div style="display:grid;gap:8px;min-width:340px;max-width:560px">
      <p class="note" style="margin:0">Gửi yêu cầu cho AI: AI lập bản phân tích + bảng pha (mỗi pha một key pose) để bạn duyệt, duyệt xong AI tạo ảnh key pose cho anim.</p>
      <label class="sub">Tên anim <input id="arName" placeholder="vd Hit, Die, Reload_02" style="width:100%"></label>
      <label class="sub">Anim làm gì <textarea id="arDesc" rows="4" style="width:100%" placeholder="Hành động, cảm xúc, nhịp, bắt đầu / kết thúc ở đâu, sự kiện game (frame bắn, trúng đòn)…"></textarea></label>
      <div class="row" style="gap:8px;flex-wrap:wrap"><label class="sub">Kiểu <select id="arLoop"><option value="once">Một lần</option><option value="loop">Lặp</option></select></label>
        <label class="sub">Số frame <input id="arFrames" type="number" min="1" placeholder="AI đề xuất" style="width:100px"></label>
        <label class="sub">FPS <input id="arFps" type="number" min="1" value="30" style="width:70px"></label></div>
      <label class="sub">Tài liệu / GDD (link hoặc ghi chú, không bắt buộc) <input id="arDoc" placeholder="vd link Google Sheet, tab Anim, dòng 12" style="width:100%"></label>
      <p class="s-bad" id="arErr" style="margin:0"></p>
      <div class="row" style="gap:8px;justify-content:flex-end"><button id="arNo">Huỷ</button><button class="on" id="arOk">Gửi cho AI</button></div></div>`, b => {
      const q = x => b.querySelector(x); q("#arName").focus();
      b.querySelectorAll("input,textarea,select").forEach(i => i.addEventListener("keydown", e => { e.stopPropagation(); if (e.key === "Escape") ST.closeDialog(); }));
      q("#arNo").onclick = () => ST.closeDialog();
      q("#arOk").onclick = async () => {
        const name = q("#arName").value.trim(), desc = q("#arDesc").value.trim();
        if (!name) { q("#arErr").textContent = "Nhập tên anim."; return q("#arName").focus(); }
        if (!desc) { q("#arErr").textContent = "Mô tả anim làm gì."; return q("#arDesc").focus(); }
        q("#arOk").disabled = true;
        try {
          await post(`${NS}/animreqs`, { char: ST.char.id, charName: ST.char.name, job: data && data.job || "", name, desc, loop: q("#arLoop").value === "loop",
            frames: +q("#arFrames").value || null, fps: +q("#arFps").value || 30, doc: q("#arDoc").value.trim(), by: who(), at: new Date().toISOString(), sent: true, status: "sent" });
          ST.closeDialog(); ST.toast("Đã gửi yêu cầu anim mới cho AI"); loadReqs();
        } catch (e) { q("#arErr").textContent = "Không gửi được: " + e.message; q("#arOk").disabled = false; }
      };
    });
  }
  K.newAnim = newAnimDialog;
  async function anims(force) {
    if (!ST.char || alistBusy || (alist && !force)) return; alistBusy = true;   // chờ nhân vật nạp: không có thì /api/poses trả anim của mọi nhân vật
    try {
      const L = await (await fetch("/api/poses" + (ST.char ? "?char=" + encodeURIComponent(ST.char.id) : ""))).json();
      const out = await Promise.all((Array.isArray(L) ? L : []).map(async c => {
        try { const d = await api("/api/keypose/clip?id=" + encodeURIComponent(c.id)); const keyed = (d.phases || []).filter(p => p.key), have = new Set(d.keys.map(k => k.key));
          const vm = (d.views && d.views.main) || "right", ks = [...new Set(keyed.map(p => p.key))];
          const views = ((d.views && d.views.use) || [vm]).map(v => { const hv = new Set(d.keys.filter(g => g.images.some(i => (i.view || vm) === v)).map(g => g.key));
            return { v, main: v === vm, miss: ks.filter(x => !hv.has(x)).length, imgs: hv.size }; });
          return { id: c.id, name: c.name, job: d.job, phases: (d.phases || []).length, keys: ks.length, miss: new Set(keyed.filter(p => !have.has(p.key)).map(p => p.key)).size, imgs: d.keys.length, views }; }
        catch (e) { return { id: c.id, name: c.name, err: true }; }
      }));
      alist = out; if (out.length && !out.some(a => a.id === K.cur)) { const pf = ST.pref.get(ikPref(), null), f = out.find(a => a.id === pf) || out.find(a => a.phases) || out[0]; K.pickClip(f.id); }
    } catch (e) { alist = []; }
    alistBusy = false; ST.refresh();
  }
  // cột trái nằm ngoài dock (#olLeft) nên không qua panel_click: bắt click ở document
  K.open = new Set(); K.shut = new Set();
  document.addEventListener("click", async e => { const b = e.target.closest(".kpanims [data-k]"); if (!b || !b.closest("#olLeft")) return;
    const id = b.dataset.id, a = b.dataset.k;
    if (a === "anim") { if (id !== K.cur) { P.close(); K.pickClip(id); P.open(); } K.shut.delete(id); ST.refresh(); }
    else if (a === "fold") { const op = K.open.has(id) || (id === K.cur && !K.shut.has(id)); if (op) { K.open.delete(id); K.shut.add(id); } else { K.open.add(id); K.shut.delete(id); } ST.refresh(); }
    else if (a === "view") { if (id !== K.cur) { P.close(); K.pickClip(id); P.open(); } K.vw = b.dataset.v; ST.pref.set("kp:view", K.vw); P.grid = false; ST.pref.set("kp:grid", false); P.draw(); ST.refresh(); }
    else if (a === "addview") { if (id !== K.cur) { P.close(); K.pickClip(id); P.open(); await load(); } viewsDialog(); }
    else if (a === "newanim") newAnimDialog();
    else if (a === "reanims") anims(true); });
  const animsKey = () => JSON.stringify(areqs) + K.cur + cv() + [...K.open].join() + "/" + [...K.shut].join() + JSON.stringify(alist);
  K.panelAnims = () => {
    if (!ST.char) return '<p class="note" style="padding:10px">Mở một nhân vật để xem anim của nó.</p>';
    if (!alist) { anims(); loadReqs(); return '<div class="sub" style="padding:10px">Đang tải anim…</div>'; }
    const top = `<div class="kpahead"><button class="on" data-k="newanim" title="Gửi yêu cầu anim mới cho AI: AI lập phân tích + bảng pha để duyệt, rồi tạo ảnh key pose">+ Anim mới</button></div>`;
    const rq = areqs.length ? `<div class="kpareqs"><div class="sub">Chờ AI</div>${areqs.map(r => `<div class="kpareq" title="${esc(r.desc || "")}"><b>${esc(r.name)}</b><span class="st ${r.status || "sent"}">${AST[r.status] || r.status || "Đã gửi"}</span>${r.reply ? `<div class="sub">AI: ${esc(r.reply)}</div>` : ""}</div>`).join("")}</div>` : "";
    if (!alist.length) return `<div class="kpanims">${top}${rq}<p class="note" style="padding:4px 2px">Nhân vật này chưa có anim.</p></div>`;
    const open = a => K.open.has(a.id) || (a.id === K.cur && !K.shut.has(a.id));
    return `<div class="kpanims">${top}${rq}${alist.map(a => `<div class="kpatree ${open(a) ? "open" : ""}"><div class="kparow"><button class="kpcaret" data-k="fold" data-id="${esc(a.id)}" title="${open(a) ? "Thu gọn" : "Mở các góc"}" ${a.views && a.phases ? "" : "disabled"}>${open(a) ? "▾" : "▸"}</button><button class="kpanim ${a.id === K.cur ? "on" : ""}" data-k="anim" data-id="${esc(a.id)}" title="${esc(a.id)}">
      <b>${esc(a.name)}</b><span class="sub">${a.err ? "lỗi đọc" : !a.job ? "chưa có ảnh" : !a.phases ? a.imgs + " key · chưa có bảng pha" : a.phases + " pha · " + a.keys + " key"}${a.miss ? ` · <span class="s-bad">thiếu ${a.miss}</span>` : a.phases ? " · đủ ảnh" : ""}</span></button><button class="kpadd" data-k="addview" data-id="${esc(a.id)}" title="Thêm / bớt góc của nhân vật">+</button></div>
      ${open(a) && a.views && a.phases ? `<div class="kpvlist">${a.views.map(x => `<button class="kpview ${a.id === K.cur && x.v === cv() ? "on" : ""}" data-k="view" data-id="${esc(a.id)}" data-v="${x.v}" title="Xem góc ${VL[x.v]}${x.main ? " (góc chính)" : ""}">${ST.ic("img")}<span>${VL[x.v]}${x.main ? " ·  chính" : ""}</span><span class="sub">${x.miss ? `<span class="s-bad">thiếu ${x.miss}</span>` : "đủ ảnh"}</span></button>`).join("")}</div>` : ""}</div>`).join("")}
      <button class="kplink" data-k="reanims" title="Đọc lại danh sách">↻ Đọc lại</button></div>`;
  };
  ST.IC.img = '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="M3 17l5-5 4 4 3-3 6 6"/>';
  addEventListener("keydown", e => { if (!P.on || /INPUT|TEXTAREA|SELECT/.test((e.target || {}).tagName || "") || document.body.classList.contains("noting")) return;
    if (e.key === "Escape" && !P.own) { P.close(); e.stopImmediatePropagation(); return; }
    if (!P.own) return;
    if (e.key === " ") { e.preventDefault(); e.stopImmediatePropagation(); P.toggle(); }
    else if (e.key === "ArrowLeft" || e.key === "ArrowRight") { e.preventDefault(); e.stopImmediatePropagation(); P.jump(e.key === "ArrowRight" ? 1 : -1); } }, true);
  K.player = P;

  function viewsDialog() {
    if (!data || !data.job) return;
    const all = (data.views && data.views.all) || Object.keys(VL), use = vuse(), cr = (data.views && data.views.camref) || {};
    ST.dialog("Góc nhìn ảnh key · " + data.job.split("/").pop(), `<div style="display:grid;gap:8px;min-width:320px">
      <p class="note" style="margin:0">Chọn các góc dùng cho nhân vật này (mọi anim của nhân vật). Góc chính: ảnh được duyệt trước, các góc khác AI dựng lại từ ảnh góc chính đã ★. Mọi góc là camera <b>trực giao (Orthographic)</b>, chiếu vuông góc như cam front / side / top của Maya. "Ảnh model làm khung" = ảnh render trực giao của model ở góc đó (chưa có thì nhờ Claude render).</p>
      <table class="kpvt"><tr><th>Góc</th><th>Dùng</th><th>Chính</th><th>Ảnh model làm khung</th></tr>${all.map(v => `<tr><td>${VL[v] || v}</td><td><input type="checkbox" data-u="${v}" ${use.includes(v) ? "checked" : ""}></td><td><input type="radio" name="kpmain" value="${v}" ${v === vmain() ? "checked" : ""}></td><td class="sub">${cr[v] ? "có" : "chưa có"}</td></tr>`).join("")}</table>
      <p class="s-bad" id="kvErr" style="margin:0"></p>
      <div class="row" style="gap:8px;justify-content:flex-end"><button id="kvNo">Huỷ</button><button class="on" id="kvOk">Lưu</button></div></div>`, b => {
      b.querySelector("#kvNo").onclick = () => ST.closeDialog();
      b.querySelector("#kvOk").onclick = async () => {
        const u = [...b.querySelectorAll("[data-u]")].filter(i => i.checked).map(i => i.dataset.u), m = (b.querySelector("[name=kpmain]:checked") || {}).value;
        try { await post("/api/keypose/views", { clip: clipId(), use: u, main: m }); ST.closeDialog(); load.sig = ""; await load(); P.draw(); anims(true); ST.refresh(); }
        catch (e) { b.querySelector("#kvErr").textContent = "Không lưu được: " + e.message + oldSrv(e.message); }
      };
    });
  }
  function request(key, base, text) {
    const keys = [...new Set(data.keys.map(k => k.key).concat(key ? [key] : []))];
    ST.dialog("Yêu cầu ảnh key pose · " + (ST.mods.pose.nodeLabel ? ST.mods.pose.nodeLabel().replace(/^Anim · /, "") : ""), `<div style="display:grid;gap:8px;min-width:320px;max-width:520px">
      <div class="row" style="gap:8px;flex-wrap:wrap"><label class="sub">Key <select id="kqKey">${keys.map(k => `<option ${k === key ? "selected" : ""}>${esc(k)}</option>`).join("")}<option value="__new" ${!key ? "selected" : ""}>+ Key mới…</option></select></label>
        <label class="sub" id="kqNewW">Tên key mới <input id="kqNew" placeholder="vd k6_recoil" size="14"></label>
        <label class="sub">Số ảnh <select id="kqN"><option>1</option><option selected>2</option><option>3</option><option>4</option></select></label></div>
      <div class="row" style="gap:8px;align-items:flex-start"><label class="sub">Dựa trên ảnh <select id="kqBase"></select></label><img id="kqImg" alt="" style="max-width:110px;max-height:110px;object-fit:contain;background:#8882;border-radius:6px"></div>
      <label class="sub">Cần sửa gì / ảnh mới thế nào <textarea id="kqText" rows="4" style="width:100%" placeholder="vd: nỏ to hơn khoảng 20%, người ngả ra sau nhiều hơn"></textarea></label>
      <p class="note" style="margin:0">Mỗi ảnh khoảng 1,5 phút, tạo lần lượt. Ảnh mới tự hiện trong key của anim này.</p><p class="s-bad" id="kqErr" style="margin:0"></p>
      <div class="row" style="gap:8px;justify-content:flex-end"><button id="kqNo">Huỷ</button><button class="on" id="kqOk">Gửi cho AI</button></div></div>`, b => {
      const q = s => b.querySelector(s);
      const fill = sel => {
        const k = q("#kqKey").value, isNew = k === "__new", g = group(k); q("#kqNewW").hidden = !isNew;
        const imgs = isNew || !g ? data.keys.flatMap(x => x.images) : g.images, none = isNew || !g;
        const star = imgs.slice().reverse().find(i => mk(i.name).mark === "star");
        q("#kqBase").innerHTML = (none ? `<option value="">(không, chỉ theo mô tả)</option>` : "") + imgs.slice().reverse().map(i => `<option>${esc(i.name)}</option>`).join("");
        q("#kqBase").value = sel || (none ? "" : (star || imgs[imgs.length - 1]).name); show();
      };
      const show = () => { const im = imgOf(q("#kqBase").value); q("#kqImg").src = im ? im.url : ""; q("#kqImg").hidden = !im; };
      q("#kqKey").onchange = () => fill(); q("#kqBase").onchange = show; fill(base);
      if (text) q("#kqText").value = text;
      b.querySelectorAll("input,textarea,select").forEach(i => i.addEventListener("keydown", e => { e.stopPropagation(); if (e.key === "Escape") ST.closeDialog(); }));
      q("#kqNo").onclick = () => ST.closeDialog(); setTimeout(() => q("#kqText").focus(), 0);
      q("#kqOk").onclick = async () => {
        let k = q("#kqKey").value; const t = q("#kqText").value.trim();
        if (k === "__new") { k = q("#kqNew").value.trim().replace(/[^A-Za-z0-9_]+/g, "_"); if (!k) { q("#kqErr").textContent = "Nhập tên key mới."; return q("#kqNew").focus(); } }
        if (!t) { q("#kqErr").textContent = "Ghi cần sửa gì / ảnh mới thế nào."; return q("#kqText").focus(); }
        q("#kqOk").disabled = true;
        try {
          const known = data.keys.some(x => x.key === k) || (data.phases || []).some(p => p.key === k);
          if (!known) await post("/api/keypose/assign", { clip: clipId(), key: k, on: true });   // key mới: gắn trước, ảnh ra là hiện
          await post(`${NS}/requests`, { job: data.job, clip: clipId(), key: k, base: q("#kqBase").value || "", text: t, n: +q("#kqN").value, by: who(), at: new Date().toISOString(), sent: true, status: "sent", from: "studio" });
          ST.closeDialog(); ST.toast("Đã gửi cho AI"); load.sig = ""; load();
        } catch (e) { q("#kqErr").textContent = "Không gửi được: " + e.message; q("#kqOk").disabled = false; }
      };
    });
  }

  K.panel_click = async e => {
    if (e.target.closest("#kpNotes") && ST.mods.notes && ST.mods.notes.panel_click) return ST.mods.notes.panel_click(e);
    const b = e.target.closest("[data-k]"); if (!b) return;
    if (b.dataset.k === "anim") { P.close(); K.pickClip(b.dataset.id); return P.open(); }
    if (b.dataset.k === "reanims") return anims(true);
    if (!data) return;
    const a = b.dataset.k, host = b.closest("[data-key]"), key = b.dataset.key || (host && host.dataset.key);
    const nh = b.closest("[data-n]"), n = b.dataset.n || (nh && nh.dataset.n);
    if (a === "goph") { P.stop(); P.frame = +b.dataset.f; P.draw(); return; }
    if (a === "zoom") return zoom(b.src, b.alt);
    if (a === "pick") { pick[key + "@" + cv()] = n; if (P.on) P.draw(); return ST.refresh(); }
    if (a === "choose") {
      const g = group(key), patch = {}, cur = chosen(key), explicit = g && g.images.some(i => mk(i.name).mark === "star");
      if (cur && cur.name === n && explicit) return;
      for (const i of g ? g.images : []) { const m = mk(i.name); if (i.name === n) patch[i.name] = Object.assign({}, m, { mark: "star", by: who() || m.by || "" }); else if (m.mark === "star") patch[i.name] = Object.assign({}, m, { mark: "" }); }
      Object.assign(marks, patch); rev++; ST.refresh(); if (P.on) P.draw();   // rev: panel vẽ lại ngay, không chờ server
      await api(`${NS}/marks/${docId(data.job)}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(patch) }); load.sig = ""; load(); return;
    }
    if (a === "star" || a === "reject") return saveMark(n, { mark: mk(n).mark === a ? "" : a });
    if (a === "redo") return request(key, n);
    if (a === "make") { const p = (data.phases || []).find(x => x.key === key); return request(key, "", p ? `${p.name} (F${p.f}): ${p.desc || ""}`.trim() : ""); }
    if (a === "req") return request(data.keys[0] && data.keys[0].key);
    if (a === "makeview") {   // góc phụ: dựng từ ảnh góc chính đã chọn, không cần gõ gì
      b.disabled = true;
      try { await post(`${NS}/requests`, { job: data.job, clip: clipId(), key, view: cv(), base: n, text: "", n: 1, by: who(), at: new Date().toISOString(), sent: true, status: "sent", from: "studio-view" });
        ST.toast(`Đã gửi AI: góc ${VL[cv()]} của ${key} (khoảng 2–4 phút)`); load.sig = ""; load(); }
      catch (e) { b.disabled = false; ST.toast("Không gửi được: " + e.message); }
      return;
    }
    if (a === "play") { P.on ? P.close() : P.open(); return ST.refresh(); }
    if (a === "pin") return setPin(n);
    if (a === "other") { showOther = !showOther; return ST.refresh(); }
    if (a === "assign") return write("/api/keypose/assign", { key, on: true });
    if (a === "unassign") return write("/api/keypose/assign", { key, on: false });
  };
  K.panel_change = e => {
    const t = e.target;
    if (t.classList.contains("kpnote")) return saveMark(t.dataset.n, { note: t.value }).then(() => ST.toast("Đã lưu ghi chú"));
    if (t.classList.contains("kpf")) {
      const f = t.value === "" ? null : Math.max(1, Math.round(+t.value));
      if (t.dataset.i != null) return write("/api/keypose/phase", { i: +t.dataset.i, f });
      if (t.dataset.key && f) return write("/api/keypose/phase", { i: -1, key: t.dataset.key, f });
    }
  };

  // đổi anim: tải lại; panel đang mở hoặc đang chạy ảnh: đọc lại mỗi 4 s (ảnh mới từ AI, trạng thái yêu cầu, đánh dấu của người khác)
  ST.on("pose:clip", () => { if (IK()) return; loadedFor = null; load.sig = ""; pick = {}; if (pin) setPin(pin); if (P.on) { P.frame = 0; load(); } if (myTab()) ST.refresh(); });
  ST.on("char", () => { loadedFor = null; data = null; if (ST.ws !== "imagekey") P.close(); });
  setInterval(() => { if ((myTab() || P.on) && clipId() && document.visibilityState === "visible") load(); }, 4000);
  K.data = () => data;

  ST.cmd({ id: "keypose.open", menu: "Window", label: "Image Key của anim", icon: "img", global: true, keep: true, on: () => !!clipId(), run: () => {
    if (ST.tabs && !ST.tabs().includes("keypose:list")) ST.setWS("pose");
    ST.pref.set("tab:" + ST.ws, "keypose:list"); ST.refresh();
  } });
  ST.cmd({ id: "keypose.play", menu: "Window", label: "Chạy Image Key của anim", icon: "img", global: true, keep: true, on: () => !!clipId(), run: async () => {
    if (loadedFor !== clipId()) { loadedFor = null; await load(); }
    if (!data || !(data.phases || []).length) return ST.toast("Anim này chưa có bảng pha key pose.");
    P.open();
  } });
})();
