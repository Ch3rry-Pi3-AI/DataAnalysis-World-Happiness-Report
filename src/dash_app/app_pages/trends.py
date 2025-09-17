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

def _region_options(df: pd.DataFrame):
    if "regional_indicator" not in df.columns:
        return []
    regs = sorted(pd.Series(df["regional_indicator"]).dropna().unique().tolist())
    return [{"label": r, "value": r} for r in regs]

def _metric_options(df: pd.DataFrame):
    return[{"label": _labels(c), "value": c} for c in _numeric_cols(df)]

def _apply_filters(df: pd.DataFrame, year_range, regions, country_text):
    # Year range
    if year_range and "year" in df.columns:
        y0, y1 = map(int, year_range)
        df = df[(df["year"] >= y0) & (df["year"] <= y1)]

    # Regions
    if regions and "regional_indicator" in df.columns:
        if not isinstance(regions, list):
            regions = [regions]
        df = df[df["regional_indicator"].isin(regions)]

    # Country contains
    if country_text and "country_name" in df.columns:
        t = str(country_text).strip().lower()
        if t:
            df = df[df["country_name"].str.lower().str.contains(t, na=False)]
        return df
    
def _make_snapshot_table(df: pd.DataFrame, metrics: list[str], latest_year: int) -> go.Figure:
    cols = ["country_name", "regional_indicator", "year"] + [m for m in (metrics or []) if m in df.columns]
    cols = [c for c in cols if c in df.columns]
    snap = df[df["year"] == latest_year][cols].copy() if "year" in df.columns else df[cols].copy()

    if "country_name" in snap.columns and "ladder_score" in snap.columns:
        snap = snap.sort_values(by = "ladder_score", ascending=False)
    
    fig = go.Figure(data=[
        go.Table(
            header=dict(values=[_labels(c) for c in snap.columns], align="left"),
            cells=dict(values=[snap[c].head(200) for c in snap.columns], align="left")
        )
    ])

    fig.update_layout(margin={"t": 0, "l": 0, "r": 0, "b": 0})
    return fig

def _make_top10_yoy(df: pd.DataFrame, metric: str, latest_year: int) -> go.Figure:
    if not metric or "year" not in df.columns or "country_name" not in df.columns:
        return px.bar(title="Top-10 YoY Change (select a metric)")
    
    prev_year = latest_year - 1
    now =df[df["year"] == latest_year][["country_name", "regional_indicator", metric]].rename(columns={metric: "now"})
    prev = df[df["year"] == prev_year][["country_name", metric]].rename(columns={metric: "prev"})
    merged = pd.merge(now, prev, on="country_name", how="left")
    merged["yoy"] = merged["now"] - merged["prev"]

    # keep rows with valid previous year
    merged = merged.dropna(subset="yoy")
    if merged.empty:
        return px.bar(title=f"Top-10 YoY change (no {prev_year} data)")
    
    top10 = merged.sort_values(by="yoy", ascending=False).head(10)

    fig = px.bar(
        top10,
        x="yoy",
        y="country_name",
        orientation="h",
        color="regional_indicator" if "regional_indicator" in top10.columns else None,
        title=f"Top-10 YoY Change in {_labels(metric)} - {prev_year} -> {latest_year}",
        hover_data=["now", "prev"]
    )

def _make_time_series(df: pd.DataFrame, metrics: list[str]) -> go.Figure:
    # Aggregat to mean for year for  each metric
    need = [m for m in (metrics or []) if m in df.columns]
    if "year" not in df.columns or not need:
        return px.line(title="Select at least one metric")
    
    agg = (
        df[["year"] + need]
        .groupby("year", as_index=False)
        .mean(numeric_only=True)
        .sort_values("year")
    )

    # Multiple lines
    long = agg.melt(id_vars="year", value_vars=need, var_name="metric", value_name="value")
    fig = px.line(
        long, x="year", 
        y="value", 
        color="metric", 
        markers=True,
        title="Trends Over Time (mean)",
        labels={"value": "Value", "year": "Year", "metric": "Metric"}
    )

    fig.update_layout(margin={"t": 10, "l": 10, "r": 10, "b": 10})
    return fig

