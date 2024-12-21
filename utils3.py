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
        # Étape 1 : Recherche des films correspondant au titre saisi
        # Recherche insensible à la casse pour les films contenant le texte saisi
        films_potentiels = df[df['title'].str.contains(film_nom, case=False, na=False)].reset_index(drop=True)

        # Si aucun film correspondant n'est trouvé
        if films_potentiels.empty:
            return f"Aucun film trouvé contenant '{film_nom}'."

        # Interface interactive : l'utilisateur sélectionne le film exact qu'il recherche
        st.write("Plusieurs films correspondent à votre recherche. Veuillez sélectionner celui que vous recherchez :")
        film_selection = st.radio("Sélectionnez un film :", films_potentiels['title'].tolist())

        # Mettre à jour `film_nom` avec le titre sélectionné
        film_selection = films_potentiels

        # Récupération des données du film sélectionné
        film_data = films_potentiels[films_potentiels['title'] == film_recherche]
        if film_data.empty:
            return f"Le film '{film_nom}' n'existe pas dans la base."

        # Étape 2 : Récupérer les acteurs associés au film sélectionné
        film_actors = film_data.iloc[0]['two_actors']

        # Nettoyage des acteurs pour s'assurer qu'ils sont au bon format
        if isinstance(film_actors, str):
            film_actors_list = [actor.strip() for actor in film_actors.split(',')]
        elif isinstance(film_actors, list):
            film_actors_list = film_actors
        else:
            return f"Les acteurs du film '{film_recherche}' ne sont pas au bon format."

        # Vérifier qu'au moins deux acteurs existent
        if len(film_actors_list) < 2:
            return f"Le film '{film_recherche}' n'a pas suffisamment d'acteurs pour effectuer la recherche."

        # Fonction pour vérifier la présence d'un acteur
        def verifier_presence(element, mot):
            if isinstance(element, list):
                return any(mot.lower() in acteur.lower() for acteur in element)
            elif isinstance(element, str):
                return mot.lower() in element.lower()
            return False

        # Recherche pour actor1 et actor2
        actor1, actor2 = film_actors_list[0], film_actors_list[1]
        df['presence_actor1'] = df['two_actors'].apply(lambda x: verifier_presence(x, actor1))
        df['presence_actor2'] = df['two_actors'].apply(lambda x: verifier_presence(x, actor2))

        df_actor1 = df[df['presence_actor1']].drop(columns=['presence_actor1']).reset_index(drop=True)
        df_actor2 = df[df['presence_actor2']].drop(columns=['presence_actor2']).reset_index(drop=True)

        # Vérification des résultats pour actor1 et actor2
        message_actor1 = f"Le film '{film_recherche}' est le seul contenant l'acteur '{actor1}'." if len(df_actor1) <= 1 else None
        message_actor2 = f"Le film '{film_recherche}' est le seul contenant l'acteur '{actor2}'." if len(df_actor2) <= 1 else None

        if message_actor1 and message_actor2:
            return f"{message_actor1}\n{message_actor2}"

        # Combiner les résultats pour actor1 et actor2
        df_combined = pd.concat([df_actor1, df_actor2]).drop_duplicates().reset_index(drop=True)

        # Vérifier les colonnes nécessaires pour KNN
        features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
        missing_features = [feature for feature in features if feature not in df_combined.columns]
        if missing_features:
            return f"Colonnes manquantes pour KNN : {missing_features}"

        # Normaliser les données
        scaler = MinMaxScaler()
        X = scaler.fit_transform(df_combined[features])

        # Initialiser KNN et trouver les films similaires
        model = NearestNeighbors(n_neighbors=len(df_combined), metric='euclidean')
        model.fit(X)

        film_index = df_combined[df_combined['title'] == film_recherche].index
        if len(film_index) == 0:
            return f"Le film '{film_recherche}' n'est pas dans la base filtrée."

        distances, indices = model.kneighbors([X[film_index[0]]])

        resultats = []
        for idx in indices[0][1:]:
            film_title = df_combined.iloc[idx]['title']
            lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
            imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values
            resultats.append({
                "title": film_title,
                "poster_path": lien_poster[0] if len(lien_poster) > 0 else None,
                "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
            })

        if message_actor1:
            resultats.insert(0, {"message": message_actor1})
        if message_actor2:
            resultats.insert(0, {"message": message_actor2})

        return resultats

    except Exception as e:
        return f"Erreur lors du traitement : {e}"




# def films_similaires3(film_nom, df, df_tmdb):
#     try:
#         # Étape 1 : Recherche des films correspondant au titre saisi
#         # Recherche insensible à la casse pour les films contenant le texte saisi
#         films_potentiels = df[df['title'].str.contains(film_nom, case=False, na=False)].reset_index(drop=True)

