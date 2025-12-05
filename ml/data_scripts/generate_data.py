import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

print(" MAIZE SYNTHETIC DATA GENERATOR")
print("=================================")

#  1. CONSTANTS FROM STRATEGY DOC =
REGIONS = {
    "High": ["Mbeya", "Iringa", "Ruvuma"],           # Surplus regions
    "Medium": ["Rukwa", "Morogoro", "Dodoma"],       # Medium production
    "Low": ["Arusha", "Kilimanjaro", "Dar es Salaam", "Mwanza", "Shinyanga"]  # Deficit regions
}

# All regions flattened
ALL_REGIONS = [region for categories in REGIONS.values() for region in categories]

# Markets (at least one per region, major cities have 2)
MARKETS = {
    "Dar es Salaam": ["Kariakoo", "Mwenge"],
    "Mbeya": ["Mbeya Central"],
    "Iringa": ["Iringa Central"],
    "Arusha": ["Arusha Central"],
    "Mwanza": ["Mwanza Central"],
    "Ruvuma": ["Songea Central"],
    "Rukwa": ["Sumbawanga Central"],
    "Morogoro": ["Morogoro Central"],
    "Dodoma": ["Dodoma Central"],
    "Kilimanjaro": ["Moshi Central"],
    "Shinyanga": ["Shinyanga Central"]
}

GRADES = ["A", "B", "C"]

# Warehouse IDs (2 per region)
WAREHOUSES = []
for region in ALL_REGIONS:
    prefix = region[:3].upper()
    WAREHOUSES.append(f"WH-{prefix}-001")
    WAREHOUSES.append(f"WH-{prefix}-002")

# ===== 2. HELPER FUNCTIONS =====
def get_region_category(region):
    """Return if region is High, Medium, or Low production"""
    for category, regions in REGIONS.items():
        if region in regions:
            return category
    return "Medium"

def monthly_price_modifier(month):
    """Monthly price modifiers from strategy doc"""
    modifiers = {
        1: 1.10,   # Jan +10%
        2: 1.15,   # Feb +15%
        3: 1.20,   # Mar +20%
        4: 1.20,   # Apr +20%
        5: 1.05,   # May +5%
        6: 0.90,   # Jun -10%
        7: 0.80,   # Jul -20%
        8: 0.85,   # Aug -15%
        9: 0.95,   # Sep -5%
        10: 1.00,  # Oct +0%
        11: 1.10,  # Nov +10%
        12: 1.05   # Dec +5%
    }
    return modifiers.get(month, 1.0)

def day_of_week_modifier(weekday):
    """Day of week price effects"""
    if weekday >= 5:  # Friday (4) or Saturday (5)
        return 1.02  # +2%
    elif weekday == 6:  # Sunday
        return 0.99   # -1%
    else:
        return 1.00   # Monday-Thursday normal

def grade_multiplier(grade):
    """Quality grade price multipliers"""
    multipliers = {"A": 1.20, "B": 1.00, "C": 0.85}
    return multipliers.get(grade, 1.0)

# ===== 3. GENERATE PRODUCTION DATA =====
print("\n1. Generating production data...")

production_data = []
production_id = 1

for year in [2023, 2024]:
    for region in ALL_REGIONS:
        region_category = get_region_category(region)
        
        # Regional modifier
        regional_mod = {"High": 1.5, "Medium": 1.0, "Low": 0.4}[region_category]
        
        # Masika season (harvest May-July)
        for harvest_month in [5, 6, 7]:
            date = datetime(year, harvest_month, 1)
            season = "Masika"
            base_yield = 500  # tons for Medium region, Masika
            
            # Calculate with seasonal modifier (Masika 1.8x, Vuli 1.0x)
            quantity = base_yield * regional_mod * 1.8 * random.uniform(0.9, 1.1)
            farm_area = quantity / random.uniform(3.5, 4.5)  # Yield 3.5-4.5 tons/hectare
            
            production_data.append({
                "id": production_id,
                "date": date.strftime("%Y-%m-%d"),
                "region": region,
                "season": season,
                "quantity_tons": round(quantity, 2),
                "farm_area_hectares": round(farm_area, 2)
            })
            production_id += 1
        
        # Vuli season (harvest Dec-Feb)
        for harvest_month in [12, 1, 2]:
            if harvest_month == 12:
                date = datetime(year, harvest_month, 1)
            else:  # Jan/Feb of next year
                date = datetime(year + 1, harvest_month, 1)
            
            season = "Vuli"
            base_yield = 500  # tons for Medium region, Vuli is smaller
            
            quantity = base_yield * regional_mod * 1.0 * random.uniform(0.9, 1.1)
            farm_area = quantity / random.uniform(3.5, 4.5)
            
            production_data.append({
                "id": production_id,
                "date": date.strftime("%Y-%m-%d"),
                "region": region,
                "season": season,
                "quantity_tons": round(quantity, 2),
                "farm_area_hectares": round(farm_area, 2)
            })
            production_id += 1

df_production = pd.DataFrame(production_data)
print(f"   ✓ Generated {len(df_production)} production records")

# ===== 4. GENERATE PRICE DATA =====
print("\n2. Generating daily price data (this may take a moment)...")

