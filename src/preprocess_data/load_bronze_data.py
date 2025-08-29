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
        # Raised when a CSV cannot be found / does not exist
        raise FileNotFoundError(
            f"Could not find '{path.name}' in {path.parent.resolve()}"
        ) from e

    except pd.errors.EmptyDataError as e:
        # Raised when a CSV exists but has no parsable content
        raise ValueError(
            f"Data file '{path.name}' in {path.parent.resolve()} is empty"
        ) from e

    except pd.errors.ParserError as e:
        # Malformed CSV structure (bad rows/columns)
        raise ValueError(
            f"Data file '{path.name}' in {path.parent.resolve()} appears malformed: {e}"
        ) from e


def load_bronze_happiness_data(
    verbose: bool = False,
    bronze_folder: str = "data/bronze",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the multi-year and 2021 World Happiness CSVs from the bronze layer.

    Parameters
    ----------
    verbose : bool, optional
        If True, print a short summary for each loaded file (default: False).
    bronze_folder : str, optional
        Folder path to the bronze layer (default: 'data/bronze').

    Returns
    -------
    (multi_df, y2021_df) : tuple[pandas.DataFrame, pandas.DataFrame]
        `multi_df` is the multi-year table (world-happiness-report.csv);
        `y2021_df` is the 2021-only table (world-happiness-report-2021.csv).

    Notes
    -----
    - Paths are resolved relative to the provided `bronze_folder`.
    - This function only *loads* raw CSVs (no cleaning or validation).
    """

    # ----------------------------------------------------------------------
    # Step 1: Build file paths (cross-platform)
    # ----------------------------------------------------------------------
    bronze_path = Path(bronze_folder)
    multi_file = bronze_path / "world-happiness-report.csv"
    y2021_file = bronze_path / "world-happiness-report-2021.csv"

    # ----------------------------------------------------------------------
    # Step 2: Read with friendly error handling
    # ----------------------------------------------------------------------
    multi_df = _read_csv(multi_file)
    if verbose:
        print(
            f"📄 Loaded multi-year [{multi_file.name}]: "
            f"{multi_df.shape[0]} rows x {multi_df.shape[1]} cols"
        )

    y2021_df = _read_csv(y2021_file)
    if verbose:
        print(
            f"📄 Loaded 2021-only [{y2021_file.name}]: "
            f"{y2021_df.shape[0]} rows x {y2021_df.shape[1]} cols"
        )

    # ----------------------------------------------------------------------
    # Step 3: Return both DataFrames for downstream processing
    # ----------------------------------------------------------------------
    return multi_df, y2021_df


def load_bronze_geolocation_data(
    verbose: bool = False,
    bronze_folder: str = "data/bronze",
) -> pd.DataFrame:
    """
    Load the geolocation CSV from the bronze layer.

    Parameters
    ----------
    verbose : bool, optional
        If True, print a short summary for the loaded file (default: False).
    bronze_folder : str, optional
        Folder path to the bronze layer (default: 'data/bronze').

    Returns
    -------
    pandas.DataFrame
        Geolocation table with at least: country (ISO-ish code), country_name,
        latitude, longitude.

    Notes
    -----
    - This function only *loads* the table. Any renaming/cleaning happens in
      the preprocessing/cleaning stage.
    """

    # ----------------------------------------------------------------------
    # Step 1: Build file path
    # ----------------------------------------------------------------------
    bronze_path = Path(bronze_folder)
    geo_file = bronze_path / "geolocation.csv"

    # ----------------------------------------------------------------------
    # Step 2: Read with friendly error handling
    # ----------------------------------------------------------------------
    geo_df = _read_csv(geo_file)
    if verbose:
        print(
            f"📄 Loaded geolocation [{geo_file.name}]: "
            f"{geo_df.shape[0]} rows x {geo_df.shape[1]} cols"
        )

    # ----------------------------------------------------------------------
    # Step 3: Return DataFrame for downstream processing
    # ----------------------------------------------------------------------
    return geo_df


def load_all_bronze_data(
    bronze_folder: str = "data/bronze",
    verbose: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Convenience loader for all bronze datasets.

    Parameters
    ----------
    bronze_folder : str, optional
        Folder path to the bronze layer (default: 'data/bronze').
    verbose : bool, optional
        If True, print a short summary for each loaded file (default: False).

    Returns
    -------
    (multi_df, y2021_df, geo_df) : tuple[pandas.DataFrame, pandas.DataFrame, pandas.DataFrame]
        The three bronze DataFrames in a single call.

    Notes
    -----
    - Equivalent to calling `load_bronze_happiness_data(...)` and
      `load_bronze_geolocation_data(...)` separately.
    """

    # ----------------------------------------------------------------------
    # Step 1: Load the two happiness tables
    # ----------------------------------------------------------------------
    multi_df, y2021_df = load_bronze_happiness_data(
        verbose=verbose, bronze_folder=bronze_folder
    )

    # ----------------------------------------------------------------------
    # Step 2: Load the geolocation table
    # ----------------------------------------------------------------------
    geo_df = load_bronze_geolocation_data(
        verbose=verbose, bronze_folder=bronze_folder
    )

    if verbose:
        print("\n✅ Success: Loaded all 🥉 data\n")

    # ----------------------------------------------------------------------
    # Step 3: Return all three
    # ----------------------------------------------------------------------
    return multi_df, y2021_df, geo_df


# Allow standalone execution (useful for quick, manual checks)
if __name__ == "__main__":
    # Minimal smoke run
    _ = load_bronze_happiness_data(verbose=True)
    _ = load_bronze_geolocation_data(verbose=True)
    _ = load_all_bronze_data(verbose=True)
    print("✅ Bronze loaders OK")