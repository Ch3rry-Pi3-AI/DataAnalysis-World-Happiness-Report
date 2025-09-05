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
dash.register_page(__name__, path="/", name="Home 🏠", order=0)

# ----------------------------------------------------------------------
# Data access
# ----------------------------------------------------------------------

# Small wrapper so tests can patch this easily
def _df() -> pd.DataFrame:
    """
    Return the gold dataset used across pages.

    Isolated so that:
    - unit tests can inject a small DataFrame,
    - other pages can reuse the same loader.
    """

    # Return central data accessor function
    return get_gold_df()

# ----------------------------------------------------------------------
# UI helpers
# ----------------------------------------------------------------------

# Build a short “facts” list for the dataset
def _dataset_summary(df: pd.DataFrame) -> List[Component]:
    """
    Build a short, human-readable summary as list items.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Gold dataset

    Returns
    -------
    list :
        List items for CSS Bootstrap list group.
    """

    # Count total rows + columns
    n_rows = df.shape[0]
    n_cols = df.shape[1]

    # Count number of numeric columns + non-numeric columns
    num_cols = df.select_dtypes(include="number").shape[1]
    cat_cols = df.select_dtypes(exclude="number").shape[1]

    # Number of distinct countries
    countries = df["country_name"].nunique()

    # Calculate year range
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
    """
    Build a small block with a heading + bulleted list for Top/Bottom N in the latest year.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Gold dataset
    kind : {"top", "bottom"}, optional
        Whether to show happiest (top) or least happy (bottom) countries (default: top)
    n : int, optional
        Number of countries to display (default: 5)

    Returns
    -------
        List of countries and their respective scores.
    """
    
    # Latest year in data
    latest_year = int(df["year"].max())
    
    # Set asc to True if kind == "bottom"
    asc = (kind == "bottom")

    # Title text decided by value of asc
    title = (
        f"Least {n} happy countries - {latest_year}" if asc else f"Top {n} happiest countries - {latest_year}"
    )

    # Filter to latest (rows) and country name and ladder score (columns)
    ordered = (
        df.loc[df["year"] == latest_year, ["country_name", "ladder_score"]]
            # Sort values (ascending or descending) based on if asc == True or asc == False
            .sort_values(by="ladder_score", ascending=asc)
            .head(n)
    )

    # List of items as tuples (Country: Ladder Score)
    items = [
        html.Li(f"{o.country_name}: {o.ladder_score:.2f}") for o in ordered.itertuples(index=False)
    ]

    # Return title + list wrapped together
    return html.Div(
        [
            # Heading
            html.H5(
                title,
                className="fw-bold mt-3 mb-2",
            ),

            # List of formatted tuples
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

            className="text-center mb-4", # Centre heading and add space below: mb (margin-bottom)
            children=[

                # Home page heading
                html.H2(
                    "Overview", 
                    className="text-light fw-bold"
                ),

                # Brief description of the app
                html.P(
                    "Explore the World Happiness Report (WHR) through interactive charts, maps, and tables. "
                    "This app uses a curated dataset combining WHR indicators with geolocation. "
                    "Use the navigation bar at the top to switch between views.",
                    className="text-light fw-bold",
                ),
            ],
        ),

        # --------------------------------------------------------------
        # Two columns: Overview (left) + Facts (right)
        # --------------------------------------------------------------
        
        html.Div(
            className="row g-4", # Row with gap (g-4) between columns
            children=[

                # ------------------------------------------------------
                # Left column
                # ------------------------------------------------------

                html.Div(
                    className="col lg-7", # 7/12 width on large screens
                    children = [

                        # ----------------------------------------------
                        # Top Card: What is WHR?
                        # ----------------------------------------------

                        html.Div(
                            className="card shadow-sm rounded-2 mb-4", # Card container with small shadow (shadow-sm)
                            children=[

                                # Card content area with padding
                                html.Div(
                                    className="card-body p-4",
                                    children=[

                                        # Card title
                                        html.H3("What is the World Happiness Report?", className="fw-bold"),

                                        # Horizontal line
                                        html.Hr(),

                                        # High-level explanation of the WHR
                                        html.P(
                                            "The World Happiness Report (WHR) is an annual publication on global well-being. "
                                            "It ranks countries using survey-based life evaluations (the 'Cantril ladder') and "
                                            "analyses key correlations such as income, social support, healthy life expectancy, "
                                            "freedom to make life choices, generosity, and perceptions of corruption.",
                                        ),

                                        # Link to official WHR site
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

                                        # Link to 2021 WHR overview
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

                        # ----------------------------------------------
                        # Bottom Card: GitHub Repository
                        # ----------------------------------------------

                        html.Div(
                            # Second card below the first
                            className="card shadow-sm rounded-2",
                            children=[

                                # Card content area with padding
                                html.Div(
                                    className="card-body p-4",
                                    children=[

                                        # Card title
                                        html.H3(
                                            "Source Code", 
                                            className="fw-bold"
                                        ),

                                        # Horizontal line
                                        html.Hr(),

                                        # Link to repository
                                        html.P([
                                            "The full source code for this dashboard is available on GitHub: ",
                                            html.A(
                                                "github.com/Ch3rry-Pi3-AI/DataAnalysis-World-Happiness-Report",
                                                href="https://github.com/Ch3rry-Pi3-AI/DataAnalysis-World-Happiness-Report",
                                                target="_blank",
                                                rel="noopener noreferrer",
                                            ),
                                            ".",
                                        ]),
                                        html.P(
                                            "The repository is organised into one branch per project stage "
                                            "(e.g., 00_project_setup, 01_import_data). Each branch includes its own "
                                            "README for quick orientation and reproducible steps."
                                        ),
                                    ],
                                )
                            ],
                        ),
                    ],
                ),

                # ------------------------------------------------------
                # Right column (Snapshot + Top/Bottom 5 Rankings)
                # ------------------------------------------------------

                html.Div(
                    className="col-lg-5",
                    children=[

                        # Dataset snapshot + rankings
                        html.Div(

                            # ------------------------------------------
                            # Single card for Snapshot + Rankings
                            # ------------------------------------------

                            className="card shadow-sm rounded-2",
                            children=[

                                # Content
                                html.Div(
                                    className="card-body p-4",
                                    children=[
                                        
                                        # Title for the single card
                                        html.H3(
                                            "Dataset at a glance",
                                            className="fw-bold"
                                        ),

                                        # Horizontal line
                                        html.Hr(),

                                        # ------------------------------
                                        # Snapshot 
                                        # ------------------------------

                                        html.H5(
                                            "Snapshot",
                                            className="fw-bold mt-3 mb-2",
                                        ),

                                        # Grouped list
                                        html.Ul(
                                            _dataset_summary(_df0), 
                                            className="list-group list-group-flush"
                                        ),

                                        # Horizontal line
                                        html.Hr(),

                                        # ------------------------------
                                        # Ranking 
                                        # ------------------------------

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

    # Styling for background colour of the main container
    style = {"backgroundColor": "#649ec784"}
)
