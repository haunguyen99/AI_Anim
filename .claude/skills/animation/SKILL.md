---
name: animation
description: Làm anim 3D cho nhân vật game trên các trang Lab (Mesh/Rig/Pose/Review trong Home, không Blender, không Cascadeur). Claude làm như animator senior - phân tích ref hoặc yêu cầu, dựng P0 và blocking trên Pose Lab, spline + polish, kiểm giải phẫu, xuất FBX cho Unity. Dùng khi người dùng muốn anim cho model của họ từ video ref, từ file blocking FBX của team, hoặc chỉ từ mô tả bằng lời, hoặc muốn sửa/xuất anim đã có.
---

# Animation (Pose Lab, animator-first)

Người dùng nói tiếng Việt: trả lời bằng tiếng Việt. Ref là **ref diễn xuất**, không phải mocap. Công cụ: Home (`/project`) với các trang Mesh Lab, Rig Lab, Pose Lab, Review Lab (`docs/app_shell.md`, `docs/data_flow.md`). Thiết kế gốc: `docs/pipeline_v2.md` (phần Blender trong đó đã ngừng dùng).

## Knowledge base (đọc lõi mỗi task, chi tiết khi cần)
**Luôn đọc** `knowledge/CORE.md` (quy tắc một dòng cho mọi clip, mỗi dòng có con trỏ) và `knowledge/INDEX.md` (mục lục: mỗi mục một dòng kèm "đọc khi…", và trạng thái từng loại anim). **Chỉ mở `knowledge/details/<file>.md#<mục>` khi task chạm tới nó** (file chủ đề: `arms_hands`, `props_weapons`, `torso_head`, `legs_feet`, `timing_spline`, `review_process`, `qa_anatomy`, `export`, `principles` (12 nguyên tắc animation áp vào đây: mỗi note feedback gọi tên nguyên tắc bị vi phạm); file theo loại: `idle`, `attack`, `shoot_reload`, `other_types` (mẫu trống cho loại chưa làm), `user_blocking`, `text_brief`).
**Sau mỗi task** (mỗi vòng review sửa xong, mỗi clip duyệt/xuất), không cần hỏi: ghi bài học vào đúng mục `details/` (câu feedback → nguyên tắc, lỗi đo được → cách sửa, tham số đã duyệt, checklist QA; giữ ngày và lời người dùng; bài mới thay bài cũ tại chỗ, ghi ngày), thêm một dòng vào `INDEX.md` nếu có mục mới, và chỉ thêm quy tắc một dòng vào `CORE.md` **khi áp dụng cho mọi clip** (giữ `CORE.md` dưới ~6 KB). Một số file kiến thức còn nhắc Blender / Cascadeur như lịch sử của các clip cũ: bỏ qua phần công cụ đó, giữ phần bài học diễn xuất.

## Ba quy trình: chọn theo nguồn vào
Cả ba chạy trên Pose Lab. Đăng ký clip và nối các trang bằng `/new_clip`; Rig Lab bằng `/rig`; đọc note review bằng `/check_fb`.
- **A — từ video ref** (mặc định): phân tích ref → P0 → blocking → spline → polish (xem phần dưới và `docs/pipeline_v2.md` §2, bỏ phần Blender).
- **B — từ blocking của người dùng** (FBX đã có key của chính rig, vd `Bloking50.fbx`): nạp vào Pose Lab, khớp file → phân tích nhân vật + đòn từ blocking → sửa lỗi blocking → AI thêm pose chuyển tiếp → trọng lượng → spline + polish nướng từng frame → FBX từ chính file của team. Bước, cổng duyệt, lệnh, luật: `knowledge/details/user_blocking.md`; bộ script mẫu `work/gaygor_attack_50_blocking/` (duyệt 2026-10-23).
- **C — chỉ có yêu cầu bằng lời** (không ref, không blocking): intake gộp → bản thiết kế + bảng timing (duyệt) → pose kể chuyện 10% trên Pose Lab, người dùng chỉnh được (duyệt) → blocking 25–50% (duyệt) → đi tiếp nhánh B từ bước 3. `knowledge/details/text_brief.md`.

Mọi quy trình có **cổng duyệt**: không sang bước sau khi người dùng chưa duyệt bước trước.

## Chuỗi trang (trong Home)
Mesh Lab (sửa mesh) → Rig Lab (khớp, skin, Outliner; dùng luôn xương/skin khách nếu mesh đã rig) → nút ➤ gửi glTF có skin sang Pose Lab (base pose) → dựng pose, key, spline, vật lý, xuất FBX → nút 🎞 quay playblast nhiều camera sang Review Lab → note theo frame, `/check_fb`. Dữ liệu lưu ở `work/store/` (`docs/storage.md`).

