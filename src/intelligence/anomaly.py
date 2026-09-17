import pandas as pd
import numpy as np
from src.models.artifact_loader import load_anomaly_artifacts

def detect_anomalies_inference(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects demand anomalies using the OFFLINE TRAINED Isolation Forest artifact.
    NEVER fits models at runtime.
    """
    iso, meta = load_anomaly_artifacts()
    expected_features = meta.get('features', [])
    
    if df.empty or 'sales' not in df.columns:
        return df
        
    df_result = df.copy()
    
    df_result['rolling_mean_14'] = df_result.groupby(['outlet', 'product_identifier'])['sales'].transform(lambda x: x.rolling(14, min_periods=1).mean())
    df_result['rolling_std_14'] = df_result.groupby(['outlet', 'product_identifier'])['sales'].transform(lambda x: x.rolling(14, min_periods=1).std().fillna(0))
    
    for feat in expected_features:
        if feat not in df_result.columns:
            df_result[feat] = 0.0
            
    valid_idx = df_result[expected_features].dropna().index
    
    if len(valid_idx) == 0:
        df_result['Anomaly'] = 'NORMAL'
        df_result['Anomaly_Score'] = 0.0
        return df_result
        
    X = df_result.loc[valid_idx, expected_features]
    
    # -1 for anomaly, 1 for normal
    preds = iso.predict(X)
    scores = iso.decision_function(X)
    
    df_result.loc[valid_idx, 'Anomaly'] = np.where(preds == -1, 'ANOMALY', 'NORMAL')
    df_result.loc[valid_idx, 'Anomaly_Score'] = scores
    
    df_result['Anomaly'] = df_result['Anomaly'].fillna('NORMAL')
    df_result['Anomaly_Score'] = df_result['Anomaly_Score'].fillna(0.0)
    
    return df_result
