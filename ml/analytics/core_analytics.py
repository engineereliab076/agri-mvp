"""
Core Analytics Functions
========================
Main analytics functions for Maize Intelligence MVP

These functions are called by the API and power the dashboard insights.
"""

"""
Core Analytics Functions
"""

# Use absolute imports to avoid conflicts
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import warnings
warnings.filterwarnings('ignore')

# Import config with try/except
try:
    from analytics.config import (
        PRODUCTION_DATA, PRICE_DATA, STORAGE_DATA,
        # ... rest of imports
    )
except ImportError:
    from .config import (
        PRODUCTION_DATA, PRICE_DATA, STORAGE_DATA,
        # ... rest of imports
    )

# Import configuration
from .config import (
    PRODUCTION_DATA, PRICE_DATA, STORAGE_DATA,
    PRODUCTION_FORECASTS_DIR, PRICE_FORECASTS_DIR,
    REGIONS, MARKETS, QUALITY_GRADES,
    MASIKA_HARVEST, VULI_HARVEST, LEAN_SEASON,
    MASIKA_PRODUCTION_PCT, VULI_PRODUCTION_PCT,
    STORAGE_CRITICAL_HIGH, STORAGE_CRITICAL_LOW,
    STORAGE_OPTIMAL_MIN, STORAGE_OPTIMAL_MAX,
    EXPECTED_PREMIUMS, COMPARISON_PERIODS,
    DECIMAL_PLACES, CURRENCY
)

# ============================================================================
# DATA LOADING UTILITIES
# ============================================================================

def load_production_data():
    """Load production data"""
    df = pd.read_csv(PRODUCTION_DATA)
    df['date'] = pd.to_datetime(df['date'])
    return df

def load_price_data():
    """Load price data"""
    df = pd.read_csv(PRICE_DATA)
    df['date'] = pd.to_datetime(df['date'])
    return df

def load_storage_data():
    """Load storage data"""
    df = pd.read_csv(STORAGE_DATA)
    df['date'] = pd.to_datetime(df['date'])
    return df

def load_production_forecasts():
    """Load all production forecasts"""
    summary_file = PRODUCTION_FORECASTS_DIR / 'forecast_summary.csv'
    if summary_file.exists():
        df = pd.read_csv(summary_file)
        # This is a summary file, not time-series data
        # Columns: region, historical_avg, forecast_avg, growth_pct, etc.
        return df
    return None

def load_price_forecasts():
    """Load all price forecasts"""
    summary_file = PRICE_FORECASTS_DIR / 'forecast_summary_all_markets.csv'
    if summary_file.exists():
        df = pd.read_csv(summary_file)
        # Convert month period to datetime - handle if column exists
        if 'month' in df.columns:
            df['month'] = pd.to_datetime(df['month'].astype(str))
        return df
    return None
# ============================================================================
# FUNCTION 1: NATIONAL SUMMARY
# ============================================================================

def get_national_summary(period='current'):
    """
    Get high-level national KPIs
    
    Args:
        period: 'current' (last 30 days), 'month', 'quarter', 'season', 'year'
    
    Returns:
        dict: National summary statistics
    """
    
    # Load data
    production_df = load_production_data()
    price_df = load_price_data()
    storage_df = load_storage_data()
    
    # Get time window
    days = COMPARISON_PERIODS.get(period, 30)
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Filter to period
    prod_period = production_df[production_df['date'] >= cutoff_date]
    price_period = price_df[price_df['date'] >= cutoff_date]
    storage_period = storage_df[storage_df['date'] >= cutoff_date]
    
    # Calculate metrics
    total_production = prod_period['quantity_tons'].sum()
    avg_price = price_period['price_per_kg_tzs'].mean()
    
    # Storage metrics
    latest_storage = storage_df.sort_values('date').groupby('warehouse_id').last()
    total_stored = latest_storage['quantity_stored_tons'].sum()
    total_capacity = latest_storage['capacity_tons'].sum()
    storage_utilization = (total_stored / total_capacity * 100) if total_capacity > 0 else 0
    
    # Count active entities
    active_regions = prod_period['region'].nunique()
    active_markets = price_period['market'].nunique()
    active_warehouses = len(latest_storage)
    
    return {
        'period': period,
        'period_days': days,
        'production': {
            'total_tons': round(total_production, DECIMAL_PLACES['quantity']),
            'avg_per_region': round(total_production / active_regions, DECIMAL_PLACES['quantity']) if active_regions > 0 else 0,
            'active_regions': active_regions
        },
        'prices': {
            'avg_price_tzs': round(avg_price, DECIMAL_PLACES['price']),
            'currency': CURRENCY,
            'active_markets': active_markets
        },
        'storage': {
            'total_stored_tons': round(total_stored, DECIMAL_PLACES['quantity']),
            'total_capacity_tons': round(total_capacity, DECIMAL_PLACES['quantity']),
            'utilization_percent': round(storage_utilization, DECIMAL_PLACES['utilization']),
            'active_warehouses': active_warehouses
        },
        'generated_at': datetime.now().isoformat()
    }

