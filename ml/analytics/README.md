# 📊 Analytics Module

**Core intelligence functions for Maize Intelligence MVP**

---

## 🎯 Overview

This module provides **8 core analytics functions** that power the dashboard and API insights. These functions analyze production, prices, storage, and forecasts to deliver actionable intelligence for farmers, traders, and policymakers.

## 🚀 Quick Start

### Installation

```bash
cd ml/analytics
pip install -r requirements.txt
```

### Basic Usage

```python
from analytics import get_national_summary, get_price_analysis

# Get national overview
summary = get_national_summary(period='current')
print(summary)

# Analyze prices
prices = get_price_analysis(market='Mbeya Central', grade='A')
print(prices)
```

---

## 📊 Available Functions

### 1. **get_national_summary(period='current')**

High-level national KPIs across production, prices, and storage.

**Parameters:**
- `period`: Time period - 'current' (30 days), 'month', 'quarter', 'season', 'year'

**Returns:**
```python
{
    'production': {
        'total_tons': 47234.52,
        'avg_per_region': 4294.96,
        'active_regions': 11
    },
    'prices': {
        'avg_price_tzs': 1695.43,
        'active_markets': 12
    },
    'storage': {
        'total_stored_tons': 31456.78,
        'total_capacity_tons': 50000.00,
        'utilization_percent': 62.9
    }
}
```

**Dashboard Use:** Hero KPIs at top of dashboard

---

### 2. **get_production_summary(region=None, period='current')**

Production analysis by region or national level.

**Parameters:**
- `region`: Specific region or None for all (e.g., 'Mbeya', 'Iringa')
- `period`: Time period for analysis

**Returns:**
```python
{
    'region': 'Mbeya',
    'current_period': {
        'total_production_tons': 8532.45,
        'avg_monthly_tons': 2844.15,
        'yoy_growth_percent': 12.3
    },
    'forecast_comparison': {
        'forecast_next_30_days': 9120.50,
        'vs_current_period': 6.9
    }
}
```

**Dashboard Use:** Regional production page, performance tracking

---

### 3. **get_price_analysis(market=None, grade=None)**

Comprehensive price intelligence across markets and quality grades.

**Parameters:**
- `market`: Specific market or None for all (e.g., 'Kariakoo', 'Mbeya Central')
- `grade`: Quality grade ('A', 'B', 'C') or None for all

**Returns:**
```python
{
    'market': 'Mbeya Central',
    'grade': 'A',
    'current_prices': {
        'avg_price_tzs': 1577.45,
        'min_price_tzs': 1520.00,
        'max_price_tzs': 1650.00,
        'volatility': 35.67
    },
    'grade_analysis': {
        'prices_by_grade': {'A': 1577, 'B': 1450, 'C': 1320},
        'grade_premiums': {
            'A': {'actual_premium_percent': 19.5, 'expected_premium_percent': 25.0}
        }
    },
    'forecast_comparison': {
        'forecast_next_month': 1650.00,
        'vs_current': 4.6
    }
}
```

**Dashboard Use:** Price intelligence page, market comparison

---

### 4. **get_storage_status(warehouse=None)**

Storage monitoring with utilization analysis and alerts.

**Parameters:**
- `warehouse`: Specific warehouse ID or None for all

**Returns:**
```python
{
    'national_summary': {
        'total_stored_tons': 31456.78,
        'total_capacity_tons': 50000.00,
        'utilization_percent': 62.9,
        'active_warehouses': 15
    },
    'utilization_categories': {
        'optimal': 10,
        'overstocked': 2,
        'understocked': 3
    },
    'alerts': [
        {
            'type': 'overstocked',
            'severity': 'high',
            'message': '2 warehouse(s) over 90% capacity',
            'warehouses': ['WH_001', 'WH_005']
        }
    ]
}
```

**Dashboard Use:** Storage monitoring page, capacity alerts

---

### 5. **get_seasonal_pattern(crop='maize')**

Seasonal analysis with Masika/Vuli cycles and monthly patterns.

**Parameters:**
- `crop`: Crop type (currently only 'maize')

**Returns:**
```python
{
    'seasonal_patterns': {
        'masika_season': {
            'harvest_months': ['Jun', 'Jul', 'Aug'],
            'production_share_percent': 65.0,
            'characteristics': 'Main harvest - highest production, lowest prices'
        },
        'vuli_season': {
            'harvest_months': ['Jan', 'Feb'],
            'production_share_percent': 35.0
        },
        'lean_season': {
            'months': ['Mar', 'Apr', 'May'],
            'characteristics': 'Pre-harvest period - low production, high prices'
        }
    },
    'insights': {
        'peak_production_month': 'Jul',
        'low_production_month': 'Apr',
        'peak_price_month': 'May',
        'low_price_month': 'Aug'
    }
}
```

**Dashboard Use:** Seasonal calendar view, planning tools

---

### 6. **get_forecast_accuracy()**

ML model performance metrics and validation.

**Returns:**
```python
{
    'production_models': {
        'by_region': {
            'Mbeya': {
                'mae': 245.67,
                'rmse': 312.45,
                'mape_percent': 5.8,
                'data_points': 120
            }
        },
        'model_type': 'Prophet',
        'status': 'active'
    },
    'price_models': {
        'sample_metrics': {...},
        'model_type': 'Prophet',
        'status': 'active'
    },
    'overall_performance': {
        'production_models_active': 11,
        'price_models_active': 36,
        'status': 'All models operational'
    }
}
```

**Dashboard Use:** Model performance page, accuracy reporting

---

### 7. **get_supply_demand_balance()**

