import math
CT = [c for c in api.ls("Curve") if c.startswith("CTL_") and c != "CTL_Main"]
def setpose(d):
    for c in CT: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    for c, v in d.items(): api.rotate(c, v[0], v[1], v[2])
    api.set_frame(3); api.set_frame(0)
o = "Pet_lucky_neko"; o2 = "Pet_lucky_neko.001"; setpose({})
md = api.mesh_data(o); idx = list(md['vertices']); P = md['positions']; P0 = [P[i*3:i*3+3] for i in range(len(idx))]
E = set(); c = 0
for s in md['face_sizes']:
    cs = md['face_corners'][c:c+s]; c += s
    for k in range(s): E.add(tuple(sorted((cs[k], cs[(k+1) % s]))))
E = sorted(E)
md2 = api.mesh_data(o2); P20 = [md2['positions'][i*3:i*3+3] for i in range(len(md2['vertices']))]
# weld by position so uv seams don't count
def test(name, d):
    setpose(d); Pf = api.mesh_data(o, True)['positions']; Q = [Pf[i*3:i*3+3] for i in range(len(idx))]
    Pf2 = api.mesh_data(o2, True)['positions']; mv2 = max(math.dist(Pf2[3*i:3*i+3], P20[i]) for i in range(len(P20)))
    bad = []; mx = 0
    for a, b in E:
        l0 = math.dist(P0[a], P0[b])
        if l0 < 0.006: continue
        r = math.dist(Q[a], Q[b]) / l0
        if r < 0.6 or r > 1.6: bad.append((round(r, 2), [round(x, 2) for x in P0[a]]))
    mvmax = max(math.dist(Q[i], P0[i]) for i in range(len(idx)))
    bad.sort(key=lambda t: abs(math.log(t[0])), reverse=True)
    print("%-14s jar-move %.3f" % (name, mv2), end=" "); print("%-14s move %.3f bad %2d %s" % (name, mvmax, len(bad), bad[:2]))
T = {"Head ry40": {"CTL_Head_M": (0, 40, 0)}, "Head rx30": {"CTL_Head_M": (30, 0, 0)}, "Head rz25": {"CTL_Head_M": (0, 0, 25)},
 "Ear1L rz-40": {"CTL_Ear1_L": (0, 0, -40)}, "Ear1L rx40": {"CTL_Ear1_L": (40, 0, 0)}, "Ear2L rx40": {"CTL_Ear2_L": (40, 0, 0)},
 "ShL rz50": {"CTL_Shoulder_L": (0, 0, 50)}, "ShL rz-50": {"CTL_Shoulder_L": (0, 0, -50)}, "ShL ry40": {"CTL_Shoulder_L": (0, 40, 0)}, "ShL rx40": {"CTL_Shoulder_L": (40, 0, 0)},
 "ElL rz60": {"CTL_Elbow_L": (0, 0, 60)}, "ElL ry60": {"CTL_Elbow_L": (0, 60, 0)}, "WrL rz40": {"CTL_Wrist_L": (0, 0, 40)}, "WrL ry40": {"CTL_Wrist_L": (0, 40, 0)},
 "ShR rz-50": {"CTL_Shoulder_R": (0, 0, -50)}, "ElR ry-60": {"CTL_Elbow_R": (0, -60, 0)},
 "HipL rx40": {"CTL_Hip_L": (40, 0, 0)}, "HipL rz30": {"CTL_Hip_L": (0, 0, 30)}, "AnkL rx35": {"CTL_Ankle_L": (35, 0, 0)}, "ToeL rx35": {"CTL_Toes_L": (35, 0, 0)}, "HipR rx40": {"CTL_Hip_R": (40, 0, 0)},
 "Tail1 ry40": {"CTL_Tail1_M": (0, 40, 0)}, "Tail1 rx40": {"CTL_Tail1_M": (-40, 0, 0)}, "Tail2 rx50": {"CTL_Tail2_M": (-50, 0, 0)}, "Tail3 ry50": {"CTL_Tail3_M": (0, 50, 0)},
 "Spine rx20": {"CTL_Spine1_M": (20, 0, 0)}, "Spine ry30": {"CTL_Spine1_M": (0, 30, 0)}, "Spine rz20": {"CTL_Spine1_M": (0, 0, 20)}, "Root rx20": {"CTL_Root_M": (20, 0, 0)},
 "Bell rx40": {"CTL_Bell_M": (40, 0, 0)}, "Bell rz40": {"CTL_Bell_M": (0, 0, 40)}, "TsA2 rz40": {"CTL_TasselA2_M": (0, 0, 40)}, "TsA1 rx40": {"CTL_TasselA1_M": (40, 0, 0)}, "TsB1 rz40": {"CTL_TasselB1_M": (0, 0, 40)}, "TsB2 rx40": {"CTL_TasselB2_M": (40, 0, 0)}, "Jar rz30": {"CTL_Jar_M": (0, 0, 30)}}
for k, v in T.items(): test(k, v)
setpose({}); print("done")
