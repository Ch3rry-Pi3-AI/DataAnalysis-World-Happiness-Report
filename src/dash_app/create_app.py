from dash import Dash, html, dcc
import dash

def dashboard(enable_pages: bool = True) -> Dash:
    """Function to create and configure Dash app."""

    external_css = [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css"
    ]

    app = Dash(
        __name__,
        external_stylesheets=external_css,
        use_pages=enable_pages,
        pages_folder="app_pages" if enable_pages else None,
        suppress_callback_exceptions=True,
    )

    #----------------- Placeholder pages -------------------#

    home_layout = html.Div(
        [
            html.H1("Home", className="text-center mt-4"),
            html.P("Welcome to the demo scaffold.", className="text-center"),
        ],
        className="container",
    )

    about_layout = html.Div(
        [
            html.H1("About", className="text-center mt-4"),
            html.P("This page is defined inline for now.", className="text-center"),
        ],
        className="container",
    )

    manual_routes = {
        "/": home_layout,
        "/about": about_layout,
    }

    #----------------- Main content -------------------#

    app.layout = html.Div([
        # Main page
        html.Div([
            html.Br(),
            html.P(
                "Multi-Page Dash-Plotly Web App",
                className="text-dark text-centre fw-bold fs-1"
            ),
            dash.page_container
        ], className="col-6 mx-auto")
    ], style={"height": "100vh", "background-colour": "#e3f2fd"})

    return app


if __name__ == "__main__":
    dashboard()
    print("Dash app entrypoint")