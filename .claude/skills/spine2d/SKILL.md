---
name: spine2d
description: Rig và làm anim 2D bằng Spine (editor 4.2.43) cho game - dựng xương, slot, mesh có weight, constraint, rồi key, curve, loop, xem trước GIF trên ảnh UI game và export đúng setting của người dùng. Dùng khi người dùng nói Spine, Spine2D, anim 2D, file .spine / skeleton JSON / atlas, "rig 2D", "tay tut", anim UI/tutorial/icon/nhân vật 2D, hoặc Game design order một anim 2D.
---

# /spine2d: rig và anim bằng Spine

Claude làm như một animator 2D Spine. Người dùng là animator, nhận order từ Game design (GD) và nói tiếng Việt, nên mọi câu trả lời viết bằng tiếng Việt.

Không điều khiển được cửa sổ Spine đang mở. Mọi việc đi qua **file JSON** (do script dựng hoặc tool MCP sửa) và **Spine CLI**.

Để người dùng thấy ngay mỗi lần sửa: trang **Spine Live** `http://127.0.0.1:8780/spine?json=<work/...json>` (Home phải đang chạy). Trang dùng spine-player chính thức nên vẽ đủ IK, mesh, deform, draw order, và tự nạp lại khi JSON / atlas / ảnh đổi, giữ nguyên anim và thời điểm đang xem. Đầu việc, gửi người dùng link này; sửa xong chỉ cần báo đã ghi file, không cần nhắc họ mở lại Spine.

**Làm việc trước mắt người dùng (người dùng 2026-10-28: "tôi không thấy được quá trình bạn làm việc trên Spine Live"):** mỗi bước đáng xem thì đẩy lên trang bằng `tools/spine_live_cmd.py`, trang ở chế độ **Theo Claude** tự nhảy theo:
```bash
.venv/Scripts/python.exe -I tools/spine_live_cmd.py show work/<game>/spine/<anim>/<x>.json --anim tap --frame 8 --bones --weight wrist --say "đang làm gì, cần nhìn chỗ nào"
.venv/Scripts/python.exe -I tools/spine_live_cmd.py say "kết quả đo / bước tiếp"
.venv/Scripts/python.exe -I tools/spine_live_cmd.py status   # trang có mở và đang Theo Claude không
```
- Người dùng muốn **xem quá trình dựng** (2026-10-28), không chỉ kết quả: sau khi dựng/sửa rig hoặc anim, chạy `tools/spine_live_replay.py <json> --anim <a> [--delay 3] [--ui <tên>] [--only rig|anim]`: trang dựng lại từng bước (ảnh → từng xương → lưới mesh → weight từng xương → từng key blocking stepped → spline), mỗi bước có chú thích. Kiểm `spine_live_cmd.py status` trước: không có trang nào mở thì báo người dùng mở trang rồi mới chạy.
- Bản thử tạm (bẻ thử khớp, so phương án) ghi vào `work/<game>/spine/<anim>/_live/`, không để trong scratchpad: trang chỉ thấy file trong thư mục anim.
- Dùng `show` khi đổi file / anim / frame / lớp xem (xương, lưới, weight); `say` cho kết quả đo và bước tiếp. Câu `--say` nói cái cần nhìn, ví dụ "đầu ngón phải nằm đúng dấu + đỏ".
- Contact sheet (`render_spine.py`) vẫn dùng để tự kiểm; Spine Live là nơi người dùng theo dõi.
- Ghép lên UI game trên Spine Live: `work/<game>/spine/<anim>/ui/<tên>.json` = `{"name", "image" (PNG cạnh file), "at": [x, y] px ảnh (y xuống) = gốc skeleton / điểm chạm, "scale": px ảnh mỗi đơn vị Spine}`; trang có ô "UI: <tên>", lệnh `show … --ui <tên>`. HandTut: `ui/equipment.json` (at 110,660, scale 0.55 như GIF đã duyệt).

## Công cụ

