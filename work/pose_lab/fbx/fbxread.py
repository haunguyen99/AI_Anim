import struct, zlib
def read(path):
    b = open(path, "rb").read()
    ver = struct.unpack("<I", b[23:27])[0]; pos = 27; out = []
    def rec(pos):
        if ver >= 7500: end, np_, pl, nl = struct.unpack("<QQQB", b[pos:pos+25]); h = 25
        else: end, np_, pl, nl = struct.unpack("<IIIB", b[pos:pos+13]); h = 13
        if end == 0: return None, pos + h
        name = b[pos+h:pos+h+nl].decode(); p = pos + h + nl; props = []
        for _ in range(np_):
            t = chr(b[p]); p += 1
            if t in "YCIFDL":
                f = {"Y": "<h", "C": "<?", "I": "<i", "F": "<f", "D": "<d", "L": "<q"}[t]; props.append(struct.unpack(f, b[p:p+struct.calcsize(f)])[0]); p += struct.calcsize(f)
            elif t in "SR":
                n = struct.unpack("<I", b[p:p+4])[0]; d = b[p+4:p+4+n]; p += 4 + n; props.append(d.decode("latin1") if t == "S" else d)
            else:
                n, enc, cl = struct.unpack("<III", b[p:p+12]); p += 12; d = b[p:p+cl]; p += cl
                if enc: d = zlib.decompress(d)
                sz = {"f": 4, "d": 8, "i": 4, "l": 8, "b": 1}[t]; fm = {"f": "f", "d": "d", "i": "i", "l": "q", "b": "b"}[t]
                props.append(list(struct.unpack("<%d%s" % (n, fm), d)))
        kids = []; p = pos + h + nl + pl
        while p < end:
            k, p = rec(p)
            if k is None: break
            kids.append(k)
        return (name, props, kids), end
    while pos < len(b) - 200:
        n, pos2 = rec(pos)
        if n is None: break
        out.append(n); pos = pos2
    return ver, out
def dump(n, ind=0, maxp=6, maxlen=100):
    name, props, kids = n
    ps = []
    for p in props[:maxp]:
        s = repr(p) if not isinstance(p, list) else "[%d]%r" % (len(p), p[:6])
        ps.append(s[:maxlen])
    print("  " * ind + name, ", ".join(ps))
    for k in kids: dump(k, ind + 1, maxp, maxlen)
