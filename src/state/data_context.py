import streamlit as st
import pandas as pd
from typing import Optional

class DataContext:
    MODE_DEMO = "DEMO"
    MODE_USER = "USER"
    MODE_SCENARIO = "SCENARIO"
    
    @staticmethod
    def init():
        if "data_mode" not in st.session_state:
            st.session_state.data_mode = DataContext.MODE_DEMO
        if "demo_data" not in st.session_state:
            from src.data.demo_loader import load_demo_dataset
            st.session_state.demo_data = load_demo_dataset()
        if "user_data" not in st.session_state:
            st.session_state.user_data = None
            
    @staticmethod
    def get_mode() -> str:
        return st.session_state.get("data_mode", DataContext.MODE_DEMO)
        
    @staticmethod
    def get_dataset() -> Optional[pd.DataFrame]:
        mode = DataContext.get_mode()
        if mode == DataContext.MODE_USER and st.session_state.get("user_data") is not None:
            return st.session_state.user_data
        return st.session_state.get("demo_data", pd.DataFrame())
        
    @staticmethod
    def set_user_dataset(df: pd.DataFrame):
        st.session_state.user_data = df
        st.session_state.data_mode = DataContext.MODE_USER
        
    @staticmethod
    def restore_demo():
        st.session_state.data_mode = DataContext.MODE_DEMO
        
    @staticmethod
    def has_user_data() -> bool:
        return st.session_state.get("user_data") is not None