| Việc | Công cụ |
|---|---|
| CLI: thông tin, export, import, pack/unpack atlas, clean up | MCP `spine`: `spine_project_info`, `spine_export`, `spine_import`, `spine_pack_atlas`, `spine_unpack_atlas`, `spine_clean_animations` (code `tools/spine_mcp/`) |
| Đọc JSON | `skeleton_summary`, `skeleton_bone_tree`, `skeleton_get`, `slot_list`, `animation_get` |
| Sửa nhỏ JSON | `bone_add`, `bone_update`, `slot_update`, `animation_create/rename/delete/scale_time`, `keyframe_set_bone`, `keyframe_set_slot`, `keyframe_remove`, `skeleton_set` (mỗi lần sửa có backup trong `.spine_mcp_backups/`) |
| Dựng rig + anim có tính toán (mesh, weight, FK, đặt điểm chạm) | Script `work/<game>/spine/<anim>/build_<anim>.py` sinh JSON (mẫu: `work/pirate_goldrush/spine/HandTut/build_handtut.py`) |
| Xem trực tiếp (người dùng) | Spine Live: Home `/spine` (`tools/spine_live/`, `tools/home/spine_live.py`); skeleton chỉ có `images/` thì server tự sinh atlas `images/_auto.atlas`; lớp xem rig (xương, lưới, weight, dấu + gốc) |
| Cho người dùng thấy bước đang làm | `tools/spine_live_cmd.py show/say/status` → trang ở chế độ Theo Claude nhảy theo; bản thử để trong `_live/` |
| Xem trước | `tools/spine/render_spine.py skel.json images_dir anim out_prefix [--bg ui.png --at X Y --scale S] [--cross] [--frames 0,4,8]` → `<out>.gif` + `<out>_frames.png` |

`render_spine.py` là bản xem gần đúng. Nó chỉ hỗ trợ translate/rotate/scale của xương, alpha của slot, region và mesh (có hoặc không weight). Nó **không** vẽ IK, path, clipping, deform timeline hay draw order. Anim dùng những thứ đó phải mở trong Spine để kiểm, và phải nói rõ với người dùng như vậy.

MCP `spine` khai báo trong `.mcp.json` (cần session mới sau khi thêm). Nếu không có tool `mcp__spine__*` thì gọi thẳng CLI:
```bash
"C:/Program Files/Spine/Spine.com" -u 4.2.43 -i <in> -o <out> -e <settings.json>
```

## Thư mục mỗi anim

`work/<game>/spine/<Anim>/` (vd `work/pirate_goldrush/spine/HandTut/`):
- `images/`: ảnh gốc, mỗi attachment một PNG (tên = tên attachment).
- `build_<anim>.py`: dựng skeleton JSON.
- `<anim>.json` → `<Anim>.spine`: project mới import từ JSON.
- `export/`: bản giao cho game.
- `preview/`: GIF và contact sheet.
- `_v1`, `_v2_<ghi chú>`…: bản cũ, mỗi vòng duyệt một thư mục, không ghi đè.

Thêm game hoặc anim mới thì ghi một dòng vào `MAP.md`.

## Quy trình

1. **Nhận order (hỏi gộp một lần, chỉ phần chưa biết):**
   - game, tên asset, anim dùng ở đâu (màn tut, UI, nhân vật);
   - ảnh nguồn, kích thước hiển thị;
   - fps (mặc định 30), độ dài, loop hay chạy một lần, khoảng nghỉ cuối loop;
   - hướng hoặc biến thể (trái/phải, các góc);
   - ảnh chụp UI game để ghép xem thử;
   - định dạng giao (JSON + atlas theo setting của người dùng).

   Xem anim cũ của team cùng loại trước khi thiết kế: `E:\tvc_source\2D ANIM\Export\_InLibrarys` (anim tut).
2. **Thiết kế (chờ duyệt):** mô tả ngắn từng pha theo frame (chuẩn bị → hành động → giữ → trả về → nghỉ), xương nào chuyển động, điểm gốc đặt ở đâu. Không dựng khi người dùng chưa OK.
3. **Rig:** xem các luật ở mục "Rig" dưới đây. Dựng bằng script, in ra số đỉnh, số tam giác và các điểm đo được.
4. **Anim:** key trước (blocking), xem GIF và contact sheet, rồi mới chỉnh curve. Xem các luật ở mục "Anim".
5. **Xem trước:**
   - `render_spine.py --cross`: dấu + là gốc skeleton hoặc điểm chạm.
   - Ghép lên ảnh UI game (`--bg`, `--at`, `--scale`) để GD thấy đúng chỗ.
   - Tự xem contact sheet trước, rồi mới gửi GIF bằng `SendUserFile`.
