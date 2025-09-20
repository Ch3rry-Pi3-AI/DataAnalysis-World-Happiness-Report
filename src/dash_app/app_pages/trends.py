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
    Reformat snake_case labels for display.
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


def _default_metric(df: pd.DataFrame) -> str | None:
    """
    Choose a single sensible default metric.

    Prefers 'ladder_score' if available; otherwise first numeric column.
    """

    nums = _numeric_cols(df)
    if "ladder_score" in nums:
        return "ladder_score"
    return nums[0] if nums else None


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


def _smart_year_marks(years: list[int], max_ticks: int = 8) -> dict[int, str] | None:
    """
    Build sparse RangeSlider marks that avoid crowding.

    Notes
    -----
    - The RangeSlider axis direction is always min→max (left→right).
    - We generate at most `max_ticks` evenly spaced labels across the range.

    Parameters
    ----------
    years : list[int]
        Sorted, unique year values (ascending).
    max_ticks : int
        Maximum number of labels to show.

    Returns
    -------
    dict[int, str] | None
        Mapping of tick positions to label strings, or None if no years.
    """

    if not years:
        return None
    if len(years) <= max_ticks:
        return {int(y): str(int(y)) for y in years}
    
    # Evenly sample years for labels (always include ends)
    idxs = np.linspace(0, len(years) - 1, num=max_ticks, dtype=int)
    sampled = sorted(set(years[i] for i in idxs))
    return {int(y): str(int(y)) for y in sampled}


def _region_color_map(df: pd.DataFrame) -> dict[str, str]:
    """
    Produce a consistent colour map for regions across all charts.

    Uses Plotly's qualitative palette and cycles if needed.
    """

    reg_col = "regional_indicator"
    if reg_col not in df.columns:
        return {}

    regions = sorted(pd.Series(df[reg_col]).dropna().unique().tolist())
    palette = px.colors.qualitative.Set2  # gentle, distinct
    # Cycle if more regions than colours available
    cmap = {r: palette[i % len(palette)] for i, r in enumerate(regions)}
    return cmap


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

def _make_top_change_between_bounds(
    df: pd.DataFrame,
    metric: str,
    start_year: int,
    end_year: int,
    color_map: dict[str, str],
    top_n: int = 10,
) -> go.Figure:
    """
    Top-N change between the **first and last** years selected in the slider.

    Change is computed as: delta = value(end_year) - value(start_year)

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered dataset (already subset to the year range + any region/country filters).
    metric : str
        Metric for which to compute the change.
    start_year : int
        First (left handle) year from slider.
    end_year : int
        Last (right handle) year from slider.
    color_map : dict[str, str]
        Mapping of region -> colour used across both charts.
    top_n : int
        Number of countries with the largest positive change to show.

    Returns
    -------
    plotly.graph_objects.Figure
        Horizontal bar chart of Top-N changes, colour by region (if available),
        with labelised axes and visible legend.
    """

    reg_col = "regional_indicator"

    if not metric or "year" not in df.columns or "country_name" not in df.columns:
        return px.bar(title="Top Change (select a metric)")

    # Current & base snapshots
    end = df[df["year"] == int(end_year)][["country_name", reg_col, metric]].rename(columns={metric: "end"})
    start = df[df["year"] == int(start_year)][["country_name", metric]].rename(columns={metric: "start"})

    # Inner-join on countries so both endpoints exist
    merged = pd.merge(end, start, on="country_name", how="inner")
    if merged.empty:
        return px.bar(title=f"Top Change in {_labels(metric)} · {start_year}→{end_year} (no overlapping countries)")

    merged["delta"] = merged["end"] - merged["start"]

    # Keep Top-N positive changes (largest first)
    top = merged.sort_values("delta", ascending=False).head(top_n)

    if top.empty:
        return px.bar(title=f"Top Change in {_labels(metric)} · {start_year}→{end_year} (no change)")

    # Explicitly order Y so the largest delta appears at the TOP (descending)
    y_order = top.sort_values("delta", ascending=False)["country_name"].tolist()

    fig = px.bar(
        top,
        x="delta",
        y="country_name",
        orientation="h",
        color=reg_col if reg_col in top.columns else None,
        color_discrete_map=color_map,
        hover_data={"start": True, "end": True, "delta": ":.2f"},
        title=f"Top 10 Change in {_labels(metric)} · {start_year}→{end_year}",
        labels={
            "delta": f"delta {_labels(metric)}",
            "country_name": "Country",
            reg_col: "Region",
        },
    )
    fig.update_layout(
        xaxis_title=f"delta {_labels(metric)}",
        yaxis_title="Country",
        showlegend=True,  # keep legend visible (now we have full width)
        margin={"t": 70, "l": 10, "r": 10, "b": 10},
        yaxis=dict(categoryorder="array", categoryarray=y_order),  # largest delta at TOP
    )
    return fig


def _make_time_series(df: pd.DataFrame, metric: str, color_map: dict[str, str]) -> go.Figure:
    """
    Region-mean time series for a single chosen metric.

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered dataset.
    metric : str
        One metric to plot across time.
    color_map : dict[str, str]
        Mapping of region -> colour, shared with the bar chart.

    Returns
    -------
    plotly.graph_objects.Figure
        Line chart of mean values per year for each region (legend = Region).
    """

    reg_col = "regional_indicator"
    if "year" not in df.columns or metric not in df.columns or reg_col not in df.columns:
        return px.line(title="Select a metric")

    # Aggregate mean by year and region for the chosen metric
    agg = (
        df[["year", reg_col, metric]]
        .groupby(["year", reg_col], as_index=False)
        .mean(numeric_only=True)
        .sort_values(["year", reg_col])
    )

    fig = px.line(
        agg,
        x="year",
        y=metric,
        color=reg_col,                       
        color_discrete_map=color_map,        
        markers=True,
        title=f"Trends Over Time — {_labels(metric)} (mean by Region)",
        labels={
            metric: _labels(metric),
            "year": "Year",
            reg_col: "Region",
        },
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=_labels(metric),
        margin={"t": 70, "l": 10, "r": 10, "b": 10},
    )
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

_DEFAULT_METRIC = _default_metric(_BASE)  

# Precompute a consistent region colour map for both charts
_REGION_CMAP = _region_color_map(_BASE)