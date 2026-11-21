# VFX_ElectricBolt: kế hoạch v2, code + shader (duyệt 2026-11-09)

Art lead: "tôi muốn làm hoàn toàn bằng code và shader" → bỏ mọi texture (kể cả Library). Không gian, timing, màu giữ như v1 (bên dưới).

| ID | Layer | Timing (s) | Carrier | Shader |
|---|---|---|---|---|
| L1 | HandGlow (root) | 0–0.14 | Billboard 0.8 m | `VFX/FX/Glow Star` (tròn) |
| L2 | Bolt | quét A→B 0–0.05 (Custom1.z), đổi hình 12 lần/s, mảnh dần + đứt khúc tới 0.32 (Custom1.x) | Stretched 1.6 × 8 m, hạt ở tay bay ngược rất chậm | `VFX/FX/Electric Bolt` (mới) |
| L2b | Bolt2 | 0.1–0.34, mảnh, xanh đậm hơn, 15 lần/s | như L2 | `VFX/FX/Electric Bolt` |
| L3 | SideArcs | ~12 cung 0.03–0.33 | Stretched 0.8–1.2 m (aspect 2), hướng ngẫu nhiên | `VFX/FX/Electric Bolt` |
| L4 | ImpactFlash | 0.04–0.18 tại B | Billboard 1.6 m | `VFX/FX/Glow Star` |
| L5 | ImpactStar | 0.05–0.14 | Billboard 1.4 m | `VFX/FX/Glow Star` + `_STAR` |
| L6 | ImpactArcs | 4–6 cung quanh B, 0.05–0.35 | Billboard 0.6–1.0 m (aspect 1), xoay ngẫu nhiên | `VFX/FX/Electric Bolt` |
| L7 | Sparks | 12 tia 0.04–0.34 | Stretched, pivot (0,1,0) | `VFX/FX/Spark` (dùng lại) |

Thứ tự vẽ: SideArcs 1, ImpactArcs 2, Bolt2 3, Bolt 4, Sparks 5, HandGlow 6, ImpactFlash 7, ImpactStar 8.
Chi phí: 0 texture sample ở mọi lớp; Electric Bolt ~10 hash (frac/mul), target 3.0 (fwidth). 8 Particle System, 8 material.
Đã kiểm từ preview v1: quad Stretched kéo từ tay về phía B (đúng hướng). Nếu tia quét ngược: bật `_Flip` trên material.

---

## v1 (thay bằng v2): texture Library + Lightning_CustomBlend

Không gian: air (dir) · tia ngang A→B = Stretched Billboard (texture ngang, quad kéo từ tay ra), chớp / spark = Billboard · camera 3/4 nhìn xuống 40° · neo = tay (A, cao 1.3 m), mục tiêu B cách 8 m theo +Z · nền Showcase (focus z 4).
Đã chốt: tia nối A→B, 8 m tay → ngực, một phát 0.4 s, xanh-trắng toon cứng, 3/4 40°. Đề xuất: B cùng cao 1.3 m, các lớp phụ bên dưới.
Thời lượng: ~0.45 s · Art Style: toon nét cứng, lõi trắng viền xanh lam.

Tham khảo (chi tiết: `Research.md`): 80.lv Sokolov (tia nối đầu-cuối thẳng hàng, tắt Start Rotation, mảnh dần khi tắt), Real Time VFX (mép texture trống, Clamp), MinionsArt (Custom Data cắt dần thân tia).

| ID | Layer | Vai trò & timing (s) | Carrier | Shader | Texture | Kết thúc |
|---|---|---|---|---|---|---|
| L1 | HandGlow (root) | sáng ở tay lúc phóng, 0–0.14 | Billboard 0.8 m | `Mobile/Particles/Additive` | `glow/soft_round/glow_soft_round_004` | mờ nhanh |
| L2 | Bolt | thân tia: dài ra từ tay 0–0.05, đổi 4 khung trong 0.32, nháy sáng-tối, mảnh dần; tia thứ hai (khung khác, mảnh hơn) ở t=0.1 | Stretched 1.6 × 8 m (lengthScale 5), hạt ở tay, bay ngược rất chậm để quad kéo về B | dùng lại `Particles/Lightning_CustomBlend` (Speed 0, Custom1.y = 0): cắt theo độ sáng → nét cứng; ramp → viền xanh, lõi trắng | `lightning/bolt_sheet/lightning_bolt_sheet_001` (1×4) + `T_ElectricBolt_Ramp` (mới) | Custom1.x 0.12 → 0.95 |
| L3 | SideArcs | ~12 cung điện nhỏ dọc thân, đời 0.06–0.12, phát 0.03–0.33 | Stretched 0.8–1.2 m, Box dài 7.5 m, hướng ngẫu nhiên | Additive | `lightning/arc_sheet/lightning_arc_sheet_003` (3×3, khung random) | tắt theo đời |
| L4 | ImpactFlash | chớp Impact duy nhất tại B, 0.04–0.18 | Billboard 1.6 m | Additive | `glow/soft_round/glow_soft_round_005` | phình rồi tắt |
| L5 | ImpactStar | sao gai toon tại B, 0.05–0.14 | Billboard 1.2 m, xoay random | Additive | `impact/flash_spiky/impact_flash_spiky_012` | co lại |
| L6 | ImpactArcs | 4–6 cung cuộn quanh B, 0.05–0.35 | Billboard 0.6–1.0 m, xoay random (cung cuộn đọc rõ hơn Stretched) | Additive | `lightning/arc_sheet/lightning_arc_sheet_006` (4×4, khung random) | tắt theo đời |
| L7 | Sparks | 12 tia lửa văng tại B, 4–8 m/s, đời 0.15–0.3, trọng lực nhẹ | Stretched, pivot (0,1,0) | Additive | `spark/streak/spark_streak_001` | thu nhỏ |

Tia thứ hai của L2 dựng thành lớp riêng `Bolt2` (cutoff gốc 0.3, tối hơn, offset ramp −0.08 nên xanh hơn), vì độ dài tia gắn với size nên không thể làm mảnh bằng size.

Thứ tự vẽ: SideArcs 1, ImpactArcs 2, Bolt2 3, Bolt 4, Sparks 5, HandGlow 6, ImpactFlash 7, ImpactStar 8.

Builder: `Assets/VFX/ElectricBolt/Editor/ElectricBoltBuild.cs` (menu `VFX/ElectricBolt/Build`).

Khác với: LightningStrike / VioletThunder (sét từ trời xuống đất, có lớp nằm đất). Bản này: **bố cục** ngang A→B trên không; **timing** không tích điện, dài ra 0.05 s rồi nháy và mảnh dần; **lớp phụ** cung điện dọc thân + cung cuộn tại điểm trúng, không lớp đất; màu xanh-trắng.

Shader: không viết mới. Ngân sách: 7 Particle System, ~30 hạt lúc cao nhất, 7 material, 1 texture mới (ramp 256×4; Library không có ramp xanh, `Gradient_lightning` màu cam).

Giả định: A, B cố định 8 m (chưa có script nối mục tiêu thật lúc chạy game). Sáng ở tay không tính là chớp Impact.
