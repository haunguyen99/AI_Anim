---
name: exportspine
description: Xuất bản giao Spine 2D (JSON + atlas + PNG) cho game theo đúng setting Export người dùng đang dùng trong Spine, kèm bản .spine giao và kiểm bản xuất bằng runtime thật. Dùng khi người dùng gõ /exportspine, hoặc nói "xuất spine", "export spine", "xuất bản giao", "giao file cho game" cho một skeleton Spine đã làm xong anim.
---

# /exportspine: xuất bản giao Spine

Trả lời bằng tiếng Việt. Luật chung Spine ở skill `spine2d` (bước 8–9 của quy trình).

Một lệnh làm hết: `tools/spine/export_spine.py`. Không gọi `spine_export` của MCP với setting mặc định.
Ngày 2026-10-26, bản xuất theo mặc định của CLI (`.atlas`, PMA, tên theo project) bị báo lỗi trong game.

## 1. Trước khi xuất (1 phút)
1. Xác định file skeleton JSON làm việc (`work/<game>/spine/<Anim>/<x>.json`) và **tên asset giao** (`--name`). Tên asset thành tên file export (`<Tên>.json`, `<Tên>.atlas.txt`, `<Tên>.png`). Người dùng chưa nói tên thì lấy tên thư mục anim.
2. Kiểm người dùng có đang sửa dở trên Spine Live không, để xuất đúng bản mới nhất:
   ```bash
   .venv/Scripts/python.exe -I tools/spine_live_cmd.py history <json>
   ```
   Lần ghi cuối của người dùng sau lần gen cuối của Claude thì bản xuất đã gồm sửa đó. Báo người dùng một dòng.
3. Chọn anim giao.
   - Mặc định: mọi anim trừ `setup`, `rig_test`, `test_*`, tên bắt đầu `_`.
   - Có idle + active mà chưa có `mix` thì hỏi có cần mix không. Mix dựng bằng `K.mix(...)`, mẫu `work/test/spine/CuuSakura/build_mix.py`.
4. Xem trước setting + danh sách anim:
   ```bash
   .venv/Scripts/python.exe -I tools/spine/export_spine.py <json> --name <Tên> [--anims idle,active,mix] --dry
   ```
   Báo người dùng scale atlas đang đặt trong Spine. Scale này đổi theo từng lần người dùng xuất tay: Cừu Sakura 1.3, cừu bóng bay 1.18. Chỉ dùng `--scale` khi người dùng nói rõ.

## 2. Xuất (~15 giây)
```bash
.venv/Scripts/python.exe -I tools/spine/export_spine.py <json> --name <Tên> [--anims ...] [--scale S] [--out <thư mục>]
```
Script làm:
1. **Setting**:
   - đọc `C:/Users/<user>/Spine/settings/editor-2.json`, khoá `export.json`. File này là JSON libgdx, khoá và chuỗi không có ngoặc kép, nên `json.load` sẽ lỗi; script có bộ đọc riêng `parse_gdx`;
   - ghi ra `<thư mục>/export_settings.json` (`"class": "export-json"`, output = thư mục export).
2. **Bản giao** `<tên>_final.json`: chỉ giữ anim giao. Import ra project mới `<Tên>_final.spine` (cờ `-r` thay project cũ). Không đè project làm việc của người dùng.
3. **Export** vào `<thư mục>/export/`. Bản xuất cũ dời sang `export_old/`.
4. **Kiểm**:
   - đủ anim, không thừa;
   - độ dài từng anim khớp bản nguồn. `cleanUp` xoá key giữ ở cuối làm anim ngắn lại; khi đó script tự thêm event `loop_end` ở cuối anim đó rồi xuất lại;
   - atlas đúng đuôi, không PMA; liệt kê trang PNG.

   Dòng cuối phải là `KẾT QUẢ: đạt`.

## 3. Tự kiểm bằng runtime thật (1 phút)
Spine Live đọc được atlas `.atlas.txt` cạnh file export (cầu nối `bridge.js`, hàm `findAtlas`). Trang phải đang mở (`spine_live_cmd.py status`).
```bash
.venv/Scripts/python.exe -I tools/spine_live_cmd.py snap <thư mục>/export/<Tên>.json --anim <anim> --frames 0,30,60 --out <thư mục>/_live/export_check.png
.venv/Scripts/python.exe -I tools/spine_live_cmd.py measure <thư mục>/export/<Tên>.json --anim active --from idle
```
- Xem ảnh. Ảnh lấy từ atlas đã đóng gói, nên thiếu vùng hay lệch ảnh sẽ lộ ở đây.
- Nối idle ↔ active lệch ≲ 0,2 px là bình thường (làm tròn khi xuất).

## 4. Báo người dùng
- Đường dẫn thư mục `export/` và file `<Tên>_final.spine`.
- Từng anim kèm độ dài (giây / frame), scale atlas, số trang PNG + kích thước, có PMA hay không.
- Anim đã bỏ khỏi bản giao. Event `loop_end` nếu script đã thêm (game nhận thêm một event).
- Cập nhật dòng của asset trong `MAP.md` (bản giao, thư mục export, scale).
- Không commit / push khi người dùng chưa bảo.

## Bài học
- 2026-11-03 Cừu cầm bóng bay (`work/test/spine/MascotBackToSchool/`): skill tạo từ lần xuất này.
  - Setting người dùng: `.atlas.txt`, scale 1.18, không PMA, pot + square, max 2048, `cleanUp`, `nonessential`, `perskeleton`.
  - Kết quả: idle + active 90F, 1 trang 2048×2048, kiểm runtime đạt.
  - Spine Live trước đó chỉ tìm `.atlas` hoặc atlas tự sinh, nên bản export (`.atlas.txt`) báo 404; đã thêm `findAtlas`.
- 2026-11-18 Char4 trên **máy Linux**: Spine cài ở `~/.local/opt/Spine/Spine.sh` (CLI `-u 4.2.43` chạy được); `~/.spine/settings/editor-3.json` có `export:{}` (chưa từng xuất trên máy này) -> `export_spine.py` dùng `export_settings.json` mới nhất trong `work/` (setting người dùng lần giao trước trên Windows, lần này Invester: scale 1.5). Báo người dùng scale lấy từ đâu. Xuất 13 s, kiểm runtime đạt.
