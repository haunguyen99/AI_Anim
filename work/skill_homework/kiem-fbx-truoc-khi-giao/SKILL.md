---
name: kiem-fbx-truoc-khi-giao
description: Kiểm file FBX nhân vật (Base) và file anim trước khi đưa vào Unity: mesh, xương, bind pose, vũ khí gắn đúng xương. Dùng trước khi giao hoặc khi import Unity bị méo, mất mesh.
---
# Kiểm FBX trước khi giao
## Khi nào dùng / không dùng
Dùng: sắp giao FBX cho Unity, hoặc import lỗi. Không dùng: sửa anim, rig, skin.
## Cần hỏi người dùng (nếu thiếu)
File nào là Base, file nào là anim; công cụ xuất; vũ khí/prop treo vào xương nào; đơn vị (cm hay m).
## Các bước
1. Phân loại: Base (xương + mesh, T-pose, không clip) hay anim (chỉ xương + clip, không mesh).
2. Base: mesh có skin và BindPose; không có clip; mọi mesh có xương hoặc nhóm cha; prop dưới đúng xương.
3. Anim: 0 mesh, 0 vật liệu; tên và số xương trùng Base; tên take = tên clip.
4. Import thử trong Unity: tab Rig, xem preview T-pose, đếm mesh bằng số mesh trong file.
5. Lỗi hay gặp và cách sửa: xem checklist_fbx.md.
## Định dạng đầu ra + ví dụ
Bảng: Mục kiểm | Đạt/Lỗi | Ghi chú. Ví dụ: `Mesh vũ khí có cha | Lỗi | nằm ngoài cây xương, Unity bỏ qua`.
## Tự kiểm trước khi trả kết quả
Mọi mục đều có kết quả Đạt hoặc Lỗi; mục chưa kiểm được ghi "chưa kiểm", không đoán; lỗi nào cũng kèm cách sửa.
