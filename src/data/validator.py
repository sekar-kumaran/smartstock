import pandas as pd
import streamlit as st

def validate_dataset_schema(df: pd.DataFrame, expected_schema: dict) -> dict:
    """
    Validates that the uploaded DataFrame meets the required schema.
    Returns a dictionary with status and missing columns.
    """
    required_cols = (
        [expected_schema['date_column'], expected_schema['target_column']] +
        expected_schema['grain_features'] +
        expected_schema['categorical_features'] +
        expected_schema['numeric_features'] +
        expected_schema['time_features']
    )
    
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        return {"valid": False, "missing_columns": missing}
        
    # Optional: We could check data types here, but for now we trust pandas inference
    # and handle conversions during feature engineering.
    
    return {"valid": True, "missing_columns": []}

def get_data_quality_report(df: pd.DataFrame) -> dict:
    """Generates a high-level data quality report."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicates": df.duplicated().sum(),
        "memory_usage_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
    }
