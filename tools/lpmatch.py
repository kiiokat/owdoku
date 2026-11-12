import json,re,unicodedata,collections
html=open('/home/claude/owdoku.html').read()
blk=html[html.find('const PLAYERS = ['):]; blk=blk[:blk.find('];')]
P=[json.loads(l.strip().rstrip(',')) for l in blk.splitlines()[1:] if l.strip().startswith('{')]
lp=json.load(open('/home/claude/lpdata/players.json')); sq=json.load(open('/home/claude/lpdata/squadplayers.json'))
def norm(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
byid=collections.defaultdict(list)
for r in lp:
  for k in [r['id'],r['pagename'].replace('_',' ')]+[a for a in r['alternateid'].split(',') if a.strip()]:
    byid[norm(k)].append(r)
# OWL squad links: squadplayer rows on OWL team pages give id->link
owl_links=collections.Counter(); sqid=collections.defaultdict(set)
for r in sq: sqid[norm(r['id'])].add(r['link'])
bypage={r['pagename']:r for r in lp}
res={};miss=[];amb=[]
for p in P:
  k=norm(p['n']); c={id(r):r for r in byid.get(k,[])}
  c=list(c.values())
  if len(c)>1:
    # prefer one whose page appears in squad rows under that id, or exact id
    ex=[r for r in c if norm(r['id'])==k]
    if len(ex)==1: c=ex
    else:
      links={l.replace(' ','_') for l in sqid.get(k,())}
      ex=[r for r in c if r['pagename'] in links]
      if len(ex)==1: c=ex
  if len(c)==1: res[p['n']]=c[0]
  elif not c: miss.append(p['n'])
  else: amb.append((p['n'],[(r['pagename'],r['nationality'],r['teampagename']) for r in c]))
print(len(P),'matched',len(res),'miss',len(miss),'amb',len(amb))
print('MISS',miss); 
for a in amb: print('AMB',a)
json.dump({k:{'page':v['pagename'],'nat':v['nationality'],'alt':v['alternateid'],'id':v['id']} for k,v in res.items()},open('/home/claude/lpdata/match.json','w'),ensure_ascii=False,indent=0)
print(collections.Counter(v['nationality'] for v in res.values()).most_common(40))

# --- second pass: use OWL team rosters to pick the right person
blk2=html[html.find('const TEAMS = {'):]; blk2=blk2[:blk2.find('};')]
TEAMN={k:v for k,v in re.findall(r'(\w+):\{n:"([^"]+)"',blk2)}
owl={TEAMN[k].replace(' ','_'):k for k in TEAMN}
owl.update({'Los_Angeles_Gladiators':'GLA','Los_Angeles_Valiant':'VAL','New_York_Excelsior':'YXL','Seoul_Infernal':'INF','Vegas_Eternal':'VEG'})
roster=collections.defaultdict(set)
for r in sq:
  if r['pagename'] in owl: roster[(norm(r['id']),owl[r['pagename']])].add(r['link'].replace(' ','_'))
fixed={};still=[]
for p in P:
  links=set()
  for t in p['t']: links|=roster.get((norm(p['n']),t),set())
  links={l for l in links if l in bypage}
  if len(links)==1:
    pg=links.pop(); 
    if p['n'] in res and res[p['n']]['pagename']!=pg: print('CHANGED',p['n'],res[p['n']]['pagename'],'->',pg)
    res[p['n']]=bypage[pg]
  elif p['n'] not in res: still.append((p['n'],p['t'],links))
res['Beast']=bypage['Beast_(Kwang-jin_Baek)'] if 'Beast_(Kwang-jin_Baek)' in bypage else res.get('Beast')
res['ZEST']=bypage['ZEST']
print('after roster pass matched',len(res)); print('STILL',still)
json.dump({k:{'page':v['pagename'],'nat':v['nationality'],'alt':v['alternateid'],'id':v['id']} for k,v in res.items()},open('/home/claude/lpdata/match.json','w'),ensure_ascii=False,indent=0)
