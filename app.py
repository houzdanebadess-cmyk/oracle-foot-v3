import streamlit as st
import requests
import random

# --- CONFIGURATION ÉCRAN ---
st.set_page_config(page_title="ALPHA-ORACLE ULTRA", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- DESIGN AGRESSIF ET MODERNE ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: white; }
    .carte-match { 
        background: linear-gradient(145deg, #111, #1a1a1a); 
        border-left: 6px solid #ff0055; 
        border-radius: 12px; 
        padding: 25px; 
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    .equipe-nom { font-size: 18px; font-weight: 800; color: #ffffff; }
    .score-ia { 
        font-size: 55px; 
        font-weight: 900; 
        color: #00ff88; 
        text-align: center; 
        letter-spacing: 5px;
        margin: 10px 0;
    }
    .win-prob { 
        background: #ff0055; 
        padding: 4px 12px; 
        border-radius: 20px; 
        color: white; 
        font-weight: bold; 
        font-size: 12px;
    }
    .vs-text { color: #444; font-style: italic; }
    .footer-card { border-top: 1px solid #333; padding-top: 10px; margin-top: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- MOTEUR DE CALCUL "ULTRA-DOMINATION" ---
# On booste les stats pour obtenir des scores plus élevés et moins de nuls
DB_PUISSANCE = {
    "Real Madrid": {"atk": 98, "def": 92},
    "Manchester City": {"atk": 99, "def": 94},
    "Paris Saint-Germain": {"atk": 95, "def": 85},
    "Bayern": {"atk": 94, "def": 88},
    "Barcelona": {"atk": 92, "def": 84},
    "Juventus": {"atk": 89, "def": 91}
}

def moteur_ultra(m_id, dom, ext):
    random.seed(m_id)
    # Récupération des données ou base "Ultra" par défaut
    d1 = next((v for k, v in DB_PUISSANCE.items() if k.lower() in dom.lower()), {"atk": 82, "def": 78})
    d2 = next((v for k, v in DB_PUISSANCE.items() if k.lower() in ext.lower()), {"atk": 80, "def": 76})

    # Algorithme de Domination Relative
    # On force l'agressivité avec un multiplicateur de 1.3x pour l'avantage
    diff_h = (d1['atk'] * 1.3) - d2['def']
    diff_a = (d2['atk'] * 1.1) - d1['def']

    # Génération des buts (Moteur Ultra : plus de buts, plus d'action)
    f_h = max(0, round(diff_h / 5.5 + random.uniform(0.5, 2.5)))
    f_a = max(0, round(diff_a / 7.5 + random.uniform(0, 1.5)))

    # Calcul Probabilité de Victoire
    prob = round((d1['atk'] / (d1['atk'] + d2['atk'])) * 100 + random.randint(5, 15))
    prob = min(prob, 99) # Plafond à 99%

    vainqueur = dom if f_h > f_a else ext if f_a > f_h else "MATCH NUL"
    return f"{f_h} - {f_a}", f"{prob}%", vainqueur

# --- RÉCUPÉRATION DATA ---
def obtenir_matchs():
    try:
        url = "https://api.football-data.org/v4/matches"
        headers = {'X-Auth-Token': API_KEY}
        res = requests.get(url, headers=headers).json()
        return res.get('matches', [])
    except:
        return []

# --- INTERFACE PRINCIPALE ---
st.title("⚡ ALPHA-ORACLE : ULTRA ENGINE V4")
st.markdown("---")

tous_matchs = obtenir_matchs()

if tous_matchs:
    # Filtrer pour ne montrer que les matchs intéressants (Direct ou à venir)
    matchs_actifs = [m for m in tous_matchs if m['status'] != 'FINISHED'][:30]
    
    for m in matchs_actifs:
        dom_name = m['homeTeam']['name']
        ext_name = m['awayTeam']['name']
        score_ia, certitude, winner = moteur_ultra(m['id'], dom_name, ext_name)
        
        st.markdown(f"""
        <div class="carte-match">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="equipe-nom">{dom_name}</span>
                <span class="vs-text">VS</span>
                <span class="equipe-nom">{ext_name}</span>
                <span class="win-prob">FIABILITÉ : {certitude}</span>
            </div>
            <div class="score-ia">{score_ia}</div>
            <div class="footer-card">
                <span style="color:#ffca28; font-weight:bold;">VAINQUEUR PRÉDIT : {winner.upper()}</span>
                <br><small style="color:#666;">STATUT : {m['status']} | {m['competition']['name']}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.error("Impossible de charger les données. Vérifiez votre clé API ou votre connexion.")

st.sidebar.info("Moteur Ultra : Activé (Mode Domination)")
