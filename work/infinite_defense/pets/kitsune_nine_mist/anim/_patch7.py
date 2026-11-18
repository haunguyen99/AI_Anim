s = open("attack.py", encoding="utf-8").read()
a = s.index("def build_atk(api):")
new = r'''# ---- cụm đuôi hạ xuống sau lưng (pitch cả bó quanh trục X thế giới quanh gốc từng đuôi) ----
PITCH = -105.0   # độ; -90 = nằm ngang ra sau, -105 = hơi chúc xuống
TP = [(0, 0), (3, 0.35), (6, 0.9), (7, 1.0), (8.5, 1.0), (10.5, 0.0), (30, 0)]
def _rx(a):
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a)); return [[1, 0, 0], [0, c, -s_], [0, s_, c]]
def _ry(a):
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a)); return [[c, 0, s_], [0, 1, 0], [-s_, 0, c]]
def _rz(a):
    c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a)); return [[c, -s_, 0], [s_, c, 0], [0, 0, 1]]
def _mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def _euler(M):   # R = Rz Ry Rx (Maya XYZ)
    b = math.asin(max(-1.0, min(1.0, -M[2][0]))); a = math.atan2(M[2][1], M[2][2]); c = math.atan2(M[1][0], M[0][0])
    return [math.degrees(a), math.degrees(b), math.degrees(c)]
def pitch_tails(P, alphas, f):
    w = T(TP, f)
    if abs(w) < 1e-6: return
    th = PITCH * w
    for (k, s), al in alphas.items():
        c_ = P["CTL_Tail%d_1_%s" % (k, s)]
        Rex = _mm(_rz(c_[2]), _mm(_ry(c_[1]), _rx(c_[0])))
        L = _mm(_rz(-al), _mm(_rx(th), _rz(al)))
        c_[0], c_[1], c_[2] = _euler(_mm(L, Rex))
def build_atk(api):
    api.set_frame_range(0, N); api.set_frame(1)
    for f in range(0, N + 1):
        api.set_frame(f); api.select(KEYED); api.set_key()
    for f in range(0, N + 1):
        api.set_frame(f); P, fan = pose_atk(f)
        api.set_attr("CTL_TailFan.fan", fan)
        al = {}
        for k, s in TAILS:
            al[(k, s)] = 0.0 if k == 1 else api.get_attr("CTL_Tail%d_1_%s_grp.rz" % (k, s))
        pitch_tails(P, al, f)
        apply(api, P, fan); api.select(KEYED); api.set_key()
    api.set_frame(1); api.set_frame(0); api.select([])
'''
s = s[:a] + new
open("attack.py", "w", encoding="utf-8").write(s)
