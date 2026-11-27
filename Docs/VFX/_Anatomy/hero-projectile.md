# HeroProjectile — đạn bay thẳng có đuôi (cầu lửa Pyro, đạn Nova)
Độ chắc: **suy từ ảnh ref đã xem** (animlibrary "AAA Projectiles Vol 1": Projectile 25 và Projectile 6, xem ở `Docs/VFX/PyroNova_Runner6/ref/`) + brief sheet · Cập nhật: 2026-11-16 · Nguồn: `http://192.168.10.29:14765/?type=VFX&parent=AAA+Projectiles+Vol+1&item=Projectile+25|6`, prefab `D:\Projects\animlibrary\Assets\VFX_Library\VFX\Gameplay\AAA Projectiles Vol 1\Projectile 25|6.prefab`

Khác với `fireball-throw.md` (ném vòng cung 8 m rồi nổ ở đất): đây là **đạn bay thẳng theo hướng bắn**, có hạt thân + đuôi, chạm thì có hit nhỏ.

## Nó là gì
Một vật bay nhìn rõ, **đầu dẫn theo hướng bay, đuôi kéo ngược lại**, kèm hạt phụ. Hai dạng trong brief:
- **Pyro (VFXPyroProjectile, ref Projectile 25):** khối lửa thuôn dài như giọt nước, thân cam–vàng có vân nhiễu tối, **đuôi đỏ cam loe ra phía sau**.
- **Nova (NovaProjectile, ref Projectile 6):** **vệt đạn rất mảnh trắng, viền xanh dương nhạt**, đầu nhọn, kèm **trail xanh dương** (brief) và vài tia lửa.

## Cấu trúc
| Phần | Vai trò | Pyro | Nova | Bắt buộc |
|---|---|---|---|---|
| Body | thân bay | khối lửa thuôn (Stretched Billboard, hoặc mesh) | vệt mảnh trắng | **xương sống** |
| Tail / Trail | đuôi | đuôi lửa đỏ + khói đuôi | trail xanh dương mảnh (Trails) | **có** |
| Core glow | quầng | glow cam nhỏ | glow xanh nhạt nhỏ | có |
| Sparks | tia phụ | tàn lửa rơi lại | tia xanh nhỏ | có |
| Hit | chạm | chớp + bung lửa nhỏ | chớp xanh + tia | có (nhẹ) |

## Bất biến
- Thân **đầu hướng đúng chiều bay** (Stretched), đuôi **liền** sau thân (frame 2–4 phải thấy thân + đuôi tách bạch).
- Pyro: **nhìn ra lửa** (không phải bóng sáng trơn); Nova: **nhìn ra vệt mảnh và trail xanh dương**.
- Bay thẳng (không vòng cung), tốc độ cao, không bay chậm lờ đờ.
- Hit (nếu có) chỉ nhẹ ở điểm chạm; không biến thành vụ nổ lớn (đó là fireball-throw / explosion). Brief Run 6 không yêu cầu hit: v1 không có.

## Được đổi
Màu (lửa / xanh), độ dày thân, độ dài đuôi, loại tia, chất liệu đuôi.

## Lỗi biến thể đã gặp
Kế thừa từ `fireball-throw.md`: đuôi là thanh trắng đặc (dùng texture trail alpha thật, mảnh); mesh có đầu-đuôi phải quay mũi theo hướng bay.
- **Stretched Billboard: đầu tại vị trí hạt, thân kéo ngược về sau** (2026-11-17). Quầng lõi nên đặt lùi về giữa thân (z ≈ −0,4), không ở đầu (hiện thành đĩa phẳng ở mũi).
- **Ribbon đuôi (Trails) có mép cắt vuông ở đầu** nếu alpha bắt đầu ở 1: cho alpha bắt đầu từ 0 rồi lên 0,9 trong 10–12% đầu.
- **Hạt Stretched đứng yên** cần vận tốc rất nhỏ (+Z 0,01) để có hướng xác định; length = size × lengthScale.
- Đạn loop do code game di chuyển root; đuôi ribbon chỉ thấy khi root chuyển động (đặt hạt đuôi Local + Trails World space).

## Biến thể đã làm
`VFXPyroProjectile`, `NovaProjectile` (project runner6, 2026-11-17, chờ art lead).
