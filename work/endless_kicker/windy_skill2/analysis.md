# Windy Skill 2 "Hunting Tornado" — phân tích lại (GDD + ref, nhánh C)

Nguồn: FDD Hero Windy (Vũ Việt Tiến, 14/10/2026) mục 2b + ref anim của GD (`ref/anim_sheet_all.png`, `ref/cycle_even.png`: 24 khung chia đều một chu kỳ; video `ref/anim_ref.mp4`, chưa đo thời lượng thật vì máy Linux thiếu ffprobe).
Nhãn: [GDD] · [ref] · [rig] · [suy luận] · [?] cần hỏi. Số liệu độ dài/mốc lấy từ bản đã duyệt 2026-11-04 (45F @30fps, triệu hồi F31), chưa duyệt lại.

## A. GDD nói gì → hệ quả cho anim

| # | Câu gốc | Hệ quả |
|---|---|---|
| 1 | [GDD] Triệu hồi một cơn lốc tồn tại 6 s, tự truy đuổi mục tiêu | Anim chỉ là **cú triệu hồi**; lốc sống riêng sau đó. Ra khỏi anim phải về đúng Idle |
| 2 | [GDD] Lốc xuất hiện **tại vị trí mục tiêu**, không phải tại tay | Không cần đầu trượng chĩa thẳng như Skill 1. Cần một khoảnh khắc **"ra lệnh"** đọc rõ (điểm sinh = F31) |
| 3 | [GDD] Tự kích hoạt khi hết hồi 15 s, có enemy trong tầm | Chạy xen giữa Attack: vào/ra **đúng Idle F0** |
| 4 | [GDD] Animation: "Windy bay nhẹ lên, cầm trượng quay một vòng" | Hai việc: (1) **bay nhẹ lên**, (2) **quay một vòng** cùng trượng |
| 5 | [GDD] Hero đứng cố định ở tâm | Không root motion; bay lên chỉ theo trục đứng, rồi hạ về đúng chỗ |

## B. Ref cho thấy gì (24 khung của một chu kỳ) [ref]

Ref là nhân vật khác (tóc lửa, trượng có lưỡi), chỉ học **nhịp và hình dáng**, không chép.

| Khung ref | Thấy gì | Vai trò |
|---|---|---|
| 1–6 | Đứng, trượng dựng thẳng bên phải, gần như đứng yên | Giữ idle (~25% chu kỳ) |
| 7–8 | Ngả người, trượng bắt đầu hạ, tóc/vải hất | Lấy đà |
| 9–10 | Chùng sâu, trượng quét thấp ra sau, đầu trượng gần chạm đất, thân bắt đầu xoay | Đáy lấy đà |
| 11–13 | Thân xoay hết nửa sau (quay lưng), trượng quét vòng thấp sang phải | Quay một vòng, trượng như bánh lái |
| 14–15 | Bật lên, trôi lơ lửng, trượng dựng thẳng đứng phía trước hướng xuống, tóc/vải bay ngược lên | **Bay nhẹ lên** = đỉnh, đọc rõ nhất |
| 16–17 | Chạm đất, trượng nghiêng, vải còn bay | Hạ |
| 18–21 | Lắng dần về đứng, trượng dựng thẳng | Về idle |
| 22–24 | Đứng, rồi bắt đầu vòng kế tiếp | Chu kỳ lặp |

Điểm mấu chốt: **quay xảy ra trước, bay lên sau** (quay → bật → lơ lửng → hạ). Trượng luôn là thứ vẽ ra vòng cung lớn; vải/tóc trễ nhịp so với thân.

## C. Thiết kế đề xuất [suy luận]

**45F @30fps (1,5 s), triệu hồi F31 (0,69).** Vào/ra đúng Idle F0.

| F | Pha | Thân / chân | Tay + trượng | Vải |
|---|---|---|---|---|
| 0 | Idle F0 | Như Idle | Trượng chéo như Idle | Như Idle |
| 0→8 | Lấy đà (8F) | Chùng gối, hông hạ 6–8 cm, ngả người, vặn thân sang trái | Trượng kéo thấp ra sau-trái, đuôi gần đất (không cắm) | Hất ngược theo hướng vặn |
| 8→20 | Quay một vòng (12F) | Thân xoay 360° quanh trục đứng (bắt đầu chậm, nhanh nhất ở giữa), chân giữ chỗ, trọng tâm dần dâng | Trượng quét vòng thấp quanh người, tay trái giang cân bằng | Quật theo vòng, trễ 2–3F mỗi đốt |
| 20→27 | Bật lên (7F) | Hết vòng quay thì bật, người dâng 15–20 cm, gối co | Trượng thu về dựng đứng trước người, đầu hướng lên | Bay ngược lên |
| 27→31 | Lơ lửng + ra lệnh (4F) | Đỉnh, người thẳng, đầu nhìn mục tiêu | Trượng chúc xuống, mũi chỉ ra trước-xuống = **điểm triệu hồi F31** | Bay lên mạnh nhất |
| 31→38 | Hạ (7F) | Hạ về đất, nhún gối 3–4 cm khi chạm | Trượng hạ, nảy nhẹ | Rơi theo, quật xuống |
| 38→45 | Về (7F) | Đứng lên, trọng tâm về giữa | Trượng về chéo như Idle | Về pha Idle |
| 45 | = Idle F0 | | | |

Phân bổ: 8 lấy đà · 12 quay · 7 bật · 4 lơ lửng · 7 hạ · 7 về.

**Ràng buộc từ rig [rig]:** vai→cổ tay ≤ 0,42 m; trượng 2,15 m không xuyên người, vạt sau, áo choàng khi quét vòng thấp; đuôi trượng không cắm đất; chân không bước, chỉ xoay tại chỗ (kiểm trượt chân khi quay).

**Đọc từ camera game (trên chéo xuống, hero ~60–70 px) [suy luận]:** vòng quay đọc tốt (tóc, trượng vẽ vòng); **bay lên đọc yếu** từ trên xuống → phóng đại bằng trượng dựng đứng, vải/tóc bay ngược lên, nhún gối rõ khi bật và khi hạ; dev có thể thêm bóng/VFX gió dưới chân.

**Điểm sinh cho dev:** F31 (tỉ lệ 0,689). Lốc sinh tại vị trí mục tiêu, không phụ thuộc vị trí trượng.

## D. Cần hỏi [?]

1. "Quay một vòng" = **cả thân quay 360° cùng trượng** (như ref, đề xuất) hay chỉ trượng xoay trên tay, thân đứng?
2. Quay **trước** rồi bay (như ref, đề xuất) hay vừa quay vừa bay lên?
3. Có cần **loop phần lơ lửng** để khớp 6 s của lốc, hay chỉ một cú triệu hồi 1,5 s rồi về Idle (đề xuất)?
4. Độ cao bay 15–20 cm đã đủ "bay nhẹ" chưa, hay muốn cao hơn?
