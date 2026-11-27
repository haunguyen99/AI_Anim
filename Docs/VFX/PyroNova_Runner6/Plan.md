# PyroNova_Runner6: VFX hero Pyromancer + Nova cho Run 6 (2026-11-16 → 11-17)

Nguồn brief: `Run 6 - Work.xlsx`, tab "Anim & VFX", dòng 208–217 (trạng thái "Đã Order").
Đích: project **runner6** (`/media/sondh/New Volume/Projects/runner6`), prefab trong `Assets/VFX_Library/Prefabs/`, đặt vào scene `Assets/VFX_Library/VFX_Scene.unity` (art lead 2026-11-16: "làm trực tiếp vào scene này, ở thư mục runner 6"). Built-in pipeline, Linear color, Unity 2022.3.62f3. Art lead bỏ bước cài Unity MCP (2026-11-17).

**Trạng thái (2026-11-17): v1 đã build + chụp preview ở project tạm, đã chép sang runner6 và ĐÃ ĐẶT VÀO `VFX_Scene` (qua Unity MCP, đã lưu scene). CHƯA qua review agent khác, CHƯA art lead duyệt, CHƯA xem chạy trong Unity của runner6.** Root `PyroNova_VFX` trong Hierarchy chứa 7 instance (cột trái laser 3 màu, cột phải cast / cầu lửa / đạn / lửa tay, xoay Y 90°).

**Unity MCP (2026-11-17):** art lead tự cài MCP for Unity (Coplay) vào runner6, server `http://127.0.0.1:8080/mcp` (uv chạy Python). Đã `claude mcp add --transport http unity http://127.0.0.1:8080/mcp` (local scope). Tool xuất hiện sau khi khởi động lại phiên Claude; trong phiên đang chạy gọi bằng JSON-RPC qua `curl`. Lỗi biên dịch có sẵn của runner6: `ButtonClickEffect` không tìm thấy (`Assets/_Game/Arts/VFX/Scripts/ButtonEffect.cs` và `Arts/Vfx/Scripts/ButtonEffect.cs` trùng tên khác hoa thường, hệ file Linux phân biệt) làm Assembly-CSharp không biên dịch, nên menu script Editor mới không hiện; vì vậy đặt prefab bằng `manage_gameobject` thay vì menu. Không sửa code game. **Còn lại cho art lead: xoá `Assets/VFX_Library/Editor/PyroNovaPlaceInScene.cs` + `.meta` (công cụ tạm không dùng nữa; lệnh xoá bị chặn).**

NOTE của sheet: mọi đòn tấn công / cast ingame làm dựa trên anim idle ingame (bay lơ lửng) → điểm neo là tay / nòng, không chạm đất.

## 5 VFX → 7 prefab

| Prefab | Brief sheet | Loại (Anatomy) | Ref |
|---|---|---|---|
| `VFXHandFlame` | FX lửa bốc lên ở hai tay | `fire-hand-flame.md` | YT qeUuME4z9yY t=21 (Dota 2 Lina) |
| `VFXPyroCast` | Thổi ra một sóng lửa | `fire-wave-cast.md` | YT qeUuME4z9yY t=40 |
| `VFXPyroProjectile` | Projectile dạng cầu lửa | `hero-projectile.md` | YT t=75 + animlibrary `Projectile 25` (đã xem ảnh) |
| `NovaProjectile` | Bắn đạn và có trail xanh dương | `hero-projectile.md` | animlibrary `Projectile 6` (đã xem ảnh) |
| `NovaCast_1/2/3` | Bắn một tia laser, 3 màu xanh dương / tím / đỏ, có hiệu ứng tại điểm va chạm | `laser-beam.md` | YT 1WCHyUvPaxA (video hướng dẫn laser) |

`NovaCast_1/2/3` = xanh dương / tím / đỏ, đặt theo `_1/_2/_3` của Druid (đề xuất, chờ art lead).

## Đã xem ref gì (và chưa xem được gì)

- **Đã xem hình:** `Projectile 25` (khối lửa thuôn, thân cam–vàng có vân tối, đuôi đỏ cam loe sau) và `Projectile 6` (vệt mảnh trắng viền xanh nhạt). Ảnh: `ref/`.
- **Chưa xem được hình:** các video YouTube (Linux không có `ffmpeg`; `yt-dlp` bị chặn định dạng). Tạo hình HandFlame / PyroCast / Laser là **giả định** từ brief + tiêu đề video. **Cần art lead** gửi ảnh chụp các mốc t=21 / 40 / 75 của video Lina và ảnh chính video laser, hoặc xác nhận.
- Prefab `Projectile 25/6` của animlibrary **chưa đọc sâu** (module, shader, mesh); v1 làm theo hình ảnh, không theo số của họ.

