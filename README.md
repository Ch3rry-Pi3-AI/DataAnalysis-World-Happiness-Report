# Data Preprocessing – Bronze -> Silver

This branch of the project is focused on **loading the bronze datasets** and **cleaning them** into the silver layer.
The following two datasets are cleaned individually in this stage, preparing them for merging in the upcoming feature engineering stage:

* World Happiness Report (multi-year)
* World Happiness Report 2021

The purpose of this stage is to ensure consistent column naming, add missing metadata (such as `year`), and perform basic numeric imputations.
The cleaned outputs are stored in the **silver** container for downstream use.



## Project Structure

The new modules are stored in `src/preprocess_data/`:

```
project-root/
├── app.py
├── src/
│   ├── __init__.py
│   ├── get_data/
│   │   ├── __init__.py
│   │   └── import_happiness_data.py
│   ├── preprocess_data/                    🆕 (NEW)
│   │   ├── __init__.py                     🆕
│   │   ├── load_bronze_data.py             🆕
│   │   └── clean_bronze_data.py            🆕
└── data/
    ├── bronze/    
    └── silver/    # cleaned outputs        🆕
```

* `load_bronze_data.py` → Loads all bronze CSVs (multi-year, 2021) into pandas DataFrames.
* `clean_bronze_data.py` → Cleans each DataFrame (standardises columns, imputes missing values, etc.) and saves them to the silver folder.
* `app.py` → Updated to run the full pipeline: download bronze → load bronze → clean → save silver.



## How to Run

You can run the preprocessing in three different ways depending on your workflow:

### 1) Run via the app entry point (recommended)

From the project root:

```bash
python app.py
```

This will:

* Download the bronze data if missing,
* Load both bronze DataFrames,
* Clean them individually,
* Save the cleaned outputs into `data/silver/`.



### 2) Run the bronze loader directly

From the project root:

```bash
python -m src.preprocess_data.load_bronze_data
```

This will load all bronze CSVs and print quick summaries (row/column counts).



### 3) Run the bronze cleaner directly

From the project root:

```bash
python -m src.preprocess_data.clean_bronze_data
```

This will clean one or more of the bronze DataFrames and display before/after column names.
When used through `app.py`, it will also save the cleaned versions into the silver folder.



## Output

* Cleaned silver CSVs will be stored under the `data/silver/` folder:

  * `world_happiness_multi_silver.csv`
  * `world_happiness_2021_silver.csv`

* Logging confirms column standardisation and imputation.



## Notes

* These scripts are designed for the **silver stage** of the medallion architecture.
* Each dataset is cleaned **individually** in this stage. They will be merged together in the **feature engineering stage (gold)**.
* All modules follow the same style as earlier stages with docstrings, comments, and logging for clarity.