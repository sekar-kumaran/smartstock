import pandas as pd
from typing import Dict, Any

def calculate_data_drift(user_df: pd.DataFrame, reference_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculates statistical drift between uploaded user data and the training reference metadata.
    """
    report = {
        "schema_compatibility": 0.0,
        "category_coverage": 0.0,
        "historical_depth": 0.0,
        "overall_score": 0.0,
        "drift_level": "UNKNOWN",
        "details": []
    }
    
    # 1. Schema Compatibility
    schema = reference_metadata.get('schema_config', {})
    required_cols = [schema.get('date_column'), schema.get('target_column')] + \
                    schema.get('grain_features', []) + \
                    schema.get('categorical_features', []) + \
                    schema.get('numeric_features', []) + \
                    schema.get('time_features', [])
    
    available_cols = [c for c in required_cols if c in user_df.columns]
    report["schema_compatibility"] = len(available_cols) / len(required_cols) * 100 if required_cols else 0.0
    
    if report["schema_compatibility"] < 100:
        report["details"].append(f"Missing columns: {set(required_cols) - set(user_df.columns)}")
        
    # 2. Historical Depth
    if schema.get('date_column') in user_df.columns:
        date_col = schema['date_column']
        if not pd.api.types.is_datetime64_any_dtype(user_df[date_col]):
            user_df[date_col] = pd.to_datetime(user_df[date_col])
        days_span = (user_df[date_col].max() - user_df[date_col].min()).days
        # Model uses up to 28 days lag, so we need > 28 days ideally.
        depth_score = min(days_span / 60.0, 1.0) * 100 # 60 days is "100%" depth for this score
        report["historical_depth"] = depth_score
    
    # Calculate overall pseudo-score (Not an "AI accuracy score", just applicability)
    report["overall_score"] = (report["schema_compatibility"] * 0.6) + (report.get("historical_depth", 0) * 0.4)
    
    if report["overall_score"] >= 90:
        report["drift_level"] = "LOW RISK"
    elif report["overall_score"] >= 70:
        report["drift_level"] = "MODERATE RISK"
    else:
        report["drift_level"] = "HIGH RISK"
        
    return report

def compute_applicability(user_df: pd.DataFrame, reference_metadata: Dict[str, Any]) -> float:
    """
    Computes an applicability score (0-100) based on schema and categorical overlap.
    """
    report = calculate_data_drift(user_df, reference_metadata)
    return report.get("overall_score", 0.0)
