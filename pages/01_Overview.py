import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

from src.ui.theme import apply_theme
from src.ui.sidebar import render_sidebar
from src.ui.components import page_header, insight_card, kpi_card, section_header, empty_state, plotly_light_layout
from src.state.data_context import DataContext
from src.intelligence.anomaly import detect_anomalies_inference
from src.intelligence.clustering import perform_clustering_inference

st.set_page_config(page_title="Executive Overview — SmartStock", layout="wide", page_icon="📊")
apply_theme()
render_sidebar()
DataContext.init()
df = DataContext.get_dataset()

page_header("Executive Overview", "Real-time retail performance, risk signals, and product intelligence at a glance.")

if df.empty:
    empty_state("No Dataset Active", "Load a dataset via Data Explorer to activate the intelligence dashboard.", "📊")
    st.stop()

# ──────────────────────────────────────────────
# DATA PREPARATION
# ──────────────────────────────────────────────
df['date'] = pd.to_datetime(df['date'])
max_date = df['date'].max()
p1 = df[df['date'] >= max_date - timedelta(days=30)]
p2 = df[(df['date'] >= max_date - timedelta(days=60)) & (df['date'] < max_date - timedelta(days=30))]

total_revenue = (df['sales'] * df['sell_price']).sum()
p1_revenue = (p1['sales'] * p1['sell_price']).sum()
p2_revenue = (p2['sales'] * p2['sell_price']).sum()
rev_growth = ((p1_revenue - p2_revenue) / p2_revenue * 100) if p2_revenue > 0 else 0

total_units = df['sales'].sum()
p1_units = p1['sales'].sum()
p2_units = p2['sales'].sum()
unit_growth = ((p1_units - p2_units) / p2_units * 100) if p2_units > 0 else 0

n_products = df['product_identifier'].nunique()
n_outlets = df['outlet'].nunique()
avg_price = df['sell_price'].mean()

try:
    anomaly_df = detect_anomalies_inference(df)
    n_anomalies = len(anomaly_df[anomaly_df['Anomaly'] == 'ANOMALY'])
except Exception:
    anomaly_df = pd.DataFrame()
    n_anomalies = 0

# ──────────────────────────────────────────────
# ROW 1: KPI CARDS
# ──────────────────────────────────────────────
section_header("Key Performance Indicators", "30-day vs previous 30-day comparison")

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    kpi_card("Total Revenue", f"₹{total_revenue/100000:,.1f}L", f"{rev_growth:+.1f}% MoM", "green" if rev_growth >= 0 else "red")
with c2:
    kpi_card("Units Sold (30d)", f"{p1_units:,.0f}", f"{unit_growth:+.1f}% MoM", "green" if unit_growth >= 0 else "red")
with c3:
    kpi_card("Products", f"{n_products}", f"{n_outlets} outlets")
with c4:
    kpi_card("Avg Price", f"₹{avg_price:,.0f}", "")
with c5:
    kpi_card("Anomalies", f"{n_anomalies}", "detected", "red" if n_anomalies > 10 else "green")

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# ROW 2: CHART 1 - Revenue & Demand Trend (Dual Axis)
# ──────────────────────────────────────────────
section_header("📈 Chart 1: Revenue & Demand Trend", "Daily aggregated revenue and unit volume over time")

daily = df.groupby('date').agg(
    Units=('sales', 'sum'),
    Revenue=('sales', lambda x: (x * df.loc[x.index, 'sell_price']).sum())
).reset_index()

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=daily['date'], y=daily['Revenue'], name='Revenue (₹)',
                           fill='tozeroy', fillcolor='rgba(99,102,241,0.1)',
                           line=dict(color='#6366f1', width=2)))
fig1.add_trace(go.Scatter(x=daily['date'], y=daily['Units'], name='Units Sold',
                           yaxis='y2', line=dict(color='#06b6d4', width=2, dash='dot')))
layout_opts = plotly_light_layout()
layout_opts.pop('yaxis', None)
layout_opts.pop('xaxis', None)
fig1.update_layout(**layout_opts,
                   title="Revenue & Demand Over Time",
                   yaxis=dict(title="Revenue (₹)", showgrid=True, gridcolor="rgba(99,102,241,0.06)"),
                   yaxis2=dict(title="Units", overlaying='y', side='right', showgrid=False))
