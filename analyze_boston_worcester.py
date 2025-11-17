"""
Analyze Boston and Worcester area performance across all risk segments
Focuses on urban watersheds serving these major metropolitan areas
"""

import pandas as pd
import numpy as np

print("="*80)
print("🏙️ BOSTON & WORCESTER METROPOLITAN AREAS - COMPREHENSIVE ANALYSIS")
print("="*80)

# Load data
df = pd.read_csv('data/exports/heatwave_risk_dashboard_data.csv')

# Boston area watersheds
boston_watersheds = [
    'Boston Harbor',
    'Charles',
    'Mystic',
    'Neponset',
    'Weir',
    'Malden',
    'Chelsea'
]

# Worcester area watersheds
worcester_watersheds = [
    'Blackstone',
    'Nashua',
    'Quinebaug',
    'French',
    'Chicopee',
    'SuAsCo',
    'Concord (SuAsCo)'
]

# Filter data
boston_sites = df[df['watershed'].isin(boston_watersheds)].copy()
worcester_sites = df[df['watershed'].isin(worcester_watersheds)].copy()

print(f"\n📊 DATASET OVERVIEW:")
print(f"   Boston Metro Area: {len(boston_sites)} sites across {boston_sites['watershed'].nunique()} watersheds")
print(f"   Worcester Metro Area: {len(worcester_sites)} sites across {worcester_sites['watershed'].nunique()} watersheds")

# ============================================================================
# 1. OVERALL HEATWAVE RISK COMPARISON
# ============================================================================
print("\n" + "="*80)
print("1️⃣ OVERALL HEATWAVE RISK - METRO COMPARISON")
print("="*80)

boston_sites['composite_risk_score'] = (
    boston_sites['avg_TEMP'] * 0.5 + boston_sites['DO_critical_percent'] * 0.5
)
worcester_sites['composite_risk_score'] = (
    worcester_sites['avg_TEMP'] * 0.5 + worcester_sites['DO_critical_percent'] * 0.5
)

boston_avg_risk = boston_sites['composite_risk_score'].mean()
worcester_avg_risk = worcester_sites['composite_risk_score'].mean()

print(f"\n🏙️ BOSTON METRO AREA:")
print(f"   Average Risk Score: {boston_avg_risk:.2f}")
print(f"   Average Temperature: {boston_sites['avg_TEMP'].mean():.1f}°C ({boston_sites['avg_TEMP'].mean()*9/5+32:.1f}°F)")
print(f"   Average DO: {boston_sites['avg_DO'].mean():.1f} mg/L")
print(f"   Average Critical Events: {boston_sites['DO_critical_percent'].mean():.1f}%")
print(f"   Sites in CRISIS (>25% critical): {len(boston_sites[boston_sites['DO_critical_percent'] >= 25])}")
print(f"   Sites in SEVERE (20-25% critical): {len(boston_sites[(boston_sites['DO_critical_percent'] >= 20) & (boston_sites['DO_critical_percent'] < 25)])}")

print(f"\n🏙️ WORCESTER METRO AREA:")
print(f"   Average Risk Score: {worcester_avg_risk:.2f}")
print(f"   Average Temperature: {worcester_sites['avg_TEMP'].mean():.1f}°C ({worcester_sites['avg_TEMP'].mean()*9/5+32:.1f}°F)")
print(f"   Average DO: {worcester_sites['avg_DO'].mean():.1f} mg/L")
print(f"   Average Critical Events: {worcester_sites['DO_critical_percent'].mean():.1f}%")
print(f"   Sites in CRISIS (>25% critical): {len(worcester_sites[worcester_sites['DO_critical_percent'] >= 25])}")
print(f"   Sites in SEVERE (20-25% critical): {len(worcester_sites[(worcester_sites['DO_critical_percent'] >= 20) & (worcester_sites['DO_critical_percent'] < 25)])}")

if boston_avg_risk > worcester_avg_risk:
    print(f"\n⚠️ BOSTON has {((boston_avg_risk - worcester_avg_risk) / worcester_avg_risk * 100):.1f}% HIGHER overall risk than Worcester")
else:
    print(f"\n⚠️ WORCESTER has {((worcester_avg_risk - boston_avg_risk) / boston_avg_risk * 100):.1f}% HIGHER overall risk than Boston")

# ============================================================================
# 2. TOP 5 WORST SITES IN EACH METRO
# ============================================================================
print("\n" + "="*80)
print("2️⃣ TOP 5 WORST SITES IN EACH METRO AREA")
print("="*80)

