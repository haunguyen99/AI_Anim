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
| G4b | Duyệt ảnh với team: Home `/keypose?job=<dự án>/<job>` (★ / ✕ / ghi chú, nút Yêu cầu thêm ảnh). Yêu cầu tới (kind `keypose_req`): viết lại phần sửa thành tiếng Anh rõ ràng, chạy `tools/keypose_gen.py <id> --extra "..."` nền (~1,5 phút/ảnh, lần lượt), xem ảnh ra, **gọi director mốc `key-pose` (mục "Đồng nhất chuỗi ảnh" phần 7)**, ghi `--reply` ngắn | `keys/<key>_rN.png` |

## Luật cho "phân tích sát"
- **Mỗi ý một nhãn nguồn:** [GDD] trích nguyên văn câu gốc, [rig] đo trên rig, [clip cũ], [suy luận], [?]. Người duyệt soát kỹ chỗ [suy luận].
- **Đối chiếu GDD với rig trước khi viết:** liệt kê xương (cha, mesh skin vào đâu). Ví dụ map3: nỏ là con của `Wrist_L`, khớp GDD "tay trái đỡ nỏ"; dây và mũi tên chung `slingshot_1`, nên ẩn mũi tên khi bắn là câu hỏi.
- **Đọc cả tab số liệu:** cột "Reload speed ×" = 4,0 ÷ nhịp bắn, tức code tua anim tới ×5,33. Đây là ràng buộc độ dài clip mà mô tả anim không nói.
- **Tìm mâu thuẫn trong chính GDD:** phần mô tả có "đặt tên mới lên rãnh" nhưng các bước Reload không có; Fire Rate lv6 chậm hơn lv5. Đưa thành câu hỏi kèm phương án đề xuất, không tự chọn.
- **Rig không có ngón trỏ** (găng) thì động tác "bóp cò" phải đổi thành siết găng. Ghi rõ là [suy luận].

## Concept gốc bắt buộc trong mọi lần tạo ảnh (người dùng 2026-10-31)
Người dùng: "khi tạo ảnh mới nhất định phải gửi theo concept gốc theo prompt để AI tham khảo, để đảm bảo không tạo ra đối tượng khác
với mong muốn". Áp cho **mọi** lần gọi Codex: key mới, sửa, góc phụ, sửa theo nét khoanh, Tạo ảnh trong Studio.
- **Ảnh concept gốc** (ảnh trong GDD hoặc người dùng gửi) luôn nằm trong danh sách `--ref`, và prompt luôn có đoạn
  `ORIGINAL CHARACTER CONCEPT` ghi đúng **số thứ tự ảnh** concept ("attached image 4"). Đoạn này nói: vẽ đúng nhân vật này, không bịa
  người khác, áo, phụ kiện, giáp hay đồ vật không có trong concept.
- **Concept và render model chia vai:** concept quyết định nhân vật **là ai** (mặt, tóc, tỉ lệ, các món trang phục, loại đạo cụ).
  Render model quyết định **hình khối và màu 3D** đúng game (luật "Ref tốt nhất là render model thật" vẫn giữ, vũ khí lấy theo model).
  Chỗ hai bên khác chi tiết thì theo model, nhưng **không thêm thứ mà cả hai đều không có**.
- Concept đặt **sau** các ref model, để giữ số "image 1/2/3" của prompt cũ. Ảnh gốc và ảnh khoanh vẫn là ảnh cuối.
- Nơi đặt: file `concept*.png|jpg|webp` trong thư mục job (hoặc `model_ref/`, `keys/`), hoặc `keys/keypose.json` "concept": [...].
  File webp được đổi sang png.
- `tools/keypose_gen.py` tự làm việc này (`keypose.concept_for` + `concept_text`). Job **không có concept thì dừng**, báo lỗi
  "Thiếu concept gốc" lên trang. Khi đó hỏi người dùng xin concept, không tạo ảnh chỉ từ render.
