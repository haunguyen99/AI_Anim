// AI Anim Studio — workspace Pose (S4): lõi Pose Lab (modules/pose_engine.js, sinh bằng port_pose.py) chạy trong viewport chung.
// Giao diện Pose Lab dựng lại từ HTML gốc rồi đặt vào vỏ Studio: thanh công cụ → shelf, Khớp / Vật lý / Ghi chú / Phiên bản → tab dock,
// timeline (key, lane, Timing, transport) → vùng timeline, HUD / camera / ref / vẽ ghi chú → lớp phủ viewport. Một anim mỗi lần
// (đổi anim = tải lại với ?clip=…), lưu cùng kho với Pose Lab cũ (<tiêu đề trang>_pose_lab).
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
  const goClip = id => { const u = new URL(location.href); u.searchParams.set("clip", id); u.searchParams.set("ws", "pose"); ST.pref.set(prefKey(), id); location.href = u; };

  // ---- dựng giao diện Pose Lab, chia khối cho các vùng của Studio
  function buildDom() {
    stash = document.createElement("div"); stash.id = "poseStash"; stash.hidden = true; document.body.appendChild(stash);
    const w = document.createElement("div"); w.innerHTML = ST.POSE_HTML;
    const wrap = (cls, node, inner) => { const d = document.createElement("div"); d.className = "pz " + cls; if (inner) { const i = document.createElement("div"); i.className = inner; i.appendChild(node); d.appendChild(i); } else d.appendChild(node); stash.appendChild(d); return d; };
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
  function makeHost(ns) {
    const alive = () => ST.ws === "pose";
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
      cam: () => V.active.cam, alive,
      scenes: (s, o) => { scenes = { scene: s, overlay: o }; if (ST.ws === "pose") V.extra = scenes; },
      resize: () => V.resize(), renderNow: () => V.renderNow(),
      onFrame: f => V.onFrame(now => { if (alive()) f(now); }),
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
      const fix = o => { for (const k in o) { const v = o[k]; if (typeof v === "string" && /^(models|refs|fbx)\//.test(v)) o[k] = "/work/pose_lab/" + v; else if (v && typeof v === "object") fix(v); } };
      POSES.forEach(fix);
      ST.pref.set(prefKey(), id);
      if (!parts) buildDom();
      eng = ST.poseEngine(POSES, makeHost(clipInfo.ns));
      state = "ready"; fillPicker();
      if (!ST.char) { const e = $("empty"); if (e) e.hidden = true; ST.$("charName").textContent = clipInfo.name; }
      else ST.$("charName").textContent = ST.char.name + " · " + clipInfo.name;
      M.enter();
    } catch (e) { console.error(e); state = "error"; err = e.message || String(e); }
    ST.refresh();
  }

  // ---- vào / ra workspace
  let saved = null;
  M.enter = () => {
    ST.mods.mesh.display("hidden");
    const tc = V.gizmo.tc;
    if (!saved) saved = { space: tc.space, size: tc.size, enc: V.renderer.outputEncoding };
    V.renderer.outputEncoding = THREE.sRGBEncoding;
    if (scenes) V.extra = scenes;
    if (parts) { V.gizmo.detach(); $("vp").appendChild(parts.overlay); parts.overlay.hidden = false; if (eng) { tc.setSpace($("mSpace") && /world/.test($("mSpace").textContent) ? "world" : "local"); } }
    if (!eng) ensure();
    ST.refresh();
  };
  M.leave = () => {
    V.extra = null; if (eng) eng.stopPlay();
    const tc = V.gizmo.tc; tc.detach();
    if (saved) { tc.setSpace(saved.space || "world"); tc.setSize(saved.size || 0.85); V.renderer.outputEncoding = saved.enc; saved = null; }
    if (parts) { parts.overlay.hidden = true; stash.appendChild(parts.overlay); [parts.shelf, parts.timeline].forEach(n => stash.appendChild(n)); }
  };

  // ---- vùng giao diện
  const msg = html => { const d = document.createElement("div"); d.className = "note"; d.style.padding = "10px 12px"; d.innerHTML = html; return d; };
  M.shelfNode = () => parts && eng ? parts.shelf : null;
  M.timelineNode = () => parts && eng ? parts.timeline : msg('<span class="sub">Timeline</span>');
  M.panelNode = t => {
    if (state === "loading" || state === "none") return msg("Đang nạp anim…");
    if (state === "error") return msg(`<span class="s-bad">Không nạp được anim: ${esc(err)}</span>`);
    if (state === "noclip") return msg(ST.char ? esc(ST.char.name) + " chưa có anim nào trong Pose Lab. Tạo anim ở Home (/home) hoặc gõ /new_clip." : "Chưa có anim nào trong Pose Lab.");
    if (t === "phys" && $("physBox") && $("physBox").hidden) return msg("Vật lý dùng cho phiên bản dạng key (làm trên trang). Phiên bản này là anim nướng sẵn: mở phiên bản key ở tab Phiên bản.");
    return { joint: parts.joint, phys: parts.phys, notes: parts.notes, versions: parts.versions }[t] || parts.joint;
  };
  M.info = () => { if (!eng) return "Pose · " + ({ loading: "đang nạp", noclip: "chưa có anim", error: "lỗi" }[state] || ""); const g = eng.get(); return (clipInfo ? clipInfo.name : "") + " · " + (g.P ? g.P.version : "") + " · F" + g.frame + "/" + (g.P ? g.P.frames : 1) + (g.sel ? " · " + g.sel : ""); };
  M.undo = () => eng && eng.undo(); M.canUndo = () => !!eng && eng.canUndo();
  M.bounds = () => { if (!eng || !eng.get().model) return null; return new THREE.Box3().setFromObject(eng.get().model); };

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
  M.olAct = (id, a, e) => {
    if (!eng) return; const n = String(id).slice(2);
    if (a === "fold") { open.has(n) ? open.delete(n) : open.add(n); ST.pref.set("pose:open", [...open]); return; }
    const g = eng.get();
    if (ST.addSel(e)) { const s = new Set(g.selSet); s.has(n) ? s.delete(n) : s.add(n); eng.setSelection([...s], n); } else eng.select(n);
  };
  ST.on("prerender", () => { if (ST.ws === "pose" && eng) { const g = eng.get(); const sig = (g.model ? g.model.uuid : "-") + ":" + g.frame + ":" + g.sel + ":" + g.selSet.size + ":" + g.playing; if (sig !== M._sig) { M._sig = sig; ST.refresh(); } } });

  // playblast → Review (như nút 🎞 của Home cũ): quay trên trang, server lưu webm + nén + thêm version Review
  ST.cmd({ id: "pose.playblast", menu: "Animate", sep: true, label: "Quay playblast và gửi sang Review…", icon: "export", on: () => !!eng && !!window.DDC && !!window.DDC.askPlayblast, run: async () => {
    try {
      const o = await window.DDC.askPlayblast(); if (!o) return;
      ST.toast("Đang quay playblast…"); const r = await window.DDC.playblast(o);
      const b64 = b => new Promise(res => { const f = new FileReader(); f.onload = () => res(String(f.result).split(",")[1]); f.readAsDataURL(b); });
      ST.toast("Đang lưu và nén video…");
      const j = await (await fetch("/api/playblast", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ clip: clipInfo.id, n: r.n, fps: r.fps, w: r.w, h: r.h, views: r.views, webm_b64: await b64(r.webm), thumb_b64: r.thumb ? await b64(r.thumb) : "" }) })).json();
      if (!j.ok) throw new Error(j.error); ST.toast("Đã thêm version " + j.id.version + " vào Review Lab");
    } catch (e) { ST.toast("Không gửi được: " + (e.message || e)); }
  } });
  ST.cmd({ id: "pose.oldlab", menu: "Animate", label: "Mở Pose Lab cũ của anim này", icon: "ext", on: () => !!clipInfo, run: () => window.open("/lab/pose/" + encodeURIComponent(clipInfo.id), "_blank") });
  ST.cmd({ id: "pose.clip", menu: "Animate", label: "Đổi anim…", icon: "pose", global: true, run: async () => {
    await loadClips();
    ST.dialog("Mở anim", (clips || []).length ? `<div class="list">${clips.map(c => `<button class="it" data-id="${esc(c.id)}">${ic("pose")}<span>${esc(c.name)}</span><small>${c.versions} bản · ${esc(c.stage)}</small></button>`).join("")}</div>` : '<p class="note">Chưa có anim nào.</p>', b => { b.onclick = e => { const x = e.target.closest("[data-id]"); if (x) goClip(x.dataset.id); }; });
  } });
})();
