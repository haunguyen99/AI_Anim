# gdd_stage0 — Giai đoạn 0: GDD → phân tích → ảnh key pose làm ref

Người dùng yêu cầu ngày 2026-10-28 ("phát triển tính năng ở giai đoạn đầu, lúc đọc GDD và viết tài liệu phân tích"; vướng nhất:
"phân tích chưa sát"). Chạy trước quy trình C (`text_brief.md`). Ảnh key pose thay cho "không có ref".
Clip đầu tiên: SDR map3 nỏ (`work/shoot_die_repeat/sdr03/`).

## Các bước
| # | Bước | Ra gì |
|---|---|---|
| G1 | Đọc GDD (xlsx/Google Sheet: tải `.../export?format=xlsx`; `tools/gdd_read_xlsx.py` in mọi ô, `tools/gdd_xlsx_images.py` tách ảnh kèm ô neo). Lọc phần liên quan anim, gồm cả tab số liệu (nhịp bắn, hệ số tua) và tab "ref game gốc" (camera) | `work/<dự án>/gdd/anim_list.md` |
| G2 | Hỏi lại chỗ thiếu **và chỗ mâu thuẫn** trong GDD | mục câu hỏi trong `anim_list.md` (cấp dự án) và `analysis.md` mục E (cấp clip) |
| G3 | Phân tích từng clip theo mẫu `sdr06/analysis.md` | `analysis.md` |
| G4 | Prompt viết từ analysis (`keys/make_prompts.py`) → `tools/codex_img.py --ref concept --ref ảnh vũ khí` | `keys/k*.png` |
| G5 | Trang duyệt (artifact): key pose + thước frame + bảng pha + câu hỏi có phương án đề xuất | `review/index.html` |

## Luật cho "phân tích sát"
- **Mỗi ý một nhãn nguồn:** [GDD] trích nguyên văn câu gốc, [rig] đo trên rig, [clip cũ], [suy luận], [?]. Người duyệt soát kỹ chỗ [suy luận].
- **Đối chiếu GDD với rig trước khi viết:** liệt kê xương (cha, mesh skin vào đâu). Ví dụ map3: nỏ là con của `Wrist_L`, khớp GDD "tay trái đỡ nỏ"; dây và mũi tên chung `slingshot_1`, nên ẩn mũi tên khi bắn là câu hỏi.
- **Đọc cả tab số liệu:** cột "Reload speed ×" = 4,0 ÷ nhịp bắn, tức code tua anim tới ×5,33. Đây là ràng buộc độ dài clip mà mô tả anim không nói.
- **Tìm mâu thuẫn trong chính GDD:** phần mô tả có "đặt tên mới lên rãnh" nhưng các bước Reload không có; Fire Rate lv6 chậm hơn lv5. Đưa thành câu hỏi kèm phương án đề xuất, không tự chọn.
- **Rig không có ngón trỏ** (găng) thì động tác "bóp cò" phải đổi thành siết găng. Ghi rõ là [suy luận].

## Ảnh key pose (G4)
- Prompt chung: camera game (side, quay phải), nền xám trơn, giữ đúng tạo hình theo ảnh ref, luật cầm (tay nào cầm đâu) lặp lại trong mọi prompt.
- **Không chạy Codex song song** (401, xem `tools/codex_img.py`). Mỗi ảnh 80–120 s.
- **Cơ chế đạo cụ hay bị vẽ sai** (nỏ map3, v1): dây vẫn căng sau khi bắn, tên còn trên rãnh, kéo dây kiểu cung vượt chốt.
  Câu chung "dây bật về trước" không đủ. Phải tả **trạng thái nhìn thấy được**: "string slack, straight line between the two
  limb tips at the very front; top of the stock completely bare". Kéo dây: "brought back to the small catch just in front of
  the trigger, V shape, stops there". k2 cần 3 lần, k5 cần 2 lần (2026-10-28).
- **Bộ lọc an toàn có thể chặn** prompt vũ khí nhiều chữ "effort / counter-force / pulled". Thêm "toy-like stylized game prop,
  friendly mobile game", dùng từ "catch" thay "latch / trigger mechanism", là qua.
- Xem từng ảnh, ghi lệch vào chú thích trang, chỉ tạo lại ảnh lệch, lưu bản mới `_v2/_v3` (giữ bản cũ).
- Ảnh chỉ dùng để chốt ý đồ và dáng nhìn, **không đo góc** (`review_process.md`, bài học Attack: ước góc bằng mắt lệch 20–40°).
