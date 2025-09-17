# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------

# Dash framework + primitives
import dash
from dash import html, dcc, Input, Output, callback

# Data handling
import pandas as pd
import numpy as np

# Plotting
import plotly.express as px

# Project data accessor
from src.dash_app.data_access import get_gold_df


# ----------------------------------------------------------------------
# Page registration
# ----------------------------------------------------------------------

# Register the page so Dash discovers it at startup
dash.register_page(__name__, path="/relationship", name="Relationship", order=2)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------


def _numeric_cols(df: pd.DataFrame) -> list[str]:
    num = df.select_dtypes(include="number").columns.tolist()
    headline = [
        "ladder_score",
        "logged_gdp_per_capita",
        "healthy_life_expectancy",
        "social_support",
        "freedom_to_make_life_choices",
        "generosity",
        "perceptions_of_corruption",
    ]
    return [c for c in headline if c in num] + [c for c in num if c not in headline]

def _year_options(df: pd.DataFrame):
    years = sorted(pd.Series(df["year"]).dropna().unique().tolist()) if "year" in df.columns else []
    return [{"label": str(int(y)), "value": int(y)} for y in years]

def _region_options(df: pd.DataFrame):
    if "regional_indicator" not in df.columns:
        return []
    regs = sorted(pd.Series(df["regional_indicator"]).dropna().unique().tolist())
    return [{"label": r, "value": r} for r in regs]

def _labels(s: str) -> str:
    return s.replace("_", " ").title()

# ----------------------------------------------------------------------
# Data / Defaults
# ----------------------------------------------------------------------

_BASE = _df()
_NUMS = _numeric_cols(_BASE)
_DEFAULT_X = _NUMS[0] if _NUMS else None
_DEFAULT_Y = _NUMS[1] if len(_NUMS) > 1 else _DEFAULT_X

# ----------------------------------------------------------------------
# Layout (modular: controls_col, plots_col, layout)
# ----------------------------------------------------------------------

controls_col = html.Div(
    className="col-12 col-lg-3",
    children=[
        html.H5("Controls", className="fw-bold mb-3"),
        html.Label("Year", className="form-label mb-1"),
        dcc.Dropdown(
            id="ex-year-dd",
            options=_year_options(_BASE),
            placeholder="(optional)",
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        html.Label("Region(s)", className="form-label mb-1"),
        dcc.Dropdown(
            id="ex-region-dd",
            options=_region_options(_BASE),
            placeholder="(optional)",
            multi=True,
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        html.Label("X axis", className="form-label mb-1"),
        dcc.Dropdown(
            id="ex-x-dd",
            options=[{"label": _labels(c), "value": c} for c in _NUMS],
            value=_DEFAULT_X,
            clearable=False,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        html.Label("Y axis", className="form-label mb-1"),
        dcc.Dropdown(
            id="ex-y-dd",
            options=[{"label": _labels(c), "value": c} for c in _NUMS],
            value=_DEFAULT_Y,
            clearable=False,
            style={"fontSize": "12px"},
        ),
        html.Hr(),
        html.Small("Tip: choose X & Y, then refine by year and region.", className="text-muted"),
    ],
)

plots_col = html.Div(
    className="col-12 col-lg-9",
    children=[
        dcc.Graph(id="ex-rel-fig", style={"height": "400px"}, className="mb-3"),
        dcc.Graph(id="ex-corr-fig", style={"height": "400px"}),  # correlation plot (new)
    ],
)

layout = html.Div(
    className="container-fluid py-4 rounded-2",
    style={"backgroundColor": "#649ec784"},
    children=[
        html.Div(
            className="text-center mb-4",
            children=[
                html.H2("Explore", className="text-light fw-bold"),
                html.P(
                    "Investigate relationships and correlations in the World Happiness dataset.",
                    className="text-light fw-bold",
                ),
            ],
        ),
        html.Div(
            className="card shadow-sm rounded-2",
            children=[
                html.Div(
                    className="card-body",
                    children=[html.Div(className="row g-3", children=[controls_col, plots_col])],
                )
            ],
        ),
    ],
)

# ----------------------------------------------------------------------
# Callbacks
# ----------------------------------------------------------------------

def _apply_filters(df: pd.DataFrame, year_value, regions):
    if year_value is not None and "year" in df.columns:
        df = df[df["year"] == int(year_value)]
    if regions and "regional_indicator" in df.columns:
        if not isinstance(regions, list):
            regions = [regions]
        df = df[df["regional_indicator"].isin(regions)]
    return df

@callback(
    Output("ex-rel-fig", "figure"),
    Input("ex-x-dd", "value"),
    Input("ex-y-dd", "value"),
    Input("ex-year-dd", "value"),
    Input("ex-region-dd", "value"),
)
def _update_relationship(x_col, y_col, year_value, region_values):
    df = _apply_filters(_df(), year_value, region_values)
    if not x_col or not y_col or x_col not in df.columns or y_col not in df.columns:
        return px.scatter(title="Select X and Y to view their relationship")

    color = "regional_indicator" if "regional_indicator" in df.columns else None
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color,
        hover_data=["country_name", "year"] if {"country_name", "year"}.issubset(df.columns) else None,
        title=f"{_labels(x_col)} vs {_labels(y_col)}"
              + (f" — Year {year_value}" if year_value else ""),
        opacity=0.9,
    )
    fig.update_traces(marker={"line": {"width": 0.5}})
    fig.update_layout(
        margin={"t": 60, "l": 10, "r": 10, "b": 10},
        legend=dict(title="Region", bgcolor="rgba(255,255,255,0.6)"),
    )
    return fig

@callback(
    Output("ex-corr-fig", "figure"),
    Input("ex-year-dd", "value"),
    Input("ex-region-dd", "value"),
)
def _update_correlation(year_value, region_values):
    df = _apply_filters(_df(), year_value, region_values)

    cols = [c for c in _numeric_cols(df) if c in df.columns]
    if not cols:
        return px.imshow([[np.nan]], labels=dict(x="Metric", y="Metric", color="ρ"),
                         title="No numeric columns found")

    # Compute correlation on filtered data; drop all-NA columns/rows
    sub = df[cols].select_dtypes(include="number").dropna(how="all", axis=0)
    # If too few rows, show friendly message
    if len(sub) < 2:
        return px.imshow([[np.nan]], labels=dict(x="Metric", y="Metric", color="ρ"),
                         title="Not enough data after filters to compute correlation")

    corr = sub.corr(numeric_only=True)
    # If correlation is empty (e.g., single column), handle gracefully
    if corr.empty or corr.shape[0] < 2:
        title = "Correlation (need ≥ 2 numeric columns)"
        return px.imshow([[np.nan]], labels=dict(x="Metric", y="Metric", color="ρ"), title=title)

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1, zmax=1,
        title="Correlation of Numeric Metrics"
              + (f" — Year {year_value}" if year_value else ""),
        labels=dict(color="ρ"),
    )
    fig.update_layout(
        margin={"t": 60, "l": 10, "r": 10, "b": 10},
        coloraxis_colorbar=dict(title="ρ"),
    )
    return fig
