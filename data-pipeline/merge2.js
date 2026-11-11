const fs=require('fs');
const path=require('path');
const P=require(path.join(__dirname,'players_full.json'));
// Reads hand-checked names, roles and countries from the current game's script
const HTML=path.join(__dirname,'..','index.html');
const src=fs.readFileSync(HTML,'utf8').match(/<script>([\s\S]*)<\/script>/)[1];
const g=new Function('module',src.replace('if (typeof document!=="undefined") boot();','')+';return module.exports;')({exports:{}});
const hand=Object.fromEntries(g.PLAYERS.map(p=>[p.n.toLowerCase(),p]));
const lines=P.map(p=>{
  const h=hand[p.n.toLowerCase()];
  const name=h?h.n:p.n, r=h?h.r:p.r, hero=(p.hb&&p.hb[r])||p.h;
  const rs=[...new Set([r,...p.rs])].sort();
  const o={n:name,t:p.t,r,h:hero,hr:p.hr,y:p.y};
  if(rs.length>1){ o.rs=rs; o.hb=Object.fromEntries(rs.filter(x=>p.hb&&p.hb[x]).map(x=>[x,p.hb[x]])); }
  if(p.ch.length) o.ch=p.ch;
  if(h&&h.c) o.c=h.c;
  return '  '+JSON.stringify(o)+',';
});
let s=fs.readFileSync(HTML,'utf8');
const before=s;
s=s.replace(/\/\/ Built from OWL Stats Lab[^\n]*\n\/\/ hr=[^\n]*\nconst PLAYERS = \[[\s\S]*?\n\];/,
 '// Built from OWL Stats Lab match data (2018–2022, 2023 through June). n=name t=teams r=role h=most-played hero in role\n// hr=recorded hours y=seasons ch=championship seasons c=country (hand-entered, partial) rs=all roles with 25%+ of playtime\nconst PLAYERS = [\n'+lines.join('\n')+'\n];');
if(!/\/\/ Built from OWL Stats Lab[^\n]*\n\/\/ hr=[^\n]*\nconst PLAYERS = \[/.test(before)) throw new Error('PLAYERS block not found - nothing written');
if(s===before) console.log('No changes: game data already up to date.');
fs.writeFileSync(HTML,s);
console.log(lines.length,'players written; with country:',P.filter(p=>hand[p.n.toLowerCase()]?.c).length);
