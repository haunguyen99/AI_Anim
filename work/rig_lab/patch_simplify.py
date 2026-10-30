# Một lần: đơn giản hóa UI. Mỗi bước chỉ giữ thao tác chính, phần phụ gom vào mục "Chi tiết" (nhớ trạng thái mở),
# thanh hiển thị gom vào menu "Hiển thị", hướng dẫn phím gom vào nút "?", tự lưu thay cho nút Lưu.
p = "template.html"
s = open(p, encoding="utf8").read()


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


def swap(start, end, new):
    global s
    a, b = s.index(start), s.index(end)
    s = s[:a] + new + s[b:]


# ---------------------------------------------------------------- CSS
rep(".gate h2{margin:0 0 4px}", r'''.gate h2{margin:0 0 4px}
.big{font-size:15px;font-weight:600;margin:6px 0}.big.ok{color:var(--ok)}.big.warn{color:var(--warn)}
details.more{margin:10px 0;border-top:1px solid var(--line);padding-top:6px}
details.more>summary{cursor:pointer;color:var(--mute);font-size:12px;padding:2px 0}
details.more[open]>summary{margin-bottom:6px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0}
.chip{display:inline-block;padding:1px 8px;border-radius:10px;border:1px solid var(--line);font-size:11px;color:var(--mute)}
.chip.ok{color:var(--ok);border-color:var(--ok)}.chip.fix{color:var(--bad);border-color:var(--bad)}
.ghead{display:flex;align-items:center;gap:8px;margin-bottom:6px}.ghead .msg{margin-left:auto;min-height:0}
.dd{position:relative}.dd>summary{cursor:pointer;list-style:none;font-size:12px}.dd>summary::-webkit-details-marker{display:none}
.ddbox{position:absolute;left:0;bottom:calc(100% + 10px);background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 10px;display:flex;flex-direction:column;gap:6px;min-width:160px;z-index:5}
.helpbtn{position:absolute;right:8px;top:8px;width:28px;height:28px;border-radius:50%;padding:0;z-index:4}
.vhelp[hidden]{display:none}''')
rep(".vhelp{position:absolute;right:8px;top:8px;", ".vhelp{position:absolute;right:8px;top:44px;z-index:4;")
rep("padding:3px 8px;border-radius:6px;max-width:45%}", "padding:6px 10px;border-radius:6px;max-width:min(360px,70%);line-height:1.6}")
rep(".jbox{position:absolute;right:8px;top:62px;", ".jbox{position:absolute;right:8px;top:48px;")
rep("textarea{width:100%;min-height:54px;", "textarea{width:100%;min-height:44px;")

# ---------------------------------------------------------------- header, trợ giúp, bước
rep('<div><h1>Gaygor Rig Lab</h1><div class="sub">Mesh trần → khớp → skeleton. Mốc M1, thử trên Gaygor, đối chiếu với rig khách.</div></div>', '<div><h1>Gaygor Rig Lab</h1></div>')
a = s.index('<div class="vhelp">')
b = s.index("</div>", a) + 6
s = s[:a] + '<button class="helpbtn" id="helpBtn" aria-label="Hướng dẫn thao tác" title="Hướng dẫn thao tác">?</button>\n    <div class="vhelp" id="vhelp" hidden>Alt + chuột trái: xoay<br>Alt + chuột giữa: kéo<br>Alt + chuột phải hoặc lăn: zoom<br>Click hoặc kéo khung: chọn (Shift đảo, Ctrl bỏ, Ctrl+Shift thêm)<br>Q chọn · W dời · E xoay · R co giãn<br>F nhìn vùng chọn · A nhìn toàn bộ · Ctrl+Z hoàn tác</div>' + s[b:]
rep('const names = ["1 · Mesh", "2 · Khớp", "3 · Skeleton", "4 · Skin", "5 · Thử khớp"];', 'const names = ["1 Mesh", "2 Khớp", "3 Xương", "4 Skin", "5 Thử khớp"];')
rep('$("bUndo").addEventListener("click", undo);', '$("helpBtn").onclick = () => { $("vhelp").hidden = !$("vhelp").hidden; };\n  $("bUndo").addEventListener("click", undo);')