Supply-demand dynamics with production-price correlations.

**Returns:**
```python
{
    'current_balance': {
        'status': 'surplus',
        'message': 'Production above average - favorable supply conditions',
        'production_tons': 5234.56,
        'avg_price_tzs': 1450.00,
        'storage_tons': 3200.00
    },
    'correlation_analysis': {
        'price_production_correlation': -0.72,
        'interpretation': 'Negative correlation expected (high production → low prices)'
    },
    'historical_patterns': {
        'surplus_periods': ['2023-06', '2023-07', '2023-08'],
        'shortage_periods': ['2023-03', '2023-04'],
        'avg_production': 4523.45
    }
}
```

**Dashboard Use:** Market dynamics page, supply chain intelligence

---

### 8. **get_market_opportunities()**

Trading opportunities and actionable recommendations.

**Returns:**
```python
{
    'arbitrage_opportunity': {
        'buy_market': 'Mbeya Central',
        'buy_price_tzs': 1577.45,
        'sell_market': 'Kariakoo',
        'sell_price_tzs': 1813.20,
        'price_gap_tzs': 235.75,
        'profit_margin_percent': 14.9,
        'recommendation': 'Strong opportunity'
    },
    'quality_premium_opportunity': {
        'grade_c_price_tzs': 1320.00,
        'grade_a_price_tzs': 1577.00,
        'premium_percent': 19.5,
        'recommendation': 'Moderate quality focus'
    },
    'timing_recommendation': {
        'current_period': 'Masika harvest',
        'action': 'HOLD or STORE',
        'reason': 'Prices typically drop during harvest. Consider storage.',
        'confidence': 'High'
    },
    'forecast_opportunities': [
        {
            'market': 'Dodoma Central',
            'current_price': 1650.00,
            'forecast_price': 1850.00,
            'change_percent': 12.1,
            'action': 'Consider storing'
        }
    ]
}
```

**Dashboard Use:** Recommendations page, trading intelligence

---

## 🔄 Data Validation

The module includes comprehensive validation functions:

### Validate Production Data

```python
from analytics import validate_production_data
import pandas as pd

df = pd.read_csv('maize_production.csv')
result = validate_production_data(df)

if result.is_valid():
    print("✅ Data is valid!")
else:
    print("❌ Validation errors:")
    for error in result.errors:
        print(f"  - {error}")
```

### Validate All Datasets

```python
from analytics import validate_all_data

results = validate_all_data()

for dataset_name, result in results.items():
    status = "✅ VALID" if result.is_valid() else "❌ INVALID"
    print(f"{dataset_name}: {status}")
```

---

## 🧪 Testing

Run the test suite:

```bash
# Test all analytics functions
python core_analytics.py

# Test all validators
python validators.py
```

---

## 📁 Module Structure

```
ml/analytics/
├── __init__.py              # Package initialization
├── config.py                # Configuration settings
├── core_analytics.py        # 8 main analytics functions
├── validators.py            # Data validation functions
├── requirements.txt         # Dependencies
└── README.md               # This file
```

---

## 🔗 Integration

### For @Benard (Backend API):

```python
# In your Flask/FastAPI app
from ml.analytics import get_national_summary, get_price_analysis

@app.get("/api/analytics/summary")
def national_summary():
    return get_national_summary(period='current')

@app.get("/api/analytics/prices/{market}")
def market_prices(market: str):
    return get_price_analysis(market=market)
```

### For @Richard (Frontend Dashboard):

```javascript
// Fetch national summary
fetch('/api/analytics/summary')
  .then(res => res.json())
  .then(data => {
    displayKPIs(data.production, data.prices, data.storage);
  });

// Fetch market opportunities
fetch('/api/analytics/opportunities')
  .then(res => res.json())
  .then(data => {
    displayOpportunities(data.arbitrage_opportunity);
  });
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

- **Regions and Markets:** Add/remove regions and markets
- **Seasonal Definitions:** Adjust Masika/Vuli dates
- **Thresholds:** Change storage alerts, price ranges
- **Periods:** Modify default analysis periods

Example:

```python
# config.py
STORAGE_CRITICAL_HIGH = 90  # Alert when >90% full
STORAGE_CRITICAL_LOW = 10   # Alert when <10% full
LEAN_SEASON = [3, 4, 5]     # March-May
```

---

## 🐛 Troubleshooting

**Error: "Data file not found"**
```bash
# Ensure CSV files exist
ls ../../data/*.csv
```

**Error: "Invalid region/market"**
```python
# Check valid values in config
from analytics.config import REGIONS, MARKETS
print(REGIONS)
print(MARKETS)
```

**Error: "Insufficient data"**
- Minimum 10 data points required per analysis
- Check data quality with validators

---

## 📊 Performance

- **Function execution:** < 1 second (typical)
- **Memory usage:** ~50-100 MB for full datasets
- **Concurrent requests:** Supports multiple simultaneous calls

---

## 🚀 Future Enhancements

Potential additions after MVP:

- [ ] Weather correlation analysis
- [ ] Transport cost integration
- [ ] Regional trade flow mapping
- [ ] Predictive alerts
- [ ] Multi-crop support
- [ ] Real-time streaming analytics

---

## 📞 Support

**Author:** Eliabu - CEO + Data & AI Engineer  
**Company:** African Intelligence Company  
**Project:** Maize Intelligence MVP

For questions or issues, contact the development team.

---

## 📄 License

Proprietary - African Intelligence Company © 2024

---

**🎉 DELIVERABLE 4 COMPLETE - 8 ANALYTICS FUNCTIONS READY FOR PRODUCTION!**