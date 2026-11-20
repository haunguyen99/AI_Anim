# VFX_FireballThrow: biến thể Poison và Frost (2026-11-09)

Art lead: "tự chọn nguyên tố + chất liệu". Cùng hành vi với `Plan.md`: ném từ tay (pivot, cao 1.2 m) vòng cung 8 m về +Z, chạm chân mục tiêu (bóng cao 0.3 m) rồi nổ. Một prefab tự chạy, thân = hạt gốc, chết khi chạm thì kích lớp nổ (sub-emitter Death), lớp bay là sub-emitter Birth. Khung giống bản gốc: Showcase xoay instance Y 90°, `focusOffset` z 4 vẫn dùng được. Không viết shader mới.

Không gian (giữ như gốc): bay (dir) + nổ ground · camera 3/4 40° · thân Stretched Billboard (Poison) hoặc mesh xoay 3D (Frost) · nằm đất = Billboard + Render Alignment Local, GameObject X 90 (vết độc, vòng sương giá) · mọi ParticleSystem Scaling Mode Hierarchy · không Horizontal / Vertical Billboard.

Builder: `Assets/VFX/FireballThrow/Editor/FireballThrowPoisonBuild.cs` (menu `VFX/FireballThrow/Build Poison`) và `FireballThrowFrostBuild.cs` (`VFX/FireballThrow/Build Frost`). Prefab: `Prefabs/VFX_FireballThrow_Poison.prefab`, `VFX_FireballThrow_Frost.prefab`. Preview + BuildReport: `Docs/VFX/FireballThrow_Poison/`, `Docs/VFX/FireballThrow_Frost/`.

## So với bản gốc (lửa) và hai bản kia

| Trục | Gốc (Fire) | Poison | Frost |
|---|---|---|---|
| Layout / quỹ đạo | 0.8 s, đỉnh 2.2 m | **lob cao** 1.0 s, đỉnh 3.4 m (Vy0 9.623, G 21.046, +Z 8 m/s) | **phẳng nhanh** 0.65 s, đỉnh 1.9 m (Vy0 5.411, G 20.908, +Z 12.31 m/s) |
| Timing | nổ ~1.3 s sau chạm | khí độc nở chậm, ở lại ~2.2 s sau chạm; chớp ngắn 0.12 s | vỡ nhanh: vòng 0.5 s, mảnh 1.1 s, kết thúc ~1.7 s |
| Mesh | quad Meteor + 14 cầu ăn mòn (Erode Sphere) | quad Meteor (đuôi ngắn nhớt) + billboard, không cầu | **mesh tinh thể** `SM_VFX_Debris_Crystal_01` (thân, xoay 3D), `Small_Crystal_02` (14 mảnh vỡ), `Small_Crystal_04` (vụn); shader `Rock Facet` + MatCap như IceSpike Ice |
| Lớp phụ | FlameLicks, TrailSmoke, Embers, trail ribbon, Sparks, FireBurst, Smoke cầu | Drips (giọt rơi), Bubbles (bọt), TrailGas (khí nặng, chìm), GasBurst, **Splat** (vết độc trên đất), Globs; bỏ ribbon, embers, sparks | Trail mỏng + Glints (sao lấp lánh), FrostMist, Chips (vụn băng, mesh), FrostRing (vòng sương giá trên đất), Shards (mesh), Mist, Glitter; bỏ ribbon dày, lửa |

Mỗi bản khác gốc ở ≥ 3 trục (layout, timing, lớp phụ; Frost thêm mesh).

Số chính:
- Poison: thân 0.8 m Stretched (lengthScale 3), `VFX/FX/Meteor` màu xanh độc (`_TailLength` 2.0, `_CrustAmount` 0.38, noise chạy chậm), Core `glow_soft_round_007`; khí = `fx_t_smoke_02` + shader mobile mặc định (không phải nổ lửa nên không dùng Erode Sphere); Splat = `ground/splat/ground_splat_002` 2.8 m (đổi 2026-11-09: `water_splash_002` là ảnh bắn nước nhìn ngang, nằm đất bị có hướng trên/dưới); bọt = `water_bubble_004`; chớp = `impact_flash_spiky_001`. Thứ tự vẽ: Splat 0, TrailGas 1, GasBurst 2, Drips 3, Body 4, Core 5, Bubbles 6, Globs 7, Flash 8. ~120 hạt, 8 material.
- Frost: thân mesh 0.7 m (kích thước chuẩn hoá theo cạnh dài nhất của mesh), xoay ±9 rad/s; palette + MatCap = bản copy của IceSpike (`Textures/T_FireballThrow_Frost_Palette.tga`, `_MatCap.png`); vòng = `impact_radial_ring_004` 3.6 m; sao = `spark_star_002`; trail = `trail_streak_012`. Thứ tự vẽ: FrostRing 0, FrostMist 1, Mist 2, Chips 3, Body 4, Core + trail 6 (mesh thân 5), Glints 7, Shards 8, Flash 9, Glitter 10. ~140 hạt, 7 material.

Texture: toàn bộ từ `Assets/Library/` (đường dẫn mới theo thư mục con) + `fx_t_smoke_02`; không tạo texture mới.

Chưa kiểm chứng (Unity đang mở, không build batch): chưa chạy build, chưa xem preview. Bounds của mesh Frost được log lúc build (`[FireballThrow_Frost] mesh bounds`); mesh xoay 3D nên trục mesh không ảnh hưởng. Cần xem Review Lab: độ sáng MatCap của thân, đuôi Meteor của Poison.

## Poison body có khối (2026-11-09)
Art lead: "body trông flat quá". Đầu cầu chỉ tô theo khoảng cách tới tâm (vòng màu đồng tâm) + lõi trắng bị cắt ngưỡng. Sửa: shader `VFX/FX/Meteor` thêm `_Volume` / `_Gloss` (pháp tuyến cầu giả, sáng từ trên theo hướng thế giới, viền tối, điểm bóng loáng; mặc định 0 nên bản Lửa / Băng không đổi); material Poison `_Volume` 1, `_Gloss` 1.1, `_CrustAmount` 0.38 -> 0.18, lõi lime thay vì trắng, lớp Core (glow cộng) nhỏ và mờ hơn.
