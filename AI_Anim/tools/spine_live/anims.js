// Mục Anim (người dùng 2026-10-30): mọi sửa / key / gen thuộc anim đang xem (sửa ở run chỉ vào run, không đụng idle).
// Chọn anim, tạo anim mới (tên, dài N frame, loop) để pose trực tiếp, xoá anim (Hoàn tác được),
// mô tả anim cho Claude: lưu ở server (anims.json), gửi kèm mỗi yêu cầu Gen để Claude gen theo mô tả.
(() => {
  const M = { data: {}, json: null, anim: null, saveT: 0 };
  const meta = () => (cur && M.json === cur.json && M.data[curAnim()]) || {};
  // anim "chạy 1 lần" (sổ anim loop: false): player phát hết rồi dừng ở frame cuối (index.html onceGuard)
  window.animOnce = name => !!(cur && M.json === cur.json && M.data[name] && M.data[name].loop === false);

  async function load() {
    if (!cur) return;
    try { M.data = await (await fetch("/api/spine/anims?json=" + encodeURIComponent(cur.json), { cache: "no-store" })).json(); M.json = cur.json } catch {}
    M.anim = null; sync();
  }
  // đổi anim / nạp lại: điền mô tả + độ dài của anim đang xem
  function sync() {
    if (!player || !cur) return;
    const a = curAnim();
    const e = player.animationState.getCurrent(0), n = e ? Math.round(e.animation.duration * fpsOf()) : 0;
    $("animLen").textContent = a ? " · " + n + " frame" + (meta().loop === false ? " · chạy 1 lần" : "") : "";
    if (a !== M.anim) {
      M.anim = a;
      if (document.activeElement !== $("animDesc")) $("animDesc").value = meta().desc || "";
      $("animDescSt").textContent = "";
    }
  }
  setInterval(() => { try { sync() } catch {} }, 300);

  // nút Loop / 1 lần cạnh ▶ (2026-11-10, rà soát: cờ loop trước chỉ đặt được qua API hoặc lúc tạo anim mới)
  function loopBtn() {
    const b = $("tlLoop"); if (!b) return;
    const a = curAnim(), once = !!(a && window.animOnce?.(a));
    const lbl = once ? "→ 1 lần" : "⟳ Loop";
    if (b.textContent !== lbl) b.textContent = lbl;
    b.classList.toggle("on", once);
    b.disabled = !a;
    const src = (M.data[a] || {}).from;
    b.title = (once ? "Chạy 1 lần: phát hết thì dừng ở frame cuối (như trong game)" : "Loop: phát lặp") +
      (src ? " · cờ lấy theo " + src : "") + " · bấm để đổi";
  }
  setInterval(() => { try { loopBtn() } catch {} }, 300);
  $("tlLoop")?.addEventListener("click", async () => {
    const a = curAnim(); if (!cur || !a) return;
    const loop = !!window.animOnce?.(a);   // đang 1 lần -> chuyển sang loop và ngược lại
    try {
      await edPost("/api/spine/anim", { json: cur.json, op: "meta", name: a, loop });
      M.data[a] = Object.assign({}, M.data[a] || {}, { loop }); delete M.data[a].from;
      M.json = cur.json; loopBtn();
      setStatus("anim " + a + ": " + (loop ? "loop" : "chạy 1 lần"), "ok");
    } catch (e) { setStatus("không đổi được loop: " + e.message, "err") }
  });

  async function saveDesc() {
    if (!cur || !curAnim()) return;
    const desc = $("animDesc").value.trim();
    if ((meta().desc || "") === desc) return;
    try {
      await edPost("/api/spine/anim", { json: cur.json, op: "meta", name: curAnim(), desc });
      (M.data[curAnim()] ||= {}).desc = desc;
      $("animDescSt").textContent = "đã lưu " + hhmmss();
    } catch (e) { $("animDescSt").textContent = "lưu lỗi: " + e.message }
  }
  $("animDesc").addEventListener("input", () => { clearTimeout(M.saveT); $("animDescSt").textContent = "…"; M.saveT = setTimeout(saveDesc, 900) });
  $("animDesc").addEventListener("blur", () => { clearTimeout(M.saveT); saveDesc() });

  $("animNew").onclick = () => { $("animNewRow").hidden = !$("animNewRow").hidden; if (!$("animNewRow").hidden) $("animNewName").focus() };
  $("animNewOk").onclick = async () => {
    if (!cur) return;
    if (ed.dirty.size) return setStatus("đang sửa dở: Key pose hoặc Bỏ sửa trước khi tạo anim", "bad");
    const name = $("animNewName").value.trim(), frames = Math.max(1, parseInt($("animNewLen").value) || 30);
    if (!name) return setStatus("nhập tên anim mới", "bad");
    try {
      await edPost("/api/spine/anim", { json: cur.json, op: "create", name, frames, loop: $("animNewLoop").checked, desc: $("animNewDesc").value.trim() });
      $("animNewRow").hidden = true; $("animNewName").value = ""; $("animNewDesc").value = "";
      store.set("anim." + cur.json, name); stamp = null;
      build({ anim: name, time: 0, paused: true, speed: player?.speed || 1, viewport: true });
      load(); setStatus("đã tạo anim " + name + " (" + frames + " frame): pose rồi Key pose, hoặc ghi mô tả rồi bấm Gen", "ok");
    } catch (e) { setStatus("tạo anim lỗi: " + e.message, "bad") }
  };
  // xoá anim theo tên (nút Xoá của mục Anim, ✕ trong danh sách anim ở timeline). Hỏi lại 2 bước ở nơi bấm (armDelete).
  async function delAnim(a) {
    if (!cur || !player || !a) return;
    if (ed.dirty.size) return setStatus("đang sửa dở: Key pose hoặc Bỏ sửa trước khi xoá anim", "bad");
    const names = player.skeleton.data.animations.map(x => x.name);
    if (names.length < 2) return setStatus("không xoá anim cuối cùng của file", "bad");
    try {
      await edPost("/api/spine/anim", { json: cur.json, op: "delete", name: a });
      const keep = curAnim() !== a ? curAnim() : names.find(x => x !== a);
      store.set("anim." + cur.json, keep); stamp = null;
      await build({ anim: keep, time: curAnim() !== a ? (player.playTime || 0) : 0, paused: true, speed: player.speed, viewport: true });
      const msg = "đã xoá anim " + a + " (Hoàn tác để lấy lại)";
      setStatus(msg, "ok"); setTimeout(() => setStatus(msg, "ok"), 1500);   // sau dòng "đã nạp" của lần nạp lại
    } catch (e) { setStatus("xoá anim lỗi: " + e.message, "bad") }
  }
  $("animDel").onclick = () => armDelete($("animDel"), () => delAnim(curAnim()), "Xoá " + curAnim() + "?");
  // Skin (2026-10-30, rig Hộp quà: 1 bộ xương, 7 skin): chọn skin; skin default trống thì tự lấy skin đầu tiên; nhớ theo file
  function skinSync() {
    if (!player || !cur) return;
    const sk = player.skeleton, skins = sk.data.skins.filter(x => x.name !== "default" || x.attachments.some(a => a && Object.keys(a).length));
    $("skinRow").hidden = skins.length < 2 && !(skins.length === 1 && skins[0].name !== "default");
    const sel = $("skinPick"), sig = skins.map(x => x.name).join("|");
    if (sel.dataset.sig !== sig) { sel.innerHTML = skins.map(x => `<option value="${x.name}">${x.name}</option>`).join(""); sel.dataset.sig = sig }
    const curSkin = sk.skin?.name;
    if ((!curSkin || curSkin === "default") && skins.length && skins[0].name !== "default") {
      const want = store.get("skin." + cur.json, ""); setSkin(skins.some(x => x.name === want) ? want : skins[0].name); return;
    }
    if (document.activeElement !== sel && curSkin) sel.value = curSkin;
  }
  function setSkin(name) {
    const sk = player.skeleton; sk.setSkinByName(name); sk.setSlotsToSetupPose();
    const st = player.animationState, e = st.getCurrent(0);
    if (e) { sk.setBonesToSetupPose(); setTrack(e, player.playTime || 0); st.apply(sk) }
    sk.updateWorldTransform(2); store.set("skin." + cur.json, name); $("skinPick").value = name;
  }
  $("skinPick").onchange = () => { if (player) { setSkin($("skinPick").value); setStatus("skin: " + $("skinPick").value, "ok") } };
  setInterval(() => { try { skinSync() } catch {} }, 300);
  window.spineAnims = { load, sync, meta, delAnim, desc: () => $("animDesc").value.trim() };
})();
