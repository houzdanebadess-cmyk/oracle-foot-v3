import streamlit as st
import requests
import random
from datetime import datetime

st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS AMÉLIORÉ ---
st.markdown("""
<style>
    .stApp { background-color: #0f0c29; color: white; }
    .match-card { background: rgba(255,255,255,0.05); border: 1px solid #00f2fe; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    .score-live { font-size: 40px; color: #ff0055; font-weight: bold; text-shadow: 0 0 10px #ff0055; }
    .score-finished { font-size: 40px; color: #25d366; font-weight: bold; }
    .score-ia { font-size: 40px; color: #00f2fe; font-weight: bold; }
    .half-time-badge { font-size: 12px; color: #aaa; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data():
    headers = {'X-Auth-Token': API_KEY}
    all_m, logos, stats = [], {}, {}
    try:
        for lg in ['FL1', 'PL', 'CL']:
            # Récupération des statistiques pour une IA plus intelligente
            s_req = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/standings", headers=headers).json()
            if 'standings' in s_req:
                for t in s_req['standings'][0]['table']:
                    team_n = t['team']['name']
                    logos[team_n] = t['team']['crest']
                    # On calcule la moyenne de buts pour prédire le futur
                    stats[team_n] = {
                        'gf': t['goalsFor'] / max(1, t['playedGames']), 
                        'ga': t['goalsAgainst'] / max(1, t['playedGames']), 
                        'rank': t['position']
                    }
            m_req = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/matches", headers=headers).json()
            if 'matches' in m_req: all_m.extend(m_req['matches'])
        return all_m, logos, stats
    except: return [], {}, {}

matches, logos, team_stats = get_data()

def predict_smart(h, a, m_id):
    # Algorithme basé sur la puissance offensive et défensive
    if h in team_stats and a in team_stats:
        exp_h = (team_stats[h]['gf'] + team_stats[a]['ga']) / 2
        exp_a = (team_stats[a]['gf'] + team_stats[h]['ga']) / 2
        # Bonus pour l'équipe mieux classée
        if team_stats[h]['rank'] < team_stats[a]['rank']: exp_h += 0.3
        else: exp_a += 0.3
        return round(exp_h), round(exp_a)
    # Si pas de stats, on utilise l'ID pour une prédiction fixe
    random.seed(m_id)
    return random.randint(0, 2), random.randint(0, 1)

def draw_match(m):
    h, a = m['homeTeam']['name'], m['awayTeam']['name']
    h_logo, a_logo = logos.get(h, ""), logos.get(a, "")
    status = m['status']
    
    # Récupération des scores Mi-temps (HT) et Fin de match (FT)
    mt_h = m['score']['halfTime']['home'] if m['score']['halfTime']['home'] is not None else 0
    mt_a = m['score']['halfTime']['away'] if m['score']['halfTime']['away'] is not None else 0
    ft_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
    ft_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
    
    p_h, p_a = predict_smart(h, a, m['id'])
    
    # Choix du style selon le statut
    if status in ['IN_PLAY', 'PAUSED']:
        score_class, score_txt, label = "score-live", f"{ft_h} - {ft_a}", "🔴 EN DIRECT"
    elif status == 'FINISHED':
        score_class, score_txt, label = "score-finished", f"{ft_h} - {ft_a}", "✅ TERMINÉ"
    else:
        score_class, score_txt, label = "score-ia", f"{p_h} - {p_a}", "⏳ À VENIR"

    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:12px; color:#888;">📅 {m['utcDate'][:10]} | 🕒 {m['utcDate'][11:16]} UTC</span>
            <span class="half-time-badge">MI-TEMPS: {mt_h} - {mt_a}</span>
            <span style="font-size:11px; font-weight:bold; color:{'#ff0055' if 'DIRECT' in label else '#aaa'};">{label}</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center;">
            <div style="text-align:center; width:30%;"><img src="{h_logo}" width="50"><br><small>{h}</small></div>
            <div style="text-align:center; width:40%;">
                <div class="{score_class}">{score_txt}</div>
                <div style="color:#00f2fe; font-size:13px; font-weight:bold; margin-top:8px; background:rgba(0,242,254,0.1); padding:4px; border-radius:5px;">
                    PRONO IA : {p_h} - {p_a}
                </div>
            </div>
            <div style="text-align:center; width:30%;"><img src="{a_logo}" width="50"><br><small>{a}</small></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.title("🎯 ALPHA-ORACLE ELITE")

if matches:
    t1, t2, t3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER", "📊 COMPARATEUR"])
    today = datetime.utcnow().strftime('%Y-%m-%d')
    
    with t1:
        for m in [m for m in matches if m['utcDate'].startswith(today)]: draw_match(m)
    with t2:
        for m in [m for m in matches if m['status'] in ['TIMED', 'SCHEDULED'] and not m['utcDate'].startswith(today)][:15]: draw_match(m)
    with t3:
        for m in [m for m in matches if m['status'] == 'FINISHED' and not m['utcDate'].startswith(today)][::-1][:15]: draw_match(m)
else:
    st.error("Données indisponibles. Vérifie ta clé API.")
