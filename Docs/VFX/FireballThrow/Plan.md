# VFX_FireballThrow — kế hoạch v1 (art lead "làm và ghép vào scene showcase", 2026-11-05)

Quả cầu lửa ném từ tay theo vòng cung, rơi vào chân mục tiêu rồi phát nổ. Một prefab tự chạy trọn vòng (bay → chạm → nổ), không cần script: thân cầu là một hạt có vận tốc vẽ cung, hạt chết lúc chạm đất thì kích các lớp nổ (sub-emitter Death).

Không gian: bay (dir) + nổ ground · thân Stretched Billboard theo hướng bay, nổ Billboard đứng · camera 3/4 40° · neo: pivot = tay người ném, bay theo +Z (forward) · cầu 0.6 m, nổ ~2.5 m · nền lẫn (đã chốt: bay cong rơi vào chân, cầu 0.6 m / nổ 2.5 m, ~8 m trong 0.8 s, Stylized toon, 3/4 40°; đề xuất: điểm ném cao 1.2 m, đỉnh cung 2.2 m)
Thời lượng: ~2.2 s (chạm đất 0.8 s) · Art Style: Stylized toon, cam-vàng-trắng, khói than

| ID | Layer | Vai trò & timing (s) | Carrier | Shader | Texture | Kết thúc |
|---|---|---|---|---|---|---|
| L1 | Body (root) | thân cầu lửa + đuôi lửa ngắn, 0–0.8 | 1 hạt, Stretched Billboard theo vận tốc (đầu = mép trái), 0.75 m × 2.25 m | dùng lại `VFX/FX/Meteor` (crust thấp) | noise `T_Noise_Streaks` | chết khi chạm đất → kích L4–L7 |
| L2 | Core | lõi sáng nhấp nháy, 0–0.8 | 1 hạt Billboard, cùng quỹ đạo L1 | stock Additive | `glow/glow_022` | tắt khi chạm |
| L3 | Trail | đuôi trail cam → đỏ, sống 0.2 s | Trails module của L2 (World) | stock Additive | `trail/trail_027` | mờ dần sau khi chạm |
| L4 | Flash | một chớp Impact, 0.8–0.95 | Billboard ~2.6 m | stock Additive | `impact/impact_018.psd` | co + tắt |
| L5 | FireBurst | khối glow lửa nóng → cam → đỏ, 0.8–1.25 | Billboard ~2.2 m, cao 0.8 m | stock Additive | `glow/glow_085` | tắt |
| L6 | Sparks | 12 tia lửa comet bắn lên rồi rơi, 0.8–1.35 | Stretched (đầu trái) | stock Additive | `glow/glow_072` | co lại |
| L8 | FlameLicks (v2) | cụm lửa toon sôi khỏi đầu cầu, xoay, vàng → cam → đỏ, co lại; 80/s, 0–0.8 | Billboard, Birth sub-emitter (World) | stock Alpha Blended | `smoke/smoke_007` (2×2, khung ngẫu nhiên) | co + tắt |
| L9 | TrailSmoke (v2) | khói xám đậm để lại dọc cung, ấm sát cầu → xám, nở, bay lên; 55/s, sống ~1 s | Billboard, Birth sub-emitter | stock Alpha Blended (luật khói mặc định) | `Assets/VFX/fx_t_smoke_02.png`, Start Color | mờ dần |
| L10 | Embers (v2) | tàn lửa rơi khỏi cầu, noise; 28/s | Billboard, Birth sub-emitter | dùng chung M_Core | `glow/glow_022` | co + tắt |
| L7 | Smoke | khói vụ nổ: ~14 cầu ăn mòn, cháy → gân → than → tan sợi, 0.8–2.1 | Mesh `SM_VFX_SphereUV` | dùng lại `VFX/FX/Erode Sphere` | mask + ramp của GroundBlast | ăn mòn thành sợi |

Khác với bản nào: FireballImpact cũ (đã xoá 2026-11-05) rơi chéo từ trời, nổ bằng quad `Blast` + vòng + vết cháy. Bản này: **bố cục** (ném vòng cung từ tay), **lớp phụ** (trail ribbon, khói khối cầu thay quad khói, không vòng / vết cháy), **timing** (0.8 s bay, nổ ngắn). GroundBlast: khói cùng kỹ thuật nhưng nhỏ hơn ~0.6×, 14 cầu thay 30.

Shader: không viết mới, không mở rộng. Ngân sách: ~32 hạt, 7 material, mọi texture từ Library / GroundBlast.

Giả định: chạm đất theo thời gian (0.8 s), không dùng va chạm vật lý; trong game, dev có thể tách L1–L3 (bay) và L4–L7 (nổ). Showcase: xoay instance Y 90° để bay ngang màn hình.

## v2 (2026-11-05) — art lead: "quả cầu lửa trông đơn giản quá, không có khói trail, phần đầu lửa quá tĩnh"
- Thêm L8 FlameLicks, L9 TrailSmoke, L10 Embers (sinh liên tục dọc đường bay bằng sub-emitter Birth).
- Đầu cầu (L1): vỏ ăn mòn 0.1 → 0.3, vân tối 0.12 → 0.25, noise chạy nhanh gấp ~2–4 lần, lắc đuôi 0.08 → 0.18.
- Thứ tự vẽ: TrailSmoke 0, Smoke 1, FlameLicks 2, Body 3, Core + trail 4, Embers 5, FireBurst 6, Sparks 7, Flash 8. Ngân sách ~130 hạt, 9 material.

## v3 (2026-11-13) — art lead: "shader smoke, thêm burn dissolve, kiểu vệt cháy ở cạnh của khói"
- Khói vụ nổ (L7, `VFX/FX/Erode Sphere`) trước đó chỉ sáng ở các **gân bên trong** (ngưỡng nhiệt Custom1.y), không có gì phát sáng ở **rìa đang tan** (ngưỡng alpha Custom1.x).
- Mở rộng shader (v5): thuộc tính mới `_BurnWidth`. Ngay phía trong ngưỡng alpha, dải rộng `_BurnWidth` (theo đơn vị mask) được tô: sát mép = vàng sáng (đầu ramp nhiệt), vào trong = cam → đỏ sẫm, rồi dải **than tối** phía sau, trước khi tới màu khói. Vệt chạy theo Custom1.x nên **di chuyển cùng với lúc khói tan**. Màu lấy từ ramp có sẵn (`T_GroundBlast_SmokeRamp`), không thêm thuộc tính màu. Mặc định 0 (tắt) nên GroundBlast / MushroomBlast không đổi.
- **Art lead 2026-11-13: lấy lại setting cũ của prefab, chỉ giữ shader đã sửa.** Builder `FireballThrowBuild.cs` đã bỏ dòng bật `_BurnWidth`, prefab và material `M_FireballThrow_Smoke_Alpha` giữ nguyên như trước (`_BurnWidth` = 0 = tắt). Muốn bật lại: thêm `mSmoke.SetFloat("_BurnWidth", 0.12f);` sau `_Lumps`. Khói đuôi (L9 TrailSmoke, shader stock + `fx_t_smoke_02`) **không đổi** (không có ăn mòn).
- Không gian, bất biến, timing của effect giữ nguyên. Frost / Poison không dùng shader này nên không đổi.
- Chưa xác minh: shader mới chưa từng được xem chạy (chưa build prefab với `_BurnWidth` > 0). Khi bật: xem frame 0.85–1.8 s, chỉnh `_BurnWidth` (0,06–0,2) và `_EmisBoost`.
