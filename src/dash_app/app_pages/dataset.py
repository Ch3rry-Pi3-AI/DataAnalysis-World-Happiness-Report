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
    preferred = [
        "country_name", "year", "ladder_score", "logged_gdp_per_capita",
        "healthy_life_expectancy", "social_support", "freedom_to_make_life_choices",
        "generosity", "perceptions_of_corruption", "regional_indicator",
        "latitude", "longitude", "country"
    ]

    cols = [c for c in preferred if c in df_show.columns]

    header_vals = [c.replace("_", " ").title() for c in cols]
    cell_vals = [df.show[c].tolist() for c in cols]

    git = go.Figure(
        data=[
            go.Table(
                header=dict(values=header_vals, align="left"),
                cells=dict(values=cell_vals, align="left"),
            )
        ]
    )

# ----------------------- Layout
_BASE_DF = _df()

layout = html.Div(
    className="container py-3",
    children=[

        html.H2

        # Page title
        html.Div(
            className="",
            children=[

                # Year dropdown
                html.Div(
                    [
                        html.Label(),
                        dcc.Dropdown(

                        ),
                    ]
                ),

                # Region dropdown
                html.Div(
                    [
                        html.Label(),
                        dcc.Dropdown(

                        ),
                    ]
                ),
            ],
        ),

        # Table
        html.Div(),
        dcc.Graph(),
        html.Div(
            className="",
            children=html.Small()
        ),
    ],
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