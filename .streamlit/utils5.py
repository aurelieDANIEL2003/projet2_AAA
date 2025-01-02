import pandas as pd

chemin_bd = r"./bd_ignore/"
df_tmdb = pd.read_csv(chemin_bd + 'resultat/df_tmdb2.csv')  # Dataset des films 
df_filtered = pd.read_csv(chemin_bd + 'resultat/df_filtered.csv')

# Sélectionner 3 films au hasard
films_au_hasard = df_filtered.sample(n=3, random_state=1)

# Affichage des résultats
print("Films choisis au hasard :")

