# SmartStock Sales Forecasting Project

## Overview
This project implements a time series forecasting pipeline to predict product sales of a retail chain using history-based machine learning.

## Features Engineered
- **Temporal Features**: Year, Month, Day, Day of Week, Day of Year.
- **Lag Features**: 7-day, 14-day, and 28-day historical lag of sales.
- **Rolling Statistics**: 7-day and 28-day rolling means calculated over lagged data.
- **Categorical Encodings**: Encoded categoricals via robust label encoders.

## Champion Model
- **Architecture**: LightGBM Regressor
- **Parameters**: n_estimators=100, max_depth=6, learning_rate=0.1

## Final Performance on Test Split
- **MAE**: 1.0069
- **RMSE**: 3.3139
- **SMAPE**: 155.46%
