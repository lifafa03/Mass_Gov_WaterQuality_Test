"""
Risk Modeling Module for MA Waterways Heatwave Risk Analysis

This module contains functions for scenario modeling, risk predictions,
and climate impact simulations.
"""

import pandas as pd
import numpy as np
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')


def estimate_do_from_temp(temp, method='empirical', params=None):
    """
    Estimate dissolved oxygen from water temperature.
    
    Methods:
    - 'empirical': Based on observed data relationship
    - 'saturation': Based on Henry's Law (theoretical saturation)
    - 'linear': Simple linear regression model
    
    Parameters:
    -----------
    temp : float or array-like
        Water temperature in Celsius
    method : str
        Estimation method
    params : dict, optional
        Model parameters (slope, intercept for linear)
        
    Returns:
    --------
    float or array-like
        Estimated DO in mg/L
    """
    temp = np.asarray(temp)
    
    if method == 'saturation':
        # Henry's Law approximation for DO saturation
        # Formula: DO_sat = 14.652 - 0.41022*T + 0.007991*T^2 - 0.000077774*T^3
        do_sat = (14.652 - 0.41022 * temp + 
                  0.007991 * temp**2 - 
                  0.000077774 * temp**3)
        return do_sat
    
    elif method == 'linear':
        # Linear relationship from observed data
        if params is None:
            # Default parameters (approximate)
            slope = -0.25
            intercept = 12.0
        else:
            slope = params.get('slope', -0.25)
            intercept = params.get('intercept', 12.0)
        
        return slope * temp + intercept
    
    elif method == 'empirical':
        # Empirical model combining saturation with correction factor
        # Assumes ~70% of saturation value (typical for natural systems)
        do_sat = estimate_do_from_temp(temp, method='saturation')
        return do_sat * 0.70
    
    else:
        raise ValueError(f"Unknown method: {method}")


def fit_temp_do_model(df, temp_column='temp', do_column='do'):
    """
    Fit a temperature-DO relationship model from observed data.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with temperature and DO measurements
    temp_column : str
        Temperature column name
    do_column : str
        DO column name
        
    Returns:
    --------
    dict
        Model parameters and statistics
    """
    # Filter valid data
    data = df[[temp_column, do_column]].dropna()
    
    if len(data) < 10:
        print("Warning: Insufficient data for model fitting")
        return None
    
    # Fit linear regression
    slope, intercept, r_value, p_value, std_err = linregress(
        data[temp_column], data[do_column]
    )
    
    model = {
        'method': 'linear_regression',
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value**2,
        'p_value': p_value,
        'std_error': std_err,
        'n_samples': len(data),
        'temp_range': (data[temp_column].min(), data[temp_column].max()),
        'do_range': (data[do_column].min(), data[do_column].max())
    }
    
    print("Temperature-DO Model Fit:")
    print(f"  Equation: DO = {slope:.4f} × TEMP + {intercept:.4f}")
    print(f"  R² = {r_value**2:.4f}")
    print(f"  p-value = {p_value:.6f}")
    print(f"  n = {len(data):,}")
    
    return model


def simulate_warming_scenario(df, temp_column='temp', do_column='do',
                              warming_amount=2.0, model=None):
    """
    Simulate the impact of water temperature increase on DO levels.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Baseline dataframe
    temp_column : str
        Temperature column name
    do_column : str
        DO column name
    warming_amount : float
        Temperature increase in °C
    model : dict, optional
        Pre-fitted temp-DO model. If None, will fit from data.
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with simulated scenario values
    """
    df_scenario = df.copy()
    
    # Apply temperature increase
    if temp_column in df_scenario.columns:
        df_scenario[f'{temp_column}_original'] = df_scenario[temp_column]
        df_scenario[temp_column] = df_scenario[temp_column] + warming_amount
    else:
        print(f"Warning: {temp_column} not found in dataframe")
        return df_scenario
    
    # Estimate DO change
    if model is None:
        model = fit_temp_do_model(df, temp_column, do_column)
    
    if model and do_column in df_scenario.columns:
        # Calculate expected DO reduction
        # Method 1: Use linear model
        do_reduction = model['slope'] * warming_amount
        
        df_scenario[f'{do_column}_original'] = df_scenario[do_column]
        df_scenario[do_column] = df_scenario[do_column] + do_reduction  # Note: slope is negative
        
        # Ensure DO doesn't go below 0
        df_scenario[do_column] = df_scenario[do_column].clip(lower=0)
        
        print(f"\nWarming Scenario: +{warming_amount}°C")
        print(f"  Expected DO change: {do_reduction:.3f} mg/L")
        print(f"  Baseline mean DO: {df[do_column].mean():.2f} mg/L")
        print(f"  Scenario mean DO: {df_scenario[do_column].mean():.2f} mg/L")
    
    return df_scenario


