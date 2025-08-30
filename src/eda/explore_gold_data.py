from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class EDAExplorer:

    def __init__(
            self,
            df: pd.DataFrame,
            lat_col: str = "latitude",
            lon_col: str = "longitude"
    ) -> None:
        
        self.df = df.copy()
        self.lat_col = lat_col
        self.lat_col = lon_col

    def preview(self, n: int = 5) -> None:
        """Show head and tail"""
        print(f"\nFirst {n} rows\n")
        print(self.df.head(n))
        print(f"\nLast {n} rows\n")
        print(self.df.tail(n))
        
    def info(self) -> None:
        """Print shape, dtypes, memory usage, and basic null summary"""
        print("\nShape:\n")
        print(self.df.shape)
        print("\nDtypes:\n")
        print(self.df.dtypes.sort_index())

        memory_mb = self.df.memory_usage(deep=True).sum() / (1024 ** 2)
        print(f"Memory usage: {memory_mb} MB\n")

        na = self.df.isna().sum().sort_values(ascending=False)
        print("Missing values\n")
        print(na[na > 0])

    def describe_numeric(
            self, 
            exclude: Optional[Sequence[str]] = None
    ) -> pd.DataFrame:
        """Return numeric summary, excluding specific columns"""

        exclude = set(exclude or [])

        num = self.df.select_dtypes(include="number")
        num = num.drop(columns=[c for c in exclude if c in num.columns], errors="ignore")

        if num.empty:
            print("No numeric columns to describe after exclusion.")

        desc = num.describe().T
        print(desc)
        return desc
    
    def describe_categorical(self, top_n: int = 10) -> pd.DataFrame:
        "Show top frequencies for object/category columns"

        cats = self.df.select_dtypes(include=["object", "category"]).columns
        rows = []
        for col in cats:
            vc = self.df[col].value_counts(dropna=False).head(top_n)
            for index, count in vc.items():
                rows.append({"column": col, "value": index, "count": int(count)})
        out = pd.DataFrame(rows)
        print(out)
        return out


if __name__ == "__main__":

    from load_gold_data import load_gold_happiness_data

    gold_df = load_gold_happiness_data()

    exp = EDAExplorer(df = gold_df)
    exp.preview()
    exp.info()
    exp.describe_numeric(exclude=["year", "latitude", "longitude"])
    exp.describe_categorical()