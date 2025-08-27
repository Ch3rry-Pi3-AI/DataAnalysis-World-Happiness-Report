from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple
import re
import pandas as pd

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

        def _find_col(df: pd.DataFrame, target_norm: str) -> str:
            norm_map = _build_normalised_map(df.columns)
            for n, orig in norm_map.items():
                if n == target_norm:
                    return orig
            raise KeyError(f"Expected a column matching '{target_norm}' in DataFrame (e.g., '{target_norm}' or a close variant).")


        multi_country = _find_col(multi_df, "country_name")
        multi_year = _find_col(multi_df, "year")
        y21_country = _find_col(y2021_df, "country_name")
        y21_year = _find_col(y2021_df, "year")
        geo_country = _find_col(geo_df, "country_name")

        multi_work = multi_df.copy()
        y2021_work = y2021_df.copy()

        if restrict_multi_to_2021_countries:
            valid = set(y2021_work[y21_country].astype(str))
            before = len(multi_work)
            multi_work = multi_work[multi_work[multi_country].astype(str).isin(valid)].copy()
            removed = before - len(multi_work)

            if verbose:
                print(f"Filtered multi-year to 2021 countries: {removed} rows removed")


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