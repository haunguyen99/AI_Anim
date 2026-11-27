# Disintegrate — tan biến (dính đòn rồi tan thành cát bụi, kiểu Thanos)
Độ chắc: **order Cường 2026-11-18 xác nhận 4 điểm: (1) nhân vật đang tấn công bị dính chưởng rồi tan như búng tay Thanos, (2) thiên về màu đất, cái chết = thân xác trở về cát bụi, (3) game góc nhìn xiên kiểu Diablo 2, (4) html chạy trực tiếp không cần mạng**; phần còn lại suy từ research chung · Cập nhật: 2026-11-18 · Nguồn: kỹ thuật dissolve / erosion + hạt (`vfx-code/references/techniques.md`), mẫu "snap" dạng cát bay (hiệu ứng tan thành tro phổ biến trong game / phim), Plan `Docs/VFX/Disintegrate/Plan.md`

## Nó là gì
Một đối tượng đang đứng yên **vỡ thành hàng nghìn hạt nhỏ, tách dần từng mảng theo một mặt sóng quét qua, hạt bay lên + trôi theo gió, sáng rồi tắt**; cuối cùng không còn gì. Người xem nhận ra nhờ **hình đối tượng còn nguyên ở phần chưa tan** và **mép tan phát sáng**.

## Cấu trúc
| Phần | Vai trò | Hình | Bắt buộc |
|---|---|---|---|
| Thân đối tượng | thứ bị tan, giữ nguyên hình tới khi tới lượt | silhouette thật (có màu, có khối) | **có** |
| Mặt sóng tan (v2: lan từ điểm trúng; v1: chân→đầu) (mép phát sáng) | cho thấy "đang tan" + hướng tan | dải hẹp trên thân, sáng hơn, đổi sang màu hạt | **có** |
| Hạt tách ra | thân biến thành hạt (mỗi hạt lấy màu mảnh gốc rồi chuyển sang màu năng lượng) | hạt vuông nhỏ + vài hạt glow + vài vệt sao | **có** |
| Chuyển động hạt | bay lên + trôi ngang theo gió, chậm dần, nhỏ dần, mờ dần | dòng hạt cong, không rơi thẳng | **có** |
| Phản ứng nền (chân) | báo hiệu năng lượng: vòng pulse trên đất + quầng sáng dưới chân + bóng nhạt dần | ellipse theo camera 3/4 | phụ |
| Tích (anticipation) | thân sáng lên, rung nhẹ ngay trước khi tan | 0,15 s | phụ (nhưng nên có) |

## Nhịp (mặc định, ~3,1 s tổng)
**v2:** chưởng phóng 0,12 s → trúng 0,55 s (chớp + giật lùi) → tan lan từ điểm trúng 0,63–1,73 s (khoảng cách + noise) → bụi tàn tới ~4,0 s. (v1: giữ 0,15 → tích 0,15 → quét chân→đầu 0,9 → tàn ~3,1 s.) Một chớp duy nhất: v2 = **cầu sáng + vòng + tia ở điểm trúng** (v1 = vòng pulse ở chân); không chớp trắng toàn màn.

## Bản v2 (theo Cường): thêm 2 phần
- **Đòn chạm**: chưởng (sóng năng lượng cung cong + đuôi) bay dọc **đường chéo mặt đất** từ phải-sau vào ngực nhân vật đang ở tư thế tung đòn; **một chớp duy nhất ở điểm trúng** (cầu sáng + vòng + tia toả), thân giật lùi + rung.
- **Tan từ điểm trúng lan ra** (khoảng cách tới điểm trúng + noise), bụi **cát nâu vàng, trộn thường (không cộng sáng)**, trôi **theo hướng chưởng** (xuống-trái trên màn), nhỏ + mờ dần.
- Góc nhìn **Diablo 2**: ô nền 2:1 (nhìn xuống 30°), lưới thoi 45° dưới chân; đổi được 3/4 40° hoặc top-down 60°.

