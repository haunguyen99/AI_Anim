// Mục "Tham số anim" (2026-10-31). Script dựng anim khai báo tham số (tools/spine/anim_params.py -> <thư mục>/params.json);
// ở đây hiện thanh trượt cho nhóm của anim đang xem (+ nhóm dùng chung anim "*", vd Physics). Đổi giá trị -> server ghi
// rồi chạy lại script (POST /api/spine/params), file đổi -> trang tự nạp lại, giữ frame. Một lần đổi = một bước Hoàn tác.
// Tự đánh giá Spine Live: sửa nhỏ kiểu "nhắm mắt từ F20" trước phải qua Claude sửa script, chậm hơn kéo key trong Spine.
(() => {
  const box = document.createElement("div");
  box.id = "parBox"; box.className = "sec tool animOnly";
  box.innerHTML = `<h3 class="secT">Tham số anim</h3><span id="parInfo" class="mute"></span>
    <div id="parList"></div>
    <div class="row"><label title="Thả thanh trượt / đổi số là dựng lại ngay"><input type="checkbox" id="parAuto">Tự dựng lại</label>
      <button id="parApply" class="primary" title="Ghi các giá trị đang chỉnh rồi chạy lại script dựng anim">Dựng lại</button></div>
    <div id="parSt" style="color:var(--mute)"></div>`;
  ($("physBox") || $("noteBox")).before(box);
  const st = document.createElement("style");
  st.textContent = `
    #parList{display:flex;flex-direction:column;gap:4px} #parList .pg{font-weight:600;margin-top:4px;display:flex;gap:6px;align-items:center}
    #parList .pr{display:grid;grid-template-columns:1fr 64px;gap:2px 6px;align-items:center}
    #parList .pr span{grid-column:1/3;color:var(--mute);font-size:11px} #parList .pr input[type=range]{width:100%}
    #parList .pr input[type=number]{width:64px} #parList .pr.chg span{color:#ffd21a}`;
  document.head.appendChild(st);
  const P = { data: null, key: "", pend: {}, busy: false, timer: null };
  $("parAuto").checked = store.get("parAuto", "1") === "1";
  $("parAuto").onchange = () => store.set("parAuto", $("parAuto").checked ? "1" : "0");

  const groupsFor = a => Object.entries(P.data?.groups || {}).filter(([, g]) => g.anim === a || g.anim === "*")
    .sort((x, y) => (x[1].anim === "*") - (y[1].anim === "*"));
  function render() {
    const a = curAnim(), list = $("parList"), gs = groupsFor(a);
    $("parInfo").textContent = gs.length ? "" : "Anim này chưa có tham số (script dựng anim chưa khai báo)";
    list.innerHTML = "";
    for (const [gid, g] of gs) {
      const h = document.createElement("div"); h.className = "pg";
      h.innerHTML = `<span>${g.label}</span>`;
      const rs = document.createElement("button"); rs.textContent = "Mặc định"; rs.title = "Đưa cả nhóm về giá trị mặc định rồi dựng lại";
      rs.onclick = () => apply(gid, true); h.appendChild(rs); list.appendChild(h);
      for (const d of g.defs) {
        const v = P.pend[gid]?.[d.key] ?? g.values?.[d.key] ?? d.default;
        const row = document.createElement("div"); row.className = "pr" + (v !== d.default ? " chg" : "");
        row.title = `${d.key} · mặc định ${d.default}${d.unit ? " " + d.unit : ""} · ${d.min} .. ${d.max}`;
        row.innerHTML = `<span>${d.label}</span><input type="range" min="${d.min}" max="${d.max}" step="${d.step}" value="${v}"><input type="number" min="${d.min}" max="${d.max}" step="${d.step}" value="${v}">`;
        const [r, n] = row.querySelectorAll("input");
        const set = (x, commit) => {
          x = Math.min(d.max, Math.max(d.min, +x)); r.value = x; n.value = x;
          (P.pend[gid] ||= {})[d.key] = x; row.classList.toggle("chg", x !== d.default);
          if (commit && $("parAuto").checked) { clearTimeout(P.timer); P.timer = setTimeout(() => apply(gid), 250) }
        };
        r.oninput = () => set(r.value, false); r.onchange = () => set(r.value, true);
        n.onchange = () => set(n.value, true);
        list.appendChild(row);
      }
    }
  }
  async function load(force) {
    if (!cur) return;
    const key = cur.json + "|" + curAnim();
    if (!force && key === P.key) return;
    P.key = key;
    try { P.data = await (await fetch("/api/spine/params?json=" + encodeURIComponent(cur.json), { cache: "no-store" })).json() } catch { P.data = null }
    render();
  }
  async function apply(gid, reset) {
    if (!cur) return;
    if (ed.dirty.size) return setStatus("đang có " + ed.dirty.size + " xương sửa chưa key: Key pose hoặc Bỏ sửa trước khi dựng lại", "bad");
    const ids = gid ? [gid] : Object.keys(P.pend);
    if (!ids.length) return setStatus("chưa đổi tham số nào", "");
    if (P.busy) { P.again = true; return }
    P.busy = true;
    try {
      for (const g of ids) {
        $("parSt").textContent = "đang dựng lại " + (P.data?.groups?.[g]?.label || g) + "…";
        const t0 = performance.now();
        const j = await edPost("/api/spine/params", { json: cur.json, group: g, values: P.pend[g] || {}, reset: !!reset });
        delete P.pend[g];
        $("parSt").textContent = `xong ${((performance.now() - t0) / 1000).toFixed(1)} s · ${hhmmss()} (Ctrl+Z / Hoàn tác để lùi)`;
        setStatus("đã dựng lại theo tham số: " + j.log.join(" · "), "ok");
      }
      await load(true);
    } catch (e) { $("parSt").textContent = "lỗi: " + e.message; setStatus("dựng lại lỗi: " + e.message, "bad") }
    P.busy = false;
    if (P.again) { P.again = false; apply() }
  }
  $("parApply").onclick = () => apply();
  setInterval(() => { if (!document.hidden) load() }, 800);
  window.spineParams = { load, P, apply };
})();
