import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.ui.theme import apply_theme
from src.ui.sidebar import render_sidebar
from src.ui.components import page_header, insight_card, section_header, empty_state, kpi_card, plotly_light_layout
from src.state.data_context import DataContext
from src.intelligence.clustering import perform_clustering_inference, find_similar_products
from src.models.artifact_loader import load_clustering_artifacts

st.set_page_config(page_title="Product Intelligence — SmartStock", layout="wide", page_icon="🎯")
apply_theme()
render_sidebar()
DataContext.init()
df = DataContext.get_dataset()

page_header("Product Intelligence", "AI-powered product segmentation using KMeans clustering and PCA dimensionality reduction.")

try:
    kmeans, scaler, pca, profiles, features_meta, behavior_matrix, index_meta = load_clustering_artifacts()
except Exception:
    empty_state("Clustering Artifacts Missing", "The offline KMeans model has not been trained. Please run the training pipeline.", "⚠️")
    st.stop()

if df.empty:
    empty_state("No Dataset Active", "Upload a dataset to activate product intelligence.", "🗄️")
    st.stop()

with st.spinner("Mapping product catalog against KMeans clusters..."):
    behavior_df, scaled_features = perform_clustering_inference(df)

if behavior_df.empty:
    empty_state("Insufficient Data", "Cannot extract behavioral features from the current dataset.", "ℹ️")
    st.stop()

# ──────────────────────────────────────────────
# KPI ROW
# ──────────────────────────────────────────────
n_clusters = behavior_df['Cluster_Name'].nunique()
n_products = len(behavior_df)
dist = behavior_df['Cluster_Name'].value_counts()
largest_segment = dist.index[0]

section_header("Segmentation Summary", f"{n_products} products classified into {n_clusters} behavioral segments")

c1, c2, c3, c4 = st.columns(4)
for idx, (name, count) in enumerate(dist.items()):
    with [c1, c2, c3, c4][idx % 4]:
        kpi_card(name, f"{count} products", f"{count/n_products*100:.0f}% of catalog")

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# CHART 6: PCA Product Behavior Map
# ──────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    section_header("📍 Chart 6: Product Behavior Map", "PCA-projected product positions in behavioral space")
    if 'PCA_1' in behavior_df.columns:
        plot_df = behavior_df.reset_index()
        fig6 = px.scatter(plot_df, x='PCA_1', y='PCA_2', color='Cluster_Name',
                          size='mean_sales', hover_data=['product_identifier', 'mean_sales', 'coefficient_of_variation'],
                          labels={'PCA_1': 'Behavioral Dimension 1', 'PCA_2': 'Behavioral Dimension 2'},
                          color_discrete_sequence=['#6366f1', '#3b82f6', '#10b981', '#f59e0b'])
        fig6.update_layout(**plotly_light_layout(), title="Product Behavior Map (PCA)", height=450)
        fig6.update_traces(marker=dict(line=dict(width=1, color='white')))
        st.plotly_chart(fig6, use_container_width=True)

# ──────────────────────────────────────────────
# CHART 7: Cluster Radar / Spider Chart
# ──────────────────────────────────────────────
with col_right:
    section_header("🕸️ Chart 7: Segment Radar Chart", "Comparing segment profiles across behavioral dimensions")

    # Build radar data from actual cluster statistics
    radar_features = ['mean_sales', 'sales_std', 'coefficient_of_variation', 'zero_sales_ratio', 'median_sales']
    available_features = [f for f in radar_features if f in behavior_df.columns]

    if len(available_features) >= 3:
        cluster_means = behavior_df.groupby('Cluster_Name')[available_features].mean()
        # Normalize to 0-1 for radar
        normalized = (cluster_means - cluster_means.min()) / (cluster_means.max() - cluster_means.min() + 1e-9)

        fig7 = go.Figure()
        colors = ['#6366f1', '#3b82f6', '#10b981', '#f59e0b']
        for idx, (cluster_name, row) in enumerate(normalized.iterrows()):
            fig7.add_trace(go.Scatterpolar(
                r=row.values.tolist() + [row.values[0]],  # close the polygon
                theta=available_features + [available_features[0]],
                fill='toself',
                fillcolor=f"rgba({int(colors[idx % len(colors)][1:3], 16)},{int(colors[idx % len(colors)][3:5], 16)},{int(colors[idx % len(colors)][5:7], 16)},0.15)",
                line=dict(color=colors[idx % len(colors)], width=2),
                name=cluster_name
            ))
        fig7.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1], showticklabels=False, gridcolor="rgba(99,102,241,0.1)"),
                bgcolor="rgba(255,255,255,0)"
            ),
            paper_bgcolor="rgba(255,255,255,0)",
            font=dict(family="Inter, sans-serif", color="#334155"),
            title="Segment Profile Comparison",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            height=450
        )
        st.plotly_chart(fig7, use_container_width=True)

