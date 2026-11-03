"""Bộ máy dựng anim idle (loop) Spine 4.2 từ một file cấu hình nhân vật. Skill /skillidle.

Cấu hình (module Python, xem mẫu `.claude/skills/skillidle/examples/cuusakura_idle_cfg.py`) khai báo:
  PATH        đường dẫn skeleton JSON (rig đã xong)
  ANIM        tên anim (mặc định "idle")
  END         số frame một vòng loop (vd 90 / 96)
  OWN         {xương: f(t giây) -> độ}: sóng riêng (anim_kit.wave / add)
  INERTIA     {xương: (gain, trễ frame)}: quán tính theo góc thế giới của cha
  L_OVL       nhân độ trễ quán tính (tham số "lag")
  TRANSLATE   {xương: f(t) -> (x, y)} dời thêm (vd ctrl nhấp nhô)
  SCALE       {xương: f(t) -> (sx, sy)} (miệng, tóc mái...)
  CHAINS      [anim_kit.Chain]: physics tuần hoàn (khăn, vây...)
  BLINK       dict(frame=, eyes=[(slot, ảnh nhắm, ảnh mở, xương)], brows=[...], dx=-6) hoặc None
  N_KEYS      số key đều mỗi vòng cho kênh sóng (mặc định 12)
Chạy: build_idle(cfg) -> ghi anim vào PATH (giữ anim khác, có Hoàn tác trên Spine Live).
"""
import math
import anim_kit as K
from anim_kit import FPS


class IdleModel:
    """phần idle dùng lại được (active cần nó làm nền và trạng thái physics ban đầu)."""
    def __init__(self, cfg, skel):
        self.cfg, self.skel = cfg, skel
        self.rig = K.Rig(skel)
        self.N = cfg.END
        self.T = cfg.END / FPS
        self.inertia = K.Inertia(self.rig.parent, cfg.OWN, cfg.INERTIA, self.T, getattr(cfg, "L_OVL", 1.0))
        self.tr = getattr(cfg, "TRANSLATE", {})
        self.sc = getattr(cfg, "SCALE", {})
        self.chains = getattr(cfg, "CHAINS", [])
        fk = self.fk()
        self.phys = K.simulate_loop(self.rig, self.chains, fk, self.N) if self.chains else {}

    def local(self, b, t):
        return self.inertia.local(b, t)

    def translate(self, b, f):
        return self.tr[b](f / FPS) if b in self.tr else (0.0, 0.0)

    def scale(self, b, f):
        return self.sc[b](f / FPS) if b in self.sc else (1.0, 1.0)

    def fk(self):
        return self.rig.fk(lambda n, f: self.local(n, f / FPS), lambda n, f: self.translate(n, f))

    def rot(self, b, f):
        """góc idle (độ thêm) tại frame f bất kỳ (kể cả âm): physics nếu xương có trong chuỗi idle, không thì sóng."""
        if b in self.phys:
            v = self.phys[b]; N = self.N; x = f % N; i = int(x); u = x - i
            return v[i] * (1 - u) + v[min(N, i + 1)] * u
        return self.local(b, f / FPS)


def build_idle(cfg, write=True):
    skel = K.load(cfg.PATH)
    m = IdleModel(cfg, skel)
    T, END = m.T, m.N
    nk = getattr(cfg, "N_KEYS", 12)
    bones = {}
    for b in m.rig.parent:
        if b in cfg.OWN or b in cfg.INERTIA:
            bones[b] = {"rotate": K.periodic_keys(lambda t, b=b: (m.local(b, t),), ["value"], T, nk, END)}
    for b, fn in m.tr.items():
        bones.setdefault(b, {})["translate"] = K.periodic_keys(fn, ["x", "y"], T, nk, END)
    for b, fn in m.sc.items():
        bones.setdefault(b, {})["scale"] = K.periodic_keys(fn, ["x", "y"], T, nk, END)
    for b, v in m.phys.items():
        bones[b] = {"rotate": K.sample_keys(v)}
    slots = {}
    bl = getattr(cfg, "BLINK", None)
    if bl:
        bb, ss = K.blink(bl["frame"], bl["eyes"], bl.get("brows", ()), bl.get("dx", -6.0), bl.get("squash", 0.6))
        bones.update(bb); slots.update(ss)
    anim = {"bones": bones, "slots": slots}
    if write:
        K.write_anim(cfg.PATH, getattr(cfg, "ANIM", "idle"), anim, skel=skel)
        print(f"{getattr(cfg, 'ANIM', 'idle')}: {END} frame, {len(bones)} xương có key -> {cfg.PATH}")
    return anim
