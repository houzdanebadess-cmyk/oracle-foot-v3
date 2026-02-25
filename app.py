import streamlit as st
import requests
import random
import math

# --- CONFIGURATION ---
st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")
API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- DESIGN PREMIUM FOOTBALL ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .stTabs [data-baseweb="tab-list"] { background-color: #161b22; padding: 10px; border-radius: 10px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: #21262d; border-radius: 8px; color: #8b949e; }
    .stTabs [aria-selected="true"] { background-color: #238636 !important; color: white !important; }
    
    .carte-match { 
        background: #1c2128; border: 1px solid #30363d; border-radius: 15px; 
        padding: 20px; margin-bottom: 20px;
    }
    .score-reel { font-size: 35px; font-weight: 900; color: #f85149; text-align: center; }
    .tableau-oracle { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .tableau-oracle td { padding: 12px; text-align: center; border: 1px solid #333; background: rgba(0,0,0,0.1); }
    .label-ia { color: #58a6ff; font-size: 10px; text-transform: uppercase; }
    .label-reel { color: #3fb950; font-size: 10px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- MOTEUR DE CALCUL FOOTBALL (POISSON xG) ---
def moteur_football(m_id, dom, ext):
    random.seed(m_id)
    # Simulation d'une moyenne de buts réaliste pour le foot (1.3 à 1.6 par match)
    lambda_dom = 1.5 + random.uniform(-0.4, 0.4)
    lambda_ext = 1.2 + random.uniform(-0.4, 0.4)
    
    def sim_poisson(lam):
        L, k, p = math.exp(-lam), 0, 1
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    # On plafonne pour éviter tout score de basket
    f_h = min(4, sim_poisson(lambda_dom))
    f_a = min(3, sim_poisson(lambda_ext))
    
    # Mi-temps logique
    m_h = random.randint(0, math.floor(f_h/2) if f_h > 0 else 0)
    m_a = random.randint(0, math.floor(f_a/2) if f_a > 0 else 0)
    
    v_ia = dom if f_h > f_a else ext if f_a > f_h else "MATCH NUL"
    return f"{m_h}-{m_a}", f"{f_h}-{f_a}", v_ia

# --- CHARGEMENT API ---
@st.cache_data(ttl=60)
def charger_donnees():
    try:
        r = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': API_KEY}).json()
        return r.get('matches', [])
    except: return []

# --- INTERFACE ---
st.title("🎯 ALPHA-ORACLE ELITE")
matchs = charger_donnees()

if matchs:
    t1, t2, t3 = st.tabs(["⚽ DIRECT / JOUR", "📅 CALENDRIER", "📊 HISTORIQUE"])

    def card(m):
        dom, ext = m['homeTeam']['name'], m['awayTeam']['name']
        mt_ia, ft_ia, v_ia = moteur_football(m['id'], dom, ext)
        r_h, r_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
        r_mt = f"{m['score']['halfTime']['home'] or 0}-{m['score']['halfTime']['away'] or 0}"

        st.markdown(f"""
        <div class="carte-match">
            <div style="display:flex; justify-content:space-between; font-size:11px; color:#8b949e; margin-bottom:15px;">
                <span>🕒 {m['utcDate'][11:16]} | {m['competition']['name']}</span>
                <span style="color:#f85149; font-weight:bold;">{m['status']}</span>
            </div>
            
            <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
                <div style="width:35%;">
                    <img src="{m['homeTeam'].get('crest','')}" width="45"><br>
                    <b style="font-size:13px;">{dom[:15]}</b>
                </div>
                <div style="width:30%;" class="score-reel">
                    {r_h if r_h is not None else '?'} - {r_a if r_a is not None else '?'}
                </div>
                <div style="width:35%;">
                    <img src="{m['awayTeam'].get('crest','')}" width="45"><br>
                    <b style="font-size:13px;">{ext[:15]}</b>
                </div>
            </div>

            <table class="tableau-oracle">
                <tr>
                    <td><span class="label-reel">RÉEL MT</span><br><b>{r_mt}</b></td>
                    <td style="background:rgba(88,166,255,0.05);"><span class="label-ia">ORACLE MT</span><br><b>{mt_ia}</b></td>
                </tr>
                <tr>
                    <td><span class="label-reel">RÉEL FINAL</span><br><b>{r_h if r_h is not None else 0}-{r_a if r_a is not None else 0}</b></td>
                    <td style="background:rgba(88,166,255,0.05);"><span class="label-ia">ORACLE FINAL</span><br><b>{ft_ia}</b></td>
                </tr>
            </table>
            <div style="text-align:center; color:#ffca28; font-weight:bold; margin-top:15px; border-top:1px solid #333; padding-top:10px;">
                🏆 PRÉDICTION : {v_ia.upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with t1:
        for m in [m for m in matchs if m['status'] in ['IN_PLAY', 'PAUSED', 'TIMED']][:20]: card(m)
    with t2:
        for m in [m for m in matchs if m['status'] == 'SCHEDULED'][:15]: card(m)
    with t3:
        for m in [m for m in matchs if m['status'] == 'FINISHED'][::-1][:15]: card(m)
else:
    st.error("Données API indisponibles.")
