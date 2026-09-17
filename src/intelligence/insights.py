import pandas as pd
from typing import List

def generate_insights(df: pd.DataFrame, perf_df: pd.DataFrame = None) -> List[str]:
    """
    Generates deterministic business insights based on the loaded dataset and model metadata.
    No LLM used. Purely data-driven.
    """
    insights = []
    
    if df is not None and not df.empty and 'sales' in df.columns:
        # Top Outlet
        outlet_sales = df.groupby('outlet')['sales'].sum()
        top_outlet = outlet_sales.idxmax()
        insights.append(f"**Outlet {top_outlet}** contributes the highest historical demand.")
        
        # Most Volatile Product
        prod_volatility = df.groupby('product_identifier')['sales'].std().fillna(0)
        if not prod_volatility.empty and prod_volatility.max() > 0:
            most_volatile = prod_volatility.idxmax()
            insights.append(f"**Product {most_volatile}** exhibits unusually high demand volatility.")
            
        # Overall Trend Placeholder (could be expanded)
        avg_sales = df['sales'].mean()
        insights.append(f"The average daily demand across the network is **{avg_sales:.2f}** units.")
        
    if perf_df is not None and not perf_df.empty:
        # Check if LightGBM beats Naive
        try:
            lgb_mae = perf_df.loc[perf_df['Model'] == 'LightGBM', 'MAE'].values[0]
            naive_mae = perf_df.loc[perf_df['Model'] == 'Seasonal Naive (7 Days Ago)', 'MAE'].values[0]
            if lgb_mae < naive_mae:
                improvement = ((naive_mae - lgb_mae) / naive_mae) * 100
                insights.append(f"The LightGBM champion model improves accuracy (MAE) by **{improvement:.1f}%** over the seasonal-naive baseline.")
        except Exception:
            pass
            
    if not insights:
        insights.append("Please upload data to generate insights.")
        
    return insights
