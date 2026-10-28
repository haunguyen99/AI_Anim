# gdd_stage0 — Giai đoạn 0: GDD → phân tích → ảnh key pose làm ref

Người dùng yêu cầu ngày 2026-10-28 ("phát triển tính năng ở giai đoạn đầu, lúc đọc GDD và viết tài liệu phân tích"; vướng nhất:
"phân tích chưa sát"). Chạy trước quy trình C (`text_brief.md`). Ảnh key pose thay cho "không có ref".
Clip đầu tiên: SDR map3 nỏ (`work/shoot_die_repeat/sdr03/`).

## Các bước
| # | Bước | Ra gì |
|---|---|---|
| G1 | Đọc GDD (xlsx/Google Sheet: tải `.../export?format=xlsx`; `tools/gdd_read_xlsx.py` in mọi ô, `tools/gdd_xlsx_images.py` tách ảnh kèm ô neo). Lọc phần liên quan anim, gồm cả tab số liệu (nhịp bắn, hệ số tua) và tab "ref game gốc" (camera) | `work/<dự án>/gdd/anim_list.md` |
| G2 | Hỏi lại chỗ thiếu **và chỗ mâu thuẫn** trong GDD | mục câu hỏi trong `anim_list.md` (cấp dự án) và `analysis.md` mục E (cấp clip) |
| G3 | Phân tích từng clip theo mẫu `sdr06/analysis.md` | `analysis.md` |
| G4 | Ref = render model thật (mục "Trình tự G4") → prompt theo **mẫu prompt** dưới → `tools/codex_img.py` (lần lượt) → `tools/keypose_scale.py` + xem từng ảnh | `keys/k*.png` |
| G5 | Trang duyệt (artifact): key pose + thước frame + bảng pha + câu hỏi có phương án đề xuất | `review/index.html` |

## Luật cho "phân tích sát"
- **Mỗi ý một nhãn nguồn:** [GDD] trích nguyên văn câu gốc, [rig] đo trên rig, [clip cũ], [suy luận], [?]. Người duyệt soát kỹ chỗ [suy luận].
- **Đối chiếu GDD với rig trước khi viết:** liệt kê xương (cha, mesh skin vào đâu). Ví dụ map3: nỏ là con của `Wrist_L`, khớp GDD "tay trái đỡ nỏ"; dây và mũi tên chung `slingshot_1`, nên ẩn mũi tên khi bắn là câu hỏi.
- **Đọc cả tab số liệu:** cột "Reload speed ×" = 4,0 ÷ nhịp bắn, tức code tua anim tới ×5,33. Đây là ràng buộc độ dài clip mà mô tả anim không nói.
- **Tìm mâu thuẫn trong chính GDD:** phần mô tả có "đặt tên mới lên rãnh" nhưng các bước Reload không có; Fire Rate lv6 chậm hơn lv5. Đưa thành câu hỏi kèm phương án đề xuất, không tự chọn.
- **Rig không có ngón trỏ** (găng) thì động tác "bóp cò" phải đổi thành siết găng. Ghi rõ là [suy luận].

## Trình tự G4 (đã chạy đạt trên SDR03, 2026-10-28)
1. **Ref model đúng màu** (`tools/render_fbx_tex.py`, texture bảng màu của game):
   `render_fbx_tex.py <rig.fbx> <tex> <job>/model_ref --skip <mesh vũ khí> --views q34,side_r --name char_` và
   `--only <mesh vũ khí> --views q34 --name prop_`.
2. **Ref cùng tỉ lệ**: nhân vật + vũ khí đặt cạnh nhau, góc side_r, cùng một lần render (`scale_side.png`; ví dụ dựng trong
   `sdr03` bằng `render_fbx_tex.load` + `render`). Đo mốc: `tools/keypose_scale.py scale_side.png`.
3. **Prompt** theo mẫu dưới, mỗi key một file `.txt` (ví dụ sinh bằng script: `sdr03/keys/make_prompts_model.py`).
4. **Tạo ảnh lần lượt** (không song song):
   `tools/codex_img.py prompts/kN.txt --out keys/kN_m1.png --ref model_ref/char_q34.png --ref model_ref/scale_side.png --ref model_ref/prop_q34.png --timeout 600`
   Ảnh sau dùng ảnh đã đạt làm ref thứ 3/4 (cùng tỉ lệ, cùng tay, cùng tấn).
5. **Kiểm**: `tools/keypose_scale.py keys/*.png --ref model_ref/scale_side.png` (tỉ lệ vũ khí), rồi xem từng ảnh theo checklist:
   đúng tay, đủ 2 tay, cơ chế prop đúng trạng thái, biên độ đúng số trong analysis, chân/tấn giữ nguyên. Ghi lệch vào chú thích trang.

