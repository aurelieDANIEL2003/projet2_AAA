#Anissa

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from utils import films_similaires
import plotly.express as px
import plotly.graph_objects as go

# Chemin vers les données
chemin_bd = r"./bd_ignore/"

# Chargement des fichiers nécessaires
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')

# Création du menu dans la barre latérale
with st.sidebar:
    selection = option_menu(
        menu_title=None,  # Pas de titre pour le menu
        options=["Accueil 🙋🏼‍♀️", "Recommendation 🎬", "KPI"]  # Options disponibles
    )

# Page d'accueil
if selection == "Accueil 🙋🏼‍♀️":
    st.title('Bienvenue au CINÉMA !')
    st.image(chemin_bd + "medias/logo_canape.jpeg", width=500)  # Affichage du logo
    st.write('Made by Aurélie, Anissa et Anaëlle.')  # Signature des auteurs

# Page de recommandations
elif selection == "Recommendation 🎬":
    st.title("Recommandation de films 🎬")
    film = st.text_input("Cherchez un film :")  # Entrée pour le titre du film
    
    if film:
        # Vérification si le film est présent dans la base
        film_trouve = df_filtered['title'].str.lower().eq(film.lower()).any()

        if film_trouve:
            st.success(f"🎬 Le film '{film}' est présent dans la liste !")
            resultats = films_similaires(film, df_filtered)

            if resultats:
                st.write(f"🎬 Voici des films similaires à **{film}** :")
                for res in resultats:
                    # Affichage des films similaires avec distance
                    st.write(f"- **{res['title']}** (distance: {res['distance']:.2f})")
                    
                    # Lien IMDb si disponible
                    if res.get('imdb_id'):
                        st.write(f"[Lien IMDb](https://www.imdb.com/title/{res['imdb_id']}/)")
                    # Affiche du film si disponible
                    if res.get('poster_path'):
                        st.image(res['poster_path'])
            else:
                st.error(f"❌ Aucun film similaire trouvé pour '{film}'.")
        else:
            st.error(f"❌ Le film '{film}' n'est pas présent dans la base.")
    else:
        st.info("🔎 Entrez un titre de film pour rechercher des recommandations.")

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
