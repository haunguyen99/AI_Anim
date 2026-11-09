# Kho case idle (Spine 2D)

Mỗi mục: một nhân vật đã duyệt. Đọc mục gần nhất trước khi làm; thêm mục mới sau mỗi lần duyệt (mẫu ở cuối).

## Quái xương BoneMaw — 2026-11-03 · `work/test/spine/BoneMawPSD/`
- **Rig**: 42 xương, quái đứng 2 chân (IK), thân `hip → spine1 → spine2 → head → jaw → tongue1-3`, tay FK 3 đốt, lưng `back1-7`, gai `spike1-6`, vảy `scale1-5`, mắt 1 ảnh (không mí).
- **Yêu cầu**: "nhịp của vảy và xương gai lưng thi thoảng giật mạnh random để tạo ra cảm giác quái dị quái vật".
- **Lượt 1**: thở nặng (hông nhún 4 px, thân / đầu sóng, hàm há thở, mắt sáng nhấp nháy), loop 120F; gai / vảy = sóng thở + **giật ngẫu nhiên** (bật 2F ease-out rồi rung tắt dần 5 Hz / 0,16 s, cộng tuần hoàn để loop khép; seed; một lần rùng mình lan dọc lưng). Xương giật **key mỗi frame** (engine chỉ 12 key / vòng).
- **Lượt 2**: "đầu giảm xoay lại, trục Y giảm trọng tâm, tăng giao động trục Y, lưỡi uốn mạnh tự nhiên hơn" → đầu 2,0 → 0,8° + **bù ngược 60% độ nghiêng thân** (góc nhìn thấy 7,6 → ~4°), hạ trọng tâm 14 px, nhún 4 → 10 px, lưỡi sóng gốc → ngọn.
- **Lượt 3**: "nhịp đầu và tay đang overlapped cùng nhau... nháy mắt, lưỡi uốn lên chậm rồi uốn nhanh 1 2 lần, nhịp overlapped cần khác nhau" → mỗi phần nhịp chính lệch pha xa + nhịp phụ khác tần số (2 / 3 lần / vòng), trễ quán tính khác nhau; nháy mắt = co dọc ảnh mắt (3F nhắm, giữ 1F, 4F mở) F44 + nháy đôi F92/99; lưỡi pose-to-pose (`K.spl`): uốn lên chậm F0-47, quẫy nhanh 2 lần, thả lỏng, đốt sau trễ 2F.
- **Lượt 4-7** (hàm khép, mở theo lưỡi, thân chồm tới lúc lè lưỡi): người dùng **bỏ hết**, bấm "Về bản #108" (= lượt 3) trên Spine Live, rồi chỉ yêu cầu dời cú quẫy lưỡi: "tới frame 60 mới uốn nhanh" → "lùi thêm tới frame 70"; "chỉ rời lưỡi quẫy, còn lại toàn bộ giữ nguyên như bản 108, không ghép thêm chồm gì cả".
- **Cách sửa trên bản người dùng chọn**: cất anim bản đó (`idle_v108/idle_base.json`) làm gốc; script riêng (`idle_lean.py`) chỉ thay đúng xương được yêu cầu (dời thời gian lưỡi bằng ánh xạ frame từng đoạn: giữ đoạn đầu, kéo dài đoạn chờ, dời nguyên cú quẫy, thu đoạn thả lỏng), so file với bản gốc để chắc chỉ xương đó khác.
- **Cấu hình chốt**: bản #108 (`idle_cfg.py` lượt 3) + `idle_lean.py` (tongue_shift 19, lean_on 0). Số khác preset: thân 1,5°, đầu 0,8° + bù ngược 60%, tay 3-4° + nhịp phụ, lưỡi đầu ngọn ±16°, giật gai 16° / vảy 11°.
- **Người dùng tự key**: có sửa curve / key ở bản lượt 6-7 nhưng đã bỏ khi quay về #108.
- **Thời gian**: 8 lượt + 3 lượt chỉnh lưỡi.
- **Lần sau**:
  - quái dị: giật ngẫu nhiên (bật nhanh + rung tắt) trên phụ kiện cứng (gai, vảy) được nhận; key mỗi frame cho xương giật;
  - người dùng quay về một phiên bản cũ rồi xin sửa "tại bản này" → hỏi lại bản gốc nếu mâu thuẫn, rồi chỉ đụng đúng phần được xin, không ghép thêm thay đổi của các lượt sau.

