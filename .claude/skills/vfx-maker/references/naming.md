# Quy ước đặt tên

Mục tiêu: nhìn tên là biết loại asset, thuộc effect nào, dùng thế nào. Tên tiếng Anh, PascalCase, phân tách bằng `_`, không dấu cách, không tiếng Việt có dấu.

## Thư mục

```
Assets/VFX/
├── _Kit/                    build kit (Editor/, Runtime/) — dùng chung
├── _Shared/                 asset dùng cho nhiều effect
│   ├── Textures/  Materials/  Shaders/  Meshes/
└── <Effect>/                một thư mục cho mỗi effect
    ├── Editor/<Effect>Build.cs
    ├── Prefabs/  Materials/  Textures/  Meshes/  Scenes/
Docs/VFX/<Effect>/           Plan.md, BuildReport.txt, Preview_sheet.png (ngoài Assets)
```

Asset chỉ effect đó dùng → thư mục effect. Từ effect thứ hai trở đi cần dùng lại → chuyển vào `_Shared/` (cập nhật đường dẫn trong các build script liên quan).

## Tên effect

`<Element/Chủ đề><Hành động/Loại>` PascalCase: `FireballImpact`, `IceShardProjectile`, `PoisonAura`, `HealBurst`. Biến thể thêm hậu tố: `FireballImpact_Small`, `FireballImpact_Blue`.

## Tiền tố asset

| Loại | Mẫu | Ví dụ |
|---|---|---|
| Prefab | `VFX_<Effect>[_<Variant>]` | `VFX_FireballImpact`, `VFX_FireballImpact_Small` |
| Prefab thành phần (mỗi lớp 1 prefab, lồng trong `VFX_`) | `Prefabs/Components/CMP_<Effect>_<Layer>` — dựng bằng `VfxBuildKit.SaveNested` (kit 1.1.0) | `CMP_GroundBlast_Smoke` |
| Material | `M_<Effect>_<Layer>_<Blend>` | `M_FireballImpact_Flash_Add`, `M_FireballImpact_Smoke_Alpha` |
| Material dùng chung | `M_<Mô tả>_<Blend>` | `M_Glow_Soft_Add` |
| Texture | `T_<Mô tả>[_<Biến thể>][_<Cols>x<Rows>]` | `T_Glow_Soft`, `T_Smoke_Puff_4x4`, `T_Spark_Streak` |
| Texture tạm | thêm `_TEMP` | `T_Spark_Streak_TEMP` |
| Mesh | `SM_<Effect>_<Tên>` hoặc `SM_<Mô tả>` | `SM_FireballImpact_Debris_A`, `SM_Ring_Flat` |
| Shader (file) | `SH_<Tên>.shader` | `SH_VFX_Particle.shader` |
| Shader (path trong menu) | `VFX/<Tên có dấu cách>` | `VFX/Particle Basic` |
| Build script | `<Effect>Build.cs`, menu `VFX/<Effect>/Build` | `FireballImpactBuild.cs` |
| Demo scene | `<Effect>_Demo.unity` | `FireballImpact_Demo.unity` |

`<Blend>`: `Add` (additive), `Alpha` (alpha blend), `Mul` (multiply), `Premul` (premultiplied).

Hậu tố flipbook `_<Cols>x<Rows>` bắt buộc khi texture là sheet nhiều frame — build script đọc nó để cấu hình Texture Sheet Animation đúng.

## GameObject trong prefab

- Root: trùng tên prefab (`VFX_FireballImpact`).
- Layer con: tên vai trò, PascalCase, không lặp tên effect: `Flash`, `Glow`, `Core`, `Sparks`, `Embers`, `Smoke`, `Shockwave`, `Debris`, `Trail`, `Ground`, `Decal`.
- Nhiều layer cùng loại: `Sparks_01`, `Sparks_02` hoặc mô tả rõ hơn `Sparks_Fast`, `Sparks_Slow`.
- Nhóm khi có nhiều phần: `Charge/`, `Projectile/`, `Impact/` là GameObject rỗng chứa các layer.

## Asset từ thư viện

Đổi tên theo quy ước khi copy vào project. Ghi tên + đường dẫn gốc vào `Docs/VFX/<Effect>/Plan.md` để truy ngược được.
