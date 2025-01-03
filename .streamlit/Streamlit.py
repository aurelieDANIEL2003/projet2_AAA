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

# Charger les données
chemin_bd = r"./bd_ignore/"
df_tmdb = pd.read_csv(chemin_bd + 'resultat/df_tmdb2.csv')  # Dataset des films
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')
df_filtered_actor = pd.read_csv(chemin_bd + 'resultat/df_filtered2.csv')


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
    st.image(chemin_bd + "medias/logo_canape.jpeg", width=500)
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
                            st.image(chemin_bd + "medias/affiche.jpeg", width=150, caption="Affiche non disponible")
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
                                st.image(chemin_bd + "medias/affiche.jpeg", width=150, caption="Affiche non disponible")
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
                                st.image(chemin_bd + "medias/affiche.jpeg", width=150, caption="Affiche non disponible")
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
                                        st.image(chemin_bd + "medias/affiche.jpeg", 
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
                                st.image(chemin_bd + "medias/affiche.jpeg", 
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
                    st.image(chemin_bd + "medias/affiche.jpeg", width=150, caption=title)

                # Afficher le titre du film
                st.write(f"**Titre :** {title}")

                # Lien vers IMDb_x
                if imdb_id and str(imdb_id).strip():
                    st.write(f"[Lien IMDb](https://www.imdb.com/title/{imdb_id}/)")




# Page KPI

elif selection == "KPI":

    st.title("KPI")
    try:
      df_final_KPI = pd.read_csv(chemin_bd+"resultat/df_final.csv")
      df_top_5_actors_per_periods = pd.read_csv(chemin_bd + 'resultat/df_top_5_actors_per_periodsa.csv')
      df_top5_act_films = pd.read_csv(chemin_bd + 'resultat/df_top5_act_films.csv')  #graph de top5 acteurs avec leurs projets les plus connus (vient de df_final_re)
      df_top5_mean = pd.read_csv(chemin_bd + 'resultat/df_top5_mean.csv') #graph de moyenne d'apparitions par période(vient de df_final_re)
      age_moyen1 = pd.read_csv(chemin_bd+"resultat/age_moyen.csv") #graph âge moyen par période
      df_best_movies = pd.read_csv(chemin_bd+"resultat/df_best_movies.csv")
      comparaison_FSduree =  pd.read_csv(chemin_bd + 'resultat/comparaison_FSa.csv')


      #faire une liste de la colonne péridoe
      liste_periode = df_final_KPI['période'].tolist()
      st.subheader("Top 5 des acteurs")
           
      #faire une barre de sélection de la période 
      annees = st.selectbox("Choisissez la période", liste_periode)
      
      #faire un df en prenant que la période selectionnée
      df_top5_graph = df_top5_act_films[df_top5_act_films['periode'] == annees].sort_values(by='count', ascending=True)

      dico_labels = {'count':"Nombre d'apparitions",
                     'primaryName':"Acteurs"}   # dico pour renommer les axes
      
      plot1 = px.bar(data_frame = df_top5_graph, x='count', y='primaryName', labels=dico_labels, orientation = 'h', barmode = 'overlay', hover_name='primaryTitle', color_discrete_sequence =['#1b8585']*len(df_top5_graph))
      st.plotly_chart(plot1)    # graph en utilisant le df de la période selectionnée
      
      #GRAPH 2
      st.subheader("Age moyen des acteurs")
      plot3 = px.line(data_frame = age_moyen1, x = 'période', y = 'age', range_y = [0,80], markers=True, color_discrete_sequence =['#1b8585']*len(df_top5_graph))
      st.plotly_chart(plot3)

      #GRAPH 3
      st.subheader("Comparaison du nombre d'acteurs dans les films et séries")
      plot2 = go.Figure()
      plot2.add_trace(go.Scatter(x=df_final_KPI['période'], y=df_final_KPI['acteurs_films'],name='Acteurs Films', legendgroup = 'films', marker_color='#61D2C7'))
      plot2.add_trace(go.Bar(x=df_final_KPI['période'],y=df_final_KPI['acteurs_films'], name='films', legendgroup = 'films', marker_color='#196b6b'))
      plot2.add_trace(go.Scatter(x=df_final_KPI['période'], y=df_final_KPI['acteurs_series'], name='Acteurs séries', legendgroup = 'séries', marker_color='#cb96b7'))
      plot2.add_trace(go.Bar(x=df_final_KPI['période'],y=df_final_KPI['acteurs_series'], name='séries', legendgroup = 'séries', marker_color='#613650'))
    # Mise en page du graphique
      plot2.update_layout(
            xaxis_title="Période",
            yaxis_title="Nombre d'Acteurs",
            barmode='group',
            )
      st.plotly_chart(plot2)

      #GFRAPH 4
      #Graphique : Comparaison des durées moyennes des films et séries

      st.subheader("Comparaison des durées moyennes des films et séries")
      plot4 = go.Figure()
      plot4.add_trace(go.Scatter(x=comparaison_FSduree['période'], y=comparaison_FSduree['durée_moyenne_films'],name="Durée Moyenne Films",legendgroup = 'films', mode="lines+markers", marker_color='#61D2C7'))
      plot4.add_trace(go.Bar(x=comparaison_FSduree['période'],y=comparaison_FSduree['durée_moyenne_films'], name='films', legendgroup = 'films', marker_color='#196b6b'))
      plot4.add_trace(go.Scatter(x=comparaison_FSduree['période'], y=comparaison_FSduree['durée_moyenne_series'], name="Durée Moyenne Séries", legendgroup = 'séries', marker_color='#cb96b7'))
      plot4.add_trace(go.Bar(x=comparaison_FSduree['période'],y=comparaison_FSduree['durée_moyenne_series'], name='séries', legendgroup = 'séries', marker_color='#613650'))
      # Mise en page du graphique
      plot4.update_layout(
            xaxis_title="Période",
            yaxis_title="Durée Moyenne (min)",
            barmode='group',
            yaxis_range=[0,100]
        )
      st.plotly_chart(plot4)

      
    #   #MEILLEURS FILMS
    #   df_best_movies = df_best_movies.iloc[:,:4]
    #   df_best_movies = df_best_movies.style.format({"year": lambda x : '{:.0f}'.format(x)}) #permet de supprimer la virgule qui se met par défaut dans la colonne année
      
      
      st.subheader('Les 3 meilleurs films et leurs caractéristiques')
      st.image(chemin_bd + "medias/top3.png", width=700)  
      st.image(chemin_bd + "medias/tableau_podium.png", width=700)       
      #st.table(df_best_movies)
      
    except FileNotFoundError:
        st.error("Le fichier 'df_final.csv' est introuvable.")


