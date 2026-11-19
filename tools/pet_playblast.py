"""Playblast MP4 cac Pet (Linux): mo tung file .fv trong mot Frolvy rieng, dung camera1 goc 3/4, an control, xuat MP4 + poster.

  python3 -I tools/pet_playblast.py [so_pet[:Idle|:Attack] ...]      (khong doi so = ca 12 pet 11-23, 25; vd "11:Idle")
Ra: work/infinite_defense/_review_pet_new/playblast/Pet_<so>_<ten>_<Idle|Attack>.mp4 + .jpg
Khong dung cong cua nguoi dung (9877...): moi file mot Frolvy rieng cong 9900+, xong thi tat.
"""
import glob, json, math, os, signal, subprocess, sys, time

HOME = os.path.expanduser("~")
APP = HOME + "/.local/share/frolvy/Frolvy.AppImage"
MCP = HOME + "/.local/share/frolvy/Frolvy-mcp"
SRC = HOME + "/Projects/tvc_source/3D ANIM/EndlessKicker/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "infinite_defense", "_review_pet_new", "playblast")
PETS = {  # so: (thu muc, idle, attack)
    11: ("Pet_11_Mecha_Pup", "mecha_pup_idle.fv", "mecha_pup_attack.fv"),
    12: ("Pet_12_Pebble_Turtle", "PebbleTurtle_idle.fv", "PebbleTurtle_attack.fv"),
    13: ("Pet_13_Tiny_Chick", "tiny_chick_idle.fv", "tiny_chick_attack_new.fv"),
    14: ("Pet_14_Lucky_Neko", "lucky_neko_idle.fv", "lucky_neko_attack.fv"),
    15: ("Pet_15_Night_Bat", "night_bat_idle.fv", "night_bat_attack.fv"),
    16: ("Pet_16_Wind_Chameleon", "wind_chameleon_idle.fv", "wind_chameleon_attack.fv"),
    17: ("Pet_17_Pinchy_Balboa", "pinchy_idle_v7.fv", "pinchy_attack_v9.fv"),
    18: ("Pet_18_Tengu_Swift", "tengu_swift_idle.fv", "tengu_swift_attack.fv"),
    19: ("Pet_19_Kabuto_Striker", "kabuto_striker_idle.fv", "kabuto_striker_attack.fv"),
    22: ("Pet_22_Steam_Pug_Turbo", "steam_pug_turbo_idle.fv", "steam_pug_turbo_attack.fv"),
    23: ("Pet_23_Kitsune_Nine_Mist", "kitsune_nine_mist_idle.fv", "kitsune_nine_mist_attack_v6.fv"),
    25: ("Pet_25_Chrono_Ouroboros", "chrono_ouroboros_idle.fv", "chrono_ouroboros_attack.fv"),
}
CAM = r'''
import math
MESHES=%(meshes)r
CURVES=%(curves)r
JOINTS=%(joints)r
f0,f1=api.frame_range()
lo=[1e9]*3; hi=[-1e9]*3
for fr in range(f0,f1+1,max(1,(f1-f0)//12)):
    api.set_frame(fr)
    for m in MESHES:
        p=api.mesh_data(m,True)['positions']
        for i in range(0,len(p),3):
            for k in range(3):
                lo[k]=min(lo[k],p[i+k]); hi[k]=max(hi[k],p[i+k])
api.set_frame(f0)
c=[(lo[k]+hi[k])/2 for k in range(3)]
dim=max(hi[k]-lo[k] for k in range(3))
rx,ry=math.radians(-18),math.radians(32)
fwd=(-math.cos(rx)*math.sin(ry), math.sin(rx), -math.cos(rx)*math.cos(ry))
D=dim*1.8
pos=[c[k]-fwd[k]*D for k in range(3)]
cam=%(cam)r
for j in JOINTS: api.set_joint_draw_style(j,'none')
api.select(CURVES+JOINTS)
api.hide(True)
api.select([])
api.set_transform(cam,pos,[-18,32,0],[1,1,1])
api.look_through(cam)
print('range',f0,f1,'dim',round(dim,2))
'''
BLAST = '''
print(api.set_playblast_video(True,18,False,'',%(out)r))
print(api.playblast(%(f0)d,%(f1)d,%(dir)r))
'''