def calculate_scenario_impacts(df_baseline, df_scenario, do_column='do'):
    """
    Calculate detailed impacts of warming scenario.
    
    Parameters:
    -----------
    df_baseline : pd.DataFrame
        Baseline (historical) data
    df_scenario : pd.DataFrame
        Scenario (warmed) data
    do_column : str
        DO column name
        
    Returns:
    --------
    dict
        Impact metrics
    """
    impacts = {}
    
    # DO changes
    baseline_do_mean = df_baseline[do_column].mean()
    scenario_do_mean = df_scenario[do_column].mean()
    
    impacts['do_mean_baseline'] = baseline_do_mean
    impacts['do_mean_scenario'] = scenario_do_mean
    impacts['do_mean_change'] = scenario_do_mean - baseline_do_mean
    impacts['do_pct_change'] = (scenario_do_mean / baseline_do_mean - 1) * 100
    
    # Critical events (DO < 5 mg/L)
    if 'DO_critical' in df_baseline.columns:
        baseline_critical = df_baseline['DO_critical'].sum()
        scenario_critical = df_scenario['DO_critical'].sum()
        
        impacts['critical_events_baseline'] = int(baseline_critical)
        impacts['critical_events_scenario'] = int(scenario_critical)
        impacts['critical_events_increase'] = int(scenario_critical - baseline_critical)
        impacts['critical_events_pct_increase'] = (
            (scenario_critical / baseline_critical - 1) * 100 
            if baseline_critical > 0 else np.inf
        )
    
    # Stress events (combined high temp + low DO)
    if 'stress_combo' in df_baseline.columns:
        baseline_stress = df_baseline['stress_combo'].sum()
        scenario_stress = df_scenario['stress_combo'].sum()
        
        impacts['stress_events_baseline'] = int(baseline_stress)
        impacts['stress_events_scenario'] = int(scenario_stress)
        impacts['stress_events_increase'] = int(scenario_stress - baseline_stress)
    
    # Risk score changes
    if 'risk_score' in df_baseline.columns:
        baseline_risk_mean = df_baseline['risk_score'].mean()
        scenario_risk_mean = df_scenario['risk_score'].mean()
        
        impacts['risk_score_baseline'] = baseline_risk_mean
        impacts['risk_score_scenario'] = scenario_risk_mean
        impacts['risk_score_increase'] = scenario_risk_mean - baseline_risk_mean
    
    # Sites affected
    if 'site_id' in df_baseline.columns and 'DO_critical' in df_baseline.columns:
        baseline_sites_affected = df_baseline[df_baseline['DO_critical'] == 1]['site_id'].nunique()
        scenario_sites_affected = df_scenario[df_scenario['DO_critical'] == 1]['site_id'].nunique()
        
        impacts['sites_affected_baseline'] = baseline_sites_affected
        impacts['sites_affected_scenario'] = scenario_sites_affected
        impacts['sites_affected_increase'] = scenario_sites_affected - baseline_sites_affected
    
    # Print summary
    print("\n" + "="*60)
    print("SCENARIO IMPACT SUMMARY")
    print("="*60)
    
    for key, value in impacts.items():
        print(f"{key:.<50} {value:.2f}" if isinstance(value, float) else f"{key:.<50} {value}")
    
    print("="*60)
    
    return impacts


