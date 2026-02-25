import streamlit as st
import requests
import random
from datetime import datetime

# Config de la page
st.set_page_config(page_title="ALPHA-ORACLE", layout="wide")

API_KEY = '0d92c9d206f74cb3abd38b7b7ba2d873'

# --- STYLE VISUEL (PROPRE ET FRANÇAIS) ---
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
    .score-geant { 
        font-size: 45px; 
        font-weight: 900; 
        color: #f85149; 
        text-align: center;
    }
    .nom-equipe { font-size: 16px; font-weight: bold; margin-top: 10px; }
    
    /* Tableau de comparaison */
    .tableau-oracle { 
        width: 100%; 
        margin-top: 20px; 
        border-collapse: collapse; 
        background: rgba(88, 166, 255, 0.05); 
        border-radius: 10px;
    }
    .tableau-oracle th { color: #8b949e; font-size: 12px; padding: 10px; border-bottom: 1px solid #30363d; }
    .tableau-oracle td { padding: 12px; text-align: center; font-weight: bold; font-size: 16px; border-bottom: 1px solid #21262d; }
    
    .label-ia { color: #58a6ff; } /* Bleu pour l'IA */
    .label-reel { color: #3fb950; } /* Vert pour le Réel */
    .direct-badge { color: #f85149; font-weight: bold; animation: clignote 1s infinite; }
    @keyframes clignote { 50% { opacity: 0.3; } }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def charger_donnees():
    headers = {'X-Auth-Token': API_KEY}
    matchs_liste, logos, stats = [], {}, {}
    # Ligues : France (FL1), Angleterre (PL), Champions League (CL)
    ligues = ['FL1', 'PL', 'CL']
    
    for lg in ligues:
        try:
            # Récupérer classement pour l'intelligence de l'IA
            classement = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/standings", headers=headers).json()
            if 'standings' in classement:
                for equipe in classement['standings'][0]['table']:
                    nom = equipe['team']['name']
                    logos[nom] = equipe['team']['crest']
                    stats[nom] = {
                        'buts_marques': equipe['goalsFor'] / max(1, equipe['playedGames']),
                        'buts_encaisses': equipe['goalsAgainst'] / max(1, equipe['playedGames']),
                        'rang': equipe['position']
                    }
            
            # Récupérer les matchs
            r_matchs = requests.get(f"https://api.football-data.org/v4/competitions/{lg}/matches", headers=headers).json()
            if 'matches' in r_matchs:
                matchs_liste.extend(r_matchs['matches'])
        except:
            pass
    return matchs_liste, logos, stats

matchs, logos_equipes, stats_equipes = charger_donnees()

def predire_score_intelligent(domicile, exterieur, id_match):
    random.seed(id_match)
    # On récupère les stats ou on met des valeurs par défaut
    s1 = stats_equipes.get(domicile, {'buts_marques': 1.2, 'buts_encaisses': 1.2, 'rang': 10})
    s2 = stats_equipes.get(exterieur, {'buts_marques': 1.0, 'buts_encaisses': 1.4, 'rang': 15})
    
    # Calcul Score Final (FT)
    score_f_dom = round((s1['buts_marques'] + s2['buts_encaisses']) / 2 + (0.5 if s1['rang'] < s2['rang'] else 0))
    score_f_ext = round((s2['buts_marques'] + s1['buts_encaisses']) / 2)
    
    # Calcul Mi-temps (MT) - Toujours inférieur ou égal au final
    score_m_dom = random.randint(0, score_f_dom)
    score_m_ext = random.randint(0, score_f_ext)
    
    return f"{score_m_dom}-{score_m_ext}", f"{score_f_dom}-{score_f_ext}"

def afficher_match(m):
    equipe_dom = m['homeTeam']['name']
    equipe_ext = m['awayTeam']['name']
    logo_dom = logos_equipes.get(equipe_dom, "")
    logo_ext = logos_equipes.get(equipe_ext, "")
    statut = m['status']
    
    # Heure et Date
    dt = datetime.strptime(m['utcDate'], "%Y-%m-%dT%H:%M:%SZ")
    heure = dt.strftime("%H:%M")
    date_f = dt.strftime("%d/%m")
    
    # Scores RÉELS
    score_m_reel = f"{m['score']['halfTime']['home'] or 0} - {m['score']['halfTime']['away'] or 0}"
    score_f_dom_reel = m['score']['fullTime']['home'] if m['score']['fullTime']['home'] is not None else 0
    score_f_ext_reel = m['score']['fullTime']['away'] if m['score']['fullTime']['away'] is not None else 0
    
    # Prédictions IA
    ia_mt, ia_ft = predire_score_intelligent(equipe_dom, equipe_ext, m['id'])
    
    # Traduction statut
    statut_fr = "EN DIRECT" if statut in ["IN_PLAY", "PAUSED"] else "TERMINÉ" if statut == "FINISHED" else "À VENIR"
    badge_classe = "direct-badge" if statut_fr == "EN DIRECT" else ""

    st.markdown(f"""
    <div class="carte-match">
        <div style="display:flex; justify-content:space-between; color:#8b949e; font-size:12px; margin-bottom:15px;">
            <span>📅 {date_f} | 🕒 {heure} UTC</span>
            <span class="{badge_classe}">{statut_fr}</span>
        </div>
        
        <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
            <div style="width:30%;">
                <img src="{logo_dom}" width="55"><br>
                <div class="nom-equipe">{equipe_dom[:15]}</div>
            </div>
            <div style="width:40%;">
                <div class="score-geant">
                    {score_f_dom_reel if statut != 'TIMED' else '?'} - {score_f_ext_reel if statut != 'TIMED' else '?'}
                </div>
            </div>
            <div style="width:30%;">
                <img src="{logo_ext}" width="55"><br>
                <div class="nom-equipe">{equipe_ext[:15]}</div>
            </div>
        </div>

        <table class="tableau-oracle">
            <tr>
                <th>PÉRIODE</th>
                <th class="label-reel">RÉEL (LIVE)</th>
                <th class="label-ia">ORACLE IA 🧠</th>
            </tr>
            <tr>
                <td>1ère Mi-temps</td>
                <td class="label-reel">{score_m_reel}</td>
                <td class="label-ia">{ia_mt}</td>
            </tr>
            <tr>
                <td>Score Final</td>
                <td class="label-reel">{score_f_dom_reel}-{score_f_ext_reel}</td>
                <td class="label-ia">{ia_ft}</td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# --- INTERFACE PRINCIPALE ---
st.title("🎯 ALPHA-ORACLE ELITE")

if matchs:
    # Navigation en français
    onglets = st.tabs(["⚽ MATCHS DU JOUR", "📅 CALENDRIER", "📊 COMPARATEUR"])
    maintenant = datetime.utcnow().strftime('%Y-%m-%d')
    
    with onglets[0]:
        # On affiche le direct en priorité
        en_direct = [m for m in matchs if m['status'] in ['IN_PLAY', 'PAUSED']]
        aujourdhui = [m for m in matchs if m['utcDate'].startswith(maintenant) and m not in en_direct]
        
        if en_direct:
            st.subheader("🔴 MATCHS EN DIRECT")
            for m in en_direct: afficher_match(m)
        
        if aujourdhui:
            st.subheader("📅 PROGRAMMÉS AUJOURD'HUI")
            for m in aujourdhui: afficher_match(m)
            
        if not en_direct and not aujourdhui:
            st.info("Aucun match majeur prévu pour aujourd'hui.")

    with onglets[1]:
        futur = [m for m in matchs if m['status'] == 'TIMED' and not m['utcDate'].startswith(maintenant)]
        for m in futur[:15]: afficher_match(m)

    with onglets[2]:
        passes = [m for m in matchs if m['status'] == 'FINISHED' and not m['utcDate'].startswith(maintenant)][::-1]
        for m in passes[:15]: afficher_match(m)
else:
    st.error("Connexion impossible avec l'API Football. Vérifie ta clé.")
