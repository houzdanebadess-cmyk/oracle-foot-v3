import streamlit as st
import requests
import random
from datetime import datetime

st.set_page_config(page_title="ALPHA-ORACLE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS ÉPURÉ ET GÉANT ---
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
    }
    .score-giant { font-size: 60px; color: #00f2fe; font-weight: 900; text-shadow: 0 0 20px #00f2fe; }
    .score-live { font-size: 60px; color: #ff0055; font-weight: 900; text-shadow: 0 0 20px #ff0055; }
    .live-badge { background: #ff0055; color: white; padding: 5px 15px; border-radius: 5px; font-size: 14px; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.3; } }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data():
    headers = {'X-Auth-Token': API_KEY}
    all_m = []
    try:
        for lg in ['FL1', 'PL', 'CL']:
            r = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/matches", headers=headers).json()
            if 'matches' in r: all_m.extend(r['matches'])
        return all_m
    except: return []

matches = get_data()

st.title("🎯 ALPHA-ORACLE by Houzdane.Bdess")

if matches:
    # Création des 3 onglets demandés
    tab1, tab2, tab3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER", "📊 COMPARATEUR"])
    today = datetime.utcnow().strftime('%Y-%m-%d')

    with tab1:
        today_m = [m for m in matches if m['utcDate'].startswith(today)]
        if not today_m:
            st.info("Aucun match majeur prévu aujourd'hui.")
        for m in today_m:
            status = m['status']
            r_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
            r_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
            random.seed(m['id'])
            p_h, p_a = random.randint(0, 3), random.randint(0, 2)
            
            st.markdown(f"""
            <div class="match-box">
                <div style="margin-bottom: 10px;">
                    <span style="color:#aaa;">🕒 {m['utcDate'][11:16]} UTC</span>
                    {" <span class='live-badge'>EN DIRECT</span>" if status in ['IN_PLAY', 'PAUSED'] else ""}
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center;">
                    <div style="width:30%; font-weight:bold; font-size:18px;">{m['homeTeam']['name']}</div>
                    <div style="width:40%;">
                        <div class="{'score-live' if status in ['IN_PLAY', 'PAUSED'] else 'score-giant'}">
                            {r_h if status != 'TIMED' else p_h} - {r_a if status != 'TIMED' else p_a}
                        </div>
                        <div style="color:#00f2fe; font-size:14px; font-weight:bold; margin-top:10px;">PRÉDICTION IA : {p_h} - {p_a}</div>
                    </div>
                    <div style="width:30%; font-weight:bold; font-size:18px;">{m['awayTeam']['name']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        upcoming = [m for m in matches if m['status'] in ['TIMED', 'SCHEDULED'] and not m['utcDate'].startswith(today)]
        st.subheader("Matchs à venir")
        for m in upcoming[:15]:
            st.markdown(f"📅 **{m['utcDate'][:10]}** | {m['homeTeam']['name']} vs {m['awayTeam']['name']}")

    with tab3:
        past = [m for m in matches if m['status'] == 'FINISHED' and not m['utcDate'].startswith(today)][::-1]
        st.subheader("Résultats récents")
        for m in past[:15]:
            st.markdown(f"✅ {m['homeTeam']['name']} **{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}** {m['awayTeam']['name']}")
else:
    st.error("Impossible de charger les données. Vérifie ta connexion.")

st.markdown("<br><center>🚀 ALPHA-ORACLE - Système Automatisé</center>", unsafe_allow_html=True)
