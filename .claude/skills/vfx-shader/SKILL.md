---
name: vfx-shader
description: "VFX_Shader — làm VFX cần tới shader (technical): chọn đúng shader có sẵn trong project trước (bộ Coloso VFXLib dùng cho slash / trail / vệt trên mesh + UV, shader nhập từ rpg-game, SH_VFX_* dùng chung), cấu hình material + Custom Vertex Streams, texture lấy từ Assets/Library (slash chạy UV dùng Assets/Library/Slash), và chỉ viết hoặc mở rộng shader nhẹ cho mobile (Built-in + URP) khi chưa có cái nào đủ. Bắt đầu bằng định hướng không gian (bắt buộc, thiếu thì hỏi), kế hoạch duyệt 1 lần, prefab dựng bằng build script, tự chụp preview, Review Lab, đăng ký shader. Dùng cho effect mà hình khối / chuyển động / kết thúc do shader quyết định (slash, dissolve, vệt, lửa / khói toon, shockwave, beam, aura). Chỉ chạy khi người dùng gọi /vfx-shader."
disable-model-invocation: true
metadata:
  version: "1.3.0"
---

# VFX_Shader

Làm effect mà **shader quyết định hình, chuyển động, màu hoặc kết thúc**. Thứ tự ưu tiên khi cần shader:

1. **Dùng lại shader có sẵn** chỉ bằng material (bộ Coloso, shader nhập từ rpg-game, `SH_VFX_*` dùng chung).
2. **Mở rộng** shader do mình viết bằng keyword mới (mặc định tắt).
3. **Viết shader mới** (nhẹ, một pass, Built-in + URP) khi chưa có cái nào đủ.

Trao đổi bằng tiếng Việt; code và tên asset bằng tiếng Anh. Skill tạo ngày 2026-11-03; bản `/vfx-shader` cũ (chỉ quad + noise, đã gộp vào vfx-maker rồi xoá 2026-11-02) lưu ở `Docs/VFX/_ArtDirection/_archive/vfx-shader_skill_2026-11-02/`.

**Người dùng là art lead.** Yêu cầu hình khối / luật của họ thắng tài liệu. Luật hiện hành:
- **Slash chỉ làm bằng bộ Coloso** (art lead 2026-11-03), theo [references/coloso.md](references/coloso.md); slash = mesh + UV.
- **Texture lấy từ `Assets/Library/` trước** (art lead 2026-11-04). Thư viện đã phân loại bằng mắt:
  - cây `Assets/Library/<nhóm>/<vai trò>/`, tên `<nhóm>_<vai trò>_NNN`; **chọn theo `Docs/VFX/_Library/LIBRARY.md` (bảng thành phần → thư mục)**;
  - tên cũ và nguồn ở `Docs/VFX/_Library/library_index.csv`;
  - xem ảnh rồi chọn; chỉ bake / tạo texture mới khi Library không có hình hợp, nói lý do trong kế hoạch.
- **Texture chạy UV của slash (`_MainTex`) lấy trong `Assets/Library/Slash/Main_tex(Uvmesh)/`** (art lead 2026-11-04). Cách chọn ở [references/coloso.md](references/coloso.md) mục "Texture slash".
- Không dùng Horizontal / Vertical Billboard (nằm đất = Billboard + Render Alignment Local; đứng bay = Stretched).
- Frame over Time của flipbook phải là đường thẳng.
- Chưa "chốt" thì không đổi `vfx-maker`.

```
Mô tả → ĐỊNH HƯỚNG KHÔNG GIAN (thiếu → HỎI) → CHỌN SHADER (dùng lại / mở rộng / mới) → KẾ HOẠCH (DUYỆT 1 lần)
      → asset (texture bake / mesh) → [shader mới] → material + build script → build + preview → REVIEW LAB → đăng ký shader → bàn giao → sửa
```

## 0. Chuẩn bị project (lần đầu)

