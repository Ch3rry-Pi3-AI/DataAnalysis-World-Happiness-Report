import pandas as pd
from pathlib import Path

def fetch_geolocation_data(
        cache_folder: Path = Path("data/geolocation"),
        filename: str = "geolocation.csv"        
) -> Path:
    
    # Ensure cache directory exists
    cache_folder = Path(cache_folder)
    cache_folder.mkdir(parents=True, exist_ok=True)

    # Compute full output path
    output_path = cache_folder / filename

    if output_path.exists():
        return output_path


check = "OK"
if __name__ == "__main__":
    print(check)
    fetch_geolocation_data()