# Rig Lab: thiết kế tool rigging (bản nháp chờ duyệt, 2026-10-23)

## 1. Vị trí trong quy trình

Hiện bước rigging nằm ở pipeline_v2 bước 3, chạy bằng Blender (`inspect_rig.py`, `build_ctrl_rig.py`, `joint_limits.py`, `pole_audit.py`) và chỉ làm được khi khách đã đưa rig FBX có sẵn. Rig Lab thay bước này bằng một trang web, cùng kiểu Pose Lab, và thêm phần mới: **từ mesh trần tạo xương và skin**. Theo quyết định 2026-10-23 ("bỏ hẳn Blender"), Rig Lab không gọi Blender, kể cả headless.

```
mesh trần (GLB/FBX/OBJ)
  → 1 Chuẩn bị mesh → 2 Đặt khớp → 3 Skeleton → 4 Skin → 5 Control rig → 6 QA → 7 Xuất
  → Base.fbx (xương + mesh + skin)  +  rig.json  → Pose Lab đọc luôn
```

## 2. Đầu ra (hợp đồng với Pose Lab)

| File | Nội dung |
|---|---|
| `<char>_Base.fbx` | Joint + mesh + skin, tên xương theo chuẩn dự án (`Root_M, Hip_M, Spine1_M, Chest_M, Neck_M, Head_M, Shoulder_R, Elbow_R, Wrist_R…`), cùng quy ước với rig khách để FBX Unity không đổi |
| `<char>_rig.json` | Danh sách xương, IK chain (gốc–giữa–đầu), pole và cha của pole, follow space, prop + khớp cha, giới hạn khớp (min/max từng trục), nhóm xương chính/phụ |
| `<char>_weights.json` | Trọng số skin (thưa, tối đa 4 ảnh hưởng/đỉnh) để sửa lại được |

Pose Lab hiện đọc glTF xuất từ Blender (`models/*.json`) và ghi FBX bằng `fbx/fbxwrite.py`. Rig Lab dùng lại hai phần đó, nên không viết lại writer FBX.

## 3. Bảy bước chi tiết

**1. Chuẩn bị mesh.** Nạp mesh, hiển thị 3D + 3 view orthographic. Kiểm tra: tỉ lệ (chiều cao thật, cm), hướng (+Y lên, mặt nhìn +Z hoặc theo quy ước dự án), thân có kín không, các phần rời (vũ khí, giáp) gom thành "island". Người dùng đánh dấu island nào là prop (không skin theo thân, gắn vào một khớp).

**2. Đặt khớp (landmark).** Chọn template: `biped` (người, gangster, lính), `biped+tail`, `quadruped`, `spider8`. Template cho sẵn danh sách khớp cần đặt (khoảng 20 cho biped). Cách đặt:
- Gợi ý tự động: lấy trục thân bằng voxel hóa mesh (medial axis), khớp với template theo tỉ lệ người; **Claude xem render 3 góc rồi đề xuất vị trí**, người dùng kéo chỉnh. Không tin tuyệt đối vào auto (bài học: đo số mà không nhìn bằng mắt đã sai nhiều lần).
- Mỗi khớp là điểm 3D có thể kéo ngay trên view 3D, có gizmo, đối xứng L/R bật mặc định (kéo bên R thì bên L theo).
- Khớp gập (gối, khuỷu) đặt thẳng hàng trong mặt phẳng gập, có chỉ báo cung gập để pole không bị lệch ngay từ đầu.

**3. Skeleton.** Sinh xương từ landmark, tính trục cục bộ: trục X dọc xương, trục gập (hinge) cố định cho gối/khuỷu, roll tay/chân theo quy ước dự án. Xương phụ (ngón, đuôi, tai, giáp) sinh theo chuỗi, người dùng thêm/xóa xương trên trang. Sinh tên chuẩn, báo trùng tên.

**4. Skin.** Hai lớp:
- Tự động: trọng số khuếch tán theo khoảng cách trắc địa trong voxel (kiểu Pinocchio / heat diffusion), tính trong trình duyệt (Web Worker). Cắt tối đa 4 ảnh hưởng, chuẩn hóa tổng bằng 1.
- Chỉnh tay: cọ vẽ (add/subtract/smooth), tô màu heatmap theo xương, khóa xương, mirror L→R, flood-normalize.
- Thử biến dạng: thanh trượt xoay từng khớp, bộ "pose căng" cố định (giơ tay, ngồi xổm, vặn thân, gập hông) và chấm điểm vùng bị co hay bẹp (tỉ lệ thể tích/diện tích tam giác so với rest), tô đỏ vùng vượt ngưỡng. Gần với `skin strain` đã dùng ở Attack.

