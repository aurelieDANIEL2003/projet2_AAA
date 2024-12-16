import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd

chemin_bd = r"./bd_ignore/"

#création du menu
with st.sidebar:
     st.write(f"AAA")
     selection = option_menu(
            menu_title=None,
            options = ["Accueil 🙋🏼‍♀️", "Recommendation 🎬", "KPI"])

# On indique au programme quoi faire en fonction du choix
if selection == "Accueil 🙋🏼‍♀️":
    st.title('Bienvenue sur notre projet 2 !')
    st.image("/Users/anaellepinceloup/Pictures/AAA/logo_canape.jpeg", width=500)
    st.write('Made by Aurélie, Anissa and Anaëlle.')

elif selection == "Recommendation 🎬":
   st.text_input("Cherchez un film:")

elif selection == "KPI":
   df_final_KPI = pd.read_csv(chemin_bd+"resultat/df_final.csv")
   st.bar_chart(data=df_final_KPI,x='', y='count')


# idées de graph pour chaque kpi
# l’identification des acteurs les plus présents et les périodes associées --> histogram/barplot avec 5 barres(= 5 acteurs) par période et count de leur apparition en axe y
# l’évolution de la durée moyenne des films au fil des années --> lineplot ou peut être un bar plot car nos périodes sont définies en catégories
# la comparaison entre les acteurs présents au cinéma et dans les séries
# l’âge moyen des acteurs, 
# ainsi que les films les mieux notés et les caractéristiques qu’ils partagent 