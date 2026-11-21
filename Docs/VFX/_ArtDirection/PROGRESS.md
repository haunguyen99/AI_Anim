# VFX_LIb – Tiến trình (cập nhật 2026-11-06)

> ## ĐIỂM BẮT ĐẦU CHO PHIÊN MỚI (cập nhật 2026-11-06)
> Đọc cùng `CLAUDE.md` + `MAP.md`. Các khối bên dưới là lịch sử theo ngày; khi mâu thuẫn thì khối này và `CLAUDE.md` thắng.
>
> **Skill hiện có (3, ở `.claude/skills/`):**
> - `/vfx-maker` **2.3.1**: texture + particle → prefab. Định hướng không gian bắt buộc (§1a), auto mix thành phần chuẩn (§9). **Đã bỏ chế độ C (codefx)** từ 2.3.0 (2026-11-03).
> - `/vfx-code` **1.1.1**: VFX hoàn toàn bằng code (~50 thư viện GitHub), tách hẳn khỏi vfx-maker; chung duy nhất là Review Lab.
> - `/vfx-shader` **1.2.0** (tạo lại 2026-11-03; 2026-11-06 thêm tornado + quy trình học prefab tham chiếu): VFX cần shader; dùng lại shader có sẵn trước. Slash chỉ dùng bộ Coloso.
> - Luật art lead: `.claude/rules/vfx-art-lead.md`. Texture lấy từ `Assets/Library/` trước.
>
> **Scene chung `Assets/VFX/_Showcase/Scenes/VFX_Showcase.unity`** (menu VFX → Showcase → Build Scene; chỉ thêm effect trong `Included`, giữ nguyên setup của art lead). Danh sách khi chạy lấy từ Hierarchy (`VFX_Instances`). Đèn demo chỉ lúc Play (`VfxShowcaseLights.cs`).
>
> **Effect đang có trong Showcase:**
> - `Slash360_Earth`: vệt chém 360° (Coloso).
> - `IceSpikeFan` Băng (pha lê) + Đất (đá): chờ art lead duyệt.
> - `HealCircle` v2.
> - 4 effect điện: `LightningStrike`, `ThunderSpear`, `LightningTrail`, `AuraGauntlet` (học từ rpg-game; số liệu: `vfx-shader/references/thunder-core.md`, `lightning-set.md`).
> - `FireballThrow` (2026-11-05): cầu lửa ném vòng cung 8 m / 0,8 s rồi nổ tại chân mục tiêu; một prefab tự chạy (sub-emitter Death). Plan: `Docs/VFX/FireballThrow/Plan.md`.
> - `VioletThunder` (2026-11-05): sét tím-hồng đánh xuống đất, tích điện 0,4 s → tia toon + chớp + impact đất + dòng điện bò ~1,4 s. Plan: `Docs/VFX/VioletThunder/Plan.md`.
> - `ElectricBolt` (2026-11-09, art lead "ổn đó"): tia điện nối A→B, tay → ngực 8 m, một phát ~0,45 s, xanh-trắng toon, **hoàn toàn code + shader, không texture** (shader mới `VFX/FX/Electric Bolt` + `VFX/FX/Glow Star`, dùng lại `VFX/FX/Spark`). Đã vào `Included` (Showcase: cao 1,3 m, xoay Y 90°, focus z 4) và bảng đèn demo; cần bấm **VFX → Showcase → Build Scene**. Research: `Docs/VFX/ElectricBolt/Research.md`, Plan: `Docs/VFX/ElectricBolt/Plan.md`.
>
> - `Disintegrate` (2026-11-18, order Cường): tan biến bản **HTML canvas + WebAudio** (`Docs/VFX/Disintegrate/index.html`), chưa có prefab Unity, chưa vào `Included`; chờ Cường + art lead duyệt. Plan: `Docs/VFX/Disintegrate/Plan.md`.
>
> - `WindTornado` v3 (2026-11-06): lốc xoáy gió 3,6 m làm lại từng lớp từ `Stupid_Tornado_Projectile` của rpg-game (vành gió + Shader Graph + ống + sương). Prefab trong project chính cần bấm **VFX → WindTornado → Build** (Unity đang mở lúc làm). Chờ art lead duyệt, chưa vào `Included`. Plan: `Docs/VFX/WindTornado/Plan.md`.
>
> - `FireTornado` (2026-11-06): lốc lửa 4,5 m, tornado thứ hai (khác WindTornado cả mesh / bố cục / timing / lớp phụ), làm theo quy trình tornado của skill, không cần prefab tham chiếu. **Đã thêm vào `Included`** và bảng đèn demo; cần bấm **VFX → FireTornado → Build** rồi **VFX → Showcase → Build Scene** (Unity đang mở lúc làm). Plan: `Docs/VFX/FireTornado/Plan.md`.
>
> **Đã làm nhưng chưa vào `Included` / cần làm lại:**
> - `GroundBlast` v5c: khói `VFX/FX/Erode Sphere` (số lấy ở `GroundBlastBuild.cs` mục 3b). **Chưa build lại với shader v3.** Mask `_TEMP` từ video, không ship.
> - `MushroomBlast` v2: nổ nấm ~3 m, chưa vào `Included`.
> - Thành phần mix `Assets/VFX/_Components/` (Impact / Glow / Ring / Sparks / Dust) còn giữ; Mix cũ và Scorch / CodeFX đã xoá hoặc bỏ.
>
> **Git:** nhánh `master` chỉ ở máy này (GitHub là `main`). Chỉ commit kiến thức + skill + `.md`; Task Scheduler `VFX_LIb Auto Commit` chạy 17:30 hằng ngày. Asset / code Assets không lên git.
>
> **Còn mở:**
> - Duyệt IceSpikeFan Băng / Đất, FireballThrow, VioletThunder; quyết định đưa GroundBlast / MushroomBlast vào `Included`.
> - Cách làm từng nguyên tố (Lửa, Băng, Sét, Độc, Đất): art lead sẽ cập nhật vào skill (`references/elements.md` chưa tạo).
> - Debris (thành phần tuỳ chọn), hit-stop / rung camera trong recipe, biến thể Dir (Scorch đã bỏ nên có thể không còn cần).
> - Quy trình "shader → bake sheet" vẫn tạm dừng, chưa chốt.

