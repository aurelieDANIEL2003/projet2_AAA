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

        # Graphique : Podium des 3 meilleurs films par période
        df_final_KPI = df_final_KPI.assign(Top_3_films=df_final_KPI['Top 3 films'].str.split(','))
        df_final_KPI = df_final_KPI.explode('Top_3_films')  # Une ligne par titre associé

                # Menu déroulant pour sélectionner une période
        st.title("Podium des Meilleurs Films par Période")
        periode_selection = st.selectbox("Sélectionnez une période :", df_final_KPI['période'].unique())

        # Filtrer les données en fonction de la période sélectionnée
        df_filtered = df_final_KPI[df_final_KPI['période'] == periode_selection]
        df_filtered = df_filtered.assign(Top_3_films=df_filtered['Top 3 films'].str.split(','))
        df_filtered = df_filtered.explode('Top_3_films')  # Une ligne par titre associé

        # Ajouter des couleurs pour les positions (Or, Argent, Bronze)
        colors = {"Film A": "#FFD700", "Film B": "#C0C0C0", "Film C": "#CD7F32", 
                "Film D": "#FFD700", "Film E": "#C0C0C0", "Film F": "#CD7F32"}
        df_filtered['Couleur'] = df_filtered['Top_3_films'].map(colors)

        # Créer un graphique en barres pour les Top 3 films par période
        ###############
            
        import pandas as pd
        import plotly.graph_objects as go
        import streamlit as st

        # Chargement des données existantes pour les films par période
        #df_final_KPI = pd.read_csv("chemin_vers_vos_donnees/df_final_KPI.csv")  # Remplacez par votre chemin réel

        # Menu déroulant pour sélectionner une période
        st.title("Podium des Meilleurs Films par Période")
        periode_selection = st.selectbox(
            "Sélectionnez une période :", 
            df_final_KPI['période'].unique(), 
            key="periode_selectbox"  # Clé unique
        )

        # Filtrer les données en fonction de la période sélectionnée
        df_filtered = df_final_KPI[df_final_KPI['période'] == periode_selection]
        df_filtered = df_filtered.assign(Top_3_films=df_filtered['Top 3 films'].str.split(','))
        df_filtered = df_filtered.explode('Top_3_films')  # Une ligne par titre associé

        # Ajouter des couleurs pour les positions (Or, Argent, Bronze)
        colors = {"Film A": "#FFD700", "Film B": "#C0C0C0", "Film C": "#CD7F32", 
                "Film D": "#FFD700", "Film E": "#C0C0C0", "Film F": "#CD7F32"}
        df_filtered['Couleur'] = df_filtered['Top_3_films'].map(colors)

        # Obtenir les trois films avec leurs positions
        top_3_films = df_filtered['Top_3_films'].unique()[:3]
        top_3_colors = [colors[film] for film in top_3_films]
        positions = [3, 2, 1]  # Hauteurs pour les podiums

        # Créer un graphique avec trois barres colorées
        fig = go.Figure()

        for film, color, position in zip(top_3_films, top_3_colors, positions):
            fig.add_trace(go.Bar(
                x=[film],
                y=[position],
                name=film,
                marker_color=color
            ))

        # Configurer l'apparence du graphique
        fig.update_layout(
            title=f"Podium des Meilleurs Films pour la Période {periode_selection}",
            xaxis=dict(title="Films", showline=False, showgrid=False),
            yaxis=dict(title="Position", range=[0, 4], showline=False, showgrid=False),
            plot_bgcolor="rgba(0,0,0,0)",  # Fond transparent
            showlegend=False
        )

        # Afficher le graphique dans Streamlit
        st.plotly_chart(fig)



    ###############""
        # Graph : Camembert pour l'âge moyen des acteurs par période
        st.title("Âge moyen des acteurs par période")
        fig_camembert = px.pie(
            data_frame=age_moyen1,
            names='période',  
            values='age',  
            title="Répartition de l'âge moyen des acteurs par période",
            hole=0,
            color_discrete_sequence=["#6A8EAE", "#92A8D1", "#C5D8FF", "#B2C6DE", "#D1E7FF"]
        )
        st.plotly_chart(fig_camembert)

    except FileNotFoundError as e:
        st.error(f"Fichier manquant : {str(e)}")
