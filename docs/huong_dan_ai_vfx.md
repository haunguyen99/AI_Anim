# AI VFX: tài liệu dựng Agent làm VFX game (bản nháp, 2026-11-18)

Mục tiêu: một Agent chuyên VFX (hiệu ứng game trong Unity), làm việc giống AI Animation: nhận order, làm bản đầu dùng được, có người chấm độc lập, tự ghi bài học sau mỗi việc.

**Hiện trạng thật:** chưa có công cụ, skill hay kho kiến thức VFX. Mission VFX trên WorkAI (id 638, "GĐ2: AI VFX Workflow") ghi "chưa bắt đầu". Đã có sẵn: ComfyUI (sinh ảnh game, tách nền), Codex sinh ảnh, danh sách VFX của G-LumberCity (`work/g_lumbercity/gdd/anim_vfx.md`). Tài liệu này là kế hoạch để dựng phần còn thiếu, đi theo từng giai đoạn, giai đoạn nào cũng có cổng duyệt.

## 1. Agent VFX làm gì / không làm gì

| Làm | Chưa làm (giai đoạn đầu) |
|---|---|
| Đọc order VFX trong GDD, tách thành danh sách hiệu ứng + câu hỏi còn thiếu | Tự đưa VFX vào bản build chính của game |
| Sinh texture / sprite sheet flipbook (khói, bụi, tia lửa, lá rơi, mảnh gỗ) | Shader phức tạp (water, foam, dissolve) khi chưa có ca mẫu đã duyệt |
| Dựng và chỉnh Particle System trong Unity (kích thước, màu, vòng đời, đuôi, burst) | Sửa prefab / scene của dev khi chưa được giao |
| Dựng scene test, quay video ngắn từ Unity để xem | VFX có yêu cầu hiệu năng chặt (mobile thấp) khi chưa đo |
| Đo hiệu năng cơ bản (số hạt, overdraw, kích thước texture) | Nhận lệnh từ người khác ngoài người được giao |
| Xuất gói giao: prefab + texture + video preview + ghi chú dùng | |

## 2. Các loại VFX trong dự án (lấy từ GDD G-LumberCity)

| Nhóm | Ví dụ | Cách làm dự kiến | Độ khó |
|---|---|---|---|
| Khói / bụi một lần | Smoke puff khi vật nhảy tới đích, Chipping output dust, Debarking dust | Texture flipbook + Particle burst | Dễ |
| Tia / mảnh | Sawmill sparks, woodchips sparks, VFX_Cutting chỗ cưa | Particle + sprite nhỏ + trail | Dễ – vừa |
| Rơi / bay | Chopping leaf fall, Snow fall, Birds fly | Particle (hình dạng vùng phát, xoay, lắc) | Vừa |
| Vệt theo vật | Truck / Forklift trail | Trail Renderer | Vừa |
| Nước | Water flow, Splash & Ripple, Waterfall + Foam | Shader + flipbook | Khó |
| Chỉ báo UI | Net max sagging nhấp nháy đỏ, VFX blink nút Ads | Animation màu / scale | Dễ |

Làm theo thứ tự dễ → khó. Ca đầu tiên đề xuất: **VFX_Cutting chỗ cưa** (đã có trong mission 638).

## 3. Quy trình một VFX (đề xuất)

1. **Nhận order.** Đọc GDD / ref (video, ảnh), ghi: hiệu ứng xảy ra lúc nào, kéo dài bao lâu, camera nhìn từ đâu, nền sáng hay tối, nền tảng chạy.
2. **Bản thiết kế + bảng thời gian** (duyệt): các lớp (lõi, khói, tia, bụi), mỗi lớp bao nhiêu giây, màu, kích thước theo đơn vị Unity. Người dùng duyệt trước khi làm.
3. **Texture / flipbook.** Sinh bằng ComfyUI hoặc Codex, tách nền, ghép sprite sheet (số ô, kích thước ô), nén theo chuẩn game. Người dùng xem ảnh tĩnh.
4. **Dựng trong Unity.** Particle System + material, đặt trong scene test có camera giống game. Quay video ngắn.
5. **Agent chấm** (xem mục 5) xem video + số đo, trả Duyệt / Cần sửa.
6. **Người dùng duyệt** trên video. Mỗi note sửa gộp vào một bản mới.
7. **Giao.** Prefab + texture + video preview + ghi chú dùng (tên trong Unity, cách gọi, thông số có thể chỉnh).
8. **Ghi bài học** vào kho kiến thức.

Cổng duyệt: bước 2 (thiết kế), bước 3 (texture), bước 6 (video). Không bỏ cổng nào ở giai đoạn đầu.

## 4. Khung file cần tạo (theo khuôn AI Animation)

| File | Nội dung |
|---|---|
| `.claude/skills/vfx/SKILL.md` | Quy trình mục 3, khi nào kích hoạt ("làm VFX", "hiệu ứng khói", `/vfx`) |
| `.claude/skills/vfx/knowledge/CORE.md` | Luật một dòng cho mọi VFX (dưới ~6 KB) |
| `.claude/skills/vfx/knowledge/INDEX.md` | Mục lục + trạng thái từng loại VFX |
| `.claude/skills/vfx/knowledge/details/` | `smoke_dust`, `sparks`, `falling`, `trail`, `water`, `flipbook`, `unity_particle`, `performance`, `review_process`, `export` |
| `.claude/agents/vfx-director.md` | Người chấm độc lập, chỉ xem và chấm |
| `docs/huong_dan_ai_vfx.md` | Tài liệu này |
| `work/<game>/vfx/<tên>/` | Thư mục từng order: brief, texture, prefab, video, nhật ký chấm |

