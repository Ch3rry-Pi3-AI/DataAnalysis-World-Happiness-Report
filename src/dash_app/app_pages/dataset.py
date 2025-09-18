# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------

# Dash framework + primitives
import dash
from dash import html, dcc, Input, Output, callback

# Data handling
import pandas as pd
import numpy as np

# Plotting (table figures)
import plotly.graph_objects as go

# Project data accessor
from src.dash_app.data_access import get_gold_df

# ----------------------------------------------------------------------
# Page registration
# ----------------------------------------------------------------------

# Register the page so Dash discovers it at startup
dash.register_page(__name__, path="/dataset", name="Dataset 📋", order=1)

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

def _text_cols(df: pd.DataFrame) -> list[str]:
    """
    Return non-numeric (text/categorical) column names.
    
    Parameters
    ----------
    df : pandas.DataFrame
    
    Returns
    -------
    list of str
        Non-numeric columns.
    """
    
    return df.select_dtypes(exclude="number").columns.tolist()

def _year_options(df: pd.DataFrame):
    """
    Build (label, value) options for the Year drop-down.

    Returns empty list if 'year' is missing.
    """
    
    if "year" not in df.columns:
        return []

    years = sorted(pd.Series(df["year"]).dropna().unique().tolist()) if "year" in df.columns else []

    return [{"label": str(int(y)), "value": int(y)} for y in years]

def _region_options(df: pd.DataFrame):
    """
    Build (label, value) options for Region(s).

    Returns empty list if 'regional_indicator' column is missing. 
    """
    
    if "regional_indicator" not in df.columns:
        return []
    
    regs = sorted(pd.Series(df["regional_indicator"]).dropna().unique().tolist())
    return [{"label": r, "value": r} for r in regs]

def _labels(s: str) -> str:
    """
    Reformat snake_case columns
    """
    
    return s.replace("_", " ").title()

def _col_options(df: pd.DataFrame):
    """
    Build (label, value) options for the main-table column selector.
    """
    
    return [{"label":_labels(c), "value": c} for c in df.columns]

def _make_table_figure(df: pd.DataFrame, max_rows: int = 200) -> go.Figure:
    """
    Render a simple pageless table with the first 'max_rows' number of rows.

    Parameters
    ----------
    df : pandas.DataFrame
        Data to render (with filtered/column-selected).
    max_rows : int, optional
        Row cap for display. (Default: 200).

    Returns
    -------
    plotly.graph_objects.Figure
        Table figure.
    """
    
    df_show = df.head(max_rows)
    cols = list(df_show.columns)
    header_vals = [_labels(c) for c in cols]
    cell_vals = [df_show[c] for c in cols]

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=header_vals, align="left"),
                cells=dict(values=cell_vals, align="left"),
            )
        ]
    )

    fig.update_layout(margin={"t": 0, "l": 0, "r": 0, "b": 0})
    return fig

def _make_overall_summary(df: pd.DataFrame, metric: str) -> go.Figure:
    """
    Overall (global) summary stats for a chosen metric.

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered dataset.
    metric : str
        Column name to summarise.

    Returns
    -------
    plotly.graph_objects.Figure
        Table figure with summary stats.
    """
    
    if metric not in df.columns or df[metric].dropna().empty:
        return go.Figure(data=[go.Table(
            header=dict(values=["Notice", "Detail"], align="left"),
            cells=dict(values=[["Info"], ["Select a metric with data"]], align="left"),
        )])
    
    s = df[metric].dropna()
    
    # Stats block
    stats = pd.DataFrame({
        "stat": ["count", "mean", "std", "min", "25%", "50%", "75%", "max"],
        "value": [
            int(s.count()),
            s.mean(),
            s.std(),
            s.min(),
            s.quantile(0.25),
            s.median(),
            s.quantile(0.50),
            s.max(),
        ],
    })

    stats["value"] = stats["value"].astype(float).round(1)
    
    fig = go.Figure(data=[
        go.Table(
            header=dict(values=[_labels(metric), "Value"], align="left"),
            cells=dict(values=[stats["stat"], stats["value"]], align="left"),
        )
    ])

    fig.update_layout(margin={"t": 0, "l": 0, "r": 0, "b": 0})
    
    return fig

