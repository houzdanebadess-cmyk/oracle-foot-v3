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
    .card { background: rgba(255, 255, 255, 0.05); border: 1px solid #00f2fe; border-radius: 15px; padding: 15px; margin-bottom: 15px; position: relative; }
    .score-exact { font-size: 32px; color: #00f2fe; font-weight: bold; text-align: center; }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: rgba(15, 12, 41, 0.95); color: #00f2fe;
        text-align: center; padding: 10px; font-weight: bold; border-top: 1px solid #00f2fe; z-index: 999;
    }
    /* Style du bouton WhatsApp */
    .btn-share {
        background-color: #25d366 !important;
        color: white !important;
        padding: 8px 15px !important;
        border-radius: 25px !important;
        text-decoration: none !important;
        font-weight: bold !important;
        font-size: 14px !important;
        display: inline-block !important;
        margin-bottom: 10px !important;
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
                        'gf': (t['goalsFor'] / max(1, t['playedGames'])),
                        'ga': (t['goalsAgainst'] / max(1, t['playedGames']))
                    }
            if 'matches' in m: all_matches.extend(m['matches'])
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
    st.title("🎯 ALPHA-ORACLE by Houzdane.Bdess")
    tab1, tab2, tab3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER FUTUR", "📊 COMPARATEUR"])

    now = datetime.utcnow()
    today_str = now.strftime('%Y-%m-%d')

    # --- ONGLET 1 : JOUR J ---
    with tab1:
        today_matches = [m for m in all_matches if m['utcDate'].startswith(today_str)]
        if not today_matches: st.info("Pas de matchs majeurs aujourd'hui.")
        for m in today_matches:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            p_h, p_a = predict_score(h_n, a_n, stats)
            
            text_whatsapp = f"⚽ Prono Houzdane.Bdess : {h_n} {p_h}-{p_a} {a_n} ! Analysé par ALPHA-ORACLE"
            link_whatsapp = f"https://wa.me/?text={urllib.parse.quote(text_whatsapp)}"

            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#ff0055; font-weight:bold;">🕒 Aujourd'hui {dt.strftime('%H:%M')}</span>
                    <a href="{link_whatsapp}" target="_blank" class="btn-share">📲 PARTAGER PRONO</a>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px;">
                    <div style="text-align:center;"><img src="{stats.get(h_n,{}).get('logo','')}" width="45"><br>{h_n}</div>
                    <div class="score-exact">{p_h} - {p_a}</div>
                    <div style="text-align:center;"><img src="{stats.get(a_n,{}).get('logo','')}" width="45"><br>{a_n}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- ONGLET 2 : FUTUR ---
    with tab2:
        upcoming = [m for m in all_matches if m['status'] in ['TIMED', 'SCHEDULED'] and not m['utcDate'].startswith(today_str)]
        for m in upcoming[:10]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            p_h, p_a = predict_score(h_n, a_n, stats)
            
            link_wa = f"https://wa.me/?text={urllib.parse.quote(f'⚽ {h_n} vs {a_n} : {p_h}-{p_a} (IA Houzdane)')}"

            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between;">
                    <span style="color:#aaa;">📅 {dt.strftime('%d/%m à %H:%M')}</span>
                    <a href="{link_wa}" target="_blank" class="btn-share">📲 PARTAGER</a>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center; margin-top:5px;">
                    <div style="text-align:center;"><img src="{stats.get(h_n,{}).get('logo','')}" width="40"><br><small>{h_n}</small></div>
                    <div style="font-size:24px; font-weight:bold; color:#00f2fe;">{p_h} - {p_a}</div>
                    <div style="text-align:center;"><img src="{stats.get(a_n,{}).get('logo','')}" width="40"><br><small>{a_n}</small></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- ONGLET 3 : COMPARATEUR ---
    with tab3:
        past = [m for m in all_matches if m['status'] == 'FINISHED'][::-1]
        for m in past[:15]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            r_h, r_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
            st.markdown(f"""
            <div class="card" style="border-color:#333;">
                <div style="display:flex; align-items:center; gap:15px;">
                    <img src="{stats.get(h_n,{}).get('logo','')}" width="25">
                    <span>{h_n} <b>{r_h} - {r_a}</b> {a_n}</span>
                    <img src="{stats.get(a_n,{}).get('logo','')}" width="25">
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("""<div class="footer">🚀 Codé avec Houzdane.Bdess</div>""", unsafe_allow_html=True)
else:
    st.error("Données indisponibles. Attends 1 minute.")nnées indisponibles.")
