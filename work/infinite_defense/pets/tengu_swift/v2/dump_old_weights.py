import json
print(api.save_scene('/tmp/tg/scratch_new.fv'))
print(api.open_scene('/tmp/tg/tengu_swift_rig.fv'))
md=api.mesh_data('Pet_tengu_swift'); V0=md['vertices']; P0=md['positions']
json.dump({'P':list(P0),'W':[api.vertex_weights(g) for g in V0]},open('/tmp/tg/oldw.json','w'))
print(len(V0), V0[:3])
