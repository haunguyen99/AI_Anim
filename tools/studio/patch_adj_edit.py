"""Vá lõi Pose: điều chỉnh key (collection adjusts) có nút Sửa (lời ghi chú, sửa tại chỗ) + Xoá cũng cho mục không có người tạo
(Studio chạy trên máy một người, điều chỉnh không ghi author nên trước đây không hiện Xoá). User 2026-10-29: "các fb cần có tính năng xóa, sửa".
Áp CÙNG bản vá vào work/pose_lab/index.html và tools/studio/modules/pose_engine.js (không chạy port_pose.py, xem patch_onion.py).
Chạy: python -I tools/studio/patch_adj_edit.py   (chạy lại an toàn)"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FILES = [os.path.join(ROOT, "work", "pose_lab", "index.html"), os.path.join(ROOT, "tools", "studio", "modules", "pose_engine.js")]

OLD = '''    if (a.id && db && canWrite && (a.author === myId || (user && user.canEdit && user.canEdit()))) {
      const del = document.createElement("button"); del.className = "btn"; del.textContent = "Xoá";'''
NEW = '''    if (a.id && db && canWrite && (!a.author || a.author === myId || (user && user.canEdit && user.canEdit()))) {
      // Sửa lời ghi chú tại chỗ (user 2026-10-29 "các fb cần có tính năng xóa, sửa"); mục không ghi người tạo (Studio trên máy) cũng sửa / xoá được
      const ed = document.createElement("button"); ed.className = "btn"; ed.textContent = "Sửa";
      ed.onclick = () => {
        const ta = document.createElement("textarea"); ta.value = a.text || ""; ta.rows = 3; ta.style.cssText = "width:100%;margin:4px 0";
        const ok = document.createElement("button"); ok.className = "btn primary"; ok.textContent = "Lưu";
        const no = document.createElement("button"); no.className = "btn"; no.textContent = "Huỷ";
        const r2 = document.createElement("div"); r2.className = "row"; r2.append(ok, no);
        ta.addEventListener("keydown", e => e.stopPropagation());   // gõ chữ không chạy phím tắt Pose
        no.onclick = () => renderAdjs();
        ok.onclick = async () => { const { id, ...rest } = a; rest.text = ta.value.trim(); rest.editedAt = new Date().toISOString();
          try { await db.doc("adjusts/" + a.id).set(rest); a.text = rest.text; } catch (e) { fail(e); } renderAdjs(); };
        el.querySelector("p") ? el.querySelector("p").replaceWith(ta) : el.insertBefore(ta, row); row.replaceWith(r2); ta.focus();
      };
      row.append(ed);
      const del = document.createElement("button"); del.className = "btn"; del.textContent = "Xoá";'''

for p in FILES:
    raw = open(p, "rb").read().decode("utf8"); crlf = "\r\n" in raw; s = raw.replace("\r\n", "\n")
    if 'ed.textContent = "Sửa"' in s: print("đã vá:", os.path.relpath(p, ROOT)); continue
    assert s.count(OLD) == 1, os.path.basename(p) + ": không thấy khối Xoá điều chỉnh"
    s = s.replace(OLD, NEW)
    if crlf: s = s.replace("\n", "\r\n")
    open(p, "wb").write(s.encode("utf8")); print("vá xong:", os.path.relpath(p, ROOT))
