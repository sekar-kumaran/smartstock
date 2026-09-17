import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta

from src.ui.theme import apply_theme
from src.ui.sidebar import render_sidebar
from src.ui.components import page_header, insight_card, section_header, empty_state, kpi_card, plotly_light_layout
from src.state.data_context import DataContext
from src.forecasting.forecaster import generate_multi_day_forecast

st.set_page_config(page_title="Demand Forecasting — SmartStock", layout="wide", page_icon="📈")
apply_theme()
render_sidebar()
DataContext.init()
df = DataContext.get_dataset()

page_header("Demand Forecasting", "LightGBM-powered demand prediction with scenario simulation and price sensitivity analysis.")

if df.empty:
    empty_state("No Dataset Active", "Upload a dataset to access demand forecasting.", "📈")
    st.stop()

tab_forecast, tab_scenario, tab_sensitivity = st.tabs(["📈 Forecast Explorer", "🔬 Scenario Simulator", "💰 Price Sensitivity"])

products = sorted(df['product_identifier'].unique())

# ──────────────────────────────────────────────
# TAB 1: FORECAST EXPLORER
# ──────────────────────────────────────────────
with tab_forecast:
    section_header("Forecast Configuration", "Select a product-outlet combination and forecast horizon")

    c1, c2, c3 = st.columns(3)
    sel_prod = c1.selectbox("Product", options=products, key="fc_prod")
    outlets = sorted(df[df['product_identifier'] == sel_prod]['outlet'].unique())
    sel_out = c2.selectbox("Outlet", options=outlets, key="fc_out")
    horizon = c3.selectbox("Horizon", options=[7, 14, 30], format_func=lambda x: f"{x} days", key="fc_horizon")

    hist_sub = df[(df['product_identifier'] == sel_prod) & (df['outlet'] == sel_out)].copy()

    if hist_sub.empty:
        empty_state("No Data", "No historical data for this product-outlet combination.", "ℹ️")
    else:
        start_date = pd.to_datetime(hist_sub['date']).max() + timedelta(days=1)

        with st.spinner("Running LightGBM inference..."):
            try:
                forecast = generate_multi_day_forecast(df, sel_prod, sel_out, start_date, horizon)

                tot = forecast['predicted_sales'].sum()
                avg = forecast['predicted_sales'].mean()
                peak = forecast['predicted_sales'].max()
                price = hist_sub['sell_price'].iloc[-1] if 'sell_price' in hist_sub.columns else 0
                rev = tot * price

                # KPIs
                k1, k2, k3, k4 = st.columns(4)
                with k1: kpi_card("Expected Demand", f"{tot:,.0f} units", f"{horizon}d horizon")
                with k2: kpi_card("Expected Revenue", f"₹{rev:,.0f}", f"@ ₹{price:.0f}/unit")
                with k3: kpi_card("Avg Daily", f"{avg:.1f} units", "")
                with k4: kpi_card("Peak Day", f"{peak:.0f} units", "")

                st.markdown("<br>", unsafe_allow_html=True)

                # CHART 9: Forecast vs Historical
                section_header("📈 Chart 9: Forecast vs Historical", "Historical demand overlaid with LightGBM predictions")

                h_plot = hist_sub[['date', 'sales']].tail(60).copy()
                h_plot.columns = ['date', 'Demand']
                h_plot['Type'] = 'Historical'

                f_plot = forecast[['date', 'predicted_sales']].copy()
                f_plot.columns = ['date', 'Demand']
                f_plot['Type'] = 'Forecast'

                plot_df = pd.concat([h_plot, f_plot])

                fig9 = go.Figure()
                fig9.add_trace(go.Scatter(x=h_plot['date'], y=h_plot['Demand'], name='Historical',
                                          line=dict(color='#64748b', width=2), fill='tozeroy',
                                          fillcolor='rgba(100,116,139,0.08)'))
                fig9.add_trace(go.Scatter(x=f_plot['date'], y=f_plot['Demand'], name='Forecast',
                                          line=dict(color='#3b82f6', width=3), fill='tozeroy',
                                          fillcolor='rgba(59,130,246,0.1)'))
                fig9.update_layout(**plotly_light_layout(), title=f"Demand Forecast: {sel_prod} @ {sel_out}", height=400)
                st.plotly_chart(fig9, use_container_width=True)

                # CHART 10: Top 10 Growth Products
                section_header("🚀 Chart 10: Forecasted Growth Leaders", "Products with highest predicted demand over next period")

                growth_data = []
                for prod in products[:10]:  # top 10 for speed
                    p_outs = df[df['product_identifier'] == prod]['outlet'].unique()
                    if len(p_outs) > 0:
                        p_hist = df[(df['product_identifier'] == prod) & (df['outlet'] == p_outs[0])]
                        if not p_hist.empty:
                            hist_avg = p_hist['sales'].tail(14).mean()
                            try:
                                p_fc = generate_multi_day_forecast(df, prod, p_outs[0],
                                                                   pd.to_datetime(p_hist['date']).max() + timedelta(days=1), 7)
                                fc_avg = p_fc['predicted_sales'].mean()
                                growth = ((fc_avg - hist_avg) / hist_avg * 100) if hist_avg > 0 else 0
                                growth_data.append({'Product': prod, 'Historical Avg': hist_avg,
                                                   'Forecast Avg': fc_avg, 'Growth %': growth})
                            except Exception:
                                pass

                if growth_data:
                    growth_df = pd.DataFrame(growth_data).sort_values('Growth %', ascending=True)
                    colors = ['#10b981' if g >= 0 else '#ef4444' for g in growth_df['Growth %']]
                    fig10 = px.bar(growth_df, y='Product', x='Growth %', orientation='h',
                                  color='Growth %', color_continuous_scale='RdYlGn', color_continuous_midpoint=0)
                    fig10.update_layout(**plotly_light_layout(), title="Predicted Demand Growth (Next 7 Days vs Last 14 Days)",
                                       coloraxis_showscale=False, height=400)
                    st.plotly_chart(fig10, use_container_width=True)

            except Exception as e:
                st.error(f"Forecast failed: {e}")