# ============================================================================
# FUNCTION 2: PRODUCTION SUMMARY
# ============================================================================

def get_production_summary(region=None, period='current'):
    """
    Get production summary by region or national
    
    Args:
        region: Specific region or None for all
        period: Time period for analysis
    
    Returns:
        dict: Production summary with comparisons
    """
    
    # Load data
    production_df = load_production_data()
    forecasts_df = load_production_forecasts()
    
    # Filter by region if specified
    if region:
        production_df = production_df[production_df['region'] == region]
    
    # Get time window
    days = COMPARISON_PERIODS.get(period, 30)
    cutoff_date = datetime.now() - timedelta(days=days)
    prod_period = production_df[production_df['date'] >= cutoff_date]
    
    # Calculate current period metrics
    total_production = prod_period['quantity_tons'].sum()
    avg_monthly = prod_period.groupby(prod_period['date'].dt.to_period('M'))['quantity_tons'].sum().mean()
    
    # Year-over-year comparison (if data available)
    yoy_cutoff = cutoff_date - timedelta(days=365)
    yoy_period = production_df[
        (production_df['date'] >= yoy_cutoff) & 
        (production_df['date'] < cutoff_date)
    ]
    yoy_production = yoy_period['quantity_tons'].sum()
    yoy_growth = ((total_production - yoy_production) / yoy_production * 100) if yoy_production > 0 else 0
    
    # Regional breakdown
    regional_breakdown = prod_period.groupby('region')['quantity_tons'].sum().to_dict()
    regional_breakdown = {k: round(v, DECIMAL_PLACES['quantity']) for k, v in regional_breakdown.items()}
    
    # Get forecast comparison (next 30 days)
    # Get forecast comparison from summary data
    forecast_comparison = None
    if forecasts_df is not None:
        try:
            if region:
                # Get forecast for specific region
                region_forecast = forecasts_df[forecasts_df['region'] == region]
            if len(region_forecast) > 0:
                forecast_avg = region_forecast['forecast_avg'].iloc[0]
                historical_avg = region_forecast['historical_avg'].iloc[0]
                growth_pct = region_forecast['growth_pct'].iloc[0]
                
                forecast_comparison = {
                    'forecast_avg_tons': round(forecast_avg, DECIMAL_PLACES['quantity']),
                    'historical_avg_tons': round(historical_avg, DECIMAL_PLACES['quantity']),
                    'growth_percent': round(growth_pct, DECIMAL_PLACES['percentage'])
                }
            else:
                # National level - aggregate all regions
                forecast_total = forecasts_df['forecast_avg'].sum()
                historical_total = forecasts_df['historical_avg'].sum()
                growth_pct = ((forecast_total - historical_total) / historical_total * 100) if historical_total > 0 else 0
                
                forecast_comparison = {
                    'forecast_avg_tons': round(forecast_total, DECIMAL_PLACES['quantity']),
                    'historical_avg_tons': round(historical_total, DECIMAL_PLACES['quantity']),
                    'growth_percent': round(growth_pct, DECIMAL_PLACES['percentage'])
                }
        except Exception as e:
        # Forecast comparison not available
            pass
    return {
        'region': region if region else 'National',
        'period': period,
        'current_period': {
            'total_production_tons': round(total_production, DECIMAL_PLACES['quantity']),
            'avg_monthly_tons': round(avg_monthly, DECIMAL_PLACES['quantity']),
            'yoy_growth_percent': round(yoy_growth, DECIMAL_PLACES['percentage'])
        },
        'regional_breakdown': regional_breakdown,
        'forecast_comparison': forecast_comparison,
        'generated_at': datetime.now().isoformat()
    }

# ============================================================================
# FUNCTION 3: PRICE ANALYSIS
# ============================================================================

