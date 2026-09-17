import pandas as pd
from datetime import timedelta
import streamlit as st
from src.ml.predictor import SmartStockPredictor

def generate_multi_day_forecast(
    historical_df: pd.DataFrame, 
    product_id: str, 
    outlet_id: str, 
    start_date: pd.Timestamp, 
    horizon_days: int
) -> pd.DataFrame:
    """
    Generates a forecast for a specific product and outlet over a given horizon.
    Uses recursive forecasting if the horizon requires predicted values for lags.
    """
    predictor = SmartStockPredictor()
    
    # Filter history for the specific product and outlet
    df_context = historical_df[
        (historical_df['product_identifier'] == product_id) & 
        (historical_df['outlet'] == outlet_id)
    ].copy()
    
    df_context['date'] = pd.to_datetime(df_context['date'])
    df_context = df_context.sort_values('date').reset_index(drop=True)
    
    if df_context.empty:
        raise ValueError("No historical data found for this product and outlet.")
        
    # Get the static categorical info from the last known record
    static_info = df_context.iloc[-1][['category_of_product', 'state', 'department_identifier', 'sell_price']].to_dict()
    
    predictions = []
    current_context = df_context.copy()
    
    # We will predict one day at a time
    for i in range(horizon_days):
        target_date = start_date + timedelta(days=i)
        
        # Create a new row for the target date
        new_row = {
            'date': target_date,
            'outlet': outlet_id,
            'product_identifier': product_id,
            'category_of_product': static_info['category_of_product'],
            'state': static_info['state'],
            'department_identifier': static_info['department_identifier'],
            'sell_price': static_info['sell_price'],
            'week_id': target_date.isocalendar()[1],
            'sales': 0.0 # Dummy value, will be overwritten by prediction
        }
        
        # Append to context
        current_context = pd.concat([current_context, pd.DataFrame([new_row])], ignore_index=True)
        
        # Predict the latest row
        try:
            pred_df = predictor.predict(current_context)
            latest_pred = pred_df.iloc[-1]['predicted_sales']
        except Exception as e:
            st.error(f"Prediction failed for date {target_date}: {e}")
            break
            
        # Store prediction
        predictions.append({
            'date': target_date,
            'product_identifier': product_id,
            'outlet': outlet_id,
            'predicted_sales': latest_pred
        })
        
        # Update the context with the predicted sales so future lags can use it
        current_context.at[current_context.index[-1], 'sales'] = latest_pred
        
    return pd.DataFrame(predictions)
