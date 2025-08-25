"""
Simple entry point for downloading the World Happiness Report dataset(s).

This script imports the data download function from the project `src` package
and runs it in verbose mode (currently). It is intended for quick testing and to
demonstrate how the download process works.

Notes
-----
- Run this script directly (`python app.py`) to fetch the dataset.
- The dataset will be saved in the `data/bronze` folder by default.
"""

# import the download function
from src import (
    get_world_happiness_data,  # src/get_data/import_happiness_data.py
)

# Run only if this script is executed directly (not when imported)
if __name__ == "__main__":
    
    # Call the download function with verbose output enabled
    get_world_happiness_data(verbose=True)