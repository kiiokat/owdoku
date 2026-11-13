# Per-player OWCS facts for the OWCS-day categories:
#  oy = years (2024-2026) spent on an OWCS team or played at an OWCS event
#  ww = won an OWCS international (Major, EWC 2024, Champions Clash, Midseason Championship, World Finals)
#  wf = played at an OWCS World Finals
import json,re,collections,sys
H=sys.argv[1]; s=open(H).read()
D='/home/claude/lpdata/'
lp=json.load(open(D+'players.json')); sq=json.load(open(D+'squadplayers.json')); pl=json.load(open(D+'placements.json'))
pl=pl.get('result',pl) if isinstance(pl,dict) else pl
m=json.load(open(D+'match.json'))
pg=lambda x:x.replace(' ','_')
src=open('/home/claude/owdoku/tools/owcs_build.py').read()
OWCS=eval(src[src.index('OWCS={')+5:src.index('\n}\n',src.index('OWCS={'))+2])
page2code={p:k for k,v in OWCS.items() for p in v[1]}
oy=collections.defaultdict(set); ww=set(); wf=set()
INTL=re.compile(r'(Major|Esports World Cup 2024|Champions Clash|Midseason Championship$|World Finals$)')
for r in pl:
  t=r['tournament']
  if not (t.startswith('Overwatch Champions Series') or t=='Esports World Cup 2024') or r['opponenttype']!='team': continue
  ps={pg(v) for k,v in (r['opponentplayers'] or {}).items() if re.fullmatch(r'p\d+',k) and v}
  y=int(r['date'][:4])
  for p in ps:
    if 2024<=y<=2026: oy[p].add(y)
    if 'World Finals' in t and 'Road to' not in t: wf.add(p)
    if r['placement']=='1' and INTL.search(t) and 'LCQ' not in t: ww.add(p)
for r in sq:
  if page2code.get(r['pagename']) is None or r['type']!='player': continue
  if r['role'] in ('Coach','Head Coach','Assistant Coach','Manager','Analyst'): continue
  j=(r['joindate'] or '2000-01-01')[:10]; l=(r['leavedate'] or '9999-12-31')[:10]
  if l.startswith('0000') or l=='': l='9999-12-31'
  for y in (2024,2025,2026):
    a=max(f'{y}-01-01','2024-03-01'); b=f'{y}-12-31'
    if j<=b and l>=a: oy[pg(r['link'])].add(y)
# game players -> Liquipedia page
blk=s.index('const PLAYERS = ['); end=s.index('];',blk)
P=[json.loads(l.strip().rstrip(',')) for l in s[blk:end].split('\n')[1:] if l.strip().startswith('{')]
byid=collections.defaultdict(list)
for r in lp: byid[(r['id'] or '').lower()].append(r['pagename'])
pages=set(r['pagename'] for r in lp)
def page_of(n):
  if n in m: return m[n]['page']
  base=re.sub(r' \([A-Z]{2}\)$','',n)
  if pg(base) in pages: return pg(base)
  c=byid.get(base.lower(),[])
  return c[0] if len(c)==1 else None
miss=0; stat=collections.Counter()
for p in P:
  for k in ('oy','ww','wf'): p.pop(k,None)
  pgn=page_of(p['n'])
  if not pgn: 
    if any(t in OWCS for t in p['t']): miss+=1
    continue
  if oy.get(pgn): p['oy']=sorted(oy[pgn]); [stat.update([y]) for y in p['oy']]
  if pgn in ww: p['ww']=1; stat['ww']+=1
  if pgn in wf: p['wf']=1; stat['wf']+=1
print('owcs players without page:',miss, dict(stat))
s=s[:blk]+'const PLAYERS = [\n'+'\n'.join('  '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+',' for p in P)+'\n'+s[end:]
open(H,'w').write(s)

# ---- OWCS regions: which regional stages (main events only) each player played in ----
s=open(H).read()
rg_rows=json.load(open(D+'regional.json')); rg_rows=rg_rows.get('result',rg_rows) if isinstance(rg_rows,dict) else rg_rows
REG=re.compile(r'Overwatch Champions Series 20\d\d - (Korea|NA|EMEA|China|Japan|Pacific) Stage \d$')
reg=collections.defaultdict(set)
for r in rg_rows:
  mm=REG.match(r['tournament'])
  if not mm or r['opponenttype']!='team': continue
  for k,v in (r['opponentplayers'] or {}).items():
    if re.fullmatch(r'p\d+',k) and v: reg[pg(v)].add(mm.group(1))
blk=s.index('const PLAYERS = ['); end=s.index('];',blk)
P=[json.loads(l.strip().rstrip(',')) for l in s[blk:end].split('\n')[1:] if l.strip().startswith('{')]
cnt=collections.Counter()
for p in P:
  p.pop('rg',None); pgn=page_of(p['n'])
  if pgn and reg.get(pgn): p['rg']=sorted(reg[pgn]); cnt.update(p['rg'])
print('regions:',dict(cnt))
s=s[:blk]+'const PLAYERS = [\n'+'\n'.join('  '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+',' for p in P)+'\n'+s[end:]
open(H,'w').write(s)

# ---- Overwatch World Cup: main events only (no qualifiers, conference cups or open trials) ----
s=open(H).read()
wc_rows=json.load(open(D+'worldcup.json')); wc_rows=wc_rows.get('result',wc_rows) if isinstance(wc_rows,dict) else wc_rows
WCM=re.compile(r'Overwatch World Cup (\d{4})$')
wcy=collections.defaultdict(set); wcw=set()
for r in wc_rows:
  mm=WCM.match(r['tournament'])
  if not mm or r['opponenttype']!='team': continue
  for k,v in (r['opponentplayers'] or {}).items():
    if re.fullmatch(r'p\d+',k) and v:
      wcy[pg(v)].add(int(mm.group(1)))
      if r['placement']=='1': wcw.add(pg(v))
blk=s.index('const PLAYERS = ['); end=s.index('];',blk)
P=[json.loads(l.strip().rstrip(',')) for l in s[blk:end].split('\n')[1:] if l.strip().startswith('{')]
n=w=0
for p in P:
  p.pop('wc',None); p.pop('wcw',None); pgn=page_of(p['n'])
  if pgn and wcy.get(pgn): p['wc']=sorted(wcy[pgn]); n+=1
  if pgn and pgn in wcw: p['wcw']=1; w+=1
print('world cup players:',n,'champions:',w)
s=s[:blk]+'const PLAYERS = [\n'+'\n'.join('  '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+',' for p in P)+'\n'+s[end:]
open(H,'w').write(s)
