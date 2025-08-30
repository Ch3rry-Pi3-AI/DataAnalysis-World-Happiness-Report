"""
Silver -> Gold transformation for the World Happiness project.

This module contains helper functions and a SilverToGold class that:
- normalises and aligns multi-year, 2021-only, and geolocation datasets,
- applies alias mappings to harmonise semantics,
- merges with geolocation coordinates,
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

    # Lower-case and trim the input, then replace any run of non-word chars with a single underscore.
    s = re.sub(r"[^\w]+", "_", name.strip().lower())            # e.g. " GDP / Capita " -> "gdp_capita"

    # Collapse multiple underscores and remove any leading/trailing underscores.
    s = re.sub(r"_+", "_", s).strip("_")                        # e.g. "__gdp__per__capita__" -> "gdp_per_capita"

    # Return the normalised snake_case string.
    return s

def _build_normalised_map(columns: Iterable[str]) -> Dict[str, str]:
    """
    Build a mapping from normalised names to original column names.

    Parameters
    ----------
    columns : Iterable[str]
        Iterable of original column names.

    Returns
    -------
    dict[str, str]
        Mapping of normalised_name -> first-occurring original name.
    """
    
    # Start with an empty mapping (normalised_name -> first-seen original column).
    mapping: Dict[str, str] = {}

    # Walk through the provided column names in order.
    for c in columns:

        # Compute the normalised key for this column.
        key = _snake_normalise(c)

        # Only keep the first occurrence for each normalised key (stable mapping).
        if key not in mapping:
            mapping[key] = c  

    # Return the mapping for downstream lookups.
    return mapping

# ----------------------------------------------------------------------
# Aliases (normalised_names -> canonical [2021-style] names)
# ----------------------------------------------------------------------

# Map *normalised* source names to canonical 2021-style column names.
ALIASES: Dict[str, str] = {
    "life_ladder": "ladder_score",
    "log_gdp_per_capita": "logged_gdp_per_capita",
    "healthy_life_expectancy_at_birth": "healthy_life_expectancy",
}

def _apply_aliases(df: pd.DataFrame, aliases: Dict[str, str]) -> pd.DataFrame:
    """
    Rename DataFrame columns to canonical targets using normalise-name aliases.

    Parameters
    ----------
    df: pandas.DataFrame
        Input DataFrame with original column names.
    aliases: dict[str, str]
        Mapping of normalised_name -> canonical target name.

    Returns
    -------
    pandas.DataFrame
        Copy of the DataFrame with columns renames where aliases apply
    """

    # Build a lookup from normalised_name -> original_name for the current DataFrame.
    norm_to_orig = _build_normalised_map(df.columns)

    # Prepare a rename dict mapping original_name -> canonical_target.
    rename_dict: Dict[str, str] = {}

    # For each normalised key in the DataFrame ...
    for norm_name, orig_name in norm_to_orig.items():

        # ... if we have an alias and the original differs from the canonical ...
        if norm_name in aliases and aliases[norm_name] != orig_name:

            # ... schedule a rename.
            rename_dict[orig_name] = aliases[norm_name]  # e.g. "life_ladder" -> "ladder_score"

    # Apply renames if any; otherwise return the DataFrame untouched.
    return df.rename(columns=rename_dict) if rename_dict else df
    

def _intersect_and_align(a: pd.DataFrame, b: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Intersect columns between `a` and `b` using normalised names.
    Returns aligned copies with identical column order/names.
    """
    # Build normalised_name -> original_name maps for both DataFrames.
    a_map = _build_normalised_map(a.columns)
    b_map = _build_normalised_map(b.columns)

    # Compute the set of shared normalised keys (i.e., common columns ignoring minor name differences).
    shared_keys = sorted(set(a_map).intersection(b_map))

    if not shared_keys:

        # No overlap after normalisation — bail out with a clear error.
        raise ValueError("No shared columns found between the two DataFrames after normalisation")

    # Pretty-name helper
    def _pretty(orig: str) -> str:
        snake = _snake_normalise(orig)

        # If the original is already snake_case, keep it; otherwise show the snake_case.
        return orig if orig == snake else snake

    # Create the output column names in a stable order.
    out_cols = [_pretty(a_map[k]) for k in shared_keys]

    # Select and copy the shared columns from each DataFrame in the same order.
    a_aligned = a.loc[:, [a_map[k] for k in shared_keys]].copy()
    b_aligned = b.loc[:, [b_map[k] for k in shared_keys]].copy()

    # Rename both to the common set of names so downstream concatenation/merges are trivial.
    a_aligned.columns = out_cols
    b_aligned.columns = out_cols

    # Return the aligned DataFrames (same columns, same order, same names).
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
            # Build a mapping from normalised_name -> original_name for columns in df.
            norm_map = _build_normalised_map(df.columns)

            # Scan for the target normalised name and return the original column name when found.
            for n, orig in norm_map.items():
                if n == target_norm:
                    return orig

            # If nothing matched, raise a clear error with a helpful hint.
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

        # Build the set of valid country labels from the 2021 dataset.
        if restrict_multi_to_2021_countries:
            
            # Cast to str on both sides to avoid type-mismatch issues before the membership test.
            valid = set(y2021_work[y21_country].astype(str))

            # Keep a count so we can report how many rows were removed by the filter.
            before = len(multi_work)

            # Filter multi_work down to only those rows whose country is present in 2021.
            multi_work = multi_work[multi_work[multi_country].astype(str).isin(valid)].copy()

            # Number of rows dropped by the restriction.
            removed = before - len(multi_work)

            if verbose:
                print(f"Filtered multi-year to 2021 countries: {removed} rows removed\n")

        # ------------------------------------------------------------------
        # Step 3: Inject `regional_indicator` into multi-year from 2021 mapping
        # ------------------------------------------------------------------

        # Build a country -> regional_indicator lookup from the 2021 dataset.
        country_region = (
            y2021_work[[y21_country, y21_region]]
            .drop_duplicates()  # ensure one row per country/region pairing
            .rename(columns={y21_country: multi_country, y21_region: "regional_indicator"})
        )

        # If multi_work has 'regional_indicator' column AND the country column name != 'country_name'...
        if "regional_indicator" in multi_work.columns and multi_country != "country_name":
            
            # ... drop the existing region column to avoid duplicate/conflicting columns at merge time.
            multi_work = multi_work.drop(columns="regional_indicator")

        # Left-join the region info onto the multi-year data so every country gets its 2021 region label.
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
        
        # Combine the aligned multi-year and 2021 DataFrames into a single table.
        union = pd.concat([multi_aligned, y2021_aligned], ignore_index=True)

        # Build the set of (country_name, year) keys that originate from the 2021 dataset.
        y2021_keys = set(zip(
            # Cast country to str on both sides to avoid type mismatches in tuple comparisons.
            y2021_aligned["country_name"].astype(str),
            y2021_aligned["year"],
        ))

        # Create (country_name, year) key and flag for whether that key exists in the 2021 set.
        union["_is_2021_row"] = list(zip(union["country_name"].astype(str), union["year"]))
        union["_is_2021_row"] = union["_is_2021_row"].isin(y2021_keys).astype(int)

        # Sort so non-2021 rows (0) come first and 2021 rows (1) come last.
        appended = (
            union.sort_values(["country_name", "year", "_is_2021_row"])   # 0 before 1
                 .drop_duplicates(["country_name", "year"], keep="last")  # keep the 2021 row if present
                 .drop(columns=["_is_2021_row"])                          # remove helper flag
                 .reset_index(drop=True)                                  # tidy index
        )

        if verbose:
            print(f"Appended DataFrame shape: {appended.shape}\n")


        # ------------------------------------------------------------------
        # Step 7: harmonise geo country names to match happiness names
        # ------------------------------------------------------------------

        # Map geo country labels -> happiness labels 
        geo_to_happy = {
            "Congo [Republic]": "Congo (Brazzaville)",
            "Congo [DRC]": "Congo (Brazzaville)",  
            "Hong Kong": "Hong Kong S.A.R. of China",
            "Côte d'Ivoire": "Ivory Coast",
            "Myanmar [Burma]": "Myanmar",
            "Cyprus": "North Cyprus",
            "Macedonia [FYROM]": "North Macedonia",
            "Taiwan": "Taiwan Province of China",
        }

        # Work on a copy; rename the geo country column to 'country_name' for a clean merge key
        geo_harmonised = geo_df.rename(columns={geo_country: "country_name"}).copy()

        # Apply the mapping
        if "country_name" in geo_harmonised.columns:
            geo_harmonised["country_name"] = (
                geo_harmonised["country_name"].replace(geo_to_happy)
            )

        if verbose:
            n_changed = sum(
                1
                for v in geo_df[geo_country].astype(str).unique()
                if v in geo_to_happy
            )
            print(f"Harmonised geo names using {n_changed} explicit mappings.\n")

        # ------------------------------------------------------------------
        # Step 8: merge with geolocation on country_name
        # ------------------------------------------------------------------

        # Standardise the geo country column name to match the merge key used in `appended`
        geo_renamed = geo_df.rename(columns={geo_country: "country_name"})

        # Left-join geolocation onto the happiness data.
        merged = appended.merge(
            geo_renamed,
            on="country_name",
            how="left",
            suffixes=("", "_geo"),
        )

        if verbose:
            missing_geo = merged["latitude"].isna().sum() if "latitude" in merged.columns else len(merged)
            print(f"After geo merge: {merged.shape[0]} rows x {merged.shape[1]} cols "
                  f"(rows missing coords: {missing_geo}).\n")

        # ------------------------------------------------------------------
        # Step 9: save to gold
        # ------------------------------------------------------------------

        # Ensure the gold output directory exists (create parents if needed).
        out_dir = Path(self.gold_folder)
        out_dir.mkdir(parents=True, exist_ok=True)

        # Compose the full output path and write the engineered dataset as CSV (no row index).
        out_path = out_dir / self.engineered_name
        merged.to_csv(out_path, index=False)
        
        if verbose:
            print(f"Saved gold dataset: {out_path.resolve()}\n")

        return merged


# ----------------------------------------------------------------------
# Script Entry Point (quick smoke run)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    
    # Load inputs from the silver layer (helper returns 3 DataFrames).
    from load_silver_data import load_all_silver_data
    multi_clean, y2021_clean, geo_clean = load_all_silver_data(verbose=True)

    # Instantiate the transformer (dataclass holds folders and output filename).
    s2g = SilverToGold()

    # Run the end-to-end silver -> gold transformation.
    gold_df = s2g.run(
        multi_df=multi_clean,
        y2021_df=y2021_clean,
        geo_df=geo_clean,
        restrict_multi_to_2021_countries=True,
        verbose=True,
        save_output=True,
    )

    # Show the transformer configuration (dataclass repr is concise and readable).
    print("\n— SilverToGold configuration —")
    print(s2g)

    # Quick preview of the engineered dataset.
    print("\n— Gold preview (first 10 rows) —")
    try:
        # to_string avoids truncated columns in some terminals.
        print(gold_df.head(10).to_string(index=False))
    except Exception:
        print(gold_df.head(10))