print("\n🔴 BOSTON METRO - TOP 5 HIGHEST RISK SITES:")
boston_top5 = boston_sites.nlargest(5, 'composite_risk_score')[
    ['SITE_ID', 'watershed', 'avg_TEMP', 'avg_DO', 'DO_critical_percent', 'composite_risk_score']
]
for idx, (i, row) in enumerate(boston_top5.iterrows(), 1):
    print(f"\n#{idx}: {row['SITE_ID']} ({row['watershed']})")
    print(f"    🎯 Risk Score: {row['composite_risk_score']:.2f}")
    print(f"    🌡️  Temperature: {row['avg_TEMP']:.1f}°C ({row['avg_TEMP']*9/5+32:.1f}°F)")
    print(f"    💧 DO: {row['avg_DO']:.1f} mg/L")
    print(f"    ⚠️  Critical Events: {row['DO_critical_percent']:.1f}%")

print("\n\n🔴 WORCESTER METRO - TOP 5 HIGHEST RISK SITES:")
worcester_top5 = worcester_sites.nlargest(5, 'composite_risk_score')[
    ['SITE_ID', 'watershed', 'avg_TEMP', 'avg_DO', 'DO_critical_percent', 'composite_risk_score']
]
for idx, (i, row) in enumerate(worcester_top5.iterrows(), 1):
    print(f"\n#{idx}: {row['SITE_ID']} ({row['watershed']})")
    print(f"    🎯 Risk Score: {row['composite_risk_score']:.2f}")
    print(f"    🌡️  Temperature: {row['avg_TEMP']:.1f}°C ({row['avg_TEMP']*9/5+32:.1f}°F)")
    print(f"    💧 DO: {row['avg_DO']:.1f} mg/L")
    print(f"    ⚠️  Critical Events: {row['DO_critical_percent']:.1f}%")

# ============================================================================
# 3. TEMPERATURE ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("3️⃣ SUMMER TEMPERATURE HOTSPOTS")
print("="*80)

boston_hot = boston_sites.nlargest(3, 'avg_TEMP')[['SITE_ID', 'watershed', 'avg_TEMP', 'avg_DO']]
worcester_hot = worcester_sites.nlargest(3, 'avg_TEMP')[['SITE_ID', 'watershed', 'avg_TEMP', 'avg_DO']]

print("\n🔴 BOSTON - Hottest 3 Sites:")
for idx, (i, row) in enumerate(boston_hot.iterrows(), 1):
    print(f"   {idx}. {row['SITE_ID']} ({row['watershed']}): {row['avg_TEMP']:.1f}°C ({row['avg_TEMP']*9/5+32:.1f}°F), DO: {row['avg_DO']:.1f} mg/L")

print("\n🔴 WORCESTER - Hottest 3 Sites:")
for idx, (i, row) in enumerate(worcester_hot.iterrows(), 1):
    print(f"   {idx}. {row['SITE_ID']} ({row['watershed']}): {row['avg_TEMP']:.1f}°C ({row['avg_TEMP']*9/5+32:.1f}°F), DO: {row['avg_DO']:.1f} mg/L")

# ============================================================================
# 4. CRITICAL EVENTS FREQUENCY
# ============================================================================
print("\n" + "="*80)
print("4️⃣ CRITICAL LOW-OXYGEN EVENT FREQUENCY")
print("="*80)

boston_critical = boston_sites.nlargest(3, 'DO_critical_percent')[
    ['SITE_ID', 'watershed', 'DO_critical_percent', 'DO_critical_baseline', 'avg_DO']
]
worcester_critical = worcester_sites.nlargest(3, 'DO_critical_percent')[
    ['SITE_ID', 'watershed', 'DO_critical_percent', 'DO_critical_baseline', 'avg_DO']
]

print("\n🚨 BOSTON - Most Frequent Critical Events:")
for idx, (i, row) in enumerate(boston_critical.iterrows(), 1):
    print(f"   {idx}. {row['SITE_ID']} ({row['watershed']}): {row['DO_critical_percent']:.1f}% critical ({row['DO_critical_baseline']:.0f} events), Avg DO: {row['avg_DO']:.1f} mg/L")

print("\n🚨 WORCESTER - Most Frequent Critical Events:")
for idx, (i, row) in enumerate(worcester_critical.iterrows(), 1):
    print(f"   {idx}. {row['SITE_ID']} ({row['watershed']}): {row['DO_critical_percent']:.1f}% critical ({row['DO_critical_baseline']:.0f} events), Avg DO: {row['avg_DO']:.1f} mg/L")

# ============================================================================
# 5. WATER QUALITY (DO Levels)
# ============================================================================
print("\n" + "="*80)
print("5️⃣ DISSOLVED OXYGEN - WATER QUALITY COMPARISON")
print("="*80)

boston_worst_do = boston_sites.nsmallest(3, 'avg_DO')[['SITE_ID', 'watershed', 'avg_DO', 'avg_TEMP']]
worcester_worst_do = worcester_sites.nsmallest(3, 'avg_DO')[['SITE_ID', 'watershed', 'avg_DO', 'avg_TEMP']]

