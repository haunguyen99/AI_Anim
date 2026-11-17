ns = {}; exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\chrono_ouroboros\anim\idle2.py").read(), ns)
for c in ns['CTLS']:   # bỏ key thừa quá frame 72 (không làm rỗng curve)
    for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
        for k in list(api.list_keys(c + "." + a)):
            if k > ns['N']: api.delete_key(c + "." + a, int(round(k)))
ns['build'](api); api.select([])
print(api.save_scene("C:/Users/Admin/Documents/Ngoc/EndlessKicker/New_PET/Pet_25_Chrono_Ouroboros/chrono_ouroboros_idle_v5.fv"))
