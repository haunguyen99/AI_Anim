exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\anim\attack.py").read())
# fan = -1 khép HẲN: mọi đuôi dựng thẳng thành một bó sau lưng (rig gốc chỉ khép 55%)
# kit_common chạy trong namespace riêng (nó cũng có biến TAILS, trùng tên với idle.py)
_ns = {"api": api}
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read(), _ns)
for t in _ns["TAILS"]:
    if t['k'] == 1: continue
    P0_, P3_ = t['J'][0], t['tip']; phi = abs(math.degrees(math.atan2(P3_[0] - P0_[0], P3_[1] - P0_[1]))); sg = 1 if t['s'] == "L" else -1
    api.set_driven_key("CTL_TailFan.fan", "CTL_Tail%d_1_%s_grp.rz" % (t['k'], t['s']), -1.0, sg * 0.95 * phi)
build_atk(api)
print("keys built", api.check_rig())
