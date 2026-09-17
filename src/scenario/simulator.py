import pandas as pd
import numpy as np
from src.ml.predictor import generate_forecast

def run_scenario(df: pd.DataFrame, 
                 price_multiplier: float = 1.0, 
                 demand_multiplier: float = 1.0) -> pd.DataFrame:
    """
    Runs a business scenario by altering inference inputs and invoking 
    the baseline forecasting model (artifact). No retraining occurs.
    """
    scenario_df = df.copy()
    
    # Apply business logic modifications to the features used for inference
    if 'sell_price' in scenario_df.columns:
        scenario_df['sell_price'] = scenario_df['sell_price'] * price_multiplier
        
    # We alter historical sales to simulate what the lag features will see
    if 'sales' in scenario_df.columns:
        scenario_df['sales'] = scenario_df['sales'] * demand_multiplier

    # Run the standard artifact-driven forecast on the altered data
    forecast = generate_forecast(scenario_df)
    return forecast
