# SmartStock Inference Contract & ML Pipeline

This document defines the strict ML inference contract for the SmartStock Streamlit application. It must be adhered to during feature engineering to avoid data leakage and ensure accurate predictions from the pre-trained LightGBM model.

## 1. Model Details
- **Model File**: `champion_lightgbm.pkl`
- **Model Type**: LightGBM Regressor
- **Target Variable**: `sales`
- **Performance Baseline**: MAE 1.0069, RMSE 3.3139, sMAPE 155.46%.

## 2. Input Data Schema
The uploaded dataset must contain at minimum the following columns:
- **Date Column**: `date` (datetime or parseable date string)
- **Grouping/Grain Features**: `outlet`, `product_identifier` 
- **Categorical Features**: `category_of_product`, `state`, `department_identifier`
- **Numeric Features**: `sell_price`
- **Time Features**: `week_id`
- **Target History**: `sales` - Required to compute historical lags and rolling means.

## 3. Feature Engineering & Strict Temporal Leakage Prevention
Features must be generated in the EXACT order expected by the model. 
To prevent temporal leakage, all lag and rolling calculations MUST be performed using strict chronological backward-looking windows grouped by `outlet` and `product_identifier`.

1. `product_identifier`
2. `department_identifier`
3. `category_of_product`
4. `outlet`
5. `state`
6. `week_id`
7. `sell_price`
8. `year`
9. `month`
10. `day`
11. `dayofweek`
12. `dayofyear`
13. `lag_7` (sales shifted by 7 days)
14. `lag_14` (sales shifted by 14 days)
15. `lag_28` (sales shifted by 28 days)
16. `rolling_mean_7` (7-day mean of the 7-day shifted sales)
17. `rolling_mean_28` (28-day mean of the 7-day shifted sales)

*Note on Recursive Forecasting*: When forecasting day `T+N`, the prediction for `T+(N-1)` is appended to the historical dataset, and features are recalculated.

## 4. Product Segmentation (Clustering)
- **Methodology**: Unsupervised KMeans clustering.
- **Target**: There is no legitimate supervised classification target (e.g., "HIGH_DEMAND"). We use clustering to group products by behavior.
- **Features**: Mean sales, Sales STD, Coefficient of Variation, Recent Growth, Zero Sales Ratio.
- **K Selection**: Evaluated dynamically using Silhouette Score.

## 5. Anomaly Detection
- **Methodology**: Isolation Forest.
- **Features**: Historical sales, rolling mean, rolling standard deviation.
- **Output**: NORMAL or ANOMALY.