- Gọi tay `tools/codex_img.py` (G4 bước 4) thì tự thêm `--ref <concept>` và đoạn prompt trên (lấy chữ từ `keypose.concept_text`).
- Kiểm mỗi ảnh ra: so với concept xem có món nào lạ (mũ, khăn, giáp, túi, vũ khí phụ) hay khác người không. Có thì ảnh hỏng, sinh lại.

## Trình tự G4 (đã chạy đạt trên SDR03, 2026-10-28)
1. **Ref model đúng màu** (`tools/render_fbx_tex.py`, texture bảng màu của game):
   `render_fbx_tex.py <rig.fbx> <tex> <job>/model_ref --skip <mesh vũ khí> --views q34,side_r --name char_` và
   `--only <mesh vũ khí> --views q34 --name prop_`.
2. **Ref cùng tỉ lệ**: nhân vật + vũ khí đặt cạnh nhau, góc side_r, cùng một lần render (`scale_side.png`; ví dụ dựng trong
   `sdr03` bằng `render_fbx_tex.load` + `render`). Đo mốc: `tools/keypose_scale.py scale_side.png`.
3. **Prompt** theo mẫu dưới, mỗi key một file `.txt` (ví dụ sinh bằng script: `sdr03/keys/make_prompts_model.py`).
4. **Tạo ảnh lần lượt** (không song song):
   `tools/codex_img.py prompts/kN.txt --out keys/kN_m1.png --ref model_ref/char_q34.png --ref model_ref/scale_side.png --ref model_ref/prop_q34.png --ref concept.png --timeout 600`
   (concept gốc bắt buộc, prompt ghi số thứ tự ảnh concept, xem mục "Concept gốc bắt buộc").
   Ảnh sau dùng ảnh đã đạt làm ref thứ 3/4 (cùng tỉ lệ, cùng tay, cùng tấn). Sinh theo chuỗi: key chủ + key liền trước (mục "Đồng nhất chuỗi ảnh").
5. **Kiểm**: `tools/keypose_scale.py keys/*.png --ref model_ref/scale_side.png` (tỉ lệ vũ khí), rồi xem từng ảnh theo checklist:
   đúng tay, đủ 2 tay, cơ chế prop đúng trạng thái, biên độ đúng số trong analysis, chân/tấn giữ nguyên. Ghi lệch vào chú thích trang.
6. **Kiểm cả chuỗi** như flipbook 2D (mục "Đồng nhất chuỗi ảnh", phần 5) rồi mới gửi.
7. **Director check**: subagent `animation-director` mốc `key-pose` chấm chuỗi so với GDD (phần 7 cùng mục), ≤ 2 vòng sửa, rồi mới gửi.

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

## Đồng nhất chuỗi ảnh = một anim 2D (người dùng 2026-10-31)
Người dùng: "việc tạo ảnh cho giai đoạn này là sự đồng nhất… giống diễn hoạt 2D vẽ các hình xong cho chạy liên tiếp để thành một anim".
Bộ ảnh key của một anim là **một chuỗi flipbook**, không phải các ảnh minh hoạ rời. Ảnh đẹp mà phát lên bị giật, nhảy hay đổi nhân vật thì
coi là **hỏng**. Đây là luật cứng cho mọi lần tạo ảnh (G4, G4b, Tạo ảnh trong panel Key Pose, sửa bằng `--markup`, góc phụ).

**1. Khoá "trường quay" (giống nhau ở mọi key của anim)**
- Cùng camera trực giao, cùng góc, cùng hướng nhân vật (vd quay phải). Cùng khổ ảnh và cùng cỡ nhân vật trong khung (chiều cao người
  lệch ≤ 3 %). Cùng nền xám, cùng ánh sáng và cách tô (flat-shaded).
- **Đường đất** (đáy bàn chân đứng) nằm cùng một hàng điểm ảnh. Gốc nhân vật (hông) cùng một cột điểm ảnh, trừ khi bảng pha thiết kế
  có di chuyển. Khi đó quãng dời phải đúng số cm trong analysis, quy ra điểm ảnh theo chiều cao model.
- Bàn chân đang **trụ** ở hai key liền nhau thì đứng yên đúng chỗ (lệch ≤ 1 % chiều cao). Chân trượt khi lật ảnh là lỗi, giống lỗi
  foot slide trong 3D.
