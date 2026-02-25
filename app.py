import streamlit as st
import requests
import random
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="ALPHA-ORACLE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE VISUEL CORRIGÉ ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .carte-match { 
        background: #161b22; 
        border: 2px solid #30363d; 
        border-radius: 15px; 
        padding: 20px; 
        margin-bottom: 25px; 
    }
    .score-geant { font-size: 45px; font-weight: 900; color: #f85149; text-align: center; }
    .nom-equipe { font-size: 16px; font-weight: bold; margin-top: 10px; }
    .tableau-oracle { width: 100%; margin-top: 20px; border-collapse: collapse; background: rgba(88, 166, 255, 0.05); }
    .tableau-oracle th { color: #8b949e; font-size: 12px; padding: 10px; border-bottom: 1px solid #30363d; }
    .tableau-oracle td { padding: 12px; text-align: center; font-weight: bold; font-size: 16px; }
    .label-ia { color: #58a6ff; }
    .label-reel { color: #3fb950; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def charger_donnees():
    headers = {'X-Auth-Token': API_KEY}
    matchs_liste, logos, stats = [], {}, {}
    for lg in ['FL1', 'PL', 'CL']:
        try:
            # Récupération classement et logos
            cl = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/standings", headers=headers).json()
            if 'standings' in cl:
                for eq in cl['standings'][0]['table']:
                    n = eq['team']['name']
                    logos[n] = eq['team']['crest']
                    stats[n] = {'gf': eq['goalsFor']/max(1, eq['playedGames']), 'rank': eq['position']}
            # Récupération matchs
            m_req = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/matches", headers=headers).json()
            if 'matches' in m_req: matchs_liste.extend(m_req['matches'])
        except: pass
    return matchs_liste, logos, stats

matchs, logos_equipes, stats_equipes = charger_donnees()

def predire_mi_temps_et_final(dom, ext, m_id):
    random.seed(m_id)
    s1 = stats_equipes.get(dom, {'gf': 1.2, 'rank': 10})
    s2 = stats_equipes.get(ext, {'gf': 1.0, 'rank': 15})
    # Intelligence IA : Avantage au mieux classé
    f_dom = round(s1['gf'] + (0.5 if s1['rank'] < s2['rank'] else 0))
    f_ext = round(s2['gf'])
    # Mi-temps
    m_dom, m_ext = random.randint(0, f_dom), random.randint(0, f_ext)
    return f"{m_dom}-{m_ext}", f"{f_dom}-{f_ext}"

def afficher_match(m):
    dom, ext = m['homeTeam']['name'], m['awayTeam']['name']
    statut = m['status']
    statut_fr = "EN DIRECT" if statut in ["IN_PLAY", "PAUSED"] else "TERMINÉ" if statut == "FINISHED" else "À VENIR"
    
    # Scores Réels
    r_mt = f"{m['score']['halfTime']['home'] or 0} - {m['score']['halfTime']['away'] or 0}"
    r_f_h = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
    r_f_a = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
    
    # Pronos IA
    ia_mt, ia_ft = predire_mi_temps_et_final(dom, ext, m['id'])
    
    # AFFICHAGE DU MATCH (C'est ici que la correction opère)
    st.markdown(f"""
    <div class="carte-match">
        <div style="display:flex; justify-content:space-between; color:#8b949e; font-size:12px; margin-bottom:15px;">
            <span>🕒 {m['utcDate'][11:16]} UTC</span>
            <span style="color:#f85149; font-weight:bold;">{statut_fr}</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
            <div style="width:30%;"><img src="{logos_equipes.get(dom, "")}" width="50"><br><div class="nom-equipe">{dom[:12]}</div></div>
            <div style="width:40%;"><div class="score-geant">{r_f_h if statut != 'TIMED' else '?'} - {r_f_a if statut != 'TIMED' else '?'}</div></div>
            <div style="width:30%;"><img src="{logos_equipes.get(ext, "")}" width="50"><br><div class="nom-equipe">{ext[:12]}</div></div>
        </div>
        <table class="tableau-oracle">
            <tr><th>PÉRIODE</th><th class="label-reel">RÉEL (LIVE)</th><th class="label-ia">PRONO IA 🧠</th></tr>
            <tr><td>1ère Mi-temps</td><td class="label-reel">{r_mt}</td><td class="label-ia">{ia_mt}</td></tr>
            <tr><td>Score Final</td><td class="label-reel">{r_f_h}-{r_f_a}</td><td class="label-ia">{ia_ft}</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# Interface
st.title("🎯 ALPHA-ORACLE : PRONOSTICS MI-TEMPS")
if matchs:
    t1, t2, t3 = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER", "📊 HISTORIQUE"])
    mnt = datetime.utcnow().strftime('%Y-%m-%d')
    with t1:
        en_cours = [m for m in matchs if m['status'] in ['IN_PLAY', 'PAUSED'] or m['utcDate'].startswith(mnt)]
        for m in en_cours: afficher_match(m)
    with t2:
        for m in [m for m in matchs if m['status'] == 'TIMED' and not m['utcDate'].startswith(mnt)][:10]: afficher_match(m)
    with t3:
        for m in [m for m in matchs if m['status'] == 'FINISHED'][:10]: afficher_match(m)