price_data = []
price_id = 1
current_date = START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

# Base price for Grade B in Medium region
BASE_PRICE = 1500  # TZS/kg

days = (END_DATE - START_DATE).days + 1
day_count = 0

while current_date <= END_DATE:
    day_count += 1
    if day_count % 100 == 0:
        print(f"   Processing day {day_count}/{days}...")
    
    month = current_date.month
    weekday = current_date.weekday()  # 0=Monday, 6=Sunday
    
    for region in ALL_REGIONS:
        if region in MARKETS:
            for market in MARKETS[region]:
                for grade in GRADES:
                    # Start with base price
                    price = BASE_PRICE
                    
                    # Apply monthly seasonal modifier
                    price *= monthly_price_modifier(month)
                    
                    # Apply regional premium (deficit regions +15%)
                    if get_region_category(region) == "Low":
                        price *= 1.15
                    
                    # Apply quality grade multiplier
                    price *= grade_multiplier(grade)
                    
                    # Apply day-of-week effect
                    price *= day_of_week_modifier(weekday)
                    
                    # Add ±2% daily random noise
                    price *= random.uniform(0.98, 1.02)
                    
                    # Ensure price is reasonable (800-2500 TZS/kg)
                    price = max(800, min(2500, price))
                    
                    price_data.append({
                        "id": price_id,
                        "date": current_date.strftime("%Y-%m-%d"),
                        "market": market,
                        "region": region,
                        "quality_grade": grade,
                        "price_per_kg_tzs": round(price, 2)
                    })
                    price_id += 1
    
    current_date += timedelta(days=1)

df_prices = pd.DataFrame(price_data)
print(f"   ✓ Generated {len(df_prices)} daily price records")

# ===== 5. GENERATE STORAGE DATA =====
print("\n3. Generating weekly storage data...")

storage_data = []
storage_id = 1

# Assign capacities to warehouses
warehouse_capacities = {}
for warehouse in WAREHOUSES:
    # Extract region from warehouse ID
    region_code = warehouse.split('-')[1]
    # Simple mapping back to region
    for region in ALL_REGIONS:
        if region[:3].upper() == region_code:
            warehouse_region = region
            break
    
    capacity = random.randint(500, 5000)
    warehouse_capacities[warehouse] = {
        "capacity": capacity,
        "region": warehouse_region,
        "current_stock": capacity * random.uniform(0.3, 0.7)  # Start at 30-70% full
    }

# Generate weekly data
current_date = START_DATE
while current_date <= END_DATE:
    # Only store Monday dates (weekly)
    if current_date.weekday() == 0:  # Monday
        month = current_date.month
        
        for warehouse, info in warehouse_capacities.items():
            region = info["region"]
            capacity = info["capacity"]
            current_stock = info["current_stock"]
            
            # Seasonal adjustment
            month = current_date.month
            if month in [8, 9, 3]:  # Post-harvest months
                # Increase stock
                weekly_change = random.uniform(0.05, 0.15)
            elif month in [4, 5, 11]:  # Lean season months
                # Decrease stock
                weekly_change = -random.uniform(0.03, 0.08)
            else:
                weekly_change = random.uniform(-0.02, 0.02)
            
            # Apply weekly change
            current_stock *= (1 + weekly_change)
            
            # Ensure stock is within bounds
            current_stock = max(0, min(capacity, current_stock))
            
            # Update warehouse info
            warehouse_capacities[warehouse]["current_stock"] = current_stock
            
            utilization = (current_stock / capacity) * 100
            
            storage_data.append({
                "id": storage_id,
                "date": current_date.strftime("%Y-%m-%d"),
                "warehouse_id": warehouse,
                "region": region,
                "quantity_stored_tons": round(current_stock, 2),
                "capacity_tons": capacity,
                "utilization_percent": round(utilization, 1)
            })
            storage_id += 1
    
    current_date += timedelta(days=1)

df_storage = pd.DataFrame(storage_data)
print(f"   ✓ Generated {len(df_storage)} weekly storage records")

# ===== 6. SAVE TO CSV =====
print("\n4. Saving to CSV files...")

# Create data directory if it doesn't exist
import os
os.makedirs("data", exist_ok=True)

# Save files
df_production.to_csv("data/maize_production.csv", index=False)
df_prices.to_csv("data/maize_prices.csv", index=False)
df_storage.to_csv("data/maize_storage.csv", index=False)

print("   ✓ Saved maize_production.csv")
print("   ✓ Saved maize_prices.csv")
print("   ✓ Saved maize_storage.csv")

# ===== 7. SUMMARY =====
print("\n" + "="*50)
print("📊 DATA GENERATION SUMMARY")
print("="*50)
print(f"Production records: {len(df_production):,}")
print(f"Price records:      {len(df_prices):,}")
print(f"Storage records:    {len(df_storage):,}")
print(f"Total records:      {len(df_production)+len(df_prices)+len(df_storage):,}")
print("\n Date range: 2023-01-01 to 2024-12-31")
print("📍 Regions covered: " + ", ".join(ALL_REGIONS))
print("\n✅ Synthetic maize dataset generation COMPLETE!")
print("="*50)