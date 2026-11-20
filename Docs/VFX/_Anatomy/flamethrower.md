# Flamethrower — súng phun lửa (phun liên tục thành tia lửa hình nón)
Độ chắc: **suy từ research chung (game stylized: League of Legends / Overwatch Torbjörn-Pyro kiểu hoạt hình) + đề xuất mặc định (Phong, order 20261118_phongdq_phunlua; Phong trả lời "oke" cho đề xuất, chưa xem ảnh ref cụ thể)** · Cập nhật: 2026-11-18 · Nguồn: Plan `Docs/VFX/Flamethrower/Plan.md`; `fire-hand-flame.md`, `fire-wave-cast.md` (cùng nguyên tố lửa); `materials.md` (lửa)

## Nó là gì
Một người cầm súng, **giữ nút thì phun ra một dòng lửa liên tục từ đầu nòng**: lửa bắn nhanh ra phía trước, nở dần thành nón, đầu dòng cong lên và tan thành đỏ sẫm + khói; trúng vật thì vật bốc cháy. Thả nút thì dòng tắt dần, còn lửa mồi nhỏ ở đầu nòng.

## Cấu trúc
| Phần | Vai trò | Hình dáng | Bắt buộc |
|---|---|---|---|
| Dòng lửa (stream) | **xương sống**: lưỡi lửa nối nhau từ nòng ra ~5 m | lưỡi lửa mũi nhọn hướng bay, cel nhiều lớp (đỏ cam ngoài → vàng → trắng vàng lõi), hẹp ở nòng, nở ở cuối | **có** |
| Lửa đầu nòng (muzzle) | cho thấy nơi lửa ra | sao nhọn nhấp nháy + quầng sáng | **có** |
| Tàn / tia lửa | sống động, chỉ hướng | mảnh kim cương nhỏ bay quanh dòng chính, rơi | có |
| Khói cuối dòng | đuôi dòng lửa | cục tròn phẳng tối (tím xám), 2 lớp, bay lên | có (nhạt) |
| Ánh sáng hắt | lửa chiếu lên sàn + mép người | quầng cam trên sàn, rim sáng | có |
| Lửa mồi khi nghỉ | báo súng còn "sống" | lưỡi lửa nhỏ ở nòng, chấm xanh | phụ |
| Phản ứng vật trúng (bia) | cho thấy lửa có tác dụng | lửa bốc trên bia, cháy xém, khói | phụ |
| Âm thanh | tiếng phụt + lách tách | noise băng giữa + rền thấp + "fwoomp" lúc bắt | phụ (brief html có thể yêu cầu) |

## Nhịp
Bấm → lửa bắt (**fwoomp**, 0,12 s lên đủ) → phun **liên tục** (hạt ra đều 180/s) → thả → dòng tắt trong ~0,3 s, lửa còn lại tan trong ~0,9 s, khói bay thêm ~1,5 s → lửa mồi nhỏ. Một lần bắn mặc định 2,9 s.

## Bất biến
- Phải là **một dòng nối liền từ đầu nòng ra tới ~5 m**, không phải vài cục lửa rời hay quả cầu lửa.
- **Nhìn ra lưỡi lửa** (mũi nhọn, nhiều lớp màu cel), không phải khói tròn hay quầng glow.
- Dòng **hẹp ở nòng, nở dần thành nón**, màu **nóng ở gốc (vàng / trắng) → cam → đỏ sẫm ở đầu**; đầu dòng **cong lên** + tan.
- Có **lửa đầu nòng** gắn vào nòng, thả nút thì **ngắt thật** (không cháy mãi).
- Một ngữ cảnh (người đứng đất, bắn ngang), không chớp trắng toàn màn.
- Stylized: khối rõ, **bậc màu cứng (cel)**, bão hòa; không mờ nhoè kiểu thực tế.

## Được đổi
Màu lửa (cam đỏ / xanh hextech / tím), độ nở nón, tầm phun, tốc độ, có / không bia, nhịp bắn (liên tục / từng loạt), hình súng (cầm tay / tháp), mức khói, âm thanh.

## Lỗi đã gặp (bản HTML đầu, 2026-11-18)
- Bản nháp 1: lớp ngoài dùng màu quá nóng, **dòng cream nhạt, không ra lửa** → lệch bậc màu: lớp ngoài bắt đầu từ vàng cam, chỉ lớp trong mới trắng vàng.
- Bản nháp 1: dòng **mảnh như tia laser** → tăng bán kính cuối (0,40–0,62 m) + nón 9°.
- Chụp ảnh bằng Chrome headless mà canvas chỉ vẽ một lần thì ảnh trắng (không paint) → ở chế độ `?t=` phải vẽ lại bằng requestAnimationFrame.

- `?t=Infinity` / `?t=1e9` làm treo trang (vòng mô phỏng không kết thúc): kiểm `isFinite` + kẹp 120 s. Phím / chuột giữ bắn phải thả khi mất focus (`blur`, `pointercancel`, `visibilitychange`).

## Biến thể đã làm
- `Docs/VFX/Flamethrower/index.html` — bản HTML canvas 2D + WebAudio (order Phong 2026-11-18, `work/vfx_orders/20261118_phongdq_phunlua/`). Chưa có prefab Unity.
