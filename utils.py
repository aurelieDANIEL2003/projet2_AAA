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

# Fonction films_similaires par vote
chemin_bd = r"./bd_ignore/"
df_tmdb = pd.read_csv(chemin_bd + 'resultat/df_tmdb2.csv')  # Dataset des films 
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')
# df_filtered = df_filtered.reset_index(drop=True)

# Fonction films_similaires par vote
def films_similaires(film_nom, df):
    try:
        # Normaliser les titres pour éviter les problèmes de correspondance
        df_tmdb['title_normalized'] = df_tmdb['title'].str.lower().str.strip()
        df['title_normalized'] = df['title'].str.lower().str.strip()

        # Préparer les caractéristiques pour le modèle Nearest Neighbors
        features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
        df_encoded = pd.concat(
            [df[features], pd.get_dummies(df['genres'], prefix='genre')],
            axis=1
        )
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df_encoded)

        # Initialiser le modèle Nearest Neighbors
        model = NearestNeighbors(n_neighbors=6, metric='euclidean')
        model.fit(X)

        # Rechercher l'index du film donné
        film_index = df[df['title_normalized'] == film_nom.lower().strip()].index

        if len(film_index) == 0:
            return None

        # Trouver les films similaires
        distances, indices = model.kneighbors([X[film_index[0]]])

        # Retourner les résultats avec lien
        resultats = []
        for idx in indices[0][1:]:  # Exclure le film d'origine
            film_title = df.iloc[idx]['title']

            try:
                # Récupérer le lien depuis df_tmdb
                lien_poster = df_tmdb[df_tmdb['title_normalized'] == film_title.lower()]['poster_path'].values
                imdb_id = df_tmdb[df_tmdb['title_normalized'] == film_title.lower()]['imdb_id'].values

                resultats.append({
                    "title": film_title,
                    "poster_path": lien_poster[0] if len(lien_poster) > 0 else None,
                    "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
                })
            except IndexError:
                st.warning(f"Impossible de trouver les informations pour le film : {film_title}")

        return resultats

    except Exception as e:
        st.error(f"Erreur lors du traitement : {e}")
        return None

    