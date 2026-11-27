import re
HEAD=open('/tmp/rigparts/a_head.html').read().replace('<title>Quy trình Rigging 3D với AI</title>','<title>Rigging 3D bằng AI trong Frolvy: hướng dẫn cho người mới</title>')
EXTRA='''
.blk{background:var(--card);border-radius:14px;padding:14px 22px}
.dark .blk{background:#1D3554}
.bl{font-size:19px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--goldtxt);margin-bottom:4px}
.dark .bl{color:var(--gold)}
.bt{font-size:25px;line-height:1.35}
.bt ul{padding-left:24px;display:flex;flex-direction:column;gap:3px}
.bt li{font-size:25px}
.fig.wd figcaption::before{content:"WINDY · VẼ TỪ FILE JOINT THẬT · ";font-weight:700;color:var(--goldtxt)}
.fig.nr figcaption::before{content:"";}
.row2{flex-direction:row!important;gap:16px!important}.row2 .fig{flex:1;min-width:0}
.tgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;flex:1}
.tc{background:var(--card);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}
.tc img{width:100%;height:185px;object-fit:cover;background:#fff;display:block}
.tc .tt{padding:10px 16px;display:flex;flex-direction:column;gap:4px}
.tc b{font-size:28px}.tc span{font-size:21px;line-height:1.3}
.tc small{font-size:18px;color:var(--mute)}
.prog{position:absolute;right:128px;top:38px;display:flex;flex-direction:column;align-items:flex-end;gap:4px;font-size:19px;color:var(--mute)}
.dark .prog{color:#9db0cc}
.prog .pl{font-size:16px;color:var(--goldtxt);font-weight:600}
.prog i{width:30px;height:30px;border-radius:50%;border:2px solid #B9B1A0;display:flex;align-items:center;justify-content:center;font-style:normal;font-size:16px;font-weight:700}
.prog i.g{border-color:var(--gold)}
.prog i.d{background:#8793A8;border-color:#8793A8;color:#fff}
.prog i.n{background:var(--gold);border-color:var(--gold);color:#13203A;width:40px;height:40px;font-size:21px}
.prog b{margin-right:8px;font-size:20px;color:var(--ink)}.dark .prog b{color:#fff}
.cmd{background:#fff;border-left:10px solid var(--gold);border-radius:12px;padding:12px 20px}
.dark .cmd{background:#1D3554}
.cmd .cl{font-size:18px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--goldtxt)}
.dark .cmd .cl{color:var(--gold)}
.cmd .ct{font-size:25px;line-height:1.35;font-weight:600;margin:2px 0 8px}
.cmd .cr{font-size:22px;line-height:1.3;color:var(--mute)}
.dark .cmd .cr{color:#c9d6ea}
.qgrid{display:grid;grid-template-columns:1fr 1fr;gap:20px;flex:1}
.qc{background:var(--card);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}
.solo .card{flex:none}.solo .card p{font-size:30px;line-height:1.4}.solo .card .lab{font-size:22px}
.bigl li{font-size:32px!important;line-height:1.5}
.qc img{width:100%;height:225px;object-fit:contain;background:#fff;display:block}
.qt{padding:10px 20px;display:flex;flex-direction:column;gap:4px}.qt b{font-size:30px}.qt span{font-size:23px;line-height:1.3}
.fig.bad figcaption::before{content:"CHƯA ĐẠT · ";font-weight:800;color:var(--bad)}
.fig.good figcaption::before{content:"ĐẠT · ";font-weight:800;color:var(--good)}
.fig.bad{border-color:var(--bad)}.fig.good{border-color:var(--good)}
.say{background:#fff;border-left:10px solid var(--gold);border-radius:10px;padding:16px 22px;font-size:25px;line-height:1.35}
.dark .say{background:#1D3554;color:#fff}
.say b{color:var(--goldtxt)}.dark .say b{color:var(--gold)}
'''
HEAD=HEAD.replace('</style>',EXTRA+'</style>')
TAIL=open('/tmp/rigparts/z_tail.html').read()
S=[]
def esc(x): return x
def fig(src,cap,kind='real',mh=None):
    st=f' style="max-height:{mh}px"' if mh else ''
    return f'<figure class="fig {kind}"><img src="{src}"{st}><figcaption>{cap}</figcaption></figure>'
def blk(label,html): return f'<div class="blk"><div class="bl">{label}</div><div class="bt">{html}</div></div>'
def ul(*items): return '<ul>'+''.join(f'<li>{i}</li>' for i in items)+'</ul>'
def err(label,html): return f'<div class="card err"><span class="lab">{label}</span><p>{html}</p></div>'
def fix(label,html): return f'<div class="card fix"><span class="lab">{label}</span><p>{html}</p></div>'
GATES={2,3,7,9}
CMDS={}
def prog(n):
    items=''.join(f'<i class="{"n" if k==n else ("d" if k<n else "")}{" g" if (k in GATES and k!=n) else ""}">{k}</i>' for k in range(1,11))
    return f'<div class="prog"><div style="display:flex;align-items:center;gap:7px"><b>Bước {n}/10</b>{items}</div><div class="pl">viền vàng = review gate</div></div>'
def cmdblk(t,r): return f'<div class="cmd"><div class="cl">Câu lệnh mẫu</div><div class="ct">{t}</div><div class="cr"><b>Bạn sẽ nhận được:</b> {r}</div></div>'
def std(kick,title,blocks,figs,dark=False,fw=1.35,mh=None,row=False):
    import re as _re
    _m=_re.search(r'Bước (\d+)',kick); _p=prog(int(_m.group(1))) if _m else ''
    if title in CMDS: blocks=list(blocks)+[cmdblk(*CMDS[title])]
    n=len(figs); mh=mh or (600 if n==1 else 270)
    figs_html=''.join(fig(*f[:3],mh) if len(f)==3 else fig(*f,'real',mh) for f in figs)
    cls='dark' if dark else ''
    if not figs:
        S.append(f'<section class="{cls}">{_p}<p class="kick">{kick}</p><h2>{title}</h2><div class="col solo">{"".join(blocks)}</div></section>'); return
    S.append(f'<section class="{cls}">{_p}<p class="kick">{kick}</p><h2>{title}</h2><div class="split"><div class="col">{"".join(blocks)}</div><div class="col{" row2" if row else ""}" style="flex:{fw}">{figs_html}</div></div></section>')
def raw(html,dark=False): S.append(f'<section class="{"dark" if dark else ""}">{html}</section>')
def terms(kick,title,items,dark=False):
    cards=''.join(f'<div class="tc"><img src="{i}" style="{st}"><div class="tt"><b>{t}</b><span>{d}</span><small>{s}</small></div></div>' for t,d,i,s,st in items)
    S.append(f'<section class="{"dark" if dark else ""}"><p class="kick">{kick}</p><h2>{title}</h2><div class="tgrid">{cards}</div></section>')
def quad(kick,title,items,dark=False):
    cards=''.join(f'<div class="qc"><img src="{i}"><div class="qt"><b>{t}</b><span>{d}</span></div></div>' for t,d,i in items)
    S.append(f'<section class="{"dark" if dark else ""}"><p class="kick">{kick}</p><h2>{title}</h2><div class="qgrid">{cards}</div></section>')
def build(path):
    open(path,'w').write(HEAD+'\n'.join(S)+TAIL)
