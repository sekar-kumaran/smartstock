import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ML Artifacts
ARTIFACTS_DIR = BASE_DIR / "VIF_SmartStock_Model_Artifacts"
MODEL_PATH = ARTIFACTS_DIR / "models" / "champion_lightgbm.pkl"
ENCODERS_PATH = ARTIFACTS_DIR / "models" / "label_encoders.pkl"
METADATA_PATH = ARTIFACTS_DIR / "metadata.json"

# Data Storage
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
FORECASTS_DIR = OUTPUTS_DIR / "forecasts"
REPORTS_DIR = OUTPUTS_DIR / "reports"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
FORECASTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# App Settings
APP_NAME = "VIF SmartStock"
MAX_UPLOAD_SIZE_MB = 200
