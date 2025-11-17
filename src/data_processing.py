"""
Data Processing Module for MA Waterways Heatwave Risk Analysis

This module contains functions for loading, cleaning, and preprocessing
water quality data from the Massachusetts DEP.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def load_water_quality_data(filepath):
    """
    Load water quality data from Excel file.
    
    Parameters:
    -----------
    filepath : str or Path
        Path to the Excel file containing water quality data
        
    Returns:
    --------
    pd.DataFrame
        Raw water quality dataframe
    """
    print(f"Loading data from {filepath}...")
    df = pd.read_excel(filepath)
    print(f"Loaded {len(df):,} records with {len(df.columns)} columns")
    return df


def inspect_data_quality(df):
    """
    Generate comprehensive data quality report.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
        
    Returns:
    --------
    dict
        Dictionary containing quality metrics
    """
    report = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'missing_pct': (df.isnull().sum() / len(df) * 100).to_dict(),
        'duplicates': df.duplicated().sum(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }
    
    print("=" * 60)
    print("DATA QUALITY REPORT")
    print("=" * 60)
    print(f"Total Records: {report['total_records']:,}")
    print(f"Total Columns: {report['total_columns']}")
    print(f"Duplicate Rows: {report['duplicates']:,}")
    print(f"Memory Usage: {report['memory_usage_mb']:.2f} MB")
    print("\nTop Missing Value Columns:")
    
    missing_df = pd.DataFrame({
        'Missing_Count': df.isnull().sum(),
        'Missing_Pct': df.isnull().sum() / len(df) * 100
    }).sort_values('Missing_Count', ascending=False).head(10)
    
    print(missing_df)
    
    return report


def clean_water_quality_data(df):
    """
    Clean and preprocess water quality data.
    
    Steps:
    1. Standardize column names
    2. Convert date/time columns
    3. Handle missing values
    4. Remove invalid measurements
    5. Create clean datetime index
    
    Parameters:
    -----------
    df : pd.DataFrame
        Raw water quality dataframe
        
    Returns:
    --------
    pd.DataFrame
        Cleaned dataframe
    """
    df_clean = df.copy()
    
    # Standardize column names (lowercase, replace spaces with underscores)
    df_clean.columns = df_clean.columns.str.lower().str.replace(' ', '_')
    
    # Identify key columns (adjust based on actual column names)
    # Common expected columns: date, time, site_id, do, temp, ph, conductivity, depth, flow
    
    print("\nCleaning steps:")
    print("-" * 60)
    
    # 1. Handle date/time columns
    date_cols = [col for col in df_clean.columns if 'date' in col.lower()]
    time_cols = [col for col in df_clean.columns if 'time' in col.lower()]
    
    if date_cols:
        for col in date_cols:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
            print(f"✓ Converted {col} to datetime")
    
    # 2. Extract year, month, day for analysis
    if len(date_cols) > 0:
        primary_date_col = date_cols[0]
        df_clean['year'] = df_clean[primary_date_col].dt.year
        df_clean['month'] = df_clean[primary_date_col].dt.month
        df_clean['day'] = df_clean[primary_date_col].dt.day
        df_clean['day_of_year'] = df_clean[primary_date_col].dt.dayofyear
        print(f"✓ Extracted temporal features from {primary_date_col}")
    
    # 3. Clean numeric columns (DO, TEMP, pH, etc.)
    numeric_indicators = ['do', 'temp', 'ph', 'conductivity', 'depth', 'oxygen']
    numeric_cols = [col for col in df_clean.columns 
                   if any(ind in col.lower() for ind in numeric_indicators)]
    
    for col in numeric_cols:
        # Convert to numeric, coercing errors
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Remove extreme outliers (beyond reasonable physical limits)
        if 'temp' in col.lower():
            # Water temperature: reasonable range 0-40°C
            df_clean.loc[(df_clean[col] < 0) | (df_clean[col] > 40), col] = np.nan
            print(f"✓ Cleaned {col} (valid range: 0-40°C)")
        
        elif 'do' in col.lower() or 'oxygen' in col.lower():
            # Dissolved oxygen: reasonable range 0-20 mg/L
            df_clean.loc[(df_clean[col] < 0) | (df_clean[col] > 20), col] = np.nan
            print(f"✓ Cleaned {col} (valid range: 0-20 mg/L)")
        
        elif 'ph' in col.lower():
            # pH: reasonable range 4-10
            df_clean.loc[(df_clean[col] < 4) | (df_clean[col] > 10), col] = np.nan
            print(f"✓ Cleaned {col} (valid range: 4-10)")
        
        elif 'conductivity' in col.lower():
            # Conductivity: reasonable range 0-2000 µS/cm
            df_clean.loc[(df_clean[col] < 0) | (df_clean[col] > 2000), col] = np.nan
            print(f"✓ Cleaned {col} (valid range: 0-2000 µS/cm)")
    
    # 4. Remove completely empty rows
    initial_count = len(df_clean)
    df_clean = df_clean.dropna(how='all')
    removed = initial_count - len(df_clean)
    if removed > 0:
        print(f"✓ Removed {removed:,} completely empty rows")
    
    # 5. Sort by date
    if len(date_cols) > 0:
        df_clean = df_clean.sort_values(date_cols[0]).reset_index(drop=True)
        print(f"✓ Sorted by {date_cols[0]}")
    
    print("-" * 60)
    print(f"Final cleaned dataset: {len(df_clean):,} records")
    
    return df_clean


def get_column_mapping(df):
    """
    Create a mapping of standardized names to actual column names.
    Useful for handling variations in column naming.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
        
    Returns:
    --------
    dict
        Mapping of standard names to actual column names
    """
    mapping = {}
    cols_lower = {col: col.lower() for col in df.columns}
    
    # Define standard mappings
    patterns = {
        'date': ['date', 'sample_date', 'sampledate'],
        'time': ['time', 'sample_time', 'sampletime'],
        'site_id': ['site', 'site_id', 'location', 'station'],
        'do': ['do', 'dissolved_oxygen', 'oxygen'],
        'temp': ['temp', 'temperature', 'water_temp'],
        'ph': ['ph'],
        'conductivity': ['conductivity', 'cond', 'specific_conductance'],
        'depth': ['depth', 'water_depth'],
        'flow': ['flow', 'flow_status', 'flow_condition']
    }
    
    for standard, patterns_list in patterns.items():
        for pattern in patterns_list:
            matching = [col for col, col_lower in cols_lower.items() 
                       if pattern in col_lower]
            if matching:
                mapping[standard] = matching[0]
                break
    
    return mapping


def filter_complete_cases(df, required_columns):
    """
    Filter to records with complete data for required columns.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    required_columns : list
        List of column names that must have non-null values
        
    Returns:
    --------
    pd.DataFrame
        Filtered dataframe
    """
    initial_count = len(df)
    df_filtered = df.dropna(subset=required_columns)
    removed = initial_count - len(df_filtered)
    
    print(f"\nFiltering for complete cases:")
    print(f"Required columns: {required_columns}")
    print(f"Records removed: {removed:,} ({removed/initial_count*100:.1f}%)")
    print(f"Records retained: {len(df_filtered):,}")
    
    return df_filtered


def save_processed_data(df, output_path, compression=None):
    """
    Save processed dataframe to file.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Dataframe to save
    output_path : str or Path
        Output file path (.csv, .parquet, or .xlsx)
    compression : str, optional
        Compression method for CSV files
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.suffix == '.csv':
        df.to_csv(output_path, index=False, compression=compression)
    elif output_path.suffix == '.parquet':
        df.to_parquet(output_path, index=False)
    elif output_path.suffix == '.xlsx':
        df.to_excel(output_path, index=False, engine='openpyxl')
    else:
        raise ValueError(f"Unsupported file format: {output_path.suffix}")
    
    print(f"\n✓ Saved processed data to {output_path}")
    print(f"  File size: {output_path.stat().st_size / 1024**2:.2f} MB")
