import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from utils import films_similaires

chemin_bd = r"./bd_ignore/"
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')


#création du menu
with st.sidebar:
     st.write(f"AAA")
     selection = option_menu(
            menu_title=None,
            options = ["Accueil 🙋🏼‍♀️", "Recommendation 🎬", "KPI"])

# On indique au programme quoi faire en fonction du choix
if selection == "Accueil 🙋🏼‍♀️":
    st.title('Bienvenue sur notre projet 2 !')
    st.image(chemin_bd + "medias/logo_canape.jpeg", width=500)
    st.write('Made by Aurélie, Anissa and Anaëlle.')

elif selection == "Recommendation 🎬":
   
   film = st.text_input("Cherchez un film:")
   
   films_similaires(film)
   
   if film:
    # Vérifier si le film existe dans le dataset (insensible à la casse)
    film_trouve = df_filtered['original_title'].str.lower().eq(film.lower()).any()

    if film_trouve:
        st.success(f"🎬 Le film '{film}' est présent dans la liste !")
        film_fonction = films_similaires(film, df_filtered)
        for film in film_trouve:
                st.write(f"🎬 {film}")
    else:
        st.error(f"❌ Le film '{film}' n'a pas été trouvé.")
   else:
    st.info("🔎 Entrez un titre de film pour vérifier sa présence dans la liste.")




elif selection == "KPI":
   df_final_KPI = pd.read_csv(chemin_bd+"resultat/df_final.csv")
   st.bar_chart(data=df_final_KPI,x='', y='count')


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
