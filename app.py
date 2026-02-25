import streamlit as st
import requests
import random
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS (PROPRE) ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .stats-header { background: linear-gradient(90deg, #1f6feb, #238636); padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px; }
    .carte-match { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 15px; margin-bottom: 20px; }
    .score-live { font-size: 35px; font-weight: 900; color: #ff0055; text-align: center; }
    .tableau-ia { width: 100%; margin-top: 15px; border-collapse: collapse; background: rgba(255, 255, 255, 0.03); }
    .tableau-ia td { padding: 10px; text-align: center; font-weight: bold; border: 1px solid #30363d; font-size: 13px; }
    .label-ia { color: #58a6ff; font-size: 10px; }
    .label-reel { color: #3fb950; font-size: 10px; }
    .formation { color: #ffca28; font-size: 10px; }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES ÉLARGIE (Pour éviter le 4-4-2 par défaut) ---
DATA_CLUBS = {
    "Real Madrid": {"atk": 92, "def": 88, "form": "4-3-3"},
    "Paris Saint-Germain": {"atk": 90, "def": 84, "form": "4-3-3"},
    "Manchester City": {"atk": 94, "def": 90, "form": "3-2-4-1"},
    "Bayern": {"atk": 89, "def": 87, "form": "4-2-3-1"},
    "Millwall": {"atk": 74, "def": 72, "form": "4-2-3-1"},
    "Birmingham": {"atk": 72, "def": 70, "form": "3-5-2"},
    "Sheffield Utd": {"atk": 75, "def": 73, "form": "3-4-2-1"},
    "Coventry": {"atk": 76, "def": 74, "form": "4-2-3-1"},
    "Norwich": {"atk": 77, "def": 75, "form": "4-3-3"},
    "Liverpool": {"atk": 91, "def": 86, "form": "4-3-3"},
    "Monaco": {"atk": 83, "def": 78, "form": "4-4-2"}
}

def trouver_equipe(nom):
    # Cherche si une partie du nom existe dans notre base
    for cle in DATA_CLUBS:
        if cle.lower() in nom.lower():
            return DATA_CLUBS[cle]
    return {"atk": 70, "def": 70, "form": "4-4-2"} # Vraie base par défaut pour éviter 0-0

@st.cache_data(ttl=60)
def charger_donnees():
    headers = {'X-Auth-Token': API_KEY}
    try:
        res = requests.get("https://api.football-data.org/v4/matches", headers=headers).json()
        return res.get('matches', [])
    except: return []

def calcul_ia_oracle(m_id, dom, ext):
    random.seed(m_id)
    c1 = trouver_equipe(dom)
    c2 = trouver_equipe(ext)
    
    # Calcul des buts attendus (xG)
    # On ajoute un petit bonus aléatoire pour ne jamais avoir 0-0 tout le temps
    exp_dom = max(0.8, (c1['atk'] - c2['def']) / 5 + random.uniform(0, 1))
    exp_ext = max(0.5, (c2['atk'] - c1['def']) / 7 + random.uniform(0, 0.5))
    
    f_dom = round(exp_dom)
    f_ext = round(exp_ext)
    
    mt_dom = random.randint(0, f_dom)
    mt_ext = random.randint(0, f_ext)
    
    v_code = "HOME" if f_dom > f_ext else "AWAY" if f_ext > f_dom else "DRAW"
    return f"{mt_dom}-{mt_ext}", f"{f_dom}-{f_ext}", v_code, c1['form'], c2['form']

def afficher_match(m):
    dom, ext = m['homeTeam']['name'], m['awayTeam']['name']
    ia_mt, ia_ft, ia_v_code, f1, f2 = calcul_ia_oracle(m['id'], dom, ext)
    
    r_h, r_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
    r_mt_h = m['score']['halfTime']['home'] if m['score']['halfTime']['home'] is not None else 0
    r_mt_a = m['score']['halfTime']['away'] if m['score']['halfTime']['away'] is not None else 0
    
    ia_v_nom = dom if ia_v_code == "HOME" else ext if ia_v_code == "AWAY" else "MATCH NUL"

    st.markdown(f"""
    <div class="carte-match">
        <div style="display:flex; justify-content:space-between; color:#8b949e; font-size:10px; margin-bottom:10px;">
            <span>🕒 {m['utcDate'][11:16]} | {m['status']}</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
            <div style="width:30%;">
                <img src="{m['homeTeam'].get('crest','')}" width="40"><br>
                <div style="font-size:12px; font-weight:bold;">{dom[:12]}</div>
                <div class="formation">{f1}</div>
            </div>
            <div style="width:40%;" class="score-live">{r_h if r_h is not None else '?'} - {r_a if r_a is not None else '?'}</div>
            <div style="width:30%;">
                <img src="{m['awayTeam'].get('crest','')}" width="40"><br>
                <div style="font-size:12px; font-weight:bold;">{ext[:12]}</div>
                <div class="formation">{f2}</div>
            </div>
        </div>
        <table class="tableau-ia">
            <tr>
                <td><span class="label-reel">RÉEL MT</span><br>{r_mt_h}-{r_mt_a}</td>
                <td><span class="label-ia">ORACLE MT</span><br>{ia_mt}</td>
            </tr>
            <tr>
                <td><span class="label-reel">RÉEL FINAL</span><br>{r_h if r_h is not None else 0}-{r_a if r_a is not None else 0}</td>
                <td><span class="label-ia">ORACLE FINAL</span><br>{ia_ft}</td>
            </tr>
            <tr><td colspan="2" style="color:#ffca28; padding:8px;">🏆 PRÉDICTION : {ia_v_nom.upper()}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# --- APP ---
st.title("🎯 ALPHA-ORACLE ELITE")
matchs = charger_donnees()
if matchs:
    t1, t2 = st.tabs(["⚽ MATCHS DU JOUR", "📊 HISTORIQUE"])
    with t1:
        for m in [m for m in matchs if m['status'] != 'FINISHED'][:25]:
            afficher_match(m)
    with t2:
        for m in [m for m in matchs if m['status'] == 'FINISHED'][::-1][:20]:
            afficher_match(m)