## Không gian (đề xuất, art lead chưa xác nhận; làm theo đề xuất)

- Ngữ cảnh **air** (lơ lửng). Camera 3/4 nhìn xuống 40° (preview chụp từ bên hông, cao hơn). Nhân vật cao 2 m; gốc prefab = tay / nòng ở cao ~1,25 m; +Z local = hướng bắn.
- Quy mô: lửa tay ~0,3 m cao / tay (một prefab = một tay, dev tạo hai bản); cầu lửa ~0,5 m + đuôi ~1 m; sóng lửa nón dài ~4 m, rộng ~3 m ở đầu xa, tổng ~1,3 s (tụ 0,25 s); đạn Nova mảnh dài ~1,5 m + trail; laser dài 8 m, ~1,4 s, rộng lõi 0,2 m / viền 0,9 m.
- Không dùng Horizontal / Vertical Billboard. Thân đạn / tia / tia lửa / lửa sóng = **Stretched Billboard** (đầu = mép TRÁI); lửa tay và glow = Billboard.
- **Phát hiện kỹ thuật:** Stretched Billboard có **đầu tại vị trí hạt, thân kéo ngược về sau**. Tia laser nên đặt hạt ở cuối tia (z = 8 m) để tia trải 0→8 m. (Ghi vào `hero-projectile.md` / `laser-beam.md` mục Lỗi đã gặp.)
- Đạn = **loop + dev di chuyển root**: thân Local (một hạt, vận tốc +Z 0,01 chỉ để có hướng), đuôi ribbon (Trails, World) và tàn (World, rate over distance). Đứng yên thì chỉ thấy thân + tàn, không có đuôi.
- Model Pyro / Nova chưa có trong runner6 (anim đang order). Khi có thì gắn vào xương bàn tay / nòng.

## Bất biến và kết quả đối chiếu preview (tự kiểm, chưa phải review)

| Prefab | Bất biến | Preview |
|---|---|---|
| VFXHandFlame | dính tay; thấy lưỡi lửa; ~0,3 m; lặp mượt | Thấy lưỡi lửa bốc lên, bầu cam ở gốc; quầng glow dưới. Một tay. Cần xem lặp mượt trong Unity. |
| VFXPyroCast | nón mở rộng theo hướng bắn; có bước tụ; một lần; ~4 m | Có tụ (0,15–0,3 s), quạt lửa mở rộng ra ~4 m rồi tan hết trước 1,6 s. |
| VFXPyroProjectile | thân lửa thuôn đầu hướng bay + đuôi đỏ liền; bay thẳng | Đầu sáng vàng + đuôi cam đỏ mềm (đã bỏ mép cắt vuông), đầu dẫn đúng hướng. |
| NovaProjectile | vệt mảnh trắng viền xanh + trail xanh dương liền | Vệt mảnh trắng-xanh + trail xanh liền. Hơi mảnh ở camera xa. |
| NovaCast_1/2/3 | tia thẳng liền, lõi trắng + viền màu, chớp ở nòng, hiệu ứng ở điểm va chạm; ba màu cùng hình | Tia liền 0→8 m, chớp + sao ở nòng, chớp + sao + tia lửa văng ở đích; ba màu cùng hình. |

Điểm yếu tự biết: Pyro cast và đạn chưa thấy rõ "vân nhiễu tối" như ref Projectile 25 (texture lửa không có); chưa có khói; `NovaCast` chưa có vòng sóng ở đích; chỉ xem 1 góc camera; chưa chạy trong Unity của runner6 (màu / render có thể lệch nhẹ).

## Texture (Luật chọn: yêu cầu → LIBRARY.md → contact sheet → props → chốt)

Ảnh copy / resize vào `runner6/Assets/VFX_Library/Textures/` (prefix `PN_`); Library gốc không đổi. Script: `Source/prep_tex.py`. Shader: `Mobile/Particles/Additive` (một pass).

