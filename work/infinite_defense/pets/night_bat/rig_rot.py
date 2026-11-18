api.rotate("Pet_Night_Bat", -90, 0, 0); api.select(["Pet_Night_Bat"]); print(api.freeze_transform()); api.select([])
md = api.mesh_data("Pet_Night_Bat"); P = md['positions']; xs=P[0::3]; ys=P[1::3]; zs=P[2::3]
print("x", min(xs), max(xs), "y", min(ys), max(ys), "z", min(zs), max(zs))
