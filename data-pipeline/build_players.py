import csv, glob, json, collections, re, sys
import os
HERE=os.path.dirname(os.path.abspath(__file__))
root=os.path.join(HERE,'raw_data')   # put the Stats Lab CSVs here: raw_data/phs_2018/*.csv ... phs_2023/*.csv
CODE={'Atlanta Reign':'ATL','Boston Uprising':'BOS','Chengdu Hunters':'CDH','Dallas Fuel':'DAL','Florida Mayhem':'FLA',
 'Guangzhou Charge':'GZC','Hangzhou Spark':'HZS','Houston Outlaws':'HOU','London Spitfire':'LDN','Los Angeles Gladiators':'GLA',
 'Los Angeles Valiant':'VAL','New York Excelsior':'NYXL','Paris Eternal':'PAR','Philadelphia Fusion':'PHI','San Francisco Shock':'SFS',
 'Seoul Dynasty':'SEO','Shanghai Dragons':'SHD','Toronto Defiant':'TOR','Vancouver Titans':'VAN','Washington Justice':'WAS'}
def team_code(name, year):
    if name=='Seoul Infernal': return 'PHI' if year<2023 else 'INF'
    if name=='Vegas Eternal':  return 'PAR' if year<2023 else 'VEG'
    return CODE.get(name)
CHAMP={2018:'LDN',2019:'SFS',2020:'SFS',2021:'SHD',2022:'DAL',2023:'FLA'}
RENAME={'McCree':'Cassidy','Lucio':'Lúcio','Torbjorn':'Torbjörn'}
TANK=set('D.Va Orisa Reinhardt Roadhog Winston Zarya Sigma Ramattra Mauga Hazard'.split())|{'Wrecking Ball','Junker Queen'}
SUP=set('Ana Baptiste Brigitte Lúcio Mercy Moira Zenyatta Kiriko Lifeweaver Illari Juno'.split())
def role(h): return 'Tank' if h in TANK else 'Support' if h in SUP else 'DPS'
def year_of(ts):
    m=re.search(r'(20\d\d)',ts); return int(m.group(1))
P=collections.defaultdict(lambda:{'names':collections.Counter(),'teams':set(),'heroes':collections.Counter(),'heroesNo19':collections.Counter(),'years':set(),'champ':set(),'last':0})
for f in sorted(glob.glob(root+'/phs_*/*.csv')):
    with open(f,encoding='utf-8-sig') as fh:
        for r in csv.DictReader(fh):
            if r['stat_name']!='Time Played': continue
            name=(r.get('player') or r.get('player_name') or '').strip()
            y=year_of(r.get('start_time') or r.get('pelstart_time') or '')
            t=team_code(r.get('team') or r.get('team_name'), y)
            if not name or not t: continue          # skips Contenders / Pro-Am teams
            p=P[name.lower()]; p['names'][name]+=1; p['teams'].add(t); p['years'].add(y)
            p['last']=max(p['last'],y)
            if CHAMP.get(y)==t: p['champ'].add(y)
            h=r.get('hero') or r.get('hero_name')
            if h!='All Heroes':
                h=RENAME.get(h,h); v=float(r.get('stat_amount') or r.get('amount') or 0); p['heroes'][h]+=v
                if y!=2019: p['heroesNo19'][h]+=v
out=[]
for k,p in P.items():
    tot=sum(p['heroes'].values())
    if tot<300: continue   # under 5 minutes of recorded play
    src=p['heroesNo19'] if sum(p['heroesNo19'].values())>=3*3600 else p['heroes']   # GOATS-era 2019 skews roles
    byrole=collections.Counter()
    for h,v in src.items(): byrole[role(h)]+=v
    r=byrole.most_common(1)[0][0]
    h=max((h for h in p['heroes'] if role(h)==r), key=lambda h:p['heroes'][h], default=None)
    names=p['names']; mixed=[n for n,_ in names.most_common() if not n.isupper() and not n.islower()]
    # every role with at least 25% of playtime (non-2019 time when there's an hour of it, to dodge GOATS)
    rsrc=p['heroesNo19'] if sum(p['heroesNo19'].values())>=3600 else p['heroes']
    rb=collections.Counter()
    for hh,v in rsrc.items(): rb[role(hh)]+=v
    rt=sum(rb.values()) or 1
    rs=sorted({r}|{k for k,v in rb.items() if v/rt>=0.25})
    out.append({'rs':rs,'n':(mixed[0] if mixed else names.most_common(1)[0][0]),'t':sorted(p['teams']),'r':r,'h':h,
                'hr':round(tot/3600,1),'hb':{rr:max((x for x in p['heroes'] if role(x)==rr), key=lambda x:p['heroes'][x], default=None) for rr in ['Tank','DPS','Support']},'y':sorted(p['years']),'ch':sorted(p['champ'])})
out.sort(key=lambda x:x['n'].lower())
json.dump(out,open(os.path.join(HERE,'players_full.json'),'w'),ensure_ascii=False)
print(len(out),'players;',sum(1 for x in out if x['ch']),'champions;',sum(1 for x in out if x['hr']>=15),'with 15h+')
