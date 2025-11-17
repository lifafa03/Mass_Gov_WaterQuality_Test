"""
Visualization Module for MA Waterways Heatwave Risk Analysis

This module contains functions for creating publication-quality visualizations
of water quality trends, risk patterns, and climate scenarios.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


def plot_monthly_do_pattern(df, do_column='do', save_path=None):
    """
    Plot seasonal U-curve pattern of dissolved oxygen levels.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with month and DO columns
    do_column : str
        Dissolved oxygen column name
    save_path : str, optional
        Path to save figure
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Calculate monthly statistics
    monthly_stats = df.groupby('month')[do_column].agg(['mean', 'std', 'count'])
    monthly_stats = monthly_stats.reindex(range(1, 13))
    
    # Plot mean with error bars
    ax.errorbar(monthly_stats.index, 
                monthly_stats['mean'],
                yerr=monthly_stats['std'],
                marker='o', 
                markersize=8,
                capsize=5,
                capthick=2,
                linewidth=2,
                color='steelblue',
                label='Mean ± Std Dev')
    
    # Add critical threshold line
    ax.axhline(y=5, color='red', linestyle='--', linewidth=2, 
               label='Critical Threshold (5 mg/L)', alpha=0.7)
    
    # Formatting
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_names)
    ax.set_xlabel('Month', fontsize=12, fontweight='bold')
    ax.set_ylabel('Dissolved Oxygen (mg/L)', fontsize=12, fontweight='bold')
    ax.set_title('Seasonal Pattern of Dissolved Oxygen in MA Waterways\n(2005-2020)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Add sample size annotation
    for idx, row in monthly_stats.iterrows():
        if not pd.isna(row['mean']):
            ax.annotate(f"n={int(row['count'])}", 
                       xy=(idx, row['mean']), 
                       xytext=(0, 10),
                       textcoords='offset points',
                       ha='center',
                       fontsize=8,
                       alpha=0.6)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved figure to {save_path}")
    
    return fig, ax


def plot_temp_do_relationship(df, temp_column='temp', do_column='do', 
                              save_path=None):
    """
    Scatterplot of temperature vs DO with regression line.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with temperature and DO
    temp_column : str
        Temperature column name
    do_column : str
        DO column name
    save_path : str, optional
        Path to save figure
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create sample for visualization (to avoid overplotting)
    if len(df) > 10000:
        df_sample = df.sample(n=10000, random_state=42)
    else:
        df_sample = df
    
    # Filter valid data
    df_plot = df_sample[[temp_column, do_column]].dropna()
    
    # Scatter plot with color gradient
    scatter = ax.scatter(df_plot[temp_column], 
                        df_plot[do_column],
                        c=df_plot[temp_column],
                        cmap='RdYlBu_r',
                        alpha=0.5,
                        s=20,
                        edgecolors='none')
    
    # Add regression line
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, std_err = linregress(df_plot[temp_column], 
                                                             df_plot[do_column])
    
    x_line = np.linspace(df_plot[temp_column].min(), df_plot[temp_column].max(), 100)
    y_line = slope * x_line + intercept
    
    ax.plot(x_line, y_line, 'r-', linewidth=3, alpha=0.8,
            label=f'Linear Fit: DO = {slope:.3f}×TEMP + {intercept:.2f}\nR² = {r_value**2:.3f}')
    
    # Critical zones
    ax.axhline(y=5, color='darkred', linestyle='--', linewidth=2, 
               alpha=0.7, label='Critical DO (5 mg/L)')
    ax.axvline(x=25, color='orange', linestyle='--', linewidth=2, 
               alpha=0.7, label='Warm Water (25°C)')
    
    # Formatting
    ax.set_xlabel('Water Temperature (°C)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Dissolved Oxygen (mg/L)', fontsize=12, fontweight='bold')
    ax.set_title('Temperature-Oxygen Relationship in MA Waterways\n(2005-2020)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, label='Temperature (°C)')
    
    # Stats annotation
    stats_text = f'n = {len(df_plot):,}\nCorr = {r_value:.3f}'
    ax.text(0.02, 0.98, stats_text,
            transform=ax.transAxes,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved figure to {save_path}")
    
    return fig, ax


def plot_summer_temp_trend(df, temp_column='temp', save_path=None):
    """
    Plot summer temperature trends over years.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with year, is_summer, and temperature
    temp_column : str
        Temperature column name
    save_path : str, optional
        Path to save figure
    """
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Filter summer data
    if 'is_summer' in df.columns:
        df_summer = df[df['is_summer'] == 1].copy()
    else:
        df_summer = df[df['month'].isin([6, 7, 8])].copy()
    
    # Calculate yearly summer averages
    yearly_temp = df_summer.groupby('year')[temp_column].agg(['mean', 'std', 'count'])
    
    # Plot with error bars
    ax.errorbar(yearly_temp.index,
                yearly_temp['mean'],
                yerr=yearly_temp['std'],
                marker='o',
                markersize=6,
                capsize=4,
                linewidth=2,
                color='orangered',
                label='Summer Average ± Std Dev')
    
    # Add trend line
    from scipy.stats import linregress
    slope, intercept, r_value, p_value, std_err = linregress(yearly_temp.index, 
                                                             yearly_temp['mean'])
    
    trend_line = slope * yearly_temp.index + intercept
    ax.plot(yearly_temp.index, trend_line, 'k--', linewidth=2, alpha=0.7,
            label=f'Trend: {slope:.3f}°C/year (p={p_value:.4f})')
    
    # Formatting
    ax.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax.set_ylabel('Summer Water Temperature (°C)', fontsize=12, fontweight='bold')
    ax.set_title('Summer Water Temperature Trends in MA Waterways\n(June-August, 2005-2020)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # Highlight warming
    if slope > 0:
        total_increase = slope * (yearly_temp.index.max() - yearly_temp.index.min())
        ax.text(0.98, 0.02, 
                f'Total warming: {total_increase:.2f}°C over period',
                transform=ax.transAxes,
                ha='right',
                va='bottom',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.6),
                fontsize=11)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved figure to {save_path}")
    
    return fig, ax


def plot_correlation_heatmap(df, columns=None, save_path=None):
    """
    Plot correlation heatmap for numeric features.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    columns : list, optional
        Specific columns to include
    save_path : str, optional
        Path to save figure
    """
    if columns is None:
        # Auto-select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        # Exclude ID and count columns
        exclude = ['year', 'month', 'day', 'day_of_year', 'week_of_year']
        columns = [col for col in numeric_cols if col not in exclude][:15]  # Limit to 15
    
    # Calculate correlation matrix
    corr_matrix = df[columns].corr()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create heatmap
    sns.heatmap(corr_matrix,
                annot=True,
                fmt='.2f',
                cmap='coolwarm',
                center=0,
                vmin=-1,
                vmax=1,
                square=True,
                linewidths=0.5,
                cbar_kws={'label': 'Correlation Coefficient'},
                ax=ax)
    
    ax.set_title('Water Quality Parameters Correlation Matrix\n(MA Waterways 2005-2020)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved figure to {save_path}")
    
    return fig, ax


def plot_risk_distribution(df, risk_column='risk_score', save_path=None):
    """
    Plot risk score distribution.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with risk scores
    risk_column : str
        Risk score column name
    save_path : str, optional
        Path to save figure
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Histogram
    ax1.hist(df[risk_column].dropna(), bins=50, color='coral', 
             edgecolor='black', alpha=0.7)
    ax1.axvline(df[risk_column].median(), color='red', linestyle='--', 
                linewidth=2, label=f'Median: {df[risk_column].median():.1f}')
    ax1.axvline(df[risk_column].mean(), color='blue', linestyle='--', 
                linewidth=2, label=f'Mean: {df[risk_column].mean():.1f}')
    ax1.set_xlabel('Risk Score', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax1.set_title('Distribution of Heat-Stress Risk Scores', 
                  fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Category counts
    if 'risk_category' in df.columns:
        category_order = ['Low', 'Moderate', 'High', 'Very High', 'Extreme']
        category_counts = df['risk_category'].value_counts()
        category_counts = category_counts.reindex(category_order, fill_value=0)
        
        colors = ['green', 'yellow', 'orange', 'orangered', 'darkred']
        bars = ax2.bar(range(len(category_counts)), category_counts.values, 
                      color=colors, edgecolor='black', alpha=0.7)
        
        ax2.set_xticks(range(len(category_counts)))
        ax2.set_xticklabels(category_counts.index, rotation=45)
        ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax2.set_title('Risk Category Distribution', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}',
                    ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved figure to {save_path}")
    
    return fig, (ax1, ax2)


def plot_scenario_comparison(df_baseline, df_scenario, 
                             metric='do', save_path=None):
    """
    Compare baseline vs climate scenario (+2°C warming).
    
    Parameters:
    -----------
    df_baseline : pd.DataFrame
        Baseline (historical) data
    df_scenario : pd.DataFrame
        Scenario (warmed) data
    metric : str
        Metric to compare ('do', 'risk_score', etc.)
    save_path : str, optional
        Path to save figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Monthly averages comparison
    ax = axes[0, 0]
    baseline_monthly = df_baseline.groupby('month')[metric].mean()
    scenario_monthly = df_scenario.groupby('month')[metric].mean()
    
    months = range(1, 13)
    month_names = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']
    
    ax.plot(months, baseline_monthly.reindex(months), 'o-', linewidth=2, 
            markersize=8, label='Baseline (2005-2020)', color='steelblue')
    ax.plot(months, scenario_monthly.reindex(months), 's-', linewidth=2, 
            markersize=8, label='+2°C Scenario', color='orangered')
    
    ax.set_xticks(months)
    ax.set_xticklabels(month_names)
    ax.set_xlabel('Month', fontweight='bold')
    ax.set_ylabel(f'{metric.upper()}', fontweight='bold')
    ax.set_title('Monthly Comparison', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Distribution comparison
    ax = axes[0, 1]
    ax.hist([df_baseline[metric].dropna(), df_scenario[metric].dropna()],
            bins=40, label=['Baseline', '+2°C Scenario'],
            color=['steelblue', 'orangered'], alpha=0.6, edgecolor='black')
    ax.set_xlabel(f'{metric.upper()}', fontweight='bold')
    ax.set_ylabel('Frequency', fontweight='bold')
    ax.set_title('Distribution Comparison', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Critical events comparison
    ax = axes[1, 0]
    if 'DO_critical' in df_baseline.columns:
        baseline_critical = df_baseline.groupby('year')['DO_critical'].sum()
        scenario_critical = df_scenario.groupby('year')['DO_critical'].sum()
        
        years = baseline_critical.index
        width = 0.35
        x = np.arange(len(years))
        
        ax.bar(x - width/2, baseline_critical.values, width, 
               label='Baseline', color='steelblue', alpha=0.7)
        ax.bar(x + width/2, scenario_critical.values, width, 
               label='+2°C Scenario', color='orangered', alpha=0.7)
        
        ax.set_xticks(x[::2])  # Every other year
        ax.set_xticklabels(years[::2], rotation=45)
        ax.set_xlabel('Year', fontweight='bold')
        ax.set_ylabel('Critical DO Events', fontweight='bold')
        ax.set_title('Critical Oxygen Events by Year', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    # 4. Summary statistics
    ax = axes[1, 1]
    ax.axis('off')
    
    stats_text = f"""
    SCENARIO IMPACT SUMMARY
    {'='*40}
    
    Baseline (2005-2020):
      Mean {metric}: {df_baseline[metric].mean():.2f}
      Std Dev: {df_baseline[metric].std():.2f}
      
    +2°C Warming Scenario:
      Mean {metric}: {df_scenario[metric].mean():.2f}
      Std Dev: {df_scenario[metric].std():.2f}
      
    Change:
      Δ{metric}: {df_scenario[metric].mean() - df_baseline[metric].mean():.2f}
      % Change: {(df_scenario[metric].mean() / df_baseline[metric].mean() - 1) * 100:.1f}%
    """
    
    if 'DO_critical' in df_baseline.columns:
        baseline_events = df_baseline['DO_critical'].sum()
        scenario_events = df_scenario['DO_critical'].sum()
        stats_text += f"""
    Critical Events:
      Baseline: {baseline_events:,}
      Scenario: {scenario_events:,}
      Increase: {scenario_events - baseline_events:,} ({(scenario_events/baseline_events - 1)*100:.1f}%)
    """
    
    ax.text(0.1, 0.9, stats_text, transform=ax.transAxes,
            fontsize=11, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle('Climate Scenario Analysis: +2°C Warming Impact',
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved figure to {save_path}")
    
    return fig, axes


def create_summary_dashboard(df, output_dir):
    """
    Create a multi-panel summary dashboard.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Processed dataframe with all features
    output_dir : str or Path
        Directory to save figures
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating summary dashboard...")
    
    # Generate all key visualizations
    plot_monthly_do_pattern(df, save_path=output_dir / '01_monthly_do_pattern.png')
    plot_temp_do_relationship(df, save_path=output_dir / '02_temp_do_relationship.png')
    plot_summer_temp_trend(df, save_path=output_dir / '03_summer_temp_trend.png')
    plot_correlation_heatmap(df, save_path=output_dir / '04_correlation_heatmap.png')
    
    if 'risk_score' in df.columns:
        plot_risk_distribution(df, save_path=output_dir / '05_risk_distribution.png')
    
    print(f"\n✓ Dashboard figures saved to {output_dir}")
