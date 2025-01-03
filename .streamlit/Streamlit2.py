import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import random
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from utils1 import films_similaires
from utils2 import films_similaires2
from utils3 import films_par_acteur
from utils4 import search_actor
from utils5 import films_similaires3
import ast 
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import base64
import re

import pandas as pd
import requests

def download_file(url, output_file):
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_file, "wb") as file:
            file.write(response.content)
        return True
    else:
        return False

# URLs des fichiers à télécharger
file_urls = {
    "df_tmdb2": "https://drive.google.com/uc?id=1QF-nUGIoyo8eEecSOV2iDmMzfmU2X_eM&export=download",
    "df_filtered": "https://drive.google.com/uc?id=1qMIPty8HywHHLC2aW8dWYAMxiNIxCrWk&export=download",
    "df_filtered_actor": "https://drive.google.com/uc?id=1SUFDuf9ibJIkt3TdwVW54Yd-_89rHKzN&export=download"
}

# Télécharger et charger les fichiers
dataframes = {}
for name, url in file_urls.items():
    if download_file(url, f"{name}.csv"):
        try:
            dataframes[name] = pd.read_csv(f"{name}.csv")
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier {name}: {e}")
    else:
        st.error(f"Erreur lors du téléchargement du fichier {name}.")

# Assignation des DataFrames
df_tmdb = dataframes.get("df_tmdb2")
df_filtered = dataframes.get("df_filtered")
df_filtered_actor = dataframes.get("df_filtered_actor")

# Vérification des fichiers chargés
if not df_tmdb.empty and not df_filtered.empty:
    # Normalisation des titres pour éviter les problèmes de correspondance
    df_tmdb['title_normalized'] = df_tmdb['title'].str.lower().str.strip()
    df_filtered['title_normalized'] = df_filtered['title'].str.lower().str.strip()
else:
    st.error("Certains fichiers nécessaires sont manquants ou vides.")

# les images
image_url = "https://drive.google.com/uc?id=1_CMnzTFdhjMzlcHUT7uhP5j-P2O2IfNu"
image_affiche = "https://drive.google.com/uc?id=1pH6tNjNdKlnr6nRORncGIfMf0ZLaA1Tk&export=download"
top3 = "https://drive.google.com/uc?id=1RKHLneSZN__XAJ-QfZw7nqZUQUsVCIb0&export=download"
podium = "https://drive.google.com/uc?id=1Lq-zVIU7ZKKOzGruHWzHf0N6SHlqeTVR&export=download"


# Normaliser les titres pour éviter les problèmes de correspondance
df_tmdb['title_normalized'] = df_tmdb['title'].str.lower().str.strip()
df_filtered['title_normalized'] = df_filtered['title'].str.lower().str.strip()


# Menu latéral
with st.sidebar:
    selection = option_menu(
        menu_title=None,
        options=["Accueil", "Recommandation par film", "Recommandation par acteur", "Surprise", "KPI"],
        icons=["house", "film", "film", "film", "bar-chart"],
        menu_icon="cast",
        default_index=0
    )

   
# Page d'accueil
if selection == "Accueil":
    st.title('Bienvenue au CINÉMA ! 🎥')
    st.image(image_url, width=500)
    st.write("""
        Recommandations personnalisées de films Made by Aurélie, Anissa et Anaëlle. 🎬
    """)

