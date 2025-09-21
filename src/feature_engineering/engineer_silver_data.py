"""
Silver -> Gold transformation for the World Happiness project.

This module contains helper functions and a SilverToGold class that:
- normalises and aligns multi-year and 2021-only datasets,
- applies alias mappings to harmonise semantics,
- injects regional labels from 2021 into the multi-year table,
- appends with 2021 precedence on (country_name, year),
- and writes engineered CSVs into the 🥇 gold layer.

The goal is to provide a reproducible, teaching-friendly pipeline:
silver/cleaned -> gold/engineered.
"""

# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple
import re
import pandas as pd

# ----------------------------------------------------------------------
# Normalisation helpers
# ----------------------------------------------------------------------

def _snake_normalise(name: str) -> str:
    """
    Convert a string to normalised snake_case.

    Parameters
    ----------
    name : str
        Original column name.

    Returns
    -------
    str
        Normalised snake_case string (lowercased, non-alphanumerics as underscores).
    """
    s = re.sub(r"[^\w]+", "_", name.strip().lower())
    s = re.sub(r"_+", "_", s).strip("_")
    return s


# ----------------------------------------------------------------------
# Normalised Map (normalised_name -> original column)
# ----------------------------------------------------------------------

def _build_normalised_map(columns: Iterable[str]) -> Dict[str, str]:
    """
    Build a mapping from normalised names to original column names.

    Parameters
    ----------
    columns : Iterable[str]

    Returns
    -------
    dict[str, str]
        Mapping of normalised_name -> first-occurring original name.
    """
    mapping: Dict[str, str] = {}
    for c in columns:
        key = _snake_normalise(c)
        if key not in mapping:
            mapping[key] = c
    return mapping


# ----------------------------------------------------------------------
# Aliases (normalised_names -> canonical [2021-style] names)
# ----------------------------------------------------------------------

ALIASES: Dict[str, str] = {
    "life_ladder": "ladder_score",
    "log_gdp_per_capita": "logged_gdp_per_capita",
    "healthy_life_expectancy_at_birth": "healthy_life_expectancy",
}

def _apply_aliases(df: pd.DataFrame, aliases: Dict[str, str]) -> pd.DataFrame:
    """
    Rename DataFrame columns to canonical targets using normalised-name aliases.
    """
    norm_to_orig = _build_normalised_map(df.columns)
    rename_dict: Dict[str, str] = {}
    for norm_name, orig_name in norm_to_orig.items():
        if norm_name in aliases and aliases[norm_name] != orig_name:
            rename_dict[orig_name] = aliases[norm_name]
    return df.rename(columns=rename_dict) if rename_dict else df


# ----------------------------------------------------------------------
# Intersect & Align (harmonise shared columns across DataFrames)
# ----------------------------------------------------------------------

