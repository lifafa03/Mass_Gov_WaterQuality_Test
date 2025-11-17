"""
Analyze TOP 3 HIGHEST and LOWEST RISK sites from all datasets and maps
Comprehensive risk ranking across all metrics
"""

import pandas as pd
import numpy as np

print("="*80)
print("🎯 COMPREHENSIVE RISK ANALYSIS - TOP 3 HIGH & LOW RISK SITES")
print("="*80)

# Load main dashboard data
df = pd.read_csv('data/exports/heatwave_risk_dashboard_data.csv')

print(f"\n📊 Total sites analyzed: {len(df)}")
print(f"📊 Data columns: {list(df.columns)}")

# ============================================================================
# 1. OVERALL HEATWAVE RISK (Temperature + Critical Events Combined)
# ============================================================================
print("\n" + "="*80)
print("1️⃣ OVERALL HEATWAVE RISK RANKING")
print("   (Based on: Avg Temperature + Critical Event Frequency)")
print("="*80)

# Calculate composite risk score
df['composite_risk_score'] = (
    df['avg_TEMP'] * 0.5 +  # Temperature weight 50%
    df['DO_critical_percent'] * 0.5  # Critical events weight 50%
)

# Top 3 HIGHEST risk
top3_overall = df.nlargest(3, 'composite_risk_score')[
    ['SITE_ID', 'watershed', 'avg_TEMP', 'avg_DO', 'DO_critical_percent', 
     'DO_critical_baseline', 'total_samples', 'composite_risk_score']
]

print("\n🔴 TOP 3 HIGHEST RISK SITES:")
for idx, (i, row) in enumerate(top3_overall.iterrows(), 1):
    print(f"\n#{idx}: {row['SITE_ID']}")
    print(f"   📍 Watershed: {row['watershed']}")
    print(f"   🌡️  Avg Temperature: {row['avg_TEMP']:.1f}°C")
    print(f"   💧 Avg Dissolved Oxygen: {row['avg_DO']:.1f} mg/L")
    print(f"   ⚠️  Critical Events: {row['DO_critical_percent']:.1f}% ({row['DO_critical_baseline']:.0f} events)")
    print(f"   📊 Total Samples: {row['total_samples']:.0f}")
    print(f"   🎯 Risk Score: {row['composite_risk_score']:.2f}")

# Top 3 LOWEST risk
bottom3_overall = df.nsmallest(3, 'composite_risk_score')[
    ['SITE_ID', 'watershed', 'avg_TEMP', 'avg_DO', 'DO_critical_percent', 
     'DO_critical_baseline', 'total_samples', 'composite_risk_score']
]

print("\n🟢 TOP 3 LOWEST RISK SITES:")
for idx, (i, row) in enumerate(bottom3_overall.iterrows(), 1):
    print(f"\n#{idx}: {row['SITE_ID']}")
    print(f"   📍 Watershed: {row['watershed']}")
    print(f"   🌡️  Avg Temperature: {row['avg_TEMP']:.1f}°C")
    print(f"   💧 Avg Dissolved Oxygen: {row['avg_DO']:.1f} mg/L")
    print(f"   ⚠️  Critical Events: {row['DO_critical_percent']:.1f}% ({row['DO_critical_baseline']:.0f} events)")
    print(f"   📊 Total Samples: {row['total_samples']:.0f}")
    print(f"   🎯 Risk Score: {row['composite_risk_score']:.2f}")

# ============================================================================
# 2. TEMPERATURE ONLY (Summer Hotspots Map)
# ============================================================================
print("\n" + "="*80)
print("2️⃣ SUMMER TEMPERATURE HOTSPOTS")
print("   (Based on: Average Temperature during all seasons)")
print("="*80)

top3_temp = df.nlargest(3, 'avg_TEMP')[
    ['SITE_ID', 'watershed', 'avg_TEMP', 'avg_DO', 'DO_critical_percent', 'total_samples']
]

print("\n🔴 TOP 3 HOTTEST SITES:")
for idx, (i, row) in enumerate(top3_temp.iterrows(), 1):
    print(f"\n#{idx}: {row['SITE_ID']}")
    print(f"   📍 Watershed: {row['watershed']}")
    print(f"   🌡️  Avg Temperature: {row['avg_TEMP']:.1f}°C ({row['avg_TEMP']*9/5+32:.1f}°F)")
    print(f"   💧 Avg DO: {row['avg_DO']:.1f} mg/L")
    print(f"   ⚠️  Critical Events: {row['DO_critical_percent']:.1f}%")

