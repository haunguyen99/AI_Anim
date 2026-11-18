import json
print(api.save_scene('/tmp/tg/scratch_%s.fv'%TAG))
print(api.open_scene(SRC))
chs=('tx','ty','tz','rx','ry','rz','sx','sy','sz')
keyed=[n+'.'+ch for n in api.ls() if api.node_type(n)!='Object' for ch in chs if api.list_keys(n+'.'+ch)]
a,b=api.frame_range(); vals={}
for f in range(int(a),int(b)+1):
    api.set_frame(f); vals[f]={p:api.get_attr(p) for p in keyed}
api.set_frame(1); api.set_frame(0)
json.dump({'range':[a,b],'vals':vals},open('/tmp/tg/vals_%s.json'%TAG,'w'))
nodes=sorted({p.split('.')[0] for p in keyed}); api.select(nodes)
print('range',a,b,'keyed',len(keyed),'nodes',len(nodes), [n for n in nodes if not n.startswith('CTL_')])
print('save_anim',api.save_anim('tg18_'+TAG,int(a),int(b),nodes))
print('layers',api.list_layers() if hasattr(api,'list_layers') else '')
