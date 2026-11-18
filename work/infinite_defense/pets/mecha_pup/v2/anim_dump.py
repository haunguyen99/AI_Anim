# Chay trong Frolvy. Dat TAG truoc khi exec: ghi gia tri moi kenh co key moi frame ra /tmp/mp_vals_<TAG>.json
# va luu animation vao thu vien ("mp11_<TAG>") de ap sang rig moi.
import json
chs = ('tx','ty','tz','rx','ry','rz','sx','sy','sz')
keyed = []
for n in api.ls():
    if api.node_type(n) == 'Object': continue
    for ch in chs:
        if api.list_keys(n + '.' + ch): keyed.append(n + '.' + ch)
a, b = api.frame_range()
vals = {}
for f in range(int(a), int(b) + 1):
    api.set_frame(f)
    vals[f] = {p: api.get_attr(p) for p in keyed}
api.set_frame(1); api.set_frame(0)
json.dump({'range': [a, b], 'vals': vals}, open('/tmp/mp_vals_%s.json' % TAG, 'w'))
nodes = sorted({p.split('.')[0] for p in keyed})
api.select(nodes)
print('keyed', len(keyed), 'nodes', len(nodes))
if globals().get('SAVE', True):
    print('save_anim', api.save_anim('mp11_' + TAG, int(a), int(b), nodes), api.list_anims())
