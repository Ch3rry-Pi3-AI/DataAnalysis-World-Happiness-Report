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
import plotly.graph_objects as go

# Project data accessor
from src.dash_app.data_access import get_gold_df

# ----------------------------------------------------------------------
# Page registration
# ----------------------------------------------------------------------

# Register the page so Dash discovers it at startup
dash.register_page(__name__, path="/trends", name="Trends ⏱️", order=4)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _df() -> pd.DataFrame:
    """
    Return the gold dataset used across pages.

    Isolated so that:
    - unit tests can inject a small DataFrame,
    - other pages can reuse the same loader.

    Returns
    -------
    pandas.DataFrame
        Gold dataset.
    """

    return get_gold_df()


def _labels(s: str) -> str:
    """
    Humanise snake_case labels for display.
    """

    return s.replace("_", " ").title()


def _numeric_cols(df: pd.DataFrame) -> list[str]:
    """
    Return numeric column names.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    list of str
        Numeric columns.
    """

    return df.select_dtypes(include="number").columns.tolist()


def _default_ts_metrics(df: pd.DataFrame) -> list[str]:
    """
    Choose sensible default time-series metrics.

    Prefers ['ladder_score', 'logged_gdp_per_capita'] when available,
    otherwise falls back to the first two numeric columns.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    list of str
        Default metric names (length 1–2).
    """

    defaults = ["ladder_score", "logged_gdp_per_capita"]
    available = [m for m in defaults if m in df.columns]
    if available:
        return available
    nums = _numeric_cols(df)
    return nums[:2] if len(nums) >= 2 else nums


def _region_options(df: pd.DataFrame) -> list[dict]:
    """
    Build (label, value) options for Region(s).
    """
    col = "regional_indicator"

    if col not in df.columns:
        return []
    regs = sorted(pd.Series(df[col]).dropna().unique().tolist())
    return [{"label": r, "value": r} for r in regs]


def _metric_options(df: pd.DataFrame) -> list[dict]:
    """
    Build (label, value) options for metric selector (numeric only).
    """

    return [{"label": _labels(c), "value": c} for c in _numeric_cols(df)]


def _apply_filters(df: pd.DataFrame, year_range, regions, country_text) -> pd.DataFrame:
    """
    Apply Year range, Region(s), and Country text filters.

    Parameters
    ----------
    df : pandas.DataFrame
        Unfiltered dataset.
    year_range : (int, int) or None
        Inclusive [start, end] year range (optional).
    regions : list[str] or str or None
        Region(s) to keep (optional).
    country_text : str or None
        Case-insensitive substring to match against 'country_name'.

    Returns
    -------
    pandas.DataFrame
        Filtered dataset.
    """

    # Year range (inclusive)
    if year_range and "year" in df.columns:
        y0, y1 = map(int, year_range)
        df = df[(df["year"] >= y0) & (df["year"] <= y1)]

    # Region(s) membership
    if regions and "regional_indicator" in df.columns:
        if not isinstance(regions, list):
            regions = [regions]
        df = df[df["regional_indicator"].isin(regions)]

    # Country text search (contains; case-insensitive)
    if country_text and "country_name" in df.columns:
        t = str(country_text).strip().lower()
        if t:
            df = df[df["country_name"].str.lower().str.contains(t, na=False)]

    return df  


def _make_snapshot_table(df: pd.DataFrame, metrics: list[str], latest_year: int) -> go.Figure:
    """
    Latest-year snapshot table (countries × selected metrics).

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered dataset.
    metrics : list[str]
        Metrics to include as columns.
    latest_year : int
        Year to snapshot.

    Returns
    -------
    plotly.graph_objects.Figure
        Table of up to 200 rows.
    """

    cols = ["country_name", "regional_indicator", "year"] + [m for m in (metrics or []) if m in df.columns]
    cols = [c for c in cols if c in df.columns]
    snap = df[df["year"] == latest_year][cols].copy() if "year" in df.columns else df[cols].copy()

    # Helpful sort if ladder_score present
    if {"country_name", "ladder_score"}.issubset(snap.columns):
        snap = snap.sort_values("ladder_score", ascending=False)

    fig = go.Figure(data=[
        go.Table(
            header=dict(values=[_labels(c) for c in snap.columns], align="left"),
            cells=dict(values=[snap[c].head(200) for c in snap.columns], align="left"),
        )
    ])
    fig.update_layout(margin={"t": 0, "l": 0, "r": 0, "b": 0})
    return fig


