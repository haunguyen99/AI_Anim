# Kho case active (Spine 2D)

Đọc mục gần nhất trước khi làm; thêm mục mới sau mỗi lần duyệt (mẫu ở cuối). Cột quan trọng nhất: **người dùng tự key gì**. Đó là phần công thức chưa đạt; lần sau đặt pose cho phần đó trước.

## Cừu đi học cầm chùm bóng bay — 2026-11-03 · `work/test/spine/MascotBackToSchool/`
- **Yêu cầu**: `/skillactive` không mô tả. AI đề xuất bảng nhịp, người dùng duyệt: chùm bóng vọt lên kéo cừu, cừu vui vẫy tay đá chân, hạ dần về idle, 90F.
- **v1** (5,2 phút gen):
  - lấy đà −8 px F8 → vọt 45 px F24 → hạ thấp hơn idle F62;
  - tay vẫy 2 nhịp, chân đá qua lại;
  - thân là chuỗi physics; biên độ 60%.

  Góp ý: "đang quá giật, cừu và bóng lấy nhịp từ cừu cầm ô, chỉ bay lên và lắc lư 1 lần chứ không giật giật như thế".
- **v2** (2,8 phút):
  - chép nhịp `SheepUmbrella/active/build_active.py`: chùm bóng lên 1 lần (không lấy đà), nghiêng rồi về dần;
  - cừu = một nhịp `damp` tắt dần, mọi đốt cùng nhịp đó trễ dần (`lagd`);
  - gia tốc tối đa 11,5 → 2 px/f².

  Góp ý: "frame 17 đã active, hơn 30 đã hồi về, quá nhanh; nhẹ nhàng lại; cừu bay mạnh hơn; ctrl tổng bóng xoay nhẹ; dây theo tay cừu".
- **v3** (2 phút):
  - đỉnh F24 → F36, cao 55 → 90 px, nghiêng 6 → 3°;
  - lắc chu kỳ 58 → 80F;
  - mốc hạ F64 / F80 (mốc `_t(50)` bị kẹp ở F75 làm tụt nhanh ở cuối);
  - rig: `string_end` thành con của tay nắm.
- **Người dùng tự key** (08:36–08:42, 22 lần ghi, ~6,5 phút): `arm_R1` F29, `arm_R2` F38 / F66 + sửa curve, smooth graph. Đây là **nhịp lắc của cả người**.

  Rồi góp ý: "sửa overlap tay trái, 2 chân theo nhịp sửa lắc mới nhất vừa key".
- **v4** (3,4 phút):
  - key tay → `active_user_keys.json`, ghi y nguyên;
  - tay trái / chân = quán tính theo góc thế giới thân (dây + key tay + spine), trễ 5–12F;
  - chỉnh tay cầm bezier cuối của key tay cho độ dốc khớp idle (trước đó khựng 1,84 px/f ở chỗ nối).

  Góp ý: "recover về idle chưa mượt, chưa có overlap 2 tai (chưa chuẩn physics)".
- **v5** (2,4 phút):
  - `BLEND` env (48, 72) / phys (0, 6, 44, 72) / stiff (0, 10, 66, 72): lớp hành động tắt dần F60–90 (trước bị ép F77–90);
  - `damp` tắt dần từ F56;
  - balo zeta 0,9 (không văng ngược);
  - tai = `Chain` physics 2,6 Hz / 0,75 / lim 30.
- **Người dùng tự key sau v5** (08:51–08:53, 20 lần ghi): `arm_L1` (xoá 2 key, sửa curve) / `arm_L2` → đã lưu vào `active_user_keys.json`. Xoá anim test rồi xuất.
- **Giao**: idle + active 90F, `/exportspine` (atlas `.atlas.txt` scale 1.18, không PMA, 1 PNG 2048).
- **Thời gian**: 5 lượt, 15,8 phút gen + 7,1 phút chờ duyệt bảng nhịp; người dùng ~8 phút tự key.
- **Cấu hình chốt**: `work/test/spine/MascotBackToSchool/active_cfg.py` + `active_user_keys.json` (`arm_R1`, `arm_R2`, `arm_L1`, `arm_L2`).
- **Lần sau**:
  - case gần nhất có sẵn nhịp đã duyệt (Cừu cầm ô) thì **chép nhịp đó ngay bản đầu**, không tự lập bảng nhịp mới (mất 2 lượt);
  - đỉnh hành động không sớm hơn ~F30 / 90F;
  - hỏi người dùng key 2–3 pose tay nắm / tay vẫy trước khi gen (lần thứ hai người dùng tự key nhịp tay / thân);
  - lớp hành động tắt dần ≥ 30F cuối;
  - key tay đưa vào `USER_KEYS` thì kiểm độ dốc ở F cuối so với idle F0.