def _intersect_and_align(a: pd.DataFrame, b: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Intersect columns between two DataFrames using normalised names
    and return aligned copies with identical column order and names.
    """
    a_map = _build_normalised_map(a.columns)
    b_map = _build_normalised_map(b.columns)
    shared_keys = sorted(set(a_map).intersection(b_map))
    if not shared_keys:
        raise ValueError("No shared columns found between the two DataFrames after normalisation")

    def _pretty(orig: str) -> str:
        snake = _snake_normalise(orig)
        return orig if orig == snake else snake

    out_cols = [_pretty(a_map[k]) for k in shared_keys]
    a_aligned = a.loc[:, [a_map[k] for k in shared_keys]].copy()
    b_aligned = b.loc[:, [b_map[k] for k in shared_keys]].copy()
    a_aligned.columns = out_cols
    b_aligned.columns = out_cols
    return a_aligned, b_aligned


# ----------------------------------------------------------------------
# Column Finder (locate original name from normalised target)
# ----------------------------------------------------------------------

def _find_col(df: pd.DataFrame, target_norm: str) -> str:
    """
    Locate the original column name corresponding to a normalised target.
    """
    norm_map = _build_normalised_map(df.columns)
    for n, orig in norm_map.items():
        if n == target_norm:
            return orig
    raise KeyError(
        f"Expected a column matching '{target_norm}' (e.g., '{target_norm}' or a close variant)."
    )


# ----------------------------------------------------------------------
# Core class
# ----------------------------------------------------------------------

@dataclass
class SilverToGold:
    """
    Transformer for silver -> gold World Happiness datasets.

    Attributes
    ----------
    silver_folder: str
        Path to the silver layer folder (input).
    gold_folder: str
        Path to the gold layer folder (output).
    engineered_name: str
        Output CSV filename for the engineered dataset.
    """

    silver_folder: str = "data/silver"
    gold_folder: str = "data/gold"
    engineered_name: str = "world_happiness_gold.csv"

    def run(
        self,
        multi_df: pd.DataFrame,
        y2021_df: pd.DataFrame,
        *,
        restrict_multi_to_2021_countries: bool = True,
        verbose: bool = False,
        save_output: bool = True,
    ) -> pd.DataFrame:
        """
        Execute the silver -> gold transformation (no geolocation required).

        Parameters
        ----------
        multi_df: pandas.DataFrame
            Cleaned multi-year dataset from the silver layer.
        y2021_df: pandas.DataFrame
            Cleaned 2021-only dataset from the silver layer.
        restrict_multi_to_2021_countries: bool, optional
            If True, filter multi_df to only countries present in y2021_df (default: True)
        verbose: bool, optional
            If True, print progress information (default: False).
        save_output: bool, optional
            If True, save the engineered DataFrame to the gold folder (default: True)

        Returns
        -------
        pandas.DataFrame
            Engineered (gold) DataFrame with aligned columns and 2021-precedence append.
        """

        # ------------------------------------------------------------------
        # Step 1: Locate key columns robustly by normalised name
        # ------------------------------------------------------------------
        multi_country = _find_col(multi_df, "country_name")
        multi_year    = _find_col(multi_df, "year")
        y21_country   = _find_col(y2021_df, "country_name")
        y21_year      = _find_col(y2021_df, "year")
        y21_region    = _find_col(y2021_df, "regional_indicator")

        # ------------------------------------------------------------------
        # Step 2: Restrict multi-year to 2021 countries (optional)
        # ------------------------------------------------------------------
        multi_work = multi_df.copy()
        y2021_work = y2021_df.copy()

        if restrict_multi_to_2021_countries:
            valid = set(y2021_work[y21_country].astype(str))
            before = len(multi_work)
            multi_work = multi_work[multi_work[multi_country].astype(str).isin(valid)].copy()
            removed = before - len(multi_work)
            if verbose:
                print(f"Filtered multi-year to 2021 countries: {removed} rows removed\n")

        # ------------------------------------------------------------------
        # Step 3: Inject `regional_indicator` into multi-year from 2021 mapping
        # ------------------------------------------------------------------
        country_region = (
            y2021_work[[y21_country, y21_region]]
            .drop_duplicates()
            .rename(columns={y21_country: multi_country, y21_region: "regional_indicator"})
        )

        if "regional_indicator" in multi_work.columns and multi_country != "country_name":
            multi_work = multi_work.drop(columns="regional_indicator")

        multi_work = multi_work.merge(country_region, on=multi_country, how="left")

        # ------------------------------------------------------------------
        # Step 4: Apply alias renames to harmonise semantics
        # ------------------------------------------------------------------
        multi_work = _apply_aliases(multi_work, ALIASES)
        y2021_work = _apply_aliases(y2021_work, ALIASES)

        # ------------------------------------------------------------------
        # Step 5: Intersect & align columns (robust to slight name differences)
        # ------------------------------------------------------------------
        multi_aligned, y2021_aligned = _intersect_and_align(multi_work, y2021_work)

        if verbose:
            print(f"Using {multi_aligned.shape[1]} shared columns for append.")
            print(f"Shared columns: {list(multi_aligned.columns)}")

        # ------------------------------------------------------------------
        # Step 6: Append with precedence to 2021 rows on (country_name, year)
        # ------------------------------------------------------------------
        union = pd.concat([multi_aligned, y2021_aligned], ignore_index=True)
        y2021_keys = set(zip(y2021_aligned["country_name"].astype(str), y2021_aligned["year"]))

        union["_is_2021_row"] = list(zip(union["country_name"].astype(str), union["year"]))
        union["_is_2021_row"] = union["_is_2021_row"].isin(y2021_keys).astype(int)

        appended = (
            union.sort_values(["country_name", "year", "_is_2021_row"])  # 0 before 1
                 .drop_duplicates(["country_name", "year"], keep="last")
                 .drop(columns=["_is_2021_row"])
                 .reset_index(drop=True)
        )

        if verbose:
            print(f"Appended DataFrame shape: {appended.shape}\n")

        # ------------------------------------------------------------------
        # Step 7: Save to gold
        # ------------------------------------------------------------------
        if save_output:
            out_dir = Path(self.gold_folder)
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / self.engineered_name
            appended.to_csv(out_path, index=False)
            if verbose:
                print(f"Saved gold dataset: {out_path.resolve()}\n")

        return appended


# ----------------------------------------------------------------------
# Script Entry Point (quick smoke run)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # Load inputs from the silver layer (helper returns 2 DataFrames).
    from load_silver_data import load_all_silver_data
    multi_clean, y2021_clean = load_all_silver_data(verbose=True)

    # Instantiate the transformer.
    s2g = SilverToGold()

    # Run the end-to-end silver -> gold transformation.
    gold_df = s2g.run(
        multi_df=multi_clean,
        y2021_df=y2021_clean,
        restrict_multi_to_2021_countries=True,
        verbose=True,
        save_output=True,
    )

    # Show the transformer configuration (dataclass repr is concise).
    print("\n— SilverToGold configuration —")
    print(s2g)

    # Quick preview of the engineered dataset.
    print("\n— Gold preview (first 10 rows) —")
    try:
        print(gold_df.head(10).to_string(index=False))
    except Exception:
        print(gold_df.head(10))
