"""
Create Interactive Geographic Map of MA Waterways Risk Sites
Shows all 1,125 monitoring sites on actual Massachusetts map
Color-coded by risk score with interactive popups
"""

import pandas as pd
import folium
from folium import plugins
import numpy as np

print("="*80)
print("CREATING INTERACTIVE GEOGRAPHIC MAP")
print("="*80)

# Load dashboard data
print("\n📊 Loading site data...")
df = pd.read_csv('data/exports/heatwave_risk_dashboard_data.csv')
print(f"✓ Loaded {len(df):,} sites")

# Remove sites with missing coordinates
df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])
print(f"✓ Sites with valid coordinates: {len(df):,}")

# Calculate map center (Massachusetts centroid)
center_lat = df['LATITUDE'].mean()
center_lon = df['LONGITUDE'].mean()
print(f"✓ Map center: {center_lat:.4f}, {center_lon:.4f}")

# Create base map centered on Massachusetts
print("\n🗺️  Creating base map...")
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=8,
    tiles='OpenStreetMap'
)

# Add alternative tile layers
folium.TileLayer('cartodbpositron', name='Light Map').add_to(m)
folium.TileLayer('cartodbdark_matter', name='Dark Map').add_to(m)

# Define color function based on risk score
def get_color(risk_score):
    """Return color based on risk score"""
    if pd.isna(risk_score):
        return 'gray'
    elif risk_score >= 2.5:
        return 'darkred'  # Extreme risk
    elif risk_score >= 2.0:
        return 'red'      # High risk
    elif risk_score >= 1.5:
        return 'orange'   # Medium-high risk
    elif risk_score >= 1.0:
        return 'yellow'   # Medium risk
    else:
        return 'green'    # Low risk

# Create feature groups for different risk levels
print("\n🎨 Creating risk layer groups...")
extreme_risk = folium.FeatureGroup(name='Extreme Risk (≥2.5)', show=True)
high_risk = folium.FeatureGroup(name='High Risk (2.0-2.5)', show=True)
medium_high_risk = folium.FeatureGroup(name='Medium-High Risk (1.5-2.0)', show=True)
medium_risk = folium.FeatureGroup(name='Medium Risk (1.0-1.5)', show=True)
low_risk = folium.FeatureGroup(name='Low Risk (<1.0)', show=True)

# Add markers for each site
print("\n📍 Adding site markers...")
site_counts = {
    'extreme': 0,
    'high': 0,
    'medium_high': 0,
    'medium': 0,
    'low': 0
}

for idx, row in df.iterrows():
    # Get site info
    site_id = row['SITE_ID']
    lat = row['LATITUDE']
    lon = row['LONGITUDE']
    risk_score = row['avg_risk_score']
    avg_temp = row['avg_TEMP']
    avg_do = row['avg_DO']
    critical_pct = row['DO_critical_percent']
    scenario_temp = row['avg_TEMP_plus2']
    scenario_do = row['avg_DO_plus2']
    new_critical = row['new_critical_events']
    
    # Get watershed if available
    watershed = row.get('watershed', 'Unknown')
    
    # Determine color and group
    color = get_color(risk_score)
    
    # Create popup HTML
    popup_html = f"""
    <div style="font-family: Arial; width: 300px;">
        <h4 style="margin: 0 0 10px 0; color: {color};">
            {site_id}
        </h4>
        <b>Watershed:</b> {watershed}<br>
        <b>Risk Score:</b> {risk_score:.2f}<br>
        <hr style="margin: 8px 0;">
        <b>Current Conditions:</b><br>
        • Avg Temp: {avg_temp:.1f}°C<br>
        • Avg DO: {avg_do:.1f} mg/L<br>
        • Critical Events: {critical_pct:.1f}%<br>
        <hr style="margin: 8px 0;">
        <b>+2°C Scenario:</b><br>
        • Projected Temp: {scenario_temp:.1f}°C<br>
        • Projected DO: {scenario_do:.1f} mg/L<br>
        • New Critical Events: <span style="color: red;">+{new_critical:.0f}</span><br>
    </div>
    """
    
    # Create marker
    marker = folium.CircleMarker(
        location=[lat, lon],
        radius=6,
        popup=folium.Popup(popup_html, max_width=300),
        color=color,
        fill=True,
        fillColor=color,
        fillOpacity=0.7,
        weight=2
    )
    
    # Add to appropriate group
    if risk_score >= 2.5:
        marker.add_to(extreme_risk)
        site_counts['extreme'] += 1
    elif risk_score >= 2.0:
        marker.add_to(high_risk)
        site_counts['high'] += 1
    elif risk_score >= 1.5:
        marker.add_to(medium_high_risk)
        site_counts['medium_high'] += 1
    elif risk_score >= 1.0:
        marker.add_to(medium_risk)
        site_counts['medium'] += 1
    else:
        marker.add_to(low_risk)
        site_counts['low'] += 1

