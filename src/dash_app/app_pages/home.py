import dash
from dash import html
import pandas as pd
from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/", name="Home", order=0)

def _df() -> pd.DataFrame:
    return get_gold_df()

def _summary_items(df: pd.DataFrame):
    n_rows = len(df)
    n_cols = df.shape[1]
    num_cols = df.select_dtypes(include="number").shape[1]
    cat_cols = df.select_dtypes(exclude="number").shape[1]

    countries = df["country_name"].nunique()
    years = sorted(df["year"].dropna().unique())
    year_range = f"{years[0]}-{years[-1] if years else "N/A"}"

    items = [
        html.Li([html.B("Rows: "), (f"{n_rows}")]),
        html.Li([html.B("Columns:" ), f"{n_cols}" f"(numeric: {num_cols}" f"(numeric: {num_cols}, non-numeric: {cat_cols})"]),
        html.Li([html.B("Countries: "), f"{countries}"]),
        html.Li([html.B("Years present: "), year_range])
    ]

    return items

_df0 = _df()

layout = html.Div(
    className="container py-4",
    children=[
        # Title
        html.Div(
            className="text-center mb-4",
            children=[
                html.H1("World Happiness - Interactive Explorer", className="fw-bold"),
                html.P(
                    "Explore the World Happiness Report with interactive charts, maps and tables. "
                    "This app reads a curated 'gold' dataset that merges WHR indicators with geolocation.",
                    className="text-muted"
                )
            ]
        )
    ]
)