# Mesh Lab

Trang sửa mesh cơ bản, đứng **trước Rig Lab** trong chuỗi Mesh → Rig → Pose → Review. Mục đích: sửa nhanh những lỗi mesh làm rig hay skin hỏng (khối rời, điểm trùng, mesh lệch tâm, sai tỉ lệ) mà không phải mở Blender/Maya. Không có extrude, bevel, loop cut, UV, retopo.

- **Mở:** tab **Mesh** trong vỏ ứng dụng (Home → anim → Mesh), hoặc `http://127.0.0.1:8780/lab/mesh/<nhân vật>`.
- **Build:** `python work/mesh_lab/build_mesh.py <gaygor|id trong work/rig_lab/chars>` → `work/mesh_lab/pages/<id>/index.html` (nhúng mesh gốc cm từ `ref_gaygor/ref_mesh.json` hoặc `chars/<id>/mesh_cm.json`). Template: `work/mesh_lab/template.html` (dấu `/*DATA*/null`).

## Thao tác

| | |
|---|---|
| Chế độ chọn | Mesh (1) · Điểm (2) · Mặt (3) · Khối rời (4). Click, kéo khung (Chỉ mặt trước = bỏ điểm sau lưng), Shift hoặc nút + thêm/bớt |
| Công cụ | Chỉ chọn (Q) · Dời (W) · Xoay (E) · Scale (R) bằng gizmo · **Free Transform (T)**; **Mềm** (falloff theo bán kính cm) và **Đối xứng X** (điểm đối xứng đi theo) |
| Camera | Alt + chuột trái hoặc chuột phải xoay, chuột giữa kéo, lăn = zoom, A = nhìn toàn bộ. Cảm ứng: checkbox bàn tay + thanh Xoay / Chọn / Khung / + |
| Chọn nhanh | Tất cả (Ctrl+A) · Bỏ · Đảo · Nới một vòng |
| Sửa | Xoá (Del) · Tách mesh · Gộp mesh · Nhân bản · Lật pháp tuyến · Làm mượt · Lật trái/phải (X) · Dọn mesh (mặt hỏng, mặt trùng, điểm lẻ) · Hàn điểm gần (ngưỡng cm) |
| Cảnh | Đặt xuống sàn (chân Y=0, tâm X=Z=0) · scale cả cảnh về chiều cao (cm) |
| Kiểm tra | điểm lẻ, mặt hỏng, mặt trùng, điểm trùng, cạnh chung >2 mặt, số khối rời, cạnh hở |
| Danh sách mesh | mắt ẩn/hiện, khoá, bấm đôi đổi tên, xoá |
| Hoàn tác | Ctrl+Z / Ctrl+Shift+Z, 40 bước |

## Channel Box và Free Transform

- **Channel Box** (góc trên phải viewport, gập được): Translate / Rotate / Scale của **vùng chọn** (mesh đang chọn, hoặc các điểm / mặt / khối). Gõ số rồi Enter, hoặc **kéo trái / phải trên nhãn** X / Y / Z để đổi liên tục (Shift = tinh, Ctrl = thô). Translate là tâm vùng chọn (cm, thế giới); Rotate (độ, XYZ) và Scale là phép biến đổi **cộng dồn** từ lúc chọn, cộng cả những lần kéo gizmo / Free Transform; đổi vùng chọn thì về 0 / 1, hoặc bấm **Đặt lại 0/1**. Mesh được "nướng" vào đỉnh (không có transform riêng cho object), nên đây là phép đang áp lên các đỉnh, dùng chung **Mềm** và **Đối xứng X**; Hoàn tác từng lần sửa.
- **Free Transform (T)**: hộp bao quanh vùng chọn với tay nắm: **mặt** (ô vuông) giãn một trục, neo mặt đối diện; **góc** (tròn) scale đều, neo góc đối diện; **tâm** (xanh) dời trong mặt phẳng camera. **Shift** ở tay mặt = giãn đều 3 trục, **Alt** = neo ở tâm hộp. Hộp bao thẳng theo trục thế giới. Chưa có tay xoay (dùng Xoay hoặc Channel Box).

## Lưu và xuất

- Tự lưu 1,5 giây sau mỗi thay đổi vào `mesh/edit` của kho (`docs/storage.md`, file `work/store/<ns>/mesh/edit.json`); mở lại thì nạp bản đã sửa. **Về bản gốc** bỏ mọi sửa.
- **Xuất OBJ** (cm, +Y lên) và **Xuất cho Rig** (`<tên>_mesh_cm.json`, cùng định dạng Rig Lab đọc: `[{name, verts, tris}]`). Nút Lưu trữ ở góc trên xuất / mở cả kho dạng `.json`.
- Sửa mesh làm số điểm đổi, nên skin khách (`weights`) của mesh gốc không đi theo bản xuất.

## Chưa làm

- Rig Lab tự đọc bản đã sửa (xem `docs/data_flow.md`); Xuất cho Rig chỉ cần khi dùng ngoài Home.
- Chọn điểm xuyên mesh (X-ray), loop/ring select, extrude, bevel, UV.
