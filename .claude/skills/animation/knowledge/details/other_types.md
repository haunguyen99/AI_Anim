# Các loại chưa làm (khung trống) + mẫu file loại anim
Khi làm loại mới: tạo `details/<loại>.md` theo mẫu dưới, thêm dòng vào `INDEX.md`, xoá mục tương ứng ở đây.

## template
Mẫu cho mỗi file loại anim:
1. **Đặc trưng & mục tiêu** - anim này cần truyền đạt gì, chuẩn game (loop hay không, độ dài, root motion).
2. **Công thức** - các bước dựng đã chứng minh hiệu quả, theo thứ tự.
3. **Tham số đã duyệt** - theo từng nhân vật/clip (để làm mốc cho lần sau).
4. **Feedback của người duyệt** - câu gốc (tiếng Việt) -> nguyên tắc rút ra.
5. **Lỗi đã gặp & cách sửa** - triệu chứng, nguyên nhân đo được, cách sửa.
6. **Checklist QA riêng** - số đo phải kiểm trước khi gửi review (checklist chung: `qa_anatomy.md#pre-send-checklist`).
7. **Công cụ** - script và hàm dùng cho loại này.
Khi clip được duyệt -> ghi tham số cuối vào mục 3 và cập nhật trạng thái trong `INDEX.md`.

## locomotion
Walk / Run (di chuyển chu kỳ) - chưa làm.
- 2026-10-22 Gaygor Walk (ref 57F, 30fps, in-place, chùy gác vai): thử mocap từ ref (user: "kết hợp mocap trước rồi AI clean"). MediaPipe bắt 0-51/57 frame (top 0). RTMPose-x Halpe26 (rtmlib, onnx CPU, bbox từ silhouette; `work/boss_gaygor/walk/mocap_rtm.py`): score TB 0,1-0,5, nhảy tới 500 px, thân trên/tay bị chùy làm nhiễu, side view sai nặng; chân/bàn chân front+back còn dùng được (score 0,4-0,57). Người-pose model không hợp khỉ đột cầm chùy - chỉ nên dùng làm nhịp bước, không làm nguồn 3D.
- Phân tích Walk: lịch bước chân đo từ dải sát sàn 0-4/4-12 cm + chiều cao điểm thấp nhất mỗi chân (front/back), đối chiếu đáy nhún đỉnh silhouette (trùng lúc gót chạm); front/back lệch 1-9 cm khi hai chân chồng nhau, nên gót/mũi tách bằng so sánh 2 góc. Gaygor Walk: 56F, 2 bước lệch nhau (trái 8,7 cm/14F, phải 4,7 cm/7F), nhún ~20 cm 2 lần/chu kỳ, đảo ngang 17 cm 1 lần.
- Dựng scene Walk (2026-10-22): `build_attack_v4.py` đổi hằng số (px/m, gốc lưới = đường lưới ĐẬM đo bằng độ sáng, sàn y=934,5); `Ref_left` hiển thị file `right.mov` nên overlay phải ghép đúng (ghép nhầm = nhân vật quay ngược). Blender -b ghi ảnh theo đường dẫn tuyệt đối.
- Loop, thường có root motion hoặc in-place; chân bám đất trong pha chống (trượt = 0); nhịp bước, nhún hông, đánh tay đối pha.

## hit
Hit / Hurt (trúng đòn) - chưa làm.
- Ngắn, không loop; phản ứng theo hướng đòn, đầu/ngực dẫn, hồi về tư thế chờ.

## death
Death (chết) - chưa làm.
- Không loop; mất trọng lượng có kiểm soát, va chạm sàn, settle; frame cuối giữ yên.

## skill
Skill / Cast / Special - chưa làm.
- Anticipation rõ, khoảnh khắc tung chiêu đọc được từ camera game, hiệu ứng ăn khớp timing.

## other
Jump / Fly / Transition / khác - chưa làm.
- Ghi theo từng loại cụ thể khi gặp. (Bài học Reload súng trước đây nằm ở file này → `shoot_reload.md#reload-minimal`.)
- Walk dựng từ action Idle_Front: `CTRL_hand_ik_L` trong action đó lưu theo parent cũ, scene Walk gắn nó vào `CTRL_weapon` nên cổ tay bay ra 25–32 m. Đặt loc=0, quat=(1,0,0,0) ở f1 thì tay về đúng vai. Mỗi lệnh MCP có namespace riêng: nạp lại `walk_pose.py` và pose + `key_pose` trong cùng một lệnh (2026-10-22).

