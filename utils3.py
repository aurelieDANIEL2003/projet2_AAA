import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import pandas as pd

chemin_bd = r"./bd_ignore/"
df_tmdb = pd.read_csv(chemin_bd + 'resultat/df_tmdb2.csv')  # Dataset des films 
df_tmdbF = pd.read_csv(chemin_bd + 'resultat/df_tmdb3.csv')
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
    


def films_similaires2(df_tmdbF, nom_film, k=6):
    try:
        # Vérifier si le film existe
        if nom_film not in df_tmdbF['title'].values:
            return f"Le film '{nom_film}' n'existe pas dans la base de données."
        
        # Obtenir les genres du film cible
        genre2 = df_tmdbF.loc[df_tmdbF['title'] == nom_film, 'genres'].iloc[0]
        
        # Filtrer les films ayant le même genre
        genreF = df_tmdbF[df_tmdbF['genres'].str.contains(genre2, na=False)].copy()
        
        # Si moins de `k` films dans le genre, retourner les films disponibles
        if genreF.shape[0] < k:
            return genreF[['title', 'genres', 'popularity', 'vote_average']].reset_index(drop=True)
        
        # Sélectionner les caractéristiques pour KNN
        features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
        knn_data = genreF[features].fillna(0)  # Remplacer les valeurs manquantes par 0
        
        # Normaliser les données
        scaler = MinMaxScaler()
        knn_data_scaled = scaler.fit_transform(knn_data)
        
        # Appliquer KNN
        knn = NearestNeighbors(n_neighbors=k, metric='euclidean')
        knn.fit(knn_data_scaled)
        
        # Obtenir l'index du film cible dans le DataFrame
        target_index = genreF[genreF['title'] == nom_film].index[0]
        target_features = knn_data_scaled[genreF.index.get_loc(target_index)].reshape(1, -1)
        
        # Trouver les voisins les plus proches
        distances, indices = knn.kneighbors(target_features)
        
        # Préparer les résultats
        resultats = []
        for i, idx in enumerate(indices[0][1:], start=1):  # Exclure le film d'origine
            film_title = genreF.iloc[idx]['title']
            
            # Récupérer le lien depuis df_tmdbF
            lien_poster = df_tmdbF[df_tmdbF['title'] == film_title]['poster_path'].values
            imdb_id = df_tmdbF[df_tmdbF['title'] == film_title]['imdb_id'].values

            resultats.append({
                "title": film_title,
                "poster_path": lien_poster[0] if len(lien_poster) > 0 else None, 
                "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
            })
        
        return resultats
    
    except Exception as e:
        return f"Erreur lors du traitement : {e}"


  

def films_similaires3(film_nom, df, df_tmdb):
    try:
        # Nettoyer la colonne actors
        df = df.dropna(subset=['actors'])  # Supprimer les lignes avec NaN dans 'actors'
        df = df[df['actors'].str.strip() != '']  # Supprimer les lignes où 'actors' est une chaîne vide


        # Préparer les caractéristiques pour le modèle Nearest Neighbors
        features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']

        # Diviser les acteurs en liste pour chaque film
        df['actors_unique'] = df['actors'].apply(lambda x: x.split(', ') if x else [])

        # Encodage pour chaque acteur
        df_encoded = pd.concat(
            [df[features], pd.get_dummies(df['actors_unique'].apply(lambda x: ','.join(x)), prefix='actor')],
            axis=1
        )

        scaler = MinMaxScaler()
        X = scaler.fit_transform(df_encoded)

        # Initialiser le modèle Nearest Neighbors
        model = NearestNeighbors(n_neighbors=6, metric='euclidean')  # Augmenter le nombre de voisins si nécessaire
        model.fit(X)

        # Rechercher l'index du film donné
        film_index = df[df['title'].str.lower() == film_nom.lower()].index

        if len(film_index) == 0:
            st.error(f"❌ Le film '{film_nom}' n'a pas été trouvé.")
            return None

        # Trouver les films similaires
        distances, indices = model.kneighbors([X[film_index[0]]])

        # Récupérer les acteurs du film d'origine
        film_actors = df.iloc[film_index[0]]['actors_unique']

        # Si le film d'origine n'a pas d'acteurs, retourner un message
        if not film_actors:
            st.warning("❌ Aucun acteur n'est défini pour ce film.")
            return None

        # Filtrer les voisins par acteur
        resultats = []
        for i, idx in enumerate(indices[0][1:], start=1):  # Exclure le film d'origine
            film_title = df.iloc[idx]['title']
            neighbor_actors = df.iloc[idx]['actors_unique']

            # Vérifier si au moins un acteur est commun
            if any(actor in neighbor_actors for actor in film_actors):
                lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
                imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values

                resultats.append({
                    "title": film_title,
                    "poster_path": lien_poster[0] if len(lien_poster) > 0 else None,
                    "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
                })

        # Si aucun acteur en commun n'est trouvé
        if not resultats:
            st.warning("❌ Aucun acteur commun trouvé avec d'autres films.")
            return None

        return resultats

    except Exception as e:
        st.error(f"Erreur lors du traitement : {e}")
        return None
