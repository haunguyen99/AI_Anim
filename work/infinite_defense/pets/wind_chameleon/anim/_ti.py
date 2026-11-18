api.set_frame(1)
ns = {}; exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\wind_chameleon\anim\idle.py").read(), ns)
ns['apply'](api, ns['pose'](36))

api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])
api.look_through('side'); api.set_camera_ortho('side', True); api.set_attr('side.ow', 1.7); api.move('side', 100, 0.45, 0.05)
