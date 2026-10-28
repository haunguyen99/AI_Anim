// AI Anim Studio — Tệp → Nhập FBX: gửi file lên Home server (tools/home/fbx_import.py, đọc không cần Blender),
// rồi thay mesh trùng tên / thêm vào cảnh (có undo, lưu như mọi sửa mesh) hoặc tạo nhân vật mới (work/rig_lab/chars/<id>).
(function () {
  const esc = ST.esc, ic = ST.ic, $ = ST.$;
  const b64 = f => new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(String(r.result).split(",")[1]); r.onerror = () => rej(r.error); r.readAsDataURL(f); });
  async function post(url, body) {
    const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const j = await r.json(); if (!j.ok) throw new Error(j.error || r.status); return j.id;
  }
  let file = null, data = null, parsed = null;

  function open() {
    file = data = parsed = null;
    ST.dialog("Nhập FBX", `<div class="row"><input type="file" id="fbxIn" accept=".fbx"></div>
      <p class="note">Đọc mesh, xương và skin từ FBX binary (không cần Blender), đổi về cm, trục Y lên.</p><div id="fbxOut"></div>`, b => {
      b.querySelector("#fbxIn").onchange = e => { const f = e.target.files[0]; if (f) read(f); };
      b.onclick = click;
    });
  }
  async function read(f) {
    const out = $("fbxOut"); file = f; out.innerHTML = `<div class="sub">Đang đọc ${esc(f.name)} (${(f.size / 1048576).toFixed(1)} MB)…</div>`;
    try { data = await b64(f); parsed = await post("/api/fbx/parse", { fbx_b64: data }); }
    catch (e) { out.innerHTML = `<div class="s-bad">Không đọc được: ${esc(e.message || e)}</div>`; return; }
    show();
  }
  function show() {
    const have = new Set(ST.char && ST.mods.mesh ? ST.mods.mesh.objects().map(o => o.name) : []), P = parsed;
    const anyMatch = P.meshes.some(m => have.has(m.name)), base = file.name.replace(/\.fbx$/i, "").replace(/_?rig$/i, "");
    $("fbxOut").innerHTML = `<h2 style="font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);margin:10px 0 4px">${P.meshes.length} mesh · ${P.bones} xương</h2>
      <div class="list" style="max-height:30vh">${P.meshes.map((m, i) => `<label class="it" style="cursor:pointer"><input type="checkbox" data-i="${i}" checked>
        <span>${esc(m.name)}${have.has(m.name) ? ' <span class="sub">· trùng tên</span>' : ""}</span>
        <small>${m.verts.length / 3} điểm · cao ${(m.max[1] - m.min[1]).toFixed(1)} cm${m.bones ? " · skin " + m.bones + " xương" : ""}</small></label>`).join("")}</div>
      <p class="note">Đơn vị: ×${P.unit_cm} → cm · trục lên ${esc(P.up)}${P.note ? " · " + esc(P.note) : ""}</p>
      ${ST.char ? `<div class="row"><button class="${anyMatch ? "on" : ""}" data-a="replace" ${anyMatch ? "" : "disabled"} title="Thay mesh trùng tên trong ${esc(ST.char.name)}, mesh mới thì thêm">${ic("reset")} Thay mesh trùng tên</button>
        <button class="${anyMatch ? "" : "on"}" data-a="add" title="Thêm mọi mesh đã chọn vào cảnh">${ic("plus")} Thêm vào cảnh</button></div>` : ""}
      <h2 style="font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);margin:12px 0 4px">Hoặc tạo nhân vật mới</h2>
      <div class="row"><input type="text" id="fbxName" value="${esc(base)}" style="flex:1" aria-label="Tên nhân vật"><button data-a="new">${ic("rig")} Tạo nhân vật</button></div>
      <div class="note" id="fbxMsg"></div>`;
  }
  const picked = () => [...document.querySelectorAll('#fbxOut input[type=checkbox][data-i]')].filter(c => c.checked).map(c => parsed.meshes[+c.dataset.i]);
  async function click(e) {
    const a = e.target.closest("button[data-a]"); if (!a || a.disabled || !parsed) return;
    const msg = $("fbxMsg");
    if (a.dataset.a === "new") {
      const name = $("fbxName").value.trim(); msg.textContent = "Đang tạo nhân vật…";
      try {
        const r = await post("/api/fbx/new-char", { fbx_b64: data, name, filename: file.name });
        msg.textContent = "Đã tạo " + r.id + " (" + r.meshes + " mesh, " + r.bones + " xương). Đang mở…";
        const u = new URL("/studio/" + encodeURIComponent(r.id), location.origin); u.searchParams.set("ws", "general"); location.href = u;
      } catch (err) { msg.textContent = "Không tạo được: " + (err.message || err); }
      return;
    }
    const list = picked(); if (!list.length) { msg.textContent = "Chọn ít nhất một mesh."; return; }
    ST.setFocus("mesh");
    const r = ST.mods.mesh.importMeshes(list, a.dataset.a);
    ST.closeDialog(); ST.toast("Nhập FBX: thay " + r.rep + " mesh, thêm " + r.add + " mesh (Ctrl+Z để bỏ)");
  }

  ST.cmd({ id: "file.fbx", menu: "File", label: "Nhập FBX…", icon: "import", key: "ctrl+shift+i", run: open });
  // đặt ngay sau "Mở nhân vật…" trong menu Tệp
  const all = [...ST.cmds.entries()], i = all.findIndex(([k]) => k === "file.open"), me = all.findIndex(([k]) => k === "file.fbx");
  if (i >= 0 && me > i + 1) { const [x] = all.splice(me, 1); all.splice(i + 1, 0, x); ST.cmds.clear(); all.forEach(([k, v]) => ST.cmds.set(k, v)); }
})();
