import streamlit as st
import requests
import random
import math

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")
API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS (LOGOS, BOUTONS, CARTES) ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    /* Navigation */
    .stTabs [data-baseweb="tab-list"] { background-color: #161b22; padding: 10px; border-radius: 12px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: #21262d; border-radius: 8px; color: #8b949e; border: none; }
    .stTabs [aria-selected="true"] { background-color: #238636 !important; color: white !important; border-bottom: 3px solid #3fb950; }
    
    /* Cartes de Match */
    .carte-match { 
        background: #1c2128; border: 1px solid #30363d; border-radius: 15px; 
        padding: 20px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .score-live { font-size: 38px; font-weight: 900; color: #f85149; text-align: center; }
    .formation { color: #ffca28; font-size: 11px; font-family: monospace; font-weight: bold; }
    
    /* Tableau Oracle */
    .tableau-oracle { width: 100%; border-collapse: collapse; margin-top: 15px; border-radius: 10px; overflow: hidden; }
    .tableau-oracle td { padding: 12px; text-align: center; border: 1px solid #333; background: rgba(0,0,0,0.1); }
    .label-cell { font-size: 10px; color: #8b949e; text-transform: uppercase; margin-bottom: 4px; display: block; }
    
    /* Prono Final */
    .prono-final { color: #ffca28; font-weight: 900; font-size: 18px; text-align: center; border-top: 1px solid #333; padding-top: 15px; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

# --- MOTEUR DE CALCUL "FOOTBALL PRO" (POISSON) ---
def moteur_oracle_foot(m_id, dom, ext):
    random.seed(m_id)
    # Stats de base pour les gros clubs
    favoris = {"Real Madrid": 95, "Man City": 97, "Bayern": 93, "PSG": 92, "Juve": 88, "Liverpool": 94}
    p1 = next((v for k, v in favoris.items() if k.lower() in dom.lower()), 76)
    p2 = next((v for k, v in favoris.items() if k.lower() in ext.lower()), 74)

    # Calcul de la moyenne de buts (xG) - On reste entre 0 et 4 buts
    diff = (p1 - p2) / 20
    lam1 = max(0.5, 1.4 + diff + random.uniform(-0.2, 0.2))
    lam2 = max(0.3, 1.1 - diff + random.uniform(-0.2, 0.2))

    # Loi de Poisson (Mathématiques du foot)
    def poisson(lam):
        L, k, p = math.exp(-lam), 0, 1
        while p > L: k += 1; p *= random.random()
        return k - 1

    f_h, f_a = min(4, poisson(lam1)), min(3, poisson(lam2))
    m_h, m_a = min(f_h, random.randint(0, 1)), min(f_a, random.randint(0, 1))
    
    v_ia = dom if f_h > f_a else ext if f_a > f_h else "MATCH NUL"
    return f"{m_h}-{m_a}", f"{f_h}-{f_a}", v_ia

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data(ttl=60)
def charger_data():
    try:
        r = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': API_KEY}).json()
        return r.get('matches', [])
    except: return []

# --- INTERFACE ---
st.title("🎯 ALPHA-ORACLE ELITE")
matchs = charger_data()

if matchs:
    # LA NAVIGATION RÉTABLIE
    t1, t2, t3 = st.tabs(["🔴 DIRECT / JOUR", "📅 CALENDRIER", "📊 HISTORIQUE"])

    def afficher_match(m):
        dom_name, ext_name = m['homeTeam']['name'], m['awayTeam']['name']
        mt_ia, ft_ia, v_ia = moteur_oracle_foot(m['id'], dom_name, ext_name)
        
        r_h, r_a = m['score']['fullTime']['home'], m['score']['fullTime']['away']
        r_mt = f"{m['score']['halfTime']['home'] or 0}-{m['score']['halfTime']['away'] or 0}"

        # Affichage de la carte
        st.markdown(f"""
        <div class="carte-match">
            <div style="display:flex; justify-content:space-between; font-size:11px; color:#8b949e; margin-bottom:15px;">
                <span>🕒 {m['utcDate'][11:16]} | {m['competition']['name']}</span>
                <span style="color:#f85149; font-weight:bold;">{m['status']}</span>
            </div>
            
            <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
                <div style="width:35%;">
                    <img src="{m['homeTeam'].get('crest','')}" width="55"><br>
                    <b style="font-size:14px;">{dom_name[:15]}</b><br>
                    <span class="formation">4-3-3</span>
                </div>
                
                <div style="width:30%;" class="score-live">
                    {r_h if r_h is not None else '?'} - {r_a if r_a is not None else '?'}
                </div>
                
                <div style="width:35%;">
                    <img src="{m['awayTeam'].get('crest','')}" width="55"><br>
                    <b style="font-size:14px;">{ext_name[:15]}</b><br>
                    <span class="formation">4-4-2</span>
                </div>
            </div>

            <table class="tableau-oracle">
                <tr>
                    <td><span class="label-cell" style="color:#3fb950;">RÉEL MT</span><b>{r_mt}</b></td>
                    <td style="background:rgba(88,166,255,0.05);"><span class="label-cell" style="color:#58a6ff;">ORACLE MT</span><b>{mt_ia}</b></td>
                </tr>
                <tr>
                    <td><span class="label-cell" style="color:#3fb950;">RÉEL FINAL</span><b>{r_h if r_h is not None else 0}-{r_a if r_a is not None else 0}</b></td>
                    <td style="background:rgba(88,166,255,0.05);"><span class="label-cell" style="color:#58a6ff;">ORACLE FINAL</span><b>{ft_ia}</b></td>
                </tr>
            </table>
            
            <div class="prono-final">🎯 PRONO : {v_ia.upper()}</div>
        </div>
        """, unsafe_allow_html=True)

    with t1:
        en_cours = [m for m in matchs if m['status'] in ['IN_PLAY', 'PAUSED', 'TIMED']]
        for m in en_cours[:20]: afficher_match(m)
    with t2:
        avenir = [m for m in matchs if m['status'] == 'SCHEDULED']
        for m in avenir[:15]: afficher_match(m)
    with t3:
        finis = [m for m in matchs if m['status'] == 'FINISHED']
        for m in finis[::-1][:15]: afficher_match(m)
else:
    st.error("Données indisponibles. Vérifie ta connexion.")