Theo [references/setup.md](references/setup.md) (build kit, thư viện hàm, noise dùng chung, sổ shader, Review Lab). Mesh và texture nhập sẵn của art lead: `Assets/VFX/_Imported/Mesh/` (55 `SM_VFX_*`), `Assets/VFX/_Imported/RpgGame/` (shader; xem `README.md` trong đó).

## 1. Nhận mô tả

Đọc mô tả, ảnh / video tham chiếu (Read), JSON Shape Lab nếu có. Đọc hết những gì đã có trước khi hỏi. **Brief nói "học theo / làm giống prefab X" (rpg-game…):** làm đủ [references/study-reference.md](references/study-reference.md) (copy bản gốc, render, dump, đọc mesh + texture + Shader Graph) trước khi lập kế hoạch; dùng mesh + shader + số của họ trước, không chỉ đọc số rồi tự dựng (art lead 2026-11-04 và 2026-11-06). Người dùng chỉ sửa một effect đã có thì nhảy tới mục 8.

## 2. Định hướng không gian — BẮT BUỘC

Đọc [references/direction.md](references/direction.md): ngữ cảnh (air / ground / dir), mặt phẳng, góc camera (mặc định 3/4 nhìn xuống 40°; art lead hay ra lệnh góc khác, ví dụ topdown 60°), neo, quy mô (m, người 2 m), di chuyển, nền, thời gian, thành phần, Art Style + màu. **Thiếu thông tin thì hỏi** (`AskUserQuestion`, ≤ 2 lượt, ≤ 4 câu mỗi lượt); không tự đoán. Đề xuất của Claude ghi là *đề xuất*.

## 2b. Research nhanh trên mạng — BẮT BUỘC (art lead 2026-11-09)

Trước khi chọn shader, tìm nhanh VFX tương tự trên mạng để biết người ta làm thế nào (lớp nào, mesh / texture gì, shader làm gì, timing). Làm theo [references/web-research.md](references/web-research.md): ~3–5 nguồn, tối đa vài phút, rồi ghi **"Tham khảo"** (nguồn → điều học được → áp dụng vào đâu) vào kế hoạch ở mục 4. Chỉ lấy ý tưởng cách làm; không copy asset có bản quyền; luật art lead vẫn thắng nguồn nghiên cứu. Bỏ qua khi: brief đã có prefab / video tham chiếu cụ thể (dùng mục 1 + study-reference), hoặc chỉ sửa effect đã có (mục 8).

## 3. Chọn shader — BẮT BUỘC, từng thành phần

1. Đọc sổ `Docs/VFX/SHADERS.md` (menu, làm được gì, thuộc tính, chi phí, "không sửa" nếu có).
2. Rà thực tế: Glob `Assets/**/*.shader` (bỏ `Library/`), đọc `Properties` + `#pragma shader_feature` của ứng viên. Sổ có thể thiếu shader mới thêm.
3. **Gai đâm lên đất (băng / đất):** làm theo [references/ground-spike.md](references/ground-spike.md).
3b. **Magic circle (vòng phép):** không viết shader; làm theo [references/magic-circle.md](references/magic-circle.md) (texture vẽ bằng script + particle, cách của vfx-maker / HealCircle).
3c. **Tornado / cột gió xoáy:** không viết shader; làm theo [references/tornado.md](references/tornado.md) (làm lại `Stupid_Tornado_Projectile` của rpg-game từng lớp: vành `fbx_fx_cylinder_03` + Shader Graph `Fx_dissolve_particle_apb`, ống, sương, vụn; art lead 2026-11-06). Mẫu: `Assets/VFX/WindTornado/`.
4. Với **mesh + UV** (slash, vệt, trail, vòng): đọc [references/coloso.md](references/coloso.md) và chọn mesh trong `_Imported/Mesh`. Render thử mesh với texture tô UV (đỏ = u, xanh lá = v) trước khi chọn: tên mesh không nói hướng UV (ví dụ `Slash_360` là vòng dây đứng, không hợp topdown; `Slash_Circle_Thin` là vành phẳng).
5. Quyết định: **Dùng lại** (chỉ đổi thuộc tính, tạo material) → **Mở rộng** (keyword mới, mặc định tắt, không đổi thuộc tính cũ; shader "không sửa" thì không mở rộng) → **Viết mới**.
6. Ghi quyết định và lý do vào cột "Shader" của bảng thành phần.

