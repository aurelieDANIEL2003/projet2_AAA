import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MinMaxScaler

import pandas as pd
import numpy as np

chemin_bd = r"./bd_ignore/"

df_filtered= pd.read_csv(chemin_bd + 'df_filtered.csv')

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