# AuraGauntlet — aura ôm vật thể (găng)
Độ chắc: suy từ `Docs/VFX/AuraGauntlet/Plan_Variants.md` (bản gốc không có Plan) · **cần art lead xác nhận bản gốc** · Cập nhật: 2026-11-10 · Nguồn: Plan_Variants.md, prefab `VFX_AuraGauntlet.prefab`

## Nó là gì
Aura **lặp (loop)** quanh một vật thể cao 1.5 m đứng ở gốc toạ độ, ~2 m. Bản gốc: **sét tím-hồng bò quanh vật** (mesh bolt `Guardian_Lighting`) + khói đỏ + haze + chấm sáng; vòng lặp 2 s.

## Cấu trúc (bản gốc)
| Phần | Vai trò | Bắt buộc |
|---|---|---|
| mesh bolt (`electric`) | **tia sét chạy quanh vật**, nét đặc trưng | **xương sống** (suy) |
| smoke / haze | khí quyển bao quanh | có |
| dot_Light | chấm sáng | phụ |

## Bất biến (suy, cần xác nhận)
- Là **aura ôm vật thể** (không phải vụ nổ, không rải rộng): hiệu ứng nằm sát và bao quanh vật, loop mượt.
- **Có chuyển động đặc trưng quanh vật** (sét bò / hạt xoáy quanh trục).
- Không có điểm kích nổ hay một lần: lặp liên tục.

## Được đổi
Nguyên tố, chất liệu hạt, nhịp lặp, layout quanh vật. **Nhưng phải giữ "nét đặc trưng chạy quanh vật"** (bản gốc là tia sét): biến thể nên có phần tử tương đương theo chất liệu (lửa: lưỡi lửa liếm quanh; độc: giọt / khí chảy quanh).

## Lỗi biến thể đã gặp
- **Fire**: bỏ mesh sét và dùng `smoke_sheet_002` (cụm mây cartoon trắng) làm lửa → ra bông khói / vụ nổ, **không còn là aura quanh vật**.
- **Poison**: khí + bong bóng ổn, nhưng không có phần tử "bò quanh vật" mạnh; vũng loang (`water_splash_002`) gần như không thấy.
- **AuraGauntlet_Fire lần làm lại (2026-11-10), ba lần hỏng**: (1) `FireLoop_03` phun 28 hạt/s → đám que diêm (sheet **có hướng** không được spam); (2) còn 6 ngọn, xoay sai chiều → chúi xuống; (3) mượn mesh phễu tornado (rồi `SM_VFX_Cylinder_02`) làm vỏ lửa → ra **cột lốc xoáy lửa**, mất hình "ôm vật". Art lead bỏ phần aura, chưa có cách dựng được duyệt.
- Tránh: không mượn mesh của effect khác nếu nó làm đổi tạo hình; lửa ôm vật phải học từ prefab tham chiếu của art lead trước khi dựng (`rpg-game/_Game/Resources_moved/Prefabs/Effects/Player/InUse/VFX_Guantlet_Hand_Aura.prefab`, `RPG_VFX/Duong/Prefab/VFX_BossRaid_Bishop_Idle_Fire.prefab`, `VFX_Library/Prefabs/Gameplay/Elemental Mesh FX/MeshFX_Fire.prefab`); luôn có 1 phần tử xoáy quanh trục vật.

## Biến thể đã làm
Gốc (sét tím), Fire, Poison.
