# VFX_Explosion — kế hoạch v1 (đã duyệt)
Built-in · one-shot ~2s · bán kính ~4m · stylized

| # | Layer | Vai trò & timing | Kỹ thuật | Shape |
|---|---|---|---|---|
| 1 | Flash | 0–0.12s | billboard burst 1, additive | Impact đa gai (Shape Lab) |
| 2 | Core Fireball | 0–0.8s | billboard burst ~10 | Lửa (Shape Lab) |
| 3 | Fire Tongues | 0.05–0.6s | billboard burst ~14, hướng ra ngoài | Fire tongue (Shape Lab) |
| 4 | Shockwave Ring | 0–0.45s | mesh vòng scale nhanh + mờ | script `ring` |
| 5 | Smoke | 0.2–2.0s | burst ~12, bay lên tan chậm | Smoke cluster (Shape Lab) |
| 6 | Sparks | 0–0.9s | stretched billboard burst ~30, gravity | script `comet` |
| 7 | Debris | 0–1.2s | burst ~14, quay, gravity | Vụn gai (Shape Lab) |
| 8 | Ground Scorch | 0–2s | quad ngang, mờ dần | script `glow` tối |
| 9 | Embers | 0.3–2s | burst ~16, nhỏ, nhẹ | script `ember` |

Ngân sách: ~100 particle, 9 material, texture <= 1024.
Giả định: cam-vàng, khói xám ấm.
Shape Lab: art lead dựng #1,#2,#3,#5,#7 và gửi JSON/ảnh; còn lại sinh bằng script.

## Cập nhật khi build (2026-10-28)
- Debris: bỏ theo yêu cầu art lead.
- Flash gồm Flash_Slash (shape Slash từ Shape Lab, xoay ngẫu nhiên) + Flash_Glow (script glow).
- Core Fireball = thư viện Shape Lab DirectionalFlame03 (sheet 4x4, 14 frame, ô 1.54:1).
- Fire Tongues, Smoke, Slash: sheet 4x2 once xuất từ Shape Lab (thư mục Shapes/).
- Chưa kiểm chứng: shockwave ring nhìn còn nhỏ/mờ trong preview; chưa test mobile.