6. **Góp ý của GD:** mỗi vòng một version. Ghi nguyên văn câu góp ý và đổi gì.
   - Hỏi nhiều phương án (hướng, góc) thì làm 2–4 bản cạnh nhau (contact sheet so sánh), đặt tên theo tham số (`_v2_-170`).
   - Chỉnh hướng hoặc góc thì sửa xương `dir`, không key lại anim.
7. **Import:** dùng `spine_import` từ JSON ra **file `.spine` mới** trong thư mục anim. Không import đè project gốc của người dùng.
8. **Export:** luôn theo setting người dùng đã lưu trong Spine, không dùng mặc định của CLI:
   - đọc lại `C:\Users\HLC_2021\Spine\settings\editor-2.json`, khóa `export.json`;
   - dựng file setting CLI (`"class": "export-json"`), mẫu ở `work/pirate_goldrush/spine/HandTut/export_settings.json`. Setting hiện tại: atlas `.atlas.txt`, `premultiplyAlpha` false, pot + square, `cleanUp` true, `nonessential` true, `packTarget` perskeleton.

   Ngày 2026-10-26, bản export theo mặc định của CLI (`.atlas`, PMA, tên theo project) bị báo lỗi trong game.
9. **Kiểm bản export:**
   - `spine_project_info` trên file JSON vừa export: đủ anim và độ dài đúng;
   - atlas đúng đuôi, PNG không PMA.

   Rồi xem GIF lần cuối từ chính file export.
10. **Sau khi duyệt:**
    - commit kèm câu duyệt của người dùng và gắn tag;
    - cập nhật dòng trong `MAP.md`;
    - bài học mới ghi vào mục "Bài học" cuối file này.

## Rig

- **Thứ tự xương:** cha luôn đứng trước con trong `bones`. `bone_add` tự xếp; nếu dựng bằng script thì tự giữ thứ tự này.
- **Ma trận local của Spine:** `T · R · S`, góc tính bằng độ, ngược chiều kim đồng hồ, trục y hướng lên. Ảnh có y hướng xuống, nên phải đổi trục khi lấy điểm từ ảnh. FK để tính điểm thế giới có sẵn trong `build_handtut.py` (`local_mat`, `world`, `inv_apply`).
- **Gốc skeleton:** đặt ở điểm game dùng để căn anim, ví dụ đầu ngón tay chạm nút. Game chỉ cần đặt skeleton vào tọa độ nút.
- **Xương `dir`:** đặt giữa `root` và phần chính, để xoay cả cụm quanh điểm gốc. Mọi hướng hoặc biến thể (vd `tap`, `tap_right`) dùng chung key, chỉ khác góc `dir`. Bản lật trái/phải lấy đối xứng theo **trục nhìn** (gốc → tâm khối ảnh), không lấy theo trục xương, để độ nghiêng hai bên trông bằng nhau.
- **Mesh có weight:** dùng lưới đều phủ ảnh. Mỗi đỉnh có `[số xương, (idx, x, y, w)…]`, trong đó x, y là tọa độ **trong không gian xương ở setup pose**.
  - Weight đổi dần bằng smoothstep theo dọc xương và theo khoảng cách ngang. Chặn các phần không được kéo theo (ví dụ đốt ngón bên cạnh).
  - Tổng weight = 1, bỏ weight < 0.01.
  - Các đỉnh `hull` đi trước, `edges` theo đường bao.
