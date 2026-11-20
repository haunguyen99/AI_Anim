"""Tia sét nối 2 điểm, loop 8 frame (4×2). Kỹ thuật: fxlib.bolt (chia đôi đoạn + nhánh),
thân toon 2 lớp (viền màu dày + lõi trắng mảnh), sáng cộng dọc tia, đổi hình theo "nhịp chớp"
(giữ hình 2 frame rồi đổi seed — cách của lightning generator / Effekseer ribbon random).

Mẫu: không gian chỉ là ví dụ, effect thật phải hỏi art lead.
"""
import math

import core as cf
import fxlib as fx

META = dict(name="CFX_Lightning_Arc", size=(192, 96), origin=(16, 48), duration=8 / 30, loop=True, fps=30,
            blend="add", stepped=True,      # đổi hình theo nhịp, không chuyển động liên tục → check bỏ phép đo nối loop

            space=dict(context="dir", plane="stretch", camera="3/4 40", width_m=3.0,
                       anchor="nối 2 điểm (tay → mục tiêu)", background="dark"),
            options=dict(seed=3, length=160, hold=2, core=(1.0, 1.0, 1.0), mid=(0.55, 0.8, 1.0), outer=(0.25, 0.4, 1.0)))


def draw(cv, t, o):
    f = int(math.floor(t * 30 + 1e-6)) % 8      # frame 0..7 (floor, không round: round đẩy frame cuối sang hình mới)
    shape = f // o["hold"]                      # giữ một hình trong `hold` frame
    L = o["length"]
    segs = fx.bolt(0, 0, L, 0, seed=o["seed"] * 101 + shape, depth=6, offset=0.18, branch_p=0.45)
    flick = 1.0 if f % o["hold"] == 0 else 0.7  # frame đầu của mỗi hình sáng nhất
    # lớp sáng (mềm) trước, thân (cứng) sau
    for x0, y0, x1, y1, lv in segs:
        k = (0.55 if lv == 0 else 0.25) * flick
        cv.glow_line(x0, y0, x1, y1, 10 if lv == 0 else 5, o["outer"], k)
    for x0, y0, x1, y1, lv in segs:
        w = (2.6 if lv == 0 else 1.4 / lv) * flick
        cv.streak(x0, y0, x1, y1, w, w, o["mid"], 1.0)
    for x0, y0, x1, y1, lv in segs:
        if lv == 0:
            cv.streak(x0, y0, x1, y1, 1.0, 1.0, o["core"], 1.0)
    # chớp ở 2 đầu
    for x in (0, L):
        cv.glow(x, 0, 14, o["mid"], 0.6 * flick)
