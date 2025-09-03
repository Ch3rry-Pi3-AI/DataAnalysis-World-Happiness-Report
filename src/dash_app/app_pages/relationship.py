# src/dash_app/app_pages/relationship.py
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

# ---------- Layout ----------
_BASE = _df()
_NUMS = _numeric_cols(_BASE)
_DEFAULT_X = _NUMS[0] if _NUMS else None
_DEFAULT_Y = _NUMS[1] if len(_NUMS) > 1 else _DEFAULT_X

layout = html.Div(
    [
        html.H2("Explore Relationships Between Metrics", className="fw-bold text-center my-3"),

        # Controls (Bootstrap utilities only)
        html.Div(
            className="d-flex flex-wrap justify-content-center gap-3 mb-3",
            children=[
                dcc.Dropdown(
                    id="rel-x-dd",
                    options=[{"label": c.replace("_", " ").title(), "value": c} for c in _NUMS],
                    value=_DEFAULT_X,
                    clearable=False,
                    placeholder="X axis",
                ),
                dcc.Dropdown(
                    id="rel-y-dd",
                    options=[{"label": c.replace("_", " ").title(), "value": c} for c in _NUMS],
                    value=_DEFAULT_Y,
                    clearable=False,
                    placeholder="Y axis",
                ),
                dcc.Dropdown(
                    id="rel-year-dd",
                    options=_year_options(_BASE),
                    placeholder="Filter Year (optional)",
                    clearable=True,
                ),
                dcc.Dropdown(
                    id="rel-region-dd",
                    options=_region_options(_BASE),
                    placeholder="Filter Region(s) (optional)",
                    multi=True,
                    clearable=True,
                ),
                dcc.Checklist(
                    id="rel-toggles",
                    options=[
                        {"label": " Colour by Region", "value": "by_region"},
                        {"label": " Add Trendline", "value": "trend"},
                    ],
                    value=[],
                    className="d-flex align-items-center",
                ),
            ],
        ),

        dcc.Graph(id="rel-fig"),
        html.Small(
            "Tip: pick X and Y, then filter by year/region or add a trendline.",
            className="d-block text-center text-muted mt-2",
        ),
    ]
)

# ---------- Callback ----------
@callback(
    Output("rel-fig", "figure"),
    Input("rel-x-dd", "value"),
    Input("rel-y-dd", "value"),
    Input("rel-year-dd", "value"),
    Input("rel-region-dd", "value"),
    Input("rel-toggles", "value"),
)
def _update_relationship(x_col, y_col, year_value, region_values, toggles):
    df = _df()

    if x_col is None or y_col is None or x_col not in df.columns or y_col not in df.columns:
        return px.scatter(title="Select X and Y to view their relationship")

    # Filters
    if year_value is not None and "year" in df.columns:
        df = df[df["year"] == int(year_value)]
    if region_values and "regional_indicator" in df.columns:
        if not isinstance(region_values, list):
            region_values = [region_values]
        df = df[df["regional_indicator"].isin(region_values)]

    color = "regional_indicator" if ("by_region" in (toggles or []) and "regional_indicator" in df.columns) else None
    trendline = "ols" if ("trend" in (toggles or [])) else None

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color,
        trendline=trendline,
        hover_data=["country_name", "year"] if {"country_name", "year"}.issubset(df.columns) else None,
        title=f"{x_col.replace('_',' ').title()} vs {y_col.replace('_',' ').title()}"
              + (f" – Year {year_value}" if year_value else ""),
        opacity=0.85,
    )

    # A little polish, still minimal
    fig.update_traces(marker={"line": {"width": 0.5}})
    fig.update_layout(margin={"t": 60, "l": 10, "r": 10, "b": 10}, legend_title_text="Region" if color else None)
    return fig