- **Chuỗi xương** (ngón tay, đuôi, tóc): 3 đốt, tỷ lệ khoảng 0.35 / 0.30 / 0.35. Cong theo chuỗi thì đốt sau xoay nhiều hơn đốt trước.
- **Slot:** thứ tự slot là thứ tự vẽ. Hiệu ứng (vòng chạm, sáng) để slot riêng, xương riêng dưới `root`, không nằm dưới `dir`.
- **Đặt tên:** tiếng Anh, chữ thường, rõ vai trò (`hand`, `finger1..3`, `ring`, `dir`). Không đổi tên hay xóa xương có anim, slot hay mesh tham chiếu tới. Nếu thật cần thì sửa đủ mọi chỗ bằng `skeleton_set`.

## Anim

- **Thời gian:** tính bằng giây trong JSON. Làm việc theo frame ở fps 30 (`f(fr) = fr/30`).
- **Curve Spine 4.2:**
  - mỗi kênh 4 số `[cx1, cy1, cx2, cy2]`, trong đó cx là thời gian và cy là giá trị;
  - translate/scale có 2 kênh nên 8 số;
  - `"stepped"` để giữ nguyên giá trị.

  Curve đặt ở key **đầu** của đoạn. Hàm `ease()` / `ease2()` có sẵn trong `build_handtut.py`.
- **Nhịp:** có chuẩn bị, hành động nhanh, giữ ngắn, trả về chậm hơn lúc vào.
  - Ví dụ tap 1 s: ấn F0–8 (vào nhanh, `end_slope` để chạm có lực), giữ F8–11, nhả F11–19, nghỉ tới F30.
  - Lúc ấn thì scale khoảng 0.88 và xoay vài độ.
  - Ngón cong theo chuỗi: đốt 1 4°, đốt 2 7°, đốt 3 9°.
- **Đúng điểm chạm:** giải ngược vị trí tay sao cho đầu ngón nằm đúng gốc ở frame chạm, không chỉnh bằng mắt.
- **Loop:**
  - key đầu = key cuối; hiệu ứng tắt hẳn trước điểm cuối;
  - `cleanUp` khi export **xóa key giữ ở cuối**, làm anim ngắn lại. Muốn có khoảng nghỉ cuối loop thì đặt **event** ở thời điểm cuối (vd `loop_end`). Không dùng key giữ.
- **Hiệu ứng chạm:**
  - vòng scale từ 0.3 lên 1.15, alpha từ 1 về 0, trong khoảng F8–22;
  - trước lúc chạm alpha bằng 0 và dùng `"stepped"`.
- Áp dụng 12 nguyên lý animation như skill `animation` (`knowledge/details/principles.md`). Khi GD góp ý, gọi tên nguyên lý bị vi phạm.

## Luật làm việc

- Không ghi đè file người dùng đã chỉnh trong Spine. Trước khi sửa thì export `.spine` hiện tại ra JSON và so sánh, rồi giữ phần người dùng đã chỉnh.
- Mỗi vòng sửa là một version mới. Bản cũ dời vào `_vN`.
- Gửi xem trước dạng GIF ghép trên ảnh UI game, kèm contact sheet các frame key. Không nói "khớp" hay "đẹp" khi chưa tự xem ảnh.
- Bước nào chạy lâu (export, pack atlas, render nhiều GIF) thì báo trước thời gian.

## Bài học

- 2026-10-26 HandTut (G-PirateGoldrush, tay chỉ màn tut), GD duyệt "Pass".
  - GD muốn tay phải, ngón cong nhẹ khi ấn, tay đến từ phía trên cho các nút ở thanh dưới.
  - Góp ý "bàn tay nghiêng về bên trái nhiều quá" → đổi góc `dir` (các bản thử -170/-182/-194/-206). Chốt mức 2 (-194).
  - "Thêm 1 anim bàn tay xoay sang phải" → `tap_right` = `dir` đối xứng theo trục nhìn (lệch -53.64°).
  - Export theo mặc định CLI bị lỗi → export theo setting của người dùng (mục Quy trình, bước 8).