## Cừu đi học cầm chùm bóng bay — 2026-11-02 / 03 · `work/test/spine/MascotBackToSchool/`
- **Rig**: 34 xương, cừu treo dưới chùm bóng (gần Cừu cầm ô).
  - `root` giữa canvas → `balloon_ctrl` (ctrl tổng, giữa chùm bóng) → 6 xương bóng (gốc ở nút buộc) + `string` (dây chung từ ctrl tổng xuống chỗ nắm) → `arm_R1` (tay nắm) ─ `string_end` (đuôi dây, theo tay) / `arm_R2` → `spine1` → `spine2`.
  - Tai 2 đốt, balo `bag`, chân phải 2 đốt, chân trái 1 xương (mesh, mép sát thân 100% spine2, scale giả co chân).
- **Yêu cầu**: `/skillidle` không mô tả thêm; AI dùng preset "ctrl bay" của Cừu cầm ô, loop 90F.
- **Lượt 1** (2,4 phút gen): chùm bóng nhấp nhô 14 px + trôi 6 px + nghiêng 1,5°; cừu con lắc trễ 20F; overlap sóng + quán tính; chớp mắt F62.
- **Lượt 2** (3,9 phút) — góp ý:
  - "hướng lông mày, mắt, mũi miệng cần đúng hướng mặt để scale dọc mắt đúng tỉ lệ";
  - chân trái cần mesh bind `spine2` sát thân;
  - "biên độ lắc lư tổng thể khá nhiều, từ spine với chân giảm lại".

  Đã sửa:
  - **trục mặt nghiêng sai chiều.** AI đo theo mũi–cằm (lệch do mặt 3/4); phải lấy vuông góc đường hai mắt, đo bằng moment ảnh mắt nhắm / mày;
  - chân trái thành mesh;
  - `string` = bù hẳn độ nghiêng ctrl + nhịp con lắc. Thân ±4,7° → ±2,8° (góc thế giới cộng dồn dọc chuỗi treo, phải đo bằng `pose`).
- **Lượt 3** (2,7 phút) — góp ý: "nhịp dây bóng dưới chưa đúng physics / nhịp tổng (nhanh, loạn xạ), overlap tai, chân trái chưa đúng".
  - Gió của `Chain` có hoạ âm 2–5 nhịp/loop → bỏ gió.
  - Dây đuôi / tai / chân trái = physics thuần do xương cha kéo (tai 1,3 Hz / 0,45; dây 0,55 / 0,4; chân 1,5 / 0,55).
  - Chân trái thêm dáng nghỉ đá 2° qua `Chain.rest`; scaleX co tính từ chính góc physics.
- **Lượt 4** (1 phút): "mắt nháy giữa timeline, nháy 2 lần liên tục" → chớp đôi F41 + F50, lông mày hạ giữ qua cả hai (`double_blink` trong `idle_cfg.py`).
- **Lượt 5–6** (2 phút):
  - "mỗi quả bóng giao động khác để giống physics (nhẹ)" → mỗi quả một lò xo riêng (0,5–0,85 Hz) + dáng nghỉ trôi riêng;
  - "bóng xanh đảo lắc nhanh" → dáng nghỉ 2 nhịp/loop bị chê, chỉ dùng 1 nhịp/loop.
- **Cấu hình chốt**: `work/test/spine/MascotBackToSchool/idle_cfg.py`. Số khác preset:
  - thân / đầu 0,7 / 0,6 / 1,2° (preset 2 / 1,5 / 2,5);
  - tay nắm 0,5 / 0,6°;
  - chân 1,6 / 2°.
- **Người dùng tự key**: không. Chỉ vẽ nét lên ảnh để sửa rig (tai, tóc, chân trái, weight).
- **Thời gian**: 6 lượt, 11,9 phút gen.
- **Lần sau**:
  - nhân vật treo dưới vật bay: đặt biên độ thân theo **góc thế giới** (±2,5–3°), không theo góc local từng đốt;
  - phụ kiện physics để gió = 0, dáng nghỉ trôi chỉ 1 nhịp/loop.