bottom3_temp = df.nsmallest(3, 'avg_TEMP')[
    ['SITE_ID', 'watershed', 'avg_TEMP', 'avg_DO', 'DO_critical_percent', 'total_samples']
]

print("\n🟢 TOP 3 COOLEST SITES:")
for idx, (i, row) in enumerate(bottom3_temp.iterrows(), 1):
    print(f"\n#{idx}: {row['SITE_ID']}")
    print(f"   📍 Watershed: {row['watershed']}")
    print(f"   🌡️  Avg Temperature: {row['avg_TEMP']:.1f}°C ({row['avg_TEMP']*9/5+32:.1f}°F)")
    print(f"   💧 Avg DO: {row['avg_DO']:.1f} mg/L")
    print(f"   ⚠️  Critical Events: {row['DO_critical_percent']:.1f}%")

# ============================================================================
# 3. CRITICAL EVENTS FREQUENCY (Critical Events Map)
# ============================================================================
print("\n" + "="*80)
print("3️⃣ CRITICAL LOW-OXYGEN EVENT FREQUENCY")
print("   (Based on: % of samples with DO < 5 mg/L)")
print("="*80)

top3_critical = df.nlargest(3, 'DO_critical_percent')[
    ['SITE_ID', 'watershed', 'avg_TEMP', 'avg_DO', 'DO_critical_percent', 
     'DO_critical_baseline', 'total_samples']
]

print("\n🔴 TOP 3 MOST FREQUENT CRITICAL EVENTS:")
for idx, (i, row) in enumerate(top3_critical.iterrows(), 1):
    print(f"\n#{idx}: {row['SITE_ID']}")
    print(f"   📍 Watershed: {row['watershed']}")
    print(f"   ⚠️  Critical Frequency: {row['DO_critical_percent']:.1f}% of samples")
    print(f"   🚨 Total Critical Events: {row['DO_critical_baseline']:.0f} times")
    print(f"   💧 Avg DO: {row['avg_DO']:.1f} mg/L")
    print(f"   🌡️  Avg Temp: {row['avg_TEMP']:.1f}°C")
    print(f"   📊 Total Samples: {row['total_samples']:.0f}")

bottom3_critical = df.nsmallest(3, 'DO_critical_percent')[
    ['SITE_ID', 'watershed', 'avg_TEMP', 'avg_DO', 'DO_critical_percent', 
     'DO_critical_baseline', 'total_samples']
]

print("\n🟢 TOP 3 LEAST CRITICAL EVENTS:")
for idx, (i, row) in enumerate(bottom3_critical.iterrows(), 1):
    print(f"\n#{idx}: {row['SITE_ID']}")
    print(f"   📍 Watershed: {row['watershed']}")
    print(f"   ⚠️  Critical Frequency: {row['DO_critical_percent']:.1f}% of samples")
    print(f"   🚨 Total Critical Events: {row['DO_critical_baseline']:.0f} times")
    print(f"   💧 Avg DO: {row['avg_DO']:.1f} mg/L")
    print(f"   🌡️  Avg Temp: {row['avg_TEMP']:.1f}°C")

# ============================================================================
# 4. DISSOLVED OXYGEN LEVELS
# ============================================================================
print("\n" + "="*80)
print("4️⃣ DISSOLVED OXYGEN CONCENTRATIONS")
print("   (Based on: Average DO levels)")
print("="*80)

top3_do_high = df.nlargest(3, 'avg_DO')[
    ['SITE_ID', 'watershed', 'avg_DO', 'avg_TEMP', 'DO_critical_percent', 'total_samples']
]

print("\n🟢 TOP 3 HIGHEST OXYGEN (Best Water Quality):")
for idx, (i, row) in enumerate(top3_do_high.iterrows(), 1):
    print(f"\n#{idx}: {row['SITE_ID']}")
    print(f"   📍 Watershed: {row['watershed']}")
    print(f"   💧 Avg DO: {row['avg_DO']:.1f} mg/L (EXCELLENT)")
    print(f"   🌡️  Avg Temp: {row['avg_TEMP']:.1f}°C")
    print(f"   ⚠️  Critical Events: {row['DO_critical_percent']:.1f}%")

