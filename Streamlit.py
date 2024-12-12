import streamlit as st
from streamlit_option_menu import option_menu

st.title('')

with st.sidebar:
     st.write(f"Bienvenue")
     selection = option_menu(
            menu_title=None,
            options = ["🤩 Accueil", ""])