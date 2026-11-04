---
name: reference-animation-director
description: Subagent animation-director (.claude/agents/) chấm anim ở mỗi mốc trước khi gửi người dùng; log ở work/<dự án>/<clip>/director_log.md
metadata:
  node_type: memory
  type: reference
  originSessionId: 6bd27684-0e76-4e22-bce7-d0c34956b805
  modified: 2026-10-30T06:06:08.669Z
---

Người dùng yêu cầu 2026-10-30: agent "Animation Director" định hướng + feedback anim trong sản xuất. File `.claude/agents/animation-director.md` (model opus, chỉ xem, không sửa anim; chỉ ghi director_log.md). Gọi trước mỗi cổng duyệt (analysis, P0, blocking, spline, polish, pre-export) và trong /check_fb trước khi render đầy đủ; lỗi mức A sửa trước khi gửi, tối đa 2 vòng. Người dùng vẫn duyệt cuối.

Liên quan: [[feedback-ai-does-user-approves]], [[feedback-pose-accuracy]], [[feedback-anatomy-pass]].

Tự học (user 2026-10-30 "cứ tự học trong quá trình làm việc"): sau mỗi lần user duyệt/trả, so với kết luận director, ghi vào `.claude/skills/animation/knowledge/details/director_standards.md` (#blockers, #severity, #calibration). Không hỏi user tài liệu tiêu chuẩn.

Rig (user 2026-10-30 "check cả skin trong bước rig"): director chấm cả mốc rig-joints / rig-skin / rig-test (lbs_test.py, ảnh cận 3 góc), gọi trong /rig trước gate-done; log work/rig_lab/director/<id>.md.

Ghi chú vẽ Studio (2026-10-30): /check_fb bước 3b gọi director (ảnh nét vẽ gốc vs snap sau sửa, cùng góc) trước note-done; ghi chú nhỏ đã đo rõ được bỏ qua kèm lý do.

Gọi tay (2026-11-03): skill `/director [clip|nhân vật] [mốc]` (.claude/skills/director/) gom ảnh + số đo rồi gọi agent.
