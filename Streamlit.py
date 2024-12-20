#anissa
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
from utils import films_similaires
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

chemin_bd = r"./bd_ignore/"
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')

# Création du menu
with st.sidebar:
    st.write(f"AAA")
    selection = option_menu(
        menu_title=None,
        options=["Accueil 🙋🏼‍♀️", "Recommendation 🎬", "KPI"]
    )

# Accueil
if selection == "Accueil 🙋🏼‍♀️":
    st.title('Bienvenue au CINEMA !')
    st.image(chemin_bd + "medias/logo_canape.jpeg", width=500)
    st.write('Made by Aurélie, Anissa et Anaëlle.')

# Recommendation
elif selection == "Recommendation 🎬":
    st.title("Recommandation de films 🎬")
    film = st.text_input("Cherchez un film :")
    
    if film:
        # Vérifier si le film existe dans la base
        film_trouve = df_filtered['title'].str.lower().eq(film.lower()).any()

        if film_trouve:
            st.success(f"🎬 Le film '{film}' est présent dans la liste !")
            resultats = films_similaires(film, df_filtered)

            if resultats:
                st.write(f"🎬 Voici des films similaires à **{film}** :")
                for res in resultats:
                    st.write(f"- **{res['title']}** (distance: {res['distance']:.2f})")
                   
                    # Ajouter un lien IMDb si l'identifiant IMDb existe
                    if res.get('imdb_id'):
                       st.write(f"  [Lien du film](https://www.imdb.com/title/{res['imdb_id']}/)")
                    if res.get('poster_path'):
                       st.image(lien_poster)
            else:
                st.error(f"❌ Le film '{film}' n'a pas été trouvé.")
    else:
        st.info("🔎 Entrez un titre de film pour rechercher des recommandations.")


# KPI
elif selection == "KPI":
    st.title("KPI")
    try:
      df_final_KPI = pd.read_csv(chemin_bd+"resultat/df_final.csv")
      df_top_5_actors_per_periods = pd.read_csv(chemin_bd + 'resultat/df_top_5_actors_per_periodsa.csv')
      # df_top5_acteurs_nv = pd.read_csv(chemin_bd + '/resultat/df_top5_acteurs_nv.csv')
      
      #st.bar_chart(data = df_top5_acteurs_nv, x='primaryName', y='count', color = 'periode', stack="layered", horizontal=True)
      
      #plot = sns.barplot(data = df_top5_acteurs_nv, x='primaryName', y='count')
      #Affichez le graphique dans Streamlit
      #st.pyplot(plot.get_figure()) #pour seaborn
      
      plot1 = px.bar(data_frame = df_top_5_actors_per_periods, x='count', y='primaryName', color='periode', orientation = 'h', title='Top 5 des acteurs', barmode = 'overlay', hover_name='periode')
      st.plotly_chart(plot1)
      
      plot2 = go.Figure()
      plot2.add_trace(go.Scatter(x=df_final_KPI['période'], y=df_final_KPI['acteurs_films']))
      plot2.add_trace(go.Bar(x=df_final_KPI['période'],y=df_final_KPI['acteurs_films']))
      plot2.add_trace(go.Scatter(x=df_final_KPI['période'], y=df_final_KPI['acteurs_series']))
      plot2.add_trace(go.Bar(x=df_final_KPI['période'],y=df_final_KPI['acteurs_series']))
      plot2.update_layout(title=dict(text="Nombre d'acteurs dans les films et séries"))
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
