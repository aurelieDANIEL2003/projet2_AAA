#copie 02/01
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import pandas as pd
from utils3 import films_par_acteur
import ast

import re

chemin_bd = r"./bd_ignore/"
df_tmdb = pd.read_csv(chemin_bd + 'resultat/df_tmdb2.csv')  # Dataset des films 
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')
df_filtered = df_filtered.reset_index(drop=True)
df_filtered_actor = pd.read_csv(chemin_bd + 'resultat/df_filtered2.csv')
    
########## par acteur  
def films_similaires3(film_nom, df, df_tmdb, list_actor_unique):
    try:
        # Normalisation des titres
        df['title'] = df['title'].str.strip().str.lower()
        df_tmdb['title'] = df_tmdb['title'].str.strip().str.lower()
        film_nom = film_nom.strip().lower()

        # Étape 1 : Recherche du film
        film_data = df[df['title'] == film_nom].reset_index(drop=True)

        if film_data.empty:
            return [{"message": f"Le film '{film_nom}' n'existe pas dans la base."}]

        # Récupérer les acteurs du film
        film_actors = film_data.iloc[0]['two_actors']

        # Nettoyage des acteurs
        if isinstance(film_actors, str):
            try:
                film_actors_list = [actor.strip() for actor in ast.literal_eval(film_actors)]
            except Exception:
                film_actors_list = [actor.strip() for actor in film_actors.split(',')]
        elif isinstance(film_actors, list):
            film_actors_list = film_actors
        else:
            return [{"message": f"Les acteurs du film '{film_nom}' ne sont pas au bon format."}]
        


  # Vérification dans list_actor_unique
        filtered_actors = [actor for actor in film_actors_list if actor in list_actor_unique]

        if not filtered_actors:
            return [{"message": f"Aucun acteur du film '{film_nom}' n'est dans la liste des acteurs uniques."}]

        # Étape 2 : Recherche des films avec ces acteurs
        films_acteur = []
        for acteur in filtered_actors:
            for _, row in df.iterrows():
                if pd.notna(row['two_actors']):
                    # Convertir les acteurs en liste
                    try:
                        row_actors = [actor.strip() for actor in ast.literal_eval(row['two_actors'])]
                    except Exception:
                        row_actors = [actor.strip() for actor in row['two_actors'].split(',')]


                    if acteur in row_actors:
                        films_acteur.append({
                            "title": row['title'],
                            "imdb_id": row.get('imdb_id', None),
                            "poster_path": row.get('poster_path', None)
                        })

        # Suppression des doublons et exclusion du film de départ
        films_acteur_df = pd.DataFrame(films_acteur).drop_duplicates(subset='title')
        films_acteur_df = films_acteur_df[films_acteur_df['title'] != film_nom.lower()]

        if films_acteur_df.empty:
            return [{"message": f"Aucun film trouvé avec les acteurs du film '{film_nom}'."}]

        # Ajout des colonnes poster_path et imdb_id depuis df_tmdb
        films_acteur_df = films_acteur_df.merge(
            df_tmdb[['title', 'poster_path', 'imdb_id']],
            on='title',
            how='left'
        )

        # Conversion en liste de dictionnaires pour le retour
        resultats = films_acteur_df.to_dict(orient='records')
        return resultats

    except Exception as e:
        return [{"message": f"Erreur lors du traitement : {str(e)}"}]







