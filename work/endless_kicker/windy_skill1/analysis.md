# Windy Skill 1 "Wind Cyclone" — phân tích (nhánh C: GDD + rig Frolvy, chưa đo ref)

Nguồn: FDD "Hero: Windy" (Vũ Việt Tiến, 14/10/2026), mục 2a. Ref anim của GD: `drive.horusvn.com/s/5mL6G2nrJ39bRqP` — **chưa xem** (trình duyệt không mở được), nên mọi thời lượng dưới đây là [suy luận], cần đối chiếu ref.
Rig + số đo: lấy từ phân tích Attack (`work/endless_kicker/windy_attack/analysis.md`, mục C).
Nhãn: [GDD] · [rig] · [suy luận] · [?] cần hỏi.

## A. FDD nói gì

| # | Câu gốc | Hệ quả |
|---|---|---|
| 1 | [GDD] Windy tung một cơn lốc nhỏ bay thẳng, xuyên enemy, gây damage và hất tung 1 giây | Đòn "ném / phóng" có một **frame phóng** rõ; game sinh lốc ở frame này |
| 2 | [GDD] Tự kích hoạt khi hết hồi (12 s) và có enemy trong tầm | Chạy xen giữa các đòn Attack: vào và ra **đúng Idle F0** |
| 3 | [GDD] Hướng bay khóa theo mục tiêu lúc cast, không bám | Lúc phóng trượng phải chĩa **thẳng trước** (+Z), như Attack |
| 4 | [GDD] Animation: "đưa cả trượng ra trước, rồi trượng xoay tròn" | Hai pha: (1) đẩy cả trượng ra trước, (2) trượng xoay tròn |
| 5 | [GDD] VFX là cơn lốc bay thẳng | Anim không cần chừa chỗ VFX tích tụ |
| 6 | [GDD] Hero đứng cố định ở tâm | Không root motion, chân không rời chỗ |

## B. Khác Attack ở đâu

Attack: đầu trượng chĩa ra trước, một cú vung nhanh 24F. Skill 1 phải **lớn và đọc rõ hơn** vì là kỹ năng hồi 12 s: đẩy cả trượng ra xa hơn, thêm vòng xoay trượng, người ngả theo. Camera game từ trên chéo xuống, hero chỉ ~60–70 px nên chỉ hình lớn đọc được: **đường trượng, vòng xoay, độ ngả người, vải**.

## C. Thiết kế đề xuất

**Độ dài 36F @ 30 fps (1,2 s), phóng F24** (số đã chốt trong dự án). Vào/ra đúng Idle F0.

| F | Pha | Thân / chân | Tay + trượng | Vải |
|---|---|---|---|---|
| 0 | Idle F0 | Như Idle | Trượng chéo 45° như Idle | Như Idle |
| 0→8 | Lấy đà (8F) | Ngực ưỡn, ngả sau ~8°, trọng tâm về chân trái, đầu ngửa nhẹ | Kéo trượng về sau-bên phải, đuôi nhấc khỏi đất (cao ≥ 0) | Chùng, hất ra sau |
| 8→16 | Đẩy ra trước (8F) | Đổ người trước 15°, hông hạ 4–5 cm, trọng tâm chân phải | Cả trượng đẩy ra trước, đầu trượng chĩa +Z | Quật về trước, trễ 2–3F mỗi đốt |
| 16→24 | Xoay trượng (8F) | Giữ thế, vai xoay theo | Trượng quay tròn trong **mặt phẳng dọc bên phải** (đã duyệt: Skill1 xoay trong mặt phẳng dọc bên phải), tăng tốc dần | Bay theo vòng xoay |
| **24** | **PHÓNG** | Hông thấp nhất, thân nghiêng trước, đầu nhìn mục tiêu | Trượng dừng/chĩa thẳng +Z, đầu trượng = điểm sinh lốc | Quật mạnh nhất |
| 24→28 | Theo đà (4F) | Nảy lên 2 cm rồi lắng | Đầu trượng nảy ~5° rồi lắng | Lắng |
| 28→36 | Về (8F) | Đứng lên, trọng tâm về giữa | Trượng hạ về chéo 45°, đuôi ngoài chân phải không cắm đất | Về pha Idle |
| 36 | = Idle F0 | | | |

Phân bổ: 8 lấy đà · 8 đẩy · 8 xoay · 4 theo đà · 8 về.
Chân không bước (bài học Ninja: tấn rộng thành ngồi xổm). Tay trái giang ra cân bằng, không cầm trượng (cầm một tay, trượng 2,15 m xoay một tay vẫn đọc được ở cỡ 60 px).

**Ràng buộc từ rig [rig]:** vai→cổ tay ≤ 0,42 m; cán trượng cách đầu/mũ ≥ 10 cm; đuôi trượng không xuyên eo/mông phải, không xuyên vạt sau và áo choàng; vòng xoay trượng phải mở ra ngoài khối đầu to mới đọc được từ trên cao.

**Điểm phóng cho dev:** F24 (tỉ lệ 0,667), vị trí `DEF_WeaponEnd_R`, hướng +Z. Hướng bay do code quyết định.

## D. Cần hỏi [?]

1. Xem ref GD (link trên) rồi đối chiếu: ref xoay trượng **trước** hay **sau** khi phóng? Thứ tự trên là suy luận.
2. Xoay mấy vòng: 1 vòng (đề xuất) hay 2?
3. Mặt phẳng xoay: dọc bên phải (đã duyệt ở bản phân tích cũ) hay ngang?
4. 36F có khớp ý GD không, hay cần ngắn hơn?
