import streamlit as st
import pandas as pd

from src.ui.theme import apply_theme
from src.ui.sidebar import render_sidebar
from src.ui.components import page_header, insight_card, section_header, empty_state, kpi_card
from src.state.data_context import DataContext

st.set_page_config(page_title="Data Explorer — SmartStock", layout="wide", page_icon="🗄️")
apply_theme()
render_sidebar()
DataContext.init()

page_header("Data Explorer", "Upload, validate, and onboard your retail dataset into the SmartStock intelligence platform.")

mode = DataContext.get_mode()
df = DataContext.get_dataset()

# ──────────────────────────────────────────────
# CURRENT DATASET STATUS
# ──────────────────────────────────────────────
section_header("Active Dataset", "Currently loaded dataset statistics")

c1, c2, c3, c4 = st.columns(4)
with c1:
    mode_label = "Demo Dataset" if mode == DataContext.MODE_DEMO else "User Dataset"
    kpi_card("Mode", mode_label, "🟢 Active")
with c2:
    kpi_card("Rows", f"{len(df):,}" if not df.empty else "0", "")
with c3:
    kpi_card("Products", f"{df['product_identifier'].nunique():,}" if not df.empty and 'product_identifier' in df.columns else "0", "")
with c4:
    kpi_card("Columns", f"{len(df.columns)}" if not df.empty else "0", "")

if mode == DataContext.MODE_USER:
    if st.button("🔄 Restore Demo Dataset"):
        DataContext.restore_demo()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA UPLOAD
# ──────────────────────────────────────────────
section_header("Upload Your Data", "Upload a CSV file matching the SmartStock schema")

with st.expander("📋 Required Schema", expanded=False):
    st.markdown("""
    | Column | Type | Description |
    |--------|------|-------------|
    | `date` | Date | Transaction date (YYYY-MM-DD) |
    | `product_identifier` | String | Unique product ID |
    | `outlet` | String | Store / location ID |
    | `sales` | Integer | Units sold |
    | `sell_price` | Float | Price per unit |
    | `category_of_product` | String | Product category |
    | `state` | String | Geographic state |
    | `department_identifier` | String | Department ID |
    """)

uploaded = st.file_uploader("Upload Retail CSV", type=["csv"])

if uploaded is not None:
    section_header("Validation Results", "Schema compatibility check")
    with st.spinner("Validating..."):
        try:
            new_df = pd.read_csv(uploaded)
            required = ['date', 'product_identifier', 'sales', 'outlet']
            missing = [c for c in required if c not in new_df.columns]

            if missing:
                insight_card("❌ Validation Failed", f"Missing required columns: **{', '.join(missing)}**",
                             "Fix the CSV and re-upload. Active dataset was not modified.", "danger")
            else:
                new_df['date'] = pd.to_datetime(new_df['date'])
                nulls = new_df[required].isnull().sum()
                total_nulls = nulls.sum()

                if total_nulls > 0:
                    insight_card("⚠️ Data Quality Warning",
                                 f"Found {total_nulls} null values in required columns.",
                                 "Rows with missing values may produce degraded predictions.", "warning")
                else:
                    insight_card("✅ Validation Passed", "All required columns present with no missing values.",
                                 "You can safely apply this dataset.", "success")

                st.dataframe(new_df.head(10), use_container_width=True, hide_index=True)

                if st.button("🚀 Apply Dataset & Enter User Mode", type="primary"):
                    DataContext.set_user_dataset(new_df)
                    st.success("✅ Dataset applied! All modules now use your data.")
                    st.rerun()

        except Exception as e:
            insight_card("❌ Parse Error", f"Failed to read CSV: {str(e)}", "Ensure it's a valid CSV file.", "danger")

# ──────────────────────────────────────────────
# DATA PREVIEW
# ──────────────────────────────────────────────
if not df.empty:
    section_header("Data Preview", "First 20 rows of the active dataset")
    st.dataframe(df.head(20), use_container_width=True, hide_index=True)
