import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/trends", name="Trends ⏱️", order=4)

# Helpers

def _df() -> pd.DataFrame:
    return get_gold_df()

def _labels(s: str) -> str:
    return s.replace("_", " ").title()

def _numeric_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()

def _default_ts_metrics(df: pd.DataFrame) -> list[str]:
    # Get defaults
    defaults = ["ladder_score", "logged_gdp_per_capita"]
    available = [m for m in defaults if m in df.columns]
    if available:
        return available
    nums = _numeric_cols(df)
    return nums[:2] if len(nums) >=2 else nums