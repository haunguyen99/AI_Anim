# Vỏ ứng dụng (Home)

Bước 2 của kế hoạch gộp: Home (`tools/home`, http://127.0.0.1:8780) vừa là danh sách dự án vừa chứa các Lab trong **một cửa sổ**.

- **Vào:** Home → dự án → anim. Nút ▶ Tiếp tục và các icon Rig / Pose / Review mở Lab **ngay trong Home** (đường dẫn `#/app/<clip>/<rig|pose|review>`). Chưa có trang build trên máy thì icon vẫn mở bản artifact trên claude.ai ở tab mới như cũ.
- **Thanh điều hướng:** ◀ về dự án · tên nhân vật + anim · tab **Mesh | Rig | Pose | Review** (xám khi chưa có trang) · ☁ mở bản trên claude.ai · ⟳ tải lại Lab đang xem. Mỗi Lab là một iframe và được **giữ nguyên khi chuyển tab** (không mất pose đang chỉnh, không tải lại model).
- **Server** (`tools/home/server.py`): `GET /lab/<pose|review|rig>/<id>` trả trang đã build (`work/pose_lab/pages/<clip>/`, `work/review_page/pages/<clip>/`, `work/rig_lab/pages/<nhân vật>/`) kèm `<base>` để model, ảnh ref, clip, `fbx/fbxexport.js` tìm đúng chỗ; phục vụ file tĩnh `.js .json .glb .css` trong `work/pose_lab`, `work/review_page`, `work/rig_lab` (không có `work/store`); video hỗ trợ Range nên tua được. `/api/state` thêm `labs: {pose, review, rig}` cho mỗi anim.
- **Lưu:** cùng nguồn gốc với Home nên các Lab dùng kho trên máy (`docs/storage.md`) và nút Lưu trữ như khi mở riêng.
- **Rig của nhân vật:** thư mục `work/rig_lab/pages/<tên>` trùng tên nhân vật (không phân biệt hoa thường, hoặc bắt đầu bằng tên đó); đặt khóa `rig_page` trong `characters` của `work/clips.json` để chỉ định.
- **Sau khi sửa master Lab:** build lại trang (`tools/clip_registry.py build`, `work/rig_lab/build_char.py <id>`, `work/rig_lab/build_page.py`) để vỏ thấy bản mới. Vỏ không tự build.

Chưa làm: trang Mesh (bước 3), nối dữ liệu Mesh → Rig → Pose → Review (bước 4), mở nhiều Lab cạnh nhau.
