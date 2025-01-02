import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import random
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from utils1 import films_similaires
from utils2 import films_similaires2
from utils3 import films_similaires_par_acteur
from utils4 import films_similaires3
import plotly.express as px
import plotly.graph_objects as go

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
    def search_movies(film_nom, df):
        results = df[df['title'].str.contains(film_nom, case=False, na=False)]
        return results
    
  
    if film_nom:
        # Étape 1 : Recherche des films correspondants
        results = search_movies(film_nom, df_filtered)

        if not results.empty:
            # st.write("### Films trouvés correspondant à votre recherche :")
            # st.dataframe(results[['title', 'genres']])

            # Étape 2 : Sélectionner un film parmi les résultats
            selected_title = st.selectbox(
                "Sélectionnez un film :",
                options=results['title'].tolist()
            )

            if selected_title:
                selected_movie = results[results['title'] == selected_title]
                imdb_id = selected_movie['imdb_id'].iloc[0]

                st.write(f"### Film sélectionné : **{selected_title}**")
                #st.write(f"L'identifiant IMDb du film est : **{imdb_id}**")
                st.write(f"[Voir le film](https://www.imdb.com/title/{imdb_id}/)")

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
            st.write("🔍 Recherche de recommandations par vote...")
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
                        if imdb_id:
                            st.write(f"[Lien du film](https://www.imdb.com/title/{imdb_id}/)")
                        else:
                            st.warning(f"IMDb ID manquant pour le film {title}")
            else:
                st.error("❌ Aucune recommandation trouvée par vote.")

        # Recommandation par genre
        if genre_button:
            st.write("🔍 Recherche de recommandations par genre...")
            resultats = films_similaires2(selected_title, df_filtered, df_tmdb)

            if isinstance(resultats, list):
                cols = st.columns(3)  # Trois colonnes pour l'affichage côte à côte
                for idx, res in enumerate(resultats):
                    title = res.get('titre', 'Titre inconnu')
                    poster_path = res.get('poster_path')
                    imdb_id = res.get('imdb_id')

                    with cols[idx % 3]:
                        if poster_path:
                            st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=150, caption=title)
                        if imdb_id:
                            st.write(f"[Lien du film](https://www.imdb.com/title/{imdb_id}/)")
            else:
                st.error("❌ Aucune recommandation trouvée par vote.")

        # Recommandation par acteur
        if actor_button:
            st.write("### Recommandations par acteur ⭐")
            resultats = films_similaires3(selected_title, df_filtered, df_tmdb)
            if resultats:
                cols = st.columns(3)  # Trois colonnes pour l'affichage côte à côte
                for idx, res in enumerate(resultats):
                    title = res.get('title', 'Titre inconnu')
                    poster_path = res.get('poster_path')
                    imdb_id = res.get('imdb_id')

                    with cols[idx % 3]:
                        if poster_path:
                            st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=150, caption=title)
                        if imdb_id:
                            st.write(f"[Lien du film](https://www.imdb.com/title/{imdb_id}/)")
            else:
                st.error("❌ Aucune recommandation trouvée par vote.")                


### recommandation par acteur


elif selection == "Recommandation par acteur":
    st.title("Recommandation par acteur")
    # Champ de recherche par acteur
    # Interface utilisateur pour la recherche par acteur
    actor = st.text_input("Cherchez un acteur :", value="", key="acteur")

    def search_actor(actor, df):
        results = df[df['two_actors'].str.contains(actor, case=False, na=False)]
        return results
    
  
    if actor:
        # Étape 1 : Recherche des films correspondants
        results = search_actor(actor, df_filtered)
        print (results)
        if not results.empty:
            # st.write("### Films trouvés correspondant à votre recherche :")
            # st.dataframe(results[['title', 'genres']])

            # Étape 2 : Sélectionner un film parmi les résultats
            selected_actor = st.selectbox(
                "Sélectionnez un acteur :",
                options=results['two_actors'].tolist()
                
            )
            print (selected_actor)

            if selected_actor:
                selected_actor = results[results['two_actors'] == selected_actor]
                imdb_id = selected_actor['imdb_id'].iloc[0]

                st.write(f"### Film sélectionné : **{selected_actor}**")
                #st.write(f"L'identifiant IMDb du film est : **{imdb_id}**")
                st.write(f"[Voir le film](https://www.imdb.com/title/{imdb_id}/)")

    if actor:
        st.write(f"🎭 Recherche des films avec l'acteur **{actor}**...")
        resultats_acteur = films_similaires_par_acteur(actor, df_filtered, df_tmdb)

        if isinstance(resultats_acteur, list) and resultats_acteur:
            cols = st.columns(3)  # Trois colonnes pour l'affichage côte à côte
            for idx, res in enumerate(resultats_acteur):
                title = res.get('title', 'Titre inconnu')
                poster_path = res.get('poster_path')
                imdb_id = res.get('imdb_id')

                with cols[idx % 3]:
                    if poster_path:
                        st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=150, caption=title)
                    if imdb_id:
                            st.write(f"[Lien du film](https://www.imdb.com/title/{imdb_id}/)")
        else:
            st.error(f"❌ Aucun film trouvé avec l'acteur **{actor}**.")


