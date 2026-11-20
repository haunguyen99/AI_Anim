# Tạo hình đặc trưng theo chất liệu / nguyên tố

Độ chắc: kiến thức chung (VFX stylized), **chưa duyệt từng dòng bởi art lead**; chỉnh khi art lead chốt khác. Cập nhật: 2026-11-10.

Dùng khi đổi nguyên tố của một biến thể: **chất liệu mới phải có hình riêng của nó**, không chỉ đổi màu. Bảng này nói "hình gì làm người xem nhận ra chất liệu"; còn việc giữ hình của *effect* thì xem file của loại đó.

| Chất liệu | Hình nhận dạng | Chuyển động | Texture / hình hợp (Library) | Dễ sai |
|---|---|---|---|---|
| Lửa | lưỡi nhọn hướng lên, đáy rộng, đầu cong; vàng trắng lõi → cam → đỏ → tro | bốc lên, sôi, co nhỏ khi tắt; tàn lửa bay lên | flipbook lửa (`smoke/sheet`, `Flipbooks/Fire`), `glow`, `spark/streak` | dùng **mây cartoon / khói** làm lửa; phun sheet lửa **có hướng** thành đám que diêm; mượn mesh phễu tornado làm lửa ôm vật (đã gặp cả ba: AuraGauntlet_Fire); dải thẳng cứng |
| Băng | tinh thể **cạnh sắc, mặt phẳng**, trong, sáng ở mép; hơi lạnh trắng xanh | trồi / vỡ dứt khoát, ít chuyển động mềm; mảnh vỡ lấp lánh | mesh tinh thể, `spark/shard`, `ground/crack_*` (mảnh), `glow/flare` | cạnh tròn mềm như thuỷ tinh; trail trắng đặc (đã gặp: FireballThrow_Frost) |
| Nước | giọt, sóng cuộn, bọt, mặt cong có vệt sáng | chảy cong, văng giọt, rơi | `water/splash`, `bubble`, `tile` | khói xám quanh nước; giọt là chấm tròn |
| Độc | khí đặc xanh vàng, **bong bóng nổi lên, giọt nhỏ, vũng loang** | nặng, chậm, dồn thấp, giọt rơi | `water/bubble`, `smoke/soft`, `ground/splat` | màu xanh nhưng hình là khói/sét (laser) |
| Đất | khối thô, góc cạnh, đỉnh vỡ, bụi bốc | trồi nhanh, rơi mảnh, bụi nở | mesh đá, `ground/crack_*`, `smoke/soft` bụi | quá sắc / quá bóng như băng |
| Dung nham | khối đen sẫm + **vết nứt phát sáng cam**, bong bóng, tàn lửa | chậm, nặng, nứt sáng dần rồi nguội | `ground/crack_*` (additive), `glow` | thiếu khối đen, chỉ có sáng |
| Sét / điện | **zig-zag phân nhánh**, lõi trắng viền màu, chớp gắt, tia lan trên đất | giáng nhanh, nhấp nháy, tắt vỡ vụn | `lightning/*`, `noise/electric_web` | tia thẳng mờ như laser; quầng tròn cứng |
| Gió | **vệt cong / xoắn** mảnh, sáng mờ, bụi lá cuốn | cuộn quanh trục, kéo dài | `noise/streak`, `noise/swirl`, `trail/*` | khối khói tròn |
| Thánh / hồi máu | vòng, chấm, cánh tròn, tia sáng đứng, lấp lánh (không gai nhọn) | bốc lên chậm, mềm | `rune/circle`, `glow/*`, `spark/star` | gai nhọn, tối |
| Thiên nhiên | dây leo, lá, bào tử, rễ | mọc, uốn, lá rơi | script (hữu cơ cần xem phương án) | vòng rune bị rối đến không đọc được |
