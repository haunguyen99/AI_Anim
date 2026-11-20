# Chế độ B: spec + prompt bàn giao

Đọc khi không dựng prefab trực tiếp mà xuất spec/prompt cho người hoặc agent khác (engine khác, phiên khác, team khác). Gộp từ dynamic-vfx-prompt-builder 2.0.0 (spec-and-prompt, concept-to-implementation), rút gọn.

## Nguyên tắc

- Trao đổi và spec bằng tiếng Việt; **prompt cuối hoàn toàn bằng tiếng Anh**, tự chứa, dán được vào chat mới. Không viết "như đã nói ở trên", không chỉ trỏ link tới skill.
- **Vẫn một lần duyệt**: kế hoạch/spec ở mục 2 là thứ được duyệt. Prompt chỉ xuất sau khi duyệt. Người dùng xin trước thì xuất bản có nhãn **DRAFT — NOT APPROVED**.
- Tách rõ 4 loại: **đã chốt** (người dùng nói), **quan sát được** (thật sự thấy trong ảnh/video), **đề xuất** (Claude), **chưa rõ**. Không nâng đề xuất thành yêu cầu.
- Không bịa engine version, pipeline, package hay cấu trúc repo. Chưa biết thì prompt yêu cầu agent nhận kiểm tra môi trường trước.
- Chỉ viết prompt thì không sửa project, không tạo asset, không tuyên bố đã test.

## Spec (bổ sung vào kế hoạch mục 2)

1. Tên / version / trạng thái (draft, approved, revised).
2. Concept: mục đích, ảnh tham chiếu đã xem (path), Art Style + trạng thái, màu, tỷ lệ, camera.
3. Timeline theo layer: start / peak / hold / end, đơn vị giây; timing chưa chốt ghi đề xuất.
4. Gameplay: trigger, target, thời điểm có hiệu lực, ai sở hữu trạng thái (hit/damage/khoá), cancel/end/replay. Chỉ trang trí thì ghi rõ.
5. Asset: đơn / sheet / atlas / mesh / material / shader; kênh shader đọc (R hay alpha); grayscale + tint; nguồn reuse hay tạo mới; texture brief nếu cần tạo.
6. Thông số có đơn vị, khoảng tuning, trạng thái. Khoảng "2–3 nhánh" không được ghi thành "3" là quyết định.
7. Bảng quyết định (ID, giá trị, nguồn, trạng thái) khi effect có nhiều quyết định.
8. Nghiệm thu: dấu hiệu đúng hình, chuyển động, kết thúc, gameplay; môi trường đánh giá.

## Có ảnh concept

Mở đúng ảnh trước khi viết. Mỗi layer mô tả cụ thể theo những gì thật sự thấy:
- vai trò và độ ưu tiên;
- vị trí và tỷ lệ tương đối;
- silhouette: phình/thắt, đặc/rỗng, dày–mỏng;
- đầu–thân–đuôi hoặc lõi–mép;
- phân bố sáng tối và màu;
- mép sắc hay mềm;
- quan hệ che nhau giữa các layer.

Lập bảng **dấu hiệu trong concept → yêu cầu hình ảnh → cách dựng → cách kiểm tra**; mọi dấu hiệu nổi bật phải có một dòng. Không đo mét từ ảnh không có thước. Không suy timing từ ảnh tĩnh. Ảnh trái với spec đã duyệt: ghi xung đột, giữ spec.

## Texture brief (khi cần tạo texture mới)

```text
Asset type: runtime VFX texture — one reusable local component
Component: <layer + function>
Silhouette: <main/secondary masses, edges, negative space to keep>
Value structure: <white / mid / dark zones; core–edge falloff>
Direction and pivot: <axis, root/tip, padding>
Channel contract: <which channel the shader reads; grayscale neutral, no hue>
Background: <true transparent alpha, or black for R-mask>
Grid: <single / atlas 2x2 / flipbook 4x2 loop or 4x4 one-shot>
Constraints: isolated component, no scene/ground/text/checkerboard; no baked glow unless specified
Avoid: <evenly repeated lobes, holed core, noisy detail, ...>
```

Kèm quy tắc art lead liên quan từ shape-language.md.

## Cấu trúc prompt tiếng Anh

1. **Task & scope**: effect, spec version/status, deliverables (prefab/material/script/demo scene/docs theo engine).
2. **Project check**: read repo conventions, verify engine/version/pipeline, existing pooling/VFX manager; do not install packages or switch pipeline.
3. **Visual spec**: art style, camera, every layer with ID and the concrete visual description above; concept→build mapping table.
4. **Assets & setup**: per-layer textures (reuse vs new, briefs), channel read, blend, shader/material, import settings, naming.
5. **Timeline & animation** per layer, including each layer's end behavior (see dissolve.md).
6. **Gameplay & lifecycle** (if any): ownership contract, callbacks, cancel/death/despawn, disable/destroy, pool reuse; visuals never decide gameplay.
7. **Performance**: mobile-first; particle/material/texture budget (labelled as proposed if not measured), overdraw; no FPS promises before measuring.
8. **Tests & acceptance**: condition → action → expected; render/playback compared to concept at matching camera/scale/time; report visual gaps per layer ID (expected → observed → cause → fix → evidence). Build passing ≠ art approved.
9. **Report back**: files changed, how to run, what was and was not tested, limitations, open gates.

Unity: native Particle Systems, prefab không cần runtime controller; script demo/trigger nằm ngoài prefab; shader mới hỗ trợ Built-in + URP.

## Kiểm tra trước khi giao

Mọi quyết định đã chốt có trong prompt; đơn vị và tên dễ nhầm đúng; timeline nhất quán; cleanup có kết thúc; trạng thái duyệt khớp. Prompt dài thì lưu `Docs/VFX/<Effect>/Handoff_Prompt.md` và kèm danh sách ảnh cần gửi theo.
