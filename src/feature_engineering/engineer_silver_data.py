from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple
import re
import pandas as pd

# ----------------------------------------------------------------------
# Normalisation helpers
# ----------------------------------------------------------------------

def _snake_normalise(name: str) -> str:
    s = re.sub(r"[^\w]+", "_", name.strip().lower())
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def _build_normalised_map(columns: Iterable[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for c in columns:
        key = _snake_normalise(c)
        if key not in mapping:
            mapping [key] = c
    return mapping

# ----------------------------------------------------------------------
# Aliases (normalised_name -> canonical name)
# Use 2021-style names as canonical targets.
# ----------------------------------------------------------------------

ALIASES: Dict[str, str] = {
    "life_ladder": "ladder_score",
    "log_gdp_per_capita": "logged_gdp_per_capita",
    "healthy_life_expectancy_at_birth": "healthy_life_expectancy"
}

def _apply_aliases(df: pd.DataFrame, aliases: Dict[str, str]) -> pd.DataFrame:
    """
    Use normalised-name aliases to rename columns to canonical targets.
    """
    norm_to_orig = _build_normalised_map(df.columns)
    rename_dict: Dict[str, str] = {}
    for norm_name, orig_name in norm_to_orig.items():
        if norm_name in aliases and aliases[norm_name] != orig_name:
            rename_dict[orig_name] = aliases[norm_name]
    return df.rename(columns=rename_dict) if rename_dict else df
    
def _intersect_and_align(a: pd.DataFrame, b: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Intersect columns between `a` and `b` using normalised names.
    Returns aligned copies with identical column order/names.
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


@dataclass
class SilverToGold:
    silver_folder: str = "data/silver"
    gold_folder: str = "data/gold"
    engineered_name: str = "world_happiness_gold.csv"

    def run(
            self,
            multi_df: pd.DataFrame,
            y2021_df: pd.DataFrame,
            geo_df: pd.DataFrame,
            *,
            restrict_multi_to_2021_countries: bool = True,
            verbose: bool = False
    ) -> pd.DataFrame:

        # ------------------------------------------------------------------
        # Step 1: Locate key columns robustly by normalised name
        # ------------------------------------------------------------------

        def _find_col(df: pd.DataFrame, target_norm: str) -> str:
            norm_map = _build_normalised_map(df.columns)
            for n, orig in norm_map.items():
                if n == target_norm:
                    return orig
            raise KeyError(
                f"Expected a column matching '{target_norm}' (e.g., '{target_norm}' or a close variant)."
            )

        multi_country = _find_col(multi_df, "country_name")
        multi_year    = _find_col(multi_df, "year")
        y21_country   = _find_col(y2021_df, "country_name")
        y21_year      = _find_col(y2021_df, "year")
        geo_country   = _find_col(geo_df, "country_name")
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
                print(f"Filtered multi-year to 2021 countries: {removed} rows removed")

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
        
        multi_work = multi_work.merge(
            country_region, on=multi_country, how="left"
        )

        # ------------------------------------------------------------------
        # Step 4: apply alias renames to harmonise semantics
        # ------------------------------------------------------------------

        multi_work = _apply_aliases(multi_work, ALIASES)
        y2021_work = _apply_aliases(y2021_work, ALIASES)

        # ------------------------------------------------------------------
        # Step 5: intersect & align columns (robust to slight name differences)
        # ------------------------------------------------------------------

        multi_aligned, y2021_aligned = _intersect_and_align(multi_work, y2021_work)

        if verbose:
            print(f"Using {multi_aligned.shape[1]} shared columns for append.")
            print(f"Shared columns: {list(multi_aligned.columns)}")

        # Return the aligned frames to test
        return multi_aligned, y2021_aligned


if __name__ == "__main__":
    from load_silver_data import load_all_silver_data
    multi_clean, y2021_clean, geo_clean = load_all_silver_data(verbose=True)

    s2g = SilverToGold()
    multi_aligned, y2021_aligned = s2g.run(
        multi_df=multi_clean,
        y2021_df=y2021_clean,
        geo_df=geo_clean,
        restrict_multi_to_2021_countries=True,
        verbose=True,
    )

    print("— multi_aligned —")
    print(multi_aligned[multi_aligned["country_name"] == "Afghanistan"].head(25))
    print("\n— y2021_aligned —")
    print(y2021_aligned[y2021_aligned["country_name"] == "Afghanistan"].head(25))
    print("OK")
