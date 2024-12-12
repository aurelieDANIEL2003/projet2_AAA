import streamlit as st
from streamlit_option_menu import option_menu

st.title('')

st.markdown(
    """
    <style>
    .reportview-container {
        background: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgqfQeBM3AKLr8EtO3qqFcFd_RFgqCd0fCdQ&s);
    }
   </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
     st.write(f"Bienvenue")
     selection = option_menu(
            menu_title=None,
            options = ["🤩 Accueil", ""])