# ---------------------------------------------------------------- menu Hiển thị
swap("function renderVopts() {", "function showSkinFor() {", r'''function renderVopts() {
  const lab = (id, txt, on, cls) => `<label class="t"><input type="checkbox" id="${id}" ${cls ? `class="${cls}"` : ""} ${on ? "checked" : ""}> ${txt}</label>`;
  const open = $("vopts").querySelector("details") && $("vopts").querySelector("details").open;
  $("vopts").innerHTML = `<details class="dd" ${open ? "open" : ""}><summary>Hiển thị ▾</summary><div class="ddbox">` +
    lab("ovb", "Thân", vis.body) +
    DATA.props.map((x, i) => `<label class="t"><input type="checkbox" class="ovp" data-i="${i}" ${vis.props[i] ? "checked" : ""}> ${x.name.replace("EN_M11_Boss_Gaygor_", "Prop ")}</label>`).join("") +
    lab("owire", "Lưới mesh", showWire) +
    (step === 2 ? lab("oskel", "Xương", showSkel) + lab("ofing", "Khớp ngón", showFing) : "") +
    (step >= 2 ? lab("oref", "Xương khách (đối chiếu)", showRef) : "") + `</div></details>`;
  $("ovb").onchange = e => { vis.body = e.target.checked; syncScene(); };
  document.querySelectorAll(".ovp").forEach(c => c.onchange = () => { vis.props[+c.dataset.i] = c.checked; syncScene(); });
  const w = $("owire"); w.onchange = () => { showWire = w.checked; syncScene(); };
  const s = $("oskel"); if (s) s.onchange = () => { showSkel = s.checked; syncScene(); };
  const f = $("ofing"); if (f) f.onchange = () => { showFing = f.checked; if (!showFing) { [...S].filter(isFinger).forEach(k => S.delete(k)); sel = [...S].pop() || null; } syncScene(); renderPanel(); };
  const r = $("oref"); if (r) r.onchange = () => { showRef = r.checked; syncScene(); if (step === 3) renderPanel(); };
}
''')
rep("if (step < 4) skinWire.visible = false;", "skinWire.visible = step >= 4 && showWire;")

# ---------------------------------------------------------------- tự lưu
rep('function dirty() { dirtyFlag.v = true; saveMsg = "Có thay đổi chưa lưu."; renderPanelLight(); }',
    'let lmTimer = null;\nfunction dirty() { dirtyFlag.v = true; saveMsg = "Đang lưu…"; renderPanelLight(); clearTimeout(lmTimer); lmTimer = setTimeout(saveLM, 1200); }')
rep('dirtyFlag.v = false; saveMsg = "Đã lưu vị trí khớp" + (db ? "." : " (chỉ trong trình duyệt này).");', 'dirtyFlag.v = false; saveMsg = db ? "Đã lưu" : "Đã lưu (chỉ trình duyệt này)";')
rep("async function saveSkin() {", "let skTimer = null;\nfunction scheduleSkinSave() { saveMsg = \"Đang lưu…\"; renderPanelLight(); clearTimeout(skTimer); skTimer = setTimeout(saveSkin, 2500); }\nasync function saveSkin() {")
rep('dirtySkin = false; saveMsg = "Đã lưu skin" + (db ? "." : " (chỉ trong trình duyệt này).");', 'dirtySkin = false; saveMsg = db ? "Đã lưu" : "Đã lưu (chỉ trình duyệt này)";')
rep('saveMsg = "Skin có thay đổi chưa lưu."; renderPanelLight(); }', 'scheduleSkinSave(); }')
rep('+ " đỉnh cho " + skinBone + " 100%. Nhớ bấm Lưu skin."; renderPanelLight();', '+ " đỉnh cho " + skinBone + " 100%."; scheduleSkinSave();')
rep("restoreSkin(m); renderPanelLight(); }", "restoreSkin(m); scheduleSkinSave(); }")
rep("skinUndo.push(skinSnapshotOf(m)); restoreSkin(m); }", "skinUndo.push(skinSnapshotOf(m)); restoreSkin(m); scheduleSkinSave(); }")
rep("skinMs = performance.now() - t0; if (!skinBone) skinBone = names[0];", "skinMs = performance.now() - t0; if (!skinBone) skinBone = names[0]; setTimeout(scheduleSkinSave, 0);")

