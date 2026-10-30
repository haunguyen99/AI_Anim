"""Binary FBX 7.4 serializer (no compression: array encoding 0 is valid). Mirrors Blender's io_scene_fbx/encode_bin.py.
Port target: fbxbin.js. Element = (id:str, props:[(type, value)], kids:[Element]).
Property types: S string, R raw bytes, C char, I int32, L int64, D float64, i int32[], l int64[], f float32[], d float64[]."""
import struct

SENT = b"\0" * 13
HEAD = b"Kaydara FBX Binary\x20\x20\x00\x1a\x00"
FOOT_ID = b"\xfa\xbc\xab\x09\xd0\xc8\xd4\x66\xb1\x76\xfb\x83\x1c\xf7\x26\x7e"
FOOT_MAGIC = b"\xf8\x5a\x8c\x6a\xde\xf5\xd9\x7e\xec\xe9\x0c\xe3\x75\x8f\x29\x0b"
ALWAYS_SENT = {"AnimationStack", "AnimationLayer"}


def E(id, props=None, kids=None):
    return (id, props or [], kids or [])


def enc_prop(t, v):
    if t == "S":
        b = v.encode("utf8")
        return b"S" + struct.pack("<I", len(b)) + b
    if t == "R":
        return b"R" + struct.pack("<I", len(v)) + v
    if t == "C":
        return b"C" + v.encode("latin1")
    if t == "I":
        return b"I" + struct.pack("<i", v)
    if t == "L":
        return b"L" + struct.pack("<q", v)
    if t == "D":
        return b"D" + struct.pack("<d", v)
    fm = {"i": "i", "l": "q", "f": "f", "d": "d"}[t]
    data = struct.pack("<%d%s" % (len(v), fm), *v)
    return t.encode() + struct.pack("<III", len(v), 0, len(data)) + data


def enc_elem(el, pos, is_last, out, wide=False):
    # wide (FBX >= 7500): record header = 3 x uint64 and sentinel = 25 zero bytes (7.4: 3 x uint32, 13 bytes).
    # The version written must match the tree: a 7.7 template written as 7400 is refused by the FBX SDK (Unity, Maya).
    id, props, kids = el
    pb = b"".join(enc_prop(t, v) for t, v in props)
    idb = id.encode()
    hl = 24 if wide else 12
    sent = b"\0" * (hl + 1)
    p = pos + hl + 1 + len(idb) + len(pb)
    sub = []
    if kids:
        for k in kids:
            p = enc_elem(k, p, False, sub, wide)
        sub.append(sent)
        p += len(sent)
    elif (not props and not is_last) or id in ALWAYS_SENT:
        sub.append(sent)
        p += len(sent)
    out.append(struct.pack("<QQQ" if wide else "<III", p, len(props), len(pb)) + bytes([len(idb)]) + idb + pb)
    out.extend(sub)
    return p


def foot_id_of(path):
    """Footer code of an existing binary FBX (16 bytes right after the root sentinel). It is derived from the file's
    FileId / CreationTime: when a template's FileId / CreationTime are kept, its footer code must be kept too, or the
    FBX SDK (Unity 'Couldn't read file', Maya 'File is corrupted') refuses the file (SDR03, 2026-10-29)."""
    b = open(path, "rb").read(); ver = struct.unpack("<I", b[23:27])[0]; W = ver >= 7500
    H = 25 if W else 13; F = "<QQQB" if W else "<IIIB"; p = 27
    while b[p:p + H] != b"\0" * H:
        p = struct.unpack(F, b[p:p + H])[0]
    return b[p + H:p + H + 16]


def serialize(top, version=7400, foot_id=None):
    global FOOT_ID
    if foot_id is not None:
        saved = FOOT_ID; FOOT_ID = foot_id
        try:
            return serialize(top, version)
        finally:
            FOOT_ID = saved
    wide = version >= 7500
    out = [HEAD + struct.pack("<I", version)]
    pos = len(out[0])
    # children of the (virtual) root: laid out in order; the last one has is_last
    for i, el in enumerate(top):
        # enc_elem appends its own header before its children's bytes; keep order by collecting per element
        sub = []
        pos = enc_elem(el, pos, i == len(top) - 1, sub, wide)
        out.extend(sub)
    sent = b"\0" * (25 if wide else 13)
    out.append(sent)  # root sentinel
    pos += len(sent)
    out.append(FOOT_ID + b"\0" * 4)
    pos += 20
    pad = ((pos + 15) & ~15) - pos
    if pad == 0:
        pad = 16
    out.append(b"\0" * pad)
    out.append(struct.pack("<I", version))
    out.append(b"\0" * 120)
    out.append(FOOT_MAGIC)
    return b"".join(out)
