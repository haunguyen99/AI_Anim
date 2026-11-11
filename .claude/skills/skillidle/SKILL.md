---
name: skillidle
description: Dựng anim idle (loop) cho nhân vật Spine 2D đã rig, bằng bộ máy có sẵn (tools/spine/idle_engine.py) và kho case đã duyệt (Cừu cầm ô, Cừu Sakura) để ra bản dùng được ngay lượt đầu. Dùng khi người dùng gõ /skillidle, hoặc xin "làm idle", "anim idle", "loop đứng / lơ lửng / thở" cho một skeleton Spine (sau khi rig xong).
---

# /skillidle: idle loop Spine từ kho case

Mục tiêu: idle đạt trong **1–2 lượt** (Cừu Sakura cần 3 lượt, 6,8 phút gen + 11 phút người xem; Cừu cầm ô nhiều hơn).
Mọi số mặc định dưới đây là số **người dùng đã duyệt**, không phải đoán. Trả lời bằng tiếng Việt. Luật chung Spine ở skill `spine2d`.

## 0. Trước khi làm (2 phút)
1. Đọc [CASES.md](CASES.md): tìm case gần nhất (nhân vật cưỡi / cầm vật bay / đứng). Bắt đầu từ cấu hình của case đó.
2. Kiểm sửa tay của người dùng trên file (không đè):
   `.venv/Scripts/python.exe -I -c "import sys; sys.path.insert(0,'tools/spine'); import anim_kit as K; print(K.user_edits('<json>', 'idle'))"`
   Có `user_since_claude` → hỏi / chép key đó vào cấu hình trước khi dựng.
3. Kiểm rig theo danh sách mục 2. Thiếu thì sửa rig trước (sửa sau tốn cả vòng anim).

## 1. Thông tin cần có (chỉ hỏi cái còn thiếu)
- File skeleton JSON + ảnh (`work/<game>/spine/<anim>/`). Spine Live: `http://127.0.0.1:8780/spine?json=<json>`.
- Mô tả của người dùng: cái gì chuyển động (ctrl tổng, thân, tay cầm đồ, chân, tai, khăn, chuông...).
- Độ dài loop: mặc định **96F** (cưỡi vật) / **90F** (lơ lửng), 30 fps.

## 2. Rig phải sẵn (bài học đã trả giá)
- Mặt nghiêng: `head` dọc đường giữa mặt; mắt / mày / miệng / mũi **rotation local 0 theo head** (trục X = dọc mặt) → bóp mắt / mở miệng bằng scaleX không bị xéo.
- **Miệng**: gốc xương ở mép trên miệng (ngay dưới mũi) → scaleX = mở miệng xuống. **Mũi là con của miệng, `inherit: noScale`** (dời + xoay theo đầu, không ăn scale). Không dùng `onlyTranslation`: mũi sẽ không xoay theo đầu.
- Slot mắt có thêm ảnh mắt nhắm (`eyeClose_L/R`).
- Tóc mái: chỉ scale (người dùng: "tóc chỉ scale nhẹ chứ không rotate").
- Vây / phụ kiện gắn thân: 1 xương, mesh gốc 100% xương thân gần nhất. Khăn: xương 1 kéo cả 2 dây, xương 2 chỉ dây dài. Chuông: cả nơ 100% xương thân.

## 3. Dựng (5 phút)
1. Chép `examples/cuusakura_idle_cfg.py` thành `<thư mục anim>/idle_cfg.py`. Đổi `FOLDER` / `PATH`, đổi tên xương theo bảng **vai trò** ở đầu file mẫu, xoá vai trò không có.
2. Đặt số theo **bảng preset** (mục 4). Mọi số người dùng hay sửa khai báo `P.num(...)` → thanh trượt "Tham số anim" trên Spine Live.
3. Chạy: `.venv/Scripts/python.exe -I <thư mục anim>/idle_cfg.py` (ghi anim `idle`, giữ anim khác, có Hoàn tác trên Spine Live).

