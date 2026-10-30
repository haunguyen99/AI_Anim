# Xóa một (hoặc nhiều) mesh khỏi FBX binary, giữ nguyên mọi thứ khác từng byte (xương, skin, mesh còn lại, material).
# Bỏ: Model mesh, Geometry, Skin + Cluster của nó, các Connection tới chúng, PoseNode của mesh; sửa số đếm trong Definitions.
# Chạy: .venv\Scripts\python.exe -I tools\fbx_remove_mesh.py <in.fbx> <out.fbx> <tên mesh> [tên mesh ...]
#       .venv\Scripts\python.exe -I tools\fbx_remove_mesh.py --selftest <in.fbx>   (đọc + ghi lại không xóa gì, phải trùng byte)
import struct, sys, zlib
sys.stdout.reconfigure(encoding="utf-8")

def parse(b):
    ver = struct.unpack("<I", b[23:27])[0]
    big = ver >= 7500
    H = 25 if big else 13
    def rec(pos):
        if big: end, nprop, plen, nl = struct.unpack("<QQQB", b[pos:pos + 25])
        else: end, nprop, plen, nl = struct.unpack("<IIIB", b[pos:pos + 13])
        if end == 0: return None, pos + H
        name = b[pos + H:pos + H + nl].decode()
        p0 = pos + H + nl
        raw = b[p0:p0 + plen]
        kids, p = [], p0 + plen
        while p < end:
            k, p = rec(p)
            if k is None: break
            kids.append(k)
        # node có con luôn kết thúc bằng null record; node không con thì không có (trừ khi file gốc vẫn ghi)
        has_null = (end - (p0 + plen)) > 0 and not kids or bool(kids)
        return [name, nprop, raw, kids, has_null], end
    pos, top = 27, []
    while True:
        n, pos = rec(pos)
        if n is None: break
        top.append(n)
    footer = b[pos:]
    return ver, b[:27], top, footer, pos

def props(raw, nprop):
    """Giải mã nhẹ các thuộc tính (đủ để đọc id/tên)."""
    out, p = [], 0
    for _ in range(nprop):
        t = chr(raw[p]); p += 1
        if t in "YCIFDL":
            f = {"Y": "<h", "C": "<?", "I": "<i", "F": "<f", "D": "<d", "L": "<q"}[t]
            out.append(struct.unpack(f, raw[p:p + struct.calcsize(f)])[0]); p += struct.calcsize(f)
        elif t in "SR":
            n = struct.unpack("<I", raw[p:p + 4])[0]; d = raw[p + 4:p + 4 + n]; p += 4 + n
            out.append(d.decode("latin1") if t == "S" else d)
        else:
            n, enc, cl = struct.unpack("<III", raw[p:p + 12]); p += 12; d = raw[p:p + cl]; p += cl
            if enc: d = zlib.decompress(d)
            fm = {"f": "f", "d": "d", "i": "i", "l": "q", "b": "b"}[t]
            out.append(list(struct.unpack("<%d%s" % (n, fm), d)))
    return out

def set_int_prop(node, value):
    """Thay thuộc tính đầu tiên kiểu I (vd. Count) bằng value."""
    raw = node[2]
    assert raw[0:1] == b"I"
    node[2] = b"I" + struct.pack("<i", value) + raw[5:]

def serialize(ver, header, top, footer_tail_from_orig, orig_layout):
    big = ver >= 7500
    H = 25 if big else 13
    null = b"\x00" * H
    out = bytearray(header)
    def w(n):
        name, nprop, raw, kids, has_null = n
        start = len(out)
        out.extend(b"\x00" * H)
        nb = name.encode(); out.extend(nb); out.extend(raw)
        for k in kids: w(k)
        if has_null: out.extend(null)
        end = len(out)
        hdr = struct.pack("<QQQB", end, nprop, len(raw), len(nb)) if big else struct.pack("<IIIB", end, nprop, len(raw), len(nb))
        out[start:start + H] = hdr
    for n in top: w(n)
    out.extend(null)
    # footer: id 16 byte (giữ của file gốc), các byte 0, version, 120 số 0, magic.
    # Số byte 0 = của file gốc + độ dời vị trí cuối node (giữ nguyên độ căn lề của version); file không đổi thì ra đúng byte gốc.
    # (Không có 1 công thức chung: Maya cũ căn 16 + 4, Blender căn version vào bội 16, nên bám theo file gốc.)
    out.extend(footer_tail_from_orig["id"])
    out.extend(bytes(footer_tail_from_orig["z"] + ((footer_tail_from_orig["after"] - (len(out) - 16)) % 16)))
    out.extend(struct.pack("<I", ver)); out.extend(b"\x00" * 120)
    out.extend(bytes.fromhex("f85a8c6adef5d97eece90ce3758f290b"))
    return bytes(out)

