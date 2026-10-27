# AI Animation

Bộ công cụ làm anim game cho nhân vật 3D cùng Claude Code. Đầu vào có thể là video ref, file blocking FBX của team, hoặc chỉ một yêu cầu bằng lời. Đầu ra là FBX cho Unity.

Mọi thứ chạy trong **Home**, một ứng dụng web trên máy bạn (http://127.0.0.1:8780) với thanh tab. Mỗi anim đi qua các trang:
- **Mesh Lab:** sửa mesh cơ bản (chọn điểm / mặt / khối, dời xoay scale, Channel Box, Free Transform, hàn, tách, dọn, đặt sàn, chiều cao).
- **Rig Lab:** dựng khớp và skin cho nhân vật (có Outliner; dùng luôn xương và skin có sẵn của mesh).
- **Pose Lab:** dựng pose, key, spline, vật lý, xuất FBX.
- **Review Lab:** xem playblast và ghi note theo từng frame.

Dữ liệu đi từ trang này sang trang sau ngay trong Home: Rig Lab tự dùng mesh đã sửa, nút ➤ gửi rig sang Pose Lab (glTF có skin), nút 🎞 quay playblast nhiều camera sang Review Lab. Mọi Lab lưu vào file thật trong `work/store/` (nút Lưu trữ ở góc trên để xuất / mở `.json`). Chi tiết: `docs/app_shell.md`, `docs/data_flow.md`, `docs/storage.md`, `docs/mesh_lab.md`.

Claude làm phần dựng và sửa theo note duyệt của bạn. Hỗ trợ cả iPad / điện thoại: tick ô hình bàn tay ở Pose Lab, Rig Lab, Mesh Lab.

Repo **chỉ có mã nguồn**: skill, tool, tài liệu quy trình và mã của các trang Lab. Model nhân vật, video ref, playblast, file dựng cũ (.blend, .casc) và lịch sử duyệt không nằm trong repo (xem mục [Dữ liệu không có trong repo](#dữ-liệu-không-có-trong-repo)).

## Cài đặt (một lần)

1. **Cài phần mềm:**
   - [Git](https://git-scm.com/download/win)
   - [Python 3.10+](https://www.python.org/downloads/): lúc cài nhớ tick "Add python.exe to PATH".
   - [Claude Code](https://claude.com/claude-code): app desktop (tab Code) hoặc CLI, đăng nhập bằng tài khoản Claude của bạn.
   - Không bắt buộc: ffmpeg (nén playblast để tua mượt). **Không cần Blender hay Cascadeur**: team không còn dùng hai phần mềm này, và repo đã bỏ mọi tool của chúng.
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
5. **Mở Home:** gõ `/project` trong Claude Code, hoặc bấm đúp `tools\home\start.bat` rồi mở http://127.0.0.1:8780. Các Lab cần mạng (tải three.js từ CDN). ffmpeg có thì playblast được nén lại để tua mượt; không có thì vẫn dùng được.

## Bắt đầu dùng

Trong Claude Code, gõ:

| Lệnh | Làm gì |
|---|---|
| `/project` | Mở **Home** (trang quản lý chạy trên máy, http://127.0.0.1:8780): dự án theo game → anim → nút **Tiếp tục** mở đúng trang Lab. Có thể mở Home không cần Claude bằng cách bấm đúp `tools\home\start.bat`. |
| `/new_clip` | Tạo anim mới và đăng ký vào sổ `work/clips.json`. Claude hỏi một lần những gì còn thiếu (nhân vật, số frame, ref…) rồi chọn quy trình. |
| `/rig` | Rig Lab: dựng khớp và skin cho nhân vật mới. |
| `/spine2d` | Rig và làm anim 2D bằng Spine (order của GD → thiết kế → rig → anim → GIF trên UI → export) |
| `/push` | Đẩy mã nguồn (skill, tool, quy trình, tài liệu, mã các Lab) lên GitHub `main` bằng `tools/push_source.py`; không đẩy dữ liệu, không force. |
| `/check_fb` | Sau khi bạn ghi note trên Review Lab hoặc Pose Lab và bấm gửi, gõ `/check_fb` (có thể kèm tên clip) để Claude sửa **mọi** note của đợt đó trong một version mới. |

Có thể nói chuyện tự nhiên bằng tiếng Việt, ví dụ "làm anim Gaygor bị đánh 32 frame".

### Ba quy trình

- **A. Có video ref nhiều góc:** phân tích ref → P0 → blocking → spline → polish → FBX. Xem `docs/pipeline_v2.md`.
- **B. Có file blocking FBX của team:** nạp vào Pose Lab → phân tích → pose chuyển tiếp → polish → FBX. Xem `.claude/skills/animation/knowledge/details/user_blocking.md`.
- **C. Chỉ có yêu cầu bằng lời:** thiết kế và bảng timing (chờ duyệt) → pose kể chuyện → blocking → tiếp như B. Xem `.claude/skills/animation/knowledge/details/text_brief.md`.

Mọi quy trình đều có **cổng duyệt**: Claude không sang bước sau khi bạn chưa duyệt bước trước.

### Các trang Lab

Các trang Lab được dựng từ bản gốc trong repo:
- `work/pose_lab/index.html`
- `work/review_page/index.html`
- `work/rig_lab/template.html`
- `work/mesh_lab/template.html`

Lệnh `tools/clip_registry.py build` tạo trang cho từng clip, rồi Claude đăng thành trang trên claude.ai. Trang thuộc về tài khoản đã đăng nó. Muốn người khác xem hoặc ghi note, chủ trang mở trang và bấm **Share**.

Tài liệu Pose Lab:
- `docs/poselab_physics_p1.md` … `p5_impact.md`: vật lý, tác động, ragdoll.
- `docs/poselab_autophysics.md`: AutoPhysics, motion trail.

## Spine 2D

`tools/spine_mcp/` là MCP server cho Spine 2D (editor 4.2.43), chuyển từ `E:\SpineAI` ngày 2026-10-26. Server cho Claude:
- gọi Spine CLI: export, import, pack/unpack atlas;
- đọc và sửa skeleton JSON: xương, slot, animation, keyframe.

Skill **`/spine2d`** biến Claude thành animator Spine: nhận order của GD, thiết kế, rig (xương, mesh có weight), key + curve, xem trước GIF ghép trên ảnh UI game (`tools/spine/render_spine.py`), export đúng setting của bạn.

Cách dùng điển hình: export `.spine` → JSON, sửa JSON, import ra **file `.spine` mới** (không đè project gốc), mở trong Spine để kiểm tra. Chi tiết và danh sách tool ở `tools/spine_mcp/README.md`.

Cài trên máy bạn:
1. Cài [uv](https://docs.astral.sh/uv/) (phải có `uv` trong PATH) và Spine (mặc định `C:\Program Files\Spine\Spine.com`, phiên bản 4.2.43; Spine ở chỗ khác thì đặt biến môi trường `SPINE_EXE`, `SPINE_VERSION`).
2. Repo đã có sẵn `.mcp.json` khai báo server `spine` (chạy từ thư mục gốc dự án, không ghi cứng đường dẫn). Mở dự án trong Claude Code, duyệt server `spine` khi được hỏi, mở lại session nếu cần. Máy bạn đã có `.mcp.json` riêng (Blender, Cascadeur…) thì gộp mục `spine` vào đó thay vì ghi đè.

Project Spine nằm ở `work/spine/<game>/<anim>/`, ví dụ `work/spine/G-PirateGoldrush/HandTut/` (dựng bằng `build_handtut.py`). Phần này không có trong repo GitHub.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `.claude/skills/` | Skill của Claude: `animation` (kiến thức animator, `knowledge/CORE.md` + `details/`), `new_clip`, `check_fb`, `push`, `project`, `rig`, `spine2d` (rig + anim Spine 2D) |
| `tools/` | Tool Python: sổ clip `clip_registry.py`, Home `tools/home/`, so sánh hình, sửa FBX (`fbx_remove_mesh.py`, `fbx_replace_mesh.py`), vật lý `physics_sim.py`; `tools/cascadeur/` chạy trong Cascadeur |
| `tools/spine_mcp/` | MCP server Spine 2D (Spine CLI + sửa skeleton JSON) |
| `tools/spine/` | `render_spine.py`: xem trước anim Spine thành GIF + contact sheet (xương, alpha slot, region, mesh có weight; không IK/clipping) |
| `docs/` | Quy trình (`pipeline_v2.md`), thiết kế Rig Lab, vật lý Pose Lab |
| `work/pose_lab/`, `work/review_page/`, `work/rig_lab/`, `work/mesh_lab/` | Mã các trang Lab (bản gốc + script dựng trang), đọc/ghi FBX (`work/pose_lab/fbx/`) |
| `work/store/` | Kho dữ liệu Lab trên máy (ghi chú, key, skin, mesh đã sửa), mỗi máy một bản, **không** có trong repo |
| `work/clips.json` | Sổ clip: dự án, nhân vật, clip, giai đoạn, link trang |
| `MAP.md` | Bản đồ file và trạng thái từng clip. Đọc trước khi tạo file mới, cập nhật sau khi thêm hoặc dời file |

## Dữ liệu không có trong repo

- Model nhân vật đã xuất cho Pose Lab (`work/pose_lab/models/`), ảnh ref (`work/pose_lab/refs/`), trang đã dựng (`pages/`).
- Video ref, playblast (`work/review_page/clips/`), FBX đã xuất, file `.blend` / `.casc`.
- Mesh gốc của nhân vật (vd `work/rig_lab/ref_gaygor/`): thiếu thì Mesh Lab và Rig Lab của nhân vật đó không dựng lại được (`work/mesh_lab/build_mesh.py <nhân vật>`, `work/rig_lab/build_char.py <id>`). Trang Pose / Review của anim cũ cũng cần model và video gốc; Home vẫn liệt kê anim từ `work/clips.json` và mở link claude.ai nếu chưa có trang trên máy.
- `work/store/`: dữ liệu làm việc của riêng mỗi máy. Muốn chuyển sang máy khác thì xuất file `.json` bằng nút Lưu trữ rồi mở lại ở máy kia.
- `.mcp.json` có sẵn trong repo chỉ khai báo server Spine; muốn thêm server khác thì gộp vào file đó trên máy bạn.

Muốn làm tiếp clip của người khác thì xin họ thư mục `work/<clip>/` và model tương ứng. Làm nhân vật mới thì bắt đầu bằng `/rig` hoặc `/new_clip` với FBX nhân vật của bạn.

## Cập nhật và đóng góp

- Lấy bản mới: `git pull`.
- Sửa tool, skill hoặc tài liệu: tạo nhánh riêng, commit, mở Pull Request vào `main`. Không commit dữ liệu (model, video, FBX, cache).
- Bài học mới về animation ghi vào `.claude/skills/animation/knowledge/details/*.md`. Chỉ quy tắc áp dụng cho mọi clip mới vào `knowledge/CORE.md`.
