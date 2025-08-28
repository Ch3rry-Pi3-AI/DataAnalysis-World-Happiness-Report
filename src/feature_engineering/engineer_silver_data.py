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
    "healthy_life_expectancy_at_birt": "health_life_expectancy"
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

        return multi_work



if __name__ == "__main__":
    from load_silver_data import load_all_silver_data
    multi_clean, y2021_clean, geo_clean = load_all_silver_data(verbose=True)
    print(multi_clean.head())
    print(y2021_clean.head())
    print(geo_clean.head())
    s2g = SilverToGold()
    gold_df = s2g.run(
        multi_df=multi_clean,
        y2021_df=y2021_clean,
        geo_df=geo_clean,
        restrict_multi_to_2021_countries=True,
        verbose=True,
    )
    print("OK")