#         # Si aucun film correspondant n'est trouvé
#         if films_potentiels.empty:
#             return f"Aucun film trouvé contenant '{film_nom}'."

#         # Interface interactive : l'utilisateur sélectionne le film exact qu'il recherche
#         st.write("Plusieurs films correspondent à votre recherche. Veuillez sélectionner celui que vous recherchez :")
#         film_selection = st.radio("Sélectionnez un film :", films_potentiels['title'].tolist())

#         # Récupération des données du film sélectionné
#         film_data = films_potentiels[films_potentiels['title'] == film_selection]
#         if film_data.empty:
#             return f"Le film '{film_selection}' n'existe pas dans la base."

#         # Étape 2 : Récupérer les acteurs associés au film sélectionné
#         film_actors = film_data.iloc[0]['two_actors']

#         # Nettoyage des acteurs pour s'assurer qu'ils sont au bon format
#         if isinstance(film_actors, str):
#             film_actors_list = [actor.strip() for actor in film_actors.split(',')]
#         elif isinstance(film_actors, list):
#             film_actors_list = film_actors
#         else:
#             return f"Les acteurs du film '{film_nom}' ne sont pas au bon format."

#         # Vérifier qu'au moins deux acteurs existent
#         if len(film_actors_list) < 2:
#             return f"Le film '{film_nom}' n'a pas suffisamment d'acteurs pour effectuer la recherche."

#         # Fonction pour vérifier la présence d'un acteur
#         def verifier_presence(element, mot):
#             if isinstance(element, list):
#                 return any(mot.lower() in acteur.lower() for acteur in element)
#             elif isinstance(element, str):
#                 return mot.lower() in element.lower()
#             return False

#         # Recherche pour actor1 et actor2
#         actor1, actor2 = film_actors_list[0], film_actors_list[1]
#         df['presence_actor1'] = df['two_actors'].apply(lambda x: verifier_presence(x, actor1))
#         df['presence_actor2'] = df['two_actors'].apply(lambda x: verifier_presence(x, actor2))

#         df_actor1 = df[df['presence_actor1']].drop(columns=['presence_actor1']).reset_index(drop=True)
#         df_actor2 = df[df['presence_actor2']].drop(columns=['presence_actor2']).reset_index(drop=True)

#         # Vérification des résultats pour actor1 et actor2
#         message_actor1 = f"Le film '{film_selection}' est le seul contenant l'acteur '{actor1}'." if len(df_actor1) <= 1 else None
#         message_actor2 = f"Le film '{film_selection}' est le seul contenant l'acteur '{actor2}'." if len(df_actor2) <= 1 else None

#         if message_actor1 and message_actor2:
#             return f"{message_actor1}\n{message_actor2}"

#         # Combiner les résultats pour actor1 et actor2
#         df_combined = pd.concat([df_actor1, df_actor2]).drop_duplicates().reset_index(drop=True)

#         # Vérifier les colonnes nécessaires pour KNN
#         features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
#         missing_features = [feature for feature in features if feature not in df_combined.columns]
#         if missing_features:
#             return f"Colonnes manquantes pour KNN : {missing_features}"

#         # Normaliser les données
#         scaler = MinMaxScaler()
#         X = scaler.fit_transform(df_combined[features])

#         # Initialiser KNN et trouver les films similaires
#         model = NearestNeighbors(n_neighbors=len(df_combined), metric='euclidean')
#         model.fit(X)

#         film_index = df_combined[df_combined['title'] == film_selection].index
#         if len(film_index) == 0:
#             return f"Le film '{film_selection}' n'est pas dans la base filtrée."

#         distances, indices = model.kneighbors([X[film_index[0]]])

#         resultats = []
#         for idx in indices[0][1:]:
#             film_title = df_combined.iloc[idx]['title']
#             lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
#             imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values
#             resultats.append({
#                 "title": film_title,
#                 "poster_path": lien_poster[0] if len(lien_poster) > 0 else None,
#                 "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
#             })

#         if message_actor1:
#             resultats.insert(0, {"message": message_actor1})
#         if message_actor2:
#             resultats.insert(0, {"message": message_actor2})

#         return resultats

#     except Exception as e:
#         return f"Erreur lors du traitement : {e}"


# # 2e essai

# # def films_similaires3(film_nom, df, df_tmdb):
# #     try:
# #         # Étape 1 : Vérifier si le film existe dans la base
# #         film_data = df[df['title'].str.lower() == film_nom.lower()]
# #         if film_data.empty:
# #             return f"Le film '{film_nom}' n'existe pas dans la base."

