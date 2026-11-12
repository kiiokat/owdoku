# Flags team badges whose emoji blends into its background colour (needs Playwright).
# Usage: python3 check-badges.py  (serves the game from ../ and prints badges where >12% of the emoji is close to the background)
import asyncio, http.server, threading, functools, json
srv=http.server.ThreadingHTTPServer(('127.0.0.1',9133),functools.partial(http.server.SimpleHTTPRequestHandler,directory=__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'..')))
threading.Thread(target=srv.serve_forever,daemon=True).start()
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page()
    await pg.goto('http://127.0.0.1:9133/index.html'); await pg.wait_for_selector('#loader',state='detached')
    r=await pg.evaluate('''async()=>{
      const hex=h=>{h=h.replace("#","");return [0,2,4].map(i=>parseInt(h.substr(i,2),16))};
      const lin=c=>{c/=255;return c<=.04045?c/12.92:Math.pow((c+.055)/1.055,2.4)};
      const L=([r,g,b])=>.2126*lin(r)+.7152*lin(g)+.0722*lin(b);
      const cr=(a,b)=>{const x=L(a),y=L(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
      const dist=(a,b)=>Math.hypot(a[0]-b[0],(a[1]-b[1])*1.2,a[2]-b[2]);
      const out=[];
      for(const k in TEAM_ICONS){ const B=TEAM_BADGE[k]; if(!B) continue;
        const img=new Image(); img.src=TEAM_ICONS[k]; await img.decode();
        const cv=document.createElement("canvas"); cv.width=cv.height=64; const x=cv.getContext("2d"); x.drawImage(img,0,0,64,64);
        const d=x.getImageData(0,0,64,64).data, bg=hex(B.bg); let n=0,blend=0,dim=0,sum=[0,0,0];
        for(let i=0;i<d.length;i+=4){ if(d[i+3]<128) continue; n++; const c=[d[i],d[i+1],d[i+2]]; sum=sum.map((v,j)=>v+c[j]); if(dist(c,bg)<90) blend++; if(cr(c,bg)<1.4) dim++; }
        const avg=sum.map(v=>v/n);
        out.push({k,name:TEAMS[k].n,bg:B.bg,ring:B.ring,blend:+(blend/n).toFixed(2),dim:+(dim/n).toFixed(2),avgCR:+cr(avg,bg).toFixed(2),ringPage:+cr(hex(B.ring),[11,13,18]).toFixed(2),ringBg:+cr(hex(B.ring),bg).toFixed(2)});
      }
      return out}''')
        # flag: emoji colours close to the background, or most of the emoji about as bright as it
    bad=[x for x in r if x['blend']>0.12 or x['dim']>0.6]
    for x in sorted(bad,key=lambda x:-x['blend']): print(x)
    print(len(r),'checked',len(bad),'flagged')
    await b.close()
asyncio.run(main())