# ---------------------------------------------------------------- panel: cổng duyệt + bước 1-3
swap("function gateHtml(n) {", "function dockGate(p)", r'''const esc = t => String(t).replace(/</g, "&lt;");
const OPEN = {};
const more = (id, title, html) => `<details class="more" data-more="${id}" ${OPEN[id] ? "open" : ""}><summary>${title}</summary>${html}</details>`;
function gateHtml(n) {
  const g = gates[n];
  const st = g ? (g.status === "ok" ? '<span class="chip ok">Đã duyệt</span>' : '<span class="chip fix">Cần sửa</span>') : '<span class="chip">Chưa duyệt</span>';
  return `<div class="gate"><div class="ghead"><b>Bước ${n}</b>${st}<span class="msg" id="smsg">${saveMsg}</span></div>
    <textarea id="note" rows="2" placeholder="Ghi chú cho AI nếu cần sửa">${g ? esc(g.note) : ""}</textarea>
    <div class="row"><button class="pri" id="gOk">Duyệt</button><button class="bad" id="gFix">Cần sửa</button></div></div>`;
}
function renderPanel() {
  const p = $("panel");
  if (step === 1) {
    const [dx, dy, dz] = dims(), front = LM.ToesEnd_R[2] > LM.Ankle_R[2], tris = DATA.body.tris.length / 3 | 0;
    const items = [
      [Math.abs(bb.mn[1]) < 1.5 ? "ok" : "warn", "Chân đứng trên sàn", "y nhỏ nhất " + fix(bb.mn[1]) + " cm"],
      [Math.abs((bb.mn[0] + bb.mx[0]) / 2) < 2 ? "ok" : "warn", "Thân đối xứng quanh x = 0", "tâm bbox x = " + fix((bb.mn[0] + bb.mx[0]) / 2) + " cm"],
      ["ok", "Hướng: đầu +Y", "đỉnh đầu y = " + fix(bb.mx[1]) + " cm"],
      [front ? "ok" : "warn", "Mặt nhìn +Z", "mũi chân ở trước cổ chân theo trục z"],
      [SYM.med < 1.5 ? "ok" : "warn", "Mesh đối xứng gương", "lệch trung vị " + fix(SYM.med) + " cm"],
      [DATA.props.length ? "warn" : "ok", "Phần rời (island)", DATA.props.length ? "1 prop rời: gắn vào xương Weapon" : "không có"],
      [dx > dy * 1.5 ? "warn" : "ok", "Tư thế bind", dx > dy ? "tay dang ngang (T-pose)" : ""]];
    const warns = items.filter(x => x[0] !== "ok").length;
    p.innerHTML = `<h2>Kiểm tra mesh</h2>
      <div class="big ${warns ? "warn" : "ok"}">${warns ? "! " + warns + " mục cần chú ý" : "✓ Mesh ổn"}</div>
      <div class="sub">${fix(dy, 0)} cm cao · ${bodyV.length} đỉnh${DATA.props.length ? " · " + DATA.props.length + " prop rời" : ""}</div>
      ${more("m1", "Chi tiết kiểm tra", items.map(x => chk(x[0], x[1], x[2])).join("") + `<div class="kv"><span>Rộng (sải tay)</span><span>${fix(dx)} cm</span><span>Sâu</span><span>${fix(dz)} cm</span><span>Tam giác</span><span>${tris}</span></div>`)}
      <div class="row"><button class="pri" id="toStep2">Tiếp: đặt khớp</button></div>${gateHtml(1)}`;
  } else if (step === 2) {
    const rows = LM_ORDER.filter(k => showFing || !isFinger(k)).map(k => `<tr class="pick ${S.has(k) ? "sel" : ""}" data-k="${k}"><td><span class="ltxt" style="background:${lmColor(k)}"></span>${k}</td><td>${fix(LM[k][0])}</td><td>${fix(LM[k][1])}</td><td>${fix(LM[k][2])}</td></tr>`).join("");
    p.innerHTML = `<h2>Đặt khớp</h2>
      <div class="row"><label class="t"><input type="checkbox" id="mir" ${mirror ? "checked" : ""}> Đối xứng R→L</label><button id="resetAuto">Về gợi ý</button></div>
      <div id="selbox"></div>
      ${more("m2", "Bảng toạ độ (" + LM_ORDER.filter(k => showFing || !isFinger(k)).length + " khớp)", `<table><thead><tr><th>Khớp</th><th>x</th><th>y</th><th>z</th></tr></thead><tbody id="lmrows">${rows}</tbody></table>`)}
      ${gateHtml(2)}`;
    renderSel();
  } else if (step === 3) {
    const checks = skelChecks(), errs = refErrors().sort((a, b) => b[1] - a[1]), mean = errs.reduce((s, e) => s + e[1], 0) / errs.length;
    const bad = checks.filter(c => c[0] !== "ok");
    p.innerHTML = `<h2>Bộ xương</h2>
      <div class="big ${bad.length ? "warn" : "ok"}">${bad.length ? "! " + bad.length + " mục cần chú ý" : "✓ " + checks.length + " kiểm tra đạt"} · ${buildSkeleton(LM).length} xương</div>
      ${bad.map(c => chk(c[0], c[1], c[2])).join("")}
      <h2>Twist joint</h2>
      <div class="kv" style="align-items:center">${Object.keys(TW_SEG).map(st => `<span><label for="tw_${st}">${TW_SEG[st][1]}</label></span><span><select id="tw_${st}">${[0, 1, 2, 3].map(n => `<option value="${n}" ${TW[st] === n ? "selected" : ""}>${n}</option>`).join("")}</select></span>`).join("")}</div>
      <div class="row"><button data-tw="0">Không twist</button><button data-tw="1">1 mỗi đoạn</button><button data-tw="2">2 mỗi đoạn</button></div>
      ${more("m3a", "Tất cả kiểm tra", checks.map(c => chk(c[0], c[1], c[2])).join(""))}
      ${more("m3b", "Đối chiếu rig khách", `<div class="kv"><span>Sai lệch trung bình</span><span>${fix(mean)} cm</span><span>Lớn nhất</span><span>${errs[0][0]} ${fix(errs[0][1])} cm</span></div>
        <div class="row"><label class="t"><input type="checkbox" id="ref" ${showRef ? "checked" : ""}> Vẽ xương khách (vàng)</label></div>
        <table><thead><tr><th>Xương</th><th>lệch cm</th></tr></thead><tbody>${errs.slice(0, 10).map(e => `<tr><td>${e[0]}</td><td class="${e[1] > 8 ? "err-hi" : e[1] > 4 ? "err-mid" : ""}">${fix(e[1])}</td></tr>`).join("")}</tbody></table>`)}
      ${more("m3c", "Xuất", `<div class="row"><button id="exportRig">Xuất rig.json</button></div>`)}
      ${gateHtml(3)}`;
  } else if (step === 4) { renderSkinPanel(p); } else { renderPosePanel(p); }
  dockGate(p); wirePanel(); renderJointBox();
}
''')
rep("function wirePanel() {\n  const on", "function wirePanel() {\n  document.querySelectorAll(\"[data-more]\").forEach(d => d.addEventListener(\"toggle\", () => OPEN[d.dataset.more] = d.open));\n  const on")

