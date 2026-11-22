import pandas as pd, urllib.request, time, csv, io
from pathlib import Path
P=Path(__file__).parent
G=pd.read_csv(P/'games.csv',dtype={'universe_id':str})
H=pd.read_csv(P/'daily_history.csv',dtype={'universe_id':str})
known=set(H.universe_id.astype(str))
missing=G[~G.universe_id.astype(str).isin(known)]
new=[]; failures=[]
for i,(_,g) in enumerate(missing.iterrows(),1):
 uid=str(g.universe_id); url=f'https://rowatcher.com/api/v1/games/{uid}/history.csv?days=90'
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'RobloxMarketResearch/1.0'})
  with urllib.request.urlopen(req,timeout=15) as r: data=r.read().decode('utf-8','replace')
  for row in csv.DictReader(data.splitlines()):
   if not row.get('date'): continue
   new.append({'universe_id':uid,'game_name':g['name'],'api_genre':g['api_genre'],'date':row.get('date'),
    'playing_avg':int(row['playing_avg']) if row.get('playing_avg') else None,
    'playing_min':int(row['playing_min']) if row.get('playing_min') else None,
    'playing_max':int(row['playing_max']) if row.get('playing_max') else None,
    'history_source':url})
 except Exception as e: failures.append({'universe_id':uid,'game_name':g['name'],'genre':g['api_genre'],'error':str(e)})
 time.sleep(1.15)
 if i%15==0: print(f'{i}/{len(missing)}; success={len(set(x["universe_id"] for x in new))}; failures={len(failures)}',flush=True)
if new:
 H=pd.concat([H,pd.DataFrame(new)],ignore_index=True).drop_duplicates(['universe_id','date'])
 H.to_csv(P/'daily_history.csv',index=False)
pd.DataFrame(failures).to_csv(P/'history_failures.csv',index=False)
print('DONE historical_games=',H.universe_id.nunique(),'rows=',len(H),'new_rows=',len(new),'failed_games=',len(failures),flush=True)
