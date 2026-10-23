---
name: new_clip
description: Bắt đầu một anim (clip) mới hoặc một việc mới và nối nó vào chuỗi Rig Lab → Pose Lab → Review Lab. Dùng khi người dùng gõ /new_clip, nói "làm anim mới", "thêm clip", "nhân vật mới", hoặc hỏi clip đang ở giai đoạn nào. Đăng ký clip vào sổ work/clips.json, dựng và đăng trang, ghi link, nêu bước tiếp theo.
---

# /new_clip: chuỗi Rig Lab → Pose Lab → Review Lab

Mọi clip nằm trong **sổ clip** `work/clips.json` (đọc/ghi bằng `tools/clip_registry.py`). Sổ là điểm nối duy nhất: `split_pages.py` của Review Lab và Pose Lab, skill `/fb` và `/rig_ai` đều đọc từ đó. Trả lời bằng tiếng Việt. Chạy script bằng `.venv\Scripts\python.exe -I tools\clip_registry.py <lệnh>`.

## Chuỗi

| Giai đoạn | Công cụ | Ra gì | Lệnh sổ |
|---|---|---|---|
| rig (mỗi nhân vật một lần) | Rig Lab (`/rig_ai`) | khớp, skin, `rig.json` | `set-url char:<Tên> rig <url>` |
| analysis, p0 | `ai-animation` (phân tích → P0 theo mức) | `work/<job>/analysis.md`, P0 | `stage <id> p0` |
| blocking → spline → polish | Pose Lab (và Blender nếu clip cũ) | version trên Pose Lab | `pose-version`, `build`, `set-url <id> pose` |
| duyệt | Review Lab (`/fb` đọc note) | video playblast, note theo frame | `review-version`, `build`, `set-url <id> review` |
| export | `export_clip.py` / Pose Lab Xuất FBX | FBX Unity | `stage <id> export` |

Rig Lab chưa xuất FBX có skin và Pose Lab chưa đọc `rig.json` hay xương twist của Rig Lab (xem `/rig_ai`, phần "Chưa làm"). Chuỗi hiện nối ở mức đăng ký, trang và link, chưa nối dữ liệu rig tự động.

## Khi gõ /new_clip

1. **Xem sổ:** `clip_registry.py list`. Nếu người dùng chỉ hỏi trạng thái thì trả lời từ đây rồi dừng.
2. **Hỏi người dùng một lần, gộp** (`AskUserQuestion`), chỉ những gì chưa biết: nhân vật (có sẵn hay mới), tên clip, số frame và fps, có ref hay không (nơi để file), có prop và khớp cha của prop, tên bộ phận cho khung ghi note (mặc định: Vai, Tay phải, Tay trái, Chùy, Chân là của Gaygor; nhân vật khác phải đưa danh sách).
3. **Nhân vật mới (chưa có `rig_url`):** làm `/rig_ai` chế độ 3 trước, ghi link Rig Lab vào sổ rồi mới làm P0.
4. **Đăng ký:** `clip_registry.py new <Nhân vật> <Clip> [--parts "A,B,C"] [--stage analysis]`. Lệnh in id (vd `testchar_walk`).
5. **Phân tích rồi P0** theo skill `ai-animation` (viết phân tích chi tiết, chờ duyệt; P0 theo mức). Mỗi khi qua giai đoạn: `clip_registry.py stage <id> <giai đoạn>`.
6. **Trang Pose Lab (khi có P0 hoặc anim đầu tiên):** xuất model (`models/<id>_p0_v1.json`) và ảnh ref (`make_ref_sprites.py`), rồi
   `clip_registry.py pose-version <id> --version p0_v1 --label "..." --glb models/<file>.json --frames N [--keys 1 --mode keys --note "..."]`
   → `clip_registry.py build` → `Artifact` đăng `work/pose_lab/pages/<id>/index.html` (**không** truyền `url`; trang mới) → `clip_registry.py set-url <id> pose <url>`.
7. **Trang Review Lab (khi có playblast đầu tiên):** frame và video vào `work/review_page/clips/`, rồi
   `clip_registry.py review-version <id> --version v1 --label "..." --src clips/<id>_v1.webm --thumb clips/<id>_v1.jpg --n N [--fps 30 --w --h --views "..." --note "..."]`
   → `build` → `Artifact` đăng `work/review_page/pages/<id>/index.html` (trang mới) → `set-url <id> review <url>`.
8. **Các lần sau:** mỗi version mới chỉ cần `pose-version` hoặc `review-version`, `build`, rồi đăng lại **cùng file path** (Artifact giữ link và db). Đăng lại một trang cũ phải đọc bản live trước (đối chiếu diff) và công bố khi diff chỉ là phần đã biết.
9. **Cập nhật tài liệu:** dòng cho clip trong bảng "Đang làm gì" của `MAP.md`, commit kèm lý do. Bài học mới vào `knowledge/details/`.

## Quy tắc

- Mỗi clip một trang mỗi lab, mỗi trang một artifact và một db riêng; không dùng chung trang giữa các clip.
- Trang chỉ tạo khi có ít nhất một version (`split_pages.py` bỏ qua clip chưa có version).
- Không sửa `PAGES` trong `split_pages.py`: chúng tự đọc `work/clips.json`.
- Giữ tên Review Lab: tiêu đề trang `<Nhân vật> <Clip> Review Lab`, Pose Lab `<Nhân vật> <Clip> Pose Lab`.
- Cổng duyệt từng bước. Không sang giai đoạn sau khi người dùng chưa duyệt giai đoạn trước.
