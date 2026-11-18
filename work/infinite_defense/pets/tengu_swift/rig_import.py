for n in list(api.ls("Object")) + list(api.ls("Joint")) + list(api.ls("Curve")) + [g for g in api.ls("Group") if g not in ("persp","top","front","side")]:
    try: api.delete_node(n)
    except Exception: pass
print("clean", api.ls("Object"), len(api.ls("Joint")))
print(api.import_file(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\tengu_swift\Pet_Tengu_Swift.fbx"))
for o in ("Pet_tengu_swift", "Vu_khi_Pet_tengu_swift"):   # Frolvy them hau to "1" khi ten da tung dung
    if o + "1" in api.ls("Object"): api.rename(o + "1", o)
for n in api.ls("Object"):
    md = api.mesh_data(n); P = md['positions']; xs=P[0::3]; ys=P[1::3]; zs=P[2::3]
    print(n, len(xs), "x", round(min(xs),3), round(max(xs),3), "y", round(min(ys),3), round(max(ys),3), "z", round(min(zs),3), round(max(zs),3))
print(api.ls("Joint"))

# quat Ba Tieu: dua vao nam tay phai ngay tu bind (nam tay x -0.319, y 0.34, z -0.037; cuon quat x -0.372, y -0.005, z 0)
api.move("Vu_khi_Pet_tengu_swift", 0.053, 0.345, -0.037); api.select(["Vu_khi_Pet_tengu_swift"]); print(api.freeze_transform()); api.select([])
