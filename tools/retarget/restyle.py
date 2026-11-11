"""Chỉnh anim thư viện (đã retarget sang xương team) theo style game: dáng từ clip team, chuyển động từ thư viện.

  dáng gốc   = một frame của clip team (vd Idle1 F1): thế đứng, thân, đầu, tay, ngón, cách cầm prop của game
  chuyển động = độ lệch từng frame của bản retarget so với dáng trung bình của nó, nhân hệ số k
               (k tự tính = biên độ clip team / biên độ thư viện, đo ở ngực + độ nhún hông: idle game không diễn thừa)
  rồi: khoá bàn chân đúng chỗ của dáng gốc (IK), nối loop (frame cuối = frame đầu), prop bám xương như clip team.

    .venv/Scripts/python.exe -I tools/retarget/restyle.py --anim raw.fbx --base MC_Lumber_Idle1.fbx [--base-frame 1]
        --template MC_Lumber_Run.fbx --out styled.fbx [--k auto|0.6] [--prop accessory:Wrist_R] [--no-loop]
"""
import argparse, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, ".."))
import retarget as RT
from compare import track

LEGS = [("Hip_L", "Knee_L", "Ankle_L"), ("Hip_R", "Knee_R", "Ankle_R")]


def rot_log(R):
    c = np.clip((np.trace(R) - 1) / 2, -1, 1); a = np.arccos(c)
    if a < 1e-8:
        return np.zeros(3)
    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    if np.pi - a < 1e-4:  # gần 180°
        w, V = np.linalg.eigh((R + np.eye(3)) / 2); ax = V[:, np.argmax(w)]
        return ax * a
    return v / (2 * np.sin(a)) * a


def rot_exp(v):
    a = np.linalg.norm(v)
    return np.eye(3) if a < 1e-12 else RT.axis_angle(v / a, a)


def mean_rot(Rs):
    return RT.ortho(sum(Rs) / len(Rs))


def locals_of(W, parent, names):
    return {n: (np.linalg.inv(W[parent[n]]) @ W[n]) if n in parent else W[n].copy() for n in names}


def fk(L, parent, names):
    W = {}
    for n in names:
        W[n] = (W[parent[n]] @ L[n]) if n in parent else L[n].copy()
    return W


