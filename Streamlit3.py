import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from utils import films_similaires
from utils2 import films_similaires2
from utils3 import films_similaires3

# Charger les données
chemin_bd = r"./bd_ignore/"
df_tmdb = pd.read_csv(chemin_bd + 'resultat/df_tmdb2.csv')  # Dataset des films 
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')

# Fonction pour réinitialiser la recherche
def reset_search():
    st.session_state['film'] = ""
    st.experimental_rerun()

# Menu latéral
with st.sidebar:
    selection = option_menu(
        menu_title=None,
        options=["Accueil 🙋🏼‍♀️", "Recommandation 🎬", "KPI"]
    )

# Page d'accueil
if selection == "Accueil 🙋🏼‍♀️":
    st.title('Bienvenue au CINÉMA !')
    st.image(chemin_bd + "medias/logo_canape.jpeg", width=500)
    st.write('Made by Aurélie, Anissa et Anaëlle.')

# Page de recommandation
elif selection == "Recommandation 🎬":
    st.title("Recommandation de films 🎬")
    
    # Champ de recherche
    if "film" not in st.session_state:
        st.session_state['film'] = ""

    film = st.text_input("Cherchez un film :", value=st.session_state['film'], key="film")

    if film:
        # Vérifier si le film existe dans la base
        film_trouve = df_filtered['title'].str.lower().eq(film.lower()).any()

        if film_trouve:
            st.success(f"⏳ Je cherche des films similaires à **{film}**!")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                vote_button = st.button("👍 Par vote")
            with col2:
                genre_button = st.button("🍿 Par genre")
            with col3:
                actor_button = st.button("⭐ Par acteur")
            
            # Recommandation par vote
            if vote_button:
                st.write("🔍 Recherche de recommandations par vote...")
                resultats = films_similaires(film, df_filtered)
                if resultats:
                    for res in resultats:
                        st.write(f"- **{res.get('title', 'Titre inconnu')}**")
                        if res.get('imdb_id'):
                            st.write(f"[Lien du film](https://www.imdb.com/title/{res['imdb_id']}/)")
                        if res.get('poster_path'):
                            st.image(f"https://image.tmdb.org/t/p/w500{res['poster_path']}", width=200)
                else:
                    st.error("❌ Aucune recommandation trouvée par vote.")

            # Recommandation par genre
            if genre_button:
                st.write("🔍 Recherche de recommandations par genre...")
                resultats = films_similaires2(film, df_filtered, df_tmdb)
                if isinstance(resultats, list):
                    for res in resultats:
                        st.write(f"- **{res.get('title', 'Titre inconnu')}**")
                        if res.get('imdb_id'):
                            st.write(f"[Lien du film](https://www.imdb.com/title/{res['imdb_id']}/)")
                        if res.get('poster_path'):
                            st.image(f"https://image.tmdb.org/t/p/w500{res['poster_path']}", width=200)
                else:
                    st.error(resultats)  # Affiche le message d'erreur retourné par films_similaires2

            # Recommandation par acteur
            if actor_button:
                st.write("🔍 Recherche de recommandations par acteur...")
                resultats = films_similaires3(film, df_filtered, df_tmdb)
                if isinstance(resultats, list):
                    for res in resultats:
                        st.write(f"- **{res.get('title', 'Titre inconnu')}**")
                        if res.get('imdb_id'):
                            st.write(f"[Lien du film](https://www.imdb.com/title/{res['imdb_id']}/)")
                        if res.get('poster_path'):
                            st.image(f"https://image.tmdb.org/t/p/w500{res['poster_path']}", width=200)
                else:
                    st.error(resultats)  # Affiche le message d'erreur retourné par films_similaires3
        else:
            st.error(f"❌ Le film **'{film}'** n'a pas été trouvé dans la base.")
    else:
        st.info("🔎 Entrez un titre de film pour rechercher des recommandations.")

# Page KPI
elif selection == "KPI":
    st.title("KPI")
    try:
        df_final_KPI = pd.read_csv(chemin_bd + "resultat/df_final.csv")
        st.bar_chart(data=df_final_KPI, x='', y='count')
    except FileNotFoundError:
        st.error("Le fichier 'df_final.csv' est introuvable.")
