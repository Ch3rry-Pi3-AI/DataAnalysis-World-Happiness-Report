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
    Return numeric columns, preferring headline metrics first.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset to inspect.
    
    Returns
    -------
    list of str
        Ordered list of numeric column names with headline
        metrics (if present) at the front.
    """
    
    # All numeric columns
    num = df.select_dtypes(include="number").columns.tolist()
    
    # Headline columns to prioritise in drop-downs
    headline = [
        "ladder_score",
        "logged_gdp_per_capita",
        "healthy_life_expectancy",
        "social_support",
        "freedom_to_make_life_choices",
        "generosity",
        "perceptions_of_corruption",
    ]

    # Headline columns 
    return [c for c in headline if c in num]

def _year_options(df: pd.DataFrame):
    """
    Build (label, value) options for the Year drop-down.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset containing a 'year' column.

    Returns
    -------
    list of dict
        Dash-friendly options; empty list if no 'year'.
    """
    
    if "year" not in df.columns:
        return []
    
    years = sorted(pd.Series(df["year"]).dropna().unique().tolist()) if "year" in df.columns else []
    
    return [{"label": str(int(y)), "value": int(y)} for y in years]

def _default_years(df: pd.DataFrame) -> list[int]:
    """
    Default selected years for the Year control.
    Use 2021 if present; otherwise leave empty (no pre-filter).
    """

    if "year" in df.columns and 2021 in set(pd.Series(df["year"]).dropna().astype(int)):
        return [2021]
    return []

def _region_options(df: pd.DataFrame):
    """
    Build (label, value) options for the Region(s) drop-down.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataset containing a 'regional_indicator' column.
    
    Returns
    -------
    list of dict
        Dash-friendly options; empty list if no region column.
    """
    
    if "regional_indicator" not in df.columns:
        return []
    
    regs = sorted(pd.Series(df["regional_indicator"]).dropna().unique().tolist())
    
    return [{"label": r, "value": r} for r in regs]

def _labels(s: str) -> str:
    """
    Re-format labels from snake_case.

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

def _apply_filters(df: pd.DataFrame, year_value, regions):
    """
    Apply Year and Region filters to the dataset.

    Parameters
    ----------
    df : pandas.DataFrame
        Unfiltered dataset.
    year_value : int or None
        Exact year to keep (optional).
    regions : list[str] or str or None
        Regions(s) to keep (optional).

    Returns
    -------
    pandas.DataFrame
        Filtered dataset.
    """
    
    # Year (multi, optional)
    if year_value and "year" in df.columns:
        if not isinstance(year_value, list):
            year_value = [year_value]
        keep_years = [int(y) for y in year_value]
        df = df[df["year"].astype(int).isin(keep_years)]

    # Region(s) (if provided in filter)
    if regions and "regional_indicator" in df.columns:
        if not isinstance(regions, list):
            regions = [regions]
        df = df[df["regional_indicator"].isin(regions)]
    return df

# ----------------------------------------------------------------------
# Data / Defaults
# ----------------------------------------------------------------------

# Cache a copy for helper options
_BASE = _df()

# Numeric columns for X/Y selectors
_NUMS = _numeric_cols(_BASE)

_DEFAULT_X = _NUMS[0] if _NUMS else None
_DEFAULT_Y = _NUMS[1] if len(_NUMS) > 1 else _DEFAULT_X

# Default year(s) for filter
_DEFAULT_YEARS = _default_years(_BASE)

# ----------------------------------------------------------------------
# Layout (modular: controls_col, plots_col, layout)
# ----------------------------------------------------------------------

