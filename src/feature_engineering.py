"""
Feature Engineering Module for MA Waterways Heatwave Risk Analysis

This module contains functions for creating derived features, risk indicators,
and temporal patterns from water quality data.
"""

import pandas as pd
import numpy as np
from scipy import stats


def create_temporal_features(df, date_column='date'):
    """
    Create temporal features for time-based analysis.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe with date column
    date_column : str
        Name of the date column
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with added temporal features
    """
    df_feat = df.copy()
    
    if date_column not in df_feat.columns:
        print(f"Warning: {date_column} not found in dataframe")
        return df_feat
    
    # Ensure datetime format
    df_feat[date_column] = pd.to_datetime(df_feat[date_column])
    
    # Extract temporal components
    df_feat['year'] = df_feat[date_column].dt.year
    df_feat['month'] = df_feat[date_column].dt.month
    df_feat['day'] = df_feat[date_column].dt.day
    df_feat['day_of_year'] = df_feat[date_column].dt.dayofyear
    df_feat['week_of_year'] = df_feat[date_column].dt.isocalendar().week
    df_feat['quarter'] = df_feat[date_column].dt.quarter
    
    # Season mapping
    season_map = {
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    }
    df_feat['season'] = df_feat['month'].map(season_map)
    
    # Binary indicators
    df_feat['is_summer'] = df_feat['month'].isin([6, 7, 8]).astype(int)
    df_feat['is_winter'] = df_feat['month'].isin([12, 1, 2]).astype(int)
    
    print("✓ Created temporal features:")
    print(f"  - year, month, day, day_of_year, week_of_year, quarter")
    print(f"  - season (Winter/Spring/Summer/Fall)")
    print(f"  - is_summer, is_winter binary flags")
    
    return df_feat


def create_do_risk_features(df, do_column='do', thresholds=None):
    """
    Create dissolved oxygen risk indicators.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    do_column : str
        Name of the dissolved oxygen column
    thresholds : dict, optional
        Custom thresholds for risk levels
        Default: {'critical': 5, 'stress': 6, 'optimal': 8}
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with DO risk features
    """
    df_feat = df.copy()
    
    if do_column not in df_feat.columns:
        print(f"Warning: {do_column} not found in dataframe")
        return df_feat
    
    # Default thresholds (mg/L)
    if thresholds is None:
        thresholds = {
            'critical': 5.0,    # Below this: severe oxygen stress
            'stress': 6.0,      # Below this: moderate stress
            'optimal': 8.0      # Above this: healthy conditions
        }
    
    # Binary indicators
    df_feat['DO_critical'] = (df_feat[do_column] < thresholds['critical']).astype(int)
    df_feat['DO_stress'] = (df_feat[do_column] < thresholds['stress']).astype(int)
    df_feat['DO_optimal'] = (df_feat[do_column] >= thresholds['optimal']).astype(int)
    
    # Categorical risk level
    def categorize_do(do_val):
        if pd.isna(do_val):
            return 'Unknown'
        elif do_val < thresholds['critical']:
            return 'Critical'
        elif do_val < thresholds['stress']:
            return 'Stress'
        elif do_val < thresholds['optimal']:
            return 'Moderate'
        else:
            return 'Optimal'
    
    df_feat['DO_category'] = df_feat[do_column].apply(categorize_do)
    
    # Deviation from optimal (normalized)
    df_feat['DO_deficit'] = np.maximum(0, thresholds['optimal'] - df_feat[do_column])
    
    print("✓ Created DO risk features:")
    print(f"  - DO_critical (DO < {thresholds['critical']} mg/L)")
    print(f"  - DO_stress (DO < {thresholds['stress']} mg/L)")
    print(f"  - DO_optimal (DO >= {thresholds['optimal']} mg/L)")
    print(f"  - DO_category (Critical/Stress/Moderate/Optimal)")
    print(f"  - DO_deficit (distance from optimal level)")
    
    return df_feat


