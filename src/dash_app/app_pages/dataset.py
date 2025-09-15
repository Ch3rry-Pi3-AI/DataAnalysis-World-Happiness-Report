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

def _make_overall_summary(df: pd.DataFrame, metric: str) -> go.Figure:
    if metric not in df.columns or df[metric].dropna().empty:
        return go.Figure(data=[go.Table(
            header=dict(values=["Notice", "Detail"], align="left"),
            cells=dict(values=[["Info"], ["Select a metric with data"]], align="left"),
        )])
    s = df[metric].dropna()
    # Robust stats
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
    stats["value"] = stats["value"].astype(float).round(3)
    fig = go.Figure(data=[
        go.Table(
            header=dict(values=[_labels(metric), "Value"], align="left"),
            cells=dict(values=[stats["stat"], stats["value"]], align="left"),
        )
    ])
    fig.update_layout(margin={"t": 0, "l": 0, "r": 0, "b": 0})
    return fig

def _make_regional_summary(df: pd.DataFrame, metric: str) -> go.Figure:
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

def _apply_filters(df: pd.DataFrame, year_value, regions, country_text):
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

# ---------------- Data / Defaults ---------
_BASE = _df()
_NUMS = _numeric_cols(_BASE)
_DEFAULT_METRIC = _NUMS[0] if _NUMS else None
_DEFAULT_COLUMNS = [c for c in ["country_name", "year", "regional_indicator", "ladder_score"] if c in _BASE.columns]

# ------------ Layout--------------

tables_col = html.Div(
    className="col-12 col-lg-9",
    children=[
        # Top: full-width main table
        dcc.Graph(id="ds-main-table", style={"height": "420px"}, className="mb-3"),
        html.Div(
            className="row g-3",
            children=[

                html.Div(
                    className="col-12 col-xl-6", 
                    children=[
                        html.H6("Overall Summary", className="fw-bold mb-2"),
                        dcc.Graph(id="ds-summary-overall", style={"height": "360px"}),
                ]),
                html.Div(
                    className="col-12 col-xl-6", 
                    children=[
                        html.H6("Regional Summary", className="fw-bold mb-2"),
                        dcc.Graph(id="ds-summary-region", style={"height": "360px"}),
                        ]
                    ),
            ],
        ),
        html.Div(
            id="ds-row-count", 
            className="text-end text-muted mt-2"
        ),
        html.Small(
            "Main table shows up to 200 rows.", 
            className="d-block text-end text-muted"
        ),
    ],
)


# ------------ Callbacks
@callback(
    Output("ds-main-table", "figure"),
    Output("ds-main-table", "figure"),
    Output("ds-main-table", "figure"),
    Output("ds-main-table", "figure"),
    Output("ds-main-table", "figure"),
    Output("ds-main-table", "figure"),
    Output("ds-main-table", "figure"),
    Output("ds-main-table", "figure"),
    Output("ds-main-table", "figure"),
    Output("ds-main-table", "figure"),
)

def _update_dataset_page(year_value, region_values, country_text, selected_cols, metric):
    pass
    df = _apply_filters(_df(), year_value, region_values, country_text)

    # Main table columns (fallback to all columns if none selected)
    cols = [c for c in (selected_cols) or list(df.columns) if c in df.columns]
    df_main = df[cols] if cols else df

    main_table_fig = _make_table_figure(df_main, max_rows=200)
    overall_fig = _make_overall_summary(df, metric,) if metric else _make_overall_summary(df, _DEFAULT_METRIC or df.columns[0])
    regional_fig = _make_regional_summary(df, metric) if metric else _make_regional_summary(df, _DEFAULT_METRIC or df.columns[0])

    count_txt = f"{len(df)}:, matching rows"
    return main_table_fig, overall_fig, regional_fig, count_txt    
