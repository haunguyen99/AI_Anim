"""Ninja Idle k10_v3: pose F1 dựng lại theo ảnh concept keys/k1r2_v1.png (user 2026-10-29: "làm lại pose … mọi thứ đều chưa ổn").
So REF|ANIM ở camera Studio `view az=40 el=30` (góc của ảnh). Mọi số là cm, trục three (Y lên, +Z trước, +X trái nhân vật).
Chạy khi Studio mở anim ninja_idle bản k10_v3, F1:  .venv/Scripts/python.exe -I -X utf8 work/infinite_defense/ninja_idle/pose_k10v3.py
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ninja_pose as N

u = N.unit
P = dict(   # = pose user tự chỉnh trên k10_v5 F1 (2026-10-29 10:49, keys/F1_user_k10_v5.json): "bạn học theo nhé"
    root_drop=7.5, root_rot=(5, -12, 0),                          # hông xoay 12° cho vai trái (tay kunai) dẫn về phía địch
    spine=(13.2, 4, -0.6), chest=(4, 4, 0), neck=(-3, 2, 0), head=(-14.9, 2.9, 0.7),   # đổ người dồn vào lưng dưới, đầu bù ngược nhìn thẳng
    ankle_L=(20, 12, 9), ankle_R=(-20, 12, -20.6), pole_L=(0.6, 0, 1), pole_R=(-0.6, 0, 1), yaw_L=15, yaw_R=-25,   # tấn so le trước–sau ~30 cm, rộng ~40 cm
    wristL_from_neck=(12.5, -32.1, 18.1), poleL=(1, -0.6, 0), blade=(0.52, -0.84, 0.17),   # nắm tay giữa bụng, khuỷu khép; kunai chĩa xuống, hơi ra ngoài
    wristR_from_root=(-30.2, 8.9, -12), poleR=(-0.6, 0, -1),     # tay phải kéo hẳn ra sau hông
    scarf1=(-44, 3, 0), scarf=((-3, 0, 0), (-3, 0, 0), (-3, 0, 0)),
    scarf_yaw=0, scarf_yaw_R=0, scarf_back=6, scarf_extra_R=(-3, 4, 0),
    scarf_exact={"Scarf1_L": (-46.86, -1.84, -12.53), "Scarf1_R": (-42, 9.68, 4.25)},   # khăn rủ ra sau, đuôi trái lệch trái (giá trị user)
)


def rest_pos(n):
    return N.REST[n][1]


def rot(v, ax, deg):
    ax = u(ax); a = np.radians(deg); return v * np.cos(a) + np.cross(ax, v) * np.sin(a) + ax * np.dot(ax, v) * (1 - np.cos(a))


def main():
    br = N.Bridge(); t3 = N.blender_to_three
    rest = N.REST; L = lambda a, b: float(np.linalg.norm(rest[a][1] - rest[b][1]))
    br.anim(do="frame", f=1)
    cur = br.read(["Root_M"])["Root_M"]["pos"][2]
    br.anim(do="pos", name="Root_M", t=[0, 0, round(74 - P["root_drop"] - cur, 3)])
    for n, k in (("Root_M", "root_rot"), ("Spine1_M", "spine"), ("Chest_M", "chest"), ("Neck_M", "neck"), ("Head_M", "head")):
        br.anim(do="rot", name=n, r=list(P[k]), abs=True)
    R = br.read(["Hip_L", "Hip_R", "Shoulder_L", "Shoulder_R", "Neck_M", "Root_M"])
    out = {}
    for s in "LR":
        hip = t3(R["Hip_" + s]["pos"]); an = np.array(P["ankle_" + s], float)
        k = N.two_bone(hip, an, L("Hip_" + s, "Knee_" + s), L("Knee_" + s, "Ankle_" + s), P["pole_" + s])
        out["leg" + s] = N.leg_fk(br, s, hip, k, an, P["yaw_" + s]); out["knee" + s] = k.round(1)
    # IK chân của Studio giữ điểm đặt bàn chân cũ: dời cổ chân về đúng điểm (giữ mặt phẳng gối vừa đặt), rồi đặt bàn chân phẳng
    import math as _m
    for s in "LR":
        an = np.array(P["ankle_" + s], float); want = [an[0], -an[2], an[1]]
        cur = br.read(["Ankle_" + s])["Ankle_" + s]["pos"]
        br.anim(do="pos", name="Ankle_" + s, t=[round(w - c, 3) for w, c in zip(want, cur)])
        a2 = _m.radians(P["yaw_" + s]) / 2; br.set_world("Ankle_" + s, np.array([0, _m.sin(a2), 0, _m.cos(a2)]))
    # tay trái: cổ tay dưới-trước cổ, khuỷu ra ngoài-xuống; kunai cầm ngược, lưỡi xuống-ngoài-trước (về phía camera trong ảnh)
    S = t3(R["Shoulder_L"]["pos"]); W = t3(R["Neck_M"]["pos"]) + np.array(P["wristL_from_neck"], float)
    E = N.two_bone(S, W, L("Shoulder_L", "Elbow_L"), L("Elbow_L", "Wrist_L"), P["poleL"])
    f = u(W - E); d = u(P["blade"]); g = -d
    ax = u(np.cross(g, f)); h = rot(f, ax, -25)
    if np.dot(h, g) > np.dot(rot(f, ax, 25), g): h = rot(f, ax, 25)
    out["armL"] = N.arm_fk(br, "L", E - S, f, h, blade_dir=d, grip_thumb=g); out["elbowL"] = E.round(1)
    # tay phải: nắm tay trước hông phải, khuỷu mở ra ngoài-sau
    S = t3(R["Shoulder_R"]["pos"]); W = t3(R["Root_M"]["pos"]) + np.array(P["wristR_from_root"], float)
    E = N.two_bone(S, W, L("Shoulder_R", "Elbow_R"), L("Elbow_R", "Wrist_R"), P["poleR"])
    f = u(W - E); n = u(np.cross(u(E - S), f)); h = rot(f, n, -10)
    out["armR"] = N.arm_fk(br, "R", E - S, f, h, palm_hint=n); out["elbowR"] = E.round(1)
    for n, r in (("MiddleFinger1_L", (0, 0, -85)), ("MiddleFinger2_L", (0, 0, -75)), ("ThumbFinger1_L", (40, 0, 0)), ("ThumbFinger2_L", (35, 0, 0)),
                 ("MiddleFinger1_R", (0, 0, 85)), ("MiddleFinger2_R", (0, 0, 75)), ("ThumbFinger1_R", (40, 0, 0)), ("ThumbFinger2_R", (35, 0, 0))):
        br.anim(do="rot", name=n, r=list(r), abs=True)
    x1, y1, z1 = P["scarf1"]
    for s, sg in (("L", -1), ("R", 1)):
        br.anim(do="rot", name="Scarf1_" + s, r=[x1, sg * y1 + (P.get("scarf_yaw_R", P.get("scarf_yaw", 0)) if s == "R" else P.get("scarf_yaw", 0)), -sg * z1], abs=True)   # roll quanh dọc đuôi để dải khăn đứng dọc, rủ xuống
        for i, (x, y, z) in enumerate(P["scarf"], 2):
            br.anim(do="rot", name=f"Scarf{i}_{s}", r=[x, sg * y, -sg * z], abs=True)
    for n, r in P.get("scarf_exact", {}).items():
        br.anim(do="rot", name=n, r=list(r), abs=True)
    # gốc đuôi khăn dời ra sau (thân đổ trước + tay phải kéo sau làm lưng lấn vào gốc khăn); chỉ dời khi chưa dời (chạy lại không cộng dồn)
    R2 = br.read(["Chest_M", "Scarf1_L", "Scarf1_R"])
    for s in "LR":
        rest = float(np.linalg.norm(rest_pos("Scarf1_" + s) - rest_pos("Chest_M")))
        now = float(np.linalg.norm(np.array(R2["Scarf1_" + s]["pos"]) - np.array(R2["Chest_M"]["pos"])))
        if abs(now - rest) < 1.0 and P.get("scarf_back"):
            ex = P.get("scarf_extra_" + s, (0, 0, 0))   # gốc đuôi phải thêm ra ngoài-sau khi khăn lắc ngang (không lấn bả vai)
            br.anim(do="pos", name="Scarf1_" + s, t=[ex[0], P["scarf_back"] + ex[1], ex[2]])
    br.anim(do="key")
    chk = br.read(["Ankle_L", "Ankle_R", "Toes_L", "Toes_R", "Knee_L", "Knee_R", "Weapon", "Wrist_R"])
    for k, v in out.items(): print(k, v)
    for k, v in chk.items(): print(k, v["pos"])


if __name__ == "__main__":
    main()
