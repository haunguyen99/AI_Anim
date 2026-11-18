# Chay trong Frolvy: dump vi tri dinh da bien dang tai vai frame ra /tmp/mp_pos_<TAG>.json (TAG, FRAMES dat truoc)
import json
out = {'bind': api.mesh_data('Pet_Mecha_Pup')['positions']}
for f in FRAMES:
    api.set_frame(f); out[f] = api.mesh_data('Pet_Mecha_Pup', True)['positions']
api.set_frame(1); api.set_frame(0)
json.dump(out, open('/tmp/mp_pos_%s.json' % TAG, 'w'))
print('ok', len(out), len(out['bind']))
