# Thác nước (stylized toon, môi trường loop)
Độ chắc: theo video ref art lead (2026-11-12) + đã dựng Map6 · Cập nhật: 2026-11-12 · Nguồn: `C:\Users\Manh\Downloads\VFX waterfall.mp4` (khung hình lưu ở `Docs/VFX/Waterfall_Map6/ref_frame.png`), brief airport-tycoon S_Map6

## Nó là gì
Dải nước rơi thẳng, **màu phẳng gần như không hoạ tiết**, chỉ có **một đường viền trắng mảnh dọc mép**. Chân thác có **một cụm bọt trắng đặc** sôi tại chỗ, quanh đó **2–3 vòng gợn trắng mảnh, đứt đoạn** lan ra trên mặt nước. Loop, không chớp.

## Cấu trúc
| Phần | Vai trò | Hình dáng | Bắt buộc? |
|---|---|---|---|
| Thân thác | xương sống | mesh phủ mặt thác; màu phẳng + viền trắng mép (một bên dày hơn); chuyển động = vài dải sáng nhạt trượt xuống, **không phải vệt trắng** | có |
| Cụm bọt chân | xương sống | blob trắng đặc viền cứng, gom thành một đám mây ~1–1.3× bề rộng dải, phồng / xẹp tại chỗ, không bắn xa | có |
| Gợn sóng | xương sống | vòng trắng mảnh nằm trên mặt nước, đứt thành cung, nở ~2× cụm bọt rồi mảnh dần; 2–3 vòng cùng lúc | có |
| Viền nước chạm bờ | phụ | đường trắng mảnh ở mép mặt nước (shader nước của map lo) | tuỳ |

## Chuyển động / nhịp
- Thân: dải sáng nhạt trượt xuống chậm (~0.4 UV/s, tile dọc 45 m).
- Bọt: mỗi blob 0.5–0.9 s, phồng lên rồi co lại, gần như đứng yên.
- Gợn: mỗi vòng ~2 s, ease-out, cạn dần bằng ăn mòn (mảnh đi), không mờ đục.

## Bất biến
- Thân thác **sạch, phẳng**; chi tiết duy nhất là viền trắng mép và chuyển động rất nhẹ.
- Bọt **gom một cụm ở chân thác**, trắng đặc, viền cứng.
- Gợn **nằm phẳng trên mặt nước, tỏa từ cụm bọt**, nét mảnh, đứt đoạn.
- Loop liền, không chớp.

## Được đổi
Màu nước, độ dày viền, số dải thác, kích thước cụm bọt theo bề rộng dải, số cung của vòng gợn.

## Lỗi đã gặp
- **Vệt trắng dày đặc trên thân thác = "rối quá"** (art lead 2026-11-12). Hai lớp vệt trắng chồng nhau + mặt gờ nghiêng kéo texture thành sọc ngang. Ref chỉ có màu phẳng + viền mép. Mặt nghiêng phải lấy V theo hướng dốc của mặt, không theo trục Y.
- **Bậc nằm phẳng nối hai tầng thác cũng phải có dòng chảy** (art lead 2026-11-12, "thiếu 1 chút chỗ này… đoạn đó không có mesh nước chảy"). Lọc mặt thác theo độ dốc (normal.y < 0.93) sẽ bỏ mất bậc phẳng nước chảy ngang qua; bậc đó đứng yên, nhìn như một mảng tối cắt ngang thác. Phủ flow lên bậc với hướng chảy cố định (từ chỗ thác trên rơi xuống → mép đổ của tầng dưới), không vẽ viền mép. Hồ chứa thật (nước đọng, có bọt + gợn) thì vẫn để phẳng.
  - Sai lần đầu: tưởng thiếu bọt ở điểm rơi rồi thêm cụm bọt. Bước đúng: tô lớp flow một màu chói (đỏ) để xem mesh phủ tới đâu, rồi mới kết luận.
- **Lớp phủ thân thác quá trong** (α 0.12) thì mặt dốc vẫn mang màu tối của shader nước gốc: nền phủ α ~0.65 để mọi mặt thác cùng một màu phẳng.
- **Đá chân thác che hết bọt** (Map6): đá nhô ra ~0.6× bề rộng dải. Đặt cụm bọt + tâm gợn ra trước đá (~0.55W).
- **Blob trong sheet chỉ chiếm ~1/3 ô**: size hạt ~3× blob muốn thấy.
- **Bọt phun lên có trọng lực, rải rộng** thì thành tung toé, không giống cụm mây của ref: speed thấp, gravity 0, hộp phát mỏng.
- **Lưới bọt (`water_tile_002`) nằm phẳng nhìn như vết nứt**: không dùng.
- **Gợn to hơn hồ** thì tràn qua mép vách: hồ nhỏ cần hệ số size riêng.
- Ảnh chụp bằng camera tạm làm nước stylized (shader dùng depth) hiện trắng; kiểm tra bằng Scene view.

## Biến thể đã làm
- `VFX_Waterfall_Map6` (airport-tycoon S_Map6). Plan: `Docs/VFX/Waterfall_Map6/Plan.md`.
