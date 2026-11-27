# HealCircle — vòng hồi máu
Độ chắc: suy từ `Docs/VFX/HealCircle/Plan.md` + preview · Cập nhật: 2026-11-10 · Nguồn: Plan.md, Plan_Variants.md

## Nó là gì
Một **vòng phép nằm đất bám chân nhân vật** mở ra, có vòng ngoài + hoa văn trong xoay ngược chiều, quầng sáng dưới đất, **cột / tia sáng đứng bốc lên**, hạt sáng và sao lấp lánh bay lên; ~1.5 s, ~2 m, một lần.

## Cấu trúc
| Phần | Vai trò | Hình | Bắt buộc |
|---|---|---|---|
| Rune ngoài / trong | vòng phép xoay | tròn, chấm, cánh lá tròn (không gai nhọn) | **xương sống** |
| GroundGlow | quầng dưới chân | glow tròn mềm | có |
| Beam / Rays | cột sáng đứng | stretched, mép trái = hướng lên | có |
| Motes / Sparkles | hạt, sao bay lên | chấm, sao 4 cánh | có |

## Bất biến
- **Vòng phép đọc được** (hai lớp xoay ngược nhau, hình tròn đều, nằm đất, tâm đúng giữa). Không rối đến mất hình vòng.
- Có **chuyển động đi lên** (cột sáng + hạt bay lên): cảm giác hồi phục.
- Hình mềm, an toàn: tròn, chấm, lá tròn; không gai nhọn, không tối.
- Bám nhân vật, một lần ~1.5 s.

## Được đổi
Màu, họa tiết vòng (thánh: vòng chữ + sao; thiên nhiên: dây leo + lá), hạt bay lên (lông vũ / lá / bào tử), nhịp.

## Lỗi biến thể đã gặp
- **Nature**: dây leo quá rối nên mất cảm giác "vòng phép"; cần giữ **một vòng tròn đều** làm khung rồi mới thêm dây.
- Bản Holy tốt: dùng làm mẫu.

## Biến thể đã làm
Gốc (xanh lá), Holy, Nature, **Arcane** (tím, 2026-11-18, order thử của anh Hậu: nạp 3 nhịp + vành sóng, 2 vòng rune Library `rune/circle` 003 + 008, 6 cầu sáng leo xoắn, cột hẹp 3 m; v2: cột bùng ~0.1 s rồi tan; v3: pivot cột ở gốc + texture cột `trail_streak_001`; v4: cột đứng yên, bùng tại chỗ rồi tan; kế hoạch `Docs/VFX/HealCircle_Arcane/Plan.md`).
