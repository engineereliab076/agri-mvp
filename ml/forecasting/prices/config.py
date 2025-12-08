from pathlib import Path


# PATH CONFIGURATION

# Base directory (ml/forecasting/prices/)
BASE_DIR = Path(__file__).resolve().parent

# Project root (ml/)
ML_DIR = BASE_DIR.parent.parent

# Data directories
DATA_DIR = ML_DIR / 'data'
PRICE_DATA_FILE = DATA_DIR / 'maize_prices.csv'

# Output directories
MODELS_DIR = ML_DIR / 'models' / 'prices'
FORECASTS_DIR = ML_DIR / 'forecasts' / 'prices'
VISUALIZATIONS_DIR = ML_DIR / 'visualizations' / 'prices'
LOGS_DIR = ML_DIR / 'logs'

# Create directories if they don't exist
for directory in [MODELS_DIR, FORECASTS_DIR, VISUALIZATIONS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# MODEL CONFIGURATION


# Markets to train on
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

# Prophet model parameters
PROPHET_PARAMS = {
    'yearly_seasonality': True,      # Capture harvest cycles
    'weekly_seasonality': True,      # Capture market day effects
    'daily_seasonality': False,      # Not needed for daily data
    'seasonality_mode': 'multiplicative',  # Better for prices
    'interval_width': 0.95,          # 95% confidence intervals
    'changepoint_prior_scale': 0.05  # Control trend flexibility
}

# Training configuration
TRAIN_TEST_SPLIT = 0.8  # 80% train, 20% test
FORECAST_DAYS = 180     # 6 months

# VISUALIZATION CONFIGURATION

# Plot settings
PLOT_DPI = 300
PLOT_STYLE = 'seaborn-v0_8-darkgrid'
FIGURE_SIZE_SINGLE = (14, 8)
FIGURE_SIZE_GRID = (20, 16)

# Colors
COLORS = {
    'train': '#2E86AB',
    'test': '#27AE60',
    'forecast': '#E74C3C',
    'confidence': '#E74C3C',
    'grade_a': '#2E86AB',
    'grade_b': '#A23B72',
    'grade_c': '#F18F01'
}

# LOGGING CONFIGURATION


LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


# FILE NAMING CONVENTIONS

def get_model_filename(market: str, grade: str) -> str:
    """Generate model filename"""
    market_slug = market.lower().replace(' ', '_')
    return f"prophet_{market_slug}_grade_{grade.lower()}.pkl"

def get_forecast_filename(market: str, grade: str) -> str:
    """Generate forecast filename"""
    market_slug = market.lower().replace(' ', '_')
    return f"forecast_{market_slug}_grade_{grade.lower()}.csv"

def get_visualization_filename(name: str) -> str:
    """Generate visualization filename"""
    return f"{name}.png"


# DISPLAY SETTINGS

# Console output width
CONSOLE_WIDTH = 100

# Number of decimal places for prices
PRICE_DECIMALS = 2

# VALIDATION


# Minimum required data points
MIN_DATA_POINTS = 100

# Maximum acceptable MAPE (%)
MAX_ACCEPTABLE_MAPE = 20.0

print(" Price forecasting configuration loaded!")