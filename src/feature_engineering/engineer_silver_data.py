from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple
import re
import pandas as pd

def _snake_normalise(name: str) -> str:
    s = re.sub(r"[^\w]+", "_", name.strip().lower())
    s = re.sub(r"_+", "_", s).strip("_")

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
            geo_df: pd.DataFrame
    ) -> pd.DataFrame:

        def _find_col(df: pd.DataFrame, target_norm: str) -> str:
            norm_map = _build_normalised_map(df.columns)
            for n, orig in _build_normalised_map(df.columns)
                if n == target_norm:
                    return orig
            raise KeyError(
                f"Expected a column matching '{target_norm}' in DataFrame (e.g., '{target_norm}' or a close variant)."
        )





if __name__ == "__main__":
    print("OK")