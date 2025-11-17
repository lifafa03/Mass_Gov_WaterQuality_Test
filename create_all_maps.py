"""
Create Multiple Beautiful Interactive Maps for MA Waterways
1. Enhanced risk map with better styling
2. Heat map showing risk density
3. Watershed-level choropleth map
4. Scenario comparison (current vs +2°C)
5. Critical events cluster map
"""

import pandas as pd
import folium
from folium import plugins
import json
import numpy as np
from datetime import datetime

print("="*80)
print("CREATING MULTIPLE BEAUTIFUL INTERACTIVE MAPS")
print("="*80)

# Load data
print("\n📊 Loading data...")
df_sites = pd.read_csv('data/exports/heatwave_risk_dashboard_data.csv')
df_timeseries = pd.read_csv('data/exports/heatwave_risk_timeseries_data.csv')
df_watershed = pd.read_csv('data/exports/watershed_risk_ranking.csv')

print(f"✓ Sites: {len(df_sites):,}")
print(f"✓ Time-series records: {len(df_timeseries):,}")
print(f"✓ Watersheds: {len(df_watershed):,}")

# Remove sites with missing coordinates
df_sites = df_sites.dropna(subset=['LATITUDE', 'LONGITUDE'])
center_lat = df_sites['LATITUDE'].mean()
center_lon = df_sites['LONGITUDE'].mean()

# ============================================================================
# MAP 1: ENHANCED RISK MAP WITH BETTER STYLING
# ============================================================================
print("\n" + "="*80)
print("MAP 1: ENHANCED RISK MAP (Beautiful Styling)")
print("="*80)

m1 = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=8,
    tiles='https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png',
    attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>'
)

# Add beautiful tile options
folium.TileLayer(
    'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
    attr='Stadia Maps',
    name='Dark Theme',
    overlay=False
).add_to(m1)

folium.TileLayer(
    'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attr='CartoDB',
    name='Light Map',
    overlay=False
).add_to(m1)

# Create marker clusters for each risk level
print("📍 Creating beautiful marker clusters...")

extreme_cluster = plugins.MarkerCluster(
    name='🔴 Extreme Risk (52 sites)',
    show=True,
    overlay=True,
    control=True,
    icon_create_function="""
        function(cluster) {
            return L.divIcon({
                html: '<div style="background-color: darkred; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.5);">' + cluster.getChildCount() + '</div>',
                className: 'marker-cluster',
                iconSize: L.point(40, 40)
            });
        }
    """
)

high_cluster = plugins.MarkerCluster(
    name='🟠 High Risk (315 sites)',
    show=True,
    overlay=True,
    control=True,
    icon_create_function="""
        function(cluster) {
            return L.divIcon({
                html: '<div style="background-color: red; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.5);">' + cluster.getChildCount() + '</div>',
                className: 'marker-cluster',
                iconSize: L.point(40, 40)
            });
        }
    """
)

medium_cluster = plugins.MarkerCluster(
    name='🟡 Medium Risk (748 sites)',
    show=True,
    overlay=True,
    control=True,
    icon_create_function="""
        function(cluster) {
            return L.divIcon({
                html: '<div style="background-color: orange; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.5);">' + cluster.getChildCount() + '</div>',
                className: 'marker-cluster',
                iconSize: L.point(40, 40)
            });
        }
    """
)

low_cluster = plugins.MarkerCluster(
    name='🟢 Low Risk (10 sites)',
    show=True,
    overlay=True,
    control=True,
    icon_create_function="""
        function(cluster) {
            return L.divIcon({
                html: '<div style="background-color: green; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.5);">' + cluster.getChildCount() + '</div>',
                className: 'marker-cluster',
                iconSize: L.point(40, 40)
            });
        }
    """
)

