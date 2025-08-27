"""
Simple entry point for downloading the World Happiness Report datasets.

This script:
1) Downloads bronze datasets (World Happiness + Geolocation).

Notes
-----
- Run this script directly (`python app.py`) to fetch the datasets.
- Bronze outputs are saved in the `data/bronze/` folder by default.
"""

# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------
from src import (
    get_world_happiness_data,   # src/get_data/import_happiness_data.py
    fetch_geolocation_data,     # src/get_data/import_geolocation_data.py
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
