"""
Bronze -> Silver cleaning for the World Happiness project.

This module contains helper functions and a BronzeToSilver class that:
- standardises column names,
- filters and imputes missing values,
- normalises region names,
- and writes cleaned CSVs into the 🥈 silver layer.

The goal is to provide a reproducible, teaching-friendly pipeline:
bronze/raw -> silver/cleaned.
"""

# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import re
import pandas as pd


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _to_snake_case(name: str) -> str:
    """
    Convert a string to snake_case.

    Examples
    --------
    'Country Name' -> 'country_name'
    'regionalIndicator' -> 'regional_indicator'
    """

    # Trim whitespace
    name = name.strip()

    # Split CamelCase
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)

    # Replace non-alphanumeric characters with "_"
    name = re.sub(r"[^0-9A-Za-z]+", "_", name)

    # Collapse to single "_", trim, and lower-case
    name = re.sub(r"_+", "_", name).strip("_").lower()

    return name


def _snake_case_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply `_to_snake_case` to all DataFrame column names.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with original column names.

    Returns
    -------
    pandas.DataFrame
        Copy of the DataFrame with snake_case column names.
    """

    out = df.copy()
    out.columns = [_to_snake_case(c) for c in out.columns]
    return out


def _numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    Identify numeric columns in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    list of str
        Names of numeric columns.
    """

    return [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]


def _ensure_dir(path: Path) -> None:
    """
    Ensure a directory exists (create parents if needed).

    Parameters
    ----------
    path : pathlib.Path
    """

    path.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------
# Core Cleaner
# ----------------------------------------------------------------------

