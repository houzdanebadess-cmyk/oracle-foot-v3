import streamlit as st
import requests
import random
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="ALPHA-ORACLE by Houzdane.Bdess", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS BOOSTÉ ---
st.markdown("""
<style>
    .stApp { background: #0f0c29; color: white; }
    .card { background: rgba(255, 255, 255, 0.05); border: 1px solid #00f2fe; border-radius: 15px; padding: 15px; margin-bottom: 15px; }
    
    /* SCORE GÉANT IA */
    .score-predict { 
        font-size: 48px; 
        color: #00f2fe; 
        font-weight: 900; 
        text-align: center; 
        text-shadow: 0 0 15px rgba(0, 242, 254, 0.6);
        line-height: 1;
    }
    
    /* SCORE LIVE GÉANT */
    .score-live { 
        font-size: 48px; 
        color: #ff0055; 
        font-weight: 900; 
        text-align: center; 
        text-shadow: 0 0 15px rgba(255, 0, 85, 0.6);
        line-height: 1;
    }

    .live-badge { background: #ff0055; color: white; padding: 3px 10px; border-radius: 5px; font-size: 11px; font-weight: bold; animation: blink 1s infinite; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: rgba(15, 12, 41, 0.95); color: #00f2fe; text-align: center; padding: 10px; font-weight: bold; border-top: 1px solid #00f2fe; z-index: 999; }
    .btn-share { background-color: #25d366 !important; color: white !important; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-size: 13px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_all_data():
    headers = {'X-Auth-Token': API_KEY}
    leagues = ['FL1', 'PL', 'CL']
    all_m, all_s = [], {}
    try:
        for lg in leagues:
            s_d = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/standings", headers=headers).json()
            m_d = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/matches", headers=headers).json()
            if 'standings' in s_d:
                for t in s_d['standings'][0]['table']:
                    all_s[t['team']['name']] = {'logo': t['team']['crest'], 'rank': t['position'], 'gf': t['goalsFor']/max(1,t['playedGames']), 'ga': t['goalsAgainst']/max(1,t['playedGames'])}
            if 'matches' in m_d:
                for match in m_d['matches']: match['lg_name'] = s_d['competition']['name']
                all_m.extend(m_d['matches'])
        return all_s, all_m
    except: return None, None

def predict_score(h, a, s):
    if h not in s or a not in s: return 1, 0
    eh, ea = (s[h]['gf']+s[a]['ga'])/2, (s[a]['gf']+s[h]['ga'])/2
    if s[h]['rank'] < s[a]['rank']: eh += 0.5
    return max(0, round(eh + random.uniform(-0.2, 0.2))), max(0, round(ea + random.uniform(-0.2, 0.2)))

stats, matches = get_all_data()

if stats and matches:
    st.title("🎯 ALPHA-ORACLE : ANALYSE ÉLITE")
    t1, t2, t3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER", "📊 COMPARATEUR"])
    today = datetime.utcnow().strftime('%Y-%m-%d')

    with t1:
        today_m = [m for m in matches if m['utcDate'].startswith(today)]
        if not today_m: st.info("Aucun match majeur aujourd'hui.")
        for m in today_m:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            p_h, p_a = predict_score(h_n, a_n, stats)
            status = m['status']
            r_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
            r_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
            msg = urllib.parse.quote(f"⚽ Prono Houzdane.Bdess : {h_n} {p_h}-{p_a} {a_n}")
            
            st.markdown(f"""<div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <span style="color:#ff0055; font-weight:bold;">🕒 {m['utcDate'][11:16]}</span>
                    { '<span class="live-badge">EN DIRECT</span>' if status in ['IN_PLAY', 'PAUSED'] else '' }
                    <a href="https://wa.me/?text={msg}" target="_blank" class="btn-share">📲 PARTAGER</a>
                </div>
                <div style="display:flex; justify-content:space-around; align-items:center;">
                    <div style="text-align:center; width:30%;"><img src="{stats.get(h_n,{}).get('logo','')}" width="60"><br><small>{h_n}</small></div>
                    <div style="text-align:center;">
                        <div style="font-size:11px; color:#aaa; letter-spacing:1px;">{ 'SCORE LIVE' if status != 'TIMED' else 'PRÉDICTION IA' }</div>
                        <div class="{ 'score-live' if status in ['IN_PLAY', 'PAUSED'] else 'score-predict' }">
                            {r_h if status != 'TIMED' else p_h} - {r_a if status != 'TIMED' else p_a}
                        </div>
                        { f'<div style="font-size:12px; color:#00f2fe; margin-top:5px; font-weight:bold;">Prono IA : {p_h}-{p_a}</div>' if status != 'TIMED' else '' }
                    </div>
                    <div style="text-align:center; width:30%;"><img src="{stats.get(a_n,{}).get('logo','')}" width="60"><br><small>{a_n}</small></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with t2:
        upcoming = [m for m in matches if m['status'] in ['TIMED', 'SCHEDULED'] and not m['utcDate'].startswith(today)]
        for m in upcoming[:10]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
            p_h, p_a = predict_score(h_n, a_n, stats)
            st.markdown(f"""<div class="card">
                <span style="color:#aaa; font-size:12px;">📅 {dt.strftime('%d/%m à %H:%M')}</span>
                <div style="display:flex; justify-content:space-around; align-items:center; margin-top:10px;">
                    <div style="text-align:center; width:30%;"><img src="{stats.get(h_n,{}).get('logo','')}" width="45"><br><small>{h_n}</small></div>
                    <div class="score-predict" style="font-size:35px;">{p_h} - {p_a}</div>
                    <div style="text-align:center; width:30%;"><img src="{stats.get(a_n,{}).get('logo','')}" width="45"><br><small>{a_n}</small></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with t3:
        past = [m for m in matches if m['status'] == 'FINISHED' and not m['utcDate'].startswith(today)][::-1]
        for m in past[:15]:
            h_n, a_n = m['homeTeam']['name'], m['awayTeam']['name']
            r_h, r_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
            st.markdown(f"""<div class="card" style="padding:10px;"><img src="{stats.get(h_n,{}).get('logo','')}" width="25"> {h_n} <b>{r_h} - {r_a}</b> {a_n} <img src="{stats.get(a_n,{}).get('logo','')}" width="25"></div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:80px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">🚀 ALPHA-ORACLE by Houzdane.Bdess</div>', unsafe_allow_html=True)
else:
    st.error("Données indisponibles.")
