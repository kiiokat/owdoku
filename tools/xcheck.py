import json,re,collections
s=open('/home/claude/owdoku.html').read()
b=s[s.find('const PLAYERS = ['):];b=b[:b.find('];')]
P=[json.loads(l.strip().rstrip(',')) for l in b.split('\n')[1:] if l.strip().startswith('{')]
m=json.load(open('/home/claude/lpdata/match.json'));lp={r['pagename']:r for r in json.load(open('/home/claude/lpdata/players.json'))}
sq=json.load(open('/home/claude/lpdata/squadplayers.json'))
TEAMN=dict(re.findall(r'(\w+):\{n:"([^"]+)",c:"#[0-9a-fA-F]+"\}',s[s.find('const TEAMS'):s.find('};',s.find('const TEAMS'))]))
owl={v.replace(' ','_'):k for k,v in TEAMN.items()}
owl.update({'Los_Angeles_Gladiators':'GLA','Los_Angeles_Valiant':'VAL','New_York_Excelsior':'NYXL','Seoul_Infernal':'INF','Vegas_Eternal':'VEG'})
ROLE={'dps':'DPS','tank':'Tank','support':'Support'}
roster=collections.defaultdict(set); yrs=collections.defaultdict(set)
for r in sq:
  k=owl.get(r['pagename'])
  if not k or r['type']!='player' or r['role'] in ('Coach','Head Coach','Assistant Coach','Manager','Analyst'): continue
  j=r['joindate'] or '0000'; l=r['leavedate'] or '9999'
  if l<'2017-12-01' or j>'2023-10-31': continue   # OWL era only
  # Liquipedia moved Philadelphia Fusion and Paris Eternal history onto their 2023 pages
  if r['pagename'] in ('Seoul_Infernal','Vegas_Eternal'):
    old={'Seoul_Infernal':'PHI','Vegas_Eternal':'PAR'}[r['pagename']]
    if j<'2022-12-01': roster[r['link'].replace(' ','_')].add(old)
    if l>='2022-12-01': roster[r['link'].replace(' ','_')].add(k)
    continue
  roster[r['link'].replace(' ','_')].add(k)
owlP=[p for p in P if p['n'] in m and p.get('y')]
rolediff=[];addt=[];extra=[]
for p in owlP:
  r=lp[m[p['n']]['page']]; ex=r['extradata'] if isinstance(r['extradata'],dict) else {}
  lr=next((ROLE[x] for x in [ex.get('role'),ex.get('role2')]+list((ex.get('roles') or {}).values()) if x in ROLE),None)
  if lr and lr!=p['r'] and lr not in (p.get('rs') or []): rolediff.append((p['n'],p['r'],lr))
  owlt={t for t in p['t'] if t in TEAMN and t in set(owl.values())}
  R=roster.get(m[p['n']]['page'],set())
  for t in R-owlt: addt.append((p['n'],t))
  for t in owlt-R: extra.append((p['n'],t))
print('owl players',len(owlP)); print('role differs',len(rolediff),rolediff[:30]); print('LP roster team missing in game',len(addt),addt); print('game team not on LP roster',len(extra),extra)
json.dump({'role':rolediff,'add':addt,'extra':extra},open('/home/claude/lpdata/xcheck.json','w'))
