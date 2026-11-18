s=open("attack.py",encoding="utf-8").read()
s=s.replace("ex_back = (48 if n == 0 else 10) * tk; ex_down = (-38 * TG[k] * tk) if n == 0 else (-6 * TG[k] * tk)","ex_back = 0.0; ex_down = 0.0")
s=s.replace("else: c_[0] += -back + cross - (30 if n == 0 else 8) * tk; c_[2] += down * 0.3","else: c_[0] += -back + cross; c_[2] += down * 0.3")
s=s.replace("FAN = [(0, 0), (7, -1.0),","FAN = [(0, 0), (3, -0.35), (6, -0.93), (7, -0.96), (8.5, -0.96),")
s=s.replace("CURL = [(0, 0), (3, 0.5), (6, 1.55), (7, 1.7), (8.5, 1.7), (10, -0.2),","CURL = [(0, 0), (8.5, 0.0), (10, -0.2),")
open("attack.py","w",encoding="utf-8").write(s)
r=open("run_attack.py",encoding="utf-8").read()
add = r'''# fan = -1 khép HẲN: mọi đuôi dựng thẳng thành một bó sau lưng (rig gốc chỉ khép 55%)
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())
for t in TAILS:
    if t['k'] == 1: continue
    P0_, P3_ = t['J'][0], t['tip']; phi = abs(math.degrees(math.atan2(P3_[0] - P0_[0], P3_[1] - P0_[1]))); sg = 1 if t['s'] == "L" else -1
    api.set_driven_key("CTL_TailFan.fan", "CTL_Tail%d_1_%s_grp.rz" % (t['k'], t['s']), -1.0, sg * 0.95 * phi)
build_atk(api)'''
r=r.replace("build_atk(api)",add,1)
open("run_attack.py","w",encoding="utf-8").write(r)