## 4. Kế hoạch — lần duyệt duy nhất

Trình bày gọn trong chat rồi hỏi duyệt (`AskUserQuestion`: "Duyệt, làm luôn" / "Sửa"):

```markdown
## VFX_<Effect> — kế hoạch v1
Không gian: <air/ground/dir> · <mặt phẳng> · camera <...> · neo <...> · <m> · nền <...> (đã chốt: ...; đề xuất: ...)
Tham khảo (mục 2b): <nguồn → học được → áp dụng>; hoặc "bỏ qua: <lý do>"
Thời lượng: <s> · Art Style: <...>

| # | Layer | Vai trò & timing | Carrier (mesh / quad) | Shader (dùng lại / mở rộng / mới) | Texture | Kết thúc |
```

Thêm: **khác với effect nào, ở điểm nào** (mesh / bố cục / timing / lớp phụ), shader mới / mở rộng (hình, chuyển động, kết thúc, thuộc tính 5–10, keyword ≤ 3, chi phí sample), ngân sách (particle, material, texture), giả định. Không tạo file trong project trước khi được duyệt (trừ setup lần đầu). Sau khi duyệt lưu `Docs/VFX/<Effect>/Plan.md` (đủ bảng có ID: Review Lab đọc nó).

## 5. Asset và shader

- **Texture hình:** lấy từ `Assets/Library/<nhóm>/<vai trò>/` trước, tra `Docs/VFX/_Library/LIBRARY.md` (bảng thành phần → thư mục) (slash: `Slash/Main_tex(Uvmesh)`; mask: `mask/gradient`; dissolve: `noise/cloud|cell`; vòng: `ring/` + `impact/radial_ring`; vệt: `trail/`). Chỉ bake bằng script (ví dụ `scripts/bake_slash_textures.py`) hoặc Shape Lab khi Library không có hình hợp. Ramp màu cho slash vẫn có thể bake bằng script. **Giữ nguyên khung UV, tỉ lệ gốc** với texture slash. Kiểm tra bằng cách đọc ảnh, không đoán. Noise dùng chung: `Assets/VFX/_Shared/Textures/Noise/` (tạo bằng `scripts/make_noise.py`).
- **Shader mới:** copy `assets/SH_VFX_FX.template.shader` → `Assets/VFX/_Shared/Shaders/SH_VFX_<Name>.shader`, dựng hình theo [references/recipes.md](references/recipes.md), giữ đúng [references/mobile-rules.md](references/mobile-rules.md) (một pass unlit, không include URP, ≤ 3 sample, không vòng lặp, `// Cost:` ở header). Viết chung chung, tham số hoá, không hardcode timing của một effect.
- **Mesh:** ưu tiên `_Imported/Mesh`; mesh tạo bằng code chỉ khi thư viện không có.

## 6. Material + build script

