from pathlib import Path
from typing import Tuple
import pandas as pd

def _read_csv(path: Path) -> pd.DataFrame:
    """
    Internal CSV reader with error-handling
    """

    try:
        return pd.read_csv(path)
    
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Could not find '{path.name}' in {path.parent.resolve()}"
        ) from e
    
    except pd.errors.EmptyDataError as e:
        raise ValueError(
            f"Data file '{path.name}' in {path.parent.resolve()} is empty or corrupted"
        )
    
def load_bronze_happiness_data(
        verbose: bool = False,
        bronze_folder: str = 'data/bronze',
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the multi-year and 2021 World Happiness CSVs from the bronze layer.

    Returns
    -------
    (multi_df, y2021_df)
    """
    
    bronze_path = Path(bronze_folder)

    multi_file = bronze_path / "world-happiness-report.csv"
    y2021_file = bronze_path / "world-happiness-report-2021.csv"

    multi_df = _read_csv(multi_file)
    if verbose:
        print(
            f"Loaded multi-year: {multi_df.shape[0]} rows x {multi_df.shape[1]} columns\n"
        )

    y2021_df = _read_csv(y2021_file)
    if verbose:
        print(
            f"Loaded 2021 only: {y2021_df.shape[0]} rows x {y2021_df.shape[1]} columns\n"
        )

    return multi_df, y2021_df

def load_bronze_geolocation_data(
        verbose: bool = False,
        bronze_folder: str = 'data/bronze'
)-> pd.DataFrame:
    """
    Load the geolocation CSV (country code/name/lat/long) from the bronze layer.

    Returns
    -------
    geo_df
    """

    bronze_path = Path(bronze_folder)
    geo_file = bronze_path / "geolocation.csv"
    geo_df = _read_csv(geo_file)

    if verbose:
        print(f"Loaded geolocation: {geo_df.shape[0]} rows x {geo_df.shape[1]} columns\n")

    return geo_df

def load_all_bronze_data(
        bronze_folder: str = 'data/bronze'
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Convenience loader

    Returns
    -------
    (multi_df, y2021_df, geo_df)
    """

    multi_df, y2021_df = load_bronze_happiness_data(bronze_folder)
    geo_df = load_bronze_geolocation_data(bronze_folder)

    print("Success: Loaded all bronze data")
    return multi_df, y2021_df, geo_df

if __name__ == "__main__":
    # Test calls
    _ = load_bronze_happiness_data(verbose=True)
    _ = load_bronze_geolocation_data(verbose=True)
    _ = load_all_bronze_data()
    print("Bronze Loader")