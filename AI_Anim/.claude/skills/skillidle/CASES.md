# Kho case idle (Spine 2D)

Mỗi mục: một nhân vật đã duyệt. Đọc mục gần nhất trước khi làm; thêm mục mới sau mỗi lần duyệt (mẫu ở cuối).

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

## Cừu Back to School (6 bóng bay, vật bay kéo nhân vật) — 2026-11-13 · `work/_inbox/tung-backtoschool/spine/`
- **Rig từ PSD** (32 layer tách sẵn, mỗi bóng gồm cả dây): `psd_extract.py` (tự đọc PSD, vì pip bị chặn) → layer PNG; `build_rig.py` dựng 45 xương + mesh weight từ alpha (lưới ô 16-20 px, weight nghịch đảo luỹ thừa 4 theo khoảng cách tới đoạn xương, tối đa 4 xương, hull dò theo biên ô) → ảnh dựng lại lệch 277 / 1,1 triệu pixel so PSD.
- **Xương**: ctrl ở tay nắm dây (cha root xoay 0) → mỗi bóng chuỗi 3 xương `<màu>1` (từ điểm dây hội tụ) → `<màu>2` (tới nút buộc) → `<màu>3` (tới đỉnh bóng); người treo `ctrl → arm_R1 → arm_R2 → body1 → body2 / head / arm_L / leg / bag`. Đầu trục dọc mặt = 110° (đo từ mi mắt nhắm 15° / 24°).
- **Idle 90F** (`idle_cfg.py`): ctrl ±1.5° + nhấp nhô 12 px, người treo trễ 18F (arm_R1 bù translate), chuỗi bóng = `Chain` physics mỗi bóng hz 0.68-0.95 + pha gió 0-5.5 rad, **amp 18** (200 và 30 làm bóng văng ±40-70°), chớp mắt F62. Hậu duyệt idle ngay lượt đầu.
- **Lần sau**: bóng + dây = chain physics amp ≤ 20 (px/s²); quần / thân dưới dính hông bằng `fade`.

## Char4 ông giáo sư 2 ống nghiệm (đứng, nửa người) — 2026-11-18 · `work/test/spine/Char4/`
- **Rig từ PSD** (`build_char4.py`, 27 xương): thân hip → spine → chest → neck → head; 2 tay 2 mảng (bắp tay / cẳng tay layer riêng) + ống nghiệm; mắt mở + con ngươi clipping theo vùng hở mắt + ảnh mí nhắm; 3 xương miệng; tóc 2 bên + râu 2 đốt trong mesh đầu.
- **Yêu cầu**: idle thở, mở mắt nhìn người chơi, chớp mắt, mỉm cười nhẹ, râu / tóc physics nhẹ, tay phải đung đưa.
- **Lượt** (8 vòng, nhiều vòng là sửa rig): v1 lắc lư (đầu ±3°, ống ±8°) bị chê "thở chứ không phải lắc lư"; v3 thở = chỉ dời -> "kết hợp translate + scale spine và ngực"; mask con ngươi phải ôm vùng hở mắt (không chỉ trắng sáng); tay phải "đứng yên đi theo người" -> nhịp riêng lệch pha; "nhẹ nhàng hơn, xa mặt hơn" -> lệch cố định ra ngoài + một nhịp theo thở; tóc "chưa thấy chuyển động" -> weight tóc yếu (sửa rig) rồi ±3°; lúc nhắm tắt ảnh mắt mở + con ngươi.
- **Cấu hình chốt**: `work/test/spine/Char4/idle_cfg.py` 90F; thở: spine dời 0,5 px + scale 0,5 % / 1 %, chest trễ 3F dời 1,5 px + scale 1 % / 1,2 % (cổ / vai noScale); góc thân < 0,5°; râu / tóc Chain 0,7 Hz / 0,45, gió râu 55, tóc 120; tay phải +3 / −5 / +2° + nhịp 0,3 / 0,5 / 0,7°; miệng mép +2,5 px + nhịp 1 px; chớp F60.
- **Người dùng tự key**: vị trí con ngươi (2 lần, nướng vào setup `PUPIL_USER`); weight cẳng tay phải, bắp + cẳng tay trái (Spine Live, `KEEP`).

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

## Unlock — ruy băng 3 nơ (UI mở khoá) — 2026-11-19 · `work/unlock/spine/Unlock/`
- **Rig**: 19 xương. ctrl; mỗi nơ `bowX` (hoa) + `bowX_t` (đuôi); dải 2 nửa × 4 xương `ribL0-3` / `ribR0-3` (cha ctrl, cắt dưới nơ giữa); kéo `sc_root` → `sc_A` / `sc_B`.
- **Yêu cầu**: "idle bập bùng cử động nhẹ nhàng".
- **Idle 90F** (`build_anims.py`, chờ duyệt): ctrl nhấp 3 px, hoa nơ xoay ±2,2° + phồng 1,2-1,5%, đuôi ±5° (+ sóng bậc 2 ±1,5°, lệch pha 0,15 giữa các nơ), dải chùng ±0,35-0,5°/đốt trễ 0,07 vòng/đốt, hai nửa đối xứng; nơ giữa cưỡi theo mép cắt (FK). Kéo ẩn lúc idle (alpha 0). Đo: loop khớp 0 px, gia tốc đỉnh 0,45 px/F².
