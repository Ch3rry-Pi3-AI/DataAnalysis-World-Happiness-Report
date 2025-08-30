# Feature Engineering – Silver → Gold

This branch focuses on **loading the cleaned silver datasets** and **engineering them into a single, user-ready gold dataset**.

What this stage does:

* Robustly locates key columns by normalised names and aligns schemas across sources.
* Injects `regional_indicator` into the multi-year data from the 2021 mapping.
* Optionally restricts multi-year rows to countries present in 2021.
* Applies alias mappings (e.g., `life_ladder` → `ladder_score`) to harmonise semantics.
* Intersects & aligns columns, appends with precedence to 2021 rows on `(country_name, year)`, and merges geolocation.
* Writes a single CSV to the **gold** layer: `world_happiness_gold.csv`.

The silver inputs are loaded via small helpers for the multi-year, 2021, and geolocation tables.

## Project Structure

New modules live in `src/feature_engineering/` and the pipeline produces a new **gold** folder:

```
project-root/
├── app.py
├── src/
│   ├── __init__.py
│   ├── get_data/
│   │   ├── __init__.py
│   │   ├── import_happiness_data.py
│   │   └── import_geolocation_data.py
│   ├── preprocess_data/
│   │   ├── __init__.py
│   │   ├── load_bronze_data.py
│   │   └── clean_bronze_data.py
│   └── feature_engineering/                 🆕 (NEW)
│       ├── __init__.py                      🆕
│       ├── load_silver_data.py              🆕
│       └── engineer_silver_data.py          🆕
└── data/
    ├── bronze/
    ├── silver/
    └── gold/                                🆕 (NEW)
        └── world_happiness_gold.csv         🥇
```

* `load_silver_data.py` → Loads cleaned silver CSVs (multi-year, 2021, geolocation).
* `engineer_silver_data.py` → Normalises/aligns, injects region, applies aliases, merges geolocation, and saves the gold CSV.
* `app.py` → Orchestrates the pipeline end-to-end (silver → gold).

## How to Run

You can run the engineering step in three ways:

### 1) Run via the app entry point (recommended)

From the project root:

```bash
python app.py
```

This will:

* Load all silver tables,
* Engineer/merge them,
* Save the output to `data/gold/world_happiness_gold.csv`.

### 2) Run the silver loader directly

From the project root:

```bash
python src/feature_engineering/load_silver_data.py
```

This prints quick summaries confirming the silver files were found and loaded.

### 3) Run the engineering script directly

From the project root:

```bash
python src/feature_engineering/engineer_silver_data.py
```

This executes the **silver → gold** transformation and writes `world_happiness_gold.csv` to `data/gold/`.

## Output

* **Gold CSV**: `data/gold/world_happiness_gold.csv` (user-ready table with harmonised columns, region labels, and coordinates).
* Console logs summarise: shared columns used, rows appended, geo harmonisation count, rows missing coordinates (if any), and the saved path.

## Notes

* This stage completes the medallion flow for the assignment (**silver → gold**).
* The engineering is deliberately robust to small column-name differences via normalisation and aliasing.
* If you want to include *all* multi-year countries (not just those present in 2021), run with `restrict_multi_to_2021_countries=False` when using the `SilverToGold` class.