# VioletThunder — sét tím từ trời, tích rồi nổ một phát
Độ chắc: suy từ `Docs/VFX/VioletThunder/Plan.md` + preview · Cập nhật: 2026-11-10 · Nguồn: Plan.md, Plan_Variants.md

## Nó là gì
Sét tím-hồng stylized toon **đánh xuống một điểm đất**: **tích điện ~0.4 s** (quầng tụ ở điểm đánh) rồi **một phát giáng** (~0.4–0.72 s): tia toon dày vẽ tay vỡ vụn theo flipbook, chớp ở điểm chạm, **sóng điện lan trên đất** ~3 m, dòng điện còn lại. Tia cao ~6 m.

## Cấu trúc
| Phần | Vai trò | Bắt buộc |
|---|---|---|
| Charge | quầng tích điện | có |
| BoltGlow + BoltCore | tia đứng (Stretched, flipbook 2×4 giáng → vỡ vụn) | **xương sống** |
| Flash | chớp chạm đất | có |
| Wave / ring | sóng lan nằm đất | có |
| Cracks, arcs, embers (v2) | điện còn lại, nứt, tàn | lớp phụ |

## Bất biến
- **Nhịp: tích → một phát giáng → vỡ vụn → dư điện**, không phải chuỗi nhiều phát.
- **Tia toon dày có đường zig-zag đọc được** (viền màu + lõi sáng), vỡ vụn theo flipbook.
- Một chớp + sóng lan trên đất ở điểm chạm.

## Được đổi
Màu / nguyên tố (xanh lam, đỏ thẫm), hình dư điện (arc / vết nứt / tàn), hạt phụ, độ dài tích.

## Lỗi biến thể đã gặp
- **Crimson**: có một tia hình "móc" lạ ở frame 3–4. **Azure / Crimson** nhìn chung tốt (dùng đúng `ring_ragged`, `ring_thin`, `flare_005`) nhưng quầng `glow_soft_round_008` chỉ 128 px (nửa khung), vỡ nhẹ khi to; ưu tiên `_007`.
- Dùng chung một sheet tia cho mọi biến thể (bản Azure / Crimson) làm các bản nhìn na ná nhau. **Bất biến chỉ đòi "tia toon dày zig-zag", không đòi cùng một ảnh**: mỗi biến thể phải chọn lại sheet tia và sheet arc từ Library theo quy trình chọn (xem contact sheet `lightning/bolt_sheet`, `arc_sheet`). Toxic / Gold / VioletStorm (2026-11-13) đã làm vậy, xem `Plan_Variants.md`.
- **Lớp phụ cũng phải tra `LIBRARY.md`** (lần đầu của Toxic / Gold / Storm đã bỏ sót arc, dùng sheet tia đặt nằm phẳng).

## Biến thể đã làm
Gốc (tím-hồng), Azure, Crimson, Toxic (xanh axit, 2026-11-13), Gold (vàng, 2026-11-13). Effect cùng phong cách nhưng khác hành vi: VioletStorm (loạt sét nhiều điểm).
