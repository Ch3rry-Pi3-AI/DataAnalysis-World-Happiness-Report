import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/relationship", name="Relationship 📈", order=3)

# ---------- Helpers ----------
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

    # put headline metrics first, then the rest
    return [c for c in headline if c in num] + [c for c in num if c not in headline]

def _year_options(df: pd.DataFrame):
    years = sorted(df["year"].dropna().unique().tolist()) if "year" in df.columns else []
    return [{"label": str(int(y)), "value": int(y)} for y in years]

def _region_options(df: pd.DataFrame):
    if "regional_indicator" not in df.columns:
        return []
    regs = sorted(df["regional_indicator"].dropna().unique().tolist())
    return [{"label": r, "value": r} for r in regs]

# --------------- Layout
_BASE_DF = _df()
_NUMERIC = _numeric_cols(_BASE_DF)
_DEFAULT_X = _NUMS[0] if _NUMS else None
_DEFAULT_Y = _NUMS[1] if len(_NUMS) > 1 else _DEFAULT_X

layout = html.Div(
    [
        html.H2("Relationship Explorer", className="fw-bold text-center my-3"),
        html.Div(
            className="",
            children=[
                dcc.Dropdown(

                ),
                dcc.Dropdown(

                ),
                dcc.Dropdown(

                ),
                dcc.Dropdown(

                ),
                dcc.Checklist(

                ),
            ],
        ),

        dcc.Graph(id="relationship-graph"),
        html.Small(

        )
    ]
)

# --------------- Callbacks
@callback(
    Output("rel-scatter", "figure"),
    Input("rel-x-dd", "value"),
    Input("rel-y-dd", "value"),
    Input("rel-year-dd", "value"),
    Input("rel-region-dd", "value"),
    Input("rel-toggles", "value"),
)

def update_relationship_graph(x, y, year, region, toggles):
    pass