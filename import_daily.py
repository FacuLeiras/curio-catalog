"""Publish a bounded selection from an explicitly reviewed queue. Standard library only."""
import datetime as dt
import json
import os
from pathlib import Path
import sys
import urllib.request
import urllib.error
from zoneinfo import ZoneInfo

WEIGHTS={'philosophy':.35,'science':.35,'mobility':.25,'art':.025,'music':.025}

def choose(queue, existing, daily_limit=3, catalog_cap=1000, today=None):
    today=today or dt.datetime.now(ZoneInfo('America/Argentina/Buenos_Aires')).date()
    today_count=sum(dt.datetime.fromisoformat(r['created_at'].replace('Z','+00:00')).astimezone(ZoneInfo('America/Argentina/Buenos_Aires')).date()==today for r in existing)
    room=max(0,min(daily_limit-today_count,catalog_cap-len(existing)))
    seen={r['video_url'] for r in existing}; counts={t:sum(r['topic']==t for r in existing) for t in WEIGHTS}
    candidates=[]
    for r in queue:
        if r['video_url'] not in seen:
            candidates.append(r);seen.add(r['video_url'])
    result=[]
    while candidates and len(result)<room:
        total=len(existing)+len(result)+1
        best=max(candidates,key=lambda r:WEIGHTS[r['topic']]*total-counts[r['topic']])
        result.append(best);counts[best['topic']]+=1;candidates.remove(best)
    return result

def validate(queue):
    import re
    for r in queue:
        if r.get('topic') not in WEIGHTS or r.get('language') not in ('en','es') or r.get('status')!='approved' or r.get('origin')!='external':raise ValueError('Invalid queue metadata')
        if not re.fullmatch(r'https://www.youtube.com/watch\?v=[\w-]{11}',r.get('video_url','')):raise ValueError('Invalid video URL')
        if not r.get('source_url','').startswith('https://') or not r.get('title') or not r.get('source_name'):raise ValueError('Missing attribution')

def main():
    queue=json.loads((Path(__file__).parent/'catalog/queue.json').read_text());validate(queue)
    base=os.environ['SUPABASE_URL'].rstrip('/')
    if base!='https://jyyrbqopbftwbrhmazis.supabase.co':raise ValueError('Unexpected project URL')
    secret=os.environ.get('SUPABASE_SECRET_KEY','').strip()
    if not secret:raise ValueError('Missing server secret')
    def request(query='',body=None):
        headers={'apikey':secret,'Content-Type':'application/json','Prefer':'count=exact,resolution=ignore-duplicates,return=representation'}
        if secret.startswith('eyJ'):headers['Authorization']='Bearer '+secret
        req=urllib.request.Request(base+'/rest/v1/curio_videos'+query,data=None if body is None else json.dumps(body).encode(),headers=headers)
        with urllib.request.urlopen(req,timeout=30) as res:return json.load(res),res.headers
    existing,headers=request('?select=video_url,topic,created_at&order=created_at.desc&limit=1000')
    total=int(headers['Content-Range'].split('/')[-1])
    cap=int(os.environ.get('CATALOG_CAP','1000'));daily=int(os.environ.get('DAILY_LIMIT','3'))
    if not 1<=cap<=1000 or not 1<=daily<=10:raise ValueError('Limits outside permitted bounds')
    if total>=cap:print(f'Paused: catalog has {total} rows; cap is {cap}.');return
    if total!=len(existing):raise ValueError('Incomplete catalog response; refusing to exceed limits')
    chosen=choose(queue,existing,daily,cap)
    if not chosen:print('No additions: daily limit reached or reviewed queue exhausted.');return
    inserted,_=request('?on_conflict=video_url',chosen)
    print(f'Inserted {len(inserted)} reviewed videos. Catalog cap: {cap}. Daily maximum: {daily}.')

if __name__=='__main__':
    try:main()
    except Exception as error:
        # Never dump requests, headers, environment, or response bodies containing credentials.
        print('Import failed: '+type(error).__name__,file=sys.stderr);sys.exit(1)
