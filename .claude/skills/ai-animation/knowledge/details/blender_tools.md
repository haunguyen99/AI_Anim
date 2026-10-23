# Blender: rig, file live, công cụ (mọi loại anim)
Quy tắc nền (posing mode, scale, f-curve rỗng, mỗi clip một cửa sổ/cổng): SKILL.md quy tắc 12-13.

## action-slot
- **Blender 4.4+ (action slot):** tạo action bằng `fcurves.new` rồi gán `animation_data.action` thì CHƯA chạy, vì `action_slot`
  vẫn là None, mọi frame render ra đều giống nhau (SDR map06 b1). Phải gán `ob.animation_data.action_slot = act.slots[0]`.
  Kiểm tra: `frame_set` sang 2 key khác nhau, rồi so giá trị của một xương.

## fbx-bone-axes
- Xương FBX (Advanced Skeleton, import không auto-orient) có tail KHÔNG nằm dọc chi (trục dài = local ±X): IK đặt thẳng lên
  xương deform sai -> dùng chuỗi IK phụ (thigh/shin) + H_* copy loc/rot (SDR sdr_lib.build_ctrl); hướng chi lấy theo
  khớp con (one_dir), không theo head->tail.
- Khớp xương FBX có thể không nằm ở điểm treo thật (xương vạt khố nằm giữa tấm vải) - `timing_spline.md#secondary-cloth`.

## rig-inventory
- Kiểm rig tìm xương phụ chưa key ngay từ bước phân tích (`rig_inventory.py`); tên xương có thể sai lệch: "cần phân tích cả quần
  áo, vải, phụ kiện... chain tóc, đuôi, tai, áo choàng" (Gaygor Attack) - kiểm kê xương phụ và mảnh mesh rời trước khi phân tích,
  nhận diện bằng vùng mesh (`Prop_M` là mặt vòng ngực, không phải chùy). DressFront_M/DressBack_M bị bỏ quên tới Idle v12.

## live-posing
- Pose chưa key bị ghi đè khi render/đo; f-curve rỗng sau khi xoá key -> quaternion 0 -> người lật 180°; scale trôi tích luỹ
  tới 10^9 -> dùng chế độ dựng pose (`posing`/`goto`/`done`), reset scale sau mỗi lần gán ma trận, xoá curve rỗng, khôi phục
  file từ bản lưu khi trạng thái live đã hỏng (Gaygor Attack).
- Dựng mọi key từ snapshot P0 bằng thay đổi tương đối (SDR `work/blender/sdr_attack.py`), không gắn action khi dựng, key CONSTANT sau cùng.
- Đo đầu tiên của anatomy() nạp P0 (goto 1): gọi `_p0()` TRƯỚC khi sửa pose, không thì mất bản sửa.
- `anatomy(f)` CÓ số frame sẽ dựng lại pose đã key của frame đó → khi đang thử pose chưa key, gọi `anatomy()` không tham số (Attack v10).
- Hàm sửa key viết dạng chạy lại được: bắt đầu từ pose bản trước (`goto_v9(f)` đọc action v9 từ file cũ) chứ không từ `goto(f)` của bản
  đang sửa, không thì chạy lần 2 sẽ cộng dồn. Pole gối của v9 ở không gian cũ → giữ matrix_basis pole của bản mới.
- Ghi tham số thử vào file (`work/<job>/vNN/fixes.py`) ngay khi chọn: phiên sau mất ~10 phút dò lại trạng thái khi chưa ghi (2026-10-22).

## review-files
- View "left" của trang review = file `right.mov` (refs.json) - cắt ảnh ref từ đúng file (Gaygor Attack: `_left.mov` = camera bên
  PHẢI nhân vật). SKILL.md bước 1: kiểm file nào là trái/phải của nhân vật.
- Ảnh so sánh > 1500 px bị thu nhỏ khi đọc: nhân toạ độ với tỉ lệ trước khi dùng.
- Dùng lại camera của clip khác -> mọi độ cao sai (Gaygor Attack v3 dùng camera Idle: 231 vs 201 px/m) - hiệu chỉnh riêng từng clip
  (SKILL.md quy tắc 2).

