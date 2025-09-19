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
dash.register_page(__name__, path="/geo", name="Geography 🌍", order=3)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _df() -> pd.DataFrame:
    """
    Return the gold dataset used across pages.

    Isolated so that:
    - Unit tests can inject a small DataFrame,
    - Other pages can reuse the same loader.

    Returns
    -------
    pandas.DataFrame
        Gold dataset.
    """

    return get_gold_df()


def _labels(s: str) -> str:
    """
    Humanise snake_case labels for display.

    Parameters
    ----------
    s : str
        Raw column name.

    Returns
    -------
    str
        Title-cased label with underscores replaced by spaces.
    """

    return s.replace("_", " ").title()


def _numeric_cols(df: pd.DataFrame) -> list[str]:
    """
    Return numeric column names.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset to inspect.

    Returns
    -------
    list of str
        Numeric columns.
    """

    return df.select_dtypes(include="number").columns.tolist()


def _year_options(df: pd.DataFrame) -> list[dict]:
    """
    Build (label, value) options for the Year drop-down.

    Returns empty list if 'year' is missing.
    """

    if "year" not in df.columns:
        return []
    years = sorted(pd.Series(df["year"]).dropna().unique().tolist())
    return [{"label": str(int(y)), "value": int(y)} for y in years]


def _region_options(df: pd.DataFrame) -> list[dict]:
    """
    Build (label, value) options for Region(s).

    Returns empty list if region column is missing.
    """

    col = "regional_indicator"
    if col not in df.columns:
        return []
    regs = sorted(pd.Series(df[col]).dropna().unique().tolist())
    return [{"label": r, "value": r} for r in regs]


def _metric_options(df: pd.DataFrame) -> list[dict]:
    """
    Build (label, value) options for the metric selector (numeric columns only).
    """

    return [{"label": _labels(c), "value": c} for c in _numeric_cols(df)]


def _apply_filters(df: pd.DataFrame, year_value, regions) -> pd.DataFrame:
    """
    Apply Year and Region(s) filters.

    Parameters
    ----------
    df : pandas.DataFrame
        Unfiltered dataset.
    year_value : int or None
        Exact year to keep (optional).
    regions : list[str] or str or None
        Region(s) to keep (optional).

    Returns
    -------
    pandas.DataFrame
        Filtered dataset.
    """

    # Year filter (exact)
    if year_value is not None and "year" in df.columns:
        df = df[df["year"] == int(year_value)]

    # Region(s) filter (membership)
    if regions and "regional_indicator" in df.columns:
        if not isinstance(regions, list):
            regions = [regions]
        df = df[df["regional_indicator"].isin(regions)]

    return df


# ----------------------------------------------------------------------
# Data / Defaults
# ----------------------------------------------------------------------

_BASE = _df()
_NUMS = _numeric_cols(_BASE)

# Defaults requested: Year=2021, Metric="ladder_score"
_DEFAULT_YEAR = (
    2021
    if "year" in _BASE.columns and (pd.Series(_BASE["year"]).dropna() == 2021).any()
    else (int(pd.Series(_BASE["year"]).dropna().max()) if "year" in _BASE.columns else None)
)
_DEFAULT_METRIC = "ladder_score" if "ladder_score" in _NUMS else (_NUMS[0] if _NUMS else None)


# ----------------------------------------------------------------------
# Layout (modular: controls_col, charts_col, layout)
# ----------------------------------------------------------------------

