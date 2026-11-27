# FireballImpact — Bản định hướng (đã duyệt 2026-10-28)

Quả cầu lửa rơi chéo xuống rồi nổ tại điểm rơi. Đòn đánh vùng kiểu skill, nóng và mạnh.

## Phân tích
- **Tâm điểm:** khoảnh khắc chạm đất (flash, cầu lửa nổ, vòng xung kích). Cầu rơi và khói là phụ.
- **Hướng lực:** từ trên xuống, rồi toả ra từ điểm rơi.

## Không gian và thời gian
```
Camera: Isometric/3-4 (~40° nhìn xuống) · Neo: điểm rơi trong thế giới · Mặt phẳng: cầu/nổ đứng quay về camera, vòng và vết cháy nằm đất · Quy mô: cầu ~1 m, nổ ~4 m (người 2 m) · Thời lượng: 1.8 s, chạm đất ở 0.9 s · Nền: tối · Art Style: Stylized (đã chọn), cam/vàng/trắng toon
```

## Bảng thành phần

| ID | Thành phần | Vai trò | Mặt phẳng / carrier | Timing (s) | Kết thúc | Shader |
|---|---|---|---|---|---|---|
| L1 | Cầu lửa + đuôi | chính | quad theo hướng bay, rơi chéo 60°, cầu ~1 m | 0–0.9 | đầu tắt khi chạm, đuôi co lại | dùng lại `VFX/FX/Meteor` |
| L2 | Flash + cầu lửa nổ | chính | quad đứng quay về camera, ~4 m | 0.9–1.6 | ăn mòn tan từ mép vào lõi | mở rộng `VFX/FX/Blast` (+ `_NO_RING`) |
| L3 | Vòng xung kích | điểm nhấn | quad nằm đất, ~4 m | 0.9–1.5 | mỏng dần rồi tan | mở rộng `VFX/FX/Blast` (+ `_RING_ONLY`) |
| L4 | Khói sau nổ | phụ | 3 quad đứng, bốc lên ~2 m | 1.0–1.8 | tan dần, nhạt màu | mới `VFX/FX/Smoke` |
| L5 | Tia lửa bắn toả | điểm nhấn | particle Stretched, 14 hạt | 0.9–1.5 | co lại và tắt | mới `VFX/FX/Spark` |
| L6 | Vết cháy đất | phụ | quad nằm đất, ~2.5 m | 0.95–1.8 | nhạt dần | dùng lại `VFX/FX/Smoke` (tối, không bốc lên) |

## Shader
- `SH_VFX_Blast` — mở rộng: `_NO_RING` (bỏ vòng), `_RING_ONLY` (chỉ vòng). Mặc định tắt.
- `SH_VFX_Smoke` — mới: blob SDF ăn mòn noise, bốc lên, tan từ mép. 2 sample. Blend alpha.
- `SH_VFX_Spark` — mới: capsule SDF đầu sáng đuôi thon. 0 sample. Blend add.

## Giả định
Rơi từ trái sang phải; màu cam/vàng/trắng, khói xám ấm; không rung camera, damage, mảnh vỡ; số hạt, độ cao khói, kích thước vết cháy là mức đề xuất; chưa đo hiệu năng trên máy thật.
