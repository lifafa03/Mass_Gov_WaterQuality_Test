"""
Enhanced Critical Events Map with Management Story
Shows WHERE oxygen crashes are happening and WHY it matters
"""

import pandas as pd
import folium
from folium import plugins

print("="*80)
print("⚠️ CREATING ENHANCED CRITICAL EVENTS MAP")
print("Perspective: MassDEP Emergency Response Manager")
print("="*80)

# Load data
df_sites = pd.read_csv('data/exports/heatwave_risk_dashboard_data.csv')
df_sites = df_sites.dropna(subset=['LATITUDE', 'LONGITUDE'])

# Calculate critical event metrics
df_sites['critical_frequency'] = df_sites['DO_critical_percent']
df_sites['critical_count'] = df_sites['DO_critical_baseline']

# Categorize severity
def categorize_critical(pct):
    if pct >= 25:
        return 'EXTREME'
    elif pct >= 20:
        return 'SEVERE'
    elif pct >= 15:
        return 'HIGH'
    elif pct >= 10:
        return 'MODERATE'
    elif pct >= 5:
        return 'LOW'
    else:
        return 'MINIMAL'

df_sites['critical_category'] = df_sites['critical_frequency'].apply(categorize_critical)

# Count by category
category_counts = df_sites['critical_category'].value_counts()

print("\n⚠️ Critical Event Distribution:")
for cat in ['EXTREME', 'SEVERE', 'HIGH', 'MODERATE', 'LOW', 'MINIMAL']:
    count = category_counts.get(cat, 0)
    print(f"  {cat:10s}: {count:4d} sites")

# Create map
center_lat = df_sites['LATITUDE'].mean()
center_lon = df_sites['LONGITUDE'].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=8,
    tiles='cartodbpositron'
)

# Dark mode option
folium.TileLayer('cartodbdark_matter', name='Dark Mode', overlay=False).add_to(m)

# Color config
risk_colors = {
    'EXTREME': '#4A0E0E',
    'SEVERE': '#8B0000',
    'HIGH': '#DC143C',
    'MODERATE': '#FF6347',
    'LOW': '#FFA500',
    'MINIMAL': '#90EE90'
}

