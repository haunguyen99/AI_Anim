for c in api.ls('Curve'):
    if c.startswith('CTL_'): api.rotate(c,0,0,0); api.move(c,0,0,0)
api.set_frame(5); api.set_frame(0)
api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(False); api.select([]); api.look_through('persp')
