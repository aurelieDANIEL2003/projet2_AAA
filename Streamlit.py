import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from utils import films_similaires

chemin_bd = r"./bd_ignore/"
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')

# Création du menu
with st.sidebar:
    st.write(f"AAA")
    selection = option_menu(
        menu_title=None,
        options=["Accueil 🙋🏼‍♀️", "Recommendation 🎬", "KPI"]
    )

# Accueil
if selection == "Accueil 🙋🏼‍♀️":
    st.title('Bienvenue au CINEMA !')
    st.image(chemin_bd + "medias/logo_canape.jpeg", width=500)
    st.write('Made by Aurélie, Anissa et Anaëlle.')

# Recommendation
elif selection == "Recommendation 🎬":
    st.title("Recommandation de films 🎬")
    film = st.text_input("Cherchez un film :")
    
    if film:
        # Vérifier si le film existe dans la base
        film_trouve = df_filtered['original_title'].str.lower().eq(film.lower()).any()

        if film_trouve:
            st.success(f"🎬 Le film '{film}' est présent dans la liste !")
            resultats = films_similaires(film, df_filtered)

            if resultats:
                st.write(f"🎬 Voici des films similaires à **{film}** :")
                for res in resultats:
                    st.write(f"- **{res['title']}** (distance: {res['distance']:.2f})")
                   
                    # Ajouter un lien IMDb si l'identifiant IMDb existe
                    if res.get('imdb_id'):
                       st.write(f"  [Lien du film](https://www.imdb.com/title/{res['imdb_id']}/)")
            else:
                st.error(f"❌ Le film '{film}' n'a pas été trouvé.")
    else:
        st.info("🔎 Entrez un titre de film pour rechercher des recommandations.")


# KPI
elif selection == "KPI":
    st.title("KPI")
    try:
        df_final_KPI = pd.read_csv(chemin_bd + "resultat/df_final.csv")
        st.bar_chart(data=df_final_KPI, x='', y='count')
    except FileNotFoundError:
        st.error("Le fichier 'df_final.csv' est introuvable.")

        
# idées de graph pour chaque kpi
# l’identification des acteurs les plus présents et les périodes associées --> histogram/barplot avec 5 barres(= 5 acteurs) par période et count de leur apparition en axe y
# l’évolution de la durée moyenne des films au fil des années --> lineplot ou peut être un bar plot car nos périodes sont définies en catégories
# la comparaison entre les acteurs présents au cinéma et dans les séries
# l’âge moyen des acteurs, 
# ainsi que les films les mieux notés et les caractéristiques qu’ils partagent 


  # import pickle
# # Charger le modèle
#    def charger_modele():
#       with open('mon_modele.pkl', 'rb') as f: #là vous mettez l'emplacement et le nom de votre fichier pkl
#         model_charge = pickle.load(f)
#       return model_charge