# Add markers with beautiful styling
for _, row in df_sites.iterrows():
    risk = row['avg_risk_score']
    
    if risk >= 2.5:
        color = '#8B0000'  # Dark red
        icon_color = 'darkred'
        cluster = extreme_cluster
        size = 10
    elif risk >= 2.0:
        color = '#DC143C'  # Crimson
        icon_color = 'red'
        cluster = high_cluster
        size = 8
    elif risk >= 1.0:
        color = '#FF8C00'  # Dark orange
        icon_color = 'orange'
        cluster = medium_cluster
        size = 6
    else:
        color = '#228B22'  # Forest green
        icon_color = 'green'
        cluster = low_cluster
        size = 6
    
    popup_html = f"""
    <div style="font-family: 'Segoe UI', Arial; width: 350px; padding: 5px;">
        <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%); 
                    color: white; padding: 15px; margin: -10px -10px 10px -10px; 
                    border-radius: 5px 5px 0 0;">
            <h3 style="margin: 0; font-size: 18px;">📍 {row['SITE_ID']}</h3>
            <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 13px;">
                {row.get('watershed', 'Unknown Watershed')}
            </p>
        </div>
        
        <div style="padding: 5px;">
            <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <h4 style="margin: 0 0 8px 0; color: {color}; font-size: 14px;">
                    ⚠️ Risk Score: {risk:.2f}/4.0
                </h4>
            </div>
            
            <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
                <tr style="background: #e9ecef;">
                    <td style="padding: 8px; font-weight: bold;">Current Conditions</td>
                    <td style="padding: 8px;"></td>
                </tr>
                <tr>
                    <td style="padding: 6px;">🌡️ Avg Temperature</td>
                    <td style="padding: 6px; text-align: right;"><b>{row['avg_TEMP']:.1f}°C</b></td>
                </tr>
                <tr style="background: #f8f9fa;">
                    <td style="padding: 6px;">💧 Avg Dissolved O₂</td>
                    <td style="padding: 6px; text-align: right;"><b>{row['avg_DO']:.1f} mg/L</b></td>
                </tr>
                <tr>
                    <td style="padding: 6px;">⚠️ Critical Events</td>
                    <td style="padding: 6px; text-align: right;"><b>{row['DO_critical_percent']:.1f}%</b></td>
                </tr>
                
                <tr style="background: #fff3cd;">
                    <td style="padding: 8px; font-weight: bold;">+2°C Scenario</td>
                    <td style="padding: 8px;"></td>
                </tr>
                <tr>
                    <td style="padding: 6px;">🌡️ Projected Temp</td>
                    <td style="padding: 6px; text-align: right;"><b>{row['avg_TEMP_plus2']:.1f}°C</b> <span style="color: red;">(+2°C)</span></td>
                </tr>
                <tr style="background: #f8f9fa;">
                    <td style="padding: 6px;">💧 Projected DO</td>
                    <td style="padding: 6px; text-align: right;"><b>{row['avg_DO_plus2']:.1f} mg/L</b> <span style="color: red;">(-0.5)</span></td>
                </tr>
                <tr>
                    <td style="padding: 6px;">📈 New Critical Events</td>
                    <td style="padding: 6px; text-align: right;"><b style="color: red;">+{row['new_critical_events']:.0f}</b></td>
                </tr>
            </table>
            
            <div style="margin-top: 10px; padding: 8px; background: #d1ecf1; border-left: 4px solid #0c5460; font-size: 12px;">
                <b>📊 Data:</b> {row['total_samples']} samples ({row['year_start']:.0f}-{row['year_end']:.0f})
            </div>
        </div>
    </div>
    """
    
    # Create marker with icon
    folium.CircleMarker(
        location=[row['LATITUDE'], row['LONGITUDE']],
        radius=size,
        popup=folium.Popup(popup_html, max_width=400),
        tooltip=f"<b>{row['SITE_ID']}</b><br>Risk: {risk:.2f}<br>Click for details",
        color='white',
        weight=2,
        fillColor=color,
        fillOpacity=0.8
    ).add_to(cluster)

