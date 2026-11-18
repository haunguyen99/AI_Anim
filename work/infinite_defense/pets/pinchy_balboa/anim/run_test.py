exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\pinchy_balboa\anim\make_clips.py").read())
api.set_frame_range(0, 48); ns['build'](api)
api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(False); api.select([])
