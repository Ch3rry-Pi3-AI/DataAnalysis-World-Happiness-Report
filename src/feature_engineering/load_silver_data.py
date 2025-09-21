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
    """

    silver_path = Path(silver_folder)
    multi_file = silver_path / "world_happiness_multi_silver.csv"
    y2021_file = silver_path / "world_happiness_2021_silver.csv"

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

    return multi_df, y2021_df


def load_all_silver_data(
    silver_folder: str = "data/silver",
    verbose: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convenience loader for all silver datasets (happiness only).

    Parameters
    ----------
    silver_folder : str, optional
        Folder path to the silver layer (default: 'data/silver').
    verbose : bool, optional
        If True, print a short summary for each loaded file (default: False).

    Returns
    -------
    (multi_df, y2021_df) : tuple[pandas.DataFrame, pandas.DataFrame]
        The two silver DataFrames in a single call.
    """

    multi_df, y2021_df = load_silver_happiness_data(
        verbose=verbose, silver_folder=silver_folder
    )

    if verbose:
        print("\n✅ Success: Loaded all 🥈 happiness data\n")

    return multi_df, y2021_df


# Allow standalone execution (useful for quick, manual checks)
if __name__ == "__main__":
    _ = load_silver_happiness_data(verbose=True)
    _ = load_all_silver_data(verbose=True)
    print("✅ Silver loaders OK")