def call(port, tool, args):
    p = subprocess.Popen([MCP], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=dict(os.environ, DCC_MCP_PORT=str(port)))
    def send(m): p.stdin.write((json.dumps(m) + "\n").encode()); p.stdin.flush()
    def recv(i):
        while True:
            l = p.stdout.readline()
            if not l: return None
            m = json.loads(l)
            if m.get("id") == i: return m
    send({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "pb", "version": "1"}}})
    recv(1); send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": tool, "arguments": args}})
    r = recv(2); p.kill()
    return "".join(c.get("text", "") for c in (r or {}).get("result", {}).get("content", []) if c.get("type") == "text")

def run(code, port):
    t = call(port, "execute_code", {"code": code})
    try: d = json.loads(t)
    except Exception: raise RuntimeError("execute_code: " + t[:300])
    if not d.get("ok", True): raise RuntimeError(d)
    return d.get("output", "")

def ffmpeg():
    for p in glob.glob("/tmp/.mount_Frolvy*/usr/bin/ffmpeg/ffmpeg") + ["/tmp/pbwork/ffmpeg"]:
        if os.path.isfile(p): return p

def one(num, clip, fv, port):
    name = "%s_%s" % (PETS[num][0], clip)
    out = os.path.abspath(os.path.join(OUT, name + ".mp4"))
    os.makedirs(OUT, exist_ok=True)
    proc = subprocess.Popen([APP, fv], env=dict(os.environ, DCC_MCP_PORT=str(port)), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        for _ in range(60):
            time.sleep(1)
            if subprocess.run("ss -ltn | grep -q ':%d '" % port, shell=True).returncode == 0: break
        else: return "KHONG MO DUOC"
        time.sleep(3)
        info = json.loads(call(port, "get_scene_info", {}))
        names = {n["name"]: n["type"] for n in info["nodes"]}
        meshes = [n for n, t in names.items() if t == "Object"]
        cam = "camera1" if "camera1" in names else None
        if not cam: cam = run("print(api.create_camera())", port).strip()
        f0, f1 = info["frame_range"]
        keep = {cam}
        for m in meshes:  # mesh va tat ca cha cua no khong duoc an
            n = m
            while n and n not in keep or n == m:
                keep.add(n)
                n = json.loads(call(port, "get_node_info", {"name": n})).get("parent")
                if n in keep: break
        curves = [n for n, t in names.items() if t in ("Curve", "Group") and n not in keep and n not in ("persp", "top", "front", "side")]
        o = run(CAM % dict(meshes=meshes, curves=curves, joints=[n for n, t in names.items() if t == 'Joint'], cam=cam), port)
        call(port, "get_viewport_screenshot", {})  # ve lai viewport de isolate co hieu luc
        run(BLAST % dict(out=out, f0=f0, f1=f1, dir=os.path.dirname(out)), port)
        for _ in range(120):
            time.sleep(1)
            if run("print(api.playblasting())", port).strip() == "False": break
        st = run("print(api.playblast_status())", port).strip()
        ff = ffmpeg()
        if ff and os.path.isfile(out):
            subprocess.run([ff, "-v", "error", "-y", "-i", out, "-vf", "select=eq(n\\,%d),scale=640:-1" % ((f1 - f0) // 3), "-frames:v", "1", out[:-4] + ".jpg"])
        return ("OK " if os.path.isfile(out) else "LOI ") + o.strip().replace("\n", " ") + " | " + st[:90]
    finally:
        try: os.killpg(proc.pid, signal.SIGTERM)
        except Exception: pass
        time.sleep(2)
        subprocess.run("pid=$(ss -ltnp | grep ':%d ' | grep -o 'pid=[0-9]*' | head -1 | cut -d= -f2); [ -n \"$pid\" ] && kill $pid; true" % port, shell=True)

if __name__ == "__main__":
    args = [a.split(":") for a in sys.argv[1:]] or [[str(k)] for k in sorted(PETS)]
    port = 9900
    for a in args:
        n = int(a[0]); only = a[1].capitalize() if len(a) > 1 else None
        d, idle, atk = PETS[n]
        for clip, f in (("Idle", idle), ("Attack", atk)):
            if only and clip != only: continue
            fv = SRC + d + "/" + f
            t0 = time.time()
            try: r = one(n, clip, fv, port)
            except Exception as e: r = "LOI " + str(e)[:200]
            print("Pet %d %s: %s (%.0fs)" % (n, clip, r, time.time() - t0), flush=True)
            port += 1
