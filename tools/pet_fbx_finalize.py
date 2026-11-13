"""Make a Frolvy pet FBX safe for Unity (ASCII FBX already filtered by fbx_ascii_keep.py):
 - UnitScaleFactor 100 (Frolvy writes 1 = cm but pet data is in metres -> Unity showed a 1 cm pet),
 - take name = clip name (not 'take1'),
 - sanity: no nan/inf, one skinned mesh, DEF_Root_M + DEF_Muzzle_M present, clip length / key count.
usage: py tools/pet_fbx_finalize.py in.fbx out.fbx <TakeName> [--unit 100]"""
import argparse, re, sys
ap = argparse.ArgumentParser(); ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("take"); ap.add_argument("--unit", type=float, default=100); ap.add_argument("--meshes", type=int, default=1, help="expected mesh count (0 for anim-only)")
a = ap.parse_args()
t = open(a.src, encoding="utf-8").read()
t, n1 = re.subn(r'(P: "UnitScaleFactor", "double", "Number", "",)[0-9.eE+-]+', r"\g<1>%g" % a.unit, t)
t, n2 = re.subn(r'(P: "OriginalUnitScaleFactor", "double", "Number", "",)[0-9.eE+-]+', r"\g<1>%g" % a.unit, t)
if not n2:   # add Original next to UnitScaleFactor
    t = re.sub(r'(\t\tP: "UnitScaleFactor"[^\n]*\n)', r'\1\t\tP: "OriginalUnitScaleFactor", "double", "Number", "",%g\n' % a.unit, t, count=1)
t, n3 = re.subn(r'AnimStack::take1', "AnimStack::" + a.take, t)
bad = re.findall(r"[^A-Za-z_](?:nan|inf)\b", t, flags=re.I)
errs = []
for need in ("Model::DEF_Root_M", "Model::DEF_Muzzle_M"):
    if need not in t: errs.append("missing " + need)
if len(re.findall(r'\tModel: [^\n]*"Mesh" \{', t)) != a.meshes: errs.append("mesh count != %d" % a.meshes)
if bad: errs.append("nan/inf values: %d" % len(bad))
if a.meshes == 0:   # anim-only: drop the empty Geometry/Deformer definition blocks too
    t = re.sub(r'\tObjectType: "(Geometry|Deformer)" \{\r?\n\t\tCount: 0\r?\n(?:\t\t[^\n]*\n)*?\t\}\r?\n', "", t)
open(a.dst, "w", encoding="utf-8", newline="").write(t)
stop = re.search(r'P: "LocalStop", "KTime", "Time", "",(\d+)', t)
print("unit x%d take x%d | length %.3f s | %s" % (n1, n3, int(stop.group(1)) / 46186158000.0 if stop else -1, "; ".join(errs) or "checks ok"))
