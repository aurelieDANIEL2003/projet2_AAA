# import warnings
# warnings.filterwarnings("ignore", category=UserWarning)
# warnings.filterwarnings("ignore", category=FutureWarning)
# from sklearn.neighbors import NearestNeighbors
# from sklearn.preprocessing import MinMaxScaler

# import pandas as pd
# import numpy as np

# chemin_bd = r"./bd_ignore/"

# df_filtered= pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')

# features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']

# # Encodage des genres
# df_encoded = pd.concat(
#     [df_filtered[features], pd.get_dummies(df_filtered['genres'], prefix='genre')],
#     axis=1
# )

# # Normalisation des données
# scaler = MinMaxScaler()
# X = scaler.fit_transform(df_encoded)

# # Modèle Nearest Neighbors
# k = 11 # Meilleure valeur de K = 6 d'aprés fig

# model = NearestNeighbors(n_neighbors=k, metric='euclidean')
# model.fit(X)

# df_filtered = df_filtered.reset_index(drop=True)


# def films_similaires(titre_film):
#     try:
#         #trouver l'index du film dans df_filtered
#         film_index = df_filtered[df_filtered['title'] == titre_film].index[0]
        
#         #obtenir les films similaires
#         distances, indices = model.kneighbors([X[film_index]])
        
#         print(f"\nFilms similaires à '{titre_film}':\n")
#         for i, index in enumerate(indices[0][1:]):  
#             film = df_filtered.iloc[index]
#             print(f"{i + 1}: {film['title']} (distance: {distances[0][i+1]:.2f})")
#             print(f"   Acteurs: {film['actors']}")
#             print(f"   Genres: {film['genres']}\n")
            
#     except IndexError:
#         print(f"Erreur: Le film '{titre_film}' n'a pas été trouvé dans la base de données.")
#     except Exception as e:
#         print(f"Une erreur s'est produite: {str(e)}")




# # a voir pour mettre dans streamlit(jonathan)

# #réinitialiser les indices de df_filtered


# #exemple d'utilisation
# # films_similaires("Inception")  

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

chemin_bd = r"./bd_ignore/"
df_tmdb = pd.read_csv(chemin_bd + 'resultat/df_tmdb2.csv')  # Dataset des films 

# Fonction films_similaires
def films_similaires(film_nom, df):
    try:
        # Préparer les caractéristiques pour le modèle Nearest Neighbors
        features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
        df_encoded = pd.concat(
            [df[features], pd.get_dummies(df['genres'], prefix='genre')],
            axis=1
        )
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df_encoded)

        # Initialiser le modèle Nearest Neighbors
        model = NearestNeighbors(n_neighbors=11, metric='euclidean')
        model.fit(X)

        # Rechercher l'index du film donné
        film_index = df[df['original_title'].str.lower() == film_nom.lower()].index

        if len(film_index) == 0:
            return None

        # Trouver les films similaires
        distances, indices = model.kneighbors([X[film_index[0]]])

        # # Retourner les résultats
        # resultats = [
        #     {"title": df.iloc[idx]['original_title'], "distance": distances[0][i]}
        #     for i, idx in enumerate(indices[0][1:], start=1)  # Exclure le film d'origine
        # ]
        # return resultats

        # Retourner les résultats avec lien
        resultats = []
        for i, idx in enumerate(indices[0][1:], start=1):  # Exclure le film d'origine
            film_title = df_filtered.iloc[idx]['original_title']
            distance = distances[0][i]
            
            # Récupérer le lien depuis df_tmdb
            lien_film = df_tmdb[df_tmdb['original_title'] == film_title]['homepage'].values
            imdb_id = df_tmdb[df_tmdb['original_title'] == film_title]['imdb_id'].values

            resultats.append({
                "title": film_title,
                "distance": distance,
                "homepage": lien_film[0] if len(lien_film) > 0 else None,
                "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
            })

        return resultats

    except Exception as e:
        st.error(f"Erreur lors du traitement : {e}")
        return None

# Chemin vers les fichiers
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
            # else:
            #     st.error(f"❌ Impossible de trouver des films similaires pour '{film}'.")
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
