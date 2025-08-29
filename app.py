"""
Simple entry point for the World Happiness pipeline.

This script:
1) Downloads bronze datasets (World Happiness + Geolocation).
2) Loads bronze data.
3) Cleans and saves to silver.
4) Loads silver data (mirrors bronze loader style).
5) [Optional] Runs Stage 3 feature engineering to append 2021 into multi-year
   and merge with geolocation.
6) Runs Silver → Gold to produce the final dataset in `data/gold/`.

Notes
-----
- Run this script directly (`python app.py`) to execute the end-to-end pipeline.
- Bronze outputs are saved in `data/bronze/`.
- Silver cleaned outputs are saved in `data/silver/`.
- Gold outputs are saved in `data/gold/`.
"""

# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------

# Existing imports exposed via src/__init__.py
from src import (
    get_world_happiness_data,   # src/get_data/import_happiness_data.py
    fetch_geolocation_data,     # src/get_data/import_geolocation_data.py
    load_all_bronze_data,       # src/preprocess_data/load_bronze_data.py
    BronzeToSilver,             # src/preprocess_data/clean_bronze_data.py
    load_all_silver_data,       # src/feature_engineering/load_silver_data.py
    SilverToGold,               # src/feature_engineering/engineer_silver_data.py
)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

if __name__ == "__main__":

    # ------------------------------------------------------------------
    # Stage 1: Download bronze datasets
    # ------------------------------------------------------------------

    get_world_happiness_data(verbose=True)
    fetch_geolocation_data(verbose=True)
    print("✅ Bronze downloaded 🥉.\n")

    # ------------------------------------------------------------------
    # Stage 1b: Load bronze datasets
    # ------------------------------------------------------------------

    # Mirrors the style used in load_bronze_data.py (friendly prints)
    multi_df, y2021_df, geo_df = load_all_bronze_data(verbose=True)
    print("✅ Bronze loaded 🥉.\n")

    # ------------------------------------------------------------------
    # Stage 2: Clean bronze -> silver (three independent cleaners)
    # ------------------------------------------------------------------

    cleaner = BronzeToSilver()

    # Clean multi-year happiness data
    multi_clean = cleaner.clean_multi_year(multi_df)
    print("✅ Multi-year cleaned.\n")

    # Clean 2021-only happiness data
    y2021_clean = cleaner.clean_y2021(y2021_df)
    print("✅ 2021-only cleaned.\n")

    # Clean geolocation data
    geo_clean = cleaner.clean_geolocation(geo_df)
    print("✅ Geolocation cleaned.\n")

    # Save each cleaned DataFrame to silver
    cleaner.save_multi(multi_clean)       # data/silver/world_happiness_multi_silver.csv
    cleaner.save_y2021(y2021_clean)       # data/silver/world_happiness_2021_silver.csv
    cleaner.save_geolocation(geo_clean)   # data/silver/geolocation_silver.csv
    print("✅ All cleaned data saved to 🥈 folder.\n")

    # ------------------------------------------------------------------
    # Stage 3: Load silver data (same style as bronze loaders)
    # ------------------------------------------------------------------

    multi_clean_s, y2021_clean_s, geo_clean_s = load_all_silver_data(verbose=True)
    print("✅ Silver loaded 🥈.\n")

    # ------------------------------------------------------------------
    # Stage 4: Silver → Gold (append 2021 into multi-year, merge geo, save)
    # ------------------------------------------------------------------

    s2g = SilverToGold()
    gold_df = s2g.run(
        multi_df=multi_clean_s,
        y2021_df=y2021_clean_s,
        geo_df=geo_clean_s,
        restrict_multi_to_2021_countries=True,
        verbose=True,
        save_output=True,
    )
    print("✅ Gold dataset created and saved to 🥇 folder.\n")
