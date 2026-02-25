import streamlit as st
import requests
import random
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="ALPHA-ORACLE by Houzdane.Bdess", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS ---
st.markdown("""
<style>
    .stApp { background: #0f0c29; color: white; }
    .card { 
        background: rgba(255, 255, 255, 0.05); 
        border: 1px solid #00f2fe; 
        border-radius: 15px; 
        padding: 15px; 
        margin-bottom: 15px; 
    }
    .score-exact { font-size: 38px; color: #00f2fe; font-weight: bold; text-align: center; }
    .time-badge { color: #ff0055; font-weight: bold; font-size: 14px; }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: rgba(15, 12, 41, 0.95); color: #00f2fe;
        text-align: center; padding: 10px; font-weight: bold; border-top: 1px solid #00f2fe; z-index: 999;
    }
    .btn-share {
        background-color: #25d366 !important;
        color: white !important;
        padding: 6px 15px !important;
        border-radius: 20px !important;
        text-decoration: none !important;
        font-weight: bold !important;
        font-size: 12px !important;
        display: inline-block !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_all_leagues_data():
    headers = {'X-Auth-Token': API_KEY}
    leagues = ['FL1', 'PL', 'CL']
    all_matches = []
    all_stats = {}
    try:
        for league in leagues:
            s = requests.get(f"https://api.football-data.org/v4/competitions/{league}/standings", headers=headers).json()
            m = requests.get(f"https://api.football-data.org/v4/competitions/{league}/matches", headers=headers).json()
            if 'standings' in s:
                for t in s['standings'][0]['table']:
                    all_stats[t['team']['name']] = {
                        'logo': t['team']['crest'], 'rank': t['position'],
                        'gf': (t['goalsFor'] / max(1, t['playedGames'])),
                        'ga': (t['goalsAgainst'] / max(1, t['playedGames']))
                    }
            if 'matches' in m: all_matches.extend(m['matches'])
        return all_stats, all_matches
    except: return None, None

def predict_score(h_n, a_n, stats):
    if h_n not in stats or a_n not in stats: return 1, 1
    exp_h = (stats[h_n]['gf'] + stats[a_n]['ga']) / 2
    exp_a = (stats[a_n]['gf'] + stats[h_n]['ga']) / 2
    if stats[h_n]['rank'] < stats[a_n]['rank']: exp_h += 0.5
    else: exp_a += 0.5
    return max(0, round(exp_h + random.uniform(-0.2, 0.2))), max(0, round(exp_a + random.uniform(-0.2, 0.2)))

stats, all_matches = get_all_leagues_data()

if stats and all_matches:
    st.title("🎯 ALPHA-ORACLE by Houzdane.Bdess")
    tab1, tab2, tab3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER FUTUR", "📊 COMPARATEUR"])

    now = datetime.utcnow()
    today_str = now.strftime('%Y-%m-%d')

    with tab1:
        matches_today = [m for m in all_matches if m['utcDate'].startswith(today_str)]
        if not matches_today: st.info("Pas de matchs aujourd'hui.")
        for m in matches_today:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            p_h, p_a = predict_score(h_n, a_n, stats)
            link_wa = f"https://wa.me/?text={urllib.parse.quote(f'⚽ Prono {h_n} {p_h}-{p_a} {a_n}')}"
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="time-badge">🕒 {dt.strftime('%H:%M')}</span>
                    <a href="{link_wa}" target="_blank" class="btn-share">📲 PARTAGER</a>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center; margin-top:15px;">
                    <div style="text-align:center; width:30%;"><img src="{stats.get(h_n,{}).get('logo','')}" width="50"><br><small>{h_n}</small></div>
                    <div class="score-exact">{p_h} - {p_a}</div>
                    <div style="text-align:center; width:30%;"><img src="{stats.get(a_n,{}).get('logo','')}" width="50"><br><small>{a_n}</small></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab2:
        upcoming = [m for m in all_matches if m['status'] in ['TIMED', 'SCHEDULED'] and not m['utcDate'].startswith(today_str)]
        for m in upcoming[:10]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            p_h, p_a = predict_score(h_n, a_n, stats)
            st.markdown(f"""<div class="card">
                <span style="color:#aaa;">📅 {dt.strftime('%d/%m à %H:%M')}</span>
                <div style="display:flex; justify-content:space-around; align-items:center;">
                    <div style="text-align:center; width:30%;"><img src="{stats.get(h_n,{}).get('logo','')}" width="40"><br><small>{h_n}</small></div>
                    <div style="font-size:24px; font-weight:bold; color:#00f2fe;">{p_h} - {p_a}</div>
                    <div style="text-align:center; width:30%;"><img src="{stats.get(a_n,{}).get('logo','')}" width="40"><br><small>{a_n}</small></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab3:
        past = [m for m in all_matches if m['status'] == 'FINISHED'][::-1]
        for m in past[:15]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            r_h, r_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
            st.markdown(f"""<div class="card"><img src="{stats.get(h_n,{}).get('logo','')}" width="20"> {h_n} <b>{r_h} - {r_a}</b> {a_n} <img src="{stats.get(a_n,{}).get('logo','')}" width="20"></div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:100px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">🚀 ALPHA-ORACLE by Houzdane.Bdess</div>', unsafe_allow_html=True)
else:
    st.error("Données indisponibles.")
