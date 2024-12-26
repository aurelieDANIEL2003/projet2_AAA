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
df_filtered_actor = pd.read_csv(chemin_bd + 'resultat/df_filtered2.csv')
    
########## par acteur  
def films_similaires3(film_nom, df, df_tmdb):
    try:
        # Normalisation des titres
        df['title'] = df['title'].str.strip().str.lower()
        df_tmdb['title'] = df_tmdb['title'].str.strip().str.lower()

        # Étape 1 : Recherche du film
        film_data = df[df['title'] == film_nom.lower()].reset_index(drop=True)

        if film_data.empty:
            return [{"message": f"Le film '{film_nom}' n'existe pas dans la base."}]

        # Récupérer les acteurs du film
        film_actors = film_data.iloc[0]['two_actors']

        # Nettoyage des acteurs
        if isinstance(film_actors, str):
            film_actors_list = [actor.strip() for actor in film_actors.split(',')]
        elif isinstance(film_actors, list):
            film_actors_list = film_actors
        else:
            return [{"message": f"Les acteurs du film '{film_nom}' ne sont pas au bon format."}]

        # Vérifier qu'il y a au moins deux acteurs
        if len(film_actors_list) < 2:
            return [{"message": f"Le film '{film_nom}' n'a pas suffisamment d'acteurs pour effectuer la recherche."}]

        actor1, actor2 = film_actors_list[0], film_actors_list[1]

        # Étape 2 : Trouver les films contenant les acteurs
        def verifier_presence(element, mot):
            if isinstance(element, list):
                return any(mot.lower() in acteur.lower() for acteur in element)
            elif isinstance(element, str):
                return mot.lower() in element.lower()
            return False

        df['contains_actor1'] = df['two_actors'].apply(lambda x: verifier_presence(x, actor1))
        df['contains_actor2'] = df['two_actors'].apply(lambda x: verifier_presence(x, actor2))

        # Combiner les films contenant actor1 et actor2
        df_combined = pd.concat([
            df[df['contains_actor1']],
            df[df['contains_actor2']]
        ]).drop_duplicates().reset_index(drop=True)

        # Supprimer les colonnes temporaires
        df_combined = df_combined.drop(columns=['contains_actor1', 'contains_actor2'], errors='ignore')
        print(df_combined)

        
        # Étape 3 : Collecte des résultats
        resultats = []
        for _, row in df_combined.iterrows():
            if row['title'] == film_nom.lower():
                continue

            film_title = row['title']
            lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
            imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values

            resultats.append({
                "title": film_title,
                "poster_path": lien_poster[0] if len(lien_poster) > 0 else None,
                "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
            })

        # Retourner la liste des résultats
        return resultats if resultats else [{"message": "Aucun film trouvé avec ces acteurs."}]

    except Exception as e:
        return [{"message": f"Erreur lors du traitement : {str(e)}"}]







