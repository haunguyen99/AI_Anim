# FireTornado — biến thể Frost và Sand (2026-11-09)

Cùng hiệu ứng với `VFX_FireTornado`: cột lốc đứng yên một lần, neo điểm đất. Không gian giữ như bản gốc *(đề xuất)*: ground, cột đứng quanh trục Y, camera 3/4 40°, lớp nằm đất = Billboard + Local (GameObject X 90°), Scaling Mode Hierarchy mọi hạt, không Horizontal / Vertical Billboard. Mỗi bản khác FireTornado **và** WindTornado ở ≥ 2 trục. Không shader mới.

## Frost (bão tuyết, băng) — menu `VFX/FireTornado/Build Frost`, prefab `VFX_FireTornado_Frost`
Cao ~5,7 m (K 0,78: mesh 2,42 m × size Z 3 × K), rộng ~3 m. Phễu = `tornado_mesh.fbx` + `Thrust` như FireTornado (hướng đã biết: Start Rotation X −90°, Y 90°, trục mesh là Z; builder vẫn log bounds + trục). Màu: trắng băng `EEFBFF`, cyan `7AD8FF`, xanh `2E7BE8`.

| Trục | Khác |
|---|---|
| Bố cục | **hai vách**: phễu ngoài (quay 2 vòng/s) + phễu trong mảnh, thấp hơn, quay ngược chiều 3,2 vòng/s, vào trễ 0,3 s (Fire: một phễu + dải lửa dựng đứng; Wind: vành rời); cột cao hơn, mảnh hơn |
| Timing | gom chậm 1,2 s, giữ có các đợt gió giật (size nhấp 0,97–1,05), tới 4,2 s cột **vỡ** thành 42 mảnh băng + 50 hạt tuyết rồi tan (Fire: sụp + tàn lửa); tổng ~5,2 s (Fire 4,4 s) |
| Lớp phụ | L3 Shards (mảnh băng `spark_shard_001` Stretched, mũi = hướng bay, xoáy quanh cột), L4 Snow (hạt tuyết `glow_soft_round_003`), L5 FrostMist (sương thấp nằm đất, khói mặc định `fx_t_smoke_02`), L6 IceGround (nứt băng nằm đất `ground_crack_radial_001`); bỏ Whips / Embers / HeatSmoke / Scorch / FootFire |

Hạt tối đa ~560 (shards 150, snow 260, mist 40...).

## Sand (lốc bụi cát) — menu `VFX/FireTornado/Build Sand`, prefab `VFX_FireTornado_Sand`
Cao ~4,5 m, hẹp ở chân, rộng dần lên đỉnh (~3 m). **Không dùng mesh** nào (không phễu, không vành), nên không có trục mesh để đọc. Màu: cát `C79E66`, nâu `735233`, nắng `FFD180`.

| Trục | Khác |
|---|---|
| Mesh / hình | cột dựng từ các cụm bụi (khói mặc định `fx_t_smoke_02`, Alpha Blended) xoắn lên: Cone phát lên + Orbital Y + Radial tăng theo tuổi, Noise module làm cột trôi nhẹ; thêm lõi tối đặc hơn quay nhanh hơn |
| Bố cục | chân hẹp đỉnh rộng (ngược phễu cát lửa), cột lắc lư; không có dải đứng quanh thân |
| Timing | dựng chậm 1,5 s, giữ dài, rồi **mỏng dần và tắt** trong 1,2 s (không sụp, không nổ); tổng ~6,2 s |
| Lớp phụ | L3 Grit (hạt cát sáng Additive), L4 Debris (mảnh đất Stretched nâu, rơi lại, gravity 0,9), L5 GroundDust (vòng bụi nằm đất lăn ra, Local + X 90°); bỏ lửa / tàn / khói đỉnh / scorch |

Hạt tối đa ~690 (dust 200, core 120, grit 260, debris 60, ground 50).

## Chưa xác minh
- Chưa build trong Unity (Unity đang mở). Cần chạy menu, xem `Docs/VFX/FireTornado_Frost|Sand/Preview_sheet.png` và Review Lab.
- Frost: thân dùng cùng shader `Thrust` như Fire nhưng tint băng sáng (SrcBlend 3 / DstBlend 10 giữ từ Fire) có thể ra hơi tối; chỉnh `_Opacity` / `_ColorInner` nếu cần.
- Sand: cột chỉ bằng hạt, nên độ "xoáy" phụ thuộc Orbital + Noise; xem chuyển động thật rồi chỉnh `Velocity()` (orbital 3,5 rad/s, radial 1,3).
- Sương nằm đất dùng Orbital Z (trục Z của GameObject xoay X 90° chính là trục đứng) cho xoáy trong mặt phẳng đất; kiểm tra chiều.
