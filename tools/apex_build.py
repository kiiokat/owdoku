# Adds OGN Overwatch APEX teams (2016-2018) and every player on their APEX-era rosters (Liquipedia, CC BY-SA 3.0).
import json,re,base64,collections
H='/home/claude/owdoku.html'; s=open(H).read()
lp=json.load(open('/home/claude/lpdata/players.json')); sq=json.load(open('/home/claude/lpdata/squadplayers.json'))
m=json.load(open('/home/claude/lpdata/match.json'))
ICONS=json.load(open('/home/claude/npmflags/node_modules/@iconify-json/fluent-emoji-flat/icons.json'))['icons']
bypage={r['pagename']:r for r in lp}; pg=lambda x:x.replace(' ','_')
APEX={ # code: (pages, name, emoji, emoji name, bg, ring)
 'LH':(['Lunatic-Hai'],'Lunatic-Hai','full-moon','full moon','#0F2340','#F4C542'),
 'ENV':(['Team_Envy'],'EnVyUs','dagger','dagger','#111111','#1E6BFF'),
 'RGE':(['Rogue'],'Rogue','ninja','ninja','#111111','#3EC4FF'),
 'AFB':(['AF.Blue'],'AF Blue','water-wave','water wave','#0B2A5B','#3D8BFF'),
 'AFR':(['AF.Red'],'AF Red','volcano','volcano','#5A0F14','#FF4747'),
 'KDP':(['Team_KongDoo_Panthera'],'KongDoo Panthera','leopard','leopard','#111111','#F2A900'),
 'KDU':(['Team_KongDoo_Uncia'],'KongDoo Uncia','paw-prints','paw prints','#1C2A3A','#BFD7EA'),
 'LWB':(['LW_Blue'],'LW Blue','dolphin','dolphin','#0A2342','#4FC3F7'),
 'LWR':(['LW_Red'],'LW Red','rose','rose','#3A0A10','#FF5252'),
 'MVP':(['Team_MVP'],'MVP Space','ringed-planet','ringed planet','#14123A','#B388FF'),
 'BKS':(['BK_Stars'],'BK Stars','glowing-star','glowing star','#1A1A1A','#FFD54F'),
 'CBX':(['CONBOX'],'CONBOX','package','package','#2B1E12','#FFB74D'),
 'FLX':(['Flash_Lux'],'Flash Lux','flashlight','flashlight','#1E1E1E','#FFF176'),
 'MTA':(['Meta_Athena'],'Meta Athena','owl','owl','#26324F','#B0BEC5'),
 'RNA':(['RunAway'],'RunAway','person-running','runner','#C2185B','#FFFFFF'),
 'GCB':(['GC_Busan'],'GC Busan','anchor','anchor','#0D3B66','#F4D35E'),
 'C9K':(['Cloud9_KongDoo'],'Cloud9 KongDoo','cloud','cloud','#0E2B47','#00AEEF'),
 'NCF':(['Foxes'],'NC Foxes','fox','fox','#1A1A1A','#E0582E'),
 'O2B':(['O2_Blast'],'O2 Blast','bubbles','bubbles','#0B3954','#4DD0E1'),
}
for k,v in APEX.items(): assert v[2] in ICONS, v[2]
START,END='2016-09-01','2018-04-30'   # APEX Seasons 1-4
members=collections.defaultdict(set); positions=collections.defaultdict(list)
page2code={p:k for k,v in APEX.items() for p in v[0]}
for r in sq:
  if r['position'] in ('DPS','Tank','Support'): positions[pg(r['link'])].append(r['position'])
  k=page2code.get(r['pagename'])
  if not k or r['type']!='player' or r['role'] in ('Coach','Head Coach','Assistant Coach','Manager','Analyst'): continue
  if (r['joindate'] or '0000')<=END and (r['leavedate'] or '9999')>=START: members[k].add(pg(r['link']))
blk_start=s.find('const PLAYERS = ['); blk_end=s.find('];',blk_start)
P=[json.loads(l.strip().rstrip(',')) for l in s[blk_start:blk_end].split('\n')[1:] if l.strip().startswith('{')]
# map game players to Liquipedia pages (OWL via match.json, OWCS/new via id)
idx=collections.defaultdict(list)
for r in lp: idx[r['id'].lower()].append(r['pagename'])
page_of={}
for p in P:
  if p['n'] in m: page_of[p['n']]=m[p['n']]['page']
  else:
    base=re.sub(r' \([A-Z?]+\)$','',p['n']).lower(); c=idx.get(base,[])
    if len(c)==1: page_of[p['n']]=c[0]