# Page de recommandation film
elif selection == "Recommandation par film":
    st.title("Recommandation par film")
    
    # Recherche d'un film
    film_nom = st.text_input("Cherchez un film par titre ou par partie de titre :")


    # # Fonction pour rechercher des titres
    def search_movies(film_nom, df, df_tmdb):
        """
        Recherche les films correspondant au titre ou partie de titre donné.
        """
        # Rechercher les films correspondants dans df_filtered
        results = df[df['title'].str.contains(film_nom, case=False, na=False)]

        # Ajouter les colonnes poster_path et imdb_id à partir de df_tmdb en fusionnant sur le titre
        results = results.merge(df_tmdb[['title', 'poster_path', 'imdb_id']], on='title', how='left')
        results = results.drop_duplicates(subset='title', keep='first')
        return results
        
    if film_nom:
            # Étape 1 : Recherche des films correspondants
            results = search_movies(film_nom, df_filtered, df_tmdb)

            if not results.empty:
                # Étape 2 : Sélectionner un film parmi les résultats
                selected_title = st.selectbox(
                    "Sélectionnez un film :",
                    options=results['title'].tolist()
                                                      
                )

                             
                if selected_title:
                    # Étape 3 : Récupérer les données du film sélectionné
                    selected_movie = results[results['title'] == selected_title]
                    
                    
                    # Vérifier que les colonnes `imdb_id` et `poster_path` existent et sont correctes
                    if 'imdb_id_x' in selected_movie.columns and 'poster_path' in selected_movie.columns:
                        imdb_id_x = selected_movie['imdb_id_x'].iloc[0].strip() if not pd.isna(selected_movie['imdb_id_x'].iloc[0]) else None
                        poster_path = selected_movie['poster_path'].iloc[0] if not pd.isna(selected_movie['poster_path'].iloc[0]) else None

                        # Afficher les informations du film sélectionné
                        st.write(f"### Film sélectionné : **{selected_title}**")

                        if imdb_id_x:
                            st.write(f"[Voir le film sur IMDb](https://www.imdb.com/title/{imdb_id_x}/)")
                        else:
                            st.warning("🔗 Lien IMDb non disponible pour ce film.")

                        if poster_path:
                            st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=150)
                        else:
                            st.image(image_affiche, width=150, caption="Affiche non disponible")
                    else:
                        st.error("Les colonnes `imdb_id` ou `poster_path` sont manquantes dans les données sélectionnées.")

                    

            # Ajout des boutons pour les différentes recommandations
            cols = st.columns(3)
            with cols[0]:
                vote_button = st.button("👍 Par vote", key="vote_button")
            with cols[1]:
                genre_button = st.button("🍿 Par genre", key="genre_button")
            with cols[2]:
                actor_button = st.button("⭐ Par acteur", key="actor_button")

            # Recommandation par vote
            if vote_button:
                st.write("### Recommandations par votes 👍")
                resultats = films_similaires(selected_title, df_filtered, df_tmdb)

                if isinstance(resultats, list) and resultats:
                    cols = st.columns(3)  # Trois colonnes pour l'affichage côte à côte
                    for idx, res in enumerate(resultats):
                        title = res.get('title', 'Titre inconnu')
                        poster_path = res.get('poster_path')
                        imdb_id = res.get('imdb_id')

                        with cols[idx % 3]:
                            if poster_path:
                                st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=150, caption=title)
                            else:
                                st.image(image_affiche, width=150, caption="Affiche non disponible")
                            if imdb_id:
                                st.write(f"[Lien du film](https://www.imdb.com/title/{imdb_id}/)")
                            else:
                                st.warning(f"IMDb ID manquant pour le film {title}")
                else:
                    st.error("❌ Aucune recommandation trouvée par vote.")

            # Recommandation par genre
            if genre_button:
                st.write("### Recommandations par genre 🍿")
                resultats2 = films_similaires2(selected_title, df_filtered, df_tmdb)

                if isinstance(resultats2, list) and resultats2:
                    cols = st.columns(3)  # Trois colonnes pour l'affichage côte à côte
                    for idx, res in enumerate(resultats2):
                        title2 = res.get('title', 'Titre inconnu')
                        poster_path2 = res.get('poster_path')
                        imdb_id2 = res.get('imdb_id')

                        with cols[idx % 3]:
                            if poster_path2:
                                st.image(f"https://image.tmdb.org/t/p/w500{poster_path2}", width=150, caption=title2)
                            else:
                                st.image(image_affiche, width=150, caption="Affiche non disponible")
                            if imdb_id2:
                                st.write(f"[Lien du film](https://www.imdb.com/title/{imdb_id2}/)")
                            else:
                                st.warning(f"IMDb ID manquant pour le film {title2}")
                else:
                    st.error("❌ Aucune recommandation trouvée par vote.")

            # Recommandation par acteur
            if actor_button:
                #st.write("### Recommandations par acteur ⭐")

                # Génération de la liste des acteurs uniques
                list_actor = df_filtered['two_actors'].apply(
                    lambda x: [actor.strip() for actor in ast.literal_eval(x)] if pd.notna(x) else []
                )
                actor_unique = set()
                for actor in list_actor:
                    actor_unique.update(actor)
                list_actor_unique = sorted(list(actor_unique))  # Liste triée des acteurs uniques
                selected_movie['two_actors']=selected_movie['two_actors'].apply(lambda x : str(x).replace('{', '').replace('}',''))
                selected_movie['two_actors']=selected_movie['two_actors'].apply(lambda x : str(x).replace("'", '').replace("'",''))
                acteurs=list(selected_movie['two_actors'])
                st.write(f"### Recommandations par acteur ⭐:\n {acteurs[0]}")
               

                # Appel de la fonction films_similaires3
                resultats = films_similaires3(selected_title, df_filtered, df_tmdb, list_actor_unique)

                # Vérifier si des résultats sont trouvés
                if isinstance(resultats, list) and resultats:
                    # Conversion des résultats en DataFrame pour une concaténation avec df_tmdb
                    resultats_df = pd.DataFrame(resultats)

                    # Concaténation explicite pour ajouter des colonnes manquantes depuis df_tmdb
                    resultats_df = pd.merge(
                        resultats_df,
                        df_tmdb[['title', 'poster_path', 'imdb_id']],  # Colonnes à ajouter
                        on='title',
                        how='left'
                    )

                    # Suppression des doublons par 'title'
                    resultats_df = resultats_df.drop_duplicates(subset='title', keep='first')


                if not resultats_df.empty:
                    
                    # Créer une liste pour stocker les films à afficher
                    films_a_afficher = []
                    for _, row in resultats_df.iterrows():
                        films_a_afficher.append({
                            'title': row.get('title', 'Titre inconnu'),
                            'poster_path': row.get('poster_path'),
                            'imdb_id': row.get('imdb_id')
                        })

                    # Calculer le nombre de lignes nécessaires
                    nb_films = len(films_a_afficher)
                    nb_lignes = (nb_films + 2) // 3  # Arrondi supérieur

                    # Afficher les films par ligne de 3
                    for ligne in range(nb_lignes):
                        cols = st.columns(3)
                        for col in range(3):
                            idx = ligne * 3 + col
                            if idx < nb_films:
                                film = films_a_afficher[idx]
                                with cols[col]:
                                    if pd.notna(film['poster_path']):
                                        st.image(f"https://image.tmdb.org/t/p/w500{film['poster_path']}", 
                                            width=150, 
                                            caption=film['title'])
                                    else:
                                        st.image(image_affiche, 
                                            width=150, 
                                            caption=film['title'])
                                    
                                    if film['imdb_id']:
                                        st.write(f"[Lien IMDb](https://www.imdb.com/title/{film['imdb_id']}/)")
                else:
                    st.error(f"❌ Aucun film trouvé pour l'acteur **{acteurs}**.")



