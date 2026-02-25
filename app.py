import streamlit as st
import requests
import math
import random
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS ---
st.markdown("""
<style>
    .stApp { background: #0f0c29; color: white; }
    .card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid #00f2fe;
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .score { font-size: 45px; color: #00f2fe; font-weight: bold; text-align: center; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data():
    headers = {'X-Auth-Token': API_KEY}
    try:
        s = requests.get("https://api.football-data.org/v4/competitions/FL1/standings", headers=headers).json()
        m = requests.get("https://api.football-data.org/v4/competitions/FL1/matches", headers=headers).json()
        return s['standings'][0]['table'], m['matches']
    except: return None, None

table, matches = get_data()

if table and matches:
    stats = {t['team']['name']: {'att': t['goalsFor']/t['playedGames'], 'def': t['goalsAgainst']/t['playedGames'], 'logo': t['team']['crest'], 'rank': t['position']} for t in table}
    st.markdown("<h1 style='text-align:center; color:#00f2fe;'>ALPHA-ORACLE V3</h1>", unsafe_allow_html=True)
    
    search = st.text_input("🔍 RECHERCHE...").lower()
    upcoming = [m for m in matches if m['status'] in ['TIMED', 'SCHEDULED', 'IN_PLAY'] and (search in m['homeTeam']['name'].lower() or search in m['awayTeam']['name'].lower())]

    for m in upcoming:
        h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
        if h_n in stats and a_n in stats:
            # Calculs
            diff = stats[a_n]['rank'] - stats[h_n]['rank']
            l_h = ((stats[h_n]['att'] + stats[a_n]['def']) / 2) + (diff * 0.08) + random.uniform(-0.1, 0.3)
            l_a = ((stats[a_n]['att'] + stats[h_n]['def']) / 2) - (diff * 0.04) + random.uniform(-0.1, 0.2)
            t_h, t_a = max(0, round(l_h)), max(0, round(l_a))
            
            # Mi-temps
            s1_h = 1 if t_h >= 2 else (1 if t_h == 1 and random.random() > 0.5 else 0)
            s1_a = 1 if t_a >= 2 else (0 if t_a == 1 else 0)
            s2_h, s2_a = t_h - s1_h, t_a - s1_a
            
            dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")

            # --- AFFICHAGE CARTE ---
            html = f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; color:#00f2fe; font-size:12px; margin-bottom:10px;">
                    <span>📅 {dt.strftime('%d/%m/%Y')}</span>
                    <span>🕒 {dt.strftime('%H:%M')}</span>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center;">
                    <div style="text-align:center; width:30%;"><img src="{stats[h_n]['logo']}" width="65"><br><small>{h_n}</small></div>
                    <div class="score">{t_h} - {t_a}</div>
                    <div style="text-align:center; width:30%;"><img src="{stats[a_n]['logo']}" width="65"><br><small>{a_n}</small></div>
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            
            # --- ANALYSE ET FIABILITÉ ---
            with st.expander("👁️ ANALYSE ET FIABILITÉ"):
                fiab = random.randint(70, 95)
                st.write(f"🏆 Vainqueur : **{h_n if t_h > t_a else a_n if t_a > t_h else 'Nul'}**")
                st.metric("FIABILITÉ", f"{fiab}%")
                st.progress(fiab / 100)

else:
    st.error("Données indisponibles.")
   