- Copy `assets/ShaderFxBuild.template.cs` (quad) hoặc `assets/ColosoMeshFxBuild.example.cs` (mesh + Coloso, ví dụ Slash360) → `Assets/VFX/<Effect>/Editor/<Effect>Build.cs`. Prefab dựng từ script, không chỉnh tay; sửa script rồi build lại. Dùng `VfxBuildKit` (`Assets/VFX/_Kit/`).
- Mỗi thành phần = một layer đúng ID. Thuộc tính material đặt trong script. Mesh renderer thì `SetActiveVertexStreams` đúng với shader (Coloso: `Position, Color, UV, Custom1XYZW`).
- **ĐỌC HƯỚNG MESH trước khi đặt Start Rotation / alignment — mọi VFX dùng mesh** (art lead 2026-11-06, lỗi FireTornado: đặt Whips nghiêng ±11° vì giả định trục mesh là Y, nhưng mesh phải xoay X 90° mới đúng hướng). Trục của mesh nhập **không mặc định là Y**: `fbx_fx_cylinder_03`, `Tornado_vertical`, `tornado_mesh` đều có trục vành / phễu trên **Z** trong Unity. Làm: (1) đọc `mesh.bounds` + trục xoay trong build script (hàm `Describe()` ở `assets/TornadoFireBuild.example.cs` log ra "revolution axis ~ Z"); (2) nếu bản tham chiếu đặt Start Rotation X ≈ 90° / 270° cho mesh đó thì **đó là tín hiệu trục khác Y**, đừng bỏ qua con số; (3) tính hướng mong muốn (vòng nằm ngang quanh cột = trục vành thẳng đứng = X 90°); (4) xem preview đủ góc rồi mới báo xong. Chi tiết: [references/tornado.md](references/tornado.md) mục "Hướng mesh".
- **Dựng đúng không gian đã chốt:** size theo mét, renderer mode theo mặt phẳng, simulation space theo neo, `cameraPos`/`lookAt` của `Finish()` khớp camera game (ví dụ topdown 60°: `lookAt + d·(0, sin60°, −cos60°)`).
- **Không `ImportTexture` lên texture dùng chung** (`Assets/Library/`, `_Shared/Textures/Noise/` …): chỉ `LoadAssetAtPath`. Cần setting khác thì copy ảnh (không copy `.meta`) sang `Assets/VFX/<Effect>/Textures/`. Import đổi wrap / sRGB của chúng sẽ hỏng các effect khác.
- Tên: `VFX_<Effect>`, `M_<Effect>_<Layer>`, `SH_VFX_<Name>`, `T_<Effect>_<Tên>`.

## 7. Build và tự kiểm tra

- Unity đang mở project (kiểm tra `Temp/UnityLockfile` / process) → nhờ người dùng chọn menu **VFX → <Effect> → Build**. Với Unity đang mở, có thể **dựng thử ở project tạm** (thư mục scratchpad: copy `_Kit`, effect, shader, mesh, noise + manifest chỉ có `com.unity.modules.*` + URP nếu cần; `-batchmode`, không `-nographics`) để xem preview trước.
- Đọc `Docs/VFX/<Effect>/BuildReport.txt`, **xem** `Preview_sheet.png`; đối chiếu bảng thành phần (đủ lớp, đúng mặt phẳng / quy mô / timing / góc camera). Phóng to khung để tìm lỗi viền (răng cưa, lớp lòi ra ngoài), cứng, cắt sắc.
- Kiểm tra shader biên dịch: `ShaderUtil.GetShaderMessages` trong script `-executeMethod` (đối chứng bằng cách làm hỏng một shader xem có báo lỗi không); `-batchmode -quit` một mình không báo lỗi shader.
- Tự sửa tối đa 2 vòng; không báo xong khi chưa xem preview. Compile được ≠ đạt mỹ thuật.

## 7b. Review Lab

```
python -I "D:/Game_prj/VFX_LIb/.claude/skills/vfx-maker/review-lab/build_review.py" --project . [--effect <Effect>]
```
Ghi `Docs/VFX/_Review/index.html` (một file; bỏ `--effect` thì gom tất cả, rất nặng). Cho art lead: timeline preview, so sánh A/B, ghim góp ý, **Xuất phản hồi**. Chạy lại sau mỗi lần build.

## 8. Đăng ký, bàn giao, sửa

