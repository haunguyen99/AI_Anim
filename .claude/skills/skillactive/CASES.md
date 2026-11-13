# Kho case active (Spine 2D)

Đọc mục gần nhất trước khi làm; thêm mục mới sau mỗi lần duyệt (mẫu ở cuối). Cột quan trọng nhất: **người dùng tự key gì**. Đó là phần công thức chưa đạt; lần sau đặt pose cho phần đó trước.

## Cừu Sakura cưỡi cá koi — 2026-11-02 · `work/test/spine/CuuSakura/`
- **Yêu cầu**: "làm Active (chuyển từ frame đầu cuối idle): Cá giãy nhảy lên như hình (ctrl tổng cá bay lên, cong người như giãy, cừu cũng hớn hở overlapped (như dáng cưỡi bò tót nhảy)" + ảnh ref.
- **v1** (6,3 phút gen): key mốc + sóng giãy nhiều nhịp + physics.
  - Ngay trong lượt: khăn / chuông lật 180° → cứng hơn lúc nhảy + chặn `tanh`.
  - Góp ý: "cho cá giãy quẫy đuôi mạnh 1 lần thôi, giảm độ giật quá của người, smooth lại mọi thứ".
- **v2**: một cú quẫy, ít đổi chiều, gia tốc giảm ~5 lần.
  - Góp ý: "translate bay lên và rotate của root cá, thân và đuôi vây cá chưa fit với nhau, đang bị cà giật … khi xuống sâu hơn idle … tóc chỉ scale, sừng giảm".
- **v3**:
  - góc ctrl suy từ đường bay;
  - đuôi = tín hiệu dọc thân;
  - rơi sâu 37 px;
  - physics ăn 40% chuyển động (tai quất như roi do cá xoay quanh đầu cá, đầu cừu ở xa ~600 px).

  Góp ý: "giảm rotate lúc giãy của spine 1 … chỉ để overlapped spine 2".
- **v4**: `spine1` bù 3/4 góc cá.
  - **Người dùng tự key** (14:36–14:41, ~20 thao tác): `fish3` thành sóng lớn −34 / +24 / −20°, `fish_tail` 4 nhịp; làm phẳng `spine1`.
  - Rồi góp ý: "dựa theo nhịp mới của cá, sửa nhịp rotate của cừu … chuẩn physics … khăn, tai".
- **v5**:
  - **Lần dựng đầu đè mất key tay** → lấy lại từ sao lưu, lưu `active_user_keys.json`;
  - cừu thành chuỗi physics (`spine1` tự giữ thăng bằng);
  - bỏ hệ số 40%, tai cứng hơn.

  **Người dùng tự key** `spine2` (F16), `head` (F36). Góp ý: "giữ nguyên các key của cá, sửa nhịp của cừu sao cho physics theo nhịp của cá".
- **v6**: `REST_FB` cho chỗ ngồi nghiêng theo nhịp quẫy `fish3`.
  - **Thay key tay `spine2` / `head` bằng physics** → người dùng key lại `head` (29 thao tác) và `arm_L1`.
- **Giao**:
  - key tay `fish3`, `fish_tail`, `spine2`, `head`, `arm_L1`;
  - physics của AI cho khăn, tai, chuông, vây, sừng;
  - mix 168F; xuất atlas scale 1.3.
- **Thời gian**: 6 lượt, 20,8 phút gen + 35,2 phút người dùng; ~95 thao tác sửa tay (~15 phút).
- **Cấu hình chốt**: `.claude/skills/skillactive/examples/cuusakura_active_cfg.py` + `work/test/spine/CuuSakura/active_user_keys.json` (khớp tuyệt đối `build_active.py`).
- **Lần sau**: hỏi người dùng key pose `thân vật cưỡi` / `đầu nhân vật` trước; không thay key tay bằng physics khi chưa hỏi.

