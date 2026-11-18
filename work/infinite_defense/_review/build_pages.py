"""Dựng BAO_CAO.html (trang báo cáo) và SLIDE.html (deck 16:9) cho Ninja từ stats_all.json + stats_frolvy.json."""
import json
A = json.load(open("stats_all.json", encoding="utf-8"))
F = json.load(open("stats_frolvy.json", encoding="utf-8"))


def fmt(x):
    x = int(round(x))
    return "%d g %02d′" % (x // 3600, x % 3600 // 60) if x >= 3600 else "%d′%02d″" % (x // 60, x % 60)


genS, humS = A["total"]["gen"], A["total"]["human"]
genF, humF = F["total"]["gen"], F["total"]["human"]
T = dict(turns=A["total"]["turns"] + F["total"]["turns"], gen=genS + genF, hum=humS + humF)
phS = list(A["phases"].items())
phF = list(F["phases"].items())
VID = [("v/idle_pb1.mp4", "v/idle_pb1.jpg", "Idle polish bản đầu", "29/10 15:01"),
       ("v/idle_pb2.mp4", "v/idle_pb2.jpg", "Idle sau góp ý tay", "29/10 16:25"),
       ("v/idle_pb3.mp4", "v/idle_pb3.jpg", "polish_v4", "29/10 16:30"),
       ("v/idle_pb4.mp4", "v/idle_pb4.jpg", "polish_v4 sửa loop F1–F40", "29/10 16:48")]
VID_A = [("v/attack_b_v2.mp4", "v/attack_b_v2.jpg", "Attack blocking b_v2", "30/10 sáng"),
         ("v/attack_polish_v5.mp4", "v/attack_polish_v5.jpg", "polish_v5: overlap thân bằng lò xo", "30/10"),
         ("v/attack_polish_v8.mp4", "v/attack_polish_v8.jpg", "polish_v8: khăn tung trái phải", "30/10"),
         ("v/attack_polish_v12.mp4", "v/attack_polish_v12.jpg", "polish_v12: BẢN CHỐT (overlap lắng tới F30)", "30/10"),
         ("v/attack_polish_v14.mp4", "v/attack_polish_v14.jpg", "polish_v14: không dùng (sửa theo Director)", "30/10 16:34")]
VID_S = [("v/skill1_blocking_v6.mp4", "v/skill1_blocking_v6.jpg", "Skill 1 blocking v6", "3/11 (chiếu chậm ×3)"),
         ("v/skill1_blocking_v7.mp4", "v/skill1_blocking_v7.jpg", "Skill 1 blocking v7: kunai 1,5 m/frame", "4/11 (chậm ×3)"),
         ("v/skill1_refine.mp4", "v/skill1_refine.jpg", "Skill 1 Refine (bản người lưu)", "4/11 (chậm ×3)")]
STRONG = [("Sửa số lớn, đo trước/sau", "Hạ hông 8 cm, gối 40° → 80° trong 1 lượt 2′48″; skin vai/khuỷu đo bằng lbs_test.py."),
          ("Tự kiểm bằng số", "pose_check.py (xuyên mesh, giãn da, chân chạm sàn), so key bằng golden file, đọc lại 41 frame khăn."),
          ("Học theo người", "Sau khi người tự key F1 Idle, AI đo chênh từng bộ phận và giữ pose đó; Attack F1/F25/F30 trùng Idle, lệch ≤ 0,02 cm."),
          ("Skill 1 từ GDD đến FBX ~1 ngày", "3/11 16:00 → 4/11 16:39: 5 key pose, 24F, refine v1–v4, 2 FBX (kunai bay và kunai trong tay).")]
WEAK = [("Ghi đè công sức người", "28/10 ghi đè khớp người vừa sửa; 30/10 v7 đổi pose đã duyệt; 4/11 phải lùi về blocking hai lần."),
        ("Khăn mất ~3 g", "Attack riêng khăn v6 → v12: lúc cứng (5–15°), lúc lắc vụn (6 lớp chồng). Chỉ ổn khi dùng mô phỏng lò xo + video tham khảo."),
        ("Nhầm tay ném kunai", "3/11 dựng ném bằng tay kia; người: \"tay ném kunai là tay đang cầm vũ khí mà\". Tay Attack 30/10 cũng xoắn 5 lần."),
        ("Key sai chỗ, mất pose", "3/11 15:47: báo đã key f0 nhưng người không thấy; key lại thì mất pose Idle. Người nhắc 3 lần."),
        ("Mất ~1 g 8′ vì đứt kết nối", "ECONNRESET, Home tắt, MCP Frolvy đứt ~8 lượt; log đếm sai 3 lượt hàng chục giờ."),
        ("Director và người lệch ý", "Director chấm v12 \"cần sửa\"; v13, v14 sửa theo Director nhưng người vẫn chốt v12.")]
HUMAN = [("28/10 15:49", "Chỉnh khớp hông, gối, bàn tay, đuôi khăn", "3 lần"),
         ("29/10 10:49", "Tự key lại pose F1 Idle sau 6 vòng AI", "1 lần, ~10′"),
         ("28–30/10", "Vẽ ghi chú ✎ trên viewport", "22 ghi chú"),
         ("29–30/10", "Gửi video khăn tham khảo (Maya playblast)", "1 lần"),
         ("30/10", "Quyết định lùi / loại bản (v7)", "4 lần"),
         ("4/11 09:33", "Tự chỉnh chi tiết pose Skill 1, bảo AI học theo", "1 lần"),
         ("4/11 14:58", "Tự lưu refine_v4 (AI không được ghi đè), bảo xuất FBX", "1 lần"),
         ("3–4/11", "Nhắc \"về bản đã chốt\"", "2 lần")]
CSS = """:root{--bg:#f4f6f8;--s:#fff;--fg:#1d2530;--m:#5b6676;--l:#dde2e8;--ok:#2e7d4f;--bad:#c2492e}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.6 'Be Vietnam Pro','Segoe UI',system-ui,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:40px 16px 64px}h1{font-size:30px;margin:0}h2{font-size:21px;margin:36px 0 14px}.lead{color:var(--m);margin-top:8px}
.num{font-family:'JetBrains Mono',Consolas,monospace}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:22px}
.stat{background:var(--s);border:1px solid var(--l);border-radius:10px;padding:14px 16px}.stat b{display:block;font:600 26px 'JetBrains Mono',Consolas,monospace}.stat span{color:var(--m);font-size:13.5px}
table{border-collapse:collapse;width:100%;background:var(--s);border:1px solid var(--l);font-size:14px}th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--l);vertical-align:top}th{color:var(--m);font-weight:600}
.vids{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}.vid{background:var(--s);border:1px solid var(--l);border-radius:10px;padding:10px}.vid video{width:100%;border-radius:6px}.vid p{margin:6px 2px 0;font-size:13.5px;color:var(--m)}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:760px){.cols{grid-template-columns:1fr}}.card{background:var(--s);border:1px solid var(--l);border-radius:10px;padding:14px 18px}
.card.ok{border-top:4px solid var(--ok)}.card.bad{border-top:4px solid var(--bad)}.card h3{margin:0 0 8px;font-size:16px}.card li{margin:0 0 8px}ul{padding-left:18px;margin:0}small{color:var(--m)}"""


def tab(head, rows):
    return "<table><tr>" + "".join(f"<th>{h}</th>" for h in head) + "</tr>" + "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</table>"


def phrows(ph):
    return [[k, v["turns"], f"<span class=num>{fmt(v['gen'])}</span>", f"<span class=num>{fmt(v['human'])}</span>"] for k, v in ph]


def vh(L): return "".join(f"<div class=vid><video src=\"{v}\" poster=\"{p}\" controls loop muted playsinline></video><p><b>{t}</b> · {w}</p></div>" for v, p, t, w in L)
vids_html = vh(VID)
strong_html = "".join(f"<li><b>{a}</b><br>{b}</li>" for a, b in STRONG)
weak_html = "".join(f"<li><b>{a}</b><br>{b}</li>" for a, b in WEAK)
page = f"""<!doctype html><html lang=vi><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1"><title>Báo cáo Ninja</title>
<link rel=stylesheet href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap"><style>{CSS}</style><div class=wrap>
<h1>Báo cáo Ninja (Infinite Defense, 3D)</h1><p class=lead>Idle + Attack trong Studio (28–30/10) và Skill 1 trong Frolvy (3–4/11). Số liệu tính từ log 9 phiên Claude bằng tools/report/session_stats.py.</p>
<div class=stats><div class=stat><b>{T['turns']}</b><span>lượt prompt</span></div><div class=stat><b>{fmt(T['gen'])}</b><span>AI gen</span></div><div class=stat><b>{fmt(T['hum'])}</b><span>người (≤ 15′ giữa lượt)</span></div><div class=stat><b>22</b><span>ghi chú vẽ trong Studio</span></div></div>
<h2>Thời gian theo giai đoạn</h2><h3>Studio 28–30/10</h3>{tab(['Giai đoạn', 'Lượt', 'AI gen', 'Người'], phrows(phS))}
<h3 style="margin-top:18px">Frolvy 3–4/11</h3>{tab(['Giai đoạn', 'Lượt', 'AI gen', 'Người'], phrows(phF))}
<p><small>Đã hiệu chỉnh 3 lượt Studio bị log đếm sai vì treo qua đêm (14 g 22′ → 5′24″, 144′ → 13′30″, 14 g 43′ → 38′36″). Phiên S1 và S2 chạy song song 29/10 14:40–17:06 nên "người" của hai phiên chồng nhau.</small></p>
<h2>Video Idle</h2><div class=vids>{vids_html}</div><h2>Video Attack</h2><div class=vids>{vh(VID_A)}</div><h2>Video Skill 1 (Frolvy)</h2><div class=vids>{vh(VID_S)}</div>
<p><small>Skill 1 quay lại từ các file .fv còn trong thư mục (refine v1–v4 và blocking v5 đã bị xoá). FBX giao: Ninja_Skill1.fbx, Ninja_Skill1_KunaiInHand.fbx.</small></p>
<h2>Mạnh / Yếu của AI</h2><div class=cols><div class="card ok"><h3>Làm tốt</h3><ul>{strong_html}</ul></div><div class="card bad"><h3>Còn vướng</h3><ul>{weak_html}</ul></div></div>
<h2>Người vẫn phải làm</h2>{tab(['Khi nào', 'Làm gì', 'Số lượng'], HUMAN)}
<h2>Gợi ý lần sau</h2><ul><li>Người chốt pose F1 / key pose chính trước rồi AI mới triển khai (tiết kiệm ~1 g 20′ của F1 Idle).</li><li>Đưa video tham khảo khăn ngay từ polish đầu.</li><li>Luật cứng: chỉ thêm overlap / breakdown, không đổi pose đã duyệt; làm trên bản copy.</li><li>Báo trước khi gặp đứt kết nối thay vì thử lại nhiều lần.</li></ul>
<h2>Cách tính</h2><p><small>AI gen = prompt → tin nhắn cuối của AI trừ lúc chờ trả lời. Người = khoảng giữa hai lượt, chỉ tính ≤ 15′. Chi tiết từng lượt trong BAO_CAO.md, timeline_all.md, stats_frolvy.json.</small></p></div></html>"""
open("BAO_CAO.html", "w", encoding="utf-8").write(page)

S = []


def sl(cls, inner):
    S.append(f"<section class='{cls}'>{inner}</section>")


sl("dark", "<h1>Ninja: AI làm anim<br><span>Idle · Attack · Skill 1</span></h1><p>Infinite Defense · 28/10 – 4/11 · Studio + Frolvy</p>")
sl("", f"<h2>Tổng quan</h2><div class=big><div><b>{T['turns']}</b>lượt prompt</div><div><b>{fmt(T['gen'])}</b>AI gen</div><div><b>{fmt(T['hum'])}</b>người</div><div><b>22</b>ghi chú vẽ</div></div>"
   + tab(["", "Studio 28–30/10", "Frolvy 3–4/11"], [["Lượt", A["total"]["turns"], F["total"]["turns"]], ["AI gen", fmt(genS), fmt(genF)], ["Người", fmt(humS), fmt(humF)], ["Làm ra", "Rig, Idle 40F, Attack 30F", "Rig lại, Skill 1 24F, 2 FBX"]]))
sl("", "<h2>Thời gian theo giai đoạn</h2><div class=two>" + tab(["Studio", "Lượt", "AI gen", "Người"], phrows(phS)) + tab(["Frolvy", "Lượt", "AI gen", "Người"], phrows(phF)) + "</div>")
for ttl, L, step in (("Video Idle", VID, 2), ("Video Attack", VID_A, 2), ("Video Skill 1", VID_S, 2)):
  for i in range(0, len(L), step):
    sl("dark", f"<h2>{ttl}</h2><div class=vids>" + "".join(f"<div><video src='{v}' poster='{p}' controls loop muted playsinline></video><b>{t}</b><i>{w}</i></div>" for v, p, t, w in L[i:i + step]) + "</div>")
sl("", "<h2>AI làm tốt</h2><div class=grid>" + "".join(f"<div class=c><b>{a}</b><p>{b}</p></div>" for a, b in STRONG) + "</div>")
sl("", "<h2>Còn vướng</h2><div class=grid>" + "".join(f"<div class='c bad'><b>{a}</b><p>{b}</p></div>" for a, b in WEAK[:4]) + "</div>")
sl("", "<h2>Người vẫn phải làm</h2>" + tab(["Khi nào", "Làm gì", "Số lượng"], HUMAN[:6]))
sl("orange", "<h2>Điểm yếu lớn nhất</h2><p class=st>Lặp lại một lỗi: đổi pose người đã duyệt, hoặc chỉnh tay.<br>28/10 · 30/10 · 4/11 (hai lần).</p>")
sl("", "<h2>Đề xuất</h2><div class=two><div><h3>Người</h3><ul><li>Chốt pose chính trước</li><li>Đưa video ref khăn từ đầu</li><li>Tự lưu bản duyệt</li></ul></div><div><h3>AI / công cụ</h3><ul><li>Luật cứng: không đổi pose đã duyệt</li><li>Làm trên bản copy, ghi version mỗi lượt</li><li>Báo sớm khi đứt kết nối</li></ul></div></div>")
n = len(S)
S = [s.replace("</section>", f"<em>{i + 1} / {n}</em></section>") for i, s in enumerate(S)]
SCSS = """body{margin:0;background:#222;font-family:'Be Vietnam Pro','Segoe UI',sans-serif}section{width:min(100vw,177.8vh);aspect-ratio:16/9;margin:0 auto 12px;background:#F6F3EE;color:#13203A;padding:5% 6%;position:relative;overflow:hidden;font-size:1.7vw}
section.dark{background:#13203A;color:#F6F3EE}section.orange{background:#E5603F;color:#fff}h1{font-size:5.5vw;margin:8% 0 2%;line-height:1.1}h1 span{color:#F0B13B;font-size:3.5vw}h2{font-size:3.3vw;margin:0 0 2.5%}h3{margin:0 0 1%}
em{position:absolute;right:3%;bottom:3%;font:1.2vw monospace;opacity:.6}.big{display:grid;grid-template-columns:repeat(4,1fr);gap:2%;margin-bottom:3%}.big div{background:#fff;border-radius:10px;padding:2% 3%;color:#555}.big b{display:block;font:600 3.2vw monospace;color:#8A5208}
table{border-collapse:collapse;width:100%}th,td{text-align:left;padding:.6% 1.2%;border-bottom:1px solid #ccc;font-size:1.5vw}th{color:#777}.two{display:grid;grid-template-columns:1fr 1fr;gap:4%}.grid{display:grid;grid-template-columns:1fr 1fr;gap:3%}
.c{background:#fff;border-radius:12px;padding:3%;border-top:5px solid #2E7D5B}.c.bad{border-top-color:#C2492E}.c b{font-size:2vw}.c p{margin:.5em 0 0;font-size:1.5vw}.vids{display:grid;grid-template-columns:1fr 1fr;gap:4%}.vids video{width:100%;height:26vw;object-fit:contain;background:#1D3554;border-radius:8px}.vids b,.vids i{display:block;font-style:normal}.vids i{opacity:.7;font-size:1.3vw}
.st{font-size:3.4vw;line-height:1.4;font-weight:600}li{margin-bottom:.6em}"""
open("SLIDE.html", "w", encoding="utf-8").write(
    f"<!doctype html><html lang=vi><meta charset=utf8><meta name=viewport content='width=device-width,initial-scale=1'><title>Slide Ninja</title><link rel=stylesheet href='https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;600;700&display=swap'><style>{SCSS}</style>"
    + "".join(S) + "</html>")
print("ok", n)