## batch-fit-traps
- Dựng hàng loạt key (Blender Attack blocking v4): khởi tạo = blend 2 key kề, tối ưu theo cấp bằng IoU 5 view; bẫy gặp: (1) dò chùy
  bằng render cả người bị cánh tay (con của chùy) làm nhiễu -> dò chùy riêng bằng chiếu đỉnh mesh; (2) bóng không phân biệt
  đầu/đuôi chùy -> ràng buộc thời gian hoặc hướng theo phân tích; (3) pose xa 2 key kề (nằm sấp) -> lưới thô thân trước;
  (4) thân tự xoắn để với tay -> khoá twist/roll khi ref đối xứng; (5) luôn thử thêm khởi tạo từ key gần nhất (f64 từ P0:
  .74 -> .82); (6) kiểm cổ tay đứt bằng độ dài cẳng tay.
- Quy trình batch tổng: SKILL.md "Batch blocking".

## Rig Lab (rigging trên web, 2026-10-23)
- Đọc FBX binary không cần Blender: `work/rig_lab/extract_fbx.py` (mesh, bind pose từ cluster `TransformLink`, trọng số). Gaygor: thân 2532 đỉnh, prop `VK` (chùy) là island rời, rig khách 59 xương (không có `Hip_M`, `Root_M` là xương hông).
- Gợi ý khớp từ mesh (`propose.py`): trung vị z của lát cắt bị lệch vì bụng to; dùng giữa khoảng min–max của lát cắt cho cột sống và tay. Tỉ lệ vị trí khớp theo chiều cao/sải tay đã tuned trên Gaygor, nhân vật khác phải chỉnh bằng mắt. Sai lệch so với rig khách: trung bình ~4,5 cm, đầu/hông/gối theo z lệch nhiều nhất (≤12 cm).
- Mỗi bước M1 có cổng duyệt (db `rig/gates`); chưa tin số đo, phải xem Trước/Cạnh/Trên.
- Twist joint (Rig Lab bước 3, 2026-10-23): số lượng 0–3 mỗi đoạn (cánh tay trên, cẳng tay, đùi, cẳng chân), đặt đều theo t = i/(n+1). Tên `<KhớpĐầu>Twist<i>_<R|L>` (vd `ElbowTwist2_R`). Đoạn đầu (Shoulder/Hip): cha = khớp đầu, roll = −t × roll khớp đầu. Đoạn cuối (Elbow/Knee): cha = Elbow/Knee, roll = +t × roll Wrist/Ankle. Spec nằm trong `rig.json` (`twist: {source, factor, segment}`); Pose Lab và skin M2 phải đọc.
- Rig Lab M1 Gaygor duyệt 2026-10-23 (commit e85c041): khớp do user chỉnh `work/rig_lab/landmarks_user_m1.json` lệch rig khách trung bình 3,0 cm (gợi ý tự động 4,7 cm); user nâng cổ lên y≈159 (rig khách 153) và đẩy đầu/đỉnh đầu ra trước (z 16/35). Gợi ý tự động sai nhất ở đầu và cổ theo z/y: lần sau đặt đầu/cổ theo view Cạnh trước. Twist user chọn: cánh tay trên 1, cẳng tay 1, đùi 1, cẳng chân 0.
- Rig Lab M2 skin (2026-10-23): khuếch tán nhiệt trên mesh (cotan Laplacian, `H = 1/d²`, Gauss-Seidel, tối đa 4 xương), ~0,3 s cho 2532 đỉnh. Xương lá không skin: `*End_*`, `Finger3`, `Weapon` (chỉ prop). Bài học khi so với skin khách (trùng xương chính 73%, lệch TB 35%): (1) xương lá gắn trên bề mặt (Prop_M, váy) phải bị phạt khoảng cách ×2,5 khi chọn seed, nếu không chúng cướp cả vùng đầu/ngực vì bề mặt gần điểm đó hơn trục thân; (2) đoạn Hip và Scapula nên bắt đầu thụt 35–40% vào đoạn xương, phần trên thuộc Root_M/Chest_M; (3) xương twist chia nhỏ đoạn chi thành các đoạn con làm seed. Pose thử có twist: xoay cẳng tay 120° co/căng quá 25% còn 0,9% đỉnh (tắt twist 1,9%).
- Rig Lab công cụ "Gán khối rời" (2026-10-23): mesh Gaygor có khối rời (khiên 90 đỉnh ở x≈−118, y≈162, tức bên R, cạnh cẳng tay) nằm trong cùng mesh với thân; gán 100% cả khối cho một joint (kể cả joint twist). Raycast phải bỏ qua khối thân chính (>30% đỉnh): lần đầu tool gán nhầm cả thân 2351 đỉnh vì tia trúng mặt cánh tay trước khiên, đã sửa và có undo.