### recommandation par acteur


elif selection == "Recommandation par acteur":
    st.title("Recommandation par acteur")

    # Recherche d'un acteur
    actor_nom = st.text_input("Commencez à saisir le nom d'un acteur :")

    # Génération de la liste des acteurs uniques
    list_actor = df_filtered['two_actors'].apply(
        lambda x: [actor.strip() for actor in ast.literal_eval(x)] if pd.notna(x) else []
    )
    actor_unique = set()
    for actor in list_actor:
        actor_unique.update(actor)
    list_actor_unique = sorted(list(actor_unique))

    # Filtrage des acteurs basés sur l'entrée utilisateur
    filtered_actors = [
        actor for actor in list_actor_unique if actor_nom.lower() in actor.lower()
    ] if actor_nom else []

    # Sélectionnez un acteur parmi les suggestions
    if filtered_actors:
        acteur_nom = st.selectbox(
            "Sélectionnez un acteur parmi les suggestions :",
            options=filtered_actors
        )
    else:
        acteur_nom = None

    if acteur_nom:  # Si un acteur est sélectionné
        # Utiliser la fonction `search_actor` pour récupérer les films
        resultats_acteur = search_actor(acteur_nom, df_filtered, df_tmdb)
        # Joindre les colonnes de df_tmdb pour inclure poster_path
        resultats_acteur = resultats_acteur.merge(df_tmdb[['title', 'poster_path', 'imdb_id']], on='title', how='left')
        # Supprimer les doublons
        resultats_acteur = resultats_acteur.drop_duplicates(subset='title', keep='first')

        if not resultats_acteur.empty:
            st.write(f"🎭 Films avec l'acteur **{acteur_nom}** :")

            # Créer une liste pour stocker les films à afficher
            films_a_afficher = []
            for _, row in resultats_acteur.iterrows():
                films_a_afficher.append({
                    'title': row.get('title', 'Titre inconnu'),
                    'poster_path': row.get('poster_path'),
                    'imdb_id': row.get('imdb_id')
                })

            # Calculer le nombre de lignes nécessaires
            nb_films = len(films_a_afficher)
            nb_lignes = (nb_films + 2) // 3  # Arrondi supérieur

            # Afficher les films par ligne de 3
            for ligne in range(nb_lignes):
                cols = st.columns(3)
                for col in range(3):
                    idx = ligne * 3 + col
                    if idx < nb_films:
                        film = films_a_afficher[idx]
                        with cols[col]:
                            if pd.notna(film['poster_path']):
                                st.image(f"https://image.tmdb.org/t/p/w500{film['poster_path']}", 
                                       width=150, 
                                       caption=film['title'])
                            else:
                                st.image(image_affiche, 
                                       width=150, 
                                       caption=film['title'])
                            
                            if film['imdb_id']:
                                st.write(f"[Lien IMDb](https://www.imdb.com/title/{film['imdb_id']}/)")
        else:
            st.error(f"❌ Aucun film trouvé pour l'acteur **{acteur_nom}**.")



