r=open("run_attack.py",encoding="utf-8").read()
r=r.replace('exec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read())\nfor t in TAILS:','_ns = {"api": api}\nexec(open(r"C:\Users\Admin\Documents\AI_animation\work\infinite_defense\pets\kitsune_nine_mist\kit_common.py").read(), _ns)\nfor t in _ns["TAILS"]:')
open("run_attack.py","w",encoding="utf-8").write(r)
