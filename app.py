import streamlit as st
import requests
import random
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS (CORRIGÉ POUR AFFICHAGE PROPRE) ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .stats-header { 
        background: linear-gradient(90deg, #1f6feb, #238636); 
        padding: 20px; 
        border-radius: 15px; 
        text-align: center; 
        margin-bottom: 25px;
        border: 1px solid #30363d;
    }
    .carte-match { 
        background: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 20px; 
    }
    .score-live { font-size: 35px; font-weight: 900; color: #ff0055; text-align: center; }
    .tableau-ia { 
        width: 100%; 
        margin-top: 15px; 
        border-collapse: collapse; 
        background: rgba(255, 255, 255, 0.03); 
        border-radius: 8px;
    }
    .tableau-ia td { 
        padding: 10px; 
        text-align: center; 
        font-weight: bold; 
        border: 1px solid #30363d;
        font-size: 13px;
    }
    .label-ia { color: #58a6ff; font-size: 10px; }
    .label-reel { color: #3fb950; font-size: 10px; }
    .formation { color: #ffca28; font-size: 10px; font-weight: normal; }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES DES CLUBS (TACTIQUE & CAPACITÉ) ---
DATA_CLUBS = {
    "Real Madrid CF": {"atk": 92, "def": 88, "form": "4-3-3"},
    "Paris Saint-Germain FC": {"atk": 90, "def": 84, "form": "4-3-3"},
    "Manchester City FC": {"atk": 94, "def": 90, "form": "4-3-3"},
    "FC Bayern München": {"atk": 89, "def": 87, "form": "4-2-3-1"},
    "SL Benfica": {"atk": 81, "def": 79, "form": "4-4-2"},
    "Borussia Dortmund": {"atk": 83, "def": 80, "form": "4-2-3-1"}
}
DEFAUT = {"atk": 75, "def": 75, "form": "4-4-2"}

@st.cache_data(ttl=60)
def charger_donnees():
    headers = {'X-Auth-Token': API_KEY}
    try:
        res = requests.get("https://api.football-data.org/v4/matches", headers=headers).json()
        return res.get('matches', [])
    except: return []

def calcul_ia_oracle(m_id, dom, ext):
    random.seed(m_id)
    c1, c2 = DATA_CLUBS.get(dom, DEFAUT), DATA_CLUBS.get(ext, DEFAUT)
    
    # Formule : (Attaque Dom + Bonus Formation) vs Défense Ext
    boost = 1.15 if c1['form'] == "4-3-3" else 1.0
    exp_dom = max(0.4, ((c1['atk'] * boost) - c2['def']) / 8)
    exp_ext = max(0.3, (c2['atk'] - c1['def']) / 10)
    
    f_dom = sum([1 for _ in range(5) if random.random() < (exp_dom/4)])
    f_ext = sum([1 for _ in range(5) if random.random() < (exp_ext/4)])
    
    mt_dom = random.randint(0, round(f_dom * 0.5))
    mt_ext = random.randint(0, round(f_ext * 0.5))
    
    vainqueur_code = "HOME" if f_dom > f_ext else "AWAY" if f_ext > f_dom else "DRAW"
    return f"{mt_dom}-{mt_ext}", f"{f_dom}-{f_ext}", vainqueur_code, c1['form'], c2['form']

def afficher_match(m):
    dom, ext = m['homeTeam']['name'], m['awayTeam']['name']
    ia_mt, ia_ft, ia_v_code, f1, f2 = calcul_ia_oracle(m['id'], dom, ext)
    
    # Données réelles
    r_h = m['score']['fullTime']['home']
    r_a = m['score']['fullTime']['away']
    r_mt_h = m['score']['halfTime']['home'] if m['score']['halfTime']['home'] is not None else 0
    r_mt_a = m['score']['halfTime']['away'] if m['score']['halfTime']['away'] is not None else 0
    
    # Vérification succès
    r_v_code = "HOME" if (r_h or 0) > (r_a or 0) else "AWAY" if (r_a or 0) > (r_h or 0) else "DRAW"
    est_correct = (ia_v_code == r_v_code) if m['status'] == 'FINISHED' else None
    
    ia_v_nom = dom if ia_v_code == "HOME" else ext if ia_v_code == "AWAY" else "MATCH NUL"

    st.markdown(f"""
    <div class="carte-match">
        <div style="display:flex; justify-content:space-between; color:#8b949e; font-size:10px; margin-bottom:10px;">
            <span>🕒 {m['utcDate'][11:16]} | {m['status']}</span>
            <span>{f'<b style="color:#238636;">✅ CORRECT</b>' if est_correct else f'<b style="color:#f85149;">❌ ÉCHEC</b>' if est_correct == False else '⏳ EN ATTENTE'}</span>
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
            <tr>
                <td colspan="2" style="color:#ffca28; padding:8px;">
                    🏆 VAINQUEUR PRÉDIT : {ia_v_nom.upper()}
                </td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    return est_correct

# --- Lancement ---
st.title("🎯 ALPHA-ORACLE : ANALYSEUR PRO")
matchs = charger_donnees()

if matchs:
    # Calcul précision globale
    finis = [m for m in matchs if m['status'] == 'FINISHED']
    if finis:
        reussites = []
        for m in finis:
            _, _, ia_v, _, _ = calcul_ia_oracle(m['id'], m['homeTeam']['name'], m['awayTeam']['name'])
            r_v = "HOME" if (m['score']['fullTime']['home'] or 0) > (m['score']['fullTime']['away'] or 0) else "AWAY" if (m['score']['fullTime']['away'] or 0) > (m['score']['fullTime']['home'] or 0) else "DRAW"
            reussites.append(ia_v == r_v)
        taux = (sum(reussites) / len(reussites)) * 100
    else: taux = 0

    st.markdown(f"""
    <div class="stats-header">
        <h2 style="margin:0; color:white;">📊 PERFORMANCE DE L'IA</h2>
        <div style="font-size:30px; font-weight:900;">{taux:.1f}%</div>
        <div style="font-size:12px; opacity:0.8;">Taux de réussite sur {len(finis)} matchs terminés</div>
    </div>
    """, unsafe_allow_html=True)

    t1, t2 = st.tabs(["⚽ MATCHS DU JOUR", "📊 HISTORIQUE"])
    with t1:
        en_cours = [m for m in matchs if m['status'] != 'FINISHED']
        for m in en_cours[:25]: afficher_match(m)
    with t2:
        for m in finis[::-1][:20]: afficher_match(m)
else:
    st.error("Impossible de charger les matchs. Vérifie ta clé API.")
