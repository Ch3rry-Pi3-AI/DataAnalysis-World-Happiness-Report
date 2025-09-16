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