def footer_info(b, after_null):
    foot = b[after_null:]
    z = next(i for i in range(16, len(foot)) if foot[i])   # byte khác 0 đầu tiên sau id = version
    return {"id": foot[:16], "z": z - 16, "after": after_null}

def child(n, name):
    return next((k for k in n[3] if k[0] == name), None)

def remove_meshes(top, names):
    T = {n[0]: n for n in top}
    objs = T["Objects"]
    info = {}
    for o in objs[3]:
        pr = props(o[2], o[1])
        info[pr[0]] = (o[0], pr[1].split("\x00")[0], pr[2] if len(pr) > 2 else "")
    conns = [(k, props(k[2], k[1])) for k in T["Connections"][3]]
    kill = set()
    for i, (typ, nm, cls) in info.items():
        if typ == "Model" and cls == "Mesh" and nm in names: kill.add(i)
    missing = set(names) - {info[i][1] for i in kill}
    if missing: raise SystemExit("Không thấy mesh: %s" % ", ".join(sorted(missing)))
    # Geometry nối vào model; Skin nối vào Geometry; Cluster nối vào Skin
    for _ in range(3):
        for k, pr in conns:
            if pr[0] != "OO": continue
            a, bb = pr[1], pr[2]
            if bb in kill and info.get(a, ("",))[0] == "Geometry": kill.add(a)
            if bb in kill and info.get(a, ("", "", ""))[2] == "Skin": kill.add(a)
            if bb in kill and info.get(a, ("", "", ""))[2] == "Cluster": kill.add(a)
    removed = {}
    for i in kill: removed[info[i][0]] = removed.get(info[i][0], 0) + 1
    objs[3] = [o for o in objs[3] if props(o[2], o[1])[0] not in kill]
    nconn = len(T["Connections"][3])
    T["Connections"][3] = [k for k, pr in conns if pr[1] not in kill and pr[2] not in kill]
    nconn -= len(T["Connections"][3])
    # PoseNode trong bind pose
    # exporter Maya/Blender ghi một BindPose cho mỗi skin: pose mất mesh và không còn mesh nào thì bỏ cả pose
    npose, drop_pose = 0, set()
    meshes = {i for i, v in info.items() if v[0] == "Model" and v[2] == "Mesh"} - kill
    for o in objs[3]:
        if o[0] == "Pose":
            keep, hit = [], False
            for k in o[3]:
                if k[0] == "PoseNode":
                    nd = child(k, "Node")
                    if nd and props(nd[2], nd[1])[0] in kill: npose += 1; hit = True; continue
                keep.append(k)
            o[3] = keep
            nb = child(o, "NbPoseNodes")
            if nb: set_int_prop(nb, sum(1 for k in keep if k[0] == "PoseNode"))
            has_mesh = any(props(child(k, "Node")[2], 1)[0] in meshes for k in keep if k[0] == "PoseNode")
            if hit and not has_mesh: drop_pose.add(props(o[2], o[1])[0])
    if drop_pose:
        objs[3] = [o for o in objs[3] if props(o[2], o[1])[0] not in drop_pose]
        removed["Pose"] = removed.get("Pose", 0) + len(drop_pose)
        kill |= drop_pose
    # Definitions: số đếm theo loại object
    defs = T.get("Definitions")
    if defs:
        total = 0
        for ot in defs[3]:
            if ot[0] != "ObjectType": continue
            typ = props(ot[2], ot[1])[0]
            cnt = child(ot, "Count")
            if cnt:
                c = props(cnt[2], cnt[1])[0] - removed.get(typ, 0)
                set_int_prop(cnt, c); total += c
        cnt = child(defs, "Count")
        if cnt: set_int_prop(cnt, total)
    return sorted(info[i][0] + ("/" + info[i][2] if info[i][2] else "") + " " + info[i][1] for i in kill), nconn, npose

def main():
    if sys.argv[1] == "--selftest":
        b = open(sys.argv[2], "rb").read()
        ver, hdr, top, footer, after = parse(b)
        o = serialize(ver, hdr, top, footer_info(b, after), None)
        print("selftest", "TRÙNG BYTE" if o == b else "KHÁC (%d vs %d byte)" % (len(o), len(b)))
        if o != b:
            i = next(i for i in range(min(len(o), len(b))) if o[i] != b[i]); print("lệch đầu tiên ở byte", i)
        return
    src, dst, names = sys.argv[1], sys.argv[2], sys.argv[3:]
    b = open(src, "rb").read()
    ver, hdr, top, footer, after = parse(b)
    gone, nconn, npose = remove_meshes(top, set(names))
    o = serialize(ver, hdr, top, footer_info(b, after), None)
    open(dst, "wb").write(o)
    print("Đã bỏ %d object:" % len(gone))
    for g in gone: print("  ", g)
    print("Bỏ %d connection, %d PoseNode. %d -> %d byte. Ghi: %s" % (nconn, npose, len(b), len(o), dst))

if __name__ == "__main__":
    main()
