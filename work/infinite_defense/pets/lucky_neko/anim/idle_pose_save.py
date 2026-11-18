# Key the idle pose at frame 0 and save as a separate file (the rig file stays clean).
# Frolvy: rotate only sticks on curves that already hold a key -> remember the pose, pre-key zeros, write the pose back, key again, verify by re-evaluating.
api.set_frame(0)
CT = [c for c in api.ls("Curve") if c.startswith("CTL_")]
A6 = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")
want = {c: [api.get_attr(c + "." + a) for a in A6] for c in CT}
for c in CT:
    api.rotate(c, 0, 0, 0); api.scale(c, 1, 1, 1)
    if c != "CTL_Main": api.move(c, 0, 0, 0)
api.select(CT); api.set_key(); api.select([])
for c in CT:
    v = want[c]; api.rotate(c, v[3], v[4], v[5]); api.move(c, v[0], v[1], v[2]); api.scale(c, v[6], v[7], v[8])
api.select(CT); api.set_key(); api.select([])
api.set_frame(5); api.set_frame(0)
bad = [c for c in CT if any(abs(api.get_attr(c + "." + a) - w) > 0.01 for a, w in zip(A6, want[c]))]
print("keys differ from the pose on:", bad)
api.select(list(api.ls('Curve')) + list(api.ls('Joint'))); api.hide(False); api.select([])
api.look_through('persp')
print(api.check_rig())
print(api.save_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_14_Lucky_Neko\lucky_neko_idle_pose.fv"))
