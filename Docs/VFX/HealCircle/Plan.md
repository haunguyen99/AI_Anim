# VFX_HealCircle — kế hoạch v1 (duyệt 2026-11-03)

Pipeline: Built-in · Kiểu: one-shot · Thời lượng: ~1.5 s · Kích thước: ~2 m · Art Style: Stylized mềm (đã chọn)
Không gian: ground · nằm đất (Billboard + Local) + đứng (Billboard / Stretched) · camera 3/4 40° · neo bám nhân vật (simulation Local) · nền tối
(đã chốt: ~2 m, bám nhân vật, một lần ~1.5 s, xanh lá hồi máu, vòng phép vẽ bằng script mới; đề xuất: camera 3/4 40°, nền tối)
Màu: Core `#F4FFE0` · Mid `#7CF29A` · Outer `#1FA85A`

| # | Layer | Vai trò & timing | Kỹ thuật | Kết thúc | Material / Shader | Texture (nguồn) |
|---|---|---|---|---|---|---|
| 1 | GroundGlow | vũng sáng dưới chân 0–1.5 s | Billboard + Local, size 2.4, alpha 0→0.6→0 | fade | M_HealCircle_Glow_Add / Mobile/Particles/Additive | T_HealCircle_Glow (make_texture glow) |
| 2 | RuneOuter | vòng ngoài mở 0–0.2 s, xoay +25°/s, tắt 1.1–1.5 s | Billboard + Local, size 2.0, SOL 0.6→1 | fade | M_HealCircle_RuneOuter_Add | T_HealCircle_RuneOuter (heal_circle_textures.py) |
| 3 | RuneInner | hoa văn trong, trễ 0.08 s, xoay −45°/s | Billboard + Local, size 1.3 | thu nhỏ + fade | M_HealCircle_RuneInner_Add | T_HealCircle_RuneInner (heal_circle_textures.py) |
| 4 | Beam | cột sáng bốc lên 0.1–1.1 s | Stretched Billboard đi lên, 1 hạt, cao ~2.2 m, pivot (0,1,0) | fade | M_HealCircle_Beam_Add | T_HealCircle_Beam (heal_circle_textures.py; đáy sáng ở mép phải, mép trái = hướng lên) |
| 5 | Motes | hạt sáng bay lên từ viền vòng 0.1–1.5 s | Billboard, 20 hạt (2 × 10 nhịp), circle r 0.9 m, bay lên 0.6–1.4 m/s, noise nhẹ | thu nhỏ | M_HealCircle_Mote_Add | T_HealCircle_Mote (make_texture dot --softness 0.5) |
| 6 | Sparkles | sao lấp lánh 0.2–1.0 s | Billboard, 6 hạt, phồng rồi xẹp, xoay ~90° | thu nhỏ | M_HealCircle_Sparkle_Add | T_HealCircle_Sparkle (make_texture star --points 4 --pinch 0.6 --halo 0.5) |

- Thứ tự vẽ: GroundGlow −5 → RuneOuter −4 → RuneInner −3 → Beam 0 → Motes 2 → Sparkles 3.
- Hình vòng phép: tròn, chấm, cánh lá tròn (hồi máu = an toàn, không gai nhọn). Ảnh: `Textures_contact.png`. Không dùng shape thư viện.
- Dựng lại texture vòng phép: `python -I Docs/VFX/HealCircle/heal_circle_textures.py Assets/VFX/HealCircle/Textures`.
- Gameplay: chỉ trang trí. Shader mới: không. Ngân sách: ~30 particle, 6 material, texture 512.
- Giả định: nền tối → mọi lớp Additive; texture nền đen import `alphaFromGray`.

## v2 (2026-11-03, art lead: thời gian tồn tại lâu hơn 2 s)
- Thời lượng một lần từ ~1,5 s lên **~2,8 s**: vòng ngoài / quầng 2,8 s, vòng trong 2,7 s, cột sáng 2,2 s, đốm sáng phát đến ~2 s (19 chu kỳ), lấp lánh đến ~2,3 s (13 chu kỳ).
- Giữ nhịp mở nhanh: các mốc "mở ra" của đường cong dời về đầu (0,07–0,09 tuổi), phần giữ dài ra (vòng sáng đủ đến ~85% tuổi) rồi mờ dần ở ~2,4–2,8 s.
- Preview thêm mốc 1,2 / 1,8 / 2,3 / 2,6 / 2,85 s.
