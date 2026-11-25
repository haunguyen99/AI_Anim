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
def std(kick,title,blocks,figs,dark=False,fw=1.35,mh=None,row=False):
    n=len(figs); mh=mh or (600 if n==1 else 270)
    figs_html=''.join(fig(*f[:3],mh) if len(f)==3 else fig(*f,'real',mh) for f in figs)
    cls='dark' if dark else ''
    S.append(f'<section class="{cls}"><p class="kick">{kick}</p><h2>{title}</h2><div class="split"><div class="col">{"".join(blocks)}</div><div class="col{" row2" if row else ""}" style="flex:{fw}">{figs_html}</div></div></section>')
def raw(html,dark=False): S.append(f'<section class="{"dark" if dark else ""}">{html}</section>')
def terms(kick,title,items,dark=False):
    cards=''.join(f'<div class="tc"><img src="{i}" style="{st}"><div class="tt"><b>{t}</b><span>{d}</span><small>{s}</small></div></div>' for t,d,i,s,st in items)
    S.append(f'<section class="{"dark" if dark else ""}"><p class="kick">{kick}</p><h2>{title}</h2><div class="tgrid">{cards}</div></section>')
def build(path):
    open(path,'w').write(HEAD+'\n'.join(S)+TAIL)
