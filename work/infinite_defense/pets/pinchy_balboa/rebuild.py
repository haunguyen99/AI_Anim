for n in list(api.ls("Object")): 
    try: api.delete_node(n)
    except Exception as e: print("x", n, e)
print(api.import_file(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa\_orig\Pet_Pinchy_Balboa_mesh_original.fbx"))
print(api.ls("Object"))