# #         # Étape 2 : Récupérer les acteurs associés au film recherché
# #         film_actors = film_data.iloc[0]['two_actors']

# #         # Nettoyage des acteurs pour s'assurer qu'ils sont au bon format
# #         if isinstance(film_actors, str):
# #             film_actors_list = [actor.strip() for actor in film_actors.split(',')]  # Si c'est une chaîne
# #         elif isinstance(film_actors, list):
# #             film_actors_list = film_actors
# #         else:
# #             return f"Les acteurs du film '{film_nom}' ne sont pas au bon format."

# #         # Vérifier qu'au moins deux acteurs existent
# #         if len(film_actors_list) < 2:
# #             return f"Le film '{film_nom}' n'a pas suffisamment d'acteurs pour effectuer la recherche."

# #         # Étape 3 : Fonction pour vérifier la présence d'un acteur
# #         def verifier_presence(element, mot):
# #             if isinstance(element, list):  # Si c'est une liste
# #                 return any(mot.lower() in acteur.lower() for acteur in element)
# #             elif isinstance(element, str):  # Si c'est une chaîne
# #                 return mot.lower() in element.lower()
# #             return False

# #         # Rechercher des films contenant actor1
# #         actor1 = film_actors_list[0]
# #         df['presence_actor1'] = df['two_actors'].apply(lambda x: verifier_presence(x, actor1))
# #         df_actor1 = df[df['presence_actor1']].drop(columns=['presence_actor1']).reset_index(drop=True)

# #         # Rechercher des films contenant actor2
# #         actor2 = film_actors_list[1]
# #         df['presence_actor2'] = df['two_actors'].apply(lambda x: verifier_presence(x, actor2))
# #         df_actor2 = df[df['presence_actor2']].drop(columns=['presence_actor2']).reset_index(drop=True)

# #         # Vérifier les résultats pour actor1
# #         if len(df_actor1) <= 1:  # Le film recherché est le seul avec cet acteur
# #             message_actor1 = f"Le film '{film_nom}' est le seul contenant l'acteur '{actor1}'."
# #         else:
# #             message_actor1 = None

# #         # Vérifier les résultats pour actor2
# #         if len(df_actor2) <= 1:  # Le film recherché est le seul avec cet acteur
# #             message_actor2 = f"Le film '{film_nom}' est le seul contenant l'acteur '{actor2}'."
# #         else:
# #             message_actor2 = None

# #         # Si aucun autre film avec actor1 et actor2 n'est trouvé
# #         if message_actor1 and message_actor2:
# #             return f"{message_actor1}\n{message_actor2}"

# #         # Combiner les films contenant actor1 et actor2 pour KNN
# #         df_combined = pd.concat([df_actor1, df_actor2]).drop_duplicates().reset_index(drop=True)

# #         # Vérifier les colonnes nécessaires pour KNN
# #         features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
# #         missing_features = [feature for feature in features if feature not in df_combined.columns]
# #         if missing_features:
# #             return f"Colonnes manquantes pour KNN : {missing_features}"

# #         # Normaliser les données
# #         scaler = MinMaxScaler()
# #         X = scaler.fit_transform(df_combined[features])

# #         # Initialiser KNN et trouver les films similaires
# #         model = NearestNeighbors(n_neighbors=len(df_combined), metric='euclidean')
# #         model.fit(X)

# #         # Rechercher l'index du film donné
# #         film_index = df_combined[df_combined['title'].str.lower() == film_nom.lower()].index
# #         if len(film_index) == 0:
# #             return f"Le film '{film_nom}' n'est pas dans la base filtrée."

# #         distances, indices = model.kneighbors([X[film_index[0]]])

# #         # Rassembler les résultats
# #         resultats = []
# #         for idx in indices[0][1:]:  # Exclure le film d'origine
# #             film_title = df_combined.iloc[idx]['title']

# #             # Récupérer les données additionnelles depuis df_tmdb
# #             lien_poster = df_tmdb[df_tmdb['title'] == film_title]['poster_path'].values
# #             imdb_id = df_tmdb[df_tmdb['title'] == film_title]['imdb_id'].values

# #             resultats.append({
# #                 "title": film_title,
# #                 "poster_path": lien_poster[0] if len(lien_poster) > 0 else None,
# #                 "imdb_id": imdb_id[0] if len(imdb_id) > 0 else None
# #             })

# #         # Ajouter les messages spécifiques pour actor1 et actor2 dans les résultats
# #         if message_actor1:
# #             resultats.insert(0, {"message": message_actor1})
# #         if message_actor2:
# #             resultats.insert(0, {"message": message_actor2})

# #         return resultats

# #     except Exception as e:
# #         return f"Erreur lors du traitement : {e}"


