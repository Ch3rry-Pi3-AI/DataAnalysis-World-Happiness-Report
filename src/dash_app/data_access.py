from typing import Callable, Optional
import pandas as pd

_DATA_PROVIDER: Optional[Callable[[], pd.DataFrame]] = None

def set_gold_df(df: pd.DataFrame) -> None:
    set_data_provider(lambda: df)

def set_data_provider(func: Callable[[], pd.DataFrame]) -> None:
    """Inject a zero-arg callable returning the DataFrame to use in pages."""
    global _DATA_PROVIDER
    _DATA_PROVIDER = func

def get_gold_df() -> pd.DataFrame:
    if _DATA_PROVIDER is None:
        raise RuntimeError("No data provider set.")

    df = _DATA_PROVIDER().copy()

    if df is None:
        raise RuntimeError("Injected data provider returned None.")
    
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    return df
if __name__ == "__main__":
    print("data access module")