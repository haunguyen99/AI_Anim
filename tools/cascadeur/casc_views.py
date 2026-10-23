"""Ortho renders from Cascadeur that land in the ref pixel frame (1920x1080), for tools/eye_side.py.

Runs INSIDE Cascadeur (mcp__cascadeur__run_script):
    import sys; sys.path.insert(0, r"E:\\AI Animation\\tools\\cascadeur")
    import casc_views; casc_views.render_view(r"E:\\AI Animation\\work\\cascadeur\\look", "p0a", "front")
    (one view per call; casc_views.restore() in the last call)
then tools/cascadeur/casc_mask.py turns the opaque PNGs into RGBA (<tag>_<view>.png).

Calibration (measured 2026-10-21): ISOMETRIC camera, px/cm = 2200 / distance(position, target).
Cascadeur world: cm, Y up, character faces +Z, character's left = +X.
Ref (work/attack/analysis.json): 231.3 px/m, ground y = 910, origin x per view, top origin (1056, 545).
"""
import os

import numpy as np
import csc

K0 = 2200.0          # px*cm: px_per_cm * distance (viewport maximised on monitor 1, 2026-10-21 morning)
# The render scale follows the viewport size/layout: when the window moves or panels change, re-measure K0 with
# calibrate_k0() and it is kept in k0.json next to this file.
_K0_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "k0.json")


def k0():
    try:
        import json
        return float(json.load(open(_K0_FILE))["K0"])
    except Exception:
        return K0


def calibrate_k0(measured_px, expected_px):
    """measured/expected size (px) of the same pose rendered now vs at a known-good calibration -> new K0."""
    import json
    v = k0() * measured_px / expected_px          # bigger K0 = camera further away = smaller image
    json.dump({"K0": v}, open(_K0_FILE, "w"))
    return v
W, H = 1920, 1080
CX, CY = W / 2, H / 2


def _cal():
    return {"px_per_cm": 2.313, "ground_y": 910,
            "origin_x": {"front": 1056, "back": 862, "left": 965, "right": 953, "top": 1056},
            "top_origin_y": 545}


def view_struct(view, cal=None):
    """position/target of the ortho camera for one ref view."""
    c = cal or _cal()
    k = c["px_per_cm"]
    d = k0() / k
    ox = c["origin_x"][view]
    ty = (c["ground_y"] - CY) / k                     # floor (Y=0) lands on ground_y
    if view == "front":                               # cam +Z, screen right = +X
        t = (-(ox - CX) / k, ty, 0.0); p = (t[0], ty, d)
    elif view == "back":                              # cam -Z, screen right = -X
        t = ((ox - CX) / k, ty, 0.0); p = (t[0], ty, -d)
    elif view == "left":                              # cam on character's left (+X), screen right = -Z
        t = (0.0, ty, (ox - CX) / k); p = (d, ty, t[2])
    elif view == "right":                             # cam on character's right (-X), screen right = +Z
        t = (0.0, ty, -(ox - CX) / k); p = (-d, ty, t[2])
    elif view == "top":                               # cam above, screen right = +X, +Z (forward) = down
        tz = -(c["top_origin_y"] - CY) / k
        t = (-(ox - CX) / k, 0.0, tz); p = (t[0], d, tz + 0.01)
    else:
        raise ValueError(view)
    return np.array(p, np.float32), np.array(t, np.float32)


def _app_scene():
    app = csc.app.get_application()
    return app, app.get_scene_manager().current_scene()


def set_view(view, cal=None):
    _, cur = _app_scene()
    dvp = cur.active_viewport().domain_viewport()
    p, t = view_struct(view, cal)
    cs = csc.view.SphericalCameraStruct()
    cs.type = csc.view.CameraType.ISOMETRIC
    cs.position = p.reshape(3, 1)
    cs.target = t.reshape(3, 1)
    dvp.set_camera_struct(cs)


def render(path):
    app, cur = _app_scene()
    r = next(t for t in app.get_tools_manager().tools() if type(t).__name__ == "RenderToFile")
    rp = csc.tools.RenderParameters()
    rp.width, rp.height = W, H
    os.makedirs(os.path.dirname(path), exist_ok=True)
    r.take_image(cur, rp, path)


def set_visible(scene, name, on=True):
    """Show/hide one object (e.g. the prop mesh) via its Basic.visibility data (2 = visible, 0 = hidden)."""
    mv = scene.model_viewer()
    bv = mv.behaviour_viewer()
    oid = next(o for o in mv.get_objects() if mv.get_object_name(o) == name)

    def mod(model, update, updater):
        d = bv.get_behaviour_data(bv.get_behaviour_by_name(oid, "Basic"), "visibility")
        model.data_editor().set_data_value(d, 2 if on else 0)

    return scene.modify_update(f"visibility {name} {on}", mod)


_saved = {}


def render_view(out_dir, tag, view, mesh_only=True):
    """Render one view to <out_dir>/<tag>_<view>_raw.png.

    take_image is deferred to the next drawn frame, so call this once per MCP run_script call
    (several in one call all come out with the last camera), then restore() in a final call.
    """
    _, cur = _app_scene()
    dvp = cur.active_viewport().domain_viewport()
    if not _saved:
        _saved["cam"], _saved["mode"] = dvp.camera_struct(), dvp.mode_visualizers()
    if mesh_only:
        dvp.set_mode_visualizers(csc.view.ViewportMode.View)
    set_view(view)
    path = os.path.join(out_dir, f"{tag}_{view}_raw.png")
    render(path)
    return path


def restore():
    """Put back the camera and viewport mode the user had before render_view."""
    if not _saved:
        return
    _, cur = _app_scene()
    dvp = cur.active_viewport().domain_viewport()
    dvp.set_camera_struct(_saved["cam"])
    dvp.set_mode_visualizers(_saved["mode"])
    _saved.clear()