## Quái xương BoneMaw — attack (cắn) — 2026-11-03 · `work/test/spine/BoneMawPSD/build_attack.py`
- **Loại**: nhân vật đứng 2 chân IK, đòn đánh tại chỗ (không cưỡi / bay) → **không dùng active_engine**; script pose-to-pose riêng:
  nền idle chạy tiếp + hoà idle(f) → idle(f − END) (F0 / cuối trùng idle F0 cả tốc độ), lớp hành động `K.spl` cộng lên, mốc viết theo bản 72F rồi co theo `END`.
- **Yêu cầu**: "tiến nhanh chân trước về phía trước, hạ người nhoài tới trước đồng thời há to miệng ra và cắn nhanh mạnh về phía trước... 2 tay giai đoạn chân đang nhấc cũng nhấc lên và lúc nhoài người cắn về phía trước thì 2 tay đưa về sau, cắn xong cần có dư âm rung lắc của đầu... recover về: nhấc người, nhấc chân rồi về dáng hạ mình giảm đà rồi về frame idle". Hỏi trước: chân bước nào (chân phải), có tự key pose không (không).
- **Lượt 1**: 72F, lấy đà → bước → nhoài + há → cắn F24 → đầu rung tắt dần → nhấc người / lùi chân → hạ mình → idle. Lỗi tự bắt: lấy đà dồn 5F làm đầu giật ở F0 (kéo ra 7F); đốt có trễ còn đuôi ở F cuối (ép lớp hành động về 0 trong 8F cuối).
- **Lượt 2**: người dùng **key pose F26** (8 xương: lunge gấp đôi, đầu ngóc +33°, cẳng tay +53°) + "giảm độ rung chấn, rung chấn nhẹ thôi", "vai ra sau, cẳng tay lên". Sửa: cất key vào `attack_user_keys.json`; lunge (hông / thân / chân bước) **phóng cả đường theo tỉ lệ key** (giữ lấy đà nhỏ), xương khác cộng "bướu" mượt để qua đúng key; rung đầu 7 → 2,5°. **Lỗi tự bắt**: hông nhoài 105 px làm chân sau duỗi không tới (hở cổ chân 31 px) → bàn chân sau trượt theo 44 px + kiễng gót.
- **Lượt 3**: "cắn nhanh hơn, há bé lại chút" → há −26 → −19,7°, sập 2F; phần bù key cho hàm chỉ rải sau lúc sập (rải từ F12 làm hàm khép sớm).
- **Lượt 4**: key thêm **F12** (ưỡn lên có overlap spine1 < spine2 < đầu) + "tổng thể nhanh hơn, ~55 frame, smooth lại" → `END` 55, mốc + key co theo (F12 → F9, F26 → F20); bướu bù mỗi key chỉ trải giữa 2 key kề (bằng 0 ở key khác). Key người dùng trên anim key-mỗi-frame là **gai nhọn 1 frame** → phải uốn mượt qua, không giữ nguyên key.
- **Lượt 5**: "chỉ nheo mắt lúc cắn, đang lỗi nháy" → nháy của idle lọt vào qua nền hoà idle lệch pha: kênh mắt / eye_lid không lấy nền idle. "thêm độ uốn lưỡi thực tế, overlap nhẹ của hàm, người khi recover" → lưỡi = kéo trễ theo góc hàm + đầu (ngọn trễ + cong nhiều, chặn tanh) + rung tắt sau cắn; spine2 / đầu / hàm trễ đốt trước chỉ trong pha thu người. **Lỗi tự bắt**: đổi độ dài làm hàm tắt gai / vảy viết theo `END` mới thay vì 72F.
- **Duyệt** sau 5 lượt. Xương người dùng tự key: hip, spine1, spine2, head, jaw, arm_f1, arm_f2, foot_b_ik (F26 = pose cắn), spine1, spine2, head (F12 = ưỡn lên). → Lần sau: hỏi / đặt **pose lấy đà (ưỡn lên có overlap) và pose cắn** trước, biên độ lunge lớn (hông ~100 px, thân −15°, đầu bù +30°).
- **Kiểm luôn**: chân IK hở cổ chân (đo đầu shin vs target), key người dùng lệch 0, nối idle 0 px, mắt không bị nháy từ nền idle.

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