# ---------------------------------------------------------------- bước 2: chọn nhanh gọn
swap("function renderSel() {", "function renderPanelLight()", r'''function renderSel() {
  const b = $("selbox"); if (!b) return;
  const modes = [["select", "Chọn (Q)"], ["translate", "Dời (W)"], ["rotate", "Xoay (E)"], ["scale", "Co giãn (R)"]].map(([m, t]) => `<button data-mode="${m}" ${mode === m ? 'class="pri"' : ""}>${t}</button>`).join("");
  const grp = `<select id="grpSel" aria-label="Chọn nhanh"><option value="">Chọn nhanh…</option>${[["armR", "Tay R"], ["armL", "Tay L"], ["fingR", "Ngón R"], ["fingL", "Ngón L"], ["legR", "Chân R"], ["legL", "Chân L"], ["spine", "Thân"], ["all", "Tất cả"]].map(([g, t]) => `<option value="${g}">${t}</option>`).join("")}</select>`;
  let body;
  if (!S.size) body = '<div class="sub">Click một chấm hoặc kéo khung để chọn.</div>';
  else if (S.size > 1) body = `<div class="msg">Đã chọn ${S.size} khớp.</div>`;
  else body = `<div class="sub"><b>${sel}</b>${LM_LABEL[sel.replace(/_[RL]$/, "")] ? " · " + LM_LABEL[sel.replace(/_[RL]$/, "")] : ""}</div><div class="num">${["x", "y", "z"].map((a, i) => `<div><label for="n${a}">${a} (cm)</label><input id="n${a}" type="number" step="0.5" value="${fix(LM[sel][i], 2)}"></div>`).join("")}</div>`;
  b.innerHTML = `<div class="row">${modes}</div><div class="row">${grp}<button id="clr">Bỏ chọn</button></div>` + body;
  $("clr").addEventListener("click", () => pick(null));
  $("grpSel").onchange = e => { if (e.target.value) setSel(GROUPS[e.target.value](), false); e.target.value = ""; };
  b.querySelectorAll("[data-mode]").forEach(x => x.addEventListener("click", () => setMode(x.dataset.mode)));
  if (S.size === 1) ["x", "y", "z"].forEach((a, i) => $("n" + a).addEventListener("change", e => {
    LM[sel][i] = +e.target.value; if (mirror && mirrorKey(sel)) { const k = mirrorKey(sel); LM[k] = [-LM[sel][0], LM[sel][1], LM[sel][2]]; }
    syncScene(); dirty(); commit(); renderPanel();
  }));
}
''')

