"""
Configuration for Production Forecasting Models
================================================
Centralized configuration for the maize production forecasting system
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent  # Points to ml/
FORECASTING_DIR = Path(__file__).parent   # Points to ml/forecasting/

# Data paths
DATA_DIR = BASE_DIR / 'data'
DATA_FILE = DATA_DIR / 'maize_production.csv'

# Output directories - organized by model type
MODELS_DIR = BASE_DIR / 'models' / 'production'
FORECASTS_DIR = BASE_DIR / 'forecasts' / 'production'
VISUALIZATIONS_DIR = BASE_DIR / 'visualizations' / 'production'
LOGS_DIR = BASE_DIR / 'logs'

# Create all directories
for directory in [DATA_DIR, MODELS_DIR, FORECASTS_DIR, VISUALIZATIONS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Model settings
FORECAST_MONTHS = 6
FORECAST_DAYS = FORECAST_MONTHS * 30
CONFIDENCE_INTERVAL = 0.95

# Prophet settings
PROPHET_CONFIG = {
    'yearly_seasonality': True,
    'weekly_seasonality': False,
    'daily_seasonality': False,
    'seasonality_mode': 'multiplicative',
    'interval_width': 0.95
}

# Bounds settings (to prevent unrealistic forecasts)
FLOOR_MULTIPLIER = 0.3  # Floor = 30% of historical minimum
CAP_MULTIPLIER = 2.5     # Cap = 2.5x historical maximum

# Visualization settings
FIGURE_DPI = 300
GRID_ROWS = 4
GRID_COLS = 3

# Color scheme
COLORS = {
    'historical': '#2E86AB',
    'forecast': '#A23B72',
    'confidence': '#A23B72',
    'cutoff': 'red',
    'growth_positive': '#388E3C',
    'growth_negative': '#D32F2F'
}

# Regions (will be auto-detected from data, but listed here for reference)
TANZANIA_REGIONS = [
    'Arusha', 'Dar es Salaam', 'Dodoma', 'Iringa', 'Kilimanjaro',
    'Mbeya', 'Morogoro', 'Mwanza', 'Rukwa', 'Ruvuma', 'Shinyanga'
]

# Print confirmation
print("=" * 80)
print("🔧 CONFIGURATION LOADED")
print("=" * 80)
print(f"📁 Base directory: {BASE_DIR}")
print(f"📊 Data file: {DATA_FILE}")
print(f"🤖 Models output: {MODELS_DIR}")
print(f"📈 Forecasts output: {FORECASTS_DIR}")
print(f"🎨 Visualizations output: {VISUALIZATIONS_DIR}")
print(f"📋 Logs output: {LOGS_DIR}")
print("=" * 80)
print()