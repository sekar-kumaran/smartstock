import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.metrics import pairwise_distances
from src.models.artifact_loader import load_clustering_artifacts
import streamlit as st

def extract_behavioral_features(df: pd.DataFrame, expected_features: list) -> pd.DataFrame:
    """
    Extracts structured behavioral features for products.
    """
    behavior = df.groupby('product_identifier').agg(
        mean_sales=('sales', 'mean'),
        median_sales=('sales', 'median'),
        sales_std=('sales', 'std'),
        zero_sales_ratio=('sales', lambda x: (x == 0).mean())
    ).reset_index()
    
    behavior['sales_std'] = behavior['sales_std'].fillna(0)
    behavior['coefficient_of_variation'] = np.where(
        behavior['mean_sales'] == 0, 0, behavior['sales_std'] / behavior['mean_sales']
    )
    
    behavior.set_index('product_identifier', inplace=True)
    
    # Ensure expected features exist, fill with 0 if missing (though rare)
    for col in expected_features:
        if col not in behavior.columns:
            behavior[col] = 0.0
            
    return behavior[expected_features]

def perform_clustering_inference(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Performs inference using the OFFLINE TRAINED KMeans and PCA artifacts.
    NEVER fits models at runtime.
    """
    kmeans, scaler, pca, profiles, features, behavior_matrix, index = load_clustering_artifacts()
    
    expected_features = features.get('features', [])
    behavior_df = extract_behavioral_features(df, expected_features)
    
    if behavior_df.empty:
        return pd.DataFrame(), pd.DataFrame()
        
    # Transform using pre-trained scaler (NO FIT)
    scaled_features = scaler.transform(behavior_df)
    
    # Predict clusters using pre-trained KMeans (NO FIT)
    labels = kmeans.predict(scaled_features)
    behavior_df['Cluster'] = labels
    
    # Map friendly names from profiles
    behavior_df['Cluster_Name'] = behavior_df['Cluster'].apply(lambda x: profiles.get(str(x), {}).get('name', f'Cluster {x}'))
    
    # Transform using pre-trained PCA for 2D visualization (NO FIT)
    try:
        pca_features = pca.transform(scaled_features)
        behavior_df['PCA_1'] = pca_features[:, 0]
        behavior_df['PCA_2'] = pca_features[:, 1]
    except Exception as e:
        st.warning(f"PCA projection failed (likely too few components): {e}")
        behavior_df['PCA_1'] = 0
        behavior_df['PCA_2'] = 0
    
    return behavior_df, scaled_features

def find_similar_products(product_id: str, behavior_df: pd.DataFrame, scaled_features: np.ndarray, top_n: int = 5) -> pd.DataFrame:
    """
    Uses Cosine Similarity on behavioral vectors to find similar products against the REFERENCE SET.
    """
    kmeans, scaler, pca, profiles, features, behavior_matrix, index = load_clustering_artifacts()
    reference_products = index.get('products', [])
    
    if product_id not in behavior_df.index:
        return pd.DataFrame()
        
    # Get user product vector
    idx = behavior_df.index.get_loc(product_id)
    target_vector = scaled_features[idx].reshape(1, -1)
    
    # Compare against offline reference matrix
    distances = pairwise_distances(target_vector, behavior_matrix, metric='cosine')[0]
    similarities = 1 - distances
    
    sim_df = pd.DataFrame({
        'Product': reference_products,
        'Similarity': similarities
    })
    
    # Filter out self and sort
    sim_df = sim_df[sim_df['Product'] != product_id].sort_values(by='Similarity', ascending=False).head(top_n)
    sim_df['Similarity'] = sim_df['Similarity'].apply(lambda x: f"{x * 100:.1f}%")
    
    return sim_df
