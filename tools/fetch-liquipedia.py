#!/usr/bin/env python3
"""
Download Overwatch player and roster data from the LiquipediaDB API (v3)
for OWdoku's data pipeline.

Your API key is never stored in this file or sent anywhere except to Liquipedia.
Give it one of two ways:
  - set the environment variable LIQUIPEDIA_API_KEY, or
  - run the script and paste it when asked (it won't be shown on screen).

Usage:
  python3 fetch-liquipedia.py

Output (next to this script, in liquipedia_data/):
  players.json       every player page on the Overwatch wiki
  squadplayers.json  every team roster entry (who played for which team, and when)

Data from Liquipedia is licensed CC-BY-SA 3.0. Credit Liquipedia wherever it is shown.
Needs only Python 3 (no extra packages). Requests are spaced out to respect
Liquipedia's rate limits, so a full run takes a few minutes.
"""
import getpass, gzip, json, os, sys, time, urllib.error, urllib.parse, urllib.request

API = "https://api.liquipedia.net/api/v3"
WIKI = "overwatch"
UA = "OWdoku/1.0 (https://owdoku.pages.dev; https://github.com/kiiokat/owdoku)"
PAGE = 1000          # rows per request (API maximum)
PAUSE = 4.0          # seconds between requests
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "liquipedia_data")

DATASETS = {
    "players": ("player", "", "pagename ASC",
        "pagename,id,alternateid,name,romanizedname,nationality,nationality2,nationality3,status,type,team,extradata"),
    "squadplayers": ("squadplayer", "", "link ASC",
        "pagename,link,id,name,nationality,position,role,type,status,joindate,leavedate,inactivedate,extradata"),
}

def get(key, endpoint, conditions, order, fields, offset):
    params = {"wiki": WIKI, "order": order, "limit": PAGE, "offset": offset}   # no "query": get every column
    if conditions: params["conditions"] = conditions
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{API}/{endpoint}?{q}", headers={
        "Authorization": f"Apikey {key}", "User-Agent": UA, "Accept-Encoding": "gzip"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
                if r.headers.get("Content-Encoding") == "gzip": raw = gzip.decompress(raw)
                data = json.loads(raw)
                if data.get("error"): raise RuntimeError(data["error"])
                return data.get("result", [])
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):                      # too fast: back off and retry
                wait = 30 * (attempt + 1); print(f"  rate limited, waiting {wait}s..."); time.sleep(wait); continue
            if e.code in (401, 403): sys.exit("The API key was refused (401/403). Check the key and try again.")
            body = e.read()
            try: body = gzip.decompress(body)
            except Exception: pass
            body = body.decode("utf-8", "replace")[:500]
            if e.code == 404 and offset > 0: return []   # past the last page
            sys.exit(f"HTTP {e.code} from {endpoint} (offset {offset}). Server said:\n{body}")
    sys.exit("Gave up after repeated rate limits. Try again later.")

def main():
    key = os.environ.get("LIQUIPEDIA_API_KEY") or getpass.getpass("Liquipedia API key (hidden): ").strip()
    if not key: sys.exit("No API key given.")
    os.makedirs(OUT, exist_ok=True)
    for name, (endpoint, cond, order, fields) in DATASETS.items():
        rows, offset = [], 0
        print(f"Fetching {name}...")
        while True:
            batch = get(key, endpoint, cond, order, fields, offset)
            rows += batch; print(f"  {len(rows)} rows")
            if len(batch) < PAGE: break
            offset += PAGE; time.sleep(PAUSE)
        path = os.path.join(OUT, f"{name}.json")
        with open(path, "w", encoding="utf-8") as f: json.dump(rows, f, ensure_ascii=False)
        print(f"  saved {path}"); time.sleep(PAUSE)
    print("\nDone. Send the files in liquipedia_data/ to Claude (they contain no API key).")

if __name__ == "__main__":
    main()