- 2026-10-28 BallBounceRoll (bài test: bóng nảy 5 lần bằng nhau rồi lăn phải ra khỏi khung), người dùng duyệt "Pass".
  - Curve Spine 4.2 ghi **thời gian (giây) và giá trị tuyệt đối**, không phải tỉ lệ 0–1; key xoay dùng `value`, không phải `angle`. Bản `_v1` sai cả hai chỗ. Hàm `curve()` và `timeline()` chuyển từ curve chuẩn hoá có trong `work/test/spine/BallBounceRoll/build_bounceroll.py`.
  - Vật lăn: chỗ sáng/bóng tối để slot riêng trên xương không xoay, nếu không đèn sẽ xoay theo. Góc lăn = -quãng / bán kính, dùng chung curve với x để không trượt.
  - Bóng đổ và độ cao tỉ lệ tuyến tính với nhau thì dùng chung curve cho scale + alpha của bóng đổ.
  - Setting export trên máy này để atlas `scale: 1.8` (atlas phóng to). Báo người dùng mỗi lần export.
- 2026-10-28 Soldier (rig lính cầm súng từ PSD, bài trainee), người dùng duyệt "Rig OK". Script mẫu `work/test/spine/Soldier/build_soldier.py`.
  - PSD → rig: `psd-tools` (đã cài trong `.venv`) tách mỗi layer một PNG theo bbox; thứ tự layer trong PSD (dưới → trên) là thứ tự slot. Đo khớp bằng trọng tâm alpha ở dải đầu và cuối mỗi part, rồi vẽ xương đè lên ảnh PSD để tự kiểm trước khi gửi.
  - Kiểm tư thế gốc: render JSON ở scale 1, trừ với ảnh PSD ghép sẵn, lệch chỉ ở viền là đặt đúng.
  - Nhân vật cầm súng: cả hai bàn tay là con của xương `gun`, mỗi tay một IK 2 xương với target là bàn tay. Súng thành ctrl kéo cả hai tay. Nếu tư thế gốc khác PSD (vd tay buông → nắm báng súng) thì gắn ảnh theo tư thế PSD, giải IK cho xương ở tư thế mới.
  - Chân: target IK ở cổ chân, nằm dưới `root`; bàn chân là con của target.
  - Mesh vải (khăn, áo choàng): người dùng muốn **bám sát viền như Trace nhưng ít điểm**. Bản được duyệt: hull `approxPolyDP` eps 3.5–4.5 px trên alpha nới 2 px, cạnh hull ≤ 110–140 px, điểm trong khoảng 1 điểm mỗi đốt xương (khăn dài 4 đốt: 24 viền + 4 trong). Bản lưới đều phủ cả ảnh và bản 70 đỉnh đều bị trả lại.
  - Xương phụ kiện (lưỡi lê): đầu xương đặt ở chốt gắn thật trên ảnh (chốt vàng), xương con bắt đầu ở chuôi và chạy dọc lưỡi.
  - `render_spine.py` không tính IK: tay chân tách rời trong GIF là bình thường, nói rõ với người dùng và nhờ thử trong Spine.
- 2026-10-28 Spine Live: người dùng hỏi "có chạy trực tiếp trên bản đang mở không". Spine editor không có API điều khiển từ ngoài, nên làm trang Spine Live (spine-player 4.2) tự nạp lại khi file đổi. Pane trình duyệt của Claude bị ẩn thì player không vẽ (không có requestAnimationFrame), kiểm dữ liệu bằng `spine.SkeletonJson` trong JS thay vì chờ `success`. Test 2026-10-28 trên HandTut: nạp lại giữ anim/thời điểm/dừng; JSON hỏng thì spine-player không gọi `error()` mà treo, nên trang tự đọc thử JSON + atlas trước khi dựng player.
- 2026-10-28 HandTut v5 cổ tay (user: "rig thêm cổ tay thay vì chỉ có ngón"): đặt khớp ở ranh giới da/cổ áo đo bằng màu điểm ảnh (đường x+y≈205), weight chuyển `hand`→`wrist` trong ~12 px qua mép đó. Thử bẻ ±25° trước để kiểm mesh và tìm chiều: góc âm = ngón gật vào nút. 6° không thấy ở cỡ 164 px, cần ~10°. Đo đầu ngón trên Spine Live phải dùng skeleton riêng (player đang trộn anim cho số sai).
