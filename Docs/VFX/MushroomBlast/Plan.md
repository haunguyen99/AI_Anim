# VFX_MushroomBlast — kế hoạch v1 (đã duyệt 2026-11-04)

Không gian: ground · camera 3/4 nhìn xuống 40° · neo tại điểm nổ · ~3 m (cao, nấm rộng ~3 m) · nền tối (đã chốt với art lead)
Thời lượng: ~2 s · Art Style: stylized, lửa cam · Skill: `/vfx-shader` · Build: menu **VFX → MushroomBlast → Build** (`Assets/VFX/MushroomBlast/Editor/MushroomBlastBuild.cs`)

| # | Layer | Vai trò & timing | Carrier | Shader | Texture | Kết thúc |
|---|---|---|---|---|---|---|
| 1 | Flash (**root**) | chớp gai 0–0.12 s, y 0.6 | Billboard 3.5 m | dùng lại `Mobile/Particles/Additive` | `Library/impact/impact_016` | co + mờ |
| 2 | Shockwave | vòng nở 0.5→5 m, 0–0.4 s | Billboard + Local, nằm đất | Additive | `Library/wave/wave_004` | mỏng + mờ |
| 3 | FireCore | glow lõi bốc theo cột 0–0.6 s, y 0.6→2.4 | Billboard 2.4 m | Additive | `Library/glow/glow_023` | vàng→cam→đỏ, mờ |
| 4 | Stem | **cột** 14 cầu (v2, tốc 1–5.5) trải từ sát đất lên ~2 m, 0–1.9 s | Mesh `SM_VFX_SphereUV` | dùng lại `VFX/FX/Erode Sphere` | mask + ramp của GroundBlast | cháy → gân → than → sợi |
| 5 | Cap | **đầu nấm** 14 cầu to ở ~2.3 m toả ngang, 0.12–2.0 s | như trên | như trên | như trên | như trên |
| 6 | Skirt | vành 16 cầu dẹt (v2, tốc 2.5–4, chồng nhau) lăn ra sát đất, 0.02–1.5 s | như trên | như trên | như trên | như trên |
| 7 | Debris | 10 mảnh đá nâu sẫm văng, rơi, xoay, 0–1.2 s | Billboard, 2×2 chọn frame ngẫu nhiên | `Mobile/Particles/Alpha Blended` | `T_MushroomBlast_Debris` (copy `impact_077`, alpha từ độ sáng) | rơi + co |
| 8 | Sparks | 20 tia lửa 0.02–0.7 s | Stretched (đầu trái) | Additive | `Library/glow/glow_072` | co |
| 9 | Scorch | vết cháy nứt trên đất 2.6 m, 0.05–2.0 s | Billboard + Local | Alpha Blended | `T_MushroomBlast_Scorch` (copy `decals_001`, alpha từ độ sáng) | mờ 0.5 s cuối |

- **Khác với GroundBlast:** bố cục (cột + đầu nấm + vành đất thay vì một vòm), timing (2 s, cột trước, nấm sau 0.12 s), lớp phụ (đá văng, vết cháy, chớp gai).
- Shader: không viết mới, toàn bộ dùng lại. Khói theo luật khói vụ nổ (số từ `GroundBlastBuild.cs` mục 3b).
- Texture Library chỉ `LoadAssetAtPath`; 2 ảnh cần alpha được copy sang `Assets/VFX/MushroomBlast/Textures/`.
- Mask khói `T_GroundBlast_SmokeErode_TEMP` lấy từ video tham chiếu: **không ship**.
- Root là Particle System (Flash), Scaling Mode Hierarchy, không scale transform; mỗi lớp là prefab thành phần `CMP_MushroomBlast_<Layer>` (SaveNested).
- Thứ tự vẽ: Scorch −5 → Shockwave −4 → Skirt −3 → Stem −2 → Cap −1 → FireCore 0 → Debris 1 → Flash 2 → Sparks 3.
- Ngân sách: ~82 particle, 7 material, 0 texture mới vẽ.
