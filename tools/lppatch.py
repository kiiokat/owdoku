import json,re,base64,collections
H='/home/claude/owdoku.html'; s=open(H).read()
m=json.load(open('/home/claude/lpdata/match.json'))
ISO={'South Korea':'KR','United States':'US','China':'CN','Canada':'CA','Finland':'FI','Sweden':'SE','France':'FR','United Kingdom':'GB','Denmark':'DK','Australia':'AU','Spain':'ES','Germany':'DE','Russia':'RU','Taiwan':'TW','Netherlands':'NL','Saudi Arabia':'SA','Belgium':'BE','Thailand':'TH','Estonia':'EE','Brazil':'BR','New Zealand':'NZ','Poland':'PL','Israel':'IL','Iceland':'IS','Portugal':'PT','Puerto Rico':'PR','Turkey':'TR','Vietnam':'VN','Mexico':'MX','Norway':'NO','Austria':'AT','Latvia':'LV','Romania':'RO','Japan':'JP','Ethiopia':'ET','Philippines':'PH','Hong Kong':'HK','Ireland':'IE','Italy':'IT','Switzerland':'CH','Ukraine':'UA','Singapore':'SG','Argentina':'AR'}
def norm(x): return re.sub(r'[^a-z0-9]','',x.lower())
# players: set "c" from Liquipedia
blk_start=s.find('const PLAYERS = ['); blk_end=s.find('];',blk_start)
lines=s[blk_start:blk_end].split('\n'); out=[lines[0]]; aliases={}; codes=collections.Counter(); unk=set()
for l in lines[1:]:
  if not l.strip().startswith('{'): out.append(l); continue
  p=json.loads(l.strip().rstrip(','))
  info=m[p['n']]; cc=ISO.get(info['nat'])
  if not cc: unk.add(info['nat'])
  p.pop('c',None)
  if cc: p['c']=cc; codes[cc]+=1
  al=[a.strip() for a in info['alt'].split(',') if a.strip()]+[info['id']]
  al=[a for i,a in enumerate(al) if norm(a)!=norm(p['n']) and norm(a) not in map(norm,al[:i]) and len(norm(a))>=2]
  if al: aliases[p['n']]=al
  out.append('  '+json.dumps(p,ensure_ascii=False,separators=(',',':'))+',')
assert not unk, unk
s=s[:blk_start]+'\n'.join(out)+s[blk_end:]
# aliases
s=s.replace('const ALIASES = {};','const ALIASES = '+json.dumps(aliases,ensure_ascii=False,separators=(',',':'))+';',1)
# flags: rebuild FLAG_SVG with every code used
fl={}
for cc in sorted(codes):
  svg=open(f'/tmp/fi/node_modules/flag-icons/flags/1x1/{cc.lower()}.svg').read()
  svg=re.sub(r'>\s+<','><',svg).strip()
  fl[cc]='data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()
s=re.sub(r'^const FLAG_SVG = \{.*\};?$', lambda _:'const FLAG_SVG = '+json.dumps(fl)+';', s, count=1, flags=re.M)
# country categories
NAMES={'KR':'South Korea','US':'USA','CN':'China','CA':'Canada','FI':'Finland','SE':'Sweden','FR':'France','GB':'UK'}
nat=[cc for cc,n in codes.most_common() if n>=10]
s=s.replace('  // nationality categories return once every player has a country (Liquipedia)\n',
 '  // countries with 10+ OWL players (nationality from Liquipedia)\n  for (const cc of '+json.dumps(nat)+') cats.push({id:"c:"+cc, kind:"nat", cc, label:"From "+COUNTRY[cc], test:p=>p.c===cc});\n',1)
s=s.replace('const NA = ["US","CA"], EU = ["FR","FI","SE","DK"];','const COUNTRY = '+json.dumps({k:NAMES[k] for k in nat})+';',1)
s=s.replace('''  if(c.kind==="hero")   return {cls:"hero",''','''  if(c.kind==="nat")    return {cls:"nat", ico:flag(c.cc), kick:"From", name:COUNTRY[c.cc], tip:"Nationality: "+COUNTRY[c.cc]};
  if(c.kind==="hero")   return {cls:"hero",''',1)
open(H,'w').write(s)
print(codes.most_common(),'nat cats',nat,'aliases',len(aliases))