# ---------------------------------------------------------------- bước 4
swap("function poseSection() {", "function setSkTool(t)", r'''function poseSection() {
  const pres = ["Giơ tay lên", "Hạ tay", "Gập khuỷu", "Xoay cẳng tay", "Gập hông", "Ngồi xổm"].map(n => `<button data-spre="${n}">${n}</button>`).join("");
  return more("m4pose", "Xoay thử để lộ phần khuất", `<div class="chips">${pres}<button id="spReset">Về pose gốc</button></div>
    <div class="sub">Click một joint trên viewport rồi kéo thanh xoay ở góc phải.</div>
    <div class="row"><select id="spBone" aria-label="Chọn xương xoay">${buildSkeleton(LM).filter(b => !b.twist && b.name !== "root").map(b => `<option ${b.name === poseBone ? "selected" : ""}>${b.name}</option>`).join("")}</select><button id="spClr">Về 0</button>
    <label class="t"><input type="checkbox" id="spTw" ${poseOpt.twist ? "checked" : ""}> Dẫn động twist</label></div>`);
}
function wirePoseSection() {
  const on = (id, f) => { const e = $(id); if (e) e.addEventListener("click", f); };
  document.querySelectorAll("[data-spre]").forEach(b => b.addEventListener("click", () => { setPose(PRESETS[b.dataset.spre]); renderPanel(); }));
  on("spReset", () => { setPose({}); renderPanel(); });
  const bs = $("spBone"); if (!bs) return;
  bs.onchange = e => { poseBone = e.target.value; jointSel = poseBone; renderPanel(); };
  on("spClr", () => { delete POSE[poseBone]; applyPose(); renderPanel(); });
  $("spTw").onchange = e => { poseOpt.twist = e.target.checked; applyPose(); renderPanel(); };
}
''')
swap("function renderSkinPanel(p) {", "async function exportWeights()", r'''function renderSkinPanel(p) {
  if (!SK) {
    p.innerHTML = `<h2>Skin</h2><div class="sub">Tính trọng số tự động từ bộ xương, sau đó tô chỉnh.</div>
      <div class="row"><button class="pri" id="doSkin" ${skinBusy ? "disabled" : ""}>${skinBusy ? "Đang tính…" : "Tính skin"}</button></div>${gateHtml(4)}`;
    const b = $("doSkin"); if (b) b.onclick = computeSkin; return;
  }
  const st = more.open ? null : null, stale = SK.LMsnap !== JSON.stringify({ LM, TW });
  const tools = [["pick", "Chọn joint (Q)"], ["brush", "Cọ tô (B)"], ["island", "Gán khối rời (I)"]].map(([t, n]) => `<button data-skt="${t}" ${skTool === t ? 'class="pri"' : ""}>${n}</button>`).join("");
  p.innerHTML = `<h2>Skin</h2>
    ${stale ? `<div class="big warn">! Khớp hoặc twist đã đổi</div><div class="row"><button class="pri" id="doSkin" ${skinBusy ? "disabled" : ""}>${skinBusy ? "Đang tính…" : "Tính lại skin"}</button></div>` : ""}
    <div class="row">${tools}</div>
    ${skTool === "island" ? '<div class="sub">Chọn joint, rồi click một khối rời của mesh để gán cả khối 100% cho joint đó.</div>' : ""}
    ${skTool === "brush" ? `<div class="row"><select id="brMode" aria-label="Kiểu cọ"><option value="add" ${brush.mode === "add" ? "selected" : ""}>Cộng trọng số</option><option value="sub" ${brush.mode === "sub" ? "selected" : ""}>Trừ trọng số</option><option value="smooth" ${brush.mode === "smooth" ? "selected" : ""}>Làm mượt</option></select>
      <label class="t"><input type="checkbox" id="brMir" ${brush.mirror ? "checked" : ""}> Đối xứng</label></div>
      <div class="row" style="flex-wrap:nowrap"><label for="brR" style="width:70px;font-size:12px">Bán kính</label><input id="brR" type="range" min="2" max="40" step="1" value="${brush.r}" style="flex:1"><span id="brRv" class="sub" style="width:44px;text-align:right">${brush.r} cm</span></div>
      <div class="row" style="flex-wrap:nowrap"><label for="brS" style="width:70px;font-size:12px">Cường độ</label><input id="brS" type="range" min="0.05" max="1" step="0.05" value="${brush.str}" style="flex:1"><span id="brSv" class="sub" style="width:44px;text-align:right">${brush.str}</span></div>` : ""}
    <h2>Xem trọng số</h2>
    <div class="row"><select id="skView" aria-label="Kiểu xem"><option value="dom">Xương chính</option><option value="one">Xương đang chọn</option><option value="ref">Skin khách</option><option value="diff">Khác skin khách</option></select></div>
    <div class="row"><button id="skPrev" aria-label="Xương trước">◀</button><select id="skBone" aria-label="Xương đang chọn">${boneList().map(n => `<option ${n === skinBone ? "selected" : ""}>${n}</option>`).join("")}</select><button id="skNext" aria-label="Xương sau">▶</button></div>
    <div class="sub">Click một joint trên viewport để chọn nó.</div>
    ${poseSection()}
    ${more("m4stats", "Thống kê và xuất", (() => { const q = skinStats(); return `<div class="kv"><span>Xương có skin</span><span>${SK.names.length}</span><span>Xương / đỉnh</span><span>${fix(q.infl, 2)}</span><span>Trùng skin khách</span><span>${fix(q.same * 100)}%</span><span>Lệch TB</span><span>${fix(q.l1 * 100)}%</span></div>
      <table><thead><tr><th>Lệch nhiều nhất</th><th>lệch</th><th>đỉnh</th></tr></thead><tbody>${q.worst.map(w => `<tr><td>${w[0]}</td><td>${fix(w[1] * 100)}%</td><td>${w[2]}</td></tr>`).join("")}</tbody></table>
      <div class="row"><button id="doSkin2">Tính lại skin</button><button id="expW">Xuất weights.json</button></div>`; })())}
    ${gateHtml(4)}`;
  const on = (id, f) => { const e = $(id); if (e) e.addEventListener("click", f); };
  on("doSkin", computeSkin); on("doSkin2", computeSkin); on("expW", exportWeights);
  const v = $("skView"); if (v) { v.value = skinView; v.onchange = () => { skinView = v.value; paintSkin(); }; }
  const b = $("skBone"); if (b) b.onchange = () => { skinBone = b.value; paintSkin(); };
  const step1 = d => { const L = boneList(), i = (L.indexOf(skinBone) + d + L.length) % L.length; skinBone = L[i]; if (skinView === "dom") skinView = "one"; renderPanel(); paintSkin(); };
  on("skPrev", () => step1(-1)); on("skNext", () => step1(1));
  document.querySelectorAll("[data-skt]").forEach(x => x.addEventListener("click", () => setSkTool(x.dataset.skt)));
  const bm = $("brMode"); if (bm) bm.onchange = () => brush.mode = bm.value;
  const bx = $("brMir"); if (bx) bx.onchange = () => brush.mirror = bx.checked;
  const br = $("brR"); if (br) br.oninput = () => { brush.r = +br.value; $("brRv").textContent = brush.r + " cm"; };
  const bs = $("brS"); if (bs) bs.oninput = () => { brush.str = +bs.value; $("brSv").textContent = brush.str; };
  wirePoseSection();
}
''')

