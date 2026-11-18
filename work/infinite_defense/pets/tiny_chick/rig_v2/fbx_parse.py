import struct, zlib, sys
def parse(path):
    d = open(path, 'rb').read(); ver = struct.unpack('<I', d[23:27])[0]; big = ver >= 7500
    def node(o):
        if big: end, nprops, plen, nl = struct.unpack('<QQQB', d[o:o+25]); o += 25
        else: end, nprops, plen, nl = struct.unpack('<IIIB', d[o:o+13]); o += 13
        if end == 0: return None, o
        name = d[o:o+nl].decode(); o += nl
        props = []
        for _ in range(nprops):
            t = chr(d[o]); o += 1
            if t in 'YCFDILB':
                fmt = {'Y':'<h','C':'<?','F':'<f','D':'<d','I':'<i','L':'<q','B':'<b'}[t]; props.append(struct.unpack(fmt, d[o:o+struct.calcsize(fmt)])[0]); o += struct.calcsize(fmt)
            elif t in 'fdilb':
                n, enc, clen = struct.unpack('<III', d[o:o+12]); o += 12
                raw = d[o:o+clen]; o += clen
                if enc: raw = zlib.decompress(raw)
                fmt = {'f':'f','d':'d','i':'i','l':'q','b':'b'}[t]; props.append(list(struct.unpack('<%d%s' % (n, fmt), raw)))
            elif t in 'SR':
                n = struct.unpack('<I', d[o:o+4])[0]; o += 4; props.append(d[o:o+n]); o += n
        kids = []
        while o < end:
            k, o = node(o)
            if k is None: break
            kids.append(k)
        return (name, props, kids), end
    o = 27; top = []
    while o < len(d) - 100:
        n, o2 = node(o)
        if n is None: break
        top.append(n); o = o2
    return top
def find(n, name):
    return [k for k in n[2] if k[0] == name]