- Một bộ ref model cố định cho cả anim (`model_ref/char_*`, `scale_side.png`, ảnh concept gốc, bắt buộc). Không đổi bộ ref giữa chừng.

**2. Khoá tạo hình (model sheet)**
- Cả chuỗi giữ y hệt tỉ lệ người, trang phục, màu, tóc, mặt, đạo cụ và cỡ đạo cụ. Đo cỡ đạo cụ bằng `keypose_scale.py` ở **mọi** key.
- Tay nào cầm gì giữ nguyên suốt chuỗi, trừ khi bảng pha ghi đổi tay. Trạng thái đạo cụ (dây, đạn, mũi tên…) phải nối logic:
  trạng thái ở key n là hệ quả của key n−1.

**3. Sinh theo chuỗi, không sinh rời**
- **Key chủ** (thường là k1, pose gốc/ready) phải được ★ duyệt trước. Ảnh này là "model sheet" của chuỗi.
- Các key sau sinh **theo thứ tự pha**. Mỗi key sinh với ref gồm render model + key chủ + **key liền trước** đã đạt. Prompt viết
  "Copy the previous key exactly: same camera, same framing, same size, same ground line, same planted foot position. The ONLY changes: …".
- Prompt chỉ liệt kê bộ phận **thay đổi** so với key trước, kèm biên độ bằng số. Mọi bộ phận khác ghi "identical to the previous key".
- Ảnh vừa có dáng đẹp vừa có độ liền mạch là hai mục tiêu khác nhau. Khi xung đột thì **độ liền mạch thắng**. Muốn đổi dáng lớn thì sửa
  key đó, rồi sinh lại các key sau nó theo chuỗi.
- Key "dùng lại" (pha trùng pose) phải là **cùng một file ảnh**, không sinh ảnh mới gần giống.
- **Tự động trong `tools/keypose_gen.py`** (người dùng 2026-10-31: "dựa vào ảnh đã tạo trước đó để viết prompt và tham khảo cho ảnh tiếp theo"):
  - Yêu cầu key mới (`base` rỗng, có `clip`) tự tìm key liền trước theo bảng pha (ảnh ★, không có thì ảnh mới nhất không ✕).
  - Prompt = prompt của ảnh key trước, bỏ khối `Pose:` và các ghi chú ref cũ, thêm khối `NEXT KEY` chỉ ghi phần thay đổi.
  - Ref = model + concept + key chủ + **key trước ở cuối**. Không gửi render camref vì khung lấy theo key trước.
  - Khi sửa một key, key trước cũng được gửi kèm làm mốc khung.
  - Soát trước khi chạy bằng `--dry`. Code ở `tools/keypose_chain.py`.
- Phần thay đổi (`--extra`) viết tiếng Anh, có số đo, chỉ ghi bộ phận đổi. Sinh **theo thứ tự pha**, mỗi lần một key: key sau chỉ chạy
  khi key trước đã đạt chuỗi.

**4. Chuyển động đọc được khi lật ảnh**
- Các bộ phận chính (hông, đầu, tay cầm vũ khí, mũi vũ khí) đi theo **đường cong (arc)** và hướng đúng thiết kế. Không đảo chiều hay nhảy
  vị trí mà bảng pha không có.
- Bộ phận không có trong danh sách thay đổi thì phải **đứng yên** (không "sôi" nét, không nhích, không đổi nếp áo). Đây là lỗi hay gặp
  nhất khi Codex sinh từng ảnh.
- Biên độ giữa hai key liền nhau phải khớp với số frame giữa chúng. Khoảng ngắn mà đổi dáng lớn thì báo lại thiết kế, không tự vẽ quá.

**5. Kiểm cả chuỗi trước khi gửi** (bước bắt buộc, sau checklist từng ảnh ở "Trình tự G4" mục 5)
- Phát chuỗi đúng timing (Studio panel Key Pose **▶ Chạy ảnh**, hoặc tự dựng flipbook nội bộ) rồi xem như xem một anim 2D: có giật,
  nhảy khung, đổi cỡ, đổi màu, trượt chân hay bộ phận đứng yên mà rung không.