def _make_regional_summary(df: pd.DataFrame, metric: str) -> go.Figure:
    """
    Regional mean + count table for a chosen metric.

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered dataset.
    metric : str
        Metric to aggregate by region.

    Returns
    -------
    plotly.graph_objects.Figure
        Table figure with Region / Mean / Count.
    """
        
    reg_col = "regional_indicator"
    if reg_col not in df.columns or metric not in df.columns:
        return go.Figure(data=[go.Table(
            header=dict(values=["Notice", "Detail"], align="left"),
            cells=dict(values=[["Info"], ["Region or metric missing"]], align="left"),
        )])

    g = (
        df[[reg_col, metric]]
        .dropna(subset=[metric])
        .groupby(reg_col, as_index=False)
        .agg(mean=(metric, "mean"), count=(metric, "count"))
        .sort_values(["count", "mean"], ascending=[False, False])
    )
    if g.empty:
        return go.Figure(data=[go.Table(
            header=dict(values=["Notice", "Detail"], align="left"),
            cells=dict(values=[["Info"], ["No data after filters"]], align="left"),
        )])
    g["mean"] = g["mean"].round(3)

    fig = go.Figure(data=[
        go.Table(
            header=dict(values=["Region", "Mean", "Count"], align="left"),
            cells=dict(values=[g[reg_col], g["mean"], g["count"]], align="left"),
        )
    ])
    fig.update_layout(margin={"t": 0, "l": 0, "r": 0, "b": 0})
    return fig

def _apply_filters(df: pd.DataFrame, year_value, regions, country_text) -> pd.DataFrame:
    """
    Apply Year, Region(s), and Country text filters.

    Parameters
    ----------
    df : pandas.DataFrame
        Unfiltered dataset.
    year_value : int or None
        Exact year to keep (optional).
    regions : list[str] or str or None
        Region(s) to keep (optional).
    country_text : str or None
        Case-insensitive substring to match against 'country_name'.

    Returns
    -------
    pandas.DataFrame
        Filtered dataset.
    """

    # Year filter
    if year_value is not None and "year" in df.columns:
        df = df[df["year"] == int(year_value)]

    # Region(s) filter
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

# ----------------------------------------------------------------------
# Data / Defaults
# ----------------------------------------------------------------------

# Cached base for options
_BASE = _df()                                    

# Numeric options
_NUMS = _numeric_cols(_BASE)                     

# Default summary metric
_DEFAULT_METRIC = _NUMS[0] if _NUMS else None    # default summary metric

# Default visible columns
_DEFAULT_COLUMNS = [                             
    c for c in ["country_name", "year", "regional_indicator", "ladder_score"]
    if c in _BASE.columns
]

# ----------------------------------------------------------------------
# Layout (modular: controls_col, tables_col, layout)
# ----------------------------------------------------------------------

