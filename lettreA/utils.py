import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import pandas as pd

# Charger les données
chemin_bd = r"./bd_ignore/"
df_tmdb = pd.read_csv(chemin_bd + 'resultat/df_tmdb2.csv')  # Dataset des films
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')

# Fonction pour rechercher des titres
def search_movies(film_nom, df):
    results = df[df['title'].str.contains(film_nom, case=False, na=False)]
    return results

# Interface utilisateur avec Streamlit
st.title("Recherche et sélection de films")
film_nom = st.text_input("Entrez le titre ou une partie du titre du film :")

if film_nom:  # Vérifier si l'utilisateur a saisi un texte
    results = search_movies(film_nom, df_filtered)
    
    if not results.empty:
        # st.write("Voici les films trouvés correspondant à votre recherche :")
        # # Affichage des résultats sous forme de tableau interactif
        # st.dataframe(results[['imdb_id', 'title', 'genres']])
        
        # Permettre à l'utilisateur de choisir un film
        selected_id = st.selectbox(
            "Sélectionnez l'identifiant IMDb du film :",
            options=results['imdb_id'].tolist()
        )
        
        # Afficher les détails du film sélectionné
        if selected_id:
            selected_movie = results[results['imdb_id'] == selected_id]
            selected_title = selected_movie.iloc[0]['title']  # Récupérer le titre du film sélectionné
            
            st.write(f"Vous avez sélectionné : **{selected_title}**")
            
            # Afficher l'identifiant IMDb et un lien vers IMDb
            st.write(f"L'identifiant IMDb du film est : **{selected_id}**")
            st.write(f"[Lien IMDb du film](https://www.imdb.com/title/{selected_id}/)")
    else:
        st.write("Aucun film trouvé pour votre recherche.")
