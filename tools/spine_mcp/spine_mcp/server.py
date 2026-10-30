"""Spine 2D MCP server.

Two groups of tools:
- spine_*      : run the Spine CLI (export, import, pack, info, clean up)
- skeleton_*, bone_*, slot_*, animation_*, keyframe_* : read/edit skeleton JSON

Typical round trip:
  spine_export(project.spine -> folder, json)  ->  edit the .json  ->
  spine_import(.json -> new_project.spine)  ->  open in Spine.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from . import skeleton as sk
from . import spine_cli

mcp = FastMCP("spine")


def _p(path: str) -> Path:
    return Path(path).expanduser().resolve()


# =====================================================================
# Spine CLI
# =====================================================================

@mcp.tool()
def spine_version() -> dict:
    """Show the Spine launcher/editor version the server uses and the CLI path."""
    res = spine_cli.run(["--version"], timeout=300)
    res["spine_exe"] = spine_cli.SPINE_EXE
    res["editor_version"] = spine_cli.SPINE_VERSION
    return res


@mcp.tool()
def spine_project_info(input_path: str) -> dict:
    """Print info (skeletons, bones, animations, ...) about a .spine project, a
    skeleton .json/.skel file or a folder, using the Spine CLI."""
    return spine_cli.run(["-i", _p(input_path)])


@mcp.tool()
def spine_export(
    input_path: str,
    output_dir: str,
    format: Literal["json", "binary"] = "json",
    pack_atlas: bool = False,
    clean_animations: bool = False,
    settings_file: str | None = None,
) -> dict:
    """Export a .spine project to skeleton JSON or binary (.skel).

    - pack_atlas: also pack a texture atlas next to the export.
    - clean_animations: run Spine's animation clean up before exporting.
    - settings_file: path to an export settings JSON saved from Spine's Export
      dialog. When given, it replaces `format`/`pack_atlas` (use it for PNG/GIF/
      video exports or custom options).
    """
    out = _p(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    args: list[Any] = ["-i", _p(input_path)]
    if clean_animations:
        args.append("-m")
    args += ["-o", out, "-e"]
    if settings_file:
        args.append(_p(settings_file))
    else:
        args.append(format + ("+pack" if pack_atlas else ""))
    res = spine_cli.run(args)
    res["files"] = sorted(str(f) for f in out.rglob("*") if f.is_file())[:200]
    return res


@mcp.tool()
def spine_import(
    input_path: str,
    project_path: str,
    skeleton_name: str | None = None,
    scale: float | None = None,
) -> dict:
    """Import skeleton JSON/.skel (or another project's skeletons) into a .spine
    project. The project is created if it does not exist. Importing into an
    existing project adds a skeleton to it, so prefer a new project path when
    re-importing an edited JSON.
    """
    args: list[Any] = ["-i", _p(input_path)]
    if scale is not None:
        args += ["-s", scale]
    args += ["-o", _p(project_path), "-r"]
    if skeleton_name:
        args.append(skeleton_name)
    return spine_cli.run(args)


@mcp.tool()
def spine_pack_atlas(
    images_dir: str,
    output_dir: str,
    atlas_name: str,
    settings_file: str | None = None,
    project_path: str | None = None,
) -> dict:
    """Pack a folder of images into a texture atlas (.atlas + .png).
    settings_file: optional pack settings JSON from Spine's Texture Packer dialog.
    project_path: optional project, used to know which images are meshes."""
    args: list[Any] = ["-i", _p(images_dir)]
    if project_path:
        args += ["-j", _p(project_path)]
    args += ["-o", _p(output_dir)]
    if settings_file:
        args += ["-n", atlas_name, "-p", _p(settings_file)]
    else:
        args += ["-p", atlas_name]
    return spine_cli.run(args)


@mcp.tool()
def spine_unpack_atlas(atlas_file: str, images_dir: str, output_dir: str) -> dict:
    """Unpack a texture atlas back into individual images.
    images_dir: folder holding the atlas page PNGs."""
    return spine_cli.run(["-i", _p(images_dir), "-o", _p(output_dir), "-c", _p(atlas_file)])


@mcp.tool()
def spine_clean_animations(project_path: str) -> dict:
    """Run Spine's animation clean up on a project (removes redundant keys) and
    save it. This modifies the .spine file in place."""
    return spine_cli.run(["-i", _p(project_path), "-m"])


# =====================================================================
# Skeleton JSON: reading
# =====================================================================

@mcp.tool()
def skeleton_summary(json_path: str) -> dict:
    """Overview of a skeleton JSON: version, size, bone/slot counts, skins,
    constraints, events and every animation with its duration (seconds)."""
    return sk.summary(sk.load(_p(json_path)))


@mcp.tool()
def skeleton_bone_tree(json_path: str) -> str:
    """Bone hierarchy as an indented tree."""
    return sk.bone_tree(sk.load(_p(json_path)))


@mcp.tool()
def skeleton_get(json_path: str, path: str = "") -> Any:
    """Read any part of the skeleton JSON by a slash path. List items can be
    picked by index or by their "name". Examples:
      "skeleton", "bones/hip", "slots/0", "animations/walk/bones/hip/rotate",
      "skins/default/attachments", "events"."""
    return sk.get_path(sk.load(_p(json_path)), path)


@mcp.tool()
def slot_list(json_path: str) -> list[dict]:
    """All slots with bone, attachment, color and blend mode."""
    return sk.slots(sk.load(_p(json_path)))


@mcp.tool()
def animation_get(json_path: str, animation: str) -> dict:
    """Full data of one animation (all timelines and keys)."""
    data = sk.load(_p(json_path))
    anims = data.get("animations", {})
    if animation not in anims:
        raise KeyError(f"Animation '{animation}' not found. Have: {list(anims)}")
    return anims[animation]


# =====================================================================
# Skeleton JSON: editing (each write keeps a backup in .spine_mcp_backups)
# =====================================================================

@mcp.tool()
def skeleton_set(json_path: str, path: str, value_json: str) -> dict:
    """Set any value by slash path (same path rules as skeleton_get).
    value_json is a JSON literal, e.g. '12.5', '"stepped"', '{"x": 1}'.
    Use 'null' to delete the key/list item."""
    p = _p(json_path)
    data = sk.load(p)
    sk.set_path(data, path, json.loads(value_json))
    return {"ok": True, "backup": sk.save(p, data)}


@mcp.tool()
def bone_update(json_path: str, bone: str, fields: dict[str, Any]) -> dict:
    """Change setup-pose fields of a bone, e.g. {"x": 10, "rotation": 45,
    "length": 80, "scaleX": 1.2, "color": "ff0000ff"}. Use null to remove a field."""
    p = _p(json_path)
    data = sk.load(p)
    b = sk.find_bone(data, bone)
    if "parent" in fields and fields["parent"] is not None:
        sk.find_bone(data, fields["parent"])
    if "name" in fields:
        raise ValueError("Renaming bones is not supported here (animations and slots refer to names).")
    for k, v in fields.items():
        if v is None:
            b.pop(k, None)
        else:
            b[k] = v
    return {"ok": True, "bone": b, "backup": sk.save(p, data)}


@mcp.tool()
def bone_add(
    json_path: str,
    name: str,
    parent: str,
    x: float = 0,
    y: float = 0,
    rotation: float = 0,
    length: float = 0,
    scale_x: float = 1,
    scale_y: float = 1,
) -> dict:
    """Add a new bone under `parent` (placed right after the parent's subtree
    entries so parents stay before children)."""
    p = _p(json_path)
    data = sk.load(p)
    bl = sk.bones(data)
    if any(b.get("name") == name for b in bl):
        raise ValueError(f"Bone '{name}' already exists")
    sk.find_bone(data, parent)
    bone: dict[str, Any] = {"name": name, "parent": parent}
    for key, val, default in (("length", length, 0), ("rotation", rotation, 0), ("x", x, 0),
                              ("y", y, 0), ("scaleX", scale_x, 1), ("scaleY", scale_y, 1)):
        if val != default:
            bone[key] = val
    bl.append(bone)
    return {"ok": True, "bone": bone, "backup": sk.save(p, data)}


@mcp.tool()
def slot_update(json_path: str, slot: str, fields: dict[str, Any]) -> dict:
    """Change setup-pose fields of a slot, e.g. {"attachment": "head-2",
    "color": "ffffff80", "blend": "additive"}. Use null to remove a field."""
    p = _p(json_path)
    data = sk.load(p)
    s = sk.find_slot(data, slot)
    if "bone" in fields:
        sk.find_bone(data, fields["bone"])
    for k, v in fields.items():
        if v is None:
            s.pop(k, None)
        else:
            s[k] = v
    return {"ok": True, "slot": s, "backup": sk.save(p, data)}


@mcp.tool()
def animation_create(json_path: str, animation: str, copy_from: str | None = None) -> dict:
    """Create an empty animation, or a copy of `copy_from`."""
    p = _p(json_path)
    data = sk.load(p)
    anims = data.setdefault("animations", {})
    if animation in anims:
        raise ValueError(f"Animation '{animation}' already exists")
    if copy_from:
        if copy_from not in anims:
            raise KeyError(f"Animation '{copy_from}' not found")
        anims[animation] = json.loads(json.dumps(anims[copy_from]))
    else:
        anims[animation] = {}
    return {"ok": True, "backup": sk.save(p, data)}


@mcp.tool()
def animation_rename(json_path: str, animation: str, new_name: str) -> dict:
    """Rename an animation (keeps order)."""
    p = _p(json_path)
    data = sk.load(p)
    anims = data.get("animations", {})
    if animation not in anims:
        raise KeyError(f"Animation '{animation}' not found")
    if new_name in anims:
        raise ValueError(f"Animation '{new_name}' already exists")
    data["animations"] = {(new_name if k == animation else k): v for k, v in anims.items()}
    return {"ok": True, "backup": sk.save(p, data)}


@mcp.tool()
def animation_delete(json_path: str, animation: str) -> dict:
    """Delete an animation."""
    p = _p(json_path)
    data = sk.load(p)
    if data.get("animations", {}).pop(animation, None) is None:
        raise KeyError(f"Animation '{animation}' not found")
    return {"ok": True, "backup": sk.save(p, data)}


@mcp.tool()
def animation_scale_time(json_path: str, animation: str, factor: float) -> dict:
    """Stretch or squash an animation in time. factor 2 = twice as long
    (half speed), 0.5 = twice as fast. Scales key times and bezier handles."""
    if factor <= 0:
        raise ValueError("factor must be > 0")
    p = _p(json_path)
    data = sk.load(p)
    anims = data.get("animations", {})
    if animation not in anims:
        raise KeyError(f"Animation '{animation}' not found")

    def walk(node: Any):
        if isinstance(node, dict):
            if "time" in node and isinstance(node["time"], (int, float)):
                node["time"] = round(node["time"] * factor, 4)
            c = node.get("curve")
            if isinstance(c, list):
                node["curve"] = [round(v * factor, 4) if i % 2 == 0 else v for i, v in enumerate(c)]
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(anims[animation])
    return {"ok": True, "new_duration": sk.animation_duration(anims[animation]),
            "backup": sk.save(p, data)}


def _curve(curve: str | list[float] | None) -> Any:
    if curve in (None, "linear"):
        return None
    return curve


@mcp.tool()
def keyframe_set_bone(
    json_path: str,
    animation: str,
    bone: str,
    timeline: Literal["rotate", "translate", "scale", "shear",
                      "translatex", "translatey", "scalex", "scaley", "shearx", "sheary"],
    time: float,
    value: float | None = None,
    x: float | None = None,
    y: float | None = None,
    curve: str | list[float] | None = None,
) -> dict:
    """Add or replace a bone key at `time` (seconds). Creates the animation if missing.
    - rotate / translatex / scalex / ... : use `value`
    - translate / scale / shear : use `x` and `y`
    Values are relative to the setup pose (rotate adds degrees, translate adds
    offset, scale multiplies).
    curve: "linear" (default), "stepped", or Spine bezier numbers
    [cx1, cy1, cx2, cy2] (x2 sets for translate/scale/shear)."""
    p = _p(json_path)
    data = sk.load(p)
    sk.find_bone(data, bone)
    anim = data.setdefault("animations", {}).setdefault(animation, {})
    keys = sk._timeline(anim.setdefault("bones", {}), bone, timeline)
    key: dict[str, Any] = {"time": time}
    if timeline in ("translate", "scale", "shear"):
        if x is None and y is None:
            raise ValueError(f"{timeline} needs x and/or y")
        default = 1 if timeline == "scale" else 0
        key["x"] = default if x is None else x
        key["y"] = default if y is None else y
    else:
        if value is None:
            raise ValueError(f"{timeline} needs value")
        key["value"] = value
    c = _curve(curve)
    if c is not None:
        key["curve"] = c
    action = sk.upsert_key(keys, key)
    return {"ok": True, "action": action, "keys": keys, "backup": sk.save(p, data)}


@mcp.tool()
def keyframe_set_slot(
    json_path: str,
    animation: str,
    slot: str,
    timeline: Literal["attachment", "rgba", "rgb", "alpha"],
    time: float,
    attachment: str | None = None,
    color: str | None = None,
    alpha: float | None = None,
    curve: str | list[float] | None = None,
) -> dict:
    """Add or replace a slot key at `time` (seconds).
    - attachment: set `attachment` (name, or "" to hide)
    - rgba: `color` as "rrggbbaa"; rgb: "rrggbb"
    - alpha: `alpha` 0..1"""
    p = _p(json_path)
    data = sk.load(p)
    sk.find_slot(data, slot)
    anim = data.setdefault("animations", {}).setdefault(animation, {})
    keys = sk._timeline(anim.setdefault("slots", {}), slot, timeline)
    key: dict[str, Any] = {"time": time}
    if timeline == "attachment":
        if attachment is None:
            raise ValueError("attachment timeline needs `attachment`")
        key["name"] = attachment or None
    elif timeline in ("rgba", "rgb"):
        if not color:
            raise ValueError(f"{timeline} needs `color`")
        key["color"] = color
    else:
        if alpha is None:
            raise ValueError("alpha needs `alpha`")
        key["value"] = alpha
    c = _curve(curve)
    if c is not None and timeline != "attachment":
        key["curve"] = c
    action = sk.upsert_key(keys, key)
    return {"ok": True, "action": action, "keys": keys, "backup": sk.save(p, data)}


@mcp.tool()
def keyframe_remove(
    json_path: str,
    animation: str,
    target_type: Literal["bones", "slots"],
    target: str,
    timeline: str,
    time: float,
) -> dict:
    """Remove the key at `time` from a bone or slot timeline. Empty timelines
    are removed too."""
    p = _p(json_path)
    data = sk.load(p)
    try:
        group = data["animations"][animation][target_type]
        keys = group[target][timeline]
    except KeyError as e:
        raise KeyError(f"Timeline not found: {e}") from None
    if not sk.remove_key(keys, time):
        raise KeyError(f"No key at time {time}")
    if not keys:
        del group[target][timeline]
        if not group[target]:
            del group[target]
    return {"ok": True, "backup": sk.save(p, data)}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
