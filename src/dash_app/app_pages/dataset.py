import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/dataset", name="Dataset", order=1)

# ----------------------- Helpers

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
    fig.update_layout()
    return fig

# ----------------------- Layout
_BASE_DF = _df()

layout = html.Div(
    [
        html.H2(),
        html.Div(
            className = "",
            children=[
                dcc.Dropdown(

                ),
                dcc.Dropdown(

                ),
            ],
        ),
        html.Div(),
        dcc.Graph(),
        html.Small()
    ]
)

# ----------------------- callbacks

@callback(
    Output(),
    Output(),
    Input(),
    Input(),
)

def _update_table(year_value, region_values):
    df = _df()

    if year_value is not None:
        df = df[df["year"] == int(year_value)]

    if region_values is not None:
        df = df[df["regional_indicator"].isin(region_values)]

    fig = _make_table_figure(df, max=max_rows=200)
    count_txt = f"{len(df):,} matching rows"
    
    return fig, count_txt