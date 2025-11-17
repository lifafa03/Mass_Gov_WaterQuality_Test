# 🚀 Project Setup Guide
## Heatwave Risk Index for Massachusetts Waterways

This guide will help you set up and run the complete analysis pipeline.

---

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **Git**: (optional, for version control)
- **Storage**: ~500 MB free space

---

## 🔧 Installation Steps

### 1. Navigate to Project Directory

```bash
cd ~/Desktop/Mass_waterways
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

This will install:
- pandas, numpy (data processing)
- matplotlib, seaborn, plotly (visualization)
- scipy, scikit-learn (analysis)
- openpyxl (Excel reading)
- jupyter (notebooks)

### 4. Verify Installation

```bash
python -c "import pandas, numpy, matplotlib, seaborn; print('✓ All packages installed successfully!')"
```

---

## 📁 Data Organization

The Excel data files should already be in the project root. If not:

1. Move `wqdiscreteprobedata-8-23-2022.xlsx` to project root
2. Move `DataDictionary20221020.xlsx` to project root

Current structure:
```
Mass_waterways/
├── wqdiscreteprobedata-8-23-2022.xlsx  ← Main data
├── DataDictionary20221020.xlsx         ← Reference
├── data/
│   ├── raw/          (for backups)
│   ├── processed/    (cleaned data)
│   └── exports/      (dashboard files)
├── notebooks/        (analysis notebooks)
├── src/              (Python modules)
└── outputs/          (figures, reports)
```

---

## 🎯 Running the Analysis

### Option 1: Jupyter Notebooks (Recommended)

```bash
# Start Jupyter
jupyter notebook
```

Then open and run notebooks in order:
1. `01_data_loading_cleaning.ipynb`
2. `02_exploratory_analysis.ipynb`
3. `03_feature_engineering.ipynb`
4. `04_visualization.ipynb`
5. `05_scenario_modeling.ipynb`

**Tips**:
- Run cells sequentially (Shift + Enter)
- Review outputs and markdown explanations
- Modify parameters as needed

### Option 2: Python Scripts

You can also use the modules directly in Python:

```python
import sys
sys.path.append('src')

from data_processing import load_water_quality_data, clean_water_quality_data
from feature_engineering import create_temporal_features, calculate_risk_score
from visualization import create_summary_dashboard
from risk_modeling import simulate_warming_scenario

# Load and process data
df = load_water_quality_data('wqdiscreteprobedata-8-23-2022.xlsx')
df_clean = clean_water_quality_data(df)
# ... continue analysis
```

---

## 📊 Expected Outputs

After running all notebooks, you'll have:

### Data Files:
- `data/processed/cleaned_water_quality.csv`
- `data/processed/water_quality_with_features.csv`
- `data/processed/site_statistics.csv`
- `data/exports/ma_waterways_baseline_risk_data.csv`
- `data/exports/ma_waterways_scenario_2c_risk_data.csv`
- `data/exports/scenario_summary_statistics.csv`

### Visualizations:
- `outputs/figures/monthly_do_pattern.png`
- `outputs/figures/temp_do_relationship.png`
- `outputs/figures/summer_temp_trend.png`
- `outputs/figures/correlation_heatmap.png`
- `outputs/figures/risk_distribution.png`
- `outputs/figures/scenario_comparison.png`
- ... and more

---

## 🔍 Troubleshooting

### Issue: "Module not found"
**Solution**: Make sure virtual environment is activated and packages are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "File not found" errors
**Solution**: Check that you're running notebooks from the `notebooks/` directory or adjust paths accordingly.

### Issue: Memory errors with large dataset
**Solution**: Process data in chunks or sample for visualization:
```python
df_sample = df.sample(n=50000, random_state=42)
```

### Issue: Excel file won't load
**Solution**: Ensure `openpyxl` is installed:
```bash
pip install openpyxl
```

---

## 📈 Customization

### Adjust Risk Thresholds

In `src/feature_engineering.py`, modify:

```python
thresholds = {
    'critical': 5.0,    # Change DO critical threshold
    'stress': 6.0,      # Change DO stress threshold
    'optimal': 8.0      # Change DO optimal threshold
}
```

### Change Warming Scenarios

In notebook 05:

```python
# Try different warming amounts
df_scenario = simulate_warming_scenario(df, warming_amount=3.0)  # +3°C

# Or different warming rates
df_future = project_future_risk(df, years_ahead=20, warming_rate=0.15)
```

### Custom Visualizations

Use the visualization module:

```python
from visualization import plot_monthly_do_pattern

# Custom styling
fig, ax = plot_monthly_do_pattern(df, do_column='your_column')
ax.set_title('Custom Title')
plt.savefig('custom_plot.png', dpi=300)
```

---

## 💾 Saving Your Work

### Version Control (Optional)

```bash
# Initialize git repository
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: MA Waterways analysis setup"
```

### Backup Important Files

Regularly backup:
- Processed data (`data/processed/`)
- Figures (`outputs/figures/`)
- Modified notebooks

---

## 📚 Next Steps

1. **Run the complete pipeline** (notebooks 01-05)
2. **Review outputs** and validate results
3. **Create dashboard** using exported CSV files in Tableau/Power BI
4. **Prepare presentation** using generated figures
5. **Document findings** in `outputs/reports/`

---

## 🆘 Getting Help

- **Documentation**: Check README.md for project overview
- **Code comments**: Each module has detailed docstrings
- **Notebook markdown**: Read explanations in each notebook cell

---

## ✅ Success Checklist

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (requirements.txt)
- [ ] Data files in correct locations
- [ ] Notebook 01: Data loaded and cleaned
- [ ] Notebook 02: EDA complete
- [ ] Notebook 03: Features engineered
- [ ] Notebook 04: Visualizations generated
- [ ] Notebook 05: Scenarios modeled
- [ ] Exports ready for dashboard

---

**Good luck with your hackathon! 🎉**

*Last updated: November 15, 2025*
