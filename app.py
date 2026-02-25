import streamlit as st
import requests
import random
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="ALPHA-ORACLE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS ÉLITE ---
st.markdown("""
<style>
    .stApp { background: #0f0c29; color: white; }
    .card { background: rgba(255, 255, 255, 0.05); border: 1px solid #00f2fe; border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    .score-giant { font-size: 55px; color: #00f2fe; font-weight: 900; text-align: center; text-shadow: 0 0 20px #00f2fe; line-height: 1; }
    .score-live { font-size: 55px; color: #ff0055; font-weight: 900; text-align: center; text-shadow: 0 0 20px #ff0055; line-height: 1; }
    .btn-share { background-color: #25d366 !important; color: white !important; padding: 10px 20px; border-radius: 25px; text-decoration: none; font-weight: bold; display: inline-block; }
    .live-badge { background: #ff0055; color: white; padding: 4px 12px; border-radius: 5px; font-size: 12px; font-weight: bold; animation: blinker 1s linear infinite; }
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
    today = datetime.utcnow().strftime('%Y-%m-%d')

    with t1:
        # Filtre pour voir TOUS les matchs d'aujourd'hui, même ceux terminés ou en cours
        today_m = [m for m in matches if m['utcDate'].startswith(today)]
        if not today_m: st.info("Aucun match majeur aujourd'hui.")
        for m in today_m:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            p_h, p_a = predict(h_n, a_n, stats)
            status = m['status']
            r_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
            r_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
            link = f"https://wa.me/?text={urllib.parse.quote(f'⚽ Prono {h_n} {p_h}-{p_a} {a_n}')}"
            
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                    <span style="color:#ff0055; font-weight:bold;">🕒 {m['utcDate'][11:16]}</span>
                    { '<span class="live-badge">DIRECT</span>' if status in ['IN_PLAY', 'PAUSED'] else '' }
                    <a href="{link}" target="_blank" class="btn-share">📲 PARTAGER</a>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center;">
                    <div style="text-align:center; width:30%;"><img src="{stats.get(h_n,{}).get('logo','')}" width="65"><br><small>{h_n}</small></div>
                    <div style="text-align:center;">
                        <div style="font-size:12px; color:#aaa;">{ 'SCORE ACTUEL' if status != 'TIMED' else 'SCORE IA' }</div>
                        <div class="{ 'score-live' if status in ['IN_PLAY', 'PAUSED'] else 'score-giant' }">
                            {r_h if status != 'TIMED' else p_h} - {r_a if status != 'TIMED' else p_a}
                        </div>
                        { f'<div style="font-size:14px; color:#00f2fe; margin-top:8px; font-weight:bold;">Prono IA : {p_h}-{p_a}</div>' if status != 'TIMED' else '' }
                    </div>
                    <div style="text-align:center; width:30%;"><img src="{stats.get(a_n,{}).get('logo','')}" width="65"><br><small>{a_n}</small></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with t2:
        upcoming = [m for m in matches if m['status'] in ['TIMED', 'SCHEDULED'] and not m['utcDate'].startswith(today)]
        for m in upcoming[:10]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            p_h, p_a = predict(h_n, a_n, stats)
            st.markdown(f'<div class="card"><div style="display:flex; justify-content:space-around; align-items:center;"><img src="{stats.get(h_n,{}).get('logo','')}" width="40"> <span class="score-giant" style="font-size:30px;">{p_h}-{p_a}</span> <img src="{stats.get(a_n,{}).get('logo','')}" width="40"></div></div>', unsafe_allow_html=True)

    with t3:
        past = [m for m in matches if m['status'] == 'FINISHED' and not m['utcDate'].startswith(today)][::-1]
        for m in past[:15]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            st.markdown(f'<div class="card" style="padding:10px;">{h_n} <b>{m["score"]["fullTime"]["home"]}-{m["score"]["fullTime"]["away"]}</b> {a_n}</div>', unsafe_allow_html=True)

    st.markdown('<div style="height:100px;"></div><div style="position:fixed; bottom:0; width:100%; background:#0f0c29; text-align:center; padding:10px; border-top:1px solid #00f2fe;">🚀 ALPHA-ORACLE by Houzdane.Bdess</div>', unsafe_allow_html=True)
else:
    st.error("Erreur API : Vérifie ta connexion ou attends 1 minute.")
