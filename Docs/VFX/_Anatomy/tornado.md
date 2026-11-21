# Tornado — lốc xoáy đứng
Độ chắc: suy từ `Docs/VFX/FireTornado/Plan.md`, `WindTornado/Plan.md` + **art lead 2026-11-10** · Cập nhật: 2026-11-10 · Nguồn: các Plan đó, `vfx-shader/references/tornado.md`

## Nó là gì
Một **cột xoáy dựng đứng quanh trục Y**, đáy hẹp, thân xoắn, **loe ở đỉnh**, quay quanh trục; chân có bụi / lửa / mảnh bắn, tàn xoáy lên. Đứng yên tại một điểm đất, một lần ~4–5 s (lên → giữ → sụp), cao ~4.5 m.

## Cấu trúc
| Phần | Vai trò | Bắt buộc |
|---|---|---|
| Thân phễu | cột xoáy (mesh phễu + Thrust, hoặc cách khác) | **xương sống** |
| Dải / lớp trong | sọc chuyển động quanh thân | nên có |
| Chân (bụi / lửa / băng) | đáy cột | có |
| Hạt xoáy lên + mảnh | bụi, tàn, mảnh | có |
| Khói / sương | bao quanh | phụ |

## Bất biến (art lead 2026-11-10)
- **Thành hình lốc xoáy**: cột dựng đứng, hẹp ở đáy, loe ở đỉnh, đọc được chuyển động xoắn. **Cách tạo không bắt buộc là mesh**: bất kì cách nào ra hình đó đều được.
- Với cặp tornado: **không cần đổi thành phần / bố cục**, chỉ cần ra hình lốc xoáy đúng.
- Texture dùng phải có **alpha thật** (không viền vuông): xem `Docs/VFX/_Library/LIBRARY.md`.

## Được đổi
Chất liệu (lửa, băng, cát...), màu, hạt chân.

## Lỗi biến thể đã gặp
- **FireTornado_Sand** (preview): chỉ là cột khói be, **thân xoáy không rõ** → không đọc được là lốc xoáy; cần thân xoắn có sọc rõ.
- **FireTornado_Sand**: art lead nói chỉ cần thành hình lốc xoáy, cách làm tuỳ ý; hiện vẫn là cột khói be, **chưa sửa**.
- **FireTornado_Frost**: tốt. Viền vuông do `crack_radial_001` / `spark_shard_001` không alpha → đã làm bản alpha thật (`Assets/VFX/FireTornado/Textures/`).

## Biến thể đã làm
FireTornado (lửa), Frost, Sand; WindTornado (gió).
