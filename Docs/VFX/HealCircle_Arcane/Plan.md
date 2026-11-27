# HealCircle_Arcane — kế hoạch (2026-11-18, order thử của anh Hậu)

Cùng hiệu ứng với HealCircle (vòng phép hồi máu bám chân, một lần, nằm đất). Pipeline Built-in (Additive mobile), Scaling Mode Hierarchy.
Không gian (*đề xuất*, brief chỉ nói "làm thử 1 VFX bất kỳ"): ground, nằm đất = Billboard + Render Alignment Local (GameObject xoay X 90°), cột đứng = Stretched Billboard (pivot 0,1,0), camera 3/4 nhìn xuống 40°, vòng ~3 m (nhân vật 2 m), bám nhân vật, nền tối, ~3.6 s.
Màu: Core `#F6E8FF` · Mid `#B66BFF` · Outer `#5B1FB0` · Magenta `#FF5FD2`.

## Bất biến (chép từ `_Anatomy/heal-circle.md`)
- Vòng phép đọc được: hai lớp xoay ngược nhau, tròn đều, nằm đất, tâm đúng giữa.
- Có chuyển động đi lên (cột sáng + hạt) = cảm giác hồi phục.
- Hình mềm, an toàn: tròn / chấm; không gai nhọn, không tối.
- Bám nhân vật, một lần ~1.5 s (Anatomy). **Arcane cố ý dài hơn: ~3.6 s và vòng 3.1 m** (timing nạp 3 nhịp; bản gốc 2.8 s) — điểm để art lead quyết.

## Khác bản gốc (≥ 2 trục, vẫn là cùng hiệu ứng)
- **Timing:** nạp 3 nhịp (t = 0.2 / 0.9 / 1.6 s), mỗi nhịp một vành sóng nở ra + sóng hạt; tổng ~3.6 s (gốc: mở một lần, 2.8 s).
- **Lớp phụ:** 6 quả cầu sáng quay quanh viền và leo xoắn lên (3 đợt) thay cho đám hạt thường.
- **Bố cục / chất liệu:** hai vòng là rune thư viện (vòng chữ + ngôi sao 5 cánh) thay cho rune vẽ script; cột sáng hẹp, cao ~3 m.

## Lớp
| # | Layer | Vai trò / timing | Kỹ thuật | sortingOrder |
|---|---|---|---|---|
| 1 | GroundGlow | quầng tím phồng theo 3 nhịp | Billboard + Local, 3.0 m | -5 |
| 2 | RuneOuter | vòng chữ mở t=0.15, xoay +18°/s | Billboard + Local, 3.1 m | -4 |
| 3 | RuneInner | ngôi sao 5 cánh mở t=0.3, xoay -50°/s | Billboard + Local, 1.9 m | -3 |
| 4 | PulseRings | 3 vành sóng nở 0.2→1.0 | Billboard + Local, burst ×3 | -2 |
| 5 | Beam | cột hẹp 1.0 m × 3 m, t=1.6 | Stretched, pivot (0,1,0) | 0 |
| 6 | Orbs | 6 cầu/đợt quay + leo, 3 đợt | Billboard, orbital Y + rise | 2 |
| 7 | Motes | bụi tím phủ đĩa, 3 đợt | Billboard, rise + noise | 3 |
| 8 | Sparkles | sao lấp lánh quanh cột | Billboard | 4 |