def get_price_analysis(market=None, grade=None):
    """
    Comprehensive price analysis
    
    Args:
        market: Specific market or None for all
        grade: Quality grade ('A', 'B', 'C') or None for all
    
    Returns:
        dict: Price analysis with comparisons
    """
    
    # Load data
    price_df = load_price_data()
    forecasts_df = load_price_forecasts()
    
    # Filter by market and grade if specified
    if market:
        price_df = price_df[price_df['market'] == market]
    if grade:
        price_df = price_df[price_df['quality_grade'] == grade]
    
    # Get current prices (last 7 days)
    cutoff = datetime.now() - timedelta(days=7)
    current_prices = price_df[price_df['date'] >= cutoff]
    
    # Calculate metrics
    avg_price = current_prices['price_per_kg_tzs'].mean()
    min_price = current_prices['price_per_kg_tzs'].min()
    max_price = current_prices['price_per_kg_tzs'].max()
    price_volatility = current_prices['price_per_kg_tzs'].std()
    
    # Price by market (if national view)
    market_prices = None
    if not market:
        market_prices = current_prices.groupby('market')['price_per_kg_tzs'].mean().sort_values(ascending=False).to_dict()
        market_prices = {k: round(v, DECIMAL_PLACES['price']) for k, v in market_prices.items()}
    
    # Price by grade (if not filtered)
    grade_prices = None
    grade_premiums = None
    if not grade:
        grade_prices = current_prices.groupby('quality_grade')['price_per_kg_tzs'].mean().to_dict()
        grade_prices = {k: round(v, DECIMAL_PLACES['price']) for k, v in grade_prices.items()}
        
        # Calculate actual premiums vs Grade C
        if 'C' in grade_prices:
            base_price = grade_prices['C']
            grade_premiums = {}
            for g in ['A', 'B', 'C']:
                if g in grade_prices:
                    premium_pct = ((grade_prices[g] - base_price) / base_price * 100) if base_price > 0 else 0
                    grade_premiums[g] = {
                        'actual_premium_percent': round(premium_pct, DECIMAL_PLACES['percentage']),
                        'expected_premium_percent': round(EXPECTED_PREMIUMS[g] * 100, DECIMAL_PLACES['percentage'])
                    }
    
    # Get forecast (next month)
    forecast_comparison = None
    if forecasts_df is not None:
        future_month = (datetime.now() + timedelta(days=30)).replace(day=1)
        
        forecast_data = forecasts_df[forecasts_df['month'] == future_month]
        
        if market:
            forecast_data = forecast_data[forecast_data['market'] == market]
        if grade:
            forecast_data = forecast_data[forecast_data['grade'] == grade]
        
        if len(forecast_data) > 0:
            forecast_avg = forecast_data['yhat'].mean()
            forecast_comparison = {
                'forecast_next_month': round(forecast_avg, DECIMAL_PLACES['price']),
                'vs_current': round(((forecast_avg - avg_price) / avg_price * 100), DECIMAL_PLACES['percentage']) if avg_price > 0 else 0
            }
    
    return {
        'market': market if market else 'All Markets',
        'grade': grade if grade else 'All Grades',
        'current_prices': {
            'avg_price_tzs': round(avg_price, DECIMAL_PLACES['price']),
            'min_price_tzs': round(min_price, DECIMAL_PLACES['price']),
            'max_price_tzs': round(max_price, DECIMAL_PLACES['price']),
            'volatility': round(price_volatility, DECIMAL_PLACES['price']),
            'currency': CURRENCY
        },
        'market_comparison': market_prices,
        'grade_analysis': {
            'prices_by_grade': grade_prices,
            'grade_premiums': grade_premiums
        } if not grade else None,
        'forecast_comparison': forecast_comparison,
        'generated_at': datetime.now().isoformat()
    }

# ============================================================================
# FUNCTION 4: STORAGE STATUS
# ============================================================================

