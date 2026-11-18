import json,sys,datetime as dt
TZ=dt.timezone(dt.timedelta(hours=7))
def ts(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(TZ)
p,a,b=sys.argv[1],sys.argv[2],sys.argv[3]
A=dt.datetime.fromisoformat(a).replace(tzinfo=TZ);B=dt.datetime.fromisoformat(b).replace(tzinfo=TZ)
prev=None
for l in open(p,encoding='utf-8'):
    try:o=json.loads(l)
    except: continue
    if 'timestamp' not in o: continue
    t=ts(o['timestamp'])
    if t<A or t>B: continue
    if prev and (t-prev[0]).total_seconds()>240:
        print('GAP',prev[0].strftime('%m-%d %H:%M:%S'),'->',t.strftime('%m-%d %H:%M:%S'),round((t-prev[0]).total_seconds()/60,1),'min | before:',prev[1],'| after:',o.get('type'))
    c=o.get('message',{}).get('content') if isinstance(o.get('message'),dict) else None
    d=o.get('type')
    if isinstance(c,list):
        for x in c:
            if x.get('type')=='tool_use': d+=':'+x.get('name','')+' '+json.dumps(x.get('input'),ensure_ascii=False)[:100]
            elif x.get('type')=='text': d+=':text '+x['text'][:60].replace('\n',' ')
    prev=(t,d)
