# Thành phần của từng VFX trong Showcase (2026-11-06)

Mục đích: làm cơ sở chia lại `Assets/Library/` để mỗi thành phần lấy đúng loại texture.
Nguồn: đọc prefab (lớp particle → material → texture). Trong ngoặc: hình dạng / dạng texture (ảnh đơn, sheet nhiều khung, mesh) / kiểu blend.
Phạm vi: 7 effect đang đặt trong scene (Slash360, IceSpikeFan, HealCircle, VioletThunder, AuraGauntlet, FireballThrow, FireTornado) + `LightningStrike` (có trong `Included`, hiện không có instance). Đã bỏ Knight Thunder và ThunderSpear (2026-11-06, art lead). `LightningTrail` không còn prefab.

## Slash360 (Earth) gồm
- Vệt mờ phía sau (ảnh vệt cung chạy UV trên mesh, alpha)
- Thân vệt chém (ảnh vệt cung chạy UV trên mesh, alpha cutout)
- Viền sáng của vệt (ảnh viền cung mảnh, chạy UV trên mesh, additive)
- Chớp lúc bắt đầu (glow tròn mềm, additive)
- Mask gradient (gradient 1D đen → trắng, dùng làm `_MaskTex`)
- Noise chi tiết (noise dạng sọc dọc theo vệt)
- Noise tan (noise mịn, làm dissolve)
- Noise méo UV (noise dùng bẻ UV)

## IceSpikeFan (Ice) gồm
- Quầng sáng dưới đất (glow tròn mềm, nằm đất, additive)
- Gai tinh thể: 4 lớp Tall / Mid / Long / Edge (mesh gai + palette màu, alpha)
- Nứt đất phát sáng (ảnh vết nứt toả tròn, nằm đất, additive)
- Hơi lạnh (ảnh khói mềm, alpha)
- Mảnh tinh thể văng (mesh mảnh vỡ + palette màu)
- Tảng đất / băng dưới chân (mesh tảng + palette màu)

## HealCircle gồm
- Vòng rune ngoài (ảnh vòng chữ lớn, nằm đất, additive)
- Vòng rune trong (ảnh vòng chữ nhỏ hơn, nằm đất, additive)
- Quầng sáng nền (glow tròn mềm, nằm đất, additive)
- Cột sáng đứng (ảnh cột sáng dọc, stretched, additive)
- Tia lấp lánh bay lên (ảnh sao 4 cánh nhỏ, additive)
- Hạt sáng nhỏ (chấm sáng tròn nhỏ, additive)

## LightningStrike gồm
- Cột sét đứng (sheet tia sét nhiều khung, stretched, additive)
- Nứt đất (ảnh vết nứt, nằm đất, alpha)
- Cung điện còn lại trên đất (ảnh cung điện vẽ tay + ramp màu, stretched)
- Flare ở gốc (flare / mask tròn, additive)
- Vòng sóng nổ (ảnh vòng lan, nằm đất, additive)

## VioletThunder gồm
- Chớp sáng đất (glow tròn mềm, nằm đất, additive)
- Quầng dư còn lại (glow tròn mềm, dùng chung texture với chớp sáng đất)
- Quầng sáng ở gốc (glow tròn mềm, cũng dùng chung texture đó)
- Vòng lan (vòng tròn mảnh, nằm đất, additive)
- Sóng nổ (ảnh sóng lan dày hơn vòng, additive)
- Sao chớp (mảng chớp gai nhọn, additive)
- Chớp tức thời (mảng chớp gai nhọn, additive)
- Lõi tia sét (sheet tia sét 2×4, stretched, additive)
- Quầng quanh tia sét (sheet 2×4 dạng glow, stretched, additive)
- Cung điện chạy trên đất (sheet cung điện 4×4, nằm đất, additive)

## AuraGauntlet gồm
- Tia điện quanh tay (ảnh tia điện đơn trên mesh + ramp màu, shader Lightning)
- Khói quanh (ảnh khói mềm, alpha)
- Chấm sáng (chấm / ô sáng nhỏ, alpha)

## FireballThrow gồm
- Thân cầu lửa (noise sọc dọc, stretched, shader Meteor)
- Lõi sáng (glow tròn mềm, additive)
- Vệt đuôi sáng (ảnh vệt đuôi dài, additive)
- Tàn lửa (glow tròn nhỏ, additive)
- Tia lửa (ảnh đuôi sao chổi, stretched, additive)
- Nổ lửa lúc phóng (glow tròn mềm, additive)
- Chớp phóng (mảng chớp gai nhọn, additive)
- Lưỡi lửa (sheet 2×2 khói cartoon trắng, alpha)
- Khói vệt (ảnh khói mềm, alpha)
- Khói nổ (mesh cầu ăn mòn + mask ăn mòn + ramp màu, alpha)

## FireTornado gồm
- Thân lốc (mesh lốc + noise cuộn gió, shader Thrust)
- Roi lửa (mesh + sheet phần tử lửa)
- Lửa chân (sheet phần tử lửa, billboard)
- Tàn lửa (sheet phần tử lửa, billboard)
- Khói nóng (ảnh khói mềm, alpha)
- Vết cháy nền (vòng tròn / glow, nằm đất, alpha)

---

## Gộp theo loại thành phần (số effect dùng)
- Glow tròn mềm: Slash360, IceSpike, HealCircle, VioletThunder, FireballThrow, FireTornado
- Chớp / flash / sao: VioletThunder, FireballThrow
- Flare: LightningStrike
- Vòng lan / sóng nổ: LightningStrike, VioletThunder
- Vòng rune: HealCircle
- Cột sáng đứng: HealCircle, LightningStrike
- Tia sét / cung điện (sheet): LightningStrike, VioletThunder, AuraGauntlet
- Nứt đất / vết cháy nền: LightningStrike, IceSpike, FireTornado
- Khói: IceSpike, AuraGauntlet, FireballThrow, FireTornado
- Lửa (lưỡi lửa, phần tử lửa, tàn lửa, tia lửa): FireballThrow, FireTornado
- Vệt đuôi: FireballThrow
- Slash (vệt chém UV): Slash360
- Noise: Slash360, FireballThrow, FireTornado
- Mask / ramp / palette: Slash360, IceSpike, AuraGauntlet, LightningStrike, FireballThrow
