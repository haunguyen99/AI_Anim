import json
d = {}
for o in api.ls("Object"):
    d[o] = {int(v): api.vertex_weights(v) for v in api.mesh_data(o)['vertices']}
json.dump(d, open(r"C:\Users\Admin\AppData\Local\Temp\_lucky_weights_before_bell.json", "w"))
print({o: len(x) for o, x in d.items()})
