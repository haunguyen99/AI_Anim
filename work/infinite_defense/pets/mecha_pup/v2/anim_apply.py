# Chay trong Frolvy (rig v2 dang mo): ap animation da luu trong thu vien len cac control, dat tam frame.
# Can dat TAG va (tuy chon) LAST truoc khi exec.
nodes = sorted({n for n in api.ls() if n.startswith('CTL_')})
api.set_frame(0)
api.select(nodes)
print('apply', api.apply_anim('mp11_' + TAG, 0, 'replace', nodes))
api.set_frame_range(0, LAST)
api.set_frame(1); api.set_frame(0)
