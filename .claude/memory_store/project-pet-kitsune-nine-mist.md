---
name: project-pet-kitsune-nine-mist
description: Pet 23 Kitsune Nine-Mist (9 đuôi, Infinite Defense): rig 73 joint + CTL_TailFan, Idle 48F + Attack v6 chốt 2026-11-14, 3 FBX đã xuất, bài học đuôi/xuất
metadata:
  type: project
---

Pet 23 Kitsune Nine-Mist (GEK-2367), thư mục `Ngoc\EndlessKicker\New_PET\Pet_23_Kitsune_Nine_Mist\`, script `work/infinite_defense/pets/kitsune_nine_mist/` (report.md, analysis.md, anim/). User "chốt" 2026-11-14: Idle (`..._idle.fv`, 49 key lặp) + Attack v6 (`..._attack_v6.fv`, 31 key, bắn F12, F30 = Idle F0); đã xuất 3 FBX (Base + Idle + Attack), CHOT.txt tạo, chưa chép vào Unity.

**Bài học**
- Đuôi cụp hẳn: KHÔNG xoay tay từng đuôi (v3/v4 lộn xộn, chồng chéo). Dùng `CTL_TailFan` (driven key lên group gốc từng đuôi) khép hẳn -1 thành MỘT bó, rồi hạ cả bó xuống sau lưng bằng xoay bù (`pitch_tails` trong anim/attack.py, ma trận conj Rz⁻¹·Rx·Rz theo xoay group). User muốn bó nằm xuôi ra sau hơi chúc xuống (~15° dưới ngang), tip không chạm đất (hover).
- Gốc đuôi dùng đường tâm = trọng tâm vòng cắt BFS (không chiếu thẳng/không geodesic: đuôi cuộn). Hai đuôi trong dính nhau ở gốc → chia đều trọng số đỉnh mối hàn.
- Khi gọi `exec` nhiều file trong cùng namespace, tên trùng (TAILS) đè nhau: chạy kit_common trong dict riêng.
- File Base xuất ra tên `Pet_<Tên>.fbx` TRÙNG file mesh gốc trong thư mục Pet → ghi đè mesh gốc: copy mesh gốc ra `raw/` trước khi chạy finalize.
- Đã sửa sau chốt (chưa áp vào rig .fv): driven key fan -1 khép 95%, trọng số mối hàn đuôi 2 (có trong Base FBX).
- Cổng Frolvy bị phiên khác chiếm / cửa sổ bị đóng giữa chừng (pet_frolvy_tidy): mở cổng riêng (9896...) và lưu file sớm.
