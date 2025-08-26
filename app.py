"""
Simple entry point for downloading the World Happiness Report dataset(s).

This script imports the data download function from the project `src` package
and runs it in verbose mode (currently). It is intended for quick testing and to
demonstrate how the download process works.

Notes
-----
- Run this script directly (`python app.py`) to fetch the datasets.
- The dataset will be saved in the `data/bronze` folder by default.
"""

# import the download function
from src import (
    get_world_happiness_data,  # src/get_data/import_happiness_data.py
    fetch_geolocation_data,    # src/get_data/import_geolocation_data.py
    load_all_bronze_data,      # src/preprocess_data/load_bronze_data.py
    BronzeToSilver,            # src/preprocess_data/clean_bronze_data.py
)

# Run only if this script is executed directly (not when imported)
if __name__ == "__main__":
    
    # Call the download function with verbose output enabled
    get_world_happiness_data(verbose=True)
    fetch_geolocation_data(verbose=True)
    print("✅ Bronze downloaded.\n")

    # Load bronze data
    multi_df, y2021_df, geo_df = load_all_bronze_data()
    print("✅ Bronze loaded.\n")

    # Clean individually
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
    cleaner.save_multi(multi_clean)       # world_happiness_multi_silver.csv
    cleaner.save_y2021(y2021_clean)       # world_happiness_2021_silver.csv
    cleaner.save_geolocation(geo_clean)   # geolocation_silver.csv
    print("✅ All cleaned data saved to silver.\n")