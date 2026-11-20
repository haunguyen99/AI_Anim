# VFX_LIb

Unity project – thư viện VFX.

## Harness (khung làm việc, 2026-11-04)

- **Đầu mỗi hội thoại:** đọc `CLAUDE.md` + `MAP.md`; việc VFX đọc thêm `Docs/VFX/_ArtDirection/PROGRESS.md`.
- Luật art lead: `.claude/rules/vfx-art-lead.md` (tự nạp). **Việc VFX: tra `Docs/VFX/_Anatomy/<loại>.md` (tạo hình bất biến) trước khi làm; chưa có thì research rồi lưu file mới** (2026-11-10). Quy tắc agent / phiên song song: `AGENTS.md`. Mục tiêu + tiêu chí xong: `SPEC.md`.
- Tạo / di chuyển file thì cập nhật `MAP.md`. Học được điều lâu dài thì ghi vào `contexte/<chủ-đề>.md`.
- Sở thích riêng máy: `CLAUDE.local.md` (không commit). Secret chỉ để trong `.env` (không commit).
- Git: https://github.com/doson2801-dos/AI_VFX (private, nhánh `main`). Asset Unity không có trong git.
  - **Chỉ commit kiến thức + skill + tài liệu** (art lead 2026-11-04): `CLAUDE.md`, `MAP.md`, `SPEC.md`, `AGENTS.md`, `contexte/`, `.claude/rules/`, `.claude/skills/`, mọi `Docs/**/*.md`. **Không** commit file code của Assets (`.cs`, `.shader`, `.py`…), BuildReport, asset.
  - **Hai nhánh, hai việc** (art lead 2026-11-10; mục đích: đổi máy / đổi nền tảng vẫn còn thông tin cũ): `main` = kiến thức, **có trên GitHub**; `master` = nhánh làm việc ở máy, chứa cả tài nguyên (Assets, builder…), **chỉ ở máy, không bao giờ push** (hook `pre-push` chặn). Có thay đổi skill / luật / `.md` / cấu hình dùng chung thì **commit lên git ngay**, không đợi cuối ngày.
  - Công cụ: `tools/sync_knowledge.py` (commit phạm vi kiến thức lên `master`, chép từng commit sang `main` bằng index tạm, không đổi nhánh, rồi push `main`). Chạy bởi hook `Stop` (sau mỗi lượt Claude, khi đã bật trong `.claude/settings.json`), Task Scheduler `VFX_LIb Auto Commit` lúc **17:30** (`tools/auto_commit.ps1`, phòng khi sửa ngoài Claude), hoặc tay `python -I tools/sync_knowledge.py [--dry-run]`. Log `tools/auto_commit.log`. Chi tiết + cách dựng lại ở máy mới: `contexte/git-sync.md`.
  - Phạm vi kiến thức: như trên, thêm `.gitignore`, `.mcp.json`, `.claude/settings.json`, `.claude/launch.json`, `tools/sync_knowledge.py`, `tools/auto_commit.ps1`, `Docs/VFX/_Library/*.csv` (bảng tra Library).
