# Ninja Idle — bản thiết kế (quy trình C, bước C2) — **ĐÃ DUYỆT 2026-10-28** (user: "Duyệt, K1"; cầm kunai K1, nhân vật quay mặt lên trên màn hình)

Nhãn nguồn: [GDD] trích FDD v1.1 · [user] lời người dùng 2026-10-28 · [rig] đo trên rig · [thiết kế] AI đề xuất · [?] cần chốt.

## A. Tổng quan
- [user] 40F @ 30 fps (1,33 s), loop, một nhịp thở, tại chỗ, không root motion. Không xoay kunai.
- [GDD] "đứng thủ thế hơi khom người … Khăn quàng bay nhẹ theo nhịp thở … loop liền mạch."
- [user] Camera game chéo từ trên (3/4) → dáng phải đọc được từ trên: hai tay tách khỏi thân, kunai không nằm sau đầu.
- [thiết kế] Giọng nhân vật: sát thủ nhanh, nhẹ, luôn sẵn sàng (FDD: "nhanh, linh hoạt, áp đảo"). Nhịp thở ngắn, gọn,
  biên độ nhỏ ở thân, phần "sống" nằm ở khăn bay.

## B. Đặc điểm rig
- [rig] Chibi cao 185 cm: đầu 47 cm (1/4 chiều cao), chân 64 cm, hông→cổ 55 cm. Vai rộng 40 cm, hông rộng 20 cm.
- [rig] Tay ngắn: cánh tay 23 + cẳng tay 20 + bàn tay 25 cm (găng: ngón cái + khối 4 ngón).
- [rig] **Kunai dài 75 cm, lưỡi 57 cm** (dài hơn cả cánh tay). Gắn cứng vào `Weapon` dưới `Wrist_L`.
- [rig] Khăn: cổ khăn đi theo ngực; 2 đuôi dài 140 cm, mỗi đuôi 5 xương `Scarf1–4, End` (gốc ở ngực).

## C. Pose chính (tư thế thủ thế, = F1)
| Bộ phận | Thiết kế | Nguồn |
|---|---|---|
| Chân | Tấn rộng hơn hông (bàn chân cách ~35 cm), **chân trái lên trước ~12 cm**, mũi chân trái chỉ hướng địch, chân phải xoay ra ~30°. Gối gập vừa. | [thiết kế] tay cầm vũ khí ở trước |
| Hông | Hạ ~8 cm (khom), xoay ~20° sang phải (vai trái hướng địch). | [GDD] "hơi khom" |
| Thân | Đổ về trước ~12° từ hông, cột sống cong đều (mỗi đốt ≤ 10°). Ngực xoay ngược lại ~8° để mở ra camera. | [GDD] + CORE#lean-from-hip |
| Đầu | Nhìn thẳng hướng địch; cằm hơi cúi ~5° (ánh mắt từ dưới vành mũ). | [thiết kế] |
| Tay trái + kunai | Nắm ngược kunai **trước ngực**: nắm tay cao ngang ngực, cách ngực ~20 cm. Lưỡi chạy dọc cẳng tay ra sau, chéo xuống ~30°. Mũi lưỡi lệch ra ngoài thân để không xuyên vai hay đùi. | [GDD] "cầm ngược kunai trước ngực" · [rig] lưỡi 57 cm |
| Tay phải (tay không) | Nắm hờ như cầm một kunai vô hình, **đẩy về sau**: khuỷu sau lưng ~15 cm, bàn tay ngang hông sau, cách hông ~25 cm. Cổ tay gập nhẹ, các ngón cong 40–60°. | [user] |
| Khăn | Đuôi khăn rủ ra sau, hơi chúc xuống ~15° (mesh gốc nằm ngang) và tách nhẹ hai bên (±10°). | [thiết kế] |

Phương án cầm kunai cho bạn chọn nếu muốn đổi [?]:
- **K1 (đề xuất):** lưỡi ra sau dọc cẳng tay, chéo xuống. Từ trên nhìn thấy rõ một vạch chéo dài.
- **K2:** lưỡi chĩa thẳng xuống. Gọn hơn nhưng mũi tới ngang gối (nắm tay ở y≈110, lưỡi 57 cm) và dễ xuyên đùi.
- **K3:** lưỡi chĩa ra trước (cầm xuôi). Trái với FDD ("cầm ngược").

## D. Nhịp thở và bảng timing (40F)
Đường cong chung dạng sine: **hít F1→F17 (16F), thở ra F17→F41 (24F)**, thở ra dài hơn (40/60). F1 = đáy, cũng là điểm nối loop.

