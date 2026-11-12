import json,re,base64,collections,unicodedata
H='/home/claude/owdoku.html'; s=open(H).read()
lp=json.load(open('/home/claude/lpdata/players.json')); sq=json.load(open('/home/claude/lpdata/squadplayers.json'))
pl=json.load(open('/home/claude/lpdata/placements.json')); m=json.load(open('/home/claude/lpdata/match.json'))
ICONS=json.load(open('/home/claude/npmflags/node_modules/@iconify-json/fluent-emoji-flat/icons.json'))['icons']
bypage={r['pagename']:r for r in lp}
pg=lambda x:x.replace(' ','_')
# code: (placement names, team pages, display name, emoji, emoji name, bg, ring)
OWCS={
 'TM':(['Twisted Minds'],['Twisted_Minds'],'Twisted Minds','cyclone','cyclone','#1A1030','#9B6BFF'),
 'SSG':(['Spacestation Gaming'],['Spacestation_Gaming'],'Spacestation Gaming','rocket','rocket','#0F1E3D','#F15A24'),
 'CR':(['Crazy Raccoon'],['Crazy_Raccoon'],'Crazy Raccoon','raccoon','raccoon','#1A1A1A','#E60012'),
 'FLC':(['Team Falcons'],['Team_Falcons'],'Team Falcons','eagle','eagle','#0B3D2E','#00A651'),
 'VP':(['Virtus.pro'],['Virtus.pro'],'Virtus.pro','bear','bear','#1A1A1A','#FF6A00'),
 'WBG':(['Weibo Gaming'],['Weibo_Gaming'],'Weibo Gaming','tiger-face','tiger','#9E0B1F','#FFFFFF'),
 'TL':(['Team Liquid'],['Team_Liquid'],'Team Liquid','horse-face','horse','#0A1E33','#4EA3DD'),
 'T1':(['T1'],['T1'],'T1','crossed-swords','crossed swords','#111111','#E2012D'),
 'ENC':(['ENCE'],['ENCE'],'ENCE','snowflake','snowflake','#14213D','#F5B700'),
 'NTM':(['NTMR'],['NTMR'],'NTMR','crescent-moon','crescent moon','#1E1036','#E6A2FF'),
 'ZETA':(['ZETA DIVISION'],['ZETA_DIVISION'],'ZETA DIVISION','fox','fox','#111111','#F2F2F2'),
 'ALQ':(['Al Qadsiah'],['Al_Qadsiah'],'Al Qadsiah','camel','camel','#E8B400','#111111'),
 'TCC':(['Team CC (Chinese orgless team)'],['Team_CC_(Chinese_orgless_team)'],'Team CC','puzzle-piece','puzzle piece','#2A2A2A','#9AA0A6'),
 'VAR':(['VARREL'],['VARREL'],'VARREL','wolf','wolf','#121212','#00D6BE'),
 'GK':(['Geekay Esports'],['Geekay_Esports'],'Geekay Esports','gem-stone','gem stone','#3B1A66','#FFB800'),
 'NRG':(['NRG Shock'],['NRG_Shock'],'NRG Shock','high-voltage','lightning','#111111','#FFFFFF'),
 'M80':(['M80'],['M80'],'M80','bomb','bomb','#1A1A1A','#FF3B3B'),
 'ROC':(['ROC Esports'],['ROC_Esports'],'ROC Esports','bird','bird','#0E2A47','#F4B400'),
 'AG':(['All Gamers','All Gamers Global'],['All_Gamers','All_Gamers_Global'],'All Gamers','video-game','video game','#B3122E','#FFD54F'),
 'PEP':(['Team Peps'],['Team_Peps'],'Team Peps','hot-pepper','hot pepper','#1F1F1F','#FF4D6D'),
}
OWL_CONT={'DAL':(['Dallas Fuel'],['Dallas_Fuel']),'TOR':(['Dallas Fuel'][:0]+['Toronto Defiant'],['Toronto_Defiant'])}
TOP=re.compile(r'(Major|Esports World Cup 2024|World Finals$|Champions Clash|Midseason Championship)')
def events_ok(t): return t.startswith('Overwatch Champions Series') or t=='Esports World Cup 2024'
# players per team, and top-event count per player page
members=collections.defaultdict(set); evcount=collections.Counter()
allteams={**{k:(v[0],v[1]) for k,v in OWCS.items()},**OWL_CONT}
name2code={n:k for k,v in allteams.items() for n in v[0]}
seen=set()
for r in pl:
  if r['opponenttype']!='team' or not events_ok(r['tournament']) or 'Road to' in r['tournament']: continue
  ps={pg(v) for k,v in (r['opponentplayers'] or {}).items() if re.fullmatch(r'p\d+',k) and v}
  for p in ps:
    if (p,r['tournament']) not in seen: seen.add((p,r['tournament'])); evcount[p]+=1
  k=name2code.get(r['opponentname'])
  if k and TOP.search(r['tournament']): members[k]|=ps
