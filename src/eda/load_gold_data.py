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


def load_gold_happiness_data(
    verbose: bool = False,
    gold_folder: str = "data/gold",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the appended and merged World Happiness Report CSV from the gold layer.

    Parameters
    ----------
    verbose : bool, optional
        If True, print a short summary for each loaded file (default: False).
    gold_folder : str, optional
        Folder path to the gold layer (default: 'data/gold').

    Returns
    -------
    gold_df : pandas.DataFrame
        `gold_df` is the appended and merged table.

    Notes
    -----
    - Paths are resolved relative to the provided `gold_folder`.
    - This function only *loads* gold CSV.
    """

    # ----------------------------------------------------------------------
    # Step 1: Build file paths
    # ----------------------------------------------------------------------

    gold_path = Path(gold_folder)
    gold_file = gold_path / "world_happiness_gold.csv"

    # ----------------------------------------------------------------------
    # Step 2: Read with friendly error handling
    # ----------------------------------------------------------------------

    gold_df = _read_csv(gold_file)
    if verbose:
        print(
            f"📄 Loaded gold data [{gold_file.name}]: "
            f"{gold_df.shape[0]} rows x {gold_df.shape[1]} cols"
        )

    # ----------------------------------------------------------------------
    # Step 3: Return DataFrame
    # ----------------------------------------------------------------------
    
    return gold_df


# Allow standalone execution (useful for quick, manual checks)
if __name__ == "__main__":
    _ = load_gold_happiness_data(verbose=True)
    print("✅ Gold loader OK")