# ──────────────────────────────────────────────
# TAB 2: SCENARIO SIMULATOR
# ──────────────────────────────────────────────
with tab_scenario:
    section_header("What-If Scenario", "Mutate price and demand inputs without retraining the model")

    s_prod = st.selectbox("Product", options=products, key="sc_prod")
    s_out = st.selectbox("Outlet", options=sorted(df[df['product_identifier'] == s_prod]['outlet'].unique()), key="sc_out")

    sc1, sc2 = st.columns(2)
    p_adj = sc1.slider("Price Change (%)", -30, 30, 0, 1)
    d_adj = sc2.slider("Demand Multiplier", 0.5, 2.0, 1.0, 0.1)

    if st.button("Run Scenario", type="primary", key="run_scenario"):
        with st.spinner("Simulating..."):
            hist_sub = df[(df['product_identifier'] == s_prod) & (df['outlet'] == s_out)]
            start_date = pd.to_datetime(hist_sub['date']).max() + timedelta(days=1)
            base_price = hist_sub['sell_price'].iloc[-1] if 'sell_price' in hist_sub.columns else 0

            try:
                base = generate_multi_day_forecast(df, s_prod, s_out, start_date, 30)
                base_demand = base['predicted_sales'].sum()
                base_rev = base_demand * base_price

                sim_df = df.copy()
                sim_df.loc[sim_df['product_identifier'] == s_prod, 'sell_price'] *= (1 + p_adj / 100)
                sim_df.loc[sim_df['product_identifier'] == s_prod, 'sales'] *= d_adj

                scene = generate_multi_day_forecast(sim_df, s_prod, s_out, start_date, 30)
                scene_demand = scene['predicted_sales'].sum()
                scene_rev = scene_demand * base_price * (1 + p_adj / 100)

                dem_delta = ((scene_demand - base_demand) / base_demand * 100) if base_demand > 0 else 0
                rev_delta = ((scene_rev - base_rev) / base_rev * 100) if base_rev > 0 else 0

                k1, k2, k3 = st.columns(3)
                with k1: kpi_card("Baseline Demand", f"{base_demand:,.0f}", "30 days")
                with k2: kpi_card("Scenario Demand", f"{scene_demand:,.0f}", f"{dem_delta:+.1f}%",
                                  "green" if dem_delta >= 0 else "red")
                with k3: kpi_card("Revenue Impact", f"₹{scene_rev:,.0f}", f"{rev_delta:+.1f}%",
                                  "green" if rev_delta >= 0 else "red")

                # CHART 11: Revenue Waterfall
                section_header("📊 Chart 11: Revenue Waterfall", "Baseline → Price Effect → Volume Effect → Scenario")

                price_effect = (scene_rev - base_rev) * 0.6  # approximate split
                volume_effect = (scene_rev - base_rev) * 0.4

                fig11 = go.Figure(go.Waterfall(
                    x=["Baseline Revenue", "Price Effect", "Volume Effect", "Scenario Revenue"],
                    measure=["absolute", "relative", "relative", "total"],
                    y=[base_rev, price_effect, volume_effect, scene_rev],
                    connector={"line": {"color": "#e2e8f0"}},
                    increasing={"marker": {"color": "#10b981"}},
                    decreasing={"marker": {"color": "#ef4444"}},
                    totals={"marker": {"color": "#3b82f6"}}
                ))
                fig11.update_layout(**plotly_light_layout(), title="Revenue Impact Waterfall", height=400)
                st.plotly_chart(fig11, use_container_width=True)

            except Exception as e:
                st.error(f"Scenario failed: {e}")

