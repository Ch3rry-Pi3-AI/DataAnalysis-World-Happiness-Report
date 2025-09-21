# Dashboard App – Gold → Visualisation

This branch focuses on **building an interactive dashboard** with Dash to explore the engineered gold dataset.
It introduces a modular app structure, a central data accessor, and five interactive pages.

What this stage does:

* Adds a new `src/dash_app/` package for Dash integration.
* Provides `create_app.py` to construct the Dash app with navigation, layout, and page routing.
* Provides `data_access.py` to inject and retrieve the gold dataset across all pages.
* Introduces a new `src/dash_app/app_pages/` folder containing **five dashboard pages**:

  * `home.py` – overview, dataset summary, and top/bottom rankings.
  * `dataset.py` – tabular view, filters, and summary tables.
  * `relationship.py` – scatterplots and correlation heatmaps.
  * `geo.py` – choropleths, regional radials, and Top-10 bar charts.
  * `trends.py` – time-series by region and Top-10 changes between years.

The dashboard is launched via `python app.py`.

## Project Structure

The project now contains **all prior stages** (bronze, silver, gold) plus the new **dashboard stage**:

```
project-root/
├── app.py                                   # Entrypoint: launches dashboard
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
│   ├── eda/
│   │   ├── __init__.py
│   │   ├── load_gold_data.py
│   │   └── explore_gold_data.py
│   └── dash_app/                            🆕 (NEW)
│       ├── __init__.py                      🆕
│       ├── create_app.py                    🆕
│       ├── data_access.py                   🆕
│       └── app_pages/                       🆕 (NEW)
│           ├── home.py                      🆕
│           ├── dataset.py                   🆕
│           ├── relationship.py              🆕
│           ├── geo.py                       🆕
│           └── trends.py                    🆕
├── notebooks/
│   └── eda_notebook.ipynb
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│       └── world_happiness_gold.csv
└── artifacts/
    ├── missing.png
    ├── histograms.png
    ├── boxplots.png
    └── correlations_pearson.png
```

* `create_app.py` → Configures the Dash app, navbar, and page routing.
* `data_access.py` → Provides central getter/setter for the gold DataFrame.
* `home.py` → Overview page with dataset snapshot and quick rankings.
* `dataset.py` → Dataset explorer with filters, tables, and regional summaries.
* `relationship.py` → Relationship explorer with scatterplots and correlation heatmaps.
* `geo.py` → Geographic views: choropleth, regional radial, and Top-10 chart.
* `trends.py` → Time-series explorer: Top-10 changes and region-mean line charts.

## How to Run

From the project root:

```bash
python app.py
```

This will:

* Load the gold dataset,
* Inject it into the `data_access` provider,
* Construct the Dash app with pages enabled,
* Launch a local web server (`http://127.0.0.1:8050`).

## Output

* **Interactive dashboard** served locally with 5 navigation tabs: Home, Dataset, Relationship, Geography, and Trends.
* Console log prints the gold dataset preview (`head()`) when starting.
* Debug mode is enabled by default (`debug=True`) for development.

## Notes

* The app uses **Dash Pages** for modular navigation.
* Dataset access is centralised through `data_access.py` to keep pages lightweight and consistent.
* Stylesheets use Bootstrap for clean, responsive design.
* This stage completes the pipeline: from raw bronze data → engineered gold data → **interactive visualisation**.