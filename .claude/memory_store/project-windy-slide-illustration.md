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
