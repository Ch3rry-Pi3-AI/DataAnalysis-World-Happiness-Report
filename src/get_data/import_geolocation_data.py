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

    # Return existing cache if present
    if output_path.exists():
        return output_path
    
    # Download the countries CSV
    url = (
        "https://raw.githubusercontent.com/google/dspl/master/"
        "samples/google/canonical/countries.csv"
    )

    try:
        df = pd.read_csv(url)
        print("Stored CSV as Pandas DataFrame:")
        print(df.head())
    except Exception as e:
        raise RuntimeError(f"Failed to download geolocation data: {e}")
    
    df = df.rename(
        columns={
            "name":"country_name"
        }
    )
    df = df[["country", "country_name", "latitude", "longitude"]]
    print("Filtered to relevant fields")

    df.to_csv(output_path, index=False)
    print(f"Geolocation data saved to 'data/geolocation' folder")
    return output_path

check = "OK"
if __name__ == "__main__":
    print(check)
    fetch_geolocation_data()