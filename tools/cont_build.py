# Adds Overwatch Contenders (2018-2023) teams and players from Liquipedia placements (CC BY-SA 3.0).
import json,re,base64,collections
H='/home/claude/owdoku.html'; s=open(H).read()
lp=json.load(open('/home/claude/lpdata/players.json')); sq=json.load(open('/home/claude/lpdata/squadplayers.json'))
pl=json.load(open('/home/claude/lpdata/contenders.json')); m=json.load(open('/home/claude/lpdata/match.json'))
ICONS=json.load(open('/home/claude/npmflags/node_modules/@iconify-json/fluent-emoji-flat/icons.json'))['icons']
bypage={r['pagename']:r for r in lp}; pg=lambda x:x.replace(' ','_')
NEW={ # code: ([placement names], display, emoji, emoji name, bg, ring)
 'TLN':(['Talon Esports'],'Talon Esports','feather','feather','#0D0D0D','#FF7A1A'),
 'EMY':(['Element Mystic'],'Element Mystic','crystal-ball','crystal ball','#2A1145','#CE93D8'),
 'EXO':(['Ex Oblivione'],'Ex Oblivione','ghost','ghost','#16161D','#8E7CFF'),
 'RVL':(['Revival'],'Revival','seedling','seedling','#10261A','#66BB6A'),
 'UPA':(['Uprising Academy'],'Uprising Academy','raised-fist','raised fist','#111111','#EFDF00'),
 'SMC':(["Shu's Money Crew EU"],"Shu's Money Crew",'money-bag','money bag','#13261A','#4CAF50'),
 'WGS':(['World Game Star Phoenix'],'WGS Phoenix','comet','comet','#2B0B0B','#FF7043'),
 'DMN':(['DarkMode NA'],'DarkMode','new-moon','new moon','#0A0A0A','#9E9E9E'),
 'GEN':(['Gen.G Esports'],'Gen.G','tiger','tiger','#111111','#C9A227'),
 'YNB':(['Young and Beautiful'],'Young and Beautiful','cherry-blossom','cherry blossom','#2A1020','#F48FB1'),
 'FUU':(['Fusion University'],'Fusion University','atom-symbol','atom','#FF9E1B','#111111'),
 'BRH':(['British Hurricane'],'British Hurricane','tornado','tornado','#0B1F3A','#E53935'),
 'SKF':(['Skyfoxes'],'Skyfoxes','kite','kite','#0E2A47','#FF8A65'),
 'WSP':(['WISP'],'WISP','wind-face','wind face','#1B2735','#B3E5FC'),
 'RRC':(['Raspberry Racers'],'Raspberry Racers','racing-car','racing car','#3A0A22','#E91E63'),
 'ODY':(['Odyssey'],'Odyssey','sailboat','sailboat','#0D2B45','#4FC3F7'),
 'SWD':(['Second Wind'],'Second Wind','dashing-away','dash','#1A1A1A','#80DEEA'),
 'XL2':(['XL2 Academy'],'XL2 Academy','statue-of-liberty','Statue of Liberty','#CE0037','#171C38'),
 'NOB':(['Noble'],'Noble','crown','crown','#2E1A47','#E1BEE7'),
 'SOL':(['Solaris'],'Solaris','sun','sun','#2A1A00','#FFB300'),
 'NRGE':(['NRG Esports'],'NRG Esports','electric-plug','plug','#111111','#FF5722'),
 'MTR':(['Montreal Rebellion'],'Montreal Rebellion','fleur-de-lis','fleur-de-lis','#0B2545','#C8102E'),
 'BLG':(['Bilibili Gaming'],'Bilibili Gaming','television','television','#0B2A3A','#00A1D6'),
 'AMT':(['American Tornado'],'American Tornado','bison','bison','#0A1F44','#B22234'),
 'UPAC':(['UP Academy'],'UP Academy','up-arrow','up arrow','#1A1A1A','#FFC107'),
 'TDM':(['Team Diamond'],'Team Diamond','gem-stone','gem stone','#0B1B2B','#81D4FA'),
 'SNT':(['Saints'],'Saints','baby-angel','angel','#1B1B2F','#FFE082'),
 'MBL':(['Meta Bellum'],'Meta Bellum','military-helmet','helmet','#26324F','#90A4AE'),
 'LGD':(['LGD Gaming'],'LGD Gaming','dragon-face','dragon','#5C0A0A','#FFD700'),
 'LFZ':(['Lucky Future Zenith'],'Lucky Future Zenith','four-leaf-clover','clover','#10261A','#A5D6A7'),
 'FLG':(['Flag Gaming'],'Flag Gaming','triangular-flag','flag','#1A1A1A','#F44336'),
 'ATLA':(['ATL Academy'],'ATL Academy','crown','crown','#2B2B2B','#C4232F'),
 'GLL':(['Gladiators Legion'],'Gladiators Legion','lion','lion','#111111','#9575CD'),
 'MAC':(['Mayhem Academy'],'Mayhem Academy','flamingo','flamingo','#CF4691','#1A1A1A'),
 'TCH':(['Team Chaser'],'Team Chaser','motorcycle','motorcycle','#1A1A1A','#4DD0E1'),
 'RBD':(['Redbird Esports'],'Redbird Esports','parrot','parrot','#3A0A0A','#EF5350'),
 'AGT':(['Angry Titans'],'Angry Titans','ogre','ogre','#1A1A1A','#FF7043'),
 'LGEH':(['LGE.Huya'],'LGE.Huya','film-projector','projector','#2A1A00','#FFA726'),
 'OBA':(['Obey Alliance'],'Obey Alliance','handshake','handshake','#1A1A1A','#7986CB'),
 'TOW':(['The One Winner'],'The One Winner','1st-place-medal','medal','#1A1A1A','#FFD54F'),
 'GZG':(['Ground Zero Gaming'],'Ground Zero','collision','collision','#1A1A1A','#FF8A65'),
 'X6':(['X6-Gaming'],'X6-Gaming','game-die','die','#101820','#7CFC9A'),
}
MERGE={'O2 Blast':'O2B','RunAway':'RNA','Team CC':'TCC','Team KongDoo Panthera':'KDP','PANTHERA':'KDP','Team Envy':'ENV',
       'Team Peps':'PEP','T1':'T1','Twisted Minds':'TM','VARREL':'VAR'}
