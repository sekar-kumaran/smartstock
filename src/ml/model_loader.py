import joblib
import json
import streamlit as st
from pathlib import Path
from src.config.settings import MODEL_PATH, ENCODERS_PATH, METADATA_PATH

@st.cache_resource(show_spinner="Loading ML Model...")
def load_model():
    """Loads the pre-trained LightGBM model."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    return joblib.load(MODEL_PATH)

@st.cache_resource(show_spinner="Loading Encoders...")
def load_encoders():
    """Loads the label encoders dictionary."""
    if not ENCODERS_PATH.exists():
        raise FileNotFoundError(f"Encoders file not found at {ENCODERS_PATH}")
    return joblib.load(ENCODERS_PATH)

@st.cache_data(show_spinner="Loading Metadata...")
def load_metadata():
    """Loads the model metadata."""
    if not METADATA_PATH.exists():
        raise FileNotFoundError(f"Metadata file not found at {METADATA_PATH}")
    with open(METADATA_PATH, 'r') as f:
        return json.load(f)

def check_model_health():
    """Checks if all ML artifacts are present and can be loaded."""
    health = {
        "model_exists": MODEL_PATH.exists(),
        "encoders_exists": ENCODERS_PATH.exists(),
        "metadata_exists": METADATA_PATH.exists(),
        "status": "Unknown",
        "error": None
    }
    
    if all([health["model_exists"], health["encoders_exists"], health["metadata_exists"]]):
        try:
            # Attempt to load without Streamlit caching if calling outside Streamlit context
            joblib.load(MODEL_PATH)
            joblib.load(ENCODERS_PATH)
            with open(METADATA_PATH, 'r') as f:
                json.load(f)
            health["status"] = "Healthy"
        except Exception as e:
            health["status"] = "Error"
            health["error"] = str(e)
    else:
        health["status"] = "Error"
        health["error"] = "Missing one or more required artifacts."
        
    return health