# Left column: filters
controls_col = html.Div(
    className="col-12 col-lg-3",
    children=[
        html.H5("Filters", className="fw-bold mb-3"),

        # Year (default to 2021 if available)
        html.Label("Year", className="form-label mb-1"),
        dcc.Dropdown(
            id="geo-year-dd",
            options=_year_options(_BASE),
            value=_DEFAULT_YEAR,
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        # Region(s) (optional, multi)
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

        # Metric (numeric only)
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

# Right column: charts
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

        # Row count (footer)
        html.Div(id="geo-row-count", className="text-end text-muted mt-2"),
    ],
)

# Page container (top-level)
layout = html.Div(
    className="container-fluid py-4 rounded-2",
    style={"backgroundColor": "#649ec784"},
    children=[
    
        # Title block
        html.Div(
            className="text-center mb-4",
            children=[
                html.H2("Global View", className="text-light fw-bold"),
                html.P(
                    "Map, regional radial, and Top-10 countries for the selected metric.",
                    className="text-light fw-bold",
                ),
            ],
        ),

        # Card containing controls + charts
        html.Div(
            className="card shadow-sm rounded-2",
            children=[
                html.Div(
                    className="card-body",
                    children=[html.Div(className="row g-3", children=[controls_col, charts_col])],
                )
            ],
        ),
    ],
)


# ----------------------------------------------------------------------
# Callbacks
# ----------------------------------------------------------------------

@callback(
    Output("geo-choropleth", "figure"),
    Output("geo-radial", "figure"),
    Output("geo-top10", "figure"),
    Output("geo-row-count", "children"),
    Input("geo-year-dd", "value"),
    Input("geo-region-dd", "value"),
    Input("geo-metric-dd", "value"),
)

def _update_geo(year_value, region_values, metric):
    """
    Update the choropleth, regional radial (donut), and Top-10 bar chart.

    Notes
    -----
    - All charts respect the current filters (Year, Region).
    - The donut encodes regional means of the selected metric.
    - Top-10 shows countries with the highest values for the metric.
    """

    df = _apply_filters(_df(), year_value, region_values)
    count_txt = f"{len(df):,} matching rows"

    # Choropleth 
    if metric and "country_name" in df.columns and metric in df.columns:
        map_df = df.dropna(subset=[metric, "country_name"])
    
        if map_df.empty:
            choropleth = px.choropleth(title="No data for selection")
    
        else:
            choropleth = px.choropleth(
                map_df,
                locations="country_name",
                locationmode="country names",
                color=metric,
                hover_name="country_name",
                hover_data=["regional_indicator", metric] if "regional_indicator" in map_df.columns else [metric],
                color_continuous_scale="Viridis",
                title=f"{_labels(metric)} - Choropleth" + (f" · {int(year_value)}" if year_value else ""),
            )
            choropleth.update_layout(
                margin={"t": 70, "l": 10, "r": 10, "b": 10},
                coloraxis_colorbar=dict(title=_labels(metric)),
            )
    else:
        choropleth = px.choropleth(title="Select a metric")

    # Radial (donut) by region
    reg_col = "regional_indicator"
    
    if metric and reg_col in df.columns and metric in df.columns:
        rad_src = df[[reg_col, metric]].dropna(subset=[metric])
    
        if rad_src.empty:
            radial = px.pie(values=[1], names=["No data"], hole=0.6, title="Regional Radial")
    
        else:
            agg = rad_src.groupby(reg_col, as_index=False).agg(value=(metric, "mean"))
            radial = px.pie(
                agg,
                names=reg_col,
                values="value",
                hole=0.55,
                title=f"Regional Radial (mean {_labels(metric)})" + (f" · {int(year_value)}" if year_value else ""),
            )
            radial.update_traces(textposition="outside", texttemplate="%{label}<br>%{value:.2f}")
            radial.update_layout(margin={"t": 70, "l": 10, "r": 10, "b": 10}, showlegend=False)
    
    else:
        radial = px.pie(values=[1], names=["Select a metric"], hole=0.6, title="Regional Radial")

    # Top-10 horizontal bar 
    if metric and "country_name" in df.columns and metric in df.columns:
        top_src = df[["country_name", reg_col, metric]] if reg_col in df.columns else df[["country_name", metric]]
        top_src = top_src.dropna(subset=[metric]).sort_values(metric, ascending=False).head(10)

        if top_src.empty:
            top10 = px.bar(title="Top 10 Countries - No data")
        
        else:
            top10 = px.bar(
                top_src.sort_values(metric, ascending=True),  
                x=metric,
                y="country_name",
                color=reg_col if reg_col in top_src.columns else None,
                orientation="h",
                hover_name="country_name",
                title=f"Top 10 Countries by {_labels(metric)}" + (f" · {int(year_value)}" if year_value else ""),
            )
            top10.update_layout(margin={"t": 70, "l": 10, "r": 10, "b": 10}, legend=dict(title="Region"))
    
    else:
        top10 = px.bar(title="Select a metric")

    return choropleth, radial, top10, count_txt