def _make_top10_yoy(df: pd.DataFrame, metric: str, latest_year: int) -> go.Figure:
    """
    Top-10 year-over-year change for a primary metric.

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered dataset.
    metric : str
        Primary metric to compute Δ on.
    latest_year : int
        Current year for YoY (prev = latest_year-1).

    Returns
    -------
    plotly.graph_objects.Figure
        Horizontal bar chart of the largest positive YoY changes.
    """

    if not metric or "year" not in df.columns or "country_name" not in df.columns:
        return px.bar(title="Top-10 YoY Change (select a metric)")

    prev_year = latest_year - 1
    now = df[df["year"] == latest_year][["country_name", "regional_indicator", metric]].rename(columns={metric: "now"})
    prev = df[df["year"] == prev_year][["country_name", metric]].rename(columns={metric: "prev"})
    merged = pd.merge(now, prev, on="country_name", how="left")
    merged["yoy"] = merged["now"] - merged["prev"]

    # Keep rows with a valid previous year
    merged = merged.dropna(subset=["yoy"])  
    if merged.empty:
        return px.bar(title=f"Top-10 YoY Change (no {prev_year} data)")

    # Sort so the biggest Δ are at the top of the horizontal bar
    top10 = merged.sort_values("yoy", ascending=False).head(10).sort_values("yoy", ascending=True)

    fig = px.bar(
        top10,
        x="yoy",
        y="country_name",
        orientation="h",
        color="regional_indicator" if "regional_indicator" in top10.columns else None,
        title=f"Top-10 YoY Change in {_labels(metric)} · {prev_year}→{latest_year}",
        hover_data=["now", "prev"],
    )
    fig.update_layout(margin={"t": 70, "l": 10, "r": 10, "b": 10}, legend=dict(title="Region"))
    return fig  # (bug fix: return the figure)


def _make_time_series(df: pd.DataFrame, metrics: list[str]) -> go.Figure:
    """
    Multi-metric time series (mean by year).

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered dataset.
    metrics : list[str]
        Metrics to plot (multiple lines).

    Returns
    -------
    plotly.graph_objects.Figure
        Line chart of mean values per year for each metric.
    """

    need = [m for m in (metrics or []) if m in df.columns]
    if "year" not in df.columns or not need:
        return px.line(title="Select at least one metric")

    agg = (
        df[["year"] + need]
        .groupby("year", as_index=False)
        .mean(numeric_only=True)
        .sort_values("year")
    )

    # Long form for multiple lines
    long = agg.melt(id_vars="year", value_vars=need, var_name="metric", value_name="value")
    fig = px.line(
        long,
        x="year",
        y="value",
        color="metric",
        markers=True,
        title="Trends Over Time (mean across current filters)",
        labels={"value": "Value", "year": "Year", "metric": "Metric"},
    )
    fig.update_layout(margin={"t": 70, "l": 10, "r": 10, "b": 10})
    return fig


# ----------------------------------------------------------------------
# Data / Defaults
# ----------------------------------------------------------------------

_BASE = _df().copy()
if "year" in _BASE.columns:
    _BASE["year"] = _BASE["year"].astype(int)

_YEARS = sorted(pd.Series(_BASE["year"]).dropna().unique().tolist()) if "year" in _BASE.columns else []
_YEAR_MIN = int(_YEARS[0]) if _YEARS else 0
_YEAR_MAX = int(_YEARS[-1]) if _YEARS else 0

_DEFAULT_METRICS = _default_ts_metrics(_BASE)             
_PRIMARY_METRIC = _DEFAULT_METRICS[0] if _DEFAULT_METRICS else None


# ----------------------------------------------------------------------
# Layout (modular: controls_col, charts_col, layout)
# ----------------------------------------------------------------------

