import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/dataset", name="Dataset 📋", order=1)

# ---- Helpers ----------------------------------------------------------------

def _df() -> pd.DataFrame:
    return get_gold_df()

def _year_options(df: pd.DataFrame):
    years = sorted(df["year"].dropna().unique().tolist())
    return [{"label": str(int(y)), "value": int(y)} for y in years]

def _region_options(df: pd.DataFrame):
    regs = sorted(df["regional_indicator"].dropna().unique().tolist())
    return [{"label": r, "value": r} for r in regs]

def _make_table_figure(df: pd.DataFrame, max_rows: int = 200) -> go.Figure:
    df_show = df.head(max_rows)
    cols = df_show.columns
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(values=[c.replace("_", " ").title() for c in cols], align="left"),
                cells=dict(values=[df_show[c] for c in cols], align="left"),
            )
        ]
    )
    fig.update_layout(margin={"t": 0, "l": 0, "r": 0, "b": 0})
    return fig

# ---- Layout -----------------------------------------------------------------

_BASE_DF = _df()

layout = html.Div(
    [
        html.H2("Dataset Explorer", className="fw-bold text-center my-3"),
        html.Div(
            className="d-flex flex-wrap justify-content-center gap-3 mb-3",
            children=[
                dcc.Dropdown(
                    id="ds-year-dd",
                    options=_year_options(_BASE_DF),
                    placeholder="Select Year",
                    clearable=True,
                    className="form-select",
                    style={"width": "220px"},
                ),
                dcc.Dropdown(
                    id="ds-region-dd",
                    options=_region_options(_BASE_DF),
                    placeholder="Select Region(s)",
                    multi=True,
                    clearable=True,
                    className="form-select",
                    style={"width": "320px"},
                ),
            ],
        ),
        html.Div(id="ds-row-count", className="text-center text-muted mb-2"),
        dcc.Graph(id="ds-table", figure=_make_table_figure(_BASE_DF)),
        html.Small("Showing up to 200 rows; refine filters to narrow results.", className="d-block text-center text-muted mt-2"),
    ]
)

# ---- Callbacks ---------------------------------------------------------------

@callback(
    Output("ds-table", "figure"),
    Output("ds-row-count", "children"),
    Input("ds-year-dd", "value"),
    Input("ds-region-dd", "value"),
)
def _update_table(year_value, region_values):
    df = _df()

    if year_value is not None:
        df = df[df["year"] == int(year_value)]
    if region_values:
        if not isinstance(region_values, list):
            region_values = [region_values]
        df = df[df["regional_indicator"].isin(region_values)]

    fig = _make_table_figure(df, max_rows=200)
    count_txt = f"{len(df):,} matching rows"
    return fig, count_txt