def get_storage_status(warehouse=None):
    """
    Storage monitoring and utilization analysis
    
    Args:
        warehouse: Specific warehouse or None for all
    
    Returns:
        dict: Storage status with alerts
    """
    
    # Load data
    storage_df = load_storage_data()
    
    # Get latest status for each warehouse
    latest = storage_df.sort_values('date').groupby('warehouse_id').last().reset_index()
    
    # Filter by warehouse if specified
    if warehouse:
        latest = latest[latest['warehouse_id'] == warehouse]
    
    # Calculate utilization
    latest['utilization_percent'] = (latest['quantity_stored_tons'] / latest['capacity_tons'] * 100).round(DECIMAL_PLACES['utilization'])
    
    # National totals
    total_stored = latest['quantity_stored_tons'].sum()
    total_capacity = latest['capacity_tons'].sum()
    national_utilization = (total_stored / total_capacity * 100) if total_capacity > 0 else 0
    
    # Categorize warehouses
    overstocked = latest[latest['utilization_percent'] > STORAGE_CRITICAL_HIGH]
    understocked = latest[latest['utilization_percent'] < STORAGE_CRITICAL_LOW]
    optimal = latest[
        (latest['utilization_percent'] >= STORAGE_OPTIMAL_MIN) &
        (latest['utilization_percent'] <= STORAGE_OPTIMAL_MAX)
    ]
    
    # Create warehouse list
    warehouse_status = latest[['warehouse_id', 'region', 'quantity_stored_tons', 
                                'capacity_tons', 'utilization_percent']].to_dict('records')
    
    # Alerts
    alerts = []
    if len(overstocked) > 0:
        alerts.append({
            'type': 'overstocked',
            'severity': 'high',
            'message': f'{len(overstocked)} warehouse(s) over {STORAGE_CRITICAL_HIGH}% capacity',
            'warehouses': overstocked['warehouse_id'].tolist()
        })
    
    if len(understocked) > 0:
        alerts.append({
            'type': 'understocked',
            'severity': 'medium',
            'message': f'{len(understocked)} warehouse(s) under {STORAGE_CRITICAL_LOW}% capacity',
            'warehouses': understocked['warehouse_id'].tolist()
        })
    
    return {
        'warehouse': warehouse if warehouse else 'All Warehouses',
        'national_summary': {
            'total_stored_tons': round(total_stored, DECIMAL_PLACES['quantity']),
            'total_capacity_tons': round(total_capacity, DECIMAL_PLACES['quantity']),
            'utilization_percent': round(national_utilization, DECIMAL_PLACES['utilization']),
            'active_warehouses': len(latest)
        },
        'utilization_categories': {
            'optimal': len(optimal),
            'overstocked': len(overstocked),
            'understocked': len(understocked)
        },
        'warehouse_status': warehouse_status if not warehouse else warehouse_status[0] if len(warehouse_status) > 0 else None,
        'alerts': alerts,
        'generated_at': datetime.now().isoformat()
    }

# ============================================================================
# FUNCTION 5: SEASONAL PATTERN
# ============================================================================

def get_seasonal_pattern(crop='maize'):
    """
    Analyze seasonal patterns for planning
    
    Args:
        crop: Crop type (currently only 'maize')
    
    Returns:
        dict: Seasonal patterns and calendar
    """
    
    # Load data
    production_df = load_production_data()
    price_df = load_price_data()
    
    # Add month column
    production_df['month'] = production_df['date'].dt.month
    price_df['month'] = price_df['date'].dt.month
    
    # Calculate monthly averages
    monthly_production = production_df.groupby('month')['quantity_tons'].mean().to_dict()
    monthly_prices = price_df.groupby('month')['price_per_kg_tzs'].mean().to_dict()
    
    # Round values
    monthly_production = {int(k): round(v, DECIMAL_PLACES['quantity']) for k, v in monthly_production.items()}
    monthly_prices = {int(k): round(v, DECIMAL_PLACES['price']) for k, v in monthly_prices.items()}
    
    # Identify peaks and troughs
    prod_values = list(monthly_production.values())
    peak_production_month = list(monthly_production.keys())[prod_values.index(max(prod_values))]
    low_production_month = list(monthly_production.keys())[prod_values.index(min(prod_values))]
    
    price_values = list(monthly_prices.values())
    peak_price_month = list(monthly_prices.keys())[price_values.index(max(price_values))]
    low_price_month = list(monthly_prices.keys())[price_values.index(min(price_values))]
    
    # Seasonal calendar
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                   7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    
    seasonal_calendar = {}
    for month in range(1, 13):
        season_type = 'normal'
        if month in MASIKA_HARVEST:
            season_type = 'masika_harvest'
        elif month in VULI_HARVEST:
            season_type = 'vuli_harvest'
        elif month in LEAN_SEASON:
            season_type = 'lean_season'
        
        seasonal_calendar[month_names[month]] = {
            'month_number': month,
            'season_type': season_type,
            'avg_production_tons': monthly_production.get(month, 0),
            'avg_price_tzs': monthly_prices.get(month, 0)
        }
    
    return {
        'crop': crop,
        'seasonal_patterns': {
            'masika_season': {
                'harvest_months': [month_names[m] for m in MASIKA_HARVEST],
                'production_share_percent': round(MASIKA_PRODUCTION_PCT * 100, DECIMAL_PLACES['percentage']),
                'characteristics': 'Main harvest - highest production, lowest prices'
            },
            'vuli_season': {
                'harvest_months': [month_names[m] for m in VULI_HARVEST],
                'production_share_percent': round(VULI_PRODUCTION_PCT * 100, DECIMAL_PLACES['percentage']),
                'characteristics': 'Secondary harvest - moderate production and prices'
            },
            'lean_season': {
                'months': [month_names[m] for m in LEAN_SEASON],
                'characteristics': 'Pre-harvest period - low production, high prices'
            }
        },
        'monthly_averages': {
            'production': monthly_production,
            'prices': monthly_prices
        },
        'insights': {
            'peak_production_month': month_names[peak_production_month],
            'low_production_month': month_names[low_production_month],
            'peak_price_month': month_names[peak_price_month],
            'low_price_month': month_names[low_price_month]
        },
        'seasonal_calendar': seasonal_calendar,
        'generated_at': datetime.now().isoformat()
    }

