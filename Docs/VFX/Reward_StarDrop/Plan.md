# Reward_StarDrop — Plan (2026-11-18)
Project đích: `idle_farm_harvesting` (Unity 2022.3, Built-in). Prefab `Assets/Anim_VFX/VFX/Prefabs/VFX_Reward_StarDrop.prefab`, dựng thử ở `Assets/Anim_VFX/Demo_scene.unity`. Builder: `Assets/Anim_VFX/Editor/StarDropRewardBuilder.cs` (menu VFX → Anim_VFX → Build Reward StarDrop). Tạo hình: `Docs/VFX/_Anatomy/reward-burst.md`.

Không gian (đề xuất, đã duyệt): billboard hướng camera, ~8 đơn vị, neo tâm vật thưởng, một lần ~2,2 s. Camera Demo_scene: ortho size 15, xoay X 55°. Màu mặc định Legendary vàng cam. Sorting layer `WorldUI`.

## Bảng texture (Library, copy sang `Assets/Anim_VFX/VFX/Textures/StarDrop/`)
Bản 2 (2026-11-18, sau phản hồi "chưa giống ref"): đổi vòng, chùm tia, chớp, quầng theo khung ref xem lại kỹ.

| Thành phần | Ảnh chọn | Lý do | Đã loại (vì sao) |
|---|---|---|---|
| Cầu chớp, lõi sáng (chớp là ellipse cao 8×11) | glow/soft_round/glow_soft_round_013 | alpha, xám, tròn mềm, không chạm mép | 006/007/009 (nền đen không alpha → viền vuông), 010 (cam cố định) |
| Halo ấm sau vật | glow/soft_round/glow_soft_round_015 | alpha, quầng rất mềm, tint cam được | 021 (quá mờ) |
| Vòng "tích" xung nhịp + vòng loe trắng | ring/thin/ring_thin_011 | vòng dày sáng, mép mềm đúng ref (vòng trắng dày); dự phòng ring_thin_005 | 005 (quá mờ, gần như không thấy), 009/014 (nét mảnh cứng) |
| Vòng vàng nhỏ đi sau | ring/thin/ring_thin_002 | mảnh, viền mềm | — |
| Chùm tia (8 tia, mỗi tia một hạt riêng) | **ảnh mới `SD_RayCyan/Pink/Orange/Teal.png`** (PIL, 1024×256, một nêm đặc, đỉnh ở mép trái, lõi trắng mảnh, không mờ ở đầu xa) | ref: tia chỉ bị cắt bởi mép màn hình, không có đầu mút → **không dùng một ảnh vuông**; mỗi tia 1 hạt, Billboard, `pivot (0.5,0,0)` để xoay quanh đỉnh, cỡ 22 × (5–16.5), thứ tự bật xen kẽ góc (cyan 22° → hồng 122° → cyan −40° → cam 97° → ngọc 212° → cyan −16° → cyan 172° → cam −70°), cách nhau 0,045 s nên tắt cũng lần lượt cùng thứ tự; ảnh có **gradient alpha mờ dần từ tâm ra ngoài** (đặc 18% đầu, rồi giảm dần về 0 ở đầu xa), sống 0,85 s, **co giãn theo chiều rộng**: rộng 0→1 trong 0,19 s đầu, giữ, rồi rộng 1→0 từ 43% tuổi đến hết kèm fade alpha từ 0,9→0 (chiều dài giữ nguyên), góc đặt tay không đều, **Alpha Blended**; Library không có | glow_flare_003, flash_spiky (tia mảnh), SD_Wedges (một ảnh vuông 12 / 8 nêm — bỏ) |
| Quầng nổ xanh-trắng | glow/flare/glow_flare_009 | tia mịn toả tâm, nền đen nên dùng Additive | glow_flare_003 (tia cứng), 002/004 (sao 4 cánh) |
| Sao lấp lánh | spark/star/spark_star_001, spark_star_008 | 4 cánh alpha, omni nên spam được | 006 (sao 5 cánh màu cố định), 015 (đỏ cố định) |
| Vệt toả tâm (12 vệt) | spark/streak/spark_streak_001 | đầu trái, thuôn; nền đen nên chỉ dùng Additive | 003 (chạm mép), 004 (mũi giáo) |

