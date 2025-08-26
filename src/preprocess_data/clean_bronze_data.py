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
    """Convert 'Country Name' or 'regionalIndicator' → 'country_name'."""
    name = name.strip()
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)     # split CamelCase
    name = re.sub(r"[^0-9A-Za-z]+", "_", name)              # non-alnum → _
    name = re.sub(r"_+", "_", name).strip("_").lower()      # collapse, trim, lower
    return name

def _snake_case_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [_to_snake_case(c) for c in out.columns]
    return out           # ← THIS return was missing


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

        if "country_name" in df.columns:
            df["country_name"] = df["country_name"].astype(str).str.strip()

        return df

        
if __name__ == "__main__":
    # Test
    path = Path("data/bronze/world-happiness-report-2021.csv")
    df = pd.read_csv(path)
    cleaned = BronzeToSilver._standardise_base(df, default_year=2021)
    print("Cleaned DataFrame shape:", cleaned.shape)
    print(cleaned.columns)
    print(cleaned.head())
    print("Cleaner")