import sys
from pathlib import Path

# Add project root to path so we can import src
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.ml.predictor import SmartStockPredictor

def test_pipeline():
    print("1. Initializing Predictor...")
    predictor = SmartStockPredictor()
    print("   Predictor initialized successfully.")
    
    print("\n2. Generating Synthetic Validation Data...")
    # Create 35 days of history to ensure lag_28 and rolling_mean_28 can be calculated
    dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(40)]
    
    data = []
    # Test for one product at one outlet
    for d in dates:
        data.append({
            'date': d,
            'outlet': 'OUTLET_001',
            'product_identifier': 'PROD_100',
            'category_of_product': 'Grocery',
            'state': 'Maharashtra',
            'department_identifier': 'Food',
            'sell_price': 15.5,
            'week_id': d.isocalendar()[1],
            'sales': np.random.randint(5, 20)  # Random historical sales
        })
        
    df = pd.DataFrame(data)
    print(f"   Generated {len(df)} rows.")
    
    print("\n3. Running Inference...")
    try:
        results = predictor.predict(df)
        print("   Inference completed successfully!")
        
        print("\n4. Checking Results Shape & Format...")
        print(results.tail())
        
        # Check if predictions are floats
        assert pd.api.types.is_numeric_dtype(results['predicted_sales']), "Predictions are not numeric"
        
        # We expect some NaNs in early predictions due to the 28 day lag
        # But the last row should have a valid prediction
        last_pred = results.iloc[-1]['predicted_sales']
        if pd.isna(last_pred):
            print("   WARNING: Last prediction is NaN. Check feature engineering windows.")
        else:
            print(f"   Latest Prediction Value: {last_pred:.2f}")
            
        print("\n=> Pipeline Validation Passed.")
    except Exception as e:
        print(f"\n=> Pipeline Validation FAILED: {e}")
        raise e

if __name__ == "__main__":
    test_pipeline()
