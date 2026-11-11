"""Đọc FBX nhị phân nhanh (mảng số giữ dạng numpy, không bung từng phần tử như work/pose_lab/fbx/fbxread.py).
Dùng cho file Mixamo ~30 MB có mesh. Trả cùng cấu trúc (name, props, kids) như fbxread.read."""
import struct, zlib
import numpy as np

_DT = {"f": "<f4", "d": "<f8", "i": "<i4", "l": "<i8", "b": "i1", "c": "i1"}


def read(path):
    b = open(path, "rb").read()
    mv = memoryview(b)
    ver = struct.unpack_from("<I", b, 23)[0]
    big = ver >= 7500

    def rec(pos):
        if big:
            end, np_, pl, nl = struct.unpack_from("<QQQB", b, pos); h = 25
        else:
            end, np_, pl, nl = struct.unpack_from("<IIIB", b, pos); h = 13
        if end == 0:
            return None, pos + h
        name = b[pos + h:pos + h + nl].decode(); p = pos + h + nl; props = []
        for _ in range(np_):
            t = chr(b[p]); p += 1
            if t in "YCIFDL":
                f = {"Y": "<h", "C": "<?", "I": "<i", "F": "<f", "D": "<d", "L": "<q"}[t]
                props.append(struct.unpack_from(f, b, p)[0]); p += struct.calcsize(f)
            elif t in "SR":
                n = struct.unpack_from("<I", b, p)[0]; d = b[p + 4:p + 4 + n]; p += 4 + n
                props.append(d.decode("latin1") if t == "S" else d)
            else:
                n, enc, cl = struct.unpack_from("<III", b, p); p += 12
                d = mv[p:p + cl]; p += cl
                if enc:
                    d = zlib.decompress(d)
                props.append(np.frombuffer(d, _DT[t], count=n))
        kids = []; p = pos + h + nl + pl
        while p < end:
            k, p = rec(p)
            if k is None:
                break
            kids.append(k)
        return (name, props, kids), end

    out, pos = [], 27
    while pos < len(b) - 200:
        n, pos2 = rec(pos)
        if n is None:
            break
        out.append(n); pos = pos2
    return ver, out
