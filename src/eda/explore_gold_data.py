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

if __name__ == "__main__":

    from load_gold_data import load_gold_happiness_data

    gold_df = load_gold_happiness_data()

    exp = EDAExplorer(df = gold_df)
    exp.preview()
    exp.info()