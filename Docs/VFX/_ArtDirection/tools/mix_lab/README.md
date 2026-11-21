# Mix Lab — ghép thành phần VFX (web + Unity) · v1 (2026-11-02)

- Bản online: https://claude.ai/artifact/CMFUvsBJ6YeqapsMZoNwbt
- Bản local: `mix_lab.html` qua server `shape-lab` (http://localhost:8765/mix_lab/mix_lab.html). Mở trực tiếp file:// thì không tải được `mix_data.js` và ảnh.

## Auto mix (mặc định từ 2026-11-02)

Art lead: "mix sẽ để thành auto: Claude tự mix thành phần theo thông tin ban đầu, có vấn đề tôi yêu cầu đổi".

1. Khi có yêu cầu VFX mới, **xác định không gian trước** (vfx-maker mục 1a). Chưa rõ ngữ cảnh (đất / trên không / có hướng) thì hỏi.
2. Ghi brief rồi chạy `python -I auto_mix.py <brief.json | ->`. Brief gồm `name`, `context`, `element`, `weight`, `smoke`, `mark`. Script chọn thành phần, nhịp, độ to, bảng màu, in **lý do từng lựa chọn**, và ghi recipe vào `Docs/VFX/_Recipes/`.
3. Chạy `MixRecipeBuild` → xem preview → đăng Review Lab → báo art lead, kèm lý do các lựa chọn.
4. Art lead yêu cầu đổi: sửa recipe (hoặc brief) rồi dựng lại. Art lead cũng có thể mở recipe trong Mix Lab để tự chỉnh, rồi copy gửi lại.

Luật hiện tại (trong `auto_mix.py`):
- luôn có: Chớp (0 s), Quầng (0 s), Tia lửa (0.02 s);
- Vòng sóng từ đòn vừa (0.03 s); đòn nặng có thêm vòng vọng (0.13 s, 0.7×);
- khói: đòn nhẹ không có khói; lửa tại đất dùng lửa → khói; còn lại dùng khói bụi theo ngữ cảnh (0.05 s);
- vết cháy: tại đất, khi đòn nặng hoặc nguyên tố lửa; phần nóng đổi màu theo nguyên tố;
- độ to: nhẹ 0.8 / vừa 1 / nặng 1.25; thời lượng: nhẹ ×0.85 / nặng ×1.15;
- trên không và có hướng: đặt ở độ cao 1.1 m.

Đã thử: `IceSlam_Ground` (đất · băng · nặng), `ArcaneHit_Air` (trên không · phép · nhẹ).

## Quy trình thủ công (Mix Lab)

1. **Ghép trên web** (Mix Lab):
   - bấm `+` để thêm thành phần;
   - trên timeline: kéo khối để đổi delay, kéo mép phải để đổi thời lượng, bước 1/30 s;
   - bảng Thông số: cỡ, cường độ, xoay Y, vị trí x/y/z (m);
   - bảng màu Core / Mid / Outer / Dust, có preset Lửa / Băng / Độc / Điện / Phép / Thánh;
   - xem trước 2 góc: 3/4 game và ngang.
2. **Copy recipe** → dán vào chat. Claude lưu thành `Docs/VFX/_Recipes/<Tên>.json`.
3. **Unity dựng:** menu `VFX/Components/Build From Recipe...`, hoặc chạy batch:
   `Unity -batchmode -projectPath . -executeMethod VfxEffects.MixRecipeBuild.BuildBatch -recipe Docs/VFX/_Recipes/<Tên>.json`
   → `Assets/VFX/Mixes/<Tên>/Prefabs/VFX_<Tên>.prefab` + scene demo, preview ở `Docs/VFX/<Tên>/` (hiện trên Review Lab).

## Recipe

```json
{ "name": "FireHit_Ground", "version": 1,
  "palette": { "Core": "#FFF3C4", "Mid": "#FF9A3C", "Outer": "#C8281E", "Dust": "#CDBBA6" },
  "items": [ { "id": "RNG_Ground_01", "delay": 0.03, "duration": 0.52, "size": 1, "intensity": 1, "rotation": 0, "offset": [0, 0, 0] } ] }
```

Ý nghĩa từng trường khi Unity dựng (`MixRecipeBuild.cs`):

| Trường | Áp vào Unity |
|---|---|
| `id` | Thành phần `CMP_<id>`, chép rồi unpack (không giữ liên kết prefab) |
| `delay` | Cộng vào Start Delay của mọi particle system (đổi theo tốc độ) |
| `duration` | `simulationSpeed = độ dài gốc / duration` |
| `size` | Scale của GameObject (Scaling Mode Hierarchy) |
| `intensity` | Nhân alpha của Start Color và Color over Lifetime |
| `rotation` | Xoay Y (độ) |
| `offset` | Vị trí (m) |
| `palette` | Thay đúng các màu chuẩn `ComponentKit.Core / Mid / Outer / Dust` trong Start Color và các key gradient |

## Dữ liệu cho web

- Tạo bằng `VFX/Components/Mix Lab - Capture Data`, script `Assets/VFX/_Components/_Mix/Editor/MixCapture.cs`.
- Mỗi thành phần được chụp 30 fps từ 2 camera cố định, ô 256 px. Mỗi frame chụp trên nền đen và nền trắng để tách alpha.
- Output: `data/<id>_<q|s>.png` (8 cột), `data/plate_<q|s>.png` (nền lưới + người 2 m), `mix_data.js` (frame, độ dài, phép chiếu camera để tính vị trí x/y/z).
- **Chụp lại sau khi thêm hoặc sửa thành phần**, rồi đăng lại trang + `mix_data.js` + `data/*.png`, chia mỗi lần không quá ~35 file.

## Giới hạn hiện tại

- Xem trên web là gần đúng:
  - đổi màu bằng cách xoay hue;
  - xoay Y chỉ có tác dụng trong Unity;
  - lớp Add được ghép gần giống chế độ screen.
- **Thành phần làm bằng codefx (Scorch, CodeFX) có màu nằm sẵn trong texture.** Khi palette khác mặc định, `MixRecipeBuild` gọi `codefx/render.py --like <json> --opts-file <palette>` để render lại sheet theo palette, lưu cache ở `Assets/VFX/Mixes/_Palettes/<fx>_<hash>/` và gắn material bản sao (2026-11-03). Cần Python trong PATH.
- Chưa có hit-stop / rung camera trong recipe (đề xuất A2 trong PIXELFX_ANALYSIS).