# Add feature groups to map
extreme_risk.add_to(m)
high_risk.add_to(m)
medium_high_risk.add_to(m)
medium_risk.add_to(m)
low_risk.add_to(m)

# Add layer control
folium.LayerControl(collapsed=False).add_to(m)

# Add title
title_html = '''
<div style="position: fixed; 
            top: 10px; left: 50px; width: 500px; height: 90px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:16px; padding: 10px; opacity: 0.9;">
    <h3 style="margin: 0;">MA Waterways Heatwave Risk Assessment</h3>
    <p style="margin: 5px 0 0 0; font-size: 12px;">
        Interactive map of 1,125 monitoring sites (2005-2020)<br>
        Click markers for site details and +2°C scenario impact
    </p>
</div>
'''
m.get_root().html.add_child(folium.Element(title_html))

# Add legend
legend_html = f'''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 200px; 
            background-color: white; border:2px solid grey; z-index:9999; 
            font-size:14px; padding: 10px; opacity: 0.9;">
    <h4 style="margin: 0 0 10px 0;">Risk Level Legend</h4>
    <p style="margin: 3px 0;"><span style="color: darkred;">●</span> Extreme (≥2.5): {site_counts['extreme']} sites</p>
    <p style="margin: 3px 0;"><span style="color: red;">●</span> High (2.0-2.5): {site_counts['high']} sites</p>
    <p style="margin: 3px 0;"><span style="color: orange;">●</span> Med-High (1.5-2.0): {site_counts['medium_high']} sites</p>
    <p style="margin: 3px 0;"><span style="color: yellow;">●</span> Medium (1.0-1.5): {site_counts['medium']} sites</p>
    <p style="margin: 3px 0;"><span style="color: green;">●</span> Low (<1.0): {site_counts['low']} sites</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Add fullscreen button
plugins.Fullscreen().add_to(m)

# Add search/locate control
plugins.LocateControl().add_to(m)

# Save map
output_path = 'outputs/figures/interactive_risk_map.html'
m.save(output_path)

print(f"\n✓ Map created successfully!")
print(f"\n📊 Site Distribution:")
print(f"  • Extreme Risk (≥2.5): {site_counts['extreme']} sites")
print(f"  • High Risk (2.0-2.5): {site_counts['high']} sites")
print(f"  • Medium-High Risk (1.5-2.0): {site_counts['medium_high']} sites")
print(f"  • Medium Risk (1.0-1.5): {site_counts['medium']} sites")
print(f"  • Low Risk (<1.0): {site_counts['low']} sites")
print(f"\n💾 Saved to: {output_path}")
print(f"\n🌐 Opening map in browser...")

print("\n" + "="*80)
print("MAP FEATURES:")
print("="*80)
print("✓ Interactive markers - Click for site details")
print("✓ Layer controls - Toggle risk levels on/off")
print("✓ Multiple base maps - Switch between map styles")
print("✓ Fullscreen mode - Expand to full screen")
print("✓ Location control - Find your current location")
print("✓ Zoom/pan - Navigate across Massachusetts")
print("\n" + "="*80)
print("✅ INTERACTIVE MAP COMPLETE!")
print("="*80 + "\n")
