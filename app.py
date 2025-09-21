"""
Simple entry point for the World Happiness pipeline.

This script:
1) Downloads bronze datasets (World Happiness + Geolocation).
2) Loads bronze data.
3) Cleans and saves to silver.

Notes
-----
- Run this script directly (`python app.py`) to execute the pipeline.
- Bronze outputs are saved in `data/bronze/`.
- Silver cleaned outputs are saved in `data/silver/`.
"""

# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from src import (
    get_world_happiness_data,   # src/get_data/import_happiness_data.py
    load_all_bronze_data,       # src/preprocess_data/load_bronze_data.py
    BronzeToSilver,             # src/preprocess_data/clean_bronze_data.py
)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
if __name__ == "__main__":

    # ------------------------------------------------------------------
    # Stage 1: Download bronze datasets
    # ------------------------------------------------------------------
    get_world_happiness_data(verbose=True)
    print("✅ Bronze downloaded 🥉.\n")

    # ------------------------------------------------------------------
    # Stage 1b: Load bronze datasets
    # ------------------------------------------------------------------
    multi_df, y2021_df = load_all_bronze_data(verbose=True)
    print("✅ Bronze loaded 🥉.\n")

    # ------------------------------------------------------------------
    # Stage 2: Clean bronze -> silver
    # ------------------------------------------------------------------
    cleaner = BronzeToSilver()

    # Clean multi-year happiness data
    multi_clean = cleaner.clean_multi_year(multi_df)
    print("✅ Multi-year cleaned.\n")

    # Clean 2021-only happiness data
    y2021_clean = cleaner.clean_y2021(y2021_df)
    print("✅ 2021-only cleaned.\n")

    # Save each cleaned DataFrame to silver
    cleaner.save_multi(multi_clean)       # data/silver/world_happiness_multi_silver.csv
    cleaner.save_y2021(y2021_clean)       # data/silver/world_happiness_2021_silver.csv
    print("✅ All cleaned data saved to 🥈 folder.\n")
