# RewardBurst — nổ mở phần thưởng (kiểu Starr Drop của Brawl Stars)
Độ chắc: **theo video ref art lead (quay màn hình mở Starr Drop, nhiều độ hiếm)** · Cập nhật: 2026-11-18 · Nguồn: `simplescreenrecorder-2026-11-18_09.24.38.mkv` (link gốc youtube.com/shorts/qy3UVPQWyF0 không tải được)

Một lần phát, dài ~2,2 s, nhìn thẳng như UI (billboard theo camera). Vật thưởng đứng giữa; effect ở quanh và sau vật.

## Cấu trúc (4 nhịp)
| Nhịp | Giây | Thành phần | Bắt buộc |
|---|---|---|---|
| Chờ / tích | 0–0,5 | Halo cầu sáng ấm sau vật (thở), sao chữ thập nhấp nháy ngẫu nhiên quanh vật, hạt sáng hút vào tâm | halo + sao |
| Chạm | 0,5 | **Vòng trắng mảnh viền mềm** loe từ vật (kèm vòng vàng nhỏ hơn đi sau) | **có** |
| Chớp | 0,7 | Cầu trắng mềm phủ vật + **chùm tia nhiều màu** (xanh, ngọc, cam, hồng) xoay chậm phía sau | **có** |
| Nổ | 0,95 | Chớp trắng-xanh mở rộng, **vệt sáng toả tâm**, sao bắn ra, rồi sao trôi lấp lánh mờ dần | **có** |

## Bất biến
- Có đủ 4 nhịp theo thứ tự; vòng trắng mảnh phải thấy rõ **trước** chớp (khung ~0,6–0,8 s).
- Chùm tia nhiều màu phải nhận ra được phía sau chớp (không chỉ là một khối trắng).
- Tâm đối xứng, mọi thứ toả từ vật thưởng; không hướng gió / không rơi trọng lực.
- Chớp không được cháy trắng kín cả khung quá ~0,4 s.

## Được đổi
Màu theo độ hiếm (xanh lá Rare, vàng Legendary, đỏ Mythic, tím Epic…), số vệt / sao, kích thước, thời gian nhịp chờ.

## Lỗi đã gặp
- **Tia không được là một ảnh vuông** (art lead 2026-11-18): ảnh vuông luôn có biên, trong khi ở ref tia chỉ bị cắt do mép màn hình. Làm mỗi tia một hạt: ảnh nêm 4:1 (đỉnh ở mép trái), `pivot (0.5,0,0)`, cỡ 3D (dài 45 × rộng 8–24), `startRotation` đặt tay từng tia.
- Ghi đè prefab bằng `SaveAsPrefabAsset` khi đã có instance trong scene làm instance cũ mất con / mất material (chỉ còn 3 renderer): sau khi dựng lại prefab phải xoá instance rồi đặt lại.
- **Tia (ray) làm sai hai lần** (art lead 2026-11-18). Ref thật: 6–8 nêm **đặc, cạnh cứng, hẹp ở tâm loe ra, dài tới mép màn hình (~2× cỡ vật)**, góc và độ rộng **không đều**, màu cyan là chính + một tia hồng-đỏ + cam, mỗi tia có **lõi trắng mảnh**, **alpha blend** (giữ màu trên nền vàng, không cộng sáng), hiện cùng lúc chớp trắng. Sai: tia mảnh mờ dần (24 tia), nêm chia đều 12 cái (nhìn như bánh xe), nhiều hạt xoay chồng bóng đôi.
- **`ParticleSystemRenderer.maxParticleSize` mặc định 0,5** (nửa chiều cao viewport) cắt cỡ mọi hạt lớn (tia 36 bị kẹt ~12). Hạt cỡ lớn phải đặt `maxParticleSize` lớn (đã đặt 5).
- Nêm quá rộng + lệch (art lead 2026-11-18): nhiều hạt nêm xoay ngẫu nhiên chồng lên nhau thành bóng đôi. Sửa: một ảnh 12 nêm hẹp chia đều, màu nướng sẵn, một hạt duy nhất.
- Bản 1 "chưa giống ref" (art lead 2026-11-18): vòng mỏng loe một lần (ref: **vòng trắng dày, xung nhịp lặp lúc tích**); chùm tia là 24 tia mảnh (ref: **8–10 nêm rộng cạnh cứng, mỗi nêm một màu**); chớp tròn nhỏ (ref: **ellipse cao, to hơn vòng**); quầng halo mờ (ref: cam-vàng đậm); vệt nổ là gạch mảnh (ref: quầng xanh-trắng tia mờ).
- Particle bị sprite nông trại che (Demo_scene idle_farm_harvesting): phải đặt sorting layer `WorldUI` (layer cao nhất của project).
- Chớp trắng + quầng xanh lớn (13 m) làm cháy cả khung, che mất chùm tia: chớp ≤ 5 m, quầng ≤ 11 m, alpha đỉnh ≤ 0,9.