Ghi chú build: Unity Editor (Linux) không biên dịch lại assembly Editor sau 09:36 nên bản 2 dựng bằng `execute_code` qua Unity MCP (cùng logic với `StarDropRewardBuilder.cs`). Khi Unity biên dịch lại, menu VFX → Anim_VFX → Build Reward StarDrop cho cùng kết quả.

## Demo Laboratory (2026-11-18)
Trong `Assets/Anim_VFX/Demo_scene.unity`, object `LabDemo` dựng theo ảnh UI Laboratory art lead gửi: 1 ô lớn phía trên + 3 ô nhỏ phía dưới (cà chua, cà chua, ô trống). Chỉ là khối đồ hoạ tạm (quad / sphere Unlit) để xem VFX đúng vị trí, không phải UI thật; đặt trước camera, xoay theo camera.
- **VFX nhẹ** `Assets/Anim_VFX/VFX/Prefabs/VFX_Lab_SlotFill.prefab` (tím hồng theo UI, ~0,5 s, 4 lớp, tối đa ~13 hạt): quầng (SD_FlashBall), vòng loe (SD_Ring), lõi chớp nhỏ, 6 sao nhỏ (SD_Sparkle). Dựng bởi `execute_code` (logic helper như Starr Drop).
- **Nhịp demo** (chỉ chạy một lần khi Play, không loop): ô 1 lúc 0,6 s; ô 2 lúc 1,6 s; ô 3 lúc 2,6 s; ô lớn `VFX_Reward_StarDrop` (scale 0,5) lúc 3,4 s. Lệch nhịp bằng `startDelay` trên từng instance.
- Preview: `Lab_demo_sheet.png`.

## Demo Laboratory trên UI (2026-11-18, thay bản world ở trên)
Trong `Demo_scene.unity`: Canvas `LabUIDemo` (Screen Space Overlay, scaler 1080×1920, match 0,5; bản world `LabDemo` đã tắt). Bố cục theo ảnh UI Laboratory của art lead, **sprite lấy trong `Assets/_Game/Sprites/Laboratory/` (chỉ tham chiếu, không sửa ảnh gốc; đã kiểm `git status` thư mục đó rỗng)**: `BG_1` nền, `Title` + chữ LABORATORY, `Info`, `Slot` (ô lớn "?"), `BG_epic_3` (ô tím đã có hạt) + `Plant_3` (icon hạt, vì thư mục không có cà chua), `BG_Plus` (ô trống), `Plus`.
- VFX hiển thị trên UI bằng `Coffee.UIExtensions.UIParticle` của project (`_FrameWork/Scripts/UIHelper/UI Particle`): `FX_SlotFill_0..2` scale 78, `FX_BigReward` scale 26 (đơn vị particle × scale = pixel canvas). Nhịp như bản world: 0,6 / 1,6 / 2,6 s ô nhỏ, 3,4 s ô lớn; chạy một lần khi Play.
- Đã chụp màn hình Play mode: `Lab_UI_slot_fill.png`, `Lab_UI_big_reward.png`.

## Cập nhật tia (2026-11-18): ảnh trắng + màu trong particle
Tia dùng **một ảnh trắng `SD_RayWhite.png`** (PIL, 1024×256, nêm thân alpha 0,69 + lõi alpha 1, gradient mờ ra ngoài), **material Additive** (`Mobile/Particles/Additive`), **màu đặt trong Start Color của từng particle system `Ray_0..7`** (hồng, cam, cyan ×3 sắc, ngọc, cam). Ảnh `SD_RayCyan/Pink/Orange/Teal.png` và `MAT_SD_Ray*.mat` cũ không còn dùng (để nguyên vì hệ thống chặn xoá). Lõi trắng giờ chỉ sáng hơn thân cùng màu (nhân màu), không còn trắng thuần.
Sửa tiếp (2026-11-18): `SD_RayWhite.png` bỏ lõi riêng, nêm **một độ đặc đồng nhất** (alpha 1 → gradient mờ ra ngoài), mỗi tia chỉ một màu từ Start Color.
Sửa tiếp (2026-11-18): `SD_RayWhite.png` thành **nêm cụt**: đầu trong rộng 40% bề rộng đầu ngoài (trước đó chụm về một điểm), để phần gần tâm rộng hơn.
Sửa tiếp (2026-11-18): đầu trong của nêm 40% → **15%** (40% quá lớn). Phát hiện đường cong co giãn bề rộng (`sizeOverLifetime.y`) của `Ray_0..7` trong prefab bị mất (về Constant) — dựng lại thì có lại. Đo bằng số (Ray_2): rộng 0,94 → 8,85 → 8,71 → 4,88 → 1,07 → hết; dài giữ 22; alpha 75 → 252 → 25. Sau mỗi lần ghi đè prefab nhớ chạy lại kiểm tra `ymode=Curve`.

