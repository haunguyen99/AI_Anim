# FireWaveCast — sóng lửa thổi ra phía trước (cast)
Độ chắc: giả định (suy từ brief "Thổi ra một sóng lửa" + tên ref Dota 2 Lina; chưa xem được hình video) · Cập nhật: 2026-11-16 · Nguồn: `Run 6 - Work.xlsx` dòng VFXPyroCast; anim PyroCast "Hai tay tụ vào để bắn ra lửa"

## Nó là gì
Hai tay chụm lại, **một luồng lửa phun ra phía trước thành hình nón mở rộng dần** (kiểu hơi thở rồng / Dragon Slave), có đầu sóng sáng và thân lửa cuộn phía sau, lan hết rồi tắt. Một phát, ~1 s. Cast = đòn kỹ năng, mạnh hơn đạn thường.

## Cấu trúc
| Phần | Vai trò | Hình dáng | Bắt buộc |
|---|---|---|---|
| Gather | tụ lửa ở hai tay trước khi bắn | glow nhỏ + hạt hút vào giữa hai tay, ~0.2–0.3 s | có |
| Wave body | thân sóng lửa | lớp hạt lửa lớn bay thẳng ra, **nón mở rộng**, đầu hẹp ở tay, loe ở xa | **xương sống** |
| Wave head | đầu sóng | khối sáng nhất, ở rìa xa nhất, chạy ra nhanh nhất | có |
| Sparks / ember | tia lửa văng hai bên | tia Stretched ngắn | có |
| Smoke | khói nóng phía sau | khói xám nâu mỏng, tan nhanh | không |

## Chuyển động
Tụ (0.25 s) → bắn (nón dài ra tới ~4 m trong ~0.35 s) → duy trì ngắn → tan (cả thảy ~1.0 s). Thân sóng đi theo hướng bắn (local +Z của điểm neo), không rơi xuống đất.

## Bất biến
- Có **hình nón / quạt mở rộng theo hướng bắn**, đầu nhỏ ở tay, loe ở xa. Không phải một quả cầu lửa, không phải vòng tròn quanh người.
- **Có bước tụ trước khi bắn** (khớp anim: hai tay tụ vào).
- Một lần, kết thúc hẳn (không dư lửa loop).
- Dài ~4 m, rộng ~3 m ở đầu xa (đề xuất; đo theo nhân vật 2 m).

## Được đổi
Màu / nguyên tố (lửa, băng, độc), kết cấu lưỡi lửa, mật độ hạt, khói, tia.

## Lỗi biến thể đã gặp
(chưa có; thêm khi build)

## Biến thể đã làm
(chưa có) — `VFXPyroCast` là bản gốc.
