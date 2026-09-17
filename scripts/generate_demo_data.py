import os
import pandas as pd
import numpy as np

def generate_demo_dataset():
    np.random.seed(42)
    dates = pd.date_range('2025-01-01', periods=180)
    products = [f"PROD_{i:03d}" for i in range(20)]
    outlets = ["OUTLET_1", "OUTLET_2"]
    categories = ["Electronics", "Home", "Clothing"]
    
    records = []
    for date in dates:
        for outlet in outlets:
            for p_idx, prod in enumerate(products):
                cat = categories[p_idx % len(categories)]
                base_sales = 10 + (p_idx % 5) * 5
                
                # Seasonality + Noise
                seasonality = np.sin((date.dayofyear / 365) * 2 * np.pi) * 5
                noise = np.random.normal(0, 3)
                
                sales = max(0, int(base_sales + seasonality + noise))
                
                # Spikes/drops for anomalies
                if np.random.rand() > 0.98:
                    sales += np.random.randint(20, 50)
                    
                records.append({
                    "date": date,
                    "outlet": outlet,
                    "product_identifier": prod,
                    "category_of_product": cat,
                    "state": "State_A" if outlet == "OUTLET_1" else "State_B",
                    "department_identifier": "DEPT_01",
                    "sell_price": 50.0 + (p_idx * 5.5),
                    "sales": sales
                })
                
    df = pd.DataFrame(records)
    
    os.makedirs("data/demo", exist_ok=True)
    df.to_csv("data/demo/smartstock_demo.csv", index=False)
    print("Demo dataset generated at data/demo/smartstock_demo.csv")

if __name__ == "__main__":
    generate_demo_dataset()
