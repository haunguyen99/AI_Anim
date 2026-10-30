"""Vá lõi Pose: bỏ nút "Xem trên model" ở điều chỉnh key; bấm vào cả mục là nhảy tới frame + áp điều chỉnh + góc camera.
User 2026-10-29: "nút này cũng nên bỏ đi, đổi thành người dùng click vào fb là tự nhảy đến frame đó".
Áp CÙNG bản vá vào work/pose_lab/index.html và tools/studio/modules/pose_engine.js (không chạy port_pose.py). Chạy lại an toàn."""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FILES = [os.path.join(ROOT, "work", "pose_lab", "index.html"), os.path.join(ROOT, "tools", "studio", "modules", "pose_engine.js")]
OLD = '''    const view = document.createElement("button"); view.className = "btn"; view.textContent = "Xem trên model";
    view.onclick = () => { applyLocal(a); if (a.cam && a.cam.pos) { CAM().position.fromArray(a.cam.pos); orbit.target.fromArray(a.cam.target); orbit.update(); } };
    row.append(view);'''
NEW = '''    // bấm vào mục (không phải nút / ô sửa / ảnh) = nhảy tới frame, áp điều chỉnh, về góc camera lúc ghi (thay nút "Xem trên model")
    el.style.cursor = "pointer"; el.title = "Bấm để tới F" + (a.frame || 1) + " và xem điều chỉnh trên model";
    el.onclick = e => { if (e.target.closest("button,textarea,img,a")) return;
      applyLocal(a); if (a.cam && a.cam.pos) { CAM().position.fromArray(a.cam.pos); orbit.target.fromArray(a.cam.target); orbit.update(); } };'''
for p in FILES:
    cam = "CAM()" if p.endswith(".js") else "camera"   # Studio gọi camera qua CAM()
    raw = open(p, "rb").read().decode("utf8"); crlf = "\r\n" in raw; s = raw.replace("\r\n", "\n")
    if "thay nút \"Xem trên model\"" in s: print("đã vá:", os.path.relpath(p, ROOT)); continue
    O, Nw = OLD.replace("CAM()", cam), NEW.replace("CAM()", cam)
    assert s.count(O) == 1, os.path.basename(p) + ": không thấy nút Xem trên model"
    s = s.replace(O, Nw)
    if crlf: s = s.replace("\n", "\r\n")
    open(p, "wb").write(s.encode("utf8")); print("vá xong:", os.path.relpath(p, ROOT))
