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
    pass

if __name__ == "__main__":
    print("data access module")