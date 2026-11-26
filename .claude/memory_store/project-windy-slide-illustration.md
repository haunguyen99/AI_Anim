---
name: project-windy-slide-illustration
description: Slide dạy Rigging 3D dùng Hero Windy làm ví dụ đặt xương; hình joint phải hạ Chest 4 cm và đưa HeadEnd về đỉnh đầu (user 2026-11-25)
metadata:
  type: project
---

User 2026-11-25 làm slide phổ cập "Rigging 3D bằng AI trong Frolvy" cho người chưa biết 3D, mỗi bước rig có ví dụ Windy. Khi đưa hình Windy vào minh hoạ: **hạ điểm Chest thấp hơn một chút (đã dùng 4 cm) và đưa điểm HeadEnd về đỉnh đầu (y = 185 cm, đỉnh mesh); Scapula + Shoulder dịch ra ngoài (đã dịch 2 lần, tổng 6 cm mỗi điểm)**. Fit gốc (Hero_Windy.fvfit 17/11) có Chest 107,7 và HeadEnd 195,7 cm.

**Why:** hình joint trực tiếp từ fit trông sai (HeadEnd cao hơn đầu 10 cm, cột sống không đều); user muốn hình dạy đúng.
**How to apply:** `tools/windy_joint_overlay.py out.png` vẽ joint thân chồng mesh (--chest-drop, --head-top); chuỗi áo choàng Cape/Clo chưa vẽ đúng từ file, cần ảnh Frolvy thật. Slide ở docs/slides/. Dàn ý chờ user duyệt trước khi làm. Liên quan [[project-endless-kicker]].

**Đã làm 2026-11-25:** slide `docs/slides/rigging_3d_cho_nguoi_moi.html` (38 trang, dựng bằng `tools/slides_rigging_deck/build.py`), user duyệt dàn ý rồi bảo làm. Hình Windy sinh bằng `tools/windy_slide_images.py` (Chest −4, HeadEnd 185, Scapula/Shoulder ra 6 cm). Còn thiếu: ảnh Frolvy thật của chuỗi áo choàng, control, skin Windy (Frolvy không kết nối phiên đó).

**v2 2026-11-26:** agent "người mới" (subagent không kiến thức 3D, chỉ đọc PDF) chấm bản đầu 5/10: thiếu "bắt đầu từ đâu", từ chuyên môn không giải thích, hình nhỏ/sai ý, ví dụ Windy đứt từ bước 3, quá nhiều lỗi/tên dự án. Đã sửa: c1n/c2n/c3n.py (giọng "bạn", từ điển, 10 bước đánh số lại, 1–2 lỗi mỗi bước, đạt/chưa đạt, phụ lục). **Cách kiểm slide dạy người mới: cho subagent đọc PDF rồi trả 10 câu hỏi + danh sách từ chưa hiểu.** /tmp bị dọn khi đổi ngày: nguồn dựng slide phải nằm trong repo (tools/slides_rigging_deck/).

**2026-11-26 đổi model minh hoạ sang Ninja** (user: "ninja có lưới 4 dễ nhìn hơn lưới của windy"): hình trong slide giờ là Ninja (`tools/ninja_slide_images.py`, landmarks Ninja không chỉnh, trước/sau là giả lập lỗi); gộp bước 1+2 thành "Kiểm tra Mesh" nên slide còn 9 bước, 35 trang. Windy cũ vẫn ở `tools/windy_slide_images.py` (các chỉnh Chest/HeadEnd/Scapula chỉ áp cho Windy). Ninja rig dựng trong Studio (không phải Frolvy), kunai gắn Weapon dưới Wrist. Hình Ninja áp chỉnh riêng (user 2026-11-26, sau khi thấy bản đầu còn cao): Root hạ 3, Neck hạ 7, Head hạ 7, Hip hạ 3, Knee hạ 3, Spine hạ 5, Chest hạ 8 cm; Scapula hạ 3 cm + ra ngoài 6 cm; Shoulder ra ngoài 6 cm; Head End vốn ở đỉnh đầu.
