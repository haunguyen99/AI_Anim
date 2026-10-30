# Nối dữ liệu Mesh → Rig → Pose → Review

Bước 4 của kế hoạch gộp: dữ liệu đi từ Lab này sang Lab sau mà không phải xuất / nhập file tay. Chạy trong vỏ ứng dụng (Home, `docs/app_shell.md`); mỗi Lab vẫn mở riêng được.

| Từ → Sang | Cách nối | Ở đâu |
|---|---|---|
| **Mesh → Rig** | Rig Lab tự dùng mesh đã sửa trong Mesh Lab (kho `<tên>_mesh_lab`, doc `mesh/edit`). Thay thân, quần áo, prop **theo tên mesh**; gợi ý khớp và xương khách dịch theo phép biến đổi đo từ hộp bao thân (scale theo chiều cao + dịch); landmark đã lưu dịch một lần khi bản sửa đổi (`meshAt`). Skin khách (`weights`) bỏ nếu số điểm đổi; skin đã tính phải tính lại. Chip **Mesh đã sửa / Mesh gốc** ở tiêu đề Rig Lab để đổi qua lại (nhớ theo trang). | `work/rig_lab/patch_meshlink.py` |
| **Rig → Pose** | Nút ➤ trên thanh vỏ (tab Rig, cần skin đã tính ở bước 4): Rig Lab dựng **glTF có skin** (xương hiện tại, mét, +Y lên; thân + quần áo skin theo SK, prop gắn cứng vào `Weapon`), server ghi `work/pose_lab/models/<clip>_rig_vN.json`, đăng ký version `rig_vN` (1 frame, label "Base pose từ Rig Lab") bằng `clip_registry pose-version`, nâng giai đoạn lên p0 nếu đang rig / analysis, build lại trang Pose, rồi vỏ chuyển sang tab Pose. Nút **Xuất glTF** ở mục "Thống kê và xuất" tải file khi mở riêng. | `work/rig_lab/patch_posexport.py`, `POST /api/rig/to-pose` |
| **Pose → Review** | Nút 🎞 trên thanh vỏ (tab Pose): Pose Lab hỏi **camera, khoảng cách camera tới nhân vật (×0,3–2,5, xem thử trực tiếp trên viewport) và cỡ ô** (right, left, front, back, top, bottom, 3/4; ô 300×400 / 450×600 / 600×800; nhớ lựa chọn; mặc định 4 camera 450×600) rồi quay playblast không gizmo / khớp bằng canvas ghép + MediaRecorder theo nhịp fps; server lưu `work/review_page/clips/<clip>_pbN.webm/.jpg`, **nén lại bằng ffmpeg** (VP9, tua được; không có ffmpeg thì giữ bản gốc), đăng ký version `pbN` bằng `clip_registry review-version`, build lại, vỏ chuyển sang tab Review. Nút 🎞 trong Pose Lab chỉ tải `.webm` khi mở riêng. | `work/pose_lab/patch_playblast.py`, `POST /api/playblast` |
| **Review → Pose / Claude** | Ghi chú và vòng gửi lưu trong kho (`work/store/<ns>/notes`, `rounds`); `/check_fb` đọc từ đó khi chạy cục bộ. | `docs/storage.md` |

- **Điều kiện:** anim phải đã đăng ký Pose Lab và Review Lab trong sổ (`/new_clip <id>` tạo `pose.clip`, `review.clip`).
- **Nút gửi** gọi hàm `window.DDC.rigGltf()` / `window.DDC.playblast()` của Lab trong iframe cùng nguồn gốc; không có gì gửi ra ngoài máy.
- **Chưa có:** Pose Lab tự đọc `rig.json` / xương twist của Rig Lab (model glTF đã chứa xương hiện tại, kể cả twist); quay playblast có physics / ref cạnh nhau; Review → Pose tự tạo version sửa.

## Rig có sẵn (xương + skin khách)

Mesh đã có rig từ trước (FBX của game) thì **không cần rig lại**: Rig Lab chỉ dùng xương và skin khách để đối chiếu (đường vàng, "Skin khách"), nhưng có hai nút để dùng thẳng — hiện khi trang có dữ liệu khách (hiện có Gaygor; nhân vật build từ mesh trần như Zom1 thì không có):

- Bước 2: **Dùng xương khách** đặt mọi khớp trùng tên theo vị trí xương khách (Gaygor: 58 khớp).
- Bước 4: **Dùng skin khách** lấy trọng số khách làm skin (tối đa 4 xương mỗi đỉnh, chuẩn hoá lại), khỏi tính skin; tự kiểm chạy ngay. Đỉnh khách không có trọng số thì gán `Root_M`.

Bản vá: `work/rig_lab/patch_adoptrig.py`.
