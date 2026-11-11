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
