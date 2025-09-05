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

_BASE = _df()
_NUMS = _numeric_cols(_BASE)
_DEFAULT_X = _NUMS[0] if _NUMS else None
_DEFAULT_Y = _NUMS[1] if len(_NUMS) > 1 else _DEFAULT_X

# ----------------- layout
control_col = html.Div(

)

plots_col = html.Div(

)

layout = html.Div(

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
    