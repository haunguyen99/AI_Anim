// AI Anim Studio — workspace Rig và Pose khi chưa chuyển xong (lộ trình S3–S5, docs/studio_design.md).
// Dùng chung cảnh + Outliner của module Mesh (chỉ xem), panel trỏ sang Rig Lab / Pose Lab cũ, menu Rig/Skin/Animate/Physics ghi bước sẽ chuyển.
(function () {
  const esc = ST.esc, ic = ST.ic, mesh = () => ST.mods.mesh;
  let clips = null;
  async function loadClips() {
    if (clips || !ST.char) return;
    try {
      const s = await (await fetch("/api/state")).json();
      clips = (s.clips || []).filter(c => c.labs && (c.labs.mesh === ST.char.id || c.labs.rig === ST.char.id));
    } catch (e) { clips = []; }
    ST.refresh();
  }
  const oldRig = () => ST.char ? "/lab/rig/" + encodeURIComponent(ST.char.id) : null;
  function mk(id, kind, step) {
    return {
      id,
      enter(w) { mesh().display(w.display); loadClips(); },
      leave() {},
      outline: () => mesh().outline(),
      olAct: (rid, a, e) => { if (a === "vis" || (ST.mods.skel && ST.mods.skel.isMine(rid))) mesh().olAct(rid, a, e); },
      bounds: s => mesh().bounds(false),
      info: () => mesh().info() + " · workspace " + ST.WS[id].label + " đang chuyển (" + step + ")",
      panel() {
        if (!ST.char) return `<h2>${kind === "rig" ? "Rig" : "Pose"}</h2><p class="note">Cảnh trống: mở nhân vật (Ctrl+O) hoặc nhập FBX (Ctrl+Shift+I) trước.</p>`;
        if (kind === "rig") return `<h2>Rig</h2><p class="note">Workspace Rig sẽ có landmark, xương, skin, cọ vẽ weight và cổng duyệt ngay trong viewport này (bước ${step}). Trong lúc chờ, dùng Rig Lab cũ: nó đọc mesh vừa sửa ở workspace General.</p>
          <div class="row"><a class="note" href="${esc(oldRig())}" target="_blank">${ic("ext")} Mở Rig Lab cũ của ${esc(ST.char ? ST.char.name : "")}</a></div>`;
        const list = clips === null ? '<div class="sub">Đang tải danh sách clip…</div>' : clips.length ? clips.map(c => `<div class="row"><a class="note" href="/lab/pose/${encodeURIComponent(c.id)}" target="_blank">${ic("ext")} ${esc(c.name || c.id)}</a><span class="sub">${esc(c.stage || "")}</span></div>`).join("") : '<div class="sub">Nhân vật này chưa có clip.</div>';
        return `<h2>Pose</h2><p class="note">Workspace Pose sẽ có phiên bản, key, timeline, IK/pole, physics và xuất FBX trong viewport này (bước ${step}). Trong lúc chờ, mở Pose Lab cũ của từng clip:</p>${list}`;
      },
      timeline: () => `<span class="sub">Timeline (${step})</span><div class="tlbar"></div>`,
    };
  }

  // menu: lệnh sẽ chuyển (mờ) + lối sang Lab cũ
  const later = (menu, label, step) => ST.cmd({ id: "later." + menu + "." + label, menu, label: label + " (" + step + ")", on: () => false, tip: "Chưa chuyển vào Studio: bước " + step });
  ST.cmd({ id: "rig.oldlab", menu: "Rig", sep: true, label: "Mở Rig Lab cũ", icon: "ext", on: () => !!ST.char, run: () => open(oldRig(), "_blank") });
})();