## Demo UI: nhịp nhanh + trail bay lên ô lớn (2026-11-18)
- Nhịp ô nhỏ rút còn 0,35 / 0,65 / 0,95 s (trước 0,6 / 1,6 / 2,6 s).
- Prefab mới `Assets/Anim_VFX/VFX/Prefabs/VFX_Lab_SlotTrail.prefab`: 1 hạt đầu (SD_FlashBall hồng nhạt, cỡ 0,6, sống 0,35 s) bay theo `velocityOverLifetime` (Local) kèm module **Trails** (PerParticle, đuôi 0,7 × tuổi, `trailMaterial` Additive SD_FlashBall, rộng giảm dần). Cả 3 trail đều mất **0,35 s**; vận tốc đặt riêng từng instance trong scene (`FX_SlotTrail_0..2`, bay từ tâm ô nhỏ đến tâm ô lớn). Xuất phát sau pop ô nhỏ 0,1 s: 0,45 / 0,75 / 1,05 s.
- Ô lớn `FX_BigReward` bắt đầu **1,45 s**, sau khi trail cuối tới nơi (1,05 + 0,35 = 1,4 s).
- Đã chụp Play mode (timescale 0,4): `Lab_UI_trail_sheet.png`. Trail hiển thị qua `UIParticle` bình thường.
- Lưu ý khi rebuild: lần đầu chạy lại script dựng UI, scene vẫn ở bản cũ (có thể do thao tác ngoài); luôn đọc lại `startDelay` của `FX_*` để xác nhận trước khi chụp.

## Trail làm lại: hạt bụi + sao bay vòng cung (2026-11-18, thay bản Trails renderer)
Bỏ module Trails. `VFX_Lab_SlotTrail.prefab` giờ gồm 3 hệ hạt cùng đi một đường cong: `TrailHead` (1 hạt sáng SD_FlashBall dẫn đầu), `TrailDust` (bụi mềm SD_FlashBall, 40 hạt/s trong 0,3 s, alpha 0,5, thu nhỏ dần), `TrailSparks` (sao nhỏ SD_Sparkle, 55 hạt/s, màu ngẫu nhiên hồng–trắng); dust + sparks có `noise` nhẹ (0,25) cho cảm giác bụi. Mỗi hạt sống 0,3–0,4 s nên mỗi hạt đều bay hết đoạn đường.
- **Vòng cung:** `velocityOverLifetime` (Local) dạng đường cong: y(t) = dy·(1,8t − 0,8t²) (vọt lên rồi dẹt), x(t) = dx·t + sb·(t − t²) với sb = ∓3,2 đơn vị (ô trái vồng sang trái, ô phải và ô giữa vồng sang phải). Tổng quãng đường vẫn tới đúng tâm ô lớn sau 0,35 s. Đã đo bằng số (ô trái: (8,39) → (110,195) → (285,262) px).
- Lỗi đã gặp: instance `TrailHead` trong scene giữ lại hệ số nhân vận tốc cũ (9,34) làm hạt bay xa gấp ~9 lần → sau khi gán curve phải đặt `xMultiplier / yMultiplier / zMultiplier = 1` rồi đo lại bằng `Simulate` + `GetParticles`.
- Ảnh chụp Play mode (timescale 0,25): `Lab_UI_trail_sheet.png`.

## Bỏ trail (2026-11-18, art lead: "thôi bỏ trail đi")
Đã gỡ `FX_SlotTrail_0..2` khỏi `LabUIDemo` và xoá `VFX_Lab_SlotTrail.prefab` (+ `.meta`) cùng ảnh `Lab_UI_trail_sheet.png`; hai mục "Trail" ở trên chỉ còn là lịch sử. Nhịp demo còn lại: ô nhỏ 0,35 / 0,65 / 0,95 s, ô lớn 1,45 s (giữ nguyên).

