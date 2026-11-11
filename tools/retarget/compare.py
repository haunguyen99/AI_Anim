"""So hai FBX cùng khung xương team (vd bản retarget tự động với bản team làm tay): lệch hướng từng đoạn xương (độ),
độ cao hông, độ cao + trượt bàn chân mỗi frame.
    .venv/Scripts/python.exe -I tools/retarget/compare.py <a.fbx> <b.fbx> [--fps 30] [--json out.json]"""
import argparse, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import fbx_fast, fbxanim
fbxanim.fbxread.read = fbx_fast.read
from retarget import world_at, src_frames

SEG = [("Root_M", "Spine2_M", "hông→eo"), ("Spine2_M", "Chest_M", "eo→ngực"), ("Chest_M", "Neck_M", "ngực→cổ"),
       ("Neck_M", "Head_M", "cổ→đầu"),
       ("Shoulder_L", "Elbow_L", "cánh tay T"), ("Elbow_L", "Wrist_L", "cẳng tay T"), ("Wrist_L", "MiddleFinger1_L", "bàn tay T"),
       ("Shoulder_R", "Elbow_R", "cánh tay P"), ("Elbow_R", "Wrist_R", "cẳng tay P"), ("Wrist_R", "MiddleFinger1_R", "bàn tay P"),
       ("Hip_L", "Knee_L", "đùi T"), ("Knee_L", "Ankle_L", "ống chân T"), ("Ankle_L", "Toes_L", "bàn chân T"),
       ("Hip_R", "Knee_R", "đùi P"), ("Knee_R", "Ankle_R", "ống chân P"), ("Ankle_R", "Toes_R", "bàn chân P")]


def track(path, fps):
    m, par = fbxanim.load(path)
    nm = {k: v["name"] for k, v in m.items()}
    secs = src_frames(m)
    n = int(round((secs[-1] - secs[0]) * fps)) + 1
    out = []
    for f in range(n):
        W = world_at(m, par, secs[0] + f / fps)
        out.append({nm[k]: v for k, v in W.items()})
    return out


def ang(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b)
    return np.degrees(np.arccos(np.clip(np.dot(a, b), -1, 1)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--json")
    a = ap.parse_args()
    A, B = track(a.a, a.fps), track(a.b, a.fps)
    n = min(len(A), len(B))
    print("frame: %d vs %d" % (len(A), len(B)))
    rep = {"seg": {}, "frames": n}
    print("%-12s %8s %8s" % ("đoạn", "TB (°)", "max (°)"))
    for p, c, lab in SEG:
        d = [ang(A[f][c][:3, 3] - A[f][p][:3, 3], B[f][c][:3, 3] - B[f][p][:3, 3]) for f in range(n)]
        rep["seg"][lab] = [float(np.mean(d)), float(np.max(d)), int(np.argmax(d))]
        print("%-12s %8.1f %8.1f  (F%d)" % (lab, np.mean(d), np.max(d), np.argmax(d) + 1))
    for lab, X in (("A", A), ("B", B)):
        h = np.array([X[f]["Root_M"][:3, 3] for f in range(n)])
        print("%s hông: cao %.1f–%.1f cm (nhún %.1f), dời ngang x %.1f–%.1f z %.1f–%.1f" %
              (lab, h[:, 1].min(), h[:, 1].max(), np.ptp(h[:, 1]), h[:, 0].min(), h[:, 0].max(), h[:, 2].min(), h[:, 2].max()))
        for side in ("L", "R"):
            t = np.array([X[f]["Toes_" + side][:3, 3] for f in range(n)])
            k = np.array([X[f]["Ankle_" + side][:3, 3] for f in range(n)])
            low = np.minimum(t[:, 1], k[:, 1])
            print("   chân %s: thấp nhất %.1f cm (F%d), sải trước-sau (z cổ chân) %.1f cm" %
                  (side, low.min(), np.argmin(low) + 1, np.ptp(k[:, 2])))
        rep[lab] = {"hip_y": h[:, 1].tolist()}
    if a.json:
        json.dump(rep, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
