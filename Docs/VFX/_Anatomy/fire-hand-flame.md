# FireHandFlame — lửa bốc ở bàn tay (loop)
Độ chắc: giả định (suy từ brief sheet Run 6 + tên ref Dota 2 "Lina Arcana - Fiery Soul of the Slayer"; chưa xem được hình video) · Cập nhật: 2026-11-16 · Nguồn: `Run 6 - Work.xlsx` tab "Anim & VFX" dòng VFXHandFlame

## Nó là gì
Ngọn lửa **bám theo bàn tay** nhân vật, cháy liên tục: một cụm lưỡi lửa bốc lên từ lòng bàn tay, vài đốm tàn bay lên rồi tắt. Loop, có ở cả hai tay. Nhân vật đang lơ lửng nên lửa **không chạm đất**, không bóng đổ lên sàn.

## Cấu trúc
| Phần | Vai trò | Hình dáng | Bắt buộc |
|---|---|---|---|
| Flame | lưỡi lửa chính | 3–5 lưỡi lửa Billboard, cam → vàng ở gốc, hẹp dần lên đỉnh, đỉnh đỏ cam | **xương sống** |
| Core glow | quầng sáng ở lòng bàn tay | glow tròn mềm Additive, nhỏ | có |
| Embers | tàn lửa | hạt nhỏ bay lên chậm, tắt dần | có |
| Heat haze / khói nhẹ | tuỳ chọn | khói xám mỏng sau lửa | không |

## Chuyển động
Loop liền (không mép nối thấy được). Lửa dao động nhẹ theo noise, bốc **lên theo trục +Y của bàn tay** (local), không theo thế giới (để tay xoay thì lửa xoay theo). Ember bay lên ~0.5–0.8 m rồi tắt.

## Bất biến
- Lửa **dính vào bàn tay** (Simulation Space Local cho lưỡi lửa), không để lại vệt rơi khi tay vung (anim PyroAttack / PyroCast).
- **Nhìn ra lửa** (lưỡi lửa có hình, không phải một quả glow tròn). Glow chỉ là phụ.
- Nhỏ: ~0.3 m cao mỗi tay, không che bàn tay.
- Lặp mượt.

## Được đổi
Màu (cam–vàng / xanh / tím), số lưỡi, nhịp bốc, lớp tàn, khói.

## Lỗi biến thể đã gặp
(chưa có; thêm khi build)

## Biến thể đã làm
(chưa có) — `VFXHandFlame` là bản gốc.
