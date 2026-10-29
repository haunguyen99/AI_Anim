# Một lần: undo/redo (Ctrl+Z, Ctrl+Shift+Z / Ctrl+Y) cho vị trí khớp và số twist
p = "template.html"
s = open(p, encoding="utf8").read()


def rep(a, b, n=1):
    global s
    assert a in s, a[:60]
    s = s.replace(a, b) if n == 0 else s.replace(a, b, n)


rep("const S = new Set();", "const S = new Set();\nlet undoS = [], redoS = [], cur = null;")
rep("function pick(k, add) {", r'''// ---- undo / redo: ảnh chụp {LM, TW} sau mỗi thao tác hoàn tất (thả chuột, nhập số, đặt lại, đổi twist)
const snap = () => JSON.stringify({ LM, TW });
function resetHist() { undoS = []; redoS = []; cur = snap(); renderVbar(); }
function commit() {
  const n = snap(); if (n === cur) return;
  undoS.push(cur); if (undoS.length > 100) undoS.shift(); cur = n; redoS = []; syncHistBtns();
}
function applySnap(str) { const o = JSON.parse(str); LM = o.LM; TW = o.TW; cur = str; syncScene(); dirty(); renderPanel(); syncHistBtns(); }
function undo() { if (!undoS.length) return; redoS.push(cur); applySnap(undoS.pop()); }
function redo() { if (!redoS.length) return; undoS.push(cur); applySnap(redoS.pop()); }
function syncHistBtns() { const u = $("bUndo"), r = $("bRedo"); if (u) u.disabled = !undoS.length; if (r) r.disabled = !redoS.length; }
function pick(k, add) {''')
# commit sau thao tác
rep("else { start = null; resetPivot(); }", "else { start = null; resetPivot(); commit(); }")
rep("syncScene(); dirty(); renderPanel();", "syncScene(); dirty(); commit(); renderPanel();", 0)
rep("syncScene(); dirty(); } });", "syncScene(); dirty(); commit(); } });")
# sau khi đọc db: lịch sử bắt đầu từ trạng thái nạp
rep("  syncScene(); renderAll();\n}\nasync function saveLM", "  syncScene(); renderAll(); resetHist();\n}\nasync function saveLM")
# nút
rep('''$("vbar").innerHTML = [["front", "Trước"], ["side", "Cạnh"], ["top", "Trên"], ["persp", "3D"]].map(([v, t]) => `<button data-v="${v}">${t}</button>`).join("");''',
    '''$("vbar").innerHTML = [["front", "Trước"], ["side", "Cạnh"], ["top", "Trên"], ["persp", "3D"]].map(([v, t]) => `<button data-v="${v}">${t}</button>`).join("") +
    `<button id="bUndo" title="Ctrl+Z" ${undoS.length ? "" : "disabled"}>Hoàn tác</button><button id="bRedo" title="Ctrl+Shift+Z" ${redoS.length ? "" : "disabled"}>Làm lại</button>`;
  $("bUndo").addEventListener("click", undo); $("bRedo").addEventListener("click", redo);''')
# phím
rep('''window.addEventListener("keydown", e => {
  if (/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) || e.altKey || e.ctrlKey || e.metaKey) return;''',
    '''window.addEventListener("keydown", e => {
  if (/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) return;
  if ((e.ctrlKey || e.metaKey) && !e.altKey) {
    const z = e.key.toLowerCase();
    if (z === "z" && !e.shiftKey) { e.preventDefault(); undo(); } else if ((z === "z" && e.shiftKey) || z === "y") { e.preventDefault(); redo(); }
    return;
  }
  if (e.altKey) return;''')
rep("renderVbar(); resize(); setView(\"front\"); syncScene(); renderAll(); frame(); initDb();",
    "renderVbar(); resize(); setView(\"front\"); syncScene(); renderAll(); frame(); resetHist(); initDb();")
open(p, "w", encoding="utf8").write(s)
