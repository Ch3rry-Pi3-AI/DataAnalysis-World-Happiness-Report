import dash
from dash import html
dash.register_page(__name__, path="/about", name="About")
layout = html.Div(
    [
        html.H1("About"),
        html.P("Now coming from app_pages/about.py")
    ]
)