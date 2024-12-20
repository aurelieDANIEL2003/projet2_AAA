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
        model = NearestNeighbors(n_neighbors=6, metric='euclidean')
        model.fit(X)

        # Rechercher l'index du film donné
        film_index = df[df['title'].str.lower() == film_nom.lower()].index

        if len(film_index) == 0:
            return None

        # Trouver les films similaires
        distances, indices = model.kneighbors([X[film_index[0]]])

        # Retourner les résultats avec lien
        resultats = []
        for i, idx in enumerate(indices[0][1:], start=1):  # Exclure le film d'origine
            film_title = df_filtered.iloc[idx]['title']
            #distance = distances[0][i]
            
            # Récupérer le lien depuis df_tmdb
            lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
            imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values

            resultats.append({
                "title": film_title,
                #"distance": distance,
                "poster_path": lien_poster[0] if len(lien_poster) > 0 else None, 
                "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
            })

        return resultats

    except Exception as e:
        st.error(f"Erreur lors du traitement : {e}")
        return None
    
# fonction de recommandation par genre

def films_similaires2(film_nom, df, df_tmdb):
    try:
              
        # Obtenir le genre du film cible
        genre2 = df.loc[df['title'] == film_nom, 'genres'].iloc[0]

        # Vérifier si le genre est valide
        if pd.isna(genre2):
            return f"Le film '{film_nom}' n'a pas de genre attribué."
        
        # Filtrer les films ayant le même genre
        df_genreF = df[df['genres'].str.contains(re.escape(genre2), na=False, case=False)].copy()

        # Préparer les caractéristiques pour le modèle Nearest Neighbors
        features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
        df_encoded = pd.concat(
            [df_genreF[features], pd.get_dummies(df_genreF['genres'], prefix='genre')],
            axis=1
        )
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df_encoded)

        # Initialiser le modèle Nearest Neighbors
        model = NearestNeighbors(n_neighbors=6, metric='euclidean')
        model.fit(X)

        # Rechercher l'index du film donné
        film_index = df_genreF[df_genreF['title'].str.lower() == film_nom.lower()].index[1]

        if len(film_index) == 0:
            return None

        # Trouver les films similaires
        distances, indices = model.kneighbors([X[film_index[0]]])

        # Retourner les résultats avec lien
        resultats = []
        for i, idx in enumerate(indices[0][1:], start=1):  # Exclure le film d'origine
            film_title = df_genreF.iloc[idx]['title']
                       
            # Récupérer le lien depuis df_tmdb
            lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
            imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values

            resultats.append({
                "title": film_title,
                #"distance": distance,
                "poster_path": lien_poster[0] if len(lien_poster) > 0 else None, 
                "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
            })

        return resultats

    except Exception as e:
        st.error(f"Erreur lors du traitement : {e}")
        return None
     
  

def films_similaires3(film_nom, df):
    try:
              
        # Obtenir le genre du film cible
        actors2 = df.loc[df['title'] == film_nom, 'actors'].iloc[0]
        
        # Filtrer les films ayant le même genre
        df_actorsF = df[df['actors'].str.contains(actor2, na=False)].copy()

        # Préparer les caractéristiques pour le modèle Nearest Neighbors
        features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
        df_encoded = pd.concat(
            [df_actorsF[features], pd.get_dummies(df_actorsF['actors'], prefix='acteur')],
            axis=1
        )
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df_encoded)

        # Initialiser le modèle Nearest Neighbors
        model = NearestNeighbors(n_neighbors=6, metric='euclidean')
        model.fit(X)

        # Rechercher l'index du film donné
        film_index = df_actorsF[df_actorsF['title'].str.lower() == film_nom.lower()].index

        if len(film_index) == 0:
            return None

        # Trouver les films similaires
        distances, indices = model.kneighbors([X[film_index[0]]])

        # Retourner les résultats avec lien
        resultats = []
        for i, idx in enumerate(indices[0][1:], start=1):  # Exclure le film d'origine
            film_title = df_filtered.iloc[idx]['title']
                       
            # Récupérer le lien depuis df_tmdb
            lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
            imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values

            resultats.append({
                "title": film_title,
                #"distance": distance,
                "poster_path": lien_poster[0] if len(lien_poster) > 0 else None, 
                "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
            })

        return resultats

    except Exception as e:
        st.error(f"Erreur lors du traitement : {e}")
        return None