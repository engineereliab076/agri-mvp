"""
MAIZE PRODUCTION FORECASTING - ALL REGIONS
============================================================
Train Prophet models for all 11 Tanzanian regions with visualization and saving

Usage:
    python train_all_models.py

Output:
    - 11 model files (.pkl) in ./models/
    - 11 forecast files (.csv) in ./forecasts/
    - Summary report in ./forecasts/
    - Visualizations in ./visualizations/
    - Training log in ./logs/
"""

import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
import pickle
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import configuration
import config

print("=" * 80)
print("MAIZE PRODUCTION FORECASTING - ALL REGIONS")
print("=" * 80)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ============================================================================
# 1. LOAD DATA
# ============================================================================

print("📊 Loading production data...")

if not config.DATA_FILE.exists():
    print(f"❌ ERROR: Data file not found at {config.DATA_FILE}")
    print(f"   Please place 'maize_production.csv' in the 'data/' folder")
    exit(1)

df = pd.read_csv(config.DATA_FILE)
df['date'] = pd.to_datetime(df['date'])

print(f"   ✅ Loaded {len(df)} records")
print(f"   📅 Date range: {df['date'].min()} to {df['date'].max()}")

regions = sorted(df['region'].unique())
print(f"   🗺️  Regions: {regions}")
print()

print(f"🌾 Training models for {len(regions)} regions:")
for region in regions:
    print(f"   • {region}")
print()

# ============================================================================
# 2. HELPER FUNCTIONS
# ============================================================================

def prepare_region_data(df, region):
    """Prepare monthly data for Prophet"""
    region_df = df[df['region'] == region].copy()
    monthly = region_df.groupby('date')['quantity_tons'].sum().reset_index()
    monthly.columns = ['ds', 'y']
    return monthly


def apply_realistic_bounds(forecast_df, historical_df):
    """Apply realistic bounds: floor = 30% of min, cap = 2.5x max"""
    hist_min = historical_df['y'].min()
    hist_max = historical_df['y'].max()
    
    floor = hist_min * config.FLOOR_MULTIPLIER
    cap = hist_max * config.CAP_MULTIPLIER
    
    forecast_df['yhat'] = forecast_df['yhat'].clip(lower=floor, upper=cap)
    forecast_df['yhat_lower'] = forecast_df['yhat_lower'].clip(lower=floor, upper=cap)
    forecast_df['yhat_upper'] = forecast_df['yhat_upper'].clip(lower=floor, upper=cap)
    
    return forecast_df, floor, cap


def train_and_forecast(region_data, region_name):
    """Train Prophet model and generate forecast"""
    # Train model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        seasonality_mode='multiplicative',
        interval_width=config.CONFIDENCE_INTERVAL
    )
    model.fit(region_data)
    
    # Generate forecast
    future = model.make_future_dataframe(periods=config.FORECAST_DAYS, freq='D')
    forecast = model.predict(future)
    
    # Get only future predictions
    last_date = region_data['ds'].max()
    future_forecast = forecast[forecast['ds'] > last_date].copy()
    
    # Resample to monthly
    future_forecast.set_index('ds', inplace=True)
    monthly_forecast = future_forecast.resample('MS')[['yhat', 'yhat_lower', 'yhat_upper']].mean()
    monthly_forecast.reset_index(inplace=True)
    
    # Apply bounds
    monthly_forecast, floor, cap = apply_realistic_bounds(monthly_forecast, region_data)
    
    return model, monthly_forecast, floor, cap, forecast


# ============================================================================
# 3. TRAIN ALL MODELS
# ============================================================================

print("=" * 80)
print("🤖 TRAINING MODELS")
print("=" * 80)
print()

results = []
models_data = {}
training_log = []

for idx, region in enumerate(regions, 1):
    print(f"📍 [{idx}/{len(regions)}] {region}")
    
    try:
        start_time = datetime.now()
        
        # Prepare data
        region_data = prepare_region_data(df, region)
        print(f"   📊 Records: {len(region_data)}")
        
        # Train and forecast
        model, forecast_df, floor, cap, full_forecast = train_and_forecast(region_data, region)
        
        # Calculate metrics
        hist_avg = region_data['y'].mean()
        forecast_avg = forecast_df['yhat'].mean()
        growth_pct = ((forecast_avg - hist_avg) / hist_avg) * 100
        
        end_time = datetime.now()
        training_time = (end_time - start_time).total_seconds()
        
        print(f"   ✅ Trained in {training_time:.2f}s")
        print(f"   📈 Historical: {hist_avg:.0f} tons/month")
        print(f"   🔮 Forecast: {forecast_avg:.0f} tons/month ({growth_pct:+.1f}%)")
        print(f"   🔧 Bounds: [{floor:.0f}, {cap:.0f}]")
        print()
        
        # Store results
        results.append({
            'region': region,
            'historical_avg': hist_avg,
            'forecast_avg': forecast_avg,
            'growth_pct': growth_pct,
            'forecast_min': forecast_df['yhat'].min(),
            'forecast_max': forecast_df['yhat'].max(),
            'training_time_sec': training_time
        })
        
        models_data[region] = {
            'model': model,
            'historical': region_data,
            'forecast': forecast_df,
            'full_forecast': full_forecast,
            'floor': floor,
            'cap': cap
        }
        
        training_log.append({
            'region': region,
            'timestamp': datetime.now().isoformat(),
            'status': 'SUCCESS',
            'training_time_sec': training_time
        })
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}\n")
        training_log.append({
            'region': region,
            'timestamp': datetime.now().isoformat(),
            'status': 'FAILED',
            'error': str(e)
        })

