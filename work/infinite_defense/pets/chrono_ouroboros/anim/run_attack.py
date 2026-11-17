ns = {}; exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\chrono_ouroboros\anim\attack.py", encoding="utf8").read(), ns)
ns['build'](api); api.select([])
for c in ns['CTLS']:
    for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
        try: api.set_infinity(c + "." + a, "constant", "constant")
        except Exception: pass
print(api.save_scene("C:/Users/Admin/Documents/Ngoc/EndlessKicker/New_PET/Pet_25_Chrono_Ouroboros/chrono_ouroboros_attack_v1.fv"))
