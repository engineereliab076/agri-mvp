import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load your synthetic production data
production = pd.read_csv('../data/synthetic/maize_production.csv')

# Convert timestamp
production['timestamp'] = pd.to_datetime(production['timestamp'])

print("=== DATA EXPLORATION ===")
print(f"Total records: {len(production)}")
print(f"Date range: {production['timestamp'].min()} to {production['timestamp'].max()}")
print(f"Unique regions: {production['region'].unique()}")
print(f"Seasons: {production['season'].unique()}")
print("\nSample data:")
print(production.head())

# ml/scripts/explore_data.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load your synthetic production data
production = pd.read_csv('../data/synthetic/maize_production.csv')

# Convert timestamp
production['timestamp'] = pd.to_datetime(production['timestamp'])

print("=== DATA EXPLORATION ===")
print(f"Total records: {len(production)}")
print(f"Date range: {production['timestamp'].min()} to {production['timestamp'].max()}")
print(f"Unique regions: {production['region'].unique()}")
print(f"Seasons: {production['season'].unique()}")
print("\nSample data:")
print(production.head())

# Plot production over time for a sample region
plt.figure(figsize=(12, 6))
sample_region = production['region'].unique()[0]  # First region
region_data = production[production['region'] == sample_region]

plt.plot(region_data['timestamp'], region_data['quantity_tons'], marker='o')
plt.title(f'Maize Production in {sample_region}')
plt.xlabel('Date')
plt.ylabel('Production (tons)')
plt.grid(True, alpha=0.3)
plt.show()