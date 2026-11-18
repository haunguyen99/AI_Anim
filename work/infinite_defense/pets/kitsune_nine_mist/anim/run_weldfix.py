# hai đuôi trong (Tail2 L/R) dính nhau ở gốc: chia đều trọng số các đỉnh mối hàn để không rách khi hai đuôi quay khác nhau
import math
_ns = {"api": api}
exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read(), _ns)
NB, IDX, V, TAILS = _ns["NB"], _ns["IDX"], _ns["V"], _ns["TAILS"]
tl = {t['s']: set(t['verts']) for t in TAILS if t['k'] == 2}
L, R = tl["L"], tl["R"]
cross = [(a, b) for a in L for b in NB[a] if b in R]
vs = sorted(set([a for a, b in cross] + [b for a, b in cross]))
print("mối hàn:", len(cross), "cạnh,", len(vs), "đỉnh")
rows = []
for i in vs:
    acc = {}
    nbs = [i] + [n for n in NB[i] if (n in L or n in R)]
    # trung bình trọng số đỉnh + hàng xóm bên kia: đều 2 phía
    for n in nbs:
        for j, v in api.vertex_weights(IDX[n]):
            if v > 0: acc[j] = acc.get(j, 0) + v / len(nbs)
    r = sorted(acc.items(), key=lambda a: -a[1])[:4]; t = sum(v for _, v in r); rows.append([(j, v / t) for j, v in r])
api.select([_ns["MESH"]]); api.set_skin_weights([IDX[i] for i in vs], rows); print("done")
