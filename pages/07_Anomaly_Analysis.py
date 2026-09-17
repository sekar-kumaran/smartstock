import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.ui.theme import apply_theme
from src.ui.sidebar import render_sidebar
from src.ui.components import page_header, insight_card, section_header, empty_state, kpi_card, plotly_light_layout
from src.state.data_context import DataContext
from src.intelligence.anomaly import detect_anomalies_inference

st.set_page_config(page_title="Anomaly Monitor — SmartStock", layout="wide", page_icon="🚨")
apply_theme()
render_sidebar()
DataContext.init()
df = DataContext.get_dataset()

page_header("Demand Anomaly Monitor", "Isolation Forest-powered anomaly detection across your retail network.")

if df.empty:
    empty_state("No Dataset Active", "Upload a dataset to activate anomaly monitoring.", "🚨")
    st.stop()

df['date'] = pd.to_datetime(df['date'])

@st.cache_data(show_spinner=False)
def get_anomalies(data):
    return detect_anomalies_inference(data.sort_values(by=['outlet', 'product_identifier', 'date']))

with st.spinner("Running Isolation Forest inference..."):
    anomaly_df = get_anomalies(df)

anomalies_only = anomaly_df[anomaly_df['Anomaly'] == 'ANOMALY']
n_total = len(anomaly_df)
n_anomalies = len(anomalies_only)
anomaly_rate = (n_anomalies / n_total * 100) if n_total > 0 else 0

# Classify direction
if not anomalies_only.empty:
    anomalies_only = anomalies_only.copy()
    anomalies_only['Direction'] = anomalies_only.apply(
        lambda x: 'SPIKE' if x['sales'] > x.get('rolling_mean_14', x['sales']) else 'DROP', axis=1)
    n_spikes = len(anomalies_only[anomalies_only['Direction'] == 'SPIKE'])
    n_drops = len(anomalies_only[anomalies_only['Direction'] == 'DROP'])
else:
    n_spikes = n_drops = 0

# ──────────────────────────────────────────────
# KPIs
# ──────────────────────────────────────────────
section_header("Monitor Overview", "Real-time anomaly statistics")

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Total Anomalies", f"{n_anomalies}", f"{anomaly_rate:.1f}% of data", "red" if anomaly_rate > 5 else "green")
with c2: kpi_card("Demand Spikes", f"{n_spikes}", "Above baseline", "red")
with c3: kpi_card("Demand Drops", f"{n_drops}", "Below baseline", "red")
with c4: kpi_card("Products Affected", f"{anomalies_only['product_identifier'].nunique() if not anomalies_only.empty else 0}",
                  f"of {df['product_identifier'].nunique()}")

st.markdown("<br>", unsafe_allow_html=True)

if anomalies_only.empty:
    empty_state("System Stable", "No significant anomalies detected by the Isolation Forest model.", "✅")
    st.stop()

# ──────────────────────────────────────────────
# CHART: Anomaly Timeline
# ──────────────────────────────────────────────
section_header("⏱️ Anomaly Timeline", "Demand events classified by the Isolation Forest model")

sel_filter = st.selectbox("Filter by Product", options=["All Products"] + sorted(anomalies_only['product_identifier'].unique().tolist()))

plot_data = anomaly_df.copy()
if sel_filter != "All Products":
    plot_data = plot_data[plot_data['product_identifier'] == sel_filter]

fig_timeline = go.Figure()

normal = plot_data[plot_data['Anomaly'] == 'NORMAL']
fig_timeline.add_trace(go.Scatter(x=normal['date'], y=normal['sales'], mode='markers',
                                   name='Normal', marker=dict(color='#94a3b8', size=5, opacity=0.4),
                                   hovertemplate="<b>%{text}</b><br>Date: %{x}<br>Sales: %{y}<extra></extra>",
                                   text=normal['product_identifier']))

for direction, color, symbol in [("SPIKE", "#ef4444", "triangle-up"), ("DROP", "#f59e0b", "triangle-down")]:
    d_df = anomalies_only[anomalies_only['Direction'] == direction]
    if sel_filter != "All Products":
        d_df = d_df[d_df['product_identifier'] == sel_filter]
    if not d_df.empty:
        fig_timeline.add_trace(go.Scatter(x=d_df['date'], y=d_df['sales'], mode='markers',
                                          name=f'Anomaly ({direction})',
                                          marker=dict(color=color, size=10, symbol=symbol,
                                                      line=dict(width=1.5, color='white')),
                                          hovertemplate="<b>%{text}</b><br>Date: %{x}<br>Sales: %{y}<extra></extra>",
                                          text=d_df['product_identifier']))

fig_timeline.update_layout(**plotly_light_layout(), title="Demand Anomaly Timeline", height=450)
st.plotly_chart(fig_timeline, use_container_width=True)

# ──────────────────────────────────────────────
# CHART: Risk Heatmap (Product × Outlet)
# ──────────────────────────────────────────────
section_header("🗺️ Stockout Risk Heatmap", "Anomaly concentration by product and outlet")

risk_matrix = anomalies_only.groupby(['product_identifier', 'outlet']).size().reset_index(name='Anomaly Count')
risk_pivot = risk_matrix.pivot(index='product_identifier', columns='outlet', values='Anomaly Count').fillna(0)

fig_heat = px.imshow(risk_pivot, aspect='auto', color_continuous_scale='OrRd',
                     labels=dict(x="Outlet", y="Product", color="Anomalies"))
fig_heat.update_layout(**plotly_light_layout(), title="Product × Outlet Risk Concentration", height=450)
st.plotly_chart(fig_heat, use_container_width=True)

# ──────────────────────────────────────────────
# TOP ANOMALY INTERPRETATIONS
# ──────────────────────────────────────────────
section_header("🧠 Top Anomaly Interpretations", "Business context for the most significant demand anomalies")

top_anomalies = anomalies_only.sort_values('Anomaly_Score').head(5)
for _, row in top_anomalies.iterrows():
    date_str = row['date'].strftime('%Y-%m-%d')
    prod = row['product_identifier']
    direction = row['Direction']

    if direction == 'SPIKE':
        insight_card(f"Demand Spike — {prod} — {date_str}",
                     f"Sales of {row['sales']:.0f} units significantly exceeded the 14-day rolling mean of {row.get('rolling_mean_14', 0):.1f}.",
                     "Check for promotional events. Verify inventory can sustain elevated demand.", "danger")
    else:
        insight_card(f"Demand Drop — {prod} — {date_str}",
                     f"Sales of {row['sales']:.0f} units fell sharply below the 14-day rolling mean of {row.get('rolling_mean_14', 0):.1f}.",
                     "Investigate competition, pricing changes, or supply disruptions.", "warning")
