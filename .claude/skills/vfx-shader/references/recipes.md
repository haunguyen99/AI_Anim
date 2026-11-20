# Công thức dựng hình bằng shader

Mọi hình khối do shader tính trên quad (hoặc mesh đơn giản tạo bằng code). Texture chỉ là noise dùng chung. Hàm `vfx*` nằm trong `VfxShaderLib.cginc`.

## Khung chung của fragment

```hlsl
float2 p = vfxCentered(i.uv.xy);          // -1..1, tâm quad = 0
half2 n = half2(tex2D(_NoiseTex, i.nuv.xy).r, tex2D(_NoiseTex, i.nuv.zw).g);
p += (n - 0.5h) * 2.0h * _DistortAmount;  // méo hình bằng noise (tuỳ chọn)
half d = <hình SDF>;                      // < 0 bên trong
half shape = vfxFill(d, _Soft);           // độ phủ 0..1
half alpha = shape * vfxDissolve(n.x, progress, _DissolveSoft) * i.color.a;
half3 col = <màu theo shape / ramp>;
return half4(col * i.color.rgb, alpha);
```

## Hình theo loại effect

| Effect | Hình (SDF / toạ độ) | Chuyển động | Ghi chú |
|---|---|---|---|
| Glow / flash | `vfxSdCircle`, màu theo `shape*shape` | progress → scale + fade | Rẻ nhất, không cần noise |
| Shockwave / ring | `vfxSdRing(p, r, w)` | r tăng theo `vfxEaseOut(progress)`, w giảm | Mép ngoài sắc, mép trong mềm: soft khác nhau hai phía (`d` âm/dương) |
| Aura / shield | vòng + noise méo | noise cuộn theo Y | Additive, loop: progress = `frac(_Time.y * speed)` |
| Lửa 2D | gradient đáy→ngọn (`uv.y`), độ rộng thu hẹp theo y | noise cuộn lên ăn mòn mép | Toon: `vfxRamp3` theo giá trị đã ăn mòn. Xem shader lửa có sẵn trước |
| Beam / laser | `vfxSdSegment` hoặc `abs(p.y) - w` | noise cuộn dọc X, độ rộng nhấp nháy theo seed | Mesh quad dài, UV.x dọc beam |
| Slash | cung: `vfxSdRing` giới hạn góc bằng mask theo `p` (không cần atan2: dùng `dot` với hướng) | progress quét dọc cung | Đầu dày đuôi mảnh: nhân width theo vị trí |
| Swirl / portal | `vfxPolar` (1 atan2) | cuộn góc theo thời gian | Hàm đắt duy nhất cho phép |
| Impact spark | vài `vfxSdSegment` toả tâm, độ dài theo noise/seed | progress kéo dài rồi co | ≤ 4–5 đoạn, nhiều hơn thì dùng particle |
| Khói toon | đĩa méo noise lớn + `vfxRamp3` (sáng/trung/bóng) | noise cuộn chậm, dissolve CoreOut | Bóng phía khuất sáng: lệch mẫu noise theo hướng đèn |

## Kết thúc (progress)

- **Fade:** `alpha *= 1 - progress`.
- **Dissolve:** `vfxDissolve(mask, progress, soft)`. `mask` từ kênh noise phù hợp:
  - Cells cho lỗ lớn/vừa/nhỏ (quy tắc art lead: lỗ không cùng cỡ cạnh nhau);
  - Streaks cho tan theo hướng.
- **Tan theo hướng:** `mask = dot(p, dir) * 0.5 + 0.5`, trộn thêm một ít noise.
- **Từ lõi ra:** `mask = 1 - length(p)`. **Từ mép vào:** `mask = length(p)`.
- **Viền tan:** `edge = shape * (1 - smoothstep(0, w, keep - 0.5))`, cộng màu viền. Chỉ thêm khi brief cần.

## Loop và one-shot

- **One-shot:** progress từ Custom1.x (curve 0→1 theo lifetime). Particle 1 burst, lifetime = thời lượng effect.
- **Loop:** dùng `_Time.y` cho cuộn noise; progress cố định hoặc `frac(_Time.y * _LoopSpeed)`. `main.loop = true`, emission rate 0 + 1 burst lặp, hoặc MeshRenderer thường.
- **Bake ra sheet** (khi cần cho mobile thật nhẹ): `ShaderSheetBaker.cs` trong `Assets/VFX/FireStylized/Editor/` (quy trình shader → bake đang thử, chưa chốt).
