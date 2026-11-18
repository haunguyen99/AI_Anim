D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_17_Pinchy_Balboa"
api.set_frame_range(0, 1); api.set_frame(1); api.set_frame(0)
d=[j for j in api.ls("Joint")]
for f in (1,0):
    api.set_frame(f); api.select(d); api.set_key()
api.set_frame(1); api.set_frame(0); api.select([])
print('base export', api.export_scene(D + r"\raw_Base.fbx", 'fbx', True, 0, 1, 30))
api.set_frame_range(0, 48)
