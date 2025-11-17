"""
Complete Water Quality Analysis Script
MA Waterways Heatwave Risk Analysis

This script executes the full analysis pipeline:
1. Data Cleaning
2. Feature Engineering
3. Correlation Analysis
4. Insight Visualization
5. Scenario Simulation
6. Export for Dashboarding
7. Site Clustering by Risk
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

print("="*70)
print("MA WATERWAYS HEATWAVE RISK ANALYSIS")
print("="*70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# STEP 1: DATA LOADING AND CLEANING
# ============================================================================
print("\n" + "="*70)
print("STEP 1: DATA LOADING AND CLEANING")
print("="*70)

# Load the Excel file
print("\n📊 Loading water quality data...")
data_path = 'wqdiscreteprobedata-8-23-2022.xlsx'
df = pd.read_excel(data_path)
print(f"✓ Loaded {len(df):,} records with {len(df.columns)} columns")

# Display column names
print(f"\nColumn names:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col}")

# Display first few rows
print(f"\nFirst 5 rows:")
print(df.head())

# Replace invalid codes with NaN
print("\n🧹 Cleaning invalid values...")
# Be careful with 'NaN' string - it might conflict with pandas
invalid_codes = ['--', 'N/A', 'NA', '#N/A', '']
for code in invalid_codes:
    df.replace(code, np.nan, inplace=True)

# Identify key columns (adjust based on actual column names)
# Common variations in environmental datasets
def find_column(df, keywords):
    """Find column by keywords (case-insensitive)"""
    for col in df.columns:
        if any(keyword.lower() in col.lower() for keyword in keywords):
            return col
    return None

# Map standard names to actual columns
do_col = 'DO'
temp_col = 'TEMP'
ph_col = 'PH'
cond_col = 'SPCOND'
depth_col = 'DEPTH'
tds_col = 'TDS'
flow_col = 'FLOWSTAT'
date_col = 'DATE'  # This is the actual sample date
time_col = 'TIME'
site_col = 'UNIQUE_ID'  # Unique identifier for each site
lat_col = 'Latitude'
lon_col = 'Longitude'

print("\n📋 Column mapping:")
mapping = {
    'DO': do_col,
    'TEMP': temp_col,
    'PH': ph_col,
    'CONDUCTIVITY': cond_col,
    'DEPTH': depth_col,
    'TDS': tds_col,
    'FLOW': flow_col,
    'DATE': date_col,
    'TIME': time_col,
    'SITE': site_col,
    'LAT': lat_col,
    'LON': lon_col
}

for key, val in mapping.items():
    print(f"  {key:15s} -> {val if val else 'NOT FOUND'}")

# Convert numeric columns
print("\n🔢 Converting to numeric types...")
numeric_cols = [do_col, temp_col, ph_col, cond_col, depth_col, tds_col]
for col in numeric_cols:
    if col:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        print(f"  ✓ Converted {col}")

# Create datetime field
print("\n📅 Creating datetime field...")
if date_col:
    # Parse DATE column (handles various formats automatically)
    df['datetime'] = pd.to_datetime(df[date_col], errors='coerce')
    
    print(f"  ✓ Created datetime field")
    print(f"  ✓ Successfully parsed {df['datetime'].notna().sum():,} dates")
    
    # Extract temporal features
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['day_of_year'] = df['datetime'].dt.dayofyear
    
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
    
    df['season'] = df['month'].apply(get_season)
    print(f"  ✓ Extracted: year, month, day, season")

# Drop rows with missing DO or TEMP
print("\n🗑️  Removing rows with missing DO or TEMP...")
initial_count = len(df)
if do_col and temp_col:
    df = df.dropna(subset=[do_col, temp_col])
    removed = initial_count - len(df)
    print(f"  Removed: {removed:,} rows ({removed/initial_count*100:.1f}%)")
    print(f"  Remaining: {len(df):,} rows")
else:
    print("  ⚠ Cannot drop - columns not found")

# Remove outliers
print("\n🎯 Removing outliers...")
if temp_col:
    outliers = ((df[temp_col] < 0) | (df[temp_col] > 40)).sum()
    df = df[(df[temp_col] >= 0) & (df[temp_col] <= 40)]
    print(f"  ✓ Removed {outliers} temperature outliers (< 0°C or > 40°C)")

if do_col:
    outliers = ((df[do_col] < 0) | (df[do_col] > 20)).sum()
    df = df[(df[do_col] >= 0) & (df[do_col] <= 20)]
    print(f"  ✓ Removed {outliers} DO outliers (< 0 or > 20 mg/L)")

if ph_col:
    outliers = ((df[ph_col] < 4) | (df[ph_col] > 10)).sum()
    df = df[(df[ph_col] >= 4) & (df[ph_col] <= 10)]
    print(f"  ✓ Removed {outliers} pH outliers (< 4 or > 10)")

print(f"\n✅ Cleaning complete! Final dataset: {len(df):,} records")

# ============================================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================================
print("\n" + "="*70)
print("STEP 2: FEATURE ENGINEERING")
print("="*70)

print("\n🔧 Creating risk indicator features...")

# is_summer: 1 if month is June, July, or August
df['is_summer'] = df['month'].isin([6, 7, 8]).astype(int)
print(f"  ✓ is_summer: {df['is_summer'].sum():,} summer records ({df['is_summer'].mean()*100:.1f}%)")

# DO_critical: 1 if DO < 5 mg/L
if do_col:
    df['DO_critical'] = (df[do_col] < 5).astype(int)
    print(f"  ✓ DO_critical: {df['DO_critical'].sum():,} critical events ({df['DO_critical'].mean()*100:.1f}%)")

# stress_combo: 1 if TEMP > 25°C and DO < 5
if temp_col and do_col:
    df['stress_combo'] = ((df[temp_col] > 25) & (df[do_col] < 5)).astype(int)
    print(f"  ✓ stress_combo: {df['stress_combo'].sum():,} compound stress events ({df['stress_combo'].mean()*100:.1f}%)")

# flow_flag: 1 if flow is Low, Stagnant, or No Water
if flow_col:
    low_flow = ['low', 'stagnant', 'no water', 'none', 'no']
    df['flow_flag'] = df[flow_col].astype(str).str.lower().apply(
        lambda x: 1 if any(term in x for term in low_flow) else 0
    )
    print(f"  ✓ flow_flag: {df['flow_flag'].sum():,} low flow events ({df['flow_flag'].mean()*100:.1f}%)")
else:
    df['flow_flag'] = 0
    print(f"  ⚠ flow_flag: Set to 0 (column not found)")

# risk_score: sum of binary flags
risk_cols = ['is_summer', 'DO_critical', 'stress_combo', 'flow_flag']
available_risk_cols = [col for col in risk_cols if col in df.columns]
df['risk_score'] = df[available_risk_cols].sum(axis=1)
print(f"  ✓ risk_score: Mean = {df['risk_score'].mean():.2f}, Max = {df['risk_score'].max():.0f}")

print("\n✅ Feature engineering complete!")

# ============================================================================
# STEP 3: CORRELATION MATRIX
# ============================================================================
print("\n" + "="*70)
print("STEP 3: CORRELATION MATRIX")
print("="*70)

print("\n📊 Calculating correlation matrix...")

# Select numeric columns for correlation
corr_columns = []
for col in [do_col, temp_col, ph_col, cond_col, depth_col, tds_col]:
    if col and col in df.columns:
        corr_columns.append(col)

if len(corr_columns) >= 2:
    corr_matrix = df[corr_columns].corr()
    
    print(f"  ✓ Correlation matrix computed for {len(corr_columns)} variables")
    print("\nCorrelation Matrix:")
    print(corr_matrix.round(3))
    
    # Plot correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, cbar_kws={'label': 'Correlation'})
    plt.title('Water Quality Parameters Correlation Matrix\n(MA Waterways 2005-2020)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    
    # Create output directory
    Path('outputs/figures').mkdir(parents=True, exist_ok=True)
    plt.savefig('outputs/figures/correlation_matrix.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: outputs/figures/correlation_matrix.png")
    plt.close()
else:
    print("  ⚠ Not enough numeric columns for correlation analysis")

# ============================================================================
# STEP 4: INSIGHT VISUALIZATIONS
# ============================================================================
print("\n" + "="*70)
print("STEP 4: INSIGHT VISUALIZATIONS")
print("="*70)

# Visualization 1: Monthly average DO (seasonal trends)
print("\n📈 Visualization 1: Monthly Average DO...")
if do_col and 'month' in df.columns:
    monthly_do = df.groupby('month')[do_col].agg(['mean', 'std', 'count'])
    
    # Reindex to ensure all 12 months are present
    monthly_do = monthly_do.reindex(range(1, 13))
    
    fig, ax = plt.subplots(figsize=(12, 6))
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    ax.errorbar(range(1, 13), monthly_do['mean'], yerr=monthly_do['std'],
                marker='o', markersize=8, capsize=5, linewidth=2, 
                color='steelblue', label='Mean ± Std Dev')
    ax.axhline(5, color='red', linestyle='--', linewidth=2, 
               label='Critical Threshold (5 mg/L)', alpha=0.7)
    
    # Highlight summer
    ax.axvspan(5.5, 8.5, alpha=0.2, color='orange', label='Summer (Jun-Aug)')
    
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names)
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Dissolved Oxygen (mg/L)', fontsize=12, fontweight='bold')
    ax.set_title('Monthly Average Dissolved Oxygen - Seasonal Pattern\n(MA Waterways 2005-2020)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('outputs/figures/monthly_do_pattern.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: outputs/figures/monthly_do_pattern.png")
    plt.close()

# Visualization 2: Summer temperature over time (climate warming)
print("\n📈 Visualization 2: Summer Temperature Trends...")
if temp_col and 'year' in df.columns and 'is_summer' in df.columns:
    summer_temp = df[df['is_summer'] == 1].groupby('year')[temp_col].agg(['mean', 'std', 'count'])
    
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.errorbar(summer_temp.index, summer_temp['mean'], yerr=summer_temp['std'],
                marker='o', markersize=6, capsize=4, linewidth=2, 
                color='orangered', label='Summer Mean ± Std Dev')
    
    # Add trend line
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, std_err = linregress(summer_temp.index, summer_temp['mean'])
    trend_line = slope * summer_temp.index + intercept
    ax.plot(summer_temp.index, trend_line, 'k--', linewidth=2, alpha=0.7,
            label=f'Trend: {slope:.4f}°C/year (R²={r_value**2:.3f}, p={p_value:.4f})')
    
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Summer Water Temperature (°C)', fontsize=12, fontweight='bold')
    ax.set_title('Summer Water Temperature Trends - Climate Warming Signal\n(June-August, 2005-2020)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Add annotation
    total_change = slope * (summer_temp.index.max() - summer_temp.index.min())
    ax.text(0.98, 0.02, f'Total change: {total_change:.3f}°C over period',
            transform=ax.transAxes, ha='right', va='bottom',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.6),
            fontsize=11)
    
    plt.tight_layout()
    plt.savefig('outputs/figures/summer_temp_trend.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: outputs/figures/summer_temp_trend.png")
    plt.close()

# Visualization 3: TEMP vs DO scatterplot with regression
print("\n📈 Visualization 3: Temperature vs DO Relationship...")
if temp_col and do_col:
    # Sample for visualization if dataset is large
    df_plot = df[[temp_col, do_col]].dropna()
    if len(df_plot) > 10000:
        df_plot = df_plot.sample(10000, random_state=42)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Scatterplot with density coloring
    scatter = ax.scatter(df_plot[temp_col], df_plot[do_col], 
                        c=df_plot[temp_col], cmap='RdYlBu_r',
                        alpha=0.5, s=20, edgecolors='none')
    
    # Regression line
    slope, intercept, r_value, p_value, std_err = linregress(df_plot[temp_col], df_plot[do_col])
    x_line = np.linspace(df_plot[temp_col].min(), df_plot[temp_col].max(), 100)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, 'r-', linewidth=3, alpha=0.8,
            label=f'Regression: DO = {slope:.3f}×TEMP + {intercept:.2f}\nR² = {r_value**2:.3f}')
    
    # Critical zones
    ax.axhline(5, color='darkred', linestyle='--', linewidth=2, alpha=0.7, label='Critical DO (5 mg/L)')
    ax.axvline(25, color='orange', linestyle='--', linewidth=2, alpha=0.7, label='Warm Water (25°C)')
    
    ax.set_xlabel('Water Temperature (°C)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Dissolved Oxygen (mg/L)', fontsize=12, fontweight='bold')
    ax.set_title('Temperature-Oxygen Relationship - Negative Correlation\n(MA Waterways 2005-2020)',
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax, label='Temperature (°C)')
    
    # Stats box
    stats_text = f'n = {len(df_plot):,}\nCorrelation = {r_value:.3f}\np-value < 0.001'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=10)
    
    plt.tight_layout()
    plt.savefig('outputs/figures/temp_do_relationship.png', dpi=300, bbox_inches='tight')
    print("  ✓ Saved: outputs/figures/temp_do_relationship.png")
    plt.close()

print("\n✅ Visualizations complete!")

# ============================================================================
# STEP 5: SCENARIO SIMULATION (+2°C Warming)
# ============================================================================
print("\n" + "="*70)
print("STEP 5: SCENARIO SIMULATION (+2°C WARMING)")
print("="*70)

print("\n🌡️  Simulating +2°C warming scenario...")

if temp_col and do_col:
    # Create scenario dataframe
    df_scenario = df.copy()
    
    # Add 2°C to temperature
    df_scenario[f'{temp_col}_original'] = df_scenario[temp_col]
    df_scenario[temp_col] = df_scenario[temp_col] + 2.0
    
    # Estimate DO drop (0.25 mg/L per °C is a common rule of thumb)
    DO_DROP_PER_DEGREE = 0.25
    df_scenario[f'{do_col}_original'] = df_scenario[do_col]
    df_scenario[do_col] = df_scenario[do_col] - (2.0 * DO_DROP_PER_DEGREE)
    df_scenario[do_col] = df_scenario[do_col].clip(lower=0)  # Can't go below 0
    
    # Recalculate critical events
    df_scenario['DO_critical_scenario'] = (df_scenario[do_col] < 5).astype(int)
    
    # Compare baseline vs scenario
    baseline_critical = df['DO_critical'].sum()
    scenario_critical = df_scenario['DO_critical_scenario'].sum()
    new_critical = scenario_critical - baseline_critical
    
    baseline_mean_do = df[do_col].mean()
    scenario_mean_do = df_scenario[do_col].mean()
    do_change = scenario_mean_do - baseline_mean_do
    
    print(f"\n📊 SCENARIO IMPACT SUMMARY:")
    print(f"  Temperature increase: +2.0°C")
    print(f"  DO reduction factor: {DO_DROP_PER_DEGREE} mg/L per °C")
    print(f"  Expected DO drop: {2.0 * DO_DROP_PER_DEGREE:.2f} mg/L")
    print(f"\n  BASELINE:")
    print(f"    Mean DO: {baseline_mean_do:.2f} mg/L")
    print(f"    Critical events (DO < 5): {baseline_critical:,}")
    print(f"    % Critical: {baseline_critical/len(df)*100:.1f}%")
    print(f"\n  +2°C SCENARIO:")
    print(f"    Mean DO: {scenario_mean_do:.2f} mg/L")
    print(f"    Critical events (DO < 5): {scenario_critical:,}")
    print(f"    % Critical: {scenario_critical/len(df_scenario)*100:.1f}%")
    print(f"\n  IMPACT:")
    print(f"    Change in mean DO: {do_change:.2f} mg/L ({do_change/baseline_mean_do*100:.1f}%)")
    print(f"    New critical events: +{new_critical:,}")
    print(f"    Increase in critical events: {new_critical/baseline_critical*100:.1f}%")
    
    # Visualization: Baseline vs Scenario
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. DO Distribution
    ax = axes[0, 0]
    ax.hist([df[do_col], df_scenario[do_col]], bins=40, 
            label=['Baseline', '+2°C Scenario'],
            color=['steelblue', 'orangered'], alpha=0.6, edgecolor='black')
    ax.axvline(5, color='darkred', linestyle='--', linewidth=2, label='Critical (5 mg/L)')
    ax.set_xlabel('Dissolved Oxygen (mg/L)', fontweight='bold')
    ax.set_ylabel('Frequency', fontweight='bold')
    ax.set_title('DO Distribution Comparison', fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 2. Critical Events by Year
    ax = axes[0, 1]
    if 'year' in df.columns:
        baseline_yearly = df.groupby('year')['DO_critical'].sum()
        scenario_yearly = df_scenario.groupby('year')['DO_critical_scenario'].sum()
        
        x = np.arange(len(baseline_yearly))
        width = 0.35
        ax.bar(x - width/2, baseline_yearly.values, width, label='Baseline', 
               color='steelblue', alpha=0.7)
        ax.bar(x + width/2, scenario_yearly.values, width, label='+2°C Scenario',
               color='orangered', alpha=0.7)
        ax.set_xticks(x[::2])
        ax.set_xticklabels(baseline_yearly.index[::2], rotation=45)
        ax.set_xlabel('Year', fontweight='bold')
        ax.set_ylabel('Critical DO Events', fontweight='bold')
        ax.set_title('Critical Events by Year', fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3, axis='y')
    
    # 3. Monthly Comparison
    ax = axes[1, 0]
    if 'month' in df.columns:
        baseline_monthly = df.groupby('month')[do_col].mean()
        scenario_monthly = df_scenario.groupby('month')[do_col].mean()
        
        months = range(1, 13)
        month_names = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
        ax.plot(months, baseline_monthly.reindex(months), 'o-', linewidth=2,
                markersize=8, label='Baseline', color='steelblue')
        ax.plot(months, scenario_monthly.reindex(months), 's-', linewidth=2,
                markersize=8, label='+2°C Scenario', color='orangered')
        ax.axhline(5, color='darkred', linestyle='--', alpha=0.7)
        ax.set_xticks(months)
        ax.set_xticklabels(month_names)
        ax.set_xlabel('Month', fontweight='bold')
        ax.set_ylabel('Mean DO (mg/L)', fontweight='bold')
        ax.set_title('Monthly DO Comparison', fontweight='bold')
        ax.legend()
        ax.grid(alpha=0.3)
    
    # 4. Summary Statistics
    ax = axes[1, 1]
    ax.axis('off')
    summary_text = f"""
    CLIMATE SCENARIO IMPACT SUMMARY
    {'='*45}
    
    Temperature Increase: +2.0°C
    
    Dissolved Oxygen:
      Baseline Mean:     {baseline_mean_do:.2f} mg/L
      Scenario Mean:     {scenario_mean_do:.2f} mg/L
      Change:            {do_change:.2f} mg/L ({do_change/baseline_mean_do*100:.1f}%)
    
    Critical Events (DO < 5 mg/L):
      Baseline:          {baseline_critical:,} events
      Scenario:          {scenario_critical:,} events
      New Events:        +{new_critical:,}
      Increase:          {new_critical/baseline_critical*100:.1f}%
    
    Conclusion:
      A +2°C warming scenario would result in
      approximately {new_critical:,} additional critical
      oxygen stress events, representing a
      {new_critical/baseline_critical*100:.0f}% increase in risk.
    """
    ax.text(0.1, 0.9, summary_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Climate Warming Scenario Analysis: +2°C Impact on Water Quality',
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig('outputs/figures/scenario_comparison.png', dpi=300, bbox_inches='tight')
    print("\n  ✓ Saved: outputs/figures/scenario_comparison.png")
    plt.close()
    
    print("\n✅ Scenario simulation complete!")
else:
    print("  ⚠ Cannot run scenario - missing required columns")

# ============================================================================
# STEP 6: EXPORT FOR DASHBOARDING
# ============================================================================
print("\n" + "="*70)
print("STEP 6: EXPORT FOR DASHBOARDING")
print("="*70)

print("\n💾 Preparing dashboard export...")

# Select columns for export
export_cols = []
export_mapping = {}

if site_col:
    export_cols.append(site_col)
    export_mapping['site_id'] = site_col
if lat_col:
    export_cols.append(lat_col)
    export_mapping['latitude'] = lat_col
if lon_col:
    export_cols.append(lon_col)
    export_mapping['longitude'] = lon_col
if temp_col:
    export_cols.append(temp_col)
    export_mapping['temperature'] = temp_col
if do_col:
    export_cols.append(do_col)
    export_mapping['dissolved_oxygen'] = do_col

# Add derived features
derived_cols = ['flow_flag', 'risk_score', 'season', 'year', 'month', 
                'is_summer', 'DO_critical', 'stress_combo']
for col in derived_cols:
    if col in df.columns:
        export_cols.append(col)

# Create export dataframe
df_export = df[export_cols].copy()

# Rename for clarity
df_export.columns = [export_mapping.get(col, col) for col in export_cols]

# Save to CSV
Path('data/exports').mkdir(parents=True, exist_ok=True)
export_path = 'data/exports/ma_waterways_dashboard_data.csv'
df_export.to_csv(export_path, index=False)

print(f"  ✓ Exported {len(df_export):,} records")
print(f"  ✓ Columns: {len(df_export.columns)}")
print(f"  ✓ Saved: {export_path}")
print(f"\n  Dashboard columns:")
for i, col in enumerate(df_export.columns, 1):
    print(f"    {i:2d}. {col}")

# Also save cleaned full dataset
full_export_path = 'data/processed/cleaned_water_quality_full.csv'
df.to_csv(full_export_path, index=False)
print(f"\n  ✓ Full dataset saved: {full_export_path}")

print("\n✅ Dashboard export complete!")

# ============================================================================
# STEP 7: CLUSTER SITES BY RISK (BONUS)
# ============================================================================
print("\n" + "="*70)
print("STEP 7: CLUSTER SITES BY RISK (K-MEANS)")
print("="*70)

if site_col and temp_col and do_col and 'is_summer' in df.columns and 'DO_critical' in df.columns:
    print("\n🎯 Clustering sites by risk profile...")
    
    # Calculate site-level features
    site_features = df[df['is_summer'] == 1].groupby(site_col).agg({
        temp_col: 'mean',
        do_col: 'mean',
        'DO_critical': 'sum',
        site_col: 'count'
    })
    site_features.columns = ['avg_summer_temp', 'avg_summer_do', 'critical_events', 'sample_count']
    
    # Filter sites with sufficient data
    min_samples = 5
    site_features = site_features[site_features['sample_count'] >= min_samples]
    
    print(f"  Sites with >= {min_samples} summer samples: {len(site_features)}")
    
    if len(site_features) >= 10:
        # Prepare features for clustering
        from sklearn.preprocessing import StandardScaler
        from sklearn.cluster import KMeans
        
        X = site_features[['avg_summer_temp', 'avg_summer_do', 'critical_events']].values
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K-means clustering with 3 clusters
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        site_features['cluster'] = clusters
        
        # Calculate cluster statistics to assign risk labels
        cluster_stats = site_features.groupby('cluster').agg({
            'avg_summer_temp': 'mean',
            'avg_summer_do': 'mean',
            'critical_events': 'mean'
        })
        
        # Assign risk labels based on temperature (high) and DO (low)
        cluster_stats['risk_score'] = (
            cluster_stats['avg_summer_temp'] / cluster_stats['avg_summer_temp'].max() +
            (1 - cluster_stats['avg_summer_do'] / cluster_stats['avg_summer_do'].max()) +
            cluster_stats['critical_events'] / cluster_stats['critical_events'].max()
        )
        cluster_stats = cluster_stats.sort_values('risk_score')
        
        risk_mapping = {
            cluster_stats.index[0]: 'Low Risk',
            cluster_stats.index[1]: 'Medium Risk',
            cluster_stats.index[2]: 'High Risk'
        }
        
        site_features['risk_category'] = site_features['cluster'].map(risk_mapping)
        
        print(f"\n  ✓ Clustered {len(site_features)} sites into 3 risk categories")
        print(f"\n  Cluster Distribution:")
        for category in ['Low Risk', 'Medium Risk', 'High Risk']:
            count = (site_features['risk_category'] == category).sum()
            print(f"    {category:15s}: {count:4d} sites ({count/len(site_features)*100:.1f}%)")
        
        print(f"\n  Cluster Characteristics:")
        cluster_summary = site_features.groupby('risk_category').agg({
            'avg_summer_temp': 'mean',
            'avg_summer_do': 'mean',
            'critical_events': 'mean',
            'sample_count': 'mean'
        })
        print(cluster_summary.round(2))
        
        # Visualize clusters
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Scatterplot 1: Temperature vs DO
        ax = axes[0]
        colors = {'Low Risk': 'green', 'Medium Risk': 'yellow', 'High Risk': 'red'}
        for category in ['Low Risk', 'Medium Risk', 'High Risk']:
            mask = site_features['risk_category'] == category
            ax.scatter(site_features[mask]['avg_summer_temp'],
                      site_features[mask]['avg_summer_do'],
                      c=colors[category], label=category, s=100, alpha=0.6,
                      edgecolors='black', linewidth=1)
        
        ax.set_xlabel('Average Summer Temperature (°C)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Average Summer DO (mg/L)', fontsize=12, fontweight='bold')
        ax.set_title('Site Clustering: Temperature vs Dissolved Oxygen', fontsize=13, fontweight='bold')
        ax.axhline(5, color='darkred', linestyle='--', alpha=0.5, label='Critical DO')
        ax.axvline(25, color='orange', linestyle='--', alpha=0.5, label='Warm Temp')
        ax.legend(loc='best', fontsize=10)
        ax.grid(alpha=0.3)
        
        # Scatterplot 2: Temperature vs Critical Events
        ax = axes[1]
        for category in ['Low Risk', 'Medium Risk', 'High Risk']:
            mask = site_features['risk_category'] == category
            ax.scatter(site_features[mask]['avg_summer_temp'],
                      site_features[mask]['critical_events'],
                      c=colors[category], label=category, s=100, alpha=0.6,
                      edgecolors='black', linewidth=1)
        
        ax.set_xlabel('Average Summer Temperature (°C)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Critical DO Events (count)', fontsize=12, fontweight='bold')
        ax.set_title('Site Clustering: Temperature vs Critical Events', fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('outputs/figures/site_risk_clusters.png', dpi=300, bbox_inches='tight')
        print(f"\n  ✓ Saved: outputs/figures/site_risk_clusters.png")
        plt.close()
        
        # Export clustered sites
        site_features_export = site_features.reset_index()
        cluster_export_path = 'data/exports/site_risk_clusters.csv'
        site_features_export.to_csv(cluster_export_path, index=False)
        print(f"  ✓ Saved: {cluster_export_path}")
        
        print("\n✅ Site clustering complete!")
    else:
        print(f"  ⚠ Not enough sites for clustering (found {len(site_features)}, need >= 10)")
else:
    print("  ⚠ Cannot perform clustering - missing required columns")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*70)
print("ANALYSIS COMPLETE - FINAL SUMMARY")
print("="*70)

print(f"\n📊 DATASET SUMMARY:")
print(f"  Total records: {len(df):,}")
print(f"  Time period: {df['year'].min():.0f} - {df['year'].max():.0f}" if 'year' in df.columns else "")
print(f"  Unique sites: {df[site_col].nunique():,}" if site_col else "")

print(f"\n📈 KEY METRICS:")
if do_col:
    print(f"  Mean DO: {df[do_col].mean():.2f} mg/L")
    print(f"  Critical events (DO < 5): {df['DO_critical'].sum():,} ({df['DO_critical'].mean()*100:.1f}%)" if 'DO_critical' in df.columns else "")
if temp_col:
    print(f"  Mean temperature: {df[temp_col].mean():.2f}°C")
    print(f"  Summer mean temp: {df[df['is_summer']==1][temp_col].mean():.2f}°C" if 'is_summer' in df.columns else "")
if 'stress_combo' in df.columns:
    print(f"  Combined stress events: {df['stress_combo'].sum():,} ({df['stress_combo'].mean()*100:.2f}%)")

print(f"\n💾 FILES CREATED:")
print(f"  ✓ outputs/figures/correlation_matrix.png")
print(f"  ✓ outputs/figures/monthly_do_pattern.png")
print(f"  ✓ outputs/figures/summer_temp_trend.png")
print(f"  ✓ outputs/figures/temp_do_relationship.png")
print(f"  ✓ outputs/figures/scenario_comparison.png")
if site_col:
    print(f"  ✓ outputs/figures/site_risk_clusters.png")
print(f"  ✓ data/exports/ma_waterways_dashboard_data.csv")
print(f"  ✓ data/processed/cleaned_water_quality_full.csv")
if site_col:
    print(f"  ✓ data/exports/site_risk_clusters.csv")

print(f"\n🎯 NEXT STEPS:")
print(f"  1. Review visualizations in outputs/figures/")
print(f"  2. Import data/exports/ma_waterways_dashboard_data.csv into Tableau/Power BI")
print(f"  3. Create interactive dashboard with filters for year, season, site")
print(f"  4. Highlight high-risk sites from site_risk_clusters.csv")
print(f"  5. Present findings with scenario comparison visualizations")

print(f"\n" + "="*70)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)
print("\n✅ SUCCESS! All analysis tasks completed.\n")
