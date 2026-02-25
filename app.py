import streamlit as st
import requests
import random
import math

# --- CONFIGURATION ---
st.set_page_config(page_title="ALPHA-ORACLE ELITE", layout="wide")
API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE CSS PREMIUM ---
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .stTabs [data-baseweb="tab-list"] { background-color: #161b22; padding: 10px; border-radius: 10px; gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: #21262d; border-radius: 8px; color: #8b949e; border: none; }
    .stTabs [aria-selected="true"] { background-color: #238636 !important; color: white !important; border-bottom: 3px solid #3fb950; }
    
    .carte-match { 
        background: #1c2128; border: 1px solid #30363d; border-radius: 15px; 
        padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .score-reel { font-size: 38px; font-weight: 900; color: #f85149; text-align: center; }
    .badge-formation { background: #30363d; color: #ffca28; padding: 2px 8px; border-radius: 12px; font-size: 10px; font-weight: bold; }
    .tableau-oracle { width: 100%; border-collapse: collapse; margin-top: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; overflow: hidden; }
    .tableau-oracle td { padding: 12px; text-align: center; border: 1px solid #30363d; }
    .label-tab { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; display: block; }
    .prono-final { color: #ffca28; font-weight: 900; font-size: 16px; border-top: 1px solid #333; padding-top: 12px; margin-top: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DONNÉES CLUBS (STATS & FORMATIONS) ---
DB_CLUBS = {
    "Real Madrid": {"atk": 95, "def": 92, "form": "4-3-1-2"},
    "Manchester City": {"atk": 97, "def": 94, "form": "3-2-4-1"},
    "Juventus": {"atk": 86, "def": 90, "form": "3-5-2"},
    "Paris Saint-Germain": {"atk": 92, "def": 85, "form": "4-3-3"},
    "Bayern": {"atk": 93, "def": 88, "form": "4-2-3-1"},
    "EC Bahia": {"atk": 78, "def": 75, "form": "4-3-3"},
    "CR Flamengo": {"atk": 85, "def": 80, "form": "4-2-3-1"}
}

def moteur_oracle(m_id, dom, ext):
    random.seed(m_id)
    d1 = next((v for k, v in DB_CLUBS.items() if k.lower() in dom.lower()), {"atk": 76, "def": 74, "form": "4-4-2"})
    d2 = next((v for k, v in DB_CLUBS.items() if k.lower() in ext.lower()), {"atk": 74, "def": 72, "form": "4-4-2"})

    # Formule de Poisson pour éviter le basket (max 5 buts)
    diff = (d1['atk'] - d2['def']) / 15
    l1 = max(0.5, 1.4 + diff + random.uniform(-0.2, 0.2))
    l2 = max(0.2, 1.1 - diff + random.uniform(-0.2, 0.2))

    def sim(lam):
        L, k, p = math.exp(-lam), 0, 1
        while p > L: k += 1; p *= random.random()
        return k - 1

    f_h, f_a = min(5, sim(l1)), min(4, sim(l2))
    m_h, m_a = min(f_h, random.randint(0, 1)), min(f_a, random.randint(0, 1))
    
    v_ia = dom if f_h > f_a else ext if f_a > f_h else "MATCH NUL"
    return f"{m_h}-{m_a}", f"{f_h}-{f_a}", v_ia, d1['form'], d2['form']

@st.cache_data(ttl=60)
def fetch_matches():
    try:
        r = requests.get("https://api.football-data.org/v4/matches", headers={'X-Auth-Token': API_KEY}).json()
        return r.get('matches', [])
    except: return []

# --- INTERFACE ---
st.title("🎯 ALPHA-ORACLE ELITE")
matchs = fetch_matches()

if matchs:
    # NAVIGATION RÉTABLIE
    tab1, tab2, tab3 = st.tabs(["🔴 DIRECT / JOUR", "📅 CALENDRIER", "📊 HISTORIQUE"])

    def card(m):
        dom_name = m['homeTeam']['name']
        ext_name = m['awayTeam']['name']
        mt_ia, ft_ia, v_ia, f1, f2 = moteur_oracle(m['id'], dom_name, ext_name)
        
        r_h = m['score']['fullTime']['home']
        r_a = m['score']['fullTime']['away']
        r_mt = f"{m['score']['halfTime']['home'] or 0}-{m['score']['halfTime']['away'] or 0}"

        st.markdown(f"""
        <div class="carte-match">
            <div style="display:flex; justify-content:space-between; font-size:11px; color:#8b949e; margin-bottom:15px;">
                <span>🕒 {m['utcDate'][11:16]} | {m['competition']['name']}</span>
                <span style="color:#f85149; font-weight:bold;">{m['status']}</span>
            </div>
            
            <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
                <div style="width:35%;">
                    <img src="{m['homeTeam'].get('crest','')}" width="50" style="margin-bottom:8px;"><br>
                    <b style="font-size:14px;">{dom_name[:15]}</b><br>
                    <span class="badge-formation">{f1}</span>
                </div>
                
                <div style="width:30%;" class="score-reel">
                    {r_h if r_h is not None else '?'} - {r_a if r_a is not None else '?'}
                </div>
                
                <div style="width:35%;">
                    <img src="{m['awayTeam'].get('crest','')}" width="50" style="margin-bottom:8px;"><br>
                    <b style="font-size:14px;">{ext_name[:15]}</b><br>
                    <span class="badge-formation">{f2}</span>
                </div>
            </div>

            <table class="tableau-oracle">
                <tr>
                    <td>
                        <span class="label-tab" style="color:#3fb950;">RÉEL MI-TEMPS</span>
                        <b>{r_mt}</b>
                    </td>
                    <td style="background: rgba(88,166,255,0.05);">
                        <span class="label-tab" style="color:#58a6ff;">ORACLE MI-TEMPS</span>
                        <b>{mt_ia}</b>
                    </td>
                </tr>
                <tr>
                    <td>
                        <span class="label-tab" style="color:#3fb950;">RÉEL FINAL</span>
                        <b>{r_h if r_h is not None else 0}-{r_a if r_a is not None else 0}</b>
                    </td>
                    <td style="background: rgba(88,166,255,0.05);">
                        <span class="label-tab" style="color:#58a6ff;">ORACLE FINAL</span>
                        <b>{ft_ia}</b>
                    </td>
                </tr>
            </table>
            
            <div class="prono-final">
                🎯 PRONO : {v_ia.upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab1:
        for m in [m for m in matchs if m['status'] in ['IN_PLAY', 'PAUSED', 'TIMED']][:25]:
            card(m)
    with tab2:
        for m in [m for m in matchs if m['status'] == 'SCHEDULED'][:15]:
            card(m)
    with tab3:
        for m in [m for m in matchs if m['status'] == 'FINISHED'][::-1][:15]:
            card(m)
else:
    st.error("Erreur de connexion aux serveurs de football.")
