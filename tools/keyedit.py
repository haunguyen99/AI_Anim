"""Edit keys.json from the command line and keep it compact (one bone per line).

  python tools/keyedit.py W set 6 Head_M aim=0.2,0.9,-0.4 Neck_M aim=0,0.7,0.7 root=0,-0.03,-0.11
  python tools/keyedit.py W set 6 Spine1_M rot=0,0,10 Weapon "aim=-0.17,0.32,-0.23" grip=Wrist_L@0.75
  python tools/keyedit.py W copy 1 6          (duplicate a key, then edit it)
  python tools/keyedit.py W del 6             (remove a key)
  python tools/keyedit.py W del 6 Head_M      (remove one bone from a key)
  python tools/keyedit.py W show [6]
  python tools/keyedit.py W unbake            (drop "bake" so eye keys drive the animation)
  python tools/keyedit.py W fmt               (rewrite compactly)
  python tools/keyedit.py W layer breath Chest_M rot 1=0,0,0 18=-3,0,0 31=0,0,0   (set a layer track)
  python tools/keyedit.py W layer breath Root_M loc 1=0,0,0 16=0,0,-0.04 31=0,0,0
  python tools/keyedit.py W layer breath --cyclic on|off
  python tools/keyedit.py W layer breath Chest_M rot --clear

Bone specs: aim=x,y,z  rot=x,y,z  twist=deg  loc=x,y,z  grip=Bone@at
"""
import json
import os
import sys


def load(work):
    return json.load(open(os.path.join(work, "keys.json"), encoding="utf-8"))


def num(v):
    return int(v) if float(v).is_integer() and abs(float(v)) < 1e6 and "." not in str(v) else round(float(v), 4)


def save(work, k):
    lines = ["{"]
    for key in ("fps", "frame_count", "interpolation", "bake", "foot_lock", "foot_lock_frame", "props", "arm_ik", "loop"):
        if key in k:
            lines.append(f' "{key}": {json.dumps(k[key])},')
    lines.append(' "keys": {')
    frames = sorted(k["keys"], key=int)
    for i, f in enumerate(frames):
        kk = k["keys"][f]
        lines.append(f'  "{f}": {{')
        parts = []
        if "root" in kk:
            parts.append(f'   "root": {json.dumps(kk["root"])}')
        bl = []
        for b, spec in kk.get("bones", {}).items():
            bl.append(f'    {json.dumps(b)}: {json.dumps(spec)}')
        parts.append('   "bones": {\n' + ",\n".join(bl) + "\n   }")
        lines.append(",\n".join(parts))
        lines.append("  }" + ("," if i < len(frames) - 1 else ""))
    if k.get("layers"):
        lines.append(" },")
        lines.append(' "layers": [')
        for li, L in enumerate(k["layers"]):
            extra = "".join(f', "{x}": {json.dumps(L[x])}' for x in ("period", "span") if x in L)
            lines.append(f'  {{"name": {json.dumps(L.get("name", ""))}, "cyclic": {json.dumps(L.get("cyclic", False))}{extra}, "bones": {{')
            bl = []
            for b, chans in L.get("bones", {}).items():
                cl = [f'      {json.dumps(c)}: {json.dumps(dict(sorted(tr.items(), key=lambda kv: int(kv[0]))))}'
                      for c, tr in chans.items()]
                bl.append(f'    {json.dumps(b)}: {{' + "\n" + ",\n".join(cl) + "\n    }")
            lines.append(",\n".join(bl))
            lines.append("  }}" + ("," if li < len(k["layers"]) - 1 else ""))
        lines.append(" ]")
    else:
        lines.append(" }")
    lines.append("}")
    open(os.path.join(work, "keys.json"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


def vec(s):
    return [num(x) for x in s.split(",")]


def main():
    work, cmd, *rest = sys.argv[1:]
    k = load(work)
    if cmd == "set":
        f, args = rest[0], rest[1:]
        key = k["keys"].setdefault(str(int(f)), {"bones": {}})
        key.setdefault("bones", {})
        bone = None
        for a in args:
            if "=" not in a:
                bone = a
                continue
            name, val = a.split("=", 1)
            if name == "root":
                key["root"] = {"loc": vec(val)}
                continue
            if bone is None:
                sys.exit(f"no bone given before {a}")
            spec = key["bones"].setdefault(bone, {})
            if name in ("aim", "rot"):
                spec.pop("aim" if name == "rot" else "rot", None)
                spec[name] = vec(val)
            elif name == "loc":
                spec["loc"] = vec(val)
            elif name == "twist":
                spec["twist"] = num(val)
            elif name == "grip":
                gb, at = val.split("@")
                spec["grip"] = {"bone": gb, "at": float(at)}
            else:
                sys.exit(f"unknown spec {name}")
    elif cmd == "copy":
        src, dst = rest
        k["keys"][str(int(dst))] = json.loads(json.dumps(k["keys"][str(int(src))]))
    elif cmd == "del":
        if len(rest) == 1:
            k["keys"].pop(str(int(rest[0])), None)
        else:
            for b in rest[1:]:
                k["keys"][str(int(rest[0]))]["bones"].pop(b, None)
    elif cmd == "show":
        for f in sorted(k["keys"], key=int):
            if rest and f != str(int(rest[0])):
                continue
            kk = k["keys"][f]
            print(f"[{f}] root={kk.get('root', {}).get('loc')}")
            for b, s in kk.get("bones", {}).items():
                print(f"   {b:12s} {json.dumps(s)}")
        return
    elif cmd == "layer":
        name, args = rest[0], rest[1:]
        layers = k.setdefault("layers", [])
        L = next((x for x in layers if x.get("name") == name), None)
        if L is None:
            L = {"name": name, "cyclic": True, "bones": {}}
            layers.append(L)
        if args and args[0] == "--cyclic":
            L["cyclic"] = args[1] == "on"
        else:
            bone, chan, vals = args[0], args[1], args[2:]
            tr = L["bones"].setdefault(bone, {}).setdefault(chan, {})
            if vals == ["--clear"]:
                L["bones"][bone].pop(chan)
            for kv in vals:
                if "=" in kv:
                    f, v = kv.split("=", 1)
                    tr[str(int(f))] = vec(v)
    elif cmd == "unbake":
        k.pop("bake", None)
    elif cmd != "fmt":
        sys.exit(__doc__)
    save(work, k)
    print(f"keys: {sorted(int(f) for f in k['keys'])}" + (f"  bake={k['bake']}" if k.get("bake") else ""))


if __name__ == "__main__":
    main()
