# Steam-Pug Turbo - phân tích lại Idle + Attack (chờ duyệt, chưa dựng)

GDD: Idle = "Mặt cau có thở phì phò, kim đồng hồ đo áp lực nhấp nháy đỏ". Attack = "Van áp suất mở toang xả hơi nước trắng xóa, phóng luồng đạn liên hoàn xé gió".
Rig có (26 joint): Root, Spine1, Head, Goggles, Gauge, Tail1/2, Valve, Exhaust (+Muzzle), Pipe L/R, Tank L/R, 4 chân x3. KHÔNG có hàm/mắt/mày/má.

## Điều anim làm được / không làm được
- Làm được bằng anim: nhịp thở (thân, ngực, đầu), cau có bằng TƯ THẾ (đầu cúi, ngước mắt nhìn xéo, kính thợ hàn tụt xuống), kim đồng hồ rung/vụt, van, ống xả giật, ống/bình rung, chân thả trễ, đuôi.
- Không làm được bằng anim (là VFX/material): đỏ nhấp nháy của kim, hơi nước trắng, đạn/bánh răng, nhăn mặt thật. Anim chỉ cho nhịp + frame để gắn event.

## Idle (lặp, 48F mặc định, f48 = f0)
| Pha | Frame | Làm gì | Lý do |
|---|---|---|---|
| Hít | 0-6 (x6 nhịp/vòng, mỗi nhịp 8F) | ngực/Spine1 phồng ra, đầu ngửa ~2°, kính nhích lên, kim đồng hồ nhích lên | phì phò = thở NHANH, ngắn |
| Thở ra phì | 6-8 | thân xẹp xuống nhanh hơn lúc hít, đầu chúi + giật nhẹ, ống xả hé (rx giật), van rung | thở ra là cú "phì"; đây là frame gắn event hơi nhỏ |
| Cau có (giữ suốt) | cả vòng | đầu cúi ~4°, quay nhìn xéo chậm 1 vòng/48F, kính tụt nhẹ | cau có không có mặt rig nên đọc bằng tư thế đầu |
| Kim đồng hồ | cả vòng | rung nhanh nhỏ + vụt lên mỗi lần thở ra; đỏ nhấp nháy theo cùng nhịp (VFX) | nhấp nháy bám nhịp thở cho dễ đọc |
| Lơ lửng | cả vòng | bồng bềnh 12 cm, 1 nhịp/vòng; chân, đuôi, ống, bình thả TRỄ sau thân | luật Pet bay |

## Attack (30F, f30 = Idle f0)
| Pha | Frame | Làm gì | Lý do |
|---|---|---|---|
| Gom hơi (anticipation) | 0-9 | hít sâu: thân phồng + ngửa, kính nhích lên, kim vụt hết cỡ, van/ống/bình rung tăng dần | báo trước cú bắn |
| Mở van | 9-12 | van quay mở toang (nhanh), ống xả giật hướng ra, thân bật lao | "mở toang" |
| **BẮN** | **12** | event bắn; thân lao ~12 cm theo hướng ngược miệng ống xả (phản lực), chân trải ra sau | "xé gió" |
| Xả liên hồi | 12-20 | rung liên tục (thân, ống, bình, van), kim giữ đỉnh; đây là đoạn "luồng đạn liên hoàn" | liên hoàn = RUNG LIÊN TỤC, 1 event bắt đầu + VFX lặp |
| Xẹp áp | 20-26 | van đóng, kim tụt, thân giật lại + nảy tắt dần, chân đuôi trễ | hồi lại |
| Về idle | 26-30 | đúng tư thế Idle f0 | nối clip |

## Chỗ bản đang có CHƯA đạt (cần sửa nếu duyệt)
1. Thở 4 nhịp/vòng hơi chậm cho "phì phò": đề xuất 6 nhịp/vòng và nhịp thở ra ngắn, gắt hơn nhịp hít.
2. Cau có: mới chỉ cúi đầu 4°. Đề xuất thêm kính tụt xuống và ngước nhìn xéo.
3. Kim đồng hồ chỉ rung ngẫu nhiên, chưa bám nhịp thở: đề xuất vụt lên đúng lúc thở ra.
4. Attack: pha gom hơi (f4-8) thân hạ + ngả khá nhiều, f9-10 đỉnh mesh nhảy 20 cm/frame; "xé gió" cần nhanh nhưng van "mở toang" chưa đủ thấy: tăng góc van và cho mở trước frame bắn 2-3F.
5. "Liên hoàn": bản đang có 1 cú giật lớn rồi tắt. Đề xuất giữ rung đều tới f20 (đang tắt dần từ f18).

## Câu hỏi cần quyết
1. **Hướng bắn.** Muzzle ở ống xả SAU LƯNG, nên đạn bay ra phía sau. Pet quay mặt (+Z) hướng nào so với địch trong game? Nếu địch ở phía mặt thì ống xả đang bắn ngược: cần xoay thân 180° khi bắn hoặc dời Muzzle. Mặc định làm phản lực đẩy thân ra phía mặt.
2. Idle 48F lặp có được không, hay muốn ngắn hơn (36F, 8 nhịp thở)?