## Cừu Sakura cưỡi cá koi — 2026-11-02 · `work/test/spine/CuuSakura/`
- **Rig**: 36 xương. Ctrl tổng `fish1` ở đầu cá; thân cá `fish2-3`, `fish_tail`; vây `fin_side` / `fin_bottom`. Cừu `spine1` (con fish1) → `spine2` → `head`; tay quạt 3 đốt; tai 2 đốt; khăn `cloth1-2`; chuông `bell1`, `bell2-3`; sừng 1 xương.
- **Yêu cầu**: "ctl tổng cá xoay nhẹ, thân đuôi vây uốn lượn nhẹ, cừu cũng ngả nghiêng overlapped theo, vảy nhẹ tay quạt, 2 chân cử động nhẹ, tai, khăn đầu, 2 chuông overlapped theo vật lý".
- **Lượt 1** (2,4 phút gen): sóng + quán tính, 96F. Không bị chê về chuyển động.
- **Lượt 2** — góp ý:
  - mũi con của miệng; miệng chỉ scale theo chiều mở;
  - nhắm mắt như Cừu cầm ô;
  - sừng xoay nhẹ;
  - khăn lắc lư physics thật hơn;
  - vây "chưa ổn".

  Đã sửa:
  - mũi `noScale` (`onlyTranslation` làm mũi không xoay theo đầu);
  - miệng gốc ở mép trên, chỉ scaleX;
  - chớp mắt 3 bước;
  - khăn + vây chuyển sang physics thật.
- **Lượt 3**: "miệng scale mạnh thêm chút (không quá biến dạng)" → +10% thành +18%.
- **Sau khi làm active** người dùng còn yêu cầu:
  - tóc mái chỉ scale, không xoay;
  - sừng "chỉ còn 1 chút" (2,5° + quán tính 0,7 → 0,8° + 0,25).
- **Cấu hình chốt**: `.claude/skills/skillidle/examples/cuusakura_idle_cfg.py` (khớp tuyệt đối `work/test/spine/CuuSakura/build_idle.py`).
- **Người dùng tự key**: không.

## Cừu cầm ô — 2026-10-31 · `work/test/spine/SheepUmbrella/`
- **Rig**: 38 xương.
  - `umbrella_ctrl` ở ngọn ô là ctrl → cán → `arm_R` → thân `body1-2` → `head`.
  - Tay giỏ `arm_L1-2` → `basket_ctrl` (`noRotationOrReflection`) → 3 xương rau.
  - Khăn cổ, tai 2 đốt, 4 ruy băng ô (mỗi cái 2 đốt), chân, đuôi.
- **Idle 90F** (`idle/build_idle.py`, hệ "kênh = tổng sóng (biên độ, nhịp, trễ frame)"):
  - ô nhấp nhô 14 px, trôi 6 px, nghiêng 1,5° theo vận tốc;
  - cừu trễ sau ô 20F;
  - chuỗi tay → thân → đầu / chân / đuôi trễ dần.
- **Góp ý theo thứ tự**:
  1. "cừu đang xoay cùng lúc với ô" → tay cầm ô bù góc ô, cừu theo góc thế giới trễ 20F.
  2. "tai phải theo nhịp bay / lắc, chậm như physics thật" → quán tính theo góc đầu + nhịp lên xuống.
  3. "ruy băng mềm hơn, xương cuối xoay rộng hơn".
  4. "chớp mắt mượt hơn" → bóp 60% → ảnh nhắm giữ 2F → mở.
  5. Miệng chậm lại 1 nhịp / vòng.
  6. "tất cả đang quá cứng" → `phys.py` (lò xo + giảm chấn + gió tuần hoàn) cho ruy băng / khăn / tai.
- **Bài học**:
  - xương mắt / miệng local 0 theo head;
  - chuỗi overlap cùng một nhịp;
  - giỏ `noRotationOrReflection` phải key góc thế giới;
  - key thời gian làm tròn xuống.

---
Mẫu mục mới:
```
## <Nhân vật> — <ngày> · <thư mục>
- Rig: ... (vai trò xương khác preset)
- Yêu cầu: "<nguyên văn>"
- Lượt N (phút gen): góp ý "<nguyên văn>" → đã sửa gì
- Cấu hình chốt: <đường dẫn idle_cfg.py>; số khác preset: ...
- Người dùng tự key: <xương, frame> hoặc không
```
