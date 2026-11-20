# LightningStrike — sét đánh xuống (cột sét)
Độ chắc: suy từ `Docs/VFX/LightningStrike/Plan.md` (bản 3, art lead chốt) · Cập nhật: 2026-11-10 · Nguồn: Plan.md, `.claude/skills/vfx-shader/references/thunder-core.md`

## Nó là gì
Từ trời **một cột sét sáng đâm xuống một điểm**, chớp lõi ở điểm chạm, **vòng sóng nổ lan trên đất**, nứt đất toả tròn, cung điện còn lại trên đất. Cột cao ~25 m, vòng / nứt ~15 m, top-down 60°.

## Cấu trúc (art lead chốt 3 phần cốt lõi)
| Phần | Vai trò | Bắt buộc |
|---|---|---|
| `line_impact` | cột sáng đứng (Stretched) | **xương sống** |
| `wave` | vòng nền lan | có |
| `flare` (root) | chớp lõi | có |
| Cracks | nứt đất toả tròn | lớp phụ |
| `electric_remain` | cung điện trắng còn lại | lớp phụ |

## Bất biến
- **Có tia sét thật đâm từ trên xuống**: cột sáng + tia điện, đọc được là *sét*, không phải chùm laser mờ.
- Chớp lõi sáng gắt ở điểm chạm, rồi vòng sóng lan ra.
- Điểm đánh duy nhất, cột đứng.

## Được đổi
Màu / nguyên tố (sét băng: tinh thể; sét độc: bong bóng / bào tử), hình nứt đất, lớp phụ, độ dày cột. **Không** đổi bản chất thành effect khác (zig-zag mảnh, chuỗi sét: đã bỏ ở bản 3).

## Lỗi biến thể đã gặp
- **Frost**: tia chỉ thoáng 2 frame; `TX_VFX_Mask16` làm quầng tròn cứng; bubble / pool dùng cùng mask.
- **Toxic**: tia xiên lớn là ảnh `lightning_texture_sheet1` trông như laser mờ; bubbles không ra bong bóng (dùng cùng `Mask16`).
- Tránh: giữ cột sét **rõ trong ≥ 0.2 s**, có zig-zag / phân nhánh; chất liệu thể hiện ở **lớp phụ** (nứt băng / vũng độc), không bằng đổi màu cột.

## Biến thể đã làm
Gốc (vàng), Frost, Toxic.
