# gdd_stage0 — Giai đoạn 0: GDD → phân tích → ảnh key pose làm ref

Người dùng yêu cầu ngày 2026-10-28 ("phát triển tính năng ở giai đoạn đầu, lúc đọc GDD và viết tài liệu phân tích"; vướng nhất:
"phân tích chưa sát"). Chạy trước quy trình C (`text_brief.md`). Ảnh key pose thay cho "không có ref".
Vị trí cố định (người dùng 2026-10-30): ảnh key pose (G4/G4b) luôn đi **sau** khi duyệt phân tích/thiết kế và **trước** pose 3D đầu tiên; trong nhánh C là bước C2b. Đầu vào gồm cả concept thật của nhân vật (ảnh concept trong GDD hoặc người dùng gửi), không chỉ render model. Nhánh A (có video) không cần; nhánh B tuỳ chọn.
**Pha = key pose (người dùng 2026-10-30):** bảng pha của mỗi anim trong bản phân tích có thêm cột **Key pose**: mặc định một pha một key ở frame đỉnh của pha (`k<n>_<tên>`); pha trùng pose pha khác ghi lại đúng key đó (vd Lắng = `k1_ready`); pha chỉ nhích nhỏ, không đổi dáng (vài cm / vài độ) ghi `—` (chuyển tiếp, AI dựng ở blocking). Duyệt phân tích xong, chép bảng vào `keys/keypose.json` "clips": {"<id anim>": {"frames", "fps", "phases": [{"f", "name", "desc", "key"|null}]}}. Studio panel Key Pose đọc bảng này: pha thiếu ảnh có nút Tạo ảnh (theo mô tả pha), đủ ảnh thì **▶ Chạy ảnh** phát ảnh các pha đúng frame của anim = bản demo blocking đầu tiên (không xuất video).
Workspace **Image Key** (Studio, trước Pose, 2026-10-30): ảnh phủ viewport theo timeline của anim, góp ý bằng ✎ vẽ khoanh trên ảnh → AI sửa ảnh (`keypose_gen.py --markup`, xem `/check_fb`).
**Nhiều góc (2026-10-30):** ảnh `<key>__<góc>_rN` (right/left/front/back/top/q34, không hậu tố = góc chính); góc dùng cho nhân vật ở keypose.json "views" {main, use} do người dùng chọn (⚙ Góc). Góc phụ dựng từ ảnh góc chính đã ★ (`keypose_gen.py`, yêu cầu có `view`), kèm render model ở góc đó làm khung (model_ref/char_<side_r|side_l|front|back|top|q34>.png; thiếu thì render bằng `tools/render_fbx_tex.py --views …`). Mọi góc là camera **trực giao** như cam Maya (người dùng 2026-10-30), kể cả 3/4; không dùng ảnh phối cảnh làm khung.
Duyệt trong Studio (2026-10-30): panel **Key Pose** của anim (workspace Pose) hiện đúng key của anim đó, cùng dữ liệu với Home `/keypose`. Khi tạo ảnh cho một anim, ghi `keys/keypose.json` "clips": {"<id anim>": ["k1_…", …]} (hoặc đặt tên key chứa tên anim, vd `k2_shoot_f05`) để panel gắn đúng; yêu cầu từ Studio có thêm trường `clip`.
Clip đầu tiên: SDR map3 nỏ (`work/shoot_die_repeat/sdr03/`).