**5. Control rig.** Từ skeleton sinh sẵn spec, người dùng xem và chỉnh:
- IK chân (hông–gối–cổ chân), IK tay (vai–khuỷu–cổ tay); có chế độ FK/IK.
- **Pole luôn gắn cha** (gối → bàn chân, khuỷu → ngực hoặc tay), kèm hướng mặc định, theo luật "Pole not free".
- Control chân/bàn chân (gót, mũi) cho bám sàn, control hông, ngực, đầu; follow space cho tay cầm prop.
- Prop: chọn khớp cha (hỏi khi intake, như bài học SDR: súng nằm ở `Wrist_R`).
- Giới hạn khớp theo template, sửa từng trục.

**6. QA tự động.** Chạy trên rig trước khi xuất: xương zero-length hoặc đảo chiều, trục gập lệch mặt phẳng, đối xứng L/R (sai lệch vị trí/roll), đỉnh chưa gán xương hoặc tổng trọng số khác 1, đỉnh dính quá 4 xương, pole nằm ngoài cung gập, giới hạn khớp thiếu, tên xương sai quy ước, độ biến dạng ở bộ pose căng. Có báo cáo PASS/FAIL từng mục, giống `qa_report.py`.

**7. Xuất.** Bake ra `Base.fbx` (đúng tên xương, đúng đơn vị cm, tỉ lệ 1) + `rig.json` + `weights.json`. Kiểm bằng nạp lại vào Pose Lab và so vị trí từng xương (như `cmp_page_track.py`).

## 4. Kiến trúc kỹ thuật

- Một trang tĩnh `work/rig_lab/index.html` (three.js như Pose Lab), tách mỗi nhân vật thành một artifact bằng `split_pages.py`; lưu trạng thái (landmark, weights, rig) trong db của artifact để mở lại và sửa.
- Phần nặng (voxel hóa, khuếch tán trọng số) chạy trong Web Worker; mesh dưới khoảng 100k tam giác thì vài giây.
- Dùng lại `fbx/fbxwrite.py`/`fbxexport.js` để ghi FBX; thêm phần ghi skin cluster (hiện writer mới ghi xương và animation, cần kiểm tra).
- Mã dùng chung: tách logic rig (IK, pole, giới hạn) thành module mà Pose Lab cũng import, tránh hai nơi lệch nhau.

## 5. Phân kỳ (mỗi mốc có sản phẩm xem được)

| Mốc | Làm gì | Thử trên |
|---|---|---|
| M1 | Nạp mesh, đặt khớp biped có đối xứng, sinh skeleton + xuất rig.json | mesh Gaygor (so với rig khách) |
| M2 | Skin tự động + heatmap + thử khớp | mesh SDR map06 (so với skin khách) |
| M3 | Cọ vẽ trọng số, bộ pose căng, tô vùng lỗi | cùng mesh |
| M4 | Control rig: IK, pole, giới hạn khớp, prop, QA tự động | Gaygor Walk (nạp thẳng vào Pose Lab) |
| M5 | Xuất FBX skin đầy đủ, kiểm nạp lại; template quadruped/spider8 | Queen Spider (chưa có rig) |

Cách kiểm chất lượng: dùng chính rig khách làm đáp án (Gaygor, SDR). Tool dựng lại rig từ mesh trần rồi so vị trí khớp và biến dạng với rig khách, không dùng điểm số này để quyết định, vẫn xem bằng mắt.

## 6. Rủi ro

- Auto-skin trên nhân vật cách điệu (Gaygor: tay dài, bụng to) thường cần chỉnh tay; ngân sách thời gian chủ yếu ở M3.
- Writer FBX chưa chắc ghi được skin cluster mà Unity nhận; kiểm sớm ở M1 bằng một FBX tối thiểu.
- Quadruped/nhện 8 chân: template khác hẳn, để M5.
- Mesh có nhiều phần rời (giáp, vũ khí) làm sai voxel hóa; cần bước đánh dấu island.

## 7. Cần bạn quyết

1. Thứ tự ưu tiên: bắt đầu M1 trên Gaygor hay trên Queen Spider (cần ngay, nhưng khó nhất)?
2. Quy ước tên xương và trục: giữ y nguyên rig khách (`Hip_M`, `Shoulder_R`, trục X dọc xương) cho mọi nhân vật mới, đúng không?
3. Mức tự động mong muốn: tự động hết rồi sửa, hay từng bước đều có cổng duyệt như các bước animation?
