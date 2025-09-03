# src/dash_app/app_pages/heatmap.py
import dash
from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.express as px

from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/heatmap", name="Correlation 📊", order=5)

# ---------- Helpers ----------
def _df() -> pd.DataFrame:
    return get_gold_df()

def _year_options(df: pd.DataFrame):
    if "year" not in df.columns:
        return []
    years = sorted(pd.Series(df["year"]).dropna().unique().tolist())
    return [{"label": str(int(y)), "value": int(y)} for y in years]

def _numeric(df: pd.DataFrame) -> pd.DataFrame:
    # numeric only, drop columns with all-NaN or zero variance (to avoid NaNs/flat rows in corr)
    num = df.select_dtypes(include="number")
    if num.empty:
        return num
    # drop columns that are all NaN or constant
    mask_constant = num.nunique(dropna=True) <= 1
    return num.loc[:, ~mask_constant]

# ---------- Layout ----------
_BASE = _df()

layout = html.Div(
    [
        html.H2("Features Correlation Heatmap", className="fw-bold text-center my-3"),

        html.Div(
            className="d-flex flex-wrap justify-content-center gap-3 mb-3",
            children=[
                dcc.Dropdown(
                    id="hm-year-dd",
                    options=_year_options(_BASE),
                    value=None,
                    clearable=True,
                    placeholder="Filter by Year",
                ),
                dcc.Dropdown(
                    id="hm-method-dd",
                    options=[
                        {"label": "Pearson", "value": "pearson"},
                        {"label": "Kendall", "value": "kendall"},
                        {"label": "Spearman", "value": "spearman"},
                    ],
                    value="pearson",
                    clearable=False,
                    placeholder="Select correlation method",
                ),
                dcc.Checklist(
                    id="hm-abs-toggle",
                    options=[{"label": "Show absolute values", "value": "abs"}],
                    value=[],
                    inline=True,
                ),
            ],
        ),

        dcc.Graph(id="hm-fig"),
        html.Small(

        ),
    ]
)

# ---------- Callback ----------
@callback(
    Output("hm-fig", "figure"),
    Input("hm-year-dd", "value"),
    Input("hm-method-dd", "value"),
    Input("hm-abs-toggle", "value"),
)
def _update_heatmap(year_value, method, abs_toggle):
    df = _df()

    if year_value is not None and "year" in df.columns:
        df = df[df["year"] == year_value]

    num = _numeric(df)
    num = _numeric(df)
    if num.empty or num.shape[1] < 2:
        fig = px.imshow([[1]], labels=dict(x="N/A", y="N/A", color="corr"), height=300)
        fig.update_layout(title="Not enough numeric columns to compute correlation")
        return fig
    
    corr = num.corr(method=method)
    if abs_toggle:
        corr = corr.abs()

    try:
        import scipy.cluster.hierarchy as sch
        dist = 1 - corr.abs()
        linkage = sch.linkage(dist, method="average")
        dendro_order = sch.leaves_list(sch.dendrogram(linkage, no_plot=True)["leaves"])
        corr = corr.iloc[dendro_order, :].iloc[:, dendro_order]
    except Exception:
        pass

    fig = px.imshow(
        corr,
        height=600,
        color_continuous_scale="RdBu",
        zmin=-1 if not abs_toggle else 0,
        zmax=1,
        aspect="auto",
    )
    title = f"({method.title()} correlation)"
    title_year = f" - Year {year_value}" if year_value else ""
    fig.update_layout(
        title=f"Correlation Heatmap{title}{title_year}",
        margin={"t": 60, "l": 10, "r": 10, "b": 10},
        coloraxis_colorbar_title="corr",
    )
    return fig