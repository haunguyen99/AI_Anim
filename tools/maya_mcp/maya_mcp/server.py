"""Maya 2024 MCP server.

Nói chuyện với listener chạy trong Maya (maya_side/maya_mcp_listener.py) qua 127.0.0.1:7022.
Maya phải đang mở và đã bật listener (hoặc dùng maya_launch để mở Maya có sẵn listener).

Nhóm tool:
- maya_launch, maya_ping                 : mở Maya / kiểm tra kết nối
- maya_exec, maya_eval                   : chạy Python tùy ý trong Maya (maya.cmds có sẵn)
- maya_scene_info, maya_ls, maya_hierarchy : đọc scene
- maya_get_attrs, maya_set_attrs, maya_set_keys, maya_get_keys : thuộc tính và key
- maya_open, maya_save, maya_import_fbx, maya_export_fbx : file
- maya_snapshot                          : chụp viewport một frame, trả ảnh về để xem
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP, Image

HOST = os.environ.get("MAYA_MCP_HOST", "127.0.0.1")
PORT = int(os.environ.get("MAYA_MCP_PORT", "7022"))
MAYA_EXE = os.environ.get("MAYA_EXE", r"C:\Program Files\Autodesk\Maya2024\bin\maya.exe")
LISTENER_DIR = (Path(__file__).resolve().parent.parent / "maya_side").as_posix()

mcp = FastMCP("maya")


def _send(code: str, mode: str = "exec", timeout: float = 600) -> dict:
    try:
        with socket.create_connection((HOST, PORT), timeout=5) as s:
            s.settimeout(timeout)
            s.sendall((json.dumps({"code": code, "mode": mode}) + "\n").encode("utf-8"))
            buf = b""
            while not buf.endswith(b"\n"):
                chunk = s.recv(65536)
                if not chunk:
                    break
                buf += chunk
    except (ConnectionRefusedError, socket.timeout, OSError) as e:
        return {"ok": False, "error": (
            f"Không kết nối được Maya ở {HOST}:{PORT} ({e}). Mở Maya 2024 và chạy trong Script Editor (Python):\n"
            f'import sys; sys.path.insert(0, r"{LISTENER_DIR}"); '
            "import maya_mcp_listener; maya_mcp_listener.start()\n"
            "hoặc gọi tool maya_launch.")}
    return json.loads(buf.decode("utf-8"))


def _call(code: str, timeout: float = 600) -> Any:
    """Chạy code (gán `result`) và trả result; ném lỗi nếu Maya báo lỗi."""
    res = _send("import maya.cmds as cmds\n" + code, "exec", timeout)
    if not res.get("ok"):
        raise RuntimeError(res.get("error"))
    return res.get("result")


def _q(v: Any) -> str:
    """Python literal for embedding a value in Maya code (None/True stay valid Python)."""
    return repr(v)


# ---------------------------------------------------------------- kết nối

@mcp.tool()
def maya_ping() -> dict:
    """Kiểm tra Maya có đang nghe không; trả phiên bản Maya, file scene và frame hiện tại."""
    res = _send(
        "import maya.cmds as cmds\n"
        "result = {'version': cmds.about(version=True), 'scene': cmds.file(q=True, sn=True),"
        " 'time': cmds.currentTime(q=True), 'fps_unit': cmds.currentUnit(q=True, time=True)}")
    return res


@mcp.tool()
def maya_launch(scene: str = "", wait_seconds: int = 120) -> dict:
    """Mở Maya 2024 với listener bật sẵn (mất khoảng 30–90 giây). scene: file .ma/.mb để mở (tùy chọn)."""
    if _send("result = 1", "exec", 3).get("ok"):
        return {"ok": True, "note": "Maya đã chạy và đang nghe sẵn"}
    py = (f'import sys; sys.path.insert(0, r\\"{LISTENER_DIR}\\"); '
          'import maya_mcp_listener; maya_mcp_listener.start()')
    args = [MAYA_EXE, "-command", f'python("{py}")']
    if scene:
        args += ["-file", str(Path(scene).resolve())]
    subprocess.Popen(args, creationflags=getattr(subprocess, "DETACHED_PROCESS", 0))
    t0 = time.time()
    while time.time() - t0 < wait_seconds:
        time.sleep(3)
        if _send("result = 1", "exec", 3).get("ok"):
            return {"ok": True, "seconds": round(time.time() - t0)}
    return {"ok": False, "error": f"Maya chưa trả lời sau {wait_seconds}s, gọi maya_ping lại sau"}


# ---------------------------------------------------------------- chạy code

@mcp.tool()
def maya_exec(code: str, timeout: float = 600) -> dict:
    """Chạy Python trong Maya (namespace __main__, giữ biến giữa các lần gọi).
    Gán biến `result` để trả giá trị về; print() được gom vào stdout.
    Ví dụ: "import maya.cmds as cmds\\nresult = cmds.ls(type='joint')"."""
    return _send(code, "exec", timeout)


@mcp.tool()
def maya_eval(expression: str) -> dict:
    """Tính một biểu thức Python trong Maya và trả kết quả, ví dụ "cmds.playbackOptions(q=True, max=True)"."""
    return _send(expression, "eval")


# ---------------------------------------------------------------- đọc scene

@mcp.tool()
def maya_scene_info() -> Any:
    """Tóm tắt scene: file, fps, khoảng frame, số mesh/joint/camera, các node gốc, anim layers."""
    return _call(
        "result = {"
        "'scene': cmds.file(q=True, sn=True),"
        "'time_unit': cmds.currentUnit(q=True, time=True),"
        "'linear_unit': cmds.currentUnit(q=True, linear=True),"
        "'up_axis': cmds.upAxis(q=True, axis=True),"
        "'range': [cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)],"
        "'current': cmds.currentTime(q=True),"
        "'meshes': len(cmds.ls(type='mesh', noIntermediate=True)),"
        "'joints': len(cmds.ls(type='joint')),"
        "'cameras': cmds.ls(type='camera'),"
        "'roots': cmds.ls(assemblies=True),"
        "'anim_layers': cmds.ls(type='animLayer'),"
        "'selection': cmds.ls(sl=True)}")


@mcp.tool()
def maya_ls(type: str = "", pattern: str = "", selected: bool = False, limit: int = 500) -> Any:
    """Liệt kê node (cmds.ls). type: 'joint', 'mesh', 'transform', 'nurbsCurve'... pattern: tên có thể có *."""
    return _call(
        f"kw = {{'long': False}}\n"
        f"if {_q(type)}: kw['type'] = {_q(type)}\n"
        f"if {selected}: kw['sl'] = True\n"
        f"r = cmds.ls({_q(pattern)}, **kw) if {_q(pattern)} else cmds.ls(**kw)\n"
        f"result = {{'count': len(r), 'nodes': r[:{limit}]}}")


@mcp.tool()
def maya_hierarchy(root: str, max_depth: int = 30) -> Any:
    """Cây con của một node (vd. joint gốc), dạng lồng nhau {name, type, children}."""
    return _call(
        "def walk(n, d):\n"
        "    kids = cmds.listRelatives(n, children=True, type='transform', fullPath=False) or []\n"
        "    kids += cmds.listRelatives(n, children=True, type='joint') or []\n"
        "    kids = list(dict.fromkeys(kids))\n"
        f"    return {{'name': n, 'type': cmds.nodeType(n), 'children': [walk(k, d+1) for k in kids] if d < {max_depth} else '...'}}\n"
        f"result = walk({_q(root)}, 0)")


# ---------------------------------------------------------------- thuộc tính, key

@mcp.tool()
def maya_get_attrs(nodes: list[str], attrs: list[str] | None = None, frame: float | None = None) -> Any:
    """Đọc thuộc tính của node (mặc định translate/rotate/scale). frame: đọc tại frame đó."""
    attrs = attrs or ["translate", "rotate", "scale"]
    return _call(
        "result = {}\n"
        f"for n in {_q(nodes)}:\n"
        "    result[n] = {}\n"
        f"    for a in {_q(attrs)}:\n"
        f"        kw = {{'time': {frame}}} if {frame is not None} else {{}}\n"
        "        v = cmds.getAttr(n + '.' + a, **kw)\n"
        "        result[n][a] = v[0] if isinstance(v, list) and len(v) == 1 and isinstance(v[0], tuple) else v")


@mcp.tool()
def maya_set_attrs(values: dict[str, Any]) -> Any:
    """Đặt thuộc tính: {"node.attr": số hoặc [x,y,z]}, vd. {"pelvis.rotate": [0,10,0]}."""
    return _call(
        f"for k, v in {_q(values)}.items():\n"
        "    if isinstance(v, list): cmds.setAttr(k, *v)\n"
        "    elif isinstance(v, str): cmds.setAttr(k, v, type='string')\n"
        "    else: cmds.setAttr(k, v)\n"
        f"result = len({_q(values)})")


@mcp.tool()
def maya_set_keys(keys: list[dict], tangent: str = "auto") -> Any:
    """Đặt key. Mỗi phần tử: {"node": "...", "attr": "rotateX", "frame": 10, "value": 25}.
    tangent: auto | spline | linear | step | flat | clamped (step = blocking CONSTANT)."""
    return _call(
        f"tg = {_q(tangent)}\n"
        "ot = 'step' if tg == 'step' else tg\n"
        "it = 'linear' if tg == 'step' else tg\n"
        f"for k in {_q(keys)}:\n"
        "    cmds.setKeyframe(k['node'], attribute=k['attr'], time=k['frame'], value=k['value'],"
        " inTangentType=it, outTangentType=ot)\n"
        f"result = len({_q(keys)})")


@mcp.tool()
def maya_get_keys(nodes: list[str], attrs: list[str] | None = None) -> Any:
    """Đọc key của node: {node: {attr: [[frame, value], ...]}}. attrs bỏ trống = mọi attr có key."""
    return _call(
        "result = {}\n"
        f"for n in {_q(nodes)}:\n"
        "    result[n] = {}\n"
        f"    al = {_q(attrs)} or (cmds.listAnimatable(n) or [])\n"
        "    for a in al:\n"
        "        a = a.split('.')[-1]\n"
        "        t = cmds.keyframe(n, attribute=a, q=True, timeChange=True)\n"
        "        if t:\n"
        "            v = cmds.keyframe(n, attribute=a, q=True, valueChange=True)\n"
        "            result[n][a] = [list(p) for p in zip(t, v)]")


# ---------------------------------------------------------------- file

@mcp.tool()
def maya_open(path: str, force: bool = False) -> Any:
    """Mở scene .ma/.mb. force=True bỏ thay đổi chưa lưu của scene đang mở."""
    return _call(f"result = cmds.file({_q(str(Path(path).resolve()))}, open=True, force={force})")


@mcp.tool()
def maya_save(path: str = "") -> Any:
    """Lưu scene. path bỏ trống = lưu đè file hiện tại; có path = Save As (.ma hoặc .mb)."""
    if not path:
        return _call("result = cmds.file(save=True)")
    p = str(Path(path).resolve())
    t = "mayaBinary" if p.lower().endswith(".mb") else "mayaAscii"
    return _call(f"cmds.file(rename={_q(p)})\nresult = cmds.file(save=True, type={_q(t)})")


@mcp.tool()
def maya_import_fbx(path: str) -> Any:
    """Nhập FBX vào scene đang mở; trả danh sách node mới."""
    p = Path(path).resolve().as_posix()
    return _call(
        "cmds.loadPlugin('fbxmaya', quiet=True)\n"
        "before = set(cmds.ls())\n"
        f"cmds.file({_q(p)}, i=True, type='FBX', ignoreVersion=True, mergeNamespacesOnClash=False)\n"
        "new = sorted(set(cmds.ls()) - before)\n"
        "result = {'new_nodes': len(new), 'roots': cmds.ls(assemblies=True)}")


@mcp.tool()
def maya_export_fbx(path: str, selection: list[str] | None = None, bake: bool = True,
                    start: float | None = None, end: float | None = None) -> Any:
    """Xuất FBX (chọn node hoặc cả scene). bake=True nướng anim trong khoảng start–end
    (mặc định khoảng playback)."""
    p = Path(path).resolve().as_posix()
    return _call(
        "import maya.mel as mel\n"
        "cmds.loadPlugin('fbxmaya', quiet=True)\n"
        f"s = {start} if {start is not None} else cmds.playbackOptions(q=True, min=True)\n"
        f"e = {end} if {end is not None} else cmds.playbackOptions(q=True, max=True)\n"
        "mel.eval('FBXResetExport')\n"
        f"mel.eval('FBXExportBakeComplexAnimation -v {str(bake).lower()}')\n"
        "mel.eval('FBXExportBakeComplexStart -v %d' % s)\n"
        "mel.eval('FBXExportBakeComplexEnd -v %d' % e)\n"
        "mel.eval('FBXExportSkins -v true'); mel.eval('FBXExportShapes -v true')\n"
        f"sel = {_q(selection)}\n"
        "if sel: cmds.select(sel, r=True)\n"
        f"mel.eval('FBXExport -f \"{p}\"' + (' -s' if sel else ''))\n"
        f"result = {_q(p)}")


# ---------------------------------------------------------------- xem

@mcp.tool()
def maya_snapshot(frame: float | None = None, camera: str = "", width: int = 960, height: int = 540) -> Image:
    """Chụp viewport (playblast một frame) và trả ảnh PNG để xem. camera: tên camera, bỏ trống = view đang mở."""
    out = Path(tempfile.gettempdir()) / f"maya_mcp_snap_{int(time.time()*1000)}"
    _call(
        f"f = {frame} if {frame is not None} else cmds.currentTime(q=True)\n"
        f"cam = {_q(camera)}\n"
        "if cam:\n"
        "    p = cmds.getPanel(withFocus=True)\n"
        "    if cmds.getPanel(typeOf=p) != 'modelPanel': p = cmds.getPanel(type='modelPanel')[0]\n"
        "    cmds.modelPanel(p, e=True, camera=cam)\n"
        f"result = cmds.playblast(frame=[f], format='image', compression='png', filename={_q(out.as_posix())},"
        f" widthHeight=[{width}, {height}], percent=100, viewer=False, showOrnaments=False, offScreen=True,"
        " forceOverwrite=True, framePadding=4)")
    pngs = sorted(out.parent.glob(out.name + "*.png"))
    if not pngs:
        raise RuntimeError("playblast không tạo ra ảnh")
    data = pngs[-1].read_bytes()
    for f in pngs:
        f.unlink(missing_ok=True)
    return Image(data=data, format="png")


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
