"""Pose Lab → Review Lab: quay playblast ngay trong trang (nhiều camera ghép một hàng, bỏ gizmo/khớp), trả về webm + ảnh thumb.
window.DDC.playblast() cho vỏ ứng dụng (đăng ký version Review); nút Quay playblast tải file .webm khi mở riêng. Idempotent (/*PLAYBLAST*/)."""
import os, urllib.parse
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
s = open(P, encoding="utf8").read()
if "/*PLAYBLAST*/" in s:
    print("already patched"); raise SystemExit

svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="black" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">'
       '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3z"/></svg>')
uri = 'url("data:image/svg+xml,%s")' % urllib.parse.quote(svg, safe="/:='(),")
CSS = "\n/*PLAYBLAST*/\n#bPB{--ic:%s}\n#pbMsg{position:absolute;left:50%%;top:50%%;transform:translate(-50%%,-50%%);background:#000b;color:#fff;padding:10px 16px;border-radius:10px;z-index:20;font-size:13px}\n" % uri

JS = r"""
/*PLAYBLAST*/
// Quay playblast: mỗi frame goto(f) rồi vẽ N camera cạnh nhau (chỉ scene, không overlay) vào canvas ghép, MediaRecorder thu theo nhịp fps.
window.DDC = window.DDC || {};
window.DDC.playblast = async function (opt) {
  opt = opt || {};
  if (!ready || !model) throw new Error("Model chưa tải xong.");
  const cams = opt.cams || ["right", "left", "front", "top"], cw = opt.cw || 450, ch = opt.ch || 600, n = P.frames || 1, fps = P.fps || 30;
  const mime = ["video/webm;codecs=vp9", "video/webm;codecs=vp8", "video/webm"].find(m => window.MediaRecorder && MediaRecorder.isTypeSupported(m));
  if (!mime) throw new Error("Trình duyệt không quay được video (MediaRecorder).");
  const wasFrame = frame, wasCam = curCam, wasGhost = ghost && ghost.visible, wasSize = renderer.getSize(new THREE.Vector2()), prog = opt.onProgress || (() => {});
  const out = document.createElement("canvas"); out.width = cw * cams.length; out.height = ch;
  const ctx = out.getContext("2d"), stream = out.captureStream(0), track = stream.getVideoTracks()[0];
  const rec = new MediaRecorder(stream, { mimeType: mime, videoBitsPerSecond: 8e6 }), chunks = [];
  rec.ondataavailable = e => { if (e.data && e.data.size) chunks.push(e.data); };
  const done = new Promise(r => rec.onstop = r);
  const msg = document.createElement("div"); msg.id = "pbMsg"; $("viewer").appendChild(msg);
  stopPlay(); if (ghost) ghost.visible = false; gizmo.detach();
  const clear = css("--view") || "#101218", bg = new THREE.Color(0x15181f);
  let thumb = null; const mid = Math.max(1, Math.round(n / 2));
  try {
    rec.start();
    for (let f = 1; f <= n; f++) {
      msg.textContent = "Đang quay playblast " + f + " / " + n; prog(f, n);
      goto(f); model.updateMatrixWorld(true);
      renderer.setSize(cw, ch, false); camera.aspect = cw / ch; camera.updateProjectionMatrix();
      ctx.fillStyle = "#15181f"; ctx.fillRect(0, 0, out.width, ch);
      cams.forEach((k, i) => { setCam(k); renderer.setClearColor(bg, 1); renderer.clear(); renderer.render(scene, camera); ctx.drawImage(renderer.domElement, i * cw, 0, cw, ch); });
      if (f === mid) thumb = await new Promise(r => out.toBlob(r, "image/jpeg", 0.85));
      track.requestFrame();
      await new Promise(r => setTimeout(r, 1000 / fps));
    }
    await new Promise(r => setTimeout(r, 200)); rec.stop(); await done;
  } finally {
    msg.remove(); if (ghost) ghost.visible = wasGhost; renderer.setSize(wasSize.x, wasSize.y, false); resize(); setCam(wasCam); goto(wasFrame); renderer.setClearColor(0x000000, 0);
  }
  return { webm: new Blob(chunks, { type: "video/webm" }), thumb, n, fps, w: cw * cams.length, h: ch, views: cams.map(k => CAMS[k].label.toLowerCase()).join(" | ") };
};
$("bPB").addEventListener("click", async () => {
  try { const r = await window.DDC.playblast(); const u = URL.createObjectURL(r.webm), a = document.createElement("a"); a.href = u; a.download = idOf(P.clip, P.version) + ".webm"; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 4000); $("status").textContent = "Đã quay playblast " + r.n + " frame."; }
  catch (e) { $("status").textContent = "Không quay được: " + (e.message || e); }
});
"""

def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)

rep('      <button class="ibtn tool" id="undo"', '      <button class="ibtn tool" id="bPB" title="Quay playblast (nhiều camera) và tải .webm">Quay playblast</button>\n      <button class="ibtn tool" id="undo"')
j = s.index("</style>"); s = s[:j] + CSS + s[j:]
k = s.rfind("</script>"); s = s[:k] + JS + s[k:]
open(P, "w", encoding="utf8", newline="").write(s)
print("ok")
