---
name: project-sdr06-reload-gun-f1
description: SDR06 London Reload sửa 2026-11-05 theo GD Thịnh "không đổi hướng nòng": gunF1_v2 duyệt, đã đẩy TungNV_Dev 69832562
metadata:
  type: project
---

GD (Đào Đức Thịnh, G-DieLoop, WorkAI GSDR-1497) yêu cầu Reload không đổi hướng ngắm. User chọn: thân súng giữ như F1 của chính Reload, chỉ giật nhẹ khi rút trống F12 (1 cm/1°) và lắp F26 (2 cm/2°). Bản `gunF1_v2` (sửa tối thiểu từ lspline_v1) user duyệt trong Studio, FBX xuất bằng `work/pose_lab/fbx/fbxwrite.py` từ `models/sdr06_reload_gunF1_v2.json`, đẩy `London/SDR06_MC_Reload.fbx` lên TungNV_Dev 69832562 (tag git `sdr06-reload-gunf1-v2`). Script ở `work/shoot_die_repeat/sdr06/_barrel/`.

**Why:** v1 dùng `rigpose.ik_arm` dựng lại vai/khuỷu mỗi frame → lật 180°/frame (tay giật). Phải sửa tối thiểu (`fix_arm` trong build_d.py: gập khuỷu + swing vai, giữ xoắn gốc) và đo độ xoay/frame so bản gốc.

**How to apply:** muốn đổi tư thế súng/tay trên clip có sẵn thì dùng cách của build_d.py, không dùng ik_arm. HorusChat API không có upload file: video phải user kéo vào thread tay. Studio nạp anim FBX = dựng model JSON bằng poselab_model.py + `clip_registry.py pose-version` + `anim clip` đổi sang clip khác rồi về (để tải lại danh sách version). Liên quan [[project-sdr-map06]], [[reference-horuschat-mcp]].
2026-11-06 (sau): Reload London bản gunF1_v2 bị Unity 'File is corrupted' do FileId giả 00..0f trong fbxwrite.py; đã sửa writer, vá 7 file, đẩy afbb3f44. Chưa xác nhận Unity nhập được.
