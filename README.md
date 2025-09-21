# Exploratory Data Analysis – Gold

This stage focuses on **loading the engineered gold dataset** and **exploring it with a small, teaching-friendly EDA toolkit**.

What this stage does:

* Adds a lightweight `src/eda/` package for gold-data exploration.

* Provides `load_gold_data.py` to read `data/gold/world_happiness.csv` as a `pandas.DataFrame`.

* Provides `explore_gold_data.py` with an `EDAExplorer` class (Numpy-style docstrings, clear comments) to:

  * preview rows and dataset info,
  * summarise numeric & categorical features,
  * inspect missingness (table and optional bar chart),
  * plot histograms and boxplots of numeric columns,
  * compute/plot correlation heatmaps (with optional `top_k` pruning).

* Introduces a **notebook entrypoint** (`notebooks/eda_notebook.ipynb`) that calls these helpers and writes plots to `artifacts/` as PNGs.



## Project Structure

New modules live in `src/eda/`. A new **notebooks** folder (entrypoint) and an artifacts folder (auto-created when plotting) are included:

```
project-root/
├── app.py
├── src/
│   ├── __init__.py
│   ├── get_data/
│   │   ├── __init__.py
│   │   └── import_happiness_data.py
│   ├── preprocess_data/
│   │   ├── __init__.py
│   │   ├── load_bronze_data.py
│   │   └── clean_bronze_data.py
│   ├── feature_engineering/                  
│   │   ├── __init__.py                      
│   │   ├── load_silver_data.py              
│   │   └── engineer_silver_data.py          
│   ├── eda/                                 🆕 (NEW)
│   │   ├── __init__.py                      🆕 
│   │   ├── load_gold_data.py                🆕
│   │   └── explore_gold_data.py             🆕
├── notebooks/                               🆕
│   └── eda_notebook.ipynb                   🆕
├── data/
│    ├── bronze/
│    ├── silver/
│    └── gold/                               
│        └── world_happiness_gold.csv        
└── artifacts/                               🆕 (NEW)
    ├── missing.png                          🆕 
    ├── histograms.png                       🆕
    ├── boxplots.png                         🆕
    └── correlations_pearson.png             🆕
```

* `load_gold_data.py` → Loads `data/gold/world_happiness_gold.csv` into a DataFrame.
* `explore_gold_data.py` → `EDAExplorer` with preview/describe/missingness/plots; configurable via `EDAConfig` (style, DPI, palette, optional `sns.set_theme`).
* `eda_notebook.ipynb` → Natural entrypoint: demonstrates the helpers and writes PNGs to `artifacts/`.



## Notebook

The notebook `eda_notebook.ipynb` is contained in the `notebooks/` folder. The main code comprises:

```python
from pathlib import Path
from src.eda.load_gold_data import load_gold_happiness_data
from src.eda.explore_gold_data import EDAExplorer, EDAConfig

# Load gold dataset
gold_df = load_gold_happiness_data()

# Configure EDA (save figures to artifacts/)
cfg = EDAConfig(save_dir=Path("artifacts"), use_theme=True, fig_dpi=110)
eda = EDAExplorer(gold_df, config=cfg)

# Quick looks
eda.preview(n=5)
eda.info()
eda.describe_numeric()
eda.describe_categorical(console=True)

# Data quality and distributions
eda.missing(plot=True)
eda.histograms(bins=30)
eda.boxplots(show_outliers=True)

# Relationships
eda.correlations(method="pearson", top_k=20)
```

> **Note**: The notebook contains additional code to ensure that imports resolve to the project root.



## Output

* **PNG figures** in `artifacts/` (created automatically when plotting):

  * `missing.png`, `histograms.png`, `boxplots.png`, `correlations_<method>.png`.
* **Console summaries** in the notebook (shape, dtypes, memory usage, numeric/categorical summaries).



## Notes

* `EDAExplorer` works on a defensive copy of the DataFrame (EDA is non-destructive).
* Styling uses seaborn; you can opt into `sns.set_theme()` via `EDAConfig(use_theme=True)`.
* Methods that *display* content typically print/plot rather than return tables; this keeps the notebook flow simple and more aesthetic.