# Director log – windy_idle_pose (Windy_Idle.fv, pose idle tĩnh)

## Director – Windy Idle (Windy_Idle.fv, frame đầu) – mốc p0 / key pose – 2026-11-05
**Kết luận: Cần sửa** (không Chặn: hướng dáng ổn, đúng quyết định người dùng)
Ý chính: pháp sư chibi thủ thế, trượng chéo trước thân, chân phải trước. Thái độ "sẵn sàng" đọc được, hợp chuyển sang Attack. Dáng nhìn đẹp, nhưng vì trượng dài cầm một tay nên cần kiểm 3 thứ: mũi trượng sát đất, tay phải chịu cả đòn bẩy đầu trượng, hai vạt sau bay ngang. Trọng tâm đang chia đều nên dáng hơi "đứng tấn chết".

### Lỗi (nặng → nhẹ)
| # | Mức | Frame | Bộ phận | Lỗi | Nguyên lý | Cách sửa gợi ý | Nguồn |
|---|---|---|---|---|---|---|---|
| 1 | A (chờ đo) | F đầu | mũi nhọn trượng | Nếu trượng dài 2,15 m, cầm cách đuôi 1,13 m (analysis endless_kicker), ngoại suy trục cổ tay→WeaponEnd thì mũi nhọn ở khoảng (-0,98; ~0,0; -0,10): sát hoặc ngập sàn, cách bàn chân phải ~0,8 m. Ảnh front: mũi ngang tầm bàn chân. | Prop/contact | Đo world joint mũi/đuôi trượng. Nếu < 5 cm thì hạ góc chéo: CTL_Weapon_R trượt trượng ra phía đầu (tx âm vài cm) hoặc nâng IK tay phải 3–5 cm / xoay cổ tay để trượng dốc hơn (đầu trượng lên, mũi lên). | [đo] ngoại suy, cần xác nhận |
| 2 | B | F đầu | tay phải + trượng | Đầu trượng (quả cầu + trăng, phần nặng) ra ngoài 0,89 m theo phương ngang, cao hơn tay 0,80 m, chỉ một bàn tay ở hông đỡ → về vật lý cổ tay phải gồng rất nặng, trông "đỡ không nổi" nếu nhìn kỹ. Analysis đã ghi nhược điểm này cho PA C. | Weight / Solid drawing | Giữ ý chéo của người dùng, chọn 1 trong 2: (a) kéo đầu trượng về gần vai trái (giảm z của đầu từ 0,58 xuống ~0,3, tức trượng dựng đứng hơn, tựa sát vai), (b) tay trái nắm hờ thân trượng dưới đầu (thủ thế 2 tay). Đưa 2 ảnh tĩnh để người dùng chọn. | [đo] 0,89 m / 0,80 m |
| 3 | B | F đầu | hai vạt BackFlap | Vạt chìa ngang ra sau gần nằm ngang (~0,5–0,6 m sau lưng) trong khi thân đứng yên: đọc như đang chạy trong gió. Câu hỏi GD #3 (bay ngang hay rủ) vẫn chưa có trả lời; v2/v3 trước đó đã cho rủ chữ S. | Overlap / Gravity | Hỏi người dùng. Nếu rủ: BackFlap1 rx hạ ~25–30° và xoè ra ngoài, Flap2–4 cong nhẹ; ngọn cách đất ≥ 0,3 m. Nếu giữ bay ngang: hạ gốc 10° để có độ võng, sẽ dễ loop gợn sóng hơn. | [mắt] side/top |
| 4 | B | F đầu | hông / trọng tâm | Root tx ≈ 0, rz = 0, hông ngang, vai ngang: trọng tâm chia đều hai chân, không có chân trụ nên thiếu contrapposto. Tay phải và chân phải cùng ra trước (cùng bên), ngực chỉ xoay ngược ~17° so với hông 23,6°. | Contrapposto / Line of action | Dồn trọng tâm về chân sau (trái): Root tx +2–3 cm, Root rz 2–3° (hông trái cao), IKChest rz ngược 2–3°. Gối trái thẳng hơn, gối phải chùng thêm. KHÔNG hạ hông (luật user idle). | [đo] Root x 0,004 so với trung điểm 2 cổ chân -0,012 |
| 5 | B | F đầu | silhouette cam game | Ở camera2 (rx -35), quả cầu đầu trượng chồng lên vai và tay trái thành một khối, mất khoảng trống âm bên trái người. Ảnh cam game chỉ ~60 px người nên chưa chấm kỹ được. | Staging / Silhouette | Tay trái đưa ra sau / ra ngoài thêm (FK vai trái xoay ra sau ~10°) hoặc đầu trượng cao hơn/xa hơn ra ngoài. Render cam game ≥ 512 px để xác nhận. | [mắt] |
| 6 | C | F đầu | bàn tay phải | Curl 0,65 trên trượng chéo: không thấy được găng có ôm kín thân trượng không, hay cổ tay có bị gập > 25° khi trượng chéo lên trái. | Solid drawing | Ảnh cận tay phải 3 góc. Cổ tay gập > 25° thì xoay cẳng tay (IK tay R rx/rz) thay vì gập cổ tay. | thiếu ảnh |
| 7 | C | F đầu | bàn chân trái | Cổ chân trái cao hơn phải 6 mm, Ankle_L ry 25 (mũi chân xoay ra ngoài nhiều). Kiểm gót có hở sàn không. | Contact | Đo đáy gót/mũi so sàn y = 0. | [đo] 6 mm |
| 8 | C | — | quy ước frame | File để range 0–40; quy ước Studio F1 = frame đầu. Loop 40 F cần F cuối = F đầu. | — | Chốt quy ước trước khi key. | — |

### Giữ nguyên
- Chia góc xoay dọc chuỗi: hông 23,6 → ngực -10,4 / IKChest -7 → cổ -5 → đầu -5,6, mặt gần nhìn thẳng (đúng luật "xoay từ hông, không robot").
- Gối chùng nhẹ (hông→cổ chân 93–94% chiều dài chân), hai bàn chân phẳng; tấn trước–sau rõ ở góc side.
- Thân hơi đổ về trước (~10°), đầu ra trước 5 cm: có thái độ chủ động.
- Trượng chéo là đường hành động mạnh nhất, đọc rõ ở cam game và gần với tư thế đầu của Attack.
- Tay trái nắm đấm, buông và lùi ra sau (z -0,075), khuỷu không duỗi thẳng.

### Định hướng vòng sau
- Đo mũi trượng trước tiên (#1). Rồi đưa người dùng 2 ảnh: trượng tựa vai một tay và trượng thủ thế hai tay (#2), cùng câu hỏi vạt rủ hay bay (#3).
- Khi làm loop: trượng dài ~1,2 m tính từ tay, nên cổ tay xoay 1° là đầu trượng di chuyển ~2 cm. Khoá trượng theo tay, thở chỉ ở ngực/vai ≤ 1 cm, cho đầu trượng trễ 2–3 F. Hai vạt bay ngang sẽ phải gợn liên tục mới không trông như bị đóng băng.
