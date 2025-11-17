"""
Quick fix to re-extract temporal features properly
"""

import pandas as pd
import numpy as np

print("Loading cleaned data...")
df = pd.read_csv('data/processed/cleaned_water_quality_full.csv')
print(f"Loaded {len(df):,} records")

# Re-load the Excel file to get original DATE column
print("\nRe-loading original Excel file for DATE column...")
df_orig = pd.read_excel('wqdiscreteprobedata-8-23-2022.xlsx')

# Clean and match
invalid_codes = ['--', 'N/A', 'NA', '#N/A', 'NaN', '', ' ']
df_orig.replace(invalid_codes, np.nan, inplace=True)

# Convert DO and TEMP to numeric
df_orig['DO'] = pd.to_numeric(df_orig['DO'], errors='coerce')
df_orig['TEMP'] = pd.to_numeric(df_orig['TEMP'], errors='coerce')

# Convert numeric columns to match cleaning process
df_orig['PH'] = pd.to_numeric(df_orig['PH'], errors='coerce')

# Remove outliers (matching original script)
print("\nApplying outlier filters...")
df_orig = df_orig[(df_orig['TEMP'] >= 0) & (df_orig['TEMP'] <= 40)]
df_orig = df_orig[(df_orig['DO'] >= 0) & (df_orig['DO'] <= 20)]
# Add PH filter that was in original script
if 'PH' in df_orig.columns:
    df_orig = df_orig[(df_orig['PH'].isna()) | ((df_orig['PH'] >= 4) & (df_orig['PH'] <= 10))]

print(f"After filtering: {len(df_orig):,} records")
print(f"Cleaned data: {len(df):,} records")

# Parse DATE properly
print("\nParsing DATE column...")
df_orig['datetime'] = pd.to_datetime(df_orig['DATE'], format='mixed', errors='coerce')

# Extract temporal features
df_orig['year'] = df_orig['datetime'].dt.year
df_orig['month'] = df_orig['datetime'].dt.month
df_orig['day'] = df_orig['datetime'].dt.day
df_orig['day_of_year'] = df_orig['datetime'].dt.dayofyear

# Create season
def get_season(month):
    if pd.isna(month):
        return 'Unknown'
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Fall'

df_orig['season'] = df_orig['month'].apply(get_season)
df_orig['is_summer'] = df_orig['month'].isin([6, 7, 8]).astype(int)

print(f"\n✓ Parsed {df_orig['datetime'].notna().sum():,} dates successfully")
print(f"  Year range: {df_orig['year'].min():.0f} - {df_orig['year'].max():.0f}")
print(f"  Summer records: {df_orig['is_summer'].sum():,} ({df_orig['is_summer'].mean()*100:.1f}%)")

# Update the cleaned dataframe
df['datetime'] = df_orig['datetime'].values
df['year'] = df_orig['year'].values
df['month'] = df_orig['month'].values
df['day'] = df_orig['day'].values
df['day_of_year'] = df_orig['day_of_year'].values
df['season'] = df_orig['season'].values
df['is_summer'] = df_orig['is_summer'].values

# Recalculate risk features
df['DO_critical'] = (df['DO'] < 5).astype(int)
df['stress_combo'] = ((df['TEMP'] > 25) & (df['DO'] < 5)).astype(int)

# Recalculate risk_score
risk_cols = ['is_summer', 'DO_critical', 'stress_combo', 'flow_flag']
df['risk_score'] = df[risk_cols].sum(axis=1)

print(f"\n✓ Updated risk indicators:")
print(f"  is_summer: {df['is_summer'].sum():,} ({df['is_summer'].mean()*100:.1f}%)")
print(f"  DO_critical: {df['DO_critical'].sum():,} ({df['DO_critical'].mean()*100:.1f}%)")
print(f"  stress_combo: {df['stress_combo'].sum():,} ({df['stress_combo'].mean()*100:.1f}%)")
print(f"  risk_score: Mean = {df['risk_score'].mean():.2f}, Max = {df['risk_score'].max():.0f}")

# Save updated files
print("\n💾 Saving updated files...")
df.to_csv('data/processed/cleaned_water_quality_full.csv', index=False)
print("  ✓ data/processed/cleaned_water_quality_full.csv")

# Update dashboard export
export_cols = ['UNIQUE_ID', 'Latitude', 'Longitude', 'TEMP', 'DO', 'flow_flag', 
               'risk_score', 'season', 'year', 'month', 'is_summer', 'DO_critical', 'stress_combo']
df_export = df[[col for col in export_cols if col in df.columns]].copy()
df_export.to_csv('data/exports/ma_waterways_dashboard_data.csv', index=False)
print("  ✓ data/exports/ma_waterways_dashboard_data.csv")

print("\n✅ Fix complete!")
print(f"\nDataset stats:")
print(f"  Total records: {len(df):,}")
print(f"  Date range: {df['year'].min():.0f} - {df['year'].max():.0f}")
print(f"  Unique sites: {df['UNIQUE_ID'].nunique():,}")
print(f"  Summer records: {df['is_summer'].sum():,}")
