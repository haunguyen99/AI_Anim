---
name: mirror_arm
description: "Đối xứng tay trái ↔ tay phải trong Frolvy bằng cách copy theo đường cong, cùng frame, cùng quỹ đạo cổ tay trong thế giới (run, walk, idle). Tự đọc tay nguồn đang FK hay IK. Dùng khi người dùng gõ /mirror_arm, hoặc nói \"đối xứng tay\", \"copy tay trái sang tay phải\", \"copy tay phải sang tay trái\", \"mirror tay\", \"hai tay giống nhau\"."
---

# /mirror_arm: đối xứng tay trái ↔ phải trong Frolvy

Người dùng chốt 2026-11-26: khi cần đối xứng (run, walk, idle) thì **luôn làm theo cách này**. Không thêm độ lệch nhịp nếu người dùng không nói.

## Bước làm
1. **Tìm cửa sổ Frolvy:** `wmctrl -l | grep -i frolvy`, lấy cổng `[MCP 98xx]` của file người dùng nói (nhiều cửa sổ thì hỏi / đọc tiêu đề, không đoán 9877). Kiểm bằng `python3 -I tools/frolvy_call.py <cổng> work/runner_hybrid/anim/checks/scene.py`.
2. **Kiểm trước (không ghi):**
   `echo "exec(open('<repo>/tools/frolvy_plugins/mirror_limb/mirror_limb.py', encoding='utf-8').read()); mirror_arm(api, 'L', dry=True)" | python3 -I tools/frolvy_call.py <cổng> -`
   Trả "REFUSED" thì dừng và báo lý do bằng lời (rig trái/phải không phải gương, hoặc tay nguồn không có key).
3. **Làm:** cùng lệnh, bỏ `dry=True`. `'L'` = trái → phải, `'R'` = phải → trái. Một lần chạy là một lệnh; chạy xong lệnh tự in kiểm.
4. **Báo người dùng** bằng lời: tay nguồn là IK hay FK, đường cong lệch bao nhiêu (phải 0), cổ tay trong thế giới lệch bao nhiêu (phải 0), góc khuỷu hai tay lệch tối đa bao nhiêu độ. Khuỷu lệch > 15° thì nói thẳng: thân xoắn làm vai bất đối xứng, đề nghị hạ pole tay đích nếu xấu.
5. **Không lưu file.** Người dùng bấm play xem rồi nói "lưu" thì lưu thành **bản mới** (không đè bản cũ). Khi người dùng nói xấu thì hoàn tác: mỗi lần chạy tốn nhiều bước undo (thường 3–4), undo từng bước rồi **đo lại bằng số** (cổ tay tay đích về đúng giá trị cũ, phần thân đã sửa trước đó còn nguyên), không đếm bước.

## Luật cốt lõi
- Hai tay **cùng đường cong, cùng frame**; cổ tay đi cùng quỹ đạo trong thế giới. Quy tắc kênh: tx ×-1, ty / tz giữ, rx giữ, ry / rz ×-1.
- **Đọc switch FK/IK của tay nguồn trước** (`CTL_ArmSwitch_<L|R>.fkIk`). Đang IK thì anim thật nằm ở `CTL_IKWrist` + `CTL_PoleArm` (+ `Scapula` vẫn FK); các control FK chỉ là số cũ. Lệnh tự làm việc này và chuyển tay đích sang cùng chế độ (không snap).
- **Không lật theo mặt phẳng ngực:** thân xoắn khi chạy làm tay kia lệch 20 cm trong thế giới và đường cong không trùng.
- Chỉ đụng tay. Ngón, vũ khí, thân, chân giữ nguyên. Chân chưa có lệnh (cùng ý với `IKAnkle` / `PoleLeg`, làm khi người dùng cần).
- Muốn tay đích **lệch vài độ** (người dùng 2026-11-26: "tay phải lệch tầm 5–8 độ so với tay trái", chọn "mở ra ngoài"): chạy `mirror_arm` xong thì chạy MỘT lần `spread_arm(api,'R',6.5)` — xoay cả quỹ đạo tay + pole quanh vai quanh trục thế giới Z, cùng góc mọi frame, giữ nhịp / biên độ / tầm với. Làm lại thì chạy `mirror_arm` lại trước. Chỉ tay IK. Hướng khác (ra trước/sau, ép vào thân, lệch ngẫu nhiên) hỏi người dùng, lệnh chưa có.
- Muốn tay đích **lệch nhịp** (người dùng nói rõ; "nửa chu kỳ" = đối pha khi chạy): `mirror_arm(api,'L',shift=7.5)` (clip 15 frame → 7,5 frame). Mỗi frame tay đích lấy giá trị đã lật của tay nguồn tại thời điểm f − shift, nội suy Catmull-Rom tuần hoàn giữa các frame, áp cho IKWrist + PoleArm + Scapula cùng một độ lệch. Lệnh in biên độ và frame đỉnh/đáy hai tay để kiểm (không có kiểm "đường cong trùng" khi có shift). Lưu ý: độ cao tay so với vai hai bên khác nhau vì nhịp bob thân không dời theo.

## Bẫy Frolvy đã gặp
- `set_attr` trên kênh chưa có key không dính → lệnh đã tạo key mọi frame trước rồi mới ghi.
- `delete_key` cần frame kiểu số nguyên.
- `set_frame` với số lẻ (7.5) làm script treo; chỉ dùng frame nguyên.
- Frolvy có thể khởi động lại giữa hai lượt: luôn kiểm scene trước khi sửa, chưa lưu thì mất.

Chi tiết và lý do: memory `feedback-mirror-arm-by-curves`, mã `tools/frolvy_plugins/mirror_limb/mirror_limb.py`, dòng trong `MAP.md`.
