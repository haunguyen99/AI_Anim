# VFX_FireTornado — kế hoạch v1 (2026-11-06)

Tornado thứ hai của dự án, làm bằng quy trình tornado của skill (`vfx-shader/references/tornado.md`), **không có prefab tham chiếu riêng** (art lead 2026-11-06: học tham chiếu là để lập quy trình, không phải VFX nào cũng cần tham chiếu).

Không gian *(đề xuất, art lead không nói khác)*: ground · cột dựng đứng quanh trục Y · camera 3/4 nhìn xuống 40° · cao ~4,5 m, rộng đỉnh ~2,7 m · neo điểm đất, đứng yên · một lần 4,4 s (lên chậm 0,8 s, giữ ~2,6 s, sụp 0,95 s kèm đợt tàn lửa) · stylized. Màu: vàng `FFD97A` → cam `FF7A1A` → đỏ `E03008`, khói nhiệt nâu tối.

| # | Layer | Vai trò & timing | Carrier | Shader | Texture |
|---|---|---|---|---|---|
| L1 | Funnel (root) | Thân: MỘT hạt phễu đồng hồ cát, quay 1,3 vòng/s, sọc lửa chạy trên da (hai lớp noise, rung đỉnh nhẹ); lên 0,8 s, sụp cuối | `tornado_mesh.fbx` (rpg-game, nhập) | `Thrust` (nhập), bảng màu ấm | `Library/noise/noise_098` |
| L2 | Whips | Dải lửa dựng đứng (trục vành thẳng đứng) bay lên dọc phễu, nở dần; 18/s | `fbx_fx_cylinder_03` | Graph `Fx_dissolve_particle_apb` | `Tex_fx_elements_set_01` ô 6 (sao chổi lửa) |
| L3 | FootFire | Lưỡi lửa liếm ở chân, 9/s | Billboard | Graph | cùng sheet ô 14–15 |
| L4 | Embers | Tàn lửa xoáy lên + **đợt bắn ra khi cột sụp** (45 hạt ở 3,3 s) | Billboard | Graph | cùng sheet 8×8 ô 19 |
| L5 | HeatSmoke | Khói nâu tối cuộn ở đỉnh | Billboard | Mobile Alpha Blended (khói mặc định) | `fx_t_smoke_02` |
| L6 | Scorch | Quầng cam cháy đất (Billboard + Local, xoay X 90°) | Billboard | Mobile Additive | `Library/glow/glow_005` |

**Khác WindTornado ở điểm nào (cả bốn):** mesh (một phễu liền thay vì vành rời), bố cục (cột cao hơn, dải lửa dựng đứng leo lên thân thay vì xoáy phẳng ở chân), timing (lên chậm, giữ, sụp + đợt tàn lửa), lớp phụ (tàn lửa, khói nhiệt, quầng cháy đất, lửa chân). Vẫn là cùng hiệu ứng: cột lốc xoáy đứng yên một lần.

Shader: không viết mới. Ngân sách: 6 layer, 350 hạt tối đa, 6 material. Đèn demo trong Showcase (chỉ lúc Play): `VfxShowcaseLights.Table` dòng `VFX_FireTornado`.

## Ghi chú
- Số kích thước = số của `VFX_Book_Tornado` × K (0,62): phễu 2,42 m × size Z 3 × K = 4,5 m. Thrust chạy tốt với tint ấm khi đặt `_ColorInner` vàng / `_ColorOuter` cam đỏ, hai lớp noise ngược chiều, `_VertexWobble` 0,04.
- **Hướng mesh (art lead sửa 2026-11-06):** trục vành của `fbx_fx_cylinder_03` nằm trên Z của mesh, nên để vành nằm ngang quanh cột phải Start Rotation X = 90° (Z 0, Y ngẫu nhiên), Start Size 3D (2, 2, 3). Bản v1 đặt X ±11° (sai) đã sửa. Thân phễu cuối đời chỉ chùng nhẹ (size 0,99 → 0,89), mờ dần bằng alpha. Bản prefab đã sửa tay và script đã khớp.
- Rotation over Lifetime: mọi trục cùng kiểu curve (TwoCurves) nếu không Unity bỏ qua module.
- Dựng thử ở project tạm (`D:/tmp_w/scratch_wind`) vì Unity đang mở project chính; vào project chính bằng menu **VFX → FireTornado Build** rồi **VFX → Showcase → Build Scene**.
- Chưa xem chuyển động thật trong Showcase / Game view, mới có preview tĩnh 6 mốc.
