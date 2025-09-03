import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/avg-feature", name="Avg Feature 📊", order=4)

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
    return [c for c in headline if c in num] + [c for c in num if c not in headline]

def _group_options(df: pd.DataFrame):
    # assume these columns exist; they do in your gold dataset
    options = [
        {"label": "By Region",  "value": "regional_indicator"},
        {"label": "By Year",    "value": "year"},
        {"label": "By Country", "value": "country_name"},
    ]
    return [opt for opt in options if opt["value"] in df.columns]

def _labelize(col: str) -> str:
    return col.replace("_", " ").title()

# ---------- Layout ----------
_BASE = _df()
_NUMS = _numeric_cols(_BASE)
_GROUPS = _group_options(_BASE)

_DEFAULT_METRIC = _NUMS[0] if _NUMS else None
_DEFAULT_GROUP = _GROUPS[0]["value"] if _GROUPS else None

layout = html.Div(
    [
        html.H2("Average Feature by Group", className="fw-bold text-center my-3"),

        # Controls
        html.Div(
            className="d-flex flex-wrap justify-content-center gap-3 mb-3",
            children=[
                dcc.Dropdown(
                    id="avg-metric-dd",
                    options=[{"label": _labelize(c), "value": c} for c in _NUMS],
                    value=_DEFAULT_METRIC,
                    clearable=False,
                    placeholder="Select a metric",
                ),
                dcc.Dropdown(
                    id="avg-group-dd",
                    options=_GROUPS,
                    value=_DEFAULT_GROUP,
                    clearable=False,
                    placeholder="Group by…",
                ),
                dcc.Slider(
                    id="avg-topn",
                    min=5, max=30, step=1, value=15,
                    marks={5: "5", 10: "10", 15: "15", 20: "20", 30: "30"},
                ),
            ],
        ),

        dcc.Graph(id="avg-bar"),
        html.Small(
            "Tip: Group by Region/Year for a compact view. Use Top N when grouping by Country.",
            className="d-block text-center text-muted mt-2",
        ),
    ]
)

# ---------- Callback ----------
@callback(
    Output("avg-bar", "figure"),
    Input("avg-metric-dd", "value"),
    Input("avg-group-dd", "value"),
    Input("avg-topn", "value"),
)
def _update_avg_bar(metric, group_col, topn):
    df = _df()

    if metric is None or group_col is None or metric not in df.columns or group_col not in df.columns:
        return px.bar(title="Select a metric and a grouping column")

    # aggregate
    agg = (
        df.groupby(group_col, dropna=False)[metric]
          .mean()
          .reset_index()
          .rename(columns={metric: "avg_value"})
    )

    # If grouping by country, limit to Top N by avg_value to keep chart readable
    if group_col == "country_name" and isinstance(topn, (int, float)):
        agg = agg.sort_values("avg_value", ascending=False).head(int(topn))
    else:
        agg = agg.sort_values("avg_value", ascending=False)

    # Build plot
    fig = px.bar(
        agg,
        x=group_col,
        y="avg_value",
        color=group_col if group_col in ("regional_indicator", "year") else None,
        title=f"Average {_labelize(metric)} by {_labelize(group_col)}",
    )

    # Tidy layout
    fig.update_layout(
        xaxis_title=_labelize(group_col),
        yaxis_title=f"Average {_labelize(metric)}",
        margin={"t": 60, "l": 10, "r": 10, "b": 80},
        legend_title_text=_labelize(group_col) if group_col in ("regional_indicator", "year") else None,
    )
    fig.update_xaxes(categoryorder="total descending")
    fig.update_traces(marker_line_width=0.5)
    return fig