print("\n💧 BOSTON - Lowest Oxygen (Worst Quality):")
for idx, (i, row) in enumerate(boston_worst_do.iterrows(), 1):
    print(f"   {idx}. {row['SITE_ID']} ({row['watershed']}): {row['avg_DO']:.1f} mg/L (Temp: {row['avg_TEMP']:.1f}°C)")

print("\n💧 WORCESTER - Lowest Oxygen (Worst Quality):")
for idx, (i, row) in enumerate(worcester_worst_do.iterrows(), 1):
    print(f"   {idx}. {row['SITE_ID']} ({row['watershed']}): {row['avg_DO']:.1f} mg/L (Temp: {row['avg_TEMP']:.1f}°C)")

# ============================================================================
# 6. WATERSHED BREAKDOWN
# ============================================================================
print("\n" + "="*80)
print("6️⃣ WATERSHED-BY-WATERSHED BREAKDOWN")
print("="*80)

print("\n🏙️ BOSTON METRO WATERSHEDS:")
boston_by_watershed = boston_sites.groupby('watershed').agg({
    'SITE_ID': 'count',
    'avg_TEMP': 'mean',
    'avg_DO': 'mean',
    'DO_critical_percent': 'mean'
}).rename(columns={'SITE_ID': 'num_sites'})
boston_by_watershed['risk_score'] = (boston_by_watershed['avg_TEMP'] * 0.5 + 
                                      boston_by_watershed['DO_critical_percent'] * 0.5)
boston_by_watershed = boston_by_watershed.sort_values('risk_score', ascending=False)

for watershed, row in boston_by_watershed.iterrows():
    print(f"\n   📍 {watershed}:")
    print(f"      Sites: {row['num_sites']:.0f} | Risk: {row['risk_score']:.2f}")
    print(f"      Temp: {row['avg_TEMP']:.1f}°C | DO: {row['avg_DO']:.1f} mg/L | Critical: {row['DO_critical_percent']:.1f}%")

print("\n\n🏙️ WORCESTER METRO WATERSHEDS:")
worcester_by_watershed = worcester_sites.groupby('watershed').agg({
    'SITE_ID': 'count',
    'avg_TEMP': 'mean',
    'avg_DO': 'mean',
    'DO_critical_percent': 'mean'
}).rename(columns={'SITE_ID': 'num_sites'})
worcester_by_watershed['risk_score'] = (worcester_by_watershed['avg_TEMP'] * 0.5 + 
                                         worcester_by_watershed['DO_critical_percent'] * 0.5)
worcester_by_watershed = worcester_by_watershed.sort_values('risk_score', ascending=False)

for watershed, row in worcester_by_watershed.iterrows():
    print(f"\n   📍 {watershed}:")
    print(f"      Sites: {row['num_sites']:.0f} | Risk: {row['risk_score']:.2f}")
    print(f"      Temp: {row['avg_TEMP']:.1f}°C | DO: {row['avg_DO']:.1f} mg/L | Critical: {row['DO_critical_percent']:.1f}%")

# ============================================================================
# 7. RISK DISTRIBUTION
# ============================================================================
print("\n" + "="*80)
print("7️⃣ RISK CATEGORY DISTRIBUTION")
print("="*80)

def categorize_risk(row):
    if row['avg_TEMP'] >= 25 and row['DO_critical_percent'] >= 20:
        return 'CRISIS'
    elif row['avg_TEMP'] >= 24 and row['DO_critical_percent'] >= 15:
        return 'SEVERE'
    elif row['avg_TEMP'] >= 23 and row['DO_critical_percent'] >= 10:
        return 'HIGH'
    elif row['avg_TEMP'] >= 22 or row['DO_critical_percent'] >= 5:
        return 'MODERATE'
    else:
        return 'LOW'

boston_sites['risk_category'] = boston_sites.apply(categorize_risk, axis=1)
worcester_sites['risk_category'] = worcester_sites.apply(categorize_risk, axis=1)

boston_dist = boston_sites['risk_category'].value_counts()
worcester_dist = worcester_sites['risk_category'].value_counts()

print("\n🏙️ BOSTON METRO - Risk Distribution:")
for cat in ['CRISIS', 'SEVERE', 'HIGH', 'MODERATE', 'LOW']:
    count = boston_dist.get(cat, 0)
    pct = (count / len(boston_sites) * 100) if len(boston_sites) > 0 else 0
    print(f"   {cat:10s}: {count:3d} sites ({pct:5.1f}%)")

print("\n🏙️ WORCESTER METRO - Risk Distribution:")
for cat in ['CRISIS', 'SEVERE', 'HIGH', 'MODERATE', 'LOW']:
    count = worcester_dist.get(cat, 0)
    pct = (count / len(worcester_sites) * 100) if len(worcester_sites) > 0 else 0
    print(f"   {cat:10s}: {count:3d} sites ({pct:5.1f}%)")

