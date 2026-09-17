import pandas as pd
import streamlit as st

@st.cache_data(show_spinner="Parsing and caching dataset...")
def load_csv(uploaded_file) -> pd.DataFrame:
    """Loads a CSV file into a Pandas DataFrame."""
    try:
        # Assuming comma separated for now
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
        return pd.DataFrame()

from src.state.data_context import DataContext

def init_data_session():
    """Initializes Streamlit session state for data."""
    DataContext.init()

