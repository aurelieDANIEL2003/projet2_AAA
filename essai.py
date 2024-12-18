import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from utils import films_similaires
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

chemin_bd = r"./bd_ignore/"
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')

# Préparer le modèle Nearest Neighbors
features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']
df_encoded = pd.concat(
    [df_filtered[features], pd.get_dummies(df_filtered['genres'], prefix='genre')],
    axis=1
)
scaler = MinMaxScaler()
X = scaler.fit_transform(df_encoded)

model = NearestNeighbors(n_neighbors=11, metric='euclidean')
model.fit(X)

# Création du menu
with st.sidebar:
    st.write(f"AAA")
    selection = option_menu(
        menu_title=None,
        options=["Accueil 🙋🏼‍♀️", "Recommendation 🎬", "KPI"]
    )

# Navigation
if selection == "Accueil 🙋🏼‍♀️":
    st.title('Bienvenue sur notre projet 2 !')
    st.image(chemin_bd + "medias/logo_canape.jpeg", width=500)
    st.write('Made by Aurélie, Anissa and Anaëlle.')

elif selection == "Recommendation 🎬":
    st.title("Recommandation de films 🎬")
    film = st.text_input("Cherchez un film:")
    
    if film:
        # Appeler la fonction pour rechercher des films similaires
        resultats = films_similaires(film)
        if resultats is not None:
            st.success(f"🎬 Voici des films similaires à '{film}':")
            for res in resultats:
                st.write(f"**{res['title']}** (distance: {res['distance']:.2f})")
                st.write(f"   Acteurs: {res['actors']}")
        else:
            st.error(f"❌ Le film '{film}' n'a pas été trouvé dans la base de données.")

elif selection == "KPI":
    st.title("KPI")
    df_final_KPI = pd.read_csv(chemin_bd + "resultat/df_final.csv")
    st.bar_chart(data=df_final_KPI, x='', y='count')
