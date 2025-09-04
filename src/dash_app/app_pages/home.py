import dash
from dash import html

dash.register_page(__name__, path="/home", name="Home 🏠", order=0)

layout = html.Div(
    className="container py-4 rounded-2",
    children=[
        html.Div(
            className="text-center mb-4",
            children=[
                html.H1("Overview", className="text-light fw-bold"),
                html.P(
                    "…",
                    className="text-light"
                ),
            ],
        ),
    ],
    style={"backgroundColor": "#649ec784"},
)