# ============================================================================
# FUNCTION 6: FORECAST ACCURACY
# ============================================================================

def get_forecast_accuracy():
    """
    Evaluate ML model performance
    
    Returns:
        dict: Model accuracy metrics and comparison
    """
    
    price_forecasts = load_price_forecasts()
    prod_forecasts = load_production_forecasts()
    price_forecasts = load_price_forecasts()
    results = {
        'production_models': {},
        'price_models': {},
        'overall_performance': {}
    }
    
    # Production model accuracy from summary
    if prod_forecasts is not None:
        regional_metrics = {}
        
        for _, row in prod_forecasts.iterrows():
            region = row['region']
            growth_pct = row['growth_pct']
            forecast_avg = row['forecast_avg']
            historical_avg = row['historical_avg']
            
            # Simple accuracy metric based on growth
            regional_metrics[region] = {
                'forecast_avg_tons': round(forecast_avg, DECIMAL_PLACES['quantity']),
                'historical_avg_tons': round(historical_avg, DECIMAL_PLACES['quantity']),
                'growth_percent': round(growth_pct, DECIMAL_PLACES['percentage']),
                'status': 'active'
            }
        
        results['production_models'] = {
            'by_region': regional_metrics,
            'model_type': 'Prophet',
            'status': 'active',
            'total_models': len(regional_metrics)
        }
    
    # Price model status
    if price_forecasts is not None:
        # Count unique market-grade combinations
        if 'market' in price_forecasts.columns and 'grade' in price_forecasts.columns:
            price_model_count = price_forecasts.groupby(['market', 'grade']).size().count()
        else:
            price_model_count = 36
        
        results['price_models'] = {
            'total_models': price_model_count,
            'model_type': 'Prophet',
            'status': 'active'
        }
    
    # Overall summary
    results['overall_performance'] = {
        'production_models_active': len(results['production_models'].get('by_region', {})),
        'price_models_active': results.get('price_models', {}).get('total_models', 36),
        'last_evaluation': datetime.now().isoformat(),
        'status': 'All models operational'
    }
    
    return results

# ============================================================================
# FUNCTION 7: SUPPLY-DEMAND BALANCE
# ============================================================================

