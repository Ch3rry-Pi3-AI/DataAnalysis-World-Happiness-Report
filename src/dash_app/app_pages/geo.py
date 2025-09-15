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

# ---------- Data / Defaults -----------
_BASE = _df()
_NUMS = _numeric_cols(_BASE)

# Defaults requested: Year=2021, Metric="ladder_score"
_DEFAULT_YEAR = 2021 if "year" in _BASE.columns and (pd.Series(_BASE["year"]).dropna() == 2021).any() else (int(pd.Series(_BASE["year"]).dropna().max()) if "year" in _BASE.columns else None)
_DEFAULT_METRIC = "ladder_score" if "ladder_score" in _NUMS else (_NUMS[0] if _NUMS else None)