import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/geo", name="Geography 🌍", order=3)

# ---------------- Helpers 
def _df() -> pd.DataFrame:
    return get_gold_df()

def _labels(s: str) -> str:
    return s.replace("_", " ").title()

def _numeric_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()

def _year_options(df: pd.DataFrame):
    if "year" not in df.columns:
        return []
    years = sorted(pd.Series(df["year"]).dropna().unique().tolist())
    return [{"label": str(int(y)), "value": int(y)} for y in years]

def _region_options(df: pd.DataFrame):
    if "regional_indicator" not in df.columns:
        return []
    regs = sorted(pd.Series(df["regional_indicator"]).dropna().unique().tolist())
    return [{"label": r, "value": r} for r in regs]

def _metric_options(df: pd.DataFrame):
    return [{"label": _labels(c), "value": c} for c in _numeric_cols(df)]

def _apply_filters(df: pd.DataFrame, year_value, regions):
    if year_value is not None and "year" in df.columns:
        df = df[df["year"] == int(year_value)]
    if regions and "regional_indicator" in df.columns:
        if not isinstance(regions, list):
            regions = [regions]
        df = df[df["regional_indicator"].isin(regions)]
    return df

# ---------- Data / Defaults
_BASE = _df()
_NUMS = _numeric_cols(_BASE)

# Defaults requested: Year=2021, Metric="ladder_score"
_DEFAULT_YEAR = 2021 if "year" in _BASE.columns and (pd.Series(_BASE["year"]).dropna() == 2021).any() else (int(pd.Series(_BASE["year"]).dropna().max()) if "year" in _BASE.columns else None)
_DEFAULT_METRIC = "ladder_score" if "ladder_score" in _NUMS else (_NUMS[0] if _NUMS else None)

controls_col = html.Div(
    className="col-12 col-lg-3",
    children=[
        html.H5("Filters", className="fw-bold mb-3"),

        html.Label("Year", className="form-label mb-1"),
        dcc.Dropdown(
            id="geo-year-dd",
            options=_year_options(_BASE),
            value=_DEFAULT_YEAR,
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        html.Label("Region(s)", className="form-label mb-1"),
        dcc.Dropdown(
            id="geo-region-dd",
            options=_region_options(_BASE),
            placeholder="(optional)",
            multi=True,
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        html.Label("Metric", className="form-label mb-1"),
        dcc.Dropdown(
            id="geo-metric-dd",
            options=_metric_options(_BASE),
            value=_DEFAULT_METRIC,
            clearable=False,
            style={"fontSize": "12px"},
        ),
        html.Hr(),
        html.Small("Tip: pick a year & metric, then refine by region.", className="text-muted"),
    ],
)

charts_col = html.Div(
    className="col-12 col-lg-9",
    children=[
        # Top row: full-width choropleth
        dcc.Graph(id="geo-choropleth", style={"height": "460px"}, className="mb-3"),
        # Second row: radial (by region) + top 10 bar chart
        html.Div(
            className="row g-3",
            children=[
                html.Div(className="col-12 col-xl-6", children=[
                    html.H6("Regional Radial", className="fw-bold mb-2"),
                    dcc.Graph(id="geo-radial", style={"height": "360px"}),
                ]),
                html.Div(className="col-12 col-xl-6", children=[
                    html.H6("Top 10 Countries", className="fw-bold mb-2"),
                    dcc.Graph(id="geo-top10", style={"height": "360px"}),
                ]),
            ],
        ),
        html.Div(id="geo-row-count", className="text-end text-muted mt-2"),
    ],
)

layout = html.Div(
    className="container-fluid py-4 rounded-2",
    style={"backgroundColor": "#649ec784"},
    children=[
        html.Div(
            className="text-center mb-4",
            children=[
                html.H2("Global View", className="text-light fw-bold"),
                html.P("Map, regional radial, and Top-10 countries for the seclected metric", className="text-light fw-bold"),
            ],
        ),
        html.Div(
            className="card shadow-sm rounded-2",
            children=[
                html.Div(
                    className="card-body",
                    children=[
                        html.Div(className="row g-3", children=[controls_col, charts_col]),
                    ]
                )
            ],
        ),           
    ],
)

# -------------- callbacks

@callback(
    Output(),
    Output(),
    Output(),
    Output(),
    Output(),
    Output(),
    Output(),
    Output(),
)

def _update_geo():
    pass