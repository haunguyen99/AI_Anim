# VioletStorm — loạt sét nhiều điểm, báo trước rồi đánh lần lượt
Độ chắc: suy từ `Docs/VFX/VioletThunder/Plan_Variants.md` + preview (chưa có tham chiếu ngoài) · Cập nhật: 2026-11-13 · Nguồn: builder `VioletStormBuild.cs`

## Nó là gì
Cùng phong cách VioletThunder (tia toon, flipbook, sóng đất) nhưng **khác hành vi**: mây giông tụ ~6 m trên cao, **3 điểm đất được báo trước** (vòng co lại) rồi bị đánh **lần lượt** (0,30 / 0,52 / 0,74 s), cuối cùng **một tia lớn ở tâm** (~0,98 s) kèm chớp đất, sóng, dòng điện bò, vết cháy.

## Cấu trúc
| Phần | Vai trò | Bắt buộc |
|---|---|---|
| StormGlow | mây giông / quầng tụ phía trên | có |
| Warn (mỗi điểm) | vòng báo co vào điểm sắp bị đánh | **xương sống** (nhịp báo → đánh) |
| BoltGlow + BoltCore (mỗi điểm) | tia đứng Stretched, flipbook | **xương sống** |
| Flash + Ring (mỗi điểm) | chớp + vòng gợn tại điểm | có |
| Tia cuối (rộng hơn) + GroundFlash + Shock + Arcs + Scorch | cao trào ở tâm | có |

## Bất biến
- **Nhịp: báo trước từng điểm → các phát đánh lần lượt → một phát cuối lớn ở tâm** (khác VioletThunder: ở đây *chuỗi nhiều phát* là bản chất).
- Mỗi điểm đánh có vòng báo trước **trước** khi tia xuống; tia chạm đất rồi mới chớp (không nổ trước khi tia tới).
- Tia toon zig-zag đọc được (viền màu + lõi trắng); glow và lõi **cùng bề rộng** (lệch là lỗi).
- Cao trào cuối lớn hơn các phát trước.

## Được đổi
Số điểm, vị trí điểm, thời điểm, màu, sheet tia / arc, độ dài mây, lớp phụ ở cao trào.

## Lỗi đã gặp
- Glow rộng hơn lõi → quầng lệch khỏi lõi (phải cùng bề rộng).
- Chớp đất của tia cuối nổ trước khi tia chạm đất: dời +0,05 s cho **cả** Flash, vòng, GroundFlash, Shock, Arcs (lần đầu quên Flash và vòng).
- `sortingOrder` trùng (Scorch với vòng điểm thứ 3), sửa: Scorch −8.
- GroundFlash + Scorch + Shock chồng nhau thành **đĩa hồng phẳng**: đã giảm Scorch (4 m), GroundFlash còn 1 hạt; theo dõi.
- Mây giông 4,6 m vẫn tròn đều: chưa sửa.
- Arc: sheet có hướng bị xoay ngẫu nhiên (xem Plan_Variants "Bảng chọn texture").
- **Luật "một chớp" cho effect nhiều điểm** chưa chốt: hiện mỗi điểm một chớp, các điểm cách nhau ≥ 0,22 s, nên mỗi thời điểm chỉ có một chớp; điểm cuối có thêm GroundFlash. Chờ art lead xác nhận.

## Biến thể đã làm
Bản gốc VioletStorm (tím-hồng, 2026-11-13).
