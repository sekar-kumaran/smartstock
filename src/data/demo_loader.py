import pandas as pd
import streamlit as st
import os

@st.cache_data(show_spinner=False)
def load_demo_dataset() -> pd.DataFrame:
    path = "data/demo/smartstock_demo.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame()
