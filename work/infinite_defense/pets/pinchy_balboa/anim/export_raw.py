"""CHOT: export raw_Attack / raw_Idle / raw_Base from the open scene (Frolvy 9885). Scene must be the clean rig; attack build is rebuilt here too."""
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\pinchy_balboa\anim\make_clips.py").read())
def drop_joint_keys():
    n = 0
    for j in api.ls("Joint"):
        for a in ("rx", "ry", "rz", "tx", "ty", "tz", "sx", "sy", "sz"):
            for f in list(api.list_keys(j + "." + a)): api.delete_key(j + "." + a, int(round(f))); n += 1
    return n
def bake_export(name, n):
    api.set_frame(1); api.set_frame(0)
    defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
    api.set_frame_range(0, n)
    print(name, 'bake', api.bake_keys(defs, 0, n, 1, 'all', True), 'export', api.export_scene(D + r"\raw_%s.fbx" % name, 'fbx', True, 0, n, 30))
    api.set_active_layer(0)
    for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
    print("  joint keys dropped", drop_joint_keys())
drop_joint_keys()
api.set_frame_range(0, 30); clear(30); g['build'](api); bake_export("Attack", 30)
api.set_frame_range(0, 48); ns['build'](api); bake_export("Idle", 48)
for f in range(0, 49):
    api.set_frame(f)
    for c in ALL: api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
    api.select(ALL); api.set_key()
api.set_frame(5); api.set_frame(1); api.set_frame(0); api.set_frame_range(0, 1)
print('base export', api.export_scene(D + r"\raw_Base.fbx", 'fbx', True, 0, 1, 30))
api.set_frame_range(0, 48); api.select([])