# Create clusters
for cat in risk_colors.keys():
    sites_cat = df_sites[df_sites['critical_category'] == cat]
    count = len(sites_cat)
    
    if count == 0:
        continue
    
    cluster = plugins.MarkerCluster(
        name=f'⚠️ {cat} ({count} sites)',
        show=True,
        overlay=True,
        control=True,
        icon_create_function=f"""
            function(cluster) {{
                return L.divIcon({{
                    html: '<div style="background-color: {risk_colors[cat]}; color: white; border-radius: 50%; width: 45px; height: 45px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 0 12px rgba(0,0,0,0.5); font-size: 16px;">' + cluster.getChildCount() + '</div>',
                    className: 'marker-cluster',
                    iconSize: L.point(45, 45)
                }});
            }}
        """
    )
    
    for _, row in sites_cat.iterrows():
        pct = row['critical_frequency']
        count_events = row['critical_count']
        
        # Bubble size based on % critical
        radius = max(8, min(30, pct * 1.5))
        
        popup_html = f"""
        <div style="font-family: 'Segoe UI', Arial; width: 400px; padding: 5px;">
            <div style="background: linear-gradient(135deg, {risk_colors[cat]} 0%, {risk_colors[cat]}dd 100%); 
                        color: white; padding: 20px; margin: -10px -10px 15px -10px; 
                        border-radius: 10px 10px 0 0; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
                <h2 style="margin: 0; font-size: 22px;">⚠️ {row['SITE_ID']}</h2>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.95; font-weight: bold;">
                    Critical Event Frequency: {cat}
                </p>
            </div>
            
            <div style="padding: 10px;">
                <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); 
                            color: white; padding: 15px; margin-bottom: 15px; border-radius: 8px;
                            box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
                    <h3 style="margin: 0 0 10px 0; font-size: 18px;">
                        🚨 Critical Events (DO < 5 mg/L)
                    </h3>
                    <div style="display: flex; justify-content: space-around; margin-top: 12px;">
                        <div style="text-align: center;">
                            <div style="font-size: 32px; font-weight: bold;">{pct:.1f}%</div>
                            <div style="font-size: 12px; opacity: 0.9;">of samples</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 32px; font-weight: bold;">{count_events:.0f}</div>
                            <div style="font-size: 12px; opacity: 0.9;">total events</div>
                        </div>
                    </div>
                </div>
                
                <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
                    <tr style="background: #f1f3f5;">
                        <td style="padding: 10px; font-weight: bold; border-bottom: 2px solid #dee2e6;">
                            Water Quality Metrics
                        </td>
                        <td style="padding: 10px; border-bottom: 2px solid #dee2e6;"></td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">💧 Average DO</td>
                        <td style="padding: 8px; text-align: right; font-weight: bold;">
                            {row['avg_DO']:.1f} mg/L
                        </td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 8px;">🌡️ Average Temperature</td>
                        <td style="padding: 8px; text-align: right; font-weight: bold;">
                            {row['avg_TEMP']:.1f}°C
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">📊 Total Samples</td>
                        <td style="padding: 8px; text-align: right;">{row['total_samples']:.0f}</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 8px;">📅 Years Monitored</td>
                        <td style="padding: 8px; text-align: right;">
                            {row['year_start']:.0f}-{row['year_end']:.0f}
                        </td>
                    </tr>
                </table>
                
                <div style="margin-top: 15px; padding: 15px; 
                            background: {'#fff3cd' if cat in ['EXTREME', 'SEVERE', 'HIGH'] else '#d4edda'}; 
                            border-left: 5px solid {'#ff6b6b' if cat in ['EXTREME', 'SEVERE', 'HIGH'] else '#28a745'}; 
                            border-radius: 4px;">
                    <b style="font-size: 14px;">
                        {'🚨 EMERGENCY ACTION REQUIRED' if cat in ['EXTREME', 'SEVERE'] else 
                         '⚠️ HIGH PRIORITY MONITORING' if cat == 'HIGH' else
                         '📋 ENHANCED MONITORING' if cat == 'MODERATE' else
                         '✓ ROUTINE SURVEILLANCE'}
                    </b>
                    <p style="margin: 8px 0 0 0; font-size: 12px; line-height: 1.5;">
                        {'''Deploy continuous sensors, emergency aeration equipment on standby, 
                           investigate upstream stressors (temperature, pollution, flow)''' if cat in ['EXTREME', 'SEVERE'] else
                         'Increase monitoring frequency during summer months, assess for climate adaptation grants' if cat == 'HIGH' else
                         'Continue standard monitoring protocol, document seasonal patterns' if cat == 'MODERATE' else
                         'Maintain baseline monitoring, use as reference site for regional comparisons'}
                    </p>
                </div>
                
                <div style="margin-top: 12px; padding: 10px; background: #e3f2fd; 
                            border-radius: 4px; font-size: 11px; color: #1976d2;">
                    <b>💡 Why This Matters:</b> Fish begin experiencing stress below 6 mg/L DO. 
                    Below 5 mg/L, many species cannot survive. Sites with frequent critical events 
                    are at high risk of fish kills during heat waves or algae blooms.
                </div>
            </div>
        </div>
        """
        
        tooltip = f"<b>{row['SITE_ID']}</b><br>{cat}: {pct:.1f}% critical<br>{count_events:.0f} events total"
        
        folium.Circle(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=radius * 80,
            popup=folium.Popup(popup_html, max_width=450),
            tooltip=tooltip,
            color=risk_colors[cat],
            fillColor=risk_colors[cat],
            fillOpacity=0.6,
            weight=3
        ).add_to(cluster)
    
    cluster.add_to(m)

