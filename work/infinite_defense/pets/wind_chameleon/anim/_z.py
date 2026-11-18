api.set_frame(1)
for c in api.ls("Curve"):
    if c.startswith("CTL_"):
        for a in ("rx","ry","rz","tx","ty","tz"): api.set_attr(c+"."+a, 0.0)
        for a in ("sx","sy","sz"): api.set_attr(c+"."+a, 1.0)
api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])
api.look_through('side'); api.set_camera_ortho('side', True); api.set_attr('side.ow', 1.7); api.move('side', 100, 0.4, 0.05)
print(api.get_attr("chameleon.rx"), api.get_attr("chameleon.tx"), api.get_attr("chameleon.ty"))