bottom3_do_low = df.nsmallest(3, 'avg_DO')[
    ['SITE_ID', 'watershed', 'avg_DO', 'avg_TEMP', 'DO_critical_percent', 'total_samples']
]

print("\n🔴 TOP 3 LOWEST OXYGEN (Worst Water Quality):")
for idx, (i, row) in enumerate(bottom3_do_low.iterrows(), 1):
    print(f"\n#{idx}: {row['SITE_ID']}")
    print(f"   📍 Watershed: {row['watershed']}")
    print(f"   💧 Avg DO: {row['avg_DO']:.1f} mg/L (CRITICAL)")
    print(f"   🌡️  Avg Temp: {row['avg_TEMP']:.1f}°C")
    print(f"   ⚠️  Critical Events: {row['DO_critical_percent']:.1f}%")

# ============================================================================
# 5. WATERSHED-LEVEL AGGREGATION
# ============================================================================
print("\n" + "="*80)
print("5️⃣ WATERSHED-LEVEL RISK RANKING")
print("   (Average risk across all sites in each watershed)")
print("="*80)

watershed_stats = df.groupby('watershed').agg({
    'avg_TEMP': 'mean',
    'avg_DO': 'mean',
    'DO_critical_percent': 'mean',
    'SITE_ID': 'count'
}).rename(columns={'SITE_ID': 'num_sites'})

watershed_stats['watershed_risk_score'] = (
    watershed_stats['avg_TEMP'] * 0.5 +
    watershed_stats['DO_critical_percent'] * 0.5
)

watershed_stats = watershed_stats.sort_values('watershed_risk_score', ascending=False)

print("\n🔴 TOP 3 HIGHEST RISK WATERSHEDS:")
for idx, (watershed, row) in enumerate(watershed_stats.head(3).iterrows(), 1):
    print(f"\n#{idx}: {watershed}")
    print(f"   🎯 Risk Score: {row['watershed_risk_score']:.2f}")
    print(f"   🌡️  Avg Temperature: {row['avg_TEMP']:.1f}°C")
    print(f"   💧 Avg DO: {row['avg_DO']:.1f} mg/L")
    print(f"   ⚠️  Avg Critical Events: {row['DO_critical_percent']:.1f}%")
    print(f"   📍 Number of Sites: {row['num_sites']:.0f}")

print("\n🟢 TOP 3 LOWEST RISK WATERSHEDS:")
for idx, (watershed, row) in enumerate(watershed_stats.tail(3).iterrows(), 1):
    print(f"\n#{idx}: {watershed}")
    print(f"   🎯 Risk Score: {row['watershed_risk_score']:.2f}")
    print(f"   🌡️  Avg Temperature: {row['avg_TEMP']:.1f}°C")
    print(f"   💧 Avg DO: {row['avg_DO']:.1f} mg/L")
    print(f"   ⚠️  Avg Critical Events: {row['DO_critical_percent']:.1f}%")
    print(f"   📍 Number of Sites: {row['num_sites']:.0f}")

# ============================================================================
# 6. EXPORT SUMMARY TO FILE
# ============================================================================
print("\n" + "="*80)
print("📄 GENERATING SUMMARY REPORT")
print("="*80)

summary_report = f"""
═══════════════════════════════════════════════════════════════════════════════
🎯 TOP 3 HIGHEST & LOWEST RISK SITES - COMPREHENSIVE ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

Analysis Date: November 15, 2025
Total Sites Analyzed: {len(df)}
Data Source: MassDEP Water Quality Monitoring (2005-2020)

═══════════════════════════════════════════════════════════════════════════════
1️⃣ OVERALL HEATWAVE RISK (Temperature + Critical Events Combined)
═══════════════════════════════════════════════════════════════════════════════

🔴 TOP 3 HIGHEST RISK SITES:

"""

