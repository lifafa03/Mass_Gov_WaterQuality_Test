"""
Create Community-Friendly Infographic
Visual, accessible communication for residents
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import numpy as np
import json

print("="*80)
print("🎨 CREATING COMMUNITY INFOGRAPHIC")
print("="*80)

# Load data
with open('data/exports/strategic_insights.json', 'r') as f:
    insights = json.load(f)

df_sites = pd.read_csv('data/exports/heatwave_risk_dashboard_data.csv')

# Create large infographic figure
fig = plt.figure(figsize=(18, 24))
fig.suptitle('🌊 PROTECTING MASSACHUSETTS WATERWAYS FROM CLIMATE CHANGE 🌊\nWhat Residents Need to Know',
             fontsize=28, fontweight='bold', y=0.98)

# Colors
color_danger = '#DC143C'
color_warning = '#FF8C00'
color_safe = '#228B22'
color_info = '#4169E1'
color_bg = '#F0F8FF'

# ============================================================================
# SECTION 1: The Problem (Top)
# ============================================================================
ax1 = plt.subplot(6, 2, (1, 2))
ax1.axis('off')
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 5)

# Title box
rect = FancyBboxPatch((0.5, 3.5), 9, 1.3, boxstyle="round,pad=0.1", 
                       facecolor=color_danger, edgecolor='darkred', linewidth=3)
ax1.add_patch(rect)
ax1.text(5, 4.5, '🚨 THE PROBLEM', ha='center', va='top', 
         fontsize=24, fontweight='bold', color='white')
ax1.text(5, 4, 'Warmer Water = Less Oxygen for Fish & Wildlife', ha='center', va='top',
         fontsize=18, color='white', style='italic')

# Key stats
ax1.text(1, 2.8, '13.3%', ha='center', fontsize=48, fontweight='bold', color=color_danger)
ax1.text(1, 2.2, 'of summer water\nsamples already\nhave dangerously\nlow oxygen',
         ha='center', fontsize=12, va='top')

ax1.text(5, 2.8, '+21%', ha='center', fontsize=48, fontweight='bold', color=color_warning)
ax1.text(5, 2.2, 'MORE low-oxygen\nevents expected\nwith just +2°C\nwarming',
         ha='center', fontsize=12, va='top')

ax1.text(9, 2.8, '1,125', ha='center', fontsize=48, fontweight='bold', color=color_info)
ax1.text(9, 2.2, 'monitoring sites\ntracked across\nMassachusetts\nwaterways',
         ha='center', fontsize=12, va='top')

# ============================================================================
# SECTION 2: Why It Matters
# ============================================================================
ax2 = plt.subplot(6, 2, (3, 4))
ax2.axis('off')
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 4)

rect2 = FancyBboxPatch((0.5, 2.7), 9, 1.1, boxstyle="round,pad=0.1",
                        facecolor=color_warning, edgecolor='darkorange', linewidth=3)
ax2.add_patch(rect2)
ax2.text(5, 3.5, '❓ WHY IT MATTERS TO YOU', ha='center', va='top',
         fontsize=24, fontweight='bold', color='white')

impacts = [
    ('🐟', 'Fish Kills', 'Low oxygen = dead fish in rivers & ponds'),
    ('🏊', 'Swimming', 'Unsafe water, beach closures'),
    ('🎣', 'Fishing', 'Fewer trout, bass, other game fish'),
    ('💰', 'Property', 'Waterfront home values decline'),
    ('🌿', 'Ecology', 'Ecosystem collapse, algae blooms'),
    ('💧', 'Drinking', 'Higher water treatment costs')
]

for i, (icon, title, desc) in enumerate(impacts):
    row = i // 3
    col = i % 3
    x = 1.5 + col * 3
    y = 2 - row * 1.2
    
    ax2.text(x, y, icon, ha='center', fontsize=32)
    ax2.text(x, y - 0.35, title, ha='center', fontsize=14, fontweight='bold')
    ax2.text(x, y - 0.6, desc, ha='center', fontsize=9, style='italic')

# ============================================================================
# SECTION 3: What's Causing It (Factor Importance)
# ============================================================================
ax3 = plt.subplot(6, 2, (5, 6))
ax3.axis('off')
ax3.set_xlim(0, 10)
ax3.set_ylim(0, 5)

rect3 = FancyBboxPatch((0.5, 4), 9, 0.8, boxstyle="round,pad=0.1",
                        facecolor=color_info, edgecolor='darkblue', linewidth=3)
ax3.add_patch(rect3)
ax3.text(5, 4.5, '🔍 WHAT\'S CAUSING THE PROBLEM?', ha='center', va='top',
         fontsize=24, fontweight='bold', color='white')

# Factor bars
factors = [
    ('🌡️ Water Temperature', 24.7, 'Warmer water holds less O₂'),
    ('🔥 Extreme Heat', 23.5, 'Hot days are exponentially worse'),
    ('⚡ Pollution/Road Salt', 17.9, 'Urban runoff adds stress'),
    ('🏖️ Summer Season', 5.8, 'June-Aug = perfect storm')
]

y_pos = 3.2
for icon_text, pct, explanation in factors:
    # Bar
    bar_width = (pct / 30) * 6  # Scale to fit
    rect_bar = Rectangle((1.5, y_pos - 0.15), bar_width, 0.3,
                          facecolor=color_danger, alpha=0.7, edgecolor='darkred', linewidth=2)
    ax3.add_patch(rect_bar)
    
    # Labels
    ax3.text(1, y_pos, icon_text, ha='right', fontsize=14, fontweight='bold')
    ax3.text(8, y_pos, f'{pct:.1f}%', ha='left', fontsize=16, fontweight='bold', color=color_danger)
    ax3.text(1.5, y_pos - 0.4, explanation, ha='left', fontsize=10, style='italic', color='gray')
    
    y_pos -= 0.9

# ============================================================================
# SECTION 4: What-If Scenarios
# ============================================================================
ax4 = plt.subplot(6, 2, (7, 8))
ax4.axis('off')
ax4.set_xlim(0, 10)
ax4.set_ylim(0, 4.5)

rect4 = FancyBboxPatch((0.5, 3.5), 9, 0.8, boxstyle="round,pad=0.1",
                        facecolor='#9370DB', edgecolor='purple', linewidth=3)
ax4.add_patch(rect4)
ax4.text(5, 4, '🔮 FUTURE SCENARIOS: What Could Happen?', ha='center', va='top',
         fontsize=24, fontweight='bold', color='white')

scenarios = [
    ('🌧️ More Rain\n(Climate)', '+0.19 mg/L', 'GOOD', color_safe, 'Dilutes pollution'),
    ('🧂 More Road Salt\n(30%)', '-0.25 mg/L', 'BAD', color_warning, '~200 new critical events'),
    ('🔥 Heat Wave\n(+3°C)', '-0.21 mg/L', 'BAD', color_warning, '2.9% oxygen loss'),
    ('💀 Perfect Storm\n(All 3)', '-0.62 mg/L', 'CRISIS', color_danger, '17% of water unsafe!')
]

for i, (name, change, label, color, impact) in enumerate(scenarios):
    x = 1.5 + (i * 2.2)
    y = 2.5
    
    # Circle for scenario
    circle = Circle((x, y), 0.6, facecolor=color, alpha=0.3, edgecolor=color, linewidth=3)
    ax4.add_patch(circle)
    
    ax4.text(x, y + 0.9, name, ha='center', fontsize=11, fontweight='bold')
    ax4.text(x, y, change, ha='center', fontsize=14, fontweight='bold', color='black')
    ax4.text(x, y - 0.8, label, ha='center', fontsize=12, fontweight='bold', 
             color='white', bbox=dict(boxstyle='round', facecolor=color, alpha=0.8))
    ax4.text(x, y - 1.3, impact, ha='center', fontsize=9, style='italic')

# ============================================================================
# SECTION 5: What YOU Can Do
# ============================================================================
ax5 = plt.subplot(6, 2, (9, 10))
ax5.axis('off')
ax5.set_xlim(0, 10)
ax5.set_ylim(0, 6)

rect5 = FancyBboxPatch((0.5, 5), 9, 0.8, boxstyle="round,pad=0.1",
                        facecolor=color_safe, edgecolor='darkgreen', linewidth=3)
ax5.add_patch(rect5)
ax5.text(5, 5.5, '✅ WHAT YOU CAN DO TO HELP', ha='center', va='top',
         fontsize=24, fontweight='bold', color='white')

actions = [
    ('🌳', 'Plant Trees', 'Shade streams to keep\nwater cool'),
    ('🧂', 'Less Salt', 'Use 30% less road salt\nin winter'),
    ('🚗', 'Drive Less', 'Reduce pavement heat\nand runoff pollution'),
    ('💧', 'Save Water', 'Less lawn watering\nin summer'),
    ('🏡', 'Rain Gardens', 'Capture stormwater\nat home'),
    ('📢', 'Spread Word', 'Tell neighbors\nabout this issue')
]

for i, (icon, action, desc) in enumerate(actions):
    row = i // 3
    col = i % 3
    x = 1.5 + col * 3
    y = 4.2 - row * 2
    
    # Box
    rect_action = FancyBboxPatch((x - 0.8, y - 0.9), 1.6, 1.8, 
                                 boxstyle="round,pad=0.1",
                                 facecolor='lightgreen', alpha=0.3, 
                                 edgecolor=color_safe, linewidth=2)
    ax5.add_patch(rect_action)
    
    ax5.text(x, y + 0.5, icon, ha='center', fontsize=36)
    ax5.text(x, y - 0.1, action, ha='center', fontsize=14, fontweight='bold')
    ax5.text(x, y - 0.6, desc, ha='center', fontsize=10, style='italic')

# ============================================================================
# SECTION 6: Take Action
# ============================================================================
ax6 = plt.subplot(6, 2, (11, 12))
ax6.axis('off')
ax6.set_xlim(0, 10)
ax6.set_ylim(0, 2.5)

rect6 = FancyBboxPatch((0.5, 1.5), 9, 0.8, boxstyle="round,pad=0.1",
                        facecolor='#FFD700', edgecolor='#DAA520', linewidth=3)
ax6.add_patch(rect6)
ax6.text(5, 2, '📞 TAKE ACTION TODAY', ha='center', va='top',
         fontsize=24, fontweight='bold', color='darkred')

# Contact info
ax6.text(2.5, 1, '🌐 Learn More:', ha='right', fontsize=14, fontweight='bold')
ax6.text(2.6, 1, 'mass.gov/massdep', ha='left', fontsize=14, color=color_info)

ax6.text(2.5, 0.5, '📧 Report Issues:', ha='right', fontsize=14, fontweight='bold')
ax6.text(2.6, 0.5, 'waterquality@mass.gov', ha='left', fontsize=14, color=color_info)

ax6.text(7.5, 1, '📱 Water Quality App:', ha='right', fontsize=14, fontweight='bold')
ax6.text(7.6, 1, 'Download "MA Water Watch"', ha='left', fontsize=14, color=color_info)

ax6.text(7.5, 0.5, '🤝 Volunteer:', ha='right', fontsize=14, fontweight='bold')
ax6.text(7.6, 0.5, 'Join "Cool Our Streams"', ha='left', fontsize=14, color=color_info)

# Footer
ax6.text(5, -0.2, 'Data: MassDEP 2005-2020 • 1,125 sites • 9,323 measurements',
         ha='center', fontsize=10, style='italic', color='gray')
ax6.text(5, -0.5, 'Analysis: Massachusetts Department of Environmental Protection • November 2025',
         ha='center', fontsize=10, style='italic', color='gray')

plt.tight_layout(rect=[0, 0, 1, 0.98])

# Save
output_path = 'outputs/figures/community_infographic.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✅ Community infographic saved: {output_path}")
print(f"   Resolution: 300 DPI (print quality)")
print(f"   Size: 18\" x 24\" (standard poster)")
print(f"   Format: PNG")

print("\n" + "="*80)
print("🎨 INFOGRAPHIC COMPLETE")
print("="*80)
print("\nSuggested Uses:")
print("  • Print posters for town halls and libraries")
print("  • Share on social media")
print("  • Include in community newsletters")
print("  • Present at public meetings")
print("  • Distribute to schools")

plt.show()
