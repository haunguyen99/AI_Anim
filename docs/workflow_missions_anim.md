# Mission Workflow cho team Anim (AI Tiên Phong)

Nhập vào Workflow:
- Dự án: **G - QUANLY-DIEUHANH-GAME**
- Epic: **[tên team Anim]**

Mỗi mục `##` là 1 mission, mỗi dòng `-` là 1 task, mỗi dòng thụt vào là 1 subtask. Trạng thái tính đến 04/11/2026.

---

## M1. AI dựng anim 3D từ video ref
**Trạng thái:** Đã xong (dùng hàng ngày)
**Kết quả:** Gaygor Idle 133F, Idle_Front 60F đã xuất FBX; Walk 57F đang polish.
- Phân tích ref theo pha và bộ phận, trình duyệt trước khi làm
  - Bản mô tả từng pha / bộ phận
  - Cổng duyệt 1: duyệt bản phân tích
- Dựng pose theo cấp: hông/chân → thân/đầu → đạo cụ → tay → bàn tay
  - So REF | ANIM từng góc (cả góc trên)
  - Kiểm giải phẫu từng key và từng frame
- Blocking stepped → spline → polish
  - Playblast từng mốc lên trang review
- Xuất FBX cho Unity

## M2. AI làm tiếp từ blocking của animator (Quy trình B)
**Trạng thái:** Đã xong (dùng hàng ngày)
**Kết quả:** Gaygor Attack (từ blocking 50%) và Hit đã xuất. SDR map3 Shoot, Reload đã chạy đúng trong Unity. G-LumberCity IdleWipe, CleanOutput, RopewayCrank đã xuất.
- Animator key blocking → nạp FBX vào Studio
  - Đọc đúng thứ tự xoay từng xương
- AI thêm pose chuyển tiếp (breakdown) 75%
- AI làm spline + polish (overlap, ease, rung đạo cụ)
- Xuất FBX + .meta, kiểm chạy trong Unity

## M3. AI làm anim chỉ từ mô tả GDD (Quy trình C) + ảnh key pose AI
**Trạng thái:** Đã xong (dùng hàng ngày)
**Kết quả:** Gaygor Hit, SDR map1 Idle/Shoot, SDR map3 Idle, SDR map5 (Colt) Idle/Shoot. Reload map5 đang làm.
- Đọc order GDD → thiết kế diễn xuất + timing
- Tạo ảnh key pose bằng AI (Codex) theo concept
  - Khoá camera / khung / sàn để các ảnh thành flipbook
  - Trang duyệt ảnh key
- Dựng P0 → blocking → spline → polish trên Studio
- Xuất FBX + event (OnWeaponRelease, …)

## M4. AI Anim Studio: phần mềm anim chạy trên web
**Trạng thái:** Đã xong (giai đoạn S1–S4, W1–W3), đang bổ sung tính năng
**Kết quả:** Một app kiểu Maya thay cho Blender/Cascadeur: Mesh, Rig, Pose, Review, vật lý, xuất FBX.
- Mesh: sửa mesh cơ bản
- Rig: đặt khớp, skin, thử khớp gập
- Pose: key, spline, bám sàn, khớp ref
  - Lớp vật lý: lò xo, va chạm, cân bằng, ragdoll
- Review: playblast, ghi chú vẽ theo frame, nút "Gửi cho AI"
- Cầu nối để AI điều khiển Studio trực tiếp
- Home: quản lý dự án theo game → anim → giai đoạn

## M5. AI tự rig nhân vật trong Frolvy
**Trạng thái:** Đang triển khai
**Kết quả:** Rig MC_Worker (G-LumberCity) đã dùng để làm anim và xuất FBX.
- Kiểm model → đặt joint theo chuẩn AdvancedSkeleton
- Build rig + skin bằng joint DEF, sửa skin theo vùng
- Control, switch, picker cho animator
- Xuất rig lái skeleton của team cho Unity
- Ghi lỗi Frolvy, gửi feedback cho đội phát triển

## M6. AI làm anim 2D Spine
**Trạng thái:** Đang triển khai
**Kết quả:** Engine idle và active cho Spine; case đã duyệt: Cừu cầm ô, Cừu Sakura.
- Rig Spine: xương, slot, mesh weight
- Engine idle (loop) dùng lại case đã duyệt
- Engine active + mix idle → active
- Xem trực tiếp trên Home (Spine Live) và export

## M7. AI tự kiểm chất lượng: Animation Director + luật khớp
**Trạng thái:** Đã xong (chạy mọi mốc)
**Kết quả:** Director chấm mỗi mốc trước khi gửi người duyệt; luật giới hạn và liên động khớp chạy trên mọi key.
- Agent Director chấm theo frame + nguyên lý animation
  - Tự học ngưỡng duyệt sau mỗi lần duyệt / trả
- Luật khớp: giới hạn góc, bả vai theo tay, cột sống/cổ chia góc
- Ghi mọi lần duyệt / từ chối vào git kèm lý do → thành luật cho clip sau

## M8. Đưa anim vào Unity tự động
**Trạng thái:** Đã xong
**Kết quả:** File SDR map1, map3, map5, map6 đã đẩy lên nhánh TungNV_Dev; .meta và event tạo tự động.
- Xuất FBX theo khuôn file của team
- Tạo .meta (loop, takeName, Humanoid)
- Gắn event theo frame
- Đẩy lên đúng nhánh repo game

## M9. Trợ lý AI trên chat (HorusChat) nhận và điều phối việc
**Trạng thái:** Đang triển khai
**Kết quả:** Bot theo dõi tag / DM, tóm tắt order, đề xuất tự làm hoặc chuyển người phụ trách; đã xử lý order London zombie 2, nỏ Mayah.
- Kết nối API HorusChat (đọc tin, gửi tin sau khi người dùng đồng ý)
- Bộ canh tin chạy nền
- Tóm tắt order (sheet, ảnh, thread) → đề xuất làm / chuyển / hỏi thêm
- Mỗi việc một phiên AI riêng, báo kết quả lại
- Góp ý API cho đội HorusChat (gửi kèm ảnh)

## M10. Báo cáo và slide tự động từ phiên làm việc AI
**Trạng thái:** Đã xong
**Kết quả:** Deck "Quy trình diễn hoạt với AI" (32 slide) và "Báo cáo áp dụng AI cho diễn hoạt" (10 slide).
- Đọc log phiên + lịch sử phiên bản → số liệu
- Dựng video tiến độ từ từng bản
- Sinh báo cáo + slide
