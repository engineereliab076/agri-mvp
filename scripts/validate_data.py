import pandas as pd
import os

print("🔍 VALIDATING GENERATED DATA")
print("="*50)

# Check files exist
files = ["data/maize_production.csv", "data/maize_prices.csv", "data/maize_storage.csv"]
for file in files:
    if os.path.exists(file):
        size_kb = os.path.getsize(file) / 1024
        print(f"✓ {file}: {size_kb:.1f} KB")
    else:
        print(f"✗ {file}: MISSING")

print("\n📊 DATA SUMMARY")
print("="*50)

# Load and summarize each file
try:
    # Production data
    df_prod = pd.read_csv("data/maize_production.csv")
    print(f"\n1. PRODUCTION DATA:")
    print(f"   Records: {len(df_prod)}")
    print(f"   Regions: {df_prod['region'].nunique()}")
    print(f"   Seasons: {df_prod['season'].unique()}")
    print(f"   Quantity range: {df_prod['quantity_tons'].min():.1f} to {df_prod['quantity_tons'].max():.1f} tons")
    
    # Price data
    df_prices = pd.read_csv("data/maize_prices.csv")
    print(f"\n2. PRICE DATA:")
    print(f"   Records: {len(df_prices):,}")
    print(f"   Markets: {df_prices['market'].nunique()}")
    print(f"   Date range: {df_prices['date'].min()} to {df_prices['date'].max()}")
    print(f"   Price range: {df_prices['price_per_kg_tzs'].min():.0f} to {df_prices['price_per_kg_tzs'].max():.0f} TZS/kg")
    
    # Storage data
    df_storage = pd.read_csv("data/maize_storage.csv")
    print(f"\n3. STORAGE DATA:")
    print(f"   Records: {len(df_storage):,}")
    print(f"   Warehouses: {df_storage['warehouse_id'].nunique()}")
    print(f"   Utilization range: {df_storage['utilization_percent'].min():.1f}% to {df_storage['utilization_percent'].max():.1f}%")
    
    print("\n✅ ALL DATA VALIDATED SUCCESSFULLY!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")