# ============================================================================
# 8. MANAGEMENT SUMMARY
# ============================================================================
print("\n" + "="*80)
print("8️⃣ MANAGEMENT SUMMARY & RECOMMENDATIONS")
print("="*80)

boston_crisis_sites = boston_sites[boston_sites['risk_category'].isin(['CRISIS', 'SEVERE'])]
worcester_crisis_sites = worcester_sites[worcester_sites['risk_category'].isin(['CRISIS', 'SEVERE'])]

print(f"\n🚨 IMMEDIATE ACTION REQUIRED:")
print(f"\n   BOSTON: {len(boston_crisis_sites)} sites in CRISIS/SEVERE status")
if len(boston_crisis_sites) > 0:
    print(f"   Watersheds affected: {', '.join(boston_crisis_sites['watershed'].unique())}")
    print(f"   Worst site: {boston_crisis_sites.nlargest(1, 'composite_risk_score')['SITE_ID'].values[0]}")

print(f"\n   WORCESTER: {len(worcester_crisis_sites)} sites in CRISIS/SEVERE status")
if len(worcester_crisis_sites) > 0:
    print(f"   Watersheds affected: {', '.join(worcester_crisis_sites['watershed'].unique())}")
    print(f"   Worst site: {worcester_crisis_sites.nlargest(1, 'composite_risk_score')['SITE_ID'].values[0]}")

print(f"\n📊 COMPARATIVE ASSESSMENT:")
if boston_avg_risk > worcester_avg_risk:
    print(f"   ⚠️ BOSTON is the higher-priority metro area")
    print(f"   • {len(boston_crisis_sites)} vs {len(worcester_crisis_sites)} crisis sites")
    print(f"   • {boston_avg_risk:.2f} vs {worcester_avg_risk:.2f} average risk score")
    print(f"   • Urban heat island effect more severe in coastal areas")
else:
    print(f"   ⚠️ WORCESTER is the higher-priority metro area")
    print(f"   • {len(worcester_crisis_sites)} vs {len(boston_crisis_sites)} crisis sites")
    print(f"   • {worcester_avg_risk:.2f} vs {boston_avg_risk:.2f} average risk score")
    print(f"   • Industrial/urban pollution combined with heat stress")

print(f"\n💡 RECOMMENDED ACTIONS:")
print(f"\n   FOR BOSTON:")
print(f"   • Deploy continuous sensors in {boston_by_watershed.index[0]} (highest risk watershed)")
print(f"   • Urban heat mitigation: cool pavement, street trees along urban rivers")
print(f"   • Stormwater management for harbor tributaries")

print(f"\n   FOR WORCESTER:")
print(f"   • Deploy continuous sensors in {worcester_by_watershed.index[0]} (highest risk watershed)")
print(f"   • Industrial discharge monitoring and enforcement")
print(f"   • Agricultural runoff controls in upstream watersheds")

# Export summary
summary = {
    'Metro_Area': ['Boston', 'Worcester'],
    'Total_Sites': [len(boston_sites), len(worcester_sites)],
    'Avg_Risk_Score': [boston_avg_risk, worcester_avg_risk],
    'Avg_Temperature_C': [boston_sites['avg_TEMP'].mean(), worcester_sites['avg_TEMP'].mean()],
    'Avg_DO_mgL': [boston_sites['avg_DO'].mean(), worcester_sites['avg_DO'].mean()],
    'Avg_Critical_Pct': [boston_sites['DO_critical_percent'].mean(), worcester_sites['DO_critical_percent'].mean()],
    'Crisis_Sites': [len(boston_sites[boston_sites['risk_category'] == 'CRISIS']), 
                     len(worcester_sites[worcester_sites['risk_category'] == 'CRISIS'])],
    'Severe_Sites': [len(boston_sites[boston_sites['risk_category'] == 'SEVERE']), 
                     len(worcester_sites[worcester_sites['risk_category'] == 'SEVERE'])]
}

summary_df = pd.DataFrame(summary)
summary_df.to_csv('outputs/reports/boston_worcester_comparison.csv', index=False)

print(f"\n✅ Comparison data saved: outputs/reports/boston_worcester_comparison.csv")

# Export detailed site lists
boston_sites.to_csv('outputs/reports/boston_metro_sites_detailed.csv', index=False)
worcester_sites.to_csv('outputs/reports/worcester_metro_sites_detailed.csv', index=False)

print(f"✅ Boston detailed data: outputs/reports/boston_metro_sites_detailed.csv")
print(f"✅ Worcester detailed data: outputs/reports/worcester_metro_sites_detailed.csv")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)
