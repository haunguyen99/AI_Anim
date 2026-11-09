"""Bộ máy dựng anim active (một lần, vào / ra từ idle F0) Spine 4.2 từ file cấu hình. Skill /skillactive.

active(f) = nền idle (hoà idle(f) -> idle(f - L) trong cửa sổ BLEND để cuối khớp idle F0 cả vị trí lẫn tốc độ)
          + lớp hành động (key mốc pose-to-pose, tắt hẳn ở F cuối)
          + physics: các chuỗi chạy tiếp từ trạng thái tuần hoàn của idle, ăn đủ chuyển động thật (cha mô phỏng trước con),
            hai đầu hoà về giá trị idle
          + key tay của người dùng (USER_KEYS): ghi y nguyên, không mô phỏng đè, physics các phần gắn trên chạy theo.

Cấu hình (module, mẫu `.claude/skills/skillactive/examples/cuusakura_active_cfg.py`):
  IDLE        module cấu hình idle (cùng nhân vật)
  ANIM        tên anim (mặc định "active");  L = số frame;  K_SCALE = L / L gốc của các mốc (giãn mốc)
  ACT_ROT     {xương: f(frame) -> độ} lớp hành động xoay
  ACT_TR      {xương: (fx(frame), fy(frame))} lớp hành động dời
  ACT_SCALE   {xương: f(frame, sx_idle, sy_idle) -> (sx, sy)}
  REST_TGT    {xương chuỗi physics: f(frame) -> độ}: đích lò xo thêm (vd spine1 tự giữ thăng bằng = -0.75 * góc ctrl)
  REST_FB     {xương chuỗi: (gain, trễ frame, xương nguồn)}: đích thêm gain * (góc nguồn so với idle) trễ (cừu theo nhịp
              quẫy thân cá); FB_GAIN nhân chung
  CHAINS      [anim_kit.Chain] theo thứ tự cha trước con (thân nhân vật trước, phụ kiện gắn trên thân sau)
  USER_KEYS   đường dẫn json {xương: {"rotate": [...]}} key người dùng sửa tay (có thể không có file)
  EYES_CLOSED dict(e0=, e1=, eyes=, brows=, dx=) nhắm mắt cười, hoặc None
  BLEND       cửa sổ (frame theo mốc gốc): base=(16, 56), env=(62, 72), phys=(0, 6, 56, 72), stiff=(0, 10, 54, 66)
"""
import json, math, os
import anim_kit as K
from anim_kit import FPS, ss
from idle_engine import IdleModel


