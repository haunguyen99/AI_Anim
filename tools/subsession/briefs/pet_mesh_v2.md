# Việc chung: chuyển rig + anim Pet đã chốt sang MESH MỚI (Infinite Defense)

Bạn làm MỘT Pet (tên và cổng ở prompt). Trả lời tiếng Việt, lời thường.

## Bối cảnh
- Artist vừa cập nhật model 5 Pet (2026-11-18). Mesh mới: gọn hơn (ít đỉnh), Y lên, UV + texture mới. Rig và Idle/Attack cũ đã chốt (user 2026-11-13/14) làm trên mesh CŨ. Việc của bạn: đưa mesh mới vào, skin lại, giữ nguyên anim đã chốt.
- Ảnh so sánh lưới/UV cũ-mới: work/infinite_defense/_review_pet_new/mesh_check/<Tên>.png (xem trước). Mỗi con có ghi chú riêng ở prompt.
- Mesh mới (chỉ đọc, KHÔNG sửa): /home/ngocvb/Projects/endless-kicker/Assets/Kho/Skin/mesh/Pet_new/mesh/Pet_<Tên>.fbx (texture ở ../texture/T_Pet_*.png).
- Thư mục làm việc (file cũ, KHÔNG ghi đè, KHÔNG xóa): /home/ngocvb/Projects/tvc_source/3D ANIM/EndlessKicker/Pet_<ID>_<Tên>/ (có <tên>_rig.fv, _idle.fv, _attack*.fv, FBX đã xuất, CHOT.txt). Làm bản mới trong thư mục con `v2_mesh_moi/` của nó; tên file thêm `_v2` (vd `tiny_chick_rig_v2.fv`).
- Script + báo cáo cũ của con này: work/infinite_defense/pets/<folder>/ (report.md, rig/, anim/). ĐỌC report.md trước, tái dùng script rig/skin cũ khi được.

## Luật (đọc trước khi làm)
- `.claude/skills/frolvy_rig/` và `.claude/skills/frolvy_auto_rig/`, `.claude/skills/animation/knowledge/CORE.md`.
- Memory trong `.claude/memory_store/`: frolvy-bind-pose-and-empty-curve.md (bind khi mọi control = 0, rồi set_frame(3); set_frame(0); đừng xóa hết key một channel; đừng dựng lại rig trong cùng scene), frolvy-game-rig-base-joints-only.md (skin chỉ DEF, tối đa 4 influence), frolvy-fit-controls-after-build.md, keep-existing-keys-when-editing.md (KHÔNG đổi key đã có), frolvy-loop-seam-smooth.md, project-pets-float.md (Pet bay lơ lửng), feedback-self-fix-twist.md (tự dò xoắn rồi sửa).
- Pet BAY LƠ LỬNG: không tiếp đất. Hướng mặt +Z, Y lên (rig cũ đúng như vậy).

## Cách làm gợi ý
1. Mở file rig cũ (+ idle, attack cũ) để lấy tên joint DEF, tên control, vị trí joint. Giữ NGUYÊN tên joint/control/cây phân cấp để key cũ áp lại được.
2. Nhập mesh mới vào Frolvy, kiểm hướng (mặt +Z, Y lên, chân/đáy ở y≈0; nếu quay ngược thì xoay quanh Y rồi freeze). Mesh mới Y lên: KHÔNG cần xoay -90° quanh X như mesh cũ.
3. Đặt mesh mới thay mesh cũ trong rig (joint đặt theo vị trí cũ, chỉnh nếu hình khối mới lệch), bind skin: lấy trọng số cũ làm điểm xuất phát (chuyển theo bề mặt gần nhất), rồi sửa theo vùng. Skin chỉ DEF, max 4 influence, tổng = 1.
4. Kiểm: xoay thử các khớp chính, skin_check.py nếu có (xem rig/ của con này), tự dò xoắn/vỡ lưới; Idle và Attack: chạy đúng như bản chốt (so frame mấu chốt cũ/mới, mesh không xuyên, không lộ khe).
5. Đưa mesh+skin mới vào file idle và attack (hoặc nạp lại key cũ vào rig mới), lưu `_rig_v2.fv`, `_idle_v2.fv`, `_attack_v2.fv`. Idle vẫn lặp liền mạch; Attack cuối về đúng idle F0, frame bắn như cũ.
6. Tự kiểm bằng render nhanh (xem tools/quick_sheet.py / pet_playblast.py nếu có). Không gửi playblast cho người dùng; chỉ cần ảnh tự kiểm lưu trong `v2_mesh_moi/shots/`.

## Điều khiển Frolvy (QUAN TRỌNG)
- Máy này là Linux, Frolvy là AppImage `~/.local/share/frolvy/Frolvy.AppImage`. KHÔNG dùng công cụ MCP `frolvy` có sẵn (lỗi, nối cổng 9877 của người dùng). Dùng: `python3 -I tools/frolvy_port.py <cổng> <file.py>` hoặc `... <cổng> scene` (chạy đoạn Python trong Frolvy, in kết quả). Đọc đầu file tools/frolvy_port.py.
- Cổng của bạn ở prompt. Nếu chưa có cửa sổ trên cổng đó (`ss -ltn | grep <cổng>`), mở: `DISPLAY=:0 XAUTHORITY=/home/ngocvb/.Xauthority DCC_MCP_PORT=<cổng> nohup ~/.local/share/frolvy/Frolvy.AppImage >/tmp/frolvy_<cổng>.log 2>&1 &` rồi đợi ~15 giây. TUYỆT ĐỐI không đụng 9877 và các cổng khác (4 agent song song dùng 9881–9885, mỗi người một cổng).
- Script Python chạy trong repo: dùng `python3 -I` (không có .venv/Scripts trên Linux). Đường dẫn Windows trong script cũ (C:\Users\Admin\...) đổi sang đường dẫn Linux ở trên.
- Lưu .fv sớm và thường xuyên (cửa sổ Frolvy có thể bị đóng giữa chừng).

## Cấm
- KHÔNG xuất FBX (chỉ xuất khi người dùng nói "chốt"), KHÔNG chép vào Unity, KHÔNG commit/đổi nhánh/đẩy git (kể cả repo endless-kicker), KHÔNG gửi HorusChat/WorkAI, KHÔNG đọc hay in .env / key / token. KHÔNG sửa file cũ ngoài `v2_mesh_moi/`. KHÔNG chạm các Pet khác.
- Việc ngoài phạm vi hoặc mesh có vấn đề không xử lý được (vd mảnh lạ không rõ là gì): ghi vào báo cáo, dừng phần đó, không đoán.

## Xong là gì
- File `_rig_v2.fv`, `_idle_v2.fv`, `_attack_v2.fv` trong `v2_mesh_moi/` (mở được, anim chạy đúng).
- work/infinite_defense/pets/<folder>/report_mesh_v2.md: đã làm gì, skin ra sao, so Idle/Attack cũ-mới (frame nào khác, vì sao), chỗ chưa chắc, đường dẫn file. Lời thường, không dán code dài.
- Dòng đầu báo cáo cuối cho phiên chính: `XONG: ...` hoặc `CHẶN: <câu hỏi>`; nêu rõ phần nào chưa kiểm được.
