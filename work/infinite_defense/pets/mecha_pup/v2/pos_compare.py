import json, sys, math
from collections import defaultdict
old = json.load(open('/tmp/mp_pos_%s_old.json' % sys.argv[1])); new = json.load(open('/tmp/mp_pos_%s_new.json' % sys.argv[1]))
ob = old['bind']; nb = new['bind']
op = [ob[i:i+3] for i in range(0, len(ob), 3)]
cell = 0.02; grid = defaultdict(list)
for i, p in enumerate(op): grid[tuple(int(c//cell) for c in p)].append(i)
def nn(q):
    c = tuple(int(x//cell) for x in q); best = (9, None)
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            for dz in (-1,0,1):
                for i in grid.get((c[0]+dx,c[1]+dy,c[2]+dz), []):
                    d = math.dist(q, op[i])
                    if d < best[0]: best = (d, i)
    return best[1]
mp = [nn(nb[i:i+3]) for i in range(0, len(nb), 3)]
print('frame  max_dev(cm)  mean_dev(cm)  worst_vertex')
for f in new:
    if f == 'bind': continue
    o = old[f]; n = new[f]; ds = []
    for k, oi in enumerate(mp):
        ds.append(math.dist(n[k*3:k*3+3], o[oi*3:oi*3+3]) * 100)
    print(f, round(max(ds), 3), round(sum(ds)/len(ds), 4), ds.index(max(ds)))
