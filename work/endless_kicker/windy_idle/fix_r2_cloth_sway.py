"""Windy Idle - fix round 2: cape + both back flaps swing left/right TOGETHER with overlap (user 2026-11-05: "cai ao
choang lan 2 cai vat cho bay danh sang trai phai cung nhau roi gan overlap").

Found in Base: cape tip swung LEFT (+26 cm) while both flaps swung RIGHT (-33/-37 cm) -> opposite directions.
This layer REPLACES the sideways channel of every segment (layer = wanted - Base on that channel); the up/down wind
flutter on the other channels stays. Sideways channel measured per control (tip moves along shoulder line):
Cape1-4 rz (+ = to char's left), BackFlap1-4 L/R ry (- = to char's left, same sign both sides).

One sway per 40F loop, root 2F after F0, +4F per segment, amplitude 3/4/5/6 deg root -> tip.
Result: left peak F12 (seg 2) -> F17 (tip), right F32 -> F37, tips +-15..16 cm, loop F0 == F40.
Run inside Frolvy (after round 1) via MCP execute_code:
    exec(open(r"C:\\Users\\Admin\\Documents\\AI_animation\\work\\endless_kicker\\windy_idle\\fix_r2_cloth_sway.py",
              encoding="utf-8").read())
"""
import sys, math, importlib

sys.path.insert(0, r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_rig\scripts")
import frolvy_layers as FL
importlib.reload(FL)

P = "Windy_rig:"
N, STEP = 40, 2
LAYER = "fix_r2_cloth_sway"
AMP = [3.0, 4.0, 5.0, 6.0]
ROOT_LAG, SEG_LAG = 2, 4
AX = {**{"CTL_Cape%d_M" % i: ("rz", 1) for i in range(1, 5)},
      **{"CTL_BackFlap%d_%s" % (i, s): ("ry", -1) for i in range(1, 5) for s in "LR"}}
CHAINS = [["CTL_Cape%d_M" % i for i in range(1, 5)]] + [["CTL_BackFlap%d_%s" % (i, s) for i in range(1, 5)]
                                                         for s in "RL"]


def run():
    if LAYER in api.layers():
        raise RuntimeError("layer %s already exists" % LAYER)
    L = FL.start_fix(api, LAYER)
    for i in range(1, len(api.layers())):
        api.set_layer_mute(i, True)
    base = {}
    for f in range(0, N + 1, STEP):
        api.set_frame(f)
        for cn, (ch, _) in AX.items():
            base[cn, f] = api.get_attr(P + cn + "." + ch)
    for i in range(1, len(api.layers())):
        api.set_layer_mute(i, False)
    nodes = [P + c for c in AX]
    for f in range(0, N + 1, STEP):
        FL._key_nodes(api, L, nodes, {}, f, "spline")
        for chain in CHAINS:
            for i, cn in enumerate(chain):
                ch, sg = AX[cn]
                want = sg * AMP[i] * math.sin(2 * math.pi * (f - ROOT_LAG - SEG_LAG * i) / N)
                for c in ("tx", "ty", "tz", "rx", "ry", "rz"):
                    api.move_key(P + cn + "." + c, f, f, want - base[cn, f] if c == ch else 0.0)
    return L


print("layer", run(), api.layers())