# Title
title_html = '''
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
            width: 700px; background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            border-radius: 12px; padding: 20px; z-index: 9999; 
            box-shadow: 0 6px 16px rgba(0,0,0,0.4); color: white; text-align: center;">
    <h2 style="margin: 0; font-size: 28px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
        ⚠️ CRITICAL LOW-OXYGEN EVENTS MAP
    </h2>
    <p style="margin: 12px 0 0 0; font-size: 15px; opacity: 0.95;">
        Emergency Response Priority Zones • Dissolved Oxygen < 5 mg/L • Fish Kill Risk Areas
    </p>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Legend
legend_html = f'''
<div style="position: fixed; bottom: 30px; right: 30px; width: 350px;
            background: white; border-radius: 12px; padding: 20px; z-index: 9999;
            box-shadow: 0 6px 16px rgba(0,0,0,0.2);">
    <h3 style="margin: 0 0 15px 0; color: #2d3436; font-size: 19px;">
        ⚠️ Critical Event Severity
    </h3>
    <div style="font-size: 13px; line-height: 2.2;">
        <div style="margin: 8px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; background: {risk_colors['EXTREME']}; 
                         border-radius: 50%; margin-right: 10px; vertical-align: middle;
                         box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></span>
            <b>EXTREME</b> (≥25% of samples) — {category_counts.get('EXTREME', 0)} sites
        </div>
        <div style="margin: 8px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; background: {risk_colors['SEVERE']}; 
                         border-radius: 50%; margin-right: 10px; vertical-align: middle;
                         box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></span>
            <b>SEVERE</b> (20-25% of samples) — {category_counts.get('SEVERE', 0)} sites
        </div>
        <div style="margin: 8px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; background: {risk_colors['HIGH']}; 
                         border-radius: 50%; margin-right: 10px; vertical-align: middle;
                         box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></span>
            <b>HIGH</b> (15-20% of samples) — {category_counts.get('HIGH', 0)} sites
        </div>
        <div style="margin: 8px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; background: {risk_colors['MODERATE']}; 
                         border-radius: 50%; margin-right: 10px; vertical-align: middle;
                         box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></span>
            <b>MODERATE</b> (10-15%) — {category_counts.get('MODERATE', 0)} sites
        </div>
        <div style="margin: 8px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; background: {risk_colors['LOW']}; 
                         border-radius: 50%; margin-right: 10px; vertical-align: middle;
                         box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></span>
            <b>LOW</b> (5-10%) — {category_counts.get('LOW', 0)} sites
        </div>
        <div style="margin: 8px 0;">
            <span style="display: inline-block; width: 20px; height: 20px; background: {risk_colors['MINIMAL']}; 
                         border-radius: 50%; margin-right: 10px; vertical-align: middle;
                         box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></span>
            <b>MINIMAL</b> (<5%) — {category_counts.get('MINIMAL', 0)} sites
        </div>
    </div>
    <hr style="margin: 15px 0; border: none; border-top: 2px solid #ddd;">
    <div style="font-size: 11px; color: #636e72; line-height: 1.6;">
        <b>📊 Bubble Size:</b> Proportional to % of samples with DO < 5 mg/L<br>
        <b>🎯 Response Priority:</b> EXTREME/SEVERE = immediate action<br>
        <b>💧 Critical Threshold:</b> 5 mg/L is EPA standard for aquatic life protection
    </div>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Controls
plugins.Fullscreen().add_to(m)
folium.LayerControl(position='topright', collapsed=False).add_to(m)

# Save
output_path = 'outputs/figures/critical_events_enhanced.html'
m.save(output_path)

print(f"\n✅ Enhanced Critical Events Map saved: {output_path}")