- **Cập nhật `Docs/VFX/SHADERS.md`** khi viết mới / mở rộng (menu, file, làm được gì, thuộc tính + keyword chính, chi phí, effect đang dùng); dùng lại thì thêm tên effect vào cột "Đang dùng".
- Bàn giao: prefab, scene demo, ảnh preview, link Review Lab; shader dùng lại / mở rộng / mới; chi phí; **phần chưa kiểm chứng** (chưa xem chuyển động thật, chưa đo máy thật).
- **Sửa theo phản hồi:** mỗi ghim Review Lab gán vào ID thành phần theo timing + vị trí; ghim không gán được thì hỏi, không đoán. Đổi màu / kích thước / timing chỉ sửa material trong build script. Sửa shader dùng chung thì kiểm tra và build lại effect khác trong cột "Đang dùng".
- **Scene chung:** mọi VFX nằm trong `Assets/VFX/_Showcase/Scenes/VFX_Showcase.unity` (có UI đổi qua lại). Khi thêm effect mới, nhắc người dùng chạy **VFX → Showcase → Build Scene**: lệnh này chỉ thêm effect chưa có và giữ nguyên setup art lead đã sắp (camera, môi trường, vị trí); không dùng **Rebuild Scene From Scratch** nếu art lead không yêu cầu. Build lại effect đã có thì scene tự cập nhật. Đèn demo chỉ có trong Showcase lúc Play (bảng `Table` của `_Showcase/Runtime/VfxShowcaseLights.cs`), không gắn đèn vào prefab: effect mới thêm một dòng vào bảng đó. Scene chỉ liệt kê effect trong `Included` của `VfxShowcaseBuild.cs`: thêm tiền tố `VFX_<Tên>_` vào đó khi effect mới đã được art lead duyệt.
- Phản hồi mơ hồ ("đang có lỗi visual") không kèm ảnh: tìm lỗi ở preview phóng to, sửa những gì thấy được, nói rõ phần chưa chắc và xin ảnh / mô tả.

## Mặc định của art lead (áp dụng nếu brief không nói khác)
- **Mọi Particle System đều để Scaling Mode = Hierarchy** (art lead 2026-11-04). Nếu mẫu dùng Local mà dưới nhóm có scale ≠ 1 thì bù lại size cho giống kích thước thật. `VfxBuildKit.Validate` báo lỗi nếu có layer khác Hierarchy.
- **Cấu trúc prefab chuẩn: `Tên VFX (các thành phần)`**, không có nhóm trung gian (không `Scale05`…) và không scale trên transform nào: nếu mẫu có scale ở root/nhóm thì nhân vào size của từng layer. Root cũng là Particle System:
  **Root của prefab cũng phải là một Particle System** (art lead 2026-11-04): chọn một layer làm root (LightningStrike: flare), các layer khác là con. Dùng `VfxBuildKit.ParticleOn(rootGameObject, ...)`; `Validate` cảnh báo nếu root không có ParticleSystem. Các effect cũ (IceSpike, Slash360, HealCircle, Mixes) chưa theo luật này.

