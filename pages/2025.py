import streamlit as st

from pages.season_loader import render_temporada

st.set_page_config(
    page_title="Classificação 2025",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_temporada(2025)