# Add clusters to map
extreme_cluster.add_to(m1)
high_cluster.add_to(m1)
medium_cluster.add_to(m1)
low_cluster.add_to(m1)

# Add beautiful title
title_html = '''
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
            width: 600px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px; padding: 15px; z-index: 9999; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.3); color: white; text-align: center;">
    <h2 style="margin: 0; font-family: 'Segoe UI', Arial; font-size: 24px;">
        🌊 Massachusetts Waterways Heatwave Risk Assessment
    </h2>
    <p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.95;">
        Interactive Risk Map • 1,125 Monitoring Sites • 2005-2020 Data
    </p>
</div>
'''
m1.get_root().html.add_child(folium.Element(title_html))

# Add beautiful legend
legend_html = '''
<div style="position: fixed; bottom: 30px; right: 30px; width: 280px;
            background: white; border-radius: 10px; padding: 15px; z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    <h4 style="margin: 0 0 12px 0; font-family: 'Segoe UI', Arial; color: #333;">
        📊 Risk Level Legend
    </h4>
    <div style="font-size: 13px; line-height: 1.8;">
        <div style="margin: 6px 0;">
            <span style="display: inline-block; width: 16px; height: 16px; background: #8B0000; 
                         border-radius: 50%; margin-right: 8px; vertical-align: middle; 
                         box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></span>
            <b>Extreme Risk (≥2.5)</b> — 52 sites
        </div>
        <div style="margin: 6px 0;">
            <span style="display: inline-block; width: 16px; height: 16px; background: #DC143C; 
                         border-radius: 50%; margin-right: 8px; vertical-align: middle;
                         box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></span>
            <b>High Risk (2.0-2.5)</b> — 315 sites
        </div>
        <div style="margin: 6px 0;">
            <span style="display: inline-block; width: 16px; height: 16px; background: #FF8C00; 
                         border-radius: 50%; margin-right: 8px; vertical-align: middle;
                         box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></span>
            <b>Medium Risk (1.0-2.0)</b> — 748 sites
        </div>
        <div style="margin: 6px 0;">
            <span style="display: inline-block; width: 16px; height: 16px; background: #228B22; 
                         border-radius: 50%; margin-right: 8px; vertical-align: middle;
                         box-shadow: 0 2px 4px rgba(0,0,0,0.2);"></span>
            <b>Low Risk (<1.0)</b> — 10 sites
        </div>
    </div>
    <hr style="margin: 12px 0; border: none; border-top: 1px solid #ddd;">
    <p style="margin: 8px 0 0 0; font-size: 11px; color: #666;">
        💡 Click markers for detailed site information<br>
        🔍 Use layer control to filter risk levels<br>
        🌐 Toggle between map themes
    </p>
</div>
'''
m1.get_root().html.add_child(folium.Element(legend_html))

# Add plugins
plugins.Fullscreen(position='topleft').add_to(m1)
plugins.LocateControl(position='topleft').add_to(m1)
plugins.MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m1)

# Add layer control
folium.LayerControl(position='topright', collapsed=False).add_to(m1)

m1.save('outputs/figures/enhanced_risk_map.html')
print("✓ Saved: outputs/figures/enhanced_risk_map.html")

# ============================================================================
# MAP 2: HEAT MAP (Risk Density)
# ============================================================================
print("\n" + "="*80)
print("MAP 2: HEAT MAP (Risk Density Visualization)")
print("="*80)

m2 = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=8,
    tiles='cartodbdark_matter'
)

# Prepare data for heatmap (weight by risk score)
heat_data = []
for _, row in df_sites.iterrows():
    heat_data.append([
        row['LATITUDE'],
        row['LONGITUDE'],
        row['avg_risk_score']  # Weight by risk
    ])