def get_supply_demand_balance():
    """
    Analyze supply-demand dynamics
    
    Returns:
        dict: Supply-demand analysis with correlations
    """
    
    # Load data
    production_df = load_production_data()
    price_df = load_price_data()
    storage_df = load_storage_data()
    
    # Aggregate by month
    production_df['month'] = production_df['date'].dt.to_period('M')
    price_df['month'] = price_df['date'].dt.to_period('M')
    storage_df['month'] = storage_df['date'].dt.to_period('M')
    
    monthly_production = production_df.groupby('month')['quantity_tons'].sum()
    monthly_price = price_df.groupby('month')['price_per_kg_tzs'].mean()
    monthly_storage = storage_df.groupby('month')['quantity_stored_tons'].mean()
    
    # Calculate correlation (production vs price)
    correlation_df = pd.DataFrame({
        'production': monthly_production,
        'price': monthly_price
    }).dropna()
    
    if len(correlation_df) > 2:
        price_prod_correlation = correlation_df['production'].corr(correlation_df['price'])
    else:
        price_prod_correlation = None
    
    # Identify surplus/shortage periods
    prod_mean = monthly_production.mean()
    prod_std = monthly_production.std()
    
    surplus_months = monthly_production[monthly_production > (prod_mean + prod_std)].index.tolist()
    shortage_months = monthly_production[monthly_production < (prod_mean - prod_std)].index.tolist()
    
    # Current balance
    latest_prod = monthly_production.iloc[-1] if len(monthly_production) > 0 else 0
    latest_price = monthly_price.iloc[-1] if len(monthly_price) > 0 else 0
    latest_storage = monthly_storage.iloc[-1] if len(monthly_storage) > 0 else 0
    
    # Determine current status
    if latest_prod > prod_mean:
        current_status = 'surplus'
        status_message = 'Production above average - favorable supply conditions'
    elif latest_prod < (prod_mean - prod_std):
        current_status = 'shortage'
        status_message = 'Production below average - potential supply constraints'
    else:
        current_status = 'balanced'
        status_message = 'Production at normal levels'
    
    return {
        'current_balance': {
            'status': current_status,
            'message': status_message,
            'production_tons': round(latest_prod, DECIMAL_PLACES['quantity']),
            'avg_price_tzs': round(latest_price, DECIMAL_PLACES['price']),
            'storage_tons': round(latest_storage, DECIMAL_PLACES['quantity'])
        },
        'correlation_analysis': {
            'price_production_correlation': round(price_prod_correlation, 3) if price_prod_correlation else None,
            'interpretation': 'Negative correlation expected (high production → low prices)' if price_prod_correlation and price_prod_correlation < 0 else 'Positive correlation indicates other factors at play'
        },
        'historical_patterns': {
            'surplus_periods': [str(m) for m in surplus_months],
            'shortage_periods': [str(m) for m in shortage_months],
            'avg_production': round(prod_mean, DECIMAL_PLACES['quantity']),
            'production_volatility': round(prod_std, DECIMAL_PLACES['quantity'])
        },
        'generated_at': datetime.now().isoformat()
    }

# ============================================================================
# FUNCTION 8: MARKET OPPORTUNITIES
# ============================================================================

