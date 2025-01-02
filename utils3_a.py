
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

########## par acteur

def films_similaires_par_acteur(acteur_nom, df, df_tmdb):
    """
    Rechercher des films similaires à partir d'un acteur donné.
    """
    # Étape 1 : Recherche des films avec l'acteur
    resultats = []
    for _, row in df.iterrows():
        actors = row.get('actors', '')
        if isinstance(actors, str) and acteur_nom.lower() in actors.lower():  # Vérifier si l'acteur est présent
            resultats.append({
                "title": row['title'],
                "poster_path": row.get('poster_path', None),
                "imdb_id": row.get('imdb_id', None)
            })

    # Si aucun résultat trouvé pour l'acteur
    if not resultats:
        return []

    # Étape 2 : Création du DataFrame pour les similarités
    df_actor_films = pd.DataFrame(resultats)
    features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']

    # Vérification des colonnes nécessaires pour KNN
    missing_features = [feature for feature in features if feature not in df.columns]
    if missing_features:
        return f"Colonnes manquantes pour KNN : {missing_features}"

    # Normaliser les données
    scaler = MinMaxScaler()
    X = scaler.fit_transform(df[features])

    # Initialiser KNN
    model = NearestNeighbors(n_neighbors=min(len(df), 10), metric='euclidean')
    model.fit(X)

    # Trouver l'index des films avec cet acteur
    film_indices = df[df['title'].str.lower().isin([res['title'].lower() for res in resultats])].index

    similar_results = []
    for film_index in film_indices:
        distances, indices = model.kneighbors([X[film_index]])
        for idx in indices[0][1:]:  # Exclure le film de départ
            film_title = df.iloc[idx]['title']
            if film_title.lower() not in [res['title'].lower() for res in similar_results]:
                lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
                imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values
                similar_results.append({
                    "title": film_title,
                    "poster_path": lien_poster[0] if len(lien_poster) > 0 else None,
                    "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
                })

    return similar_results
