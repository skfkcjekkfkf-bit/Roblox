import concurrent.futures, csv, json, time, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

OUT=Path(__file__).parent
BASE='https://rowatcher.com/api/v1'
GENRES=['Simulation','Survival','Action','Roleplay & Avatar Sim','RPG','Sports & Racing']
HEAD={'User-Agent':'RobloxMarketResearch/1.0 (public data analysis)'}

def get_json(url, attempts=4):
    for n in range(attempts):
        try:
            req=urllib.request.Request(url,headers=HEAD)
            with urllib.request.urlopen(req,timeout=25) as r:
                return json.load(r)
        except Exception:
            if n==attempts-1: raise
            time.sleep(1.5*(n+1))

def fetch_genre(genre):
    url=f'{BASE}/games?genre={urllib.parse.quote(genre)}'
    res=get_json(url)
    return genre,res

stamp=datetime.now(timezone.utc).isoformat(timespec='seconds')
# Collect up to 25 records surfaced per platform genre; record the returned sample as-is.
genre_results=[]
for genre in GENRES:
    genre_results.append(fetch_genre(genre))
    time.sleep(1.2)
rows=[]
for genre,res in genre_results:
    data=res.get('data',[])
    # Systematic sample across the endpoint's 25 surfaced records to include its full observed range.
    chosen=[data[i] for i in sorted(set(round(j*(len(data)-1)/14) for j in range(min(15,len(data)))))] if data else []
    for rank,g in enumerate(chosen,1):
        rows.append({
            'universe_id':str(g.get('universeId') or g.get('_id')),
            'name':g.get('name'), 'creator':g.get('creatorName'), 'creator_type':g.get('creatorType'),
            'api_genre':genre, 'api_subgenre':g.get('subgenre'), 'selection_source':'RoWatcher genre-filtered games endpoint',
            'within_response_position':rank, 'roblox_created_at':g.get('robloxCreatedAt'),
            'playing_at_collection':g.get('playing'), 'visits_lifetime':g.get('visits'), 'favorites':g.get('favorites'),
            'likes':g.get('likes'), 'dislikes':g.get('dislikes'), 'like_ratio':g.get('likeRatio'),
            'tracker_first_seen':g.get('firstSeen'), 'tracker_last_scraped':g.get('lastScraped'),
            'ccu_delta_24h_tracker':g.get('ccuDelta24h'), 'ccu_delta_pct_24h_tracker':g.get('ccuDeltaPercent24h'),
            'estimated_monthly_revenue_usd_tracker':g.get('estimatedMonthlyRevenueUsd'),
            'revenue_estimate_methodology':json.dumps(g.get('revenueEstimate'),ensure_ascii=False),
            'data_source':'https://rowatcher.com/api/v1/games?genre='+urllib.parse.quote(genre), 'collected_utc':stamp,
        })
# Deduplicate universe IDs, retaining first encountered genre assignment while recording duplicates separately.
seen={}; duplicates=[]
for r in rows:
    k=r['universe_id']
    if k in seen:
        duplicates.append({'universe_id':k,'name':r['name'],'first_genre':seen[k]['api_genre'],'also_returned_under':r['api_genre']})
    else: seen[k]=r
unique=list(seen.values())
# Daily average/min/max player history for 90 days, when available.
def fetch_history(r):
    url=f"{BASE}/games/{urllib.parse.quote(r['universe_id'])}/history.csv?days=90"
    try:
        req=urllib.request.Request(url,headers=HEAD)
        with urllib.request.urlopen(req,timeout=25) as x: txt=x.read().decode('utf-8','replace')
        return r['universe_id'],txt,None
    except Exception as e: return r['universe_id'],'',str(e)
histories=[]
for r in unique:
    histories.append(fetch_history(r))
    time.sleep(1.2)
byid={r['universe_id']:r for r in unique}
long=[]; errors=[]
for uid,txt,err in histories:
    if err:
        errors.append({'universe_id':uid,'error':err});continue
    lines=list(csv.DictReader(txt.splitlines()))
    for x in lines:
        try:
            long.append({'universe_id':uid,'game_name':byid[uid]['name'],'api_genre':byid[uid]['api_genre'],
                         'date':x.get('date'),'playing_avg':int(x['playing_avg']) if x.get('playing_avg') else None,
                         'playing_min':int(x['playing_min']) if x.get('playing_min') else None,
                         'playing_max':int(x['playing_max']) if x.get('playing_max') else None,
                         'history_source':f"{BASE}/games/{uid}/history.csv?days=90"})
        except Exception: pass
pd.DataFrame(unique).to_csv(OUT/'games.csv',index=False)
pd.DataFrame(long).to_csv(OUT/'daily_history.csv',index=False)
pd.DataFrame(duplicates).to_csv(OUT/'deduped_duplicates.csv',index=False)
# Reproducible descriptive summaries; report category sample counts and coverage.
games=pd.DataFrame(unique)
hist=pd.DataFrame(long)
summary={'collected_utc':stamp,'genres_requested':GENRES,'unique_games':len(unique),'raw_rows':len(rows),'duplicate_rows':len(duplicates),'history_error_games':len(errors),'history_rows':len(long),'history_days_by_game':{},'genre_summary':{},'limitations':[
 'RoWatcher dataset/search endpoint sample, not a random sample of all Roblox experiences.',
 'The six labels are platform/tracker genre labels, not validated gameplay-mechanic taxonomies.',
 'Current players are a single time-specific snapshot and depend on time zone/day.',
 'The tracker revenue field is modeled estimate, not verified revenue or net profit.',
 'Daily histories are tracker observations; game-by-game lookback can differ and chart visibility does not prove popularity duration.'
]}
if not hist.empty:
    summary['history_days_by_game']=hist.groupby('universe_id').size().describe().to_dict()
for genre,g in games.groupby('api_genre'):
    ids=set(g.universe_id)
    h=hist[hist.universe_id.isin(ids)] if not hist.empty else pd.DataFrame()
    rec={'n':int(len(g))}
    for col in ['playing_at_collection','visits_lifetime','favorites','likes','like_ratio']:
        v=pd.to_numeric(g[col],errors='coerce').dropna()
        if len(v):rec[col]={'n':int(len(v)),'median':float(v.median()),'q1':float(v.quantile(.25)),'q3':float(v.quantile(.75)),'min':float(v.min()),'max':float(v.max())}
    if not h.empty:
        h['playing_avg']=pd.to_numeric(h.playing_avg,errors='coerce')
        peak=h.loc[h.groupby('universe_id').playing_avg.idxmax().dropna()]
        rec['history_games']=int(h.universe_id.nunique())
        rec['median_observed_days_per_game']=float(h.groupby('universe_id').size().median())
        rec['median_peak_daily_avg_ccu']=float(peak.playing_avg.median()) if len(peak) else None
    summary['genre_summary'][genre]=rec
(OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))
print(json.dumps(summary,ensure_ascii=False,indent=2))
print('history errors:',errors[:5])
