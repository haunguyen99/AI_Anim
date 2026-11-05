"""Windy Idle - fix round 3 (2026-11-05): user re-keyed the MAIN segments (Cape1, BackFlap1 L/R: ry, keys F0/10/20,
20F cycle = 2 swings per 40F loop) and reset the child segments -> "m overlap lai di".

Additive layer `fix_r3_cloth_overlap` on the children only (user's keys untouched). Travelling wave: segment i points
where the main segment pointed LAG*i frames ago, swing around the main's mean grows GAIN[i] toward the tip;
child local = world_i - world_(i-1).
Axis per child, measured as rotation parallel to the main segment's ry in world:
  flaps: child ry (+);  cape: child rz with sign -1 (Cape1 tilted rx 49 deg, so child ry is out of the swing plane).
Result: segment peaks F10 -> F11-12 -> F12-14 (tip), loop F0 == F40.
Run inside Frolvy via MCP execute_code:
    exec(open(r"C:\\Users\\Admin\\Documents\\AI_animation\\work\\endless_kicker\\windy_idle\\fix_r3_cloth_overlap.py",
              encoding="utf-8").read())
"""
import sys, importlib

sys.path.insert(0, r"C:\Users\Admin\Documents\AI_animation\.claude\skills\frolvy_rig\scripts")
import frolvy_layers as FL
importlib.reload(FL)

P = "Windy_rig:"
LAYER = "fix_r3_cloth_overlap"
PER, LAG, GAIN = 20, 2, [1.0, 1.15, 1.3, 1.45]
CHAINS = {
    "CTL_Cape1_M": (["CTL_Cape2_M", "CTL_Cape3_M", "CTL_Cape4_M"], "rz", -1),
    "CTL_BackFlap1_R": (["CTL_BackFlap2_R", "CTL_BackFlap3_R", "CTL_BackFlap4_R"], "ry", 1),
    "CTL_BackFlap1_L": (["CTL_BackFlap2_L", "CTL_BackFlap3_L", "CTL_BackFlap4_L"], "ry", 1),
}


def run():
    if LAYER in api.layers():
        raise RuntimeError("layer %s already exists" % LAYER)
    main = {}
    for r in CHAINS:
        main[r] = []
        for f in range(PER):
            api.set_frame(f)
            main[r].append(api.get_attr(P + r + ".ry"))
    L = FL.start_fix(api, LAYER)
    nodes = [P + k for kids, _, _ in CHAINS.values() for k in kids]
    for f in range(0, 41, 2):
        FL._key_nodes(api, L, nodes, {}, f, "spline")
        for r, (kids, ch, sg) in CHAINS.items():
            m = sum(main[r]) / PER
            world = [main[r][f % PER]] + [(main[r][(f - LAG * i) % PER] - m) * GAIN[i] + m for i in range(1, 4)]
            for i, k in enumerate(kids, start=1):
                loc = world[i] - world[i - 1]
                for c in ("tx", "ty", "tz", "rx", "ry", "rz"):
                    api.move_key(P + k + "." + c, f, f, sg * loc if c == ch else 0.0)
    return L


print("layer", run(), api.layers())
