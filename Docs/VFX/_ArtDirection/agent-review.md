# Review bằng agent khác trước khi chuyển art lead (art lead chốt 2026-11-13)

Quy trình bắt buộc cho mọi VFX / biến thể **tạo mới**: làm xong → script kiểm → **agent khác review theo luật** → sửa đến khi đạt → **mới chuyển art lead review lần cuối**. Không tự nói "xong" và không thêm vào `Included` của `VfxShowcaseBuild.cs` khi chưa qua đủ các bước.

## Thứ tự
1. Người làm tự chạy `python -I tools/check_texture_plan.py` (phải exit 0) + xem preview / Review Lab của chính mình.
2. Gọi **agent review** (Agent tool, `subagent_type` mặc định, **không fork**: agent phải không biết người làm đã chọn gì và vì sao). Đưa brief ở dưới, **chỉ đưa đường dẫn, không đưa kết luận của người làm** (tránh bị dẫn).
3. Agent trả báo cáo: mỗi mục `ĐẠT` / `LỖI` + bằng chứng (đường dẫn file, dòng, ảnh). Người làm sửa mọi `LỖI`, build lại, **gọi agent review lại** đến khi không còn lỗi (tối đa 3 vòng; vòng 3 vẫn lỗi thì báo art lead kèm lỗi còn lại, không giấu).
3b. **Khi đưa vào Showcase** (sau khi art lead duyệt): thêm tiền tố vào `Included`, **thêm dòng đèn vào `VfxShowcaseLights.Table`** (khớp tên chính xác, mỗi biến thể một dòng), chạy Build Scene, rồi Play kiểm đèn bật và log không có cảnh báo. (Bỏ sót đèn ở đợt Toxic / Gold / Storm 2026-11-13.)
4. Chuyển art lead: nêu **kết quả review của agent** (đã đạt những gì, đã sửa gì, còn điểm yếu nào mình biết) + link Review Lab. Art lead là người duyệt cuối; mình không tự chốt "đạt".

## Brief mẫu cho agent review (điền `<...>`)
> Bạn là reviewer VFX độc lập. Chỉ đọc và kiểm, **không sửa file**. Project `D:\Game_prj\VFX_LIb`. Review effect `<Tên>` (prefab `Assets/VFX/<Tên>/Prefabs/VFX_<...>.prefab`, builder `<đường dẫn .cs>`, plan `Docs/VFX/<...>/`, preview `Docs/VFX/<...>/Preview_sheet.png`, Anatomy `Docs/VFX/_Anatomy/<loại>.md`).
> Kiểm theo `.claude/rules/vfx-art-lead.md`, `Docs/VFX/_Library/LIBRARY.md` (mục "Luật chọn") và `AGENTS.md`. Trả về bảng, mỗi dòng `ĐẠT` / `LỖI` + bằng chứng:
> 1. **Texture từng thành phần**: với *mỗi* ảnh trong builder (kể cả lớp phụ: arc, cracks, ring, glow), tra `LIBRARY.md` ra thư mục đúng vai trò; chạy `python -I tools/library_props.py --contact <nhóm>/<vai trò>` và **xem contact sheet**; đối chiếu `library_props.csv` / `library_direction.csv`. Ảnh có đúng vai trò? Plan có ghi thành phần → thư mục → ảnh chốt + ảnh loại? Có dùng ảnh ngoài Library (thư mục effect) mà không nói lý do? Chạy `python -I tools/check_texture_plan.py --builder <builder>`.
> 2. **Hướng sheet**: sheet có hướng (tia, vệt, lửa thổi một phía) có bị spam / xoay ngẫu nhiên không?
> 3. **Không gian**: không Horizontal / Vertical Billboard; dựng đứng = Stretched (sheet ngang, đầu = mép TRÁI); nằm đất = Billboard + Render Alignment Local/World; quy mô và camera 3/4 40° đúng plan.
> 4. **Kỹ thuật prefab** (đọc builder / dùng prefab): Scaling Mode Hierarchy mọi Particle System; `sortingOrder` không trùng (mặt phẳng trước, rồi tới độ sáng); Frame over Time tuyến tính (`LinearFrames`, không `VfxBuildKit.Curve`); shader đúng luật (slash chỉ Coloso, khói mặc định đúng loại); một ngữ cảnh + một chớp Impact mỗi effect.
> 5. **Bất biến**: chép "Bất biến" từ file Anatomy, xem preview, từng bất biến có thấy trong ảnh không? Biến thể: đổi ít nhất hai trục (mesh / bố cục / timing / lớp phụ) **thực chất** nhưng vẫn nhận ra là cùng hiệu ứng; không chỉ đổi màu / texture. Có hình lạ (móc, đĩa phẳng, quầng lệch lõi, nổ trước khi tia chạm đất…)?
> 6. **Tài liệu**: `MAP.md`, Plan, Anatomy (mục "Biến thể đã làm") đã cập nhật?
> Nếu không chắc một mục, ghi `KHÔNG CHẮC` + lý do, đừng đoán `ĐẠT`. Kết thúc bằng danh sách `LỖI` theo mức nghiêm trọng.

## Ghi chú
- Agent review không thay art lead: nó chỉ chặn lỗi luật; thẩm mỹ và "có đúng ý không" vẫn do art lead quyết.
- Agent review cũng có thể sai: người làm xem lại từng `LỖI`, nếu cho là sai thì ghi lý do trong báo cáo gửi art lead, không âm thầm bỏ qua.