- **Máy mới / vừa clone nhánh `VFX` mà thiếu `Assets/Library/`** (2026-11-20): chạy `python -I tools/fetch_library.py` — tải `Library.tar.gz` từ Google Drive (https://drive.google.com/drive/folders/1Yar5LDgR5drwZ2-1LaOi-xHExtbJHMVm, ~113 MB, 460 ảnh + .meta giữ GUID) và giải nén vào `Assets/`. Đủ rồi thì tự bỏ qua; `--force` tải lại. **Claude: đầu hội thoại, nếu `Assets/Library/` không có thì chạy lệnh này trước khi làm việc VFX.** Cần `gdown` (script tự cài). Cập nhật Library thì nén lại `Library.tar.gz` (gốc `Library/`) và thay file trên Drive.
- **Texture cho mọi skill lấy từ `Assets/Library/`** (2026-11-04; cây chia lại 2026-11-09: `<nhóm>/<vai trò>/<nhóm>_<vai trò>_NNN`). **Chọn theo `Docs/VFX/_Library/LIBRARY.md`** (thành phần → thư mục), xem ảnh rồi chốt; nguồn ở `library_index.csv`. Slash của `/vfx-shader` dùng `Assets/Library/Slash/Main_tex(Uvmesh)/` làm texture chạy UV.

## Skill: VFX_Maker (`/vfx-maker`)

Skill quy trình VFX chính của dự án (texture + particle → prefab), ở cấp project (chuyển từ user-level ngày 2026-11-03): `.claude\skills\vfx-maker\` trong project (`D:\Game_prj\VFX_LIb\.claude\skills\vfx-maker\`, version `2.3.1`). Gọi bằng `/vfx-maker`.

- Quy trình: mô tả / ảnh / JSON Shape Lab → **định hướng không gian** (bắt buộc; thiếu thông tin thì **hỏi**, không tự đoán) → kế hoạch (duyệt 1 lần) → asset → build script → build + preview → Review Lab → bàn giao.
- Định hướng không gian (`references/direction.md`):
  - ngữ cảnh: air / ground / dir;
  - mặt phẳng: Billboard / nằm đất = Billboard + Local / Stretched; **không dùng Horizontal / Vertical Billboard**;
  - camera: mặc định 3/4, nhìn xuống 40°;
  - neo, quy mô (m), di chuyển, nền.
- Asset theo thứ tự: script → Shape Lab / thư viện (có nhóm PixelFX) → ChatGPT. VFX bằng code: dùng skill `/vfx-code`.
- Chế độ B: chỉ xuất spec + prompt tiếng Anh để bàn giao, không dựng prefab.
- 2.3.0 (2026-11-03): **bỏ chế độ C (codefx)** cùng thành phần Scorch / CodeFX khỏi skill. Bản lưu 2.2.0: `Docs/VFX/_ArtDirection/_archive/vfx-maker_2.2.0_before_codefx_removal_2026-11-03/`.
  - Prefab Scorch / CodeFX trong project vẫn giữ; `MixRecipeBuild.cs` và `CodeFxComponentsBuild.cs` của project trỏ vào codefx trong bản lưu đó.
  - Cùng đợt: sửa mâu thuẫn tài liệu (Horizontal Billboard trong particles.md, bộ số thứ tự vẽ theo `ComponentKit` của project, texture comet quay đầu sang trái, luật lửa hạt đậu, Frame over Time thẳng).
- Lịch sử skill:
  - 2026-10-28: `unity-vfx-maker` đổi tên thành `vfx-maker`, gộp phần đáng giữ của `dynamic-vfx-prompt-builder` (bản Claude, đã xoá).
  - 2026-11-02: skill `/vfx-shader` đã **xoá**. Bước định hướng của nó được gộp vào `vfx-maker` mục 1a. Bản lưu: `Docs/VFX/_ArtDirection/_archive/vfx-shader_skill_2026-11-02/`.
  - Các bản sao lưu khác ở `Docs/VFX/_ArtDirection/_archive/`.
  - Bản Codex ở `C:\Users\Manh\.agents\skills\dynamic-vfx-prompt-builder` là bản độc lập, không bị đụng tới.
- Shader dùng chung của project, vẫn giữ:
  - `Docs/VFX/SHADERS.md` (kiểm tra trước khi viết shader mới);
  - `Assets/VFX/_Shared/Shaders/VfxShaderLib.cginc`;
  - noise `Assets/VFX/_Shared/Textures/Noise/`;
  - build kit `Assets/VFX/_Kit/`.
- **Thành phần chuẩn + auto mix** (mục 9; 2.2.0, art lead chốt 2026-11-03): đòn trúng / nổ thì Claude **tự mix** từ Impact / Glow / Ring / Sparks / Dust theo brief.
  - Luồng: `mix/auto_mix.py` → recipe → Unity `MixRecipeBuild` → Review Lab. Art lead yêu cầu đổi.
  - Luật: một effect chỉ một ngữ cảnh và một chớp; thứ tự vẽ theo mặt phẳng trước (bảng ở `ComponentKit`).
  - Mix Lab (web xem và tinh chỉnh): https://claude.ai/artifact/CMFUvsBJ6YeqapsMZoNwbt. Chi tiết: skill `references/mix.md`.

## Skill: vfx-code (`/vfx-code`, 2026-11-03)

VFX hoàn toàn bằng code, tổng hợp từ ~50 thư viện VFX mã nguồn mở trên GitHub (danh mục + giấy phép: `references/sources.md`). Ở `.claude\skills\vfx-code\`, version `1.2.0`.

- **Skill tách riêng hoàn toàn với `vfx-maker`** (art lead 2026-11-03): không dùng công cụ / asset / quy trình của nó. Điểm chung duy nhất: gọi **Review Lab** để review.
- Tự chứa: `lib/core.py` (Canvas, xuất sheet, `--check`) + `fxlib` (noise có chu kỳ, SDF, polar, toon, dissolve/erosion, sét, lửa) + `stylize` (minerva) + `particles` (three.quarks / Godot / Effekseer) + `fluid` (stable fluids). Builder Unity riêng: `assets/VfxCodeBuild.cs` (menu `VFX/vfx-code/Build From Json...`).
- Lệnh: `python -I D:/Game_prj/VFX_LIb/.claude/skills/vfx-code/lib/render.py <effect.py> --project . --effect <Tên> --gif --check --review` → sheet + json vào `Assets/VFX/<Tên>/Textures/`, preview + GIF + BuildReport vào `Docs/VFX/<Tên>/`, rồi dựng Review Lab.
- Luật art lead vẫn áp dụng: không gian trước (thiếu thì hỏi), không Horizontal / Vertical Billboard, khói thuỳ, vệt chém = mesh + UV, Frame over Time tuyến tính.
- 4 mẫu trong `examples/` (shockwave, spark burst, lightning loop, fluid plume), đều qua `--check`.
- **Realtime code + shader, không texture** (v1.2.0, 2026-11-09): mục 5b + `references/electric-bolt.md`. Mẫu đã duyệt: ElectricBolt (tia điện A→B), shader lưu ở `assets/shaders/` (`SH_VFX_ElectricBolt`, `SH_VFX_GlowStar`), builder `assets/ElectricBoltBuild.example.cs`.

## Skill: vfx-shader (`/vfx-shader`, tạo lại 2026-11-03)

VFX cần shader. Ở `.claude/skills/vfx-shader/`, version `1.3.0`. Gọi bằng `/vfx-shader`.

- **Bước 2b research nhanh trên mạng** (art lead 2026-11-09, v1.3.0): trước khi chọn shader, tìm 3–5 nguồn VFX tương tự, ghi "Tham khảo" vào kế hoạch (`references/web-research.md`).
- Thứ tự: dùng lại shader có sẵn → mở rộng → viết mới (nhẹ, một pass, Built-in + URP). Định hướng không gian bắt buộc (thiếu thì hỏi), kế hoạch duyệt 1 lần, prefab dựng bằng build script, Review Lab.
- **Tornado / cột gió + học từ prefab tham chiếu** (art lead 2026-11-06, v1.2.0): tornado làm lại từng lớp từ `Stupid_Tornado_Projectile` của rpg-game (`references/tornado.md`; mẫu `Assets/VFX/WindTornado/`). Brief "học theo prefab X": copy theo GUID + render + dump + đọc mesh / texture / Shader Graph trước khi dựng (`references/study-reference.md`; công cụ `scripts/copy_closure.py`, `assets/RefRender.example.cs`). Không tự làm mesh khi họ có, không bỏ lớp chỉ vì hồng.
- **Slash chỉ làm bằng bộ Coloso** (`VFXLib/ColosoShaderAdditive|Alpha|AlphaCutOut_Optimized`, art lead 2026-11-03), theo `references/coloso.md`: texture xám, màu từ ramp / Color over Lifetime, `MaskTex` = `T_VFX_Gradient_01`, stream `Custom1XYZW`.
- Mesh nhập: `Assets/VFX/_Imported/Mesh/` (55 `SM_VFX_*`). Shader nhập: `Assets/VFX/_Imported/RpgGame/` (xem `README.md` trong đó).
- Ví dụ làm xong: `Assets/VFX/Slash360/` (vệt chém 360°, hiện chỉ còn nguyên tố Đất; bản 5 nguyên tố lưu ở `_archive/Slash360_5elements_2026-11-03/`), ghi chú `Docs/VFX/Slash360/Plan.md`; `Assets/VFX/IceSpike/` (gai đâm lên: bản Băng pha lê và bản Đất đá, cùng hiệu ứng nhưng khác mesh, bố cục, timing).
- **Có khác biệt giữa các effect / biến thể, không chỉ đổi màu** (art lead 2026-11-04): khi làm effect mới hoặc biến thể (ví dụ Băng → Đất), đổi ít nhất hai trong mesh / vị trí-bố cục / timing / lớp phụ so với bản đã có. **Nhưng đúng yêu cầu: biến thể vẫn là cùng hiệu ứng; không tự biến nó thành một effect khác.** Effect khác chỉ làm khi art lead yêu cầu.
- Bản `/vfx-shader` cũ (quad + noise) đã gộp vào vfx-maker rồi xoá 2026-11-02, bản lưu ở `Docs/VFX/_ArtDirection/_archive/vfx-shader_skill_2026-11-02/`.

## Scene chung VFX_Showcase (2026-11-03)

Mọi VFX để chung một scene: `Assets/VFX/_Showcase/Scenes/VFX_Showcase.unity`. Khi chạy có giao diện (uGUI dựng bằng code, `Assets/VFX/_Showcase/Runtime/VfxShowcase.cs`) để đổi qua lại: danh sách theo nhóm bên trái, Prev / Replay / Next, Loop, Speed, 3 góc camera (Top-down 60°, 3/4 40°, Side 8°). Phím: ← → đổi VFX, Space phát lại, 1/2/3 camera, L loop, con lăn chuột zoom. **UI tự fit mọi tỉ lệ game view** (2026-11-13): Canvas `ScaleWithScreenSize` 1280×720 + `ScreenMatchMode.Expand` (vùng 1280×720 luôn nằm gọn, màn rộng hơn thì giãn thêm); nút co chữ thay vì ngắt dòng.
- **Môi trường thực tế** (2026-11-04): trời hoàng hôn, nắng ấm + bóng mềm, sương, nền đất, sàn đá tròn 16 m ở giữa, đá tảng và cột vỡ xung quanh; **không còn spawn hình tham chiếu `Reference_2m`** (art lead 2026-11-05); dựng bởi `Editor/VfxShowcaseEnvironment.cs` (Built-in, không asset ngoài).
- **VFX nằm sẵn trong Hierarchy** (2026-11-04): `VFX_Instances` chứa một prefab instance cho mỗi effect, xếp hàng cách nhau 16 m trên trục X. Kéo từng cái để sắp vị trí. **Danh sách khi chạy lấy từ Hierarchy**: xoá một cái thì mất khỏi danh sách, tắt (disable) thì ẩn, kéo thêm prefab vào `VFX_Instances` thì có thêm (nhóm "Scene", tên theo GameObject), đổi thứ tự thì đổi thứ tự; tên và nhóm của các effect do Build Scene tạo lưu ở component `VfxShowcaseTag`. Khi Play, UI chọn effect thì bật cái đó (camera bám theo vị trí của nó) và tắt các cái khác. **Build Scene giữ nguyên setup** (art lead 2026-11-05): mở scene có sẵn, giữ camera, môi trường, đèn, vị trí / xoay / override của từng instance và mọi thứ tự thêm; chỉ thêm effect trong `Included` chưa từng được đặt (nối cuối hàng). Effect đã xoá tay không bị thêm lại (nhớ ở `VfxShowcase.addedPrefabs`). Mỗi lần chạy tự lưu bản sao ở `Assets/VFX/_Showcase/Scenes/_Backup/` (giữ 5 bản). Dựng lại từ đầu chỉ bằng menu **VFX → Showcase → Rebuild Scene From Scratch** (có hỏi xác nhận).
- Tạo / cập nhật scene: menu **VFX → Showcase → Build Scene** (`VfxShowcaseBuild.cs`): chỉ gom các effect trong danh sách `Included` của `VfxShowcaseBuild.cs` (hiện: `VFX_Slash360_*`, `VFX_IceSpikeFan_*`, `VFX_HealCircle`, các effect điện, `VFX_FireballThrow`, `VFX_VioletThunder` (kèm Toxic / Gold), `VFX_VioletStorm`, `VFX_FireTornado`; các effect cũ khác chưa thử nên chưa đưa vào). Thêm effect mới thì thêm tiền tố tên prefab vào `Included`. **Thêm VFX mới thì chạy lại menu này**; build lại một VFX đã có thì không cần (instance trong scene tự cập nhật theo prefab). Thiếu prefab IceSpike thì tự build.
- **Đèn demo chỉ trong Showcase, lúc Play** (art lead 2026-11-05: "thêm vào scene showcase thôi"; không gắn vào prefab, không cần chạy menu): `Assets/VFX/_Showcase/Runtime/VfxShowcaseLights.cs` giữ bảng `Table`; khi Showcase khởi động, mỗi effect trong bảng được bật module Lights của một lớp (đèn bám theo hạt và nhịp của lớp đó, màu + đường cong cường độ theo bảng). Không sửa prefab, không lưu vào scene. Lớp đã bật Lights bằng tay trong scene thì giữ nguyên. Effect mới: thêm một dòng vào `Table`.
- Effect bay xa (projectile): đặt `focusOffset` trên `VfxShowcaseTag` (camera nhìn vào giữa đường bay) và xoay instance trong `VfxShowcaseBuild` (ví dụ FireballThrow: Y 90°, focus z 4).
- VFX mới (kể cả của `/vfx-shader`, `/vfx-maker`, `/vfx-code`) cần prefab tên `VFX_<Tên>.prefab` trong `Prefabs/` và một dòng trong `Included` để vào danh sách.

## Review Lab (web review, không cần mở Unity)

- Lệnh: `python -I D:/Game_prj/VFX_LIb/.claude/skills/vfx-maker/review-lab/build_review.py --project . [--effect Tên]` → `Docs/VFX/_Review/index.html` (1 file tự chứa).
- Gồm: timeline preview, flipbook, ảnh/GIF, so sánh A/B, ghim góp ý, nút "Xuất phản hồi" để dán vào chat.
- Gắn vào `/vfx-maker` (mục 5b). Có cấu hình `review-lab` trong `.claude/launch.json` (cổng 8776).

Trạng thái công việc VFX: đọc `Docs/VFX/_ArtDirection/PROGRESS.md` trước.