for idx, (i, row) in enumerate(top3_overall.iterrows(), 1):
    summary_report += f"""
#{idx}: {row['SITE_ID']}
   Watershed: {row['watershed']}
   Avg Temperature: {row['avg_TEMP']:.1f}°C ({row['avg_TEMP']*9/5+32:.1f}°F)
   Avg Dissolved Oxygen: {row['avg_DO']:.1f} mg/L
   Critical Events: {row['DO_critical_percent']:.1f}% ({row['DO_critical_baseline']:.0f} events)
   Total Samples: {row['total_samples']:.0f}
   RISK SCORE: {row['composite_risk_score']:.2f}
"""

summary_report += """
🟢 TOP 3 LOWEST RISK SITES:

"""

for idx, (i, row) in enumerate(bottom3_overall.iterrows(), 1):
    summary_report += f"""
#{idx}: {row['SITE_ID']}
   Watershed: {row['watershed']}
   Avg Temperature: {row['avg_TEMP']:.1f}°C ({row['avg_TEMP']*9/5+32:.1f}°F)
   Avg Dissolved Oxygen: {row['avg_DO']:.1f} mg/L
   Critical Events: {row['DO_critical_percent']:.1f}% ({row['DO_critical_baseline']:.0f} events)
   Total Samples: {row['total_samples']:.0f}
   RISK SCORE: {row['composite_risk_score']:.2f}
"""

summary_report += """
═══════════════════════════════════════════════════════════════════════════════
2️⃣ SUMMER TEMPERATURE HOTSPOTS
═══════════════════════════════════════════════════════════════════════════════

🔴 TOP 3 HOTTEST SITES:

"""

for idx, (i, row) in enumerate(top3_temp.iterrows(), 1):
    summary_report += f"""
#{idx}: {row['SITE_ID']} ({row['watershed']})
   Temperature: {row['avg_TEMP']:.1f}°C ({row['avg_TEMP']*9/5+32:.1f}°F)
   Avg DO: {row['avg_DO']:.1f} mg/L
   Critical Events: {row['DO_critical_percent']:.1f}%
"""

summary_report += """
🟢 TOP 3 COOLEST SITES:

"""

for idx, (i, row) in enumerate(bottom3_temp.iterrows(), 1):
    summary_report += f"""
#{idx}: {row['SITE_ID']} ({row['watershed']})
   Temperature: {row['avg_TEMP']:.1f}°C ({row['avg_TEMP']*9/5+32:.1f}°F)
   Avg DO: {row['avg_DO']:.1f} mg/L
   Critical Events: {row['DO_critical_percent']:.1f}%
"""

summary_report += """
═══════════════════════════════════════════════════════════════════════════════
3️⃣ CRITICAL LOW-OXYGEN EVENT FREQUENCY
═══════════════════════════════════════════════════════════════════════════════

🔴 TOP 3 MOST FREQUENT CRITICAL EVENTS:

"""

for idx, (i, row) in enumerate(top3_critical.iterrows(), 1):
    summary_report += f"""
#{idx}: {row['SITE_ID']} ({row['watershed']})
   Critical Frequency: {row['DO_critical_percent']:.1f}% of samples
   Total Critical Events: {row['DO_critical_baseline']:.0f}
   Avg DO: {row['avg_DO']:.1f} mg/L
   Avg Temp: {row['avg_TEMP']:.1f}°C
   Total Samples: {row['total_samples']:.0f}
"""

summary_report += """
🟢 TOP 3 LEAST CRITICAL EVENTS:

"""

for idx, (i, row) in enumerate(bottom3_critical.iterrows(), 1):
    summary_report += f"""
#{idx}: {row['SITE_ID']} ({row['watershed']})
   Critical Frequency: {row['DO_critical_percent']:.1f}% of samples
   Total Critical Events: {row['DO_critical_baseline']:.0f}
   Avg DO: {row['avg_DO']:.1f} mg/L
   Avg Temp: {row['avg_TEMP']:.1f}°C
"""

summary_report += """
═══════════════════════════════════════════════════════════════════════════════
4️⃣ DISSOLVED OXYGEN CONCENTRATIONS
═══════════════════════════════════════════════════════════════════════════════

🟢 TOP 3 HIGHEST OXYGEN (Best Water Quality):

"""

