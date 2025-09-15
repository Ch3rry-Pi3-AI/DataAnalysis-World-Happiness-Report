# src/dash_app/app_pages/dataset.py
import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/dataset", name="Dataset 📋", order=1)

# ---------------- Helpers ----------------
def _df() -> pd.DataFrame:
    return get_gold_df()

def _numeric_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()

def _text_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(exclude="number").columns.tolist()

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

def _col_options(df: pd.DataFrame):
    return [{"label":_labels(c), "value": c} for c in df.columns]

def _make_table_figure(df: pd.DataFrame, max_rows: int = 200) -> go.Figure:
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