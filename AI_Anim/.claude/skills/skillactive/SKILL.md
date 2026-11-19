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

Cừu cầm ô (90F, vật bay kéo nhân vật): ô vọt ~70 px chếch phải tới F24, nghiêng 7° ở F25 rồi quay về ngay (không hold), hạ dần tới F86. Cừu giật xoay về trước khoảng 8° rồi đung đưa tắt dần; chuỗi tay → thân → đầu / chân / đuôi cùng một nhịp.

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
| "chuyển active -> idle khựng / giật, cần giảm tốc từ từ" (Back to School, 4 lượt) | xem mục 4b: ctrl hạ theo đường giảm dần (ease out dài), bỏ key đảo chiều ở cuối, giảm chấn cao cho chân / tay / balo, rồi chạy `smooth_tail.py` |
| "lắc cuối mạnh quá" | bỏ cú nảy lại sau đỉnh, gió chỉ MỘT thùy (lên rồi về, không âm dư), giảm biên độ chuỗi bóng / dây ở cuối |
| "thân dưới đứt rời thân trên" | mesh quần: xương chân mất weight dần khi lên gần hông (`fade` trong `mesh()`), bỏ khớp bẻ body1 / body2 trong chain physics |
| "bay nhẹ" mà người xem không thấy bay | đo theo chiều cao nhân vật: 90 px trên 1275 px = không thấy; dùng ≥ 10% chiều cao (150 px) và có hạ lấy đà trước |

## 4b. Chuyển active -> idle phải giảm tốc (Cừu Back to School 2026-11-13: bị chê "khựng" 4 lần liền)
- **Đo trước khi sửa**: tốc độ thế giới (px / frame) của đầu xương ở 30 frame cuối active + 10 frame đầu idle (FK từ JSON; mẫu `work/_inbox/tung-backtoschool/spine/_fk.py`). Lỗi nhìn thấy là **dừng rồi bật lại** (tốc độ về ~0 rồi vọt lên 8-14 px/f) ở tay / chân; ctrl và thân thường đã mượt.
- Nguyên nhân thường gặp: (1) mốc cuối của ctrl là S-curve đối xứng + một mốc dư làm nảy lại; (2) chain physics tay / chân dao động tiếp ở 2-3 Hz khi phần mờ dần (`BLEND`) đang kéo về idle; (3) mốc ACT_ROT của tay có giá trị âm / dương rồi mới về 0 (đảo chiều).
- Cách sửa, theo thứ tự:
  1. Đường bay hạ: nhiều mốc giảm dần kiểu mũ (vd 150 → 93% → 62% → 27% → 8% → 0 ở F44 / 52 / 60 / 66 / 72) để tốc độ giảm đều tới ~1 px/f ở F71, không mốc dưới 0.
  2. Cú gió / lắc: một thùy, kết thúc sớm (về 0 ở ~F48 trên 72F), không âm dư.
  3. `BLEND = dict(base=(16, 50), env=(52, 72), phys=(0, 6, 46, 72), stiff=(0, 10, 44, 62))`: cửa sổ trả về idle rộng ra, bắt đầu sớm.
  4. Chain tay / chân / balo: giảm chấn ~1.0 (balo 0.9), lim 7-9°; tay nên bỏ khỏi `CHAINS` (chỉ `ACT_ROT`) nếu vẫn đảo chiều.
  5. **`examples/smooth_tail.py`** (chạy sau `active_cfg.py`; chép sang thư mục anim, sửa `PATH` / đường tới `tools/spine`): lọc Gaussian góc xoay mọi xương trong F40 → F72, tail-weighted, F0 và F72 giữ nguyên (trùng idle), pad bằng idle sau F72. **`SMOOTH_SIG=5.5`** (3.5 còn dừng nhẹ). Script cũng dựng lại `mix`. Sau lọc, tốc độ giảm đơn điệu, chỗ dừng nhất còn ≥ 1.4 px/f.
