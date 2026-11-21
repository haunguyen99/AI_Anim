# Kiểm kê asset VFX trong `D:\Projects\rpg-game\Assets` (2026-11-02)

Chỉ đọc, không sửa gì trong rpg-game. Danh sách đầy đủ từng texture (đường dẫn, lớp, trạng thái): `library_inventory_rpg-game.csv` (cùng thư mục).

"Đã có" = đã nằm trong Shape Lab, hoặc cùng tên file trong thư viện chung `animlibrary/Assets/VFX_Library` (library.md), hoặc trùng nội dung (md5) với file khác trong rpg-game.

## 1. Tổng số theo loại

| Loại | Số lượng | Nằm chủ yếu ở |
|---|---|---|
| Texture VFX | 940 (57 không phải VFX: icon, UI, PBR) | `RPG_VFX/Duong/Texture` 415, `RPG_VFX/Texture` 155, `_Game/Resources_moved/Textures` 263 |
| Prefab particle | ~620 | `_Game/.../Prefabs/Effects` 433 (effect của game), `RPG_VFX/Duong/Prefab` 107, pack 80 |
| Material | ~560 | đi kèm prefab |
| Shader | 39 | HunFX, CFXR Ubershader, HCFX, UberFX, Ice_Glacier, Electricity, Lightning, Procedural Ring, Distortion… |
| Mesh | ~130 | `RPG_VFX` (rock, ice, ring wind, lightning, arrow…) |

## 2. Texture: đã có / chưa có

| Lớp | Chưa có | Có ở animlibrary | Có ở Shape Lab | Trùng nội bộ |
|---|---|---|---|---|
| Lửa | 66* | 14 | 34 | 0 |
| Khói / bụi | 13 | 26 | 22 | 1 |
| Impact / burst | 34 | 21 | 10 | 3 |
| Đất / nứt / decal | 34 | 20 | 0 | 3 |
| Nước / splash / máu | 15 | 8 | 0 | 0 |
| Điện | 14 | 14 | 0 | 1 |
| Băng | 8 | 8 | 0 | 0 |
| Gió | 9 | 5 | 0 | 1 |
| Độc | 3 | 4 | 0 | 0 |
| Phép (rune, magic circle, symbol) | 11 | 3 | 0 | 0 |
| Glow / flare | 25 | 38 | 0 | 4 |
| Ring / radial / wave | 38 | 35 | 0 | 6 |
| Slash | 23 | 19 | 1 | 2 |
| Trail / beam | 25 | 14 | 0 | 4 |
| Spark / star | 27 | 10 | 0 | 0 |
| Mask | 13 | 4 | 0 | 2 |
| Noise (tiện ích) | 47 | 55 | 0 | 6 |
| Gradient / ramp (tiện ích) | 34 | 15 | 0 | 0 |
| **Tổng VFX** | **~440** | ~320 | 67 | 34 |

\* Lửa "chưa có" gồm ~20 biến thể `_C/_Grayscale/_Blur` đã cố ý bỏ, và 10 flipbook lửa chỉ có ở dạng PSD (`FlipbookPSD`: DirectionalFlame_02, FireImpact_01/02, GroundFire_01/03, SimpleFlame_01, TiledFlames_01, TorchlightLoop_01, Traveling_03, VerticalFlame_01).

Phần chưa có nằm chủ yếu ở: thư viện Duong (243 file: Decals, Electric, Flame, Flipbooks gốc, Glow, Mask, Noise, Radials, Ramps, Shared, Slash, Spark, Trails, Water, Wave), `_Game/Resources_moved/Textures` (127), `RPG_VFX/Texture` (~50), `2D_Art/Vfx` (14), `EffectCore` (8). Hovl Studio và `VFX_Library` (pack) đều đã có ở animlibrary.

## 3. Giới hạn cần biết

- Artifact Shape Lab giữ tối đa **511 file/phiên bản**. Mỗi shape = 2 file (mask + thumb). Hiện đã dùng ~140 → còn chỗ cho **~180 shape** nữa.
- Noise, gradient, ramp không phải shape → không hợp với Shape Lab.

## 4. Đề xuất nhập vào đâu

| Nhóm | Đề xuất |
|---|---|
| Shape có hình rõ (impact, slash, spark, glow, ring, trail, nứt đất, nước, điện, băng, gió, độc, phép, flipbook lửa PSD) | Shape Lab, nguyên tố có sẵn + thêm nguyên tố/vai trò mới `glow`, `ring`, `slash`, `spark`, `trail`, `decal`. Ưu tiên thư viện Duong, chọn lọc để vừa ~180 slot |
| Noise, gradient, ramp, mask | Thư viện texture chung trong VFX_LIb: `Assets/VFX/_Shared/Textures/<Noise|Gradient|Mask>/` (copy kèm .meta), ghi vào library.md |
| Prefab, material, shader, mesh | Không copy hàng loạt (phụ thuộc lẫn nhau, 600+ prefab là effect của game). Chỉ ghi chỉ mục vào library.md để tham khảo; lấy từng cái khi cần |

## 5. Đã làm (bản thử 2026-11-02, chờ art lead đánh giá)

- Shape Lab: thêm **262 shape** (tổng 335), thêm 5 vai trò `glow`, `ring`, `slash`, `spark`, `trail`. Mỗi shape ghi `src` = đường dẫn gốc trong rpg-game.
- Thư viện chuyển sang atlas (`tools/shape_library/_atlas/`, 34 file), nên không còn vướng giới hạn 511 file.
- Phân loại theo tên file rồi sửa tay sau khi xem contact sheet. Grid flipbook tự dò, nên có thể sai ở vài sheet không ghi lưới trong tên (ví dụ `Tex_fx_splash_set`, `healing`).
- Bỏ qua: biến thể `_C/_Gray/_Blur/ 1/ - Copy/(n)`, file trùng md5, file đã có ở animlibrary, PSD lửa đã có bản PNG, `Vortex 4` và `WindAlpha_02` (không tách được shape).
- Tiện ích: 107 file copy vào `Assets/VFX/_Shared/Textures/RpgLib/{Noise,Gradient,Mask}/` (kèm .meta).
- Prefab / material / shader / mesh: chưa copy, chỉ ghi chỉ mục trong `references/library.md`.