def build_active(cfg, write=True):
    I = cfg.IDLE
    skel = K.load(I.PATH)
    m = IdleModel(I, skel)
    rig, N = m.rig, m.N
    parent, B = rig.parent, rig.B
    L, Kk = cfg.L, getattr(cfg, "K_SCALE", 1.0)
    bl = dict(base=(16, 56), env=(62, 72), phys=(0, 6, 56, 72), stiff=(0, 10, 54, 66))
    bl.update(getattr(cfg, "BLEND", {}))
    S = lambda a, b, x: ss(a * Kk, b * Kk, x)
    W = lambda f: S(*bl["base"], f)
    env = lambda f: 1 - S(*bl["env"], f)
    A = lambda f: S(bl["phys"][0], bl["phys"][1], f) * (1 - S(bl["phys"][2], bl["phys"][3], f))
    U = lambda f: S(bl["stiff"][0], bl["stiff"][1], f) * (1 - S(bl["stiff"][2], bl["stiff"][3], f))

    def base(fn, f):
        w = W(f)
        return fn(f) * (1 - w) + fn(f - L) * w if w else fn(f)

    ACT = getattr(cfg, "ACT_ROT", {})
    ACT_TR = getattr(cfg, "ACT_TR", {})
    TGT = getattr(cfg, "REST_TGT", {})
    FB = getattr(cfg, "REST_FB", {})
    FBG = getattr(cfg, "FB_GAIN", 1.0)
    chains = getattr(cfg, "CHAINS", [])
    SIM = [b for c in chains for b in c.bones]
    uk_path = getattr(cfg, "USER_KEYS", None)
    USER_KEYS = {}
    if uk_path and os.path.exists(uk_path):
        USER_KEYS = json.load(open(uk_path, encoding="utf-8"))
        USER_KEYS.pop("_note", None)
    USER_ROT = {b: K.spine_curve(v["rotate"]) for b, v in USER_KEYS.items() if "rotate" in v}

    idle_rot = m.rot

    def act_local(b, f):
        if b in USER_ROT:
            return USER_ROT[b](f)
        v = base(lambda x: idle_rot(b, x), f)
        if b in ACT:
            v += ACT[b](f) * env(f)
        return v

    def act_tr(b, f):
        ix = base(lambda x: m.translate(b, x)[0], f)
        iy = base(lambda x: m.translate(b, x)[1], f)
        if b in ACT_TR:
            fx, fy = ACT_TR[b]
            ix += fx(f); iy += fy(f)
        return ix, iy

    def tgt(b, f):
        v = TGT[b](f) if b in TGT else 0.0
        if b in FB:
            g, lg, src = FB[b]
            sf = f - lg * Kk
            v += FBG * g * (act_local(src, sf) - base(lambda x: idle_rot(src, x), sf))
        return v * env(f)

    done = {}

    def done_at(n, f):
        v = done[n]; x = min(max(f, 0.0), L); i = min(int(x), L - 1); u = x - i
        return v[i] * (1 - u) + v[i + 1] * u

    idle_fk = rig.fk(lambda n, f: idle_rot(n, f), lambda n, f: m.translate(n, f))
    act_fk = rig.fk(lambda n, f: done_at(n, f) if n in done else act_local(n, f), act_tr)

    sim = {}
    dt = 1.0 / (FPS * 8)
    for ch in chains:
        if all(b in USER_ROT for b in ch.bones):     # người dùng đã key tay: dùng đúng key đó
            for b in ch.bones:
                sim[b] = done[b] = [USER_ROT[b](f) for f in range(L + 1)]
            continue
        s = K.ChainSim(rig, ch, N, 8)
        s.init(idle_fk, 0)
        has_rest = [b in TGT or b in FB for b in ch.bones]
        own = getattr(ch, "rest", None)              # dáng nghỉ riêng khai trên Chain ở idle (vd bóng trôi, chân đá nhẹ)
        if own:   # idle dùng đúng dáng nghỉ này -> active giữ nguyên nó (+ đích TGT nếu có) để F0 trùng idle
            s.rest = own
        else:
            s.rest = lambda i, f, s=s, hr=has_rest: idle_rot(ch.bones[i], f) if hr[i] else 0.0
        for fr in range(1, 4 * N + 1):              # idle tới tuần hoàn (hết 4 vòng = idle F0)
            for k in range(8):
                s.step(idle_fk, (fr - 1 + (k + 1) / 8) % N, ch.hz, ch.zeta, dt)
        if own:
            s.rest = (lambda i, f, hr=has_rest, bs=ch.bones, own=own:
                      own(i, f) + (tgt(bs[i], f) if hr[i] else 0.0))
        else:
            s.rest = (lambda i, f, hr=has_rest, bs=ch.bones:
                      base(lambda x: idle_rot(bs[i], x), f) + tgt(bs[i], f) if hr[i] else 0.0)
        rec = {b: [] for b in ch.bones}
        last = {b: 0.0 for b in ch.bones}
        lim = ch.lim or 180.0
        for fr in range(L + 1):
            if fr:
                for k in range(8):
                    f = fr - 1 + (k + 1) / 8
                    u = U(f)
                    s.step(act_fk, f, ch.hz + (ch.hz_act - ch.hz) * u, ch.zeta + (ch.zeta_act - ch.zeta) * u, dt)
            for i, (b, v) in enumerate(zip(ch.bones, s.read(act_fk, fr))):
                iv = base(lambda x: idle_rot(b, x), fr) + (tgt(b, fr) if has_rest[i] else 0.0)
                d = v - iv
                d += 360 * round((last[b] - d) / 360)   # góc liên tục, không nhảy ±360
                last[b] = d
                rec[b].append(iv + lim * math.tanh(d / lim))
        sim.update(rec)
        for b in ch.bones:
            done[b] = [base(lambda x: idle_rot(b, x), f) * (1 - A(f)) + rec[b][f] * A(f) for f in range(L + 1)]

    def final_rot(b, f):
        if b in USER_ROT:
            return USER_ROT[b](f)
        if b in SIM:
            a = A(f)
            return base(lambda x: idle_rot(b, x), f) * (1 - a) + sim[b][f] * a
        return act_local(b, f)

    rot_bones = sorted(set(I.OWN) | set(I.INERTIA) | set(ACT) | set(SIM))
    bones = {}
    for b in rot_bones:
        bones[b] = {"rotate": K.curve_keys([[final_rot(b, f) for f in range(L + 1)]], ["value"], 0.08)}
    for b, v in USER_KEYS.items():
        bones.setdefault(b, {}).update(v)
    for b in sorted(set(m.tr) | set(ACT_TR)):
        xs, ys = zip(*[act_tr(b, f) for f in range(L + 1)])
        bones.setdefault(b, {})["translate"] = K.curve_keys([list(xs), list(ys)], ["x", "y"], 0.25)
    asc = getattr(cfg, "ACT_SCALE", {})
    for b in sorted(set(m.sc) | set(asc)):
        vals = []
        for f in range(L + 1):
            sx = base(lambda x: m.scale(b, x)[0], f); sy = base(lambda x: m.scale(b, x)[1], f)
            vals.append(asc[b](f, sx, sy) if b in asc else (sx, sy))
        xs, ys = zip(*vals)
        bones.setdefault(b, {})["scale"] = K.curve_keys([list(xs), list(ys)], ["x", "y"], 0.003)
    slots = {}
    ec = getattr(cfg, "EYES_CLOSED", None)
    if ec:
        bb, sl = K.eyes_closed(ec["e0"], ec["e1"], ec["eyes"], ec.get("brows", ()), ec.get("dx", -6.0), ec.get("squash", 0.6))
        bones.update(bb); slots.update(sl)
    anim = {"bones": bones, "slots": slots}
    if write:
        K.write_anim(I.PATH, getattr(cfg, "ANIM", "active"), anim, skel=skel)
        nk = sum(len(c) for bb in bones.values() for c in bb.values())
        print(f"{getattr(cfg, 'ANIM', 'active')}: {L} frame, {len(bones)} xương, {nk} key -> {I.PATH}")
    return anim
