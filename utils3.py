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

def films_similaires3(film_nom, df, df_tmdb):
    try:
        # Étape 1 : Recherche du film correspondant
        film_data = df[df['title'].str.lower() == film_nom.lower()].reset_index(drop=True)

        if film_data.empty:
            return f"Le film '{film_nom}' n'existe pas dans la base."

        # Récupérer les acteurs du film
        film_actors = film_data.iloc[0]['two_actors']

        # Nettoyage des acteurs
        if isinstance(film_actors, str):
            film_actors_list = [actor.strip() for actor in film_actors.split(',')]
        elif isinstance(film_actors, list):
            film_actors_list = film_actors
        else:
            return f"Les acteurs du film '{film_nom}' ne sont pas au bon format."

        # Vérification qu'il y a au moins deux acteurs
        if len(film_actors_list) < 2:
            return f"Le film '{film_nom}' n'a pas suffisamment d'acteurs pour effectuer la recherche."

        # Définir actor1 et actor2
        actor1, actor2 = film_actors_list[0], film_actors_list[1]

        # Fonction pour vérifier la présence d'un acteur
        def verifier_presence(element, mot):
            if isinstance(element, list):
                return any(mot.lower() in acteur.lower() for acteur in element)
            elif isinstance(element, str):
                return mot.lower() in element.lower()
            return False

        # Étape 2 : Recherche de films contenant actor1 et actor2
        df['presence_actor1'] = df['two_actors'].apply(lambda x: verifier_presence(x, actor1))
        df['presence_actor2'] = df['two_actors'].apply(lambda x: verifier_presence(x, actor2))

        df_actor1 = df[df['presence_actor1']].drop(columns=['presence_actor1']).reset_index(drop=True)
        df_actor2 = df[df['presence_actor2']].drop(columns=['presence_actor2']).reset_index(drop=True)

        # Vérification des résultats
        message_actor1 = f"Le film '{film_nom}' est le seul contenant l'acteur '{actor1}'." if len(df_actor1) <= 1 else None
        message_actor2 = f"Le film '{film_nom}' est le seul contenant l'acteur '{actor2}'." if len(df_actor2) <= 1 else None

        if message_actor1 and message_actor2:
            return f"{message_actor1}\n{message_actor2}"

        # Étape 3 : Combiner les résultats pour actor1 et actor2
        df_combined = pd.concat([df_actor1, df_actor2]).drop_duplicates().reset_index(drop=True)

        # Vérification des colonnes nécessaires pour KNN
        features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
        missing_features = [feature for feature in features if feature not in df_combined.columns]
        if missing_features:
            return f"Colonnes manquantes pour KNN : {missing_features}"

        # Normaliser les données
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df_combined[features])

        # Initialiser KNN
        model = NearestNeighbors(n_neighbors=min(len(df_combined), 10), metric='euclidean')
        model.fit(X)

        # Trouver l'index du film dans la base filtrée
        film_index = df_combined[df_combined['title'].str.lower() == film_nom.lower()].index
        if len(film_index) == 0:
            return f"Le film '{film_nom}' n'est pas dans la base filtrée."

        distances, indices = model.kneighbors([X[film_index[0]]])

        # Étape 4 : Collecte des résultats
        resultats = []
        for idx in indices[0][1:]:  # Exclure le film de départ
            film_title = df_combined.iloc[idx]['title']
            if film_title.lower() == film_nom.lower():  # Exclure le film recherché
                continue
            lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
            imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values
            resultats.append({
                "title": film_title,
                "poster_path": lien_poster[0] if len(lien_poster) > 0 else None,
                "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
            })

        # Ajouter les messages spécifiques si actor1 ou actor2 est unique
        if message_actor1:
            resultats.insert(0, {"message": message_actor1})
        if message_actor2:
            resultats.insert(0, {"message": message_actor2})

        return resultats

    except Exception as e:
        return f"Erreur lors du traitement : {e}"



