# Một lần: nội dung trang chiếm hết chiều cao cửa sổ (viewport và panel kéo dài tới đáy)
p = "template.html"
s = open(p, encoding="utf8").read()
def rep(a, b):
    global s
    assert a in s, a[:70]
    s = s.replace(a, b, 1)
rep("*{box-sizing:border-box}", "*{box-sizing:border-box}\nhtml,body{height:100%}\nbody{display:flex;flex-direction:column}")
rep("main{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:12px;align-items:start}", "main{flex:1;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 360px;grid-template-rows:minmax(0,1fr);gap:12px}")
rep("#vp{position:relative;height:min(78vh,720px);min-height:360px;", "#vp{position:relative;min-height:320px;")
rep("padding:0;min-width:0;height:min(78vh,720px);display:flex;", "padding:0;min-width:0;min-height:0;display:flex;")
rep("header{display:flex;", "header{flex:none;display:flex;")
rep("@media (max-width:900px){main{grid-template-columns:minmax(0,1fr)} aside{height:auto;overflow:visible} aside .pbody{overflow:visible} #vp{height:56vh}}",
    "@media (max-width:900px){html,body{height:auto} main{display:block} aside{height:auto;overflow:visible;margin-top:12px} aside .pbody{overflow:visible} #vp{height:60vh}}")
open(p, "w", encoding="utf8").write(s)
