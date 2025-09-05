import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/explore", name="Explore", order=2)

def _df() -> pd.DataFrame:
    return get_gold_df()

def _numeric_cols(df: pd.DataFrame) -> list[str]:
    pass

def _year_options(df: pd.DataFrame):
    pass

def _region_options(df: pd.DataFrame):
    pass

def _labels(s: str) -> str:
    pass