## Các bước
| # | Bước | Ra gì |
|---|---|---|
| G1 | Đọc GDD (xlsx/Google Sheet: tải `.../export?format=xlsx`; `tools/gdd_read_xlsx.py` in mọi ô, `tools/gdd_xlsx_images.py` tách ảnh kèm ô neo). Lọc phần liên quan anim, gồm cả tab số liệu (nhịp bắn, hệ số tua) và tab "ref game gốc" (camera) | `work/<dự án>/gdd/anim_list.md` |
| G2 | Hỏi lại chỗ thiếu **và chỗ mâu thuẫn** trong GDD | mục câu hỏi trong `anim_list.md` (cấp dự án) và `analysis.md` mục E (cấp clip) |
| G3 | Phân tích từng clip theo mẫu `sdr06/analysis.md` | `analysis.md` |
| G4 | Ref = render model thật (mục "Trình tự G4") → prompt theo **mẫu prompt** dưới → `tools/codex_img.py` (lần lượt) → `tools/keypose_scale.py` + xem từng ảnh | `keys/k*.png` |
| G5 | Trang duyệt (artifact): key pose + thước frame + bảng pha + câu hỏi có phương án đề xuất | `review/index.html` |
| G4b | Duyệt ảnh với team: Home `/keypose?job=<dự án>/<job>` (★ / ✕ / ghi chú, nút Yêu cầu thêm ảnh). Yêu cầu tới (kind `keypose_req`): viết lại phần sửa thành tiếng Anh rõ ràng, chạy `tools/keypose_gen.py <id> --extra "..."` nền (~1,5 phút/ảnh, lần lượt), xem ảnh ra, ghi `--reply` ngắn | `keys/<key>_rN.png` |

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
- **Chỉnh nhỏ bằng số sau khi đã chọn key thì áp trên rig, không sinh lại ảnh** (SDR01 Idle, 2026-10-29): user chọn v3 + "thân
  xoay −30 %, đầu +50 %"; sinh lại 3 ảnh (`sdr01/keys/k1_idle_e1_*`) mất ~10 phút, Codex làm quá (mặt gần nhìn thẳng, thân không
  giảm), user giữ v3 gốc ("dùng bản này đi"). Key = ý đồ; % chỉnh là tham số P0 (`p0_build.py` CFG), đưa thẳng vào Studio để duyệt.
- **Thêm góc front / top cho một key đã chọn** (SDR01, 2026-10-29, user: "bạn phải sinh từ ảnh mẫu này ra chứ"): ảnh key là ảnh 1 và là
  nguồn pose DUY NHẤT ("chỉ xoay camera quanh tượng"), không gửi render P0 làm mẫu camera (P0 đã chỉnh khác key → Codex lấy dáng P0).
  Tự suy hình học từ key rồi tả trong prompt cái phải thấy ở góc mới (ngực quay về cam side 60° → front thấy ngực gần nghiêng, hướng trái;
  dao chĩa về sau → front thấy dao gần đầu mút). Ghi "TRUE ORTHOGRAPHIC". Mẫu: `sdr01/keys/prompts/k1_idle_v3_turn.py`.

## Anim mới từ Studio (Image Key "+ Anim mới", 2026-10-30)
Người dùng: "Khi người dùng muốn thêm một anim mới. Khi click vào tạo anim hãy gửi cho AI yêu cầu". Yêu cầu lưu ở `work/store/keypose/animreqs/<id>.json` {char (id Studio), charName, job, name, desc, loop, frames (null = AI đề xuất), fps, doc (link / ghi chú GDD), by}. Bộ canh `notes_watch.py` in mục `kind: anim_req` và đánh dấu picked. Trạng thái hiện ngay trong cột Anim của Image Key: cập nhật bằng `tools/notes_watch.py --anim-status <id> <picked|analysis|review|images|done|error> "lời nhắn"`.
1. `--anim-status <id> analysis`. Đăng ký anim: `/new_clip` (tools/clip_registry.py) cho nhân vật của registry khớp `char`; anim phải có trong `/api/poses?char=` thì mới hiện trong cột Anim (cần dòng POSES / phiên bản P0 như `studio_new_clip` trong server.py).
2. Bản phân tích theo G3 (mẫu `sdr06/analysis.md`; không ref = nhánh C: C1 intake chỉ hỏi chỗ thiếu, C2 thiết kế + bảng timing), đọc `doc` nếu có. Bảng pha có cột **Key pose** (một pha một key, pha trùng pose dùng lại key, pha nhích nhỏ = chuyển tiếp).
3. Chép bảng pha vào `keys/keypose.json` "clips"[<id anim>] {frames, fps, phases}. `--anim-status <id> review "Bản phân tích: <đường dẫn>, N pha / M key, chờ duyệt"` và báo người dùng; **không tạo ảnh trước khi duyệt** (cổng duyệt như mọi quy trình).
4. Duyệt xong: `--anim-status <id> images`, tạo ảnh từng key theo G4 (góc chính trước, góc phụ khi người dùng bật), xong `--anim-status <id> done "N ảnh"`. Ảnh tự hiện trong Image Key.