def create_temperature_features(df, temp_column='temp'):
    """
    Create temperature-related features and risk indicators.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    temp_column : str
        Name of the temperature column
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with temperature features
    """
    df_feat = df.copy()
    
    if temp_column not in df_feat.columns:
        print(f"Warning: {temp_column} not found in dataframe")
        return df_feat
    
    # Temperature thresholds for aquatic stress (°C)
    thresholds = {
        'cold_stress': 10,
        'optimal_low': 15,
        'optimal_high': 20,
        'warm': 25,
        'hot': 28
    }
    
    # Binary indicators
    df_feat['temp_cold'] = (df_feat[temp_column] < thresholds['cold_stress']).astype(int)
    df_feat['temp_optimal'] = ((df_feat[temp_column] >= thresholds['optimal_low']) & 
                               (df_feat[temp_column] <= thresholds['optimal_high'])).astype(int)
    df_feat['temp_warm'] = (df_feat[temp_column] > thresholds['warm']).astype(int)
    df_feat['temp_hot'] = (df_feat[temp_column] > thresholds['hot']).astype(int)
    
    # Categorical
    def categorize_temp(temp_val):
        if pd.isna(temp_val):
            return 'Unknown'
        elif temp_val < thresholds['cold_stress']:
            return 'Cold'
        elif temp_val < thresholds['optimal_low']:
            return 'Cool'
        elif temp_val <= thresholds['optimal_high']:
            return 'Optimal'
        elif temp_val <= thresholds['warm']:
            return 'Warm'
        elif temp_val <= thresholds['hot']:
            return 'Hot'
        else:
            return 'Extreme'
    
    df_feat['temp_category'] = df_feat[temp_column].apply(categorize_temp)
    
    # Temperature anomaly (if year is available)
    if 'year' in df_feat.columns:
        yearly_avg = df_feat.groupby('year')[temp_column].transform('mean')
        df_feat['temp_anomaly'] = df_feat[temp_column] - yearly_avg
    
    print("✓ Created temperature features:")
    print(f"  - temp_cold, temp_optimal, temp_warm, temp_hot (binary flags)")
    print(f"  - temp_category (Cold/Cool/Optimal/Warm/Hot/Extreme)")
    if 'temp_anomaly' in df_feat.columns:
        print(f"  - temp_anomaly (deviation from yearly average)")
    
    return df_feat


def create_combined_stress_features(df, do_column='do', temp_column='temp', 
                                   flow_column=None):
    """
    Create combined stress indicators from multiple parameters.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    do_column : str
        Dissolved oxygen column name
    temp_column : str
        Temperature column name
    flow_column : str, optional
        Flow status column name
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with combined stress features
    """
    df_feat = df.copy()
    
    # High temperature + Low DO = Critical stress
    if do_column in df_feat.columns and temp_column in df_feat.columns:
        df_feat['stress_combo'] = (
            (df_feat[temp_column] > 25) & 
            (df_feat[do_column] < 5)
        ).astype(int)
        print("✓ Created stress_combo (TEMP > 25°C AND DO < 5 mg/L)")
    
    # Flow-related stress (if flow data available)
    if flow_column and flow_column in df_feat.columns:
        low_flow_conditions = ['low', 'stagnant', 'no water', 'none']
        df_feat['flow_flag'] = df_feat[flow_column].astype(str).str.lower().isin(low_flow_conditions).astype(int)
        print("✓ Created flow_flag (low/stagnant flow conditions)")
        
        # Triple threat: high temp + low DO + low flow
        if 'stress_combo' in df_feat.columns:
            df_feat['extreme_stress'] = (
                (df_feat['stress_combo'] == 1) & 
                (df_feat['flow_flag'] == 1)
            ).astype(int)
            print("✓ Created extreme_stress (temp + DO + flow stress)")
    
    return df_feat


