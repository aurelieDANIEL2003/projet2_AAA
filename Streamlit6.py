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
# import plotly.express as px
# import plotly.graph_objects as go

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

elif selection == "Recommandation Surprise":
    st.title("Recommandation Surprise")
    
    # Recherche de 3 films au hasard 
    # Utiliser random.randint pour choisir 3 indices aléatoires
    resultats = df_filtered.sample(3)
    st.write (f"### Film sélectionné : **{resultats}**")

    if not resultats.empty:
            cols = st.columns(3)  # Trois colonnes pour afficher les films

            for idx, res in enumerate(resultats.iterrows()):
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


# Page KPI

# Page KPI (Indicateurs clés de performance)
elif selection == "KPI":
    st.title("KPI")
    try:
        # Chargement des fichiers nécessaires pour les KPI
        df_final_KPI = pd.read_csv(chemin_bd + "resultat/df_final.csv")
        df_top_5_actors_per_periods = pd.read_csv(chemin_bd + 'resultat/df_top_5_actors_per_periodsa.csv')
        comparaison_FSduree = pd.read_csv(chemin_bd + 'resultat/comparaison_FSa.csv')
        df_resulta = pd.read_csv(chemin_bd + 'resultat/resulta.csv')
        age_moyen1 = pd.read_csv(chemin_bd + "resultat/age_moyen.csv")

        # Graphique : Top 5 des acteurs par période
        plot1 = px.bar(
            data_frame=df_top_5_actors_per_periods,
            x='count',
            y='primaryName',
            color='periode',
            orientation='h',  # Barres horizontales
            title='Top 5 des acteurs',
            barmode='overlay',  # Superposition des barres
            hover_name='periode'
        )
        st.plotly_chart(plot1)

        # Graphique : Nombre d'acteurs dans les films et séries par période
        plot2 = go.Figure()
        plot2.add_trace(go.Scatter(x=df_final_KPI['période'], y=df_final_KPI['acteurs_films'], name="Acteurs Films"))
        plot2.add_trace(go.Bar(x=df_final_KPI['période'], y=df_final_KPI['acteurs_films'], name="Films", opacity=0.5))
        plot2.add_trace(go.Scatter(x=df_final_KPI['période'], y=df_final_KPI['acteurs_series'], name="Acteurs Séries"))
        plot2.add_trace(go.Bar(x=df_final_KPI['période'], y=df_final_KPI['acteurs_series'], name="Séries", opacity=0.5))
        plot2.update_layout(
            title=dict(text="Nombre d'acteurs dans les films et séries"),
            barmode='overlay'  # Superposition des barres
        )
        st.plotly_chart(plot2)

        # Graphique : Comparaison des durées moyennes des films et séries
        plot3 = go.Figure()

        # Traces pour les films
        plot3.add_trace(go.Scatter(
            x=comparaison_FSduree['période'], 
            y=comparaison_FSduree['durée_moyenne_films'], 
            name="Durée Moyenne Films", 
            mode="lines+markers"
        ))
        plot3.add_trace(go.Bar(
            x=comparaison_FSduree['période'], 
            y=comparaison_FSduree['durée_moyenne_films'], 
            name="Films", 
            opacity=0.5
        ))

        # Traces pour les séries
        plot3.add_trace(go.Scatter(
            x=comparaison_FSduree['période'], 
            y=comparaison_FSduree['durée_moyenne_series'], 
            name="Durée Moyenne Séries", 
            mode="lines+markers"
        ))
        plot3.add_trace(go.Bar(
            x=comparaison_FSduree['période'], 
            y=comparaison_FSduree['durée_moyenne_series'], 
            name="Séries", 
            opacity=0.5
        ))

        # Mise en page du graphique
        plot3.update_layout(
            title=dict(text="Comparaison des durées moyennes des films et séries"),
            xaxis_title="Période",
            yaxis_title="Durée Moyenne (min)",
            barmode='overlay'
        )
        st.plotly_chart(plot3)

        # Transformation des données pour afficher le Top 3 films par période
        df_resulta_expanded = df_resulta.copy()
        df_resulta_expanded = df_resulta_expanded.assign(
            Films=df_resulta_expanded['Top 3 films'].str.split(", ")
        ).explode('Films')

        # Ajouter une colonne pour le rang des films dans chaque période
        df_resulta_expanded['Rang'] = df_resulta_expanded.groupby('période').cumcount() + 1

        # Graph: Top 3 films par période avec dégradé de couleurs
        # plot_top3_films = px.bar(
        #     data_frame=df_resulta_expanded,
        #     x='Films',
        #     y='période',
        #     color='Rang',  # Dégradé de couleurs basé sur le rang
        #     orientation='h',  # Barres horizontales
        #     title='Top 3 des films par période',
        #     hover_name='Films',  # Affichage des films au survol
        #     labels={"Films": "Films", "période": "Période", "Rang": "Rang (Top 1 à 3)"},
        #   color_continuous_scale=px.colors.sequential.Blues 
        #   #color_continuous_scale=px.colors.make_colorscale(px.colors.sequential.Blues, scale=[0.1, 1])
 

        # )
        df_final_KPI = df_final_KPI.assign(Top_3_films=df_final_KPI['Top 3 films'].str.split(','))
        df_final_KPI = df_final_KPI.explode('Top 3 films')  # Une ligne par titre associé
        df_final_KPI = df_final_KPI['Top_3_films'].explode()
        plot_top3_films = px.bar(
        df_final_KPI,
        x='période',
        y="Top_3_films",
        animation_frame='Top_3_films',
        color="Top_3_films",
        title="Top_3_films",

            )
            #fig8.update_xaxes(range=[0, 31])
            #fig8.update_yaxes(range=[0, 40])
            #fig8.show()
        st.plotly_chart(plot_top3_films)
        # st.plotly_chart(plot_top3_films)
    # # Exploser les titres associés (knownForTitles)
    #     df_final_KPI = df_final_KPI.assign(Top_3_films=df_final_KPI['Top 3 films'].str.split(','))
    #     df_final_KPI = df_final_KPI.explode('Top 3 films')  # Une ligne par titre associé
    #     plot_top3_films = px.bar(
    #         data_frame = df_final_KPI,
    #         x="période",              # Classement des films (1er, 2e, 3e)
    #         y="Top 3 films",             # Score des films
    #         color="Top 3 films",         # Couleur pour chaque film
    #         animation_frame="période",  # Animation basée sur les décennies
    #         hover_name="Top 3 films",    # Affichage du titre au survol
    #         title="Podium des 3 meilleurs films par période",
    #         labels={"rank": "Classement", "score": "Score"},
    #         text="Top 3 films"           # Afficher le titre sur les barres
    #     )

    #     #Ajuster l'apparence
    #     plot_top3_films.update_layout(
    #         xaxis=dict(title="Classement (1er, 2e, 3e)", tickvals=[1, 2, 3]),
    #         yaxis=dict(title="Score"),
    #         showlegend=False
    #     )

    #     st.plotly_chart(plot_top3_films)
        

        # Graph : Camembert pour l'âge moyen des acteurs par période
        st.title("Âge moyen des acteurs par période")
        fig_camembert = px.pie(
            data_frame=age_moyen1,
            names='période',  
            values='age',  
            title="Répartition de l'âge moyen des acteurs par période",
            hole=0, 
            #color_discrete_sequence=px.colors.qualitative.Pastel  # Palette de couleurs pastel
            color_discrete_sequence=["#6A8EAE", "#92A8D1", "#C5D8FF", "#B2C6DE", "#D1E7FF"]
            #color_discrete_sequence=["#6A8EAE", "#4A6FA5", "#3B5998", "#2B4570", "#1D3557"]
            #color_discrete_sequence=["#AFCBFF", "#92A8D1", "#C5D8FF", "#B2C6DE", "#D1E7FF"]


        )
        st.plotly_chart(fig_camembert)

    except FileNotFoundError as e:
        st.error(f"Fichier manquant : {str(e)}")