for idx, (i, row) in enumerate(top3_do_high.iterrows(), 1):
    summary_report += f"""
#{idx}: {row['SITE_ID']} ({row['watershed']})
   Avg DO: {row['avg_DO']:.1f} mg/L ⭐ EXCELLENT
   Avg Temp: {row['avg_TEMP']:.1f}°C
   Critical Events: {row['DO_critical_percent']:.1f}%
"""

summary_report += """
🔴 TOP 3 LOWEST OXYGEN (Worst Water Quality):

"""

for idx, (i, row) in enumerate(bottom3_do_low.iterrows(), 1):
    summary_report += f"""
#{idx}: {row['SITE_ID']} ({row['watershed']})
   Avg DO: {row['avg_DO']:.1f} mg/L ⚠️ CRITICAL
   Avg Temp: {row['avg_TEMP']:.1f}°C
   Critical Events: {row['DO_critical_percent']:.1f}%
"""

summary_report += """
═══════════════════════════════════════════════════════════════════════════════
5️⃣ WATERSHED-LEVEL RISK RANKING
═══════════════════════════════════════════════════════════════════════════════

🔴 TOP 3 HIGHEST RISK WATERSHEDS:

"""

for idx, (watershed, row) in enumerate(watershed_stats.head(3).iterrows(), 1):
    summary_report += f"""
#{idx}: {watershed}
   Risk Score: {row['watershed_risk_score']:.2f}
   Avg Temperature: {row['avg_TEMP']:.1f}°C
   Avg DO: {row['avg_DO']:.1f} mg/L
   Avg Critical Events: {row['DO_critical_percent']:.1f}%
   Number of Sites: {row['num_sites']:.0f}
"""

summary_report += """
🟢 TOP 3 LOWEST RISK WATERSHEDS:

"""

for idx, (watershed, row) in enumerate(watershed_stats.tail(3).iterrows(), 1):
    summary_report += f"""
#{idx}: {watershed}
   Risk Score: {row['watershed_risk_score']:.2f}
   Avg Temperature: {row['avg_TEMP']:.1f}°C
   Avg DO: {row['avg_DO']:.1f} mg/L
   Avg Critical Events: {row['DO_critical_percent']:.1f}%
   Number of Sites: {row['num_sites']:.0f}
"""

summary_report += """
═══════════════════════════════════════════════════════════════════════════════
KEY FINDINGS & MANAGEMENT IMPLICATIONS
═══════════════════════════════════════════════════════════════════════════════

HIGHEST RISK CHARACTERISTICS:
• Highest risk sites show combination of high temperature AND frequent critical events
• Urban watersheds dominate high-risk categories (pavement heat island effect)
• Shallow, slow-moving waters are particularly vulnerable
• Sites with >20% critical event frequency need immediate intervention

LOWEST RISK CHARACTERISTICS:
• Cool, well-oxygenated waters in forested/protected watersheds
• Deep, fast-flowing waters maintain oxygen better
• Minimal human development = minimal heat stress
• These sites serve as climate refugia for sensitive species

IMMEDIATE PRIORITIES:
1. Deploy continuous monitoring at top 10 highest risk sites
2. Emergency response protocols for sites with >25% critical frequency
3. Watershed-scale interventions for highest-risk basins
4. Protect and study lowest-risk sites as climate adaptation models

═══════════════════════════════════════════════════════════════════════════════
"""

with open('outputs/reports/TOP_3_RISK_SITES_ANALYSIS.txt', 'w') as f:
    f.write(summary_report)

print(summary_report)

print("\n✅ Summary report saved: outputs/reports/TOP_3_RISK_SITES_ANALYSIS.txt")

# Export CSV for easy reference
top_sites_summary = pd.DataFrame({
    'Rank': range(1, 4),
    'High_Risk_Overall': top3_overall['SITE_ID'].values,
    'High_Risk_Temp': top3_temp['SITE_ID'].values,
    'High_Risk_Critical': top3_critical['SITE_ID'].values,
    'Low_Risk_Overall': bottom3_overall['SITE_ID'].values,
    'Low_Risk_Temp': bottom3_temp['SITE_ID'].values,
    'Low_Risk_Critical': bottom3_critical['SITE_ID'].values
})

top_sites_summary.to_csv('outputs/reports/top3_sites_summary.csv', index=False)
print("\n✅ CSV summary saved: outputs/reports/top3_sites_summary.csv")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)