# Data/defaults
_BASE = _df().copy()
if "year" in _BASE.columns:
    _BASE["year"] = _BASE["year"].astype(int)
_YEARS = sorted(pd.Series(_BASE["year"]).dropna().unique().tolist()) if "year" in _BASE.columns else None
_YEAR_MIN = int(_YEARS[0]) if _YEARS else None
_YEAR_MAX = int(_YEARS[-1]) if _YEARS else None

_DEFAULT_METRICS = _default_ts_metrics(_BASE)
_PRIMARY_METRIC = _DEFAULT_METRICS[0] if _DEFAULT_METRICS else None


# ---------- layout

controls_col = html.Div(
    className="col-12 col-lg-3",
    children=[
        html.H5("Filters", className="fw=bold mb-3"),
        
        html.Label("Year range", className="form-label mb-1"),
        dcc.Rangeslider(
            id="ts-year-range",
            min=_YEAR_MIN or 0,
            max=_YEAR_MAX or 0,
            value=[min, max],
            marks={int(y): str(int(y)) for y in _YEARS[:1] + _YEARS[1:: max(1, len(_YEARS)//6)] + _YEARS[-1:] } if _YEARS else None,
            tooltip={"always_visible": False, "placement": "bottom"},
        ),
        html.Div(style={"height": "8px"}),

        html.Label("Regions(s)", className="form-label mb-1"),
        dcc.Dropdown(
            id="ts-region-dd",
            options=_region_options(_BASE),
            placeholder="(optional)",
            multi=True,
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        html.Label("Country contains", className="form-label mb-1"),

        html.Label("Metrics (time series)", className="form-label mb-1")
    ]
)


charts_col = html.Div(
    className="col-12 col-lg-9",
    children=[
        html.Div(
            className="row g-3",
            children=[
                html.Div(
                    className="col-12 col-xl-6",
                    children=[
                        html.H6("Latest Snapshot (by Country)", className="fw-bold mb-2"),
                        dcc.Graph(id="ts-snapshot-table", style={"height": "360px"}),
                    ]
                ),
                html.Div(
                    className="col-12 col-xl-6",
                    children=[
                        html.H6("Top-10 YoY Change (Primary Metric)", className="fw-bold mb-2"),
                        dcc.Graph(id="ts-top10-you", style={"height": "360px"}),
                    ]
                ),
            ],
        ),
        # Bottom row
        dcc.Graph(id="ts-lines", style={"height": "430px"}, className="mt-3"),
        html.Div(id="ts-row-count", className="text-end text-muted mt-2"),
    ],
)

layout = html.Div(
    className="container-fluid py-4 rounded-2",
    style={"backgroundColor": "#649ec784"},
    children=[
        html.Div(
            className="text-center mb-4",
            children=[
                html.H2("Trends", className="text-light fw-bold"),
                html.P("Explore how key metrics evolve over time.", className="text-light fw-bold"),
            ],
        ),
        html.Div(
            className="card shadow-sm rounded-2",
            children=[
                html.Div(
                    className="card-body",
                    children=[
                        html.Div(
                            className="row g-3",
                            children=[controls_col, charts_col]
                        )
                    ]
                )
            ],
        ),
    ],
)

# ---------- Callbacks
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
    df = _apply_filters(_df(), year_range, _region_options, country_text)
    count_txt = f"{len(df):,} matching rows"

    # Determine latest year within selected range
    latest_year = int(df["year"].max()) if "year" in df.columns and not df.empty else None

    snapshot_fig = _make_snapshot_table(df, metrics, latest_year) if latest_year else go.Figure()
    primary = (metrics or _DEFAULT_METRICS or [])[:1]
    primary_metric = primary[0] if primary else None
    yoy_fig = _make_top10_yoy(df, primary_metric, latest_year) if latest_year else px.bar(title="Top-10 YoY Change")

    ts_fig = _make_time_series(df, metrics)

    return snapshot_fig, yoy_fig, ts_fig, count_txt
