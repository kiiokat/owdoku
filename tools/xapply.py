# Cross-check OWL data (Stats Lab) against Liquipedia rosters/roles; Liquipedia wins where they disagree.
import json,re,collections,datetime as dt
H='/home/claude/owdoku.html'; s=open(H).read()
m=json.load(open('/home/claude/lpdata/match.json')); lp={r['pagename']:r for r in json.load(open('/home/claude/lpdata/players.json'))}
sq=json.load(open('/home/claude/lpdata/squadplayers.json'))
bs=s.find('const PLAYERS = ['); be=s.find('];',bs)
P=[json.loads(l.strip().rstrip(',')) for l in s[bs:be].split('\n')[1:] if l.strip().startswith('{')]
byn={p['n']:p for p in P}
# 1. blase and blasé are one player (Jeffrey Tsang); Stats Lab split him by spelling
a,b=byn.pop('blase'),byn['blasé']
b['t']=sorted(set(b['t'])|set(a['t']),key=(b['t']+a['t']).index); b['y']=sorted(set(a['y'])|set(b['y'])); b['hr']=round(a['hr']+b['hr'],1)
b['rs']=['DPS','Support']; b['hb']={'DPS':a['h'],'Support':b['h']}; b['r']='DPS'; b['h']=a['h']
P=[p for p in P if p['n']!='blase']
TEAMN=dict(re.findall(r'(\w+):\{n:"([^"]+)",c:"#[0-9a-fA-F]+"\}',s[s.find('const TEAMS'):s.find('};',s.find('const TEAMS'))]))
owl={v.replace(' ','_'):k for k,v in TEAMN.items()}
owl.update({'Los_Angeles_Gladiators':'GLA','Los_Angeles_Valiant':'VAL','New_York_Excelsior':'NYXL','Seoul_Infernal':'INF','Vegas_Eternal':'VEG'})
SEASONS={2018:('2018-01-10','2018-07-28'),2019:('2019-02-14','2019-09-29'),2020:('2020-02-08','2020-10-10'),2021:('2021-04-16','2021-09-25'),2022:('2022-05-05','2022-11-04'),2023:('2023-04-27','2023-09-30')}
D=lambda x:dt.date.fromisoformat(x)
team_add=collections.defaultdict(set); yr_add=collections.defaultdict(set)
for r in sq:
  k=owl.get(r['pagename'])
  if not k or r['type']!='player' or r['role'] in ('Coach','Head Coach','Assistant Coach','Manager','Analyst'): continue
  j=r['joindate'] or '2016-01-01'; l=r['leavedate'] or '2099-01-01'
  if j<'2000': j='2016-01-01'
  if l<'2000': l='2099-01-01'
  j=j.replace('-00','-01'); l=l.replace('-00','-28')
  page=r['link'].replace(' ','_'); spans=[]
  if r['pagename'] in ('Seoul_Infernal','Vegas_Eternal'):   # these pages also hold the Philadelphia Fusion / Paris Eternal years
    old={'Seoul_Infernal':'PHI','Vegas_Eternal':'PAR'}[r['pagename']]
    if j<'2022-11-15': spans.append((old,j,min(l,'2022-11-15')))
    if l>='2023-03-01': spans.append((k,max(j,'2023-03-01'),l))
  else: spans.append((k,j,l))
  for team,a1,b1 in spans:
    hit=False
    for y,(ss,se) in SEASONS.items():
      ov=(min(D(b1),D(se))-max(D(a1),D(ss))).days
      if ov>=45: hit=True; yr_add[page].add(y)      # on the roster for 45+ days of that season
    if hit: team_add[page].add(team)
ROLE={'dps':'DPS','tank':'Tank','support':'Support'}
stats=collections.Counter(); log=[]
for p in P:
  if p['n'] not in m: continue
  pgn=m[p['n']]['page']
  if not p.get('y') and not any(t in TEAMN and t in owl.values() for t in p['t']): continue
  for t in sorted(team_add.get(pgn,())):
    if t not in p['t']: p['t'].append(t); stats['team']+=1; log.append(f"{p['n']}: +{t}")
  if p.get('y') or team_add.get(pgn):
    for y in sorted(yr_add.get(pgn,())):
      if y not in p['y']: p['y'].append(y); stats['year']+=1; log.append(f"{p['n']}: +{y}")
    p['y'].sort()
  ex=lp[pgn]['extradata'] if isinstance(lp[pgn]['extradata'],dict) else {}
  lr=next((ROLE[x] for x in [ex.get('role'),ex.get('role2')]+list((ex.get('roles') or {}).values()) if x in ROLE),None)
  if lr and lr!=p['r'] and lr not in (p.get('rs') or []):
    old=p['r']; p['rs']=[lr,old]; p['hb']=p.get('hb') or {old:p.get('h')}
    if ex.get('signatureHero1') and lr not in p['hb']: p['hb'][lr]=ex['signatureHero1']
    p['r']=lr; stats['role']+=1; log.append(f"{p['n']}: role {old} -> {lr} (still counts as {old})")
P.sort(key=lambda p:p['n'].lower())
s=s[:bs]+'const PLAYERS = [\n'+'\n'.join('  '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+',' for p in P)+'\n'+s[be:]
s=s.replace('"blase":','"blasé_old":',0)
open(H,'w').write(s); print(dict(stats)); open('/home/claude/lpdata/xapply_log.txt','w').write('\n'.join(log)); print('\n'.join(log[:80]))
