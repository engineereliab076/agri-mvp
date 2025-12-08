"""
Train All Price Prediction Models
==================================
Trains Prophet models for all market-grade combinations

Usage:
    cd ml/forecasting/prices
    python train_price_models.py
"""

import pandas as pd
import numpy as np
import pickle
import json
from prophet import Prophet
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Import configuration
from config import (
    PRICE_DATA_FILE, MODELS_DIR, FORECASTS_DIR, VISUALIZATIONS_DIR, LOGS_DIR,
    MARKETS, QUALITY_GRADES, PROPHET_PARAMS, TRAIN_TEST_SPLIT, FORECAST_DAYS,
    PLOT_DPI, COLORS, FIGURE_SIZE_GRID, CONSOLE_WIDTH,
    get_model_filename, get_forecast_filename, get_visualization_filename,
    MIN_DATA_POINTS, MAX_ACCEPTABLE_MAPE, PRICE_DECIMALS
)

# HELPER FUNCTIONS

def print_header(text: str):
    """Print formatted header"""
    print()
    print("=" * CONSOLE_WIDTH)
    print(text.center(CONSOLE_WIDTH))
    print("=" * CONSOLE_WIDTH)
    print()

def print_subheader(text: str):
    """Print formatted subheader"""
    print()
    print("-" * CONSOLE_WIDTH)
    print(text)
    print("-" * CONSOLE_WIDTH)

def load_price_data():
    """Load and validate price data"""
    print_subheader(" LOADING PRICE DATA")
    
    if not PRICE_DATA_FILE.exists():
        raise FileNotFoundError(f"Price data not found: {PRICE_DATA_FILE}")
    
    df = pd.read_csv(PRICE_DATA_FILE)
    df['date'] = pd.to_datetime(df['date'])
    
    print(f" Loaded {len(df):,} records")
    print(f" Date range: {df['date'].min()} to {df['date'].max()}")
    print(f" Markets: {df['market'].nunique()}")
    print(f" Quality grades: {sorted(df['quality_grade'].unique())}")
    
    return df

def prepare_market_grade_data(df, market, grade):
    """Filter and prepare data for specific market and grade"""
    data = df[
        (df['market'] == market) & 
        (df['quality_grade'] == grade)
    ].copy()
    
    # Sort by date
    data = data.sort_values('date').reset_index(drop=True)
    
    # Prepare for Prophet (needs 'ds' and 'y' columns)
    prophet_data = data[['date', 'price_per_kg_tzs']].copy()
    prophet_data.columns = ['ds', 'y']
    
    return prophet_data

def train_test_split_data(data, split_ratio=TRAIN_TEST_SPLIT):
    """Split data into train and test sets"""
    split_idx = int(len(data) * split_ratio)
    train = data[:split_idx].copy()
    test = data[split_idx:].copy()
    return train, test

def train_prophet_model(train_data):
    """Train Prophet model"""
    model = Prophet(**PROPHET_PARAMS)
    model.fit(train_data)
    return model

def evaluate_model(model, test_data):
    """Evaluate model on test data"""
    # Make predictions
    future = model.make_future_dataframe(periods=len(test_data), freq='D')
    forecast = model.predict(future)
    
    # Get test predictions
    test_predictions = forecast.tail(len(test_data))
    
    # Calculate metrics
    mae = mean_absolute_error(test_data['y'], test_predictions['yhat'])
    rmse = np.sqrt(mean_squared_error(test_data['y'], test_predictions['yhat']))
    mape = np.mean(np.abs((test_data['y'] - test_predictions['yhat']) / test_data['y'])) * 100
    r2 = r2_score(test_data['y'], test_predictions['yhat'])
    
    return {
        'mae': mae,
        'rmse': rmse,
        'mape': mape,
        'r2': r2
    }

def generate_forecast(model, periods=FORECAST_DAYS):
    """Generate future forecast"""
    future = model.make_future_dataframe(periods=periods, freq='D')
    forecast = model.predict(future)
    
    # Get only future predictions
    future_forecast = forecast.tail(periods).copy()
    
    # Resample to monthly for summary
    future_forecast['month'] = pd.to_datetime(future_forecast['ds']).dt.to_period('M')
    monthly_forecast = future_forecast.groupby('month')[['yhat', 'yhat_lower', 'yhat_upper']].mean()
    
    return future_forecast, monthly_forecast

