import json,time
res={}
for tag,f,frames in JOBS:
    api.save_scene('/tmp/tg/d_%d.fv'%int(time.time()*1000)); api.new_scene(); assert api.open_scene(f)
    api.set_frame(1); api.set_frame(0)
    out={}
    for fr in frames:
        api.set_frame(fr); md={}
        for ob in ('Pet_tengu_swift','Vu_khi_Pet_tengu_swift'):
            m=api.mesh_data(ob,True); out[(ob,fr)]=list(m['positions'])
    # bind pos: frame 0 with go_to_bind? use mesh_data no-arg
    bind={ob:list(api.mesh_data(ob)['positions']) for ob in ('Pet_tengu_swift','Vu_khi_Pet_tengu_swift')}
    res[tag]={'bind':bind,'def':{'%s|%d'%k:v for k,v in out.items()},'range':list(api.frame_range())}
    api.set_frame(1); api.set_frame(0)
json.dump(res,open(OUTJ,'w')); print({t:r['range'] for t,r in res.items()})
