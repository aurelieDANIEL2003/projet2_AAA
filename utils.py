import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

import pandas as pd
import numpy as np

chemin_bd = r"./bd_ignore/"

df_filtered= pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')

features = ['popularity', 'vote_average', 'vote_count', 'budget', 'revenue', 'runtime']

# Encodage des genres
df_encoded = pd.concat(
    [df_filtered[features], pd.get_dummies(df_filtered['genres'], prefix='genre')],
    axis=1
)

# Normalisation des données
scaler = MinMaxScaler()
X = scaler.fit_transform(df_encoded)

# Modèle Nearest Neighbors
k = 11 # Meilleure valeur de K = 6 d'aprés fig

model = NearestNeighbors(n_neighbors=k, metric='euclidean')
model.fit(X)

def films_similaires(film_index):
    distances, indices = model.kneighbors([X[film_index]])
    print("Films similaires :")
    for i, index in enumerate(indices[0]):
        film = df_filtered.iloc[index]
        print(f"{i + 1}: {film['title']} (distance: {distances[0][i]:.2f})")
        print(f"   Acteurs: {film['actors']}")




# a voir pour mettre dans streamlit(jonathan)

#réinitialiser les indices de df_filtered
df_filtered = df_filtered.reset_index(drop=True)

def films_similaires(titre_film):
    try:
        #trouver l'index du film dans df_filtered
        film_index = df_filtered[df_filtered['title'] == titre_film].index[0]
        
        #obtenir les films similaires
        distances, indices = model.kneighbors([X[film_index]])
        
        print(f"\nFilms similaires à '{titre_film}':\n")
        for i, index in enumerate(indices[0][1:]):  
            film = df_filtered.iloc[index]
            print(f"{i + 1}: {film['title']} (distance: {distances[0][i+1]:.2f})")
            print(f"   Acteurs: {film['actors']}")
            print(f"   Genres: {film['genres']}\n")
            
    except IndexError:
        print(f"Erreur: Le film '{titre_film}' n'a pas été trouvé dans la base de données.")
    except Exception as e:
        print(f"Une erreur s'est produite: {str(e)}")

#exemple d'utilisation
# films_similaires("Inception")  