## Đường sét kiểu Candy Crush (2026-11-18, thử nghiệm "xem sao")
Prefab `Assets/Anim_VFX/VFX/Prefabs/VFX_Lab_LightningLine.prefab`, trong demo là `FX_LightningLine` (UIParticle scale 78) nối tâm ô nhỏ 1 → ô nhỏ 2 (L = 4,24 đơn vị = 331 px), bắt đầu 0,5 s, dài 0,6 s.
- **Texture:** `SD_LightningLine.png` **vẽ mới** (PIL, flipbook 4 khung xếp dọc, mỗi khung 1024×256 dải ngang): lõi trắng, viền sáng, quầng xanh dương, đường ngoằn ngoèo + 1 nhánh, thon hai đầu. Library không có: `bolt_sheet` là tia đứng, `arc_sheet` là cung ngắn nằm đất, `arc_single_001` nền đen chạm mép. Preview ảnh: `SD_LightningLine_preview.png`.
- **Cấu trúc:** `LineBolt` (hạt Billboard, `pivot (0.5,0,0)` để đầu trái nằm ở tâm, cỡ 3D dài L × rộng 2,1, sống 0,09 s, phát 26 hạt/s trong 0,6 s, texture sheet 1×4 `startFrame` ngẫu nhiên → nhấp nháy), `EndGlowA/B` (chớp sáng hai đầu, SD_FlashBall), `EndSparkA/B` (5 sao nhỏ mỗi đầu). Material Additive. Mỗi instance chỉnh `startSizeX` = L và dời `EndGlowB` / `EndSparkB` tới x = L.
- Đã chụp Play mode: `Lab_UI_lightning_line.png`.
- **Lỗi quy trình:** lệnh `manage_scene save` báo thành công nhưng **không ghi file** khi scene không "dirty" (sửa bằng `execute_code`), nên việc gỡ trail và thêm đường sét bị mất khi vào Play. Phải gọi `EditorSceneManager.MarkSceneDirty` + `SaveScene` rồi kiểm tra file bằng `grep` / mtime.

## Chớp chuyển cảnh sang popup reveal (2026-11-18)
Câu hỏi art lead: "có tích hợp được vào vfx reward stardrop không?" → **được**: thêm lớp `TransitionFlash` vào chính `VFX_Reward_StarDrop.prefab` (cũng có trong `StarDropRewardBuilder.cs`).
- `TransitionFlash`: SD_FlashBall, 3 hạt chồng nhau (additive), cỡ 90 đơn vị (UIParticle scale 26 → ~2300 px, phủ kín 1080×1920), bắt đầu **1,2 s** sau prefab, sống 0,9 s, alpha 0 → 1 trong 0,25 s, giữ đến 50% tuổi, rồi tắt dần. Đỉnh trắng nhất ≈ 1,45–1,65 s sau lúc prefab bắt đầu (đo: alpha 51 → 253 → 255 → 119 → 17).
- Để chớp phủ lên cả popup, `FX_BigReward` được chuyển ra **gốc canvas, sibling cuối** (trên `LabPanel` và `RevealPanel`). Dùng ngoài UI thì lớp này là chớp trắng toàn màn hình rất lớn; muốn tắt thì tắt GameObject `TransitionFlash`.
- Popup mô phỏng `RevealPanel` theo ảnh popup art lead gửi (PURPLE POTATO / COMMON, vật phẩm, 210K / 30, ô BUFF, nút Claim), sprite lấy trong `_Game/Sprites/Laboratory/` (`BG_common_5`, `Glow`, `Plant_1` thay cho quả cà chua vì thư mục không có, `BG_common_7`, `BG_common`), chữ font mặc định. Kèm `FX_RevealSparkles` (prefab `VFX_Reveal_Sparkles`: sao nhấp nháy loop quanh vật phẩm).
- Chuyển cảnh bằng Animator (`Assets/Anim_VFX/Anim/LabDemo_Swap.controller` + `.anim`, gắn ở `LabUIDemo`): bật/tắt `m_IsActive` của `LabPanel` / `RevealPanel` tại **2,95 s** (= 1,45 s prefab bắt đầu + 1,5 s, đúng đỉnh chớp). Kiểm bằng `SampleAnimation`: 2,9 s còn Lab, 3,0 s đã là Reveal.
- **Chưa xem bằng mắt trong Play mode** (Unity đang kẹt chờ biên dịch script nên không vào Play được).

