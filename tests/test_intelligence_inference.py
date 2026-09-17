import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from src.intelligence.clustering import perform_clustering_inference, find_similar_products
from src.intelligence.anomaly import detect_anomalies_inference

@pytest.fixture
def mock_user_data():
    return pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=100),
        'product_identifier': ['PROD_001'] * 50 + ['PROD_002'] * 50,
        'outlet': ['OUTLET_1'] * 100,
        'sales': np.random.rand(100) * 100
    })

@patch('sklearn.cluster.KMeans.fit')
@patch('sklearn.cluster.KMeans.fit_predict')
@patch('sklearn.preprocessing.StandardScaler.fit')
@patch('sklearn.preprocessing.StandardScaler.fit_transform')
@patch('sklearn.decomposition.PCA.fit')
@patch('sklearn.decomposition.PCA.fit_transform')
@patch('sklearn.ensemble.IsolationForest.fit')
@patch('sklearn.ensemble.IsolationForest.fit_predict')
def test_no_runtime_fitting(
    mock_iso_fp, mock_iso_f, 
    mock_pca_ft, mock_pca_f, 
    mock_scaler_ft, mock_scaler_f, 
    mock_kmeans_fp, mock_kmeans_f,
    mock_user_data
):
    """
    CRITICAL TEST: Ensures that normal application inference NEVER calls .fit() 
    on any intelligence model, guaranteeing that the application uses pre-trained offline artifacts.
    """
    
    # 1. Clustering Inference
    behavior_df, scaled = perform_clustering_inference(mock_user_data)
    assert not behavior_df.empty
    
    # 2. Similarity Inference
    sim_df = find_similar_products('PROD_001', behavior_df, scaled)
    # Could be empty depending on mocked data sizes, but should not crash or fit
    
    # 3. Anomaly Inference
    anomaly_df = detect_anomalies_inference(mock_user_data)
    assert not anomaly_df.empty
    
    # ASSERTIONS: None of the fitting methods should have been called!
    mock_kmeans_f.assert_not_called()
    mock_kmeans_fp.assert_not_called()
    mock_scaler_f.assert_not_called()
    mock_scaler_ft.assert_not_called()
    mock_pca_f.assert_not_called()
    mock_pca_ft.assert_not_called()
    mock_iso_f.assert_not_called()
    mock_iso_fp.assert_not_called()

def test_missing_features_handled_gracefully():
    # Provide missing columns
    df = pd.DataFrame({
        'product_identifier': ['PROD_001'],
        'outlet': ['OUTLET_1']
    })
    
    # Should not crash, should return empty or base df
    anomaly_df = detect_anomalies_inference(df)
    assert anomaly_df.empty or 'Anomaly' not in anomaly_df.columns or anomaly_df['Anomaly'].iloc[0] == 'NORMAL'
