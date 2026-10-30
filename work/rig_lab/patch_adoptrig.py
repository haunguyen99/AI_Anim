"""Rig Lab: dùng rig có sẵn của mesh (xương + skin khách) thay vì rig lại từ đầu.
- Bước 2: nút "Dùng xương khách" đặt khớp theo vị trí xương khách (DATA.ref) cùng tên.
- Bước 4: nút "Dùng skin khách" lấy trọng số khách (DATA.refW) làm skin, bỏ qua bước tính.
Chỉ hiện khi trang có dữ liệu khách (Gaygor: có; nhân vật build từ mesh trần: không). Idempotent (/*ADOPTRIG*/)."""
import os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")
s = open(P, encoding="utf8").read()
if "/*ADOPTRIG*/" in s:
    print("already patched"); raise SystemExit

def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:80], s.count(a))
    s = s.replace(a, b)

# bước 2
rep('<button id="resetAuto">Về gợi ý</button></div>', '<button id="resetAuto">Về gợi ý</button>${guestJ() ? \'<button id="useRefJ" title="Đặt mọi khớp theo xương có sẵn của mesh (vàng), khỏi đặt tay">Dùng xương khách</button>\' : ""}</div>')
rep('  on("resetAuto", () => {', '  on("useRefJ", () => adoptGuestJoints());\n  on("resetAuto", () => {')
# bước 4: hai chỗ có nút tính skin
rep('''<div class="row"><button class="pri" id="doSkin" ${skinBusy ? "disabled" : ""}>${skinBusy ? "Đang tính…" : "Tính skin"}</button></div>${gateHtml(4)}`;''',
    '''<div class="row"><button class="pri" id="doSkin" ${skinBusy ? "disabled" : ""}>${skinBusy ? "Đang tính…" : "Tính skin"}</button>${guestS() ? '<button id="useRefS" title="Lấy luôn skin có sẵn của mesh, không tính lại">Dùng skin khách</button>' : ""}</div>${gateHtml(4)}`;''')
rep('''${skinBusy ? "Đang tính…" : "Tính lại skin"}</button></div>` : ""}''', '''${skinBusy ? "Đang tính…" : "Tính lại skin"}</button>${guestS() ? '<button id="useRefS" title="Lấy luôn skin có sẵn của mesh, không tính lại">Dùng skin khách</button>' : ""}</div>` : ""}''')
# nút dùng skin cũng cần ở mục Thống kê và xuất (đã có Tính lại skin): thêm
rep('<button id="expGltf" title="glTF có skin để mở trong Pose Lab">Xuất glTF</button>', '<button id="expGltf" title="glTF có skin để mở trong Pose Lab">Xuất glTF</button>${guestS() ? \'<button id="useRefS2" title="Lấy luôn skin có sẵn của mesh">Dùng skin khách</button>\' : ""}')
rep('on("expW", exportWeights); on("expGltf", () => exportGltf());', 'on("expW", exportWeights); on("expGltf", () => exportGltf()); on("useRefS", () => adoptGuestSkin()); on("useRefS2", () => adoptGuestSkin());')

JS = r"""
/*ADOPTRIG*/
// Rig có sẵn (xương + skin khách) đi kèm mesh: dùng thẳng thay vì rig lại. DATA.ref = xương khách (tên, cha, vị trí), DATA.refW = trọng số khách theo xương.
function guestJ() { return (DATA.ref || []).filter(b => b.pos && LM_ORDER.includes(b.name)).length >= 10; }
function guestS() { return guestJ() && Object.keys(DATA.refW || {}).length > 5; }
function adoptGuestJoints() {
  const by = {}; (DATA.ref || []).forEach(b => { if (b.pos) by[b.name] = b.pos; });
  let n = 0; for (const k of LM_ORDER) if (by[k]) { LM[k] = by[k].slice(); n++; }
  initFingers(LM, false); syncScene(); dirty(); commit(); saveMsg = "Đã đặt " + n + " khớp theo xương khách."; renderPanel();
}
function adoptGuestSkin() {
  const B = buildSkeleton(LM), segs = boneSegments(B), names = segs.map(x => x.name), idx = Object.fromEntries(names.map((n, i) => [n, i])), nb = names.length;
  const I = new Uint16Array(NV * 4), W = new Float32Array(NV * 4); let bare = 0, kept = 0;
  const fall = idx.Root_M !== undefined ? idx.Root_M : 0;
  for (let i = 0; i < NV; i++) {
    const a = Object.entries(REFW[i] || {}).filter(([b, w]) => idx[b] !== undefined && w > 0).sort((p, q) => q[1] - p[1]).slice(0, 4), t = a.reduce((x, p) => x + p[1], 0);
    if (!a.length || t <= 0) { I[i * 4] = fall; W[i * 4] = 1; bare++; continue; }
    a.forEach(([b, w], k) => { I[i * 4 + k] = idx[b]; W[i * 4 + k] = w / t; }); kept++;
  }
  SK = { names, idx, I, W, full: null, nb, LMsnap: JSON.stringify({ LM, TW }) };
  SK.full = denseFrom(I, W, nb); skinUndo = []; skinRedo = []; skinStale = false; skinBusy = false; if (!skinBone) skinBone = names[0]; setTimeout(scheduleSkinSave, 0);
  try { SK_TEST = skinSelfTest(); } catch (e) { SK_TEST = { rows: [["warn", "Tự kiểm lỗi", String(e.message || e)]], leaks: [], t: Date.now() }; }
  saveMsg = "Đã dùng skin khách (" + kept + " đỉnh có trọng số" + (bare ? ", " + bare + " đỉnh không có nên gán Root_M" : "") + ").";
  paintSkin(); syncScene(); renderPanel();
}
"""
k = s.rfind("</script>")
s = s[:k] + JS + s[k:]
open(P, "w", encoding="utf8", newline="").write(s)
print("ok")
