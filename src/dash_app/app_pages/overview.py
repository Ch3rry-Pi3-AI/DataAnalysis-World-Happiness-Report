import dash
from dash import html
import pandas as pd
from src.dash_app.data_access import get_gold_df

dash.register_page(__name__, path="/overview", name="Overview", order=1)

def _df() -> pd.DataFrame:
    return get_gold_df()

_df0 = _df()

layout = html.Div(
    [
        html.H2("World Happiness - Overview", className="fw-bold text-center mt-3")
    ]
)