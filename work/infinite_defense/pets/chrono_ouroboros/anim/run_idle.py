ns = {}; exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\chrono_ouroboros\anim\idle.py").read(), ns)
# bắt buộc: control bind pose = 0 trước
ns['build'](api)
api.select([])
print(api.save_scene("C:/Users/Admin/Documents/Ngoc/EndlessKicker/New_PET/Pet_25_Chrono_Ouroboros/chrono_ouroboros_idle_v1.fv"))