def identify_vulnerable_sites(df, site_column='site_id', risk_column='risk_score',
                              threshold=60):
    """
    Identify high-risk sites based on risk scores.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe with site and risk information
    site_column : str
        Site identifier column
    risk_column : str
        Risk score column
    threshold : float
        Risk score threshold for vulnerability
        
    Returns:
    --------
    pd.DataFrame
        Summary of vulnerable sites
    """
    if site_column not in df.columns or risk_column not in df.columns:
        print("Warning: Required columns not found")
        return pd.DataFrame()
    
    # Calculate site-level statistics
    site_stats = df.groupby(site_column).agg({
        risk_column: ['mean', 'max', 'count'],
        'DO_critical': 'sum' if 'DO_critical' in df.columns else 'count',
        'temp': 'mean' if 'temp' in df.columns else 'count',
        'do': 'mean' if 'do' in df.columns else 'count'
    }).reset_index()
    
    site_stats.columns = ['_'.join(col).strip('_') for col in site_stats.columns.values]
    
    # Identify vulnerable sites
    vulnerable = site_stats[site_stats[f'{risk_column}_mean'] >= threshold].copy()
    vulnerable = vulnerable.sort_values(f'{risk_column}_mean', ascending=False)
    
    print(f"\nVulnerable Sites (Risk Score >= {threshold}):")
    print(f"  Total sites identified: {len(vulnerable)}")
    print(f"  Percentage of all sites: {len(vulnerable)/len(site_stats)*100:.1f}%")
    
    return vulnerable


def project_future_risk(df, temp_column='temp', years_ahead=10, 
                       warming_rate=0.1):
    """
    Project future risk under continued warming.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Historical dataframe
    temp_column : str
        Temperature column name
    years_ahead : int
        Number of years to project forward
    warming_rate : float
        Degrees Celsius per year warming rate
        
    Returns:
    --------
    pd.DataFrame
        Projected scenario dataframe
    """
    # Calculate total warming
    total_warming = warming_rate * years_ahead
    
    print(f"\nFuture Projection ({years_ahead} years):")
    print(f"  Warming rate: {warming_rate}°C/year")
    print(f"  Total warming: {total_warming}°C")
    
    # Create scenario
    df_future = simulate_warming_scenario(df, temp_column=temp_column,
                                         warming_amount=total_warming)
    
    return df_future


def export_risk_assessment(df, site_stats, output_path, include_coords=False):
    """
    Export comprehensive risk assessment for dashboard/GIS.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Full dataframe with risk features
    site_stats : pd.DataFrame
        Site-level aggregations
    output_path : str or Path
        Output file path
    include_coords : bool
        Whether to include lat/lon if available
        
    Returns:
    --------
    pd.DataFrame
        Export dataframe
    """
    from pathlib import Path
    
    # Create comprehensive export
    export_df = df.copy()
    
    # Select key columns
    key_columns = [
        'date', 'year', 'month', 'season', 'site_id',
        'temp', 'do', 'ph', 'conductivity',
        'is_summer', 'DO_critical', 'stress_combo',
        'risk_score', 'risk_category'
    ]
    
    # Filter to available columns
    export_columns = [col for col in key_columns if col in export_df.columns]
    export_df = export_df[export_columns]
    
    # Save to file
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    export_df.to_csv(output_path, index=False)
    
    print(f"\n✓ Exported risk assessment to {output_path}")
    print(f"  Records: {len(export_df):,}")
    print(f"  Columns: {len(export_df.columns)}")
    print(f"  File size: {output_path.stat().st_size / 1024:.1f} KB")
    
    # Also export site summary
    if site_stats is not None and len(site_stats) > 0:
        site_output = output_path.parent / f"{output_path.stem}_site_summary.csv"
        site_stats.to_csv(site_output, index=False)
        print(f"✓ Exported site summary to {site_output}")
    
    return export_df
