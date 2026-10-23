# Một lần: công cụ "Gán island": click một khối rời của mesh (khiên, giáp) để gán 100% cho joint đang chọn
p = "template.html"
s = open(p, encoding="utf8").read()


def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)


rep("function denseFrom(I, W, nb) {", r'''// ---- island = khối liên thông của mesh
const COMP = (() => {
  const par = Array.from({ length: NV }, (_, i) => i), f = a => { while (par[a] !== a) { par[a] = par[par[a]]; a = par[a]; } return a; };
  for (let t = 0; t < NT; t++) { const a = f(TRI[3 * t]), b = f(TRI[3 * t + 1]), c = f(TRI[3 * t + 2]); par[b] = a; par[c] = a; }
  const id = new Int32Array(NV), roots = new Map(), size = [];
  for (let i = 0; i < NV; i++) { const r = f(i); if (!roots.has(r)) { roots.set(r, size.length); size.push(0); } id[i] = roots.get(r); size[id[i]]++; }
  return { id, size };
})();
function assignIsland(e) {
  if (!SK || !skinBone || SK.idx[skinBone] === undefined) { saveMsg = "Chọn một joint có skin trước (click joint ở chế độ Chọn joint)."; renderPanelLight(); return; }
  const r = cv.getBoundingClientRect();
  ray.setFromCamera({ x: ((e.clientX - r.left) / r.width) * 2 - 1, y: -((e.clientY - r.top) / r.height) * 2 + 1 }, cam);
  const h = ray.intersectObject(skinMesh, false)[0]; if (!h) return;
  const c = COMP.id[TRI[h.faceIndex * 3]], j = SK.idx[skinBone], m = new Map(), v = new Float64Array(SK.nb); v[j] = 1;
  for (let i = 0; i < NV; i++) if (COMP.id[i] === c) { m.set(i, [Array.from(SK.I.slice(i * 4, i * 4 + 4)), Array.from(SK.W.slice(i * 4, i * 4 + 4))]); setVec(i, Float64Array.from(v)); }
  skinUndo.push(m); skinRedo = []; dirtySkin = true; paintSkin();
  saveMsg = "Đã gán khối rời " + m.size + " đỉnh cho " + skinBone + " 100%. Nhớ bấm Lưu skin."; renderPanelLight();
}
function denseFrom(I, W, nb) {''')
rep("<button data-skt=\"brush\" ${skTool === \"brush\" ? 'class=\"pri\"' : \"\"}>Cọ tô (B)</button></div>",
    "<button data-skt=\"brush\" ${skTool === \"brush\" ? 'class=\"pri\"' : \"\"}>Cọ tô (B)</button><button data-skt=\"island\" ${skTool === \"island\" ? 'class=\"pri\"' : \"\"}>Gán khối rời (I)</button></div>\n      ${skTool === \"island\" ? '<div class=\"sub\">Chọn joint (kể cả joint twist) bằng Chọn joint, rồi vào chế độ này và click một khối rời của mesh (khiên, giáp): cả khối gán 100% cho joint đó. Không đối xứng; click bên kia nếu cần.</div>' : \"\"}")
rep("if (step === 4 && skTool === \"brush\" && SK) { painting = true;", "if (step === 4 && skTool === \"island\" && SK) { assignIsland(e); }\n  else if (step === 4 && skTool === \"brush\" && SK) { painting = true;")
rep('if (k === "b") setSkTool("brush"); }', 'if (k === "b") setSkTool("brush"); if (k === "i") setSkTool("island"); }')
rep("function setSkTool(t) { skTool = t;", "function setSkTool(t) { skTool = t; if (t === 'island' && skinView === 'dom') skinView = 'one';")
open(p, "w", encoding="utf8").write(s)
