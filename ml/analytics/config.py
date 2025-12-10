"""
Analytics Module Configuration
"""

from pathlib import Path

# PATH CONFIGURATION


# Base directory (ml/analytics/)
BASE_DIR = Path(__file__).resolve().parent

# Project root (ml/)
ML_DIR = BASE_DIR.parent

# Data directories
DATA_DIR = ML_DIR / 'data'
PRODUCTION_DATA = DATA_DIR / 'maize_production.csv'
PRICE_DATA = DATA_DIR / 'maize_prices.csv'
STORAGE_DATA = DATA_DIR / 'maize_storage.csv'

# Model directories
MODELS_DIR = ML_DIR / 'models'
PRODUCTION_MODELS_DIR = MODELS_DIR / 'production'
PRICE_MODELS_DIR = MODELS_DIR / 'prices'

# Forecast directories
FORECASTS_DIR = ML_DIR / 'forecasts'
PRODUCTION_FORECASTS_DIR = FORECASTS_DIR / 'production'
PRICE_FORECASTS_DIR = FORECASTS_DIR / 'prices'

# REGIONS & MARKETS

# Maize producing regions
REGIONS = [
    'Mbeya',
    'Iringa', 
    'Ruvuma',
    'Rukwa',
    'Morogoro',
    'Dodoma',
    'Arusha',
    'Kilimanjaro',
    'Dar es Salaam',
    'Mwanza',
    'Shinyanga'
]

# Markets
MARKETS = [
    'Mbeya Central',
    'Iringa Central',
    'Songea Central',
    'Sumbawanga Central',
    'Morogoro Central',
    'Dodoma Central',
    'Arusha Central',
    'Moshi Central',
    'Kariakoo',
    'Mwenge',
    'Mwanza Central',
    'Shinyanga Central'
]

# Quality grades
QUALITY_GRADES = ['A', 'B', 'C']

# SEASONAL CONFIGURATION

# Masika season (long rains)
MASIKA_PLANTING = [3, 4]  # March-April
MASIKA_HARVEST = [6, 7, 8]  # June-July-August (PEAK)

# Vuli season (short rains)  
VULI_PLANTING = [10, 11]  # October-November
VULI_HARVEST = [1, 2]  # January-February

# Lean season
LEAN_SEASON = [3, 4, 5]  # March-May (before Masika harvest)

# Production percentages
MASIKA_PRODUCTION_PCT = 0.65  # 65% of annual production
VULI_PRODUCTION_PCT = 0.35   # 35% of annual production

# THRESHOLDS & ALERTS

# Storage thresholds
STORAGE_CRITICAL_HIGH = 90  # % utilization - overstocked
STORAGE_CRITICAL_LOW = 10   # % utilization - understocked
STORAGE_OPTIMAL_MIN = 40    # % utilization - optimal range start
STORAGE_OPTIMAL_MAX = 80    # % utilization - optimal range end

# Price thresholds (TZS per kg)
PRICE_MIN_NORMAL = 800      # Below this = unusually low
PRICE_MAX_NORMAL = 2500     # Above this = unusually high

# Forecast accuracy thresholds
MAPE_EXCELLENT = 5.0   # < 5% = excellent
MAPE_GOOD = 10.0       # < 10% = good
MAPE_ACCEPTABLE = 20.0 # < 20% = acceptable

# ANALYTICS PERIODS


# Default time periods for analysis
DEFAULT_PERIOD = 'current'  # Current month/season
COMPARISON_PERIODS = {
    'current': 30,      # Last 30 days
    'month': 30,
    'quarter': 90,
    'season': 180,      # 6 months
    'year': 365
}

# QUALITY GRADE PREMIUMS

# Expected price premiums (percentage above Grade C)
EXPECTED_PREMIUMS = {
    'A': 0.25,  # Grade A should be ~25% more than Grade C
    'B': 0.12,  # Grade B should be ~12% more than Grade C
    'C': 0.00   # Grade C is baseline
}


# REGIONAL CHARACTERISTICS

# Regional classification
HIGH_PRODUCTION_REGIONS = ['Mbeya', 'Iringa', 'Ruvuma', 'Shinyanga']
MEDIUM_PRODUCTION_REGIONS = ['Rukwa', 'Morogoro', 'Dodoma', 'Mwanza']
LOW_PRODUCTION_REGIONS = ['Arusha', 'Kilimanjaro', 'Dar es Salaam']

# Consumption vs Production centers
PRODUCTION_CENTERS = ['Mbeya', 'Iringa', 'Ruvuma', 'Rukwa']
CONSUMPTION_CENTERS = ['Dar es Salaam', 'Arusha', 'Dodoma']

# DISPLAY SETTINGS

# Decimal places for different metrics
DECIMAL_PLACES = {
    'price': 2,
    'quantity': 2,
    'percentage': 1,
    'utilization': 1
}

# Currency formatting
CURRENCY = 'TZS'
CURRENCY_SYMBOL = 'TZS'

# VALIDATION RULES

# Data quality thresholds
MIN_DATA_POINTS = 10  # Minimum records needed for analysis
MAX_MISSING_PCT = 20  # Maximum % of missing data allowed

print("Analytics configuration loaded")