| Key | Frame | Tầng | Nội dung |
|---|---|---|---|
| P1 | F1 (= F41) | 10% | Đáy thở ra: tư thế thủ thế ở mục C, ngực gù nhẹ, vai thấp. |
| P2 | F17 | 10% | Đỉnh hít: ngực nâng + ưỡn ~2,5°, vai nhô 1,5 cm, hông nhấc 0,8 cm (gối duỗi bớt), đầu bù ~-2° để vẫn nhìn thẳng. |
| B1 | F9 | 25% | Giữa lúc hít: thân và hông theo đường cong; tay và kunai còn trễ. |
| B2 | F29 | 25% | Giữa lúc thở ra: thân đã xuống; tay, khăn còn ở trên. |
| (50%) | F5, F13, F23, F35 | 50% | Breakdown theo độ trễ ở mục E. |

Biên độ [thiết kế] nhỏ vì nhân vật nhẹ và nhanh: hông lên xuống 0,8 cm; Spine1 ±1°, ngực ±2,5°, cổ ±0,5°; vai 1,5 cm.
Tay trái nâng theo ngực 1 cm, lưỡi kunai nghiêng thêm ~3°. Tay phải nhấc 1 cm và đưa ra sau thêm 1 cm.

## E. Overlap (độ trễ so với hông, frame)
hông 0 · Spine1 +1 · ngực +2 · cổ/bả vai +3 · đầu +4 · vai +3 · khuỷu +4 · cổ tay/kunai +5 · ngón +6 (theo công thức idle
đã duyệt, rút ngắn tỉ lệ 40/60) → `idle.md#breath-recipe`.

## F. Chuyển động phụ: khăn (phần "sống" chính của Idle)
- [GDD] "Khăn quàng bay nhẹ theo nhịp thở."
- [thiết kế] Mỗi đuôi khăn là một sóng truyền từ gốc ra đuôi: `Scarf1` trễ +3F so với ngực, mỗi xương sau trễ thêm 2F
  (End +11F). Biên độ tăng dần ra đuôi: lên/xuống 4° → 12°, lắc ngang 2° → 6°.
- Gió nhẹ: thêm một sóng chu kỳ 20F (2 lần mỗi loop, để loop khép kín). Đuôi trái và phải lệch pha nhau 5F để không đập
  cùng lúc. Đuôi khăn không chạm đất và không xuyên chân (đáy khăn ở y ≈ 100 cm, cao hơn hông).
- Cổ khăn đi cứng theo ngực.

## G. Sự kiện game
Không có. Clip loop; Attack và các skill sau sẽ bắt đầu và kết thúc ở F1 của Idle này.

## H. Kiểm trước khi gửi
- Chân cắm đất (trượt 0), F41 = F1.
- Kunai không xuyên thân, đùi, đầu ở mọi frame. Tay phải không xuyên mông, hông.
- Đọc ở camera 3/4 từ trên: hai tay tách khỏi thân, thấy rõ vạch kunai.
- Khớp trong giới hạn; skin vai và hông không giãn quá bind (rig còn giãn ở góc lớn, nên giữ tay dưới ~60°).

## Câu hỏi còn mở
- [?] Hướng địch trong game: nhân vật đứng quay mặt về phía nào so với camera (địch đến từ trên màn hình xuống)? Mặc định:
  nhân vật quay mặt về phía trên màn hình, camera thấy lưng chéo 3/4. Nếu camera thấy mặt thì pose phải mở ra camera hơn.
- [?] Cầm kunai: K1 / K2 / K3 (mục C).


## I. Ảnh key pose (giai đoạn 0, G4) — chốt 2026-10-28
- User: "cái pose idle đang xấu quá … nhờ Codex ren cho cái ảnh concept key pose idle" → `keys/k1_v1.png`, vẽ lại 2 lượt → **chốt `keys/k1r2_v1.png`** (user: "Chốt k1r2_v1").
- Ref = render model thật (`tools/render_fbx_tex.py`, `keys/ref/`), prompt `keys/k1_prompt.txt`, `k1r_prompt.txt`, `k1r2_prompt.txt`.
- So với thiết kế mục C: tấn sâu và rộng hơn, thân thẳng hơn, nắm tay kunai sát ngực trên (dưới khăn), khuỷu trái mở ra ngoài-xuống; tay phải nắm bên hông (ảnh chưa lùi hẳn ra sau như yêu cầu).