## Cừu cầm ô — 2026-10-31 · `work/test/spine/SheepUmbrella/`
- **Yêu cầu v2**: "active cần có hành động mạnh hơn để gây chú ý khi chuyển idle-active-idle, key đầu cuối của active là từ idle. Ô bay nhanh dứt khoát nhẹ lên trên rồi từ từ hạ xuống, lúc bay nhanh lên cừu cũng bị overlapped xoay người tiến về phía trước, tay cầm giỏ trái cây cũng giơ lên" (bản loop 60F cũ bị bỏ).
- **v3** — góp ý "đang giật cục quá mạnh … bay lên nhanh chứ không phải giật cục", ô xoay về bên phải → smootherstep, ô lên 55 px chếch phải, nghiêng 6°.
- **v4** — góp ý "trục xoay của ô xoay luôn chứ không hold … bay xoay lên nhanh nhưng mượt" → mốc nối spline C2 liên tục (không dừng ở mốc), ô lên ~70 px, nghiêng 7° rồi quay về ngay.
- **v5**:
  - chuỗi tay → thân → đầu / chân / đuôi cùng một nhịp (đốt sau trễ vài frame);
  - giỏ (`noRotationOrReflection`) key = góc thế giới tay;
  - bớt key 861 → 417.
- **Physics**:
  - `phys.py` cho ruy băng / khăn / tai: active tiếp trạng thái idle F0, hoà về idle F64–90;
  - nhắm mắt F20–49 (người dùng chỉnh 27 → 20, mở lại F50).
- **Người dùng tự key**: không (sửa qua lời).

## Cừu Back to School (6 bóng bay) — 2026-11-13 · `work/_inbox/tung-backtoschool/spine/`
- **Yêu cầu** (Tùng): "Active: bay nhẹ lên lắc 1 lần như gió thổi" (idle: "lơ lửng nhẹ nhàng, các object overlapped nhẹ nhàng, nhịp có thể khác nhau nhẹ nhàng"; rig "lấy ctrl tổng từ bóng, dây, rồi kéo xương xuống người").
- v1 (bay 90 px, gió 7°, 2-3 nhịp lắc): "idle oki, active chưa ổn lắm" (mơ hồ) → tự soi: bay quá thấp (7% chiều cao) + bóng lắc 2-3 lần = rung.
- v2: bay 150 px có hạ lấy đà, một cú gió 9°, chuỗi bóng ít wind (0.3x lúc active) → "nhịp lắc cuối mạnh quá, thân dưới đứt rời thân trên".
- v3: bỏ nảy lại cuối, giảm lim; quần dính hông (`fade`), bỏ body2 khỏi chain → "ổn hơn, chuyển active -> idle hơi khựng".
- v4-v5: mục 4b (đường hạ giảm dần, BLEND rộng, giảm chấn chân tay, bỏ chain tay trái, `smooth_tail.py` σ 5.5) → "tách 2 anim, chỉ playblast active" → "Oki rồi".
- **Giao**: idle 90F loop + active 72F một lần, 45 xương, export JSON + atlas `.atlas.txt` + PNG 2 MB + `.spine`; zip 1.8 MB gửi Tùng.
- **Thời gian**: 5 vòng góp ý của Hậu (qua lễ tân), ~10-15 phút mỗi vòng; dựng rig + idle + active đầu ~60 phút. Người dùng tự key: không.
- **Cấu hình chốt**: `work/_inbox/tung-backtoschool/spine/{build_rig.py, idle_cfg.py, active_cfg.py, smooth_tail.py}`; khác preset: bóng = chuỗi 3 xương, active 150 px, gió một thùy.
- **Lần sau**: đo tốc độ cuối active trước khi gửi (mục 4b); đo chiều cao bay theo % nhân vật; lọc `animations` chỉ idle + active khi xuất.

---
Mẫu mục mới:
```
## <Nhân vật> — <ngày> · <thư mục>
- Yêu cầu: "<nguyên văn>" (+ ref)
- vN (phút gen): đã làm gì · góp ý "<nguyên văn>"
- Người dùng tự key: <xương, frame, số thao tác> (lý do suy ra)
- Giao: <anim, độ dài, xuất>
- Thời gian: N lượt, gen / người dùng
- Cấu hình chốt: <active_cfg.py + active_user_keys.json>
- Lần sau: <điều cần làm khác>
```
