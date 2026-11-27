---
name: mirror_arm_run_walk
description: "Copy tay trái sang tay phải cho clip chạy / đi (run, walk) với tay phải lệch nửa chu kỳ, để hai tay vung ngược nhau (tay này ra trước thì tay kia ra sau): lật theo trục riêng của khớp phải, copy cả Scapula + IKWrist + PoleArm, nội suy mượt, giữ biên độ và nhịp. Dùng khi người dùng gõ /mirror_arm_run_walk, hoặc nói \"copy tay trái sang phải lệch nửa chu kỳ\", \"hai tay vung ngược nhau\", \"tay phải đối pha với tay trái\", \"alternate arms\" cho run / walk."
---

# /mirror_arm_run_walk: đối xứng tay trái → phải, lệch nửa chu kỳ (run, walk)

Người dùng chốt 2026-11-26 (Hero Gun run). Đây là bản **đối pha** của skill `mirror_arm` (bản đó copy cùng nhịp, không lệch). Dùng skill này khi cần tay phải vung **ngược** tay trái.

## Điều kiện nguồn
- Tay trái là bản **đã hoàn chỉnh**; người dùng có thể vừa chỉnh một pose (vd F8): lấy bản hiện tại làm nguồn, không dựa vào số cũ. Không sửa tay trái, thân, hông, chân.
- Tay trái đang IK (anim thật ở `CTL_IKWrist_L` + `CTL_PoleArm_L`, `Scapula_L` vẫn FK). Tay trái FK: lệnh vẫn chạy (copy Scapula + Shoulder + Elbow + Wrist) nhưng chưa dùng thử với `shift`; kiểm kỹ và báo người dùng.

## Bước làm
1. **Cửa sổ Frolvy:** `wmctrl -l | grep -i frolvy`, lấy cổng `[MCP 98xx]` của file người dùng nói (nhiều cửa sổ thì đọc tiêu đề, không đoán 9877). Kiểm scene: `python3 -I tools/frolvy_call.py <cổng> work/runner_hybrid/anim/checks/scene.py`. Frolvy bận có thể trả chậm hàng phút: thêm `--timeout 280`, đừng chạy lệnh thứ hai chồng lên.
2. **Độ lệch:** chu kỳ N = frame cuối − frame đầu (F15 = F0 nên chạy 15 frame → N = 15). `shift = N / 2` (15 → 7,5; walk 30 → 15). N lẻ thì shift có .5: lệnh nội suy Catmull-Rom tuần hoàn giữa các frame (mượt, không giật chỗ nối).
3. **Kiểm khô (không ghi):**
   `echo "exec(open('<repo>/tools/frolvy_plugins/mirror_limb/mirror_limb.py', encoding='utf-8').read()); mirror_arm(api, 'L', dry=True, shift=7.5)" | python3 -I tools/frolvy_call.py <cổng> - --timeout 280`
   "REFUSED" thì dừng và báo lý do bằng lời.
4. **Sao lưu tay phải cũ** (để hoàn tác chính xác): đọc `CTL_IKWrist_R`, `CTL_PoleArm_R`, `CTL_Scapula_R`, `CTL_ArmSwitch_R.fkIk`, mọi frame, lưu `/tmp`. Việc này không có sẵn trong lệnh.
5. **Làm:** cùng lệnh bỏ `dry=True`. Lệnh tự: chuyển tay phải sang cùng chế độ tay trái (không snap), lật theo quy tắc kênh (tx ×-1, ty/tz giữ, rx giữ, ry/rz ×-1), dời mọi frame theo `shift`, áp cho `IKWrist` + `PoleArm` + `Scapula` cùng một độ lệch, in biên độ và frame đỉnh/đáy.
6. **Đo và báo bằng lời:**
   - biên độ vung hai tay (bàn tay so với vai: trước–sau, lên–xuống) phải gần bằng nhau (trước–sau lệch ≤ ~3%);
   - đỉnh và đáy cách nhau khoảng nửa chu kỳ (tay trái ra trước F1 thì tay phải ra trước ~F8);
   - tay duỗi tối đa (% tầm với, 29,4 + 23,4 cm với Hero) không kẹt thẳng (< 100%);
   - F15 nối F0 (không có vết nối);
   - lên–xuống tính từ vai của tay phải có thể lớn/nhỏ hơn trái: nhịp bob thân không dời theo. Độ cao bàn tay trong thế giới thì hai bên bằng nhau. Báo thẳng, đừng giấu.
7. **Không lưu file.** Người dùng bấm play xem rồi nói "lưu" → lưu thành **bản mới**. Nói xấu → hoàn tác bằng bản sao lưu ở bước 4 rồi đo lại (đừng đếm bước undo).

## Luật cốt lõi
- Tay phải = bản lật của tay trái **lệch nửa chu kỳ**; Scapula + Pole theo cùng độ lệch để vai, khuỷu, bàn tay phối hợp.
- Không chép số xoay thô; không lật theo mặt phẳng ngực; không đụng tay trái / thân / hông / chân. Chỉ vai + tay (ngón và `handPose` không đụng trừ khi người dùng nói).
- Nhịp chạy, biên độ, phong cách giữ như nguồn. Chỉ nội suy để mượt giữa các frame, không dựng lại anim.

## Việc đi kèm hay gặp (làm khi người dùng nói)
- **Làm mượt quanh một pose người dùng vừa chỉnh** (vd F8): giữ nguyên frame đó, lấy phần lệch của nó so với đường mượt (nội suy bậc ba từ 2 frame mỗi bên), chia cho 2 frame kề (50%) và 2 frame xa hơn (15%); chỉ sửa các control tay đang làm. Chạy lại bước 5 sau khi sửa tay trái để tay phải cập nhật.
- **Giảm biên độ vung N%:** nhân (1−N) độ lệch quanh trung bình của mọi kênh IKWrist + PoleArm, hai tay cùng hệ số; hoàn tác bằng chia ngược.
- **Tay phải lệch vài độ:** `spread_arm(api,'R',6.5)` (xem skill `mirror_arm`).

## Bẫy đã gặp
- Phép kiểm gương của khớp gốc vai lấy nhóm cha `CTL_Chest_M_follow` (khớp bám DEF ngực, lệch `CTL_Chest_M` ~1,5° khi cột sống uốn); lệnh đã sửa, nhưng nếu thấy "REFUSED" lệch nhỏ (~0,03) thì xem lại điểm này.
- `set_attr` trên kênh chưa có key không dính (lệnh tạo key mọi frame trước); `delete_key` cần frame nguyên; `set_frame` số lẻ làm treo.
- Đặt `fkIk` bằng `set_attr` khi auto-key bật có thể rải key lên switch → kiểm `CTL_ArmSwitch_*.fkIk` không có key rải (lệnh dọn sẵn, vẫn kiểm).
- Frolvy có thể khởi động lại / đổi file giữa hai lượt: kiểm scene trước khi sửa; người dùng có thể đã chỉnh tay trái sau lần đo trước.

Mã: `tools/frolvy_plugins/mirror_limb/mirror_limb.py` (`mirror_arm(api,'L',shift=…)`). Skill cùng họ: `mirror_arm` (cùng nhịp, không lệch). Memory: `feedback-mirror-arm-by-curves`.