by_page={v:k for k,v in page_of.items()}; names={p['n'].lower() for p in P}; byn={p['n']:p for p in P}
ISO=json.loads(re.search(r'ISO=(\{.*?\})\n',open('/home/claude/lppatch.py').read()).group(1).replace("'",'"'))
ROLE={'dps':'DPS','tank':'Tank','support':'Support'}
newp={}; skipped=[]; existing_hits=0
for k,ps in members.items():
  for page in ps:
    if page in by_page:
      p=byn[by_page[page]]
      if k not in p['t']: p['t'].append(k); existing_hits+=1
      continue
    if page in newp: newp[page]['t'].append(k); continue
    r=bypage.get(page)
    if not r:   # no player page on Liquipedia: use the roster entry itself
      row=next((x for x in sq if pg(x['link'])==page and x['type']=='player'),None)
      pos=collections.Counter(positions.get(page,[])).most_common(1)
      if not row or not pos: skipped.append((k,page)); continue
      n=row['id'] or page.replace('_',' ')
      if n.lower() in names: n=f"{n} ({ISO.get(row['nationality'],'?')})"
      names.add(n.lower()); q={'n':n,'t':[k],'r':pos[0][0],'hr':0,'y':[]}
      if ISO.get(row['nationality']): q['c']=ISO[row['nationality']]
      newp[page]=q; continue
    ex=r['extradata'] if isinstance(r['extradata'],dict) else {}
    role=next((ROLE[x] for x in [ex.get('role'),ex.get('role2')]+list((ex.get('roles') or {}).values()) if x in ROLE),None)
    if not role and positions.get(page): role=collections.Counter(positions[page]).most_common(1)[0][0]
    if not role: skipped.append((k,page,'norole')); continue
    n=r['id'] or page.replace('_',' ')
    if n.lower() in names: n=f"{n} ({ISO.get(r['nationality'],'?')})"
    names.add(n.lower())
    q={'n':n,'t':[k],'r':role,'hr':0,'y':[]}
    if ex.get('signatureHero1'): q['h']=ex['signatureHero1']
    cc=ISO.get(r['nationality'])
    if cc: q['c']=cc
    newp[page]=q
print('members',{k:len(v) for k,v in members.items()}); print('existing players gaining a team',existing_hits,'new',len(newp),'skipped',skipped)
allP=sorted(P+list(newp.values()),key=lambda p:p['n'].lower())
s=s[:blk_start]+'const PLAYERS = [\n'+'\n'.join('  '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+',' for p in allP)+'\n'+s[blk_end:]
add=''.join(f'  {k}:{{n:"{v[1]}",c:"{v[5]}",lg:"APEX"}},\n' for k,v in APEX.items())
i=s.find('const TEAMS = {'); j=s.find('\n};',i); s=s[:j]+'\n'+add.rstrip('\n').rstrip(',')+s[j:] if s[j-1]==',' else s[:j]+',\n'+add.rstrip('\n').rstrip(',')+s[j:]
badd=''.join(f'  {k}:{{bg:"{v[4]}",ring:"{v[5]}"}},\n' for k,v in APEX.items()).rstrip('\n').rstrip(',')
i=s.find('const TEAM_BADGE = {'); j=s.find('\n};',i); s=s[:j]+',\n'+badd+s[j:]
i=s.find('const TEAM_ICON_NAMES = {'); j=s.find('}',i); s=s[:j]+',\n  '+','.join(f'{k}:"{v[3]}"' for k,v in APEX.items())+s[j:]
line=[x for x in s.splitlines() if x.startswith('const TEAM_ICONS')][0]
ti=json.loads(line[len('const TEAM_ICONS = '):].rstrip(';'))
for k,v in APEX.items():
  ti[k]='data:image/svg+xml;base64,'+base64.b64encode(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{ICONS[v[2]]["body"]}</svg>'.encode()).decode()
s=s.replace(line,'const TEAM_ICONS = '+json.dumps(ti)+';',1)
codes={p.get('c') for p in allP}-{None}
fl=json.loads(re.search(r'^const FLAG_SVG = (\{.*\});$',s,re.M).group(1))
for cc in codes-set(fl):
  svg=re.sub(r'>\s+<','><',open(f'/tmp/fi/node_modules/flag-icons/flags/1x1/{cc.lower()}.svg').read()).strip()
  fl[cc]='data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()
s=re.sub(r'^const FLAG_SVG = \{.*\};$',lambda _:'const FLAG_SVG = '+json.dumps(fl)+';',s,count=1,flags=re.M)
open(H,'w').write(s); print('players',len(allP))