print("=" * 80)
print(f"✅ TRAINING COMPLETE: {len(models_data)}/{len(regions)} models")
print("=" * 80)
print()

# ============================================================================
# 4. SAVE MODELS
# ============================================================================

print("💾 SAVING MODELS...")
print()

for region, data in models_data.items():
    region_slug = region.lower().replace(' ', '_')
    
    # Save model
    model_file = config.MODELS_DIR / f'production_model_{region_slug}.pkl'
    with open(model_file, 'wb') as f:
        pickle.dump(data['model'], f)
    print(f"   ✅ {model_file.name}")

print()

# ============================================================================
# 5. SAVE FORECASTS
# ============================================================================

print("📊 SAVING FORECASTS...")
print()

for region, data in models_data.items():
    region_slug = region.lower().replace(' ', '_')
    
    # Save forecast
    forecast_file = config.FORECASTS_DIR / f'forecast_{region_slug}.csv'
    data['forecast'].to_csv(forecast_file, index=False)
    print(f"   ✅ {forecast_file.name}")

print()

# ============================================================================
# 6. SAVE SUMMARY
# ============================================================================

print("📋 SAVING SUMMARY REPORT...")

summary_df = pd.DataFrame(results)
summary_df = summary_df.sort_values('historical_avg', ascending=False)
summary_file = config.FORECASTS_DIR / 'forecast_summary.csv'
summary_df.to_csv(summary_file, index=False)

print(f"   ✅ {summary_file.name}")
print()

# Display summary
print("=" * 80)
print("📊 FORECAST SUMMARY")
print("=" * 80)
print()
print(f"{'Region':<15} {'Historical':<12} {'Forecast':<12} {'Growth %':<10}")
print("-" * 80)
for _, row in summary_df.iterrows():
    print(f"{row['region']:<15} {row['historical_avg']:>8.0f} tons  "
          f"{row['forecast_avg']:>8.0f} tons  {row['growth_pct']:>6.1f}%")
print()

# ============================================================================
# 7. SAVE METADATA
# ============================================================================

print("📝 SAVING METADATA...")

metadata = {
    'created_at': datetime.now().isoformat(),
    'total_regions': len(regions),
    'models_trained': len(models_data),
    'forecast_horizon_months': config.FORECAST_MONTHS,
    'confidence_interval': config.CONFIDENCE_INTERVAL,
    'regions': []
}

for region, data in models_data.items():
    region_slug = region.lower().replace(' ', '_')
    metadata['regions'].append({
        'name': region,
        'model_file': f'production_model_{region_slug}.pkl',
        'forecast_file': f'forecast_{region_slug}.csv',
        'historical_avg': float(data['historical']['y'].mean()),
        'forecast_avg': float(data['forecast']['yhat'].mean()),
        'training_records': len(data['historical']),
        'floor': float(data['floor']),
        'cap': float(data['cap'])
    })

metadata_file = config.MODELS_DIR / 'metadata.json'
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"   ✅ {metadata_file.name}")
print()

# ============================================================================
# 8. SAVE TRAINING LOG
# ============================================================================

print("📋 SAVING TRAINING LOG...")

log_filename = f"training_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
log_file = config.LOGS_DIR / log_filename
with open(log_file, 'w') as f:
    json.dump(training_log, f, indent=2)

print(f"   ✅ {log_filename}")
print()

# ============================================================================
# 9. VISUALIZATIONS
# ============================================================================

print("=" * 80)
print("📊 CREATING VISUALIZATIONS")
print("=" * 80)
print()

# Plot 1: All Regions Grid
print("📈 Creating grid view...")
fig, axes = plt.subplots(config.GRID_ROWS, config.GRID_COLS, 
                         figsize=(20, 16))
axes = axes.flatten()

