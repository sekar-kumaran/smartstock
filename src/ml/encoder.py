import pandas as pd
from typing import Dict, Any

def apply_encoders(df: pd.DataFrame, encoders: Dict[str, Any]) -> pd.DataFrame:
    """
    Applies the pre-trained label encoders to the categorical columns.
    Handles unseen categories by filling them with a default value (-1 or a specific class).
    """
    df_encoded = df.copy()
    
    for col, le in encoders.items():
        if col in df_encoded.columns:
            # Identify unseen categories
            known_classes = set(le.classes_)
            # Map unseen to a default value (-1 or the first class)
            # A common safe approach is to use a special 'unknown' mapping or map to -1 if LightGBM supports it.
            # LightGBM handles negative categorical values as unseen/NaN nicely.
            
            # Temporary mapping dictionary
            mapping = {val: idx for idx, val in enumerate(le.classes_)}
            
            # Map known values, fill unknown with -1
            df_encoded[col] = df_encoded[col].map(mapping).fillna(-1).astype(int)
            
    return df_encoded
