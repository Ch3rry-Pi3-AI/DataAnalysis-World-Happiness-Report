"""
Bronze → Silver cleaning for the World Happiness project.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import re
import pandas as pd
from pathlib import Path

# ------------------------------- #
# Helpers
# ------------------------------- #

def _to_snake_case(name: str) -> str:
    """
    Convert 'Country Name' → 'country_name' or 
    'regionalIndicator' → 'regional_indicator'
    """
    
    # Trim whitespace
    name = name.strip()

    # Split CamelCase
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)     

    # Replace non-alphanumeric characters with "_"
    name = re.sub(r"[^0-9A-Za-z]+", "_", name)              

    # Collapse to single "_", trim whitespace, and put into lower-case
    name = re.sub(r"_+", "_", name).strip("_").lower()
      
    return name

def _snake_case_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Apply _to_snake_case helper function to df columns."""

    # Create a copy of df
    out = df.copy()

    # Apply helper function to df columns
    out.columns = [_to_snake_case(c) for c in out.columns]

    return out

def _numeric_columns(df: pd.DataFrame) -> List[str]:
    """Create a list of numeric columns in a DataFrame"""

    return [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]

def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# ------------------------------- #
# Core Cleaner
# ------------------------------- #

@dataclass
class BronzeToSilver:
    """
    Cleans raw bronze data and stores it in silver folder
    """

    @staticmethod
    def _standardise_base(df: pd.DataFrame, *, default_year: Optional[int] = 2021) -> pd.DataFrame:
        """
        Snake-case columns, ensure 'country_name'
        """

        df = _snake_case_columns(df)

        if "country_name" not in df.columns and "country" in df.columns:
            df = df.rename(columns={"country": "country_name"})

        if default_year is not None and "year" not in df.columns:
            df["year"] = default_year

        # Strip whitespace from country_name if present
        if "country_name" in df.columns:
            df["country_name"] = df["country_name"].astype(str).str.strip()

        return df
    
    @staticmethod
    def _basic_filter(df: pd.DataFrame) -> pd.DataFrame:
        """Drop missing values in country_name column"""

        if "country_name" in df.columns:
            df = df.dropna(subset=["country_name"])
        
        return df
    
    @staticmethod
    def _impute_numeric(df: pd.DataFrame) -> pd.DataFrame:
        """Two-pass imputation: (1) per-country (2) global"""
        
        num_cols = _numeric_columns(df)

        if not num_cols:
            return df
        
        if "country_name" in df.columns:
            df[num_cols] = (
                df.groupby("country_name")[num_cols]
                .transform(lambda g: g.fillna(g.mean))
            )

        for col in num_cols:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].mean())
        
        return df
    
    @staticmethod
    def _normalise_regions(df: pd.DataFrame) -> pd.DataFrame:
        if "regional_indicator" in df.columns:
            replacements = {
                "North America and ANZ":"North America",
                "Eastern Asia":"East Asia",
                "Southeastern Asia":"Southeast Asia",
                "Southern Asia":"South Asia"
            }

            df["regional_indicator"] = df["regional_indicator"].replace(replacements)

        return df
    
    @staticmethod
    def _save_silver(df: pd.DataFrame, filename: str, silver_folder: str = 'data/silver') -> Path:
        silver_path = Path(silver_folder)
        _ensure_dir(silver_path)
        out = silver_path / filename
        df.to_csv(out, index=False)

        return(out)

# ------------------------------- #
# Public cleaners (one per file)
# ------------------------------- #

    def clean_y2021(self, df_2021: pd.DataFrame) -> pd.DataFrame:
        """Clean the 2021-only World Happiness dataset"""

        df = self._standardise_base(df_2021, default_year=2021)
        df = self._basic_filter(df)
        df = self._impute_numeric(df)
        df = self._normalise_regions(df)

        print("y2021 data cleaned")

        return df 

# ------------------------------- #
# Saver methods
# ------------------------------- #

    def save_multi(self, df: pd.DataFrame, silver_folder: str = 'data/silver') -> Path:
        return self._save_silver(df, "world_happiness_multi_silver.csv", silver_folder)
    
    def save_y2021(self, df: pd.DataFrame, silver_folder: str = 'data/silver') -> Path:
        return self._save_silver(df, "world_happiness_2021_silver.csv", silver_folder)
    
    def save_geolocation(self, df: pd.DataFrame, silver_folder: str = "data/silver") -> Path:
        return self._save_silver(df, "geolocation_silver.csv", silver_folder)

        
if __name__ == "__main__":
    # Test

    path_multi = Path("data/bronze/world-happiness-report.csv")
    bronze_multi_df = pd.read_csv(path_multi)

    path_y2021 = Path("data/bronze/world-happiness-report-2021.csv")
    bronze_y2021_df = pd.read_csv(path_y2021)

    path_geo = Path("data/bronze/geolocation.csv")
    bronze_geolocation_df = pd.read_csv(path_geo)

    cleaner = BronzeToSilver()

    y2021_clean = cleaner.clean_y2021(bronze_y2021_df)
    print("Before:", list(bronze_y2021_df.columns)[:8])
    print("After: ", list(y2021_clean.columns)[:8])

    cleaner.save_y2021(y2021_clean)
    print("✅ Saved cleaned 2021 CSV to 🥈 folder")

    print("Cleaner")