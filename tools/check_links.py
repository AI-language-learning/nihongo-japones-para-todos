import sys,os,re
from html.parser import HTMLParser
root=sys.argv[1]; bad=[]; n=0; ids={}
class P(HTMLParser):
    def __init__(s): super().__init__(); s.l=[]; s.ids=set()
    def handle_starttag(s,t,a):
        a=dict(a)
        if a.get('id'): s.ids.add(a['id'])
        for k in ('href','src'):
            if a.get(k): s.l.append(a[k])
pages={}
for r,d,f in os.walk(root):
    if '.git' in r: continue
    for x in f:
        if x.endswith('.html'):
            p=P(); p.feed(open(os.path.join(r,x),encoding='utf-8').read()); pages[os.path.join(r,x)]=p
for f,p in pages.items():
    for l in p.l:
        if l.startswith(('http','mailto','javascript','data:')): continue
        path,_,frag=l.partition('#'); n+=1
        t=f if path=='' else os.path.normpath(os.path.join(os.path.dirname(f),path))
        if os.path.isdir(t): t=os.path.join(t,'index.html')
        if not os.path.exists(t): bad.append((f,l,'no existe'))
        elif frag and t in pages and frag not in pages[t].ids: bad.append((f,l,'ancla'))
print('enlaces internos:',n,'rotos:',len(bad))
for b in bad[:30]: print(' ',b)
