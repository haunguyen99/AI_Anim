# Key the pose as it is now (all controls, frame 0), verify by re-evaluating, save to the idle pose file.
api.set_frame(0)
CT = [c for c in api.ls("Curve") if c.startswith("CTL_")]
A9 = ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz")
want = {c: [api.get_attr(c + "." + a) for a in A9] for c in CT}
api.select(CT); api.set_key(); api.select([])
api.set_frame(5); api.set_frame(0)
bad = [c for c in CT if any(abs(api.get_attr(c + "." + a) - w) > 0.01 for a, w in zip(A9, want[c]))]
print("keys differ from the pose on:", bad); print(api.check_rig())
