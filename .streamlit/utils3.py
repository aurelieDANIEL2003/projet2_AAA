########## par acteur

import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import pandas as pd
import re


def films_par_acteur(acteur_nom, df, df_tmdb):
    """
    Trouver les films où un acteur donné est présent.
    """
    acteur_nom = acteur_nom.strip().lower()  # Nettoyer et uniformiser le nom

    # Nettoyage supplémentaire de la colonne two_actors
    df['two_actors'] = df['two_actors'].str.strip().str.lower()

    # Filtrer les films où l'acteur apparaît
    films_acteur = []
    for _, row in df.iterrows():
        if pd.notna(row['two_actors']):
            # Vérifier si l'acteur est dans la liste
            if acteur_nom in row['two_actors']:
                # Récupérer les informations du film
                titre = row['title']
                imdb_id = row.get('imdb_id', None)
                poster_path = row.get('poster_path', None)
                films_acteur.append({
                    "title": titre,
                    "imdb_id": imdb_id,
                    "poster_path": poster_path
                })

    if not films_acteur:
        return f"Aucun film trouvé pour l'acteur '{acteur_nom}'."

    # Créer un DataFrame pour afficher les résultats
    df_result = pd.DataFrame(films_acteur)
    return df_result