### Sửa chớp chuyển cảnh: phủ kín màn hình (2026-11-18)
Bản trước dùng 3 hạt tròn mềm (`SD_FlashBall`, cỡ 90) nên **không phủ tới góc** màn 1080×1920. Cách mới: **1 hạt vuông trắng đặc** với texture `SD_White.png` (16×16 trắng 100%, tạo mới vì Library không có ảnh đặc), cỡ 90 đơn vị × UIParticle scale 26 = **2340 px** vuông, tâm ở ô lớn (0, −61) → phủ x ±1170, y −1231…+1109, trùm kín 1080×1920 (và màn rộng hơn). Vẫn là lớp `TransitionFlash` trong `VFX_Reward_StarDrop.prefab`, timing giữ nguyên (bắt đầu 1,2 s, alpha 0 → 1 trong 0,25 s, giữ đến 55% tuổi, tắt dần). Đo: alpha 91 → 255 → 255 → 6.
- Chưa chụp Play mode xác nhận bằng mắt (Unity lại kẹt chờ biên dịch sau khi sửa `StarDropRewardBuilder.cs`; cần focus cửa sổ Unity).

## 3 đường sét nối 3 ô nhỏ lên ô lớn, kéo dài đến lúc chớp chuyển cảnh (2026-11-18)
Art lead đã tự sửa trong Unity (tạo prefab `LabUIDemo`, `FX_LightningLine`, `FX_RevealSparkles`, `FX_SlotFill_0`; scene có thay đổi chưa lưu) và yêu cầu **giữ nguyên**, nên lần này **không dựng lại UI**, chỉ thêm đối tượng mới vào instance `LabUIDemo` rồi áp phần thêm vào `LabUIDemo.prefab`.
- `FX_LightningLink_0..2` trong `LabPanel` (UIParticle scale 78, instance `VFX_Lab_LightningLine`): nối **tâm `Slot_i` → tâm `BigSlot`** (toạ độ đọc trực tiếp từ scene), dài 5,36 / 3,27 / 5,36 đơn vị (418 / 255 / 418 px), góc 37,6° / 90° / 142,4°.
- Xoay bằng `LineBolt.startRotation = −góc` (UIParticle **không** nhận xoay của RectTransform; dấu âm vì UIParticle xoay ngược chiều kim đồng hồ khi góc dương). `EndGlowB` / `EndSparkB` đặt ở (dx, dy)/78 chứ không phải (L, 0).
- Nhịp: bắt đầu **0,55 / 0,85 / 1,15 s** (sau pop mỗi ô 0,2 s), **cùng kết thúc ở thời điểm chớp chuyển cảnh lên đỉnh** (đọc `TransitionFlash.startDelay` = 2,6 s, cộng 0,25 → 2,85 s; thời lượng 2,30 / 2,00 / 1,70 s). Tốc độ phát hạt có đường cong vào (0 → 1 trong 0,04) và ra (còn 0,3 ở cuối). Chớp hai đầu nhịp lại mỗi 0,45 s, sao nhỏ mỗi 0,3 s (bursts, không loop).
- `FX_LightningLine` cũ (nối ô 1 → ô 2, bản thử) được **tắt (SetActive false)**, không xoá.
- Đã chụp Play mode (timescale 0,4, đã trả về 1): `Lab_UI_lightning_links.png`: sét lần lượt nối lên ô lớn, ô lớn sáng dần, tia ra lúc ~2,15 s, chớp phủ kín và đổi sang popup lúc ~2,8–2,95 s.

### Sửa texture `SD_LightningLine.png`: bỏ vệt tím (2026-11-18)
Vệt tím ở art lead thấy nằm ở **các nhánh rẽ**: quầng mờ của nhánh (blur trên ảnh RGBA có điểm ảnh trong suốt màu đen) bị lem màu, nén DXT5 ám tím. Sửa: **bỏ hết nhánh**, vẽ mỗi lớp (quầng / viền / lõi) thành mask xám rồi blur mask và mới tô màu; điểm ảnh trong suốt mang sẵn màu quầng xanh (không còn đen). Chỉ ghi đè file PNG, `.meta` (import setting của art lead) giữ nguyên, không đụng scene / prefab. Ảnh gốc trước khi sửa lưu ở `/tmp/ref_work/SD_LightningLine_backup.png` (tạm). Preview nền caro: `SD_LightningLine_preview.png`.
