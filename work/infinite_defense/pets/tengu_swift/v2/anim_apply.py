api.new_scene(); assert api.open_scene('/tmp/tg/rig_v2_keep.fv')
nodes=sorted(n for n in api.ls('Curve') if n.startswith('CTL_') and n!='CTL_Main')
api.set_frame(0); api.select(nodes)
print(TAG,len(nodes),'apply',api.apply_anim('tg18_'+TAG,0,'replace',nodes))
api.set_frame_range(0,LAST); api.set_frame(1); api.set_frame(0)
api.save_scene('/tmp/tg/_dummy.fv') if False else None
print('save',api.save_scene(OUT)); print(api.frame_range())
