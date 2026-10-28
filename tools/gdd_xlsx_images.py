"""Tách ảnh nhúng trong xlsx, tên file ghi sheet + ô neo: s3_C1_image27.png = sheet 3, ô C1.
    .venv/Scripts/python.exe -I tools/gdd_xlsx_images.py GDD.xlsx <thư mục ra>"""
import sys, zipfile, os, re, posixpath, xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8")
z = zipfile.ZipFile(sys.argv[1]); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
names = set(z.namelist())
X = "{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
def rels(p):
    rp = posixpath.join(posixpath.dirname(p), "_rels", posixpath.basename(p) + ".rels")
    if rp not in names: return {}
    return {r.get("Id"): posixpath.normpath(posixpath.join(posixpath.dirname(p), r.get("Target")))
            for r in ET.fromstring(z.read(rp))}
for i in range(1, 13):
    sp = "xl/worksheets/sheet%d.xml" % i
    for rid, dp in rels(sp).items():
        if "drawing" not in dp or dp not in names: continue
        dr = rels(dp); root = ET.fromstring(z.read(dp))
        for anc in root:
            fr = anc.find(X + "from")
            if fr is None: continue
            col = int(fr.find(X + "col").text); row = int(fr.find(X + "row").text)
            for b in anc.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
                media = dr.get(b.get(R + "embed"))
                if media:
                    name = "s%d_%s%d_%s" % (i, chr(65 + col), row + 1, posixpath.basename(media))
                    open(os.path.join(out, name), "wb").write(z.read(media))
                    print(name, len(z.read(media)))
