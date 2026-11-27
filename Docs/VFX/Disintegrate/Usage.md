# Disintegrate (tan biến thành cát bụi) — ghi chú dùng (giao 2026-11-18)
Order: Cường (`work/vfx_orders/20261118_cuongdt_tanbien/`). Cường đã đồng ý demo v2 ("được đấy nhỉ, done task"). **Đây là Cường duyệt demo, chưa phải art lead duyệt vào thư viện.**

## Gói giao
- `Docs/VFX/Disintegrate/index.html` — 1 file, mở thẳng bằng trình duyệt (file://), **không cần mạng**, không file ngoài. Bấm 1 lần để bật tiếng.
- `Docs/VFX/Disintegrate/Preview/tan_bien_final.gif` — clip ~4 s (nhân vật tấn công → dính chưởng → tan thành cát bụi).
- Plan: `Docs/VFX/Disintegrate/Plan.md`; Anatomy: `Docs/VFX/_Anatomy/disintegrate.md`.
- **Không có Unity prefab** (Cường chỉ cần bản html; chưa ai yêu cầu prefab). Không thêm `Included` / Showcase.

## Cách dùng
- Mở `index.html`; Space = phát lại. Thanh trên: đối tượng (nhân vật tấn công / đứng / thùng / chữ), màu (đất / xanh lam / tím), góc nhìn (Diablo 2 2:1 / 3/4 40° / top-down 60°), lặp, âm thanh + âm lượng, tốc độ.
- URL: `?target=attacker|figure|crate|text&color=earth|blue|violet&cam=d2|34|top`; `?t=<giây>&ui=0&seed=7` vẽ 1 khung (xuất ảnh).
- Quy mô: nhân vật ~1,7 m, ô nền 1 m; nhịp: chưởng 0,12 s → trúng 0,55 s → tan 0,63–1,73 s → bụi tàn tới ~4,0 s.
- Chỉnh nhanh: hằng số `T` (nhịp), `PAL` (màu), `DIR` (hướng chưởng / gió), `CELL` (độ mịn hạt), hàm `TARGETS` (đổi đối tượng; thay bằng sprite thật cần thêm hàm nạp ảnh, chưa làm).

## Còn lại / điểm yếu
Nhân vật vẽ tạm (không phải model game), 1 pose; thùng / chữ chưa đo độ sáng ở v2; âm thanh chưa nghe bằng tai (chỉ kiểm không lỗi); chưa có prefab.
