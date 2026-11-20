# VFX_VioletThunder — kế hoạch v1 (2026-11-05)

Sét tím-hồng từ trời đánh xuống một điểm trên đất: tích điện ngắn rồi nổ một phát.

Không gian: ground · tia đứng = Stretched Billboard (texture ngang, đầu chạm đất = mép trái), sóng nằm đất = Billboard + Local · camera 3/4 40° · neo điểm đất · tia cao ~6 m, vùng nổ ~3 m · nền lẫn (đã chốt: ground, tím-hồng stylized, ~3 m, 3/4 40°, tích điện rồi nổ một phát, lớp = tia sét + chớp + sóng nền; đề xuất: nhịp tích điện nằm trong lớp chớp, tia cao 6 m)
Thời lượng: ~1.1 s (đánh ở 0.4 s) · Art Style: stylized toon

| ID | Layer | Vai trò & timing (s) | Carrier | Shader | Texture | Kết thúc |
|---|---|---|---|---|---|---|
| L1 | Charge (root) | phần "tích" của lớp chớp: quầng hồng tụ ở điểm đánh, lớn dần + nhấp nháy, 0–0.4 | Billboard ~1.4 m | stock Additive | `glow/glow_023` | tắt khi tia đánh |
| L2 | BoltGlow | viền tím của tia, flipbook 8 khung (giáng → vỡ vụn), 0.4–0.72 | Stretched, 3.4 × 6.8 m | stock Additive | `T_VioletThunder_Bolt_2x4` (cắt lại từ `Lightnings_Electrics_026`) | vỡ vụn theo sheet |
| L3 | BoltCore | lõi trắng hồng của tia, cùng khung với L2 | Stretched, 3 × 6 m | stock Additive | như L2 | như L2 |
| L4 | Flash | một chớp khi tia chạm đất (0.44), 0.44–0.62 | Billboard ~4 m | stock Additive | `glow/glow_083` | co + tắt |
| L5 | Wave | sóng điện lan trên đất tới ~3.5 m, 0.42–0.92 | Billboard + Local (nằm đất) | stock Additive | `wave/wave_015` | mờ dần |

Khác với: LightningStrike (cột sáng vàng 25 m, top-down), ThunderImpact (tia zig-zag mảnh vàng, 3 nhịp, `Lightnings_Electrics_007`), ThunderChainImpact (sét lan 3 mục tiêu, `_025`). Bản này: **mesh/hình** (tia toon dày vẽ tay giáng xuống rồi vỡ vụn, sheet `_026`), **timing** (tích 0.4 s rồi một phát), **lớp phụ** (quầng tích điện, sóng tia toả `wave_015`), màu tím-hồng.

Shader: không viết mới, dùng `Mobile/Particles/Additive`. Ngân sách: 5 hạt, 5 material, 1 texture mới (bản cắt lại của texture Library; Library không có sheet tia nằm ngang).

Giả định: sheet 026 xoay từng khung 90° cho đúng luật Stretched (hướng giáng = mép trái).

## v2 (2026-11-05) — art lead: "phần effect trên mặt đất chưa đủ mạnh, làm impact mạnh hơn, thêm dòng điện tồn lại trên mặt đất sau impact"

| ID | Layer | Vai trò & timing (s) | Carrier | Texture |
|---|---|---|---|---|
| L4 | Flash (sửa) | 4 → 5.5 m, 2 hạt chồng, 0.22 s | Billboard | `glow/glow_083` |
| L6 | GroundFlash | vùng đất bừng sáng trắng → hồng → tím, 5.5 m, 0.44–0.84 | nằm đất (Billboard + Local) | `glow/glow_023` |
| L7 | ImpactStar | sao gai toon in trên đất, 3.6 m, 0.16 s | nằm đất | `impact/impact_092` |
| L8 | Ring | vành sóng sắc chạy trước sóng mềm, 5.2 m, 0.28 s | nằm đất | `wave/wave_004` |
| L9 | Residue | vệt điện hồng mờ tồn trên đất ~1.5 s | nằm đất | `glow/glow_023` |
| L10 | GroundArcs | dòng điện bò trên đất sau cú đánh: cung điện toon ngắn (0.12–0.24 s), mỗi hạt một hàng ngẫu nhiên của sheet 4×4, 10 hạt bùng ngay + 48/s giảm dần trong 1.4 s, rải bán kính 1.7 m | nằm đất | `T_VioletThunder_GroundArcs_4x4` (từ `Lightnings_Electrics_020`, nướng sẵn viền tím quanh lõi trắng hồng như tia) |

Thứ tự vẽ: GroundFlash −3, Residue −2, Wave −1, Ring 0, GroundArcs 1, ImpactStar 2, Charge 3, BoltGlow 4, BoltCore 5, Flash 6. Thời lượng ~1.9 s. Đèn demo Showcase: thêm đèn nhấp nháy theo GroundArcs.