# Left column: filters and selectors
controls_col = html.Div(
    className="col-12 col-lg-3",
    children=[
        html.H5("Filters", className="fw-bold mb-3"),

        # Year (optional)
        html.Label("Year", className="form-label mb-1"),
        dcc.Dropdown(
            id="ds-year-dd",
            options=_year_options(_BASE),
            placeholder="(optional)",
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        # Region(s) (optional, multi)
        html.Label("Region(s)", className="form-label mb-1"),
        dcc.Dropdown(
            id="ds-region-dd",
            options=_region_options(_BASE),
            placeholder="(optional)",
            multi=True,
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        # Country contains (text search)
        html.Label("Country contains", className="form-label mb-1"),
        dcc.Input(
            id="ds-country-text",
            type="text",
            placeholder="e.g., 'Uni' for 'United...'",
            style={"width": "100%", "fontSize": "12px"},
        ),
        html.Div(style={"height": "12px"}),

        html.Hr(),

        # Main table: choose columns to display
        html.Label("Columns to show (main table)", className="form-label mb-1"),
        dcc.Dropdown(
            id="ds-colselect-dd",
            options=_col_options(_BASE),
            value=_DEFAULT_COLUMNS,
            multi=True,
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        # Summary metric used by the two lower tables
        html.Label("Summary metric", className="form-label mb-1"),
        dcc.Dropdown(
            id="ds-metric-dd",
            options=[{"label": _labels(c), "value": c} for c in _NUMS],
            value=_DEFAULT_METRIC,
            clearable=False,
            style={"fontSize": "12px"},
        ),

        html.Hr(),
        html.Small(
            "Tip: refine by year/region/country; choose columns and a metric for summaries.",
            className="text-muted",
        ),
    ],
)

# Right column: tables
tables_col = html.Div(
    className="col-12 col-lg-9",
    children=[
        # Top: full-width main table
        dcc.Graph(id="ds-main-table", style={"height": "420px"}, className="mb-3"),

        # Second row: two summary tables side-by-side
        html.Div(
            className="row g-3",
            children=[
                html.Div(
                    className="col-12 col-xl-6",
                    children=[
                        html.H6("Overall Summary", className="fw-bold mb-2"),
                        dcc.Graph(id="ds-summary-overall", style={"height": "360px"}),
                    ],
                ),
                html.Div(
                    className="col-12 col-xl-6",
                    children=[
                        html.H6("Regional Summary", className="fw-bold mb-2"),
                        dcc.Graph(id="ds-summary-region", style={"height": "360px"}),
                    ],
                ),
            ],
        ),

        # Row count + hint
        html.Div(id="ds-row-count", className="text-end text-muted mt-2"),
        html.Small("Main table shows up to 200 rows.", className="d-block text-end text-muted"),
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
                html.H2("Dataset Explorer", className="text-light fw-bold"),
                html.P("Filter, view, and summarise the World Happiness dataset.", className="text-light fw-bold"),
            ],
        ),

        # Card containing controls + tables
        html.Div(
            className="card shadow-sm rounded-2",
            children=[html.Div(className="card-body", children=[
                html.Div(className="row g-3", children=[controls_col, tables_col])
            ])],
        ),
    ],
)


# ----------------------------------------------------------------------
# Callbacks
# ----------------------------------------------------------------------

@callback(
    Output("ds-main-table", "figure"),
    Output("ds-summary-overall", "figure"),
    Output("ds-summary-region", "figure"),
    Output("ds-row-count", "children"),
    Input("ds-year-dd", "value"),
    Input("ds-region-dd", "value"),
    Input("ds-country-text", "value"),
    Input("ds-colselect-dd", "value"),
    Input("ds-metric-dd", "value"),
)
def _update_dataset_page(year_value, region_values, country_text, selected_cols, metric):
    """
    Update the main (pageless) table and the two summary tables.

    Notes
    -----
    - Main table respects selected columns; falls back to all columns if none selected.
    - Summary tables use the chosen metric; fall back to a default numeric if needed.
    """
    
    df = _apply_filters(_df(), year_value, region_values, country_text)

    # Main table columns (fallback to all if none selected)
    cols = [c for c in (selected_cols or list(df.columns)) if c in df.columns]
    df_main = df[cols] if cols else df

    # Build figures
    main_table_fig = _make_table_figure(df_main, max_rows=200)
    fallback_metric = metric or (_DEFAULT_METRIC if _DEFAULT_METRIC in df.columns else (cols[0] if cols else None))
    overall_fig = _make_overall_summary(df, fallback_metric) if fallback_metric else _make_overall_summary(df, metric)
    regional_fig = _make_regional_summary(df, fallback_metric) if fallback_metric else _make_regional_summary(df, metric)

    # Nicely formatted row count
    count_txt = f"{len(df):,} matching rows"

    return main_table_fig, overall_fig, regional_fig, count_txt
