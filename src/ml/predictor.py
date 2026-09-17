import pandas as pd
import numpy as np
from src.models.artifact_loader import load_forecasting_artifacts
from src.ml.encoder import apply_encoders
from src.ml.feature_engineering import prepare_features, get_expected_feature_order

class SmartStockPredictor:
    def __init__(self):
        self.model, self.encoders, self.metadata = load_forecasting_artifacts()
        self.expected_features = get_expected_feature_order()

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates predictions for the provided DataFrame.
        """
        # 1. Feature Engineering
        df_features = prepare_features(df)
        
        # 2. Check and map unknown categories
        for col, le in self.encoders.items():
            if col in df_features.columns:
                known_classes = set(le.classes_)
                user_classes = set(df_features[col].dropna().unique())
                unknowns = user_classes - known_classes
                if unknowns:
                    # Gracefully map unknown categories to the first known class to prevent inference crashes
                    fallback_class = le.classes_[0]
                    df_features[col] = df_features[col].apply(lambda x: fallback_class if x in unknowns else x)
        
        # 3. Apply Encoders
        df_encoded = apply_encoders(df_features, self.encoders)
        
        # 4. Ensure all expected features are present
        missing_cols = set(self.expected_features) - set(df_encoded.columns)
        if missing_cols:
            raise ValueError(f"Missing required features after engineering: {missing_cols}")
            
        for col in self.expected_features:
            if col not in self.encoders.keys() and df_encoded[col].dtype == 'object':
                try:
                    df_encoded[col] = df_encoded[col].astype(float)
                except ValueError:
                    df_encoded[col] = df_encoded[col].astype('category').cat.codes

        # 5. Select and order features exactly as the model expects
        X = df_encoded[self.expected_features]
        
        # 6. Predict
        predictions = self.model.predict(X)
        
        # 7. Clip negative predictions to 0
        predictions = np.clip(predictions, a_min=0, a_max=None)
        
        # 8. Return results attached to original dataframe identifiers
        result_df = df[['date', 'outlet', 'product_identifier']].copy()
        result_df['predicted_sales'] = predictions
        
        return result_df

def generate_forecast(df: pd.DataFrame) -> pd.DataFrame:
    predictor = SmartStockPredictor()
    return predictor.predict(df)
