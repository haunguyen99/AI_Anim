md = api.mesh_data("Pet_lucky_neko"); P = md['positions']; n = len(P)//3
V = [(P[3*i], P[3*i+1], P[3*i+2]) for i in range(n)]
b = [v for v in V if 0.2 < v[1] < 0.3 and v[2] > 0.06 and abs(v[0]) < 0.07]
for v in sorted(b, key=lambda v:(round(v[1],2), v[2])): print(" %.3f %.3f %.3f" % v)
print("---- tassels")
m = api.mesh_data("Pet_lucky_neko.001"); Q = m['positions']
W = [(Q[3*i], Q[3*i+1], Q[3*i+2]) for i in range(len(Q)//3)]
t = [v for v in W if v[0] > -0.46 and v[1] > 0.0]
import collections
for k in (1, 2):
    pass
for v in sorted([v for v in W if v[0] > -0.47 and v[0] < -0.40 and v[2] > 0.0], key=lambda v:-v[1])[:40]: print(" %.3f %.3f %.3f" % v)
