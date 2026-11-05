---
name: skillactive
description: Dựng anim active (hành động một lần, vào và ra đúng idle F0) cho nhân vật Spine 2D, kèm anim mix idle → active, bằng bộ máy có sẵn (tools/spine/active_engine.py) và kho case đã duyệt (Cừu cầm ô, Cừu Sakura). Dùng khi người dùng gõ /skillactive, hoặc xin "làm active", "anim hành động / nhảy / giãy / bay lên" nối từ idle, hay "mix idle với active".
---

# /skillactive: active một lần, nối idle, từ kho case

Mục tiêu: active đạt trong **≤ 3 lượt** và **không đè sửa tay của người dùng**. Ở Cừu Sakura, active tốn 6 lượt (21 phút gen + 35 phút người dùng). Cuối cùng người dùng tự key các xương quyết định nhịp, và 2 lần dựng lại đã đè mất sửa tay.

Trả lời bằng tiếng Việt. Idle làm trước bằng skill `skillidle`, active dùng chính cấu hình idle đó làm nền. Luật chung Spine ở skill `spine2d`.

## 0. Trước khi làm
1. Đọc [CASES.md](CASES.md) (và `../skillidle/CASES.md`): tìm case gần nhất, dùng cấu hình của case đó làm điểm xuất phát.
2. **Idle phải có cấu hình bộ máy** (`idle_cfg.py`). Nếu idle được dựng bằng script cũ, viết `idle_cfg.py` trước. Rồi kiểm khớp với script cũ trên bản sao (cách làm ở mục 6).
3. **Kiểm sửa tay trước MỌI lần dựng lại**:
   `.venv/Scripts/python.exe -I -c "import sys; sys.path.insert(0,'tools/spine'); import anim_kit as K; print(K.user_edits('<json>', 'active'))"`
   - Có keypose hoặc có `user_since_claude`: chép key của các xương đó từ file hiện tại vào `active_user_keys.json` ở thư mục anim (`{xương: {"rotate": [...]}}`), rồi mới dựng.
   - Bộ máy ghi các key đó y nguyên và cho physics các phần gắn trên chạy theo.
   - Người dùng nói "giữ key của X" thì làm đúng như vậy.

## 1. Chốt pose và nhịp trước khi gen đủ (bài học lớn nhất)
Người dùng đánh giá nhịp diễn theo cảm nhận. Công thức (sóng, quán tính) chỉ lo phần phụ. Vì vậy, trước khi chạy bộ máy:
- Viết bảng nhịp 4–6 mốc bằng chữ:
  - lấy đà;
  - bật / hành động chính;
  - đỉnh;
  - rơi / chạm (**sâu hơn idle rồi mới nảy về**);
  - lắng.

  Kèm frame và hướng của ctrl, thân, đầu, tay.
- Hỏi người dùng có muốn tự key 3–5 pose chính trên Spine Live không (Key pose, rồi bấm Gen). Có thì lấy đúng các pose đó làm mốc.
- Bản đầu để biên độ khoảng **60%** mức dự định, rồi tăng theo góp ý. Cả hai case đều bị chê "giật / quá" ở bản đầu.

