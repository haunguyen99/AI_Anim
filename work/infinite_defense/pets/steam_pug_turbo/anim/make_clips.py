# MODE = "idle" | "attack" (dat o dau file chay). Chay: frolvy_port.py 9888 <file>
D = r"C:\Users\Admin\Documents\Ngoc\EndlessKicker\New_PET\Pet_22_Steam_Pug_Turbo"
W = r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\steam_pug_turbo\anim"
ns = {}; exec(open(W + r"\idle.py").read(), ns)
g = {"idle_pose": ns['pose'], "api": api}; exec(open(W + r"\attack.py").read(), g)
ALL = ns['CTLS']
def clear(n):
    for c in ALL:
        for a in ("rx", "ry", "rz", "tx", "ty", "tz"):
            try:
                for f in list(api.list_keys(c + "." + a)):
                    if f > n: api.delete_key(c + "." + a, int(round(f)))
            except Exception: pass
if MODE == "idle":
    ns['build'](api); api.set_frame(1); api.set_frame(0); print("idle saved", api.save_scene(D + r"\steam_pug_turbo_idle_new.fv"))
else:
    clear(30); g['build'](api); api.set_frame_range(0, 30); api.set_frame(1); api.set_frame(0); print("attack saved", api.save_scene(D + r"\steam_pug_turbo_attack_n2.fv"))
