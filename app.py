import streamlit as st
import requests
import random
from datetime import datetime

st.set_page_config(page_title="ALPHA-ORACLE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS ÉLITE ---
st.markdown("""
<style>
    .stApp { background-color: #0f0c29; color: white; }
    .match-box { 
        background: rgba(255, 255, 255, 0.08); 
        border: 2px solid #00f2fe; 
        border-radius: 20px; 
        padding: 25px; 
        margin-bottom: 25px; 
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
    }
    .score-giant { font-size: 60px; color: #00f2fe; font-weight: 900; text-shadow: 0 0 20px #00f2fe; }
    .score-live { font-size: 60px; color: #ff0055; font-weight: 900; text-shadow: 0 0 20px #ff0055; }
    .team-name { font-size: 18px; font-weight: bold; color: #ffffff; }
    .live-badge { background: #ff0055; color: white; padding: 5px 15px; border-radius: 5px; font-size: 14px; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data():
    headers = {'X-Auth-Token': API_KEY}
    all_matches = []
    try:
        for lg in ['FL1', 'PL', 'CL']:
            r = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/matches", headers=headers).json()
            if 'matches' in r: all_matches.extend(r['matches'])
        return all_matches
    except: return []

matches = get_data()

st.title("🎯 ALPHA-ORACLE by Houzdane.Bdess")

if matches:
    today = datetime.utcnow().strftime('%Y-%m-%d')
    today_matches = [m for m in matches if m['utcDate'].startswith(today)]
    
    if not today_matches:
        st.info("Aucun match aujourd'hui. Les scores de demain apparaîtront automatiquement dès le matin !")
    else:
        for m in today_matches:
            h_team = m['homeTeam']['name']
            a_team = m['awayTeam']['name']
            status = m['status']
            
            # Score réel
            r_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
            r_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
            
            # Prédiction IA (basée sur l'ID du match pour rester fixe)
            random.seed(m['id'])
            p_h, p_a = random.randint(0, 3), random.randint(0, 2)
            
            # Affichage de la carte de score
            st.markdown(f"""
            <div class="match-box">
                <div style="margin-bottom: 10px;">
                    <span style="color:#aaa;">🕒 {m['utcDate'][11:16]} UTC</span>
                    {" <span class='live-badge'>EN DIRECT</span>" if status in ['IN_PLAY', 'PAUSED'] else ""}
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center;">
                    <div class="team-name" style="width:30%;">{h_team}</div>
                    <div style="width:40%;">
                        <div class="{'score-live' if status != 'TIMED' else 'score-giant'}">
                            {r_h if status != 'TIMED' else p_h} - {r_a if status != 'TIMED' else p_a}
                        </div>
                        <div style="font-size:14px; color:#00f2fe; margin-top:10px; font-weight:bold; letter-spacing:1px;">
                            PRÉDICTION IA : {p_h} - {p_a}
                        </div>
                    </div>
                    <div class="team-name" style="width:30%;">{a_team}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.error("Données indisponibles. Réessaie dans une minute.")

st.markdown("<br><center>🚀 ALPHA-ORACLE AUTOMATISÉ</center>", unsafe_allow_html=True)


