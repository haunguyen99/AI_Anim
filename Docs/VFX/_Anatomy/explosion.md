# Vụ nổ (nổ đất)
Độ chắc: suy từ Plan GroundBlast + MushroomBlast (đã duyệt) + video Beyond-FX (yt LzZ_9tmWPS8) · Cập nhật: 2026-11-11 · Nguồn: `Docs/VFX/GroundBlast/Plan.md`, `Docs/VFX/MushroomBlast/Plan.md`

## Nó là gì
Một chớp sáng tại điểm nổ, khối lửa phồng nhanh rồi nguội thành **khối khói sần, đáy rộng, bốc lên**, kèm vòng sóng nằm đất và mảnh / tia văng ra. Nhìn từ 3/4: một vòm / đống mây lửa trên mặt đất.

## Cấu trúc
| Phần | Vai trò | Hình dáng | Bắt buộc? |
|---|---|---|---|
| Flash | chớp 0–0,15 s | sáng trắng vàng, to hơn thân | có (đúng một chớp) |
| Thân lửa → khói | xương sống | **cụm nhiều khối cầu sần chồng nhau**, đáy rộng, giữa cao; không tròn trơn | có |
| Vòng sóng | nằm đất, nở nhanh 0–0,4 s | vòng mảnh | có (nổ đất) |
| Mảnh / tia lửa | văng ra, rơi theo trọng lực | nhỏ, có hướng | nên có |
| Vết cháy / bụi đất | lớp phụ | | tuỳ |

## Chuyển động / nhịp
Nở rất nhanh (ease-out, ~0,15–0,25 s đạt gần cỡ tối đa) → lửa nguội cam → đỏ → than xám trong ~0,4 s → khói bốc chậm lên và tan / ăn mòn thành sợi tới hết ~1,5 s. Cụm trên cao bốc nhanh hơn cụm đáy.

## Bất biến
- Một chớp, một ngữ cảnh.
- Thân là **cụm khối sần**, đáy rộng, có chiều cao; lửa nằm trong lòng khói.
- Nhịp: nở nhanh – nguội – tan chậm (không nở đều tuyến tính).
- Màu chuyển nóng → nguội (vàng trắng → cam → đỏ → xám than).

## Được đổi
Nguyên tố (ma thuật, độc…), bố cục (vòm, nấm, cột), timing tổng, lớp phụ (đá văng, vết cháy), cách làm (sheet, cầu ăn mòn, mesh hoạt hình Blender).

## Lỗi đã gặp
- Khói tròn trơn như bóng bay (GroundBlast v4: "khói của họ đâu có tròn") → mép sần.
- Lửa bằng flipbook khói / khối dot bị chê xấu (GroundBlast v1, v2).

## Biến thể đã làm
- `GroundBlast` v5c (vòm, cầu ăn mòn shader), `MushroomBlast` v2 (nấm), `BlenderBlast` (2026-11-11, thử mesh hoạt hình dựng trong Blender qua MCP).
