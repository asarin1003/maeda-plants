#!/usr/bin/env python3
# Conservative free backfill. Uses X's public profile syndication only and
# persists every discovered ID so repeated runs never lose prior discoveries.
import json, re, urllib.request, urllib.parse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
POSTS=ROOT/"data"/"posts.json"
STATE=ROOT/"data"/"backfill-state.json"
UA="Mozilla/5.0"

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"text/html"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.read().decode("utf-8","replace")

def main():
    posts=json.loads(POSTS.read_text(encoding="utf-8"))
    known={p["id"] for p in posts}
    state=json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"seen_ids":[]}
    seen=set(state.get("seen_ids",[]))|known
    # Public web-search HTML is used only to discover candidate status IDs.
    # Every candidate is later re-fetched through X syndication and filtered.
    queries=[
      'site:x.com/yukio_maeda/status yukio_maeda 花',
      'site:x.com/yukio_maeda/status yukio_maeda お花',
      'site:x.com/yukio_maeda/status yukio_maeda バラ',
      'site:x.com/yukio_maeda/status yukio_maeda 梅',
      'site:x.com/yukio_maeda/status yukio_maeda 桜',
      'site:x.com/yukio_maeda/status yukio_maeda 植物'
    ]
    search_urls=[
      "https://www.google.com/search?"+urllib.parse.urlencode({"q":q,"num":"20"})
      for q in queries
    ]
    search_urls += [
      "https://www.bing.com/search?"+urllib.parse.urlencode({"q":q,"count":"20"})
      for q in queries
    ]
    urls=search_urls+[
      "https://syndication.twitter.com/srv/timeline-profile/screen-name/yukio_maeda",
      "https://x.com/yukio_maeda"
    ]
    found=set()
    for url in urls:
        try:
            html=fetch(url)
            found.update(re.findall(r'(?:status[\\/]|status%2F)(\\d{15,22})',html))
            found.update(re.findall(r'"id_str"\\s*:\\s*"(\\d{15,22})"',html))
            # Strictly accept only URLs belonging to the target account.
            pats=[
              r'https?://(?:www\\.)?x\\.com/yukio_maeda/status/(\\d{15,22})',
              r'https?%3A%2F%2F(?:www\\.)?x\\.com%2Fyukio_maeda%2Fstatus%2F(\\d{15,22})',
              r'x\\.com/yukio_maeda/status/(\\d{15,22})'
            ]
            for pat in pats:
                found.update(re.findall(pat,html,re.I))
        except Exception as e:
            print("source unavailable",url,e)
    new=sorted(found-seen,key=int,reverse=True)
    for tid in new:
        posts.append({"id":tid,"url":f"https://x.com/yukio_maeda/status/{tid}",
                      "text":"","created_at":"","photos":[],"seed":False})
    seen.update(found)
    POSTS.write_text(json.dumps(posts,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    STATE.write_text(json.dumps({"seen_ids":sorted(seen,key=int,reverse=True)},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("found",len(found),"new",len(new),"known total",len(seen))

if __name__=="__main__": main()
