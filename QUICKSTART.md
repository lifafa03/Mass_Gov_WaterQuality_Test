# 🚀 Quick Start Guide

## Get Up and Running in 5 Minutes

### 1. Install Dependencies (2 min)

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install packages
pip install -r requirements.txt
```

### 2. Launch Jupyter (1 min)

```bash
jupyter notebook
```

### 3. Run First Notebook (2 min)

1. Open `notebooks/01_data_loading_cleaning.ipynb`
2. Click **Run All** (Cell → Run All)
3. Wait for processing to complete

---

## 📊 What Gets Created

After running all 5 notebooks:

✅ **Cleaned dataset** → `data/processed/cleaned_water_quality.csv`  
✅ **Featured dataset** → `data/processed/water_quality_with_features.csv`  
✅ **Visualizations** → `outputs/figures/*.png`  
✅ **Dashboard exports** → `data/exports/*.csv`  

---

## 🎯 Notebook Sequence

| # | Notebook | What It Does | Runtime |
|---|----------|--------------|---------|
| 01 | Data Loading & Cleaning | Loads Excel, removes outliers, handles missing values | ~2 min |
| 02 | Exploratory Analysis | Stats, distributions, trends, patterns | ~3 min |
| 03 | Feature Engineering | Creates risk indicators, temporal features | ~2 min |
| 04 | Visualization | Generates all publication-quality plots | ~4 min |
| 05 | Scenario Modeling | Simulates +2°C warming, future projections | ~3 min |

**Total time**: ~15 minutes

---

## 🔑 Key Features Created

```python
# Temporal
'is_summer'      # Binary: June-August
'season'         # Winter/Spring/Summer/Fall

# Risk Indicators
'DO_critical'    # DO < 5 mg/L
'temp_warm'      # Temp > 25°C
'stress_combo'   # High temp + Low DO

# Composite Score
'risk_score'     # 0-100 heat-stress index
'risk_category'  # Low/Moderate/High/Very High/Extreme
```

---

## 📈 Key Outputs

### Visualizations
1. **Monthly DO Pattern** - Seasonal U-curve
2. **Temp-DO Relationship** - Negative correlation
3. **Summer Warming Trend** - 2005-2020
4. **Risk Distribution** - Histogram + categories
5. **Scenario Comparison** - Baseline vs +2°C

### Data Exports (for Tableau/Power BI)
- `ma_waterways_baseline_risk_data.csv`
- `ma_waterways_scenario_2c_risk_data.csv`
- `scenario_summary_statistics.csv`
- `vulnerable_sites_scenario.csv`

---

## 💡 Pro Tips

1. **Run notebooks in order** - Each depends on previous outputs
2. **Check output paths** - Verify files are being created
3. **Customize thresholds** - Edit in `src/feature_engineering.py`
4. **Sample large visualizations** - Use `df.sample(10000)` if slow
5. **Save often** - Jupyter auto-saves, but manual saves don't hurt

---

## 🆘 Common Issues

### "Module not found"
```bash
pip install -r requirements.txt
```

### "File not found"
Check you're in correct directory:
```bash
pwd  # Should show .../Mass_waterways
```

### "Kernel died"
Restart kernel: Kernel → Restart

---

## ✅ Success Checkpoint

After notebook 01, you should see:
```
✓ Loaded [X] records
✓ Cleaned [Y] records
✓ Saved to data/processed/cleaned_water_quality.csv
```

After all notebooks:
```bash
ls data/exports/
# Should show: 4 CSV files

ls outputs/figures/
# Should show: 10+ PNG files
```

---

## 🎉 You're Ready!

Next: Create your dashboard using the exported CSV files!

**Questions?** Check `SETUP.md` for detailed instructions.
