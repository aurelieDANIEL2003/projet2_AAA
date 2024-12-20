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
    
####### fonction de recommandation par genre

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



########## par acteur  

def films_similaires3(film_nom, df, df_tmdb):
    try:
        # Étape 1 : Vérifier si le film recherché existe dans la base
        film_data = df[df['title'].str.lower() == film_nom.lower()]
        if film_data.empty:
            return f"Le film '{film_nom}' n'existe pas dans la base."
        
        # Debugging : Vérifier les données du film recherché
        st.write("Données du film recherché :", film_data)

        # Étape 2 : Récupérer les acteurs du film recherché
        two_actors = film_data.iloc[0]['two_actors']
        if isinstance(two_actors, str):
            # Convertir les acteurs en vraie liste si nécessaire
            two_actors = eval(two_actors)
        if not isinstance(two_actors, list):
            two_actors = []

        st.write(f"Acteurs du film recherché ({film_nom}) :", two_actors)

        # Extraire les deux acteurs ou gérer l'absence
        actor1 = two_actors[0].strip() if len(two_actors) > 0 else None
        actor2 = two_actors[1].strip() if len(two_actors) > 1 else None

        st.write(f"Acteur 1 : {actor1}, Acteur 2 : {actor2}")

        if not actor1 and not actor2:
            return f"Les acteurs pour le film '{film_nom}' ne sont pas disponibles ou pas au bon format."

        # Étape 3 : Filtrer les films avec des acteurs communs
        df_actor1 = df[df['two_actors'].apply(lambda x: actor1 in x if isinstance(x, list) else False)] if actor1 else pd.DataFrame()
        df_actor2 = df[df['two_actors'].apply(lambda x: actor2 in x if isinstance(x, list) else False)] if actor2 else pd.DataFrame()

        # Fusionner les deux DataFrames (sans doublons)
        df_filtered_actors = pd.concat([df_actor1, df_actor2]).drop_duplicates().reset_index(drop=True)

        st.write("Films filtrés par acteurs communs :", df_filtered_actors[['title', 'two_actors']])

        # Vérifier si des films ont été trouvés après filtrage
        if df_filtered_actors.empty:
            return f"Aucun film trouvé avec les acteurs communs à '{film_nom}'."

        # Étape 4 : Vérifier les colonnes nécessaires pour KNN
        features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
        if not all(feature in df_filtered_actors.columns for feature in features):
            return f"Certaines colonnes nécessaires pour KNN sont manquantes : {features}"

        # Étape 5 : Normaliser les données
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df_filtered_actors[features])

        # Étape 6 : Initialiser le modèle KNN et trouver les films similaires
        model = NearestNeighbors(n_neighbors=6, metric='euclidean')
        model.fit(X)

        # Rechercher l'index du film donné
        film_index = df_filtered_actors[df_filtered_actors['title'].str.lower() == film_nom.lower()].index
        if len(film_index) == 0:
            return f"Le film '{film_nom}' n'est pas dans la base filtrée."

        distances, indices = model.kneighbors([X[film_index[0]]])

        # Étape 7 : Rassembler les résultats
        resultats = []
        for idx in indices[0][1:]:  # Exclure le film d'origine
            film_title = df_filtered_actors.iloc[idx]['title']

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
        st.error(f"Erreur lors du traitement : {e}")
        return None