# ──────────────────────────────────────────────
# TAB 3: PRICE SENSITIVITY
# ──────────────────────────────────────────────
with tab_sensitivity:
    section_header("Price Sensitivity Analysis", "How does demand respond to incremental price changes?")

    ps_prod = st.selectbox("Product", options=products, key="ps_prod")
    ps_out = st.selectbox("Outlet", options=sorted(df[df['product_identifier'] == ps_prod]['outlet'].unique()), key="ps_out")

    if st.button("Analyze Price Sensitivity", type="primary", key="run_ps"):
        with st.spinner("Computing price elasticity curve..."):
            hist_sub = df[(df['product_identifier'] == ps_prod) & (df['outlet'] == ps_out)]
            start_date = pd.to_datetime(hist_sub['date']).max() + timedelta(days=1)
            base_price = hist_sub['sell_price'].iloc[-1] if 'sell_price' in hist_sub.columns else 1

            curve_data = []
            for pct in range(-20, 25, 5):
                sim_df = df.copy()
                sim_df.loc[sim_df['product_identifier'] == ps_prod, 'sell_price'] *= (1 + pct / 100)
                try:
                    fc = generate_multi_day_forecast(sim_df, ps_prod, ps_out, start_date, 14)
                    demand = fc['predicted_sales'].sum()
                    price = base_price * (1 + pct / 100)
                    revenue = demand * price
                    curve_data.append({'Price Change (%)': pct, 'Price (₹)': price,
                                      'Predicted Demand': demand, 'Predicted Revenue': revenue})
                except Exception:
                    pass

            if curve_data:
                # CHART 12: Price Sensitivity Curve
                section_header("📈 Chart 12: Price-Demand Curve", "Demand elasticity across price scenarios")

                curve_df = pd.DataFrame(curve_data)
                fig12 = go.Figure()
                fig12.add_trace(go.Scatter(x=curve_df['Price Change (%)'], y=curve_df['Predicted Demand'],
                                           name='Demand', line=dict(color='#3b82f6', width=3),
                                           fill='tozeroy', fillcolor='rgba(59,130,246,0.08)'))
                fig12.add_trace(go.Scatter(x=curve_df['Price Change (%)'], y=curve_df['Predicted Revenue'],
                                           name='Revenue', yaxis='y2',
                                           line=dict(color='#10b981', width=3, dash='dot')))
                fig12.add_vline(x=0, line_dash="dash", line_color="rgba(100,116,139,0.3)")
                layout_opts = plotly_light_layout()
                layout_opts.pop('yaxis', None)
                layout_opts.pop('xaxis', None)
                fig12.update_layout(**layout_opts,
                                   title="Price Sensitivity: Demand & Revenue Response",
                                   xaxis_title="Price Change (%)",
                                   yaxis=dict(title="Predicted Demand (units)"),
                                   yaxis2=dict(title="Predicted Revenue (₹)", overlaying='y', side='right'),
                                   height=450)
                st.plotly_chart(fig12, use_container_width=True)

                # Find optimal price point
                optimal = curve_df.loc[curve_df['Predicted Revenue'].idxmax()]
                insight_card("Revenue-Maximizing Price",
                             f"The optimal price point is ₹{optimal['Price (₹)']:.0f} ({optimal['Price Change (%)']:+.0f}% from current), yielding ₹{optimal['Predicted Revenue']:,.0f} in estimated revenue.",
                             "Consider adjusting pricing strategy to capture maximum revenue.", "success")
            else:
                st.warning("Unable to compute price sensitivity for this product.")