# Add heatmap layer
plugins.HeatMap(
    heat_data,
    name='Risk Density',
    min_opacity=0.3,
    max_opacity=0.8,
    radius=25,
    blur=35,
    gradient={
        0.0: 'blue',
        0.3: 'cyan',
        0.5: 'lime',
        0.7: 'yellow',
        0.9: 'orange',
        1.0: 'red'
    }
).add_to(m2)

# Add title
title_html2 = '''
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
            width: 500px; background: rgba(0,0,0,0.8); border-radius: 10px; 
            padding: 15px; z-index: 9999; color: white; text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.5);">
    <h2 style="margin: 0;">🔥 Heatwave Risk Density Map</h2>
    <p style="margin: 8px 0 0 0; font-size: 14px;">
        Hotter colors = Higher risk concentration
    </p>
</div>
'''
m2.get_root().html.add_child(folium.Element(title_html2))

plugins.Fullscreen().add_to(m2)
m2.save('outputs/figures/risk_heatmap.html')
print("✓ Saved: outputs/figures/risk_heatmap.html")

# ============================================================================
# MAP 3: CRITICAL EVENTS MAP (Size by DO Critical %)
# ============================================================================
print("\n" + "="*80)
print("MAP 3: CRITICAL EVENTS MAP (Bubble Size)")
print("="*80)

m3 = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=8,
    tiles='OpenStreetMap'
)

# Add circles sized by critical event percentage
for _, row in df_sites.iterrows():
    critical_pct = row['DO_critical_percent']
    
    # Size based on critical percentage (min 3, max 30)
    radius = max(3, min(30, critical_pct * 2))
    
    # Color based on percentage
    if critical_pct >= 20:
        color = 'darkred'
    elif critical_pct >= 15:
        color = 'red'
    elif critical_pct >= 10:
        color = 'orange'
    elif critical_pct >= 5:
        color = 'yellow'
    else:
        color = 'green'
    
    folium.Circle(
        location=[row['LATITUDE'], row['LONGITUDE']],
        radius=radius * 100,  # Convert to meters
        popup=f"<b>{row['SITE_ID']}</b><br>Critical Events: {critical_pct:.1f}%<br>Count: {row['DO_critical_baseline']:.0f}",
        tooltip=f"{row['SITE_ID']}: {critical_pct:.1f}% critical",
        color=color,
        fillColor=color,
        fillOpacity=0.6,
        weight=2
    ).add_to(m3)

title_html3 = '''
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
            width: 550px; background: white; border-radius: 10px; padding: 15px; 
            z-index: 9999; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
    <h2 style="margin: 0; color: #333;">⚠️ Critical Low-Oxygen Events</h2>
    <p style="margin: 8px 0 0 0; font-size: 14px; color: #666;">
        Bubble size = % of samples with DO < 5 mg/L
    </p>
</div>
'''
m3.get_root().html.add_child(folium.Element(title_html3))

plugins.Fullscreen().add_to(m3)
m3.save('outputs/figures/critical_events_map.html')
print("✓ Saved: outputs/figures/critical_events_map.html")

# ============================================================================
# MAP 4: SCENARIO COMPARISON (Side-by-Side)
# ============================================================================
print("\n" + "="*80)
print("MAP 4: SCENARIO COMPARISON (Current vs +2°C)")
print("="*80)

m4 = folium.plugins.DualMap(
    location=[center_lat, center_lon],
    zoom_start=8,
    tiles='cartodbpositron'
)

# Left map: Current conditions
for _, row in df_sites.iterrows():
    do_current = row['avg_DO']
    
    if do_current < 5:
        color = 'red'
    elif do_current < 6:
        color = 'orange'
    elif do_current < 7:
        color = 'yellow'
    else:
        color = 'green'
    
    folium.CircleMarker(
        location=[row['LATITUDE'], row['LONGITUDE']],
        radius=5,
        popup=f"<b>{row['SITE_ID']}</b><br>Current DO: {do_current:.1f} mg/L",
        color='white',
        weight=1,
        fillColor=color,
        fillOpacity=0.7
    ).add_to(m4.m1)

