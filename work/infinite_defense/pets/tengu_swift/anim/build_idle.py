W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\tengu_swift\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns); ns['build'](api); print("idle built", api.list_keys("CTL_Root_M.ty")[:3])
ns['hold_fix'](api, 48); print("hold fixed")
