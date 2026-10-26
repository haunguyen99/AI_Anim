---
name: rig_ai
description: Gọi tool rigging Rig Lab (trang web, không Blender). Dùng khi người dùng gõ /rig_ai, muốn rig hoặc skin một nhân vật, mở lại trang Rig Lab, hoặc đã duyệt hoặc ghi note ở các cổng của Rig Lab. Có ba chế độ: mở trang, đọc phản hồi (db), dựng nhân vật mới.
---

# /rig_ai: Rig Lab

Rig Lab là trang web một-file (three.js) để rig từ mesh: kiểm mesh, đặt khớp, sinh xương (có twist), skin tự động + tô tay, thử khớp. Trả lời bằng tiếng Việt. Không dùng Blender, kể cả headless (người dùng 2026-10-23).

Thiết kế: `docs/rig_lab_design.md`. Bản đồ file: mục `work/rig_lab/` trong `MAP.md`.

## Trang hiện có

| Nhân vật | Artifact | Nguồn |
|---|---|---|
| Gaygor | https://claude.ai/artifact/UgRawtmJZW6biJZVbUK4Rs | `work/rig_lab/template.html` → `build_page.py` → `pages/gaygor/index.html` |

Capabilities đã khai: `db`, `user`, `downloads` (publish lại thì bỏ trống `capabilities`, giữ khai báo cũ). Preview cục bộ: `preview_start` tên `rig-lab` (cổng 8772).

## Chọn chế độ theo lời người dùng

- **Chỉ gõ `/rig_ai` hoặc "mở Rig Lab"** → chế độ 1.
- **"/rig_ai fb", đã duyệt, đã ghi note, đã lưu skin** → chế độ 2.
- **Nhân vật mới / mesh mới** → chế độ 3.

### 1. Mở trang

`Artifact` action `open` với URL bảng trên. Nói một dòng: đang ở bước nào (đọc `rig/gates`, xem chế độ 2) và nhắc phím tắt chính: Alt+chuột trái xoay, Alt+chuột giữa kéo, Alt+chuột phải hoặc lăn zoom, Q W E R công cụ, F nhìn vùng chọn, A nhìn toàn bộ, Ctrl+Z hoàn tác, nút `?` góc viewport.

### 2. Đọc phản hồi từ db (không polling)

Dữ liệu nằm trong db của artifact (`ArtifactData`, nạp bằng ToolSearch `select:ArtifactData` nếu chưa có), collection `rig`:

| doc | nội dung |
|---|---|
| `gates` | `g[1..5] = {status: "ok"\|"fix", note, at}` (bước 1 Mesh, 2 Khớp, 3 Xương, 4 Skin, 5 Thử khớp) |
| `landmarks` | `lm` (tên khớp → [x,y,z] cm), `tw` (số xương twist mỗi đoạn: Shoulder, Elbow, Hip, Knee) |
| `skin` | `names`, `I`, `W` (4 ảnh hưởng/đỉnh, phẳng), `sig`, `nv` |

Cách làm:
1. `list` collection `rig` với `out_dir` vào scratchpad, đọc các file.
2. Báo tóm tắt: bước nào đã duyệt, bước nào cần sửa kèm note; có skin đã lưu không (`sig` khớp `landmarks` hiện tại không).
3. Không có doc nào hoặc `gates` trống: người dùng chưa lưu được, nói thẳng (trang báo "chỉ trình duyệt này" khi db không nối).
4. Note sửa → sửa **gộp một lần** trong `template.html`, rồi chạy `build_page.py`, xem thử bằng preview, publish lại cùng file path (`pages/gaygor/index.html`). Muốn thử trên dữ liệu của người dùng: chép `landmarks` từ db ra file JSON trong `pages/<nv>/` tạm, nạp bằng `fetch` trong `javascript_tool`, **xóa file tạm trước khi publish**.
5. Khi người dùng duyệt xong bước: `git commit` nêu lý do, cập nhật `.claude/skills/ai-animation/knowledge/details/blender_tools.md` (mục Rig Lab) nếu có bài học mới.

### 3. Nhân vật mới

`build_page.py` và `propose.py` còn viết cứng cho Gaygor (tên xương theo rig khách, tỉ lệ khớp tuned trên Gaygor, `pages/gaygor`). Dựng nhân vật mới theo thứ tự:

1. **Hỏi người dùng (một lần, gộp):** mesh/FBX ở đâu, rig có sẵn hay mesh trần, template (biped, biped+đuôi, quadruped, nhện 8 chân), quy ước tên xương, có prop rời không, khớp cha của prop.
2. **Mesh:** FBX → `python work/rig_lab/extract_fbx.py <fbx> work/rig_lab/ref_<tên>` (dùng `.venv\Scripts\python.exe -I`). GLB/OBJ: viết bộ đọc cùng đầu ra (`verts`, `tris`, nhiều mesh thì mesh nhiều đỉnh nhất = thân, còn lại = prop).
3. **Gợi ý khớp:** `propose.py` chỉ đúng cho biped giống Gaygor. Tỉ lệ khớp (trong code) tuned trên Gaygor nên nhân vật khác phải đối chiếu bằng mắt ở view Trước và Cạnh; đầu và cổ theo z/y sai nhiều nhất.
4. **Trang:** nhân bản `build_page.py` thành tham số (tên nhân vật, đường dẫn ref), thêm một mục `rig-lab-<tên>` vào `.claude/launch.json`, `pages/<tên>/index.html`, publish trang MỚI (không đè trang Gaygor; mỗi nhân vật một artifact và một db), thêm dòng vào bảng "Trang hiện có" ở trên và `MAP.md`.
5. **Ghi sổ clip:** `clip_registry.py set-url char:<Tên> rig <url>` (xem skill `/new_clip`); `/fb` và `/new_clip` đọc link từ `work/clips.json`.
6. **Giữ cổng duyệt từng bước.** Không sang bước sau khi bước trước chưa duyệt.

## Bẫy đã gặp (đừng lặp lại)

- Sửa template bằng script Python: viết script ra file rồi chạy, không dùng heredoc Python trong Bash có ngoặc kép lồng (đã hỏng hai lần).
- `javascript_tool` trên preview: trang có thể cache bản cũ, `navigate` lại trước khi thử.
- Raycast gán khối rời phải bỏ khối thân chính (>30% đỉnh), nếu không gán nhầm cả thân.
- Tô skin ở bước 4 đang pose: dùng vị trí đã pose, và phải `computeBoundingSphere` sau khi pose.
- Gaygor: khiên rời 90 đỉnh bên R (x≈−118) gán 100% cho joint twist cẳng tay; xương cuối (`*End_*`, `Finger3`, `Weapon`) không skin.

## Chưa làm

Xuất FBX có skin (writer `work/pose_lab/fbx/fbxwrite.py` mới ghi xương và animation), Pose Lab đọc `rig.json` và xương twist, template quadruped/nhện 8 chân. Khi người dùng đòi, kiểm sớm bằng một FBX tối thiểu nạp lại vào Pose Lab (so vị trí xương như `fbx/cmp_page_track.py`).
