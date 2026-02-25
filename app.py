import streamlit as st
import requests
import random
from datetime import datetime

st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0f0c29; color: white; }
    .match-card { background: rgba(255,255,255,0.05); border: 1px solid #00f2fe; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    .score-live { font-size: 35px; color: #ff0055; font-weight: bold; }
    .score-finished { font-size: 35px; color: #25d366; font-weight: bold; }
    .prono-box { background: rgba(0,242,254,0.1); border-radius: 8px; padding: 10px; margin-top: 10px; border: 1px solid #00f2fe; }
    .prono-title { color: #00f2fe; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }
    .prono-value { font-size: 16px; font-weight: bold; color: white; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data():
    headers = {'X-Auth-Token': API_KEY}
    all_m, logos, stats = [], {}, {}
    try:
        for lg in ['FL1', 'PL', 'CL']:
            s_req = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/standings", headers=headers).json()
            if 'standings' in s_req:
                for t in s_req['standings'][0]['table']:
                    team_n = t['team']['name']
                    logos[team_n] = t['team']['crest']
                    stats[team_n] = {'gf': t['goalsFor']/max(1,t['playedGames']), 'ga': t['goalsAgainst']/max(1,t['playedGames']), 'rank': t['position']}
            m_req = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/matches", headers=headers).json()
            if 'matches' in m_req: all_m.extend(m_req['matches'])
        return all_m, logos, stats
    except: return [], {}, {}

matches, logos, team_stats = get_data()

def predict_double(h, a, m_id):
    # Calcul intelligent MT et FT
    random.seed(m_id)
    if h in team_stats and a in team_stats:
        # Force offensive
        pwr_h = (team_stats[h]['gf'] + team_stats[a]['ga']) / 2
        pwr_a = (team_stats[a]['gf'] + team_stats[h]['ga']) / 2
        # Score Final (FT)
        ft_h, ft_a = round(pwr_h + random.uniform(-0.5, 0.5)), round(pwr_a + random.uniform(-0.5, 0.5))
        # Score Mi-temps (MT) - Souvent 0-0, 1-0 ou 0-1
        mt_h = random.randint(0, ft_h)
        mt_a = random.randint(0, ft_a)
        return f"{mt_h}-{mt_a}", f"{ft_h}-{ft_a}"
    return "0-0", "1-1"

def draw_match(m):
    h, a = m['homeTeam']['name'], m['awayTeam']['name']
    h_logo, a_logo = logos.get(h, ""), logos.get(a, "")
    status = m['status']
    
    # Réel
    mt_real = f"{m['score']['halfTime']['home'] or 0} - {m['score']['halfTime']['away'] or 0}"
    ft_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
    ft_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
    
    # IA Prono
    p_mt, p_ft = predict_double(h, a, m['id'])
    
    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; font-size:11px; color:#888; margin-bottom:10px;">
            <span>🕒 {m['utcDate'][11:16]} UTC</span>
            <span style="background:rgba(255,255,255,0.1); padding:2px 8px; border-radius:4px;">RÉEL MT: {mt_real}</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center;">
            <div style="text-align:center; width:25%;"><img src="{h_logo}" width="45"><br><small>{h[:10]}</small></div>
            <div style="text-align:center; width:50%;">
                <div class="{'score-live' if status == 'IN_PLAY' else 'score-finished'}">
                    {ft_h if status != 'TIMED' else p_ft}
                </div>
                <div class="prono-box">
                    <div style="display:flex; justify-content:space-around;">
                        <div>
                            <div class="prono-title">Prono MT</div>
                            <div class="prono-value">{p_mt}</div>
                        </div>
                        <div style="border-left:1px solid #00f2fe; height:25px; margin-top:5px;"></div>
                        <div>
                            <div class="prono-title">Prono FT</div>
                            <div class="prono-value">{p_ft}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div style="text-align:center; width:25%;"><img src="{a_logo}" width="45"><br><small>{a[:10]}</small></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.title("🎯 ALPHA-ORACLE ELITE")
if matches:
    tabs = st.tabs(["⚽ AUJOURD'HUI", "📅 CALENDRIER", "📊 COMPARATEUR"])
    day = datetime.utcnow().strftime('%Y-%m-%d')
    with tabs[0]:
        for m in [m for m in matches if m['utcDate'].startswith(day)]: draw_match(m)
    with tabs[1]:
        for m in [m for m in matches if m['status'] == 'TIMED' and not m['utcDate'].startswith(day)][:10]: draw_match(m)
    with tabs[2]:
        for m in [m for m in matches if m['status'] == 'FINISHED' and not m['utcDate'].startswith(day)][::-1][:10]: draw_match(m)
