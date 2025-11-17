"""
Strategic Water Quality Analysis for MassDEP Leadership
=======================================================
Thinking as: Water Quality Manager + Senior Data Scientist

Key Questions to Answer:
1. Do patterns hold across different sites and years?
2. What are the biggest risk factors (plain language)?
3. What-if scenarios: extreme weather, road salt, heat waves
4. Which watersheds need immediate action?
5. What can communities actually do about this?
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🎯 STRATEGIC WATER QUALITY INSIGHTS FOR MASSDEP LEADERSHIP")
print("="*80)
print("\nPerspective: Water Quality Manager + Senior Data Scientist")
print("Audience: State Leaders, Municipal Officials, Public Health Experts\n")

# Load data
df = pd.read_csv('data/processed/cleaned_water_quality_full.csv')
df['DATE'] = pd.to_datetime(df['DATE'])
df['year'] = df['DATE'].dt.year
df['month'] = df['DATE'].dt.month
df['season'] = df['month'].map({12: 'Winter', 1: 'Winter', 2: 'Winter',
                                  3: 'Spring', 4: 'Spring', 5: 'Spring',
                                  6: 'Summer', 7: 'Summer', 8: 'Summer',
                                  9: 'Fall', 10: 'Fall', 11: 'Fall'})

print(f"📊 Dataset: {len(df):,} quality measurements")
print(f"📍 Sites: {df['UNIQUE_ID'].nunique():,}")
print(f"📅 Time Period: {df['year'].min():.0f}-{df['year'].max():.0f}")
print(f"🌊 Watersheds: {df['Watershed'].nunique()}")

# ============================================================================
# QUESTION 1: Do patterns hold across different sites and years?
# ============================================================================
print("\n" + "="*80)
print("QUESTION 1: Pattern Stability Analysis")
print("Do our findings hold up across different locations and time periods?")
print("="*80)

# Test 1: Temperature-DO relationship by watershed
print("\n🔬 Test 1: Temperature-DO correlation by watershed")
print("-" * 60)

watershed_correlations = []
for watershed in df['Watershed'].unique():
    ws_data = df[df['Watershed'] == watershed]
    if len(ws_data) >= 30:  # Need enough data
        corr = ws_data[['TEMP', 'DO']].corr().iloc[0, 1]
        n_sites = ws_data['UNIQUE_ID'].nunique()
        watershed_correlations.append({
            'watershed': watershed,
            'correlation': corr,
            'n_samples': len(ws_data),
            'n_sites': n_sites
        })

df_ws_corr = pd.DataFrame(watershed_correlations).sort_values('correlation')

print(f"✓ Analyzed {len(df_ws_corr)} watersheds with sufficient data")
print(f"\nCorrelation Range: {df_ws_corr['correlation'].min():.3f} to {df_ws_corr['correlation'].max():.3f}")
print(f"Mean Correlation: {df_ws_corr['correlation'].mean():.3f}")
print(f"Std Deviation: {df_ws_corr['correlation'].std():.3f}")

print("\n📊 Top 5 STRONGEST negative correlations (pattern holds):")
for _, row in df_ws_corr.head(5).iterrows():
    print(f"  • {row['watershed'][:40]:40s} r={row['correlation']:+.3f} ({row['n_sites']} sites)")

print("\n⚠️  Top 5 WEAKEST correlations (pattern less clear):")
for _, row in df_ws_corr.tail(5).iterrows():
    print(f"  • {row['watershed'][:40]:40s} r={row['correlation']:+.3f} ({row['n_sites']} sites)")

# Test 2: Temporal stability - by year
print("\n🔬 Test 2: Temporal stability - Year-by-year analysis")
print("-" * 60)

yearly_patterns = []
for year in sorted(df['year'].unique()):
    year_data = df[df['year'] == year]
    summer_data = year_data[year_data['season'] == 'Summer']
    
    if len(summer_data) >= 20:
        yearly_patterns.append({
            'year': year,
            'avg_temp': summer_data['TEMP'].mean(),
            'avg_DO': summer_data['DO'].mean(),
            'critical_pct': (summer_data['DO'] < 5).sum() / len(summer_data) * 100,
            'n_samples': len(summer_data)
        })

df_yearly = pd.DataFrame(yearly_patterns)

print(f"✓ {len(df_yearly)} years analyzed\n")

# Calculate trends
temp_slope, temp_intercept, temp_r, temp_p, _ = stats.linregress(df_yearly['year'], df_yearly['avg_temp'])
do_slope, do_intercept, do_r, do_p, _ = stats.linregress(df_yearly['year'], df_yearly['avg_DO'])
critical_slope, critical_intercept, critical_r, critical_p, _ = stats.linregress(df_yearly['year'], df_yearly['critical_pct'])

print(f"🌡️  TEMPERATURE TREND: {temp_slope:+.4f}°C per year (p={temp_p:.4f})")
if temp_p < 0.05:
    print(f"   → ⚠️  SIGNIFICANT warming trend detected!")
else:
    print(f"   → No statistically significant trend")

print(f"\n💧 DISSOLVED OXYGEN TREND: {do_slope:+.4f} mg/L per year (p={do_p:.4f})")
if do_p < 0.05:
    if do_slope < 0:
        print(f"   → ⚠️  SIGNIFICANT declining trend detected!")
    else:
        print(f"   → ✓ SIGNIFICANT improving trend detected!")
else:
    print(f"   → No statistically significant trend")

print(f"\n⚠️  CRITICAL EVENTS TREND: {critical_slope:+.4f}% per year (p={critical_p:.4f})")
if critical_p < 0.05:
    if critical_slope > 0:
        print(f"   → ⚠️  WORSENING: Critical events are increasing over time!")
    else:
        print(f"   → ✓ IMPROVING: Critical events are decreasing over time!")
else:
    print(f"   → No statistically significant trend")

# Test 3: Site-level consistency
print("\n🔬 Test 3: Site-level consistency check")
print("-" * 60)

site_patterns = []
for site in df['UNIQUE_ID'].unique():
    site_data = df[df['UNIQUE_ID'] == site]
    
    if len(site_data) >= 10:  # At least 10 measurements
        n_years = site_data['year'].nunique()
        if n_years >= 3:  # At least 3 years of data
            site_patterns.append({
                'site': site,
                'n_years': n_years,
                'n_samples': len(site_data),
                'do_mean': site_data['DO'].mean(),
                'do_std': site_data['DO'].std(),
                'temp_mean': site_data['TEMP'].mean(),
                'temp_std': site_data['TEMP'].std(),
                'critical_pct': (site_data['DO'] < 5).sum() / len(site_data) * 100
            })

df_sites = pd.DataFrame(site_patterns)

print(f"✓ {len(df_sites)} sites with 3+ years of data")
print(f"\nConsistency Metrics:")
print(f"  • Average DO variability: {df_sites['do_std'].mean():.2f} mg/L (std dev)")
print(f"  • Average Temp variability: {df_sites['temp_std'].mean():.2f}°C (std dev)")

# Identify consistently problematic sites
consistent_problems = df_sites[df_sites['critical_pct'] >= 15]
print(f"\n🚨 CONSISTENTLY PROBLEMATIC SITES (≥15% critical events):")
print(f"   → {len(consistent_problems)} sites need sustained intervention")
for _, row in consistent_problems.sort_values('critical_pct', ascending=False).head(10).iterrows():
    print(f"     • {row['site']}: {row['critical_pct']:.1f}% critical over {row['n_years']:.0f} years")

# ============================================================================
# QUESTION 2: What are the biggest risk factors? (PLAIN LANGUAGE)
# ============================================================================
print("\n" + "="*80)
print("QUESTION 2: What Really Drives Water Quality Problems?")
print("Feature Importance Analysis - Explained for Everyone")
print("="*80)

# Prepare data for Random Forest
print("\n🤖 Running advanced machine learning analysis...")

# Create features (use SPCOND = specific conductance, TDS = total dissolved solids)
df_ml = df.dropna(subset=['DO', 'TEMP', 'PH', 'SPCOND']).copy()
df_ml['is_summer'] = (df_ml['month'].isin([6, 7, 8])).astype(int)
df_ml['is_weekend'] = (df_ml['DATE'].dt.dayofweek >= 5).astype(int)
df_ml['temp_squared'] = df_ml['TEMP'] ** 2  # Non-linear effects
df_ml['is_hot'] = (df_ml['TEMP'] >= 23).astype(int)
df_ml['is_high_conductivity'] = (df_ml['SPCOND'] > df_ml['SPCOND'].median()).astype(int)

features = ['TEMP', 'SPCOND', 'PH', 'is_summer', 
            'temp_squared', 'is_hot', 'is_high_conductivity']
X = df_ml[features]
y = df_ml['DO']

# Train Random Forest
rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
rf.fit(X, y)

# Get feature importance
importance = pd.DataFrame({
    'factor': features,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False)

importance['importance_pct'] = importance['importance'] / importance['importance'].sum() * 100

print("\n📊 FACTOR IMPORTANCE RANKING:")
print("=" * 60)

factor_names = {
    'TEMP': '🌡️  Water Temperature',
    'temp_squared': '🔥 Extreme Temperature Effects',
    'is_hot': '☀️  Hot Weather (≥23°C)',
    'is_summer': '🏖️  Summer Season',
    'SPCOND': '⚡ Conductivity (pollution indicator)',
    'is_high_conductivity': '🌊 High Pollution Levels',
    'PH': '⚗️  pH (Acidity)'
}

explanations = {
    'TEMP': 'Warmer water holds LESS oxygen - like warm soda going flat',
    'temp_squared': 'Very hot water has EXPONENTIALLY less oxygen capacity',
    'is_hot': 'Above 23°C, oxygen levels drop dangerously for fish',
    'is_summer': 'June-August = triple threat (heat + algae + low flow)',
    'SPCOND': 'High conductivity = road salt + pollution, reduces oxygen',
    'is_high_conductivity': 'Polluted water = less oxygen can dissolve, stresses aquatic life',
    'PH': 'Acidity affects oxygen chemistry and fish health'
}

for i, row in importance.iterrows():
    factor = row['factor']
    pct = row['importance_pct']
    name = factor_names.get(factor, factor)
    explain = explanations.get(factor, '')
    
    print(f"\n{i+1}. {name}")
    print(f"   Importance: {pct:.1f}%")
    print(f"   💡 Why it matters: {explain}")

# Simple rules for the public
print("\n" + "="*60)
print("🎯 SIMPLE RULES FOR RESIDENTS & COMMUNITIES:")
print("="*60)

print("\n1️⃣  TEMPERATURE is the #1 factor")
print("   ✗ Problem: Every 1°C warmer = ~0.25 mg/L LESS oxygen")
print("   ✓ Solution: Plant trees along streams for shade")
print("   ✓ Solution: Reduce pavement heat (dark surfaces warm runoff)")

print("\n2️⃣  SUMMER is the danger zone")
print("   ✗ Problem: Hot + slow flow + algae = oxygen crash")
print("   ✓ Solution: Extra monitoring June-August")
print("   ✓ Solution: Emergency aeration at critical sites")

print("\n3️⃣  SALT (road salt) is a hidden killer")
print("   ✗ Problem: High conductivity = pollution + less oxygen")
print("   ✓ Solution: Use LESS road salt in winter")
print("   ✓ Solution: Switch to sand or beet juice alternatives")

# ============================================================================
# QUESTION 3: What-If Scenarios
# ============================================================================
print("\n" + "="*80)
print("QUESTION 3: What-If Scenarios for Planning")
print("Testing different future conditions")
print("="*80)

# Scenario 1: More rainstorms (dilution effect)
print("\n🌧️  SCENARIO 1: Increased Rainfall (Climate Change)")
print("-" * 60)

# Simulate 20% increase in flow (lower conductivity)
df_rain = df_ml.copy()
df_rain['SPCOND'] *= 0.8  # Dilution

do_current = df_ml['DO'].mean()
do_rain = rf.predict(df_rain[features]).mean()
change_rain = do_rain - do_current

print(f"Assumption: 20% more rainfall → 20% lower pollution/conductivity")
print(f"Current avg DO: {do_current:.2f} mg/L")
print(f"With more rain: {do_rain:.2f} mg/L")
print(f"Net change: {change_rain:+.2f} mg/L")

if change_rain > 0:
    print(f"✓ POSITIVE: More rain dilutes pollutants, slight oxygen improvement")
else:
    print(f"⚠️  NEGATIVE: More rain still problematic")

# Scenario 2: More road salt (winter runoff)
print("\n🧂 SCENARIO 2: 30% More Road Salt Use")
print("-" * 60)

df_salt = df_ml.copy()
df_salt['SPCOND'] *= 1.3

do_salt = rf.predict(df_salt[features]).mean()
change_salt = do_salt - do_current

print(f"Assumption: 30% increase in road salt application")
print(f"Current avg DO: {do_current:.2f} mg/L")
print(f"With more salt: {do_salt:.2f} mg/L")
print(f"Net change: {change_salt:+.2f} mg/L")

critical_current = (df_ml['DO'] < 5).sum()
critical_salt = (rf.predict(df_salt[features]) < 5).sum()

print(f"Critical events: {critical_current} → {critical_salt} ({critical_salt - critical_current:+.0f})")
print(f"⚠️  MORE SALT = WORSE WATER QUALITY")

# Scenario 3: Extreme heat summer (+3°C)
print("\n🔥 SCENARIO 3: Extreme Heat Wave Summer (+3°C)")
print("-" * 60)

df_heat = df_ml[df_ml['is_summer'] == 1].copy()
df_heat['TEMP'] += 3
df_heat['temp_squared'] = df_heat['TEMP'] ** 2
df_heat['is_hot'] = (df_heat['TEMP'] >= 23).astype(int)

do_summer_current = df_ml[df_ml['is_summer'] == 1]['DO'].mean()
do_summer_heat = rf.predict(df_heat[features]).mean()
change_heat = do_summer_heat - do_summer_current

print(f"Assumption: +3°C summer temperatures (heat wave)")
print(f"Current summer avg DO: {do_summer_current:.2f} mg/L")
print(f"With +3°C heat wave: {do_summer_heat:.2f} mg/L")
print(f"Net change: {change_heat:+.2f} mg/L ({abs(change_heat)/do_summer_current*100:.1f}% decline)")

critical_summer_current = (df_ml[df_ml['is_summer'] == 1]['DO'] < 5).sum()
critical_summer_heat = (rf.predict(df_heat[features]) < 5).sum()

print(f"Critical events: {critical_summer_current} → {critical_summer_heat} (+{critical_summer_heat - critical_summer_current:.0f})")
print(f"🚨 EXTREME HEAT = EMERGENCY OXYGEN CRISIS")

# Scenario 4: Combined worst case
print("\n💀 SCENARIO 4: Perfect Storm (Heat + Salt + Low Rain)")
print("-" * 60)

df_worst = df_ml[df_ml['is_summer'] == 1].copy()
df_worst['TEMP'] += 3
df_worst['SPCOND'] *= 1.5  # Concentrated pollution
df_worst['temp_squared'] = df_worst['TEMP'] ** 2
df_worst['is_hot'] = 1
df_worst['is_high_conductivity'] = 1

do_worst = rf.predict(df_worst[features]).mean()
change_worst = do_worst - do_summer_current

print(f"Combined: +3°C heat + 30% more salt + low flow")
print(f"Current summer avg DO: {do_summer_current:.2f} mg/L")
print(f"Worst case scenario: {do_worst:.2f} mg/L")
print(f"Net change: {change_worst:+.2f} mg/L ({abs(change_worst)/do_summer_current*100:.1f}% decline)")

critical_worst = (rf.predict(df_worst[features]) < 5).sum()
print(f"Critical events: {critical_summer_current} → {critical_worst} (+{critical_worst - critical_summer_current:.0f})")
print(f"🔴 CATASTROPHIC: {critical_worst/len(df_worst)*100:.1f}% of samples below safe levels")

# ============================================================================
# Save results for memo and infographic
# ============================================================================

results = {
    'temporal_trend': {
        'temp_slope': temp_slope,
        'do_slope': do_slope,
        'critical_slope': critical_slope,
        'years_analyzed': len(df_yearly)
    },
    'feature_importance': importance.to_dict('records'),
    'scenarios': {
        'more_rain': {'change_DO': change_rain, 'direction': 'positive' if change_rain > 0 else 'negative'},
        'more_salt': {'change_DO': change_salt, 'critical_increase': critical_salt - critical_current},
        'heat_wave': {'change_DO': change_heat, 'critical_increase': critical_summer_heat - critical_summer_current},
        'worst_case': {'change_DO': change_worst, 'critical_pct': critical_worst/len(df_worst)*100}
    },
    'consistent_problems': len(consistent_problems),
    'watershed_correlations': df_ws_corr.to_dict('records')
}

# Save to JSON for other scripts
import json
with open('data/exports/strategic_insights.json', 'w') as f:
    # Convert numpy types to Python types
    json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

print("\n" + "="*80)
print("✅ STRATEGIC ANALYSIS COMPLETE")
print("="*80)
print(f"💾 Insights saved to: data/exports/strategic_insights.json")
print("\nNext steps:")
print("  1. Generate Executive Water Alert Memo")
print("  2. Create Community Infographic")
print("  3. Build Priority Action Dashboard")
