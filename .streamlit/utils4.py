#copie 02/01
import ast  # Pour convertir des chaînes en listes Python
import pandas as pd

def search_actor(actor_nom, df, df_tmdb):
    """
    Rechercher les films liés à un acteur en utilisant une liste unique d'acteurs.
    
    :param actor_nom: Nom ou partie du nom de l'acteur à rechercher
    :param df: DataFrame principal contenant les informations sur les films et les acteurs
    :param df_tmdb: DataFrame complémentaire contenant les posters et IDs IMDb
    :return: DataFrame contenant les résultats de la recherche
    """
    # Étape 1 : Génération de la liste des acteurs uniques
    list_actor = df['two_actors'].apply(
        lambda x: [actor.strip() for actor in ast.literal_eval(x)] if pd.notna(x) else []
    )
    actor_unique = set()
    for actor in list_actor:
        actor_unique.update(actor)
    list_actor_unique = sorted(list(actor_unique))  # Liste triée pour une meilleure présentation

    # Étape 2 : Vérifier si l'acteur existe dans la liste des acteurs uniques
    if actor_nom.lower() not in [actor.lower() for actor in list_actor_unique]:
        return pd.DataFrame()  # Retourne un DataFrame vide si l'acteur n'est pas trouvé

    # Étape 3 : Filtrer les films contenant cet acteur
    results = []
    for _, row in df.iterrows():
        if pd.notna(row['two_actors']):
            actor_list = [actor.strip() for actor in ast.literal_eval(row['two_actors'])]
            if actor_nom in actor_list:
                results.append({
                    "title": row['title'],
                    "poster_path": row.get('poster_path', None),
                    "imdb_id": row.get('imdb_id', None)
                })

    # Étape 4 : Créer un DataFrame des résultats
    results_df = pd.DataFrame(results)

    # Ajouter les colonnes poster_path et imdb_id depuis df_tmdb
    if not results_df.empty:
        results_df = results_df.merge(
            df_tmdb[['title', 'poster_path', 'imdb_id']],
            on='title',
            how='left'
        )

    return results_df
