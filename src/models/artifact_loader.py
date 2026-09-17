import streamlit as st
import joblib
import json
import os
import pandas as pd

MODELS_DIR = "models"

@st.cache_resource
def load_forecasting_artifacts():
    lightgbm_path = os.path.join(MODELS_DIR, "forecasting", "champion_lightgbm.pkl")
    encoders_path = os.path.join(MODELS_DIR, "forecasting", "label_encoders.pkl")
    meta_path = os.path.join(MODELS_DIR, "forecasting", "metadata.json")
    
    if not (os.path.exists(lightgbm_path) and os.path.exists(encoders_path) and os.path.exists(meta_path)):
        st.error("Forecasting artifacts not found. Please ensure offline training is complete.")
        st.stop()
        
    model = joblib.load(lightgbm_path)
    encoders = joblib.load(encoders_path)
    with open(meta_path, 'r') as f:
        meta = json.load(f)
        
    return model, encoders, meta

@st.cache_resource
def load_clustering_artifacts():
    kmeans_path = os.path.join(MODELS_DIR, "clustering", "product_kmeans.joblib")
    scaler_path = os.path.join(MODELS_DIR, "clustering", "product_scaler.joblib")
    pca_path = os.path.join(MODELS_DIR, "clustering", "product_pca.joblib")
    profiles_path = os.path.join(MODELS_DIR, "clustering", "cluster_profiles.json")
    features_path = os.path.join(MODELS_DIR, "clustering", "clustering_features.json")
    matrix_path = os.path.join(MODELS_DIR, "clustering", "product_behavior_matrix.joblib")
    index_path = os.path.join(MODELS_DIR, "clustering", "product_index.json")
    
    if not all(os.path.exists(p) for p in [kmeans_path, scaler_path, pca_path, profiles_path, features_path, matrix_path, index_path]):
        st.error("Clustering artifacts not found. Please ensure offline training is complete in the Colab notebook.")
        st.stop()
        
    kmeans = joblib.load(kmeans_path)
    scaler = joblib.load(scaler_path)
    pca = joblib.load(pca_path)
    behavior_matrix = joblib.load(matrix_path)
    
    with open(profiles_path, 'r') as f:
        profiles = json.load(f)
    with open(features_path, 'r') as f:
        features = json.load(f)
    with open(index_path, 'r') as f:
        index = json.load(f)
        
    return kmeans, scaler, pca, profiles, features, behavior_matrix, index

@st.cache_resource
def load_anomaly_artifacts():
    iso_path = os.path.join(MODELS_DIR, "anomaly", "isolation_forest.joblib")
    features_path = os.path.join(MODELS_DIR, "anomaly", "anomaly_features.json")
    
    if not (os.path.exists(iso_path) and os.path.exists(features_path)):
        st.error("Anomaly artifacts not found. Please ensure offline training is complete.")
        st.stop()
        
    iso = joblib.load(iso_path)
    with open(features_path, 'r') as f:
        features = json.load(f)
        
    return iso, features
