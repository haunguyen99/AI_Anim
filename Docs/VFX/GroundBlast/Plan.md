# VFX_GroundBlast — kế hoạch v1 (duyệt 2026-11-03)

Pipeline: Built-in · Kiểu: one-shot · Thời lượng: ~1.3 s · Kích thước: ~2 m · Art Style: Stylized mềm (đã chọn)
Không gian: ground · đứng (Billboard / Stretched) + nằm đất (Billboard + Local) · camera 3/4 40° · neo điểm đất · nền tối
(đã chốt: ground, ~2 m, Stylized mềm, lửa cam, texture sinh bằng script, không dùng shape thư viện; đề xuất: camera 3/4 40°, nền tối)

| # | Layer | Vai trò & timing | Kỹ thuật | Kết thúc | Material / Shader | Texture (nguồn) |
|---|---|---|---|---|---|---|
| 1 | Flash | lóe sáng 0–0.15 s | Billboard, burst 1, size 2.4, SOL 0.5→1.2 | fade | M_GroundBlast_Flash_Add / Mobile/Particles/Additive | T_GroundBlast_Glow (script: glow) |
| 2 | Fireball | lửa = **1 glow mạnh** 0–0.55 s (art lead v3) | Billboard, 1 hạt, y 0.6, size 2.8, phồng 0.5→1→1.15, sáng đủ tới 45% đời, vàng→cam→đỏ | fade | M_GroundBlast_Fireball_Add / Additive | T_GroundBlast_FireGlow (script: glow --sigma 0.2, lõi tập trung) — *v2 khối dot và v1 flipbook khói đều bị chê xấu* |
| 3 | Smoke | **khối khói cầu ăn mòn** 0.03–1.5 s (v5c, theo Beyond-FX Zelda explosion, yt LzZ_9tmWPS8 04:10–06:34, so `ref_compare.png`) | Mesh `SM_VFX_SphereUV`, 30 hạt, Cone hướng lên (r 1.5, góc 25°, tốc 0.2–2.6, drag 3) → đáy rộng + giữa cao; size 3D (ngang 0.5–1.0, cao 0.7–1.35 m); chỉ xoay quanh Y; mép sần `_Lumps` 0.22; than xám `(0.25,0.23,0.24)`; mask theo UV của cầu (`_MESH_UV`). Custom1.xyzw = ngưỡng alpha / ngưỡng emissive / bulge / sáng tối: cháy cam 0–0.15 s → gân → nguội ~0.4 s → giữ tới ½ đời → ăn từ tâm thành sợi dọc | ăn mòn thành sợi | M_GroundBlast_Smoke_Alpha / **VFX/FX/Erode Sphere** (mới) | T_GroundBlast_SmokeErode_TEMP (**lấy từ video, chỉ để thử, không ship**) · T_GroundBlast_SmokeRamp · bản tự vẽ: T_GroundBlast_SmokeErode (smoke_sphere_textures.py) |
| 4 | Shockwave | vòng sóng nằm đất 0–0.35 s | Billboard + Render Alignment Local (xoay X 90°, y 0.01), size 0.4→2.8 ease-out | mỏng + fade | M_GroundBlast_Ring_Add / Additive | T_GroundBlast_Ring (script: ring --width 0.02) |
| 5 | Sparks | tia lửa văng 0.02–0.6 s | Stretched Billboard, burst 16, speed 4–8, gravity 0.8 | thu nhỏ | M_GroundBlast_Spark_Add / Additive | T_GroundBlast_Spark (script: comet, đầu trái = hướng bay) |

- **Cấu trúc prefab (art lead 2026-11-03):** mỗi lớp là 1 prefab thành phần `Prefabs/Components/CMP_GroundBlast_<Layer>.prefab`; `VFX_GroundBlast` chỉ là root chứa các prefab đó lồng bên trong (`VfxBuildKit.SaveNested`).
- Khói: v3 (2026-11-04) đổi từ sheet flipbook sang khối cầu ăn mòn theo video tham chiếu; sheet cũ `T_GroundBlast_Puff_4x4` đã xoá. v4 sửa 6 điểm lệch so với video; v5 (art lead: "khói của họ đâu có tròn") thêm mép sần + bố cục đáy rộng; v5b/c màu ramp theo độ sâu (`_HeatRange`), khói sáng hơn nền, nguội nhanh.
- Fireball hiện: size 2.6, đời 0.45 s, y 1.0 (giữa khối khói).
- Thứ tự vẽ (sortingOrder): Shockwave −3 → Smoke −2 → Fireball −1 → Flash 0 → Sparks 3.
- Silhouette: `Textures_contact.png` (4 texture mới, sinh bằng `make_texture.py`; không lấy ảnh thư viện).
- Gameplay: chỉ trang trí.
- Shader mới: không. Ngân sách: ~29 particle, 5 material, texture 512.
- Giả định: nền tối → lửa Additive; khói `#CDBBA6` hạ tối; Frame over Time đường thẳng; texture nền đen import `alphaFromGray` (khói Alpha Blended cần alpha).
