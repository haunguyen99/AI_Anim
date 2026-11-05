"""Windy Idle - fix round 1: overlap/lag for the breath (user 2026-11-05: "2 tay va body chua co do tre voi nhip tho,
tho manh la tot nhung qua guong ep"). Ref: Pinterest Frog Wizard Idle (pin 1089097122419081799), measured by patch
tracking in the browser (not downloaded): one breath ~38F @30fps, F0 = top, short holds at both ends; belly peaks
first, chest +3F, head +4..6F with a slower settle, free hand +6F and travels ~3x the body (arm hangs, swings late),
staff hand moves little, staff top tilts with the hips.

Found in Base: hips still, shoulders shrug 10 deg (3.6 cm), LEFT arm is FK (ArmSwitch_L.fkIk = 0) so the whole arm
swung rigidly with the scapula (elbow fixed at 129 deg), right arm IK pinned, spine/chest/neck/head peaked within
1-2F -> the whole block lifted at once.

Additive layer `fix_r1_breath_lag` (Base untouched). Run inside Frolvy via MCP execute_code:
    exec(open(r"C:\\Users\\Admin\\Documents\\AI_animation\\work\\endless_kicker\\windy_idle\\fix_r1_breath_lag.py",
              encoding="utf-8").read())

Result 2026-11-05 (world peaks): hips F17 (1.5 cm) -> chest F17-19 -> shoulder F19 -> head pitch F21 -> left elbow
F22 -> left hand F23 -> right hand F23 -> staff top F27. Loop F0 == F40, feet slide 0.

Frolvy 0.9.36 notes: rotations on an additive layer compose as matrices, so FL.key's per-channel error correction
goes wrong when a node has several non-zero rotate channels -> for rotations write the layer value itself with
move_key (rx/ry/rz = delta on one channel, 0 on the others). Head lag is solved in WORLD pitch (head counters the
chest), since a local-rx delay alone left the head peaking with the chest.
"""
import sys, math, importlib

sys.path.insert(0, r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_rig\scripts")
import frolvy_layers as FL
importlib.reload(FL)

P = "Windy_rig:"
N, STEP = 40, 2
LAYER = "fix_r1_breath_lag"

LAG = {"CTL_Chest_M.rx": 2, "CTL_Scapula_L.rz": 2, "CTL_Scapula_R.rz": 2, "CTL_Neck_M.rx": 4,
       "CTL_IKWrist_R.ty": 3}
HIP_BOB = 0.0028            # Root ty (control units) on the in-breath; more makes the IK feet slide
HEAD_LAG = 4                # head world pitch follows Base 4F late
ARM_FOLLOW = 0.65           # left FK arm swings this share of the shoulder shrug...
SH_LAG, FA_LAG, HD_LAG = 6, 9, 12   # ...upper arm, forearm, hand this many F after Base scapula
SH_GAIN, EL_GAIN, WR_GAIN = 1.0, 1 / 0.58, 1 / 0.76   # control deg per deg of swing (measured axes)
STAFF_GAIN, STAFF_LAG = 2.5, 6


def wp(n):
    m = api.world_matrix(P + n)
    return (m[12], m[13], m[14])


def at(a, f):
    return a[f % N]


def head_pitch():
    a, e = wp("DEF_Head_M"), wp("DEF_HeadEnd_M")
    d = [e[i] - a[i] for i in range(3)]
    return math.degrees(math.atan2(d[2], d[1]))


def sample_base(layer):
    api.set_layer_mute(layer, True)
    chans = set(LAG) | {"CTL_Root_M.ty", "CTL_Weapon_R.rz", "CTL_Scapula_L.rz"}
    base = {c: [] for c in chans}
    chest, head = [], []
    for f in range(N + 1):
        api.set_frame(f)
        for c in chans:
            base[c].append(api.get_attr(P + c))
        chest.append(wp("DEF_Chest_M")[1])
        head.append(head_pitch())
    api.set_layer_mute(layer, False)
    return base, chest, head


def run():
    if LAYER in api.layers():
        raise RuntimeError("layer %s already exists" % LAYER)
    L = FL.start_fix(api, LAYER)
    base, chest, head = sample_base(L)
    lo, hi = min(chest), max(chest)
    breath = [(y - lo) / (hi - lo) for y in chest]
    sw = [-v for v in base["CTL_Scapula_L.rz"]]       # shoulder shrug, deg
    frames = range(0, N + 1, STEP)

    # 1. delays on single channels (+ hips)
    for f in frames:
        t = {P + c: at(base[c], f - lag) for c, lag in LAG.items()}
        t[P + "CTL_Root_M.ty"] = base["CTL_Root_M.ty"][f] + HIP_BOB * breath[f]
        FL.key(api, L, t, f)

    # 2. rotations written as layer values (matrix composition, see notes)
    arm = [P + "CTL_Shoulder_L", P + "CTL_Elbow_L", P + "CTL_Wrist_L"]
    w = base["CTL_Weapon_R.rz"]
    for f in frames:
        FL._key_nodes(api, L, arm + [P + "CTL_Weapon_R"], {}, f, "spline")
        d = {
            "CTL_Shoulder_L.rz": SH_GAIN * (at(sw, f - 2) - ARM_FOLLOW * at(sw, f - SH_LAG)),
            "CTL_Elbow_L.ry": -EL_GAIN * ARM_FOLLOW * (at(sw, f - FA_LAG) - at(sw, f - SH_LAG)),
            "CTL_Wrist_L.ry": -WR_GAIN * ARM_FOLLOW * 1.5 * (at(sw, f - HD_LAG) - at(sw, f - FA_LAG)),
            "CTL_Weapon_R.rz": STAFF_GAIN * (at(w, f - STAFF_LAG) - w[0]) - (w[f] - w[0]),
        }
        for n in ("CTL_Shoulder_L", "CTL_Elbow_L", "CTL_Wrist_L", "CTL_Weapon_R"):
            for c in ("tx", "ty", "tz", "rx", "ry", "rz"):
                api.move_key(P + n + "." + c, f, f, d.get(n + "." + c, 0.0))

    # 3. head: solve its own rx so the WORLD pitch trails Base by HEAD_LAG
    for _ in range(3):
        for f in frames:
            api.set_frame(f)
            now = head_pitch()
            cur = api.get_attr(P + "CTL_Head_M.rx")
            FL.key(api, L, {P + "CTL_Head_M.rx": cur + (at(head, f - HEAD_LAG) - now)}, f)   # ~1 deg pitch / deg rx
    return L


if __name__ == "__main__" or "api" in globals():
    print("layer", run(), api.layers())