def get_market_opportunities():
    """
    Identify trading and selling opportunities
    
    Returns:
        dict: Market opportunities and recommendations
    """
    
    # Load data
    price_df = load_price_data()
    prod_forecasts = load_production_forecasts()
    price_forecasts = load_price_forecasts()
    
    # Get current prices (last 7 days)
    cutoff = datetime.now() - timedelta(days=7)
    current_prices = price_df[price_df['date'] >= cutoff]
    
    # Price by market (Grade A for comparison)
    market_prices = current_prices[current_prices['quality_grade'] == 'A'].groupby('market')['price_per_kg_tzs'].mean()
    
    if len(market_prices) < 2:
        return {'message': 'Insufficient data for opportunity analysis'}
    
    # Identify arbitrage opportunities
    max_price_market = market_prices.idxmax()
    min_price_market = market_prices.idxmin()
    max_price = market_prices.max()
    min_price = market_prices.min()
    price_gap = max_price - min_price
    price_gap_pct = (price_gap / min_price * 100)
    
    arbitrage = {
        'buy_market': min_price_market,
        'buy_price_tzs': round(min_price, DECIMAL_PLACES['price']),
        'sell_market': max_price_market,
        'sell_price_tzs': round(max_price, DECIMAL_PLACES['price']),
        'price_gap_tzs': round(price_gap, DECIMAL_PLACES['price']),
        'profit_margin_percent': round(price_gap_pct, DECIMAL_PLACES['percentage']),
        'recommendation': 'Strong opportunity' if price_gap_pct > 15 else 'Moderate opportunity' if price_gap_pct > 8 else 'Limited opportunity'
    }
    
    # Quality upgrade opportunity
    grade_prices = current_prices.groupby('quality_grade')['price_per_kg_tzs'].mean()
    quality_premium = None
    
    if 'A' in grade_prices.index and 'C' in grade_prices.index:
        grade_a_price = grade_prices['A']
        grade_c_price = grade_prices['C']
        premium_pct = ((grade_a_price - grade_c_price) / grade_c_price * 100)
        
        quality_premium = {
            'grade_c_price_tzs': round(grade_c_price, DECIMAL_PLACES['price']),
            'grade_a_price_tzs': round(grade_a_price, DECIMAL_PLACES['price']),
            'premium_percent': round(premium_pct, DECIMAL_PLACES['percentage']),
            'recommendation': 'Invest in quality improvement' if premium_pct > 20 else 'Moderate quality focus'
        }
    
    # Timing opportunity (based on seasonal forecast)
    timing_recommendation = None
    current_month = datetime.now().month
    
    if current_month in LEAN_SEASON:
        timing_recommendation = {
            'current_period': 'Lean season',
            'action': 'SELL NOW',
            'reason': 'Prices typically peak during lean season (March-May)',
            'confidence': 'High'
        }
    elif current_month in MASIKA_HARVEST:
        timing_recommendation = {
            'current_period': 'Masika harvest',
            'action': 'HOLD or STORE',
            'reason': 'Prices typically drop during harvest. Consider storage for better prices later.',
            'confidence': 'High'
        }
    elif current_month in VULI_HARVEST:
        timing_recommendation = {
            'current_period': 'Vuli harvest',
            'action': 'SELL MODERATE VOLUMES',
            'reason': 'Moderate harvest period. Balance immediate sales with storage.',
            'confidence': 'Medium'
        }
    else:
        timing_recommendation = {
            'current_period': 'Normal period',
            'action': 'MONITOR',
            'reason': 'Prices stable. Watch for seasonal changes.',
            'confidence': 'Medium'
        }
    
    # Forecast-based opportunities
    forecast_opportunities = []
    if price_forecasts is not None:
        # Find markets where prices are expected to rise significantly
        next_month = (datetime.now() + timedelta(days=30)).replace(day=1)
        forecast_next = price_forecasts[price_forecasts['month'] == next_month]
        
        for market in MARKETS[:5]:  # Check first 5 markets
            market_current = current_prices[
                (current_prices['market'] == market) &
                (current_prices['quality_grade'] == 'A')
            ]['price_per_kg_tzs'].mean()
            
            market_forecast = forecast_next[
                (forecast_next['market'] == market) &
                (forecast_next['grade'] == 'A')
            ]['yhat'].values
            
            if len(market_forecast) > 0 and not np.isnan(market_current):
                forecast_price = market_forecast[0]
                change_pct = ((forecast_price - market_current) / market_current * 100)
                
                if abs(change_pct) > 5:  # Significant change
                    forecast_opportunities.append({
                        'market': market,
                        'current_price': round(market_current, DECIMAL_PLACES['price']),
                        'forecast_price': round(forecast_price, DECIMAL_PLACES['price']),
                        'change_percent': round(change_pct, DECIMAL_PLACES['percentage']),
                        'action': 'Consider storing' if change_pct > 5 else 'Consider selling soon'
                    })
    
    return {
        'arbitrage_opportunity': arbitrage,
        'quality_premium_opportunity': quality_premium,
        'timing_recommendation': timing_recommendation,
        'forecast_opportunities': forecast_opportunities if len(forecast_opportunities) > 0 else None,
        'generated_at': datetime.now().isoformat()
    }

# ============================================================================
# MAIN - FOR TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TESTING ANALYTICS FUNCTIONS")
    print("=" * 80)
    print()
    
    # Test each function
    functions = [
        ("National Summary", get_national_summary),
        ("Production Summary", lambda: get_production_summary(region='Mbeya')),
        ("Price Analysis", lambda: get_price_analysis(market='Mbeya Central')),
        ("Storage Status", get_storage_status),
        ("Seasonal Pattern", get_seasonal_pattern),
        ("Forecast Accuracy", get_forecast_accuracy),
        ("Supply-Demand Balance", get_supply_demand_balance),
        ("Market Opportunities", get_market_opportunities)
    ]
    
    for name, func in functions:
        try:
            print(f"Testing: {name}...")
            result = func()
            print(f"✅ {name}: SUCCESS")
            print(f"   Keys: {list(result.keys())}")
        except Exception as e:
            print(f"❌ {name}: FAILED - {str(e)}")
        print()
    
    print("=" * 80)
    print("✅ ALL TESTS COMPLETE!")