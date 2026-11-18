import json
md = api.mesh_data("Pet_Kitsune_Nine_Mist")
json.dump({"idx": list(md['vertices']), "P": list(md['positions']), "fs": list(md['face_sizes']), "fc": list(md['face_corners'])}, open(r"C:\Users\Admin\AppData\Local\Temp\kit_mesh.json","w"))
print(len(md['vertices']), len(md['face_sizes']))
