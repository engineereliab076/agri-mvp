"""
Data Validation Module
Validation rules for maize intelligence data

"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple

from config import (
    REGIONS, MARKETS, QUALITY_GRADES,
    PRICE_MIN_NORMAL, PRICE_MAX_NORMAL
)

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

class ValidationResult:
    """Store validation results"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
    
    def add_error(self, message: str):
        """Add error message"""
        self.errors.append(message)
    
    def add_warning(self, message: str):
        """Add warning message"""
        self.warnings.append(message)
    
    def add_info(self, message: str):
        """Add info message"""
        self.info.append(message)
    
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)"""
        return len(self.errors) == 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'valid': self.is_valid(),
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info
        }

# ============================================================================
# PRODUCTION DATA VALIDATION
# ============================================================================

def validate_production_data(df: pd.DataFrame) -> ValidationResult:
    """
    Validate maize production data
    
    Args:
        df: Production dataframe
    
    Returns:
        ValidationResult object
    """
    
    result = ValidationResult()
    
    # Check if dataframe is empty
    if len(df) == 0:
        result.add_error("Production data is empty")
        return result
    
    # Check required columns
    required_columns = ['date', 'region', 'quantity_tons']
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        result.add_error(f"Missing required columns: {missing_columns}")
        return result
    
    # Validate date column
    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        result.add_error(f"Invalid date format: {str(e)}")
        return result
    
    # Check for future dates
    future_dates = df[df['date'] > datetime.now()]
    if len(future_dates) > 0:
        result.add_warning(f"{len(future_dates)} records have future dates")
    
    # Validate region
    invalid_regions = df[~df['region'].isin(REGIONS)]
    if len(invalid_regions) > 0:
        unique_invalid = invalid_regions['region'].unique()
        result.add_error(f"Invalid regions found: {unique_invalid.tolist()}")
    
    # Validate quantity_tons
    if (df['quantity_tons'] < 0).any():
        negative_count = (df['quantity_tons'] < 0).sum()
        result.add_error(f"{negative_count} records have negative quantities")
    
    if (df['quantity_tons'] == 0).any():
        zero_count = (df['quantity_tons'] == 0).sum()
        result.add_warning(f"{zero_count} records have zero quantities")
    
    # Check for extreme values (outliers)
    q1 = df['quantity_tons'].quantile(0.25)
    q3 = df['quantity_tons'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 3 * iqr
    upper_bound = q3 + 3 * iqr
    
    outliers = df[(df['quantity_tons'] < lower_bound) | (df['quantity_tons'] > upper_bound)]
    if len(outliers) > 0:
        result.add_warning(f"{len(outliers)} potential outliers detected (extreme values)")
    
    # Check for missing values
    missing_summary = df.isnull().sum()
    for col, count in missing_summary.items():
        if count > 0:
            pct = (count / len(df)) * 100
            if pct > 20:
                result.add_error(f"Column '{col}' has {pct:.1f}% missing values")
            elif pct > 5:
                result.add_warning(f"Column '{col}' has {pct:.1f}% missing values")
    
    # Info messages
    result.add_info(f"Total records: {len(df)}")
    result.add_info(f"Date range: {df['date'].min()} to {df['date'].max()}")
    result.add_info(f"Regions: {df['region'].nunique()}")
    result.add_info(f"Total production: {df['quantity_tons'].sum():.2f} tons")
    
    return result

# ============================================================================
# PRICE DATA VALIDATION
# ============================================================================

def validate_price_data(df: pd.DataFrame) -> ValidationResult:
    """
    Validate maize price data
    
    Args:
        df: Price dataframe
    
    Returns:
        ValidationResult object
    """
    
    result = ValidationResult()
    
    # Check if dataframe is empty
    if len(df) == 0:
        result.add_error("Price data is empty")
        return result
    
    # Check required columns
    required_columns = ['date', 'market', 'price_per_kg_tzs', 'quality_grade']
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        result.add_error(f"Missing required columns: {missing_columns}")
        return result
    
    # Validate date column
    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        result.add_error(f"Invalid date format: {str(e)}")
        return result
    
    # Check for future dates
    future_dates = df[df['date'] > datetime.now()]
    if len(future_dates) > 0:
        result.add_warning(f"{len(future_dates)} records have future dates")
    
    # Validate market
    invalid_markets = df[~df['market'].isin(MARKETS)]
    if len(invalid_markets) > 0:
        unique_invalid = invalid_markets['market'].unique()
        result.add_error(f"Invalid markets found: {unique_invalid.tolist()}")
    
    # Validate quality_grade
    invalid_grades = df[~df['quality_grade'].isin(QUALITY_GRADES)]
    if len(invalid_grades) > 0:
        unique_invalid = invalid_grades['quality_grade'].unique()
        result.add_error(f"Invalid quality grades found: {unique_invalid.tolist()}")
    
    # Validate price_per_kg_tzs
    if (df['price_per_kg_tzs'] <= 0).any():
        negative_count = (df['price_per_kg_tzs'] <= 0).sum()
        result.add_error(f"{negative_count} records have non-positive prices")
    
    # Check for unrealistic prices
    too_low = df[df['price_per_kg_tzs'] < PRICE_MIN_NORMAL]
    if len(too_low) > 0:
        result.add_warning(f"{len(too_low)} records have unusually low prices (< {PRICE_MIN_NORMAL} TZS)")
    
    too_high = df[df['price_per_kg_tzs'] > PRICE_MAX_NORMAL]
    if len(too_high) > 0:
        result.add_warning(f"{len(too_high)} records have unusually high prices (> {PRICE_MAX_NORMAL} TZS)")
    
    # Check grade price hierarchy (Grade A should be >= Grade B >= Grade C)
    for market in df['market'].unique():
        market_data = df[df['market'] == market].groupby('quality_grade')['price_per_kg_tzs'].mean()
        
        if 'A' in market_data.index and 'B' in market_data.index:
            if market_data['A'] < market_data['B']:
                result.add_warning(f"{market}: Grade A price lower than Grade B (unusual)")
        
        if 'B' in market_data.index and 'C' in market_data.index:
            if market_data['B'] < market_data['C']:
                result.add_warning(f"{market}: Grade B price lower than Grade C (unusual)")
    
    # Check for missing values
    missing_summary = df.isnull().sum()
    for col, count in missing_summary.items():
        if count > 0:
            pct = (count / len(df)) * 100
            if pct > 20:
                result.add_error(f"Column '{col}' has {pct:.1f}% missing values")
            elif pct > 5:
                result.add_warning(f"Column '{col}' has {pct:.1f}% missing values")
    
    # Info messages
    result.add_info(f"Total records: {len(df)}")
    result.add_info(f"Date range: {df['date'].min()} to {df['date'].max()}")
    result.add_info(f"Markets: {df['market'].nunique()}")
    result.add_info(f"Average price: {df['price_per_kg_tzs'].mean():.2f} TZS")
    
    return result

# ============================================================================
# STORAGE DATA VALIDATION
# ============================================================================

def validate_storage_data(df: pd.DataFrame) -> ValidationResult:
    """
    Validate maize storage data
    
    Args:
        df: Storage dataframe
    
    Returns:
        ValidationResult object
    """
    
    result = ValidationResult()
    
    # Check if dataframe is empty
    if len(df) == 0:
        result.add_error("Storage data is empty")
        return result
    
    # Check required columns
    required_columns = ['date', 'warehouse_id', 'quantity_stored_tons', 'capacity_tons']
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        result.add_error(f"Missing required columns: {missing_columns}")
        return result
    
    # Validate date column
    try:
        df['date'] = pd.to_datetime(df['date'])
    except Exception as e:
        result.add_error(f"Invalid date format: {str(e)}")
        return result
    
    # Validate quantity_stored_tons
    if (df['quantity_stored_tons'] < 0).any():
        negative_count = (df['quantity_stored_tons'] < 0).sum()
        result.add_error(f"{negative_count} records have negative storage quantities")
    
    # Validate capacity_tons
    if (df['capacity_tons'] <= 0).any():
        invalid_count = (df['capacity_tons'] <= 0).sum()
        result.add_error(f"{invalid_count} records have non-positive capacity")
    
    # Check if stored quantity exceeds capacity
    overstocked = df[df['quantity_stored_tons'] > df['capacity_tons']]
    if len(overstocked) > 0:
        result.add_warning(f"{len(overstocked)} records exceed warehouse capacity (possible error or real overstocking)")
    
    # Calculate utilization and check for issues
    df['utilization'] = (df['quantity_stored_tons'] / df['capacity_tons'] * 100)
    
    critical_high = df[df['utilization'] > 95]
    if len(critical_high) > 0:
        result.add_warning(f"{len(critical_high)} records show critical high utilization (>95%)")
    
    # Check for warehouse_id consistency
    if 'warehouse_id' in df.columns:
        warehouse_count = df['warehouse_id'].nunique()
        result.add_info(f"Active warehouses: {warehouse_count}")
    
    # Check for missing values
    missing_summary = df.isnull().sum()
    for col, count in missing_summary.items():
        if count > 0:
            pct = (count / len(df)) * 100
            if pct > 20:
                result.add_error(f"Column '{col}' has {pct:.1f}% missing values")
            elif pct > 5:
                result.add_warning(f"Column '{col}' has {pct:.1f}% missing values")
    
    # Info messages
    result.add_info(f"Total records: {len(df)}")
    result.add_info(f"Date range: {df['date'].min()} to {df['date'].max()}")
    result.add_info(f"Total stored: {df['quantity_stored_tons'].sum():.2f} tons")
    result.add_info(f"Total capacity: {df['capacity_tons'].sum():.2f} tons")
    result.add_info(f"Avg utilization: {df['utilization'].mean():.1f}%")
    
    return result

# ============================================================================
# FORECAST DATA VALIDATION
# ============================================================================

def validate_forecast_data(df: pd.DataFrame, forecast_type: str = 'production') -> ValidationResult:
    """
    Validate forecast data
    
    Args:
        df: Forecast dataframe
        forecast_type: 'production' or 'price'
    
    Returns:
        ValidationResult object
    """
    
    result = ValidationResult()
    
    # Check if dataframe is empty
    if len(df) == 0:
        result.add_error("Forecast data is empty")
        return result
    
    # Check required columns based on type
    if forecast_type == 'production':
        required_columns = ['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'region']
    else:  # price
        required_columns = ['month', 'yhat', 'yhat_lower', 'yhat_upper', 'market', 'grade']
    
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        result.add_error(f"Missing required columns: {missing_columns}")
        return result
    
    # Validate predictions are positive
    if (df['yhat'] < 0).any():
        negative_count = (df['yhat'] < 0).sum()
        result.add_error(f"{negative_count} forecasts have negative values")
    
    # Validate confidence intervals
    invalid_ci = df[df['yhat_lower'] > df['yhat_upper']]
    if len(invalid_ci) > 0:
        result.add_error(f"{len(invalid_ci)} forecasts have invalid confidence intervals (lower > upper)")
    
    # Check if forecast is within confidence interval
    outside_ci = df[(df['yhat'] < df['yhat_lower']) | (df['yhat'] > df['yhat_upper'])]
    if len(outside_ci) > 0:
        result.add_warning(f"{len(outside_ci)} forecasts fall outside their own confidence intervals")
    
    # Info messages
    result.add_info(f"Total forecasts: {len(df)}")
    result.add_info(f"Forecast type: {forecast_type}")
    
    if forecast_type == 'production':
        result.add_info(f"Regions covered: {df['region'].nunique()}")
    else:
        result.add_info(f"Markets covered: {df['market'].nunique()}")
        result.add_info(f"Grades covered: {df['grade'].nunique()}")
    
    return result

# ============================================================================
# BATCH VALIDATION
# ============================================================================

def validate_all_data() -> Dict[str, ValidationResult]:
    """
    Validate all datasets
    
    Returns:
        dict: Validation results for each dataset
    """
    
    from config import PRODUCTION_DATA, PRICE_DATA, STORAGE_DATA
    
    results = {}
    
    # Validate production data
    try:
        prod_df = pd.read_csv(PRODUCTION_DATA)
        results['production'] = validate_production_data(prod_df)
    except Exception as e:
        result = ValidationResult()
        result.add_error(f"Failed to load production data: {str(e)}")
        results['production'] = result
    
    # Validate price data
    try:
        price_df = pd.read_csv(PRICE_DATA)
        results['price'] = validate_price_data(price_df)
    except Exception as e:
        result = ValidationResult()
        result.add_error(f"Failed to load price data: {str(e)}")
        results['price'] = result
    
    # Validate storage data
    try:
        storage_df = pd.read_csv(STORAGE_DATA)
        results['storage'] = validate_storage_data(storage_df)
    except Exception as e:
        result = ValidationResult()
        result.add_error(f"Failed to load storage data: {str(e)}")
        results['storage'] = result
    
    return results

# ============================================================================
# MAIN - FOR TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("DATA VALIDATION TESTS")
    print("=" * 80)
    print()
    
    # Run validation on all datasets
    validation_results = validate_all_data()
    
    for dataset_name, result in validation_results.items():
        print(f"\n{dataset_name.upper()} DATA VALIDATION:")
        print("-" * 80)
        
        result_dict = result.to_dict()
        
        print(f"Status: {'✅ VALID' if result_dict['valid'] else '❌ INVALID'}")
        print()
        
        if result_dict['errors']:
            print("ERRORS:")
            for error in result_dict['errors']:
                print(f"  ❌ {error}")
            print()
        
        if result_dict['warnings']:
            print("WARNINGS:")
            for warning in result_dict['warnings']:
                print(f"  ⚠️  {warning}")
            print()
        
        if result_dict['info']:
            print("INFO:")
            for info in result_dict['info']:
                print(f"  ℹ️  {info}")
        
        print()
    
    # Summary
    print("=" * 80)
    all_valid = all(r.is_valid() for r in validation_results.values())
    print(f"OVERALL STATUS: {'✅ ALL VALID' if all_valid else '❌ SOME VALIDATION FAILURES'}")
    print("=" * 80)