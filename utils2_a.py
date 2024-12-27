#copie 26/12/2024 à 10:10
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import pandas as pd
import re

chemin_bd = r"./bd_ignore/"
df_tmdb = pd.read_csv(chemin_bd + 'resultat/df_tmdb2.csv')  # Dataset des films 
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')
# df_filtered = df_filtered.reset_index(drop=True)

# par genre 

def films_similaires2(film_nom, df, df_tmdb):
    try:
        # Étape 1 : Vérifier si le film existe dans la base
        film_data = df[df['title'].str.lower() == film_nom.lower()]
        if film_data.empty:
            return f"Le film '{film_nom}' n'existe pas dans la base."

        # Étape 2 : Récupérer les genres associés au film recherché
        film_genres = film_data.iloc[0]['genres']

        # Nettoyage des genres pour s'assurer qu'ils sont au bon format
        if isinstance(film_genres, str):
            film_genres_list = [genre.strip() for genre in film_genres.split(',')]  # Si c'est une chaîne
        elif isinstance(film_genres, list):
            film_genres_list = film_genres
        else:
            return f"Les genres du film '{film_nom}' ne sont pas au bon format."

        # Debugging : Afficher les genres trouvés
        # st.write(f"Genres du film recherché ({film_nom}):", film_genres_list)

        # Étape 3 : Filtrer les films ayant au moins un genre commun
        df['genres'] = df['genres'].apply(
            lambda x: x.split(', ') if isinstance(x, str) else x
        )  # Assurez-vous que la colonne 'genres' est une liste
        df_genreF = df[df['genres'].apply(
            lambda x: bool(set(film_genres_list) & set(x)) if isinstance(x, list) else False
        )]

        # Réinitialiser les index après filtrage
        df_genreF = df_genreF.reset_index(drop=True)

        # Vérifier si des films sont disponibles après le filtrage
        if df_genreF.empty:
            return f"Aucun film trouvé avec des genres similaires à '{film_nom}'."

        # Debugging : Afficher les films filtrés
        #st.write(f"Films filtrés avec des genres communs :", df_genreF[['title', 'genres']])

        # Étape 4 : Vérifier les colonnes nécessaires pour KNN
        features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
        missing_features = [feature for feature in features if feature not in df_genreF.columns]
        if missing_features:
            return f"Colonnes manquantes pour KNN : {missing_features}"

        # Étape 5 : Normaliser les données
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df_genreF[features])

        # Étape 6 : Initialiser KNN et trouver les films similaires
        model = NearestNeighbors(n_neighbors=6, metric='euclidean')
        model.fit(X)

        # Rechercher l'index du film donné
        film_index = df_genreF[df_genreF['title'].str.lower() == film_nom.lower()].index
        if len(film_index) == 0:
            return f"Le film '{film_nom}' n'est pas dans la base filtrée."

        distances, indices = model.kneighbors([X[film_index[0]]])

        # Étape 7 : Rassembler les résultats
        resultats = []
        for idx in indices[0][1:]:  # Exclure le film d'origine
            film_title = df_genreF.iloc[idx]['title']

            # Récupérer les données additionnelles depuis df_tmdb
            lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
            imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values

            resultats.append({
                "title": film_title,
                "poster_path": lien_poster[0] if len(lien_poster) > 0 else None,
                "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
            })

        return resultats

    except Exception as e:
        return f"Erreur lors du traitement : {e}"


