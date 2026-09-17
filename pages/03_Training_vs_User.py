import streamlit as st
import pandas as pd

from src.ui.theme import apply_theme
from src.ui.sidebar import render_sidebar
from src.ui.components import page_header, insight_card, section_header, empty_state, kpi_card
from src.state.data_context import DataContext
from src.models.artifact_loader import load_forecasting_artifacts

st.set_page_config(page_title="Data Comparison — SmartStock", layout="wide", page_icon="⚖️")
apply_theme()
render_sidebar()
DataContext.init()

page_header("Data Comparison Workspace", "Measure how well the active dataset aligns with the training reference data.")

try:
    model, encoders, metadata = load_forecasting_artifacts()
except Exception:
    empty_state("Artifacts Missing", "Cannot load training reference metadata.", "⚠️")
    st.stop()

df = DataContext.get_dataset()
mode = DataContext.get_mode()

if df.empty:
    empty_state("No Dataset Active", "Upload a dataset to compare against training reference.", "⚖️")
    st.stop()

mode_label = "Demo" if mode == DataContext.MODE_DEMO else "User"
st.info(f"💡 Comparing **{mode_label} Dataset** ({len(df):,} rows) against the offline **Training Reference**.")

# ──────────────────────────────────────────────
# SCHEMA COMPATIBILITY
# ──────────────────────────────────────────────
section_header("1. Schema Compatibility", "Does the active dataset contain all required columns?")

schema = metadata.get('schema_config', {})
required_cols = list(set(
    [schema.get('date_column', 'date'), schema.get('target_column', 'sales')] +
    schema.get('grain_features', []) +
    schema.get('categorical_features', []) +
    schema.get('numeric_features', []) +
    schema.get('time_features', [])
))
required_cols = [c for c in required_cols if c]  # filter None
present = [c for c in required_cols if c in df.columns]
missing = [c for c in required_cols if c not in df.columns]
schema_score = len(present) / max(len(required_cols), 1) * 100

c1, c2, c3 = st.columns(3)
with c1: kpi_card("Required Columns", f"{len(required_cols)}", "")
with c2: kpi_card("Present", f"{len(present)}", "")
with c3: kpi_card("Schema Score", f"{schema_score:.0f}%", "", "green" if schema_score >= 80 else "red")

if missing:
    insight_card("Missing Columns", f"The following columns are missing: {', '.join(missing)}",
                 "Predictions for features dependent on these columns will use fallback values.", "warning")

# ──────────────────────────────────────────────
# CATEGORICAL COVERAGE
# ──────────────────────────────────────────────
section_header("2. Categorical Coverage", "Overlap between active and training categorical values")

ref_cats = metadata.get('categorical_coverage', {})
cat_cols = ['outlet', 'product_identifier', 'category_of_product', 'state', 'department_identifier']
overlap_data = []

for col in cat_cols:
    if col in df.columns and col in ref_cats:
        user_vals = set(df[col].dropna().unique())
        ref_vals = set(ref_cats[col])
        shared = user_vals & ref_vals
        new_vals = user_vals - ref_vals

        status = "🟢 Stable" if len(new_vals) == 0 else "🟡 Minor Drift" if len(new_vals) < len(user_vals) * 0.1 else "🔴 Significant Drift"
        overlap_data.append({
            'Feature': col, 'Active Uniques': len(user_vals), 'Reference Uniques': len(ref_vals),
            'Shared': len(shared), 'New (Unknown)': len(new_vals), 'Status': status
        })

if overlap_data:
    st.dataframe(pd.DataFrame(overlap_data), use_container_width=True, hide_index=True)

# ──────────────────────────────────────────────
# NUMERIC DRIFT
# ──────────────────────────────────────────────
section_header("3. Numeric Distribution", "Statistical comparison of key numeric features")

ref_numeric = metadata.get('numeric_stats', {})
if 'sales' in df.columns and 'sales' in ref_numeric:
    c1, c2, c3 = st.columns(3)
    user_mean = df['sales'].mean()
    ref_mean = ref_numeric['sales'].get('mean', user_mean)
    drift_pct = abs(user_mean - ref_mean) / max(ref_mean, 1) * 100

    with c1: kpi_card("Active Mean Sales", f"{user_mean:.2f}", "")
    with c2: kpi_card("Reference Mean Sales", f"{ref_mean:.2f}", "")
    with c3: kpi_card("Drift", f"{drift_pct:.1f}%", "", "red" if drift_pct > 20 else "green")

# ──────────────────────────────────────────────
# OVERALL APPLICABILITY
# ──────────────────────────────────────────────
section_header("4. Overall Applicability Score", "Composite assessment of data quality for inference")

# Simple composite score
cat_score = 100 if not overlap_data else sum(1 for o in overlap_data if '🟢' in o['Status']) / len(overlap_data) * 100
overall = schema_score * 0.5 + cat_score * 0.3 + (100 - min(drift_pct, 100) if 'drift_pct' in dir() else 80) * 0.2

if overall >= 80:
    insight_card("High Applicability", f"Score: {overall:.0f}/100. This dataset is highly compatible with the trained model.",
                 "Inference confidence is high.", "success")
elif overall >= 50:
    insight_card("Moderate Applicability", f"Score: {overall:.0f}/100. Some drift detected.",
                 "Predictions for unseen categories may be less reliable.", "warning")
else:
    insight_card("Low Applicability", f"Score: {overall:.0f}/100. Significant differences from training data.",
                 "Consider retraining the offline model with this dataset's distribution.", "danger")
