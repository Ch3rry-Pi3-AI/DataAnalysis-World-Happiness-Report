import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/explore", name="Explore", order=2)

def _df() -> pd.DataFrame:
    return get_gold_df()

def _numeric_cols(df: pd.DataFrame) -> list[str]:
    num = df.select_dtypes(include="number").columns.tolist()
    headline = [
        "ladder_score",
        "logged_gdp_per_capita",
        "healthy_life_expectancy",
        "social_support",
        "freedom_to_make_life_choices",
        "generosity",
        "perceptions_of_corruption",

    ]

    return [c for c in headline if c in num]

def _year_options(df: pd.DataFrame):
    # Extract unique years in "year" column
    years = sorted(pd.Series(df["year"]).unique().tolist(), reverse=True)

    # Return a list of dictionaries, one per year, e.g., {"label": "2021", "value": 2021}
    return [{"label": str(int(y)), "value": int(y)} for y in years]

def _region_options(df: pd.DataFrame):
    regs = sorted(pd.Series(df["regional_indicator"]).dropna().unique().tolist())
    return [{"label": r, "value": r} for r in regs]

def _labels(s: str) -> str:
    return s.replace("_", " ").title()

# ------------ Data / defaults

_BASE = _df()
_NUMS = _numeric_cols(_BASE)
_DEFAULT_X = _NUMS[0] if _NUMS else None
_DEFAULT_Y = _NUMS[1] if len(_NUMS) > 1 else _DEFAULT_X

# ----------------- layout
controls_col = html.Div(
    className="col-12 col-lg-3",
    children=[
        html.H5("Controls", className="fw-bold mb-3"),
        html.Label("Year", className="form-label mb-1"),
        dcc.Dropdown(
            id="ex-year-dd",
            options=_year_options(_BASE),
            placeholder="(optional)",
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        html.Label("Region(s)", className="form-label mb-1"),
        dcc.Dropdown(
            id="ex-region-dd",
            options=_region_options(_BASE),
            placeholder="(optional)",
            multi=True,
            clearable=True,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        html.Label("X axis", className="form-label mb-1"),
        dcc.Dropdown(
            id="ex-x-dd",
            options=[{"label": _labels(c), "value": c} for c in _NUMS],
            value=_DEFAULT_X,
            clearable=False,
            style={"fontSize": "12px"},
        ),
        html.Div(style={"height": "8px"}),

        html.Label("Y axis", className="form-label mb-1"),
        dcc.Dropdown(
            id="ex-y-dd",
            options=[{"label": _labels(c), "value": c} for c in _NUMS],
            value=_DEFAULT_Y,
            clearable=False,
            style={"fontSize": "12px"},
        ),
        html.Hr(),
        html.Small("Tip: choose X & Y, then refine by year and region.", className="text-muted"),
    ],
)

plots_col = html.Div(
    ClassName="col-12 col-lg-9",
    children=[
        dcc.Graph(id="ex-rel-fig", style={"height": "400px"}, className="mb-3"),
        dcc.Graph(id="ex-dist-fig", style={"height": "400px"}),
    ],
)

layout = html.Div(
    className="container py-4 rounded-2",
    style={"backgroundColor": "#649ec784"},
    children=[
        html.Div(
            className="text-center mb-4",
            children=[
                html.H2("Explore", className="text-light fw-bold"),
                html.P(
                    "Investigate relationships and distributions in the World Happiness dataset.", 
                    className="text-light fw-bold",
                ),
            ],
        ),
        html.Div(
            className="card shadow-sm rounded-2",
            children=[
                html.Div(
                    className="card-body",
                    children=[
                        html.Div(
                            className="row g-3",
                            children=[
                                controls_col,
                                plots_col
                            ]
                        )
                    ],
                ),
            ],
        ),
    ],
)

# ------------------- callbacks
def _apply_filters(df: pd.DataFrame, year_value: int = 2021, regions: str = "regional_indicator"):
    if year_value is not None:
        df = df[df["year"] == int(year_value)]

    if regions:
        if not isinstance(regions, list):
            regions = [regions]
        df = df[df["regional_indicator"].isin(regions)]

@callback(
    Output("ex-rel-fig", "figure"),
    Input("ex-x-dd", "value"),
    Input("ex-y-dd", "value"),
    Input("ex-year-dd", "value"),
    Input("ex-region-dd", "value"),
)

def _update_relationship(x_col, y_col, year_value, region_values):
    df = _apply_filters(_df(), year_value, region_values)
    if not x_col or y_col:
        return px.scatter(title="Select X and Y to view their relationship")
    
    colour = "regional_indicator"
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=colour,
        hover_data=["country_name", "year"],
        title=f"{_labels(x_col)} vs {_labels(y_col)}"
    )
    fig.update_traces(marker={"line": {"width": 0.5}})
    fig.update_layout(
        margin={"t": 60, "l": 10, "r": 10, "b": 10},
        legend=dict(title="Region", bgolor="rgba(225,225,225,0.6)"),
    )
    
    return fig
    