## 2. Dựng (5–10 phút)
1. Chép `examples/cuusakura_active_cfg.py` thành `<thư mục anim>/active_cfg.py`, trỏ `IDLE` vào `idle_cfg.py` của nhân vật, đổi tên xương theo vai trò.
2. Các khối cấu hình (bộ máy `tools/spine/active_engine.py` lo phần nối):
   - **Đường bay ctrl**: chỉ key `FISH_Y` / `FISH_X` (đổi tên theo nhân vật). Góc ngóc / chúi và gia tốc **suy từ đường bay** bằng `K.path_drive(...)`, nên xoay luôn khớp dời. Lỗi "dời và xoay không fit, giật" xảy ra khi key xoay riêng.
   - **Thân / đuôi vật cưỡi**: một tín hiệu chạy dọc thân, đốt sau trễ 1–5F và biên độ tăng (`lag`). Tín hiệu = cú quẫy (`FLICK`, **một lần**) − quán tính gia tốc (chạm đáy thì đuôi văng xuống) + quán tính góc ctrl.
   - **Nhân vật** = chuỗi physics `spine1 → spine2 → head` do ctrl kéo:
     - `spine1` lò xo cứng (3,2 Hz), đích `REST_TGT = -0.75 × góc ctrl` để tự giữ thăng bằng, không xoay theo ctrl;
     - `spine2` / `head` overlap tự sinh;
     - ngồi trên khúc thân có nhịp quẫy thì thêm `REST_FB` (gain 0,07 / 0,10, trễ 2 / 5F) để chỗ ngồi nghiêng theo nhịp đó.
   - **Phụ kiện** (khăn, tai, chuông, vây, sừng): `Chain` với `hz_act` / `zeta_act` lúc nhảy, chặn góc `lim`. Chuỗi cha đứng trước chuỗi con trong `CHAINS`.
   - **Mặt**:
     - `EYES_CLOSED` nhắm mắt cười trong pha bay (cùng cơ chế chớp mắt);
     - miệng cười to scaleX 1,28;
     - tóc mái nảy scale lúc chạm.
   - Nền idle hoà `idle(f)` → `idle(f − L)` trong F16–56, lớp hành động tắt hẳn F62–72, physics hoà về idle hai đầu. Nhờ vậy F0 và F cuối **trùng idle F0 cả vị trí lẫn tốc độ**.
3. Chạy: `.venv/Scripts/python.exe -I <thư mục anim>/active_cfg.py`.

## 3. Preset đã duyệt (72F, nhân vật cưỡi vật cao ~1400 px)
| Phần | Giá trị |
|---|---|
| Đường bay | lấy đà −12 px F10 · đỉnh +150 px F30 · rơi **−32 px dưới idle** F47 · nảy +5 F57 · về 0 F72 |
| Ctrl ngóc / chúi | lớn nhất 14° theo vận tốc (bay lên ngóc khoảng 8°, rơi chúi khoảng 13°) |
| Đuôi quẫy | một cú: −3° F9 → +15° F21 → +2° F33 → 0 F44; thân 0,35 / 0,65 / 1,0 trễ 1 / 3 / 5F |
| Nhân vật | `spine1` thế giới chỉ ±6° (79–93°); đầu gật khi chạm khoảng 20–25° (thấy nhiều thì tăng `sheep_hz`) |
| Nhổm khỏi lưng | −4 px F20 · +8 F37 · −6 F49 (dồn xuống lúc chạm) |
| Tay vẫy | ±12° quạt (âm = giơ lên), tay kia +28°; quá 20° thì tay che mặt |
| Physics lúc nhảy | khăn 2,2 Hz / 0,4 / ≤ 55°; tai 3,2 / 0,55 / ≤ 35°; chuông 1,9–2,0 / 0,4 / ≤ 45°; vây 2,4–2,6 / 0,6 / ≤ 22°; sừng 4 Hz / ≤ 4° |
| Mắt / miệng | nhắm cười F20–44; miệng 1,28 từ F12–18 tới F46–56 |

**Vật bay kéo nhân vật treo (90F, duyệt ở 2 nhân vật: Cừu cầm ô, Cừu cầm bóng bay):**
- Bản đầu **chép đúng nhịp này**, không tự lập bảng nhịp mới. Cừu cầm bóng mất 2 lượt vì bản đầu có lấy đà, vẫy tay 2 nhịp, chân đá qua lại.
- **Ctrl:**
  - bay lên **một lần**, không lấy đà;
  - đỉnh ở F24 (Cừu cầm ô, 70 px) hoặc F36 (Cừu cầm bóng, 90 px; F24 bị chê "quá nhanh");
  - nghiêng 3–7° rồi về dần, không hold;
  - hạ đều tới F86–90.