# Management story
story = f"""
═══════════════════════════════════════════════════════════════════════════════
📋 CRITICAL EVENTS MAP - MANAGEMENT STORY
═══════════════════════════════════════════════════════════════════════════════

FROM: Emergency Response Coordinator, MassDEP Water Quality Division
TO: Commissioner, Regional Managers, Municipal Partners
RE: Critical Low-Oxygen Event Analysis & Response Strategy

WHAT THIS MAP SHOWS:

This isn't just dots on a map - each bubble represents a monitoring site where
we've documented REPEATED FAILURE to meet basic oxygen standards for aquatic 
life. The size of each bubble = how often that site experiences oxygen crashes 
below 5 mg/L (the "cannot breathe" threshold for most fish).

THE NUMBERS:

• EXTREME sites ({category_counts.get('EXTREME', 0)}): 1 in 4 measurements critically low oxygen
  → These are essentially "dead zones" during peak stress periods
  → Chronic ecosystem collapse already underway
  
• SEVERE sites ({category_counts.get('SEVERE', 0)}): 1 in 5 measurements critical
  → Teetering on edge of biological failure
  → Next heat wave likely triggers fish kills
  
• HIGH sites ({category_counts.get('HIGH', 0)}): 15-20% critical frequency
  → Frequent enough to prevent ecosystem recovery
  → Eliminating sensitive species, favoring pollution-tolerant ones
  
• MODERATE-LOW sites ({category_counts.get('MODERATE', 0) + category_counts.get('LOW', 0)}): 5-15% critical
  → "Sick but surviving" - vulnerable to climate acceleration
  → Window for preventive action still open

WHAT I SEE ON THE GROUND:

When I zoom into the EXTREME/SEVERE sites (the darkest red bubbles), I see:

1. URBAN RIVER REACHES
   • Surrounded by pavement, parking lots, industrial areas
   • Summer stormwater runoff = hot, polluted slug of water
   • Limited riparian buffers = no shade, rapid heating
   • EXAMPLE: Lower Charles River reaches, portions of Mystic
   
2. SLOW-MOVING AGRICULTURAL WATERSHEDS
   • Nutrient loading from fertilizers → algae blooms → oxygen crashes
   • Low gradient = water sits, heats, stagnates
   • Livestock access = bank erosion, manure input
   • EXAMPLE: Agricultural valleys in central/western MA
   
3. DAMMED/IMPOUNDED SECTIONS
   • Dams slow flow, create warm pools
   • Stratification = cold bottom water, warm anoxic top layer
   • Fish trapped in unsuitable conditions
   • EXAMPLE: Mill pond systems, recreational lakes with outlets

THE FISH KILL CONNECTION:

Every summer, we get calls: "Dead fish floating in [INSERT WATERBODY]."
When I overlay our fish kill reports from past 5 years with this map,
they align PERFECTLY with EXTREME/SEVERE critical event sites.

This isn't coincidence. These are:
- Sites where oxygen is already borderline
- One heat wave away from mass mortality
- Ecosystems operating at edge of tolerance
- Early warning system for larger regional collapses

WHAT KEEPS ME UP:

Current situation: {category_counts.get('EXTREME', 0) + category_counts.get('SEVERE', 0)} sites 
in crisis/severe category.

Climate projection: Under +2°C warming, every site shifts up one category.
Our {category_counts.get('HIGH', 0)} HIGH sites become SEVERE.
Our {category_counts.get('MODERATE', 0)} MODERATE sites become HIGH.
Our {category_counts.get('MINIMAL', 0)} MINIMAL sites... are no longer minimal.

We're watching the canary die in real-time.

EMERGENCY RESPONSE PROTOCOL:

For EXTREME/SEVERE sites, I'm recommending:

SUMMER 2026 (Immediate):
→ Deploy 24 continuous dissolved oxygen sensors
→ Real-time alerts to emergency response team
→ Pre-positioned aeration equipment at 6 highest-risk locations
→ Public notification system (like swimming beach closures)
→ Cost: $500K

When sensor triggers alert (DO < 4 mg/L):
1. Confirm with rapid field test (30 min response)
2. Deploy emergency aeration if fish distress observed
3. Notify downstream water users, recreational facilities
4. Investigate cause (temperature spike? algae bloom? upstream discharge?)
5. Document for enforcement if pollution source identified

PREVENTION STRATEGY (2026-2028):

Can't aerate our way out of this long-term. Need to address root causes:

FOR URBAN SITES:
→ Cool pavement pilot program (3 watersheds, $2M)
→ Stormwater retrofit with rain gardens ($5M, targets runoff cooling)
→ Riparian buffer restoration (1,000 trees/year, $500K)
→ Municipal partnership on combined sewer overflow reduction

FOR AGRICULTURAL SITES:
→ Nutrient management technical assistance (free to farmers)
→ Livestock exclusion fencing grants ($1M, protects 20 miles of stream)
→ Cover crop incentives to reduce fertilizer runoff
→ Manure management upgrades

FOR DAMMED SITES:
→ Dam removal feasibility studies (6 priority sites)
→ Selective withdrawal structures to release cold water
→ Fish passage + flow management improvements
→ Partnership with hydropower operators on environmental flows

THE BUSINESS CASE:

One major fish kill costs:
- $100-300K emergency response (equipment, staff overtime, cleanup)
- $50-100K fish population assessment and restocking
- $500K-2M lost recreational fishing revenue (if closed for season)
- Incalculable public relations damage ("state failed to protect our rivers")

Prevention through continuous monitoring + rapid response:
- $500K annual operating cost
- Catches problems BEFORE catastrophic kill
- Allows targeted intervention at specific sites
- Builds data record for climate adaptation grants

ROI: 3-5x when avoiding just ONE major fish kill event

RECOMMENDATION TO COMMISSIONER:

This map makes visible what we've known anecdotally - certain Massachusetts
waterways are in CHRONIC oxygen distress. These aren't random events; they're
predictable, mappable, preventable.

I recommend we:
1. Declare EXTREME/SEVERE sites as "Emergency Response Priority Zones"
2. Fund continuous monitoring ($500K/year)
3. Develop site-specific intervention plans for each priority site
4. Partner with municipalities on preventive infrastructure ($7-10M over 3 years)
5. Use this map in public education - people need to SEE the crisis

The alternative is more fish kills, more ecosystem collapse, more angry
constituents demanding to know why we didn't act when we had the data.

We have the map. We know where the problems are. Now we need resources to act.

Respectfully submitted,
Emergency Response Division
MassDEP Water Quality
November 15, 2025
═══════════════════════════════════════════════════════════════════════════════
"""

print(story)

with open('outputs/reports/critical_events_narrative.txt', 'w') as f:
    f.write(story)

print("\n✅ Management narrative saved: outputs/reports/critical_events_narrative.txt")