# ──────────────────────────────────────────────
# CHART 8: Segment Revenue Contribution (Stacked)
# ──────────────────────────────────────────────
section_header("💰 Chart 8: Segment Revenue Contribution", "How much revenue does each behavioral segment generate?")

# Merge cluster labels back into original data
prod_clusters = behavior_df[['Cluster_Name']].reset_index()
merged = df.merge(prod_clusters, on='product_identifier', how='left')
merged['Revenue'] = merged['sales'] * merged['sell_price']

seg_rev = merged.groupby('Cluster_Name')['Revenue'].sum().reset_index()
seg_rev = seg_rev.sort_values('Revenue', ascending=False)

fig8 = px.bar(seg_rev, x='Cluster_Name', y='Revenue',
              color='Cluster_Name',
              color_discrete_sequence=['#6366f1', '#3b82f6', '#10b981', '#f59e0b'],
              text_auto='.2s')
fig8.update_layout(**plotly_light_layout(), title="Revenue by Product Segment",
                   xaxis_title="", yaxis_title="Revenue (₹)", showlegend=False)
fig8.update_traces(textposition='outside', marker_line_width=0)
st.plotly_chart(fig8, use_container_width=True)

# ──────────────────────────────────────────────
# SEGMENT STRATEGIES
# ──────────────────────────────────────────────
section_header("📋 Segment Strategy Recommendations", "AI-generated operational guidance for each segment")

strategy_cols = st.columns(min(len(dist), 4))
for idx, (name, count) in enumerate(dist.items()):
    with strategy_cols[idx % 4]:
        profile = profiles.get(str(behavior_df[behavior_df['Cluster_Name'] == name]['Cluster'].iloc[0]), {})
        strategy = profile.get('strategy', 'Monitor performance closely.')

        if 'High Volume' in name or 'Stable' in name or 'Steady' in name:
            level = "success"
        elif 'Volatile' in name:
            level = "warning"
        elif 'Risky' in name or 'Low' in name:
            level = "danger"
        else:
            level = "info"

        insight_card(name, f"{count} products in this segment.", strategy, level)

# ──────────────────────────────────────────────
# SIMILAR PRODUCTS FINDER
# ──────────────────────────────────────────────
section_header("🔍 Similar Product Finder", "Find behaviorally similar products using cosine similarity on cluster features")

sel_prod = st.selectbox("Select a product", options=behavior_df.index.tolist())
if sel_prod:
    sim_df = find_similar_products(sel_prod, behavior_df, scaled_features, top_n=5)
    if not sim_df.empty:
        st.dataframe(sim_df, use_container_width=True, hide_index=True)
    else:
        st.info("No similar products found in the reference set.")

# ──────────────────────────────────────────────
# FULL CATALOG TABLE
# ──────────────────────────────────────────────
section_header("📊 Full Catalog Data", "Complete behavioral feature matrix with cluster assignments")

display_df = behavior_df.reset_index()
format_dict = {c: '{:.2f}' for c in display_df.select_dtypes(include=[np.number]).columns}
st.dataframe(display_df, use_container_width=True, hide_index=True)
