# Exploratory Data Analysis – Gold

This stage focuses on **loading the engineered gold dataset** and **exploring it with a small, teaching‑friendly EDA toolkit**.

What this stage does:

* Adds a lightweight `src/eda/` package for gold‑data exploration.
* Provides `load_gold_data.py` to read `data/gold/world_happiness.csv` as a `pandas.DataFrame`.
* Provides `explore_gold_data.py` with an `EDAExplorer` class (Numpy-style docstrings, clear comments) to:

  * preview rows and dataset info,
  * summarise numeric & categorical features,
  * inspect missingness (table and optional bar chart),
  * plot histograms and boxplots of numeric columns,
  * compute/plot correlation heatmaps (with optional `top_k` pruning),
  * draw a simple longitude/latitude scatter (optional `hue`).

* Introduces a **notebook entrypoint** (`notebooks/eda_notebook.ipynb`) that calls these helpers and writes plots to `artifacts/` as PNGs.