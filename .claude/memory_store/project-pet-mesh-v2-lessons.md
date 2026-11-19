---
name: project-pet-mesh-v2-lessons
description: Bài học phiên "New Pet" 18/11/2026 — thay mesh mới cho 6 Pet (Mecha Pup, Pebble Turtle, Tiny Chick, Night Bat, Wind Chameleon, Tengu Swift) giữ nguyên key đã chốt, 6 phiên con Paseo song song
metadata:
  type: project
---

Phiên 18/11 (Linux): artist đổi mesh 6 Pet ở Pet_new → AI chuyển rig/skin/texture sang mesh mới, giữ key Idle/Attack đã chốt, xuất lại 18 FBX, chép đè Unity `3D_Art/3D_Animation/Pet_NEW`. AI 97′ + người 94,7′ (≈3 g 12′), 6 phiên con song song. Báo cáo: `work/infinite_defense/_review_pet_new/BAO_CAO_MESH_MOI.md`; bẫy chi tiết từng Pet: `work/infinite_defense/pets/<pet>/report_mesh_v2.md`.

**Việc làm đúng (giữ):**
- So mesh cũ/mới bằng số (đỉnh, mảnh rời, bbox, UV) TRƯỚC khi giao việc: bắt được 2 file mới quay ngược 180° (xoay lại +Z) và mesh gộp/tách mảnh. Mảnh rời 80 đỉnh của Night Bat là CÁNH, không phải mắt.
- Giữ key: chép key bằng `save_anim` → `apply_anim` (replace) trong rig đã bind lại, đối chiếu dump từng kênh từng frame (lệch 0–0,04°). Bind trong file rig sạch rồi chép key sang, không bind lại trong file idle/attack có key (`go_to_bind_pose` báo joint không về được).
- `api.mesh_data(tên, True)` = đỉnh đã biến dạng; không đối số = bind. Dùng để so số học.

**Sai sót (tránh):**
- Tạo phiên con mà chưa được bảo làm → phiên chạy luôn, người phải dừng, để lại file nháp. Tạo phiên: nói rõ "chỉ tạo, chưa làm"; đưa thư mục Frolvy của team ngay từ đầu.
- Dùng subagent cho việc cần người gõ trực tiếp → mất 1 vòng; việc dài cần trao đổi = phiên Paseo.
- Viết brief bằng suy đoán ("nhiều khả năng là mắt") → sai. Brief chỉ ghi cái đã đo.
- Người phải bắt lỗi mà phiên con không tự thấy: rig không về dáng gốc (kênh control có "đường cong chết" giữ giá trị lệch; bind lệch gối sau 2,1 cm) và texture lộn (Frolvy hiện PNG/TGA lật dọc → dùng bản flipV chỉ để xem, FBX/Unity vẫn dùng texture gốc). Tự kiểm: đổi frame rồi xem pose gốc có đứng yên không; xem texture trên viewport trước khi báo xong.
- Chưa kiểm tới nơi: chưa nhập Unity (skin/Copy Avatar), chưa playblast, chưa Director, chưa xuyên cánh–thân (Night Bat), đuôi–mào (Wind Chameleon). Nói rõ khi báo.
- Làm quá phần không được sửa khi feedback; anim lệch GDD sau bước pose; joint/skin lẫn ở Pet 4 chân (nhận xét của user).

**Bẫy Frolvy trên Linux:** `save_scene` sang file đã tồn tại trả False (xoá file đích trước); `open_scene` trả False khi scene đang sửa (lưu ra /tmp tên mới → `new_scene()` → `open_scene`); `frolvy_shot.py` trỏ đường dẫn Windows (dùng bản copy `mecha_pup/v2/shot.py`, camera đơn vị mét); cổng Frolvy chết thì `frolvy_port.py` TỰ nhảy sang cửa sổ Frolvy khác không báo (lệnh chạy nhầm cửa sổ Pet khác) — kiểm `scene` sau mỗi lần Frolvy khởi động lại; xuất FBX bake nên phải lưu `.fv` trước.

**Why:** lần sau thay mesh Pet (hoặc nhân vật) nhanh và ít vòng người bắt lỗi hơn.
**How to apply:** trước khi giao việc: so số mesh, tạo phiên "chưa làm"; sau khi xong: tự đổi frame kiểm dáng gốc + texture, ghi rõ chưa kiểm Unity. Xuất FBX chỉ khi user bảo "chốt" ([[feedback-export-only-on-approval]]). Liên quan [[reference-pet-fbx-unity-fixes]], [[reference-pets-unity-folder]], [[feedback-pet-open-latest-frolvy]].