## Texture (từng thành phần)
| Thành phần | Thư mục tra từ `LIBRARY.md` | Ảnh chốt | Ảnh dự phòng | Đã loại (xem contact sheet `work/vfx_orders/20261118_haunv_thu1/rune_circle_contact.png`) |
|---|---|---|---|---|
| RuneOuter (vòng chữ) | `rune/circle` | `Assets/Library/rune/circle/rune_circle_003.png` (vòng chữ cổ mảnh, 1024, tròn đều) | `rune_circle_006.png` | 001 (mặt quỷ), 004 (đá, có màu), 005 (hoa = Nature), 007 (tam giác sci-fi), 009 (bông tuyết) |
| RuneInner (ngôi sao) | `rune/circle` | `Assets/Library/rune/circle/rune_circle_008.png` (sao 5 cánh trong vòng đôi, 256 → nâng 512) | `rune_circle_002.png` (đã dùng ở Holy) | như trên |
| PulseRings (vành sóng) | `ring/thin` (xem `Docs/VFX/_Library/_contact/ring_thin.png`) | `ring_thin_002.png` (vành sáng mảnh mềm, 1024, omni) | `ring_thin_011`, `_014` | 001 (rách), 003 (nhỏ), 004/007/008 (nền đen đặc, chạm mép), 005 (quá mờ), 006 (hở), 009 (quá mảnh), 010, 012 (xanh), 013 (vàng) |
| GroundGlow (quầng đất) | `glow/soft_round` (`_contact/glow_soft_round.png`) | `glow_soft_round_004.png` (512, alpha, omni, lõi sáng + quầng mềm) | `_013`, `_014` (đĩa đặc hơn) | 001 (bong bóng), 010 (cam), 027 (màu), các ảnh 128 px (mờ vỡ khi to) |
| Orbs (cầu sáng) | `glow/soft_round` | `glow_soft_round_005.png` (329→256, cầu + quầng) | `_020` | như trên |
| Motes (bụi) | `glow/soft_round` | `glow_soft_round_002.png` (128, chấm nhỏ + quầng) | `_022`, `_033` | như trên |
| Sparkles (sao 4 cánh) | `spark/star` (`_contact/spark_star.png`) | `spark_star_003.png` (256, sao mềm có quầng, omni) | `_001`, `_008` | 006 (sao 5 cánh vàng), 014 (dấu cộng), 015 (đỏ), 017 (viền xám), 010 (xám, 5 cánh) |
| Beam (cột sáng, v3) | `trail/streak` + `spark/streak` + `trail/band` + `beam` (`_contact/trail_streak.png`, `spark_streak.png`; ảnh `beam_001`, `trail_band_001`, `trail_ribbon.png` xem riêng) | `trail/streak/trail_streak_001.png` (chóp mềm: đáy phẳng rộng, ngọn nhọn, 256×128, `dir`, `edge_touch=0`) — **lật ngang** khi chép để đáy ở mép PHẢI, ngọn (đầu) ở mép TRÁI cho Stretched | `trail_streak_011` (lật ngang, mép tia xơ), `spark_streak_002` (kim) | `beam_001` (bản v1/v2: đáy tròn, mép cứng = "ống nghiệm"), `trail_band_001` (băng chữ nhật bo), `trail_streak_009` (phình ở đầu), `_010` (chạm mép), `_012` (đặc, chạm mép), `spark_streak_001` (đầu tròn), ribbon (uốn lượn, chạm mép) |
- Mọi ảnh Library có nền trong suốt với RGB trắng, nên **sao chép** sang `Assets/VFX/HealCircle/Textures/T_HealCircle_Arcane_*.png` đặt trên nền đen (độ sáng = alpha) bằng `prep_tex.py` (Library không bị đổi). Không còn ảnh vẽ script nào trong biến thể này.
- Vòng 1 review: ảnh Glow / Beam / Mote / Sparkle / Ring ban đầu lấy lại từ bản gốc (vẽ script) mà không tra Library → LỖI quy trình → đã tra lại và thay bằng ảnh Library như bảng trên. Cột Beam cũ chỉ là vệt ngắn mờ ~0.8 m; cột mới đọc rõ hơn.

## v2 (feedback Hậu: "cột sáng bùng sáng rồi biến mất", giữ nguyên vòng Arcane)
Lớp Beam đổi: t=1.6 s bùng trong ~0.1 s (rộng 1.5×, trắng nóng), rồi thu hẹp và tắt hẳn trước 2.7 s (life 1.1 s, trước là 1.9 s mờ dần); cột cao ~3.6 m ở cỡ 1× và ~5.4 m ở đỉnh bùng (size 1.5×; trước 3.0 m). Các lớp khác, texture, Bất biến không đổi.

## v3 (feedback art lead Sơn: "cột sáng để pivot tại gốc, thay texture cột sáng")
- Pivot ở GỐC: quad Stretched nằm giữa hạt nên cột chìm nửa dưới mặt đất; đo thử ba giá trị pivot (0,1,0 / 0,0.5,0 / 0,-0.5,0) cho thấy pivot.y càng lớn cột càng lên → pivot.y = lengthScale/2 (1.8) đặt chân cột đúng tâm vòng, mọc lên từ đó, không nở hai phía.
- Texture cột đổi sang Library `trail/streak/trail_streak_001` (bảng Texture). Feedback của Hậu ("sai rồi") chưa rõ, chờ làm rõ.

## v4 (feedback Sơn: "cột sáng không di chuyển, bùng phát tại chỗ rồi biến mất")
Beam đứng yên: tốc độ lên 1 cm/s (chỉ để quad Stretched có hướng "lên"), size over lifetime 0.6 → 1.15 (0.07) → 1.0 → 1.0 (sau review: bỏ đoạn 1.0 → 0.9; alpha giữ 0.6 tới t=0.55 rồi tắt, để ngọn cột không "tụt" khi mờ) (trước 0.35 → 1.5 → 0.45 làm đỉnh cột tụt xuống) nên chân và độ cao ~3.6 m giữ nguyên, chỉ bùng sáng (alpha 0 → 1 trong 0.05) rồi mờ tắt hẳn trước 2.7 s.

## Giao (2026-11-18)
Hậu (người order) đồng ý bản v4 ("oki rồi nhé"). Gói giao + ghi chú dùng: `work/vfx_orders/20261118_haunv_thu1/giao/`. Chưa art lead duyệt, chưa vào `Included` / Showcase.

## Dựng
Menu `VFX/HealCircle/Build Arcane` hoặc batch `-executeMethod VfxEffects.HealCircleArcaneBuild.BuildBatch`. Prefab `Assets/VFX/HealCircle/Prefabs/VFX_HealCircle_Arcane.prefab`. Preview `Docs/VFX/HealCircle_Arcane/Preview_sheet.png` (36 khung, 0.1 s).
Chưa vào `Included` của Showcase (chờ art lead duyệt).