for v in NEW.values(): assert v[2] in ICONS, v[2]
name2code={**MERGE,**{n:k for k,v in NEW.items() for n in v[0]}}
members=collections.defaultdict(set); prole={}
for r in pl:
  if r['series']!='Overwatch Contenders' or r['opponenttype']!='team' or 'Trials' in r['tournament']: continue
  k=name2code.get(r['opponentname'])
  if not k: continue
  op=r['opponentplayers'] or {}
  for key,v in op.items():
    if re.fullmatch(r'p\d+',key) and v:
      members[k].add(pg(v)); rr=op.get(key+'role1')
      if rr in ('dps','tank','support'): prole.setdefault(pg(v),rr)
positions=collections.defaultdict(list)
for r in sq:
  if r['position'] in ('DPS','Tank','Support'): positions[pg(r['link'])].append(r['position'])
bs=s.find('const PLAYERS = ['); be=s.find('];',bs)
P=[json.loads(l.strip().rstrip(',')) for l in s[bs:be].split('\n')[1:] if l.strip().startswith('{')]
idx=collections.defaultdict(list)
for r in lp: idx[r['id'].lower()].append(r['pagename'])
page_of={}
for p in P:
  if p['n'] in m: page_of[p['n']]=m[p['n']]['page']
  else:
    c=idx.get(re.sub(r' \([A-Z?]+\)$','',p['n']).lower(),[])
    if len(c)==1: page_of[p['n']]=c[0]
