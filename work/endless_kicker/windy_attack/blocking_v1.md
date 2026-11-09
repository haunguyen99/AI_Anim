# Windy Attack — blocking v1 (user chốt 2026-11-06)

Scene Frolvy: `C:\Users\Admin\Documents\Ngoc\Hoctap\Anim\Windy_Attack.fv` (user tự lưu; script AI không ghi được ngoài Documents\Frolvy / %TEMP%).
7 key stepped: F0, 5, 7, 9, 13, 18, 24 (24F @ 30 fps). Tay phải FK, khuỷu chỉ gập 1 trục (ry), tay trái FK.
Pose F5, F7, F9, F13, F18 do user chỉnh trực tiếp; AI chỉ sửa khuỷu (bỏ xoay lệch trục), không đổi dáng.

Số đo thế giới (m): tay = chỗ cầm trượng; hướng = đuôi→đầu trượng; đuôi = tay − 1,13 × hướng.

| Frame | Tay | Hướng trượng | Đuôi cao | Hông cao |
|---|---|---|---|---|
| F0 | (-0.06, 0.84, 0.32) | (0.67, 0.70, 0.25) | 0.04 | 0.63 |
| F5 | (-0.51, 1.57, -0.16) | (0.32, 0.91, -0.26) | 0.54 | 0.63 |
| F7 | (-0.46, 1.60, 0.05) | (0.44, 0.83, 0.34) | 0.66 | 0.63 |
| F9 bắn | (-0.16, 0.97, 0.77) | (0.69, 0.14, 0.71) | 0.81 | 0.58 |
| F13 | (-0.07, 0.90, 0.74) | (0.82, -0.03, 0.57) | 0.94 | 0.59 |
| F18 | (-0.26, 0.96, 0.53) | (0.69, 0.54, 0.49) | 0.36 | 0.62 |
| F24 | = F0 | | | |

Ghi chú cho bước spline:
- Hướng trượng F9/F13 là quét chéo sang trái (user chỉnh), không phải thẳng +Z; hướng bắn do code quyết định, báo dev.
- Spline thử F0→F5 cần breakdown ~F3 (không thì trượng xoay 41–54°/frame, vòng ra trước rồi mới ra sau); F13→F24 giảm tốc dần, F18 không được khựng (tay 5–8 cm/frame, xoay 8°→0,2°).
- Đuôi trượng cao ≥ 0,26 m trừ F23–F24 (0,04 như Idle).
- Vải (áo choàng, vạt) chưa key.
- Director: vòng 1 Cần sửa, vòng 2 Cần sửa, vòng 3 Cần sửa nhẹ (bản trước khi user chỉnh F9/F13).
