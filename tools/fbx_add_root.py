"""Thêm nút 'root' (LimbNode, đứng yên: T 0, R 0, S 1) làm cha của nút DEF_Root_M trong FBX ASCII xuất từ Frolvy (anim-only), đúng khuôn file
Hero_Nova_Showcase.fbx / Hero_Nova_Game_Base.fbx của team (root -> {Root, DEF_Root_M}). Frolvy `export_scene` qua MCP không tự thêm 'root'; thiếu root thì
đường dẫn clip trong Unity (root/DEF_Root_M/...) không khớp Base. Đủ NodeAttribute + Model + 3 AnimationCurveNode + 9 AnimationCurve (bake đủ số key như các xương khác), cập nhật Definitions.
usage: python3 -I tools/fbx_add_root.py in.fbx out.fbx
"""
import re
import sys

ROOT_CHILD = "DEF_Root_M"   # chỉ cây xương DEF vào dưới 'root' (xương fit 'Root' của Frolvy giữ ở cấp scene, như file mẫu của team)


def main(src, dst):
    t = open(src, encoding="utf-8").read()
    ids = [int(x) for x in re.findall(r"^\t\w+: (\d+),", t, re.M)]
    nid = max(ids) + 1
    layer = re.search(r'\tAnimationLayer: (\d+),', t).group(1)
    m = re.search(r'\tAnimationCurve: \d+, "AnimCurve::", "" \{.*?KeyTime: \*(\d+) \{\n\t\t\ta: ([^\n]*)\n', t, re.S)
    n, times = int(m.group(1)), m.group(2)
    attr_id, model_id = nid, nid + 1
    cn_ids = [nid + 2, nid + 3, nid + 4]
    cv_ids = [[nid + 5 + 3 * i + j for j in range(3)] for i in range(3)]
    def curve(cid, val):
        v = ",".join(["%.6f" % val] * n)
        return ('\tAnimationCurve: %d, "AnimCurve::", "" {\n\t\tDefault: %.6f\n\t\tKeyVer: 4008\n\t\tKeyTime: *%d {\n\t\t\ta: %s\n\t\t}\n\t\tKeyValueFloat: *%d {\n\t\t\ta: %s\n\t\t}\n'
                '\t\tKeyAttrFlags: *1 {\n\t\t\ta: 24580\n\t\t}\n\t\tKeyAttrDataFloat: *4 {\n\t\t\ta: 0,0,0,0\n\t\t}\n\t\tKeyAttrRefCount: *1 {\n\t\t\ta: %d\n\t\t}\n\t}\n') % (cid, val, n, times, n, v, n)
    names = ("T", "R", "S")
    blocks = '\tNodeAttribute: %d, "NodeAttribute::", "LimbNode" {\n\t\tTypeFlags: "Skeleton"\n\t}\n' % attr_id
    blocks += ('\tModel: %d, "Model::root", "LimbNode" {\n\t\tVersion: 232\n\t\tProperties70:  {\n\t\t\tP: "Lcl Translation", "Lcl Translation", "", "A",0.000000,0.000000,0.000000\n'
               '\t\t\tP: "Lcl Rotation", "Lcl Rotation", "", "A",0.000000,-0.000000,0.000000\n\t\t\tP: "Lcl Scaling", "Lcl Scaling", "", "A",1.000000,1.000000,1.000000\n\t\t}\n\t\tShading: T\n\t\tCulling: "CullingOff"\n\t}\n') % model_id
    for i, nm in enumerate(names):
        d = 1.0 if nm == "S" else 0.0
        blocks += '\tAnimationCurveNode: %d, "AnimCurveNode::%s", "" {\n\t\tProperties70:  {\n' % (cn_ids[i], nm)
        for ax in "XYZ":
            blocks += '\t\t\tP: "d|%s", "Number", "", "A",%.6f\n' % (ax, d)
        blocks += "\t\t}\n\t}\n"
        for j in range(3):
            blocks += curve(cv_ids[i][j], d)
    # chèn trước khối Connections, sau hết Objects
    i_obj_end = t.index("\n}\nConnections:")
    t = t[:i_obj_end + 1] + blocks + t[i_obj_end + 1:]
    # cha mới của các nút gốc xương
    roots = [mid for mid, nm, typ in re.findall(r'\tModel: (\d+), "Model::([^"]*)", "(\w+)"', t) if typ == "LimbNode" and nm == ROOT_CHILD]
    top = [r for r in roots if ('\tC: "OO",%s,0\n' % r) in t]
    for r in top:
        t = t.replace('\tC: "OO",%s,0\n' % r, '\tC: "OO",%s,%d\n' % (r, model_id), 1)
    conn = '\tC: "OO",%d,0\n\tC: "OO",%d,%d\n' % (model_id, attr_id, model_id)
    for i, nm in enumerate(names):
        prop = {"T": "Lcl Translation", "R": "Lcl Rotation", "S": "Lcl Scaling"}[nm]
        conn += '\tC: "OO",%d,%s\n\tC: "OP",%d,%d, "%s"\n' % (cn_ids[i], layer, cn_ids[i], model_id, prop)
        for j, ax in enumerate("XYZ"):
            conn += '\tC: "OP",%d,%d, "d|%s"\n' % (cv_ids[i][j], cn_ids[i], ax)
    i_conn_end = t.index("\n}", t.index("Connections:"))
    t = t[:i_conn_end + 1] + conn + t[i_conn_end + 1:]
    # Definitions
    def bump(t, kind, add):
        return re.sub(r'(ObjectType: "%s" \{\n\t\tCount: )(\d+)' % kind, lambda mm: mm.group(1) + str(int(mm.group(2)) + add), t, count=1)
    for kind, add in (("NodeAttribute", 1), ("Model", 1), ("AnimationCurveNode", 3), ("AnimationCurve", 9)):
        t = bump(t, kind, add)
    t = re.sub(r'(Definitions:  \{\n\tVersion: 100\n\tCount: )(\d+)', lambda mm: mm.group(1) + str(int(mm.group(2)) + 14), t, count=1)
    open(dst, "w", encoding="utf-8", newline="\n").write(t)
    print("root them vao:", model_id, "| nut goc xuong dat lai cha:", len(top), "| so key:", n)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
