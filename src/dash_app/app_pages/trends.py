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

    Examples
    --------
    >>> _labels("ladder_score")
    'Ladder Score'
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