Công cụ cần có (làm lần lượt, mỗi cái hết một việc):
- `tools/vfx/flipbook.py`: ghép khung hình thành sprite sheet + kiểm kích thước.
- `tools/vfx/unity_cmd.py`: đưa lệnh vào Unity (tạo prefab, đặt Particle, quay video scene test). Cần chốt cách điều khiển Unity (mục 7).
- `tools/vfx/measure.py`: đếm hạt, kích thước texture, ước overdraw.

Việc nào làm lần thứ hai thì làm thành lệnh một bước.

## 5. Agent chấm VFX (vfx-director)

Cùng khuôn animation-director:
- Chỉ xem và chấm, không sửa file.
- Kết luận **Duyệt / Cần sửa**, mỗi lỗi ghi: thời điểm (frame hoặc giây), lớp nào, nguyên lý, cách sửa.
- Ghi rõ lỗi nào **[đo]** (số hạt, kích thước, thời gian) và lỗi nào **[mắt]**.
- Chấm theo góc camera thật của game, không chấm ở góc đẹp nhất.

Checklist chấm (nháp):

| Mục | Câu hỏi |
|---|---|
| Đọc được trong 1 giây | Nhìn từ camera game, biết ngay đó là gì |
| Thời điểm | Bắt đầu và kết thúc khớp với anim (frame va chạm, frame cưa) |
| Hình dạng chuyển động | Có lực, có giảm dần (nhanh lúc đầu, chậm lúc cuối), không đều đều |
| Màu và độ sáng | Hợp nền, không chói hơn nhân vật |
| Kích thước | Tỷ lệ với vật gây ra nó |
| Vòng lặp | VFX lặp: đầu và cuối khớp, không nhảy |
| Hiệu năng | Số hạt, overdraw, kích thước texture trong ngưỡng đã chốt |
| Dọn dẹp | Hạt hết đúng lúc, không để lại hạt kẹt |

## 6. Kho kiến thức tự lớn

Sau mỗi việc (mỗi vòng sửa xong, mỗi VFX duyệt), Agent tự ghi vào `details/` đúng mục:
- Câu feedback của người dùng → nguyên tắc bị vi phạm.
- Tham số đã duyệt (số hạt, vòng đời, màu, kích thước, tốc độ).
- Lỗi đo được → cách sửa.
- Thêm một dòng vào `INDEX.md` nếu có mục mới; chỉ thêm vào `CORE.md` khi áp dụng cho mọi VFX.

Giữ ngày và lời người dùng. Bài mới thay bài cũ tại chỗ.

## 7. Việc cần quyết trước khi dựng (hỏi người dùng)

| Câu hỏi | Gợi ý |
|---|---|
| Điều khiển Unity bằng cách nào? | Viết script Editor trong Unity, Agent đẩy file vào và gọi menu; hoặc dùng MCP cho Unity nếu team đã có |
| Dự án Unity nào dùng làm nơi thử? | Một project riêng "VFX test" copy từ dự án game, không chạm project chính |
| Render pipeline (Built-in / URP) và nền tảng đích | Chốt một chuẩn, ghi vào `CORE.md` |
| Ngưỡng hiệu năng | Số hạt tối đa mỗi hiệu ứng, kích thước texture tối đa |
| Ca đầu tiên | VFX_Cutting (G-LumberCity) |
| Ai duyệt cuối | Hậu, hoặc lead VFX |

## 8. Lộ trình thử nghiệm (khớp mission 638)

| Giai đoạn | Việc | Ra gì |
|---|---|---|
| 1. Khảo sát | Liệt kê loại VFX team đang làm, giờ/tuần, việc tốn giờ nhất | Bảng khảo sát |
| 2. Thử nhanh texture | Sinh 1 flipbook khói + 1 flipbook tia lửa bằng ComfyUI / Codex | Sprite sheet đã tách nền, người dùng nhận xét |
| 3. Thử nhanh Unity | Dựng 1 Particle System bằng code, quay video | Prefab + video |
| 4. Order thật | VFX_Cutting theo GDD G-LumberCity | Bản giao + số giờ so với làm tay |
| 5. Kết luận | Dùng được / cần điều chỉnh / chưa phù hợp | Báo cáo kèm ảnh, video, file |

Time-box: mỗi giai đoạn tối đa 1 tuần, không cam kết kết quả (đúng như mission ghi). Báo cáo tuần ghi số giờ AI làm và số giờ người sửa.

## 9. Điều cần nhớ khi chạy

- Trả lời tiếng Việt, đơn vị quen: giây, frame, cm / đơn vị Unity, số hạt.
- Không đụng project Unity chính khi chưa được giao.
- Frame đếm từ 1 cho khớp với anim (frame va chạm của anim ↔ frame bắt đầu VFX).
- Ảnh texture, video preview, prefab lưu vào `work/<game>/vfx/<tên>/`. File dữ liệu lớn không đưa lên git.
- Ghi MAP.md mỗi khi tạo thư mục hay công cụ mới.
