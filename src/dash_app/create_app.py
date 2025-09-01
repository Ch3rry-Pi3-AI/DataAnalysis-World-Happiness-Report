from dash import Dash, html, dcc
import dash

def dashboard() -> Dash:
    """Function to create and configure Dash app."""
    
    app = Dash(
        __name__,
    )

    return app


if __name__ == "__main__":
    dashboard()
    print("Dash app entrypoint")
