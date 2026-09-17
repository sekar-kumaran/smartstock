import streamlit as st
import pandas as pd
from src.state.data_context import DataContext


def render_sidebar():
    """Professional sidebar with grouped navigation and dataset status."""
    with st.sidebar:
        # Brand header
        st.markdown("""
            <div style="padding:1.5rem 0 1.5rem 0;text-align:center;border-bottom:1px solid rgba(99,102,241,0.12);margin-bottom:1rem;">
                <div style="font-size:1.8rem;margin-bottom:4px;">📊</div>
                <h2 style="margin:0;font-size:1.3rem;font-weight:800;color:#0f172a !important;letter-spacing:-0.02em;">SmartStock</h2>
                <p style="margin:0;font-size:0.75rem;color:#6366f1 !important;font-weight:600;letter-spacing:0.05em;">RETAIL INTELLIGENCE</p>
            </div>
        """, unsafe_allow_html=True)

        # Navigation groups
        st.markdown('<p style="font-size:0.7rem;font-weight:700;color:#94a3b8 !important;letter-spacing:0.1em;margin-bottom:4px;">DASHBOARD</p>', unsafe_allow_html=True)
        st.page_link("pages/01_Overview.py", label="Executive Overview", icon="📊")

        st.markdown('<p style="font-size:0.7rem;font-weight:700;color:#94a3b8 !important;letter-spacing:0.1em;margin-top:16px;margin-bottom:4px;">FORECASTING</p>', unsafe_allow_html=True)
        st.page_link("pages/04_Demand_Forecasting.py", label="Demand Forecast", icon="📈")

        st.markdown('<p style="font-size:0.7rem;font-weight:700;color:#94a3b8 !important;letter-spacing:0.1em;margin-top:16px;margin-bottom:4px;">INTELLIGENCE</p>', unsafe_allow_html=True)
        st.page_link("pages/06_Product_Intelligence.py", label="Product Segments", icon="🎯")
        st.page_link("pages/07_Anomaly_Analysis.py", label="Anomaly Monitor", icon="🚨")
        st.page_link("pages/08_Inventory_Intelligence.py", label="Inventory Control", icon="📦")

        st.markdown('<p style="font-size:0.7rem;font-weight:700;color:#94a3b8 !important;letter-spacing:0.1em;margin-top:16px;margin-bottom:4px;">ANALYTICS</p>', unsafe_allow_html=True)
        st.page_link("pages/05_Model_Evaluation.py", label="Model Performance", icon="⚙️")
        st.page_link("pages/03_Training_vs_User.py", label="Data Comparison", icon="⚖️")
        st.page_link("pages/09_Reports.py", label="Executive Reports", icon="📄")

        st.markdown('<p style="font-size:0.7rem;font-weight:700;color:#94a3b8 !important;letter-spacing:0.1em;margin-top:16px;margin-bottom:4px;">DATA</p>', unsafe_allow_html=True)
        st.page_link("pages/02_Data_Explorer.py", label="Data Explorer", icon="🗄️")

        st.markdown("---")

        # Dataset status card
        mode = DataContext.get_mode()
        df = DataContext.get_dataset()

        days_str = "—"
        prod_str = "—"
        rows_str = "—"

        if not df.empty:
            rows_str = f"{len(df):,}"
            if 'date' in df.columns:
                days = (pd.to_datetime(df['date']).max() - pd.to_datetime(df['date']).min()).days
                days_str = f"{days} days"
            if 'product_identifier' in df.columns:
                prod_str = f"{df['product_identifier'].nunique()}"

        mode_color = "#6366f1" if mode == DataContext.MODE_DEMO else "#10b981"
        mode_label = "DEMO" if mode == DataContext.MODE_DEMO else "USER"

        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.6);backdrop-filter:blur(8px);border:1px solid rgba(99,102,241,0.1);border-radius:12px;padding:12px 14px;margin-top:8px;">
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px;">
                    <div style="width:8px;height:8px;border-radius:50%;background:{mode_color};"></div>
                    <span style="font-size:0.75rem;font-weight:700;color:{mode_color} !important;">{mode_label} DATASET</span>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">
                    <div>
                        <span style="font-size:0.65rem;color:#94a3b8 !important;font-weight:600;">ROWS</span><br>
                        <span style="font-size:0.85rem;font-weight:700;color:#0f172a !important;">{rows_str}</span>
                    </div>
                    <div>
                        <span style="font-size:0.65rem;color:#94a3b8 !important;font-weight:600;">PRODUCTS</span><br>
                        <span style="font-size:0.85rem;font-weight:700;color:#0f172a !important;">{prod_str}</span>
                    </div>
                    <div>
                        <span style="font-size:0.65rem;color:#94a3b8 !important;font-weight:600;">SPAN</span><br>
                        <span style="font-size:0.85rem;font-weight:700;color:#0f172a !important;">{days_str}</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("📂 Change Dataset", use_container_width=True):
            st.switch_page("pages/02_Data_Explorer.py")
