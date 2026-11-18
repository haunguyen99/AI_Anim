md = api.mesh_data("Pet_lucky_neko"); P = md['positions']; n = len(P)//3
V = [(P[3*i], P[3*i+1], P[3*i+2]) for i in range(n)]
t = [v for v in V if v[2] < -0.07 and v[1] < 0.2]
print("tail", len(t))
for v in sorted(t, key=lambda v: v[2]): print(" %.3f %.3f %.3f" % v)
e = [v for v in V if v[1] > 0.43 and v[0] > 0]
print("ear L", len(e), "x", min(v[0] for v in e), max(v[0] for v in e), "y", min(v[1] for v in e), max(v[1] for v in e), "z", min(v[2] for v in e), max(v[2] for v in e))
h = [v for v in V if v[1] > 0.23]; print("head cx", sum(v[0] for v in h)/len(h), "z", (min(v[2] for v in h)+max(v[2] for v in h))/2)
for o in ("Pet_lucky_neko.001","Pet_lucky_neko.002"):
    m = api.mesh_data(o)["positions"]; k=len(m)//3
    print(o, [round(sum(m[i::3])/k,3) for i in range(3)])
