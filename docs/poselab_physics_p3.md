# Pose Lab: vật lý giai đoạn 3 (trọng tâm và cân bằng)

Đã duyệt 2026-10-25 ("theo đề xuất của bạn": có nút Đưa trọng tâm vào chân, vũ khí 15 %, ngưỡng 5 cm / 3 frame). Giai đoạn trước: `docs/poselab_physics_p1.md` (lò xo), `docs/poselab_physics_p2.md` (va chạm thân).

## 1. Mục tiêu

Cho người làm anim thấy nhân vật có đứng vững không, và báo những chỗ mà một nhân vật nặng như Gaygor sẽ ngã thật.

- **Thấy trên model:**
  - vùng đỡ trên sàn: bàn chân đang chạm đất, cộng vũ khí đang chống xuống đất;
  - điểm trọng tâm chiếu xuống sàn;
  - "điểm bắt" (capture point): nơi cần đặt chân để không ngã, tính từ trọng tâm và vận tốc của nó.
- **Báo mất cân bằng**, có xét bước chân: trọng tâm ra ngoài vùng đỡ không phải lỗi nếu có bước chân kịp đỡ.
- **Báo lơ lửng:** khi cả hai chân và vũ khí đều rời đất, trọng tâm phải rơi theo trọng lực.

**Ngoài giai đoạn 3:** gợi ý phản ứng trúng đòn; mô phỏng ngã (ragdoll); tự sửa toàn clip.

**Gói ngã/chết (gói riêng, làm sau giai đoạn 3; user 2026-10-25 "làm thành gói riêng"):**
- Sàn cho mọi khúc thân: lưng, vai, đầu, tay khi nằm không lún sàn, cả khi báo lỗi lẫn trong lớp vật lý. Dùng lại hình con nhộng và cách chạm không nảy.
- Đường "đổ theo vật lý" (người đổ quanh mép bàn chân như khúc gỗ, chừng 24–30 frame với Gaygor) vẽ cạnh đường trọng tâm thật để so timing.
- Cú đập xuống sàn rồi lắng: nối lò xo của giai đoạn 1 với điểm chạm sàn.
Giai đoạn 3 đã lo phần lúc bắt đầu ngã (điểm bắt) và tốc độ rơi (mục "lơ lửng").

## 2. Đo thử trước khi thiết kế (2026-10-25)

Trọng tâm tính từ thể tích các lõi con nhộng của giai đoạn 2. Vùng đỡ là bao lồi các điểm bề mặt bàn chân sát sàn.

| Clip | Frame trọng tâm ra ngoài vùng đỡ | Soi lại thì là |
|---|---|---|
| Hit polish_v7 | F7 (39 cm), F20 (33 cm) | Lúc nhấc chân bước lùi, rồi bước về. Bước đó chính là để giữ thăng bằng, hợp lý |
| Walk | F1–F9, F24–F40 (tới 15 cm) | Pha đứng một chân khi đi, bình thường |
| Attack 50 polish_v3 | F33–F49 (10 cm) | Chùy đang chống xuống đất. Tính chùy vào vùng đỡ thì hết |
| Attack | F9, F58 (34–47 cm) | Chân trái nhích lên 3–4 cm đúng một frame. Ngưỡng "chạm đất" 3 cm quá chặt |
| Attack | F28–F32 | Chân phải đang bước, đặt xuống ở F32. Bước kịp |

**Kết luận:**
- Clip đã duyệt không có chỗ nào thật sự mất thăng bằng.
- Phép "trọng tâm trong vùng chân" đơn thuần báo sai ở mọi bước chân. Phải xét theo **bước**, tính **vũ khí chống đất** vào vùng đỡ, và ngưỡng chạm đất khoảng 5 cm.
- **Vũ khí nặng làm lệch trọng tâm:** thêm chùy vào thì trọng tâm Gaygor cao lên 20–35 cm và dịch về phía chùy. Độ nặng của vũ khí phải là một thông số.

## 3. Cách tính

- **Khối lượng:**
  - mỗi khúc thân tỉ lệ với thể tích lõi con nhộng (đã có từ giai đoạn 2);
  - vũ khí có thanh **"Độ nặng vũ khí"**, tính theo % khối lượng cơ thể. Mặc định cho Gaygor: 15 %, chỉnh được.
- **Vùng đỡ:**
  - bao lồi của các điểm bề mặt bàn chân và vũ khí cách sàn dưới 5 cm;
  - dải chạm đất do người dùng tô (đã có trên trang) được ưu tiên hơn cách đo tự động.
- **Điểm bắt** = trọng tâm + vận tốc ngang / ω, với ω = √(g / chiều cao trọng tâm), g = 9,81 m/s².
- **Mất cân bằng:** một đoạn liên tiếp mà điểm bắt nằm ngoài vùng đỡ quá ngưỡng thì xét cuối đoạn:
  - cuối đoạn có chân (hoặc vũ khí) đặt xuống, và vùng đỡ mới chứa được trọng tâm: **bước kịp**, không báo;
  - không có gì đặt xuống mà đoạn dài hơn 3 frame: báo **"nghiêng quá, cần bước hoặc chống"**;
  - có đặt xuống mà vẫn không đỡ được trọng tâm: báo **"bước hụt"**.
- **Lơ lửng:** trong các frame không có gì chạm đất, gia tốc rơi của trọng tâm phải gần −g. Lệch quá 30 % thì báo "bay chậm / rơi nhanh bất thường".

## 4. Trên trang

