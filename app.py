# ---------- app.py ----------
import json

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from backend import compute_win_ratio
from tppwb import tppwb_matches, tppwb_player_info

st.set_page_config(
    page_title="Calculateur classement AFT padel", page_icon="🎾", layout="centered"
)
st.title("📊 Calculateur de classement AFT Padel Wallonie-Bruxelles")

if "matches" not in st.session_state:
    st.session_state["matches"] = []

if "flag_uploaded_file" not in st.session_state:
    st.session_state["flag_uploaded_file"] = False

# ---------- Retrieve data from the TPPWB website ----------

# Parse affiliation number from the URL GET parameters if provided
affiliation_prefill = ""
if hasattr(st, "query_params") and st.query_params:
    affiliation_prefill = st.query_params["affiliation_number"]

with st.form("affiliation_form", clear_on_submit=False):
    col_aff, col_btn = st.columns([1,2])
    with col_aff:
        affiliation_number = st.text_input(
            "Numéro d'affiliation",
            max_chars=7,
            value=affiliation_prefill,
            help="Entrez votre numéro d'affiliation AFT (7 chiffres)",
        )
    with col_btn:
        if len(affiliation_number) == 7:
            try:
                firstname, name, rank = tppwb_player_info(affiliation_number)
            except Exception as e:
                st.error(f"❌ Erreur lors de la récupération des informations du joueur : {e}")
                player_info = {}
            
            st.info(
                f"**Joueur :** {firstname} {name} ({rank})"
            )
        load_matches = st.form_submit_button("⬇️ Charger mes matchs depuis le site TPPWB")

    if (load_matches and affiliation_number) or affiliation_prefill:
        # Reset session in case previous data exists
        st.session_state["matches"] = []
        st.session_state["flag_uploaded_file"] = False
        
        try:
            matches = tppwb_matches(affiliation_number)
            #st.write(matches)   #Debug: check the structure

            if isinstance(matches, list):
                st.success("✅ Matchs chargés depuis le site TPPWB !")
                st.session_state["matches"] = matches
                st.session_state["flag_uploaded_file"] = True
            else:
                st.error("❌ Données reçues invalides.")
        except Exception as e:
            st.error(f"❌ Erreur lors de la récupération des données : {e}")

# ---------- DISPLAY RESULTS ----------
if st.session_state["matches"]:
    df = pd.DataFrame(st.session_state["matches"])
    win_ratio, recommendation, match_weights = compute_win_ratio(df)
    df["coefficient_total"] = match_weights

    st.markdown(f"### 🧶 Pourcentage de victoires ajusté : {win_ratio}%")
    st.markdown(f"### 📌 Recommandation : {recommendation}")

    # ---------- PLOT RATIO EVOLUTION ----------
    st.subheader("📈 Évolution du ratio de victoire")
    ratios = []
    for i in range(1, len(df) + 1):
        sub_df = df.iloc[:i]
        ratio, _, _ = compute_win_ratio(sub_df)
        ratios.append(ratio)

    fig, ax = plt.subplots()
    ax.plot(range(1, len(ratios) + 1), ratios, marker="o", color="orangered", lw=2)
    ax.set_xticks(range(1, len(ratios) + 1))
    ax.set_xlabel("Nombre de matchs",loc="right")
    ax.set_ylabel(
        "Pourcentage de\nvictoires ajusté\n[%]",
        va="top",
        loc="top",
        rotation="horizontal",
        labelpad=20,
    )
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("📋 Vos matchs enregistrés")
    st.dataframe(df)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Supprimer le dernier match encodé"):
            if st.session_state["matches"]:
                removed_match = st.session_state["matches"].pop()
                st.success("Dernier match supprimé ✅")
                st.rerun()
            else:
                st.warning("Aucun match à supprimer.")

    with col2:
        # Exporter les matchs au format JSON
        if st.session_state["matches"]:
            json_data = json.dumps(st.session_state["matches"], indent=2)
            st.download_button(
                "💾 Télécharger mes matchs", json_data, file_name="mes_matchs_AFT.json"
            )

    if st.button("🔁 Réinitialiser le calcul"):
        st.session_state["matches"] = []
        st.session_state["flag_uploaded_file"] = False
        st.rerun()
else:
    st.info("Ajoutez des matchs pour commencer le calcul.")



uploaded_file = st.file_uploader("📂 Charger un fichier de matchs (.json)", type="json")

if st.session_state["flag_uploaded_file"] is False and uploaded_file is not None:
    try:
        loaded_data = json.load(uploaded_file)
        if isinstance(loaded_data, list) and all(
            isinstance(match, dict) for match in loaded_data
        ):
            st.session_state["matches"] = st.session_state["matches"] + loaded_data
            st.success("✅ Matchs chargés avec succès !")
            st.session_state["flag_uploaded_file"] = True
        else:
            st.error("❌ Fichier invalide.")
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du fichier: {e}")


with st.form("match_form"):
    st.subheader("Ajouter un match")

    genre = st.selectbox("Genre", ["Messieurs", "Dames"])
    category = st.selectbox(
        "Votre classement actuel",
        ["P50", "P100", "P200", "P300", "P400", "P500", "P700", "P1000"],
    )
    result = st.selectbox("Résultat", ["Victoire", "Défaite"])
    comp_type = st.selectbox(
        "Type de compétition", ["Tour", "Interclubs", "Mixte", "Masters"]
    )
    phase = st.selectbox("Phase", ["Poule", "Tableau"])

    partner_rank = st.selectbox(
            "Classement partenaire", [50] + list(range(100, 600, 100)) + [700, 1000]
        )
    
    col1, col2 = st.columns(2)
    with col1:
        opp1_rank = st.selectbox(
            "Classement adversaire 1", [50] + list(range(100, 600, 100)) + [700, 1000]
        )
    with col2:        
        opp2_rank = st.selectbox(
            "Classement adversaire 2", [50] + list(range(100, 600, 100)) + [700, 1000]
        )

    submitted = st.form_submit_button("Ajouter le match")

    if submitted:
        match = {
            "genre": genre,
            "resultat": result,
            "type_competition": comp_type,
            "phase": phase,
            "classement_joueur": float(''.join(filter(str.isdigit, category))),
            "classement_partenaire": partner_rank,
            "classement_adversaire_1": opp1_rank,
            "classement_adversaire_2": opp2_rank,
            "categorie": category,
        }
        st.session_state["matches"] = st.session_state["matches"] + [match]
        st.success("✅ Match ajouté avec succès !")

st.divider()
st.caption(
    "Ce calculateur est basé sur le système de classement AFT Padel Wallonie-Bruxelles de [Janvier 2025](https://padel.tppwb.be/wp-content/uploads/2024/12/Methode-calcul-classements-janvier-2025-4.pdf). Ce calculateur est un outil indépendant, non affilié à l'AFT Padel. Les résultats obtenus n'ont aucune valeur officielle et ne remplacent en aucun cas les décisions de l'organisation. Les données que vous entrez sont traitées localement sur les serveurs de Streamlit Cloud et ne sont ni partagées, ni stockées à des fins commerciales."
)

st.caption(
    "Made by **Mattéo Hauglustaine** - 2025 - *Click [here](https://github.com/Matt-haug/AFT_padel_ranking_calculator) to get acces to the source code on my GitHub*"
)
