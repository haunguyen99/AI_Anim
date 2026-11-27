# PixelFX trong Shape Lab

Nguồn: [patch-gg/pixelfx](https://github.com/patch-gg/pixelfx), bản `0.3.0` (clone 2026-11-02).
- License MIT, xem [LICENSE](LICENSE) và [NOTICE.md](NOTICE.md). Phải giữ 2 file này khi dùng lại asset.
- Font trong gallery của họ **không** thuộc MIT, và mình không lấy font đó.

## Đã nhập (2026-11-02)

- **187 effect**, chỉ lấy nhóm VFX:
  - arcane, explosions, fire, holy, ice, impacts, lightning, melee, nature, projectiles, scifi, shadow, spawn, status, water, weather.
  - Không lấy: ui, transitions, critters, pickups, moves.
- Trong Shape Lab, các effect nằm ở nhóm **PixelFX** (element `pixelfx`), tên dạng `<Nhóm> · <Tên>`, mask tone 4×4.
- `sheets/<nhóm>/<nhóm>-<tên>_4xN.png`: sheet **màu gốc**, tối đa 16 frame lấy mẫu đều.
  - Effect loop: lấy đều trong một vòng loop.
  - Effect một lần: lấy từ frame đầu tới frame cuối.
- `index.json`: thông số của từng effect, gồm fps gốc, loop, số frame gốc, frame đã chọn, kích thước frame, pivot.

## Lấy bản đủ frame (cho Unity)

Bản gốc đầy đủ khoảng 156 MB nên không lưu trong project. Muốn lấy lại thì chạy:

```bash
git clone --depth 1 https://github.com/patch-gg/pixelfx.git
cd pixelfx
node tools/sheets.mjs fire impacts        # → sheets/<nhóm>/<tên>.png + .json (Aseprite JSON, Unity đọc được)
node tools/render.mjs fire/torch --sheet --opts '{"palette":["#000","#555","#aaa","#fff"]}'   # đổi palette, vd xám
```

Cần Node 18 trở lên. Lần nhập này dùng Node portable trong thư mục tạm, không cài vào máy.

## Nhập lại / cập nhật

```bash
python -I pixelfx_import.py <pixelfx>/sheets
python -I ../shape_library/shape_library.py build
```

Script bỏ qua effect đã có. Sau đó đăng lại Shape Lab: trang + `shape_library.js` + `shape_library/_atlas/*.png`.