- So từng cặp key liền nhau, chồng mờ để soi. Ảnh chồng chỉ dùng để tự kiểm, không gửi người dùng (luật REF|ANIM để riêng). Đo bằng
  số: đường đất, cột hông, chiều cao người, vị trí chân trụ. Không ước bằng mắt.
  **Đo ngay sau mỗi ảnh, không đợi đủ chuỗi** (người dùng 2026-10-31: chạy khi tạo hết ảnh thì tốn tài nguyên). Đo chỉ mất vài ms,
  thứ tốn là sinh lại cả đoạn sau một key lệch. `keypose_gen.py` gọi `keypose_chain.check_one` ngay khi Codex trả ảnh:
  - đo đường đất, chiều cao người, 2 bàn chân ở đường đất (ghép chân sau / chân trước theo thứ tự), bề rộng vùng chân, màu;
  - **căn khung như ghim giấy 2D**: đổi về khổ của key chủ, khớp đường đất, khớp chân với key trước. Ảnh gốc giữ ở `keys/_raw/`;
  - ghi `keys/chain.json`. Ảnh lệch được ghi "Lệch chuỗi: …" vào lời nhắn trên trang. Nhiều bản thì bản đạt lên trước. Key trước đang
    lệch thì key sau **không được tạo** (lỗi trên trang, `--force` bỏ qua).
  Ngưỡng: đường đất ≤ 1 %, chân trụ ≤ 1 %, cỡ người ≤ 3 % (chú ý), > 8 % (lỗi), bề rộng 2 chân ≤ 2 % (chú ý), > 10 % (lỗi, trừ pha có bước),
  màu ≤ 6 %. Kiểm lại cả chuỗi chỉ đọc số đã có: `tools/keypose_chain.py check <job> <anim>`.
  Chưa đo: phần đứng yên bị "sôi" (cần biết bộ phận nào được phép đổi). Phần này soát bằng mắt trên ảnh chồng mờ.
  Thử đầu trên SDR03 Hit (ảnh sinh rời trước luật): kh1 khép chân (bề rộng −33 %), kh2 dời ngang 17 %; căn khung đưa đất/chân về 0.
  **Chạy thật theo chuỗi** (SDR03 Hit kh1_r3 → kh2_r2 → kh3_r3, 2026-10-31, ~80 s/ảnh): cả 3 đạt ngay lần đầu, giữ cùng nhân vật, cùng nỏ,
  cùng tấn, chân trụ lệch ≤ 0,2 %, cỡ ≤ 2,7 %. Ảnh sinh rời trước đó không ảnh nào đạt. Hai bài học:
  - **Nền trôi màu cộng dồn** khi mỗi key chép key trước (xám (85,89,96) → xanh (75,86,103) sau 2 key). Sau khi căn khung, `fix_bg` tô
    lại nền về màu nền key chủ (dời đều màu nền + viền, nhân vật giữ nguyên).
  - **Câu "keep changes small, do not exaggerate" làm Codex vẽ thiếu** (kh2 ngả thân ~5–8° thay vì 18°). Khối NEXT KEY nay ghi "đúng số,
    không nhỏ hơn, không lớn hơn". Biên độ đúng hay chưa vẫn phải xem bằng mắt, vì tool không đo góc.
    Tạo lại kh2 (r3, 170 s) đạt: ngoài số độ, tả **cái thấy được trên silhouette** ("the WHOLE CHEST leans clearly BACK ~18°, shoulders end
    up well behind the hips, clear backward arc from feet to head"). Cỡ người lệch 6,2 % là đúng (thân ngả nên đầu thấp xuống), chỉ là chú ý.
- Ghi vào chú thích trang hoặc lời nhắn: "chuỗi N key, lệch tối đa đường đất x %, chiều cao y %, chân trụ z %".

**6. Sửa mà vẫn giữ chuỗi**
- Chỉ tạo lại key bị lệch. Ref gồm **key trước và key sau** nó (và key chủ), để nó khớp hai bên. Lưu bản mới `_rN`, giữ bản cũ.
- Lệch chỉ do khung (dời, phóng) mà dáng đúng thì **căn lại ảnh** (dời/phóng theo đường đất + chiều cao), không sinh lại.
- Sửa key chủ thì xem lại cả chuỗi. Key nào không còn khớp thì sinh lại theo thứ tự.
- Góc phụ: mỗi góc là một chuỗi riêng và cũng phải theo luật 1–5. Mỗi key ở góc phụ dựng từ key cùng tên ở góc chính đã ★, dùng key
  liền trước **cùng góc** làm ref khung.

**7. Director check (bước bắt buộc, người dùng 2026-10-31: "thêm bước agent check vào trong Image key")**
Sau khi cả chuỗi (hoặc phần vừa sinh lại) qua đo ngay sau mỗi ảnh + soát bằng mắt, và **trước khi báo "xong" / gửi người dùng**, gọi subagent
`animation-director` mốc `key-pose`. Áp cho mọi đường vào: G4, G4b (`keypose_req`), Tạo ảnh trong panel Key Pose, sửa bằng `--markup`, góc phụ,
Anim mới từ Studio. Không gọi cho một key lẻ chỉ dời khung / căn lại.
- **Đưa gì:** id clip + mốc `key-pose`; yêu cầu gốc của GD (ô GDD hoặc `anim_list.md`); thiết kế đã duyệt (`analysis.md` bảng pha); `keys/keypose.json`
  (phases); đường dẫn ảnh đang dùng của từng pha + ảnh ghép cả chuỗi để xem nhanh; **số đo** `keypose_chain.py measure` (feet / hipx / H) của
  các ảnh; các quyết định mới của người dùng sau bảng thiết kế (git log, mục blocking trong analysis). **KHÔNG đưa kết luận của mình** (director chấm
  độc lập, đưa hypothesis thì nó hay xác nhận lại). Chỉ yêu cầu xem + chấm, không sửa, không tạo ảnh.
- **Director chấm gì:** (a) từng bước của GD có thấy trong ảnh không (đúng tay: xác định tay bằng vị trí vai so với Idle, không bằng "trái/phải" trong
  ảnh; prop đúng trạng thái và **nằm trọn trong khung**); (b) đọc cả chuỗi như flipbook: nhịp, khoảng cách pose, điểm gãy, đổi vai trò hai tay;
  (c) chân khóa sàn nếu thiết kế không có bước; (d) silhouette ở camera game; (e) ảnh có theo quyết định mới nhất của người dùng chứ không chỉ theo bảng cũ.
- **Kết quả:** Duyệt → báo người dùng. Cần sửa → sinh lại **chỉ các key mức A/B** theo prompt director gợi ý (giữ bản cũ `_rN`), chạy lại bước 5 + gọi
  lại director, **tối đa 2 vòng**, rồi mới gửi người dùng kèm danh sách lỗi còn lại. Lỗi director hỏi ý người dùng (vd thiết kế cũ mâu thuẫn quyết định
  mới) thì **hỏi, không tự sửa**. Ghi lời nhắn trên trang: "director: Duyệt / còn lỗi …".
- Director không ghi `director_log.md` khi đầu bài chỉ cho xem: animator tự thêm 1 dòng (mốc `key-pose`, lỗi, đã sửa chưa).
- **Bài học lần đầu chạy (SDR01 Shoot, 2026-10-31):** chuỗi 5 ảnh Codex qua hết đo chuỗi nhưng director bắt được F7 **đổi tay** (tay ném co, tay ngắm duỗi)
  và dao bị cắt khỏi khung, cả hai mắt thường của animator cũng suýt bỏ qua. Đo chuỗi không thấy lỗi chân trước trượt ~12 cm (F5/F7/F11) vì `foot` chỉ
  so chân gần nhất; chân kia chỉ ra ở `stance` (6,5 % chỉ là "chú ý"). **Pha không có bước mà `stance` > 4 %, hoặc cạnh bàn chân trước lệch > 2 % chiều
  cao so với key chủ (đo `feet` của `keypose_chain.py measure`) thì coi là lỗi, không phải chú ý.** Prompt có hai tay phải tả bằng **vị trí vai trong
  ảnh gốc** ("tay cầm dao ở ảnh gốc, vai bên TRÁI màn hình") kèm câu "KHÔNG đảo tay", và ghi "dao nằm trọn trong khung, cách mép ≥ 80 px".
  ComfyUI (Qwen Image Edit) sinh từ ảnh Idle cho pose kém hơn Codex chuỗi: chân lệch, pose thiếu biên độ; chỉ dùng thử.

## Anim mới từ Studio (Image Key "+ Anim mới", 2026-10-30)
Người dùng: "Khi người dùng muốn thêm một anim mới. Khi click vào tạo anim hãy gửi cho AI yêu cầu". Yêu cầu lưu ở `work/store/keypose/animreqs/<id>.json` {char (id Studio), charName, job, name, desc, loop, frames (null = AI đề xuất), fps, doc (link / ghi chú GDD), by}. Bộ canh `notes_watch.py` in mục `kind: anim_req` và đánh dấu picked. Trạng thái hiện ngay trong cột Anim của Image Key: cập nhật bằng `tools/notes_watch.py --anim-status <id> <picked|analysis|review|images|done|error> "lời nhắn"`.
1. `--anim-status <id> analysis`. Đăng ký anim: `/new_clip` (tools/clip_registry.py) cho nhân vật của registry khớp `char`; anim phải có trong `/api/poses?char=` thì mới hiện trong cột Anim (cần dòng POSES / phiên bản P0 như `studio_new_clip` trong server.py).
2. Bản phân tích theo G3 (mẫu `sdr06/analysis.md`; không ref = nhánh C: C1 intake chỉ hỏi chỗ thiếu, C2 thiết kế + bảng timing), đọc `doc` nếu có. Bảng pha có cột **Key pose** (một pha một key, pha trùng pose dùng lại key, pha nhích nhỏ = chuyển tiếp).
3. Chép bảng pha vào `keys/keypose.json` "clips"[<id anim>] {frames, fps, phases}. `--anim-status <id> review "Bản phân tích: <đường dẫn>, N pha / M key, chờ duyệt"` và báo người dùng; **không tạo ảnh trước khi duyệt** (cổng duyệt như mọi quy trình).
4. Duyệt xong: `--anim-status <id> images`, tạo ảnh từng key theo G4 (góc chính trước, góc phụ khi người dùng bật), xong `--anim-status <id> done "N ảnh"`. Ảnh tự hiện trong Image Key.

## Windy Idle (Endless-kicker, 2026-11-04): ảnh key đẹp lệch thiết kế, góc trên
- **Người dùng có thể chọn ảnh lệch thiết kế đã duyệt** (k1_idle r1: tay giang ra bên thay vì khuỷu 90° ra trước; director chấm A, sinh r2 đúng thiết kế; người dùng: "tôi thấy phương án này oki rồi mà"). Ảnh key là chỗ người dùng chốt dáng: khi ảnh đẹp, đọc rõ mà lệch thiết kế thì đưa CẢ HAI bản cho người dùng chọn trước khi sinh lại; người dùng chọn thì sửa `analysis.md` theo ảnh ngay (không dựng lẫn hai bản).
- **Concept có thể nằm trong GDD Google Doc**: tải `export?format=html`, tách ảnh base64 (`<img src="data:...">`). Dải gió / VFX trong concept: ghi rõ "do NOT draw them".
- **Góc TRÊN hay chép T-pose cho vạt áo/đuôi**: Codex vẽ đuôi vạt dài chĩa ra sau như render T-pose dùng làm khung. Prompt phải tả cái thấy từ trên của vải RỦ (chỉ mép ngắn sau vai, ngọc ở đuôi bị che) và tay buông (chỉ thấy đỉnh vai). Sửa 1 lần là đạt (top_r2).
- Góc phụ chỉ là ref: tay/độ dài prop/hướng xoay đầu prop mỗi góc Codex tự vẽ khác nhau (Windy right: trượng 1,32×, tay cao hơn 20 cm) → khi dựng P0 lấy theo số trên rig + góc chính, ghi danh sách "lấy theo số" vào analysis.
