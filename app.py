import streamlit as st
import requests
import random
from datetime import datetime

st.set_page_config(page_title="ALPHA-ORACLE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS SÉCURISÉ ---
st.markdown("""
<style>
    .stApp { background-color: #0f0c29; color: white; }
    .match-card { background: rgba(255,255,255,0.05); border: 1px solid #00f2fe; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    .score-ia { font-size: 38px; color: #00f2fe; font-weight: bold; line-height: 1; }
    .score-live { font-size: 38px; color: #ff0055; font-weight: bold; line-height: 1; animation: blink 1s infinite; }
    .score-finished { font-size: 38px; color: #25d366; font-weight: bold; line-height: 1; }
    @keyframes blink { 50% { opacity: 0.4; } }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data():
    headers = {'X-Auth-Token': API_KEY}
    all_matches, all_logos = [], {}
    try:
        for lg in ['FL1', 'PL', 'CL']:
            s = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/standings", headers=headers).json()
            if 'standings' in s:
                for t in s['standings'][0]['table']:
                    all_logos[t['team']['name']] = t['team']['crest']
            m = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/matches", headers=headers).json()
            if 'matches' in m: all_matches.extend(m['matches'])
        return all_matches, all_logos
    except:
        return [], {}

matches, logos = get_data()

# --- FONCTION POUR CRÉER UNE CARTE PARFAITE ---
def afficher_carte(m):
    h_team = m['homeTeam']['name']
    a_team = m['awayTeam']['name']
    h_logo = logos.get(h_team, "https://crests.football-data.org/default.png")
    a_logo = logos.get(a_team, "https://crests.football-data.org/default.png")
    
    status = m['status']
    
    # Formatage de la date et de l'heure
    dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
    date_str = dt.strftime("%d/%m/%Y")
    heure_str = dt.strftime("%H:%M")
    
    # Récupération du score réel
    r_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
    r_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
    
    # Prédiction IA fixe
    random.seed(m['id'])
    p_h, p_a = random.randint(0, 3), random.randint(0, 2)
    
    # Logique d'affichage selon l'état du match
    if status in ['IN_PLAY', 'PAUSED']:
        classe_score = "score-live"
        txt_score = f"{r_h} - {r_a}"
        titre_score = "SCORE RÉEL"
        badge = "<span style='background:#ff0055; padding:3px 8px; border-radius:5px; font-size:11px; font-weight:bold;'>🔴 EN DIRECT</span>"
    elif status == 'FINISHED':
        classe_score = "score-finished"
        txt_score = f"{r_h} - {r_a}"
        titre_score = "SCORE FINAL"
        badge = "<span style='background:#25d366; padding:3px 8px; border-radius:5px; font-size:11px; font-weight:bold;'>✅ TERMINÉ</span>"
    else:
        classe_score = "score-ia"
        txt_score = f"{p_h} - {p_a}"
        titre_score = "SCORE IA"
        badge = "<span style='background:#555; padding:3px 8px; border-radius:5px; font-size:11px; font-weight:bold;'>⏳ À VENIR</span>"
        
    html = f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; margin-bottom:12px; font-size:12px; color:#aaa; font-weight:bold;">
            <span>📅 {date_str} | 🕒 {heure_str} UTC</span>
            {badge}
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center;">
            <div style="text-align:center; width:30%;">
                <img src="{h_logo}" width="50" style="margin-bottom:8px;"><br>
                <span style="font-size:13px; font-weight:bold;">{h_team}</span>
            </div>
            <div style="width:40%; text-align:center;">
                <div style="font-size:11px; color:#aaa; margin-bottom:5px; letter-spacing:1px;">{titre_score}</div>
                <div class="{classe_score}">{txt_score}</div>
                <div style="color:#00f2fe; font-size:13px; margin-top:8px; font-weight:bold; background:rgba(0,242,254,0.1); padding:4px; border-radius:5px;">
                    PRONO IA : {p_h} - {p_a}
                </div>
            </div>
            <div style="text-align:center; width:30%;">
                <img src="{a_logo}" width="50" style="margin-bottom:8px;"><br>
                <span style="font-size:13px; font-weight:bold;">{a_team}</span>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

st.title("🎯 ALPHA-ORACLE by Houzdane.Bdess")

if matches:
    tab1, tab2, tab3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER", "📊 COMPARATEUR"])
    date_ajd = datetime.utcnow().strftime('%Y-%m-%d')

    with tab1:
        matchs_ajd = [m for m in matches if m['utcDate'].startswith(date_ajd)]
        if not matchs_ajd:
            st.info("Aucun match prévu pour aujourd'hui.")
        for m in matchs_ajd:
            afficher_carte(m)

    with tab2:
        a_venir = [m for m in matches if m['status'] in ['TIMED', 'SCHEDULED'] and not m['utcDate'].startswith(date_ajd)]
        for m in a_venir[:10]:
            afficher_carte(m)

    with tab3:
        termines = [m for m in matches if m['status'] == 'FINISHED' and not m['utcDate'].startswith(date_ajd)][::-1]
        for m in termines[:10]:
            afficher_carte(m)
else:
    st.error("Données indisponibles. L'API charge...")

