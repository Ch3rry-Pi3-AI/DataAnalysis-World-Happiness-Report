from dash import Dash, html, dcc
import dash

def dashboard() -> Dash:
    """Function to create and configure Dash app."""
    
    app = Dash(
        __name__,
    )

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