import streamlit as st
from src.config.settings import APP_NAME
from src.ui.theme import apply_theme
from src.ui.sidebar import render_sidebar

# Note: st.set_page_config must be the first Streamlit command used on a page
st.set_page_config(
    page_title=APP_NAME,
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global theme
apply_theme()

# In Streamlit, app.py acts as the main entry point, but pages/ handles routing.
# Streamlit >= 1.30 supports `st.navigation`, but for this app we're using the standard 
# sidebar navigation via `pages/`. We just need to redirect to Overview.
st.switch_page("pages/01_Overview.py")
