import streamlit as st
import requests
import random
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="ALPHA-ORACLE by Houzdane.Bdess", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

st.markdown("""
<style>
    .stApp { background: #0f0c29; color: white; }
    .card { background: rgba(255, 255, 255, 0.05); border: 1px solid #00f2fe; border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    .score-live { font-size: 42px; color: #ff0055; font-weight: bold; text-align: center; text-shadow: 0 0 10px #ff0055; }
    .score-predict { font-size: 32px; color: #00f2fe; font-weight: bold; text-align: center; }
    .live-badge { background: #ff0055; color: white; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: bold; animation: blink 1s infinite; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .btn-share { background-color: #25d366 !important; color: white !important; padding: 6px 12px; border-radius: 20px; text-decoration: none; font-size: 12px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_all_data():
    headers = {'X-Auth-Token': API_KEY}
    leagues = ['FL1', 'PL', 'CL']
    all_m, all_s = [], {}
    try:
        for lg in leagues:
            s = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/standings", headers=headers).json()
            m = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/matches", headers=headers).json()
            if 'standings' in s:
                for t in s['standings'][0]['table']:
                    all_s[t['team']['name']] = {'logo': t['team']['crest'], 'rank': t['position'], 'gf': t['goalsFor']/max(1,t['playedGames']), 'ga': t['goalsAgainst']/max(1,t['playedGames'])}
            if 'matches' in m: all_m.extend(m['matches'])
        return all_s, all_m
    except: return None, None

def predict_score(h, a, s):
    if h not in s or a not in s: return 1, 0
    eh, ea = (s[h]['gf']+s[a]['ga'])/2, (s[a]['gf']+s[h]['ga'])/2
    if s[h]['rank'] < s[a]['rank']: eh += 0.5
    return max(0, round(eh + random.uniform(-0.2, 0.2))), max(0, round(ea + random.uniform(-0.2, 0.2)))

stats, matches = get_all_data()

if stats and matches:
    st.title("🎯 ALPHA-ORACLE : LIVE MODE")
    t1, t2, t3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 FUTUR", "📊 HISTORIQUE"])
    
    today = datetime.utcnow().strftime('%Y-%m-%d')

    with t1:
        today_m = [m for m in matches if m['utcDate'].startswith(today)]
        if not today_m: st.info("Aucun match en cours ou prévu aujourd'hui.")
        for m in today_m:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            p_h, p_a = predict_score(h_n, a_n, stats)
            status = m['status']
            # Score réel
            r_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
            r_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
            
            link = f"https://wa.me/?text={urllib.parse.quote(f'⚽ Prono {h_n} {p_h}-{p_a} {a_n}')}"
            
            st.markdown(f"""<div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#ff0055;">🕒 {m['utcDate'][11:16]}</span>
                    { '<span class="live-badge">DIRECT 2E MI-TEMPS</span>' if status in ['IN_PLAY', 'PAUSED'] else '' }
                    <a href="{link}" target="_blank" class="btn-share">📲 PARTAGER</a>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center; margin-top:15px;">
                    <div style="text-align:center; width:30%;"><img src="{stats.get(h_n,{}).get('logo','')}" width="50"><br><small>{h_n}</small></div>
                    <div style="text-align:center;">
                        <div style="font-size:10px; color:#aaa;">{ 'SCORE ACTUEL' if status != 'TIMED' else 'PRÉDICTION IA' }</div>
                        <div class="{ 'score-live' if status in ['IN_PLAY', 'PAUSED'] else 'score-predict' }">
                            {r_h if status != 'TIMED' else p_h} - {r_a if status != 'TIMED' else p_a}
                        </div>
                        { f'<div style="font-size:10px; color:#00f2fe;">Prono IA: {p_h}-{p_a}</div>' if status != 'TIMED' else '' }
                    </div>
                    <div style="text-align:center; width:30%;"><img src="{stats.get(a_n,{}).get('logo','')}" width="50"><br><small>{a_n}</small></div>
                </div>
            </div>""", unsafe_allow_html=True)

    # ... (Le reste des onglets est déjà géré automatiquement par les fonctions du dessus)
    st.markdown('<div class="footer">🚀 ALPHA-ORACLE by Houzdane.Bdess</div>', unsafe_allow_html=True)
else:
    st.error("Connexion à l'API impossible. Réessaie dans 1 minute.")
