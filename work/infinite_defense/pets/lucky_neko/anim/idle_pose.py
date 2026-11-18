# Lucky Neko idle key pose (ref: Tripo maneki-neko, ref/tripo_ref.png). Face +Z, character RIGHT = -X.
# Jar sits on the back (ref side view). Right paw raised beside the cheek (wave), left paw rests on the coin held in front, facing the front (user 2026-11-14), tail curled into a question mark, body hovering 12 cm.
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\lucky_neko\pose_lib.py", encoding="utf-8").read())
HOVER = 0.12
zero_all()
R = lambda c, *v: api.rotate("CTL_" + c, *v)
# torso / head
R("Spine1_M", 6, 0, 0); R("Head_M", 8, 0, 3)
# right (waving) arm: elbow forward-out, forearm up beside the cheek
api.rotate("CTL_Shoulder_R", 0, 30, 45); refresh()
r1, p1 = solve_rot("CTL_Shoulder_R", "DEF_Elbow_R", (-0.150, 0.205, 0.060), start=(0, 30, 40))
r2, p2 = solve_rot("CTL_Elbow_R", "DEF_Wrist_R", (-0.164, 0.245, 0.074), start=(0, 0, -90))
# left arm: forward, paw on top of the coin
r3, p3 = solve_rot("CTL_Shoulder_L", "DEF_Elbow_L", (0.130, 0.205, 0.075), start=(0, -60, -10))
r4, p4 = solve_rot("CTL_Elbow_L", "DEF_Wrist_L", (0.170, 0.225, 0.110), start=(0, 0, 0))
# coin: undo the arm yaw so it faces front, facing the front
api.rotate("CTL_Coin_L", 0, 0, 0); refresh()
import math
cry = 0.0
for k in range(4):
    m = api.world_matrix("DEF_Coin_L")
    yaw = math.degrees(math.atan2(m[8], m[10]))               # current world yaw of the coin's z axis
    cry += -yaw; api.rotate("CTL_Coin_L", 0, cry, 0); refresh()
COIN_S = 0.66                                                     # ref: coin diameter ~ 0.32 of the cat height (model coin is 0.25 m = 0.47) -> 0.17 m
api.scale("CTL_Coin_L", COIN_S, COIN_S, COIN_S); refresh()
t5, p5 = solve_move("CTL_Coin_L", "DEF_Coin_L", (0.15, 0.13, 0.165))
# legs dangle (hover), slightly forward
R("Hip_L", -20, 0, -4); R("Ankle_L", 15, 0, 0); R("Hip_R", -15, 0, 4); R("Ankle_R", 10, 0, 0)
# tail: sticks out backwards under the jar, tip curling up (ref side view)
R("Tail1_M", -12, 0, 0); R("Tail2_M", -5, 0, 0); R("Tail3_M", 18, 0, 0)
# jar on the back (ref side view): upright, centre ~ (0, 0.20, -0.175), a small lean back
api.rotate("CTL_Jar_M", -6, 0, 0); refresh()
tj, pj = solve_move("CTL_Jar_M", "DEF_Jar_M", (0.0, 0.20, -0.155))
# hover
api.move("CTL_Root_M", 0, HOVER, 0)
refresh()
print("R sh", [round(x, 1) for x in r1], [round(x, 3) for x in p1]); print("R el", [round(x, 1) for x in r2], [round(x, 3) for x in p2])
print("L sh", [round(x, 1) for x in r3], [round(x, 3) for x in p3]); print("L el", [round(x, 1) for x in r4], [round(x, 3) for x in p4])
print("jar", [round(x, 3) for x in tj], [round(x, 3) for x in pj]); print("coin", [round(x, 3) for x in t5], [round(x, 3) for x in p5])
