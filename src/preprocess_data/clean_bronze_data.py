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

        
if __name__ == "__main__":
    # Test
    path = Path("data/bronze/world-happiness-report-2021.csv")
    df = pd.read_csv(path)
    cleaned = BronzeToSilver._standardise_base(df, default_year=2021)
    filtered = BronzeToSilver._basic_filter(cleaned)
    imputed = BronzeToSilver._impute_numeric(filtered)
    print("Imputed DataFrame shape:", imputed.shape)
    print(imputed.head())
    print("Cleaner")