by_page={v:k for k,v in page_of.items()}; names={p['n'].lower() for p in P}; byn={p['n']:p for p in P}
ISO=json.loads(re.search(r'ISO=(\{.*?\})\n',open('/home/claude/lppatch.py').read()).group(1).replace("'",'"'))
ROLE={'dps':'DPS','tank':'Tank','support':'Support'}
newp={}; skipped=[]; hits=0
for k,ps in members.items():
  for page in ps:
    if page in by_page:
      p=byn[by_page[page]]
      if k not in p['t']: p['t'].append(k); hits+=1
      continue
    if page in newp:
      if k not in newp[page]['t']: newp[page]['t'].append(k)
      continue
    r=bypage.get(page); ex=(r['extradata'] if r and isinstance(r['extradata'],dict) else {})
    role=next((ROLE[x] for x in [ex.get('role'),ex.get('role2')]+list((ex.get('roles') or {}).values()) if x in ROLE),None)
    if not role and positions.get(page): role=collections.Counter(positions[page]).most_common(1)[0][0]
    if not role and page in prole: role=ROLE[prole[page]]
    if not role: skipped.append((k,page)); continue
    n=(r['id'] if r else '') or page.replace('_',' ')
    nat=r['nationality'] if r else ''
    if n.lower() in names: n=f"{n} ({ISO.get(nat,'?')})"
    names.add(n.lower()); q={'n':n,'t':[k],'r':role,'hr':0,'y':[]}
    if ex.get('signatureHero1'): q['h']=ex['signatureHero1']
    if ISO.get(nat): q['c']=ISO[nat]
    newp[page]=q
print({k:len(v) for k,v in members.items()}); print('existing gaining team',hits,'new',len(newp),'skipped',len(skipped),skipped[:10])
allP=sorted(P+list(newp.values()),key=lambda p:p['n'].lower())
s=s[:bs]+'const PLAYERS = [\n'+'\n'.join('  '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+',' for p in allP)+'\n'+s[be:]
add=',\n'.join(f'  {k}:{{n:"{v[1]}",c:"{v[5]}",lg:"Contenders"}}' for k,v in NEW.items())
i=s.find('const TEAMS = {'); j=s.find('\n};',i); s=s[:j]+',\n'+add+s[j:]
# teams that now span two leagues
for code,lg2 in [('O2B','Contenders'),('RNA','Contenders'),('KDP','Contenders'),('ENV','Contenders'),('TCC','Contenders'),('PEP','Contenders'),('T1','Contenders'),('TM','Contenders'),('VAR','Contenders')]:
  s=re.sub(r'(\n  '+code+r':\{n:"[^"]+",c:"#[0-9A-Fa-f]+",lg:"[A-Z]+")\}',r'\1,lg2:"'+lg2+'"}',s,count=1)
badd=',\n'.join(f'  {k}:{{bg:"{v[4]}",ring:"{v[5]}"}}' for k,v in NEW.items())
i=s.find('const TEAM_BADGE = {'); j=s.find('\n};',i); s=s[:j]+',\n'+badd+s[j:]
i=s.find('const TEAM_ICON_NAMES = {'); j=s.find('}',i); s=s[:j]+',\n  '+','.join(f'{k}:"{v[3]}"' for k,v in NEW.items())+s[j:]
line=[x for x in s.splitlines() if x.startswith('const TEAM_ICONS')][0]
ti=json.loads(line[len('const TEAM_ICONS = '):].rstrip(';'))
for k,v in NEW.items():
  ti[k]='data:image/svg+xml;base64,'+base64.b64encode(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{ICONS[v[2]]["body"]}</svg>'.encode()).decode()
s=s.replace(line,'const TEAM_ICONS = '+json.dumps(ti)+';',1)
codes={p.get('c') for p in allP}-{None}
fl=json.loads(re.search(r'^const FLAG_SVG = (\{.*\});$',s,re.M).group(1))
for cc in codes-set(fl):
  svg=re.sub(r'>\s+<','><',open(f'/tmp/fi/node_modules/flag-icons/flags/1x1/{cc.lower()}.svg').read()).strip()
  fl[cc]='data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()
s=re.sub(r'^const FLAG_SVG = \{.*\};$',lambda _:'const FLAG_SVG = '+json.dumps(fl)+';',s,count=1,flags=re.M)
open(H,'w').write(s); print('players',len(allP))
