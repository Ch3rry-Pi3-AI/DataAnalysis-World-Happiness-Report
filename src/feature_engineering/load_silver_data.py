from pathlib import Path
from typing import Tuple
import pandas as pd


def _read_csv(path: Path) -> pd.DataFrame:
    """
    Read a CSV with friendly errors.

    Parameters
    ----------
    path : pathlib.Path
        Absolute or relative path to the CSV file.

    Returns
    -------
    pandas.DataFrame
        The loaded DataFrame.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If the CSV is empty or malformed.
    """

    # ----------------------------------------------------------------------
    # Try to read; normalise common error cases into clear messages
    # ----------------------------------------------------------------------
    try:
        return pd.read_csv(path)

    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Could not find '{path.name}' in {path.parent.resolve()}"
        ) from e

    except pd.errors.EmptyDataError as e:
        raise ValueError(
            f"Data file '{path.name}' in {path.parent.resolve()} is empty"
        ) from e

    except pd.errors.ParserError as e:
        raise ValueError(
            f"Data file '{path.name}' in {path.parent.resolve()} appears malformed: {e}"
        ) from e


def load_silver_happiness_data(
    verbose: bool = False,
    silver_folder: str = "data/silver",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the cleaned multi-year and 2021 World Happiness CSVs from the silver layer.

    Parameters
    ----------
    verbose : bool, optional
        If True, print a short summary for each loaded file (default: False).
    silver_folder : str, optional
        Folder path to the silver layer (default: 'data/silver').

    Returns
    -------
    (multi_df, y2021_df) : tuple[pandas.DataFrame, pandas.DataFrame]
        `multi_df` is the multi-year cleaned table;
        `y2021_df` is the 2021-only cleaned table.

    Notes
    -----
    - Paths are resolved relative to the provided `silver_folder`.
    - This function only *loads* silver CSVs (no further engineering).
    """

    # ----------------------------------------------------------------------
    # Step 1: Build file paths
    # ----------------------------------------------------------------------
    silver_path = Path(silver_folder)
    multi_file = silver_path / "world_happiness_multi_silver.csv"
    y2021_file = silver_path / "world_happiness_2021_silver.csv"

    # ----------------------------------------------------------------------
    # Step 2: Read with friendly error handling
    # ----------------------------------------------------------------------
    multi_df = _read_csv(multi_file)
    if verbose:
        print(
            f"📄 Loaded silver multi-year [{multi_file.name}]: "
            f"{multi_df.shape[0]} rows x {multi_df.shape[1]} cols"
        )

    y2021_df = _read_csv(y2021_file)
    if verbose:
        print(
            f"📄 Loaded silver 2021-only [{y2021_file.name}]: "
            f"{y2021_df.shape[0]} rows x {y2021_df.shape[1]} cols"
        )

    # ----------------------------------------------------------------------
    # Step 3: Return both DataFrames
    # ----------------------------------------------------------------------
    return multi_df, y2021_df


def load_silver_geolocation_data(
    verbose: bool = False,
    silver_folder: str = "data/silver",
) -> pd.DataFrame:
    """
    Load the cleaned geolocation CSV from the silver layer.

    Parameters
    ----------
    verbose : bool, optional
        If True, print a short summary for the loaded file (default: False).
    silver_folder : str, optional
        Folder path to the silver layer (default: 'data/silver').

    Returns
    -------
    pandas.DataFrame
        Cleaned geolocation table with country_name and coordinates.
    """

    # ----------------------------------------------------------------------
    # Step 1: Build file path
    # ----------------------------------------------------------------------
    silver_path = Path(silver_folder)
    geo_file = silver_path / "geolocation_silver.csv"

    # ----------------------------------------------------------------------
    # Step 2: Read with friendly error handling
    # ----------------------------------------------------------------------
    geo_df = _read_csv(geo_file)
    if verbose:
        print(
            f"📄 Loaded silver geolocation [{geo_file.name}]: "
            f"{geo_df.shape[0]} rows x {geo_df.shape[1]} cols"
        )

    # ----------------------------------------------------------------------
    # Step 3: Return DataFrame
    # ----------------------------------------------------------------------
    return geo_df


def load_all_silver_data(
    silver_folder: str = "data/silver",
    verbose: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Convenience loader for all silver datasets.

    Parameters
    ----------
    silver_folder : str, optional
        Folder path to the silver layer (default: 'data/silver').
    verbose : bool, optional
        If True, print a short summary for each loaded file (default: False).

    Returns
    -------
    (multi_df, y2021_df, geo_df) : tuple[pandas.DataFrame, pandas.DataFrame, pandas.DataFrame]
        The three silver DataFrames in a single call.
    """

    # ----------------------------------------------------------------------
    # Step 1: Load the two happiness tables
    # ----------------------------------------------------------------------
    multi_df, y2021_df = load_silver_happiness_data(
        verbose=verbose, silver_folder=silver_folder
    )

    # ----------------------------------------------------------------------
    # Step 2: Load the geolocation table
    # ----------------------------------------------------------------------
    geo_df = load_silver_geolocation_data(
        verbose=verbose, silver_folder=silver_folder
    )

    if verbose:
        print("\n✅ Success: Loaded all 🥈 data\n")

    # ----------------------------------------------------------------------
    # Step 3: Return all three
    # ----------------------------------------------------------------------
    return multi_df, y2021_df, geo_df


# Allow standalone execution (useful for quick, manual checks)
if __name__ == "__main__":
    _ = load_silver_happiness_data(verbose=True)
    _ = load_silver_geolocation_data(verbose=True)
    _ = load_all_silver_data(verbose=True)
    print("✅ Silver loaders OK")
