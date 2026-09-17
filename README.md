# VIF SmartStock

**Indian Retail Demand Forecasting & Inventory Intelligence**

SmartStock is a production-style Machine Learning application built in Python using Streamlit. It leverages a pre-trained LightGBM model to predict retail demand and provides actionable analytics for inventory intelligence.

## Features

- **Demand Forecasting**: Predicts future sales using advanced lag and rolling window features over historical data.
- **Product & Store Analytics**: Explore historical sales trends and demand distribution across products and outlets.
- **Inventory Risk Engine**: Identifies potential stockouts and overstock scenarios (requires inventory data).
- **Data Validation**: Enforces strict schema checking based on the ML model's inference contract.
- **Model Transparency**: Displays champion metrics and expected schema directly from model metadata.

## Architecture

```text
Streamlit UI
    │
Data Layer (CSV)
    │
ML Service (LightGBM + Encoders + Feature Engine)
    │
Business Logic (Analytics + Risk)
```

This application uses a pure Streamlit architecture. State is managed via `st.session_state`, and heavy operations (model loading) are cached via `@st.cache_resource`.

## Installation & Setup

1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure the pre-trained ML artifacts are located at `VIF_SmartStock_Model_Artifacts/` in the project root.

## Running the Application

Start the Streamlit server:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

## Using the Application

1. **Upload Data**: Navigate to **Data Explorer** and upload a CSV containing historical sales data conforming to the required schema.
2. **Dashboard**: View high-level KPIs and recent forecasts.
3. **Forecast**: Navigate to **Demand Forecast**, select a product and outlet, and generate a multi-day demand prediction.
4. **Analytics**: Use **Product Analytics** and **Demand Analytics** to explore historical trends.
5. **Model Info**: Check the health and metrics of the loaded LightGBM model.