# ---------------------------------------------------------------- bước 5
swap("function renderPosePanel(p) {", "\n\n// ================================================================ M3 sớm", r'''function renderPosePanel(p) {
  if (!SK) { p.innerHTML = '<h2>Thử khớp</h2><div class="sub">Cần tính skin trước.</div><div class="row"><button class="pri" id="doSkin2">Tính skin</button></div>' + gateHtml(5); const b = $("doSkin2"); if (b) b.onclick = async () => { await computeSkin(); }; return; }
  const sm = strainSummary();
  const pr = Object.keys(PRESETS).map(n => `<button data-pre="${n}">${n}</button>`).join("");
  const bl = (battery || []).map(r => `<tr><td>${r[0]}</td><td class="${r[1] > 5 ? "err-hi" : r[1] > 1.5 ? "err-mid" : ""}">${fix(r[1])}%</td><td>${r[2]}</td></tr>`).join("");
  const pct = sm ? sm.pct : 0;
  p.innerHTML = `<h2>Pose thử</h2><div class="chips">${pr}<button id="poseReset">Về pose gốc</button></div>
    <div class="sub">Click một joint trên viewport rồi kéo thanh xoay ở góc phải.</div>
    <div class="row"><label class="t"><input type="checkbox" id="pTw" ${poseOpt.twist ? "checked" : ""}> Dẫn động twist</label><label class="t"><input type="checkbox" id="pStr" ${strainOn ? "checked" : ""}> Tô biến dạng</label></div>
    <div class="big ${pct > 5 ? "warn" : "ok"}">Co/căng quá 25%: ${fix(pct)}%</div>
    ${sm && sm.worst.length && pct > 1 ? `<div class="sub">Vùng xấu: ${sm.worst.map(w => w[0]).join(", ")}</div>` : ""}
    ${more("m5bat", "Bộ pose căng", `<div class="row"><button id="pBat">Chạy bộ pose căng</button></div>${bl ? `<table><thead><tr><th>Pose</th><th>quá 25%</th><th>vùng xấu</th></tr></thead><tbody>${bl}</tbody></table>` : ""}`)}
    ${more("m5bone", "Chọn xương từ danh sách", `<div class="row"><select id="pBone" aria-label="Chọn xương xoay">${buildSkeleton(LM).filter(b => !b.twist && b.name !== "root").map(b => `<option ${b.name === poseBone ? "selected" : ""}>${b.name}</option>`).join("")}</select><button id="pClr">Về 0</button></div>`)}
    ${gateHtml(5)}`;
  const on = (id, f) => { const e = $(id); if (e) e.addEventListener("click", f); };
  document.querySelectorAll("[data-pre]").forEach(b => b.addEventListener("click", () => { setPose(PRESETS[b.dataset.pre]); renderPanel(); }));
  on("poseReset", () => { setPose({}); renderPanel(); });
  $("pBone").onchange = e => { poseBone = e.target.value; jointSel = poseBone; renderPanel(); };
  on("pClr", () => { delete POSE[poseBone]; applyPose(); renderPanel(); });
  $("pTw").onchange = e => { poseOpt.twist = e.target.checked; applyPose(); renderPanel(); };
  $("pStr").onchange = e => { strainOn = e.target.checked; paintSkin(); };
  on("pBat", () => { battery = batteryRun(); OPEN.m5bat = true; renderPanel(); });
}''')
open(p, "w", encoding="utf8").write(s)
