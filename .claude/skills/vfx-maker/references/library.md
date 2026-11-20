# Tìm asset tái sử dụng

Thứ tự tìm: **`Assets/Library/` → project hiện tại → thư viện của art lead / Shape Lab → thư viện VFX chung → tạo mới**. Tạo mới tốn thời gian (chờ ChatGPT, chỉnh sửa), nên tìm kỹ trước.

## 0. `Assets/Library/` (thư viện texture của project, luôn thử trước)

- Cây `Assets/Library/<nhóm>/<vai trò>/<nhóm>_<vai trò>_NNN` (đã chia lại 2026-11-09). Chọn theo bảng thành phần → thư mục ở `Docs/VFX/_Library/LIBRARY.md`; tên cũ, tên gốc và nguồn của từng file ở `Docs/VFX/_Library/library_index.csv`. Xem ảnh (Read PNG) rồi mới chọn.
- **Luật chọn 6 bước** (yêu cầu → bảng → contact sheet → lọc `library_props.csv` → chốt + dự phòng → kiểm sau dựng): `Docs/VFX/_Library/LIBRARY.md` mục "Luật chọn". Công cụ: `tools/library_props.py` (`--contact <nhóm>/<vai trò>`).
- File trong Library dùng chung: chỉ `LoadAssetAtPath`, không `ImportTexture` lên nó. Cần import setting khác thì copy ảnh (không copy `.meta`) sang `Assets/VFX/<Effect>/Textures/`.
- Các mục dưới đây (rpg-game, Shape Lab, animlibrary) là nguồn **gốc** hoặc nguồn dự phòng khi Library không có hình hợp. Ảnh lấy từ rpg-game thường đã nằm trong Library: tra `library_index.csv` theo tên gốc trước khi copy lại.

## Thư viện của art lead: `D:\Projects\rpg-game\Assets\RPG_VFX\Duong\Texture\`

Texture do art lead làm, ưu tiên hơn thư viện chung. Các thư mục chính:

| Thư mục | Nội dung |
|---|---|
| `Flipbooks/Fire` | Flipbook lửa (`TX_VFX_*`, lưới ghi trong tên, ví dụ `_4x4`) |
| `Smoke` | Khói. `TX_VFX_Smoke04/05/06` là khói cel-shading: alpha đặc, RGB mang 2–3 mảng tông, bóng lưỡi liềm ở phía khuất sáng |
| `Impact`, `Electric`, `Flame`, `Decals`... | Các nhóm khác |

Bỏ qua bản trùng có hậu tố `_Grayscale`, `_Gray`, `_C`, `_VertexOffset`, `" 1"`, `_Blur`, trừ khi cần đúng biến thể đó.

## Shape Lab và thư viện shape theo nguyên tố

Công cụ web của art lead để dựng shape bằng thông số thay vì mô tả bằng lời:
- Mở bản online: https://claude.ai/artifact/BAbVif8XRDWGL2Gt7Xkk9F
- File gốc: `D:\Game_prj\VFX_LIb\Docs\VFX\_ArtDirection\tools\shape_lab.html`

**Công cụ có:**
- Shape loại Lưỡi lửa, Cụm khói, Tự vẽ (cọ, tẩy, tô kín, Pen, Di chuyển điểm, Zoom).
- Bảng màu và nhóm Sáng tối (toon theo ánh sáng hoặc noise).
- Nhiều kiểu tan: từ lõi ra, từ mép vào, theo hướng, theo độ dày, theo độ sáng.
- Xuất PNG đơn, sheet 4×2/4×4 và JSON.

**Thư viện shape** (2026-11-02: 335 shape, đã nhập mọi texture VFX có hình rõ từ `D:\Projects\rpg-game\Assets`):
- 15 nhóm: 10 nguyên tố (fire, smoke, impact, water, lightning, ice, wind, earth, poison, magic) + 5 vai trò (glow, ring, slash, spark, trail).
- Danh sách: `tools/shape_library/library.json` (mỗi shape có `source` và `src` = đường dẫn gốc trong rpg-game). Mask gốc nằm ở `tools/shape_library/<element>/*.png`.
- `build` gộp mask + thumb vào atlas `tools/shape_library/_atlas/<element>_{m,t}_N.png` (4096², ~34 file). Tool chỉ tải atlas, vì artifact giữ tối đa 511 file. Khi publish, chỉ gửi `shape_library.js` + `shape_library/_atlas/*.png` (root = `tools`).
- Thêm ảnh: `python shape_library.py add <img> --element <id> --name "..."`.
- Thêm cả thư mục: `python shape_library.py import-folder <dir> --element <id>`.
- Nhóm Slash và Trail là texture chạy UV trên mesh: thư viện giữ nguyên khung và tỉ lệ gốc (`uv: true`, `aspect`). Lấy ảnh gốc theo `src` khi dựng mesh slash.
- Art lead xoá / chuyển nhóm shape ngay trong Shape Lab (lưu ở db `libEdits` của artifact). Áp vào thư viện gốc: `python shape_library.py apply-edits <libEdits.json>`.
- Kiểm kê nguồn rpg-game (đã có / chưa có): `Docs/VFX/_ArtDirection/library_inventory_rpg-game.md` + `.csv`.

