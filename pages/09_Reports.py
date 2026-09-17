import streamlit as st
import pandas as pd
import io
from datetime import datetime
from fpdf import FPDF

from src.ui.theme import apply_theme
from src.ui.sidebar import render_sidebar
from src.ui.components import page_header, insight_card, section_header, empty_state, kpi_card
from src.state.data_context import DataContext
from src.intelligence.anomaly import detect_anomalies_inference

st.set_page_config(page_title="Executive Reports — SmartStock", layout="wide", page_icon="📄")
apply_theme()
render_sidebar()
DataContext.init()
df = DataContext.get_dataset()

page_header("Executive Reports", "Generate management-ready PDF and CSV summaries of retail intelligence.")

if df.empty:
    empty_state("No Dataset Active", "Upload a dataset to generate reports.", "📄")
    st.stop()

mode = DataContext.get_mode()

# ──────────────────────────────────────────────
# COMPUTE REPORT DATA
# ──────────────────────────────────────────────
df['date'] = pd.to_datetime(df['date'])
total_units = df['sales'].sum()
total_revenue = (df['sales'] * df['sell_price']).sum() if 'sell_price' in df.columns else 0
n_products = df['product_identifier'].nunique()
n_outlets = df['outlet'].nunique()
date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"

try:
    anomaly_df = detect_anomalies_inference(df)
    n_anomalies = len(anomaly_df[anomaly_df['Anomaly'] == 'ANOMALY'])
except Exception:
    n_anomalies = 0

# Top products
top_products = df.groupby('product_identifier').apply(
    lambda x: (x['sales'] * x['sell_price']).sum()).reset_index()
top_products.columns = ['Product', 'Revenue']
top_products = top_products.sort_values('Revenue', ascending=False).head(5)

# Category split
cat_rev = df.groupby('category_of_product').apply(
    lambda x: (x['sales'] * x['sell_price']).sum()).reset_index()
cat_rev.columns = ['Category', 'Revenue']
cat_rev['Share'] = (cat_rev['Revenue'] / cat_rev['Revenue'].sum() * 100).round(1)

# ──────────────────────────────────────────────
# PREVIEW
# ──────────────────────────────────────────────
section_header("Report Preview", "Review before downloading")

now = datetime.now().strftime('%Y-%m-%d %H:%M')
mode_label = "DEMO" if mode == DataContext.MODE_DEMO else "USER"

st.markdown(f"""
    <div style="background:rgba(255,255,255,0.75);backdrop-filter:blur(12px);border:1px solid rgba(99,102,241,0.1);border-radius:16px;padding:2rem;margin-bottom:1.5rem;">
        <h2 style="color:#0f172a !important;margin-bottom:4px;">SmartStock Executive Intelligence Report</h2>
        <p style="color:#64748b !important;font-size:0.9rem;">Generated: {now} | Dataset: {mode_label} | Coverage: {date_range}</p>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Total Revenue", f"₹{total_revenue/100000:,.1f}L", "")
with c2: kpi_card("Total Units", f"{total_units:,.0f}", "")
with c3: kpi_card("Products", f"{n_products}", f"{n_outlets} outlets")
with c4: kpi_card("Anomalies", f"{n_anomalies}", "", "red" if n_anomalies > 5 else "green")

st.markdown("<br>", unsafe_allow_html=True)

section_header("Top Products by Revenue")
st.dataframe(top_products, use_container_width=True, hide_index=True)

section_header("Category Revenue Share")
st.dataframe(cat_rev, use_container_width=True, hide_index=True)

section_header("Key Findings")
if n_anomalies > 5:
    insight_card("Elevated Demand Volatility", f"{n_anomalies} demand anomalies detected.",
                 "Review the Anomaly Monitor for product-specific root causes.", "warning")
else:
    insight_card("Stable Operations", "Demand volatility is within normal ranges.",
                 "Maintain current replenishment strategy.", "success")

# ──────────────────────────────────────────────
# EXPORT: CSV
# ──────────────────────────────────────────────
section_header("Download Reports")

csv_data = pd.DataFrame({
    "Metric": ["Report Date", "Dataset Mode", "Data Coverage", "Total Revenue",
               "Total Units", "Products", "Outlets", "Anomalies"],
    "Value": [now, mode_label, date_range, f"₹{total_revenue:,.0f}",
              total_units, n_products, n_outlets, n_anomalies]
})

col_csv, col_pdf = st.columns(2)

with col_csv:
    st.download_button("📊 Download CSV Report", data=csv_data.to_csv(index=False),
                       file_name=f"SmartStock_Report_{datetime.now().strftime('%Y%m%d')}.csv",
                       mime='text/csv', use_container_width=True)

# ──────────────────────────────────────────────
# EXPORT: PDF
# ──────────────────────────────────────────────
with col_pdf:
    if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF..."):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 20)
            pdf.cell(0, 15, "SmartStock Intelligence Report", ln=True, align="C")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 8, f"Generated: {now} | Dataset: {mode_label}", ln=True, align="C")
            pdf.cell(0, 8, f"Coverage: {date_range}", ln=True, align="C")
            pdf.ln(10)

            # KPIs
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Key Performance Indicators", ln=True)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, f"Total Revenue: Rs {total_revenue:,.0f}", ln=True)
            pdf.cell(0, 8, f"Total Units Sold: {total_units:,.0f}", ln=True)
            pdf.cell(0, 8, f"Products Monitored: {n_products}", ln=True)
            pdf.cell(0, 8, f"Outlets: {n_outlets}", ln=True)
            pdf.cell(0, 8, f"Demand Anomalies: {n_anomalies}", ln=True)
            pdf.ln(8)

            # Top Products
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Top Products by Revenue", ln=True)
            pdf.set_font("Helvetica", "", 10)
            for _, row in top_products.iterrows():
                pdf.cell(0, 7, f"  {row['Product']}: Rs {row['Revenue']:,.0f}", ln=True)
            pdf.ln(8)

            # Category Revenue
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Category Revenue Share", ln=True)
            pdf.set_font("Helvetica", "", 10)
            for _, row in cat_rev.iterrows():
                pdf.cell(0, 7, f"  {row['Category']}: Rs {row['Revenue']:,.0f} ({row['Share']}%)", ln=True)
            pdf.ln(8)

            # Recommendations
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Recommended Actions", ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, "1. Review safety stock for top 5 revenue-driving products.", ln=True)
            pdf.cell(0, 7, "2. Use Scenario Simulator to test pricing strategies.", ln=True)
            pdf.cell(0, 7, "3. Evaluate low-volume product segments for potential discontinuation.", ln=True)

            pdf_bytes = pdf.output()

            st.download_button("⬇️ Download PDF", data=bytes(pdf_bytes),
                               file_name=f"SmartStock_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                               mime='application/pdf', use_container_width=True)
