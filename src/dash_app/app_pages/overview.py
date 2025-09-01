import dash
from dash import html
import pandas as pd
from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/overview", name="Overview", order=1)

def _df() -> pd.DataFrame:
    return get_gold_df()

def _summary_items(df: pd.DataFrame):
    n_rows = len(df)
    n_cols = df.shape[1]

    items = [
        html.Li([html.B("Rows: "), (f"{n_rows}")]),
        html.Li([html.B("Columns:" ), (f"{n_cols}")])
    ]

    return items

_df0 = _df()

layout = html.Div(
    [
        html.H2("World Happiness - Overview", className="fw-bold text-center mt-3"),
        html.Ul(_summary_items(_df0))
    ]
)