# Right map: +2°C scenario
for _, row in df_sites.iterrows():
    do_scenario = row['avg_DO_plus2']
    
    if do_scenario < 5:
        color = 'red'
    elif do_scenario < 6:
        color = 'orange'
    elif do_scenario < 7:
        color = 'yellow'
    else:
        color = 'green'
    
    folium.CircleMarker(
        location=[row['LATITUDE'], row['LONGITUDE']],
        radius=5,
        popup=f"<b>{row['SITE_ID']}</b><br>+2°C DO: {do_scenario:.1f} mg/L",
        color='white',
        weight=1,
        fillColor=color,
        fillOpacity=0.7
    ).add_to(m4.m2)

m4.save('outputs/figures/scenario_comparison_map.html')
print("✓ Saved: outputs/figures/scenario_comparison_map.html")

# ============================================================================
# MAP 5: SUMMER HOTSPOTS (June-Aug only)
# ============================================================================
print("\n" + "="*80)
print("MAP 5: SUMMER HOTSPOTS (June-August)")
print("="*80)

# Filter to summer data
df_summer_sites = df_timeseries[df_timeseries['month'].isin([6, 7, 8])].groupby('UNIQUE_ID').agg({
    'Latitude': 'first',
    'Longitude': 'first',
    'TEMP': 'mean',
    'DO': 'mean',
    'DO_critical': 'sum',
    'UNIQUE_ID': 'count'
}).reset_index(drop=True)

df_summer_sites.columns = ['LATITUDE', 'LONGITUDE', 'summer_temp', 'summer_DO', 'summer_critical', 'summer_samples']

m5 = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=8,
    tiles='https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png',
    attr='Stadia Maps'
)

for _, row in df_summer_sites.iterrows():
    temp = row['summer_temp']
    
    # Color by summer temperature
    if temp >= 24:
        color = '#8B0000'  # Very hot
        icon = '🔥'
    elif temp >= 22:
        color = '#FF4500'
        icon = '🌡️'
    elif temp >= 20:
        color = '#FFA500'
        icon = '☀️'
    else:
        color = '#4169E1'
        icon = '❄️'
    
    folium.CircleMarker(
        location=[row['LATITUDE'], row['LONGITUDE']],
        radius=7,
        popup=f"{icon} <b>Summer Stats</b><br>Avg Temp: {temp:.1f}°C<br>Avg DO: {row['summer_DO']:.1f} mg/L<br>Critical: {row['summer_critical']:.0f}",
        tooltip=f"Summer temp: {temp:.1f}°C",
        color='white',
        weight=2,
        fillColor=color,
        fillOpacity=0.8
    ).add_to(m5)

title_html5 = '''
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
            width: 500px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 10px; padding: 15px; z-index: 9999; color: white; text-align: center;">
    <h2 style="margin: 0;">☀️ Summer Temperature Hotspots</h2>
    <p style="margin: 8px 0 0 0;">June-August Average Water Temperature</p>
</div>
'''
m5.get_root().html.add_child(folium.Element(title_html5))

plugins.Fullscreen().add_to(m5)
m5.save('outputs/figures/summer_hotspots_map.html')
print("✓ Saved: outputs/figures/summer_hotspots_map.html")

# Summary
print("\n" + "="*80)
print("✅ ALL MAPS CREATED SUCCESSFULLY!")
print("="*80)
print("\n📍 Interactive Maps Created:")
print("  1. ✨ Enhanced Risk Map (beautiful styling, clusters)")
print("  2. 🔥 Heat Map (risk density visualization)")
print("  3. ⚠️  Critical Events Map (bubble size by % critical)")
print("  4. 🔄 Scenario Comparison (side-by-side current vs +2°C)")
print("  5. ☀️  Summer Hotspots (June-Aug temperature)")
print("\n💾 All saved to: outputs/figures/")
print("\n" + "="*80)