**Texture tiện ích từ rpg-game** (noise 46, gradient/ramp 33, mask mềm/tile 28), copy kèm `.meta` vào `D:\Game_prj\VFX_LIb\Assets\VFX\_Shared\Textures\RpgLib\{Noise,Gradient,Mask}\`.

**Prefab / material / shader / mesh trong rpg-game** chưa copy, chỉ tra cứu tại chỗ:
- prefab effect của game: `_Game/Resources_moved/Prefabs/Effects` (433);
- prefab của art lead: `RPG_VFX/Duong/Prefab` (107);
- 39 shader (HunFX, CFXR Ubershader, HCFX, UberFX, Ice_Glacier, Electricity, Lightning, Procedural Ring, Distortion…) trong `RPG_VFX`, `VFX_Library`, `2D_Art/Vfx`;
- mesh: `RPG_VFX/Texture` (rock, ice, ring wind, lightning).

**Khi art lead dán JSON "Copy thông số"**, đọc nó như ý đồ hình khối chính xác. Có thể dùng PNG/sheet xuất từ Shape Lab trực tiếp làm texture: định dạng "Trắng + alpha (cho Unity)", với shading thì RGB mang tông còn alpha giữ silhouette.

## Project hiện tại

Tìm trong `Assets/VFX/_Shared/` và các effect đã làm (`Assets/VFX/*/Textures`, `Materials`). Dùng Glob theo tên (`**/T_Glow*`, `**/*Smoke*.png`).

## Thư viện: `D:\Projects\animlibrary\Assets\VFX_Library`

Nếu đường dẫn không tồn tại (máy khác), hỏi người dùng đường dẫn thư viện.

Cấu trúc chính:

| Thư mục | Nội dung |
|---|---|
| `Textures/` | ~750 texture VFX (glow, slash, decal, rune, smoke, noise...) |
| `Materials/`, `Shaders/` | material/shader của các pack (Cartoon FX `.cfxrshader`, HCFX, Shader Graph...) |
| `Meshes/`, `FBX/` | mesh VFX |
| `VFX/` | prefab tham khảo theo pack |
| `Docs/References/<Pack>/` | manifest + preview theo pack |

Mỗi pack có `VFX_PackManifest.json` (`assets[]` gồm `path`, `type`, `name`) — grep trong các manifest để tìm nhanh theo từ khóa, rồi kiểm tra file thật.

### Cách tìm

1. Grep tên file theo từ khóa tiếng Anh của hình cần: `glow`, `flare`, `spark`, `streak`, `smoke`, `puff`, `ring`, `wave`, `slash`, `trail`, `noise`, `crack`, `debris`, `fire`, `flame`, `magic`, `rune`, `dot`, `star`.
2. Chọn 2–4 ứng viên, **mở xem ảnh** (Read file PNG/TGA). Đánh giá: silhouette, có alpha hay nền đen, grayscale hay đã có màu, flipbook hay ảnh đơn, độ phân giải.
3. Ưu tiên texture grayscale/trắng (tint được bằng màu particle) hơn texture đã tô màu.

### Copy vào project

- Chỉ copy file ảnh/mesh, **không copy `.meta`** (để Unity tạo GUID mới, tránh trùng GUID giữa hai project).
- Đổi tên theo [naming.md](naming.md), ghi nguồn vào `Plan.md`.
- **Không copy material dùng shader riêng của pack** (`.cfxrshader`, Shader Graph có subgraph) — chúng kéo theo importer/dependency. Lấy texture rồi gán vào shader chuẩn hoặc `SH_VFX_Particle`.
- Prefab thư viện chỉ dùng để **tham khảo thông số** (đọc file `.prefab` YAML: lifetime, size, emission, curve), không copy nguyên prefab.

### Texture nền đen không có alpha

Dùng được với blend Additive trực tiếp. Với Alpha blend, import bằng `ImportTexture(path, size, alphaFromGray: true)` để lấy độ sáng làm alpha.