> ## Khối lịch sử: điểm bắt đầu lưu 2026-11-03 (trước khi reset workspace; một số mục đã lỗi thời)
> **Skill lúc đó:** `/vfx-maker` **2.2.0** là skill VFX duy nhất (`/vfx-shader` đã xoá).
> - §1a: định hướng không gian là bắt buộc; thiếu thông tin thì hỏi.
> - §9 Chế độ C: VFX bằng code (codefx). *(đã bỏ ở 2.3.0)*
> - §10: **auto mix từ thành phần chuẩn**, mặc định cho đòn trúng / nổ.
> - Chi tiết: skill `references/mix.md`, `references/components/STANDARD.md`.
>
> **Đã xong (2026-11-02 → 11-03):**
> - **Bộ thành phần Impact** (`Assets/VFX/_Components/`):
>   - Impact (chớp), Glow (A Soft), Ring (B sóng xung kích), Sparks (A Streak + Ember);
>   - Dust (A Toon puff, kèm 2 bản Fire và FireSmoke có lớp sáng Add);
>   - Scorch (C cháy + nứt, làm bằng codefx);
>   - CodeFX: 2 mẫu.
> - **Luật chung đã chốt:**
>   - một effect chỉ một ngữ cảnh và một chớp va chạm;
>   - thứ tự vẽ theo mặt phẳng trước, rồi tới độ sáng, không trùng số (bảng ở `ComponentKit`);
>   - Frame over Time dùng `LinearFrames`;
>   - không dùng Horizontal / Vertical Billboard;
>   - khói lấy hình dáng của dự án (thân + thuỳ bám sát, không cắt đáy).
> - **Mix:**
>   - `auto_mix.py`: brief → recipe, có lý do từng lớp;
>   - `MixRecipeBuild` dựng prefab; thành phần codefx tự render lại theo bảng màu;
>   - Mix Lab v2 (web): https://claude.ai/artifact/CMFUvsBJ6YeqapsMZoNwbt. Dữ liệu chụp bằng `MixCapture`, mỗi `sortingOrder` một sheet.
>   - Mix đã dựng: FireHit_Ground, IceHit_Ground, IceSlam_Ground, ArcaneHit_Air (`Assets/VFX/Mixes/`, recipe ở `Docs/VFX/_Recipes/`).
> - **PixelFX:** 187 effect trong Shape Lab (v19). Phân tích ở `components/PIXELFX_ANALYSIS.md`.
> - **Link:**
>   - Review Lab: https://claude.ai/artifact/DKQDnM9vtH8iNXaLUkURoN (v33)
>   - Shape Lab: https://claude.ai/artifact/BAbVif8XRDWGL2Gt7Xkk9F (v19)
>
> **Còn mở / có thể làm tiếp:**
> - Debris (thành phần tuỳ chọn).
> - Muội than của Scorch có đổi theo ô Bụi của nguyên tố không (đang giữ nâu đất; chưa trả lời).
> - Hit-stop / rung camera trong recipe (đề xuất A2 của PIXELFX_ANALYSIS).
> - Biến thể Dir cho Scorch.
> - Câu hỏi còn mở trong spec 01–06.
> - Sau khi thêm hoặc sửa thành phần: build lại → `MixCapture` → dựng lại mix → đăng Review Lab + Mix Lab (mỗi lần ≤ ~35 file).

> **2026-11-02: gom asset rpg-game vào thư viện (bản thử, chờ art lead đánh giá).**
> - Kiểm kê: `library_inventory_rpg-game.md` + `.csv` (940 texture, ~620 prefab, 39 shader, ~130 mesh; đã có / chưa có).
> - Shape Lab v16: thư viện 73 → **335 shape**, thêm 5 vai trò Glow / Ring / Slash / Spark / Trail. Ảnh gộp thành 34 atlas (`shape_library/_atlas/`) để vượt giới hạn 511 file của artifact. Bản trước khi đổi: `_archive/shape_lab_2026-11-02/`.
> - Noise / gradient / mask (107 file) copy vào `Assets/VFX/_Shared/Textures/RpgLib/`. Prefab / shader / mesh chỉ ghi chỉ mục trong `references/library.md`.
> - Còn chờ art lead: phân loại có hợp lý không, shape nào loại bỏ, có copy shader/mesh không.
> - Shape Lab v17: art lead tự **xoá / chuyển nhóm** shape có sẵn ngay trong Thư viện (nút trên thẻ + "Chọn nhiều"). Chỉnh sửa lưu online (db `libEdits`). Khi art lead báo "áp dụng chỉnh sửa": đọc `libEdits` → `shape_library.py apply-edits` → xuất bản lại → xoá các bản ghi đã áp dụng.

