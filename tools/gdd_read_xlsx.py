"""In mọi ô có chữ của một file xlsx (mọi sheet) ra stdout, không cần openpyxl.
GDD trên Google Sheets: tải bằng .../export?format=xlsx rồi
    .venv/Scripts/python.exe -I tools/gdd_read_xlsx.py GDD.xlsx > gdd_cells.txt
Ảnh nhúng trong ô: tools/gdd_xlsx_images.py."""
import sys, zipfile, re, xml.etree.ElementTree as ET
sys.stdout.reconfigure(encoding="utf-8")
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
z = zipfile.ZipFile(sys.argv[1])
names = z.namelist()
ss = []
if "xl/sharedStrings.xml" in names:
    for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
        ss.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
wb = ET.fromstring(z.read("xl/workbook.xml"))
rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
rmap = {r.get("Id"): r.get("Target") for r in rels}
media = [n for n in names if n.startswith("xl/media/")]
print("MEDIA:", len(media))
for sh in wb.find("m:sheets", NS):
    rid = sh.get("{%s}id" % NS["r"])
    path = "xl/" + rmap[rid].lstrip("/").replace("xl/", "")
    root = ET.fromstring(z.read(path))
    print("=== SHEET:", sh.get("name"), path)
    for row in root.iter("{%s}row" % NS["m"]):
        out = []
        for c in row.findall("m:c", NS):
            t = c.get("t"); v = c.find("m:v", NS); txt = None
            if t == "s" and v is not None: txt = ss[int(v.text)]
            elif t == "inlineStr":
                txt = "".join(x.text or "" for x in c.iter("{%s}t" % NS["m"]))
            elif v is not None: txt = v.text
            if txt not in (None, ""):
                out.append("%s: %s" % (c.get("r"), txt.replace("\n", " / ")))
        if out: print(" | ".join(out))