| Thành phần | Ảnh chọn | Lý do | Đã loại (vì sao) |
|---|---|---|---|
| Lưỡi lửa thân đạn + sóng (có hướng, loop, màu cam) | `FX_TX_Fire_FireLoop_03_4x4.png` (rpg-game, art lead, `RPG_VFX/Duong/Texture/Flipbooks/Fire/`) → `PN_FireLoop` 1024×512, lưới 4×4 | bầu sáng dẫn đầu ở mép TRÁI, đuôi cam phải = đúng quy ước Stretched; có màu, alpha thật | `FireLoop_01` (cục trắng, không phải lửa cam), `FireLoop_04` (xám) |
| Lửa tay (bốc lên, loop) | cùng `FireLoop_03`, mỗi ô xoay 90° CCW → `PN_FireRise` 512×1024 (ô 128×256) | bầu ở dưới, đuôi bốc lên, không cần xoay lúc chạy; ít hạt, đặt đúng hướng (sheet có hướng) | xoay lúc chạy (dấu quay Billboard không chắc) |
| Đầu sóng lửa (lưỡi liềm bung rồi tan, một lần) | `FX_TX_Fire_DirectionalFlame_01_4x4.png` (rpg-game) → `PN_FireBurst` 1024×1024 | lưỡi liềm mũi dẫn đầu bên trái, bung rồi tan trong 16 khung; có màu | `DirectionalFlame_03` (xám), `FireSlash_*` (xám, dạng chém) |
| Quầng glow (nòng, đích, lõi, đạn) | `glow/soft_round/glow_soft_round_004` → `PN_Glow` 256² | alpha thật, xám, `edge_touch=0`, omni (tint được), tâm sáng + vầng mềm | `_013` / `_014` (đĩa phẳng, hiện thành "bong bóng"), `_007` (nền đen) |
| Tàn / chấm sáng | `glow/soft_round/glow_soft_round_002` → `PN_Dot` 64² | chấm nhỏ alpha thật | |
| Thân đạn Nova, tia lửa, hạt chạy dọc tia | `spark/streak/spark_streak_001` → `PN_Streak` 256² | đầu tròn ở TRÁI, đuôi nhọn; xám (tint); dir → dùng đơn / Stretched đúng hướng; nền đen → chỉ Additive (đúng) | `_002` (đầu ở phải), `_004` (đầu mũi tên bên phải), `trail_streak_012` (khối trắng đặc, trong "Sai vai trò đã biết") |
| Chớp sao ở nòng và đích | `spark/star/spark_star_004` → `PN_Star` 256² | sao 4 cánh mảnh dài, alpha thật | `_001` (cánh cong dày), `_005` (nền đen) |
| Ribbon đuôi + **thân tia laser** | **`PN_BeamBody` tạo mới** (32×128, gradient ngang: sáng giữa, mờ dần ra hai mép dọc, U không đổi) | `Library/beam` chỉ có `beam_001` (cột sáng **đứng** đầu tròn), không hợp thân tia ngang; không có 1D gradient alpha ngang trong `mask/gradient` (alpha thật, không viền) cho cả ribbon lẫn tia | `beam_001` (đứng, đầu tròn) |

`tools/check_texture_plan.py` chỉ quét builder trong `Assets/VFX/*/Editor/`; builder này nằm ở runner6 nên chưa chạy được; các ảnh Library ở bảng trên đã đối chiếu tay với `library_props.csv`.

## Cách dựng (đã chạy)

- Builder: `Source/PyroNovaBuild.cs` (menu `VFX/PyroNova/Build All`, dựng 7 prefab + 8 material). Không có trong runner6 (chỉ trong project tạm `/tmp/pn_proj`, dựng lại từ `Source/` + texture); preview: `Source/PnPreview.cs`, ra `Preview/<Tên>.png` (nhân vật 2 m làm thước, tay ở 1,25 m, Linear).
- Chạy: `Unity -batchmode -projectPath /tmp/pn_proj -executeMethod VfxLibrary.PyroNova.PnPreview.RunAll` (project tạm cần `Packages/manifest.json` chỉ có module Unity; Unity chạy được cạnh runner6 đang mở).
- Chép sang runner6 (`cp` giữ GUID): 8 texture + 8 material + 7 prefab (kèm `.meta`).
- Sort order không trùng trong mỗi prefab; Scaling Mode Hierarchy; Frame over Time tuyến tính; không Horizontal / Vertical Billboard.

## Bàn giao (art lead cần làm / quyết)

1. Mở `VFX_Scene`, chọn `PyroNova_VFX` trong Hierarchy, Play để xem (cast / laser chạy một lần lúc bắt đầu; chọn từng instance rồi bấm Restart trong cửa sổ Particle Effect để chạy lại). Bố cục: laser 3 màu ở cột trái, cast / cầu lửa / đạn / lửa tay ở cột phải, mọi cái xoay Y 90° (bắn +X) để camera của scene (đứng ở z = −10 nhìn +Z) thấy từ bên hông.
2. Xác nhận không gian + gửi ảnh ref video (mục trên).
3. Quyết: hit riêng cho đạn (brief không yêu cầu, chưa làm); một prefab hai tay hay hai prefab; tên `NovaCast_1/2/3`.

## Không làm trong v1

- Hit / impact riêng của cầu lửa và đạn Nova (brief chỉ yêu cầu laser có impact). Không có animation di chuyển cho đạn trong scene (ribbon sẽ lỗi khi dịch chuyển tức thời lúc lặp); kéo root trong Scene view lúc Play để xem đuôi.
- Ánh sáng / đèn động, khói, flipbook nhiễu, dịch chuyển nhiệt.
