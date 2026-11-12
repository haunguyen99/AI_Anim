"""Frolvy: thêm key in-between (breakdown) vào Hero_Blade Attack_02, F0-18, theo nhịp key chính hiện có.

Chạy trong Frolvy (execute_code):  exec(open(r'D:/Project/AI_Anim/tools/frolvy_inbetween.py', encoding='utf-8').read()); run(api)

Không đổi giá trị key chính (0 1 2 4 6 9 18), không đụng key từ F19. Chỉ thêm key ở các frame giữa.
Thứ tự key: HIP TRƯỚC (Root_M, người dùng 2026-11-11), rồi spine chain, rồi khuỷu, rồi cổ tay. Mỗi frame giữa đều có key hip.
  M0 hip dẫn trước 0.3 frame ở F3 5 7 8 (gốc dẫn, ngọn kéo); các frame giữa còn lại key hip đúng giá trị đường cong
  M1 tay lệch nhịp: cổ tay kéo trễ (L 0.35 / R 0.2 frame), pole khuỷu dẫn trước 0.3 frame, ở F3 5 7 8
  M2 overlap thân: Spine1 -> Chest -> Neck kéo trễ dần so với hip (0.25/0.35/0.45 frame) ở F3 5 7 8
  M3 follow-through rx sau khi dừng ở F9 (Spine1 -> Chest -> Neck đến muộn dần)
Sau đó "chạm lại" mọi key <=18 của kênh đã sửa (auto tangent tính lại với đủ hai bên). Không euler_filter (từng lật cổ tay 180 độ).
"""
import math

CH = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz')
NODES = ('CTL_Root_M', 'CTL_Spine1_M', 'CTL_Chest_M', 'CTL_Neck_M', 'CTL_IKWrist_R', 'CTL_IKWrist_L', 'CTL_PoleArm_R', 'CTL_PoleArm_L')
# Cấu hình nhịp. Mặc định = nhịp cũ (key chính 0 1 2 4 6 9 18). Sau khi giãn nhịp +6 frame: set_timing(api_less) bên dưới.
MAIN = (0, 1, 2, 4, 6, 9, 18)
IB = (3, 5, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17)
MOVE = (3, 5, 7, 8)      # frame giữa nằm trong đoạn đang chuyển động (hip dẫn / tay lệch / spine trễ)
STOP = 9                 # key chính nơi chuyển động dừng (follow-through sau đó)
END = 18                 # key chính cuối của đoạn làm việc
EXTRA = (('CTL_PoleArm_R', 4),)   # (node, frame): key tx ty tz giữ pose gốc (node không có key ở frame này)


def set_timing(main, stop, extra=()):
    """main = các key chính theo nhịp mới, vd (0,2,4,7,10,15,24); stop = key dừng; extra = key giữ pose gốc."""
    global MAIN, IB, MOVE, STOP, END, EXTRA
    MAIN = tuple(main)
    END = MAIN[-1]
    STOP = stop
    IB = tuple(f for f in range(0, END + 1) if f not in MAIN)
    # đoạn chuyển động: frame giữa sau key chính thứ 3 (hip đã rơi) đến trước STOP
    MOVE = tuple(f for f in IB if MAIN[2] < f < STOP)
    EXTRA = tuple(extra)
ORDER = {'CTL_Root_M': 0, 'CTL_Spine1_M': 1, 'CTL_Chest_M': 2, 'CTL_Neck_M': 3, 'CTL_PoleArm_R': 4, 'CTL_PoleArm_L': 4, 'CTL_IKWrist_R': 5, 'CTL_IKWrist_L': 5}


def _frames(api, f):
    api.set_frame(0)
    api.set_frame(f)


def capture(api, frames=None):
    frames = range(0, END + 4) if frames is None else frames
    B = {}
    for f in frames:
        _frames(api, f)
        for nd in NODES:
            for c in CH:
                B[(nd, c, f)] = api.get_attr(nd + '.' + c)
    return B


def unrolled(B, nd, c, frames=None):
    frames = range(0, END + 4) if frames is None else frames
    v = [B[(nd, c, f)] for f in frames]
    if c[0] == 'r':
        u = [v[0]]
        for x in v[1:]:
            u.append(u[-1] + (x - u[-1] + 180) % 360 - 180)
        v = u
    return v


