// AI Anim Studio — Tệp → Lưu cảnh… / Mở cảnh…: một file .aas (zip) chứa nhân vật + rig + kho + anim Pose,
// mang sang máy khác như .ma / .blend (tools/home/scene_file.py, /api/scene/save, /api/scene/open).
(function () {
  const esc = ST.esc, $ = ST.$;
  const b64 = f => new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(String(r.result).split(",")[1]); r.onerror = () => rej(r.error); r.readAsDataURL(f); });
  async function post(body) {
    const r = await fetch("/api/scene/open", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const j = await r.json(); if (!j.ok) throw new Error(j.error || r.status); return j.id;
  }

  function save() {
    ST.run("file.save");   // ghi nốt sửa mesh đang chờ vào kho trước khi gói
    setTimeout(() => {
      const a = document.createElement("a");
      a.href = "/api/scene/save/" + encodeURIComponent(ST.char.id); a.download = "";
      document.body.appendChild(a); a.click(); a.remove();
      ST.toast("Đang lưu cảnh " + ST.char.name + " (.aas)…");
    }, 400);
  }

  let data = null;
  function open() {
    data = null;
    ST.dialog("Mở cảnh", `<div class="row"><input type="file" id="aasIn" accept=".aas,.zip"></div>
      <p class="note">File .aas lưu từ Tệp → Lưu cảnh… (máy này hoặc máy khác): mesh, rig, skin, ghi chú và các phiên bản Pose của một nhân vật.</p><div id="aasOut"></div>`, b => {
      b.querySelector("#aasIn").onchange = e => { const f = e.target.files[0]; if (f) read(f); };
      b.onclick = click;
    });
  }
  async function read(f) {
    const out = $("aasOut"); out.innerHTML = `<div class="sub">Đang đọc ${esc(f.name)} (${(f.size / 1048576).toFixed(1)} MB)…</div>`;
    let info;
    try { data = await b64(f); info = await post({ zip_b64: data, dry: true }); }
    catch (e) { data = null; out.innerHTML = `<div class="s-bad">Không đọc được: ${esc(e.message || e)}</div>`; return; }
    out.innerHTML = `<p><b>${esc(info.name)}</b> <span class="sub">· ${esc(info.id)} · lưu ${esc((info.saved || "").replace("T", " "))} · ${info.files} file</span></p>
      ${info.clips.length ? `<p class="sub">Anim: ${info.clips.map(esc).join(", ")}</p>` : ""}
      ${info.exists ? `<p class="s-bad">Máy này đã có ${esc(info.id)}: mở cảnh sẽ ghi đè mesh, rig, kho và anim của nhân vật này bằng bản trong file.</p>` : ""}
      <div class="row"><button class="on" data-a="go">${ST.ic("open")} ${info.exists ? "Ghi đè và mở" : "Mở cảnh"}</button></div><div class="note" id="aasMsg"></div>`;
  }
  async function click(e) {
    const a = e.target.closest("button[data-a]"); if (!a || a.disabled || !data) return;
    a.disabled = true; $("aasMsg").textContent = "Đang bung file và build lại trang…";
    try {
      const r = await post({ zip_b64: data });
      $("aasMsg").textContent = "Đã mở " + r.id + (r.warn ? " · " + r.warn : "") + ". Đang tải…";
      const u = new URL("/studio/" + encodeURIComponent(r.id), location.origin); u.searchParams.set("ws", ST.ws || "general"); location.href = u;
    } catch (err) { a.disabled = false; $("aasMsg").textContent = "Không mở được: " + (err.message || err); }
  }

  ST.cmd({ id: "file.sceneOpen", global: true, menu: "File", sep: true, label: "Mở cảnh…", icon: "open", key: "ctrl+shift+o", run: open });
  ST.cmd({ id: "file.sceneSave", global: true, menu: "File", label: "Lưu cảnh…", icon: "save", key: "ctrl+shift+s", on: () => !!ST.char, run: save });
  // đặt ngay sau "Nhập FBX…" trong menu Tệp
  const all = [...ST.cmds.entries()], i = all.findIndex(([k]) => k === "file.fbx");
  if (i >= 0) { const mine = all.filter(([k]) => k === "file.sceneOpen" || k === "file.sceneSave"), rest = all.filter(([k]) => k !== "file.sceneOpen" && k !== "file.sceneSave");
    rest.splice(rest.findIndex(([k]) => k === "file.fbx") + 1, 0, ...mine); ST.cmds.clear(); rest.forEach(([k, v]) => ST.cmds.set(k, v)); }
})();
