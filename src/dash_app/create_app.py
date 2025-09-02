from dash import Dash, html, dcc, Input, Output
import dash

def dashboard(enable_pages: bool = True) -> Dash:
    """Function to create and configure Dash app."""

    external_css = [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.rtl.css"
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

    #----------------- Navbar  -------------------#

    def navbar_links():
        if enable_pages and dash.page_registry:
            return[
                dcc.Link(
                    page["name"],
                    href=page["relative_path"],
                    className="nav-link"
                )
                for page in dash.page_registry.values()
            ]
        
        else:
            return[
                dcc.Link("Home", href="/", className="nav-link"),
                dcc.Link("About", href="/about", className="nav-link"),
            ]
        
    brand = dcc.Link("  DataVis App ", href="/", className="navbar-brand")
    nav = html.Nav(
        className="navbar navbar-expand-lg bg-dark",
        **{"data-bs-theme": "dark"},
        children=html.Div(
            className="container-fluid",
            children=html.Div([brand] + navbar_links(), className="navbar-nav"),
        ),
    )

    #----------------- Main content -------------------#

    header = html.P(
        "Multi-Page Dash-Plotly Web App",
        className="text-dark text-center fw-bold fs-1",
    )

    if enable_pages:
        main_content = dash.page_container
    else:
        main_content = html.Div(id="page-content", className="container")

    app.layout = html.Div(
        [
            nav,
            html.Div(
                [
                    html.Br(),
                    header,
                    main_content
                ], className="col-10 col-lg-8 mx-auto"
            ),
        ],
        style={"minHeight": "100vh", "backgroundColor": "#e3f2df"},
    )

    #----------------- Manual router callback -------------------#
    if not enable_pages:
        app.layout.children.append(dcc.Location(id="url"))

        @app.callback(Output("page-content", "children"), Input("url", "pathname"))
        def route(pathname: str):
            return manual_routes.get(
                pathname,
                html.Div(
                    [
                        html.H1("404", className="text-center mt-4"),
                        html.P("Page not found.", className="text-center")
                    ],
                    className="container",
                )
            )

    return app


if __name__ == "__main__":
    dashboard()
    print("Dash app entrypoint")