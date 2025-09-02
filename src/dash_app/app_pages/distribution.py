import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/distribution", name="Distribution", order=2)

# ---- Helpers ----------------------------------------------------------------

def _df() -> pd.DataFrame:
    return get_gold_df()

def _numeric_cols(df: pd.DataFrame) -> list[str]:
    num_cols = df.select_dtypes(include="number").columns.tolist()
    headline = [
        "ladder_score",
        "logged_gdp_per_capita",
        "health_life_expectancy",
        "social_support",
        "freedom_to_make_life_choices",
        "generosity",
        "perceptions_of_corruption",
    ]

    ordered = [c for c in headline if c in num_cols]
    return ordered

def _year_options(df: pd.DataFrame):
    years = sorted(df["year"].dropna().unique().tolist())
    return [{"label": str(int(y)), "value": int(y)} for y in years]

def _region_options(df: pd.DataFrame):
    regs = sorted(df["regional_indicator"].dropna().unique().tolist())
    return [{"label": r, "value": r} for r in regs]

# ---- Layout -----------------------------------------------------------------
_BASE_DF = _df()
_NUMERIC = _numeric_cols(_BASE_DF)

layout = html.Div(
    [
        html.H2("Distribution Explorer", className="fw-bold text-center my-3"),
        html.Div(
            className="",
            children=[
                dcc.Dropdown(
                    id="dist-metic-dd",
                    options=[{"label": c.replace("_", " ").title(), "value": c} for c in _NUMERIC],
                    value=_NUMERIC[0] if _NUMERIC else None,
                    placeholder="Select Metric",
                    clearable=False,
                ),
                dcc.Dropdown(
                    id="dist-year-dd",
                    options=_year_options(_BASE_DF),
                    placeholder="Filter Year (optional)",
                    clearable=True,
                ),
                dcc.Dropdown(
                    id="dist-region-dd",
                    options=_region_options(_BASE_DF),
                    placeholder="Filter Region(s) (optional)",
                    multi=True,
                    clearable=True,
                ),
                dcc.Slider(
                    id="dist-bins-slider",
                    min=10,
                    max=80,
                    step=1,
                    value=30,
                    marks={i: str(i) for i in range(10, 81, 10)},
                    tooltip={"placement": "bottom", "always_visible": True},
                ),
                dcc.Checklist(
                    id="dist-colour-toggle",
                    options=[{"label": "Colour by Region", "value": "by_region"}],
                    value=[],
                    className="d-flex align-items-center",

                ),
            ],
        ),

        dcc.Graph(id="dist-fig"),
        html.Small("Tip: use the dropdowns to filter and compare distributions.", className="d-block text-center text-muted mt-2"),
    ]
)

# ---- Callbacks -------------------------------------------------------------

@callback(
    Output("dist-fig", "figure"),
    Input("dist-metic-dd", "value"),
    Input("dist-year-dd", "value"),
    Input("dist-region-dd", "value"),
    Input("dist-bins-slider", "value"),
    Input("dist-colour-toggle", "value"),
)

def update_distribution():
    pass