## Bất biến
- (v2) thân ở **tư thế tấn công** trước khi dính; chưởng **chạm trước, tan sau** (không tan khi chưa trúng); hạt là **cát bụi màu đất**, không phải hạt sáng xanh.
- Phải thấy **hình đối tượng còn nguyên** ở phần chưa tan, và **mỗi hạt lấy màu của chỗ nó tách ra**.
- Tan theo **mặt sóng + noise** (mảng), không phải mờ đều (fade alpha) và không phải nổ ra mọi hướng.
- Hạt **bay lên + lệch theo gió**, nhỏ dần + mờ dần; hạt cuối phải **hết hẳn**.
- Có **mép sáng** ở nơi đang tan.
- Một ngữ cảnh (ground, đứng), một chớp.

## Được đổi
Màu (đất mặc định / xanh lam / tím), đối tượng (nhân vật / vật / chữ), hướng quét (chân→đầu, đầu→chân, từ một bên), độ lệch gió, độ mịn hạt, thời lượng, âm thanh.

## Lỗi đã gặp (khi làm bản HTML đầu)
- **Cháy trắng, mất màu mảnh gốc** (vfx-director 2026-11-18, đo: 25–32% pixel thân ≥ 225 ở 0,6–1,0 s; màu áo choàng về 0 từ 0,95 s): do mép thân mix hẳn sang hot + ô sáng 2×2 ô + hạt sinh ra đã trộn 40% hot + cộng sáng chồng. Vòng 1 sửa chưa đủ (vẫn 27% trắng, do nhân sáng 1,5 + 25 làm màu thân xanh xám thành trắng). Vòng 3: tint ≤ 0,3, glow mép alpha 0,16, hạt giữ màu gốc (nhân 1,15, chặn 225) pha dần sang mid, 85% ở u 0,4, rồi sang màu năng lượng, alpha hạt 0,28 → đo trắng ≤ 4% (mẫu số: pixel có max kênh ≥ 100, nhân vật xanh; mẫu số ≥ 150 thì ~9,5%). **Thùng / chữ / chữ vàng vẫn cháy hơn** (thùng 13% / chữ 10–18% ở mẫu số 100; chữ gốc đã trắng nên một phần là màu nguồn) — alphaK theo đối tượng đã hạ, chưa đạt hẳn. **Khi cộng sáng nhiều hạt: không nhân sáng màu gốc, giảm alpha; đo % pixel ≥ 225.** Hạt phải còn thấy chấm đỏ / nâu bay lên trước khi hoá xanh.
- `?color=` / `?target=` ngoài danh sách (kể cả `__proto__`) làm sập trang → kiểm theo danh sách, không tra object bằng khoá do người dùng nhập.
- `?target=` sai làm sập trang; Space trong chế độ tĩnh chết; đổi tốc độ giữa chừng làm âm lệch hình (âm lên lịch cố định lúc phát) → đổi tốc độ phải restart.

## Lỗi đã gặp (v2, vfx-director 2026-11-18)
- **Chưởng bay từ phía sau nhưng vẽ đè lên thân** → vẽ chưởng TRƯỚC thân (thứ tự xa→gần theo mặt đất), chỉ chớp trúng vẽ sau.
- Thân bắt đầu ngả màu cát ~0,16 s trước khi chưởng chạm (trái bất biến "chạm trước, tan sau") → chặn tint / mép tàn bằng `t≥T.hit`.
- Mép tàn (ô 2×cs, alpha 0,1) + lấp lánh đẩy pixel ≥225 lên ~10% → ô 1,2×cs, alpha 0,045, lấp lánh 0,3 → đo ≤ 4% (0,9–1,2 s, mẫu số max kênh ≥100).
- Lấy mẫu ô 2,5 px mà vẽ ô 2,84 px (HS ≠ 1) → kẻ moiré; làm tròn toạ độ vẽ thân.

## Biến thể đã làm
- `Docs/VFX/Disintegrate/index.html` — bản HTML canvas + WebAudio, 1 file offline (order Cường 2026-11-18). v1: nhân vật đứng tan hạt sáng xanh (đã gửi). **v2**: nhân vật tấn công + chưởng + cát bụi đất + góc Diablo 2. Chưa có prefab Unity. **Cường (người order) đồng ý v2 và nhận giao 2026-11-18**; art lead chưa duyệt vào thư viện.
