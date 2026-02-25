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
    .card { background: rgba(255, 255, 255, 0.05); border: 1px solid #00f2fe; border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    .score-exact { font-size: 32px; color: #00f2fe; font-weight: bold; text-align: center; }
    .status-live { color: #ff0055; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: rgba(15, 12, 41, 0.95); color: #00f2fe;
        text-align: center; padding: 10px; font-weight: bold; border-top: 1px solid #00f2fe; z-index: 999;
    }
    .whatsapp-btn {
        background-color: #25d366; color: white !important;
        padding: 4px 10px; border-radius: 20px; text-decoration: none; font-size: 11px;
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
                        'gf': t['goalsFor'] / max(1, t['playedGames']),
                        'ga': t['goalsAgainst'] / max(1, t['playedGames'])
                    }
            if 'matches' in m:
                # On ajoute le nom de la compétition à chaque match pour l'affichage
                for match in m['matches']:
                    match['comp_name'] = s['competition']['name']
                all_matches.extend(m['matches'])
        return all_stats, all_matches
    except: return None, None

def predict_score(h_n, a_n, stats):
    if h_n not in stats or a_n not in stats: return 1, 0
    exp_h = (stats[h_n]['gf'] + stats[a_n]['ga']) / 2
    exp_a = (stats[a_n]['gf'] + stats[h_n]['ga']) / 2
    if stats[h_n]['rank'] < stats[a_n]['rank']: exp_h += 0.5
    else: exp_a += 0.5
    exp_h *= 1.15
    return max(0, round(exp_h + random.uniform(-0.3, 0.3))), max(0, round(exp_a + random.uniform(-0.3, 0.3)))

stats, all_matches = get_all_leagues_data()

if stats and all_matches:
    st.title("🎯 ALPHA-ORACLE : ANALYSE ÉLITE")
    tab1, tab2, tab3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER FUTUR", "📊 COMPARATEUR & STATS"])

    now = datetime.utcnow()
    today_str = now.strftime('%Y-%m-%d')

    with tab1:
        st.subheader("🔥 Toute l'actualité d'aujourd'hui")
        # Filtre : Matchs dont la date est AUJOURD'HUI (peu importe s'ils sont finis ou pas)
        today_matches = [m for m in all_matches if m['utcDate'].startswith(today_str)]
        
        if not today_matches:
            st.info("Aucun match de Ligue 1, PL ou CL aujourd'hui.")
        
        for m in today_matches:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            p_h, p_a = predict_score(h_n, a_n, stats)
            
            # Gestion visuelle du statut
            status = m['status']
            score_reel_h = m['score']['fullTime']['home']
            score_reel_a = m['score']['fullTime']['away']
            
            if status == 'FINISHED':
                badge = f"✅ TERMINÉ ({score_reel_h}-{score_reel_a})"
                color = "#888"
            elif status == 'IN_PLAY':
                badge = f"🔴 EN DIRECT ({score_reel_h}-{score_reel_a})"
                color = "#ff0055"
            else:
                badge = f"⏰ À VENIR : {dt.strftime('%H:%M')}"
                color = "#00f2fe"

            st.markdown(f"""<div class="card" style="border-left: 5px solid {color};">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:12px; color:{color}; font-weight:bold;">{badge}</span>
                    <small style="color:#aaa;">{m.get('comp_name', '')}</small>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px;">
                    <div style="text-align:center; width:30%;"><img src="{stats.get(h_n,{}).get('logo','')}" width="40"><br><small>{h_n}</small></div>
                    <div style="text-align:center;">
                        <div style="font-size:10px; color:#00f2fe;">IA PRÉDIT</div>
                        <div class="score-exact">{p_h} - {p_a}</div>
                    </div>
                    <div style="text-align:center; width:30%;"><img src="{stats.get(a_n,{}).get('logo','')}" width="40"><br><small>{a_n}</small></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab2: # (Code Calendrier Futur - identique au précédent avec logos)
        upcoming = [m for m in all_matches if m['status'] in ['TIMED', 'SCHEDULED'] and not m['utcDate'].startswith(today_str)]
        for m in upcoming[:15]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            p_h, p_a = predict_score(h_n, a_n, stats)
            st.markdown(f"""<div class="card">
                <div style="font-size:11px; color:#aaa; margin-bottom:10px;">📅 Match le {dt.strftime('%d/%m à %H:%M')}</div>
                <div style="display:flex; justify-content:space-around; align-items:center;">
                    <div style="text-align:center; width:30%;"><img src="{stats.get(h_n,{}).get('logo','')}" width="40"><br><small>{h_n}</small></div>
                    <div style="text-align:center;"><div style="font-size:22px; font-weight:bold; color:#00f2fe;">{p_h} - {p_a}</div></div>
                    <div style="text-align:center; width:30%;"><img src="{stats.get(a_n,{}).get('logo','')}" width="40"><br><small>{a_n}</small></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab3: # (Code Comparateur - identique avec logos)
        past = [m for m in all_matches if m['status'] == 'FINISHED' and not m['utcDate'].startswith(today_str)][::-1]
        st.markdown(f"""<div class="stats-banner">📊 HISTORIQUE DES MATCHS TERMINÉS</div>""", unsafe_allow_html=True)
        for m in past[:15]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            real_h, real_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
            st.markdown(f"""<div class="card" style="border-color: #333;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:10px;">
                        <img src="{stats.get(h_n,{}).get('logo','')}" width="25">
                        <span>{h_n} <b>{real_h} - {real_a}</b> {a_n}</span>
                        <img src="{stats.get(a_n,{}).get('logo','')}" width="25">
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="footer">🚀 Codé avec Houzdane.Bdess</div>""", unsafe_allow_html=True)
else:
    st.error("Données indisponibles.")
