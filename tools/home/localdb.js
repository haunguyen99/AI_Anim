/*LOCALDB*/
// Kho dữ liệu trên máy cho các Lab khi không có db của claude.ai: nói chuyện với Home server (tools/home/store.py), ghi file thật vào work/store/<ns>/.
// Cùng giao diện với db của artifact (doc/collection, get/set/update/delete/add/onSnapshot) nên mã Lab không phải đổi.
// Kèm nút "Lưu trữ" (xuất / mở file .json). Nguồn: tools/home/localdb.js, nhúng bằng work/patch_localdb.py.
(function () {
  const API = (window.LOCALDB_API || "http://127.0.0.1:8780") + "/api/store";
  const slug = s => String(s || "page").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_|_$/g, "").slice(0, 80) || "page";
  const NS = (new URLSearchParams(location.search).get("ns")) || slug(document.title);
  const enc = encodeURIComponent;
  async function call(method, path, body) {
    const r = await fetch(API + "/" + path, { method, headers: body !== undefined ? { "Content-Type": "application/json" } : {}, body: body !== undefined ? JSON.stringify(body) : undefined });
    if (!r.ok) throw new Error("store " + r.status);
    return r.json();
  }
  const snapOf = (id, data) => ({ id, exists: data !== null && data !== undefined, data: () => data });
  const watchers = {};   // col → { subs:Set, last:string, timer }
  async function fetchCol(col) { const r = await call("GET", enc(NS) + "/" + enc(col)); return r.docs; }
  const colSnap = docs => { const d = docs.map(x => snapOf(x.id, x.data)); return { docs: d, size: d.length, empty: !d.length, forEach: f => d.forEach(f) }; };
  async function tick(col) {
    const w = watchers[col]; if (!w || !w.subs.size) return;
    try {
      const docs = await fetchCol(col), sig = JSON.stringify(docs);
      if (sig !== w.last) { w.last = sig; const sn = colSnap(docs); w.subs.forEach(f => { try { f(sn); } catch (e) { console.error(e); } }); }
    } catch (e) {}
  }
  const poke = col => { if (watchers[col]) tick(col); };
  function docRef(col, id) {
    const base = () => enc(NS) + "/" + enc(col) + "/" + id.split("/").map(enc).join("/");
    return {
      id, path: col + "/" + id,
      get: async () => { const r = await call("GET", base()); return snapOf(id, r.exists ? r.data : null); },
      set: async d => { await call("PUT", base(), d); poke(col); },
      update: async d => { await call("PATCH", base(), d); poke(col); },
      delete: async () => { await call("DELETE", base()); poke(col); },
    };
  }
  function colRef(col) {
    return {
      id: col, doc: id => docRef(col, id),
      get: async () => colSnap(await fetchCol(col)),
      add: async d => { const r = await call("POST", enc(NS) + "/" + enc(col), d); poke(col); return docRef(col, r.id); },
      onSnapshot: cb => {
        const w = watchers[col] || (watchers[col] = { subs: new Set(), last: null, timer: 0 });
        w.subs.add(cb); w.last = null; tick(col);
        if (!w.timer) w.timer = setInterval(() => tick(col), 2000);
        return () => { w.subs.delete(cb); if (!w.subs.size) { clearInterval(w.timer); w.timer = 0; } };
      },
    };
  }
  const db = { isLocal: true, ns: NS, doc: path => { const [c, ...r] = path.split("/"); return docRef(c, r.join("/")); }, collection: colRef };
  window.localDB = async function () {
    try {
      const ctl = new AbortController(), t = setTimeout(() => ctl.abort(), 1200);
      const r = await fetch(API + "/_ping", { signal: ctl.signal }); clearTimeout(t);
      if (!r.ok) return null; await r.json(); return db;
    } catch (e) { return null; }
  };

  // ---- nút Lưu trữ: nơi lưu hiện tại, xuất / mở file .json
  const ICON = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.700 3.100 3 7 3s7-1.300 7-3V6M5 12v6c0 1.700 3.100 3 7 3s7-1.300 7-3v-6"/></svg>';
  const css = document.createElement("style");
  css.textContent = ".dbw{position:relative;display:inline-flex;align-items:center}.dbw>button{display:inline-flex;align-items:center;justify-content:center;width:34px;height:30px;padding:0;border-radius:8px;border:1px solid var(--line,#2a2f38);background:var(--raise,var(--panel,#1d2026));color:var(--fg,var(--text,#e6e9ee));cursor:pointer;position:relative}.dbw>button i{position:absolute;right:4px;top:4px;width:7px;height:7px;border-radius:50%;background:#3ab06f}.dbw>button.warn i{background:#e3a008}.dbm{position:fixed;z-index:60;min-width:250px;max-width:min(340px,calc(100vw - 16px));padding:10px;border-radius:10px;background:var(--panel,#1d2026);color:var(--fg,var(--text,#e6e9ee));border:1px solid var(--line,#2a2f38);box-shadow:0 8px 24px #0004;font:12px/1.4 system-ui,sans-serif;display:none}.dbm.show{display:block}.dbm b{display:block;font-size:12px;margin-bottom:2px}.dbm p{margin:0 0 8px;color:var(--mute,var(--muted,#8b93a0));word-break:break-all}.dbm .r{display:flex;gap:6px}.dbm button{flex:1;height:32px;border-radius:8px;border:1px solid var(--line,#2a2f38);background:var(--raise,var(--bg,#14161a));color:inherit;cursor:pointer;font:inherit}.dbm .t{margin-top:8px;color:var(--accent,#4aa3ff)}body.tm .dbw>button{width:40px;height:40px}body.tm .dbm button{height:40px}";
  document.head.appendChild(css);
  window.dbWidget = function (o) {
    const { db: d, cols, host } = o;
    if (document.getElementById("dbW")) document.getElementById("dbW").remove();
    const local = !!(d && d.isLocal), ok = !!d;
    const where = local ? "Máy này: work/store/" + NS : ok ? "claude.ai: AI đọc được" : "Chỉ trình duyệt này (chưa nối kho)";
    const w = document.createElement("span"); w.className = "dbw"; w.id = "dbW";
    w.innerHTML = '<button type="button" title="Lưu trữ: xuất / mở file" aria-label="Lưu trữ" class="' + (ok ? "" : "warn") + '">' + ICON + '<i></i></button><div class="dbm" role="dialog"><b>Nơi lưu</b><p>' + where + '</p><div class="r"><button type="button" data-a="ex">Xuất file</button><button type="button" data-a="im">Mở file</button></div><div class="t" hidden></div><input type="file" accept=".json,application/json" hidden></div>';
    const hostEl = (host && document.querySelector(host)) || null;
    if (hostEl) hostEl.appendChild(w); else { w.style.cssText = "position:fixed;right:8px;bottom:8px;z-index:50"; document.body.appendChild(w); }
    const btn = w.querySelector("button"), menu = w.querySelector(".dbm"), msg = w.querySelector(".t"), file = w.querySelector("input");
    const say = t => { msg.textContent = t; msg.hidden = !t; };
    btn.onclick = e => { e.stopPropagation(); const on = !menu.classList.contains("show"); menu.classList.toggle("show", on); if (on) { const r = btn.getBoundingClientRect(); menu.style.top = Math.min(r.bottom + 6, innerHeight - menu.offsetHeight - 8) + "px"; menu.style.left = Math.max(8, Math.min(r.left, innerWidth - menu.offsetWidth - 8)) + "px"; } };
    document.addEventListener("click", e => { if (!w.contains(e.target)) menu.classList.remove("show"); });
    w.addEventListener("click", async e => {
      const a = e.target.closest("[data-a]"); if (!a) return;
      if (a.dataset.a === "im") { file.click(); return; }
      if (!d) { say("Chưa có kho để xuất. Mở bằng Home hoặc trên claude.ai."); return; }
      try {
        const out = { format: "ddc-store-v1", ns: NS, title: document.title, at: new Date().toISOString(), collections: {} };
        for (const c of cols) { const sn = await d.collection(c).get(); out.collections[c] = {}; sn.docs.forEach(s => { if (s.exists) out.collections[c][s.id] = s.data(); }); }
        const n = Object.values(out.collections).reduce((s, c) => s + Object.keys(c).length, 0);
        const name = NS + "_" + new Date().toISOString().slice(0, 10) + ".json", blob = new Blob([JSON.stringify(out)], { type: "application/json" });
        let saved = false;
        try { if (window.claude && window.claude.use) { const dl = await window.claude.use("downloads"); if (dl) { await dl.save({ filename: name, data: blob }); saved = true; } } } catch (e2) {}
        if (!saved) { const u = URL.createObjectURL(blob), an = document.createElement("a"); an.href = u; an.download = name; document.body.appendChild(an); an.click(); an.remove(); setTimeout(() => URL.revokeObjectURL(u), 4000); }
        say("Đã xuất " + n + " mục → " + name);
      } catch (err) { say("Không xuất được: " + (err.message || err)); }
    });
    file.onchange = async () => {
      const f = file.files[0]; file.value = ""; if (!f) return;
      try {
        const o2 = JSON.parse(await f.text());
        if (o2.format !== "ddc-store-v1" || !o2.collections) throw new Error("không phải file lưu của Lab");
        if (!d) throw new Error("chưa có kho để ghi");
        let n = 0; for (const c in o2.collections) for (const id in o2.collections[c]) { await d.doc(c + "/" + id).set(o2.collections[c][id]); n++; }
        say("Đã mở " + n + " mục từ " + f.name + (o2.ns && o2.ns !== NS ? " (nguồn: " + o2.ns + ")" : "") + ". Tải lại trang để thấy.");
      } catch (err) { say("Không mở được: " + (err.message || err)); }
    };
  };
})();
