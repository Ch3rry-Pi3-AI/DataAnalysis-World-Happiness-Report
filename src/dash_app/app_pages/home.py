# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------

# Dash framework + HTML primitives
import dash
from dash import html

# Data handling
import pandas as pd

# General component type for Dash return annotations
from typing import List
from dash.development.base_component import Component

# Project data accessor
from src.dash_app.data_access import get_gold_df

# ----------------------------------------------------------------------
# Page registration
# ----------------------------------------------------------------------

# Register the page so Dash discovers it at startup
dash.register_page(__name__, path="/", name="Home", order=0)

# ----------------------------------------------------------------------
# Data access
# ----------------------------------------------------------------------

# Small wrapper so tests can patch this easily
def _df() -> pd.DataFrame:
    return get_gold_df()
# ----------------------------------------------------------------------
# UI helpers
# ----------------------------------------------------------------------

# Build a short “facts” list for the dataset
def _dataset_summary(df: pd.DataFrame) -> List[Component]:
    """Build a short, human-readable summary as list items."""
    n_rows = df.shape[0]
    n_cols = df.shape[1]
    num_cols = df.select_dtypes(include="number").shape[1]
    cat_cols = df.select_dtypes(exclude="number").shape[1]
    countries = df["country_name"].nunique()
    year_min, year_max = int(df["year"].min()), int(df["year"].max())
    year_range = f"{year_min}-{year_max}"

    # Return Bootstrap-styled list items
    return [
        html.Li([html.B("Rows: "), f"{n_rows}"]),
        html.Li([html.B("Columns: "), f"{n_cols} (numeric: {num_cols}, non-numeric: {cat_cols})"]),
        html.Li([html.B("Countries: "), f"{countries}"]),
        html.Li([html.B("Years present: "), year_range]),
    ]

# Create a Top/Bottom N list for the latest year
def _rank_list_latest(df: pd.DataFrame, kind: str = "top", n: int=5) -> Component:
    """Build a small block with a heading + bulleted list for Top/Bottom N in the latest year."""
    latest_year = int(df["year"].max())
    asc = (kind == "bottom")
    title = (
        f"Least {n} happy countries - {latest_year}" if asc else f"Top {n} happiest countries - {latest_year}"
    )

    ordered = (
        df.loc[df["year"] == latest_year, ["country_name", "ladder_score"]]
            .sort_values(by="ladder_score", ascending=asc)
            .head(n)
    )

    items = [
        html.Li(f"{r.country_name}: {r.ladder_score:.2f}") for r in ordered.itertuples(index=False)
    ]

    return html.Div(
        [
            html.H5(
                title,
                className="fw-bold mt-3 mb-2",
            ),
                html.Ul(
                    items,
                    className="mb-0"
            ),
        ]
    )

# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------

# Cache a DataFrame for this page
_df0: pd.DataFrame = _df()

# ----------------------------------------------------------------------
# Layout
# ----------------------------------------------------------------------

# Page container (L1)
layout: Component = html.Div(
    className="container py-4 rounded-2",
    children=[

        # --------------------------------------------------------------
        # Title block
        # --------------------------------------------------------------

        html.Div(

            className="text-center mb-4",
            children=[
                html.H2(
                    "Overview", 
                    className="text-light fw-bold"
                ),

                html.P(
                    "Explore the World Happiness Report with interactive charts, maps and tables. "
                    "This app reads a curated 'gold' dataset that merges WHR indicators with geolocation.",
                    className="text-light",
                ),
            ],
        ),

        # --------------------------------------------------------------
        # Two columns: Overview (left) + Facts (right)
        # --------------------------------------------------------------
        
        html.Div(
            className="row g-4",
            children=[

                # ------------------------------------------------------
                # Left column
                # ------------------------------------------------------

                html.Div(
                    className="col lg-7",
                    children = [

                        # Top - What is WHR?
                        html.Div(
                            # Card container with subtle shadow
                            className="card shadow-sm rounded-2 mb-4",
                            children=[

                                # Card content area with padding
                                html.Div(
                                    className="card-body p-4",
                                    children=[

                                        # Card title
                                        html.H3("What is the World Happiness Report?", className="fw-bold"),
                                        # High-level explanation
                                        html.P(
                                            "The World Happiness Report (WHR) is an annual publication on global well-being. "
                                            "It ranks countries using survey-based life evaluations (the 'Cantril ladder') and "
                                            "analyses key correlations such as income, social support, healthy life expectancy, "
                                            "freedom to make life choices, generosity, and perceptions of corruption."
                                        ),

                                        # Link to official site
                                        html.P([
                                            "Learn more on the official site: ",
                                            html.A(
                                                "worldhappiness.report",
                                                href="https://www.worldhappiness.report/",
                                                target="_blank",
                                                rel="noopener noreferrer",
                                            ),
                                            ".",
                                        ]),

                                        # Link to 2021 overview
                                        html.P([
                                            "Background reading for the 2021 edition (focus on COVID-19 impact): ",
                                            html.A(
                                                "WHR 2021 overview",
                                                href="https://www.worldhappiness.report/ed/2021/",
                                                target="_blank",
                                                rel="noopener noreferrer",
                                            ),
                                            ".",
                                        ]),
                                    ],
                                )
                            ],
                        ),

                        # -------- Card 2: Source code link --------
                        html.Div(
                            # Second card below the first
                            className="card shadow-sm rounded-2",
                            children=[

                                # Card content area with padding
                                html.Div(
                                    className="card-body p-4",
                                    children=[

                                        # Card title
                                        html.H3("Source Code", className="fw-bold"),

                                        # Link to rep
                                        html.P([
                                            "The full source code for this dashboard is available on GitHub: ",
                                            html.A(
                                                "github.com/your-username/your-repo",
                                                href="https://github.com/your-username/your-repo",
                                                target="_blank",
                                                rel="noopener noreferrer",
                                            ),
                                            ".",
                                        ]),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),

                # ------------------------------------------------------
                # Right column
                # ------------------------------------------------------

                html.Div(
                    className="col-lg-5",
                    children=[

                        # Dataset snapshot + rankings
                        html.Div(
                            # Single card
                            className="card shadow-sm rounded-2",
                            children=[

                                # Content
                                html.Div(
                                    className="card-body p-4",
                                    children=[
                                        
                                        # Title
                                        html.H3(
                                            "Dataset at a glance",
                                            className="fw-bold"
                                        ),
                                        html.Ul(
                                            _dataset_summary(_df0), 
                                            className="list-group list-group-flush"
                                        ),
                                        html.Hr(),
                                        _rank_list_latest(_df0, kind="top", n=5),
                                        _rank_list_latest(_df0, kind="bottom", n=5),
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ],
    style = {"backgroundColor": "#649ec784"}
)
