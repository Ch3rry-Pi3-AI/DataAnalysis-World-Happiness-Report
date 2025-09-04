import dash
from dash import html
import pandas as pd
from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/home", name="Home 🏠", order=0)

def _df() -> pd.DataFrame:
    return get_gold_df()

def _dataset_summary(df: pd.DataFrame):
    n_rows = df.shape[0]
    n_cols = df.shape[1]
    num_cols = df.select_dtypes(include="number").shape[1]
    cat_cols = df.select_dtypes(exclude="number").shape[1]
    countries = df["country_name"].nunique()
    year_min, year_max = int(df["year"].min()), int(df["year"].max())
    return [
        html.Li([html.B("Rows: "), f"{n_rows}"]),
        html.Li([html.B("Columns: "), f"{n_cols} (numeric: {num_cols}, non-numeric: {cat_cols})"]),
        html.Li([html.B("Countries: "), f"{countries}"]),
        html.Li([html.B("Years present: "), f"{year_min}-{year_max}"]),
    ]

_df0 = _df()

layout = html.Div(
    className="container py-4 rounded-2",
    children=[
        html.Div(
            className="text-center mb-4",
            children=[
                html.H1("Overview", className="text-light fw-bold"),
                html.P("Now showing a basic dataset summary.", className="text-light"),
            ],
        ),
        
        html.Div(
            className="card shadow-sm rounded-2",
            children=[
                html.Div(
                    className="card-body",
                    children=[
                        html.H3("Dataset at a glance", className="fw-bold"),
                        html.Ul(_dataset_summary(_df0), className="list-group list-group-flush"),
                    ],
                )
            ],
        ),
    ],
    style={"backgroundColor": "#649ec784"},
)
