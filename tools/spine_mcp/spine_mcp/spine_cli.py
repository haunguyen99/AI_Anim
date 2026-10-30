"""Thin wrapper around the Spine command-line interface (Spine.com)."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

SPINE_EXE = os.environ.get("SPINE_EXE", r"C:\Program Files\Spine\Spine.com")
# Editor version the launcher should load. Exports use this version's format.
SPINE_VERSION = os.environ.get("SPINE_VERSION", "4.2.43")

MAX_OUTPUT = 8000


def run(args: list[str | Path], timeout: int = 900, use_version: bool = True) -> dict:
    if not Path(SPINE_EXE).exists():
        raise FileNotFoundError(f"Spine CLI not found at {SPINE_EXE}. Set SPINE_EXE.")
    cmd = [SPINE_EXE]
    if use_version and SPINE_VERSION:
        cmd += ["-u", SPINE_VERSION]
    cmd += [str(a) for a in args]
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            creationflags=flags,
        )
    except subprocess.TimeoutExpired:
        return {"command": subprocess.list2cmdline(cmd), "exit_code": None,
                "output": f"Timed out after {timeout}s"}
    out = (p.stdout or "") + (p.stderr or "")
    if len(out) > MAX_OUTPUT:
        out = "...(truncated)...\n" + out[-MAX_OUTPUT:]
    return {"command": subprocess.list2cmdline(cmd), "exit_code": p.returncode, "output": out.strip()}
