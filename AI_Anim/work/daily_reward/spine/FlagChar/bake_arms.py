"""Nướng chuyển động IK của hai cẳng tay (arm_R, arm_L) thành KEY XOAY thật để thấy / sửa curve trong Graph, rồi tắt IK (mix 0).
Vì sao: IK tự giải góc cẳng tay nên arm_R / arm_L không có key (bấm vào IK cũng không có key: IK chỉ có timeline mix / bend).
Cách làm: (1) mix IK = 1 -> đọc góc THẾ GIỚI của chest / arm_R / arm_L mỗi frame bằng cầu nối Spine Live (runtime Spine thật, đã giải IK);
(2) góc local cộng thêm = góc thế giới arm - góc thế giới chest - góc setup; (3) giảm key (key_reduce, 0.05°); (4) ghi vào anim,
đặt mix IK = 0 -> cẳng tay chạy bằng đúng các key vừa nướng (giống hệt lúc IK, kiểm bằng so ảnh).
Chạy: .venv/Scripts/python.exe -I work/daily_reward/spine/FlagChar/bake_arms.py [idle active ...]
Trang Spine Live phải đang mở file này. idle_cfg.py / active_cfg.py tự gọi script này sau khi dựng anim (dựng lại anim xoá key tay của cẳng tay).
Sửa chuyển động cánh tay (dời grip) -> chạy lại script (hoặc dựng lại anim); sửa tay curve arm_R / arm_L thì giữ nguyên cho tới lần dựng lại."""
import json, math, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "spine")); sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.stdout.reconfigure(encoding="utf-8")
from key_reduce import reduce_keys
import anim_kit as K
J = os.path.join(HERE, "flagchar.json")
REL = os.path.relpath(J, ROOT)
PY = sys.executable
ARMS = ("arm_R", "arm_L")
LINE = re.compile(r"^\s*(\w+): thế giới \(([-\d.]+), ([-\d.]+)\) xoay ([-\d.]+)°")


def norm(a): return (a + 180.0) % 360.0 - 180.0


def save(sk, why):
    try:
        import spine_live_cmd; spine_live_cmd.claude_backup(J, why)
    except Exception as e:
        print("(backup:", e, ")")
    json.dump(sk, open(J, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def pose(anim, n):
    """{frame: {bone: góc thế giới}} cho chest / arm_R / arm_L, frame 0..n"""
    out = {}
    frames = ",".join(str(f) for f in range(n + 1))
    r = subprocess.run([PY, "-I", os.path.join(ROOT, "tools", "spine_live_cmd.py"), "pose", REL, "--anim", anim, "--frames", frames,
                        "--bones", "chest,arm_R,arm_L"], capture_output=True, text=True, cwd=ROOT, timeout=120)
    cur = None
    for ln in r.stdout.splitlines():
        m = re.match(r"^F(\d+):", ln)
        if m: cur = int(m.group(1)); out[cur] = {}; continue
        m = LINE.match(ln)
        if m and cur is not None: out[cur][m.group(1)] = float(m.group(4))
    if len(out) < n + 1 or any(len(v) < 3 for v in out.values()):
        raise RuntimeError("không đọc được pose từ Spine Live (trang đã mở file chưa?): " + (r.stdout + r.stderr)[-300:])
    return out


def main(anims):
    sk = json.load(open(J, encoding="utf-8"))
    setup = {b["name"]: b.get("rotation", 0.0) for b in sk["bones"]}
    ik_on = lambda: all(c.get("mix", 1) > 0 for c in sk["ik"])
    # (1) IK bật để đo
    if not ik_on():
        for c in sk["ik"]: c.pop("mix", None)
        save(sk, "Claude bật IK để nướng key cẳng tay")
    sk = json.load(open(J, encoding="utf-8"))
    for a in anims:                          # bỏ key tay cũ của cẳng tay để IK đo đúng (key FK bị IK ghi đè nhưng cho chắc)
        for b in ARMS: sk["animations"][a]["bones"].pop(b, None)
    save(sk, "Claude chuẩn bị nướng key cẳng tay")
    time.sleep(2.5)
    baked = {}
    for a in anims:
        dur = K.anim_len(sk["animations"][a]); n = int(round(dur * 30))
        for attempt in range(6):             # chờ trang nạp lại file: IK phải đang giải (góc thế giới khác FK ở ít nhất một frame)
            P = pose(a, n)
            diff = max(abs(norm(P[f][b] - P[f]["chest"] - setup[b])) for f in P for b in ARMS)
            if diff > 0.05 or a != "active" and attempt >= 2: break
            time.sleep(1.5)
        for b in ARMS:
            vals = [norm(P[f][b] - P[f]["chest"] - setup[b]) for f in range(n + 1)]
            for i in range(1, len(vals)):    # góc liên tục
                vals[i] = vals[i - 1] + norm(vals[i] - vals[i - 1])
            if a == "idle": vals[-1] = vals[0]
            keys = reduce_keys([vals], ["value"], 0.05, periodic=(a == "idle"))
            baked.setdefault(a, {})[b] = (keys, max(vals) - min(vals))
    sk = json.load(open(J, encoding="utf-8"))
    for a, d in baked.items():
        for b, (keys, rng) in d.items():
            sk["animations"][a].setdefault("bones", {}).setdefault(b, {})["rotate"] = keys
            print(f"{a}.{b}: {len(keys)} key, biên độ {rng:.1f}°")
    for c in sk["ik"]: c["mix"] = 0          # cẳng tay chạy bằng key vừa nướng
    save(sk, "Claude nướng key xoay cẳng tay (IK -> FK)")
    print("đã tắt IK (mix 0): arm_R / arm_L giờ có curve xoay trong Graph")


if __name__ == "__main__":
    main(sys.argv[1:] or ["idle", "active"])
