# Electric Bolt – research cách làm (2026-11-09)

Research nhanh (bước 2b của `/vfx-shader`) trước khi dựng effect "electric bolt". Chưa dựng gì, chưa chốt không gian.
Đọc kèm: `.claude/skills/vfx-shader/references/lightning.md`, `thunder-core.md`, `lightning-set.md` (những gì đã học từ rpg-game) — file này chỉ ghi phần **mới** từ nguồn ngoài.

## "Electric bolt" có 2 nghĩa – cần art lead chọn
| Kiểu | Mô tả | Gần effect nào đã có |
|---|---|---|
| **A. Bolt projectile** | quả cầu / mũi điện bay từ tay tới mục tiêu, có đuôi hồ quang, nổ điện khi trúng | FireballThrow (cấu trúc bay + nổ), LightningTrail (đuôi) |
| **B. Bolt nối A→B** (arc / chain) | tia điện giật thẳng từ điểm A tới điểm B (tay → địch), chớp nháy 0.3–0.5 s | chưa có (LightningStrike / VioletThunder là từ trời xuống đất) |

## 4 kỹ thuật tạo thân tia (từ nguồn)
| # | Kỹ thuật | Cách làm | Hợp với | Ghi chú |
|---|---|---|---|---|
| 1 | **Sprite sheet + Stretched / velocity aligned** | Sheet vài tia khác nhau; pivot lệch về một đầu, aligned theo velocity với speed rất nhỏ để tia "đứng yên" trong không gian; đời 0.3–0.4 s; đổi frame 1 lần trong đời (ví dụ 0.2 s) | A (hồ quang quanh lõi), B ngắn | Đúng luật dự án: Stretched, hướng bay = mép trái, pivot (0,1,0) khi có speed. **Tắt Start Rotation random** (lỗi hay gặp). |
| 2 | **Ribbon / strip mesh + UV** | Dải mesh UV kín chiều dọc; texture Clamp, mép ảnh trống; texture chiếm 1/N chiều dài rồi cuộn U để tia "chạy"; cuộn V theo bước (floor(time)) để đổi frame | B (A→B), đuôi của A | rpg-game đã làm thế với `Lightning_CustomBlend` (cutoff Custom1 quét dọc thân). Texture tia nối phải **đầu và cuối nằm cùng một đường** để kéo dài / ghép được. |
| 3 | **3 tia trong 3 kênh RGB** | 1 texture nhỏ chứa 3 tia ở R/G/B; shader `dot(tex, mask)`, mask chọn ngẫu nhiên theo `frac(time*0.618)` (tỉ lệ vàng), thêm mask (0,0,0) để có lúc tia biến mất → nhấp nháy | B, A | Tiết kiệm texture, nháy kiểu điện thật. Cần shader mới (nhẹ, một pass) hoặc mở rộng `Lightning_CustomBlend`. |
| 4 | **Procedural (midpoint displacement) bằng code** | Chia đoạn A→B, đẩy điểm giữa lệch ngẫu nhiên, lặp; thêm nhánh; vẽ bằng LineRenderer / mesh, tạo lại mỗi 0.05–0.1 s | B | Keijiro SpektrLightning (MIT): chỉ vẽ đoạn thẳng, **cần HDR bloom** mới đẹp → kém hợp mobile / toon. Có thể dùng `/vfx-code` (`fxlib` có sét) để **bake** ra sheet thay vì chạy runtime. |

Mẹo chung:
- **Wobble bằng UV distortion** (noise) + **gradient mask** để gốc tia không rung, chỉ thân / ngọn rung (80.lv, Sokolov).
- Tắt tia bằng cách **làm mảnh dần** (pow / cutoff) chứ không chỉ fade alpha.
- Nháy emissive ở đầu đời (flash) rồi tắt nhanh; đời ngắn.
- Mesh tia "xoắn chéo nhiều mặt phẳng" (cross-planar) để nhìn được từ nhiều góc (breakdown UE5 Lightning Bolt Hit).
- MinionsArt: mesh particle + texture distance field (SDF) + Custom Data → một texture mà cho nhiều độ dày / cắt dần.
- Gia vị: spark, flare, đèn — "đừng nêm quá tay".

