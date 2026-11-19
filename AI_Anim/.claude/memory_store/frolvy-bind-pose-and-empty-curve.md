---
name: frolvy-bind-pose-and-empty-curve
description: Frolvy bẫy khi rig Pet: bind skin phải ở pose 0 (control posed lúc bind = cánh dính mặt/tai); xóa hết key một channel làm channel chết; dựng lại rig để lại joint ma
metadata:
  type: feedback
---

Night Bat (2026-11-12): user báo "cánh dính vào mặt/tai" 4 lần, nguyên nhân gốc là **bind skin khi một control đang posed** (TransformLink ghi pose lệch) — không phải trọng số.
- Trước `bind_skin`: đưa mọi CTL về 0, `set_frame(3); set_frame(0)` để ép tính lại, rồi bind (đã vào `rig_skin.py`).
- Tách chi: nhóm trọng số WING / EAR / HEAD / BODY, chỉ cho trộn wing+body, ear+head, head+body; mặt nạ ellipsoid đầu; mesh_data luôn trả vị trí chưa biến dạng; `api.vertex_weights(v)` đọc trọng số thật để vẽ kiểm.
- Xóa hết key của một channel → channel đó "chết" (`rotate` không ăn, key sau ghi 0). Luôn key 0 mọi frame trước rồi ghi giá trị; đổi clip chỉ xóa key quá khung.
- Dựng lại rig trong cùng scene: joint/constraint cũ vẫn bị xuất ra (joint ma) → `ghost_rename.py` trước `fbx_ascii_keep`; tốt nhất build một lần. Chèn đốt giữa chuỗi: dời group control + đặt lại local joint rồi constrain lại, bind lại.
- Cổng Frolvy của phiên có thể bị user tắt: dựng lại bằng script được; khi user mở file của mình trên cổng khác thì sửa trực tiếp ở đó.

- Mesh hàn liền (tai nối cánh bằng mặt dài): skin không tách nổi, mặt nối giãn x2-3 khi xoay mạnh. Đo bằng `api.mesh_data(obj, posed=True)` (vị trí sau skin) + `skin_check.py` (giãn cạnh, dịch chuyển theo nhóm). Cách trị đã duyệt (Night Bat): `extract_faces` tách tai (+ màng nối) thành mesh riêng `Pet_Night_Bat_Ears`, gốc tai pha dần sang Head; Base FBX thành 2 mesh (`--meshes 2`).

**Why:** mất nhiều vòng sửa trọng số trong khi lỗi là bind lệch pose.
**How to apply:** mỗi lần bind/rebind skin trên Frolvy: kiểm control = 0 trước; kiểm đối xứng trái/phải ở pose 0 sau khi bind. Script: work/infinite_defense/pets/night_bat/rig_skin.py. Liên quan [[frolvy-fit-controls-after-build]].
