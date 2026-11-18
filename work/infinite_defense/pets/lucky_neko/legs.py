md = api.mesh_data("Pet_lucky_neko"); P = md['positions']; n = len(P)//3
V = [(P[3*i], P[3*i+1], P[3*i+2]) for i in range(n)]
for sg in (1,):
    a = [v for v in V if sg*v[0] > 0.0 and v[1] < 0.09]
    print(len(a))
    for v in sorted(a, key=lambda v:(round(v[1],2), v[2])): print(" %.3f %.3f %.3f" % v)
