"""Rig Pose Tools - put a Rig Builder rig back to its T-pose (bind pose) in one click.

Plugins panel "Rig Pose Tools":
  Ve T-Pose (tat ca)      - every CTL_ control back to 0 (translate, rotate), scale 1;
                            finger dials on the arm switches (curl, spread, handPose...) to 0.
                            FK/IK switches keep their mode.
  Ve T-Pose (dang chon)   - the same, only for the selected controls.
Locked channels are unlocked for the reset and locked again. One undo step per click
when the host groups plugin actions. Works on any rig with CTL_* controls.
"""

FINGER_DIALS = ("curl", "thumbCurl", "spread", "handPose", "indexCurl", "middleCurl",
                "ringCurl", "pinkyCurl")


def _controls(api):
    return [c for c in api.ls("Curve")
            if c.startswith("CTL_") and not c.endswith(("_grp", "_follow"))]


def _reset(api, nodes):
    n = 0
    for c in nodes:
        if "Switch" in c:
            for a in FINGER_DIALS:
                if api.attr_info(c, a):
                    api.set_attr(c + "." + a, 0.0)
            continue
        t = api.transform(c)
        if all(abs(v) < 1e-7 for v in t[:6]) and all(abs(v - 1) < 1e-7 for v in t[6:9]):
            continue
        lk = api.locked_channels(c)
        if lk:
            api.lock_channels(c, " ".join(lk), False)
        new_s = [1.0 if ("s" + ax) not in lk else t[6 + i] for i, ax in enumerate("xyz")]
        api.set_transform(c, [0, 0, 0], [0, 0, 0], new_s)
        if lk:
            api.lock_channels(c, " ".join(lk), True)
        n += 1
    return n


def reset_all(api):
    n = _reset(api, _controls(api))
    api.log("T-Pose: %d control ve 0." % n)


def reset_selected(api):
    sel = [c for c in api.selection() if c.startswith("CTL_")]
    if not sel:
        api.log("T-Pose: chua chon control nao.")
        return
    n = _reset(api, sel)
    api.log("T-Pose: %d control dang chon ve 0." % n)


def register(api):
    try:
        p = api.panel("Rig Pose Tools")
        p.heading("T-Pose")
        p.text("hint", "Dua control ve 0 (tu the luc rig). Giu nguyen che do FK/IK.", tone="muted")
        p.button("all", "Ve T-Pose (tat ca)", lambda: reset_all(api))
        p.button("sel", "Ve T-Pose (dang chon)", lambda: reset_selected(api), same_line=True)
    except Exception:
        pass
    api.command("Rig Pose Tools: Ve T-Pose (tat ca)", lambda: reset_all(api))
    api.command("Rig Pose Tools: Ve T-Pose (dang chon)", lambda: reset_selected(api))
