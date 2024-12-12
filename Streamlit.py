import streamlit as st
from streamlit_option_menu import option_menu



#création du menu
with st.sidebar:
     st.write(f"AAA")
     selection = option_menu(
            menu_title=None,
            options = ["Accueil 🙋🏼‍♀️", "Recommendation 🎬"])

# On indique au programme quoi faire en fonction du choix
if selection == "Accueil 🙋🏼‍♀️":
    st.markdown("<h1 style='text-align: center;'>Bienvenue sur ma page !</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
      st.write('')
    with col2:
     st.image("/Users/anaellepinceloup/Pictures/AAA/logo_canape.jpeg", width=500)
    with col3:
      st.write('')
    st.write('Made by Aurélie, Anissa and Anaëlle.')

if selection == "Recommendation 🎬":
   st.text_input("Cherchez un film:")


# idées de graph pour chaque kpi
# l’identification des acteurs les plus présents et les périodes associées --> histogram/barplot avec 5 barres(= 5 acteurs) par période et count de leur apparition en axe y
# l’évolution de la durée moyenne des films au fil des années --> lineplot
# la comparaison entre les acteurs présents au cinéma et dans les séries
# l’âge moyen des acteurs, 
# ainsi que les films les mieux notés et les caractéristiques qu’ils partagent 