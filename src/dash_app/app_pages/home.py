import dash
from dash import html
dash.register_page(__name__, path="/", name="Home")
layout = html.Div(
    [
        html.H1("Home"),
        html.P("Now coming from app_pages/home.py")
    ]
)