### Mẫu prompt (giữ thứ tự khối; điền phần <…>)
```
Toy-like stylized game prop, friendly mobile game. Game animation key pose reference for a 3D side-scrolling shooter.
Reference images: image 1 is a render of the ACTUAL 3D game model (T-pose, 3/4 view). Image 2 is a side view of the same model
with its <weapon> placed beside it AT TRUE SCALE: use image 2 for the size of the <weapon> relative to the body. Image 3 <shows the
<weapon> shape and colors only (NOT to scale) | is the SAME character already holding the <weapon> at the CORRECT SIZE and with the
CORRECT HANDS>. Reproduce the model EXACTLY: <palette + từng chi tiết trang phục, tóc, mặt>. <Weapon>: <màu, vật liệu thật của model>.
SCALE (very important): <dài vũ khí so với chiều cao và cánh tay; khi cầm thì mũi vượt tay đỡ bao nhiêu>.
Render: same simple flat-shaded look as the references, plain mid-grey background, no scenery, no text.
Camera: orthographic pure SIDE view, the character faces SCREEN RIGHT. Full body, feet visible.
Legs: <tấn đứng>. Legs identical in every key.
Holding position: <tay nào cầm đâu ở tư thế gốc>.
<Weapon> states: <mỗi trạng thái tả bằng thứ NHÌN THẤY được, vd dây ở đâu, rãnh có tên không>.
Pose:
<KEY: tên pha. Nếu sửa từ ảnh gốc: "Copy image 3 almost exactly … The ONLY changes: …". Tay tả theo vị trí trong ảnh
("hand nearest the face / nearest the camera"), "Exactly two arms". Biên độ ghi bằng số nhỏ ("about 4 degrees, barely visible").>
```

## Ảnh key pose (G4)
- Prompt chung: camera game (side, quay phải), nền xám trơn, giữ đúng tạo hình theo ảnh ref, luật cầm (tay nào cầm đâu) lặp lại trong mọi prompt.
- **Không chạy Codex song song** (401, xem `tools/codex_img.py`). Mỗi ảnh 80–120 s.
- **Cơ chế đạo cụ hay bị vẽ sai** (nỏ map3, v1): dây vẫn căng sau khi bắn, tên còn trên rãnh, kéo dây kiểu cung vượt chốt.
  Câu chung "dây bật về trước" không đủ. Phải tả **trạng thái nhìn thấy được**: "string slack, straight line between the two
  limb tips at the very front; top of the stock completely bare". Kéo dây: "brought back to the small catch just in front of
  the trigger, V shape, stops there". k2 cần 3 lần, k5 cần 2 lần (2026-10-28).
- **Bộ lọc an toàn có thể chặn** prompt vũ khí nhiều chữ "effort / counter-force / pulled". Thêm "toy-like stylized game prop,
  friendly mobile game", dùng từ "catch" thay "latch / trigger mechanism", là qua.
- Xem từng ảnh, ghi lệch vào chú thích trang, chỉ tạo lại ảnh lệch, lưu bản mới `_v2/_v3` (giữ bản cũ).
- **Ref tốt nhất là render model thật, không phải concept** (người dùng 2026-10-28: "tạo ảnh dựa theo model cho sát").
  `tools/render_fbx_tex.py <rig.fbx> <texture bảng màu> out --views q34,side_r` (+ `--only` mesh vũ khí). Studio chưa đọc UV nên
  snap của Studio là màu giả. Nỏ trong model (gỗ sẫm, sắt đen, cò vàng) KHÁC nỏ ảnh GDD (viền vàng): luôn lấy vũ khí từ model.
  Dùng ảnh tư thế ngắm đã duyệt làm ref thì Codex giữ tư thế tốt hơn.
- **Tỉ lệ vũ khí / người** (người dùng 2026-10-28: "sai tỉ lệ giữ vũ khí và nhân vật"): gửi ảnh vũ khí phóng to riêng thì Codex
  vẽ vũ khí to ~1,5 lần. Cách sửa: render nhân vật + vũ khí CÙNG TỈ LỆ cạnh nhau (`sdr03/model_ref/scale_side.png`), ghi số đo
  vào prompt (dài / cao, so với cánh tay), ảnh vũ khí riêng ghi "NOT to scale"; ảnh đã đúng tỉ lệ làm ref cho ảnh sau.
  Đo mọi ảnh bằng `tools/keypose_scale.py` (phần gỗ / chiều cao; mốc trên render model, ngưỡng mặc định ±0,08), không ước bằng mắt.
- **Tay nào làm gì là điểm yếu nhất của Codex** (map3 k4, 4 lần): luôn để tay gần camera giữ báng, tay xa vươn đi. Dùng ảnh
  tư thế ngắm làm ref còn sinh ra **3 tay**. Ghi "EXACTLY TWO ARMS" + tả từng tay thì hết thừa tay nhưng vẫn đổi tay. Không cố
  quá 2–3 lần theo cách cũ. **Cách đã chạy (k4 m8):** lấy một ảnh ĐÃ ĐÚNG TAY làm ref (k5: tay phải ở chốt, tay trái đỡ) và
  chỉ yêu cầu "change ONLY ONE ARM: move the hand that is at the catch forward to the string"; tả tay theo vị trí trong ảnh
  ("hand nearest the face") thay vì trái/phải.
- **Codex làm quá biên độ** (k2: thân ngả ~12° khi thiết kế 3–4°, người dùng: "giật về sau hơi nhiều"). Viết "copy image 3 almost
  exactly, SAME upright torso angle; the ONLY changes: …" với ref là pose gốc (k1). Đọc ảnh so với số trong analysis trước khi gửi.
- Ảnh chỉ dùng để chốt ý đồ và dáng nhìn, **không đo góc** (`review_process.md`, bài học Attack: ước góc bằng mắt lệch 20–40°).
