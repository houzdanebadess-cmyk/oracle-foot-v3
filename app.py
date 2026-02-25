import streamlit as st
import requests
import random
from datetime import datetime
import urllib.parse

# Config de la page
st.set_page_config(page_title="ALPHA-ORACLE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- DESIGN (CSS) ---
st.markdown("""
<style>
    .stApp { background: #0f0c29; color: white; }
    .card { background: rgba(255, 255, 255, 0.05); border: 1px solid #00f2fe; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    .score-giant { font-size: 50px; color: #00f2fe; font-weight: 900; text-align: center; text-shadow: 0 0 15px #00f2fe; }
    .score-live { font-size: 50px; color: #ff0055; font-weight: 900; text-align: center; text-shadow: 0 0 15px #ff0055; }
    .btn-share { background-color: #25d366 !important; color: white !important; padding: 10px 20px; border-radius: 30px; text-decoration: none; font-weight: bold; display: inline-block; }
    .live-badge { background: #ff0055; color: white; padding: 4px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data():
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

def predict(h, a, s):
    if h not in s or a not in s: return 1, 0
    eh, ea = (s[h]['gf']+s[a]['ga'])/2, (s[a]['gf']+s[h]['ga'])/2
    if s[h]['rank'] < s[a]['rank']: eh += 0.5
    return max(0, round(eh + random.uniform(-0.1, 0.1))), max(0, round(ea + random.uniform(-0.1, 0.1)))

stats, matches = get_data()

if stats and matches:
    st.title("🎯 ALPHA-ORACLE by Houzdane.Bdess")
    t1, t2, t3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER", "📊 COMPARATEUR"])
    
    # Détection de la date d'aujourd'hui
    today = datetime.utcnow().strftime('%Y-%m-%d')

    with t1:
        # On affiche TOUS les matchs qui commencent aujourd'hui
        today_m = [m for m in matches if m['utcDate'].startswith(today)]
        if not today_m: 
            st.info("Aucun match majeur aujourd'hui. Rendez-vous demain !")
        
        for m in today_m:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            p_h, p_a = predict(h_n, a_n, stats)
            status = m['status']
            
            # Récupération du score réel pour le direct
            r_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
            r_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
            
            link = f"https://wa.me/?text={urllib.parse.quote(f'⚽ Mon prono ALPHA-ORACLE : {h_n} {p_h}-{p_a} {a_n}')}"
            
            # --- STRUCTURE DE LA CARTE ---
            card_html = f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <span style="color:#ff0055; font-weight:bold;">🕒 {m['utcDate'][11:16]} UTC</span>
                    {"<span class='live-badge'>DIRECT</span>" if status in ['IN_PLAY', 'PAUSED'] else ""}
                    <a href="{link}" target="_blank" class="btn-share">📲 PARTAGER</a>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center;">
                    <div style="text-align:center; width:30%;"><img src="{stats.get(h_n,{}).get('logo','')}" width="65"><br><small>{h_n}</small></div>
                    <div style="text-align:center; width:40%;">
                        <div style="font-size:12px; color:#aaa; margin-bottom:5px;">{'SCORE LIVE' if status != 'TIMED' else 'PRONO IA'}</div>
                        <div class="{'score-live' if status in ['IN_PLAY', 'PAUSED'] else 'score-giant'}">
                            {r_h if status != 'TIMED' else p_h} - {r_a if status != 'TIMED' else p_a}
                        </div>
                        {f"<div style='color:#00f2fe; font-size:14px; margin-top:10px;'>Prono IA : {p_h}-{p_a}</div>" if status != "TIMED" else ""}
                    </div>
                    <div style="text-align:center; width:30%;"><img src="{stats.get(a_n,{}).get('logo','')}" width="65"><br><small>{a_n}</small></div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    with t2:
        # Matchs des jours suivants
        upcoming = [m for m in matches if m['status'] in ['TIMED', 'SCHEDULED'] and not m['utcDate'].startswith(today)]
        for m in upcoming[:10]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            p_h, p_a = predict(h_n, a_n, stats)
            st.markdown(f"""
            <div class="card">
                <div style="text-align:center;">
                    <small style="color:#aaa;">{m['utcDate'][:10]} à {m['utcDate'][11:16]}</small><br>
                    <span style="font-size:20px;">{h_n} <b>{p_h}-{p_a}</b> {a_n}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br><br><div style='text-align:center; color:#00f2fe;'>🚀 ALPHA-ORACLE by Houzdane.Bdess</div>", unsafe_allow_html=True)
else:
    st.error("Erreur de connexion aux données. Vérifie ta clé API.")
