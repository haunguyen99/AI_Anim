"""Xuất FBX thô từ Frolvy (chạy trong cổng có clip đang mở). MODE = 'attack' | 'idle' | 'base' (đặt trước khi exec)."""
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_23_Kitsune_Nine_Mist"
def clean_layers():
    api.set_active_layer(0)
    for L in range(len(api.layers()) - 1, 0, -1): api.delete_layer(L)
if MODE in ("attack", "idle"):
    n = 30 if MODE == "attack" else 48
    api.set_frame(1); api.set_frame(0)
    defs = [j for j in api.ls("Joint") if j.startswith("DEF_")]
    api.set_frame_range(0, n)
    print(MODE, "joints", len(defs), "bake", api.bake_keys(defs, 0, n, 1, 'all', True), "export", api.export_scene(D + r"\raw_%s.fbx" % MODE.capitalize(), 'fbx', True, 0, n, 30))
    clean_layers()
else:
    CT = [c for c in api.ls("Curve") if c.startswith("CTL_") and c != "CTL_Main"] + ["CTL_Main"]
    api.set_frame_range(0, 30)
    for f in range(0, 31):
        api.set_frame(f)
        for c in CT:
            if c == "CTL_TailFan": continue
            api.rotate(c, 0, 0, 0); api.move(c, 0, 0, 0)
        api.set_attr("CTL_TailFan.fan", 0.0)
        api.select(CT); api.set_key()
    api.set_frame(1); api.set_frame(0); api.set_frame_range(0, 1)
    print("base export", api.export_scene(D + r"\raw_Base.fbx", 'fbx', True, 0, 1, 30))
    api.set_frame_range(0, 30)