- **Hình trên sàn:** vùng đỡ (đa giác mờ), chấm trọng tâm, mũi tên tới điểm bắt.
  - Xanh: đứng vững.
  - Vàng: ra ngoài nhưng đang bước kịp.
  - Đỏ: lỗi.
- **Dải "cân bằng"** trên timeline, màu cam, và danh sách lỗi; bấm vào là nhảy tới frame.
- **Thanh "Độ nặng vũ khí"** và nút bật/tắt hiển thị, đặt trong thẻ Vật lý.
- **Đưa trọng tâm vào chân** (cho frame đang xem, xem mục 7): dời hông ngang, hai bàn chân khóa trên sàn, cho tới khi trọng tâm vào vùng đỡ, rồi đặt key.
- **Python và QA của AI:** cùng phép tính trong `tools/physics_sim.py`, thêm mục "cân bằng" vào QA.

## 5. Nghiệm thu

- **Không báo sai** trên Hit polish_v7, Attack 50 polish_v3 và Walk: các bước chân và chùy chống đất ở bảng mục 2 không bị báo.
- **Báo đúng:**
  - cố ý dời hông của một frame đứng hai chân ra ngoài 40 cm, giữ 5 frame: phải báo "nghiêng quá";
  - xóa bước chân lùi của Hit (chân trái không nhấc): phải báo ở F3–F8.
- **"Đưa trọng tâm vào chân"** ở frame bị báo: sau khi bấm, frame đó hết báo, bàn chân không trượt.
- **Tốc độ:** quét cả clip dưới 0,1 giây.
- **Python và trang:** cùng kết quả.

## 6. Ước lượng

- Tính trọng tâm, vùng đỡ, điểm bắt, quy tắc bước; soi tận mắt: 1 buổi.
- Hiển thị trên sàn, dải, danh sách, thanh độ nặng: nửa buổi.
- "Đưa trọng tâm vào chân", bản Python, nghiệm thu: nửa buổi đến 1 buổi.

## 7. Cần bạn quyết

1. **Nút "Đưa trọng tâm vào chân"** (chỉ cho frame đang xem, do người bấm): làm trong giai đoạn này không? Đề xuất: **có**, vì sửa cân bằng đơn giản và ít đụng tới chất diễn hơn sửa xuyên.
2. **Độ nặng vũ khí mặc định của Gaygor:** đề xuất **15 % khối lượng cơ thể**. Bạn có số liệu từ thiết kế game thì dùng số đó.
3. **Ngưỡng báo:** điểm bắt ra ngoài vùng đỡ quá **5 cm** và kéo dài quá **3 frame** khi không có bước. Đề xuất giữ như vậy.

## 8. Đã làm (2026-10-25)

- **Code:**
  - `work/pose_lab/index.html`: phần "balance" (`balFrame`, `balAnalyse`, `hull2`, `polyMargin`, chạy chung lượt quét với va chạm thân) và phần "balance panel" (hình trên sàn, dải cam, danh sách, thanh "Vũ khí nặng", nút "Đưa trọng tâm vào chân");
  - Python: `balance()` trong `tools/physics_sim.py`, chạy bằng `--balance`.
- **Khác thiết kế, do đo được khi làm:**
  - **Đoạn ngắt ở mỗi lần đặt chân xuống:** bản đầu gộp một bước thật (Hit F20–F21) với đoạn ngả người liền sau thành một đoạn, và cả đoạn bị coi là "bước kịp".
  - **Tách lỗi "nghiêng quá"** (chính trọng tâm ra ngoài chân) khỏi **"đà quá mạnh"** (chỉ điểm bắt ra ngoài, do trọng tâm chạy nhanh).
  - **Lỗi "nghiêng quá" nhảy tới frame trọng tâm lệch nhất**, vì nút sửa sửa đúng vị trí đó.
- **Nghiệm thu:**
  - **Không báo sai:**
    - Hit polish_v7: không lỗi; F1–F3, F20 là bước kịp.
    - Walk đo bằng độ cao bàn chân: không lỗi.
    - Attack: chỗ chùy chống đất F33–F48 không bị báo.
  - **Cần người quyết, Attack F49–F53:** báo "nghiêng quá". Người ngả ra sau gồng kéo chùy lên; ở mức chùy nặng 15 %, trọng tâm ra ngoài chân 13 cm; trọng tâm cả người lẫn chùy chạy ngang tới 4–6 m/s.
  - **Walk trong bản xem thử trên máy:** dải chạm đất tô sai (trống ở F37–F41, nên báo "rời đất"). Trang báo đúng là dải sai, không phải anim sai.
  - **Báo đúng:** ngả người và lùi hông ở Hit F22–F31 (trọng tâm ra ngoài chân 7–8 cm) bị báo "nghiêng quá F22–F32".
  - **Không báo (đúng):**
    - dời hông sang ngang 40 cm: hai chân Gaygor dang rộng 76 cm, vẫn đỡ được;
    - bỏ bước lùi của Hit: hai chân đứng rộng vẫn đỡ được cú giật, nên bước lùi là chất diễn chứ không bắt buộc.
  - **Nút "Đưa trọng tâm vào chân"** ở F26: trọng tâm từ ngoài 8 cm thành trong 5 cm (dời hông 14 cm), bàn chân trượt 0 cm.
  - **Tốc độ:** quét cả clip (va chạm thân + cân bằng) 48–68 ms.
  - **Python và trang:** lệch 0,000 cm, trạng thái từng frame trùng hết, cùng danh sách lỗi.