def amp(Wseq, joint):
    Rs = [W[joint][:3, :3] for W in Wseq]; M = mean_rot(Rs)
    return float(np.sqrt(np.mean([np.linalg.norm(rot_log(M.T @ R)) ** 2 for R in Rs])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--anim", required=True); ap.add_argument("--base", required=True)
    ap.add_argument("--base-frame", type=int, default=1); ap.add_argument("--template", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--k", default="auto")
    ap.add_argument("--prop", default="accessory:Wrist_R", help="xương prop:xương nó bám (lấy offset từ clip team); '' = bỏ")
    ap.add_argument("--no-loop", action="store_true"); ap.add_argument("--mul", default="", help="nhân thêm hệ số từng xương sau perbone, vd Chest_M=0.5,Shoulder_R=1.5"); ap.add_argument("--fps", type=int, default=30)
    a = ap.parse_args()

    T, Tpar, Tnm, Tby = RT.load_skel(a.template)
    order = []

    def visit(k):
        order.append(k)
        for c in [c for c, p in Tpar.items() if p == k and c in T]:
            visit(c)
    for k in T:
        if k not in Tpar or Tpar[k] not in T:
            visit(k)
    names = [Tnm[k] for k in order]
    parent = {Tnm[k]: Tnm[Tpar[k]] for k in order if k in Tpar and Tpar[k] in T}

    raw = track(a.anim, a.fps); base_all = track(a.base, a.fps)
    WB = base_all[a.base_frame - 1]
    n = len(raw)
    Lraw = [locals_of(W, parent, names) for W in raw]
    LB = locals_of(WB, parent, names)

    # hệ số chuyển động: biên độ clip team / thư viện (ngực = thở + lắc thân; hông = nhún)
    kb = None
    if a.k == "perbone":
        # hệ số riêng từng xương = biên độ (local) clip team / thư viện; chân khoá; cổ ≤ 1,5 × ngực (Director 2026-11-10)
        def ampL(seq, nm):
            Rs = [L[nm][:3, :3] for L in seq]; M = mean_rot(Rs)
            return float(np.sqrt(np.mean([np.linalg.norm(rot_log(M.T @ R)) ** 2 for R in Rs])))
        Lbase_all = [locals_of(W, parent, names) for W in base_all]
        kb = {}
        for nm in names:
            if any(x in nm for x in ("Hip", "Knee", "Ankle", "Toes")) or nm in ("root", "Root_M") or not nm[0].isupper():
                kb[nm] = 0.0 if nm != "Root_M" else 1.0
                continue
            ar = ampL(Lraw, nm)
            kb[nm] = float(np.clip(ampL(Lbase_all, nm) / ar, 0.0, 5.0)) if ar > np.radians(0.05) else 0.0
        if "Neck_M" in kb and "Chest_M" in kb:
            an = ampL(Lraw, "Neck_M") * kb["Neck_M"]; ac = ampL(Lraw, "Chest_M") * kb["Chest_M"]
            if an > 1.5 * ac and an > 0:
                kb["Neck_M"] *= 1.5 * ac / an
        kb["Root_M"] = float(np.clip(amp(base_all, "Root_M") / max(amp(raw, "Root_M"), 1e-6), 0, 5))
        hb = np.ptp([W["Root_M"][1, 3] for W in base_all]); hr = np.ptp([W["Root_M"][1, 3] for W in raw])
        kt = float(np.clip(hb / max(hr, 1e-6), 0.0, 1.5)); k = 1.0
        for kv in filter(None, a.mul.split(",")):
            nm_, v_ = kv.split("="); kb[nm_] = kb.get(nm_, 0.0) * float(v_)
        print("hệ số từng xương: " + ", ".join("%s %.2f" % (x, kb[x]) for x in ("Root_M", "Spine2_M", "Chest_M", "Neck_M", "Head_M", "Scapula_L", "Shoulder_L", "Elbow_L", "Wrist_L", "Scapula_R", "Shoulder_R", "Elbow_R", "Wrist_R") if x in kb) + "; hông dời %.2f" % kt)
    elif a.k == "auto":
        kc = amp(base_all, "Chest_M") / max(amp(raw, "Chest_M"), 1e-6)
        hb = np.ptp([W["Root_M"][1, 3] for W in base_all]); hr = np.ptp([W["Root_M"][1, 3] for W in raw])
        kh = hb / max(hr, 1e-6)
        k = float(np.clip(kc, 0.2, 1.5)); kt = float(np.clip(kh, 0.0, 1.5))
        print("biên độ ngực: team %.2f° / thư viện %.2f° → k xoay %.2f; nhún hông: team %.1f / thư viện %.1f cm → k hông %.2f"
              % (np.degrees(amp(base_all, "Chest_M")), np.degrees(amp(raw, "Chest_M")), k, hb, hr, kt))
    else:
        k = kt = float(a.k)

    # độ lệch quanh dáng trung bình của thư viện; nối loop: trải phần dư frame cuối → đầu đều cả clip
    Rm = {nm: mean_rot([L[nm][:3, :3] for L in Lraw]) for nm in names}
    tm = np.mean([L["Root_M"][:3, 3] for L in Lraw], axis=0)
    dlt = [{nm: rot_log(Rm[nm].T @ L[nm][:3, :3]) for nm in names} for L in Lraw]
    dt = [L["Root_M"][:3, 3] - tm for L in Lraw]
    if not a.no_loop and n > 2:
        for nm in names:
            res = dlt[-1][nm] - dlt[0][nm]
            for f in range(n):
                dlt[f][nm] = dlt[f][nm] - res * f / (n - 1)
        res = dt[-1] - dt[0]
        for f in range(n):
            dt[f] = dt[f] - res * f / (n - 1)

    prop = a.prop.split(":") if a.prop else None
    G = (np.linalg.inv(WB[prop[1]]) @ WB[prop[0]]) if prop else None
    frames = []
    feet = {an: WB[an].copy() for _, _, an in LEGS}
    for f in range(n):
        L = {nm: LB[nm].copy() for nm in names}
        for nm in names:
            L[nm][:3, :3] = LB[nm][:3, :3] @ rot_exp((kb[nm] if kb else k) * dlt[f][nm])
        L["Root_M"][:3, 3] = LB["Root_M"][:3, 3] + kt * dt[f]
        W = fk(L, parent, names)
        # khoá bàn chân: cổ chân về đúng chỗ + hướng của dáng gốc, gối giải IK (giữ hướng gối hiện tại)
        for th, kn, an in LEGS:
            H = W[th][:3, 3]; A = feet[an][:3, 3]
            l1 = np.linalg.norm(W[kn][:3, 3] - H); l2 = np.linalg.norm(W[an][:3, 3] - W[kn][:3, 3])
            d = A - H; dist = min(np.linalg.norm(d), 0.999 * (l1 + l2)); u = d / np.linalg.norm(d)
            pole = (W[kn][:3, 3] - H); pole -= np.dot(pole, u) * u; pole /= np.linalg.norm(pole)
            x = (l1 ** 2 - l2 ** 2 + dist ** 2) / (2 * dist)
            K = H + u * x + pole * np.sqrt(max(l1 ** 2 - x ** 2, 0.0))
            Q = RT.rot_between(W[kn][:3, 3] - H, K - H)
            Wt = W[th].copy(); Wt[:3, :3] = Q @ Wt[:3, :3]
            L[th] = np.linalg.inv(W[parent[th]]) @ Wt
            W = fk(L, parent, names)
            Q2 = RT.rot_between(W[an][:3, 3] - W[kn][:3, 3], H + u * dist - W[kn][:3, 3])
            Wk = W[kn].copy(); Wk[:3, :3] = Q2 @ Wk[:3, :3]
            L[kn] = np.linalg.inv(W[parent[kn]]) @ Wk
            W = fk(L, parent, names)
            Wa = W[an].copy(); Wa[:3, :3] = feet[an][:3, :3]
            L[an] = np.linalg.inv(W[parent[an]]) @ Wa
            W = fk(L, parent, names)
        if prop:
            Wp = W[prop[1]] @ G
            L[prop[0]] = np.linalg.inv(W[parent[prop[0]]]) @ Wp if prop[0] in parent else Wp
        frames.append(L)
    res = dict(names=names, parent=parent, frames=frames, fps=a.fps, T=T, Tby=Tby, nfr=n)
    nc = RT.write(res, a.template, a.out)
    print("ghi %s: %d frame, %d đường cong, k = %.2f" % (a.out, n, nc, k))


if __name__ == "__main__":
    main()