> **Hướng mới 2026-10-31: làm VFX theo thành phần.**
> - Làm từng thành phần nhỏ, chuẩn hoá, rồi dùng tool mix (web + Unity) ghép lại.
> - Kỹ thuật dùng cả particle và shader. Bắt đầu với Impact chung.
> - Bản chuẩn nháp: `components/STANDARD.md`, đang chờ art lead duyệt.
> - Review Lab online: https://claude.ai/artifact/DKQDnM9vtH8iNXaLUkURoN
> - Thành phần 01 Impact: spec `components/01_Impact.md`. Đã dựng thử 3 prefab Air / Dir / Ground ở `Assets/VFX/_Components/Impact/`.
>   - Build: `VfxEffects.ImpactComponentsBuild.BuildBatch` (batchmode).
>   - Preview ở `Docs/VFX/_Components/Impact/<ID>/`. Chờ art lead review.
> - Thành phần 02 Glow: spec `components/02_Glow.md`, kiểu A Soft. Đã dựng 3 prefab ở `Assets/VFX/_Components/Glow/`.
>   - Build: `GlowComponentsBuild.BuildBatch`.
>   - Có `Preview_combo` ghép cùng Impact. Chờ review.
> - Thành phần 03 Ring: kiểu B sóng xung kích, flipbook 4×2. Đã dựng 3 prefab ở `Assets/VFX/_Components/Ring/` (`RingComponentsBuild.BuildBatch`).
>   - Dir nghiêng 50° để không bị nhìn từ cạnh. Chờ review.
> - Thành phần 04 Sparks (2026-11-02): kiểu A Streak + lớp phụ Ember. Đã dựng 3 prefab ở `Assets/VFX/_Components/Sparks/` (`SparksComponentsBuild.BuildBatch`). Texture sinh bằng `components/scripts/spark_sheet.py`. Chờ review.
>   - Shader cũ `VFX/FX/Spark` vẽ đầu tia ở +X (mép phải), có thể ngược với hướng bay. Chưa sửa, cần kiểm tra riêng.
>   - Đã sửa theo góp ý: pivot (0,1,0) để tia bắt đầu từ gốc; size lệch rõ (0.05–0.13 m + Size by Speed).
> - Thành phần 05 Dust (2026-11-02): kiểu A Toon puff (sheet 4×4 trung tính từ SmokeStylized), Alpha, Sorting −1, ô màu Dust `#CDBBA6`. Đã dựng 3 prefab ở `Assets/VFX/_Components/Dust/` (`DustComponentsBuild.BuildBatch`). Chờ review.
> - Dust có thêm 2 biến thể chuẩn (2026-11-02, art lead chốt): `DST_Fire_Ground_01` và `DST_FireSmoke_Ground_01`. Cùng hình, chỉ đổi màu, cộng lớp Glow Additive trùng khít (`AddGlow`).
> - Thành phần 06 Scorch (2026-11-02): kiểu C Burn + Cracks, làm bằng codefx (`components/codefx/scorch.py`). Đã dựng `CMP_SCR_Ground_01` ở `Assets/VFX/_Components/Scorch/` (`ScorchComponentsBuild.BuildBatch`). Chờ review.
> - **Sửa chung (2026-11-02):** Frame over Time của mọi flipbook thành phần giờ là đường thẳng (`ComponentKit.LinearFrames`). Đường cong cũ có tangent 0 nên flipbook khựng ở đầu (Scorch trễ ~0.4 s). Đã build lại Impact, Ring, Dust, CodeFX, Scorch.
> - **Mix Lab v1 (2026-11-02):** ghép thành phần trên web → `recipe.json` → Unity `MixRecipeBuild` dựng prefab.
>   - Online: https://claude.ai/artifact/CMFUvsBJ6YeqapsMZoNwbt · local `tools/mix_lab/` (README ở đó).
>   - Dữ liệu web chụp bằng `MixCapture`. Recipe để ở `Docs/VFX/_Recipes/`.
>   - Đã thử trọn vòng: `VFX_FireHit_Ground` và `VFX_IceHit_Ground` (`Assets/VFX/Mixes/`), có trên Review Lab.
>   - Giới hạn: màu thành phần codefx (Scorch, CodeFX) nằm trong texture nên palette không đổi được.
> - **Auto mix (2026-11-02, art lead):** Claude tự mix theo thông tin ban đầu (`tools/mix_lab/auto_mix.py`, brief → recipe có lý do từng lựa chọn → Unity). Art lead yêu cầu đổi nếu có vấn đề. Đã thử IceSlam_Ground và ArcaneHit_Air.
>   - Mix Lab v2: giao diện thân thiện hơn (tên tiếng Việt, lọc ngữ cảnh, kéo thả, thanh kéo có giải thích, mẫu nhanh, phím tắt). Dùng để xem và tinh chỉnh.
> - **Sửa theo góp ý mix (2026-11-03):**
>   - Thứ tự vẽ xếp theo mặt phẳng trước rồi tới độ sáng, không trùng số (bảng ở `ComponentKit` và STANDARD). Lớp nằm đất < khói < sáng < tia < chớp.
>   - Timeline Mix Lab xếp lớp trước mặt lên trên cùng.
>   - **Một effect = một ngữ cảnh + một chớp va chạm.** Lỗi art lead chỉ ra: một effect có 2 chớp khác hướng (Ground + Dir). Mix Lab giờ chặn và cảnh báo; tên lớp trên timeline có nhãn ngữ cảnh.
>   - Lúc đầu tôi hiểu nhầm, đã đổi texture Flat của Impact Ground. Đã hoàn lại `T_IMP_GroundRing`; `T_IMP_GroundBurst` chỉ để trong thư viện.
> - **Giới hạn màu đã sửa (2026-11-03):** thành phần codefx (Scorch, CodeFX) đổi màu theo palette của recipe.
>   - `MixRecipeBuild` gọi `codefx/render.py --like` để render lại sheet, cache ở `Assets/VFX/Mixes/_Palettes/`.
>   - Muội than vẫn giữ nâu đất.
>   - Auto mix không còn bỏ vết cháy với nguyên tố khác lửa. Đã thử IceHit, IceSlam.
> - Còn lại: (Debris, tuỳ chọn) → tích hợp thành phần + Mix Lab + auto mix vào skill (khi art lead chốt).
> - **Skill (2026-11-02):** xoá `/vfx-shader` (bản lưu `_archive/vfx-shader_skill_2026-11-02/`). Bước định hướng không gian gộp vào `/vfx-maker` mục 1a (`references/direction.md`, bắt buộc, thiếu thì hỏi). Thành phần chuẩn hoá **chưa** vào skill: tích hợp khi đi hết các thành phần.
> - **PixelFX (2026-11-02):** nhập 187 effect pixel art từ [patch-gg/pixelfx](https://github.com/patch-gg/pixelfx) (MIT) vào Shape Lab, nhóm **PixelFX** (Shape Lab v19, thư viện 522 shape).
>   - Sheet màu 16 frame + license + script nhập ở `tools/pixelfx/` (xem README ở đó).
>   - Phân tích cách họ làm VFX bằng code: `components/PIXELFX_ANALYSIS.md`.
> - **codefx (2026-11-02), nháp:** bộ công cụ làm VFX hoàn toàn bằng code (Python, toon), học phương pháp pixelfx. Dùng khi thư viện shape không đạt.
>   - Ở `Docs/VFX/_ArtDirection/codefx/` (xem README).
>   - 2 effect mẫu đã build vào Unity: `IMP_Code_Air_01`, `DST_Code_Ground_01` (`CodeFxComponentsBuild.BuildBatch`), đã có trên Review Lab.
>   - **Đã đưa vào `/vfx-maker` 2.1.0 thành Chế độ C** (art lead, 2026-11-02). Công cụ ở `D:/Game_prj/VFX_LIb/Docs/VFX/_ArtDirection/_archive/vfx-maker_2.2.0_before_codefx_removal_2026-11-03/codefx/`; thư mục `_ArtDirection/codefx/` chỉ còn README chỉ đường.
>   - Luật art lead (2026-11-02): khói code lấy **hình dáng** theo cách của dự án (thân + thuỳ bám sát, không cắt đáy), tô/tan kiểu pixelfx, mép tan mềm. **2026-11-03: bỏ cách tô từng quả cầu kiểu pixelfx** (cứng như bóng nhựa), thay bằng mesh 3D (Blender metaball, chạy nền) + noise dissolve (theo TOTK 4.5–6.0 s). **Phần tan art lead duyệt 2026-11-03.** Đưa thẳng vào Unity dạng **shader realtime, không bake**: `CMP_SMK_Mesh_Ground_01` (shader `VFX/FX/Smoke Mesh`, build `VFX/Components/CodeFX - Build Smoke Mesh (realtime)`, mesh `Docs/VFX/SmokeMesh/mesh/`). Art lead 2026-11-03: **bỏ toàn bộ phần màu lửa** → shader chỉ còn khói 2 tông + dissolve; Custom Data chỉ có Dissolve. texture `DST_Code_Ground_01` trong Unity vẫn là bản cũ, cần dựng lại. **Mọi VFX code phải xác định không gian trước, thiếu thông tin thì hỏi** (`META.space` bắt buộc, `render.py` chặn nếu thiếu).
> - Hàm dùng chung cho mọi thành phần: `Assets/VFX/_Components/_Kit/Editor/ComponentKit.cs`.

> **Trạng thái cuối phiên 2026-10-28:**
> - **Skill:** còn 2 skill.
>   - `/vfx-maker` v2.0.0: texture + particle; đã gộp prompt-builder vào.
>   - `/vfx-shader` v1.1.0: chỉ shader. Có bước định hướng (không gian hoạt động, thành phần) và Review Lab.
>   - Cả hai dùng chung Review Lab (`Docs/VFX/_Review/`, cổng 8776).
> - **Effect làm bằng `/vfx-shader`** (các phiên khác): Meteor, FireballImpact. Shader dùng chung `VFX/FX/Meteor`, `Blast`, `Smoke`, `Spark` đã ghi trong `Docs/VFX/SHADERS.md`.
> - **Shape Lab** ([link](https://claude.ai/artifact/BAbVif8XRDWGL2Gt7Xkk9F), v15) đã có thêm:
>   - Pen chỉnh lại được bằng Di chuyển, Zoom;
>   - tan theo độ dày và theo độ sáng;
>   - đổi tên file xuất;
>   - nhóm Sáng tối kiểu toon (theo ánh sáng / noise).
>   - Thư viện: Lửa 37, Khói 25, Impact 11. Đang chờ art lead gửi texture các nguyên tố khác.
> - **Quy trình shader → bake sheet:** vẫn tạm dừng, chưa chốt.
> - **Bước tiếp theo có thể làm:**
>   - chạy `/vfx-shader` từ đầu trên một effect mới để thử bước định hướng;
>   - thêm lớp "khối bên trong" cho Sáng tối của Shape Lab.

File này là điểm bắt đầu cho phiên làm việc mới. Chi tiết từng vòng góp ý nằm ở `fire_WIP.md` (cùng thư mục).

## Quy tắc làm việc với art lead
- Người dùng là art lead. Yêu cầu hình khối của họ ưu tiên hơn nghiên cứu hay thư viện.
- Bản nháp lưu ở `Docs/VFX/_ArtDirection/`. **Chỉ đưa vào skill khi art lead nói "chốt"**, không tích hợp dần.
- Hai kiểu effect: (1) một ảnh để particle random hạt, (2) texture sheet chạy frame by frame.
- Bake sheet: **loop = 8 frame (4x2)**, **không loop = 16 frame (4x4)**.
- Hỏi trước khi sửa hoặc dán Instructions vào Project ChatGPT "Texture_Maker".
- **VFX slash (2026-11-02):** làm bằng mesh + texture slash chạy UV (UV scroll trên mesh cung/vệt chém). Nhóm Slash trong Shape Lab dùng cho mục đích này. Chưa đưa vào skill (chờ "chốt").
  - Shape Lab v18: nhóm Slash và Trail giữ nguyên khung + tỉ lệ UV gốc (không cắt, không chừa lề). Mở vào Tự vẽ đúng vị trí; Xuất PNG/sheet ra đúng tỉ lệ (ô "Giữ khung UV" ở phần Xuất file).
- Không đụng vào `Assets/VFX/FireballLoop/` và `Assets/VFX/Shaders/VFX_ArrowGlow.shader` (của phiên khác).

## Skill
- **`vfx-maker` (tên hiển thị VFX_Maker)** là skill VFX texture + particle. Nằm ở user-level `D:/Game_prj/VFX_LIb/.claude/skills/vfx-maker/`, version 2.0.0, gọi bằng `/vfx-maker`.
  - Quy trình VFX → prefab, một lần duyệt, đặt tên có hệ thống.
  - Thứ tự lấy texture: script `make_texture.py` → Shape Lab / thư viện Duong → thư viện `animlibrary` → ChatGPT Project Texture_Maker.
  - Có thêm chế độ B (spec + prompt tiếng Anh bàn giao), cột "Kết thúc" cho từng layer, hợp đồng gameplay, `references/dissolve.md`, `references/handoff-prompt.md`.
- **`vfx-shader` (VFX_Shader)**, tạo 2026-10-28: làm VFX hoàn toàn bằng shader, shader nhẹ cho mobile, chỉ dùng texture noise. Gọi bằng `/vfx-shader`.
  - Bắt buộc kiểm tra shader có sẵn trước, qua sổ `Docs/VFX/SHADERS.md`.
  - Từ v1.1.0: mọi effect mới duyệt 1 lần (bản định hướng + kế hoạch shader).
  - Đã thử: shader mẫu biên dịch sạch trong Unity 2022.3 (cả 2 biến thể keyword), build script mẫu biên dịch không lỗi. Effect đã làm (phiên khác): Meteor, FireballImpact.
  - v1.1.0 (2026-10-28), sau khi art lead thấy skill có nhiều vấn đề (Meteor: nhỏ, không rõ camera/không gian):
    - thêm bước **Định hướng ban đầu**: phân tích brief, hỏi không gian hoạt động (camera, neo, mặt phẳng, quy mô, di chuyển, nền), thời gian, thành phần, Art Style;
    - **Bản định hướng** gồm sơ đồ cấu trúc + bảng thành phần + kế hoạch shader, gộp thành 1 lần duyệt (`references/direction.md`);
    - camera preview phải khớp camera game;
    - **Review Lab** thành bước 7b bắt buộc; phản hồi ghim được gán về ID thành phần. Cấu hình `review-lab` chuyển sang cổng 8776, vì 8766 đang bị một server khác giữ.
- 2026-10-28: `unity-vfx-maker` được đổi tên thành `vfx-maker` và gộp `dynamic-vfx-prompt-builder` vào. Skill cũ đã xoá; bản sao lưu ở `_archive/`.
- **Đã chốt và tích hợp:** lửa kiểu 1 (`fire_element` trong `make_texture.py`, `references/shape-language.md`).

## Đang thử: quy trình "shader → bake sheet" (CHƯA chốt, CHƯA vào skill)
Ý tưởng (art lead): làm effect bằng shader để có visual tốt nhất, sau đó bake ra texture sheet dùng trong sản phẩm (nhẹ hơn trên mobile). Shader vẫn giữ để dùng cho trường hợp khác. Art lead muốn thử trên nhiều dạng effect rồi mới chốt quy trình.

| Effect | Trạng thái | Shader | Sheet |
|---|---|---|---|
| Lửa 2D (quad) | thử nghiệm, art lead thấy flat | `Assets/VFX/FireStylized/Shaders/SH_VFX_FireStylized.shader` | `T_FireStylized_Loop_4x4.png` |
| Lửa 3D (sphere) | bake theo material art lead tự chỉnh | `SH_VFX_FireStylized3D.shader` | `T_FireStylized3D_Loop_4x2.png` (8 frame) |
| Khói 3D (cụm cầu) | **"tạm ổn"** (2026-10-23) | `Assets/VFX/SmokeStylized/Shaders/SH_VFX_SmokeStylized3D.shader` | `T_SmokeStylized3D_Puff_4x4.png` (16 frame) |

### Khói – trạng thái hiện tại
- Mesh cụm cầu dựng theo bản phác của art lead (`art/smoke_shape_sketch_v1.png`): một thân lớn và 7 thùy tròn (`UseSketchLayout = true`). Bố cục ngẫu nhiên "lớn trong, nhỏ ngoài" vẫn giữ làm phương án dự phòng.
- Dissolve mặc định: **CoreOut**.
  - Tan theo khối, từ lõi cụm ra; mép sắc, có viền tối.
  - Dùng noise Cells; quả nhỏ tan trước (`_SizeStagger 0.4`).
  - Nhịp tan đều: khói đầy nhất ở frame 8, sau đó giảm còn 95/84/72/58/43/26/3%.
- Shader còn chế độ Crescent (`_EraseMode`, làm theo video tham khảo). Art lead đã thử, sau đó quay về CoreOut.
- Các phương án đã bị loại:
  - dissolve noise thường (Cells / Streaks / Chunks)
  - tan từ trong ra theo từng quả (bị khoét thành vòng)
  - bố cục "khối gom tròn" dạng elip
  - cụm quá dài hoặc các quả quá xa nhau

### Công cụ
- `Assets/VFX/FireStylized/Editor/ShaderSheetBaker.cs`: bake 2 lượt.
  - Lượt 1 đo khung thật trên GPU, lượt 2 bake sát khung với lề 6%.
  - Các mặt chồng nhau được trộn như trong game; shader cần `Blend [_SrcBlend] [_DstBlend], One OneMinusSrcAlpha`.
  - Chạy được cả trong Play mode.
- Build:
  - menu `VFX/FireStylized/3D - Build`, `VFX/SmokeStylized/3D - Build`, `.../3D - Bake Dissolve Variants`
  - batchmode: `-executeMethod VfxEffects.SmokeStylized3DBuild.BuildBatch` (chỉ dùng khi Unity đang đóng; không thêm `-nographics`)
- Trigger khi Unity đang mở: tạo file `Temp/<Effect>3D.build | .set | .variants`, sửa nhẹ file .cs để Unity biên dịch lại, rồi đưa cửa sổ Unity lên trước.
- `Docs/VFX/_ArtDirection/scripts/`:
  - `dissolve_noises.py`: 3 noise tileable
  - `fire_shader_sim.py`: mô phỏng shader lửa 2D bằng numpy

### Bài học kỹ thuật
- Project dùng Linear color space:
  - thuộc tính Color thường được Unity tự chuyển sang linear, shader không chuyển thêm;
  - màu `[HDR]` thì không được chuyển (lửa giữ `GammaToLinearSpace`);
  - texture noise phải import linear (tắt sRGB).
- Màu HDR bị cắt về 1 khi bake ra PNG.
- `EditorUtility.CopySerialized` vào mesh asset có sẵn không cập nhật dữ liệu GPU, nên phải xóa rồi tạo lại asset.
- Cực của sphere làm `atan2` ra NaN: cộng thêm eps.
- Khi tan dùng `clip`, để phần đã tan không ghi depth.
- Shader 3D chạy live trên mobile còn nặng (4 lần đọc noise, `atan2`/`sin`/`pow` mỗi pixel); trong sản phẩm dùng sheet đã bake.

## Shape Lab (2026-10-26)
- Tool web chỉnh shape bằng thông số, kiểu After Effects: `Docs/VFX/_ArtDirection/tools/shape_lab.html`, bản online https://claude.ai/artifact/BAbVif8XRDWGL2Gt7Xkk9F.
- Lý do: shape AI vẽ tay chất lượng thấp, còn dùng nhiều shader thì nặng. Art lead kéo thông số đến khi ưng, sau đó gửi JSON (nút "Copy thông số") hoặc PNG/sheet.
- Có 2 loại shape: lưỡi lửa (theo quy tắc kiểu 1 đã chốt: cặp ) (, cung 1/4–1/2, phủ ≥ 55%) và cụm khói (thân + thùy).
- Các thông số chung: mép, motion blur kiểu Photoshop, tan, lắc loop. Xuất sheet 4x2 hoặc 4x4.
- v2, theo góp ý của art lead:
  - **Tan đều theo diện tích:** ngưỡng tan tính theo phân vị, nên "tiến độ 0.3" nghĩa là mất 30% diện tích.
  - Thêm thông số Nhịp tan (đều / nhanh đầu / chậm đầu) và Còn lại ở frame cuối.
  - **Art lead sửa:** sheet Một lần mặc định frame 1 = 100% và frame cuối = 0%, tan đều qua mọi frame (16 frame: mỗi frame mất khoảng 6,7%). Không giữ nguyên nửa đầu sheet như bản khói cũ.
  - Sheet Một lần ghi "còn X%" trên từng ô.
  - **Tự vẽ:** có Cọ, Tẩy, Tô kín, Khoét, Lật, Căn giữa. Thông số riêng: làm trơn viền, co/giãn, méo noise.
  - **Pen kiểu Photoshop** (art lead yêu cầu): đặt điểm góc hoặc điểm cong, khép đường, sửa điểm và tay nắm, Alt để đổi kiểu điểm hoặc bẻ gãy tay nắm, rồi Tô hoặc Khoét vào shape.
  - Ctrl+Z / Ctrl+Shift+Z: khi đang vẽ Pen thì lùi từng điểm hoặc thao tác; ngoài ra lùi từng nét cọ, lasso, lần tô. Hoạt động cả khi đang focus thanh trượt.
  - Nút "Sửa bằng cọ" chép shape có sẵn sang Tự vẽ để sửa tiếp.
  - **Bảng màu:** 9 preset, sửa được gradient (thêm, kéo, xoá điểm màu), chỉnh độ đặc alpha và tương phản. Xuất PNG có thể theo màu.

### Thư viện shape theo nguyên tố (2026-10-27)
- Art lead yêu cầu: mỗi nguyên tố là một thư viện có nhiều shape. Shape do art lead cung cấp.
- Có 9 nguyên tố: Lửa, Khói, Nước, Điện, Băng, Gió, Đất đá, Độc, Phép / Ánh sáng. Mỗi nguyên tố có bảng màu mặc định riêng.
- Dữ liệu: `tools/shape_library/library.json` và các mask `tools/shape_library/<nguyên tố>/*.png`. Script `shape_library.py` gồm các lệnh `add` (ảnh thành mask), `import-json`, `remove`, `list`, `build`. Kết quả build là `tools/shape_library.js`.
- Trong tool:
  - nút **Thư viện**: mở shape theo nguyên tố;
  - **Nhập ảnh**: tách silhouette theo alpha, phần sáng hoặc phần tối, chỉnh được ngưỡng và độ mềm, có tuỳ chọn giữ độ sáng bên trong;
  - **Lưu vào thư viện**: chỉ lưu trên trình duyệt;
  - **Xuất shape của bạn**: tạo file .json để gửi Claude đưa vào thư viện sẵn.
- **2026-10-27:** đã nhập thư viện của art lead từ `D:\Projects\rpg-game\Assets\RPG_VFX\Duong\Texture\`:
  - Lửa: 34 flipbook từ `Flipbooks/Fire`, cộng 3 mẫu thông số. Bỏ qua các bản trùng `_Grayscale`, `_Gray`, `_C`, `_VertexOffset`, `" 1"`, `_Blur`.
  - Khói: 22 shape cộng 3 mẫu thông số.
  - Impact: 11 shape (thêm nguyên tố mới).
  - Mỗi mask giữ lớp sáng tối (độ mờ × độ sáng). Flipbook lưu cả sheet, mỗi frame tối đa 320px. Ảnh tải theo đường dẫn, tổng khoảng 4 MB.
  - Script tự lấy lưới từ tên file (ví dụ `_4x4` = 4 cột × 4 hàng) hoặc dò khe trống. Đã ép tay: `TX_VFX_Biting` = 2x1, `TX_VFX_Smoke08` = 2x2.
- Trong tool:
  - Bấm vào flipbook để mở bảng chọn frame, có ô xem trước tự chạy 12 fps.
  - **Thẻ trong lưới chỉ chạy như GIF khi được trỏ chuột** (art lead yêu cầu để tool không nặng).
  - Shape từ thư viện mở với lõi sáng = 0 và motion blur = 0, để giữ đúng như ảnh gốc.
- **2026-10-27 (sau):** Tự vẽ có thêm 2 tool.
  - **Di chuyển (V)**: hình vẽ bằng Pen vẫn giữ điểm sau khi tô hoặc khoét. Tool này kéo được điểm, tay nắm và cả hình; kéo vùng trống thì dời cả bản vẽ. Có Alt đổi góc ↔ cong, Delete, phím mũi tên. Khi dùng Cọ / Tẩy / Tô kín, hình Pen chốt thành pixel (Ctrl+Z lấy lại được).
  - **Hướng tan "Theo độ dày"** (nhóm Tan): chỗ nét mỏng tan trước, chỗ dày tan sau. Độ dày = bán kính đường tròn lớn nhất lọt trong nét tại điểm đó. Trong mỗi đoạn, mép tan sang mép đối diện: "Hai mép khép vào giữa" hoặc "Quét từ một phía" (có Góc quét). "Độ quét ngang" 0..1 chỉnh mức ăn mòn từ mép.
  - **Hướng tan "Theo độ sáng"** (tối tan trước / sáng tan trước): đo trên hình cuối cùng, sau Lõi sáng, Motion blur, Nhoè đều. Nhịp vẫn chia theo diện tích.
  - **Nhóm "Sáng tối"** (2026-10-28, thay bản Levels mà art lead thấy không ổn): tô tông kiểu toon như Smoke04/05/06. *Theo ánh sáng* dịch silhouette ngược hướng đèn, chỗ lệch ra ngoài là dải bóng hình lưỡi liềm ôm từng thuỳ. *Theo noise* lấy mảng tông từ noise. Có Số bậc tông, Ranh giới, Độ mềm, Độ sáng vùng bóng. Sáng tối vào kênh RGB, alpha giữ silhouette.
  - Xuất file: có ô Tên file, tick "Thêm đuôi tự động", dòng xem trước. Vẽ ở frame đang tan thì tự về frame 1.
  - **Zoom (Z)**: bấm để phóng to, Alt+bấm để thu nhỏ, kéo để cuộn. Ở mọi tool: lăn chuột để zoom, giữ chuột giữa để cuộn, Ctrl+0 để vừa khung. Có thanh −/%/+ ở góc khung.

## Việc tiếp theo có thể làm
- Thử quy trình shader → bake sheet với dạng effect khác (điện, impact, slash…), rồi art lead chốt và đưa vào skill.
- Nếu cần lửa hoặc khói chạy live trên mobile: làm thêm bản shader Mobile tối ưu.

## Effect làm bằng vfx-maker 2.3.0 (2026-11-03) — chờ art lead review
- **GroundBlast**: nổ tại đất ~2 m, Stylized mềm, lửa cam; texture đều sinh bằng `make_texture.py` (không shape thư viện). 5 lớp: Flash, Fireball (khối sáng mềm), Smoke (flipbook 4×4), Shockwave (Billboard+Local), Sparks (Stretched). Build 2 vòng: v1 cầu lửa dùng sheet khói bị rỗng → v2 đổi sang khối dot mềm. Còn lưu ý: khói cuối hơi rỗng dạng vòng (do sheet tan khoét lỗ lớn).
- **HealCircle**: vòng phép hồi máu ~2 m dưới chân, bám nhân vật, một lần 1.5 s, xanh lá; vòng phép vẽ mới bằng `Docs/VFX/HealCircle/heal_circle_textures.py` (tròn, chấm, cánh lá — không gai). 6 lớp: GroundGlow, RuneOuter/RuneInner xoay ngược chiều, Beam, Motes, Sparkles.
- Review Lab: `Docs/VFX/_Review/index.html` (2 effect).

## Cập nhật 2026-11-03 (phiên Slash360 / IceSpike / Showcase)
- **Thư viện nhập sẵn:** shader từ rpg-game ở `Assets/VFX/_Imported/RpgGame/` (14 shader URP gốc đã viết lại thành CG dùng chung URP + Built-in; xem `README.md` trong đó), mesh ở `Assets/VFX/_Imported/Mesh/` (55 `SM_VFX_*`).
- **Slash:** chỉ làm bằng bộ Coloso (`VFXLib/ColosoShaderAdditive|Alpha|AlphaCutOut_Optimized`). Hiện còn `VFX_Slash360_Earth` (vệt chém 360°, mesh `SM_VFX_Slash_Circle_Thin`); bản 5 nguyên tố lưu `_archive/Slash360_5elements_2026-11-03/`.
- **IceSpikeFan** (`Assets/VFX/IceSpike/`, plan `Docs/VFX/IceSpikeFan/Plan.md`, v4): cụm 8 khối băng sát nhau nghiêng ngẫu nhiên, tuổi thọ riêng, glow đất + vết nứt + đất vỡ + impact (auto mix) + khói mặc định `fx_t_smoke_02`. **Bản Đất đã làm (2026-11-04)**: `VFX_IceSpikeFan_Earth`, cùng builder (cột bảng màu nâu đỏ, vết nứt / glow hổ phách, khói bụi, recipe `EarthSpike_Impact`); chờ art lead duyệt.
- **HealCircle** v2: ~2,8 s.
- **Scene chung** `Assets/VFX/_Showcase/Scenes/VFX_Showcase.unity` (menu VFX → Showcase → Build Scene): chỉ liệt kê effect trong `Included` (Slash360, IceSpikeFan, HealCircle). Thêm effect khi art lead duyệt.
- **Skill mới** `/vfx-shader` (`.claude/skills/vfx-shader/`, v1.0.0): dùng lại shader có sẵn trước, `references/coloso.md`, `magic-circle.md`; mục "Mặc định của art lead" (khói = `fx_t_smoke_02` + shader mobile của Unity).
- **Việc tiếp theo (chờ art lead):** các VFX khác sẽ thêm sau; cách làm từng nguyên tố (Lửa, Băng, Sét, Độc, Đất) art lead sẽ cập nhật vào skill (`references/elements.md` chưa tạo).

## Cập nhật 2026-11-04
- IceSpikeFan: **Băng = pha lê** (shader mới `VFX/FX/Rock Facet` + MatCap `MC Metal Silver` của rpg-game), **Đất = đá** (bảng màu đá `T_IceSpike_RockPalette.png` + Rock Facet toon + MatCap nhẹ). Bản thử `IceCrystal` đã xoá. Chờ art lead duyệt cả hai.
- Scene chung: danh sách `Included` có `VFX_IceSpikeFan_` nên cả Băng và Đất tự vào khi chạy lại **VFX → Showcase → Build Scene**.
- IceSpikeFan v7: Băng sáng hơn (MatCap 2,7); Đất không glow, vết nứt vỡ đất tối + viền bụi, impact chỉ chớp yếu + khói. Chờ art lead duyệt.
- **IceSpikeFan Đất (v9, 2026-11-04):** cùng cấu trúc cụm gai nhọn với Băng, mesh tự vẽ bằng code (`SM_VFX_EarthSpike_*`, cột 6 cạnh thon thành mũi nhọn, mặt phẳng), vị trí và timing khác (chậm, từ giữa ra ngoài, vỡ ngoài trước), không ánh sáng. Ngà `Bone`, đá tảng tròn và `EarthTusks` đã loại (sai ý art lead). Chờ duyệt.
- **GroundBlast v3 (2026-11-04):** lửa = 1 glow mạnh (art lead); khói làm lại theo video Beyond-FX (yt LzZ_9tmWPS8 04:10–06:34): 6 mesh cầu + shader mới `VFX/FX/Erode Sphere` (Custom1 = ngưỡng alpha / emissive / bulge / sáng tối, `_RimIn` cho viền tan trước). Mask xoáy hiện là `_TEMP` lấy từ video, **không ship**; bản tự vẽ `T_GroundBlast_SmokeErode`. Mỗi lớp là 1 prefab thành phần (`SaveNested`, kit 1.1.0). Còn lưu ý: giữa đời khói là quả cầu xám trơn, sáng tối nhẹ.
- **GroundBlast v5c (2026-11-04):** khói so từng khung với video (`Docs/VFX/GroundBlast/ref_compare.png`) rồi sửa: 30 cầu `SM_VFX_SphereUV`, Cone lên → đáy rộng + giữa cao, mép sần (`_Lumps`, art lead: "khói của họ đâu có tròn"), mask quấn UV cầu (`_MESH_UV`) → tan thành sợi dọc, ramp theo độ sâu (`_HeatRange`), cháy cam → gân → nguội ~0.4 s → than xám → sợi, tắt ~1.5 s. Mask vẫn là `_TEMP` từ video (không ship). Chưa vào `Included` của Showcase.
- **Shader khói `VFX/FX/Erode Sphere` v3 (2026-11-04, art lead):** rút còn 7 thuộc tính (`_MainTex`, `_RampTex`, `_Soft`, `_EmisBoost`, `_HeatRange`, `_Lumps`, `_ShadowTone`); Custom Data chỉ còn 2 kênh (x = lúc khói tan, y = lúc lửa tắt), phồng + sáng tối cố định trong shader. Stream `Custom1XY`.
- **Dọn prefab (2026-11-05, art lead):** xoá 27 prefab không dùng trong scene Showcase (chuyển vào Thùng rác Windows, kèm `.meta`): StrongExplosion_v1, BombBlast_Shader, CodeShockwaveGround, CodeSparkBurst, Explosion, FireStylized(3D), Fireball Impact/Loop/Projectile, Lightning_Impact, Lightning_Strike (2), Meteor, Mixes ArcaneHit_Air / BombBlast_Code / FireHit_Ground / IceHit_Ground / IceSlam_Ground, SmokeStylized3D, StylizedSlash, ThunderChainImpact (2), ThunderImpact, 3 cụm cầu cũ của MushroomBlast. **Giữ:** `_Components` (thành phần mix), GroundBlast (gốc khói vụ nổ), `_Imported` (tham chiếu). Build script / material / texture của các effect đã xoá vẫn còn: build lại được; scene demo riêng của chúng mất tham chiếu prefab.
  - **Cùng ngày, xoá luôn thư mục** của 16 effect đó (kể cả build script, material, texture, scene demo) + 5 Mix cũ + `Assets/Scenes`, `Assets/_Game`, `smoke.mat`, ảnh `tread_*.png`; `VFX_ArrowGlow.shader` dời vào `_Shared/Shaders`. Tất cả trong Thùng rác Windows; tài liệu `Docs/VFX/<Tên>/` vẫn giữ. Unity biên dịch lại không lỗi.
- **MushroomBlast v2 (2026-11-04, `/vfx-shader`):** nổ tại đất ~3 m dạng nấm, 2 s: chớp gai (root) + sóng đất + glow lõi + khói Erode Sphere (thân 14 / đầu nấm 14 / vành 16 cầu) + đá văng + tia lửa + vết cháy; texture từ `Assets/Library/`. v2 sửa thân nấm bị mất và vành đất rời. Chưa vào `Included` của Showcase. GroundBlast chưa build lại với shader v3.

## Review 16 biến thể (2026-11-09)
Xem preview của 16 biến thể trong Showcase (Slash360 Fire/Water, IceSpikeFan Magma/Thorn, HealCircle Holy/Nature, LightningStrike Frost/Toxic, AuraGauntlet Fire/Poison, FireballThrow Frost/Poison, VioletThunder Azure/Crimson, FireTornado Frost/Sand), build lại 8 cái đã sửa:
- **Slash360_Fire**: cả đĩa sáng ngay từ đầu (texture Library 005 sáng sát mép đầu + clamp) -> làm tối cột đầu của bản copy; Edge đứng yên ở mép, Trail chạy vượt đầu (đường cong đầu dùng chung dù window khác nhau) -> nhân đường cong theo window từng layer; tàn lửa không bay lên do lỗi Velocity khác mode.
- **Slash360_Water**: cùng lỗi Edge / Trail; khói xám giảm (16 hạt, alpha 0.2).
- **IceSpikeFan_Magma / Thorn**: lỗi Velocity khác mode (mảnh vỡ / bào tử đứng yên) trong `IceSpikeVariantKit`.
- **LightningStrike_Frost**: sương cyan to và đặc che mất tia + vết nứt -> nhỏ, ít, mờ hơn.
- **FireTornado_Frost**: phễu cháy trắng -> tông xanh băng, `_EdgeIntensity` 1.6, camera preview lùi để không cắt đỉnh.
- **FireTornado_Sand**: không đọc ra thân lốc -> cột mảnh hơn, xoắn nhanh hơn, nhiều hạt nhỏ hơn; camera lùi.
- Giữ nguyên (xem ổn): HealCircle Holy / Nature, LightningStrike Toxic, AuraGauntlet Fire / Poison, FireballThrow Frost / Poison, VioletThunder Azure / Crimson. Ghi chú: FireballThrow Frost vệt bay là thanh trắng đặc, có thể làm mềm sau.
- Chỉ xem qua `Preview_sheet.png` (camera trên xuống / 3/4 nền tối), chưa xem chạy trong Showcase. Chờ art lead xem.