### recommandation 3 films au hasard
elif selection == "Surprise":
    st.title("Recommandation Surprise")
    
    # Recherche de 3 films au hasard
    resultats = df_filtered.sample(3)  # Sélection de 3 films aléatoires

    if not resultats.empty:
        cols = st.columns(3)  # Trois colonnes pour afficher les films
        
        for idx, res in resultats.iterrows():
            title = res.get('title', 'Titre inconnu')
            poster_path = res.get('poster_path')
            imdb_id = res.get('imdb_id')

            # Ajouter les informations dans les colonnes
            with cols[idx % 3]:
                if poster_path and str(poster_path).strip():
                    # Afficher l'affiche du film
                    st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=150, caption=title)
                else:
                    st.write(f"**{title}** (Aucune affiche disponible)")

                # Lien vers IMDb
                if imdb_id and str(imdb_id).strip():
                    st.write(f"[Voir sur IMDb](https://www.imdb.com/title/{imdb_id}/)")

    # st.write(f"### Films sélectionnés :")
    # st.write(resultats)



# Page KPI

# KPI
elif selection == "KPI 📈":
    st.title("KPI")
    try:
      df_final_KPI = pd.read_csv(chemin_bd+"resultat/df_final.csv")
      df_top_5_actors_per_periods = pd.read_csv(chemin_bd + 'resultat/df_top_5_actors_per_periodsa.csv')
      df_top5_act_films = pd.read_csv(chemin_bd + 'resultat/df_top5_act_films.csv')  #graph de top5 acteurs avec leurs projets les plus connus (vient de df_final_re)
      df_top5_mean = pd.read_csv(chemin_bd + 'resultat/df_top5_mean.csv') #graph de moyenne d'apparitions par période(vient de df_final_re)

      #faire une liste de la colonne péridoe
      liste_periode = df_final_KPI['période'].tolist()
      
      #faire une barre de sélection de la période 
      annees = st.selectbox("Choisissez la période", liste_periode)
      
      #faire un df en prenant que la période selectionnée
      df_top5_graph = df_top5_act_films[df_top5_act_films['periode'] == annees].sort_values(by='count', ascending=True)

      dico_labels = {'count':"Nombre d'apparitions",
                     'primaryName':"Acteurs"}   # dico pour renommer les axes
      
      plot1 = px.bar(data_frame = df_top5_graph, x='count', y='primaryName', labels=dico_labels, orientation = 'h', title='Top 5 des acteurs', barmode = 'overlay', hover_name='primaryTitle', color_discrete_sequence =['#1b8585']*len(df_top5_graph))
      st.plotly_chart(plot1)    # graph en utilisant le df de la période selectionnée
      
    #   dico_labels_bis = {'count':"Moyenne du nombre d'apparitions",
    #                  'primaryName':"Acteurs"} 

    #   plot1bis=px.bar(data_frame = df_top5_mean, x='count', y='période', labels=dico_labels_bis, orientation = 'h', title='Moyenne du nombre dapparition', barmode = 'overlay', hover_name='primaryTitle', color_discrete_sequence =['#1b8585']*len(df_top5_graph))
    #   st.plotly_chart(plot1)

      #GRAPH 2
      plot2 = go.Figure()
      plot2.add_trace(go.Scatter(x=df_final_KPI['période'], y=df_final_KPI['acteurs_films'],name='films', legendgroup = 'films', marker_color='#61D2C7'))
      plot2.add_trace(go.Bar(x=df_final_KPI['période'],y=df_final_KPI['acteurs_films'], name='films', legendgroup = 'films', marker_color='#356767'))
      plot2.add_trace(go.Scatter(x=df_final_KPI['période'], y=df_final_KPI['acteurs_series'], name='séries', legendgroup = 'séries', marker_color='#cb96b7'))
      plot2.add_trace(go.Bar(x=df_final_KPI['période'],y=df_final_KPI['acteurs_series'], name='séries', legendgroup = 'séries', marker_color='#613650'))
      plot2.update_layout(title=dict(text="Nombre d'acteurs dans les films et séries"))   #titre
      st.plotly_chart(plot2)

    except FileNotFoundError:
        st.error("Le fichier 'df_final.csv' est introuvable.")


# idées de graph pour chaque kpi
# l’identification des acteurs les plus présents et les périodes associées --> histogram/barplot avec 5 barres(= 5 acteurs) par période et count de leur apparition en axe y
# l’évolution de la durée moyenne des films au fil des années --> lineplot ou peut être un bar plot car nos périodes sont définies en catégories
# la comparaison entre les acteurs présents au cinéma et dans les séries
# l’âge moyen des acteurs, 
# ainsi que les films les mieux notés et les caractéristiques qu’ils partagent 


  # import pickle
# # Charger le modèle
#    def charger_modele():
#       with open('mon_modele.pkl', 'rb') as f: #là vous mettez l'emplacement et le nom de votre fichier pkl
#         model_charge = pickle.load(f)
#       return model_charge