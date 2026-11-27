# Bảng kết quả thử 2 skill

## Hướng dẫn cho người thử (đồng nghiệp)
1. Chép 2 thư mục `viet-brief-anim` và `kiem-fbx-truoc-khi-giao` vào `~/.claude/skills/` (Claude Code / Paseo) hoặc tải lên mục skill tùy chỉnh của Claude.
2. Mở một phiên **mới**. Chép nguyên văn từng câu bên dưới, mỗi câu gõ trong một phiên mới (để câu trước không ảnh hưởng câu sau).
3. Không cần file nào: mọi câu đều tự chứa đủ thông tin.
4. Ghi vào cột trống: skill có được gọi không (Có/Không; Claude thường hiện tên skill khi dùng) và kết quả có khớp cột "Dấu hiệu đúng" không (Đúng/Sai).

## Skill 1: viet-brief-anim
| # | Câu thử (chép nguyên văn) | Nên gọi? | Dấu hiệu đúng | Skill được gọi? | Kết quả đúng? |
|---|---|---|---|---|---|
| 1 | Viết brief cho clip Idle dài 2 giây, nhân vật hiệp sĩ cầm khiên, loop, camera nhìn từ trên xuống. | Có | Có bảng pha (frame, easing, ý định), mô tả từng bộ phận, bộ phận phụ, key plan; frame cuối khớp frame đầu | | |
| 2 | Tôi cần bản phân tích chi tiết cho clip Attack chém ngang của một con quái vật, 30 frame. Chia pha giúp tôi. | Có | Bảng pha cộng lại đủ 30 frame; có anticipation, đòn đánh, hồi lại; chưa dựng pose | | |
| 3 | Soạn bản mô tả chuyển động cho skill phóng cầu lửa của pháp sư để team duyệt trước khi dựng. | Có | Có đủ 5 mục của brief; hỏi lại nếu thiếu thông tin (số frame, loop, camera) | | |
| 4 | Giải thích sự khác nhau giữa ease-in và ease-out trong animation. | Không | Trả lời ngắn như kiến thức thường, không ra bản brief nhiều mục | | |
| 5 | Viết giúp tôi email xin nghỉ phép ngày mai. | Không | Ra email bình thường, không nhắc brief hay pha anim | | |

## Skill 2: kiem-fbx-truoc-khi-giao
| # | Câu thử (chép nguyên văn) | Nên gọi? | Dấu hiệu đúng | Skill được gọi? | Kết quả đúng? |
|---|---|---|---|---|---|
| 1 | Tôi sắp giao file FBX nhân vật cho Unity. Cho tôi danh sách cần kiểm trước khi giao. | Có | Phân biệt file Base (xương + mesh, không clip) và file anim (chỉ xương + clip); có bảng Mục kiểm / Đạt-Lỗi / Ghi chú | | |
| 2 | Import FBX vào Unity thì mesh bị méo: chân gập, tay chìa ra, nhưng xương nhìn đúng. Nguyên nhân thường gặp là gì và cần kiểm gì? | Có | Nêu thiếu BindPose / ma trận bind; kèm cách sửa; không đoán bừa | | |
| 3 | File FBX anim của tôi báo lỗi "Cannot find root motion transform" khi Copy Avatar từ Base. Kiểm và sửa thế nào? | Có | Nêu file anim chỉ có một nút gốc trong khi Base có mesh cùng cấp; cách sửa là thêm một nút rỗng cùng cấp vào file anim | | |
| 4 | Hướng dẫn tôi bind skin cho nhân vật, vùng vai bị móp khi giơ tay. | Không | Nói về weight / skin, không ra bảng kiểm FBX | | |
| 5 | Tóm tắt giúp tôi đoạn văn sau thành 3 ý: "Hôm nay cả nhóm họp để bàn kế hoạch quý tới, có ba việc chính là tuyển người, mua thiết bị và sắp xếp lại chỗ ngồi." | Không | Ra 3 ý tóm tắt, không nhắc FBX | | |

Quy tắc: cả 5 câu đều đúng thì đạt. Câu nên gọi mà skill không được gọi, hoặc câu không nên gọi mà skill lại được gọi: sửa phần `description` của skill, không sửa thân.

## So sánh có / không skill (cùng một việc, chạy hai lần)
| Skill | Việc thử | Số lần phải sửa tay (có skill) | Thời gian (có) | Số lần sửa tay (không skill) | Thời gian (không) |
|---|---|---|---|---|---|
| viet-brief-anim | | | | | |
| kiem-fbx-truoc-khi-giao | | | | | |

## Danh sách chấm "số lần sửa tay" cho viet-brief-anim (mỗi mục thiếu hoặc sai = 1 lần sửa)
| # | Mục | Brief đạt khi | Không skill (thiếu/sai?) | Có skill (thiếu/sai?) |
|---|---|---|---|---|
| 1 | Bảng pha | Có frame, easing, ý định; tổng frame đủ độ dài clip | | |
| 2 | Loop | Frame cuối khớp frame đầu | | |
| 3 | Từng bộ phận | Có góc, frame, độ trễ, theo thứ tự hông/chân → thân/đầu → prop → tay | | |
| 4 | Bộ phận phụ | Có vải, tóc, đuôi hoặc phụ kiện kèm độ trễ | | |
| 5 | Key plan | Có frame key chính | | |
| 6 | Nguồn | Có nhãn [ref] / [concept] / [thiết kế] | | |
| 7 | Không lan man | Không tự dựng pose, không thêm phần ngoài brief | | |
Số lần sửa tay = số dòng bị đánh dấu thiếu/sai trong từng cột. Thời gian: bấm giờ từ lúc gõ yêu cầu tới lúc brief dùng được.

## 3 dòng rút kinh nghiệm
1.
2.
3.
