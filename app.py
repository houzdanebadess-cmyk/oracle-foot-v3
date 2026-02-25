import streamlit as st
import requests
import random
import math

# --- CONFIGURATION ---
st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")
API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .carte-match { background: #1c2128; border: 1px solid #444c56; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
    .score-live { font-size: 38px; font-weight: 900; color: #f85149; text-align: center; }
    .badge-formation { background: #30363d; color: #ffca28; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: bold; }
    .tableau-oracle { width: 100%; margin-top: 15px; border-collapse: collapse; }
    .tableau-oracle td { padding: 12px; text-align: center; border: 1px solid #30363d; font-weight: bold; }
    .label-ia { color: #58a6ff; font-size: 11px; }
    .label-reel { color: #3fb950; font-size: 11px; }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES EXPERT (PUISSANCE & CLASSEMENT) ---
DB_CLUBS = {
    "Manchester City": {"rank": 1, "atk": 95, "def": 92, "form": "3-2-4-1"},
    "Real Madrid": {"rank": 2, "atk": 94, "def": 90, "form": "4-3-1-2"},
    "Juventus": {"rank": 12, "atk": 85, "def": 88, "form": "3-5-2"},
    "Liverpool": {"rank": 3, "atk": 91, "def": 88, "form": "4-3-3"},
    "Paris Saint-Germain": {"rank": 8, "atk": 89, "def": 84, "form": "4-3-3"},
    "Bayern": {"rank": 4, "atk": 90, "def": 86, "form": "4-2-3-1"},
    "Flamengo": {"rank": 15, "atk": 82, "def": 78, "form": "4-2-3-1"},
    "Galatasaray": {"rank": 30, "atk": 80, "def": 75, "form": "4-2-3-1"},
    "Benfica": {"rank": 20, "atk": 82, "def": 80, "form": "4-2-3-1"}
}
DEFAUT = {"rank": 100, "atk": 72, "def": 72, "form": "4-4-2"}

def trouver_data(nom):
    for k, v in DB_CLUBS.items():
        if k.lower() in nom.lower(): return v
    return DEFAUT

def calcul_expert(m_id, dom, ext):
    random.seed(m_id)
    d1, d2 = trouver_data(dom), trouver_data(ext)
    
    # FORMULE DE POISSON : (Attaque A / Défense B) * Coefficient de Rang
    # Plus le rank est petit (ex: 1), plus l'équipe est forte
    coeff_dom = 1.2 if d1['rank'] < d2['rank'] else 0.8
    coeff_ext = 1.2 if d2['rank'] < d1['rank'] else 0.8
    
    exp_h = (d1['atk'] / d2['def']) * coeff_dom + random.uniform(-0.5, 0.5)
    exp_a = (d2['atk'] / d1['def']) * coeff_ext + random.uniform(-0.5, 0.5)
    
    final_h, final_a = max(0, round(exp_h)), max(0, round(exp_a))
    mt_h, mt_a = random.randint(0, final_h), random.randint(0, final_a)
    
    vainqueur = dom if final_h > final_a else ext if final_a > final_h else "MATCH NUL"
    return f"{mt_h}-{mt_a}", f"{final_h}-{final_a}", vainqueur, d1['form'], d2['form']

@st.cache_data(ttl=60)
def charger_matchs():
    headers = {'X-Auth-Token': API_KEY}
    try:
        url = "https://api.football-data.org/v4/matches"
        return requests.get(url, headers=headers).json().get('matches', [])
    except: return []

def afficher_carte(m):
    dom, ext = m['homeTeam']['name'], m['awayTeam']['name']
    mt_ia, ft_ia, v_ia, f1, f2 = calcul_expert(m['id'], dom, ext)
    
    r_h, r_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
    r_mt = f"{m['score']['halfTime']['home'] or 0}-{m['score']['halfTime']['away'] or 0}"
    
    st.markdown(f"""
    <div class="carte-match">
        <div style="display:flex; justify-content:space-between; font-size:10px; color:#8b949e; margin-bottom:15px;">
            <span>🕒 {m['utcDate'][11:16]} | {m['competition']['name']}</span>
            <span style="color:#f85149; font-weight:bold;">{m['status']}</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
            <div style="width:35%;">
                <img src="{m['homeTeam'].get('crest','')}" width="45"><br>
                <b style="font-size:13px;">{dom[:14]}</b><br><span class="badge-formation">{f1}</span>
            </div>
            <div style="width:30%;" class="score-live">{r_h if r_h is not None else '?'} - {r_a if r_a is not None else '?'}</div>
            <div style="width:35%;">
                <img src="{m['awayTeam'].get('crest','')}" width="45"><br>
                <b style="font-size:13px;">{ext[:14]}</b><br><span class="badge-formation">{f2}</span>
            </div>
        </div>
        <table class="tableau-oracle">
            <tr>
                <td><span class="label-reel">RÉEL MT</span><br>{r_mt}</td>
                <td style="background: rgba(88,166,255,0.1);"><span class="label-ia">ORACLE MT</span><br>{mt_ia}</td>
            </tr>
            <tr>
                <td><span class="label-reel">RÉEL FINAL</span><br>{r_h if r_h is not None else 0}-{r_a if r_a is not None else 0}</td>
                <td style="background: rgba(88,166,255,0.1);"><span class="label-ia">ORACLE FINAL</span><br>{ft_ia}</td>
            </tr>
            <tr><td colspan="2" style="color:#ffca28; border-top:1px solid #ffca28; padding:10px;">🎯 PRONO : {v_ia.upper()}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# --- INTERFACE ---
st.title("🎯 ALPHA-ORACLE ELITE")
matchs = charger_matchs()

if matchs:
    tab1, tab2, tab3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER", "📊 HISTORIQUE"])
    with tab1:
        en_direct = [m for m in matchs if m['status'] in ['IN_PLAY', 'PAUSED']]
        if en_direct:
            for m in en_direct: afficher_carte(m)
        else: st.info("Pas de matchs en direct.")
    with tab2:
        avenir = [m for m in matchs if m['status'] == 'TIMED']
        for m in avenir[:15]: afficher_carte(m)
    with tab3:
        finis = [m for m in matchs if m['status'] == 'FINISHED']
        for m in finis[::-1][:15]: afficher_carte(m)
else:
    st.error("Erreur API ou aucun match.")