st.plotly_chart(fig1, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 3: CHART 2 + CHART 3 Side by Side
# ──────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    section_header("📊 Chart 2: Category Revenue Split", "Revenue contribution by product category")
    cat_rev = df.groupby('category_of_product').apply(lambda x: (x['sales'] * x['sell_price']).sum()).reset_index()
    cat_rev.columns = ['Category', 'Revenue']
    fig2 = px.pie(cat_rev, values='Revenue', names='Category', hole=0.55,
                  color_discrete_sequence=['#6366f1', '#3b82f6', '#06b6d4', '#10b981', '#f59e0b'])
    fig2.update_layout(**plotly_light_layout(), title="Revenue by Category", showlegend=True)
    fig2.update_traces(textposition='outside', textinfo='percent+label',
                       textfont_size=11, marker=dict(line=dict(color='white', width=2)))
    st.plotly_chart(fig2, use_container_width=True)

with col_right:
    section_header("🔥 Chart 3: Demand Heatmap", "Weekly demand intensity by product")
    heat_df = df.copy()
    heat_df['week'] = heat_df['date'].dt.isocalendar().week.astype(int)
    heatmap_data = heat_df.groupby(['product_identifier', 'week'])['sales'].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='product_identifier', columns='week', values='sales').fillna(0)

    fig3 = px.imshow(heatmap_pivot, aspect='auto',
                     color_continuous_scale='Blues',
                     labels=dict(x="Week", y="Product", color="Units"))
    fig3.update_layout(**plotly_light_layout(), title="Product × Week Demand Heatmap")
    st.plotly_chart(fig3, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 4: CHART 4 - Top / Bottom Products
# ──────────────────────────────────────────────
section_header("🏆 Chart 4: Top & Bottom Products", "Products ranked by total revenue contribution")

prod_perf = df.groupby('product_identifier').apply(
    lambda x: pd.Series({
        'Revenue': (x['sales'] * x['sell_price']).sum(),
        'Units': x['sales'].sum(),
        'Avg_Price': x['sell_price'].mean()
    })
).reset_index()
prod_perf = prod_perf.sort_values('Revenue', ascending=True)

fig4 = px.bar(prod_perf, y='product_identifier', x='Revenue', orientation='h',
              color='Revenue', color_continuous_scale='Blues',
              hover_data=['Units', 'Avg_Price'])
fig4.update_layout(**plotly_light_layout(), title="Product Revenue Ranking",
                   yaxis_title="", xaxis_title="Revenue (₹)",
                   coloraxis_showscale=False, height=500)
st.plotly_chart(fig4, use_container_width=True)

# ──────────────────────────────────────────────
# ROW 5: CHART 5 - Clustering BCG Matrix
# ──────────────────────────────────────────────
section_header("🎯 Chart 5: Product Portfolio Matrix (BCG Style)", "Products mapped by volume vs variability — powered by KMeans clustering")

try:
    behavior_df, _ = perform_clustering_inference(df)
    if not behavior_df.empty:
        bcg_df = behavior_df.reset_index()
        fig5 = px.scatter(bcg_df, x='mean_sales', y='coefficient_of_variation',
                          color='Cluster_Name', size='mean_sales',
                          hover_data=['product_identifier'],
                          labels={'mean_sales': 'Average Daily Sales (Volume)',
                                  'coefficient_of_variation': 'Demand Variability (CV)'},
                          color_discrete_sequence=['#6366f1', '#3b82f6', '#10b981', '#f59e0b'])
        # Add quadrant lines
        x_mid = bcg_df['mean_sales'].median()
        y_mid = bcg_df['coefficient_of_variation'].median()
        fig5.add_hline(y=y_mid, line_dash="dash", line_color="rgba(100,116,139,0.3)")
        fig5.add_vline(x=x_mid, line_dash="dash", line_color="rgba(100,116,139,0.3)")
        # Add quadrant labels
        fig5.add_annotation(x=bcg_df['mean_sales'].max()*0.9, y=bcg_df['coefficient_of_variation'].min()*1.1,
                           text="⭐ Stars", showarrow=False, font=dict(size=11, color="#10b981"))
        fig5.add_annotation(x=bcg_df['mean_sales'].min()*1.1, y=bcg_df['coefficient_of_variation'].max()*0.95,
                           text="❓ Question Marks", showarrow=False, font=dict(size=11, color="#f59e0b"))
        fig5.update_layout(**plotly_light_layout(), title="BCG-Style Product Portfolio Matrix", height=500)
        st.plotly_chart(fig5, use_container_width=True)
except Exception as e:
    st.info(f"Product intelligence unavailable: {e}")

# ──────────────────────────────────────────────
# ROW 6: BUSINESS SIGNALS
# ──────────────────────────────────────────────
section_header("🧠 Automated Business Signals", "AI-generated insights based on your data patterns")

s1, s2, s3 = st.columns(3)

top_product = prod_perf.iloc[-1]
bottom_product = prod_perf.iloc[0]

with s1:
    insight_card("Revenue Leader", f"{top_product['product_identifier']} generates ₹{top_product['Revenue']:,.0f} in revenue — {top_product['Revenue']/total_revenue*100:.1f}% of total.",
                 "Ensure zero stockouts for this SKU.", "success")
with s2:
    if n_anomalies > 5:
        insight_card("Elevated Anomalies", f"{n_anomalies} demand anomalies detected across the dataset.",
                     "Review Anomaly Monitor for product-specific root cause analysis.", "warning")
    else:
        insight_card("Stable Demand", "Demand volatility is within historical norms.", "Maintain current strategy.", "success")
with s3:
    insight_card("Underperformer Alert", f"{bottom_product['product_identifier']} contributes only ₹{bottom_product['Revenue']:,.0f}.",
                 "Evaluate for markdown, bundle, or discontinuation.", "danger")
