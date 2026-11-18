ns = {}; exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\wind_chameleon\anim\idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\wind_chameleon\anim\attack.py").read(), g)
g['apply'](api, g['pose'](FRAME))