def plan(B):
    BASE = {(nd, c): unrolled(B, nd, c) for nd in NODES for c in CH}
    D = {}

    def add(nd, c, f, d):
        D[(nd, c, f)] = D.get((nd, c, f), 0) + d

    # M0 hip: key mọi frame giữa; dẫn trước ở F3 5 7 8
    b0 = {c: BASE[('CTL_Root_M', c)] for c in CH}
    for f in IB:
        for c in CH:
            add('CTL_Root_M', c, f, 0.3 * (b0[c][f + 1] - b0[c][f]) if f in MOVE else 0.0)
    # M1 tay lệch nhịp
    for nd, w, mode in (('CTL_IKWrist_R', 0.2, 'lag'), ('CTL_IKWrist_L', 0.35, 'lag'), ('CTL_PoleArm_R', 0.3, 'lead'), ('CTL_PoleArm_L', 0.3, 'lead')):
        for c in CH:
            b = BASE[(nd, c)]
            for f in MOVE:
                o = b[f - 1] if mode == 'lag' else b[f + 1]
                add(nd, c, f, w * (o - b[f]))
    # M2 overlap thân ở đoạn chuyển động F3 5 7 8: hip dẫn, Spine1 -> Chest -> Neck kéo trễ dần (1 frame)
    for nd, w in (('CTL_Spine1_M', 0.25), ('CTL_Chest_M', 0.35), ('CTL_Neck_M', 0.45)):
        for c in ('rx', 'ry', 'rz'):
            b = BASE[(nd, c)]
            for f in MOVE:
                add(nd, c, f, w * (b[f - 1] - b[f]))
    # M3 follow-through rx sau F9
    G = {1: 0.55, 2: 0.65, 3: 0.45, 4: 0.25, 5: 0.1}
    chest = {}
    for nd, A in (('CTL_Spine1_M', 0.8), ('CTL_Chest_M', 1.0)):
        b = BASE[(nd, 'rx')]
        v9 = b[STOP] - b[STOP - 1]
        for t, g in G.items():
            add(nd, 'rx', STOP + t, v9 * A * g)
            if nd == 'CTL_Chest_M':
                chest[STOP + t] = v9 * A * g
    for f in range(STOP + 1, END):
        if chest.get(f - 1):
            add('CTL_Neck_M', 'rx', f, 0.5 * chest[f - 1])
    return {k: v for k, v in D.items() if k[0] == 'CTL_Root_M' or (abs(v) > 0.004 and (k[1][0] == 't' or abs(v) > 0.02))}


def run(api, dry=False, only=None, frames=None):
    # only=('CTL_Root_M',): chỉ key thêm các node đó (vd bổ sung hip vào bản đã làm)
    B = capture(api)
    D = plan(B)
    if only:
        D = {k: v for k, v in D.items() if k[0] in only}
    if frames:
        D = {k: v for k, v in D.items() if k[2] in frames}
    byf = {}
    for (nd, c, f) in D:
        byf.setdefault((nd, f), set()).add(c)
    print('node-frames to key:', len(byf), 'channels:', len(D))
    if dry:
        return D
    for (nd, f), cs in sorted(byf.items(), key=lambda x: (x[0][1], ORDER[x[0][0]])):
        at = api.list_attrs(nd)
        pre = {a for a in at if f in set(int(k) for k in api.list_keys(nd + '.' + a))}
        _frames(api, f)
        api.select([nd])
        api.set_key()
        for a in at:
            if a not in cs and a not in pre:
                try:
                    api.delete_key(nd + '.' + a, f)
                except Exception:
                    pass
        for c in cs:
            api.move_key(nd + '.' + c, f, f, unrolled(B, nd, c)[f] + D[(nd, c, f)])
            api.set_key_interp(nd + '.' + c, f, 'spline')
    # node không có key ở frame chính (vd PoleArm_R F4 cũ): thêm key giữ nguyên pose gốc (bỏ qua khi chỉ bổ sung node khác)
    extras = [(n, f) for n, f in EXTRA if not only or n in only]
    for nd, f in extras:
        at = api.list_attrs(nd)
        pre = {a for a in at if f in set(int(k) for k in api.list_keys(nd + '.' + a))}
        _frames(api, f)
        api.select([nd])
        api.set_key()
        for a in at:
            if a not in ('tx', 'ty', 'tz') and a not in pre:
                try:
                    api.delete_key(nd + '.' + a, f)
                except Exception:
                    pass
        for c in ('tx', 'ty', 'tz'):
            api.move_key(nd + '.' + c, f, f, B[(nd, c, f)])
            api.set_key_interp(nd + '.' + c, f, 'spline')
    # chạm lại key <=END: auto tangent tính lại
    pairs = sorted(set((a, c) for a, c, _ in D) | {(n, c) for n, _ in extras for c in ('tx', 'ty', 'tz')})
    for _ in range(2):
        for nd, c in pairs:
            p = nd + '.' + c
            ks = [int(k) for k in sorted(api.list_keys(p), key=int) if int(k) <= END]
            vals = {}
            for f in ks:
                _frames(api, f)
                vals[f] = api.get_attr(p)
            if c[0] == 'r':
                prev = None
                for f in ks:
                    if prev is not None:
                        vals[f] = prev + (vals[f] - prev + 180) % 360 - 180
                    prev = vals[f]
            for f in ks:
                api.move_key(p, f, f, vals[f])
    # kiểm: key chính + F19-21 không đổi
    bad = []
    for f in list(MAIN) + [END + 1, END + 2, END + 3]:
        _frames(api, f)
        for nd in NODES:
            for c in CH:
                d = abs(api.get_attr(nd + '.' + c) - B[(nd, c, f)])
                if c[0] == 'r':
                    d = min(d % 360, 360 - d % 360)
                if d > (0.03 if c[0] == 't' else 0.3):
                    bad.append((nd, c, f, round(d, 3)))
    print('lệch ở key chính / F19-21:', len(bad), bad[:10])
    _frames(api, 0)
    return D
