"""Đóng gói extension VS Code (.vsix) bằng Python, không cần Node/vsce.
Chạy:  .venv/Scripts/python.exe -I tools/vscode_ext/build_vsix.py [--install]
Ra:    tools/vscode_ext/dist/<publisher>.<name>-<version>.vsix ;  --install gọi `code --install-extension`.
"""
import json, shutil, subprocess, sys, zipfile
from pathlib import Path

SRC = Path(__file__).parent / "horus-sessions"
OUT = Path(__file__).parent / "dist"
sys.stdout.reconfigure(encoding="utf-8")
pkg = json.loads((SRC / "package.json").read_text("utf-8"))
vid = f"{pkg['publisher']}.{pkg['name']}-{pkg['version']}"
esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="{pkg['name']}" Version="{pkg['version']}" Publisher="{pkg['publisher']}"/>
    <DisplayName>{esc(pkg['displayName'])}</DisplayName>
    <Description xml:space="preserve">{esc(pkg['description'])}</Description>
    <Categories>Other</Categories>
  </Metadata>
  <Installation><InstallationTarget Id="Microsoft.VisualStudio.Code"/></Installation>
  <Dependencies/>
  <Assets><Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/></Assets>
</PackageManifest>
'''
ctypes = '''<?xml version="1.0" encoding="utf-8"?>
<Types><Default Extension=".json" ContentType="application/json"/><Default Extension=".js" ContentType="application/javascript"/>
<Default Extension=".svg" ContentType="image/svg+xml"/><Default Extension=".vsixmanifest" ContentType="text/xml"/></Types>
'''
OUT.mkdir(exist_ok=True)
vsix = OUT / f"{vid}.vsix"
with zipfile.ZipFile(vsix, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", ctypes)
    z.writestr("extension.vsixmanifest", manifest)
    for f in SRC.rglob("*"):
        if f.is_file():
            z.write(f, "extension/" + f.relative_to(SRC).as_posix())
print("đã tạo", vsix)
if "--install" in sys.argv:
    code = shutil.which("code") or shutil.which("code.cmd")
    if not code:
        sys.exit("không thấy lệnh `code`")
    p = subprocess.run([code, "--install-extension", str(vsix), "--force"], capture_output=True, text=True, encoding="utf-8")
    print((p.stdout + p.stderr).strip())