### recommandation 3 films au hasard

elif selection == "Surprise":
    st.title("Recommandation Surprise")

    def film_hasard(df_filtered, df_tmdb):
        return df_filtered.sample(3)  # Sélection de 3 films aléatoires

    # Sélection de 3 films aléatoires
    resultats = film_hasard(df_filtered, df_tmdb)

    # Joindre les colonnes de df_tmdb pour inclure poster_path
    resultats = resultats.merge(df_tmdb[['title', 'poster_path', 'imdb_id']], on='title', how='left')
    # Supprimer les doublons
    resultats = resultats.drop_duplicates(subset='title', keep='first')

    if not resultats.empty:
        cols = st.columns(3)  # Crée des colonnes pour afficher les films
        resultats = resultats.reset_index(drop=True)

        for idx, res in resultats.iterrows():
            title = res.get('title', 'Titre inconnu')
            poster_path = res.get('poster_path')
            imdb_id = res.get('imdb_id_x')

            # Associe chaque film à une colonne
            col_courante = cols[idx % 3]
            with col_courante:
                if pd.notna(poster_path):
                    # Afficher l'affiche du film
                    st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=150, caption=title)
                else:
                    # Afficher l'image locale de remplacement
                    st.image(image_affiche, width=150, caption=title)

                # Afficher le titre du film
                st.write(f"**Titre :** {title}")

                # Lien vers IMDb_x
                if imdb_id and str(imdb_id).strip():
                    st.write(f"[Lien IMDb](https://www.imdb.com/title/{imdb_id}/)")




# Page KPI