Bộ máy (`tools/spine/idle_engine.py` + `tools/spine/anim_kit.py`), đã kiểm khớp tuyệt đối với script Cừu Sakura:
- mỗi xương = sóng riêng `OWN` (biên độ, số nhịp / loop, pha) + **quán tính** `INERTIA` (gain, trễ): con giữ hướng thế giới cũ rồi đuổi theo cha → overlap tự đúng thứ tự chuỗi;
- `TRANSLATE` / `SCALE` tuần hoàn; `CHAINS` = physics thật (lò xo + giảm chấn + gió / nước), chạy tới tuần hoàn rồi khép loop;
- `BLINK` = chớp mắt 3 bước (mục 4); key đều 12 / loop, curve bezier khớp sóng (ít key, sửa tay được trong Spine).

## 4. Preset đã duyệt
| Vai trò | Giá trị | Nguồn |
|---|---|---|
| Ctrl tổng (vật cưỡi) | xoay ±3°, nhấp nhô 6 px lệch 1/4 nhịp | Sakura |
| Ctrl bay (ô) | nhấp nhô 14 px, trôi ngang 6 px, nghiêng 1,5° theo vận tốc | Cừu cầm ô |
| Nhân vật đi theo ctrl | trễ **~20F** so với ctrl (người dùng: "cừu đang xoay cùng lúc với ô" = sai) | Cừu cầm ô |
| Thân → đầu | 2 / 1,5 / 2,5°, pha 0,10 / 0,18 / 0,28; quán tính 1,0·8F / 0,6·5F / 0,7·6F | Sakura |
| Thân / đuôi vật cưỡi | nhịp 2: 2 / 3,5 / 7°, pha 0,15 / 0,30 / 0,45 | Sakura |
| Tay cầm đồ vẫy (quạt) | nhịp 2: 4 / 6 / 10°, pha 0 / 0,10 / 0,22 | Sakura |
| Tay kia / chân | 4–5°, nhịp 1; hai chân lệch pha | Sakura |
| Tai | sóng 3 / 4° + quán tính 1,2·8F / 1,2·6F | Sakura |
| Chuông treo | sóng 4–6° + quán tính 1,3–1,5·6–10F | Sakura |
| Sừng | **chỉ nhích**: 0,8° + quán tính 0,25 (2,5° bị chê nhiều) | Sakura |
| Miệng | scaleX +18% tối đa, 1 nhịp / loop (+10% bị chê ít; > 25% méo) | Sakura |
| Tóc mái | scale 1,5% / 3,5%, không xoay | Sakura |
| Chớp mắt | ~F60–62: scaleX 100 → 60% (2F) → ảnh nhắm giữ 2F → 60% → 100% (2F); mày hạ 5–6 px | cả hai |
| Khăn / ruy băng (physics) | 0,9–1,0 Hz, giảm chấn 0,22–0,30, gió 170–320 | cả hai |
| Vây (physics) | 1,2 Hz, 0,30, nước 500 (±4–5°) | Sakura |

Góp ý thường gặp → sửa gì:
- "cứng / như máy" → chuyển phần mềm sang `CHAINS` physics, đốt sau trễ hơn đốt trước.
- "xoay cùng lúc" → tăng trễ quán tính (`lag`) hoặc trễ nhân vật sau ctrl.
- "lợn cợn" → mỗi chuỗi một nhịp chung, đốt sau trễ vài frame. Không cho mỗi đốt một chu kỳ riêng.
- "chớp mắt giật" → cơ chế 3 bước ở trên, không đổi ảnh thẳng.

## 5. Tự kiểm trước khi báo (2 phút)
- `spine_live_cmd.py measure <json> --anim idle --rot <xương chính>`: loop F0 = F cuối **0 px**; gia tốc lớn nhất ≲ 15 px/f² (trừ chớp mắt); góc nằm trong preset.
- `spine_live_cmd.py snap <json> --anim idle --frames 0,24,48,72 --out <anim>/_live/idle_check.png`: xem ảnh, không rách mesh.
- `spine_live_cmd.py show <json> --anim idle --say "..."` để người dùng xem ngay.
- Import `.spine` mới (bản cũ dời `_vN/`); cập nhật dòng của anim trong `MAP.md`.

## 6. Sau khi duyệt: nạp vào kho
Thêm một mục vào [CASES.md](CASES.md): yêu cầu gốc, số lượt, từng góp ý → đã sửa gì, số chốt (chỗ khác preset), thời gian, phần người dùng tự key. Số chốt khác preset mà được duyệt ở ≥ 2 nhân vật thì sửa bảng preset.
