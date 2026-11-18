"""Pet FBX cho Unity (ban rut gon cua tools/pet_fbx_finalize.py): UnitScale 100, ten take, kiem mesh/xuong.
usage: py finalize.py in.fbx out.fbx <Take> <so mesh mong doi 0|1>"""
import re, sys
src, dst, take, meshes = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
t = open(src, encoding="utf-8").read()
t, n1 = re.subn(r'(P: "UnitScaleFactor", "double", "Number", "",)[0-9.eE+-]+', r"\g<1>100", t)
t, n2 = re.subn(r'(P: "OriginalUnitScaleFactor", "double", "Number", "",)[0-9.eE+-]+', r"\g<1>100", t)
if not n2: t = re.sub(r'(\t\tP: "UnitScaleFactor"[^\n]*\n)', r'\1\t\tP: "OriginalUnitScaleFactor", "double", "Number", "",100\n', t, count=1)
t, n3 = re.subn(r'AnimStack::take1', "AnimStack::" + take, t)
errs = []
for need in ("Model::DEF_Root_M", "Model::DEF_Muzzle_M"):
    if need not in t: errs.append("missing " + need)
nm = len(re.findall(r'\tModel: [^\n]*"Mesh" \{', t)); ng = len(re.findall(r'\tGeometry: ', t)); nd = len(re.findall(r'\tDeformer: ', t)); nmat = len(re.findall(r'\tMaterial: ', t))
if nm != meshes: errs.append("mesh %d != %d" % (nm, meshes))
if meshes == 0 and (ng or nd or nmat): errs.append("geom %d deformer %d material %d" % (ng, nd, nmat))
if re.search(r"[^A-Za-z_](?:nan|inf)\b", t, flags=re.I): errs.append("nan/inf")
open(dst, "w", encoding="utf-8", newline="").write(t)
stop = re.search(r'P: "LocalStop", "KTime", "Time", "",(\d+)', t)
print("unit x%d take x%d bones %d mesh %d | %.3f s | %s" % (n1, n3, len(re.findall(r'"LimbNode"', t)), nm, int(stop.group(1)) / 46186158000.0 if stop else -1, "; ".join(errs) or "ok"))
