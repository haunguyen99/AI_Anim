"""Pole audit: one table per clip, run BEFORE rendering a version (lesson from SDR map06, ~9 review rounds lost to free poles).
Per key: knee direction vs foot direction (deg), elbow drop below shoulder (cm), upper-arm roll vs P0 (deg).
Run inside Blender after the clip's loader (needs ARM, goto(f), done()):
    exec(open(r"E:/AI Animation/tools/blender/pole_audit.py", encoding="utf8").read()); pole_audit(KEYS)
Flags: knee > KNEE_MAX (knee not over the toes), elbow drop outside ELBOW_DROP for a free/low arm, roll jump > ROLL_JUMP between keys.
"""
import math

KNEE_MAX = 30          # deg between knee and toe direction (around the hip->ankle axis)
ELBOW_DROP = (12, 20)  # cm, free arm / arm holding something at the side (arms over the head are exempt: drop < 0)
ROLL_JUMP = 60         # deg of upper-arm roll change between neighbouring keys = the arm will twist when splined


def _p(n):
    return ARM.matrix_world @ ARM.pose.bones[n].head


def _roll(side):
    """Upper-arm roll: angle of the elbow-plane normal around the shoulder->elbow axis, in world space."""
    sh, el, wr = _p("Shoulder_" + side), _p("Elbow_" + side), _p("Wrist_" + side)
    ax = (el - sh).normalized()
    n = (el - sh).cross(wr - el)
    if n.length < 1e-6:
        return None
    ref = ARM.matrix_world.to_3x3() @ ARM.pose.bones["Chest_M"].matrix.to_3x3().col[2]
    ref = (ref - ax * ref.dot(ax)).normalized()
    n = (n - ax * n.dot(ax)).normalized()
    a = math.degrees(ref.angle(n))
    return a if ax.dot(ref.cross(n)) >= 0 else -a


def pole_audit(keys, toes=("Toes_L", "Toes_R")):
    rows, prev = [], {}
    for f in keys:
        goto(f)
        row, flags = {"f": f}, []
        for s, toe in zip("LR", toes):
            h, k, a = _p("Hip_" + s), _p("Knee_" + s), _p("Ankle_" + s)
            ax = (a - h).normalized()
            kd = (k - h) - ax * (k - h).dot(ax)
            t = (_p(toe) if toe in ARM.pose.bones else ARM.matrix_world @ ARM.pose.bones["Ankle_" + s].tail) - a
            t = t - ax * t.dot(ax)
            ang = round(math.degrees(kd.angle(t))) if kd.length > 1e-4 and t.length > 1e-4 else 0
            row["knee_" + s] = ang
            if ang > KNEE_MAX:
                flags.append(f"knee_{s} {ang}deg off the toes")
            drop = round((_p("Shoulder_" + s).z - _p("Elbow_" + s).z) * 100)
            row["drop_" + s] = drop
            r = _roll(s)
            row["roll_" + s] = None if r is None else round(r)
            if r is not None and s in prev and prev[s] is not None:
                d = abs((r - prev[s] + 180) % 360 - 180)
                if d > ROLL_JUMP:
                    flags.append(f"roll_{s} jumps {round(d)}deg from the previous key")
            prev[s] = r
        row["flags"] = flags
        rows.append(row)
    done()
    for r in rows:
        print(r["f"], {k: v for k, v in r.items() if k not in ("f", "flags")}, "  !! " + "; ".join(r["flags"]) if r["flags"] else "")
    return rows