## Ground rules (học được từ các clip đã làm)
1. **Mắt trước.** Mọi lỗi/feedback: đặt REF cạnh ANIM ở mọi view (cả top và view game), gọi tên lỗi bằng lời (bộ phận nào, hướng nào), rồi sửa thẳng vào pose. Bộ giải số chỉ cho bài toán nhỏ, rõ ràng. Một bộ tối ưu silhouette toàn thân từng ra tư thế hỏng (tay giãn) - không lặp lại.
2. **Camera trước mọi thứ.** Ref có lưới nền thì hiệu chỉnh theo lưới (px/ô = px/mét, gốc ở giao điểm lưới, sàn = đường lưới). **Mỗi clip hiệu chỉnh riêng** (playblast Attack khác camera Idle; Attack v3 dùng lại camera Idle nên mọi độ cao đều sai). **Camera game là top-down** (Gaygor): đánh giá độ đọc được từ trên xuống.
3. **Dựng P0 từ chân lên**, từng đoạn, mỗi đoạn người dùng duyệt: chân + hông (thế đứng!) → cột sống/đầu → tay tự do → prop → bàn tay trên prop. Không mặc định thế đứng chính diện.
4. **Trục khớp và giới hạn theo từng rig** (`work/<job>/joint_limits.json`); mọi pose kiểm theo giới hạn. Rig FBX này: trục dọc xương = local -X, khuỷu/gối gập quanh local Z, ngón cuộn quanh local Y.
5. **Giải phẫu hơn là khớp hình.** Xoắn cẳng tay chia giữa vai và cổ tay (khuỷu chỉ là bản lề); không ép hướng bàn tay làm xoắn cẳng tay. Tấm giáp trên cẳng tay đi theo roll của cánh tay trên.
6. **View ngang giấu chiều sâu.** Bàn tay trông như ở trước vật có thể ở sau nó - xác nhận bằng view top.
7. **Đáp án (FBX gốc), nếu người dùng đưa, chỉ để chấm điểm.** Nếu nó ảnh hưởng lựa chọn thì nói ra và ghi vào báo cáo.
8. **Mỗi note của người dùng → frame, bộ phận, vấn đề, cách sửa**; bài học chung vào `knowledge/`.
9. **Đo cái đo được, đọc phần còn lại bằng mắt - và ghi rõ cái nào là cái nào** ([đo] / [mắt]). Silhouette mù với xoắn thân khi prop và chân chi phối đường viền: đọc xoắn bằng việc mỗi camera thấy phía nào của ngực/lưng.
10. **Tay trên prop: giải, không ép bàn tay** (người dùng, Attack f13: "hai cánh tay bị bẻ quá giới hạn và xoắn vặn hỏng anatomy"): lưu đường cầm trượt quanh/dọc cán, khuỷu = bản lề thuần, cổ tay chỉ lệch nhỏ so với P0, khuỷu ngoài thân; cánh tay phải duỗi thẳng mới với tới = dời vai (xoắn/nghiêng ngực, đầu bù). Luôn nhìn cận cảnh trực giao từng tay.
11. **Bảng góc có thể nói dối.** Rig này gập khuỷu TRÁI ra sau ở rest (phải thì ra trước): xoắn vai trái so với rest lệch ~180°. Euler YZX gần góc gập 90° bị gimbal lock. Tin cận cảnh và skin strain; kiểm trục của phép xoay thêm cho bản lề.
12. **Một phiên chỉ một Lab đang sửa**: Lab lưu vào `work/store/`, đừng sửa tay file trong đó khi trang đang mở.

## Polish
- Overlap = dời key dọc chuỗi (hông → ngực +2 → bả vai +3 → tay +3/+4/+5 → prop +3), độ trễ lấy từ phân tích.
- Đừng nướng key từng frame rồi cộng chuyển động lên trên - sẽ rung. Chỉnh hằng số (vd roll khiên) = nhân quaternion lên key sẵn có, giữ dấu quaternion nhất quán giữa các key.
- Sau khi đổi giá trị key luôn kiểm đường nối vòng lặp (frame cuối = frame đầu), nếu không chỗ nối giật.
- Đánh giá độ mượt bằng gia tốc/jerk so với bản gốc nếu có (đòn quất được phép nhanh).
- Playblast lặp: phát f1..f(N-1) mỗi vòng (fN == f1), nếu không mỗi vòng có một frame khựng.
- Biến thể của clip đã duyệt (vd Idle_Front: không liếc, 60F): dùng lại đoạn key không liếc, khoá cái brief cấm (head yaw), làm các chu kỳ khác nhau rõ (biên độ 1,1 / 0,75; 28 / 31F) - lệch 12% trông như copy. Chỉ scale biên độ ở key đỉnh để mọi chu kỳ rời đáy cùng tốc độ.
- Prop dài khuếch đại xoay của xương cha (vai 1,45°/F → đầu chùy 4,5 cm/F giật): tìm xương nguồn trước, rồi làm dịu trong không gian thế giới trên key của prop; đo tốc độ đầu prop, không đo đầu xương.
- Tay tự do cứng trong nhịp thở: dùng IK, nâng bàn tay nhiều hơn vai lúc hít (khuỷu gập ra/sau ~15°), giữ bản lề trong giới hạn twist/bend.

## Blocking hàng loạt (nhiều key)
Khi các key khó nhất đã làm tay (thô → tinh), phần còn lại có thể fit hàng loạt: trộn key hai bên → chân đã chạm sàn khoá theo lịch tiếp xúc → bám prop (đỉnh prop chiếu so mặt nạ ref) → fit silhouette theo bậc thân → thân trên → đầu → tay `solve_grip` (không trượt dọc prop) → kiểm chiều dài cẳng tay → **kiểm mắt từng key theo lô** (`work/attack/batch_cmp.py`). Fit silhouette không bao giờ thay kiểm mắt.

## Review với đồng nghiệp
Review Lab là trang mỗi clip một artifact + một kho riêng (`docs/storage.md`): playlist | viewer | ghi chú, vẽ lên frame, ghi chú theo frame, nút Gửi feedback cho AI tạo vòng review. Người dùng gõ `/check_fb` để bạn nhận **mọi** note của vòng, sửa trong **một** version, tự kiểm bằng render nhanh rồi đăng. Quy trình chi tiết ở skill `check_fb`; không polling.
