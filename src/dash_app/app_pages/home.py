# ----------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------

import dash
from dash import html

from dash.development.base_component import Component

# ----------------------------------------------------------------------
# Page registration
# ----------------------------------------------------------------------

# Register the page so Dash discovers it at startup
dash.register_page(__name__, path="/", name="Home", order=0)

# ----------------------------------------------------------------------
# Data access
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# UI helpers
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Layout
# ----------------------------------------------------------------------

# Page container (L1)
layout: Component = html.Div(
    className="container py-4 rounded-2",
    children=[

        # Title block
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
        # Two columns
        html.Div(
            className="row g-4",
            children=[
                # Left column
                html.Div(
                    className="col lg-7",
                    children = [
                        # Top - What is WHR?
                        html.Div(
                            className="card shadow-sm rounded-2 p-2",
                            children=[

                                # Title card
                                html.H3(
                                    "What is the World Happiness Report (WHR)?"
                                ),

                                # High level explanation
                                html.P(
                                    "The World Happiness Report (WHR) is an annual publication on global well-being. "
                                    "It ranks countries using survey-based life evaluations (the 'Cantril ladder') and "
                                    "analyses key correlations such as income, social support, healthy life expectancy, "
                                    "freedom to make life choices, generosity, and perceptions of corruption."
                                ),

                                # Link to official site
                                html.P(
                                    [
                                        "Learn more on the official website: ",
                                        html.A(
                                            "worldhappiness.report",
                                            href="https://www.worldhappiness.report/",
                                            target="_blank",
                                            rel="noopener noreferrer",
                                        ),
                                        ".",
                                    ]
                                ),
                                # Link to 2021 overview
                                html.P(
                                    [
                                        "Background reading for the 2021 edition (focus on COVID-19): ",
                                        html.A(
                                            "WHR 2021 overview",
                                            href="",
                                            target="_blank",
                                            rel="noopener noreferrer",
                                        ),
                                        ".",
                                    ]
                                ),
                            ]
                        )
        #                 # Bottom - Source code
        #                 html.Div()
                    ]
                ),
        #         # Right column - Dataset at glance
        #         html.Div()
            ]
        )
    ]
)