def calculate_risk_score(df, do_column='do', temp_column='temp', 
                        ph_column=None, flow_column=None):
    """
    Calculate composite risk score (0-100) based on multiple parameters.
    
    Risk Score Components:
    - Temperature stress: 40 points (0-40)
    - DO deficit: 40 points (0-40)
    - pH deviation: 10 points (0-10) [optional]
    - Flow conditions: 10 points (0-10) [optional]
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe with features
    do_column : str
        Dissolved oxygen column
    temp_column : str
        Temperature column
    ph_column : str, optional
        pH column
    flow_column : str, optional
        Flow status column
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with risk_score column
    """
    df_feat = df.copy()
    df_feat['risk_score'] = 0.0
    
    # Component 1: Temperature stress (0-40 points)
    if temp_column in df_feat.columns:
        # Linear increase from 20°C (0 pts) to 32°C (40 pts)
        temp_risk = np.clip((df_feat[temp_column] - 20) / 12 * 40, 0, 40)
        df_feat['risk_score'] += temp_risk.fillna(0)
    
    # Component 2: DO deficit (0-40 points)
    if do_column in df_feat.columns:
        # Linear increase from DO=8 (0 pts) to DO=0 (40 pts)
        do_risk = np.clip((8 - df_feat[do_column]) / 8 * 40, 0, 40)
        df_feat['risk_score'] += do_risk.fillna(0)
    
    # Component 3: pH deviation (0-10 points) [optional]
    if ph_column and ph_column in df_feat.columns:
        # Optimal pH: 6.5-8.5, max deviation gets 10 points
        ph_optimal = 7.5
        ph_deviation = np.abs(df_feat[ph_column] - ph_optimal)
        ph_risk = np.clip(ph_deviation / 2 * 10, 0, 10)  # 2 units = max
        df_feat['risk_score'] += ph_risk.fillna(0)
    
    # Component 4: Flow stress (0-10 points) [optional]
    if flow_column and flow_column in df_feat.columns:
        if 'flow_flag' in df_feat.columns:
            df_feat['risk_score'] += df_feat['flow_flag'] * 10
    
    # Normalize to 0-100 scale
    df_feat['risk_score'] = np.clip(df_feat['risk_score'], 0, 100)
    
    # Risk categories
    def categorize_risk(score):
        if pd.isna(score):
            return 'Unknown'
        elif score < 20:
            return 'Low'
        elif score < 40:
            return 'Moderate'
        elif score < 60:
            return 'High'
        elif score < 80:
            return 'Very High'
        else:
            return 'Extreme'
    
    df_feat['risk_category'] = df_feat['risk_score'].apply(categorize_risk)
    
    print("✓ Calculated composite risk_score (0-100)")
    print(f"  Score distribution:")
    print(df_feat['risk_category'].value_counts().sort_index())
    
    return df_feat


def create_site_aggregations(df, site_column='site_id', metrics=['do', 'temp']):
    """
    Create site-level aggregated features.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    site_column : str
        Site identifier column
    metrics : list
        Columns to aggregate
        
    Returns:
    --------
    pd.DataFrame
        Site-level aggregations
    """
    if site_column not in df.columns:
        print(f"Warning: {site_column} not found")
        return pd.DataFrame()
    
    agg_dict = {}
    for metric in metrics:
        if metric in df.columns:
            agg_dict[f'{metric}_mean'] = (metric, 'mean')
            agg_dict[f'{metric}_std'] = (metric, 'std')
            agg_dict[f'{metric}_min'] = (metric, 'min')
            agg_dict[f'{metric}_max'] = (metric, 'max')
    
    # Add count
    agg_dict['sample_count'] = (df.columns[0], 'count')
    
    # Add risk metrics if available
    if 'risk_score' in df.columns:
        agg_dict['risk_score_mean'] = ('risk_score', 'mean')
        agg_dict['risk_score_max'] = ('risk_score', 'max')
    
    if 'DO_critical' in df.columns:
        agg_dict['critical_events'] = ('DO_critical', 'sum')
    
    site_stats = df.groupby(site_column).agg(**agg_dict).reset_index()
    
    print(f"✓ Created site-level aggregations for {len(site_stats)} sites")
    
    return site_stats


def add_rolling_features(df, date_column='date', columns=['do', 'temp'], 
                        windows=[7, 30]):
    """
    Add rolling window statistics (moving averages, etc.)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe (must be sorted by date)
    date_column : str
        Date column name
    columns : list
        Columns to calculate rolling stats for
    windows : list
        Window sizes in days
        
    Returns:
    --------
    pd.DataFrame
        Dataframe with rolling features
    """
    df_feat = df.copy()
    
    if date_column not in df_feat.columns:
        print(f"Warning: {date_column} not found")
        return df_feat
    
    # Ensure sorted by date
    df_feat = df_feat.sort_values(date_column)
    
    for col in columns:
        if col not in df_feat.columns:
            continue
        
        for window in windows:
            # Rolling mean
            df_feat[f'{col}_rolling_{window}d'] = (
                df_feat[col].rolling(window=window, min_periods=1).mean()
            )
    
    print(f"✓ Added rolling features for windows: {windows} days")
    
    return df_feat
