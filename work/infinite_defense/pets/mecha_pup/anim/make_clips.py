"""Build + save + export both clips in the open scene (Frolvy 9879). Saves *_new.fv (rename outside: save_scene refuses
existing paths), bakes DEF joints onto a temp layer for export_scene, then deletes that layer.
Run: .venv/Scripts/python.exe -I tools/frolvy_port.py 9879 work/infinite_defense/pets/mecha_pup/anim/make_clips.py"""
import sys
for _p in (r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_auto_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_rig\scripts", r"C:\Users\Admin\Documents\AI_animation\tools\frolvy_plugins\fit_controls"):
    sys.path.insert(0, _p)
import auto_rig as A
R = A.R
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_11_Mecha_Pup"
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\mecha_pup\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = dict(globals()); g['idle_pose'] = ns['pose']; exec(open(W + r"\attack.py").read(), g)
ALL = ns['CTLS']
def clear():
    # baked DEF keys from the previous clip would leak into the next .fv (and override the controls): drop them first
    for j in api.ls("Joint"):
        if j.startswith("DEF_"):
            for a in ("rx", "ry", "rz", "tx", "ty", "tz", "sx", "sy", "sz"):
                for f in list(api.list_keys(j + "." + a)): api.delete_key(j + "." + a, int(round(f)))
    for c in ALL:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            for f in list(api.list_keys(c + "." + a)): api.delete_key(c + "." + a, int(round(f)))
    R.zero_controls(api)
def setsw():
    for s in ('CTL_LegSwitch_R', 'CTL_LegSwitch_L', 'CTL_ArmSwitch_R', 'CTL_ArmSwitch_L'): api.set_attr(s + '.fkIk', 1.0)
def reach(n):
    import math
    mx = {}
    for f in range(0, n + 1):
        api.set_frame(1); api.set_frame(f)
        for nm, a, b, c in (('armR', 'DEF_Shoulder_R', 'DEF_Wrist_R', 'CTL_IKWrist_R'), ('legR', 'DEF_Hip_R', 'DEF_Ankle_R', 'CTL_IKAnkle_R')):
            m = mx.setdefault(nm, [0, 0]); m[0] = max(m[0], math.dist(R.P(api, a), R.P(api, b))); m[1] = max(m[1], math.dist(R.P(api, b), R.P(api, c)))
    print('reach check (arm max .233, leg max ~.32; miss must be ~0):', {k: (round(v[0], 3), round(v[1], 3)) for k, v in mx.items()})
def finish(name, n):
    reach(n)
    api.set_frame(1); api.set_frame(0)
    print(name, 'save', api.save_scene(D + r"\mecha_pup_%s_new.fv" % name.lower()))
    defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
    api.set_frame_range(0, n)
    print('bake', api.bake_keys(defs, 0, n, 1, 'all', True), 'export', api.export_scene(D + r"\raw_%s.fbx" % name, 'fbx', True, 0, n, 30))
    api.set_active_layer(0)
    for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
    print('layers', api.layers(), 'Root ty keys', len(api.list_keys('CTL_Root_M.ty')))
clear(); setsw(); ns['build'](api); finish("Idle", 48)
clear(); setsw(); g['setup'](); g['build'](api); finish("Attack", 24)
