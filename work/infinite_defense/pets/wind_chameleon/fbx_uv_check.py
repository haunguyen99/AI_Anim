# Đọc FBX nhị phân (thuần python): liệt kê mesh, số UV, material, texture.
import struct, sys, zlib
def parse(b):
    ver = struct.unpack("<I", b[23:27])[0]; big = ver >= 7500
    def rec(pos):
        if big: end, npr, plen, nl = struct.unpack("<QQQB", b[pos:pos+25]); h = 25
        else: end, npr, plen, nl = struct.unpack("<IIIB", b[pos:pos+13]); h = 13
        if end == 0: return None, pos + h
        name = b[pos+h:pos+h+nl].decode("latin1"); p = pos + h + nl; props = []
        for _ in range(npr):
            t = chr(b[p]); p += 1
            if t in "YCFDIL":
                f = {"Y":"<h","C":"<?","F":"<f","D":"<d","I":"<i","L":"<q"}[t]; props.append(struct.unpack_from(f, b, p)[0]); p += struct.calcsize(f)
            elif t in "fdilb":
                n, enc, cl = struct.unpack_from("<III", b, p); p += 12
                raw = b[p:p+cl]; p += cl
                if enc: raw = zlib.decompress(raw)
                props.append((t, n))
            elif t in "SR":
                n = struct.unpack_from("<I", b, p)[0]; p += 4; s = b[p:p+n]; p += n
                props.append(s.decode("latin1") if t == "S" else s)
        ch = []
        while p < end:
            c, p = rec(p)
            if c is None: break
            ch.append(c)
        return (name, props, ch), end
    pos = 27; top = []
    while pos < len(b) - 40:
        n, pos = rec(pos)
        if n is None: break
        top.append(n)
    return ver, top
def main(path):
    ver, top = parse(open(path, "rb").read())
    print(path.split("/")[-1], "FBX", ver)
    T = {n[0]: n for n in top}
    for o in T["Objects"][2]:
        nm = o[0]; pr = o[1]
        label = pr[1].split("\x00")[0] if len(pr) > 1 and isinstance(pr[1], str) else ""
        if nm == "Geometry":
            info = {c[0]: (c[1][0] if c[1] and isinstance(c[1][0], tuple) else c[1]) for c in o[2]}
            uv = [c for c in o[2] if c[0] == "LayerElementUV"]
            print(" Geometry", label, "Vertices", info.get("Vertices"), "UV layers:", len(uv))
            for u in uv:
                d = {c[0]: (c[1][0] if c[1] else None) for c in u[2]}
                print("   UV", d.get("Name"), "map", d.get("MappingInformationType"), "UV", d.get("UV"), "UVIndex", d.get("UVIndex"))
        elif nm in ("Material", "Texture", "Video"):
            extra = ""
            for c in o[2]:
                if c[0] in ("FileName", "RelativeFilename"): extra += " %s=%s" % (c[0], c[1][0] if c[1] else "")
                if c[0] == "Properties70":
                    for p in c[2]:
                        if p[1] and p[1][0] in ("DiffuseColor", "BaseColor", "Diffuse", "Emissive"): extra += " %s=%s" % (p[1][0], [round(x, 2) for x in p[1][4:7]])
            print(" ", nm, label, extra)
    for c in T["Connections"][2]:
        pr = c[1]
        if len(pr) >= 3 and False: pass
main(sys.argv[1])
