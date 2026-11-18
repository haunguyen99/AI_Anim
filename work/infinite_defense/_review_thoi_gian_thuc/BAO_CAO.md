# Thời gian làm thực của AI và người: các phiên Pet (máy Linux, 16–17/11/2026)

**Chỉ tính thời gian làm thực:**
- **AI làm:** từ lúc gửi prompt tới tin nhắn cuối của AI trong lượt. Không tính lúc AI chờ người trả lời câu hỏi.
- **Người làm:** khoảng từ lúc AI trả lời xong tới prompt kế tiếp (xem kết quả, sửa tay, viết góp ý), chỉ tính khi khoảng này ≤ 15 phút.

**Không tính:**
- Khoảng giữa hai lượt dài hơn 15 phút (chờ, nghỉ, làm việc khác).
- Lúc chờ người trả lời câu hỏi của AI.
- Thời gian qua đêm và giữa các phiên.

**Pet 11–23 không có số.** Log phiên Claude của các pet này nằm ở máy Windows (11–14/11). Máy này không có log đó, và không có ổ Windows nào để đọc.

## Bảng
| Phiên | Lượt | AI làm | Người làm | **Tổng thực** | Không tính (chờ / nghỉ) |
|---|---:|---:|---:|---:|---:|
| Pet 25 Chrono Ouroboros v2 (17/11) | 22 | 82.3′ | 52.7′ | **135.0′ (2 g 15′)** | 263.5′ (6 khoảng, dài nhất 1 g 42′) |
| Pet 16 Wind Chameleon (17/11) | 7 | 6.2′ | 23.9′ | **30.1′** | 49.9′ (1 khoảng) |
| Pet 25 Chrono Ouroboros gốc (16/11) | 1 | 0.2′ | 0′ | **0.2′** | 0′ |
| WorkAI điều phối pet (16–17/11) | 21 | 14.0′ | 21.0′ | **35.0′** | 23 g 21′ (gồm qua đêm) |
| **Tổng có log** | **51** | **102.7′** | **97.6′** | **200.3′ (3 g 20′)** | |
| Pet 11–23 (11–14/11) | — | — | — | mất log (máy Windows không còn) | WorkAI ước lượng 18,4 g, không phải số đo |

Tỉ lệ trên phần có log: AI làm 51%, người làm 49%.

## Pet 25 v2 theo giai đoạn
| Giai đoạn | AI làm | Người làm | Tổng thực |
|---|---:|---:|---:|
| Rig v2 + dựng lại | 6.0′ | 0′ | 6.0′ |
| Rig v3 | 5.3′ | 2.2′ | 7.5′ |
| Pose idle | 16.6′ | 23.2′ | 39.8′ |
| Idle | 12.2′ | 10.4′ | 22.6′ |
| Attack | 24.8′ | 12.7′ | 37.5′ |
| Chốt + xuất FBX | 4.3′ | 2.7′ | 7.0′ |
| Việc khác (chép file, git push) | 13.0′ | 1.4′ | 14.4′ |
| **Tổng** | **82.3′** | **52.7′** | **135.0′** |

Phần anim thuần (bỏ "Việc khác"): **120.6′ (2 g 01′)**, gồm AI 69.3′ và người 51.3′.

## Lưu ý
- Lúc người tự sửa pose idle trong Frolvy (11:44 → 11:54) chỉ được tính 6.8′. Đó là phần nằm giữa hai prompt. Phần còn lại không đo được từ log.
- Pet 16 không làm anim mới: phiên chỉ kiểm mesh, UV và texture.

## Để có số Pet 11–23
Trên máy Windows, chép thư mục `C:\Users\<tên>\.claude\projects\<thư mục dự án AI_animation>\` (các file `.jsonl`) sang máy này. Mình sẽ chạy cùng cách tính và điền vào bảng.
