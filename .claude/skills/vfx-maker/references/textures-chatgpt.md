# Tạo texture bằng ChatGPT

Đây là cách **chậm nhất** (1–2 phút/ảnh). Chỉ dùng khi `scripts/make_texture.py` và thư viện không đáp ứng (xem bước 3 trong SKILL.md).

## Vẽ trong Project "Texture_Maker" bằng app ChatGPT trên máy

Mọi ảnh cần vẽ đều làm trong **Project "Texture_Maker"** trên ChatGPT, mở bằng **app ChatGPT desktop** trên máy này (không dùng trình duyệt, không làm trong chat thường):

- Link Project: https://chatgpt.com/g/g-p-6ad6becc320c81918db11f3eaaa48026/project
- Project đã có Instructions riêng cho texture VFX (bản gốc: [chatgpt-texture-maker-instructions.md](chatgpt-texture-maker-instructions.md)). Instructions đặt sẵn các quy tắc chung, nên Claude chỉ cần gửi khối **TEXTURE REQUEST** bên dưới.
- Mỗi effect một chat mới trong Project, đặt tên theo effect (ví dụ `FireballProjectile`).

Claude mở được app nhưng không điều khiển được bên trong, nên chia việc như sau:

1. **Claude chuẩn bị:** viết một khối TEXTURE REQUEST cho mỗi texture. Copy khối đầu tiên vào clipboard (`Set-Clipboard`), rồi mở app:
   ```
   explorer.exe "shell:AppsFolder\OpenAI.Codex_2p2nqsd0c76g0!App"
   ```
   Nếu AppID không chạy được, tìm lại bằng `Get-StartApps | Where-Object Name -like '*ChatGPT*'`.
2. **Báo người dùng:** vào Project "Texture_Maker", mở chat mới (hoặc chat của effect nếu đã có), dán (Ctrl+V) và gửi. Lưu ảnh vào `Downloads` (hoặc thư mục người dùng chọn), rồi báo lại. Nhiều texture thì đưa lần lượt, mỗi lần copy khối tiếp theo vào clipboard, và ghi rõ tên file đích của từng ảnh.
3. **Claude nhận ảnh:** lấy file ảnh mới nhất trong `Downloads` (hoặc đường dẫn người dùng đưa), xem ảnh để kiểm tra theo mục "Khi nhận ảnh". Chưa đạt thì viết yêu cầu sửa (copy vào clipboard) để người dùng gửi tiếp trong cùng chat.
4. **Đưa vào project:** copy ảnh vào thư mục đích, đổi tên theo quy ước (ví dụ `Assets/VFX/<Effect>/Textures/T_Spark_Streak.png`), xử lý levels nếu cần, thay bản `_TEMP` và build lại.

## Nguyên tắc để texture dùng được trong game

- **Một phần tử, không phải cả cảnh:** một tia lửa, một cụm khói, một vệt chém — không vẽ cả vụ nổ. Hình tổng thể do particle tạo ra.
- **Grayscale/trắng trên nền đen thuần** (#000000) để tint bằng màu particle và dùng blend additive hoặc lấy độ sáng làm alpha. Chỉ để màu khi màu là bản chất của texture và kế hoạch đã ghi rõ.
- **Căn giữa, hình phủ ~85–90% ô (lề ~5–8%)**, không chạm mép. Chuẩn chi tiết theo loại texture: [texture-quality.md](texture-quality.md).
- **Ảnh vuông** 1024×1024 (sẽ import xuống 256–512), kể cả hình dài nằm ngang. ChatGPT hay tự ra ảnh chữ nhật cho hình ngang: kiểm tra kích thước khi nhận.
- **Flipbook:** ChatGPT không đảm bảo lưới đều. Chỉ đặt flipbook khi thực sự cần (khói cuộn, lửa cháy); ưu tiên ảnh đơn + chuyển động bằng particle module. Luôn kiểm tra lưới sau khi nhận ảnh.

## Mẫu TEXTURE REQUEST

Viết bằng tiếng Anh, điền đủ các trường (trường không áp dụng ghi `-`):

```
TEXTURE REQUEST
Name: T_Spark_Streak
Effect: FireballImpact
Type: single            (single | flipbook | variants | tileable | normal)
Size: square 1024x1024
Grid: -                 (flipbook/variants: columns x rows, frame count, e.g. 4x4, 16 frames)
Dissolve: -             (flipbook dissolve: direction A, e.g. "toward up-right (45 deg)")
Shape: one thin spark streak, elongated horizontally, hot bright core tapering to sharp points at both ends
Style: anime cel-shaded (hard edges, 2-3 flat value steps)
Color: grayscale on black
Usage: additive particle, stretched billboard
Notes: must read clearly at 64 px
```

- **Shape:** mô tả silhouette, độ dày, mép mềm/sắc, phân bố sáng–tối (lõi → mép), hướng (ngang/dọc).
- **Style:** dùng đúng art style đã duyệt trong kế hoạch.
- **Usage:** blend + render mode, để ChatGPT biết ảnh được dùng thế nào (ví dụ stretched billboard cần hình nằm ngang).
- **Flipbook:** ghi rõ chuyển động qua các frame (frame đầu → cuối) trong Shape.

Yêu cầu sửa: `FIX T_Spark_Streak: <chỉ phần cần sửa>, keep everything else the same.`

## Khi nhận ảnh

0. ChatGPT có thể vẽ vài bản trung gian (ví dụ ảnh ngang 1774×887) rồi tự vẽ lại theo Instructions: lấy **ảnh vuông cuối cùng**, chờ đến khi ChatGPT dừng hẳn.
1. Xem ảnh: đúng hình mô tả, nền đen thật (#000000), không chạm mép, đúng style.
2. Flipbook/variants: vẽ lưới đè lên ảnh (Pillow) để kiểm tra các frame nằm gọn trong ô, đủ số frame, chuyển động liền mạch.
3. ChatGPT thường trả nền hơi xám hoặc nhiễu: nếu cần, dùng Python (Pillow) để đẩy mức đen (levels), chuyển grayscale, resize — báo người dùng đã xử lý gì.
4. Xóa bản `_TEMP` và cập nhật build script sang file thật.
