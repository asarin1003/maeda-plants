#!/usr/bin/env python3
import json, math, re, urllib.parse, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"posts.json"
UA="Mozilla/5.0"
KEYWORDS=("花","お花","バラ","薔薇","梅","桜","さくら","植物","草","木","葉","実","蕾","つぼみ","紫陽花","あじさい","菊","百合","ユリ","椿","チューリップ","蘭","ラン","朝顔","ひまわり","向日葵","藤","牡丹","菜の花","紅葉")

def token(tid):
    n=int(tid)
    return ("".join(chr(int(x)) for x in str((n/1e15)*math.pi).replace(".","")))[::-1][:5]

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=25) as r:
        return json.load(r)

def tweet(tid):
    q=urllib.parse.urlencode({"id":tid,"lang":"ja","token":token(tid)})
    return get_json("https://cdn.syndication.twimg.com/tweet-result?"+q)

def normalize(tid,d,seed=False):
    photos=[]
    for m in d.get("mediaDetails") or []:
        if m.get("type")=="photo" and m.get("media_url_https"):
            photos.append(m["media_url_https"]+"?name=large")
    text=d.get("text") or ""
    return {"id":tid,"url":f"https://x.com/yukio_maeda/status/{tid}","text":text,
            "created_at":d.get("created_at") or "","photos":photos,"seed":seed}

def is_plant(p):
    return bool(p["photos"]) and any(k in (p["text"] or "") for k in KEYWORDS)

def main():
    old=json.loads(DATA.read_text(encoding="utf-8"))
    out=[]
    for p in old:
        try:
            n=normalize(p["id"],tweet(p["id"]),p.get("seed",False))
            if p.get("seed") or is_plant(n): out.append(n)
        except Exception as e:
            print("fetch failed",p["id"],e)
            out.append(p)
    # New-post discovery is intentionally separate: seed posts always work even if timeline syndication changes.
    out.sort(key=lambda p:int(p["id"]),reverse=True)
    DATA.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("posts",len(out),"photos",sum(len(p.get("photos",[])) for p in out))

if __name__=="__main__": main()
