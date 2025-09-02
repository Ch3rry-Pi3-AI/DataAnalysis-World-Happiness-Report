import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px

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

def update_distribution(metric, year_value, regions, bins, colour_toggle):
    df = _df()

    if metric is None or metric not in df.columns:
        return px.histogram(title="select a metric to view its distribution")
    
    # Apply filters
    if year_value is not None and "year" in df.columns:
        df = df[df["year"] == int(year_value)]
    if regions and "regional_indicator" in df.columns:
        if not isinstance(regions, list):
            regions = [regions]
        df = df[df["regional_indicator"].isin(regions)]

    colour_col = "regional_indicator" if ("by_region" in colour_toggle and "regional_indicator" in df.columns) else None

    # Histogram with optional colour & bin count
    fig = px.histogram(
        df,
        x=metric,
        nbins=bins,
        color=colour_col,
        barmode="overlay" if colour_col else "relative",
        opacity=0.75,
        title=f"Distribution of {metric.replace('_', ' ').title()}",
    )

    # Add lightweight box summary under x-axis (marginal) for quick spread check
    fig.update_traces(marker_line_width=0)
    fig.update_layout(margin={"t": 60, "l": 10, "r": 10, "b": 10})
    return fig