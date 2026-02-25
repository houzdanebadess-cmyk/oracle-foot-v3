import streamlit as st
import requests
import random
import math
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .nav-header { background: #161b22; padding: 10px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #30363d; }
    .carte-match { background: #1c2128; border: 1px solid #444c56; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    .score-live { font-size: 38px; font-weight: 900; color: #f85149; text-align: center; text-shadow: 0px 0px 10px rgba(248,81,73,0.3); }
    .badge-formation { background: #30363d; color: #ffca28; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: bold; }
    .tableau-oracle { width: 100%; margin-top: 15px; border-collapse: collapse; }
    .tableau-oracle td { padding: 12px; text-align: center; border: 1px solid #30363d; font-weight: bold; }
    .label-ia { color: #58a6ff; font-size: 11px; text-transform: uppercase; }
    .label-reel { color: #3fb950; font-size: 11px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES PUISSANCE (CLASSEMENT & FORMATION) ---
# Simule le classement mondial (Rank) et la force d'attaque
DB_CLUBS = {
    "Manchester City": {"rank": 1, "atk": 95, "def": 92, "form": "3-2-4-1"},
    "Real Madrid": {"rank": 2, "atk": 93, "def": 90, "form": "4-3-1-2"},
    "Liverpool": {"rank": 3, "atk": 91, "def": 88, "form": "4-3-3"},
    "Bayern": {"rank": 4, "atk": 90, "def": 86, "form": "4-2-3-1"},
    "Paris Saint-Germain": {"atk": 89, "def": 83, "rank": 7, "form": "4-3-3"},
    "Flamengo": {"rank": 15, "atk": 82, "def": 78, "form": "4-2-3-1"},
    "Bahia": {"rank": 45, "atk": 74, "def": 72, "form": "4-3-3"},
}
DEFAUT = {"rank": 100, "atk": 70, "def": 70, "form": "4-4-2"}

def loi_poisson(lambda_val, k):
    """Calcule la probabilité de marquer k buts selon la formule de Poisson"""
    return (math.exp(-lambda_val) * pow(lambda_val, k)) / math.factorial(k)

def predire_score_expert(m_id, dom_name, ext_name):
    random.seed(m_id)
    # 1. Récupération des données selon le nom
    d1 = next((v for k, v in DB_CLUBS.items() if k.lower() in dom_name.lower()), DEFAUT)
    d2 = next((v for k, v in DB_CLUBS.items() if k.lower() in ext_name.lower()), DEFAUT)
    
    # 2. Facteurs Terrain et Classement
    # Bonus domicile (+10% attaque), Malus fatigue extérieur
    lambda_dom = (d1['atk'] / d2['def']) * (1.1 if d1['rank'] < d2['rank'] else 0.9)
    lambda_ext = (d2['atk'] / d1['def']) * (0.8 if d2['rank'] > d1['rank'] else 1.0)

    # 3. Simulation des buts (Loi de Poisson)
    def tirer_buts(l):
        probs = [loi_poisson(l, i) for i in range(5)]
        return probs.index(max(probs))

    final_h, final_a = tirer_buts(lambda_dom), tirer_buts(lambda_ext)
    mt_h, mt_a = random.randint(0, final_h), random.randint(0, final_a)
    
    vainqueur = dom_name if final_h > final_a else ext_name if final_a > final_h else "MATCH NUL"
    return f"{mt_h}-{mt_a}", f"{final_h}-{final_a}", vainqueur, d1['form'], d2['form']

@st.cache_data(ttl=60)
def charger_matchs():
    headers = {'X-Auth-Token': API_KEY}
    try:
        return requests.get("https://api.football-data.org/v4/matches", headers=headers).json().get('matches', [])
    except: return []

def card(m):
    dom, ext = m['homeTeam']['name'], m['awayTeam']['name']
    mt_ia, ft_ia, v_ia, f1, f2 = predire_score_expert(m['id'], dom, ext)
    
    r_h, r_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
    r_mt = f"{m['score']['halfTime']['home'] or 0}-{m['score']['halfTime']['away'] or 0}"
    
    st.markdown(f"""
    <div class="carte-match">
        <div style="display:flex; justify-content:space-between; font-size:11px; color:#8b949e; margin-bottom:15px;">
            <span>🕒 {m['utcDate'][11:16]} | {m['competition']['name']}</span>
            <span style="color:#f85149;">{m['status']}</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
            <div style="width:30%;">
                <img src="{m['homeTeam'].get('crest','')}" width="45"><br>
                <b>{dom[:12]}</b><br><span class="badge-formation">{f1}</span>
            </div>
            <div style="width:40%;" class="score-live">{r_h if r_h is not None else '?'} - {r_a if r_a is not None else '?'}</div>
            <div style="width:30%;">
                <img src="{m['awayTeam'].get('crest','')}" width="45"><br>
                <b>{ext[:12]}</b><br><span class="badge-formation">{f2}</span>
            </div>
        </div>
        <table class="tableau-oracle">
            <tr>
                <td><span class="label-reel">RÉEL MT</span><br>{r_mt}</td>
                <td style="background: rgba(88,166,255,0.1); border-left: 2px solid #58a6ff;">
                    <span class="label-ia">ORACLE MT</span><br>{mt_ia}
                </td>
            </tr>
            <tr>
                <td><span class="label-reel">RÉEL FINAL</span><br>{r_h if r_h is not None else 0}-{r_a if r_a is not None else 0}</td>
                <td style="background: rgba(88,166,255,0.1); border-left: 2px solid #58a6ff;">
                    <span class="label-ia">ORACLE FINAL</span><br>{ft_ia}
                </td>
            </tr>
            <tr>
                <td colspan="2" style="color:#ffca28; border-top: 1px solid #ffca28; padding:10px;">
                    🎯 PRONO : {v_ia.upper()}
                </td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# --- NAVIGATION ET INTERFACE ---
st.title("🎯 ALPHA-ORACLE ELITE")
matchs = charger_matchs()

if matchs:
    # On recrée les onglets que tu avais perdus
    tab1, tab2, tab3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER", "📊 HISTORIQUE"])
    
    with tab1:
        en_direct = [m for m in matchs if m['status'] in ['IN_PLAY', 'PAUSED']]
        if en_direct:
            st.subheader("🔴 MATCHS EN DIRECT")
            for m in en_direct: card(m)
        else:
            st.info("Aucun match en direct. Consultez le calendrier.")

    with tab2:
        avenir = [m for m in matchs if m['status'] == 'TIMED']
        for m in avenir[:15]: card(m)

    with tab3:
        finis = [m for m in matchs if m['status'] == 'FINISHED']
        for m in finis[::-1][:15]: card(m)
else:
    st.warning("Connexion à l'API impossible ou aucun match aujourd'hui.")