# Left column: filters & metric selection
controls_col = html.Div(
    className="col-12 col-lg-3",
    children=[
        html.H5("Filters", className="fw-bold mb-3"),  

        # Year range
        html.Label("Year range", className="form-label mb-1"),
        dcc.RangeSlider(
            id="ts-year-range",
            min=_YEAR_MIN,
            max=_YEAR_MAX,
            value=[_YEAR_MIN, _YEAR_MAX],  
            step=1,
            marks=(
                {int(y): str(int(y)) for y in (
                    _YEARS[:1] + _YEARS[1:: max(1, len(_YEARS)//6)] + _YEARS[-1:]
                )} if _YEARS else None
            ),
            tooltip={"always_visible": False, "placement": "bottom"},
        ),
        html.Div(style={"height": "8px"}),

        # Region(s)
        html.Label("Region(s)", className="form-label mb-1"),  
        dcc.Dropdown(
            id="ts-region-dd",
            options=_region_options(_BASE),
            placeholder="(optional)",
            multi=True,
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        # Country contains
        html.Label("Country contains", className="form-label mb-1"),
        dcc.Input(
            id="ts-country-text",
            type="text",
            placeholder="e.g., 'Uni' for 'United...'",  
            style={"width": "100%", "fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        # Metrics (multi-select)
        html.Label("Metrics (time series)", className="form-label mb-1"),
        dcc.Dropdown(
            id="ts-metrics-dd",                      
            options=_metric_options(_BASE),
            value=_DEFAULT_METRICS,
            multi=True,
            clearable=False,
            style={"fontSize": "12px"},
        ),

        html.Hr(),
        html.Small(
            "Top row uses the latest year in the selected range. Time series shows means per year.",
            className="text-muted",
        ),
    ],
)

# Right column: snapshot + YoY + time series
charts_col = html.Div(
    className="col-12 col-lg-9",
    children=[
        
        # Top row: snapshot table (left) + top-10 YoY (right)
        html.Div(
            className="row g-3",
            children=[
                html.Div(
                    className="col-12 col-xl-6",
                    children=[
                        html.H6("Latest Snapshot (by Country)", className="fw-bold mb-2"),
                        dcc.Graph(id="ts-snapshot-table", style={"height": "360px"}),
                    ],
                ),
                html.Div(
                    className="col-12 col-xl-6",
                    children=[
                        html.H6("Top-10 YoY Change (Primary Metric)", className="fw-bold mb-2"),
                        dcc.Graph(id="ts-top10-yoy", style={"height": "360px"}),  
                    ],
                ),
            ],
        ),

        # Bottom row: full-width time series
        dcc.Graph(id="ts-lines", style={"height": "430px"}, className="mt-3"),

        # Row count (footer)
        html.Div(id="ts-row-count", className="text-end text-muted mt-2"),
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
                html.H2("Trends", className="text-light fw-bold"),
                html.P("Explore how key metrics evolve over time.", className="text-light fw-bold"),
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
    Output("ts-snapshot-table", "figure"),
    Output("ts-top10-yoy", "figure"),
    Output("ts-lines", "figure"),
    Output("ts-row-count", "children"),
    Input("ts-year-range", "value"),
    Input("ts-region-dd", "value"),
    Input("ts-country-text", "value"),
    Input("ts-metrics-dd", "value"),
)
def _update_trends(year_range, region_values, country_text, metrics):
    """
    Update snapshot table, Top-10 YoY bar, and bottom time series.

    Notes
    -----
    - Snapshot/YoY use the latest year within the selected range.
    - Time series shows mean per year across current filters for each metric.
    """

    df = _apply_filters(_df(), year_range, region_values, country_text)  
    count_txt = f"{len(df):,} matching rows"

    # Determine latest year within selected range
    latest_year = int(df["year"].max()) if "year" in df.columns and not df.empty else None

    snapshot_fig = _make_snapshot_table(df, metrics, latest_year) if latest_year else go.Figure()
    primary = (metrics or _DEFAULT_METRICS or [])[:1]
    primary_metric = primary[0] if primary else None
    yoy_fig = _make_top10_yoy(df, primary_metric, latest_year) if latest_year else px.bar(title="Top-10 YoY Change")

    ts_fig = _make_time_series(df, metrics)

    return snapshot_fig, yoy_fig, ts_fig, count_txt
