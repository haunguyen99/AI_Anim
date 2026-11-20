# HealCircle: biến thể Holy và Nature (2026-11-09)

Cùng hiệu ứng với bản gốc (vòng phép hồi máu dưới chân nhân vật, một lần, nằm đất). Không gian giữ như `Plan.md`: ground, nằm đất = Billboard + Render Alignment Local (GameObject xoay X 90), cột đứng = Stretched Billboard (pivot 0,1,0), camera 3/4 40°, vòng ~2 m, bám nhân vật, nền tối, tất cả Additive, Scaling Mode Hierarchy. Chưa build trong Unity (Unity đang mở); chạy menu rồi xem `Docs/VFX/HealCircle_<Tên>/Preview_sheet.png`.

Texture: Library `rune/circle/rune_circle_002.png` (Holy), `ground/crack_radial/ground_crack_radial_010.png` + `ring/soft/ring_soft_011.png` (Nature), copy sang `Assets/VFX/HealCircle/Textures/` rồi mới import. Lá, lông vũ, vòng hào quang, vòng lá vẽ bằng script trong builder (Library không có hình lá / lông vũ). Glow / Beam / Mote / Sparkle dùng lại của bản gốc.

## HealCircle_Holy (vàng-trắng)
Menu `VFX/HealCircle/Build Holy`, prefab `VFX_HealCircle_Holy`, ~4 s. Màu Core `#FFFBEA`, Mid `#FFD66B`, Outer `#E0961E`.
Khác bản gốc ở 3 trục:
- **Timing:** vòng hào quang vàng RƠI từ 2,1 m xuống đất trong ~1 s, chạm đất mới mở rune (t = 1,0) kèm gợn sóng; tổng 4 s (gốc: mở ngay, 2,8 s).
- **Lớp phụ:** không còn một cột Beam: 8 tia sáng mảnh đều quanh viền (Stretched, bay lên 0,25 m/s) + lông vũ bay lên xoáy nhẹ + gợn đáp đất (thay RuneInner).
- **Bố cục:** bụi sáng phủ cả đĩa (r 1,15) thay vì chỉ viền; rune = mandala thư viện (to 2,5 m), xoay 12°/s một chiều.
Lớp (sortingOrder): GroundGlow -5, Rune -4, LandRipple -3, Halo 1, Rays 0, Motes 2, Feathers 3, Sparkles 4.

## HealCircle_Nature (xanh lục - ngọc, đất)
Menu `VFX/HealCircle/Build Nature`, prefab `VFX_HealCircle_Nature`, ~3,4 s. Màu Core `#EFFFC8`, Mid `#5FE08A`, Outer `#13806A`, Teal `#2FD6B0`, Lime `#B6F26A`.
Khác bản gốc ở 3 trục:
- **Lớp:** không có Beam, không có hai rune: mạng rễ (crack radial) mọc ra, vòng hoa-lá vẽ bằng script, 3 gợn nước, lá bay xoáy lên, bào tử trôi (noise mạnh), 2 lần chớp nở hoa.
- **Timing:** mọc chậm (rễ 0,3 → 1 trong ~0,9 s), vòng lá trễ 0,3 s, gợn t = 0,2 / 0,9 / 1,6, thay cho mở nhanh 0,07 s.
- **Bố cục:** lá và bào tử quay quanh tâm (orbital velocity) thay vì bay thẳng từ viền; rễ xoay +8°/s, vòng lá -14°/s.
Lớp: GroundGlow -5, Roots -4, Wreath -3, Ripples -2, Spores 2, Leaves 3, Bloom 4.

## Đèn demo gợi ý (VfxShowcaseLights.Table)
Holy: layer `Halo`/`Rays`, `#FFD66B`; Nature: layer `Bloom`/`Leaves`, `#5FE08A`. Xem báo cáo cuối.
