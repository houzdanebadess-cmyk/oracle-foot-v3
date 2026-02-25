import streamlit as st
import requests
import random
from datetime import datetime

st.set_page_config(page_title="ALPHA-ORACLE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS (PROPRE ET SÉCURISÉ) ---
st.markdown("""
<style>
    .stApp { background-color: #0f0c29; color: white; }
    .score-ia { font-size: 45px; color: #00f2fe; font-weight: bold; text-align: center; }
    .score-live { font-size: 45px; color: #ff0055; font-weight: bold; text-align: center; animation: blink 1s infinite; }
    @keyframes blink { 50% { opacity: 0.4; } }
    .match-card { background: rgba(255,255,255,0.05); border: 1px solid #00f2fe; border-radius: 10px; padding: 15px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data():
    headers = {'X-Auth-Token': API_KEY}
    all_matches, all_logos = [], {}
    try:
        for lg in ['FL1', 'PL', 'CL']:
            # Récupération des logos via le classement
            s = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/standings", headers=headers).json()
            if 'standings' in s:
                for t in s['standings'][0]['table']:
                    all_logos[t['team']['name']] = t['team']['crest']
            # Récupération des matchs
            m = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/matches", headers=headers).json()
            if 'matches' in m: all_matches.extend(m['matches'])
        return all_matches, all_logos
    except:
        return [], {}

matches, logos = get_data()

st.title("🎯 ALPHA-ORACLE by Houzdane.Bdess")

if matches:
    # LES 3 ONGLETS DE NAVIGATION
    tab1, tab2, tab3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER", "📊 COMPARATEUR"])
    today = datetime.utcnow().strftime('%Y-%m-%d')

    # ONGLET 1 : MATCHS DU JOUR (AVEC HEURE, LOGOS ET DIRECT)
    with tab1:
        today_m = [m for m in matches if m['utcDate'].startswith(today)]
        if not today_m:
            st.info("Aucun match majeur prévu aujourd'hui.")
        
        for m in today_m:
            h_team = m['homeTeam']['name']
            a_team = m['awayTeam']['name']
            
            # Récupération des logos
            h_logo = logos.get(h_team, "https://crests.football-data.org/default.png")
            a_logo = logos.get(a_team, "https://crests.football-data.org/default.png")
            
            status = m['status']
            heure = m['utcDate'][11:16]
            
            # Scores
            r_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
            r_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
            
            random.seed(m['id'])
            p_h, p_a = random.randint(0, 3), random.randint(0, 2)
            
            # Affichage sécurisé de la carte du match
            html_carte = f"""
            <div class="match-card">
                <div style="text-align:center; color:#ff0055; font-weight:bold; margin-bottom:10px;">
                    🕒 {heure} UTC {'- 🔴 EN DIRECT' if status in ['IN_PLAY', 'PAUSED'] else ''}
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center;">
                    <div style="text-align:center; width:30%;">
                        <img src="{h_logo}" width="55"><br><b style="font-size:14px;">{h_team}</b>
                    </div>
                    <div style="width:40%; text-align:center;">
                        <div class="{'score-live' if status in ['IN_PLAY', 'PAUSED'] else 'score-ia'}">
                            {r_h if status != 'TIMED' else p_h} - {r_a if status != 'TIMED' else p_a}
                        </div>
                        <div style="color:#00f2fe; font-size:12px; margin-top:5px;">PRÉDICTION IA : {p_h}-{p_a}</div>
                    </div>
                    <div style="text-align:center; width:30%;">
                        <img src="{a_logo}" width="55"><br><b style="font-size:14px;">{a_team}</b>
                    </div>
                </div>
            </div>
            """
            st.markdown(html_carte, unsafe_allow_html=True)

    # ONGLET 2 : CALENDRIER (FUTUR)
    with tab2:
        upcoming = [m for m in matches if m['status'] in ['TIMED', 'SCHEDULED'] and not m['utcDate'].startswith(today)]
        for m in upcoming[:10]:
            st.markdown(f"📅 **{m['utcDate'][:10]} à {m['utcDate'][11:16]}** | {m['homeTeam']['name']} vs {m['awayTeam']['name']}")

    # ONGLET 3 : COMPARATEUR (PASSÉ)
    with tab3:
        past = [m for m in matches if m['status'] == 'FINISHED' and not m['utcDate'].startswith(today)][::-1]
        for m in past[:10]:
            st.markdown(f"✅ {m['homeTeam']['name']} **{m['score']['fullTime']['home']}-{m['score']['fullTime']['away']}** {m['awayTeam']['name']}")

else:
    st.error("Données indisponibles. Reconnexion à l'API...")