- **Khói:** texture `Assets/VFX/fx_t_smoke_02.png` + shader mobile mặc định của Unity (`Mobile/Particles/Alpha Blended`; `VfxBuildKit.Material` tự chọn, URP đổi sang URP Particles Unlit). Tô màu bằng Start Color. Không dùng thành phần Dust chuẩn / khói toon cho effect mới (art lead 2026-11-03).
- **Slash:** chỉ bộ Coloso ([references/coloso.md](references/coloso.md)); `_MainTex` chạy UV lấy từ `Assets/Library/Slash/`.
- **Magic circle:** cách vfx-maker / HealCircle ([references/magic-circle.md](references/magic-circle.md)).
- **Tornado / cột gió:** [references/tornado.md](references/tornado.md); học prefab tham chiếu theo [references/study-reference.md](references/study-reference.md).
- **Gai băng / đất đâm lên:** [references/ground-spike.md](references/ground-spike.md) (5–9 khối chính, sát nhau, nghiêng ngẫu nhiên, mỗi khối một tuổi thọ).
- **Tạo hình trước khi làm** (art lead 2026-11-10): trước bước 2 (và trước 2b), mở `Docs/VFX/_Anatomy/<loại>.md` + `materials.md`; chưa có hoặc chưa hiểu thì research rồi **lưu file mới** theo `_Anatomy/README.md`. Chép "Bất biến" vào kế hoạch; sau build đối chiếu preview với nó. Biến thể phải giữ hình xương sống của effect gốc.
- **Có khác biệt giữa các effect / biến thể, không chỉ đổi màu** (art lead 2026-11-04). Khi làm effect mới hoặc **biến thể** của effect đã có (ví dụ Băng → Đất), **đổi ít nhất hai trong bốn thứ**: **mesh** (mesh khác trong thư viện), **bố cục / vị trí** (cụm tròn ↔ cung ↔ quạt ↔ hàng ↔ rải; hướng, độ cao, số khối), **timing** (nhịp trồi / giữ / tan, thứ tự xuất hiện và biến mất, tuổi thọ), **lớp phụ** (khói, mảnh vỡ, vết nứt, impact ở đâu, lúc nào). **Nhưng biến thể vẫn là cùng hiệu ứng: đừng tự biến nó thành một effect khác** (art lead: "nếu cần fx khác tôi sẽ yêu cầu"). Đừng tái dùng nguyên builder và chỉ đổi bảng màu. Trong kế hoạch thêm dòng **"Khác với bản nào, ở điểm nào"** (mesh / bố cục / timing / lớp phụ).
- Số khối chính của cụm (băng, đá…) giữ ít (5–9) và sát nhau; hướng mỗi khối ngẫu nhiên, không thẳng đứng đều (art lead, IceSpikeFan).

## Tài liệu

| File | Nội dung |
|---|---|
| [references/coloso.md](references/coloso.md) | Bộ Coloso: cách dùng chuẩn, Custom Streams, công thức slash quanh mesh vòng, lỗi thường gặp |
| [references/magic-circle.md](references/magic-circle.md) | Vòng phép: dùng cách vfx-maker / HealCircle, không viết shader |
| [references/ground-spike.md](references/ground-spike.md) | Gai băng / đất đâm lên đất: lớp, số khối, hướng, tuổi thọ, bảng màu Băng ↔ Đất, ghi chú theo nguyên tố, bài học quy trình |
| [references/tornado.md](references/tornado.md) | Tornado / cột gió: cách bản gốc `Stupid_Tornado_Projectile` hoạt động (mesh, Shader Graph, sheet đóng gói kênh), bảng lớp + số, khác bản gốc, biến thể, lỗi đã gặp |
| [references/study-reference.md](references/study-reference.md) | Học từ prefab tham chiếu đủ bước: copy theo GUID, render + dump, Shader Graph hồng, đọc mesh / texture, dựng |
| [references/web-research.md](references/web-research.md) | Research nhanh trên mạng trước khi chọn shader (bước 2b) |
| [references/direction.md](references/direction.md) | Định hướng không gian |
| [references/mobile-rules.md](references/mobile-rules.md) | Quy tắc shader mobile (cho shader mới viết) |
| [references/recipes.md](references/recipes.md) | Công thức SDF / kết thúc cho shader mới |
| [references/setup.md](references/setup.md) | Chuẩn bị project |
| `assets/` | Template shader, build script quad, ví dụ mesh + Coloso (Slash360), ví dụ vòng phép (HealCircle), ví dụ gai đất / băng (`GroundSpikeBuild.example.cs`), ví dụ tornado (`TornadoBuild.example.cs` vành + Graph, `TornadoFireBuild.example.cs` phễu + Thrust), công cụ render + dump prefab tham chiếu (`RefRender.example.cs`), `VfxShaderLib.cginc` |
| `scripts/` | `make_noise.py`, `bake_slash_textures.py`, `heal_circle_textures.py`, `copy_closure.py` (copy prefab + phụ thuộc theo GUID) |
