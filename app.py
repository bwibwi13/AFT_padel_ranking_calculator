# ---------- app.py ----------
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from backend import compute_win_ratio

st.set_page_config(
    page_title="Calculateur classement AFT padel", page_icon="🎾", layout="centered"
)
st.title("📊 Calculateur de classement AFT Padel Wallonie-Bruxelles")

if "matches" not in st.session_state:
    st.session_state["matches"] = []

with st.form("match_form"):
    st.subheader("Ajouter un match")

    genre = st.selectbox("Genre", ["Messieurs", "Dames"])
    result = st.selectbox("Résultat", ["Victoire", "Défaite"])
    comp_type = st.selectbox(
        "Type de compétition", ["Tour", "Interclubs", "Mixte", "Masters"]
    )
    phase = st.selectbox("Phase", ["Poule", "Tableau"])
    category = st.selectbox(
        "Catégorie", ["P50", "P100", "P200", "P300", "P400", "P500", "P700", "P1000"]
    )

    col1, col2 = st.columns(2)
    with col1:
        player_rank = st.selectbox(
            "Votre classement", [50] + list(range(100, 600, 100)) + [700, 1000]
        )
        opp1_rank = st.selectbox(
            "Classement adversaire 1", [50] + list(range(100, 600, 100)) + [700, 1000]
        )
    with col2:
        partner_rank = st.selectbox(
            "Classement partenaire", [50] + list(range(100, 600, 100)) + [700, 1000]
        )
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
            "classement_joueur": player_rank,
            "classement_partenaire": partner_rank,
            "classement_adversaire_1": opp1_rank,
            "classement_adversaire_2": opp2_rank,
            "categorie": category,
        }
        st.session_state["matches"] = st.session_state["matches"] + [match]
        st.success("✅ Match ajouté avec succès !")

# ---------- DISPLAY RESULTS ----------

if st.session_state["matches"]:
    df = pd.DataFrame(st.session_state["matches"])
    st.subheader("📋 Vos matchs enregistrés")
    st.dataframe(df)

    win_ratio, recommendation = compute_win_ratio(df)
    st.markdown(f"### 🧶 Pourcentage de victoires ajusté : {win_ratio}%")
    st.markdown(f"### 📌 Recommandation : {recommendation}")

    # ---------- PLOT RATIO EVOLUTION ----------
    st.subheader("📈 Évolution du ratio de victoire")
    ratios = []
    for i in range(1, len(df) + 1):
        sub_df = df.iloc[:i]
        ratio, _ = compute_win_ratio(sub_df)
        ratios.append(ratio)

    fig, ax = plt.subplots()
    ax.plot(range(1, len(ratios) + 1), ratios, marker="o", color="orangered", lw=2)
    ax.set_xticks(range(1, len(ratios) + 1))
    ax.set_xlabel("Nombre de matchs")
    ax.set_ylabel(
        "Pourcentage de\nvictoires ajusté\n[%]",
        ha="right",
        va="top",
        rotation="horizontal",
        labelpad=20,
    )
    ax.grid(True)
    st.pyplot(fig)

    if st.button("🔁 Réinitialiser le calcul"):
        st.session_state["matches"] = []
        st.rerun()
else:
    st.info("Ajoutez des matchs pour commencer le calcul.")

st.divider()
st.caption(
    "Ce calculateur est basé sur le système de classement AFT Padel Wallonie de [Janvier 2025](https://padel.tppwb.be/wp-content/uploads/2024/12/Methode-calcul-classements-janvier-2025-4.pdf). Ce calculateur est un outil indépendant, non affilié à l'AFT Padel. Les résultats obtenus n'ont aucune valeur officielle et ne remplacent en aucun cas les décisions de l'organisation. Les données que vous entrez sont traitées localement sur les serveurs de Streamlit Cloud et ne sont ni partagées, ni stockées à des fins commerciales."
)

st.caption(
    "Made by **Mattéo Hauglustaine** - 2025 - *Click [here](https://github.com/Matt-haug/Thermodynamic_cycle_simulator) to get acces to the source code on my GitHub*"
)
