# Slash360 — vệt chém xoay 360°
Độ chắc: suy từ `Docs/VFX/Slash360/Plan.md` + preview · Cập nhật: 2026-11-10 · Nguồn: Plan.md, Plan_Variants.md, `Assets/VFX/Slash360/`

## Nó là gì
Một vệt chém hình **vành cung quét trọn một vòng quanh nhân vật** (~2 m, nghiêng 25° theo tay kiếm), nhanh (~0.35 s): đầu vệt sáng sắc, thân dày dần rồi mảnh về đuôi, tan dần theo chiều quét.

## Cấu trúc
| Phần | Vai trò | Hình | Bắt buộc |
|---|---|---|---|
| Body | thân vệt | mesh vành phẳng, texture chạy theo UV (Slash Sweep / Coloso) | có |
| Edge | mép sáng ngoài | cùng mesh, mảnh hơn, Additive, mép ngoài sắc | có |
| Trail | vệt mờ phía sau | mesh, alpha thấp | nên có |
| StartFlash | chớp ở điểm bắt đầu | glow tròn 0.1 s | nên có |
| Debris / hạt nguyên tố | mảnh theo đầu vệt | hạt quanh vành | phụ |

## Bất biến
- Là **một vành cung liền, quét hết vòng**, có đầu sắc và đuôi mảnh. Không bị cắt cụt giữa vòng, không có mép cắt dọc cứng.
- Slash = **mesh + UV**, không billboard; shader Coloso hoặc Slash Sweep.
- Mép ngoài sắc rõ, thân mềm hơn: có "độ dày thay đổi".
- Nhanh ~0.3–0.4 s, quét theo chiều kim đồng hồ từ trên.

## Được đổi
Nguyên tố (màu, texture thân, hạt phụ), mesh vành khác (`SM_VFX_Curve_*`), độ dày, hạt đi kèm theo chất liệu (lửa: tia lửa nhỏ + lưỡi lửa; nước: giọt + sóng; đất: mảnh đá). Xem `materials.md`.

## Lỗi biến thể đã gặp
- **Slash360_Fire**: mép cắt dọc cứng ở đầu vệt, tia lửa là nón cam trông như gai, viền dùng `EdgeCrescent_Earth` của bản Đất, không có lớp lửa nên không còn "chất lửa".
- **Slash360_Water**: khói xám (`fx_t_smoke_02`) quanh nước, giọt là chấm tròn.
- Tránh: kiểm preview ở frame giữa vệt (frame 3–5) xem vành có liền không; mỗi nguyên tố có mép riêng, không mượn mép Earth.

## Biến thể đã làm
Earth (gốc), Fire, Water (`Assets/VFX/Slash360/Prefabs/`). Bản 5 nguyên tố cũ ở `_archive/Slash360_5elements_2026-11-03/`.
