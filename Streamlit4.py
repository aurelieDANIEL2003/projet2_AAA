import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from utils1 import films_similaires
from utils2 import films_similaires2
from utils4 import films_similaires3

# Charger les données
chemin_bd = r"./bd_ignore/"
df_tmdb = pd.read_csv(chemin_bd + 'resultat/df_tmdb2.csv')  # Dataset des films
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')

# # Fonction pour rechercher des titres
def search_movies(film_nom, df):
    results = df[df['title'].str.contains(film_nom, case=False, na=False)]
    return results

# # Fonction pour réinitialiser la recherche
# def reset_search():
#     st.session_state['film_nom'] = ""
#     st.session_state['selected_title'] = None
    


# Menu latéral
with st.sidebar:
    selection = option_menu(
        menu_title=None,
        options=["Accueil 🙋🏼‍♀️", "Recommandation 🎬", "KPI 📊"],
        icons=["house", "film", "bar-chart"],
        menu_icon="cast",
        default_index=0
    )

    #     # Bouton pour réinitialiser la recherche
    #     # Affichage conditionnel pour "Recommandation 🎬"
    # if selection == "Recommandation 🎬":
    #     #st.write("### Options supplémentaires")
# Page d'accueil
if selection == "Accueil 🙋🏼‍♀️":
    st.title('Bienvenue au CINÉMA ! 🎥')
    st.image(chemin_bd + "medias/logo_canape.jpeg", width=500)
    st.write("""
        Recommandations personnalisées de films Made by Aurélie, Anissa et Anaëlle. 🎬
    """)

# Page de recommandation
elif selection == "Recommandation 🎬":
    st.title("Recommandation de films 🎬")
    
    # Recherche d'un film
    film_nom = st.text_input("Cherchez un film par titre ou par partie de titre :")

    if film_nom:
        # Étape 1 : Recherche des films correspondants
        results = search_movies(film_nom, df_filtered)

        if not results.empty:
            st.write("### Films trouvés correspondant à votre recherche :")
            st.dataframe(results[['title', 'genres']])

            # Étape 2 : Sélectionner un film parmi les résultats
            selected_title = st.selectbox(
                "Sélectionnez un film :",
                options=results['title'].tolist()
            )

            if selected_title:
                selected_movie = results[results['title'] == selected_title]
                imdb_id = selected_movie['imdb_id'].iloc[0]

                st.write(f"### Film sélectionné : **{selected_title}**")
                #st.write(f"L'identifiant IMDb du film est : **{imdb_id}**")
                st.write(f"[Voir le film](https://www.imdb.com/title/{imdb_id}/)")

                # Recommandations
                st.write("## Recherche de recommandations :")
                col1, col2, col3 = st.columns(3)
                with col1:
                    vote_button = st.button("👍 Par vote")
                with col2:
                    genre_button = st.button("🍿 Par genre")
                with col3:
                    actor_button = st.button("⭐ Par acteur")

                # Recommandation par vote
                if vote_button:
                    st.write("### Recommandations par vote 📈")
                    resultats = films_similaires(selected_title, df_filtered, df_tmdb)
                    if resultats:
                        for res in resultats:
                            st.write(f"- **{res.get('title')}**")
                            if res.get('imdb_id'):
                                st.write(f"[Lien du film](https://www.imdb.com/title/{res['imdb_id']}/)")
                            if res.get('poster_path'):
                                st.image(f"https://image.tmdb.org/t/p/w500{res['poster_path']}", width=200)
                    else:
                        st.error("❌ Aucune recommandation trouvée par vote.")

                # Recommandation par genre
                if genre_button:
                    st.write("### Recommandations par genre 🍿")
                    resultats = films_similaires2(selected_title, df_filtered, df_tmdb)
                    if resultats:
                        for res in resultats:
                            st.write(f"- **{res.get('title')}**")
                            if res.get('imdb_id'):
                                st.write(f"[Lien du film](https://www.imdb.com/title/{res['imdb_id']}/)")
                            if res.get('poster_path'):
                                st.image(f"https://image.tmdb.org/t/p/w500{res['poster_path']}", width=200)
                    else:
                        st.error("❌ Aucune recommandation trouvée par genre.")

                # Recommandation par acteur
                if actor_button:
                    st.write("### Recommandations par acteur ⭐")
                    resultats = films_similaires3(selected_title, df_filtered, df_tmdb)
                    if resultats:
                        for res in resultats:
                            st.write(f"- **{res.get('title')}**")
                            if res.get('imdb_id'):
                                st.write(f"[Lien du film](https://www.imdb.com/title/{res['imdb_id']}/)")
                            if res.get('poster_path'):
                                st.image(f"https://image.tmdb.org/t/p/w500{res['poster_path']}", width=200)
                    else:
                        st.error("❌ Aucune recommandation trouvée par acteur.")
        else:
            st.error(f"❌ Aucun film trouvé correspondant à '{film_nom}'.")
    else:
        st.info("🔎 Entrez un titre de film pour rechercher des recommandations.")

# Page KPI
elif selection == "KPI":
    st.title("Indicateurs Clés de Performance (KPI)")
    try:
        df_final_KPI = pd.read_csv(chemin_bd + "resultat/df_final.csv")
        st.bar_chart(data=df_final_KPI, x='', y='count')
    except FileNotFoundError:
        st.error("❌ Le fichier 'df_final.csv' est introuvable.")
