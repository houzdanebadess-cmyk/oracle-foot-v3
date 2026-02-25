import streamlit as st
import requests
import random
from datetime import datetime

st.set_page_config(page_title="ALPHA-ORACLE V3", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS (SIGNATURE INCLUSE) ---
st.markdown("""
<style>
    .stApp { background: #0f0c29; color: white; }
    .card { background: rgba(255, 255, 255, 0.05); border: 1px solid #00f2fe; border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    .score-exact { font-size: 32px; color: #00f2fe; font-weight: bold; text-align: center; }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(15, 12, 41, 0.9);
        color: #00f2fe;
        text-align: center;
        padding: 10px;
        font-family: 'Orbitron', sans-serif;
        font-size: 14px;
        border-top: 1px solid #00f2fe;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data():
    headers = {'X-Auth-Token': API_KEY}
    try:
        standings = requests.get("https://api.football-data.org/v4/competitions/FL1/standings", headers=headers).json()
        matches = requests.get("https://api.football-data.org/v4/competitions/FL1/matches", headers=headers).json()
        return standings['standings'][0]['table'], matches['matches']
    except: return None, None

table, all_matches = get_data()

def predict_score(h_n, a_n, stats):
    exp_h = (stats[h_n]['gf'] + stats[a_n]['ga']) / 2
    exp_a = (stats[a_n]['gf'] + stats[h_n]['ga']) / 2
    return max(0, round(exp_h * 1.1 + random.uniform(-0.5, 0.5))), max(0, round(exp_a + random.uniform(-0.5, 0.5)))

if table and all_matches:
    stats = {t['team']['name']: {
        'logo': t['team']['crest'], 
        'gf': t['goalsFor'] / max(1, t['playedGames']),
        'ga': t['goalsAgainst'] / max(1, t['playedGames'])
    } for t in table}

    st.title("🎯 ALPHA-ORACLE : PRÉDICTIONS vs RÉALITÉ")
    
    tab1, tab2 = st.tabs(["🔮 PRÉDICTIONS", "📊 COMPARATEUR"])

    with tab1:
        search = st.text_input("🔍 Équipe...").lower()
        upcoming = [m for m in all_matches if m['status'] in ['TIMED', 'SCHEDULED', 'IN_PLAY']]
        for m in upcoming:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            if (search in h_n.lower() or search in a_n.lower()) and h_n in stats and a_n in stats:
                p_h, p_a = predict_score(h_n, a_n, stats)
                st.markdown(f"""<div class="card"><div style="display:flex; justify-content:space-around; align-items:center;">
                    <div style="text-align:center; width:30%;"><img src="{stats[h_n]['logo']}" width="50"><br>{h_n}</div>
                    <div style="text-align:center;"><div style="font-size:10px; color:#00f2fe;">PRÉDICTION</div><div class="score-exact">{p_h} - {p_a}</div></div>
                    <div style="text-align:center; width:30%;"><img src="{stats[a_n]['logo']}" width="50"><br>{a_n}</div>
                </div></div>""", unsafe_allow_html=True)

    with tab2:
        search2 = st.text_input("🔍 Comparaison...").lower()
        past = [m for m in all_matches if m['status'] == 'FINISHED'][::-1]
        for m in past[:15]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            if (search2 in h_n.lower() or search2 in a_n.lower()) and h_n in stats and a_n in stats:
                p_h, p_a = predict_score(h_n, a_n, stats)
                real_h, real_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
                win_color = "#00ff88" if (real_h > real_a and p_h > p_a) or (real_h < real_a and p_h < p_a) or (real_h == real_a and p_h == p_a) else "#ff4444"
                st.markdown(f"""<div class="card" style="border-left: 5px solid {win_color};">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span>{h_n} <b>{real_h} - {real_a}</b> {a_n}</span>
                        <span style="color:{win_color}; font-size:11px;">🤖 PRÉDICTION : {p_h}-{p_a}</span>
                    </div></div>""", unsafe_allow_html=True)

    # --- TA SIGNATURE EN BAS ---
    st.markdown("""<div class="footer">🚀 Codé avec Houzdane.Bdess</div>""", unsafe_allow_html=True)

else:
    st.error("Données indisponibles.")
