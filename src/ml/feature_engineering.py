import pandas as pd
import numpy as np

def create_calendar_features(df: pd.DataFrame, date_col: str = 'date') -> pd.DataFrame:
    """Extracts calendar features from the date column."""
    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
        df[date_col] = pd.to_datetime(df[date_col])
        
    df['year'] = df[date_col].dt.year
    df['month'] = df[date_col].dt.month
    df['day'] = df[date_col].dt.day
    df['dayofweek'] = df[date_col].dt.dayofweek
    df['dayofyear'] = df[date_col].dt.dayofyear
    return df

def create_historical_features(df: pd.DataFrame, target_col: str = 'sales',
                              group_cols: list = None, date_col: str = 'date') -> pd.DataFrame:
    """
    Computes lag and rolling features.
    Assumes df is already sorted by date.
    """
    if group_cols is None:
        group_cols = ['outlet', 'product_identifier']
        
    df = df.copy()
    
    # Ensure sorted by date within groups
    df = df.sort_values(by=group_cols + [date_col])
    
    grouped = df.groupby(group_cols)[target_col]
    
    # Lag Features
    df['lag_7'] = grouped.shift(7)
    df['lag_14'] = grouped.shift(14)
    df['lag_28'] = grouped.shift(28)
    
    # Rolling Features (applied to lag_7 to avoid leakage)
    # The rolling mean of the last 7 days available starting from T-7 
    # i.e. rolling mean of window 7 on the 7-day shifted series.
    # We can compute it by shifting by 7 and then applying rolling(7).mean()
    df['rolling_mean_7'] = grouped.shift(7).rolling(window=7, min_periods=1).mean()
    df['rolling_mean_28'] = grouped.shift(7).rolling(window=28, min_periods=1).mean()
    
    # Restore original index order if needed, but usually we just keep it sorted
    return df

def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Executes the full feature engineering pipeline.
    Expects raw data with columns: 
    date, outlet, product_identifier, category_of_product, state, department_identifier, sell_price, week_id, sales
    """
    df = create_calendar_features(df)
    df = create_historical_features(df)
    return df

def get_expected_feature_order() -> list:
    """Returns the exact feature order expected by the model."""
    return [
        'product_identifier', 'department_identifier', 'category_of_product', 
        'outlet', 'state', 'week_id', 'sell_price', 'year', 'month', 'day', 
        'dayofweek', 'dayofyear', 'lag_7', 'lag_14', 'lag_28', 
        'rolling_mean_7', 'rolling_mean_28'
    ]
