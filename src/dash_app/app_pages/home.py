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
                ),
            ],
        ),

        # Two columns: overview + dataset facts
        html.Div(
            className="row g-4",
            children=[

                # Left: what is WHR?
                html.Div(
                    className="row g-4",
                    children=[

                        html.Div(
                            className="col-12 col-1g-7",
                            children=[

                                html.Div(

                                    className="card shadow-sm rounded-4",
                                    children=[

                                        html.H3("What is the World Happiness Report?", className="fw-bold"),

                                        html.P(
                                            "The World Happiness Report (WHR) is an annual publication on global well-being. "
                                            "It ranks countries using survey-based life evaluations (the 'Cantril ladder') and "
                                            "analyses key correlations such as income, social support, healthy life expectancy, "
                                            "freedom to make life choices, generosity, and perceptions of corruption."
                                        ),

                                        html.P(

                                            [
                                                "Learn more on the official site: ",

                                                html.A(
                                                    "worldhappiness.report",
                                                    "https://www.worldhappiness.report/",
                                                    target="_blank",
                                                    rel="noopener noreferrer",
                                                ),
                                                "."
                                            ]
                                        ),

                                        html.P(
                                            [
                                                "Background reading for the 2021 edition (focus on COVID-19 impact): ",

                                                html.A(
                                                    "WHR 2021 overview",
                                                    href="https://wwww.worldhappiness.report/ed/2021/",
                                                    target="_blank",
                                                    rel="noopener noreferrer",
                                                ),

                                                ".",
                                            ]
                                        ),
                                    ]
                                )

                            ],
                        ),
                    ],
                ),

                # Right: data snapshot
                html.Div(
                    className="col-12 col-lg-5",
                    children=[

                        html.Div(
                            className="card shadow-sm rounded-4",
                            children=[
                                

                            ],
                        ),

                    ],
                ),
            ],
        ),
    ],

    style={"backgroundColor": "#e3f2fd"},
)