### Anim thao tác máy / idle công nhân (G-LumberCity, phân tích 2026-11-02, director 2 vòng)
- **Đo prop từ FBX team trước khi viết:** sổ/bút của worker là con của `accessory1`/`accessory` → `root` (không phải cổ tay), team key bám tay → rig mới phải thêm đúng khớp + control constraint vào cổ tay, nướng khi xuất. Tay nào cầm gì đo bằng khoảng cách prop–cổ tay mọi frame.
- **Nhân vật chibi tay ngắn:** đo vai→điểm chạm (trán, miệng) so với dài tay bằng định lý cos trước khi viết pha; trán dưới vành mũ cần đầu cúi/nghiêng đón tay. Mũ không xương → không xuyên vành.
- **Camera trên cao:** chuyển động trong mặt phẳng đứng (quạt lên xuống, vòng quay tay quay) chỉ còn một vạch; chọn mặt phẳng ngang hoặc dồn phần đọc vào ngả thân, vai, hông, đầu. Góc đầu ≥ 30–40°, giữ ≥ 20 F.
- **Tay khoá vào bộ phận máy quay đều** → bàn tay đi đều, cảm giác sức đặt vào thân (thân dẫn trước tay ~2 F), không đổi tốc độ tay. Loop vòng quay: đỉnh ở F1/F31/F61, xuất 61 key phát 60.
- **Idle biến thể:** hai đầu chép đúng Idle gốc (đủ số key của chu kỳ) để khớp pha thở khi game random qua lại.
- Model máy chưa nằm trong prefab/scene thì tỉ lệ máy–nhân vật là "chờ dữ liệu", không đoán (worker prefab scale 0,4).
- **Dựng key trên Frolvy (2026-11-02, Idle Wipe):** nạp anim team lên rig bằng `work/g_lumbercity/rig/apply_team_anim.py` (khớp ≤ 0,001 cm), mỗi key dựng lại từ dáng gốc + delta (`build_keys.py`), tay FK giải 2 đoạn tới điểm đo trên mesh theo khung đầu (`pose_tools.py`). Bẫy Frolvy: set_frame bị kẹp trong playback range (nhập FBX khoảng thời gian `rig/range_fbx.py` để mở), key stepped hiện giá trị key trước ngay tại frame key (xoá key rồi dựng, stepped ở cuối; xem lệch 1 frame), sửa ở frame có key = ghi đè key (đừng thử dáng ở F1).
- **Đạo cụ theo bối cảnh, hỏi trước:** worker cầm sổ/bút ở anim máy thường, nhưng ở máy Ropeway thì KHÔNG (user 2026-11-02) → tay Relax, bỏ dò né bút. Ghi "cầm gì" vào bảng pha của mọi clip.
- **Ảnh tự kiểm sạch:** `rig/render_pose.py` (skin LBS từ dump Frolvy + texture, không control) theo cam game (ortho 40° nhìn +Z), front, top; va chạm thật: `rig/skin_clear.py`. Tay chibi lau trán: găng to che mắt ở view front → đặt cổ tay cao sát vành, lệch về thái dương.
- **Blocking breakdown trên Frolvy (Idle Wipe 2026-11-02, `lumber_idle_wipe/blocking.py`):** slerp local từng control giữa 2 key + lệch nhóm (đầu dẫn khi quay, khuỷu dẫn/bàn tay trễ khi giơ-hạ tay). Slerp vai đi đường ngắn nhất làm tay văng ngang (cổ tay x −40/−48 dù chỉ số đi vòng < 1,4) → đặt đích cổ tay có chủ ý (`ARM_PATH`). Đoạn tay trượt trên đầu: điểm giữa 2 đích phải đẩy ra theo bán kính từ khớp đầu (dây cung cắt vào trong đầu, xuyên 0,67 cm). Giữ dáng tay user đã chọn ở cả breakdown sát key (F91 xoè ngón lại thành "vẫy" — user đã chê ở k4).
- Kiểm xuyên đúng: mesh skin đủ trọng số + pháp tuyến FBX gốc + mặt gần nhất thật (`rig/skin_clear.py`); định hướng pháp tuyến "ra xa khớp đầu" sai ở mặt dưới vành mũ (báo lún 3 cm giả).
