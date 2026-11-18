print(api.import_file(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_22_Steam_Pug_Turbo\Pet_Steam_Pug_Turbo.fbx"))
for n in api.ls("Object"):
    md = api.mesh_data(n); P = md['positions']; xs=P[0::3]; ys=P[1::3]; zs=P[2::3]
    print(n, len(xs), "x", round(min(xs),3), round(max(xs),3), "y", round(min(ys),3), round(max(ys),3), "z", round(min(zs),3), round(max(zs),3))
print(api.ls("Joint"))