# Left column: controls
controls_col = html.Div(
    className="col-12 col-lg-3",
    children=[
        html.H5("Controls", className="fw-bold mb-3"),

        # Year filter (optional)
        html.Label("Year", className="form-label mb-1"),
        dcc.Dropdown(
            id="rel-year-dd",
            options=_year_options(_BASE),
            value=_DEFAULT_YEARS,
            multi=True,
            placeholder="(optional)",
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        # Region(s) filter (optional; multi-select)
        html.Label("Region(s)", className="form-label mb-1"),
        dcc.Dropdown(
            id="rel-region-dd",
            options=_region_options(_BASE),
            placeholder="(optional)",
            multi=True,
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        # X-axis selector
        html.Label("X axis", className="form-label mb-1"),
        dcc.Dropdown(
            id="rel-x-dd",
            options=[{"label": _labels(c), "value": c} for c in _NUMS],
            value=_DEFAULT_X,
            clearable=False,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        # Y=axis selector
        html.Label("Y axis", className="form-label mb-1"),
        dcc.Dropdown(
            id="rel-y-dd",
            options=[{"label": _labels(c), "value": c} for c in _NUMS],
            value=_DEFAULT_Y,
            clearable=False,
            style={"fontSize": "12px"},
        ),
        html.Hr(),
        html.Small("Tip: choose X & Y, then refine by year and region.", className="text-muted"),
    ],
)

# Right column plots
plots_col = html.Div(
    className="col-12 col-lg-9",
    children=[
        dcc.Graph(id="rel-rel-fig", style={"height": "350px"}, className="mb-3"), # Scatter plot
        dcc.Graph(id="rel-corr-fig", style={"height": "350px"}),  # Correlation plot
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
                html.H2("Relationships", className="text-light fw-bold"),
                html.P(
                    "Investigate relationships and correlations in the World Happiness dataset.",
                    className="text-light fw-bold",
                ),
            ],
        ),

        # Card contraining controls + plots
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

@callback(
    Output("rel-rel-fig", "figure"),
    Input("rel-x-dd", "value"),
    Input("rel-y-dd", "value"),
    Input("rel-year-dd", "value"),
    Input("rel-region-dd", "value"),
)
def _update_relationship(x_col, y_col, year_value, region_values):
    """
    Update the scatterplot showing the relationship between X and Y.
    """
    df = _apply_filters(_df(), year_value, region_values)

    # Guard: require valid columns to show plot
    if not x_col or not y_col or x_col not in df.columns or y_col not in df.columns:
        return px.scatter(title="Select X and Y to view their relationship")

    # Colour by region (if 'regional_indicator' is in the DataFrame)
    color = "regional_indicator" if "regional_indicator" in df.columns else None

    # Year tag for title (supports multi-year)
    year_tag = ""
    if year_value:
        ys = year_value if isinstance(year_value, list) else [year_value]
        year_tag = " - Year(s): " + ", ".join(str(int(y)) for y in sorted({int(y) for y in ys}, reverse=True))

    # Build the scatter plot
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color,
        hover_data=["country_name", "year"] if {"country_name", "year"}.issubset(df.columns) else None,
        title=f"{_labels(x_col)} vs {_labels(y_col)}{year_tag}",
        opacity=0.9,
        labels={
            x_col: _labels(x_col),
            y_col: _labels(y_col),
            "regional_indicator": "Region",
            "country_name": "Country",
            "year": "Year",
        },
    )

    # Format markers & layout
    fig.update_layout(
        xaxis_title=_labels(x_col),
        yaxis_title=_labels(y_col),
        legend_title_text="Region",
        margin={"t": 60, "l": 10, "r": 10, "b": 10},
    )
    fig.update_traces(marker={"line": {"width": 0.5}})

    return fig


@callback(
    Output("rel-corr-fig", "figure"),
    Input("rel-year-dd", "value"),
    Input("rel-region-dd", "value"),
)

def _update_correlation(year_value, region_values):
    """
    Update the correlation heatmap across numeric columns.
    """
    df = _apply_filters(_df(), year_value, region_values)

    # Candidate numeric columns (respect headline order)
    cols = [c for c in _numeric_cols(df) if c in df.columns]
    if not cols:
        return px.imshow([[np.nan]], labels=dict(x="Metric", y="Metric", color=""),
                         title="No numeric columns found")

    # Compute correlation on filtered data; drop all-NA rows
    sub = df[cols].select_dtypes(include="number").dropna(how="all", axis=0)

    # If too few rows remain, correlation is not meaningful
    if len(sub) < 2:
        return px.imshow([[np.nan]], labels=dict(x="Metric", y="Metric", color=""),
                         title="Not enough data after filters to compute correlation")

    corr = sub.corr(numeric_only=True)

    # Guard: need at least 2 numeric columns for correlation
    if corr.empty or corr.shape[0] < 2:
        return px.imshow([[np.nan]], labels=dict(x="Metric", y="Metric", color=""),
                         title="Correlation (need ≥ 2 numeric columns)")

    # Year tag (supports multi-year)
    year_tag = ""
    if year_value:
        ys = year_value if isinstance(year_value, list) else [year_value]
        year_tag = " - Year(s): " + ", ".join(str(int(y)) for y in sorted({int(y) for y in ys}, reverse=True))

    # Labelise tick labels
    colmap = {c: _labels(c) for c in corr.columns}
    corr = corr.rename(index=colmap, columns=colmap)

    # Render heatmap with fixed z-range (for interpretability)
    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu",
        zmin=-1, zmax=1,
        title=f"Correlation of Numeric Metrics{year_tag}",
        labels=dict(x="Metric", y="Metric", color=""),
    )
    fig.update_layout(
        margin={"t": 60, "l": 10, "r": 10, "b": 10},
        coloraxis_colorbar=dict(title=""),
    )

    # Update axis tick labels
    fig.update_xaxes(tickfont=dict(size=10))
    fig.update_yaxes(tickfont=dict(size=10))
    
    # Update the in-cell annotation text
    fig.update_traces(textfont=dict(size=14))

    return fig
