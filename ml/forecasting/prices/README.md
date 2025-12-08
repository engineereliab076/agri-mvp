# 💰 Maize Price Prediction Module

Prophet-based price forecasting for all Tanzania markets and quality grades.

## 🎯 Overview

This module trains Prophet models to predict maize prices 6 months ahead for:
- **12 markets** across Tanzania
- **3 quality grades** (A, B, C)
- **Total: 36 models**

## 🚀 Quick Start

### Installation
```bash
cd ml/forecasting/prices
pip install -r requirements.txt
```

### Training
```bash
python train_price_models.py
```

**Duration:** ~3-5 minutes for all 36 models

## 📁 Output Structure
```
ml/
├── models/prices/
│   ├── prophet_mbeya_central_grade_a.pkl
│   ├── prophet_mbeya_central_grade_b.pkl
│   └── ... (36 models)
│
├── forecasts/prices/
│   ├── forecast_mbeya_central_grade_a.csv
│   ├── forecast_mbeya_central_grade_b.csv
│   ├── forecast_summary_all_markets.csv
│   └── ... (36 forecasts)
│
├── visualizations/prices/
│   ├── all_markets_grid_grade_a.png
│   ├── grade_comparison.png
│   └── forecast_heatmap_grade_a.png
│
└── logs/
    └── price_training_log_YYYYMMDD_HHMMSS.csv
```

## 📊 Forecast Files

Each forecast CSV contains:
- `date`: Forecast date
- `price_forecast`: Best estimate (yhat)
- `price_lower`: Lower bound (95% CI)
- `price_upper`: Upper bound (95% CI)

## 💻 Usage Example
```python
import pickle
import pandas as pd

# Load model
with open('ml/models/prices/prophet_mbeya_central_grade_a.pkl', 'rb') as f:
    model = pickle.load(f)

# Or load pre-computed forecast
forecast = pd.read_csv('ml/forecasts/prices/forecast_mbeya_central_grade_a.csv')
print(forecast.head())
```

## 🎯 Model Performance

Typical metrics:
- **MAE:** 50-100 TZS/kg
- **RMSE:** 70-130 TZS/kg
- **MAPE:** 5-10%

## 📈 Seasonal Patterns

Models capture:
- **Lean Season (Mar-May):** Prices rise 30-50%
- **Masika Harvest (Jun-Aug):** Prices drop 20-30%
- **Vuli Harvest (Jan-Feb):** Prices drop 10-15%
- **Weekly cycles:** Market day effects

## 🔄 Retraining

Retrain monthly with new data:
```bash
# Update maize_prices.csv
python train_price_models.py
```

All models and forecasts will be regenerated.

## ⚙️ Configuration

Edit `config.py` to change:
- Markets
- Quality grades
- Forecast horizon
- Prophet parameters
- Visualization settings

## 🐛 Troubleshooting

**Error: Data file not found**
```bash
# Ensure data file exists
ls ../../data/maize_prices.csv
```

**Error: Insufficient data**
- Minimum 100 data points required per market-grade
- Check data quality

**Poor model performance (MAPE > 20%)**
- May need more data
- External shocks (drought, policy changes)
- Consider retraining with updated parameters

## 📞 Support

Contact: @Eliabu (Data & AI Engineer)