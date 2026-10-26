# AI Animation

Bộ công cụ làm anim game cho nhân vật 3D cùng Claude Code. Đầu vào có thể là video ref, file blocking FBX của team, hoặc chỉ một yêu cầu bằng lời. Đầu ra là FBX cho Unity.

Mỗi anim đi qua các trang web:
- **Rig Lab:** dựng khớp và skin cho nhân vật.
- **Pose Lab:** dựng pose, key, spline, vật lý, xuất FBX.
- **Review Lab:** xem playblast và ghi note theo từng frame.

Claude làm phần dựng và sửa theo note duyệt của bạn.

Repo **chỉ có mã nguồn**: skill, tool, tài liệu quy trình và mã của các trang Lab. Model nhân vật, video ref, playblast, file Blender/Cascadeur và lịch sử duyệt không nằm trong repo (xem mục [Dữ liệu không có trong repo](#dữ-liệu-không-có-trong-repo)).

## Cài đặt (một lần)

1. **Cài phần mềm:**
   - [Git](https://git-scm.com/download/win)
   - [Python 3.10+](https://www.python.org/downloads/): lúc cài nhớ tick "Add python.exe to PATH".
   - [Claude Code](https://claude.com/claude-code): app desktop (tab Code) hoặc CLI, đăng nhập bằng tài khoản Claude của bạn.
   - Không bắt buộc: Blender 4.5 (cho các clip cũ làm bằng Blender), Cascadeur, ffmpeg (để ghép video playblast).
2. **Lấy code** về một thư mục bất kỳ, ví dụ `D:\AI_Anim`:
   ```bash
   git clone https://github.com/haunguyen99/AI_Anim.git "D:/AI_Anim"
   ```
   Repo đang private. Chủ repo phải mời tài khoản GitHub của bạn trước (Settings → Collaborators).
3. **Cài môi trường Python:** mở PowerShell trong thư mục vừa clone, chạy:
   ```powershell
   powershell -ExecutionPolicy Bypass -File tools\setup.ps1
   ```
   Lệnh này tạo `.venv` và cài các thư viện trong `requirements.txt`.
4. **Mở thư mục trong Claude Code.** Các skill trong `.claude/skills` tự có sẵn, không cần cài thêm.

## Bắt đầu dùng

Trong Claude Code, gõ:

| Lệnh | Làm gì |
|---|---|
| `/home` | Mở **Home** (trang quản lý chạy trên máy, http://127.0.0.1:8780): dự án theo game → anim → nút **Tiếp tục** mở đúng trang Lab. Có thể mở Home không cần Claude bằng cách bấm đúp `tools\home\start.bat`. |
| `/new_clip` | Tạo anim mới và đăng ký vào sổ `work/clips.json`. Claude hỏi một lần những gì còn thiếu (nhân vật, số frame, ref…) rồi chọn quy trình. |
| `/rig_ai` | Rig Lab: dựng khớp và skin cho nhân vật mới. |
| `/fb` | Sau khi bạn ghi note trên Review Lab hoặc Pose Lab và bấm gửi, gõ `/fb` (có thể kèm tên clip) để Claude sửa **mọi** note của đợt đó trong một version mới. |

Có thể nói chuyện tự nhiên bằng tiếng Việt, ví dụ "làm anim Gaygor bị đánh 32 frame".

### Ba quy trình

- **A. Có video ref nhiều góc:** phân tích ref → P0 → blocking → spline → polish → FBX. Xem `docs/pipeline_v2.md`.
- **B. Có file blocking FBX của team:** nạp vào Pose Lab → phân tích → pose chuyển tiếp → polish → FBX. Xem `.claude/skills/ai-animation/knowledge/details/user_blocking.md`.
- **C. Chỉ có yêu cầu bằng lời:** thiết kế và bảng timing (chờ duyệt) → pose kể chuyện → blocking → tiếp như B. Xem `.claude/skills/ai-animation/knowledge/details/text_brief.md`.

Mọi quy trình đều có **cổng duyệt**: Claude không sang bước sau khi bạn chưa duyệt bước trước.

### Các trang Lab

Các trang Lab được dựng từ bản gốc trong repo:
- `work/pose_lab/index.html`
- `work/review_page/index.html`
- `work/rig_lab/template.html`

Lệnh `tools/clip_registry.py build` tạo trang cho từng clip, rồi Claude đăng thành trang trên claude.ai. Trang thuộc về tài khoản đã đăng nó. Muốn người khác xem hoặc ghi note, chủ trang mở trang và bấm **Share**.

Tài liệu Pose Lab:
- `docs/poselab_physics_p1.md` … `p5_impact.md`: vật lý, tác động, ragdoll.
- `docs/poselab_autophysics.md`: AutoPhysics, motion trail.

## Spine 2D

`tools/spine_mcp/` là MCP server cho Spine 2D (editor 4.2.43), chuyển từ `E:\SpineAI` ngày 2026-10-26. Server cho Claude:
- gọi Spine CLI: export, import, pack/unpack atlas;
- đọc và sửa skeleton JSON: xương, slot, animation, keyframe.

Cách dùng điển hình: export `.spine` → JSON, sửa JSON, import ra **file `.spine` mới** (không đè project gốc), mở trong Spine để kiểm tra. Chi tiết và danh sách tool ở `tools/spine_mcp/README.md`.

Cài trên máy bạn:
1. Cài [uv](https://docs.astral.sh/uv/) và Spine (mặc định `C:\Program Files\Spine\Spine.com`).
2. Thêm server `spine` vào `.mcp.json` ở thư mục gốc dự án theo mẫu trong `tools/spine_mcp/README.md`, sửa đường dẫn cho đúng máy bạn.
3. Mở lại session Claude Code.

Project Spine nằm ở `work/spine/<game>/<anim>/`, ví dụ `work/spine/G-PirateGoldrush/HandTut/` (dựng bằng `build_handtut.py`). Phần này không có trong repo GitHub.

## Tool cũ cho Blender (`legacy/`)

Từ 2026-10-23 clip mới làm hoàn toàn trên Pose Lab, **không cần Blender**. Tool Blender chỉ còn để dựng lại các clip cũ làm bằng Blender (Gaygor Idle, Idle_Front, Attack v10, SDR, SDR map06) và được dời vào `legacy/`:

- `legacy/blender/`: script chạy **bên trong Blender** (dựng control rig, khớp pose theo ref, render, QA, xuất FBX);
- `legacy/blender_tools/`: tool chạy ngoài nhưng chỉ dùng với Blender (`keyanim.py` gọi Blender, các `eye_*.py` / `sil_compare.py` so render Blender với ref, `playblast_*.py` ghép video từ render Blender);
- `legacy/mediapipe/`: thử nghiệm đầu tiên (mediapipe), bỏ.

Tool Python thường chạy từ thư mục dự án nên không cần làm gì thêm. Riêng script chạy bên trong Blender (`legacy/blender/*.py`, chạy bằng `exec`) và script Cascadeur cần biết thư mục dự án. Có ba cách, chọn một:

```python
ROOT = r"D:/AI_Anim"          # đặt trước khi exec, ví dụ trong console Blender
exec(open(ROOT + "/legacy/blender/live_render.py").read())
```

- hoặc đặt biến môi trường `AI_ANIM_ROOT=D:\AI_Anim` (một lần, cho mọi script);
- hoặc mở Blender với thư mục làm việc là thư mục dự án.

Không tìm thấy thư mục (không có `MAP.md`) thì script báo lỗi ngay, kèm cách sửa.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `.claude/skills/` | Skill của Claude: `ai-animation` (kiến thức animator, `knowledge/CORE.md` + `details/`), `new_clip`, `fb`, `home`, `rig_ai` |
| `tools/` | Tool Python: sổ clip `clip_registry.py`, Home `tools/home/`, so sánh hình, sửa FBX (`fbx_remove_mesh.py`, `fbx_replace_mesh.py`), vật lý `physics_sim.py`; `tools/cascadeur/` chạy trong Cascadeur |
| `tools/spine_mcp/` | MCP server Spine 2D (Spine CLI + sửa skeleton JSON) |
| `legacy/` | Tool cũ: Blender (`blender/`, `blender_tools/`) và mediapipe, chỉ để dựng lại clip cũ |
| `docs/` | Quy trình (`pipeline_v2.md`), thiết kế Rig Lab, vật lý Pose Lab |
| `work/pose_lab/`, `work/review_page/`, `work/rig_lab/` | Mã các trang Lab (bản gốc + script dựng trang), đọc/ghi FBX (`work/pose_lab/fbx/`) |
| `work/clips.json` | Sổ clip: dự án, nhân vật, clip, giai đoạn, link trang |
| `MAP.md` | Bản đồ file và trạng thái từng clip. Đọc trước khi tạo file mới, cập nhật sau khi thêm hoặc dời file |

## Dữ liệu không có trong repo

- Model nhân vật đã xuất cho Pose Lab (`work/pose_lab/models/`), ảnh ref (`work/pose_lab/refs/`), trang đã dựng (`pages/`).
- Video ref, playblast (`work/review_page/clips/`), FBX đã xuất, file `.blend` / `.casc`.

Muốn làm tiếp clip của người khác thì xin họ thư mục `work/<clip>/` và model tương ứng. Làm nhân vật mới thì bắt đầu bằng `/rig_ai` hoặc `/new_clip` với FBX nhân vật của bạn.

## Cập nhật và đóng góp

- Lấy bản mới: `git pull`.
- Sửa tool, skill hoặc tài liệu: tạo nhánh riêng, commit, mở Pull Request vào `main`. Không commit dữ liệu (model, video, FBX, cache).
- Bài học mới về animation ghi vào `.claude/skills/ai-animation/knowledge/details/*.md`. Chỉ quy tắc áp dụng cho mọi clip mới vào `knowledge/CORE.md`.
