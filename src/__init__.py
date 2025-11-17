"""
Initialize the Mass Waterways analysis package.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "Heatwave Risk Index for Massachusetts Waterways"

# Package metadata
PROJECT_NAME = "MA Waterways Heatwave Risk Analysis"
DATA_YEARS = "2005-2020"
LAST_UPDATED = "2025-11-15"

# Import key functions for easy access
from .data_processing import (
    load_water_quality_data,
    clean_water_quality_data,
    inspect_data_quality
)

from .feature_engineering import (
    create_temporal_features,
    create_do_risk_features,
    create_temperature_features,
    calculate_risk_score
)

from .visualization import (
    plot_monthly_do_pattern,
    plot_temp_do_relationship,
    plot_summer_temp_trend,
    create_summary_dashboard
)

from .risk_modeling import (
    simulate_warming_scenario,
    calculate_scenario_impacts,
    identify_vulnerable_sites
)

__all__ = [
    # Data processing
    'load_water_quality_data',
    'clean_water_quality_data',
    'inspect_data_quality',
    
    # Feature engineering
    'create_temporal_features',
    'create_do_risk_features',
    'create_temperature_features',
    'calculate_risk_score',
    
    # Visualization
    'plot_monthly_do_pattern',
    'plot_temp_do_relationship',
    'plot_summer_temp_trend',
    'create_summary_dashboard',
    
    # Risk modeling
    'simulate_warming_scenario',
    'calculate_scenario_impacts',
    'identify_vulnerable_sites'
]