- Gửi demo: video có số frame (`jobs.py say` tự ghi), nêu fps + tổng frame + đoạn nào là anim nào.

## 5. Tự kiểm trước khi báo
- `spine_live_cmd.py measure <json> --anim active --from idle --rot <ctrl>,spine1,head,<phụ kiện>`:
  - nối với idle **0 px** cả hai đầu;
  - gia tốc lớn nhất ≲ 15 px/f² (trừ mắt);
  - **không có góc ±170°** (lật physics) và không có cú đổi > 40° trong 3–5 frame (quất như roi).
- Góc thế giới thân: `spine_live_cmd.py pose ... --bones spine1,spine2,head`. Đỉnh `spine2` / đầu phải trễ sau `spine1` vài frame.
- Snap frame mốc (`--frames 10,20,30,40,48,58`), xem ảnh: không rách mesh, tay không che mặt.
- Lỗi ở chỗ nối (vị trí lệch vài px ở F0): phép làm mượt lấn sang trước F0 → nhân tín hiệu với ramp 0–8F.

## 6. Mix, xuất, nạp kho
- **Tách anim riêng**: bản giao luôn là `idle` (loop) và `active` (một lần) riêng. Người xem chỉ muốn thấy active thì playblast chỉ active (73 frame cho 72F: frame 1 = F0, frame 73 = F72 trùng idle F0). `mix` chỉ để tự kiểm / khi game đòi, bỏ khỏi bản xuất (lọc `animations` trước khi import).
- **Quy ước số frame**: video demo đếm từ 1; F n của Spine = frame n+1 trên video; loop idle: frame cuối (F N) = F0, không đưa F N vào video (90F loop = 90 frame).
- **Video demo bằng runtime thật** (2026-11-18): `tools/spine/live_video.py <json> --anim mix --frames 0-<N>,0-<idle-1> --out <anim>/preview/<tên>_mix_demo.mp4` (trang Spine Live phải mở): đủ clipping / đổi ảnh slot / noScale, khung cố định, có số frame, ~40 s cho 350 frame. Dùng thay `render_spine.py` khi làm demo.
- **Bẫy bản xem trước**: `render_spine.py` KHÔNG vẽ đổi ảnh slot (chớp mắt / nhắm cười) và KHÔNG theo `inherit: noScale` (mũi), chỉ lấy frame `n = round(dur * fps)` (thiếu frame cuối). Bản sao đã vá ở `work/_inbox/tung-backtoschool/spine/render_demo.py` (slot attachment, noScale, thêm frame cuối). Cả hai đều là xem trước, chưa phải runtime Spine thật: luôn nói rõ chưa kiểm Spine thật.
- Mix: `K.mix(skel, "idle", "active", "mix", t_first=END/30)` rồi `K.write_anim(...)`. Mẫu: `work/test/spine/CuuSakura/build_mix.py`. Kiểm mix F0–N trùng idle, phần sau trùng active.
- Xuất: setting của người dùng lấy từ `C:\Users\<user>\Spine\settings\editor-2.json` khoá `json` (atlas `.atlas.txt`, scale như lần gần nhất, không PMA, cleanUp, nonessential). Mẫu `work/test/spine/CuuSakura/export_settings.json`. Bản giao chỉ giữ anim cần giao (bỏ `setup`, `rig_test`).
- Kiểm bộ máy khớp script cũ (khi chuyển script cũ sang cấu hình): chạy cả hai trên bản sao với `ANIM_KIT_PATH=<bản sao>` và `ANIM_KIT_DRY=1`, so `K.spine_curve` từng kênh từng frame (Cừu Sakura: lệch 0).
- Sau khi duyệt: thêm mục vào [CASES.md](CASES.md), ghi:
  - từng lượt góp ý và đã sửa gì;
  - **xương người dùng tự key** (đó là chỗ công thức chưa đạt; lần sau đặt pose cho phần đó trước);
  - số chốt khác preset.