def save_model(model, market, grade):
    """Save trained model"""
    filename = get_model_filename(market, grade)
    filepath = MODELS_DIR / filename
    
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)
    
    return filepath

def save_forecast(forecast_df, market, grade):
    """Save forecast to CSV"""
    filename = get_forecast_filename(market, grade)
    filepath = FORECASTS_DIR / filename
    
    # Select relevant columns
    forecast_output = forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
    forecast_output.columns = ['date', 'price_forecast', 'price_lower', 'price_upper']
    
    forecast_output.to_csv(filepath, index=False)
    
    return filepath

# MAIN TRAINING PIPELINE

def train_all_models():
    """Train all market-grade models"""
    
    print_header("🌾 MAIZE PRICE PREDICTION - TRAINING ALL MODELS")
    
    start_time = datetime.now()
    print(f" Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load data
    df = load_price_data()
    
    # Storage for results
    models_data = {}
    training_log = []
    all_forecasts = []
    
    # Get all combinations
    combinations = [
        (market, grade) 
        for market in MARKETS 
        for grade in QUALITY_GRADES
    ]
    
    print_header(f" TRAINING {len(combinations)} PROPHET MODELS")
    
    # Train each model
    for idx, (market, grade) in enumerate(combinations, 1):
        
        combo_name = f"{market} - Grade {grade}"
        
        print(f"\n [{idx}/{len(combinations)}] {combo_name}")
        print("-" * CONSOLE_WIDTH)
        
        try:
            # Prepare data
            data = prepare_market_grade_data(df, market, grade)
            
            if len(data) < MIN_DATA_POINTS:
                raise ValueError(f"Insufficient data: {len(data)} records (minimum: {MIN_DATA_POINTS})")
            
            print(f"    Records: {len(data)}")
            print(f"    Range: {data['ds'].min()} to {data['ds'].max()}")
            print(f"    Price: {data['y'].min():.2f} - {data['y'].max():.2f} TZS")
            
            # Train/test split
            train_data, test_data = train_test_split_data(data)
            print(f"    Training on {len(train_data)} records, testing on {len(test_data)}...")
            
            # Train model
            model = train_prophet_model(train_data)
            
            # Evaluate
            metrics = evaluate_model(model, test_data)
            print(f"    MAE: {metrics['mae']:.2f} TZS")
            print(f"    RMSE: {metrics['rmse']:.2f} TZS")
            print(f"    MAPE: {metrics['mape']:.2f}%")
            print(f"    R²: {metrics['r2']:.4f}")
            
            # Check if model is acceptable
            if metrics['mape'] > MAX_ACCEPTABLE_MAPE:
                print(f"  Warning: MAPE exceeds {MAX_ACCEPTABLE_MAPE}%")
            
            # Generate forecast
            future_forecast, monthly_forecast = generate_forecast(model)
            print(f" 6-month forecast: Avg {future_forecast['yhat'].mean():.2f} TZS")
            
            # Save model
            model_path = save_model(model, market, grade)
            print(f"  Model saved: {model_path.name}")
            
            # Save forecast
            forecast_path = save_forecast(future_forecast, market, grade)
            print(f"  Forecast saved: {forecast_path.name}")
            
            # Store results
            models_data[combo_name] = {
                'market': market,
                'grade': grade,
                'records': len(data),
                'train_size': len(train_data),
                'test_size': len(test_data),
                'metrics': metrics,
                'avg_historical': data['y'].mean(),
                'avg_forecast': future_forecast['yhat'].mean(),
                'model_file': model_path.name,
                'forecast_file': forecast_path.name
            }
            
            # Add to forecast collection
            monthly_forecast_reset = monthly_forecast.reset_index()
            monthly_forecast_reset['market'] = market
            monthly_forecast_reset['grade'] = grade
            all_forecasts.append(monthly_forecast_reset)
            
            # Training log
            training_log.append({
                'market': market,
                'grade': grade,
                'status': 'SUCCESS',
                'records': len(data),
                **metrics
            })
            
            print(f" Success!")
            
        except Exception as e:
            print(f"  Error: {str(e)}")
            training_log.append({
                'market': market,
                'grade': grade,
                'status': 'FAILED',
                'error': str(e)
            })
    
    # SAVE SUMMARY FILES

    print_header(" SAVING SUMMARY FILES")
    
    # 1. Forecast summary CSV
    all_forecasts_df = pd.concat(all_forecasts, ignore_index=True)
    summary_file = FORECASTS_DIR / 'forecast_summary_all_markets.csv'
    all_forecasts_df.to_csv(summary_file, index=False)
    print(f" Forecast summary: {summary_file.name}")
    
    # 2. Training log CSV
    log_df = pd.DataFrame(training_log)
    log_file = LOGS_DIR / f"price_training_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    log_df.to_csv(log_file, index=False)
    print(f" Training log: {log_file.name}")
    
    # 3. Metadata JSON
    metadata = {
        'created_at': datetime.now().isoformat(),
        'model_type': 'Prophet',
        'total_models': len(models_data),
        'markets': MARKETS,
        'quality_grades': QUALITY_GRADES,
        'forecast_days': FORECAST_DAYS,
        'prophet_params': PROPHET_PARAMS,
        'models': models_data
    }
    
    metadata_file = MODELS_DIR / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    print(f" Metadata: {metadata_file.name}")
    
    # ========================================================================
    # TRAINING SUMMARY
    # ========================================================================
    
    print_header(" TRAINING SUMMARY")
    
    successful = log_df[log_df['status'] == 'SUCCESS']
    failed = log_df[log_df['status'] == 'FAILED']
    
    print(f" Successful: {len(successful)}/{len(combinations)}")
    print(f" Failed: {len(failed)}/{len(combinations)}")
    
    if len(successful) > 0:
        print()
        print(" PERFORMANCE METRICS (Successful Models):")
        print(f"   Average MAE:  {successful['mae'].mean():.2f} TZS")
        print(f"   Average RMSE: {successful['rmse'].mean():.2f} TZS")
        print(f"   Average MAPE: {successful['mape'].mean():.2f}%")
        print(f"   Average R²:   {successful['r2'].mean():.4f}")
        
        print()
        print(" TOP 5 MODELS (Lowest MAE):")
        top5 = successful.nsmallest(5, 'mae')
        for idx, row in top5.iterrows():
            print(f"   {row['market']} Grade {row['grade']}: MAE={row['mae']:.2f} TZS, MAPE={row['mape']:.2f}%")
    

    # GENERATE VISUALIZATIONS
   
    
    print_header(" GENERATING VISUALIZATIONS")
    
    generate_visualizations(df, all_forecasts_df)
    

    # COMPLETION
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_header(" TRAINING COMPLETE!")
    
    print(f" Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f" End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    print()
    print(f" Models trained: {len(successful)}")
    print(f" Markets covered: {len(MARKETS)}")
    print(f" Quality grades: {len(QUALITY_GRADES)}")
    print(f" Forecast horizon: {FORECAST_DAYS} days (6 months)")
    print()
    print(f" Models saved in: {MODELS_DIR}")
    print(f" Forecasts saved in: {FORECASTS_DIR}")
    print(f" Visualizations saved in: {VISUALIZATIONS_DIR}")
    print()
    print(" Ready for production deployment!")
    print()

# VISUALIZATION FUNCTIONS

def generate_visualizations(df, forecasts_df):
    """Generate all visualizations"""
    
    try:
        # 1. All markets grid (Grade A only)
        print("    Creating all markets grid...")
        create_markets_grid(df, forecasts_df)
        print("    Markets grid complete")
        
        # 2. Grade comparison
        print("    Creating grade comparison...")
        create_grade_comparison(forecasts_df)
        print("    Grade comparison complete")
        
        # 3. Forecast heatmap
        print("    Creating forecast heatmap...")
        create_forecast_heatmap(forecasts_df)
        print("    Heatmap complete")
        
    except Exception as e:
        print(f"   ⚠️  Visualization error: {str(e)}")

def create_markets_grid(df, forecasts_df):
    """Create grid visualization of all markets (Grade A)"""
    
    fig, axes = plt.subplots(4, 3, figsize=FIGURE_SIZE_GRID)
    axes = axes.flatten()
    
    for idx, market in enumerate(MARKETS):
        ax = axes[idx]
        
        # Historical data
        market_data = df[
            (df['market'] == market) & 
            (df['quality_grade'] == 'A')
        ].sort_values('date')
        
        ax.plot(market_data['date'], market_data['price_per_kg_tzs'], 
                color=COLORS['train'], linewidth=1.5, alpha=0.7, label='Historical')
        
        # Forecast data
        forecast_data = forecasts_df[
            (forecasts_df['market'] == market) & 
            (forecasts_df['grade'] == 'A')
        ]
        
        if len(forecast_data) > 0:
            forecast_dates = pd.to_datetime(forecast_data['month'].astype(str))
            ax.plot(forecast_dates, forecast_data['yhat'], 
                    color=COLORS['forecast'], linewidth=2, linestyle='--', 
                    marker='o', label='Forecast')
        
        ax.set_title(f"{market}\nGrade A", fontsize=10, fontweight='bold')
        ax.set_xlabel('Date', fontsize=8)
        ax.set_ylabel('Price (TZS/kg)', fontsize=8)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=7)
    
    plt.suptitle('6-Month Price Forecast - All Markets (Grade A)', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    filename = get_visualization_filename('all_markets_grid_grade_a')
    plt.savefig(VISUALIZATIONS_DIR / filename, dpi=PLOT_DPI, bbox_inches='tight')
    plt.close()

def create_grade_comparison(forecasts_df):
    """Create grade comparison bar chart"""
    
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Calculate average forecast by grade across all markets
    grade_averages = []
    for grade in QUALITY_GRADES:
        grade_data = forecasts_df[forecasts_df['grade'] == grade]
        avg_forecast = grade_data['yhat'].mean()
        grade_averages.append(avg_forecast)
    
    # Get first 6 months
    months = forecasts_df['month'].unique()[:6]
    month_labels = [pd.Period(m).strftime('%b %Y') for m in months]
    
    # Prepare data for each grade
    grade_a_data = []
    grade_b_data = []
    grade_c_data = []
    
    for month in months:
        grade_a_data.append(
            forecasts_df[(forecasts_df['month'] == month) & (forecasts_df['grade'] == 'A')]['yhat'].mean()
        )
        grade_b_data.append(
            forecasts_df[(forecasts_df['month'] == month) & (forecasts_df['grade'] == 'B')]['yhat'].mean()
        )
        grade_c_data.append(
            forecasts_df[(forecasts_df['month'] == month) & (forecasts_df['grade'] == 'C')]['yhat'].mean()
        )
    
    # Plot
    x = np.arange(len(month_labels))
    width = 0.25
    
    ax.bar(x - width, grade_a_data, width, label='Grade A', color=COLORS['grade_a'])
    ax.bar(x, grade_b_data, width, label='Grade B', color=COLORS['grade_b'])
    ax.bar(x + width, grade_c_data, width, label='Grade C', color=COLORS['grade_c'])
    
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Price (TZS/kg)', fontsize=12, fontweight='bold')
    ax.set_title('Average Price Forecast by Quality Grade\n(All Markets Combined)', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(month_labels, rotation=45, ha='right')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    filename = get_visualization_filename('grade_comparison')
    plt.savefig(VISUALIZATIONS_DIR / filename, dpi=PLOT_DPI, bbox_inches='tight')
    plt.close()

def create_forecast_heatmap(forecasts_df):
    """Create heatmap of forecasts"""
    
    # Filter to Grade A for clarity
    grade_a = forecasts_df[forecasts_df['grade'] == 'A'].copy()
    
    # Pivot table
    pivot_data = grade_a.pivot_table(
        values='yhat',
        index='market',
        columns='month'
    )
    
    # Select first 6 months
    pivot_data = pivot_data.iloc[:, :6]
    
    # Rename columns
    pivot_data.columns = [pd.Period(col).strftime('%b %Y') for col in pivot_data.columns]
    
    # Plot
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='RdYlGn', 
                cbar_kws={'label': 'Price (TZS/kg)'}, ax=ax)
    
    ax.set_title('6-Month Price Forecast Heatmap - Grade A (All Markets)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Market', fontsize=12)
    
    plt.tight_layout()
    
    filename = get_visualization_filename('forecast_heatmap_grade_a')
    plt.savefig(VISUALIZATIONS_DIR / filename, dpi=PLOT_DPI, bbox_inches='tight')
    plt.close()

# MAIN EXECUTION


if __name__ == "__main__":
    train_all_models()