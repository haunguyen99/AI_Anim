# VFX_WindShellTrail: kế hoạch v2 (2026-11-09)

**v2 (art lead: "phần shells dùng texture 2d thôi"):** bỏ mesh cầu + shader `VFX/FX/Wind Shell` (đã xoá). Shells = 2 lớp Billboard 2D, World, phát cùng nhịp 1 cái / 1.2 m nên trùng chỗ: **L2 Shells** `ring/soft/ring_soft_004` (bong bóng mờ viền sáng, 1.6 m, alpha 0.75) + **L2b ShellArcs** `ring/soft/ring_soft_010` (lưỡi liềm sáng một bên, 1.68 m, xoay random). Phình 1 → 1.4, mờ trong 0.5 s. Toàn bộ effect chỉ dùng `Mobile/Particles/Additive`.
Ribbon gió rộng hơn (WispA 0.7 m, WispB 0.45 m, sáng ×1.5): preview v1 thấy vệt quá mảnh vì hình trong `trail_ribbon` chỉ chiếm 1/3 chiều cao ảnh.
Thứ tự vẽ v2: Haze 0, Shells 1, ShellArcs 2, WispB 3, WispA 4, Core 5.

---

## v1

Brief: "làm 1 vfx trail như thế này" + ảnh boomerang bay để lại các vỏ cầu sóng xanh và vệt gió.
Không gian: air, trail theo vật bay (World space) · camera 3/4 nhìn xuống 40° · vật bay cao 1.2 m · Showcase: `VfxPathMover` bay thẳng 10 m / 0.8 s, dừng 0.3 s, bay về (loop).
Đã chốt: shader + texture Library, bay thẳng loop, chỉ trail (không vật bay), cầu ~1.6 m, cyan. Đề xuất: các lớp bên dưới.

Tham khảo: Real Time VFX "UE5 Projectile Effect" (ribbon + curl noise, ribbon bám vật bay, thêm noise lên cầu cho bớt lặp); anchitsh "Wind particles" (Trails, độ rộng mảnh hai đầu, Color over Lifetime mờ dần); ảnh của art lead.

| ID | Layer | Vai trò & timing | Carrier | Shader | Texture | Kết thúc |
|---|---|---|---|---|---|---|
| L1 | Core (root) | quầng cyan quanh vật bay, 8 glow/s chồng nhau = nhịp nhẹ, loop | Billboard 1.1–1.45 m, Local | Additive mobile | `glow/soft_round/glow_soft_round_004` | luôn bật |
| L2 | Shells | 1 vỏ cầu mỗi 1.2 m bay, đời 0.5 s, phình 1 → 1.4, xoay 3D random | mesh `SM_VFX_SphereUV` 1.6 m, World, alignment World | **mới** `VFX/FX/Wind Shell` | `noise/cloud/noise_cloud_020` | ăn mòn (Custom1.x) + mờ |
| L3 | WispA | ribbon gió chính, 6 điểm/m, đời 0.45 s, noise 0.25 | Trails Ribbon, Stretch, rộng 0.28 m | Additive mobile | `trail/ribbon/trail_ribbon_001` | mờ ở đuôi |
| L4 | WispB | ribbon phụ lệch (0, −0.14, 0.1), đời 0.38 s, noise 0.35 | như L3, rộng 0.16 m | Additive mobile | `trail/ribbon/trail_ribbon_009` | như L3 |
| L5 | Haze | sương cyan mờ, 3 hạt/m, đời 0.4 s | Billboard 0.7–1.0 m, World | Additive mobile | `glow/soft_round/glow_soft_round_009` | mờ dần |

Thứ tự vẽ: Haze 0, Shells 1, WispB 2, WispA 3, Core 4.

Shader mới `VFX/FX/Wind Shell` (`Assets/VFX/_Shared/Shaders/SH_VFX_WindShell.shader`): rim fresnel (tính ở vertex) + nền mờ; giữ một dải kinh độ quanh tâm ngẫu nhiên (Custom1.y) → lưỡi liềm; noise ăn mòn từ mép dải theo Custom1.x, có vạch sáng ở mép đang tan. 1 sample, Additive One One. Lý do viết mới: `Custom/BlackHole_TextureFresnel` (rpg-game) không nhận màu / alpha của particle, shader nhập không sửa.

Khác với: LightningTrail_Wind (ribbon gió Per Particle + Wisps + Specks). Bản này: **lớp chính** vỏ cầu mesh; **bố cục** vỏ đặt đều theo quãng đường, ribbon kiểu Ribbon nối theo đường bay; **timing** vỏ phình rồi tan 0.5 s; **lớp phụ** sương + quầng lõi.

Ngân sách: ~10 vỏ cầu cùng lúc, 2 ribbon (~60 điểm), ~15 hạt sương; 6 material, 1 shader mới, 0 texture mới.

Builder: `Assets/VFX/WindShellTrail/Editor/WindShellTrailBuild.cs` (menu `VFX/WindShellTrail/Build`).
Chưa chắc: hướng UV của `SM_VFX_SphereUV` (u = vòng quanh?) — build log in bounds; nếu dải là vĩ tuyến thì vỏ thành hình chỏm thay vì lưỡi liềm.
