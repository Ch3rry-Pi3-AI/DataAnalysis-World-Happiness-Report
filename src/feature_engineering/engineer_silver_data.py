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
# Aliases (normalised_names -> canonical [2021-style] names)
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

# ----------------------------------------------------------------------
# Core class
# ----------------------------------------------------------------------

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
            verbose: bool = False,
            save_output = True
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

        # ------------------------------------------------------------------
        # Step 6: append with precedence to 2021 rows on (country_name, year)
        # ------------------------------------------------------------------
        
        union = pd.concat([multi_aligned, y2021_aligned], ignore_index=True)

        y2021_keys = set(zip(
            y2021_aligned["country_name"].astype(str),
            y2021_aligned["year"],
        ))

        union["_is_2021_row"] = list(zip(union["country_name"].astype(str), union["year"]))
        union["_is_2021_row"] = union["_is_2021_row"].isin(y2021_keys).astype(int)

        appended = (
            union.sort_values(["country_name", "year", "_is_2021_row"])
                 .drop_duplicates(["country_name", "year"], keep="last")
                 .drop(columns=["_is_2021_row"])
                 .reset_index(drop=True)
        )

        if verbose:
            print(f"Appended DataFrame shape: {appended.shape}")

        # ------------------------------------------------------------------
        # Step 7: merge with geolocation on country_name
        # ------------------------------------------------------------------
        geo_renamed = geo_df.rename(columns={geo_country: "country_name"})
        merged = appended.merge(
            geo_renamed,
            on="country_name",
            how="left",
            suffixes=("", "_geo"),
        )

        if verbose:
            missing_geo = merged["latitude"].isna().sum() if "latitude" in merged.columns else len(merged)
            print(f"After geo merge: {merged.shape[0]} rows × {merged.shape[1]} cols "
                  f"(rows missing coords: {missing_geo}).")

        # ------------------------------------------------------------------
        # Step 8: save to gold
        # ------------------------------------------------------------------
        out_dir = Path(self.gold_folder)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / self.engineered_name
        merged.to_csv(out_path, index=False)
        if verbose:
            print(f"Saved gold dataset: {out_path.resolve()}")

        return merged


if __name__ == "__main__":
    from load_silver_data import load_all_silver_data
    multi_clean, y2021_clean, geo_clean = load_all_silver_data(verbose=True)

    s2g = SilverToGold()
    gold_df = s2g.run(
        multi_df=multi_clean,
        y2021_df=y2021_clean,
        geo_df=geo_clean,
        restrict_multi_to_2021_countries=True,
        verbose=True,
        save_output=True
    )

    # Quick smoke test
    print("\n— gold (Afghanistan) —")
    print(
        gold_df.loc[gold_df["country_name"] == "Afghanistan",
                    ["country_name","year","regional_indicator","ladder_score","logged_gdp_per_capita","latitude","longitude"]]
               .sort_values("year")
               .head(25)
    )
    print("\nSaved rows:", len(gold_df))
    print("OK")
    