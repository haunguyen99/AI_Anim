"""Hero Textures - put the RPG2 Hero textures on the meshes by themselves whenever a scene is opened, in Frolvy.

Why: a Hero_Blade scene that is opened again can come back with its meshes on the grey default material (the textures
stay 'loaded' but are no longer assigned), and a playblast then shows a grey hero. Doing it by hand every time was
the user's complaint (2026-11-05: "tự động add texture mỗi khi mở file").

What it does, for any scene that has the Hero meshes (matched by name after the namespace):
  M_Char_Main_T2 + tex/T_Char_Main_T2_flipV.png -> char_main_t2_body, _hood, _scarf_1, _scarf_2
  M_Colorpalette + tex/T_Colorpalette_flipV.png -> Vk_t1_Dualblades_L, Vk_t1_Dualblades_R
It creates a material that is missing, loads the texture when it is not 'loaded', assigns the material, and puts the
selection back (assign_material leaves the meshes selected, and a selection outline shows in a playblast).

The PNGs are the original T_*.tga flipped top-to-bottom: Frolvy shows a .tga upside down (frolvy_feedback.md #15), the
flipped copy shows right. They were made from C:\\Project\\RPG_2\\Hero\\T_*.tga with Pillow (ImageOps.flip).

Automatic part: register() starts a poll (api.call_later, every 3 s). It looks at a signature of the scene (the object
names + the texture ids of the materials; opening a file loads its textures again, so the ids change) and applies only
when the signature changes, then stores the new signature so its own change does not trigger itself again. Nothing is
done while the scene stays the same, so it adds no undo steps while you work.

By hand / from Claude (works without the plugin):
    exec(open(r'C:\\Users\\huongbtx\\Documents\\Frolvy\\plugins\\hero_textures\\0.1.0\\hero_textures.py', encoding='utf-8').read())
    apply(api, force=True)
Plugins menu: Add Hero Textures (same call).
"""
import os

try:
    HERE = os.path.dirname(os.path.abspath(__file__))
except NameError:                                   # exec() from execute_code has no __file__
    HERE = r"C:\Users\huongbtx\Documents\Frolvy\plugins\hero_textures\0.1.0"
TEX = os.path.join(HERE, "tex")

SPEC = (
    ("M_Char_Main_T2", "T_Char_Main_T2_flipV.png",
     ("char_main_t2_body", "char_main_t2_hood", "char_main_t2_scarf_1", "char_main_t2_scarf_2")),
    ("M_Colorpalette", "T_Colorpalette_flipV.png",
     ("Vk_t1_Dualblades_L", "Vk_t1_Dualblades_R")),
)
POLL_SECONDS = 3.0
_state = {"sig": None}


def _targets(api, names):
    return [o for o in api.ls("Object") if o.split(":")[-1] in names]


def has_hero(api):
    return any(_targets(api, names) for _, _, names in SPEC)


def apply(api, log=print, force=False):
    """Textures on the Hero meshes. Returns [(material, [objects])] for what it did."""
    done = []
    sel = list(api.selection())
    try:
        for mat, png, names in SPEC:
            objs = _targets(api, names)
            if not objs:
                continue
            if mat not in api.materials():
                api.create_material(mat)
                api.set_material(mat, 1.0, 1.0, 1.0, 0.0, 0.6, 0.0, 0.0, 0.0, 1.0, False)
            if force or api.texture_state(mat) != "loaded":
                api.set_texture(mat, os.path.join(TEX, png))
            api.assign_material(mat, objs)
            done.append((mat, objs))
    finally:
        api.select(sel)
    if done:
        log("Hero Textures: %s" % ", ".join("%s on %d mesh(es)" % (m, len(o)) for m, o in done))
    return done


def _signature(api):
    objs = tuple(sorted(api.ls("Object")))
    tex = []
    for m in api.materials():
        v = api.material(m)
        tex.append((m, v[9] if len(v) > 9 else None))
    return (objs, tuple(tex))


def _tick(api, log):
    try:
        sig = _signature(api)
        if sig != _state["sig"]:
            if has_hero(api):
                apply(api, log=log)
                sig = _signature(api)               # our own change must not count as a new scene
            _state["sig"] = sig
    except Exception as e:                           # a poll must never die, a scene may be half loaded
        log("Hero Textures: %s" % e)
    finally:
        api.call_later(POLL_SECONDS, lambda: _tick(api, log))


def register(api):
    say = lambda m: api.log(m)
    api.command("Add Hero Textures", lambda: apply(api, log=say, force=True))
    _tick(api, say)
