"""Read and edit Spine skeleton JSON files (format 4.x)."""
from __future__ import annotations

import json
import shutil
import time as _time
from pathlib import Path
from typing import Any

BONE_TIMELINES = {"rotate", "translate", "translatex", "translatey", "scale",
                  "scalex", "scaley", "shear", "shearx", "sheary", "inherit"}
SLOT_TIMELINES = {"attachment", "rgba", "rgb", "alpha", "rgba2", "rgb2"}


def load(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def save(path: str | Path, data: dict, backup: bool = True) -> str | None:
    """Write JSON. Keeps one timestamped backup of the previous file."""
    p = Path(path)
    bak = None
    if backup and p.exists():
        bak_dir = p.parent / ".spine_mcp_backups"
        bak_dir.mkdir(exist_ok=True)
        stamp = _time.strftime("%Y%m%d-%H%M%S") + f"-{int(_time.time() * 1000) % 1000:03d}"
        bak = bak_dir / f"{p.stem}.{stamp}{p.suffix}"
        shutil.copy2(p, bak)
    tmp = p.with_suffix(p.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    tmp.replace(p)
    return str(bak) if bak else None


# ---------- lookups ----------

def bones(data: dict) -> list[dict]:
    return data.setdefault("bones", [])


def slots(data: dict) -> list[dict]:
    return data.setdefault("slots", [])


def find_bone(data: dict, name: str) -> dict:
    for b in bones(data):
        if b.get("name") == name:
            return b
    raise KeyError(f"Bone '{name}' not found")


def find_slot(data: dict, name: str) -> dict:
    for s in slots(data):
        if s.get("name") == name:
            return s
    raise KeyError(f"Slot '{name}' not found")


def skins(data: dict) -> list[dict]:
    s = data.get("skins", [])
    if isinstance(s, dict):  # 3.7 and older format
        return [{"name": k, "attachments": v} for k, v in s.items()]
    return s


def animation_duration(anim: dict) -> float:
    """Largest key time found anywhere in an animation."""
    best = 0.0

    def walk(node: Any):
        nonlocal best
        if isinstance(node, list):
            for item in node:
                if isinstance(item, dict) and ("time" in item or "curve" in item or "value" in item
                                               or "x" in item or "name" in item or "color" in item):
                    best = max(best, float(item.get("time", 0)))
                walk(item)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)

    walk(anim)
    return round(best, 4)


def summary(data: dict) -> dict:
    anims = data.get("animations", {})
    return {
        "spine_version": data.get("skeleton", {}).get("spine"),
        "skeleton": {k: v for k, v in data.get("skeleton", {}).items() if k != "hash"},
        "bone_count": len(data.get("bones", [])),
        "slot_count": len(data.get("slots", [])),
        "skins": [s.get("name") for s in skins(data)],
        "ik": [c.get("name") for c in data.get("ik", [])],
        "transform": [c.get("name") for c in data.get("transform", [])],
        "path": [c.get("name") for c in data.get("path", [])],
        "physics": [c.get("name") for c in data.get("physics", [])],
        "events": list(data.get("events", {}).keys()),
        "animations": {name: animation_duration(a) for name, a in anims.items()},
    }


def bone_tree(data: dict) -> str:
    children: dict[str | None, list[str]] = {}
    for b in bones(data):
        children.setdefault(b.get("parent"), []).append(b["name"])
    lines: list[str] = []

    def walk(name: str, depth: int):
        lines.append("  " * depth + name)
        for c in children.get(name, []):
            walk(c, depth + 1)

    for root in children.get(None, []):
        walk(root, 0)
    return "\n".join(lines)


# ---------- path-based generic access ----------

def _resolve_key(node: Any, key: str):
    if isinstance(node, list):
        if key.lstrip("-").isdigit():
            return int(key)
        # allow selecting list items by their "name"
        for i, item in enumerate(node):
            if isinstance(item, dict) and item.get("name") == key:
                return i
        raise KeyError(f"No list item named '{key}'")
    return key


def get_path(data: dict, path: str) -> Any:
    node: Any = data
    if not path:
        return node
    for key in path.split("/"):
        node = node[_resolve_key(node, key)]
    return node


def set_path(data: dict, path: str, value: Any, create: bool = True) -> None:
    keys = path.split("/")
    node: Any = data
    for key in keys[:-1]:
        k = _resolve_key(node, key)
        if isinstance(node, dict) and k not in node:
            if not create:
                raise KeyError(f"'{key}' not found")
            node[k] = {}
        node = node[k]
    last = _resolve_key(node, keys[-1])
    if value is None and isinstance(node, dict):
        node.pop(last, None)
    elif value is None and isinstance(node, list):
        node.pop(last)
    else:
        node[last] = value


# ---------- keyframes ----------

def _timeline(container: dict, name: str, timeline: str) -> list[dict]:
    return container.setdefault(name, {}).setdefault(timeline, [])


def upsert_key(keys: list[dict], key: dict) -> str:
    """Insert a key sorted by time, replacing any key at the same time."""
    t = float(key.get("time", 0))
    if t == 0:
        key.pop("time", None)
    for i, k in enumerate(keys):
        kt = float(k.get("time", 0))
        if abs(kt - t) < 1e-6:
            keys[i] = key
            return "replaced"
        if kt > t:
            keys.insert(i, key)
            return "inserted"
    keys.append(key)
    return "appended"


def remove_key(keys: list[dict], t: float) -> bool:
    for i, k in enumerate(keys):
        if abs(float(k.get("time", 0)) - t) < 1e-6:
            keys.pop(i)
            return True
    return False
