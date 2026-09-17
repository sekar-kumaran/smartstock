import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import timedelta

from src.ui.theme import apply_theme
from src.ui.sidebar import render_sidebar
from src.ui.components import page_header, insight_card, section_header, empty_state, kpi_card, plotly_light_layout
from src.state.data_context import DataContext
from src.forecasting.forecaster import generate_multi_day_forecast

st.set_page_config(page_title="Inventory Control — SmartStock", layout="wide", page_icon="📦")
apply_theme()
render_sidebar()
DataContext.init()
df = DataContext.get_dataset()

page_header("Inventory Control Center", "Forecast-driven reorder points, safety stock, and stockout risk assessment.")

if df.empty:
    empty_state("No Dataset Active", "Upload a dataset to access inventory intelligence.", "📦")
    st.stop()

mode = DataContext.get_mode()
if mode == DataContext.MODE_DEMO:
    st.info("💡 **Demo Context**: Simulated current stock levels are used for demonstration purposes.")

section_header("Operational Assumptions", "Configurable supply chain parameters")

c1, c2, c3 = st.columns(3)
lead_time = c1.slider("Lead Time (Days)", 1, 30, 7)
service_level = c2.slider("Service Level (%)", 50, 99, 95)
review_period = c3.slider("Review Period (Days)", 1, 30, 7)

z_score = norm.ppf(service_level / 100.0)

products = sorted(df['product_identifier'].unique())
sel_prod = st.selectbox("Target Product", options=products)
outlets = sorted(df[df['product_identifier'] == sel_prod]['outlet'].unique())
sel_out = st.selectbox("Target Outlet", options=outlets)

hist_sub = df[(df['product_identifier'] == sel_prod) & (df['outlet'] == sel_out)]
if hist_sub.empty:
    empty_state("No Data", "No historical data for this combination.", "ℹ️")
    st.stop()

start_date = pd.to_datetime(hist_sub['date']).max() + timedelta(days=1)

with st.spinner("Computing inventory parameters via LightGBM forecast..."):
    horizon = lead_time + review_period
    forecast = generate_multi_day_forecast(df, sel_prod, sel_out, start_date, horizon)

    lead_time_demand = forecast['predicted_sales'].head(lead_time).sum()
    daily_std = hist_sub['sales'].std()
    if pd.isna(daily_std):
        daily_std = 0

    safety_stock = z_score * daily_std * np.sqrt(lead_time)
    reorder_point = lead_time_demand + safety_stock

    avg_sales = max(1, hist_sub['sales'].mean())
    current_stock = avg_sales * (lead_time + 2) if mode == DataContext.MODE_DEMO else 0
    stockout_risk = max(0, min(100, (reorder_point - current_stock) / max(1, reorder_point) * 100))
    days_of_cover = current_stock / avg_sales
    order_qty = int(max(0, reorder_point - current_stock + safety_stock))

section_header("Replenishment Parameters", "Derived from LightGBM expected demand + operational assumptions")

m1, m2, m3, m4 = st.columns(4)
with m1: kpi_card("Safety Stock", f"{safety_stock:,.0f} units", "Buffer")
with m2: kpi_card("Reorder Point", f"{reorder_point:,.0f} units", "Threshold")
with m3: kpi_card("Days of Cover", f"{days_of_cover:.1f}", "Current Stock")
with m4: kpi_card("Stockout Risk", f"{stockout_risk:.1f}%", "Risk", "red" if stockout_risk > 30 else "green")

st.markdown("<br>", unsafe_allow_html=True)
section_header("Recommendation", "Action plan based on current inventory position")

if current_stock <= reorder_point:
    insight_card(f"⚠️ ORDER NOW: {sel_prod}", f"Current stock ({current_stock:,.0f}) is below reorder point ({reorder_point:,.0f}).",
                 f"Order {order_qty} units immediately to prevent stockout.", "danger")
elif current_stock <= reorder_point * 1.3:
    insight_card(f"🔶 WATCHLIST: {sel_prod}", f"Current stock ({current_stock:,.0f}) is approaching the reorder threshold.",
                 "Prepare for normal replenishment within the review period.", "warning")
else:
    insight_card(f"✅ HEALTHY: {sel_prod}", f"Current stock ({current_stock:,.0f}) with {days_of_cover:.1f} days of cover.",
                 "No immediate action required.", "success")
