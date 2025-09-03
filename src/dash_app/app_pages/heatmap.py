# src/dash_app/app_pages/heatmap.py
import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/heatmap", name="Correlation 📊", order=5)

# ---------- Helpers ----------
def _df() -> pd.DataFrame:
    return get_gold_df()

def _year_options(df: pd.DataFrame):
    if "year" not in df.columns:
        return []
    years = sorted(pd.Series(df["year"]).dropna().unique().tolist())
    return [{"label": str(int(y)), "value": int(y)} for y in years]

def _numeric(df: pd.DataFrame) -> pd.DataFrame:
    # numeric only, drop columns with all-NaN or zero variance (to avoid NaNs/flat rows in corr)
    num = df.select_dtypes(include="number")
    if num.empty:
        return num
    # drop columns that are all NaN or constant
    mask_constant = num.nunique(dropna=True) <= 1
    return num.loc[:, ~mask_constant]

# ---------- Layout ----------
_BASE = _df()

layout = html.Div(
    [
        html.H2("Features Correlation Heatmap", className="fw-bold text-center my-3"),

        html.Div(
            className="d-flex flex-wrap justify-content-center gap-3 mb-3",
            children=[
                dcc.Dropdown(

                ),
                dcc.Dropdown(

                ),
                dcc.Checklist(

                ),
            ],
        ),

        dcc.Graph(id="hm-fig"),
        html.Small(

        ),
    ]
)

# ---------- Callback ----------
@callback(
    Output("hm-fig", "figure"),
    Input("hm-year-dd", "value"),
    Input("hm-method-dd", "value"),
    Input("hm-abs-toggle", "value"),
)
def _update_heatmap(year_value, method, abs_toggle):
    pass
