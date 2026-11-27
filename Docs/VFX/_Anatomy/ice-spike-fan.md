# IceSpikeFan — gai đâm lên từ đất
Độ chắc: suy từ `Docs/VFX/IceSpikeFan/Plan.md` (v2) + preview · Cập nhật: 2026-11-10 · Nguồn: Plan.md, Plan_Variants.md

## Nó là gì
Từ một điểm đất, **một cụm gai nhọn trồi lên** (v2: cụm tròn: 1 gai trung tâm rất dài ~4.4 m, 2 gai dài phụ, rồi 4 vòng thấp dần, các khối **sát nhau**), đứng một nhịp rồi vỡ / co; kèm vết nứt dưới chân, khói / hơi, mảnh vỡ văng. ~1.2 s, vùng ~4 m.

## Cấu trúc
| Phần | Vai trò | Hình | Bắt buộc |
|---|---|---|---|
| Spikes (nhiều hàng) | thân hiệu ứng | **mesh gai nhọn**, cao thấp xen kẽ, đỉnh nhọn | **xương sống** |
| Cracks | vết nứt dưới chân | texture nứt toả tròn, nằm đất | có |
| Impact | chớp / vòng / tia ở gốc | mix thành phần chuẩn | nên có |
| Debris | mảnh vỡ văng | mesh mảnh nhỏ | có |
| Smoke / hơi | khói chất liệu | billboard mềm | phụ |

## Bất biến
- **Gai nhọn mọc từ đất, đỉnh nhọn, cao thấp không đều, xếp sát nhau thành cụm.** Không phải đám khói hay chùm sáng.
- Có **khối dài hẳn** (trung tâm) nổi bật so với phần còn lại.
- Có nứt đất dưới chân và mảnh vỡ văng khi trồi / vỡ.
- Trồi nhanh có nảy, đứng, rồi vỡ / co.

## Được đổi
Chất liệu quyết định hình gai (băng: dài, trong, cạnh phẳng; đất: ngắn ~1–2 m, thô, đỉnh vỡ; dung nham: gai đen + nứt sáng; gai độc / thorn: gai cong có gai con). Mesh gai, số vòng, bán kính, timing, khói / hạt phụ.

## Lỗi biến thể đã gặp
- **Thorn**: khói xanh to che gai; vết nứt nhỏ mờ.
- **Magma**: tốt (gai đen + nứt sáng): dùng làm mẫu. Chớp / quầng chung `T_IceSpike_Glow` hơi trơn.
- Tránh: khói chất liệu luôn nhỏ hơn và nhạt hơn gai (đã gặp ở bản băng v1: "khói che gai").

## Biến thể đã làm
Ice, Earth (gốc, `IceSpikeFan_Ice/Earth`), Magma, Thorn.
