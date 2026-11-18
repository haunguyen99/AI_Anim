# usage inside Frolvy: set CAMS then exec; hides the rig, positions the cameras
api.select(list(api.ls('Curve'))+list(api.ls('Joint'))); api.hide(True); api.select([])
api.look_through('front'); api.set_camera_ortho('front', True); api.set_attr('front.ow', 1.8); api.move('front', 0.0, 0.36, 100)
api.look_through('side'); api.set_camera_ortho('side', True); api.set_attr('side.ow', 1.8); api.move('side', 100, 0.36, 0.0)