- **Nhân vật:** **một** nhịp lắc tắt dần (`damp`, chu kỳ 58–80F); mọi đốt cùng nhịp đó, đốt sau trễ vài frame (`lagd`).
- **Phụ kiện:** physics giảm chấn cao (zeta 0,6–0,9), văng một lần rồi lắng.
- **Lớp hành động:** tắt dần trong ≥ 30F cuối (`BLEND` env (48, 72) theo thang 72F). Ép trong 12F cuối thì bị chê "recover chưa mượt".
- **Cả hai case:** người dùng tự key nhịp **tay nắm / tay vẫy** (Cừu Sakura cũng tự key thân / đầu / tay). Trước khi gen, hỏi rõ: "bạn key 2–3 pose tay nắm + tay kia không?".

## 4. Từ điển góp ý → sửa gì
| Người dùng nói | Sửa |
|---|---|
| "giật", "giật cục", "smooth lại" | bớt số lần đổi chiều; key đỉnh có tiếp tuyến 0 (`spl`); tăng giảm chấn physics; biên độ −30% |
| "giãy / quẫy 1 lần thôi" | `FLICK` một nhịp, bỏ sóng nhiều nhịp |
| "dời và xoay chưa fit" | xoay suy từ đường bay (`path_drive`), không key riêng |
| "xuống sâu hơn idle rồi mới về" | `DIP` dưới 0 ở pha chạm + đuôi văng xuống (quán tính gia tốc) |
| "spine1 xoay quá nhiều, chỉ để spine2 overlap" | tăng bù góc ctrl ở `REST_TGT` của spine1; overlap dồn lên spine2 |
| "physics theo nhịp của cá / vật cưỡi" | `REST_FB` từ xương thân nơi nhân vật ngồi |
| "khăn / tai chưa chuẩn physics" | `Chain` ăn đủ chuyển động (không giảm tỉ lệ), tai cứng hơn khăn; mô phỏng sau xương cha đã overlap |
| "trục xoay hold / dừng ở mốc" | mốc nối spline liên tục, không smoothstep từng đoạn |
| "tay che mặt" | giảm biên độ giơ tay ở pha có đầu ngửa |

## 5. Tự kiểm trước khi báo
- `spine_live_cmd.py measure <json> --anim active --from idle --rot <ctrl>,spine1,head,<phụ kiện>`:
  - nối với idle **0 px** cả hai đầu;
  - gia tốc lớn nhất ≲ 15 px/f² (trừ mắt);
  - **không có góc ±170°** (lật physics) và không có cú đổi > 40° trong 3–5 frame (quất như roi).
- Góc thế giới thân: `spine_live_cmd.py pose ... --bones spine1,spine2,head`. Đỉnh `spine2` / đầu phải trễ sau `spine1` vài frame.
- Snap frame mốc (`--frames 10,20,30,40,48,58`), xem ảnh: không rách mesh, tay không che mặt.
- Lỗi ở chỗ nối (vị trí lệch vài px ở F0): phép làm mượt lấn sang trước F0 → nhân tín hiệu với ramp 0–8F.

## 6. Mix, xuất, nạp kho
- Mix: `K.mix(skel, "idle", "active", "mix", t_first=END/30)` rồi `K.write_anim(...)`. Mẫu: `work/test/spine/CuuSakura/build_mix.py`. Kiểm mix F0–N trùng idle, phần sau trùng active.
- Xuất: setting của người dùng lấy từ `C:\Users\<user>\Spine\settings\editor-2.json` khoá `json` (atlas `.atlas.txt`, scale như lần gần nhất, không PMA, cleanUp, nonessential). Mẫu `work/test/spine/CuuSakura/export_settings.json`. Bản giao chỉ giữ anim cần giao (bỏ `setup`, `rig_test`).
- Kiểm bộ máy khớp script cũ (khi chuyển script cũ sang cấu hình): chạy cả hai trên bản sao với `ANIM_KIT_PATH=<bản sao>` và `ANIM_KIT_DRY=1`, so `K.spine_curve` từng kênh từng frame (Cừu Sakura: lệch 0).
- Sau khi duyệt: thêm mục vào [CASES.md](CASES.md), ghi:
  - từng lượt góp ý và đã sửa gì;
  - **xương người dùng tự key** (đó là chỗ công thức chưa đạt; lần sau đặt pose cho phần đó trước);
  - số chốt khác preset.