@dataclass
class BronzeToSilver:
    """
    Cleaner for bronze -> silver World Happiness datasets.

    Provides methods to:
    - standardise and clean the multi-year and 2021 datasets,
    - clean the geolocation dataset,
    - save each cleaned DataFrame into the 🥈 silver layer.
    """

    # ------------------------------------------------------------------
    # Step 1: Standardisation
    # ------------------------------------------------------------------

    @staticmethod
    def _standardise_base(
        df: pd.DataFrame, *, default_year: Optional[int] = 2021
    ) -> pd.DataFrame:
        """
        Standardise DataFrame structure:
        - snake_case columns,
        - ensure `country_name`,
        - add `year` column if missing.

        Parameters
        ----------
        df : pandas.DataFrame
            Input dataset.
        default_year : int or None, optional
            Value for `year` if missing (default: 2021).

        Returns
        -------
        pandas.DataFrame
            Standardised DataFrame.
        """

        df = _snake_case_columns(df)

        if "country_name" not in df.columns and "country" in df.columns:
            df = df.rename(columns={"country": "country_name"})

        if default_year is not None and "year" not in df.columns:
            df["year"] = default_year

        if "country_name" in df.columns:
            df["country_name"] = df["country_name"].astype(str).str.strip()

        return df
    
    # ------------------------------------------------------------------
    # Step 2: Filtering
    # ------------------------------------------------------------------

    @staticmethod
    def _basic_filter(df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop rows with missing `country_name`.

        Parameters
        ----------
        df : pandas.DataFrame

        Returns
        -------
        pandas.DataFrame
        """

        if "country_name" in df.columns:
            df = df.dropna(subset=["country_name"])
        return df

    # ------------------------------------------------------------------
    # Step 3: Imputation
    # ------------------------------------------------------------------

    @staticmethod
    def _impute_numeric(df: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing numeric values:
        1) fill within-country mean,
        2) fill remaining with global mean.

        Parameters
        ----------
        df : pandas.DataFrame

        Returns
        -------
        pandas.DataFrame
        """

        num_cols = _numeric_columns(df)
        if not num_cols:
            return df

        if "country_name" in df.columns:
            df[num_cols] = (
                df.groupby("country_name")[num_cols]
                .transform(lambda g: g.fillna(g.mean()))
            )

        for col in num_cols:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].mean())

        return df
    
    # ------------------------------------------------------------------
    # Step 4: Region Normalisation
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_regions(df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardise region labels for consistency.

        Parameters
        ----------
        df : pandas.DataFrame

        Returns
        -------
        pandas.DataFrame
        """

        if "regional_indicator" in df.columns:
            replacements = {
                "Eastern Asia": "East Asia",
                "Southeastern Asia": "Southeast Asia",
                "Southern Asia": "South Asia",
            }

            df["regional_indicator"] = df["regional_indicator"].replace(replacements)
        
        return df
    
    # ------------------------------------------------------------------
    # Step 5: Geolocation Standardisation
    # ------------------------------------------------------------------

    @staticmethod
    def _standardise_geo_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardise geolocation dataset:
        - snake_case columns,
        - strip whitespace from `country_name`.

        Parameters
        ----------
        df : pandas.DataFrame

        Returns
        -------
        pandas.DataFrame
        """

        df = _snake_case_columns(df)
        if "country_name" in df.columns:
            df["country_name"] = df["country_name"].astype(str).str.strip()
        return df

    @staticmethod
    def _drop_missing_coords(df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop rows missing latitude/longitude.

        Parameters
        ----------
        df : pandas.DataFrame

        Returns
        -------
        pandas.DataFrame
        """

        before = len(df)
        df = df.dropna(subset=["latitude", "longitude"])
        after = len(df)
        if after != before:
            print(f"Dropped {before - after} rows without lat/lon\n")
        return df

    # ------------------------------------------------------------------
    # Step 6: Persistence
    # ------------------------------------------------------------------

    @staticmethod
    def _save_silver(
        df: pd.DataFrame, filename: str, silver_folder: str = "data/silver"
    ) -> Path:
        """
        Save a DataFrame to the silver folder.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame to save.
        filename : str
            Output filename.
        silver_folder : str, optional
            Path to silver folder (default: 'data/silver').

        Returns
        -------
        pathlib.Path
            Path to the saved file.
        """

        silver_path = Path(silver_folder)
        _ensure_dir(silver_path)
        out = silver_path / filename
        df.to_csv(out, index=False)
        return out

    # ------------------------------------------------------------------
    # Step 7: Public Cleaners
    # ------------------------------------------------------------------

    def clean_multi_year(self, df_multi: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the multi-year World Happiness dataset.

        Steps
        -----
        1. Standardise columns and ensure `country_name`.
        2. Drop rows with missing `country_name`.
        3. Impute missing numeric values.
        4. Normalise region names.

        Returns
        -------
        pandas.DataFrame
        """

        df = self._standardise_base(df_multi)
        df = self._basic_filter(df)
        df = self._impute_numeric(df)
        df = self._normalise_regions(df)
        print("✅ Multi-year cleaned\n")
        return df

    def clean_y2021(self, df_2021: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the 2021-only World Happiness dataset.

        Steps
        -----
        1. Standardise columns and add `year=2021` if missing.
        2. Drop rows with missing `country_name`.
        3. Impute missing numeric values.
        4. Normalise region names.

        Returns
        -------
        pandas.DataFrame
        """

        df = self._standardise_base(df_2021, default_year=2021)
        df = self._basic_filter(df)
        df = self._impute_numeric(df)
        df = self._normalise_regions(df)
        print("✅ 2021-only cleaned\n")
        return df

    def clean_geolocation(self, df_geo: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the geolocation dataset.

        Steps
        -----
        1. Snake-case and standardise `country_name`.
        2. Drop rows with missing `country_name`.
        3. Drop rows missing lat/lon.

        Returns
        -------
        pandas.DataFrame
        """

        df = self._standardise_geo_columns(df_geo)
        df = self._basic_filter(df)
        df = self._drop_missing_coords(df)
        print("✅ Geolocation cleaned\n")
        return df

    # ------------------------------------------------------------------
    # Step 8: Saving Methods
    # ------------------------------------------------------------------

    def save_multi(self, df: pd.DataFrame, silver_folder: str = "data/silver") -> Path:
        """Save cleaned multi-year dataset to silver folder."""
        return self._save_silver(df, "world_happiness_multi_silver.csv", silver_folder)

    def save_y2021(self, df: pd.DataFrame, silver_folder: str = "data/silver") -> Path:
        """Save cleaned 2021-only dataset to silver folder."""
        return self._save_silver(df, "world_happiness_2021_silver.csv", silver_folder)

    def save_geolocation(
        self, df: pd.DataFrame, silver_folder: str = "data/silver"
    ) -> Path:
        """Save cleaned geolocation dataset to silver folder."""
        return self._save_silver(df, "geolocation_silver.csv", silver_folder)


# ----------------------------------------------------------------------
# Standalone execution (quick smoke run)
# ----------------------------------------------------------------------

if __name__ == "__main__":

    # Instantiate the transformer (dataclass holds folders and output filename).
    cleaner = BronzeToSilver()

    paths = {
        "multi": Path("data/bronze/world-happiness-report.csv"),
        "y2021": Path("data/bronze/world-happiness-report-2021.csv"),
        "geo": Path("data/bronze/geolocation.csv"),
    }

    # Existence check
    for label, p in paths.items():
        if not p.exists():
            raise FileNotFoundError(f"Missing {label} bronze file at: {p.resolve()}")

    # Load -> clean
    multi_clean = cleaner.clean_multi_year(pd.read_csv(paths["multi"]))
    y2021_clean = cleaner.clean_y2021(pd.read_csv(paths["y2021"]))
    geo_clean = cleaner.clean_geolocation(pd.read_csv(paths["geo"]))

    # Save -> silver
    cleaner.save_multi(multi_clean)
    cleaner.save_y2021(y2021_clean)
    cleaner.save_geolocation(geo_clean)

    # Summary
    print("✅ Saved cleaned CSVs to 🥈 folder:")
    for name, df in [("multi", multi_clean), ("y2021", y2021_clean), ("geo", geo_clean)]:
        print(f"{name}: {df.shape[0]} rows x {df.shape[1]} cols")