## Bộ lớp đề xuất (*đề xuất*, chờ chốt)
### A. Bolt projectile (bay ~8 m / 0.4–0.6 s, ngữ cảnh air → trúng)
| Lớp | Kỹ thuật | Texture (Library) |
|---|---|---|
| Lõi sáng | Billboard additive, scale nháy nhẹ | `glow/` |
| Hồ quang quanh lõi | #1 Stretched, 5–8 tia/0.1 s, đời 0.1–0.2 s, start frame random | `lightning/arc_sheet` |
| Đuôi | #2 strip mesh World space (như LightningTrail) hoặc Trails module | `lightning/arc_single`, `trail/` |
| Tia lửa rơi rớt | Stretched nhỏ, gravity nhẹ | `spark/streak` |
| Trúng | sub-emitter Death: 1 chớp Impact + vành + hồ quang bắn tung + spark (auto mix nếu là đòn trúng) | `impact/`, `ring/`, `lightning/bolt_sheet` |

### B. Bolt nối A→B (dài 6–10 m, 0.4 s)
| Lớp | Kỹ thuật | Texture |
|---|---|---|
| Thân tia chính | #2 strip mesh A→B, cutoff quét A→B rồi mảnh dần; 2–3 tia chồng, đổi frame 2 lần | `lightning/bolt_sheet` (chọn tia đầu-cuối thẳng hàng) |
| Tia phụ nháy | #1 hoặc #3, lệch nhẹ quanh thân | `lightning/arc_sheet` |
| Chớp đầu (tay) + chớp cuối (mục tiêu) | Billboard flash 0.1–0.15 s | `glow/`, `impact/` |
| Spark tại điểm trúng | Stretched burst | `spark/streak` |

Không dùng Horizontal / Vertical Billboard; Frame over Time tuyến tính; Scaling Mode Hierarchy; texture lấy từ `Assets/Library/` (xem ảnh trước khi chốt).

## Cần art lead chốt trước khi dựng
1. Kiểu **A (projectile)** hay **B (tia nối A→B)**?
2. Quy mô / khoảng cách (đề xuất 8 m), thời gian (đề xuất 0.5 s), màu (vàng-trắng như rpg-game hay xanh-trắng?).
3. Phong cách: toon nét cứng (như VioletThunder) hay mềm có glow?
4. Camera: mặc định 3/4, nhìn xuống 40° — giữ?

## Tham khảo
| Nguồn | Học được |
|---|---|
| [80.lv – Dmitrii Sokolov, Lightning UE5](https://80.lv/articles/how-to-set-up-lightning-effects-with-unreal-engine-5) | 3 cách: sheet velocity aligned, tia nối tile được, 3 tia trong RGB + golden ratio; UV distortion + gradient mask; đời 0.3–0.4 s |
| [Real Time VFX – Scrolling flipbook](https://realtimevfx.com/t/scrolling-flipbook/15638) | Ribbon UV kín dọc, Clamp, mép ảnh trống, repeat U ~15 + offset để chạy, V theo floor(time) để đổi frame |
| [MinionsArt – Lightning / Shock particles](https://minionsart.github.io/tutorials/Posts.html?post=lightning_shock_particles) ([video](https://www.youtube.com/watch?v=NMTXHnsxgss)) | Mesh particle + SDF texture + Custom Data (bài chi tiết nằm sau Patreon, chưa đọc được) |
| [keijiro/SpektrLightning](https://github.com/keijiro/SpektrLightning) (MIT) | Tia procedural giữa 2 điểm bằng line shader; cần HDR bloom |
| [YouTube – Lightning Bolt Hit FX UE5.4](https://www.youtube.com/watch?v=sQz90u31nzY) | Mesh xoắn chéo nhiều mặt phẳng + noise WPO + erosion (chỉ đọc mô tả) |
| [SahilK-027/Lightning-VFX](https://github.com/SahilK-027/Lightning-VFX) (MIT, Three.js) | Bolt procedural + nứt đất + spark + rung camera |
