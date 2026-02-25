import streamlit as st
import requests
import random
from datetime import datetime

st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- DESIGN PROFESSIONNEL ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .carte-match { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 15px; margin-bottom: 20px; }
    .score-live { font-size: 40px; font-weight: 900; color: #f85149; text-align: center; }
    .tableau-ia { width: 100%; margin-top: 15px; border-collapse: collapse; background: rgba(88, 166, 255, 0.05); border-radius: 8px; }
    .tableau-ia td { padding: 10px; text-align: center; font-weight: bold; border-bottom: 1px solid #30363d; font-size: 14px; }
    .label-ia { color: #58a6ff; font-size: 11px; text-transform: uppercase; }
    .label-reel { color: #3fb950; font-size: 11px; text-transform: uppercase; }
    .vainqueur-box { color: #ffca28; font-size: 16px; border-top: 2px solid #ffca28; padding-top: 5px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def charger_matchs_universels():
    headers = {'X-Auth-Token': API_KEY}
    url = "https://api.football-data.org/v4/matches"
    try:
        res = requests.get(url, headers=headers).json()
        return res.get('matches', [])
    except:
        return []

tous_matchs = charger_matchs_universels()

def calcul_ia_complet(m_id, dom_name, ext_name):
    random.seed(m_id)
    # Simulation de puissance
    score_h = random.randint(0, 3)
    score_a = random.randint(0, 2)
    mt_h = random.randint(0, score_h)
    mt_a = random.randint(0, score_a)
    
    # Déterminer le vainqueur pour le tableau
    if score_h > score_a:
        vainqueur = dom_name
    elif score_a > score_h:
        vainqueur = ext_name
    else:
        vainqueur = "MATCH NUL"
        
    return f"{mt_h}-{mt_a}", f"{score_h}-{score_a}", vainqueur

def afficher_match_oracle(m):
    dom = m['homeTeam']['name']
    ext = m['awayTeam']['name']
    logo_dom = m['homeTeam'].get('crest', '')
    logo_ext = m['awayTeam'].get('crest', '')
    statut = m['status']
    
    # Scores Réels
    r_mt = f"{m['score']['halfTime']['home'] or 0}-{m['score']['halfTime']['away'] or 0}"
    r_ft_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
    r_ft_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
    
    # Pronos IA
    ia_mt, ia_ft, ia_vainqueur = calcul_ia_complet(m['id'], dom, ext)
    
    st.markdown(f"""
    <div class="carte-match">
        <div style="display:flex; justify-content:space-between; color:#8b949e; font-size:12px; margin-bottom:10px;">
            <span>🕒 {m['utcDate'][11:16]} UTC | {m['competition']['name']}</span>
            <span style="color:#f85149; font-weight:bold;">{statut}</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
            <div style="width:30%;"><img src="{logo_dom}" width="45"><br><small>{dom[:15]}</small></div>
            <div style="width:40%;"><div class="score-live">{r_ft_h if statut != 'TIMED' else '?'} - {r_ft_a if statut != 'TIMED' else '?'}</div></div>
            <div style="width:30%;"><img src="{logo_ext}" width="45"><br><small>{ext[:15]}</small></div>
        </div>
        <table class="tableau-ia">
            <tr>
                <td><span class="label-reel">RÉEL MI-TEMPS</span><br>{r_mt}</td>
                <td style="border-left: 1px solid #30363d;"><span class="label-ia">IA MI-TEMPS</span><br>{ia_mt}</td>
            </tr>
            <tr>
                <td><span class="label-reel">RÉEL FINAL</span><br>{r_ft_h}-{r_ft_a}</td>
                <td style="border-left: 1px solid #30363d;"><span class="label-ia">IA FINAL</span><br>{ia_ft}</td>
            </tr>
            <tr>
                <td colspan="2" class="vainqueur-box">
                    <span style="font-size:10px; color:#aaa;">🏆 VAINQUEUR PRÉDIT :</span><br>
                    {ia_vainqueur.upper()}
                </td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

st.title("🎯 ALPHA-ORACLE : PRONOS & VAINQUEURS")

if tous_matchs:
    tab1, tab2 = st.tabs(["⚽ MATCHS DU JOUR", "📊 HISTORIQUE"])
    with tab1:
        # Priorité au direct
        direct = [m for m in tous_matchs if m['status'] in ['IN_PLAY', 'PAUSED']]
        a_venir = [m for m in tous_matchs if m['status'] == 'TIMED']
        if direct:
            st.subheader("🔴 EN DIRECT")
            for m in direct: afficher_match_oracle(m)
        if a_venir:
            st.subheader("⏳ PROCHAINS MATCHS")
            for m in a_venir[:20]: afficher_match_oracle(m)
    with tab2:
        finis = [m for m in tous_matchs if m['status'] == 'FINISHED']
        for m in finis[::-1][:20]: afficher_match_oracle(m)
else:
    st.error("Aucun match disponible. Vérifie ta connexion ou ta clé API.")
