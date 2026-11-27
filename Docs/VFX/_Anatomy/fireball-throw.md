# FireballThrow — cầu ném bay cung rồi nổ
Độ chắc: suy từ `Docs/VFX/FireballThrow/Plan.md` + preview · Cập nhật: 2026-11-10 · Nguồn: Plan.md, Plan_Variants.md

## Nó là gì
Một **quả cầu 0.6 m ném từ tay theo vòng cung ~8 m trong 0.8 s**, để lại đuôi, **chạm đất thì nổ ~2.5 m** (chớp + khối nổ + tia + khói). Một prefab tự chạy trọn: bay → chạm → nổ (hạt thân chết → sub-emitter Death).

## Cấu trúc
| Phần | Vai trò | Bắt buộc |
|---|---|---|
| Body | thân cầu Stretched theo hướng bay | **xương sống** |
| Core | lõi sáng | có |
| Trail / đuôi + khói đuôi | vệt dọc cung | có |
| Flash | một chớp Impact lúc chạm | có |
| Burst / nổ + tia + mảnh | vụ nổ ở chân | có |

## Bất biến
- Có **quả cầu nhìn thấy rõ bay vòng cung**, đầu hướng đúng tiến (Stretched), **đuôi liền** theo quỹ đạo.
- **Một chớp rồi nổ ở điểm chạm đất**; trước khi chạm không có nổ.
- Kích cỡ: cầu ~0.6 m, nổ ~2.5 m.

## Được đổi
Chất liệu quả cầu (lửa; băng: cầu tinh thể + mảnh; độc: cục / bọt đặc), hình nổ (lửa bung; băng vỡ tinh thể; độc bắn tung toé và vũng), màu đuôi, khói.

## Lỗi biến thể đã gặp
- **Frost**: đuôi dùng `trail_streak_012` (trắng đặc) nên ra **thanh trắng cong**, thân tinh thể nhỏ khó thấy.
- **Poison**: thân dùng noise streak nên trông như khối trắng sáng, thiếu cảm giác độc.
- **Frost, thân tinh thể** (2026-11-10): mesh xoay tự do (tumble) nên mũi chỉ lung tung. Sửa: mesh có trục dài (`SM_VFX_Debris_Crystal_01`: trục +Y, mũi nhọn ở +Y, kiểm bằng Blender) phải **dẫn đầu theo hướng bay**: Euler X +90° đưa +Y về +Z, rồi chúi theo đường cong quỹ đạo. Mọi mesh có đầu-đuôi bay theo quỹ đạo đều theo luật này; không xoay ngẫu nhiên.
- Đuôi băng đã đổi sang vệt sao chổi mảnh `trail_streak_010` (bản alpha thật), bỏ `trail_streak_012` (khối trắng đặc).
- Tránh: kiểm preview frame 2–4 thấy **cầu + đuôi tách bạch**; đuôi băng nên là vệt mảnh có hạt lấp lánh, không phải dải đặc.

## Biến thể đã làm
Gốc (lửa), Frost, Poison.
