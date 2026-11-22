"""Reproduce descriptive statistics from games.csv and daily_history.csv."""
from pathlib import Path
import json
import pandas as pd

P=Path(__file__).parent
G=pd.read_csv(P/'games.csv',dtype={'universe_id':str})
H=pd.read_csv(P/'daily_history.csv',dtype={'universe_id':str},parse_dates=['date'])
H['playing_avg']=pd.to_numeric(H.playing_avg,errors='coerce')
H['playing_min']=pd.to_numeric(H.playing_min,errors='coerce')
H['playing_max']=pd.to_numeric(H.playing_max,errors='coerce')

def desc(series):
    s=pd.to_numeric(pd.Series(series),errors='coerce').dropna()
    if s.empty:return None
    return {'n':int(s.count()),'median':float(s.median()),'q1':float(s.quantile(.25)),
            'q3':float(s.quantile(.75)),'min':float(s.min()),'max':float(s.max())}

out={'collection_time_utc':str(G.collected_utc.iloc[0]),'games_n':int(G.universe_id.nunique()),
     'daily_history_games_n':int(H.universe_id.nunique()),'daily_history_rows_n':int(len(H)),
     'history_day_span':{'first':str(H.date.min().date()),'last':str(H.date.max().date())},
     'history_days_per_game':desc(H.groupby('universe_id').size()),
     'estimated_revenue_value_nonmissing':int(pd.to_numeric(G.estimated_monthly_revenue_usd_tracker,errors='coerce').notna().sum()),
     'verified_actual_revenue_records':0,'genres':{}}
for genre,g in G.groupby('api_genre',sort=True):
    h=H[H.api_genre==genre]
    draw=[]; history_len=[]
    for uid,d in h.groupby('universe_id'):
        d=d.dropna(subset=['playing_avg']).sort_values('date')
        history_len.append(len(d))
        if len(d)<3:continue
        peak=float(d.playing_avg.max()); last=float(d.iloc[-1].playing_avg)
        if peak>0:draw.append((last/peak-1)*100)
    out['genres'][genre]={
        'games_n':int(g.universe_id.nunique()),
        'current_ccu':desc(g.playing_at_collection),
        'lifetime_visits':desc(g.visits_lifetime),
        'likes':desc(g.likes),'favorites':desc(g.favorites),
        'games_with_history_n':int(h.universe_id.nunique()),
        'history_days_per_game':desc(history_len),
        'latest_observation_vs_own_recorded_peak_percent':desc(draw),
        'games_latest_below_recorded_peak_n':int(sum(v<0 for v in draw)),
        'games_in_drawdown_calculation_n':int(len(draw))
    }
(P/'analysis_summary.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
