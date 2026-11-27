# LaserBeam — tia laser bắn một phát, có điểm va chạm
Độ chắc: giả định (suy từ brief "Bắn một tia lazer. Làm 3 màu xanh dương, tím, đỏ. Có hiệu ứng tại điểm va chạm" + tiêu đề ref "The only Laser VFX tutorial you'll ever need"; chưa xem được video) · Cập nhật: 2026-11-16 · Nguồn: `Run 6 - Work.xlsx` dòng NovaCast (VFX); anim NovaCast "sấy lazer"

## Nó là gì
Một **tia thẳng từ nòng súng tới điểm đích**, lõi trắng sáng bọc viền màu, nòng có chớp phát, **đích có chớp + tia lửa văng**. Nova "sấy" laser: tia giữ ~1.2 s rồi tắt.

## Cấu trúc
| Phần | Vai trò | Hình dáng | Bắt buộc |
|---|---|---|---|
| Core | lõi tia | dải thẳng trắng, mảnh, sáng nhất | **xương sống** |
| Outer glow | viền màu | dải rộng hơn bọc lõi, màu chủ đạo (xanh dương / tím / đỏ), mờ dần ra mép | **xương sống** |
| Muzzle flash | chớp ở nòng | glow + chớp ngắn tại gốc tia | có |
| Impact | điểm va chạm | chớp + vòng sáng + tia lửa Stretched văng quanh | **có (brief yêu cầu)** |
| Flow detail | cảm giác năng lượng | texture chạy dọc tia (UV scroll) hoặc hạt chạy dọc | có |

## Chuyển động
Nhô ra rất nhanh (< 0.1 s) → giữ ~1.0 s với nhịp rung nhẹ độ rộng → tắt nhanh (~0.15 s). Impact sống cùng tia, tia lửa văng liên tục lúc giữ.

## Bất biến
- **Tia thẳng, liền**, hai đầu rõ: nòng và đích. Lõi sáng + viền màu (hai lớp).
- **Có hiệu ứng ở điểm va chạm** (brief) và chớp ở nòng.
- Ba màu (xanh dương, tím, đỏ) là **cùng hiệu ứng, đổi màu + giữ hình**; không đổi thành tia khác.
- Dài ~8 m (đề xuất), đúng hướng nòng.

## Được đổi
Màu, độ dày, nhịp rung, loại tia lửa ở đích, texture chạy dọc.

## Lỗi biến thể đã gặp
- **Stretched Billboard: đầu tại vị trí hạt, thân kéo ngược về sau** (2026-11-17, Run 6). Đặt hạt ở giữa tia thì chỉ hiện nửa tia. Đặt hạt ở **cuối tia** (shape position z = chiều dài) để tia trải 0→L theo +Z.
- Library không có thân tia ngang: `beam/beam_001` là cột sáng đứng đầu tròn. Dùng gradient ngang tự tạo (`PN_BeamBody`, V sáng giữa, U không đổi) cho cả thân tia lẫn ribbon.
- Quầng glow dùng ảnh đĩa phẳng (`glow_soft_round_013/014`) hiện thành "bong bóng": dùng `_004` (tâm sáng + vầng mềm).

## Biến thể đã làm
`NovaCast_1` xanh dương, `NovaCast_2` tím, `NovaCast_3` đỏ (đề xuất theo `_1/_2/_3` của Druid), project runner6. Cùng hình, đổi màu; chờ art lead.