elif selection == "KPI":

        # Fonction pour télécharger un fichier depuis Google Drive
    def download_file(url, output_file):
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_file, "wb") as file:
                file.write(response.content)
            return True
        else:
            return False


    # URLs de téléchargement des fichiers
    file_urls = {
        "df_final": "https://drive.google.com/uc?id=1a-cbrolKGMHexMZqKd6kobgZjWNfkj6i&export=download",
        "df_top5_act_films": "https://drive.google.com/uc?id=1-tv_a2353fJdpRryNK8q3jOn2kSQZaV2&export=download",
        "age_moyen": "https://drive.google.com/uc?id=1zMfxR90FQhjm4wcSEUgXtDSkGV23uV6H&export=download",
        "df_best_movies": "https://drive.google.com/uc?id=1XODwa3K0w1dgq4OKpOfCqPVRB51WhckT&export=download",
        "comparaison_FSa": "https://drive.google.com/uc?id=1JG3RalvkQ3orU9zdBT0rI-YLf24rMSrM&export=download"
    }

    # Téléchargement et chargement des fichiers
    dataframes = {}
    for name, url in file_urls.items():
        if download_file(url, f"{name}.csv"):
            try:
                dataframes[name] = pd.read_csv(f"{name}.csv")
                st.success(f"Fichier '{name}' téléchargé et chargé avec succès.")
            except Exception as e:
                st.error(f"Erreur lors du chargement du fichier '{name}': {e}")
        else:
            st.error(f"Erreur lors du téléchargement du fichier '{name}'.")

    # Vérification que tous les fichiers ont été chargés
    if not all(name in dataframes for name in file_urls):
        st.error("Certains fichiers requis n'ont pas pu être chargés.")
        st.stop()


        # Assignation des DataFrames
    df_final_KPI = dataframes.get("df_final")
    df_top5_act_films = dataframes.get("df_top5_act_films")
    age_moyen = dataframes.get("age_moyen")
    df_best_movies = dataframes.get("df_best_movies")
    comparaison_FSduree = dataframes.get("comparaison_FSa")

    # Titre de la page
    st.title("Tableau de bord des KPI")

    # **Graphique 1 : Top 5 des acteurs**
    st.subheader("Top 5 des acteurs")
    if "période" in df_final_KPI.columns:
        liste_periode = df_final_KPI['période'].unique().tolist()
        annees = st.selectbox("Choisissez la période", liste_periode)
        df_top5_graph = df_top5_act_films[df_top5_act_films['periode'] == annees].sort_values(by='count', ascending=True)
        plot1 = px.bar(
            df_top5_graph, 
            x="count", 
            y="primaryName", 
            orientation="h", 
            labels={"count": "Nombre d'apparitions", "primaryName": "Acteurs"}
        )
        st.plotly_chart(plot1)
    else:
        st.error("La colonne 'période' est manquante dans df_final.")

    # **Graphique 2 : Âge moyen**
    st.subheader("Âge moyen des acteurs par période")
    if not age_moyen.empty:
        plot2 = px.line(
            age_moyen, 
            x="période", 
            y="age", 
            markers=True, 
            labels={"période": "Période", "age": "Âge moyen"}
        )
        st.plotly_chart(plot2)
    else:
        st.error("Les données pour l'âge moyen sont manquantes.")

    # **Graphique 3 : Comparaison des durées moyennes**
    st.subheader("Comparaison des durées moyennes des films et séries")
    if not comparaison_FSduree.empty:
        plot3 = go.Figure()
        plot3.add_trace(go.Scatter(x=comparaison_FSduree['période'], y=comparaison_FSduree['durée_moyenne_films'],
                                mode="lines+markers", name="Durée Moyenne Films", marker_color="#61D2C7"))
        plot3.add_trace(go.Scatter(x=comparaison_FSduree['période'], y=comparaison_FSduree['durée_moyenne_series'],
                                mode="lines+markers", name="Durée Moyenne Séries", marker_color="#CB96B7"))
        plot3.update_layout(
            xaxis_title="Période",
            yaxis_title="Durée Moyenne (min)",
            barmode='group'
        )
        st.plotly_chart(plot3)
    else:
        st.error("Les données pour la comparaison des durées moyennes sont manquantes.")

    # **Meilleurs films**
    st.subheader('Les 3 meilleurs films et leurs caractéristiques')
    st.image(top3, width=700)  
    st.image(podium, width=700)  



