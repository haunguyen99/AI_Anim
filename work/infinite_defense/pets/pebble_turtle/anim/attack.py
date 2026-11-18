# Attack 36f (0..36): rut dau lay da (0-10), bat ra (10-15), KHAC SOI = frame 15, hoi (15-36). Base layer, chay trong Frolvy 9881.
api.open_scene(r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_12_Pebble_Turtle\PebbleTurtle_rig.fv")
api.select([]); api.reset_transforms(all_controls=True)
api.set_frame_range(0, 36)
F = [0, 6, 10, 13, 15, 19, 26, 36]
def tbl(*v): return dict(zip(F, v))
root_ty = tbl(0, -0.03, -0.04, 0.0, 0.01, 0.0, -0.008, 0)
root_tz = tbl(0, -0.02, -0.03, 0.05, 0.07, 0.04, 0.01, 0)
root_rx = tbl(0, -4, -6, 5, 7, 3, -1, 0)
K = {
 "CTL_Root_M": dict(ty=root_ty, tz=root_tz, rx=root_rx),
 "CTL_Neck_M": dict(rx=tbl(0, 10, 14, -8, -12, -4, 2, 0)),
 "CTL_Head_M": dict(tz=tbl(0, -0.20, -0.27, 0.03, 0.10, 0.05, 0.0, 0), rx=tbl(0, 4, 8, -4, -8, -2, 1, 0)),
 "CTL_Tail1_M": dict(rx=tbl(0, -10, -14, 8, 10, 3, -3, 0)),
 "CTL_Tail2_M": dict(rx=tbl(0, -8, -12, 10, 14, 4, -4, 0)),
}
fh = tbl(0, 10, 14, -6, -10, -4, 2, 0)
bh = tbl(0, -6, -9, 4, 6, 2, -1, 0)
for s in "LR":
    for pre, h in (("Front", fh), ("Back", bh)):
        hip = "CTL_%sHip_%s" % (pre, s)
        K[hip] = dict(rx=h, ty={f: -root_ty[f] for f in F}, tz={f: -root_tz[f] for f in F})
        K["CTL_%sAnkle_%s" % (pre, s)] = dict(rx={f: -0.8*h[f] for f in F})
for node, chs in K.items():
    for f in F:
        api.set_frame(f)
        for c, tb in chs.items(): api.set_attr(node + "." + c, tb[f])
        api.select([node]); api.set_key()
api.select([]); api.set_frame(0)
print("spit frame 15; keys", len(K), "nodes")
