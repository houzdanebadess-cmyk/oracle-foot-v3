import streamlit as st
import requests
import random
import math

# --- CONFIGURATION ---
st.set_page_config(page_title="ALPHA-ORACLE PRO", layout="wide")
API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS (NAVIGATION & CARTES) ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #161b22; padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: #21262d; border-radius: 5px; color: white; border: none; }
    .stTabs [aria-selected="true"] { background-color: #238636 !important; border-bottom: 3px solid #3fb950; }
    
    .carte-match { 
        background: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 15px; 
        padding: 20px; 
        margin-bottom: 20px;
    }
    .score-ia { 
        font-size: 42px; 
        font-weight: 900; 
        color: #3fb950; 
        text-align: center;
        letter-spacing: 2px;
    }
    .badge-info { background: #30363d; padding: 2px 8px; border-radius: 4px; font-size: 11px; color: #8b949e; }
</style>
""", unsafe_allow_html=True)

# --- MOTEUR DE CALCUL FOOTBALL (POISSON xG) ---
def moteur_football(m_id, dom, ext):
    random.seed(m_id)
    # Puissance simplifiée (Elite)
    favoris = {"Real Madrid": 94, "Manchester City": 96, "Bayern": 91, "Paris Saint-Germain": 90, "Juventus": 88}
    p1 = next((v for k, v in favoris.items() if k.lower() in dom.lower()), 75)
    p2 = next((v for k, v in favoris.items() if k.lower() in ext.lower()), 75)

    # Lambda ajusté (Moyenne de buts par match de foot)
    diff = (p1 - p2) / 10
    l1 = max(0.6, 1.5 + (diff * 0.4))
    l2 = max(0.4, 1.2 - (diff * 0.4))

    # Simulation Loi de Poisson (Zéro basket, pur foot)
    def poisson(lam):
        L = math.exp(-lam)
        k, p = 0, 1
        while p > L:
            k += 1
            p *= random.random()
        return k - 1

    f_h, f_a = min(5, poisson(l1)), min(4, poisson(l2))
    v_ia = dom if f_h > f_a else ext if f_a > f_h else "MATCH NUL"
    return f"{f_h} - {f_a}", v_ia

# --- RÉCUPÉRATION DATA ---
@st.cache_data(ttl=60)
def charger_donnees():
    try:
        res = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': API_KEY}).json()
        return res.get('matches', [])
    except: return []

# --- INTERFACE ---
st.title("🎯 ALPHA-ORACLE ELITE")
matchs = charger_donnees()

if matchs:
    # --- TA BARRE DE NAVIGATION EST ICI ---
    tab1, tab2, tab3 = st.tabs(["🔴 DIRECT / JOUR", "📅 CALENDRIER", "📊 HISTORIQUE"])

    def afficher_carte(m):
        score_ia, winner = moteur_football(m['id'], m['homeTeam']['name'], m['awayTeam']['name'])
        r_h, r_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
        
        st.markdown(f"""
        <div class="carte-match">
            <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
                <span class="badge-info">{m['competition']['name']}</span>
                <span style="color:#f85149; font-weight:bold;">{m['status']}</span>
            </div>
            <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
                <div style="width:35%;"><b>{m['homeTeam']['name']}</b></div>
                <div style="width:30%;">
                    <div class="score-ia">{score_ia}</div>
                    <div style="font-size:11px; color:#8b949e;">RÉEL : {r_h if r_h is not None else '?'} - {r_a if r_a is not None else '?'}</div>
                </div>
                <div style="width:35%;"><b>{m['awayTeam']['name']}</b></div>
            </div>
            <div style="text-align:center; margin-top:15px; border-top:1px solid #333; padding-top:10px;">
                <span style="color:#ffca28; font-weight:bold;">PRONO : {winner.upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab1:
        # Matchs en cours ou prévus aujourd'hui
        en_cours = [m for m in matchs if m['status'] in ['IN_PLAY', 'PAUSED', 'TIMED']]
        if en_cours:
            for m in en_cours[:20]: afficher_carte(m)
        else: st.info("Aucun match en direct.")

    with tab2:
        # Matchs futurs
        avenir = [m for m in matchs if m['status'] == 'SCHEDULED']
        for m in avenir[:15]: afficher_carte(m)

    with tab3:
        # Matchs terminés
        finis = [m for m in matchs if m['status'] == 'FINISHED']
        for m in finis[::-1][:15]: afficher_carte(m)

else:
    st.error("Impossible de charger les matchs. Vérifie ta clé API.")