page2code={p:k for k,v in allteams.items() for p in v[1]}
for r in sq:
  k=page2code.get(r['pagename'])
  if not k or r['type']!='player' or r['role'] in ('Coach','Head Coach','Assistant Coach','Manager','Analyst'): continue
  if (r['leavedate'] or '9999')>='2024-03-01' and (r['joindate'] or '0')<='2026-12-31':
    members[k].add(pg(r['link']))
# existing game players by Liquipedia page
blk_start=s.find('const PLAYERS = ['); blk_end=s.find('];',blk_start)
lines=s[blk_start:blk_end].split('\n'); P=[]; 
for l in lines[1:]:
  if l.strip().startswith('{'): P.append(json.loads(l.strip().rstrip(',')))
page_of={p['n']:m[p['n']]['page'] for p in P}; by_page={v:k for k,v in page_of.items()}
names={p['n'].lower() for p in P}
ISO=json.loads(re.search(r'ISO=(\{.*?\})\n',open('/home/claude/lppatch.py').read()).group(1).replace("'",'"'))
ROLE={'dps':'DPS','tank':'Tank','support':'Support'}
newp={}; skipped=[]
for k,ps in members.items():
  for page in ps:
    if page in by_page:
      p=next(x for x in P if x['n']==by_page[page])
      if k not in p['t']: p['t'].append(k)
      continue
    if page in newp: newp[page]['t'].append(k); continue
    r=bypage.get(page)
    if not r: skipped.append((k,page,'nopage')); continue
    ex=r['extradata'] if isinstance(r['extradata'],dict) else {}
    roles=[ex.get('role'),ex.get('role2')]+list((ex.get('roles') or {}).values())
    role=next((ROLE[x] for x in roles if x in ROLE),None)
    if not role:
      pos=[x['position'] for x in sq if pg(x['link'])==page and x['position'] in ('DPS','Tank','Support')]
      role=collections.Counter(pos).most_common(1)[0][0] if pos else None
    hero=ex.get('signatureHero1')
    if not role or not hero: skipped.append((k,page,role,hero)); continue
    n=r['id'] or page.replace('_',' ')
    if n.lower() in names: n=f"{n} ({ISO.get(r['nationality'],'?')})"
    names.add(n.lower())
    q={'n':n,'t':[k],'r':role,'h':hero,'hr':0,'y':[]}
    cc=ISO.get(r['nationality']); 
    if cc: q['c']=cc
    q['_page']=page; newp[page]=q
for p in P: 
  e=evcount.get(page_of[p['n']],0)
  if e: p['ow']=e
for q in newp.values():
  e=evcount.get(q['_page'],0)
  if e: q['ow']=e
print('new players',len(newp),'skipped',len(skipped)); print(skipped[:15])
print({k:len(v) for k,v in members.items()})
allP=sorted(P+[{k:v for k,v in q.items() if k!='_page'} for q in newp.values()],key=lambda p:p['n'].lower())
s=s[:blk_start]+'const PLAYERS = [\n'+'\n'.join('  '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+',' for p in allP)+'\n'+s[blk_end:]
# flags for any new country codes
codes={p.get('c') for p in allP}-{None}
fl=json.loads(re.search(r'^const FLAG_SVG = (\{.*\});$',s,re.M).group(1))
for cc in codes-set(fl):
  svg=re.sub(r'>\s+<','><',open(f'/tmp/fi/node_modules/flag-icons/flags/1x1/{cc.lower()}.svg').read()).strip()
  fl[cc]='data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()
s=re.sub(r'^const FLAG_SVG = \{.*\};$',lambda _:'const FLAG_SVG = '+json.dumps(fl)+';',s,count=1,flags=re.M)
# TEAMS / badges / icons / names
add=''.join(f'  {k}:{{n:"{v[2]}",c:"{v[6]}",lg:"OWCS"}},\n' for k,v in OWCS.items())
s=s.replace('  INF:{n:"Seoul Infernal",c:"#c8102e"}, VEG:{n:"Vegas Eternal",c:"#303d56"}\n};','  INF:{n:"Seoul Infernal",c:"#c8102e"}, VEG:{n:"Vegas Eternal",c:"#303d56"},\n'+add+'};',1)
badd=''.join(f'  {k}:{{bg:"{v[5]}",ring:"{v[6]}"}},\n' for k,v in OWCS.items())
s=s.replace('  VEG:{bg:"#303D56",ring:"#EF3340"}\n};','  VEG:{bg:"#303D56",ring:"#EF3340"},\n'+badd+'};',1)
i=s.find('const TEAM_ICON_NAMES = {'); j=s.find('};',i)
s=s[:j]+','+','.join(f'{k}:"{v[4]}"' for k,v in OWCS.items())+s[j:]
line=[x for x in s.splitlines() if x.startswith('const TEAM_ICONS')][0]
ti=json.loads(line[len('const TEAM_ICONS = '):].rstrip(';'))
for k,v in OWCS.items():
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{ICONS[v[3]]["body"]}</svg>'
  ti[k]='data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()
s=s.replace(line,'const TEAM_ICONS = '+json.dumps(ti)+';',1)
open(H,'w').write(s)
json.dump(sorted(p['n'] for p in allP),open('/home/claude/lpdata/allnames.json','w'),ensure_ascii=False)
