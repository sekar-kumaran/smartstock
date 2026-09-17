import os
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import joblib

os.makedirs("models/clustering", exist_ok=True)
os.makedirs("models/anomaly", exist_ok=True)
os.makedirs("models/forecasting", exist_ok=True)

# Generate synthetic reference features
np.random.seed(42)
n_products = 50
features = ['mean_sales', 'sales_std', 'coefficient_of_variation', 'zero_sales_ratio']
X = np.random.rand(n_products, 4) * [100, 20, 0.5, 0.1]
product_ids = [f"PROD_{i:03d}" for i in range(n_products)]
df = pd.DataFrame(X, index=product_ids, columns=features)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)
joblib.dump(scaler, "models/clustering/product_scaler.joblib")

kmeans = KMeans(n_clusters=4, random_state=42, n_init="auto")
labels = kmeans.fit_predict(X_scaled)
joblib.dump(kmeans, "models/clustering/product_kmeans.joblib")

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
joblib.dump(pca, "models/clustering/product_pca.joblib")

profiles = {}
for i in range(4):
    profiles[str(i)] = {
        "name": f"Cluster {i}",
        "product_count": int(np.sum(labels == i)),
        "mean_sales": float(df.iloc[labels == i]['mean_sales'].mean()),
        "sales_std": float(df.iloc[labels == i]['sales_std'].mean()),
        "coefficient_of_variation": float(df.iloc[labels == i]['coefficient_of_variation'].mean())
    }

with open("models/clustering/cluster_profiles.json", "w") as f:
    json.dump(profiles, f)

with open("models/clustering/clustering_features.json", "w") as f:
    json.dump({"features": features}, f)

joblib.dump(X_scaled, "models/clustering/product_behavior_matrix.joblib")
with open("models/clustering/product_index.json", "w") as f:
    json.dump({"products": product_ids}, f)

# Anomaly
X_anomaly = np.random.rand(200, 3) * [50, 50, 10]
iso = IsolationForest(contamination=0.05, random_state=42)
iso.fit(X_anomaly)
joblib.dump(iso, "models/anomaly/isolation_forest.joblib")

with open("models/anomaly/anomaly_features.json", "w") as f:
    json.dump({"features": ["sales", "rolling_mean_14", "rolling_std_14"]}, f)

# Copy forecasting from original dir
import shutil
shutil.copy("VIF_SmartStock_Model_Artifacts/models/champion_lightgbm.pkl", "models/forecasting/")
shutil.copy("VIF_SmartStock_Model_Artifacts/models/label_encoders.pkl", "models/forecasting/")
shutil.copy("VIF_SmartStock_Model_Artifacts/metadata.json", "models/forecasting/")

# Registry
registry = {
  "forecasting": {
    "algorithm": "LightGBM",
    "artifact": "forecasting/champion_lightgbm.pkl"
  },
  "clustering": {
    "algorithm": "KMeans",
    "artifact": "clustering/product_kmeans.joblib",
    "scaler": "clustering/product_scaler.joblib",
    "pca": "clustering/product_pca.joblib"
  },
  "anomaly_detection": {
    "algorithm": "Isolation Forest",
    "artifact": "anomaly/isolation_forest.joblib"
  }
}
with open("models/model_registry.json", "w") as f:
    json.dump(registry, f, indent=4)

print("Artifacts generated.")