for idx, (region, data) in enumerate(models_data.items()):
    if idx < len(axes):
        ax = axes[idx]
        
        hist = data['historical']
        forecast = data['forecast']
        
        ax.plot(hist['ds'], hist['y'], 'o-', label='Historical', 
                color='#2E86AB', linewidth=2, markersize=6)
        ax.plot(forecast['ds'], forecast['yhat'], 's-', label='Forecast', 
                color='#A23B72', linewidth=2, markersize=6)
        ax.fill_between(forecast['ds'], forecast['yhat_lower'], 
                        forecast['yhat_upper'], alpha=0.2, color='#A23B72')
        ax.axvline(x=hist['ds'].max(), color='red', linestyle='--', alpha=0.5)
        
        ax.set_title(region, fontsize=12, fontweight='bold')
        ax.set_xlabel('Date', fontsize=9)
        ax.set_ylabel('Production (tons)', fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45, labelsize=8)

for idx in range(len(models_data), len(axes)):
    axes[idx].axis('off')

plt.suptitle('Tanzania Maize Production Forecasts - All Regions', 
             fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout()
plt.savefig(config.VISUALIZATIONS_DIR / 'all_regions_grid.png', 
            dpi=config.FIGURE_DPI, bbox_inches='tight')
plt.close()
print(f"   ✅ all_regions_grid.png")

# Plot 2: Top 5 Detailed
print("📈 Creating top 5 detailed view...")
top5_regions = summary_df.head(5)['region'].tolist()

fig, axes = plt.subplots(len(top5_regions), 1, 
                         figsize=(14, 4*len(top5_regions)))
if len(top5_regions) == 1:
    axes = [axes]

for idx, region in enumerate(top5_regions):
    ax = axes[idx]
    data = models_data[region]
    
    data['model'].plot(data['full_forecast'], ax=ax)
    ax.axvline(x=data['historical']['ds'].max(), color='red', 
               linestyle='--', linewidth=2, alpha=0.7)
    ax.set_title(f'{region} - Production Forecast', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(config.VISUALIZATIONS_DIR / 'top5_detailed.png', 
            dpi=config.FIGURE_DPI, bbox_inches='tight')
plt.close()
print(f"   ✅ top5_detailed.png")

# Plot 3: Growth Comparison
print("📈 Creating growth comparison...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

x = np.arange(len(summary_df))
width = 0.35

ax1.bar(x - width/2, summary_df['historical_avg'], width, 
        label='Historical', color='#2E86AB', alpha=0.8)
ax1.bar(x + width/2, summary_df['forecast_avg'], width,
        label='Forecast', color='#A23B72', alpha=0.8)
ax1.set_xlabel('Region', fontweight='bold')
ax1.set_ylabel('Production (tons/month)', fontweight='bold')
ax1.set_title('Historical vs Forecast', fontweight='bold', fontsize=12)
ax1.set_xticks(x)
ax1.set_xticklabels(summary_df['region'], rotation=45, ha='right')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

colors = ['#D32F2F' if g < 0 else '#388E3C' for g in summary_df['growth_pct']]
ax2.barh(summary_df['region'], summary_df['growth_pct'], color=colors, alpha=0.8)
ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
ax2.set_xlabel('Growth Rate (%)', fontweight='bold')
ax2.set_title('Growth Rate by Region', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3, axis='x')

plt.tight_layout()
plt.savefig(config.VISUALIZATIONS_DIR / 'growth_comparison.png', 
            dpi=config.FIGURE_DPI, bbox_inches='tight')
plt.close()
print(f"   ✅ growth_comparison.png")

# Plot 4: Individual Region Forecasts
print("📈 Creating individual region plots...")
for region, data in models_data.items():
    region_slug = region.lower().replace(' ', '_')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    data['model'].plot(data['full_forecast'], ax=ax)
    ax.axvline(x=data['historical']['ds'].max(), color='red', 
               linestyle='--', linewidth=2, alpha=0.7, label='Training Cutoff')
    ax.set_title(f'{region} - 6-Month Production Forecast', 
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(config.VISUALIZATIONS_DIR / f'forecast_{region_slug}.png', 
                dpi=config.FIGURE_DPI, bbox_inches='tight')
    plt.close()

print(f"   ✅ {len(models_data)} individual region plots")
print()

# ============================================================================
# 10. FINAL SUMMARY
# ============================================================================

print("=" * 80)
print("✅ ALL DONE!")
print("=" * 80)
print()
print(f"📦 DELIVERABLES:")
print(f"   • {len(models_data)} model files in: {config.MODELS_DIR}")
print(f"   • {len(models_data)} forecast files in: {config.FORECASTS_DIR}")
print(f"   • {len(models_data) + 3} visualizations in: {config.VISUALIZATIONS_DIR}")
print(f"   • 1 summary report in: {config.FORECASTS_DIR}")
print(f"   • 1 training log in: {config.LOGS_DIR}")
print()
print(f"🎯 TOP 3 PRODUCERS:")
for i, row in summary_df.head(3).iterrows():
    print(f"   {i+1}. {row['region']}: {row['historical_avg']:.0f} tons/month")
print()
print(f"⏱️  Total training time: {sum([r['training_time_sec'] for r in results]):.1f} seconds")
print()
print("🚀 Models ready for API integration!")
print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)